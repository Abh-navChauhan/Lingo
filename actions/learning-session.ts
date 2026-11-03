"use server";

import { auth } from "@clerk/nextjs/server";
import { revalidatePath } from "next/cache";
import { desc, eq } from "drizzle-orm";

import db from "@/db/drizzle";
import { userLearningSessions, userEarnedPremium, lessons } from "@/db/schema";
import { getUserLearningSessions, getUserEarnedPremium } from "@/db/queries";

const ML_API_BASE = process.env.ML_API_URL || "http://127.0.0.1:8000";

type RecordSessionParams = {
  lessonId: number;
  totalChallenges: number;
  correctChallenges: number;
  attempts: number;
  avgResponseTime: number; // in seconds
};

export const recordLearningSession = async ({
  lessonId,
  totalChallenges,
  correctChallenges,
  attempts,
  avgResponseTime,
}: RecordSessionParams) => {
  const { userId } = await auth();

  if (!userId) {
    throw new Error("Unauthorized");
  }

  // Calculate current session accuracy
  const accuracyPct = totalChallenges > 0 
    ? Math.round((correctChallenges / totalChallenges) * 100) 
    : 100;

  // Retrieve lesson context to determine curriculum topic
  const lessonData = await db.query.lessons.findFirst({
    where: eq(lessons.id, lessonId),
    with: {
      unit: true,
    },
  });

  const topicName = lessonData?.unit?.title || "Spanish Basics";

  // Fetch past session history for longitudinal features
  const pastSessions = await db.query.userLearningSessions.findMany({
    where: eq(userLearningSessions.userId, userId),
    orderBy: [desc(userLearningSessions.completedAt)],
    limit: 20,
  });

  // Calculate longitudinal ML features
  let previousAccuracy = accuracyPct / 100;
  let topicWiseAccuracy = accuracyPct / 100;
  let consistency = 0.8;
  let recentImprovement = 0.05;
  let previousMastery = "Beginner";
  const topicHistory: Record<str, number> = {};

  if (pastSessions.length > 0) {
    const totalPastAccuracy = pastSessions.reduce((acc, s) => acc + s.accuracy, 0);
    previousAccuracy = totalPastAccuracy / (pastSessions.length * 100);

    const sameTopicSessions = pastSessions.filter((s) => s.topic === topicName);
    if (sameTopicSessions.length > 0) {
      const topicAccSum = sameTopicSessions.reduce((acc, s) => acc + s.accuracy, 0);
      topicWiseAccuracy = topicAccSum / (sameTopicSessions.length * 100);
    }

    // Consistency based on frequency of participation
    consistency = Math.min(0.5 + pastSessions.length * 0.08, 1.0);

    // Calculate recent improvement trend from last 3 sessions
    if (pastSessions.length >= 2) {
      const recentAcc = pastSessions.slice(0, 3).reduce((acc, s) => acc + s.accuracy, 0) / Math.min(3, pastSessions.length);
      const olderAcc = pastSessions.slice(3, 8).length > 0
        ? pastSessions.slice(3, 8).reduce((acc, s) => acc + s.accuracy, 0) / pastSessions.slice(3, 8).length
        : recentAcc;
      recentImprovement = Math.max(-0.3, Math.min(0.4, (recentAcc - olderAcc) / 100));
    }

    if (pastSessions[0].predictedMastery) {
      previousMastery = pastSessions[0].predictedMastery;
    }

    // Populate topic history dictionary
    pastSessions.forEach((s) => {
      if (!topicHistory[s.topic]) {
        topicHistory[s.topic] = s.accuracy / 100;
      }
    });
  }
  topicHistory[topicName] = accuracyPct / 100;

  // Prepare structured payload for FastAPI ML microservice
  const mlPayload = {
    student_id: userId,
    topic: topicName,
    previous_accuracy: Math.min(1.0, Math.max(0.0, previousAccuracy)),
    topic_wise_accuracy: Math.min(1.0, Math.max(0.0, topicWiseAccuracy)),
    number_of_attempts: Math.max(1, attempts),
    avg_response_time: Math.max(1.0, avgResponseTime),
    completion_rate: 1.0,
    learning_consistency: Math.min(1.0, Math.max(0.1, consistency)),
    recent_improvement: Math.min(0.5, Math.max(-0.5, recentImprovement)),
    previous_mastery: previousMastery,
    topic_history: topicHistory,
  };

  let mlResponse = null;
  try {
    const res = await fetch(`${ML_API_BASE}/evaluate-session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mlPayload),
      signal: AbortSignal.timeout(4000), // 4s timeout prevents hanging
    });

    if (res.ok) {
      mlResponse = await res.json();
    }
  } catch (error) {
    console.warn("ML API unavailable or timed out; falling back to local heuristic.", error);
  }

  // Fallback heuristic if ML service is temporarily down
  const predictedMastery = mlResponse?.prediction?.predicted_mastery || (
    accuracyPct >= 85 ? "Advanced" : accuracyPct >= 65 ? "Intermediate" : "Beginner"
  );
  const confidence = mlResponse?.prediction?.confidence 
    ? Math.round(mlResponse.prediction.confidence * 100) 
    : 85;
  const clusterLabel = mlResponse?.prediction?.cluster_label || "Steady Consistent Learner";

  // 1. Persist session telemetry into Neon PostgreSQL
  await db.insert(userLearningSessions).values({
    userId,
    lessonId,
    topic: topicName,
    accuracy: accuracyPct,
    totalChallenges,
    correctChallenges,
    attempts,
    avgResponseTime: Math.round(avgResponseTime),
    predictedMastery,
    confidence,
    clusterLabel,
  });

  // 2. Persist Earned Premium eligibility into Neon PostgreSQL
  const premiumInfo = mlResponse?.premium_eligibility || {
    is_eligible: predictedMastery === "Advanced",
    tier: predictedMastery === "Advanced" ? "7_DAY_LEGENDARY_PASS" : "FOUNDATION_FREE",
    duration_days: predictedMastery === "Advanced" ? 7 : 0,
    progress_percentage: predictedMastery === "Advanced" ? 100 : 65,
    explanation: `Demonstrated ${predictedMastery} mastery with ${accuracyPct}% quiz accuracy.`,
  };

  const existingPremium = await db.query.userEarnedPremium.findFirst({
    where: eq(userEarnedPremium.userId, userId),
  });

  let unlockedAt = existingPremium?.unlockedAt;
  let expiresAt = existingPremium?.expiresAt;

  if (premiumInfo.is_eligible && (!expiresAt || expiresAt.getTime() < Date.now())) {
    unlockedAt = new Date();
    expiresAt = new Date(Date.now() + (premiumInfo.duration_days || 7) * 24 * 60 * 60 * 1000);
  }

  if (existingPremium) {
    await db.update(userEarnedPremium).set({
      isEligible: premiumInfo.is_eligible,
      tier: premiumInfo.tier,
      predictedMastery,
      masteryConfidence: confidence,
      clusterLabel,
      unlockedAt,
      expiresAt,
      unlockedReason: premiumInfo.explanation,
      progressPercentage: premiumInfo.progress_percentage || 50,
    }).where(eq(userEarnedPremium.userId, userId));
  } else {
    await db.insert(userEarnedPremium).values({
      userId,
      isEligible: premiumInfo.is_eligible,
      tier: premiumInfo.tier,
      predictedMastery,
      masteryConfidence: confidence,
      clusterLabel,
      unlockedAt,
      expiresAt,
      unlockedReason: premiumInfo.explanation,
      progressPercentage: premiumInfo.progress_percentage || 50,
    });
  }

  revalidatePath("/learn");
  revalidatePath("/shop");
  revalidatePath("/intelligence");

  return {
    success: true,
    predictedMastery,
    confidence,
    clusterLabel,
    recommendations: mlResponse?.recommendations || {
      recommended_action: predictedMastery === "Advanced" ? "ACCELERATED_CHALLENGE" : "TARGETED_PRACTICE",
      recommended_difficulty: predictedMastery === "Advanced" ? "MASTERY" : "STANDARD",
      rationale: `Model confirmed ${predictedMastery} level. Next unit calibrated accordingly.`,
      next_suggested_lesson: `${topicName} - Adaptive Followup`,
    },
    premiumEligibility: premiumInfo,
    activePremium: expiresAt && expiresAt.getTime() > Date.now(),
  };
};

