import { NextResponse } from "next/server";
import { corsPreflight, applyCorsHeaders } from "@/src/server/cors";
import { verifyExtensionAccessToken } from "@/src/server/extension-auth";

export const runtime = "nodejs";

const CORS_OPTIONS = { methods: ["GET"] } as const;

function getBearerToken(headers: Headers): string | null {
  const auth = headers.get("authorization") ?? headers.get("Authorization");
  if (!auth) return null;
  const [scheme, token] = auth.split(" ");
  if (scheme !== "Bearer" || !token) return null;
  return token;
}

export async function OPTIONS(request: Request) {
  return corsPreflight(request, CORS_OPTIONS);
}

export async function GET(request: Request) {
  const token = getBearerToken(request.headers);
  if (!token || !verifyExtensionAccessToken(token)) {
    return applyCorsHeaders(
      request,
      NextResponse.json(
        { code: "auth", message: "Unauthorized", retryable: false },
        { status: 401 }
      ),
      CORS_OPTIONS
    );
  }

  return applyCorsHeaders(request, NextResponse.json({ state: "none" }), CORS_OPTIONS);
}
