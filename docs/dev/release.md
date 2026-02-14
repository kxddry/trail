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

# minimal env for Prisma + account runtime
export DATABASE_URL='postgresql://postgres:postgres@localhost:5432/trail_ci'
export TRAIL_EXTENSION_JWT_SECRET='test-extension-secret'
export WAITLIST_PROVIDER_ENDPOINT='http://localhost:3001/api/v1/waitlist'
export WAITLIST_PROVIDER_TOKEN='test-waitlist-token'

# Auth/billing placeholders required at build time
export BETTER_AUTH_URL='http://localhost:3001'
export BETTER_AUTH_SECRET='0123456789abcdef0123456789abcdef'
export BETTER_AUTH_TRUSTED_ORIGINS='http://localhost:3001'
export AUTH_BRIDGE_DEFAULT_RETURN_TO='http://localhost:3001'
export GOOGLE_CLIENT_ID='test-google-client-id'
export GOOGLE_CLIENT_SECRET='test-google-client-secret'
export APP_BASE_URL='http://localhost:3001'
export BILLING_PROVIDER='manual'
export BILLING_TEST_MODE='1'
export NOWPAYMENTS_API_KEY=''
export NOWPAYMENTS_IPN_SECRET=''
export NOWPAYMENTS_API_BASE_URL=''

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
npm ci
npm test
npm run build
```

### Package for upload
The Chrome Web Store expects a zip of the built extension (typically `dist/`).

```bash
cd extension
VERSION=$(node -p "require('./public/manifest.json').version")
cd dist
zip -r "../trail-extension-${VERSION}.zip" .
```

Checklist:
- [ ] Bump `extension/public/manifest.json` version as needed
- [ ] `npm test` passes
- [ ] `npm run build` produces `extension/dist/`
- [ ] Upload the `trail-extension-<version>.zip` to the Chrome Web Store
- [ ] After publish, install/update and sanity check:
  - [ ] extension loads
  - [ ] background/service worker starts
  - [ ] side panel opens

---

## Notes
- CI runs the same commands as the “Local build sanity check” sections above.
- The CI workflows live in `.github/workflows/`.
