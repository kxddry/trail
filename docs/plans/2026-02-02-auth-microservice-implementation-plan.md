# Auth Microservice + BetterAuth Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace Better Auth with BetterAuth, add `apps/auth` on `auth.gettrail.net`, and complete remaining API normalization tasks with JWT auth.

**Architecture:** Auth lives in `apps/auth` (BetterAuth). Web clients redirect to auth, then exchange a one-time code for a JWT via `apps/api`. API validates JWT via JWKS. Extension keeps its own HMAC token.

**Tech Stack:** Next.js (App Router), BetterAuth, Prisma/Postgres, jose.

---

### Task 1: Scaffold `apps/auth` (Next.js app)

**Files:**
- Create: `apps/auth/package.json`
- Create: `apps/auth/next.config.mjs`
- Create: `apps/auth/tsconfig.json`
- Create: `apps/auth/app/layout.tsx`
- Create: `apps/auth/app/page.tsx`
- Create: `apps/auth/app/api/auth/[...all]/route.ts`
- Create: `apps/auth/.env.example`
- Modify: `package.json` (root) add `dev:auth` script

**Step 1: Create minimal package.json**
```json
{
  "name": "@trail/auth",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "next dev -p 3003",
    "build": "pnpm --filter @trail/db prisma generate && next build",
    "start": "next start -p 3003",
    "lint": "eslint .",
    "test": "vitest run --passWithNoTests",
    "typecheck": "tsc --noEmit",
    "format": "prettier --check ."
  },
  "dependencies": {
    "@trail/db": "workspace:*",
    "better-auth": "^1.0.0",
    "next": "^16.1.6",
    "react": "^19.2.4",
    "react-dom": "^19.2.4"
  },
  "devDependencies": {
    "@types/node": "^25.1.0",
    "@types/react": "^19.2.10",
    "@types/react-dom": "^19.2.3",
    "eslint": "^9.39.2",
    "eslint-config-next": "^16.1.6",
    "prettier": "^3.8.1",
    "typescript": "^5.9.3",
    "vitest": "^4.0.18"
  }
}
```

**Step 2: Add Next config + tsconfig**
Use the same structure as `apps/account` with `baseUrl` and `@/*` alias.

**Step 3: Add minimal layout/page**
`app/layout.tsx` and `app/page.tsx` should be a placeholder “Auth Service” page for now.

**Step 4: Add auth route handler**
`app/api/auth/[...all]/route.ts`:
```ts
import { auth } from "@/src/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

**Step 5: Add .env.example**
```
BETTER_AUTH_SECRET=
BETTER_AUTH_URL=https://auth.gettrail.net
BETTER_AUTH_TRUSTED_ORIGINS=http://localhost:3001,http://localhost:3003,https://app.gettrail.net
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
MAILGUN_API_KEY=
MAILGUN_DOMAIN=
MAILGUN_FROM_EMAIL=
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trail?schema=public
```

**Step 6: Root script**
Add `dev:auth` to root `package.json`:
```json
"dev:auth": "pnpm --filter @trail/auth dev"
```

**Step 7: Commit**
```bash
git add apps/auth package.json
git commit -m "Add auth app scaffold"
```

---

### Task 2: Configure BetterAuth in `apps/auth`

**Files:**
- Create: `apps/auth/src/auth.ts`
- Create: `apps/auth/src/auth-client.ts`
- Create: `apps/auth/src/email/provider.ts`
- Create: `apps/auth/src/email/mailgun.ts`
- Create: `apps/auth/app/login/page.tsx`

**Step 1: Email provider abstraction**
`src/email/provider.ts`:
```ts
export type EmailMessage = {
  to: string;
  subject: string;
  text: string;
};

export type EmailProvider = {
  send(message: EmailMessage): Promise<void>;
};
```

`src/email/mailgun.ts` should implement `EmailProvider` using Mailgun HTTP API.

**Step 2: BetterAuth config**
`src/auth.ts`:
```ts
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { emailOTP } from "better-auth/plugins";
import { jwt } from "better-auth/plugins/jwt";
import { db } from "@trail/db";
import { mailgunProvider } from "./email/mailgun";

const trustedOrigins = (process.env.BETTER_AUTH_TRUSTED_ORIGINS ?? "")
  .split(",")
  .map((value) => value.trim())
  .filter(Boolean);

export const auth = betterAuth({
  database: prismaAdapter(db, { provider: "postgresql" }),
  trustedOrigins,
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID as string,
      clientSecret: process.env.GITHUB_CLIENT_SECRET as string
    }
  },
  plugins: [
    emailOTP({
      async sendVerificationOTP({ email, otp }) {
        const provider = mailgunProvider();
        await provider.send({
          to: email,
          subject: "Your Trail sign-in code",
          text: `Your Trail sign-in code is ${otp}`
        });
      }
    }),
    jwt()
  ]
});
```

**Step 3: Auth client**
`src/auth-client.ts`:
```ts
import { createAuthClient } from "better-auth/client";
import { emailOTPClient } from "better-auth/client/plugins";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  plugins: [emailOTPClient(), jwtClient()]
});
```

**Step 4: Login page**
Create `app/login/page.tsx` with a minimal OTP + OAuth UI:
- email input
- send OTP button -> `authClient.emailOtp.sendVerificationOtp`
- OTP input + sign-in button -> `authClient.signIn.emailOtp`
- OAuth buttons -> `authClient.signIn.social({ provider, callbackURL })`
- On success redirect to `/auth/bridge?returnTo=...`

**Step 5: Commit**
```bash
git add apps/auth/src apps/auth/app/login
git commit -m "Add BetterAuth configuration and login UI"
```

---

### Task 3: Add BetterAuth Prisma tables + `AuthBridgeCode`

**Files:**
- Modify: `packages/db/prisma/schema.prisma`
- Create: `packages/db/prisma/migrations/<timestamp>_betterauth/migration.sql`
- Modify: `packages/db/src/generated/*`

**Step 1: Generate BetterAuth schema**
Run:
```bash
npx @better-auth/cli@latest generate
```
Copy BetterAuth models into `packages/db/prisma/schema.prisma` and merge with existing `User`.

**Step 2: Add `AuthBridgeCode` model**
```prisma
model AuthBridgeCode {
  id        String   @id @default(cuid())
  code      String   @unique
  userId    String
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  jwt       String
  expiresAt DateTime
  usedAt    DateTime?
  createdAt DateTime @default(now())

  @@index([expiresAt])
}
```

**Step 3: Remove Better Auth fields**
Remove `User.legacyAuthId`.

**Step 4: Run migration**
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trail?schema=public \
pnpm --filter @trail/db prisma migrate dev --name betterauth
pnpm --filter @trail/db prisma generate
```

**Step 5: Commit**
```bash
git add packages/db
git commit -m "Add BetterAuth schema and bridge codes"
```

---

### Task 4: Auth bridge in API

**Files:**
- Create: `apps/api/src/server/auth-bridge.ts`
- Create: `apps/api/app/v1/auth/bridge/exchange/route.ts`
- Test: `apps/api/app/v1/__tests__/auth-bridge.test.ts`

**Step 1: Test (failing)**
Test exchange returns 200 with snapshot and 404 on invalid code.

**Step 2: Implement service**
`auth-bridge.ts`:
- create code (used by auth service)
- exchange code → mark used → return JWT + user

**Step 3: Implement endpoint**
`POST /v1/auth/bridge/exchange`:
- accept `code`
- validate, return `AccountSnapshot` using `buildAccountSnapshot`

**Step 4: Run tests**
```bash
pnpm --filter @trail/api test
```

**Step 5: Commit**
```bash
git add apps/api
git commit -m "Add auth bridge exchange"
```

---

### Task 5: Replace Better Auth verification in API with BetterAuth JWT

**Files:**
- Modify: `apps/api/src/server/auth/user-auth.ts`
- Modify: `apps/api/.env.example`
- Modify: `apps/api/app/v1/auth/portal/[id]/approve/route.ts`
- Modify: `apps/api/app/v1/extension/connect/route.ts` (later in Task 6)

**Step 1: Update env**
Replace Better Auth vars with:
```
BETTER_AUTH_URL=https://auth.gettrail.net
```

**Step 2: Implement JWT verification**
Use JWKS from `BETTER_AUTH_URL + "/api/auth/jwks"` and `issuer/audience = BETTER_AUTH_URL`.
Keep return type `{ sub, email?, name?, picture? }` so `ensureUser` still works.

**Step 3: Update tests**
Adjust `user-auth` tests to use JWKS from mock.

**Step 4: Run tests**
```bash
pnpm --filter @trail/api test
```

**Step 5: Commit**
```bash
git add apps/api
git commit -m "Switch API user auth to BetterAuth JWT"
```

---

### Task 6: Implement extension connect flow endpoints

**Files:**
- Create: `apps/api/src/server/connect-sessions.ts`
- Create: `apps/api/app/v1/extension/connect/route.ts`
- Create: `apps/api/app/v1/extension/connect/[id]/route.ts`
- Create: `apps/api/app/v1/extension/connect/[id]/approve/route.ts`
- Test: `apps/api/app/v1/__tests__/extension-connect.test.ts`

**Step 1: Failing tests**
Cover `start → pending → approve` with JWT user auth and extension auth.

**Step 2: Implement session store**
Add `ExtensionConnectSession` model in Prisma if missing.

**Step 3: Implement endpoints**
- start: user JWT required
- poll: user JWT required
- approve: extension JWT required

**Step 4: Run tests**
```bash
pnpm --filter @trail/api test
```

**Step 5: Commit**
```bash
git add apps/api packages/db
git commit -m "Add extension connect flow"
```

---

### Task 7: Devices + settings endpoints

**Files:**
- Create: `apps/api/app/v1/devices/route.ts`
- Create: `apps/api/app/v1/devices/claim/route.ts`
- Create: `apps/api/app/v1/devices/[id]/revoke/route.ts`
- Create: `apps/api/app/v1/account/settings/route.ts`
- Test: `apps/api/app/v1/__tests__/devices.test.ts`

**Steps:**
- Write tests for claim/list/revoke/settings.
- Implement using `apps/api/src/server/devices.ts`.
- Run tests and commit.

---

### Task 8: Trails endpoints + sync

**Files:**
- Create: `apps/api/app/v1/trails/sync/route.ts`
- Create: `apps/api/app/v1/trails/route.ts`
- Create: `apps/api/app/v1/trails/[id]/route.ts`
- Create: `apps/api/app/v1/trails/[id]/restore/route.ts`
- Test: `apps/api/app/v1/__tests__/trails.test.ts`

**Steps:**
- Add tests for sync + CRUD.
- Implement with `apps/api/src/server/trails-sync.ts`.
- Run tests and commit.

---

### Task 9: Account snapshot + billing endpoints

**Files:**
- Create: `apps/api/app/v1/account/snapshot/route.ts`
- Create: `apps/api/app/v1/billing/route.ts`
- Create: `apps/api/app/v1/billing/portal/route.ts`
- Create: `apps/api/app/v1/subscription/route.ts`
- Create: `apps/api/app/v1/subscription/checkout/route.ts`
- Test: `apps/api/app/v1/__tests__/account.test.ts`

**Steps:**
- Use `buildAccountSnapshot` and existing billing logic (if any).
- Add tests for snapshot status guest/authenticated.
- Run tests and commit.

---

### Task 10: Update account app to BetterAuth

**Files:**
- Remove: `apps/account/src/lib/auth.ts`
- Modify: `apps/account/proxy.ts`
- Modify: `apps/account/app/page.tsx`
- Modify: `apps/account/app/(app)/extension/page.tsx`
- Modify: `apps/account/app/(app)/settings/page.tsx`
- Modify: `apps/account/app/api/trpc/[trpc]/route.ts`
- Create: `apps/account/src/lib/auth.ts`
- Create: `apps/account/app/auth/callback/route.ts`
- Modify: `apps/account/.env.example`

**Steps:**
- `auth.ts` reads JWT from cookie and returns session.
- `proxy.ts` checks JWT cookie and redirects to `auth.gettrail.net/login`.
- `auth/callback` exchanges code via `/v1/auth/bridge/exchange`, sets cookie.
- Remove Better Auth references.
- Update settings page links (Better Auth profile link removal).
- Run `pnpm --filter @trail/account typecheck`.
- Commit.

---

### Task 11: Update extension to new auth flow

**Files:**
- Modify: `extension/...` (login flow)

**Steps:**
- Ensure extension uses `/v1/auth/portal` and polls `/v1/auth/portal/{id}`.
- When approved, store JWT and use as `Authorization: Bearer` for API.
- Run extension tests if present (`npm test`).
- Commit.

---

### Task 12: Remove legacy internal routes + Better Auth references

**Files:**
- Remove: `apps/api/app/api/internal/extension/*` (login code, portal)
- Remove: `apps/account/src/server/internal-api.ts` usage for auth.
- Remove: `TRAIL_INTERNAL_API_KEY` usage where no longer needed.
- Update `.env.example` files to drop Better Auth vars.

**Steps:**
- Delete internal routes and dependent code.
- Run typecheck/tests.
- Commit.

---

### Task 13: Final verification

**Steps:**
- `pnpm --filter @trail/api test`
- `pnpm --filter @trail/account typecheck`
- `pnpm --filter @trail/auth typecheck`
- Commit any remaining changes.

---

Plan complete. Two execution options:
1. **Subagent-Driven (this session)** — I dispatch fresh subagent per task, review between tasks.
2. **Parallel Session (separate)** — Open new session with executing-plans, batch execution with checkpoints.

Which approach?
