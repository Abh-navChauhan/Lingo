"use client";

import { toast } from "sonner";
import Image from "next/image";
import Link from "next/link";
import { useTransition } from "react";
import { Sparkles, Trophy, Brain, CheckCircle2, ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { POINTS_TO_REFILL } from "@/constants";
import { refillHearts } from "@/actions/user-progress";
import { claimEarnedPremium } from "@/actions/user-subscription";
import { userEarnedPremium } from "@/db/schema";

type Props = {
  hearts: number;
  points: number;
  hasActiveSubscription: boolean;
  earnedPremium: typeof userEarnedPremium.$inferSelect | null;
};

export const Items = ({
  hearts,
  points,
  hasActiveSubscription,
  earnedPremium,
}: Props) => {
  const [pending, startTransition] = useTransition();

  const onRefillHearts = () => {
    if (pending || hearts === 5 || points < POINTS_TO_REFILL) {
      return;
    }

    startTransition(() => {
      refillHearts()
        .then(() => toast.success("Hearts refilled!"))
        .catch(() => toast.error("Something went wrong"));
    });
  };

  const onClaimPremium = () => {
    startTransition(() => {
      claimEarnedPremium()
        .then((res) => {
          if (res?.error) {
            toast.error("You have not yet reached the required mastery criteria.");
          } else {
            toast.success("Congratulations! Earned Premium access unlocked!");
          }
        })
        .catch(() => toast.error("Failed to activate premium pass."));
    });
  };

  const progressPct = earnedPremium?.progressPercentage || 40;
  const predictedMastery = earnedPremium?.predictedMastery || "Beginner";
  const isEligible = !!earnedPremium?.isEligible;
  const expiresAt = earnedPremium?.expiresAt;
  const daysRemaining = expiresAt
    ? Math.max(0, Math.ceil((new Date(expiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    : 0;

  return (
    <ul className="w-full flex flex-col gap-y-6">
      {/* 1. Heart Refill with Points */}
      <div className="flex items-center w-full p-4 gap-x-4 border-2 rounded-2xl bg-white shadow-sm">
        <Image 
          src="/heart.svg"
          alt="Heart"
          height={60}
          width={60}
        />
        <div className="flex-1">
          <p className="text-neutral-700 text-base lg:text-xl font-bold">
            Refill hearts
          </p>
          <p className="text-muted-foreground text-sm">
            Use your earned study points to top up hearts.
          </p>
        </div>
        <Button
          onClick={onRefillHearts}
          disabled={pending || hearts === 5 || points < POINTS_TO_REFILL}
        >
          {hearts === 5 ? (
            "full"
          ) : (
            <div className="flex items-center gap-x-1">
              <Image
                src="/points.svg"
                alt="Points"
                height={20}
                width={20}
              />
              <p>{POINTS_TO_REFILL}</p>
            </div>
          )}
        </Button>
      </div>

      {/* 2. Merit-Based 'Earn Your Premium' Card */}
      <div className="w-full p-6 border-2 border-indigo-200 rounded-3xl bg-gradient-to-b from-indigo-50/60 to-white shadow-sm flex flex-col gap-y-4">
        <div className="flex items-start justify-between gap-x-4">
          <div className="flex items-center gap-x-3">
            <div className="p-3 bg-indigo-500 rounded-2xl text-white shadow-md">
              <Sparkles className="h-7 w-7" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-neutral-800 flex items-center gap-x-2">
                Merit Premium Pass
                {hasActiveSubscription && (
                  <span className="text-xs bg-green-500 text-white font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                    Active
                  </span>
                )}
              </h2>
              <p className="text-sm text-neutral-500">
                100% Free · Powered by Statistical Machine Learning
              </p>
            </div>
          </div>
          <Image
            src="/unlimited.svg"
            alt="Unlimited"
            height={50}
            width={50}
          />
        </div>

        {/* Status display */}
        {hasActiveSubscription ? (
          <div className="bg-green-50 border border-green-200 rounded-2xl p-4 flex flex-col gap-y-2">
            <div className="flex items-center gap-x-2 text-green-800 font-bold">
              <Trophy className="h-5 w-5 text-yellow-500" />
              <span>{earnedPremium?.tier || "Legendary Pass"} Active</span>
            </div>
            <p className="text-sm text-green-700">
              {daysRemaining} days remaining · Full Unlimited Hearts & Adaptive AI challenges unlocked.
            </p>
            <p className="text-xs text-neutral-500 italic">
              {earnedPremium?.unlockedReason || "Unlocked via proven machine learning performance."}
            </p>
          </div>
        ) : isEligible ? (
          <div className="bg-indigo-100/70 border border-indigo-300 rounded-2xl p-4 flex flex-col gap-y-3">
            <div className="flex items-center gap-x-2 text-indigo-900 font-bold">
              <CheckCircle2 className="h-5 w-5 text-indigo-600" />
              <span>You have qualified for free Premium!</span>
            </div>
            <p className="text-sm text-indigo-700">
              Your predicted mastery level is <span className="font-bold underline">{predictedMastery}</span>. Click below to activate your merit challenge pass immediately.
            </p>
            <Button
              onClick={onClaimPremium}
              disabled={pending}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold tracking-wide w-full"
            >
              Claim My Free Premium Pass
            </Button>
          </div>
        ) : (
          <div className="flex flex-col gap-y-3">
            <div className="flex items-center justify-between text-sm font-bold text-neutral-700">
              <span>Progress towards Unlocking:</span>
              <span className="text-indigo-600">{progressPct}%</span>
            </div>
            <div className="w-full bg-neutral-200 h-3 rounded-full overflow-hidden">
              <div 
                className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              />
            </div>
            <div className="bg-white border rounded-xl p-3 text-xs text-neutral-600 flex flex-col gap-y-1.5">
              <p className="font-bold text-neutral-800">Qualification Benchmarks:</p>
              <div className="flex items-center gap-x-2">
                <span className={predictedMastery !== "Beginner" ? "text-green-600 font-bold" : "text-neutral-400"}>
                  {predictedMastery !== "Beginner" ? "✓" : "○"}
                </span>
                <span>ML Predicted Mastery: <strong>{predictedMastery}</strong> (Intermediate or Advanced required)</span>
              </div>
              <div className="flex items-center gap-x-2">
                <span className="text-neutral-400">○</span>
                <span>Maintain &gt;= 70% quiz accuracy over 3+ completed lessons</span>
              </div>
              <div className="flex items-center gap-x-2">
                <span className="text-neutral-400">○</span>
                <span>Demonstrate active learning consistency</span>
              </div>
            </div>
          </div>
        )}

        {/* Benefits List */}
        <div className="border-t pt-3 flex flex-col gap-y-2">
          <p className="text-xs uppercase font-extrabold text-neutral-400 tracking-wider">
            Benefits You Can Earn:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-neutral-700">
            <div className="flex items-center gap-x-2">
              <span className="text-green-600 font-bold">✓</span>
              <span>Unlimited Hearts & practice</span>
            </div>
            <div className="flex items-center gap-x-2">
              <span className="text-green-600 font-bold">✓</span>
              <span>Personalised ML review drills</span>
            </div>
            <div className="flex items-center gap-x-2">
              <span className="text-green-600 font-bold">✓</span>
              <span>Legendary Challenge modules</span>
            </div>
            <div className="flex items-center gap-x-2">
              <span className="text-green-600 font-bold">✓</span>
              <span>Zero paywalls or subscriptions</span>
            </div>
          </div>
        </div>

        <Link href="/intelligence">
          <Button variant="ghost" className="w-full text-indigo-600 font-bold text-sm gap-x-2">
            <Brain className="h-4 w-4" />
            View My Learning Intelligence Dashboard
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>
    </ul>
  );
};
