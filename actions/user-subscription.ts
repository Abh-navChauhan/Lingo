"use server";

import { auth } from "@clerk/nextjs/server";
import { revalidatePath } from "next/cache";
import { eq } from "drizzle-orm";

import db from "@/db/drizzle";
import { userEarnedPremium } from "@/db/schema";
import { getUserEarnedPremium } from "@/db/queries";

export const claimEarnedPremium = async () => {
  const { userId } = await auth();

  if (!userId) {
    throw new Error("Unauthorized");
  }

  const current = await getUserEarnedPremium();

  if (!current || !current.isEligible) {
    return { error: "not_eligible" };
  }

  const durationDays = current.tier === "7_DAY_LEGENDARY_PASS" ? 7 : 3;
  const now = new Date();
  const expiresAt = new Date(now.getTime() + durationDays * 24 * 60 * 60 * 1000);

  await db.update(userEarnedPremium).set({
    unlockedAt: now,
    expiresAt: expiresAt,
  }).where(eq(userEarnedPremium.userId, userId));

  revalidatePath("/shop");
  revalidatePath("/learn");
  revalidatePath("/quests");
  revalidatePath("/leaderboard");
  revalidatePath("/intelligence");

  return { success: true, expiresAt };
};
