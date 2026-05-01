#!/usr/bin/env tsx
/**
 * One-shot migration: Neon (Prisma + BetterAuth, 0.9.x era) → hosted
 * Supabase (Auth + Postgres + RLS, 1.0.0+). Run once before publishing
 * 1.0.0 to the Chrome Web Store so the existing ~17 users find their
 * trails, devices, and subscriptions intact when they sign in.
 *
 * Identity bridge: BetterAuth password hashes and OAuth refresh tokens
 * do NOT port — Supabase Auth is a different auth system. The single
 * portable handle is email. For each Neon User row we either find or
 * create a matching `auth.users` row by email, with `email_confirm:
 * true` so dependent rows can be inserted immediately. Users get a
 * password-recovery email afterwards.
 *
 * Idempotency: the script keeps a JSON state file at
 * `scripts/migration-state.json` mapping Neon cuids to Supabase UUIDs.
 * Re-runs read this file first and skip already-migrated entities.
 * Delete the file to start fresh.
 *
 * Audit: every entity touched is appended as a row to a CSV at
 * `scripts/migration-audit/<UTC-timestamp>.csv` so the run can be
 * reviewed by hand and reversed if something looks wrong.
 *
 * Usage:
 *   pnpm add -D pg @types/pg @supabase/supabase-js   # at repo root
 *   DATABASE_URL_NEON=postgres://... \
 *   SUPABASE_URL=https://...supabase.co \
 *   SUPABASE_SERVICE_ROLE_KEY=eyJ... \
 *   tsx scripts/migrate-neon-to-supabase.ts [--dry-run]
 *
 * NEVER commit credentials. SUPABASE_SERVICE_ROLE_KEY bypasses RLS —
 * keep it on a developer laptop, not in CI.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Client as PgClient } from "pg";
import { createClient as createSupabaseClient } from "@supabase/supabase-js";

const here = dirname(fileURLToPath(import.meta.url));
const STATE_PATH = resolve(here, "migration-state.json");
const AUDIT_DIR = resolve(here, "migration-audit");
const DRY_RUN = process.argv.includes("--dry-run");

// ---------------------------------------------------------------------------
// State + audit helpers
// ---------------------------------------------------------------------------

type MigrationState = {
  users: Record<string, string>; // neonUserCuid → supabaseUuid
  devices: Record<string, string>; // neonDeviceCuid → supabaseUuid
  trails: Record<string, string>; // neonTrailCuid → supabaseUuid
};

function loadState(): MigrationState {
  if (!existsSync(STATE_PATH)) return { users: {}, devices: {}, trails: {} };
  return JSON.parse(readFileSync(STATE_PATH, "utf8")) as MigrationState;
}

function saveState(state: MigrationState): void {
  if (DRY_RUN) return;
  writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

const auditRows: string[] = ["entity,neon_id,supabase_id,email,status"];

function audit(
  entity: string,
  neonId: string,
  supabaseId: string,
  email: string,
  status: "created" | "reused" | "skipped" | "failed",
): void {
  const escape = (v: string): string =>
    /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
  auditRows.push(
    [entity, neonId, supabaseId, email, status].map(escape).join(","),
  );
}

function flushAudit(): void {
  if (DRY_RUN) {
    console.log("--- audit (dry-run, not written) ---");
    console.log(auditRows.join("\n"));
    return;
  }
  mkdirSync(AUDIT_DIR, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const path = resolve(AUDIT_DIR, `${stamp}.csv`);
  writeFileSync(path, auditRows.join("\n") + "\n");
  console.log(`audit written: ${path}`);
}

function uuidv7(): string {
  // Minimal uuidv7 generator: 48-bit unix-ms timestamp prefix +
  // version/variant bits + 74 random bits. Matches the runtime helper
  // at extension/src/shared/lib/uuid.ts but inlined to keep this
  // script self-contained.
  const ms = BigInt(Date.now());
  const tsHex = ms.toString(16).padStart(12, "0");
  const rand = crypto.getRandomValues(new Uint8Array(10));
  // Force version (7) and variant (10xx) bits.
  rand[0] = (rand[0] & 0x0f) | 0x70;
  rand[2] = (rand[2] & 0x3f) | 0x80;
  const randHex = Array.from(rand, (b) => b.toString(16).padStart(2, "0")).join("");
  return `${tsHex.slice(0, 8)}-${tsHex.slice(8)}-${randHex.slice(0, 4)}-${randHex.slice(4, 8)}-${randHex.slice(8, 20)}`;
}

// ---------------------------------------------------------------------------
// Env wiring
// ---------------------------------------------------------------------------

function requireEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    console.error(`Missing required env: ${key}`);
    process.exit(1);
  }
  return value;
}

const DATABASE_URL_NEON = requireEnv("DATABASE_URL_NEON");
const SUPABASE_URL = requireEnv("SUPABASE_URL");
const SUPABASE_SERVICE_ROLE_KEY = requireEnv("SUPABASE_SERVICE_ROLE_KEY");

const sb = createSupabaseClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
});

// ---------------------------------------------------------------------------
// Step 1: pull everything from Neon in one snapshot
// ---------------------------------------------------------------------------

type NeonUser = {
  id: string;
  email: string;
  name: string;
  email_verified: boolean;
  image: string | null;
  image_url: string | null;
  created_at: Date;
  updated_at: Date;
  onboarding_seen_at: Date | null;
};
type NeonDevice = {
  id: string;
  user_id: string;
  status: string;
  device_name: string | null;
  os: string | null;
  locale: string | null;
  timezone: string | null;
  browser_name: string | null;
  browser_version: string | null;
  extension_version: string | null;
  last_seen_at: Date | null;
  created_at: Date;
  updated_at: Date;
};
type NeonTrail = {
  id: string;
  user_id: string;
  device_id: string;
  label: string;
  label_source: string;
  label_updated_at: Date;
  created_at: Date;
  updated_at: Date;
  saved_at: Date;
  node_count: number;
  root_url: string | null;
  root_title: string | null;
  root_favicon: string | null;
  payload: unknown;
  deleted_at: Date | null;
};
type NeonSubscription = {
  id: string;
  user_id: string;
  plan: string;
  status: string;
  interval: string;
  pending_interval: string | null;
  polar_customer_id: string | null;
  polar_subscription_id: string | null;
  current_period_start: Date | null;
  current_period_end: Date | null;
  cancel_at_period_end: boolean;
  canceled_at: Date | null;
  created_at: Date;
  updated_at: Date;
};
type NeonSettings = {
  user_id: string;
  device_session_ttl_days: string;
  created_at: Date;
  updated_at: Date;
};

async function pullFromNeon(): Promise<{
  users: NeonUser[];
  devices: NeonDevice[];
  trails: NeonTrail[];
  subscriptions: NeonSubscription[];
  settings: NeonSettings[];
}> {
  const pg = new PgClient({ connectionString: DATABASE_URL_NEON });
  await pg.connect();
  try {
    // BEGIN ... REPEATABLE READ snapshot keeps reads consistent across
    // tables — important if anyone is still hitting the Neon DB during
    // the migration window.
    await pg.query("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY");
    const users = (await pg.query<NeonUser>(
      `SELECT id, email, name, "emailVerified" AS email_verified, image, "imageUrl" AS image_url,
              "createdAt" AS created_at, "updatedAt" AS updated_at,
              "onboardingSeenAt" AS onboarding_seen_at
       FROM "User"`,
    )).rows;
    const devices = (await pg.query<NeonDevice>(
      `SELECT id, "userId" AS user_id, status, "deviceName" AS device_name, os, locale, timezone,
              "browserName" AS browser_name, "browserVersion" AS browser_version,
              "extensionVersion" AS extension_version, "lastSeenAt" AS last_seen_at,
              "createdAt" AS created_at, "updatedAt" AS updated_at
       FROM "Device"`,
    )).rows;
    const trails = (await pg.query<NeonTrail>(
      `SELECT id, "userId" AS user_id, "deviceId" AS device_id, label,
              "labelSource"::text AS label_source, "labelUpdatedAt" AS label_updated_at,
              "createdAt" AS created_at, "updatedAt" AS updated_at, "savedAt" AS saved_at,
              "nodeCount" AS node_count, "rootUrl" AS root_url, "rootTitle" AS root_title,
              "rootFavicon" AS root_favicon, payload, "deletedAt" AS deleted_at
       FROM "Trail"`,
    )).rows;
    const subscriptions = (await pg.query<NeonSubscription>(
      `SELECT id, "userId" AS user_id, plan::text, status::text, interval::text,
              "pendingInterval"::text AS pending_interval,
              "polarCustomerId" AS polar_customer_id,
              "polarSubscriptionId" AS polar_subscription_id,
              "currentPeriodStart" AS current_period_start,
              "currentPeriodEnd" AS current_period_end,
              "cancelAtPeriodEnd" AS cancel_at_period_end,
              "canceledAt" AS canceled_at,
              "createdAt" AS created_at, "updatedAt" AS updated_at
       FROM "UserSubscription"`,
    )).rows;
    const settings = (await pg.query<NeonSettings>(
      `SELECT "userId" AS user_id,
              "deviceSessionTtlDays"::text AS device_session_ttl_days,
              "createdAt" AS created_at, "updatedAt" AS updated_at
       FROM "AccountSettings"`,
    )).rows;
    await pg.query("COMMIT");
    return { users, devices, trails, subscriptions, settings };
  } finally {
    await pg.end();
  }
}

// ---------------------------------------------------------------------------
// Step 2: push to Supabase, with idempotent state mapping
// ---------------------------------------------------------------------------

async function ensureSupabaseUser(
  state: MigrationState,
  user: NeonUser,
): Promise<string | null> {
  const cached = state.users[user.id];
  if (cached) {
    audit("user", user.id, cached, user.email, "reused");
    return cached;
  }

  // Look up by email — the user may have already been created by a
  // previous interrupted run (without state) or have signed up
  // independently in 1.0.0 already.
  const existing = await sb.auth.admin.listUsers({ page: 1, perPage: 200 });
  if (existing.error) {
    console.error("listUsers failed", existing.error);
    audit("user", user.id, "", user.email, "failed");
    return null;
  }
  type AdminUser = { id: string; email: string | null };
  const match = (existing.data.users as AdminUser[]).find(
    (u) => u.email?.toLowerCase() === user.email.toLowerCase(),
  );
  if (match) {
    state.users[user.id] = match.id;
    audit("user", user.id, match.id, user.email, "reused");
    return match.id;
  }

  if (DRY_RUN) {
    audit("user", user.id, "(dry-run)", user.email, "skipped");
    return null;
  }

  const created = await sb.auth.admin.createUser({
    email: user.email,
    email_confirm: true,
    user_metadata: {
      migrated_from: "neon",
      legacy_user_id: user.id,
      legacy_name: user.name,
    },
  });
  if (created.error || !created.data.user) {
    console.error(`createUser ${user.email} failed`, created.error);
    audit("user", user.id, "", user.email, "failed");
    return null;
  }
  state.users[user.id] = created.data.user.id;
  audit("user", user.id, created.data.user.id, user.email, "created");
  return created.data.user.id;
}

async function upsertPublicUser(
  supabaseUserId: string,
  user: NeonUser,
): Promise<void> {
  if (DRY_RUN) return;
  const { error } = await sb.from("users").upsert(
    {
      id: supabaseUserId,
      email: user.email,
      name: user.name,
      email_verified: user.email_verified,
      image: user.image,
      image_url: user.image_url,
      created_at: user.created_at.toISOString(),
      updated_at: user.updated_at.toISOString(),
      onboarding_seen_at: user.onboarding_seen_at?.toISOString() ?? null,
    },
    { onConflict: "id" },
  );
  if (error) console.error(`public.users upsert failed for ${user.email}`, error);
}

async function migrateDevice(
  state: MigrationState,
  device: NeonDevice,
  supabaseUserId: string,
): Promise<string | null> {
  if (state.devices[device.id]) {
    audit("device", device.id, state.devices[device.id], "", "reused");
    return state.devices[device.id];
  }
  const newId = uuidv7();
  if (DRY_RUN) {
    audit("device", device.id, "(dry-run)", "", "skipped");
    return null;
  }
  const { error } = await sb.from("devices").insert({
    id: newId,
    user_id: supabaseUserId,
    status: device.status,
    device_name: device.device_name,
    os: device.os,
    locale: device.locale,
    timezone: device.timezone,
    browser_name: device.browser_name,
    browser_version: device.browser_version,
    extension_version: device.extension_version,
    last_seen_at: device.last_seen_at?.toISOString() ?? null,
    created_at: device.created_at.toISOString(),
    updated_at: device.updated_at.toISOString(),
  });
  if (error) {
    console.error("device insert failed", error);
    audit("device", device.id, "", "", "failed");
    return null;
  }
  state.devices[device.id] = newId;
  audit("device", device.id, newId, "", "created");
  return newId;
}

async function migrateTrail(
  state: MigrationState,
  trail: NeonTrail,
  supabaseUserId: string,
  supabaseDeviceId: string,
): Promise<void> {
  if (state.trails[trail.id]) {
    audit("trail", trail.id, state.trails[trail.id], "", "reused");
    return;
  }
  const newId = uuidv7();
  if (DRY_RUN) {
    audit("trail", trail.id, "(dry-run)", "", "skipped");
    return;
  }
  const payloadWithMigration = {
    ...(trail.payload as object),
    _migration: { legacy_id: trail.id, source: "neon" },
  };
  const { error } = await sb.from("trails").insert({
    id: newId,
    user_id: supabaseUserId,
    device_id: supabaseDeviceId,
    label: trail.label,
    label_source: trail.label_source,
    label_updated_at: trail.label_updated_at.toISOString(),
    created_at: trail.created_at.toISOString(),
    updated_at: trail.updated_at.toISOString(),
    saved_at: trail.saved_at.toISOString(),
    node_count: trail.node_count,
    root_url: trail.root_url,
    root_title: trail.root_title,
    root_favicon: trail.root_favicon,
    payload: payloadWithMigration,
    deleted_at: trail.deleted_at?.toISOString() ?? null,
  });
  if (error) {
    console.error("trail insert failed", error);
    audit("trail", trail.id, "", "", "failed");
    return;
  }
  state.trails[trail.id] = newId;
  audit("trail", trail.id, newId, "", "created");
}

async function migrateSubscription(
  sub: NeonSubscription,
  supabaseUserId: string,
): Promise<void> {
  if (DRY_RUN) {
    audit("subscription", sub.id, "(dry-run)", "", "skipped");
    return;
  }
  // user_id is UNIQUE on user_subscriptions, so onConflict on user_id
  // gives us natural idempotency without needing state mapping.
  const { error } = await sb.from("user_subscriptions").upsert(
    {
      user_id: supabaseUserId,
      plan: sub.plan,
      status: sub.status,
      interval: sub.interval,
      pending_interval: sub.pending_interval,
      polar_customer_id: sub.polar_customer_id,
      polar_subscription_id: sub.polar_subscription_id,
      current_period_start: sub.current_period_start?.toISOString() ?? null,
      current_period_end: sub.current_period_end?.toISOString() ?? null,
      cancel_at_period_end: sub.cancel_at_period_end,
      canceled_at: sub.canceled_at?.toISOString() ?? null,
      created_at: sub.created_at.toISOString(),
      updated_at: sub.updated_at.toISOString(),
    },
    { onConflict: "user_id" },
  );
  if (error) {
    console.error("subscription upsert failed", error);
    audit("subscription", sub.id, "", "", "failed");
    return;
  }
  audit("subscription", sub.id, supabaseUserId, "", "created");
}

async function migrateSettings(
  s: NeonSettings,
  supabaseUserId: string,
): Promise<void> {
  if (DRY_RUN) {
    audit("settings", s.user_id, "(dry-run)", "", "skipped");
    return;
  }
  const { error } = await sb.from("account_settings").upsert(
    {
      user_id: supabaseUserId,
      device_session_ttl_days: s.device_session_ttl_days,
      created_at: s.created_at.toISOString(),
      updated_at: s.updated_at.toISOString(),
    },
    { onConflict: "user_id" },
  );
  if (error) {
    console.error("settings upsert failed", error);
    audit("settings", s.user_id, "", "", "failed");
    return;
  }
  audit("settings", s.user_id, supabaseUserId, "", "created");
}

async function sendRecoveryEmails(state: MigrationState, users: NeonUser[]): Promise<void> {
  for (const user of users) {
    if (!state.users[user.id]) continue;
    if (DRY_RUN) {
      console.log(`would send recovery link to ${user.email}`);
      continue;
    }
    const { error } = await sb.auth.admin.generateLink({
      type: "recovery",
      email: user.email,
    });
    if (error) console.error(`recovery link for ${user.email} failed`, error);
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  console.log(DRY_RUN ? "DRY-RUN — no writes" : "LIVE RUN — writes will occur");
  const state = loadState();

  console.log("pulling from Neon …");
  const data = await pullFromNeon();
  console.log(
    `  users=${data.users.length} devices=${data.devices.length} trails=${data.trails.length} subs=${data.subscriptions.length} settings=${data.settings.length}`,
  );

  // Insert order: users → devices → trails → subscriptions → settings.
  // FK chain: trails → devices → users.
  for (const u of data.users) {
    const sbUserId = await ensureSupabaseUser(state, u);
    if (!sbUserId) continue;
    await upsertPublicUser(sbUserId, u);
  }
  saveState(state);

  for (const d of data.devices) {
    const sbUserId = state.users[d.user_id];
    if (!sbUserId) {
      audit("device", d.id, "", "", "skipped");
      continue;
    }
    await migrateDevice(state, d, sbUserId);
  }
  saveState(state);

  for (const t of data.trails) {
    const sbUserId = state.users[t.user_id];
    const sbDeviceId = state.devices[t.device_id];
    if (!sbUserId || !sbDeviceId) {
      audit("trail", t.id, "", "", "skipped");
      continue;
    }
    await migrateTrail(state, t, sbUserId, sbDeviceId);
  }
  saveState(state);

  for (const s of data.subscriptions) {
    const sbUserId = state.users[s.user_id];
    if (!sbUserId) continue;
    await migrateSubscription(s, sbUserId);
  }
  for (const s of data.settings) {
    const sbUserId = state.users[s.user_id];
    if (!sbUserId) continue;
    await migrateSettings(s, sbUserId);
  }

  // Recovery emails are intentionally NOT sent here. Run a separate
  // pass after publishing 1.0.0 to Chrome Web Store, or trigger them
  // manually from the Supabase dashboard. Keeping them out of this
  // path avoids spamming users with a "reset password" email that
  // arrives with no context (the version they're running can't yet
  // sign in to Supabase).
  void sendRecoveryEmails;

  flushAudit();
  console.log("done");
}

main().catch((err) => {
  console.error("migration failed", err);
  flushAudit();
  process.exit(1);
});
