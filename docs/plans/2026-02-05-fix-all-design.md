# Fix-All Design (Account + API + Packages)

**Goal:** Make the entire project green by fixing all current problems (build/test/typecheck/lint/format), then align touched areas with Vercel best practices, Next.js best practices, Better Auth best practices, and security best practices.

## Scope and Success Criteria
- Run and fix issues for: `pnpm -r lint`, `pnpm -r format`, `pnpm -r typecheck`, `pnpm -r test`, `pnpm -r build`.
- Apply `vercel-composition-patterns` and `vercel-react-best-practices` when touching component code or data flows.
- Apply `next-best-practices` for App Router / route handlers / RSC boundaries / async API usage.
- Apply `better-auth-best-practices` to any Better Auth-related config or flows.
- Perform a security audit and generate `security_best_practices_report.md`, then fix findings one by one.

## Order of Execution
1. **Stabilize:** Fix build/typecheck/test blockers first, then lint/format.
2. **Optimize & Architecture:** Address Vercel best-practice violations in touched code (no sweeping refactors).
3. **Security:** Active audit, report with evidence, then fix each finding individually.

## Database / Migrations
- Use local Postgres in Docker. It is safe to drop local DBs/volumes.
- Process: `docker compose up -d postgres`, set `DATABASE_URL`, run Prisma generate/migrations.
- Do not rewrite migration history unless explicitly requested.

## Testing Strategy
- Use TDD for fixes: write failing test, confirm failure, implement minimal fix, confirm pass.
- Re-run relevant test suite after each fix; full suite before finalization.

## Security Audit Deliverable
- Create `security_best_practices_report.md` with: rule ID, severity, file/line, evidence, impact, fix, mitigation, false-positive notes.
- Fix findings one at a time in separate commits.

## Risks and Mitigations
- Dirty local DB state: drop and re-create.
- Vite tests failing on `server-only`: add test-only alias/mock to keep server-only code isolated.
- Prisma model mismatches: resolve through schema or client generation, avoid unsafe workarounds.

## Completion Criteria
- All root commands pass.
- Best-practice violations addressed in touched code.
- Security report complete and all findings fixed (after confirmation).
