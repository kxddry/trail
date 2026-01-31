import { randomBytes } from "crypto";
import { NextResponse } from "next/server";
import { corsPreflight, applyCorsHeaders } from "@/src/server/cors";
import { internalApiJson } from "@/src/server/internal-api";

export const runtime = "nodejs";

const CORS_OPTIONS = { methods: ["POST"] } as const;

const SESSION_TTL_MS = 5 * 60 * 1000;

function createSessionId() {
  return randomBytes(16).toString("hex");
}

export async function OPTIONS(request: Request) {
  return corsPreflight(request, CORS_OPTIONS);
}

export async function POST(request: Request) {
  const appBaseUrl = process.env.APP_BASE_URL ?? "https://app.gettrail.net";

  let sessionId = createSessionId();
  try {
    for (let attempt = 0; attempt < 3; attempt += 1) {
      const { exists } = await internalApiJson<{ exists: boolean }>(
        "/api/internal/extension/code-exists",
        {
          method: "POST",
          body: { code: sessionId }
        }
      );
      if (!exists) {
        break;
      }
      sessionId = createSessionId();
    }
  } catch (error) {
    return applyCorsHeaders(
      request,
      NextResponse.json({ error: "internal_error" }, { status: 500 }),
      CORS_OPTIONS
    );
  }

  const expiresAt = new Date(Date.now() + SESSION_TTL_MS);

  return applyCorsHeaders(
    request,
    NextResponse.json({
      id: sessionId,
      url: `${appBaseUrl.replace(/\/$/, "")}/extension?code=${sessionId}`,
      expiresAt: expiresAt.toISOString(),
      pollIntervalMs: 1500
    }),
    CORS_OPTIONS
  );
}
