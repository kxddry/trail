# Release checklist

This repo ships **three Next.js apps** (marketing/account/api) plus a **browser extension**.

The goal of this checklist is to make releases repeatable and to avoid regressions.

## Pre-flight
- [ ] `git fetch origin --prune`
- [ ] Ensure you’re on the intended branch + clean tree: `git status`
- [ ] Run the relevant CI commands locally (below)

---

## Web apps (marketing/account/api)

### Local build sanity check
From repo root:

```bash
pnpm install --frozen-lockfile

# minimal env for Prisma + internal API helpers
export DATABASE_URL='postgresql://postgres:postgres@localhost:5432/trail_ci'
export TRAIL_API_BASE_URL='http://localhost:3002'
export TRAIL_INTERNAL_API_KEY='ci'
export TRAIL_AUTH_BASE_URL='http://localhost:3003'
export TRAIL_EXTENSION_JWT_SECRET='test-extension-secret'
export WAITLIST_PROVIDER_ENDPOINT='http://localhost:3999/waitlist'
export WAITLIST_PROVIDER_TOKEN='test-waitlist-token'

# API auth/billing placeholders required at build time
export BETTER_AUTH_URL='http://localhost:3003'
export BETTER_AUTH_SECRET='0123456789abcdef0123456789abcdef'
export APP_BASE_URL='http://localhost:3001'
export BILLING_PROVIDER='stub' # switch to 'nowpayments' when integration is ready

pnpm --filter @trail/marketing --filter @trail/account --filter @trail/api typecheck
pnpm --filter @trail/marketing --filter @trail/account --filter @trail/api build
```

### Deploy
Deployment is environment-specific (Vercel / Docker / etc). At minimum:
- [ ] Deploy `apps/marketing` → `gettrail.net`
- [ ] Deploy `apps/account` → `app.gettrail.net`
- [ ] Deploy `apps/api` → `api.gettrail.net`
- [ ] Verify `TRAIL_API_BASE_URL` and `TRAIL_INTERNAL_API_KEY` match between account+api.

Smoke checks:
- [ ] `gettrail.net` loads, navigation works
- [ ] `app.gettrail.net` loads (login page renders)
- [ ] `api.gettrail.net` responds (and rejects missing/incorrect internal key when relevant)

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
