# Prisma Build Script Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Eliminate Prisma client generation races by running `prisma generate` once at the root before parallel app builds.

**Architecture:** Centralize Prisma client generation in the root `build` script (`db:generate`), and remove per-app `prisma generate` calls from `apps/auth`, `apps/account`, and `apps/api` build scripts. Builds then run in parallel without touching `packages/db/src/generated`.

**Tech Stack:** pnpm workspaces, Prisma, Next.js.

---

### Task 1: Reproduce the Race (Baseline)

**Files:** none

**Step 1: Run the failing build (baseline)**

Run:
```
DATABASE_URL=postgres://postgres:postgres@localhost:5432/trail \
BETTER_AUTH_SECRET=devdevdevdevdevdevdevdevdevdevdevdev \
BETTER_AUTH_URL=http://localhost:3001 \
pnpm -r build
```
Expected: **FAIL** with `EEXIST` in `packages/db/src/generated/models` (race from parallel `prisma generate`).

**Step 2: Note the error location**

Confirm error references Prisma generate in `@trail/db` during `apps/account` or `apps/api` build.

---

### Task 2: Centralize Prisma Generation

**Files:**
- Modify: `package.json`

**Step 1: Update root build script**

Change `build` to run `db:generate` first, then `pnpm -r build`.

**Step 2: Run format (if needed)**

Run:
```
pnpm -r format
```
Expected: PASS.

**Step 3: Commit**

```
git add package.json

git commit -m "Centralize prisma generate in root build"
```

---

### Task 3: Remove Per-App Prisma Generate

**Files:**
- Modify: `apps/auth/package.json`
- Modify: `apps/account/package.json`
- Modify: `apps/api/package.json`

**Step 1: Update build scripts**

Remove `pnpm --filter @trail/db prisma generate &&` from each app’s `build` script.

**Step 2: Run format (if needed)**

Run:
```
pnpm -r format
```
Expected: PASS.

**Step 3: Run build to verify**

Run:
```
DATABASE_URL=postgres://postgres:postgres@localhost:5432/trail \
BETTER_AUTH_SECRET=devdevdevdevdevdevdevdevdevdevdevdev \
BETTER_AUTH_URL=http://localhost:3001 \
pnpm run build
```
Expected: **PASS** (no Prisma `EEXIST`).

**Step 4: Commit**

```
git add apps/auth/package.json apps/account/package.json apps/api/package.json

git commit -m "Remove per-app prisma generate"
```

---

### Task 4: Verification (Full)

**Files:** none

**Step 1: Lint/typecheck/test/build**

Run:
```
pnpm -r lint
pnpm -r typecheck
pnpm -r test
DATABASE_URL=postgres://postgres:postgres@localhost:5432/trail \
BETTER_AUTH_SECRET=devdevdevdevdevdevdevdevdevdevdevdev \
BETTER_AUTH_URL=http://localhost:3001 \
pnpm run build
```
Expected: PASS.

**Step 2: Commit if any incidental changes**

```
git status -sb
```
Commit any incidental formatting changes if required.
