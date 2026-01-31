# Release checklist

## Database / Prisma
- Ensure `packages/db/prisma/migrations/` is present and committed (migrations are required for `prisma migrate deploy`).
- Ensure a connection string is available as `DATABASE_URL` (or `POSTGRES_PRISMA_URL` / `POSTGRES_URL`, which are mapped to `DATABASE_URL` by `packages/db/prisma.config.ts`).
- Generate client:
  - `pnpm db:generate`
- Apply migrations in the deploy environment:
  - `pnpm --filter @trail/db prisma migrate deploy`
