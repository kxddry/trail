import { NextResponse } from "next/server";
import { corsPreflight, applyCorsHeaders } from "@/src/server/cors";

export const runtime = "nodejs";

const CORS_OPTIONS = { methods: ["POST"] } as const;

export async function OPTIONS(request: Request) {
  return corsPreflight(request, CORS_OPTIONS);
}

export async function POST(request: Request) {
  return applyCorsHeaders(request, new NextResponse(null, { status: 204 }), CORS_OPTIONS);
}
