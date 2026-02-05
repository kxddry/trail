# Prisma Build Script Fix (Design)

## Summary
Remove per-app `prisma generate` calls and move Prisma client generation to a single root-level step so parallel builds cannot race on `packages/db/src/generated`. This avoids `EEXIST` errors during `pnpm -r build`.

## Goals
- Eliminate `prisma generate` race conditions.
- Keep build commands parallelizable.
- Make Prisma generation explicit and centralized.

## Non-Goals
- Changing Prisma schema or migrations.
- Altering runtime DB access patterns.

## Approach
1. Keep the root script `db:generate` as the single entry point for Prisma client generation.
2. Update root `build` to run `db:generate` first, then run `pnpm -r build`.
3. Remove `pnpm --filter @trail/db prisma generate` from `apps/auth`, `apps/account`, and `apps/api` build scripts.

## Data Flow / Execution
- `pnpm run build`:
  - `pnpm run db:generate` (requires `DATABASE_URL`).
  - `pnpm -r build` for all apps, now free of Prisma generation.

## Error Handling
- If `DATABASE_URL` is missing, build fails early with a clear error.
- Per-app builds assume Prisma client is generated; developers can run `pnpm run db:generate` when needed.

## Testing
- `DATABASE_URL=... pnpm run build` should complete without Prisma generation errors.

## Rollout
- Change scripts and verify local build.
- Document expected usage in case developers build a single app directly.
