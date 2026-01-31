import { NextResponse } from "next/server";
import { buildAccountSnapshot } from "@/src/server/account-snapshot";
import { corsPreflight, applyCorsHeaders } from "@/src/server/cors";
import { verifyExtensionAccessToken } from "@/src/server/extension-auth";
import { internalApiJson } from "@/src/server/internal-api";

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
  if (!token) {
    return applyCorsHeaders(
      request,
      NextResponse.json(buildAccountSnapshot({ user: null })),
      CORS_OPTIONS
    );
  }

  const payload = verifyExtensionAccessToken(token);
  if (!payload) {
    return applyCorsHeaders(
      request,
      NextResponse.json(
        { code: "auth", message: "Unauthorized", retryable: false },
        { status: 401 }
      ),
      CORS_OPTIONS
    );
  }

  try {
    const { user } = await internalApiJson<{
      user: {
        id: string;
        email: string | null;
        name: string | null;
        imageUrl: string | null;
        createdAt: string;
      } | null;
    }>(`/api/internal/users/${encodeURIComponent(payload.sub)}`, { method: "GET" });

    if (!user) {
      return applyCorsHeaders(
        request,
        NextResponse.json(buildAccountSnapshot({ user: null })),
        CORS_OPTIONS
      );
    }

    return applyCorsHeaders(
      request,
      NextResponse.json(
        buildAccountSnapshot({
          user: {
            ...user,
            createdAt: new Date(user.createdAt)
          },
          accessToken: token,
          expiresAt: new Date(payload.exp * 1000).toISOString()
        })
      ),
      CORS_OPTIONS
    );
  } catch (error) {
    return applyCorsHeaders(
      request,
      NextResponse.json({ error: "internal_error" }, { status: 500 }),
      CORS_OPTIONS
    );
  }
}
