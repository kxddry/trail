# Release checklist

This repo ships **two Next.js apps** (marketing/account) plus a **browser extension**.

The goal of this checklist is to make releases repeatable and to avoid regressions.

## Pre-flight
- [ ] `git fetch origin --prune`
- [ ] Ensure you’re on the intended branch + clean tree: `git status`
- [ ] Run the relevant CI commands locally (below)

---

## Web apps (marketing/account)

### Local build sanity check
From repo root:

```bash
pnpm install --frozen-lockfile

# Minimal env for Prisma + account runtime (mirrors CI).
# These do NOT need to point to a real database for typecheck/build.
export DATABASE_URL='postgresql://postgres:postgres@localhost:5432/trail_ci'
export TRAIL_EXTENSION_JWT_SECRET='test-extension-secret'

# Auth/billing placeholders required at build time
export BETTER_AUTH_SECRET='0123456789abcdef0123456789abcdef'
export GOOGLE_CLIENT_ID='test-google-client-id'
export GOOGLE_CLIENT_SECRET='test-google-client-secret'
export BILLING_PROVIDER='manual'
export BILLING_TEST_MODE='1'
export NOWPAYMENTS_API_KEY=''
export NOWPAYMENTS_IPN_SECRET=''
export NOWPAYMENTS_API_BASE_URL=''
export NEXT_PUBLIC_APP_URL='http://localhost:3001'

pnpm --filter @trail/marketing --filter @trail/account typecheck
pnpm --filter @trail/marketing --filter @trail/account build
```

### Deploy
Deployment is environment-specific (Vercel / Docker / etc). At minimum:
- [ ] Deploy `apps/marketing` → `gettrail.net`
- [ ] Deploy `apps/account` → `app.gettrail.net`

Smoke checks:
- [ ] `gettrail.net` loads, navigation works
- [ ] `app.gettrail.net` loads (login page renders)

---

## Extension

### Local test/build
From repo root:

```bash
cd extension
pnpm install --frozen-lockfile
pnpm test
pnpm run build
```

### Package for upload
The Chrome Web Store expects a zip of the built extension. WXT provides a `zip` script:

```bash
cd extension
pnpm run zip
```

Checklist:
- [ ] Bump extension version as needed
- [ ] `pnpm test` passes
- [ ] `pnpm run build` succeeds
- [ ] `pnpm run zip` produces the zip artifact
- [ ] Upload the zip to the Chrome Web Store
- [ ] After publish, install/update and sanity check:
  - [ ] extension loads
  - [ ] background/service worker starts
  - [ ] side panel opens

---

## Notes
- CI runs the same commands as the “Local build sanity check” sections above.
- The CI workflows live in `.github/workflows/`.
