# Trail CI/CD & Infrastructure Audit

**Date:** 2026-02-25
**Auditor:** DevOps Engineer (automated)
**Scope:** CI/CD pipelines, infrastructure, developer experience, security posture

---

## 1. Current State Inventory

### 1.1 Repository Structure

Monorepo managed by pnpm workspaces (`pnpm@10.29.3`):

| Component | Path | Framework | Has Tests | Has Lint | Has Typecheck |
|-----------|------|-----------|-----------|----------|---------------|
| Marketing app | `apps/marketing/` | Next.js 16 | No | Yes (`eslint .`) | Yes (`tsc --noEmit`) |
| Account app | `apps/account/` | Next.js 16 | Yes (vitest) | Yes (`eslint .`) | Yes (`tsc --noEmit`) |
| Browser extension | `extension/` | WXT + Vite | Yes (node:assert) | Configured | Yes (2 tsconfigs) |
| DB package | `packages/db/` | Prisma 7 | No | No | No |
| tRPC package | `packages/trpc/` | tRPC 11 | No | No | No |
| UI package | `packages/ui/` | React 19 | No | No | No |
| Content package | `packages/content/` | Plain TS | No | No | No |
| Config package | `packages/config/` | N/A | No | No | No |
| Sanity CMS | `sanity/` | Sanity Studio | No | Configured | No |

### 1.2 Existing CI/CD Workflows

#### `.github/workflows/ci-web.yml`
- **Triggers:** PR + push to `main` (path-filtered to `apps/**`, `packages/**`, lockfile)
- **Concurrency:** Cancels in-progress runs per branch
- **Steps:** Install -> Typecheck (marketing + account) -> Build (marketing) -> Build (account)
- **Environment:** Placeholder secrets for build-time env checks

#### `.github/workflows/ci-extension.yml`
- **Triggers:** PR + push to `main` (path-filtered to `extension/**`)
- **Concurrency:** Cancels in-progress runs per branch
- **Steps:** Install -> Test (`pnpm test`) -> Build (`pnpm build`)

#### `.github/workflows/neon-workflow.yml`
- **Triggers:** PR (opened/reopened/synchronize/closed)
- **Steps:** Create Neon preview branch -> Run migrations -> Schema diff comment on PR -> Delete branch on close
- **Permissions:** `contents: read`, `pull-requests: write`

### 1.3 Infrastructure

- **Database:** Neon (production), local Docker Postgres 18 (`docker-compose.yml`) for dev
- **Hosting:** Vercel (marketing + account are Next.js apps with Vercel-specific config in `next.config.mjs`)
- **CMS:** Sanity (headless CMS for marketing content)
- **Extension:** WXT-based Chrome extension, no automated publishing
- **E2E:** Cypress configured but minimal (1 smoke test for marketing landing page)

---

## 2. Critical Findings

### 2.1 CRITICAL: Production Secrets Committed to Repo

**File:** `/Users/iv/dev/trail/.env.prod`

This file contains **live production credentials** committed to the repository:
- `DATABASE_URL` with real Supabase pooler connection string and password
- `BETTER_AUTH_SECRET` (256-bit hex key)
- `TRAIL_EXTENSION_JWT_SECRET` (256-bit hex key)
- `SANITY_REVALIDATE_SECRET`

**Additionally**, `/Users/iv/dev/trail/.env.e2e` contains what appear to be real Google OAuth credentials:
- `GOOGLE_CLIENT_ID` (real format: `903791543680-...`)
- `GOOGLE_CLIENT_SECRET` (real format: `GOCSPX-...`)

**Risk:** Any contributor, any fork, any CI log leak exposes the entire production database and auth system.

**Immediate Action Required:**
1. Rotate ALL secrets in `.env.prod` and `.env.e2e` immediately
2. Remove these files from the repository and git history (`git filter-repo`)
3. Move secrets to GitHub Secrets / Vercel environment variables exclusively
4. Add `.env.prod` and `.env.e2e` to `.gitignore` (they are partially covered by `.env.*` pattern already, but these files still exist in the repo)

### 2.2 HIGH: No Lint Step in CI (Web)

`ci-web.yml` runs typecheck and build but **never runs `pnpm lint`**. The root `package.json` has a `lint` script, and both `apps/marketing` and `apps/account` have `eslint .` configured. ESLint is installed with the `eslint-config-next` ruleset (catches accessibility, React, and web vitals issues).

Code can merge with lint violations that include security-relevant patterns (e.g., `dangerouslySetInnerHTML` usage, missing `rel="noopener"`).

### 2.3 HIGH: No Unit Tests in CI (Web)

`ci-web.yml` does **not** run `pnpm test`. The account app has vitest configured with client (jsdom) and server (node) test projects, but tests are never executed in CI. The root `package.json` has `"test": "pnpm -r test"` which would cascade to all packages.

### 2.4 HIGH: No Dependency Vulnerability Scanning

No `dependabot.yml`, no `npm audit` step in CI, no Snyk/Socket/Renovate integration. The monorepo has hundreds of transitive dependencies across 5+ `node_modules` trees. A single vulnerable dependency in production could go undetected indefinitely.

### 2.5 MEDIUM: No Format Checking in CI

Both `apps/marketing` and `apps/account` have `"format": "prettier --check ."` but this is never run in CI. Formatting drift will accumulate across contributors.

### 2.6 MEDIUM: Extension CI Has No Typecheck

`ci-extension.yml` runs `pnpm test` and `pnpm build` but **never runs `pnpm typecheck`**. The extension has two TypeScript configs (`tsconfig.json` and `tsconfig.app.json`) and a dedicated typecheck script. Type errors in the extension could ship undetected if the build step does not surface them (WXT builds may skip type checking).

### 2.7 MEDIUM: No E2E Tests in CI

Cypress is installed at the root with one test (`cypress/e2e/marketing.cy.ts`), but there is no CI workflow to run it. E2E tests would require a running Next.js server, which is not set up.

### 2.8 LOW: Docker Compose Volume Path Issue

```yaml
volumes:
  - pgdata:/var/lib/postgresql/18/docker
```

The default PostgreSQL data directory in the `postgres:18-alpine` image is `/var/lib/postgresql/data`, not `/var/lib/postgresql/18/docker`. This may cause data to be written to a non-persistent path while the named volume mounts empty.

---

## 3. Missing CI/CD Workflows

### 3.1 Dependency Vulnerability Scanning

**Create:** `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      production-deps:
        dependency-type: "production"
      dev-deps:
        dependency-type: "development"
        update-types: ["minor", "patch"]
    open-pull-requests-limit: 10

  - package-ecosystem: "npm"
    directory: "/extension"
    schedule:
      interval: "weekly"
    groups:
      extension-deps:
        patterns: ["*"]
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 3.2 Security Audit Workflow

**Create:** `.github/workflows/security.yml`

```yaml
name: Security Audit

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1"  # Weekly Monday 6am UTC

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 10.29.3

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Audit root workspace
        run: pnpm audit --prod
        continue-on-error: true

      - name: Audit extension
        run: cd extension && pnpm audit --prod
        continue-on-error: true

      - name: Check for leaked secrets
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

### 3.3 Release & Extension Publishing Automation

**Create:** `.github/workflows/release-extension.yml`

```yaml
name: Release Extension

on:
  push:
    tags:
      - "extension-v*"

concurrency:
  group: release-extension
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: extension
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 10.29.3

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
          cache-dependency-path: extension/pnpm-lock.yaml

      - name: Install
        run: pnpm install --frozen-lockfile

      - name: Test
        run: pnpm test

      - name: Typecheck
        run: pnpm typecheck

      - name: Build production
        run: pnpm build:gettrail

      - name: Package zip
        run: pnpm zip

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: extension-${{ github.ref_name }}
          path: extension/.output/*.zip

      - name: Create GitHub release
        uses: softprops/action-gh-release@v2
        with:
          files: extension/.output/*.zip
          generate_release_notes: true

      # Uncomment when Chrome Web Store credentials are configured:
      # - name: Publish to Chrome Web Store
      #   uses: nicolo-ribaudo/chroma-extension@v1
      #   with:
      #     zip-path: extension/.output/trail-chrome-mv3.zip
      #     extension-id: ${{ secrets.CHROME_EXTENSION_ID }}
      #     client-id: ${{ secrets.CHROME_CLIENT_ID }}
      #     client-secret: ${{ secrets.CHROME_CLIENT_SECRET }}
      #     refresh-token: ${{ secrets.CHROME_REFRESH_TOKEN }}
```

### 3.4 PR Auto-labeling

**Create:** `.github/labeler.yml` + workflow

```yaml
# .github/labeler.yml
extension:
  - changed-files:
      - any-glob-to-any-file: "extension/**"

web:
  - changed-files:
      - any-glob-to-any-file: "apps/**"

database:
  - changed-files:
      - any-glob-to-any-file: "packages/db/**"

ui:
  - changed-files:
      - any-glob-to-any-file: "packages/ui/**"

ci:
  - changed-files:
      - any-glob-to-any-file: ".github/**"

dependencies:
  - changed-files:
      - any-glob-to-any-file:
          - "**/pnpm-lock.yaml"
          - "**/package.json"
```

**Create:** `.github/workflows/labeler.yml`

```yaml
name: Label PRs

on:
  pull_request_target:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

---

## 4. Recommended Changes to Existing Workflows

### 4.1 Enhanced `ci-web.yml`

**File:** `.github/workflows/ci-web.yml` -- add lint, test, and format steps:

```yaml
      # After Install step, add:

      - name: Lint
        run: pnpm lint

      - name: Format check
        run: pnpm format

      - name: Test
        run: pnpm test

      # Existing typecheck and build steps follow
```

### 4.2 Enhanced `ci-extension.yml`

**File:** `.github/workflows/ci-extension.yml` -- add typecheck step:

```yaml
      # After Install step, before Test:

      - name: Typecheck
        run: pnpm typecheck

      # Existing Test and Build steps follow
```

### 4.3 Neon Workflow Hardening

The `neon-workflow.yml` is well-structured, but should pin action versions to SHA for supply chain security:

```yaml
# Instead of:
uses: neondatabase/create-branch-action@v6
# Use:
uses: neondatabase/create-branch-action@v6  # pin to SHA when deploying
```

Also add a migration validation step that verifies migrations are reversible or at minimum runs `prisma validate` on the schema.

---

## 5. Developer Experience Gaps

### 5.1 No Pre-commit Hooks

There is no `.husky/` directory, no `lint-staged` configuration, and no pre-commit hook setup. Developers can push code that fails lint/typecheck/format without knowing until CI fails (or never, since lint is not in CI).

**Recommendation:** Install husky + lint-staged:

```bash
pnpm add -Dw husky lint-staged
pnpm exec husky init
```

Add to root `package.json`:

```json
{
  "lint-staged": {
    "apps/**/*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "packages/**/*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "extension/src/**/*.{ts,tsx}": ["prettier --write"]
  }
}
```

### 5.2 No PR Template

No `.github/PULL_REQUEST_TEMPLATE.md` exists. PRs lack structure for reviewers.

**Create:** `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## What

<!-- Brief description of the change -->

## Why

<!-- Motivation, link to issue if applicable -->

## Testing

- [ ] Unit tests added/updated
- [ ] Tested locally
- [ ] Extension tested (if applicable)

## Checklist

- [ ] Types pass (`pnpm typecheck`)
- [ ] Lint passes (`pnpm lint`)
- [ ] No new secrets committed
```

### 5.3 No Issue Templates

No `.github/ISSUE_TEMPLATE/` directory. Bug reports and feature requests lack structure.

### 5.4 No CONTRIBUTING.md

No contributing guidelines at the repo root. Onboarding new developers requires tribal knowledge.

---

## 6. Infrastructure Concerns

### 6.1 Environment Variable Management

| Concern | Status |
|---------|--------|
| `.env.example` files for dev setup | Partial (account, marketing, db have them) |
| Production secrets in env files | CRITICAL -- `.env.prod` committed with real secrets |
| Secret rotation process | None documented |
| Env validation at runtime | Some Next.js build-time checks via CI env vars |

**Recommendation:** Implement runtime env validation with `@t3-oss/env-nextjs` or similar. Ensure all required env vars are validated at startup, not just at build time.

### 6.2 Database Migration Safety

The Neon workflow handles preview branch creation and migration deployment well. However:

- No migration dry-run or validation step in `ci-web.yml`
- No protection against destructive migrations (column drops, table drops)
- No migration squashing strategy documented
- Only 1 migration exists (baseline), so this is not yet a scaling concern

### 6.3 Monitoring & Alerting

- **Vercel Analytics:** Installed in marketing app (`@vercel/analytics`)
- **Vercel Speed Insights:** Installed (`@vercel/speed-insights`)
- **Error tracking:** Not detected (no Sentry, Datadog, LogRocket, etc.)
- **Uptime monitoring:** Not detected
- **Database monitoring:** Relying on Neon dashboard (no custom alerting)

**Recommendation:** Add error tracking (Sentry is free tier compatible) and uptime monitoring at minimum.

### 6.4 Docker Compose

The `docker-compose.yml` is minimal (Postgres only) and appropriate for local dev. The volume mount path may be incorrect as noted in finding 2.8.

---

## 7. Security Posture Summary

| Area | Rating | Notes |
|------|--------|-------|
| Secret management | CRITICAL | Production secrets in repo |
| Dependency scanning | MISSING | No Dependabot, no audit |
| CI secret exposure | LOW | Placeholder values used in CI env |
| Supply chain (actions) | MEDIUM | Actions not pinned to SHA |
| Security headers | GOOD | Marketing app sets X-Frame-Options, CSP-adjacent headers |
| Auth security | GOOD | Extension has security audit tests, schema validation |
| CORS/Origin validation | GOOD | Origin allowlist tested |
| Database access | MEDIUM | Connection string in CI uses fake DB, but `.env.prod` is exposed |

---

## 8. Priority Action Plan

### P0 -- Do Immediately (today)
1. **Rotate all secrets** in `.env.prod` and `.env.e2e`
2. **Remove `.env.prod` from git history** using `git filter-repo` or BFG Repo-Cleaner
3. **Verify `.gitignore`** catches `.env.prod` and `.env.e2e` (the pattern `.env.*` should already match, but the files exist in the repo, meaning they were committed before the gitignore rule)

### P1 -- This Week
4. **Add lint + test steps to `ci-web.yml`** (see Section 4.1)
5. **Add typecheck to `ci-extension.yml`** (see Section 4.2)
6. **Create `.github/dependabot.yml`** (see Section 3.1)
7. **Create `.github/PULL_REQUEST_TEMPLATE.md`** (see Section 5.2)

### P2 -- This Sprint
8. **Set up pre-commit hooks** with husky + lint-staged (see Section 5.1)
9. **Create security audit workflow** (see Section 3.2)
10. **Create PR auto-labeling** (see Section 3.4)
11. **Fix Docker volume path** in `docker-compose.yml`
12. **Add error tracking** (Sentry or equivalent)

### P3 -- This Quarter
13. **Create extension release workflow** (see Section 3.3)
14. **Add E2E tests to CI** (requires Cypress + server startup in workflow)
15. **Implement runtime env validation** across all apps
16. **Set up code coverage reporting** (vitest coverage -> Codecov/Coveralls)
17. **Document secret rotation process**
18. **Add contributing guidelines**

---

## 9. Files Referenced

| File | Status |
|------|--------|
| `/Users/iv/dev/trail/.github/workflows/ci-web.yml` | Exists, needs lint + test steps |
| `/Users/iv/dev/trail/.github/workflows/ci-extension.yml` | Exists, needs typecheck step |
| `/Users/iv/dev/trail/.github/workflows/neon-workflow.yml` | Exists, well-structured |
| `/Users/iv/dev/trail/.github/dependabot.yml` | MISSING -- create |
| `/Users/iv/dev/trail/.github/PULL_REQUEST_TEMPLATE.md` | MISSING -- create |
| `/Users/iv/dev/trail/.github/labeler.yml` | MISSING -- create |
| `/Users/iv/dev/trail/.github/workflows/labeler.yml` | MISSING -- create |
| `/Users/iv/dev/trail/.github/workflows/security.yml` | MISSING -- create |
| `/Users/iv/dev/trail/.github/workflows/release-extension.yml` | MISSING -- create |
| `/Users/iv/dev/trail/.env.prod` | CRITICAL -- remove from repo |
| `/Users/iv/dev/trail/.env.e2e` | Contains real OAuth creds -- review |
| `/Users/iv/dev/trail/docker-compose.yml` | Volume path may be incorrect |
| `/Users/iv/dev/trail/package.json` | Root scripts for lint/test/typecheck exist |
| `/Users/iv/dev/trail/eslint.config.mjs` | Configured with next/core-web-vitals |
| `/Users/iv/dev/trail/apps/account/vitest.config.ts` | Well-configured with client/server projects |
| `/Users/iv/dev/trail/cypress.config.ts` | Minimal, 1 smoke test |
| `/Users/iv/dev/trail/extension/tests/basic.test.ts` | Comprehensive unit tests (node:assert based) |
| `/Users/iv/dev/trail/extension/tests/security-audit.test.ts` | Security-focused tests |
