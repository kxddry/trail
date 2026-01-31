import { NextResponse } from "next/server";
import { corsPreflight, applyCorsHeaders } from "@/src/server/cors";
import { listPlans } from "@/src/server/account-snapshot";

export const runtime = "nodejs";

const CORS_OPTIONS = { methods: ["GET"] } as const;

export async function OPTIONS(request: Request) {
  return corsPreflight(request, CORS_OPTIONS);
}

export async function GET(request: Request) {
  return applyCorsHeaders(request, NextResponse.json(listPlans()), CORS_OPTIONS);
}
