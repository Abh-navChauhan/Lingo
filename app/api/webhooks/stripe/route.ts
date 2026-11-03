import { NextResponse } from "next/server";

export async function POST() {
  return new NextResponse(
    JSON.stringify({ message: "Stripe payments disabled. Merit-based 'Earn Your Premium' active." }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
