import { NextResponse } from "next/server";
import { buildAccountSnapshot } from "@/src/server/account-snapshot";
import { corsPreflight, applyCorsHeaders } from "@/src/server/cors";
import { createExtensionAccessToken } from "@/src/server/extension-auth";
import { internalApiJson } from "@/src/server/internal-api";

export const runtime = "nodejs";

const CORS_OPTIONS = { methods: ["GET"] } as const;

export async function OPTIONS(
  request: Request,
  _context: { params: Promise<{ id: string }> }
) {
  return corsPreflight(request, CORS_OPTIONS);
}

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: sessionId } = await params;
  if (!sessionId) {
    return applyCorsHeaders(request, NextResponse.json({ status: "expired" }), CORS_OPTIONS);
  }

  let response: {
    status: "pending" | "expired" | "approved";
    user?: {
      id: string;
      email: string | null;
      name: string | null;
      imageUrl: string | null;
      createdAt: string;
    };
  };

  try {
    response = await internalApiJson(
      `/api/internal/extension/portal/${encodeURIComponent(sessionId)}`,
      { method: "GET" }
    );
  } catch (error) {
    return applyCorsHeaders(
      request,
      NextResponse.json({ error: "internal_error" }, { status: 500 }),
      CORS_OPTIONS
    );
  }

  if (response.status !== "approved") {
    return applyCorsHeaders(
      request,
      NextResponse.json({ status: response.status }),
      CORS_OPTIONS
    );
  }

  if (!response.user) {
    return applyCorsHeaders(request, NextResponse.json({ status: "expired" }), CORS_OPTIONS);
  }

  const token = createExtensionAccessToken(response.user.id);

  return applyCorsHeaders(
    request,
    NextResponse.json({
      status: "approved",
      snapshot: buildAccountSnapshot({
        user: {
          ...response.user,
          createdAt: new Date(response.user.createdAt)
        },
        accessToken: token.token,
        expiresAt: token.expiresAt
      })
    }),
    CORS_OPTIONS
  );
}
