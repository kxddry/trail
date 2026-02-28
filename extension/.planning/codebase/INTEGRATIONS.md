# External Integrations

**Analysis Date:** 2026-02-28

## APIs & External Services

**Backend API (Trail Server):**
- Service: Custom REST API at `https://app.gettrail.net` (production) or configurable URL
- What it's used for: User authentication, account management, tree sync, billing
- SDK/Client: Native fetch-based HTTP client in `src/background/services/sync/api.ts`
- Auth: Bearer token authentication via OAuth 2.0
- Configuration: `src/shared/config/backend.ts` with environment switching (production/staging/local)

**OAuth 2.0 (Auth):**
- Provider: Trail backend with PKCE flow
- Endpoints used:
  - `POST /oauth/authorize` - Initiate authorization
  - `POST /oauth/token` - Exchange code for access/refresh tokens
  - `POST /oauth/revoke` - Revoke tokens on logout
- Device ID: Generated per extension installation, stored in `chrome.storage.local`
- Token storage: `AUTH_STORAGE_KEY` in Chrome storage with expiry tracking

**Billing & Subscription:**
- Service: Stripe (via Trail backend)
- Endpoints: `/subscription/checkout`, `/billing/portal`
- Functionality: Checkout creation, billing portal generation
- No direct Stripe SDK - all proxied through Trail backend

## Data Storage

**Local Storage:**
- Chrome storage.local: Primary persistent storage for all extension state
  - Trees (navigation data): Base64-encoded Uint8Array blobs with compression (fflate)
  - Authentication tokens: OAuth session with access/refresh tokens and expiry
  - Tags: Stored in `chrome.storage.sync` for cross-device sync
  - Settings: User preferences (theme, performance, UI state)
  - Archives: Old tree snapshots with LRU eviction
  - Flags: Feature flags from backend

**Server Storage:**
- Trail backend - PostgreSQL or equivalent (assumed, not direct access)
  - Tree metadata and full tree payloads
  - User accounts and subscription data
  - Device-to-user mappings

**Caching:**
- Memory caches:
  - `faviconTextureCache` in `GraphPixiRenderer.ts` - Loaded Pixi textures for favicons
  - `faviconLoadPromises` - Dedup concurrent favicon loads
  - React Query caches - Account snapshots, subscription state, tree metadata
  - `SNAPSHOT_CACHE_KEY` - Local snapshot with fetch timestamp

**Archive Storage:**
- Compressed tree backups in `chrome.storage.local` with quota management
- Key: `trail_tree_archives_{treeId}`
- Serialization: Base64-encoded fflate-compressed NavigationTreeJSON

## Authentication & Identity

**Auth Provider:**
- Trail backend OAuth 2.0 server
- Implementation: PKCE-based authorization code flow for MV3 extension
  - `POST /oauth/authorize` for user consent
  - Code exchange in background worker (secure, non-interactive)
  - Automatic refresh token rotation
  - Token expiry monitoring with early refresh (30s buffer)

**Session Management:**
- Storage: `AUTH_STORAGE_KEY` in `chrome.storage.local`
  - `accessToken` - Bearer token for API requests
  - `refreshToken` - For silent token refresh
  - `expiresAt` - ISO timestamp of expiry
- Refresh interval: 2-minute alarms (`AUTH_REFRESH_ALARM`)
- Auto-logout on failed refresh or expired refresh token

**Device ID:**
- Generated per installation: `crypto.randomUUID()` or fallback
- Stored: `DEVICE_ID_STORAGE_KEY` in `chrome.storage.local`
- Sent with OAuth flow for device tracking/management

## Monitoring & Observability

**Error Tracking:**
- Not detected - No Sentry, LogRocket, or similar integration

**Logging:**
- Console-based, intentionally silent in production
- Local debugging: Uncomment logs in `account-keeper.ts`, `auth-orchestrator.ts`
- No centralized logging backend

**Network Monitoring:**
- Error types defined in `SyncApiError` with classification:
  - `unauthorized` (401) - Auth failure, triggers re-login
  - `feature_locked` - Subscription/plan restriction
  - `not_found` (404) - Resource deleted
  - `network` - Connection error, retryable
  - `timeout` - Request exceeded 10s default
  - `server_error` - 5xx errors, retryable
  - `invalid_response` - Parsing failure

## CI/CD & Deployment

**Hosting:**
- Browser extension distributed via:
  - Chrome Web Store (MV3 builds)
  - Firefox Add-ons (MV2 builds)

**Build Output:**
- `.output/chrome-mv3/` - Production Chrome build
- `.output/chrome-mv3-dev/` - Development Chrome build
- `.output/firefox-mv2/` - Firefox build
- `.output/trail-{version}-chrome` - Versioned archives for distribution

**CI Pipeline:**
- Not detected in codebase (assumes external CI)
- Build commands:
  - `pnpm run build` - Production build (production backend preset)
  - `pnpm run build:local` - Local development backend
  - `pnpm run build:gettrail` - Staging/gettrail backend
  - `pnpm run zip` - Generate distribution zip

## Environment Configuration

**Required env vars:**
- None directly in .env files (not committed to repo)
- Backend endpoint configuration: `src/shared/config/backend.ts`
- Default: `https://app.gettrail.net` production
- Build preset: `backend-preset.json` for tag-based override ('production', 'gettrail', 'local')

**Secrets location:**
- Chrome storage (user's local machine) - NOT version controlled
- No .env files in repository
- Runtime configuration via `initBackendConfig()` async initialization

**Configuration Scripts:**
- `scripts/backend-preset.mjs` - Generates/manages `backend-preset.json`
  - `node scripts/backend-preset.mjs status` - Show current preset
  - `node scripts/backend-preset.mjs local` - Switch to local backend
  - `node scripts/backend-preset.mjs gettrail` - Switch to staging backend

## Webhooks & Callbacks

**Incoming:**
- Not detected - Extension receives no webhooks

**Outgoing:**
- Not detected - No webhook deliveries to external services

**Message Passing:**
- Internal: Chrome messaging between content scripts, background, UI panels
- RPC contracts: `src/shared/rpc/contracts.ts` defines all handler interfaces
- No external webhook integrations

## Content Security Policy

**CSP Requirements (MV3):**
- `unsafe-eval` NOT allowed in manifest, but:
  - Pixi.js requires eval for shader compilation
  - Workaround: `pixi.js/unsafe-eval` polyfill at `src/sidepanel/ui/graph/pixi-no-eval-bootstrap.ts`
  - Enables WebGL without CSP violations

**Allowed External Hosts:**
- `https://app.gettrail.net` (production API)
- Localhost variants (dev: `http://localhost:3001`)
- Favicon hosts: Dynamically determined from visited sites (`chrome.storage.sync`)

## Third-Party Metrics/Analytics

- Not detected - No Segment, Mixpanel, Google Analytics, or similar

## API Rate Limits

- Not specified in code - Assumed handled by Trail backend
- Default timeout: 10 seconds (`timeoutMs: 10000` in backend config)

---

*Integration audit: 2026-02-28*
