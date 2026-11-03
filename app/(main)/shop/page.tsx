import Image from "next/image";
import { redirect } from "next/navigation";

import { FeedWrapper } from "@/components/feed-wrapper";
import { UserProgress } from "@/components/user-progress";
import { StickyWrapper } from "@/components/sticky-wrapper";
import { getUserProgress, getUserSubscription, getUserEarnedPremium } from "@/db/queries";

import { Items } from "./items";
import { Quests } from "@/components/quests";

const ShopPage = async () => {
  const userProgressData = getUserProgress();
  const userSubscriptionData = getUserSubscription();
  const userEarnedPremiumData = getUserEarnedPremium();

  const [
    userProgress,
    userSubscription,
    earnedPremium,
  ] = await Promise.all([
    userProgressData,
    userSubscriptionData,
    userEarnedPremiumData,
  ]);

  if (!userProgress || !userProgress.activeCourse) {
    redirect("/courses");
  }

  const isPro = !!userSubscription?.isActive;

  return ( 
    <div className="flex flex-row-reverse gap-[48px] px-6">
      <StickyWrapper>
        <UserProgress
          activeCourse={userProgress.activeCourse}
          hearts={userProgress.hearts}
          points={userProgress.points}
          hasActiveSubscription={isPro}
        />
        <Quests points={userProgress.points} />
      </StickyWrapper>
      <FeedWrapper>
        <div className="w-full flex flex-col items-center">
          <Image
            src="/shop.svg"
            alt="Earn Premium"
            height={90}
            width={90}
          />
          <h1 className="text-center font-bold text-neutral-800 text-2xl my-4">
            Earn Your Premium
          </h1>
          <p className="text-muted-foreground text-center text-base lg:text-lg mb-6 max-w-md">
            No credit card or payments required. Unlock unlimited hearts and AI learning features through demonstrated mastery and learning consistency.
          </p>
          <Items
            hearts={userProgress.hearts}
            points={userProgress.points}
            hasActiveSubscription={isPro}
            earnedPremium={earnedPremium}
          />
        </div>
      </FeedWrapper>
    </div>
  );
};
 
export default ShopPage;
