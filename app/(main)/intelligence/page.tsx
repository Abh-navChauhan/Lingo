import Image from "next/image";
import Link from "next/link";
import { redirect } from "next/navigation";
import { 
  Brain, 
  Sparkles, 
  Trophy, 
  Flame, 
  TrendingUp, 
  Target, 
  Clock, 
  Layers, 
  Award, 
  AlertCircle,
  ArrowRight,
  BookOpen
} from "lucide-react";

import { FeedWrapper } from "@/components/feed-wrapper";
import { UserProgress } from "@/components/user-progress";
import { StickyWrapper } from "@/components/sticky-wrapper";
import { Button } from "@/components/ui/button";
import { 
  getUserProgress, 
  getUserSubscription, 
  getUserLearningSessions, 
  getUserEarnedPremium 
} from "@/db/queries";

const IntelligencePage = async () => {
  const userProgressData = getUserProgress();
  const userSubscriptionData = getUserSubscription();
  const sessionsData = getUserLearningSessions();
  const earnedPremiumData = getUserEarnedPremium();

  const [
    userProgress,
    userSubscription,
    sessions,
    earnedPremium,
  ] = await Promise.all([
    userProgressData,
    userSubscriptionData,
    sessionsData,
    earnedPremiumData,
  ]);

  if (!userProgress || !userProgress.activeCourse) {
    redirect("/courses");
  }

  const isPro = !!userSubscription?.isActive;

  // Aggregate student telemetry from stored sessions
  const totalSessions = sessions.length;
  const avgAccuracy = totalSessions > 0
    ? Math.round(sessions.reduce((acc, s) => acc + s.accuracy, 0) / totalSessions)
    : 80;
  const avgResponseTime = totalSessions > 0
    ? Math.round(sessions.reduce((acc, s) => acc + s.avgResponseTime, 0) / totalSessions)
    : 14;

  // Compute topic-wise distribution
  const topicMap: Record<string, { totalAcc: number; count: number }> = {};
  sessions.forEach((s) => {
    if (!topicMap[s.topic]) {
      topicMap[s.topic] = { totalAcc: 0, count: 0 };
    }
    topicMap[s.topic].totalAcc += s.accuracy;
    topicMap[s.topic].count += 1;
  });

  const topicStats = Object.keys(topicMap).map((topic) => ({
    topic,
    accuracy: Math.round(topicMap[topic].totalAcc / topicMap[topic].count),
    sessionsCount: topicMap[topic].count,
  }));

  // Fallback default topics if student is brand new
  if (topicStats.length === 0) {
    topicStats.push(
      { topic: "Spanish Basics", accuracy: avgAccuracy, sessionsCount: 1 },
      { topic: "Grammar & Verbs", accuracy: Math.max(50, avgAccuracy - 15), sessionsCount: 1 },
      { topic: "Food & Dining", accuracy: Math.min(100, avgAccuracy + 10), sessionsCount: 1 }
    );
  }

  topicStats.sort((a, b) => b.accuracy - a.accuracy);
  const strongestTopic = topicStats[0];
  const weakestTopic = topicStats[topicStats.length - 1];

  const predictedMastery = earnedPremium?.predictedMastery || (
    avgAccuracy >= 85 ? "Advanced" : avgAccuracy >= 65 ? "Intermediate" : "Beginner"
  );
  const confidence = earnedPremium?.masteryConfidence || 88;
  const clusterLabel = earnedPremium?.clusterLabel || (
    avgResponseTime < 10 ? "Rapid High-Performer" : "Steady Consistent Learner"
  );

  return (
    <div className="flex flex-row-reverse gap-[48px] px-6">
      <StickyWrapper>
        <UserProgress
          activeCourse={userProgress.activeCourse}
          hearts={userProgress.hearts}
          points={userProgress.points}
          hasActiveSubscription={isPro}
        />
        
        {/* Merit-Based Premium Status Card */}
        <div className="border-2 rounded-2xl p-4 bg-white shadow-sm flex flex-col gap-y-3">
          <div className="flex items-center gap-x-2 text-indigo-600 font-extrabold text-sm uppercase tracking-wider">
            <Sparkles className="h-4 w-4" />
            <span>Earned Premium Status</span>
          </div>
          {isPro ? (
            <div className="bg-green-50 border border-green-200 rounded-xl p-3 text-xs text-green-800 flex flex-col gap-y-1">
              <span className="font-extrabold flex items-center gap-x-1.5">
                <Trophy className="h-4 w-4 text-yellow-500" />
                Active Pass Unlocked!
              </span>
              <span>Unlimited hearts enabled via merit prediction.</span>
            </div>
          ) : (
            <div className="flex flex-col gap-y-2 text-xs text-neutral-600">
              <div className="flex justify-between font-bold">
                <span>Unlock Progress:</span>
                <span className="text-indigo-600">{earnedPremium?.progressPercentage || 45}%</span>
              </div>
              <div className="w-full bg-neutral-200 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-indigo-500 h-full rounded-full"
                  style={{ width: `${earnedPremium?.progressPercentage || 45}%` }}
                />
              </div>
              <p className="text-[11px] text-muted-foreground">
                Earn &gt;= 70% accuracy on upcoming lessons to unlock free unlimited hearts.
              </p>
            </div>
          )}
          <Link href="/shop" className="w-full">
            <Button variant="primaryOutline" className="w-full text-xs font-bold">
              View Merit Pass
            </Button>
          </Link>
        </div>

        {/* Academic Viva Specs Card */}
        <div className="border-2 rounded-2xl p-4 bg-neutral-50 shadow-sm flex flex-col gap-y-2 text-xs text-neutral-600">
          <div className="flex items-center gap-x-1.5 font-bold text-neutral-800">
            <BookOpen className="h-4 w-4 text-blue-600" />
            <span>SML Project Details</span>
          </div>
          <p>
            <strong>Pipeline:</strong> Synthetic Data (1800 records) &rarr; Feature Scaling &rarr; Model Evaluation &rarr; FastAPI Inference.
          </p>
          <p>
            <strong>Algorithms:</strong> Logistic Regression, Decision Tree, Random Forest, K-Means.
          </p>
        </div>
      </StickyWrapper>

      <FeedWrapper>
        <div className="w-full flex flex-col gap-y-6">
          {/* Header Banner */}
          <div className="w-full p-6 border-2 border-indigo-200 rounded-3xl bg-gradient-to-r from-indigo-50 via-white to-blue-50 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-x-4">
              <div className="p-4 bg-indigo-600 rounded-2xl text-white shadow-md">
                <Brain className="h-10 w-10" />
              </div>
              <div>
                <div className="flex items-center gap-x-2">
                  <h1 className="text-2xl font-extrabold text-neutral-800">
                    Learning Intelligence
                  </h1>
                  <span className="bg-indigo-100 text-indigo-700 font-bold text-xs px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    ML-Powered
                  </span>
                </div>
                <p className="text-sm text-neutral-600 mt-1">
                  Continuous performance modeling & cognitive mastery classification.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-x-3 bg-white border-2 border-indigo-100 rounded-2xl px-5 py-3 shadow-sm">
              <div className="text-right">
                <p className="text-xs uppercase font-extrabold text-neutral-400">
                  Predicted Mastery
                </p>
                <p className="text-xl font-black text-indigo-600">
                  {predictedMastery}
                </p>
              </div>
              <div className="h-10 w-[2px] bg-neutral-200" />
              <div className="text-left">
                <p className="text-xs uppercase font-extrabold text-neutral-400">
                  Confidence
                </p>
                <p className="text-xl font-black text-green-600">
                  {confidence}%
                </p>
              </div>
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="border-2 rounded-2xl p-4 bg-white shadow-sm flex items-center gap-x-3">
              <div className="p-3 bg-green-100 rounded-xl text-green-700">
                <Target className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xs font-extrabold text-neutral-400 uppercase">Average Accuracy</p>
                <p className="text-2xl font-black text-neutral-800">{avgAccuracy}%</p>
              </div>
            </div>

            <div className="border-2 rounded-2xl p-4 bg-white shadow-sm flex items-center gap-x-3">
              <div className="p-3 bg-blue-100 rounded-xl text-blue-700">
                <Clock className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xs font-extrabold text-neutral-400 uppercase">Avg Response Latency</p>
                <p className="text-2xl font-black text-neutral-800">{avgResponseTime}s</p>
              </div>
            </div>

            <div className="border-2 rounded-2xl p-4 bg-white shadow-sm flex items-center gap-x-3">
              <div className="p-3 bg-purple-100 rounded-xl text-purple-700">
                <Layers className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xs font-extrabold text-neutral-400 uppercase">Behavioral Cluster</p>
                <p className="text-sm font-black text-neutral-800 truncate">{clusterLabel}</p>
              </div>
            </div>
          </div>

          {/* Adaptive Learning Recommendation Engine Card */}
          <div className="border-2 border-green-200 rounded-3xl p-6 bg-gradient-to-br from-green-50/70 via-white to-white shadow-sm flex flex-col gap-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-x-2">
                <div className="p-2 bg-green-600 rounded-xl text-white">
                  <TrendingUp className="h-5 w-5" />
                </div>
                <h2 className="text-lg font-extrabold text-neutral-800">
                  Personalised Learning Recommendation
                </h2>
              </div>
              <span className="text-xs bg-green-100 text-green-800 font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                {predictedMastery === "Advanced" ? "Accelerated Trial" : "Targeted Practice"}
              </span>
            </div>

            <div className="bg-white border rounded-2xl p-4 text-sm text-neutral-700 flex flex-col gap-y-2">
              <p className="font-bold text-neutral-900">
                Algorithm Policy Rationale:
              </p>
              <p className="text-neutral-600 leading-relaxed">
                {predictedMastery === "Advanced"
                  ? `Based on strong cognitive accuracy (${avgAccuracy}%) and rapid response times (${avgResponseTime}s), the recommendation policy has unlocked advanced speed syntax challenges and conversation drills.`
                  : predictedMastery === "Intermediate"
                  ? `Solid foundational grasp demonstrated. The adaptive engine suggests focusing on reinforcing '${weakestTopic.topic}' (${weakestTopic.accuracy}% accuracy) while progressing through '${strongestTopic.topic}'.`
                  : `Model detected foundational gaps in '${weakestTopic.topic}'. Recommending targeted untimed review with multiple-choice reinforcement before tackling new units.`
                }
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
              <div className="text-sm">
                <span className="text-neutral-400 font-bold uppercase text-xs">Suggested Next Action: </span>
                <span className="font-extrabold text-neutral-800">
                  {predictedMastery === "Advanced" 
                    ? `${strongestTopic.topic} - Legendary Challenge` 
                    : `${weakestTopic.topic} - Targeted Revision`}
                </span>
              </div>
              <Link href="/learn">
                <Button className="bg-green-600 hover:bg-green-700 text-white font-bold gap-x-2">
                  Launch Recommended Lesson
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>

          {/* Topic-Wise Performance & Strengths/Weaknesses */}
          <div className="border-2 rounded-3xl p-6 bg-white shadow-sm flex flex-col gap-y-5">
            <h2 className="text-lg font-extrabold text-neutral-800 flex items-center gap-x-2">
              <Award className="h-5 w-5 text-indigo-600" />
              Curriculum Topic Mastery
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-green-200 bg-green-50/50 rounded-2xl p-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-extrabold text-green-700">Strongest Topic</p>
                  <p className="text-lg font-bold text-neutral-800">{strongestTopic.topic}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-black text-green-600">{strongestTopic.accuracy}%</p>
                  <p className="text-xs text-neutral-400">Mastery</p>
                </div>
              </div>

              <div className="border border-amber-200 bg-amber-50/50 rounded-2xl p-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-extrabold text-amber-700">Topic Requiring Focus</p>
                  <p className="text-lg font-bold text-neutral-800">{weakestTopic.topic}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-black text-amber-600">{weakestTopic.accuracy}%</p>
                  <p className="text-xs text-neutral-400">Mastery</p>
                </div>
              </div>
            </div>

            {/* Topic Progress Bars */}
            <div className="flex flex-col gap-y-3 pt-2">
              {topicStats.map((item) => (
                <div key={item.topic} className="flex flex-col gap-y-1">
                  <div className="flex justify-between text-xs font-bold text-neutral-700">
                    <span>{item.topic}</span>
                    <span>{item.accuracy}%</span>
                  </div>
                  <div className="w-full bg-neutral-100 h-2.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${
                        item.accuracy >= 80 ? "bg-green-500" : item.accuracy >= 60 ? "bg-indigo-500" : "bg-amber-500"
                      }`}
                      style={{ width: `${item.accuracy}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Learning Sessions Telemetry */}
          <div className="border-2 rounded-3xl p-6 bg-white shadow-sm flex flex-col gap-y-4">
            <h2 className="text-lg font-extrabold text-neutral-800">
              Recent Session Telemetry
            </h2>
            {sessions.length === 0 ? (
              <p className="text-sm text-neutral-500 italic text-center py-4">
                No completed sessions logged yet. Complete a lesson on the Learn page to see real-time ML inference!
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-neutral-600">
                  <thead className="bg-neutral-50 uppercase text-[10px] font-extrabold text-neutral-400 border-b">
                    <tr>
                      <th className="py-2.5 px-3">Date</th>
                      <th className="py-2.5 px-3">Topic</th>
                      <th className="py-2.5 px-3">Accuracy</th>
                      <th className="py-2.5 px-3">Latency</th>
                      <th className="py-2.5 px-3">Attempts</th>
                      <th className="py-2.5 px-3">ML Prediction</th>
                      <th className="py-2.5 px-3">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {sessions.slice(0, 8).map((s) => (
                      <tr key={s.id} className="hover:bg-neutral-50/70">
                        <td className="py-2 px-3">{new Date(s.completedAt).toLocaleDateString()}</td>
                        <td className="py-2 px-3 font-semibold text-neutral-800">{s.topic}</td>
                        <td className="py-2 px-3 font-bold text-green-600">{s.accuracy}%</td>
                        <td className="py-2 px-3">{s.avgResponseTime}s</td>
                        <td className="py-2 px-3">{s.attempts}</td>
                        <td className="py-2 px-3 font-bold text-indigo-600">{s.predictedMastery || "Beginner"}</td>
                        <td className="py-2 px-3">{s.confidence || 85}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </FeedWrapper>
    </div>
  );
};

export default IntelligencePage;

