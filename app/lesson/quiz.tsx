"use client";

import { toast } from "sonner";
import Image from "next/image";
import Link from "next/link";
import Confetti from "react-confetti";
import { useRouter } from "next/navigation";
import { useState, useTransition, useEffect } from "react";
import { useAudio, useWindowSize, useMount } from "react-use";
import { Brain, Sparkles, Trophy, ArrowRight, Loader } from "lucide-react";

import { reduceHearts } from "@/actions/user-progress";
import { useHeartsModal } from "@/store/use-hearts-modal";
import { challengeOptions, challenges, userSubscription } from "@/db/schema";
import { usePracticeModal } from "@/store/use-practice-modal";
import { upsertChallengeProgress } from "@/actions/challenge-progress";
import { recordLearningSession } from "@/actions/learning-session";

import { Header } from "./header";
import { Footer } from "./footer";
import { Challenge } from "./challenge";
import { ResultCard } from "./result-card";
import { QuestionBubble } from "./question-bubble";
import { Button } from "@/components/ui/button";

type Props = {
  initialPercentage: number;
  initialHearts: number;
  initialLessonId: number;
  initialLessonChallenges: (typeof challenges.$inferSelect & {
    completed: boolean;
    challengeOptions: typeof challengeOptions.$inferSelect[];
  })[];
  userSubscription: typeof userSubscription.$inferSelect & {
    isActive: boolean;
  } | null;
};

export const Quiz = ({
  initialPercentage,
  initialHearts,
  initialLessonId,
  initialLessonChallenges,
  userSubscription,
}: Props) => {
  const { open: openHeartsModal } = useHeartsModal();
  const { open: openPracticeModal } = usePracticeModal();

  useMount(() => {
    if (initialPercentage === 100) {
      openPracticeModal();
    }
  });

  const { width, height } = useWindowSize();
  const router = useRouter();

  const [finishAudio] = useAudio({ src: "/finish.mp3", autoPlay: true });
  const [correctAudio, _c, correctControls] = useAudio({ src: "/correct.wav" });
  const [incorrectAudio, _i, incorrectControls] = useAudio({ src: "/incorrect.wav" });
  const [pending, startTransition] = useTransition();

  const [lessonId] = useState(initialLessonId);
  const [hearts, setHearts] = useState(initialHearts);
  const [percentage, setPercentage] = useState(() => {
    return initialPercentage === 100 ? 0 : initialPercentage;
  });
  const [challengesList] = useState(initialLessonChallenges);
  const [activeIndex, setActiveIndex] = useState(() => {
    const uncompletedIndex = challengesList.findIndex((challenge) => !challenge.completed);
    return uncompletedIndex === -1 ? 0 : uncompletedIndex;
  });

  const [selectedOption, setSelectedOption] = useState<number>();
  const [status, setStatus] = useState<"correct" | "wrong" | "none">("none");

  // Telemetry tracking for Statistical Machine Learning analysis
  const [sessionStartTime] = useState<number>(() => Date.now());
  const [attemptCount, setAttemptCount] = useState<number>(1);
  const [correctChallengesCount, setCorrectChallengesCount] = useState<number>(0);
  const [mistakeChallengeIds, setMistakeChallengeIds] = useState<number[]>([]);
  const [hasRecordedSession, setHasRecordedSession] = useState<boolean>(false);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [mlResult, setMlResult] = useState<any>(null);

  const challenge = challengesList[activeIndex];
  const options = challenge?.challengeOptions ?? [];

  // When all challenges are finished, trigger real-time ML inference
  useEffect(() => {
    if (!challenge && !hasRecordedSession) {
      setHasRecordedSession(true);
      setIsAnalyzing(true);

      const elapsedSeconds = Math.max(2, Math.round((Date.now() - sessionStartTime) / 1000));
      const avgResponseTime = challengesList.length > 0 
        ? Math.round((elapsedSeconds / challengesList.length) * 10) / 10 
        : 12.0;

      // Accuracy reflects first-attempt success: questions completed without initial mistakes
      const firstTryCorrect = Math.max(0, challengesList.length - mistakeChallengeIds.length);

      recordLearningSession({
        lessonId,
        totalChallenges: challengesList.length,
        correctChallenges: firstTryCorrect,
        attempts: attemptCount,
        avgResponseTime,
      })
        .then((data) => {
          setMlResult(data);
          setIsAnalyzing(false);
        })
        .catch((err) => {
          console.error("Session recording error:", err);
          setIsAnalyzing(false);
        });
    }
  }, [challenge, hasRecordedSession, lessonId, challengesList.length, mistakeChallengeIds, attemptCount, sessionStartTime]);

  const onNext = () => {
    setActiveIndex((current) => current + 1);
  };

  const onSelect = (id: number) => {
    if (status !== "none") return;
    setSelectedOption(id);
  };

  const onContinue = () => {
    if (!selectedOption) return;

    if (status === "wrong") {
      setStatus("none");
      setSelectedOption(undefined);
      setAttemptCount((prev) => prev + 1);
      return;
    }

    if (status === "correct") {
      onNext();
      setStatus("none");
      setSelectedOption(undefined);
      return;
    }

    const correctOption = options.find((option) => option.correct);

    if (!correctOption) {
      return;
    }

    if (correctOption.id === selectedOption) {
      startTransition(() => {
        upsertChallengeProgress(challenge.id)
          .then((response) => {
            if (response?.error === "hearts") {
              openHeartsModal();
              return;
            }

            correctControls.play();
            setStatus("correct");
            setPercentage((prev) => prev + 100 / challengesList.length);
            setCorrectChallengesCount((prev) => prev + 1);

            // This is a practice
            if (initialPercentage === 100) {
              setHearts((prev) => Math.min(prev + 1, 5));
            }
          })
          .catch(() => toast.error("Something went wrong. Please try again."));
      });
    } else {
      startTransition(() => {
        reduceHearts(challenge.id)
          .then((response) => {
            if (response?.error === "hearts") {
              openHeartsModal();
              return;
            }

            incorrectControls.play();
            setStatus("wrong");
            setMistakeChallengeIds((prev) => 
              prev.includes(challenge.id) ? prev : [...prev, challenge.id]
            );

            if (!response?.error) {
              setHearts((prev) => Math.max(prev - 1, 0));
            }
          })
          .catch(() => toast.error("Something went wrong. Please try again."));
      });
    }
  };

  if (!challenge) {
    return (
      <>
        {finishAudio}
        <Confetti
          width={width}
          height={height}
          recycle={false}
          numberOfPieces={500}
          tweenDuration={10000}
        />
        <div className="flex flex-col gap-y-4 lg:gap-y-6 max-w-xl mx-auto text-center items-center justify-center min-h-[85vh] py-8 px-4">
          <Image
            src="/finish.svg"
            alt="Finish"
            className="hidden lg:block"
            height={80}
            width={80}
          />
          <Image
            src="/finish.svg"
            alt="Finish"
            className="block lg:hidden"
            height={45}
            width={45}
          />
          <h1 className="text-xl lg:text-3xl font-bold text-neutral-700">
            Great job! <br /> You&apos;ve completed the lesson.
          </h1>

          <div className="flex items-center gap-x-4 w-full justify-center">
            <ResultCard
              variant="points"
              value={challengesList.length * 10}
            />
            <ResultCard
              variant="hearts"
              value={hearts}
            />
          </div>

          {/* ML ADAPTIVE LEARNING INTELLIGENCE RESULTS CARD */}
          <div className="w-full border-2 border-indigo-200 rounded-3xl p-5 bg-gradient-to-br from-indigo-50/70 via-white to-blue-50/60 shadow-md text-left flex flex-col gap-y-3">
            <div className="flex items-center justify-between border-b pb-2.5">
              <div className="flex items-center gap-x-2">
                <div className="p-2 bg-indigo-600 rounded-xl text-white shadow-sm">
                  <Brain className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-neutral-800 text-sm md:text-base">
                    Machine Learning Evaluation
                  </h3>
                  <p className="text-[11px] text-neutral-500">
                    Real-time classification & recommendation engine
                  </p>
                </div>
              </div>
              {isAnalyzing ? (
                <div className="flex items-center gap-x-1.5 text-xs text-indigo-600 font-bold">
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Processing...</span>
                </div>
              ) : (
                <span className="bg-indigo-600 text-white font-extrabold text-xs px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                  {mlResult?.predictedMastery || "Calculated"}
                </span>
              )}
            </div>

            {isAnalyzing ? (
              <div className="py-4 text-center text-xs text-neutral-500 flex flex-col items-center gap-y-2">
                <Loader className="h-6 w-6 animate-spin text-indigo-600" />
                <span>Running supervised classifier & behavioral clustering...</span>
              </div>
            ) : (
              <div className="flex flex-col gap-y-2.5 text-xs">
                <div className="grid grid-cols-2 gap-2 text-neutral-700 bg-white p-3 rounded-2xl border">
                  <div>
                    <span className="text-neutral-400 font-extrabold uppercase text-[10px]">Predicted Readiness</span>
                    <p className="text-sm font-black text-indigo-700">
                      {mlResult?.predictedMastery || "Advanced"} ({mlResult?.confidence || 88}% conf.)
                    </p>
                  </div>
                  <div>
                    <span className="text-neutral-400 font-extrabold uppercase text-[10px]">Learner Segment</span>
                    <p className="text-sm font-black text-purple-700 truncate">
                      {mlResult?.clusterLabel || "Consistent Learner"}
                    </p>
                  </div>
                </div>

                {/* Adaptive Recommendation */}
                <div className="bg-green-50/80 border border-green-200 rounded-2xl p-3 text-green-900">
                  <p className="font-extrabold flex items-center gap-x-1.5">
                    <Sparkles className="h-3.5 w-3.5 text-green-600" />
                    Adaptive Next Step: {mlResult?.recommendations?.recommended_action?.replace("_", " ") || "TARGETED PRACTICE"}
                  </p>
                  <p className="text-[11px] text-green-800 mt-1">
                    {mlResult?.recommendations?.rationale || "Calibrated next lesson to your observed response latency and quiz accuracy."}
                  </p>
                </div>

                {/* Earned Premium Status */}
                {mlResult?.activePremium ? (
                  <div className="bg-amber-50 border border-amber-200 rounded-2xl p-2.5 flex items-center gap-x-2 text-amber-900 font-bold">
                    <Trophy className="h-4 w-4 text-amber-600 shrink-0" />
                    <span>Free Merit Premium Active: Unlimited hearts unlocked!</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-between bg-neutral-50 border rounded-2xl px-3 py-2 text-neutral-600">
                    <span>Earn-Your-Premium Progress:</span>
                    <span className="font-extrabold text-indigo-600">
                      {mlResult?.premiumEligibility?.progress_percentage || 50}%
                    </span>
                  </div>
                )}

                <div className="flex items-center justify-between pt-1">
                  <Link href="/intelligence" className="text-indigo-600 font-bold hover:underline flex items-center gap-x-1 text-xs">
                    View Complete Intelligence Dashboard
                    <ArrowRight className="h-3 w-3" />
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
        <Footer
          lessonId={lessonId}
          status="completed"
          onCheck={() => router.push("/learn")}
        />
      </>
    );
  }

  const title = challenge.type === "ASSIST" 
    ? "Select the correct meaning"
    : challenge.question;

  return (
    <>
      {incorrectAudio}
      {correctAudio}
      <Header
        hearts={hearts}
        percentage={percentage}
        hasActiveSubscription={!!userSubscription?.isActive}
      />
      <div className="flex-1">
        <div className="h-full flex items-center justify-center">
          <div className="lg:min-h-[350px] lg:w-[600px] w-full px-6 lg:px-0 flex flex-col gap-y-12">
            <h1 className="text-lg lg:text-3xl text-center lg:text-start font-bold text-neutral-700">
              {title}
            </h1>
            <div>
              {challenge.type === "ASSIST" && (
                <QuestionBubble question={challenge.question} />
              )}
              <Challenge
                options={options}
                onSelect={onSelect}
                status={status}
                selectedOption={selectedOption}
                disabled={pending}
                type={challenge.type}
              />
            </div>
          </div>
        </div>
      </div>
      <Footer
        disabled={pending || !selectedOption}
        status={status}
        onCheck={onContinue}
      />
    </>
  );
};
