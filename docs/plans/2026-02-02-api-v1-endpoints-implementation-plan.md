# API v1 Endpoints Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement API v1 endpoints under `apps/api/app/v1` to match the public OpenAPI contract for devices, account settings, trails, account snapshot, and billing endpoints, with comprehensive Vitest coverage.

**Architecture:** Next.js route handlers use existing auth helpers and services, direct Prisma access where needed, and consistent JSON responses via `jsonNoStore`/`jsonError`. Enum/date mappings are localized per route for clarity.

**Tech Stack:** Next.js App Router (route handlers), Prisma (`@trail/db`), Vitest, Auth helpers.

---

### Task 1: Devices Endpoints (claim, list, revoke)

**Files:**
- Create: `apps/api/app/v1/devices/claim/route.ts`
- Create: `apps/api/app/v1/devices/route.ts`
- Create: `apps/api/app/v1/devices/[id]/revoke/route.ts`
- Create: `apps/api/app/v1/__tests__/devices.test.ts`

**Step 1: Write the failing test**
```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const authMocks = vi.hoisted(() => ({
  verifyUserToken: vi.fn(),
  verifyExtensionToken: vi.fn()
}));

const userMocks = vi.hoisted(() => ({
  ensureUser: vi.fn(),
  getUserById: vi.fn()
}));

const deviceMocks = vi.hoisted(() => ({
  claimDevice: vi.fn(),
  listDevices: vi.fn()
}));

const dbMocks = vi.hoisted(() => ({
  db: {
    device: {
      findUnique: vi.fn(),
      update: vi.fn()
    },
    deviceSession: {
      updateMany: vi.fn()
    }
  }
}));

vi.mock("@/src/server/auth/user-auth", () => ({
  ...authMocks
}));

vi.mock("@/src/server/auth/extension-auth", () => ({
  ...authMocks
}));

vi.mock("@/src/server/user", () => ({
  ...userMocks
}));

vi.mock("@/src/server/devices", () => ({
  ...deviceMocks
}));

vi.mock("@trail/db", () => ({
  ...dbMocks
}));

import { POST as claimDevice } from "../devices/claim/route";
import { GET as listDevices } from "../devices/route";
import { POST as revokeDevice } from "../devices/[id]/revoke/route";

describe("v1 devices endpoints", () => {
  beforeEach(() => {
    authMocks.verifyUserToken.mockReset();
    authMocks.verifyExtensionToken.mockReset();
    userMocks.ensureUser.mockReset();
    userMocks.getUserById.mockReset();
    deviceMocks.claimDevice.mockReset();
    deviceMocks.listDevices.mockReset();
    dbMocks.db.device.findUnique.mockReset();
    dbMocks.db.device.update.mockReset();
    dbMocks.db.deviceSession.updateMany.mockReset();
  });

  it("claims a device via extension auth", async () => {
    authMocks.verifyExtensionToken.mockReturnValue({ sub: "user-1", iat: 0, exp: 999999 });
    userMocks.getUserById.mockResolvedValue({
      id: "user-1",
      email: "user@test.com",
      name: "Test User",
      imageUrl: null,
      createdAt: new Date("2026-01-01T00:00:00Z")
    });
    deviceMocks.claimDevice.mockResolvedValue({
      device: {
        id: "device-1",
        userId: "user-1",
        status: "ACTIVE",
        deviceName: "MacBook",
        os: "macOS",
        locale: "en-US",
        timezone: "UTC",
        browserName: "Chrome",
        browserVersion: "121",
        extensionVersion: "1.0.0",
        lastSeenAt: new Date("2026-02-02T00:00:00Z"),
        createdAt: new Date("2026-02-01T00:00:00Z"),
        updatedAt: new Date("2026-02-02T00:00:00Z")
      },
      session: {
        id: "session-1",
        deviceId: "device-1",
        userId: "user-1",
        createdAt: new Date("2026-02-02T00:00:00Z"),
        updatedAt: new Date("2026-02-02T00:00:00Z"),
        expiresAt: new Date("2026-03-03T00:00:00Z"),
        lastSeenAt: new Date("2026-02-02T00:00:00Z"),
        revokedAt: null
      },
      sessionTtlDays: 30
    });

    const response = await claimDevice(
      new Request("http://localhost/v1/devices/claim", {
        method: "POST",
        headers: { Authorization: "Bearer extension-token" },
        body: JSON.stringify({
          deviceId: "device-1",
          metadata: { os: "macOS", deviceName: "MacBook" }
        })
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.device.id).toBe("device-1");
    expect(payload.session.id).toBe("session-1");
    expect(payload.sessionTtlDays).toBe(30);
  });

  it("lists devices with latest session", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    deviceMocks.listDevices.mockResolvedValue([
      {
        id: "device-1",
        userId: "user-1",
        status: "ACTIVE",
        deviceName: "MacBook",
        os: "macOS",
        locale: null,
        timezone: null,
        browserName: null,
        browserVersion: null,
        extensionVersion: null,
        lastSeenAt: null,
        createdAt: new Date("2026-02-01T00:00:00Z"),
        updatedAt: new Date("2026-02-02T00:00:00Z"),
        sessions: [
          {
            id: "session-1",
            deviceId: "device-1",
            userId: "user-1",
            createdAt: new Date("2026-02-02T00:00:00Z"),
            updatedAt: new Date("2026-02-02T00:00:00Z"),
            expiresAt: new Date("2026-03-03T00:00:00Z"),
            lastSeenAt: null,
            revokedAt: null
          }
        ]
      }
    ]);

    const response = await listDevices(
      new Request("http://localhost/v1/devices", {
        headers: { Authorization: "Bearer user-token" }
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.devices).toHaveLength(1);
    expect(payload.devices[0].session.id).toBe("session-1");
  });

  it("revokes a device and its active sessions", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    dbMocks.db.device.findUnique.mockResolvedValue({
      id: "device-1",
      userId: "user-1",
      status: "ACTIVE",
      deviceName: null,
      os: null,
      locale: null,
      timezone: null,
      browserName: null,
      browserVersion: null,
      extensionVersion: null,
      lastSeenAt: null,
      createdAt: new Date("2026-02-01T00:00:00Z"),
      updatedAt: new Date("2026-02-02T00:00:00Z")
    });
    dbMocks.db.device.update.mockResolvedValue({
      id: "device-1",
      userId: "user-1",
      status: "REVOKED",
      deviceName: null,
      os: null,
      locale: null,
      timezone: null,
      browserName: null,
      browserVersion: null,
      extensionVersion: null,
      lastSeenAt: null,
      createdAt: new Date("2026-02-01T00:00:00Z"),
      updatedAt: new Date("2026-02-02T00:00:00Z")
    });

    const response = await revokeDevice(
      new Request("http://localhost/v1/devices/device-1/revoke", {
        method: "POST",
        headers: { Authorization: "Bearer user-token" }
      }),
      { params: Promise.resolve({ id: "device-1" }) }
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.status).toBe("REVOKED");
    expect(dbMocks.db.deviceSession.updateMany).toHaveBeenCalled();
  });
});
```

**Step 2: Run test to verify it fails**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/devices.test.ts`
Expected: FAIL (routes not implemented).

**Step 3: Write minimal implementation**
```ts
// apps/api/app/v1/devices/claim/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyExtensionToken } from "@/src/server/auth/extension-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { claimDevice } from "@/src/server/devices";
import { getUserById } from "@/src/server/user";

export const runtime = "nodejs";

type DeviceMetadataInput = {
  deviceName?: string | null;
  os?: string | null;
  locale?: string | null;
  timezone?: string | null;
  browserName?: string | null;
  browserVersion?: string | null;
  extensionVersion?: string | null;
};

function asNullableString(value: unknown): string | null | undefined {
  if (value === null) return null;
  if (typeof value === "string") return value;
  return undefined;
}

function mapDevice(device: {
  id: string;
  userId: string;
  status: string;
  deviceName?: string | null;
  os?: string | null;
  locale?: string | null;
  timezone?: string | null;
  browserName?: string | null;
  browserVersion?: string | null;
  extensionVersion?: string | null;
  lastSeenAt?: Date | null;
  createdAt: Date;
  updatedAt: Date;
}) {
  return {
    id: device.id,
    userId: device.userId,
    status: device.status,
    deviceName: device.deviceName ?? null,
    os: device.os ?? null,
    locale: device.locale ?? null,
    timezone: device.timezone ?? null,
    browserName: device.browserName ?? null,
    browserVersion: device.browserVersion ?? null,
    extensionVersion: device.extensionVersion ?? null,
    lastSeenAt: device.lastSeenAt ? device.lastSeenAt.toISOString() : null,
    createdAt: device.createdAt.toISOString(),
    updatedAt: device.updatedAt.toISOString()
  };
}

function mapSession(session: {
  id: string;
  deviceId: string;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
  expiresAt: Date;
  lastSeenAt?: Date | null;
  revokedAt?: Date | null;
}) {
  return {
    id: session.id,
    deviceId: session.deviceId,
    userId: session.userId,
    createdAt: session.createdAt.toISOString(),
    updatedAt: session.updatedAt.toISOString(),
    expiresAt: session.expiresAt.toISOString(),
    lastSeenAt: session.lastSeenAt ? session.lastSeenAt.toISOString() : null,
    revokedAt: session.revokedAt ? session.revokedAt.toISOString() : null
  };
}

export async function POST(request: Request) {
  const token = getBearerToken(request.headers);
  const extension = token ? verifyExtensionToken(token) : null;
  if (!extension?.sub) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await getUserById(extension.sub);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const metadata = body?.metadata as DeviceMetadataInput | undefined;
  if (!metadata || typeof metadata !== "object") {
    return jsonError("metadata_required", "Metadata is required.", { status: 400 });
  }

  const os = typeof metadata.os === "string" ? metadata.os.trim() : "";
  if (!os) {
    return jsonError("os_required", "OS is required.", { status: 400 });
  }

  const result = await claimDevice({
    userId: user.id,
    deviceId: typeof body?.deviceId === "string" ? body.deviceId : null,
    metadata: {
      deviceName: asNullableString(metadata.deviceName),
      os,
      locale: asNullableString(metadata.locale),
      timezone: asNullableString(metadata.timezone),
      browserName: asNullableString(metadata.browserName),
      browserVersion: asNullableString(metadata.browserVersion),
      extensionVersion: asNullableString(metadata.extensionVersion)
    }
  });

  return jsonNoStore({
    device: mapDevice(result.device),
    session: mapSession(result.session),
    sessionTtlDays: result.sessionTtlDays ?? null
  });
}
```

```ts
// apps/api/app/v1/devices/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyUserToken } from "@/src/server/auth/user-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { listDevices } from "@/src/server/devices";
import { ensureUser } from "@/src/server/user";

export const runtime = "nodejs";

function mapDevice(device: {
  id: string;
  userId: string;
  status: string;
  deviceName?: string | null;
  os?: string | null;
  locale?: string | null;
  timezone?: string | null;
  browserName?: string | null;
  browserVersion?: string | null;
  extensionVersion?: string | null;
  lastSeenAt?: Date | null;
  createdAt: Date;
  updatedAt: Date;
}) {
  return {
    id: device.id,
    userId: device.userId,
    status: device.status,
    deviceName: device.deviceName ?? null,
    os: device.os ?? null,
    locale: device.locale ?? null,
    timezone: device.timezone ?? null,
    browserName: device.browserName ?? null,
    browserVersion: device.browserVersion ?? null,
    extensionVersion: device.extensionVersion ?? null,
    lastSeenAt: device.lastSeenAt ? device.lastSeenAt.toISOString() : null,
    createdAt: device.createdAt.toISOString(),
    updatedAt: device.updatedAt.toISOString()
  };
}

function mapSession(session: {
  id: string;
  deviceId: string;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
  expiresAt: Date;
  lastSeenAt?: Date | null;
  revokedAt?: Date | null;
}) {
  return {
    id: session.id,
    deviceId: session.deviceId,
    userId: session.userId,
    createdAt: session.createdAt.toISOString(),
    updatedAt: session.updatedAt.toISOString(),
    expiresAt: session.expiresAt.toISOString(),
    lastSeenAt: session.lastSeenAt ? session.lastSeenAt.toISOString() : null,
    revokedAt: session.revokedAt ? session.revokedAt.toISOString() : null
  };
}

export async function GET(request: Request) {
  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const devices = await listDevices(user.id);

  return jsonNoStore({
    devices: devices.map((device) => {
      const session = device.sessions[0];
      return {
        ...mapDevice(device),
        ...(session ? { session: mapSession(session) } : {})
      };
    })
  });
}
```

```ts
// apps/api/app/v1/devices/[id]/revoke/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyUserToken } from "@/src/server/auth/user-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { ensureUser } from "@/src/server/user";
import { db } from "@trail/db";

export const runtime = "nodejs";

function mapDevice(device: {
  id: string;
  userId: string;
  status: string;
  deviceName?: string | null;
  os?: string | null;
  locale?: string | null;
  timezone?: string | null;
  browserName?: string | null;
  browserVersion?: string | null;
  extensionVersion?: string | null;
  lastSeenAt?: Date | null;
  createdAt: Date;
  updatedAt: Date;
}) {
  return {
    id: device.id,
    userId: device.userId,
    status: device.status,
    deviceName: device.deviceName ?? null,
    os: device.os ?? null,
    locale: device.locale ?? null,
    timezone: device.timezone ?? null,
    browserName: device.browserName ?? null,
    browserVersion: device.browserVersion ?? null,
    extensionVersion: device.extensionVersion ?? null,
    lastSeenAt: device.lastSeenAt ? device.lastSeenAt.toISOString() : null,
    createdAt: device.createdAt.toISOString(),
    updatedAt: device.updatedAt.toISOString()
  };
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  if (!id) {
    return jsonError("device_not_found", "Device not found.", { status: 404 });
  }

  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const device = await db.device.findUnique({ where: { id } });
  if (!device || device.userId !== user.id) {
    return jsonError("device_not_found", "Device not found.", { status: 404 });
  }

  const now = new Date();
  const updated = await db.device.update({
    where: { id },
    data: { status: "REVOKED" }
  });

  await db.deviceSession.updateMany({
    where: { deviceId: id, revokedAt: null },
    data: { revokedAt: now }
  });

  return jsonNoStore(mapDevice(updated));
}
```

**Step 4: Run test to verify it passes**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/devices.test.ts`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/api/app/v1/devices/claim/route.ts \
  apps/api/app/v1/devices/route.ts \
  apps/api/app/v1/devices/[id]/revoke/route.ts \
  apps/api/app/v1/__tests__/devices.test.ts

git commit -m "Add devices v1 endpoints"
```

---

### Task 2: Account Settings Endpoints

**Files:**
- Create: `apps/api/app/v1/account/settings/route.ts`
- Create: `apps/api/app/v1/__tests__/account-settings.test.ts`

**Step 1: Write the failing test**
```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const authMocks = vi.hoisted(() => ({
  verifyUserToken: vi.fn()
}));

const userMocks = vi.hoisted(() => ({
  ensureUser: vi.fn()
}));

const dbMocks = vi.hoisted(() => ({
  db: {
    accountSettings: {
      findUnique: vi.fn(),
      upsert: vi.fn()
    }
  }
}));

vi.mock("@/src/server/auth/user-auth", () => ({
  ...authMocks
}));

vi.mock("@/src/server/user", () => ({
  ...userMocks
}));

vi.mock("@trail/db", () => ({
  ...dbMocks
}));

import { GET, PATCH } from "../account/settings/route";

describe("v1 account settings", () => {
  beforeEach(() => {
    authMocks.verifyUserToken.mockReset();
    userMocks.ensureUser.mockReset();
    dbMocks.db.accountSettings.findUnique.mockReset();
    dbMocks.db.accountSettings.upsert.mockReset();
  });

  it("returns default TTL when settings are missing", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    dbMocks.db.accountSettings.findUnique.mockResolvedValue(null);

    const response = await GET(
      new Request("http://localhost/v1/account/settings", {
        headers: { Authorization: "Bearer user-token" }
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.deviceSessionTtlDays).toBe(30);
  });

  it("updates device session TTL", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    dbMocks.db.accountSettings.upsert.mockResolvedValue({
      userId: "user-1",
      deviceSessionTtlDays: "DAYS_90"
    });

    const response = await PATCH(
      new Request("http://localhost/v1/account/settings", {
        method: "PATCH",
        headers: { Authorization: "Bearer user-token" },
        body: JSON.stringify({ deviceSessionTtlDays: 90 })
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.deviceSessionTtlDays).toBe(90);
  });
});
```

**Step 2: Run test to verify it fails**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/account-settings.test.ts`
Expected: FAIL (route not implemented).

**Step 3: Write minimal implementation**
```ts
// apps/api/app/v1/account/settings/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyUserToken } from "@/src/server/auth/user-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { ensureUser } from "@/src/server/user";
import { db } from "@trail/db";

export const runtime = "nodejs";

type DeviceSessionTtlDays = 7 | 30 | 90 | 180 | 365;

type DbTtl = "DAYS_7" | "DAYS_30" | "DAYS_90" | "DAYS_180" | "DAYS_365";

const TTL_TO_DB: Record<DeviceSessionTtlDays, DbTtl> = {
  7: "DAYS_7",
  30: "DAYS_30",
  90: "DAYS_90",
  180: "DAYS_180",
  365: "DAYS_365"
};

const DB_TO_TTL: Record<DbTtl, DeviceSessionTtlDays> = {
  DAYS_7: 7,
  DAYS_30: 30,
  DAYS_90: 90,
  DAYS_180: 180,
  DAYS_365: 365
};

function toApiTtl(value: DbTtl | null | undefined): DeviceSessionTtlDays {
  return DB_TO_TTL[value ?? "DAYS_30"] ?? 30;
}

function toDbTtl(value: unknown): DbTtl | null {
  if (typeof value !== "number") return null;
  return TTL_TO_DB[value as DeviceSessionTtlDays] ?? null;
}

export async function GET(request: Request) {
  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const settings = await db.accountSettings.findUnique({
    where: { userId: user.id }
  });

  return jsonNoStore({
    deviceSessionTtlDays: toApiTtl(settings?.deviceSessionTtlDays ?? null)
  });
}

export async function PATCH(request: Request) {
  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const ttl = toDbTtl(body?.deviceSessionTtlDays);
  if (!ttl) {
    return jsonError("invalid_device_session_ttl", "Invalid device session TTL.", { status: 400 });
  }

  const settings = await db.accountSettings.upsert({
    where: { userId: user.id },
    update: { deviceSessionTtlDays: ttl },
    create: { userId: user.id, deviceSessionTtlDays: ttl }
  });

  return jsonNoStore({
    deviceSessionTtlDays: toApiTtl(settings.deviceSessionTtlDays as DbTtl)
  });
}
```

**Step 4: Run test to verify it passes**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/account-settings.test.ts`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/api/app/v1/account/settings/route.ts \
  apps/api/app/v1/__tests__/account-settings.test.ts

git commit -m "Add account settings v1 endpoints"
```

---

### Task 3: Trails List + Mutations (list, update, delete, restore)

**Files:**
- Create: `apps/api/app/v1/trails/route.ts`
- Create: `apps/api/app/v1/trails/[id]/route.ts`
- Create: `apps/api/app/v1/trails/[id]/restore/route.ts`
- Create: `apps/api/app/v1/__tests__/trails.test.ts`

**Step 1: Write the failing test**
```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const authMocks = vi.hoisted(() => ({
  verifyUserToken: vi.fn()
}));

const userMocks = vi.hoisted(() => ({
  ensureUser: vi.fn()
}));

const dbMocks = vi.hoisted(() => ({
  db: {
    trail: {
      findMany: vi.fn(),
      findFirst: vi.fn(),
      update: vi.fn()
    }
  }
}));

vi.mock("@/src/server/auth/user-auth", () => ({
  ...authMocks
}));

vi.mock("@/src/server/user", () => ({
  ...userMocks
}));

vi.mock("@trail/db", () => ({
  ...dbMocks
}));

import { GET as listTrails } from "../trails/route";
import { PATCH as updateTrail, DELETE as deleteTrail } from "../trails/[id]/route";
import { POST as restoreTrail } from "../trails/[id]/restore/route";

describe("v1 trails endpoints", () => {
  beforeEach(() => {
    authMocks.verifyUserToken.mockReset();
    userMocks.ensureUser.mockReset();
    dbMocks.db.trail.findMany.mockReset();
    dbMocks.db.trail.findFirst.mockReset();
    dbMocks.db.trail.update.mockReset();
  });

  it("lists trails with pagination", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    dbMocks.db.trail.findMany.mockResolvedValue([
      {
        id: "trail-1",
        userId: "user-1",
        deviceId: "device-1",
        label: "Trail 1",
        labelSource: "USER",
        labelUpdatedAt: new Date("2026-02-01T00:00:00Z"),
        createdAt: new Date("2026-02-01T00:00:00Z"),
        updatedAt: new Date("2026-02-02T00:00:00Z"),
        savedAt: new Date("2026-02-02T00:00:00Z"),
        nodeCount: 2,
        rootUrl: null,
        rootTitle: null,
        rootFavicon: null,
        payload: { a: 1 },
        deletedAt: null
      },
      {
        id: "trail-2",
        userId: "user-1",
        deviceId: "device-1",
        label: "Trail 2",
        labelSource: "USER",
        labelUpdatedAt: new Date("2026-02-01T00:00:00Z"),
        createdAt: new Date("2026-02-01T00:00:00Z"),
        updatedAt: new Date("2026-02-01T00:00:00Z"),
        savedAt: new Date("2026-02-01T00:00:00Z"),
        nodeCount: 1,
        rootUrl: null,
        rootTitle: null,
        rootFavicon: null,
        payload: { a: 2 },
        deletedAt: null
      }
    ]);

    const response = await listTrails(
      new Request("http://localhost/v1/trails?limit=1", {
        headers: { Authorization: "Bearer user-token" }
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.items).toHaveLength(1);
    expect(payload.nextCursor).toBe("2026-02-01T00:00:00.000Z");
  });

  it("updates trail metadata", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    dbMocks.db.trail.findFirst.mockResolvedValue({
      id: "trail-1",
      userId: "user-1"
    });
    dbMocks.db.trail.update.mockResolvedValue({
      id: "trail-1",
      userId: "user-1",
      deviceId: "device-1",
      label: "Updated",
      labelSource: "USER",
      labelUpdatedAt: new Date("2026-02-02T00:00:00Z"),
      createdAt: new Date("2026-02-01T00:00:00Z"),
      updatedAt: new Date("2026-02-02T00:00:00Z"),
      savedAt: new Date("2026-02-01T00:00:00Z"),
      nodeCount: 2,
      rootUrl: null,
      rootTitle: null,
      rootFavicon: null,
      payload: { a: 1 },
      deletedAt: null
    });

    const response = await updateTrail(
      new Request("http://localhost/v1/trails/trail-1", {
        method: "PATCH",
        headers: { Authorization: "Bearer user-token" },
        body: JSON.stringify({ label: "Updated", labelSource: "user" })
      }),
      { params: Promise.resolve({ id: "trail-1" }) }
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.label).toBe("Updated");
    expect(payload.labelSource).toBe("user");
  });

  it("soft deletes a trail", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    dbMocks.db.trail.findFirst.mockResolvedValue({ id: "trail-1", userId: "user-1" });
    dbMocks.db.trail.update.mockResolvedValue({
      id: "trail-1",
      userId: "user-1",
      deviceId: "device-1",
      label: "Trail",
      labelSource: "USER",
      labelUpdatedAt: new Date("2026-02-01T00:00:00Z"),
      createdAt: new Date("2026-02-01T00:00:00Z"),
      updatedAt: new Date("2026-02-02T00:00:00Z"),
      savedAt: new Date("2026-02-01T00:00:00Z"),
      nodeCount: 2,
      rootUrl: null,
      rootTitle: null,
      rootFavicon: null,
      payload: { a: 1 },
      deletedAt: new Date("2026-02-02T00:00:00Z")
    });

    const response = await deleteTrail(
      new Request("http://localhost/v1/trails/trail-1", {
        method: "DELETE",
        headers: { Authorization: "Bearer user-token" }
      }),
      { params: Promise.resolve({ id: "trail-1" }) }
    );

    const payload = await response.json();
    expect(payload.deletedAt).toBe("2026-02-02T00:00:00.000Z");
  });

  it("restores a trail", async () => {
    authMocks.verifyUserToken.mockResolvedValue({ sub: "auth0|1" });
    userMocks.ensureUser.mockResolvedValue({ id: "user-1" });
    dbMocks.db.trail.findFirst.mockResolvedValue({ id: "trail-1", userId: "user-1" });
    dbMocks.db.trail.update.mockResolvedValue({
      id: "trail-1",
      userId: "user-1",
      deviceId: "device-1",
      label: "Trail",
      labelSource: "USER",
      labelUpdatedAt: new Date("2026-02-01T00:00:00Z"),
      createdAt: new Date("2026-02-01T00:00:00Z"),
      updatedAt: new Date("2026-02-02T00:00:00Z"),
      savedAt: new Date("2026-02-01T00:00:00Z"),
      nodeCount: 2,
      rootUrl: null,
      rootTitle: null,
      rootFavicon: null,
      payload: { a: 1 },
      deletedAt: null
    });

    const response = await restoreTrail(
      new Request("http://localhost/v1/trails/trail-1/restore", {
        method: "POST",
        headers: { Authorization: "Bearer user-token" }
      }),
      { params: Promise.resolve({ id: "trail-1" }) }
    );

    const payload = await response.json();
    expect(payload.deletedAt).toBeNull();
  });
});
```

**Step 2: Run test to verify it fails**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/trails.test.ts`
Expected: FAIL (routes not implemented).

**Step 3: Write minimal implementation**
```ts
// apps/api/app/v1/trails/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyUserToken } from "@/src/server/auth/user-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { ensureUser } from "@/src/server/user";
import { db } from "@trail/db";

export const runtime = "nodejs";

type ApiLabelSource = "user" | "auto" | "system";

type DbLabelSource = "USER" | "AUTO" | "SYSTEM";

const LABEL_TO_API: Record<DbLabelSource, ApiLabelSource> = {
  USER: "user",
  AUTO: "auto",
  SYSTEM: "system"
};

function toApiLabelSource(value: DbLabelSource): ApiLabelSource {
  return LABEL_TO_API[value] ?? "user";
}

function toTrailSummary(trail: {
  id: string;
  userId: string;
  deviceId: string;
  label: string;
  labelSource: DbLabelSource;
  labelUpdatedAt: Date;
  createdAt: Date;
  updatedAt: Date;
  savedAt: Date;
  nodeCount: number;
  rootUrl?: string | null;
  rootTitle?: string | null;
  rootFavicon?: string | null;
  deletedAt?: Date | null;
}) {
  return {
    id: trail.id,
    userId: trail.userId,
    deviceId: trail.deviceId,
    label: trail.label,
    labelSource: toApiLabelSource(trail.labelSource),
    labelUpdatedAt: trail.labelUpdatedAt.toISOString(),
    createdAt: trail.createdAt.toISOString(),
    updatedAt: trail.updatedAt.toISOString(),
    savedAt: trail.savedAt.toISOString(),
    nodeCount: trail.nodeCount,
    rootUrl: trail.rootUrl ?? null,
    rootTitle: trail.rootTitle ?? null,
    rootFavicon: trail.rootFavicon ?? null,
    deletedAt: trail.deletedAt ? trail.deletedAt.toISOString() : null
  };
}

export async function GET(request: Request) {
  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const url = new URL(request.url);
  const limitRaw = Number(url.searchParams.get("limit"));
  const limit = Number.isFinite(limitRaw) && limitRaw > 0 && limitRaw <= 200 ? limitRaw : 50;
  const cursorRaw = url.searchParams.get("cursor");
  const includeDeleted = url.searchParams.get("includeDeleted") === "true";

  const cursorDate = cursorRaw ? new Date(cursorRaw) : null;
  const cursorFilter = cursorDate && !Number.isNaN(cursorDate.getTime())
    ? { updatedAt: { lt: cursorDate } }
    : {};

  const trails = await db.trail.findMany({
    where: {
      userId: user.id,
      ...(includeDeleted ? {} : { deletedAt: null }),
      ...cursorFilter
    },
    orderBy: { updatedAt: "desc" },
    take: limit + 1
  });

  const hasNext = trails.length > limit;
  const items = hasNext ? trails.slice(0, limit) : trails;
  const nextCursor = hasNext ? trails[limit]?.updatedAt.toISOString() : null;

  return jsonNoStore({
    items: items.map(toTrailSummary),
    nextCursor
  });
}
```

```ts
// apps/api/app/v1/trails/[id]/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyUserToken } from "@/src/server/auth/user-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { ensureUser } from "@/src/server/user";
import { db } from "@trail/db";

export const runtime = "nodejs";

type ApiLabelSource = "user" | "auto" | "system";

type DbLabelSource = "USER" | "AUTO" | "SYSTEM";

const LABEL_TO_API: Record<DbLabelSource, ApiLabelSource> = {
  USER: "user",
  AUTO: "auto",
  SYSTEM: "system"
};

const API_TO_LABEL: Record<ApiLabelSource, DbLabelSource> = {
  user: "USER",
  auto: "AUTO",
  system: "SYSTEM"
};

function toApiLabelSource(value: DbLabelSource): ApiLabelSource {
  return LABEL_TO_API[value] ?? "user";
}

function toDbLabelSource(value: unknown): DbLabelSource | null {
  if (typeof value !== "string") return null;
  const lowered = value.trim().toLowerCase() as ApiLabelSource;
  return API_TO_LABEL[lowered] ?? null;
}

function parseDeletedAt(value: unknown): Date | null | undefined {
  if (value === null) return null;
  if (typeof value !== "string") return undefined;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return undefined;
  return parsed;
}

function toTrailRecord(trail: {
  id: string;
  userId: string;
  deviceId: string;
  label: string;
  labelSource: DbLabelSource;
  labelUpdatedAt: Date;
  createdAt: Date;
  updatedAt: Date;
  savedAt: Date;
  nodeCount: number;
  rootUrl?: string | null;
  rootTitle?: string | null;
  rootFavicon?: string | null;
  payload: unknown;
  deletedAt?: Date | null;
}) {
  return {
    id: trail.id,
    userId: trail.userId,
    deviceId: trail.deviceId,
    label: trail.label,
    labelSource: toApiLabelSource(trail.labelSource),
    labelUpdatedAt: trail.labelUpdatedAt.toISOString(),
    createdAt: trail.createdAt.toISOString(),
    updatedAt: trail.updatedAt.toISOString(),
    savedAt: trail.savedAt.toISOString(),
    nodeCount: trail.nodeCount,
    rootUrl: trail.rootUrl ?? null,
    rootTitle: trail.rootTitle ?? null,
    rootFavicon: trail.rootFavicon ?? null,
    payload: trail.payload,
    deletedAt: trail.deletedAt ? trail.deletedAt.toISOString() : null
  };
}

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  if (!id) {
    return jsonError("trail_not_found", "Trail not found.", { status: 404 });
  }

  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const label = typeof body?.label === "string" ? body.label : undefined;
  const labelSource = toDbLabelSource(body?.labelSource);
  const deletedAt = parseDeletedAt(body?.deletedAt);

  if (!label && !labelSource && deletedAt === undefined) {
    return jsonError("invalid_payload", "Invalid update payload.", { status: 400 });
  }

  const existing = await db.trail.findFirst({ where: { id, userId: user.id } });
  if (!existing) {
    return jsonError("trail_not_found", "Trail not found.", { status: 404 });
  }

  const now = new Date();
  const data: Record<string, unknown> = {};
  if (label !== undefined) data.label = label;
  if (labelSource) data.labelSource = labelSource;
  if (label !== undefined || labelSource) data.labelUpdatedAt = now;
  if (deletedAt !== undefined) data.deletedAt = deletedAt;

  const updated = await db.trail.update({
    where: { id },
    data
  });

  return jsonNoStore(toTrailRecord(updated as typeof existing));
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  if (!id) {
    return jsonError("trail_not_found", "Trail not found.", { status: 404 });
  }

  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const existing = await db.trail.findFirst({ where: { id, userId: user.id } });
  if (!existing) {
    return jsonError("trail_not_found", "Trail not found.", { status: 404 });
  }

  const updated = await db.trail.update({
    where: { id },
    data: { deletedAt: new Date() }
  });

  return jsonNoStore(toTrailRecord(updated as typeof existing));
}
```

```ts
// apps/api/app/v1/trails/[id]/restore/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyUserToken } from "@/src/server/auth/user-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { ensureUser } from "@/src/server/user";
import { db } from "@trail/db";

export const runtime = "nodejs";

type DbLabelSource = "USER" | "AUTO" | "SYSTEM";

type ApiLabelSource = "user" | "auto" | "system";

const LABEL_TO_API: Record<DbLabelSource, ApiLabelSource> = {
  USER: "user",
  AUTO: "auto",
  SYSTEM: "system"
};

function toApiLabelSource(value: DbLabelSource): ApiLabelSource {
  return LABEL_TO_API[value] ?? "user";
}

function toTrailRecord(trail: {
  id: string;
  userId: string;
  deviceId: string;
  label: string;
  labelSource: DbLabelSource;
  labelUpdatedAt: Date;
  createdAt: Date;
  updatedAt: Date;
  savedAt: Date;
  nodeCount: number;
  rootUrl?: string | null;
  rootTitle?: string | null;
  rootFavicon?: string | null;
  payload: unknown;
  deletedAt?: Date | null;
}) {
  return {
    id: trail.id,
    userId: trail.userId,
    deviceId: trail.deviceId,
    label: trail.label,
    labelSource: toApiLabelSource(trail.labelSource),
    labelUpdatedAt: trail.labelUpdatedAt.toISOString(),
    createdAt: trail.createdAt.toISOString(),
    updatedAt: trail.updatedAt.toISOString(),
    savedAt: trail.savedAt.toISOString(),
    nodeCount: trail.nodeCount,
    rootUrl: trail.rootUrl ?? null,
    rootTitle: trail.rootTitle ?? null,
    rootFavicon: trail.rootFavicon ?? null,
    payload: trail.payload,
    deletedAt: trail.deletedAt ? trail.deletedAt.toISOString() : null
  };
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  if (!id) {
    return jsonError("trail_not_found", "Trail not found.", { status: 404 });
  }

  const token = getBearerToken(request.headers);
  const authUser = await verifyUserToken(token);
  if (!authUser) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await ensureUser(authUser);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const existing = await db.trail.findFirst({ where: { id, userId: user.id } });
  if (!existing) {
    return jsonError("trail_not_found", "Trail not found.", { status: 404 });
  }

  const updated = await db.trail.update({
    where: { id },
    data: { deletedAt: null }
  });

  return jsonNoStore(toTrailRecord(updated as typeof existing));
}
```

**Step 4: Run test to verify it passes**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/trails.test.ts`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/api/app/v1/trails/route.ts \
  apps/api/app/v1/trails/[id]/route.ts \
  apps/api/app/v1/trails/[id]/restore/route.ts \
  apps/api/app/v1/__tests__/trails.test.ts

git commit -m "Add trails list and mutation endpoints"
```

---

### Task 4: Trails Sync Endpoint

**Files:**
- Create: `apps/api/app/v1/trails/sync/route.ts`
- Create: `apps/api/app/v1/__tests__/trails-sync.test.ts`

**Step 1: Write the failing test**
```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const authMocks = vi.hoisted(() => ({
  verifyExtensionToken: vi.fn()
}));

const userMocks = vi.hoisted(() => ({
  getUserById: vi.fn()
}));

const trailMocks = vi.hoisted(() => ({
  syncTrails: vi.fn()
}));

vi.mock("@/src/server/auth/extension-auth", () => ({
  ...authMocks
}));

vi.mock("@/src/server/user", () => ({
  ...userMocks
}));

vi.mock("@/src/server/trails-sync", () => ({
  ...trailMocks
}));

import { POST as syncTrails } from "../trails/sync/route";

describe("v1 trails sync", () => {
  beforeEach(() => {
    authMocks.verifyExtensionToken.mockReset();
    userMocks.getUserById.mockReset();
    trailMocks.syncTrails.mockReset();
  });

  it("syncs trails with extension auth", async () => {
    authMocks.verifyExtensionToken.mockReturnValue({ sub: "user-1", iat: 0, exp: 999999 });
    userMocks.getUserById.mockResolvedValue({
      id: "user-1",
      email: "user@test.com",
      name: "Test User",
      imageUrl: null,
      createdAt: new Date("2026-01-01T00:00:00Z")
    });
    trailMocks.syncTrails.mockResolvedValue({
      serverSyncAt: new Date("2026-02-02T00:00:00Z"),
      updates: []
    });

    const response = await syncTrails(
      new Request("http://localhost/v1/trails/sync", {
        method: "POST",
        headers: { Authorization: "Bearer extension-token" },
        body: JSON.stringify({
          deviceId: "device-1",
          clientSyncAt: "2026-02-01T00:00:00Z",
          trails: []
        })
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.serverSyncAt).toBe("2026-02-02T00:00:00.000Z");
  });
});
```

**Step 2: Run test to verify it fails**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/trails-sync.test.ts`
Expected: FAIL (route not implemented).

**Step 3: Write minimal implementation**
```ts
// apps/api/app/v1/trails/sync/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyExtensionToken } from "@/src/server/auth/extension-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { getUserById } from "@/src/server/user";
import { syncTrails } from "@/src/server/trails-sync";

export const runtime = "nodejs";

type ApiLabelSource = "user" | "auto" | "system";

type DbLabelSource = "USER" | "AUTO" | "SYSTEM";

const API_TO_LABEL: Record<ApiLabelSource, DbLabelSource> = {
  user: "USER",
  auto: "AUTO",
  system: "SYSTEM"
};

const LABEL_TO_API: Record<DbLabelSource, ApiLabelSource> = {
  USER: "user",
  AUTO: "auto",
  SYSTEM: "system"
};

function toDbLabelSource(value: unknown): DbLabelSource | null {
  if (typeof value !== "string") return null;
  const lowered = value.trim().toLowerCase() as ApiLabelSource;
  return API_TO_LABEL[lowered] ?? null;
}

function toApiLabelSource(value: DbLabelSource): ApiLabelSource {
  return LABEL_TO_API[value] ?? "user";
}

function parseDate(value: unknown): Date | null {
  if (typeof value !== "string") return null;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed;
}

export async function POST(request: Request) {
  const token = getBearerToken(request.headers);
  const extension = token ? verifyExtensionToken(token) : null;
  if (!extension?.sub) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await getUserById(extension.sub);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const deviceId = typeof body?.deviceId === "string" ? body.deviceId : null;
  const clientSyncAt = parseDate(body?.clientSyncAt);
  const trails = Array.isArray(body?.trails) ? body.trails : null;

  if (!deviceId || !clientSyncAt || !trails) {
    return jsonError("invalid_payload", "Invalid sync payload.", { status: 400 });
  }

  const parsedTrails = [] as Array<{
    id: string;
    deviceId?: string | null;
    label: string;
    labelSource: DbLabelSource;
    labelUpdatedAt: Date;
    createdAt: Date;
    updatedAt: Date;
    savedAt: Date;
    nodeCount: number;
    rootUrl?: string | null;
    rootTitle?: string | null;
    rootFavicon?: string | null;
    payload: unknown;
    deletedAt?: Date | null;
  }>;

  for (const trail of trails) {
    if (!trail || typeof trail !== "object") {
      return jsonError("invalid_payload", "Invalid sync payload.", { status: 400 });
    }

    const labelSource = toDbLabelSource(trail.labelSource);
    const labelUpdatedAt = parseDate(trail.labelUpdatedAt);
    const createdAt = parseDate(trail.createdAt);
    const updatedAt = parseDate(trail.updatedAt);
    const savedAt = parseDate(trail.savedAt);
    const deletedAt = trail.deletedAt === null ? null : parseDate(trail.deletedAt);

    if (
      typeof trail.id !== "string" ||
      typeof trail.label !== "string" ||
      !labelSource ||
      !labelUpdatedAt ||
      !createdAt ||
      !updatedAt ||
      !savedAt ||
      typeof trail.nodeCount !== "number"
    ) {
      return jsonError("invalid_payload", "Invalid sync payload.", { status: 400 });
    }

    parsedTrails.push({
      id: trail.id,
      deviceId: typeof trail.deviceId === "string" ? trail.deviceId : null,
      label: trail.label,
      labelSource,
      labelUpdatedAt,
      createdAt,
      updatedAt,
      savedAt,
      nodeCount: trail.nodeCount,
      rootUrl: typeof trail.rootUrl === "string" ? trail.rootUrl : null,
      rootTitle: typeof trail.rootTitle === "string" ? trail.rootTitle : null,
      rootFavicon: typeof trail.rootFavicon === "string" ? trail.rootFavicon : null,
      payload: trail.payload,
      deletedAt
    });
  }

  const result = await syncTrails({
    userId: user.id,
    deviceId,
    clientSyncAt,
    trails: parsedTrails
  });

  return jsonNoStore({
    serverSyncAt: result.serverSyncAt.toISOString(),
    updates: result.updates.map((trail) => ({
      id: trail.id,
      deviceId: trail.deviceId ?? null,
      label: trail.label,
      labelSource: toApiLabelSource(trail.labelSource),
      labelUpdatedAt: trail.labelUpdatedAt.toISOString(),
      createdAt: trail.createdAt.toISOString(),
      updatedAt: trail.updatedAt.toISOString(),
      savedAt: trail.savedAt.toISOString(),
      nodeCount: trail.nodeCount,
      rootUrl: trail.rootUrl ?? null,
      rootTitle: trail.rootTitle ?? null,
      rootFavicon: trail.rootFavicon ?? null,
      payload: trail.payload,
      deletedAt: trail.deletedAt ? trail.deletedAt.toISOString() : null
    }))
  });
}
```

**Step 4: Run test to verify it passes**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/trails-sync.test.ts`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/api/app/v1/trails/sync/route.ts \
  apps/api/app/v1/__tests__/trails-sync.test.ts

git commit -m "Add trails sync endpoint"
```

---

### Task 5: Account Snapshot Endpoint

**Files:**
- Create: `apps/api/app/v1/account/route.ts`
- Create: `apps/api/app/v1/__tests__/account.test.ts`

**Step 1: Write the failing test**
```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const authMocks = vi.hoisted(() => ({
  verifyExtensionToken: vi.fn()
}));

const userMocks = vi.hoisted(() => ({
  getUserById: vi.fn()
}));

const snapshotMocks = vi.hoisted(() => ({
  buildAccountSnapshot: vi.fn()
}));

vi.mock("@/src/server/auth/extension-auth", () => ({
  ...authMocks
}));

vi.mock("@/src/server/user", () => ({
  ...userMocks
}));

vi.mock("@/src/server/account-snapshot", () => ({
  ...snapshotMocks
}));

import { GET } from "../account/route";

describe("v1 account snapshot", () => {
  beforeEach(() => {
    authMocks.verifyExtensionToken.mockReset();
    userMocks.getUserById.mockReset();
    snapshotMocks.buildAccountSnapshot.mockReset();
  });

  it("returns an account snapshot", async () => {
    authMocks.verifyExtensionToken.mockReturnValue({ sub: "user-1", iat: 0, exp: 999999 });
    userMocks.getUserById.mockResolvedValue({
      id: "user-1",
      email: "user@test.com",
      name: "Test User",
      imageUrl: null,
      createdAt: new Date("2026-01-01T00:00:00Z")
    });
    snapshotMocks.buildAccountSnapshot.mockReturnValue({
      session: { status: "authenticated", accessToken: "token" },
      user: { id: "user-1", email: "user@test.com", displayName: "Test User", createdAt: "2026-01-01T00:00:00.000Z" },
      subscription: null,
      billing: { state: "none" },
      plans: []
    });

    const response = await GET(
      new Request("http://localhost/v1/account", {
        headers: { Authorization: "Bearer extension-token" }
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.session.status).toBe("authenticated");
    expect(payload.billing.state).toBe("none");
  });
});
```

**Step 2: Run test to verify it fails**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/account.test.ts`
Expected: FAIL (route not implemented).

**Step 3: Write minimal implementation**
```ts
// apps/api/app/v1/account/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyExtensionToken } from "@/src/server/auth/extension-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { buildAccountSnapshot } from "@/src/server/account-snapshot";
import { getUserById } from "@/src/server/user";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const token = getBearerToken(request.headers);
  const extension = token ? verifyExtensionToken(token) : null;
  if (!extension?.sub || !token) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await getUserById(extension.sub);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const expiresAt = extension.exp ? new Date(extension.exp * 1000).toISOString() : null;
  const snapshot = buildAccountSnapshot({
    user,
    accessToken: token,
    expiresAt
  });

  return jsonNoStore(snapshot);
}
```

**Step 4: Run test to verify it passes**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/account.test.ts`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/api/app/v1/account/route.ts \
  apps/api/app/v1/__tests__/account.test.ts

git commit -m "Add account snapshot endpoint"
```

---

### Task 6: Billing Endpoints (plans, subscription, billing, checkout, portal)

**Files:**
- Create: `apps/api/app/v1/plans/route.ts`
- Create: `apps/api/app/v1/subscription/route.ts`
- Create: `apps/api/app/v1/billing/route.ts`
- Create: `apps/api/app/v1/subscription/checkout/route.ts`
- Create: `apps/api/app/v1/billing/portal/route.ts`
- Create: `apps/api/app/v1/__tests__/billing.test.ts`

**Step 1: Write the failing test**
```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const authMocks = vi.hoisted(() => ({
  verifyExtensionToken: vi.fn()
}));

const userMocks = vi.hoisted(() => ({
  getUserById: vi.fn()
}));

const snapshotMocks = vi.hoisted(() => ({
  listPlans: vi.fn()
}));

const dbMocks = vi.hoisted(() => ({
  db: {
    userSubscription: {
      findUnique: vi.fn()
    }
  }
}));

vi.mock("@/src/server/auth/extension-auth", () => ({
  ...authMocks
}));

vi.mock("@/src/server/user", () => ({
  ...userMocks
}));

vi.mock("@/src/server/account-snapshot", () => ({
  ...snapshotMocks
}));

vi.mock("@trail/db", () => ({
  ...dbMocks
}));

import { GET as listPlans } from "../plans/route";
import { GET as getSubscription } from "../subscription/route";
import { GET as getBilling } from "../billing/route";
import { POST as startCheckout } from "../subscription/checkout/route";
import { POST as createPortal } from "../billing/portal/route";

describe("v1 billing endpoints", () => {
  beforeEach(() => {
    authMocks.verifyExtensionToken.mockReset();
    userMocks.getUserById.mockReset();
    snapshotMocks.listPlans.mockReset();
    dbMocks.db.userSubscription.findUnique.mockReset();
  });

  it("lists plans without auth", async () => {
    snapshotMocks.listPlans.mockReturnValue([{ id: "free" }]);

    const response = await listPlans(new Request("http://localhost/v1/plans"));

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload[0].id).toBe("free");
  });

  it("returns stub subscription when none exists", async () => {
    authMocks.verifyExtensionToken.mockReturnValue({ sub: "user-1", iat: 0, exp: 999999 });
    userMocks.getUserById.mockResolvedValue({
      id: "user-1",
      email: "user@test.com",
      name: "Test User",
      imageUrl: null,
      createdAt: new Date("2026-01-01T00:00:00Z")
    });
    dbMocks.db.userSubscription.findUnique.mockResolvedValue(null);

    const response = await getSubscription(
      new Request("http://localhost/v1/subscription", {
        headers: { Authorization: "Bearer extension-token" }
      })
    );

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.planId).toBe("free");
    expect(payload.status).toBe("active");
  });

  it("returns billing status", async () => {
    authMocks.verifyExtensionToken.mockReturnValue({ sub: "user-1", iat: 0, exp: 999999 });
    userMocks.getUserById.mockResolvedValue({
      id: "user-1",
      email: "user@test.com",
      name: "Test User",
      imageUrl: null,
      createdAt: new Date("2026-01-01T00:00:00Z")
    });

    const response = await getBilling(
      new Request("http://localhost/v1/billing", {
        headers: { Authorization: "Bearer extension-token" }
      })
    );

    const payload = await response.json();
    expect(payload.state).toBe("none");
  });

  it("creates checkout and portal links", async () => {
    authMocks.verifyExtensionToken.mockReturnValue({ sub: "user-1", iat: 0, exp: 999999 });
    userMocks.getUserById.mockResolvedValue({
      id: "user-1",
      email: "user@test.com",
      name: "Test User",
      imageUrl: null,
      createdAt: new Date("2026-01-01T00:00:00Z")
    });

    const checkoutResponse = await startCheckout(
      new Request("http://localhost/v1/subscription/checkout", {
        method: "POST",
        headers: { Authorization: "Bearer extension-token" },
        body: JSON.stringify({ planId: "pro", interval: "month", successUrl: "https://app.test/billing" })
      })
    );

    const portalResponse = await createPortal(
      new Request("http://localhost/v1/billing/portal", {
        method: "POST",
        headers: { Authorization: "Bearer extension-token" },
        body: JSON.stringify({ returnUrl: "https://app.test/billing" })
      })
    );

    const checkoutPayload = await checkoutResponse.json();
    const portalPayload = await portalResponse.json();

    expect(checkoutPayload.url).toBe("https://app.test/billing");
    expect(portalPayload.url).toBe("https://app.test/billing");
  });
});
```

**Step 2: Run test to verify it fails**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/billing.test.ts`
Expected: FAIL (routes not implemented).

**Step 3: Write minimal implementation**
```ts
// apps/api/app/v1/plans/route.ts
import { jsonNoStore } from "@/src/server/response";
import { listPlans } from "@/src/server/account-snapshot";

export const runtime = "nodejs";

export async function GET() {
  return jsonNoStore(listPlans());
}
```

```ts
// apps/api/app/v1/subscription/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyExtensionToken } from "@/src/server/auth/extension-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { getUserById } from "@/src/server/user";
import { db } from "@trail/db";

export const runtime = "nodejs";

const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;

function toIso(date: Date) {
  return date.toISOString();
}

function buildStubSubscription(params: { userId: string; createdAt: Date }) {
  const currentPeriodStart = params.createdAt;
  const currentPeriodEnd = new Date(currentPeriodStart.getTime() + THIRTY_DAYS_MS);
  return {
    id: `stub-${params.userId}`,
    planId: "free",
    status: "active",
    interval: "month",
    currentPeriodStart: toIso(currentPeriodStart),
    currentPeriodEnd: toIso(currentPeriodEnd),
    cancelAtPeriodEnd: false,
    trialEndsAt: null,
    canceledAt: null
  };
}

export async function GET(request: Request) {
  const token = getBearerToken(request.headers);
  const extension = token ? verifyExtensionToken(token) : null;
  if (!extension?.sub) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await getUserById(extension.sub);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const record = await db.userSubscription.findUnique({ where: { userId: user.id } });
  if (!record) {
    return jsonNoStore(buildStubSubscription({ userId: user.id, createdAt: user.createdAt }));
  }

  const currentPeriodStart = record.createdAt;
  const currentPeriodEnd = record.currentPeriodEnd ?? new Date(record.createdAt.getTime() + THIRTY_DAYS_MS);
  return jsonNoStore({
    id: record.id,
    planId: record.plan === "PRO" ? "pro" : "free",
    status: record.status?.toLowerCase?.() ?? "active",
    interval: "month",
    currentPeriodStart: toIso(currentPeriodStart),
    currentPeriodEnd: toIso(currentPeriodEnd),
    cancelAtPeriodEnd: false,
    trialEndsAt: null,
    canceledAt: null
  });
}
```

```ts
// apps/api/app/v1/billing/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyExtensionToken } from "@/src/server/auth/extension-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { getUserById } from "@/src/server/user";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const token = getBearerToken(request.headers);
  const extension = token ? verifyExtensionToken(token) : null;
  if (!extension?.sub) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await getUserById(extension.sub);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  return jsonNoStore({ state: "none" });
}
```

```ts
// apps/api/app/v1/subscription/checkout/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyExtensionToken } from "@/src/server/auth/extension-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { getUserById } from "@/src/server/user";

export const runtime = "nodejs";

const DEFAULT_URL = "https://app.gettrail.net/billing";

export async function POST(request: Request) {
  const token = getBearerToken(request.headers);
  const extension = token ? verifyExtensionToken(token) : null;
  if (!extension?.sub) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await getUserById(extension.sub);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const url = typeof body?.successUrl === "string" ? body.successUrl : DEFAULT_URL;

  return jsonNoStore({
    url,
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
  });
}
```

```ts
// apps/api/app/v1/billing/portal/route.ts
import { getBearerToken } from "@/src/server/auth/headers";
import { verifyExtensionToken } from "@/src/server/auth/extension-auth";
import { jsonError } from "@/src/server/error-response";
import { jsonNoStore } from "@/src/server/response";
import { getUserById } from "@/src/server/user";

export const runtime = "nodejs";

const DEFAULT_URL = "https://app.gettrail.net/billing";

export async function POST(request: Request) {
  const token = getBearerToken(request.headers);
  const extension = token ? verifyExtensionToken(token) : null;
  if (!extension?.sub) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const user = await getUserById(extension.sub);
  if (!user) {
    return jsonError("unauthorized", "Unauthorized.", { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const url = typeof body?.returnUrl === "string" ? body.returnUrl : DEFAULT_URL;

  return jsonNoStore({
    url,
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
  });
}
```

**Step 4: Run test to verify it passes**
Run: `pnpm --filter @trail/api test -- apps/api/app/v1/__tests__/billing.test.ts`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/api/app/v1/plans/route.ts \
  apps/api/app/v1/subscription/route.ts \
  apps/api/app/v1/billing/route.ts \
  apps/api/app/v1/subscription/checkout/route.ts \
  apps/api/app/v1/billing/portal/route.ts \
  apps/api/app/v1/__tests__/billing.test.ts

git commit -m "Add billing v1 endpoints"
```

---

### Task 7: Full Test Run

**Files:**
- None

**Step 1: Run full API test suite**
Run: `pnpm --filter @trail/api test`
Expected: PASS

**Step 2: Commit if needed**
If any fixes were required during the run:
```bash
git add <files>
git commit -m "Fix API v1 tests"
```
