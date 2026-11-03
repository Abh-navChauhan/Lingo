import "dotenv/config";
import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";
import { eq, inArray } from "drizzle-orm";

import * as schema from "../db/schema";

const sql = neon(process.env.DATABASE_URL!);
// @ts-ignore
const db = drizzle(sql, { schema });

const main = async () => {
  try {
    console.log("Checking and seeding missing challenge options for Lesson 2 and beyond...");

    // 1. Check existing challenge options for challenges 4, 5, 6
    const existingOptions = await db.query.challengeOptions.findMany({
      where: inArray(schema.challengeOptions.challengeId, [4, 5, 6]),
    });

    console.log(`Found ${existingOptions.length} existing options for challenges 4, 5, 6.`);

    if (existingOptions.length === 0) {
      console.log("Inserting missing challenge options for Lesson 2 (challenges 4, 5, 6)...");

      await db.insert(schema.challengeOptions).values([
        // Challenge 4: Which one of these is "the man"? (SELECT)
        {
          challengeId: 4,
          imageSrc: "/man.svg",
          correct: true,
          text: "el hombre",
          audioSrc: "/es_man.mp3",
        },
        {
          challengeId: 4,
          imageSrc: "/woman.svg",
          correct: false,
          text: "la mujer",
          audioSrc: "/es_woman.mp3",
        },
        {
          challengeId: 4,
          imageSrc: "/robot.svg",
          correct: false,
          text: "el robot",
          audioSrc: "/es_robot.mp3",
        },

        // Challenge 5: "the man" (ASSIST)
        {
          challengeId: 5,
          correct: true,
          text: "el hombre",
          audioSrc: "/es_man.mp3",
        },
        {
          challengeId: 5,
          correct: false,
          text: "la mujer",
          audioSrc: "/es_woman.mp3",
        },
        {
          challengeId: 5,
          correct: false,
          text: "el robot",
          audioSrc: "/es_robot.mp3",
        },

        // Challenge 6: Which one of these is "the robot"? (SELECT)
        {
          challengeId: 6,
          imageSrc: "/man.svg",
          correct: false,
          text: "el hombre",
          audioSrc: "/es_man.mp3",
        },
        {
          challengeId: 6,
          imageSrc: "/woman.svg",
          correct: false,
          text: "la mujer",
          audioSrc: "/es_woman.mp3",
        },
        {
          challengeId: 6,
          imageSrc: "/robot.svg",
          correct: true,
          text: "el robot",
          audioSrc: "/es_robot.mp3",
        },
      ]);

      console.log("[OK] Successfully inserted 9 challenge options for Lesson 2!");
    } else {
      console.log("Challenge options for Lesson 2 already exist.");
    }

    // 2. Check if Lessons 3, 4, 5 have challenges
    const existingL3Challenges = await db.query.challenges.findMany({
      where: inArray(schema.challenges.lessonId, [3, 4, 5]),
    });

    if (existingL3Challenges.length === 0) {
      console.log("Seeding challenges and options for Lessons 3, 4, 5...");

      // Challenges for Lesson 3
      await db.insert(schema.challenges).values([
        {
          id: 7,
          lessonId: 3,
          type: "SELECT",
          order: 1,
          question: 'Which one of these is "the woman"?',
        },
        {
          id: 8,
          lessonId: 3,
          type: "ASSIST",
          order: 2,
          question: '"the woman"',
        },
        {
          id: 9,
          lessonId: 3,
          type: "SELECT",
          order: 3,
          question: 'Which one of these is "the robot"?',
        },
      ]);

      await db.insert(schema.challengeOptions).values([
        { challengeId: 7, imageSrc: "/woman.svg", correct: true, text: "la mujer", audioSrc: "/es_woman.mp3" },
        { challengeId: 7, imageSrc: "/man.svg", correct: false, text: "el hombre", audioSrc: "/es_man.mp3" },
        { challengeId: 7, imageSrc: "/robot.svg", correct: false, text: "el robot", audioSrc: "/es_robot.mp3" },

        { challengeId: 8, correct: true, text: "la mujer", audioSrc: "/es_woman.mp3" },
        { challengeId: 8, correct: false, text: "el hombre", audioSrc: "/es_man.mp3" },
        { challengeId: 8, correct: false, text: "el robot", audioSrc: "/es_robot.mp3" },

        { challengeId: 9, imageSrc: "/robot.svg", correct: true, text: "el robot", audioSrc: "/es_robot.mp3" },
        { challengeId: 9, imageSrc: "/woman.svg", correct: false, text: "la mujer", audioSrc: "/es_woman.mp3" },
        { challengeId: 9, imageSrc: "/man.svg", correct: false, text: "el hombre", audioSrc: "/es_man.mp3" },
      ]);

      console.log("[OK] Successfully seeded challenges and options for Lesson 3!");
    }

    console.log("Done verifying curriculum content.");
  } catch (error) {
    console.error("Error updating challenges/options:", error);
  }
};

main();

