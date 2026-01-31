import { NextResponse } from "next/server";

export type CorsOptions = {
  methods: string[];
  maxAgeSeconds?: number;
};

function splitOrigins(raw: string | undefined | null): string[] {
  if (!raw) return [];
  return raw
    .split(/[,\s]+/)
    .map((value) => value.trim())
    .filter(Boolean);
}

function getAllowedOrigins(): string[] {
  // Prefer a dedicated var for the extension, but keep a generic fallback.
  const raw = process.env.TRAIL_EXTENSION_ORIGINS ?? process.env.TRAIL_CORS_ORIGINS;
  return splitOrigins(raw);
}

function isOriginAllowed(origin: string): boolean {
  const allowlist = getAllowedOrigins();
  if (allowlist.length === 0) return false;
  return allowlist.includes(origin);
}

function appendVary(headers: Headers, value: string) {
  const current = headers.get("Vary");
  if (!current) {
    headers.set("Vary", value);
    return;
  }
  const parts = current
    .split(",")
    .map((v) => v.trim().toLowerCase())
    .filter(Boolean);
  if (parts.includes(value.toLowerCase())) return;
  headers.set("Vary", `${current}, ${value}`);
}

export function applyCorsHeaders(
  request: Request,
  response: NextResponse,
  options: CorsOptions
): NextResponse {
  const origin = request.headers.get("Origin") ?? request.headers.get("origin");
  if (!origin) return response;
  if (!isOriginAllowed(origin)) return response;

  response.headers.set("Access-Control-Allow-Origin", origin);
  appendVary(response.headers, "Origin");

  const methods = [...new Set([...options.methods, "OPTIONS"])].join(", ");
  response.headers.set("Access-Control-Allow-Methods", methods);

  const requestedHeaders =
    request.headers.get("Access-Control-Request-Headers") ??
    request.headers.get("access-control-request-headers");
  response.headers.set(
    "Access-Control-Allow-Headers",
    requestedHeaders ?? "authorization, content-type, accept"
  );

  response.headers.set(
    "Access-Control-Max-Age",
    String(options.maxAgeSeconds ?? 60 * 60 * 24)
  );

  return response;
}

export function corsPreflight(request: Request, options: CorsOptions): NextResponse {
  // Note: return 204 to keep it lightweight.
  return applyCorsHeaders(request, new NextResponse(null, { status: 204 }), options);
}
