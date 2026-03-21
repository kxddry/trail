# External Integrations

**Analysis Date:** 2026-03-18

## APIs & External Services

**Authentication:**
- Google OAuth 2.0 - Social login provider
  - SDK/Client: better-auth (wraps OAuth flow)
  - Config: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - Implementation: `apps/account/src/auth.ts` - Uses better-auth with prismaAdapter

**Sync API:**
- Trail backend sync endpoints (custom REST API)
  - Endpoints:
    - `POST /trails/sync` - Index sync (metadata-only delta)
    - `PUT /trails/:id` - Upsert single tree
    - `GET /trails/:id` - Fetch single tree
    - `DELETE /trails/:id` - Soft-delete tree
    - `PATCH /trails/:id` - Editor partial update
  - Client: `extension/src/background/services/sync/api.ts` - Typed HTTP client
  - Auth: Bearer token from `authSessionItem` (stored in chrome.storage.local)
  - Protocol: Fetch-based with error retry logic (backoff schedule: 2s, 4s, 8s, 16s, 32s, 60s)

**Payment Processing:**
- NOWPayments - Optional payment processor
  - SDK/Client: Custom HTTP client (no SDK)
  - Config: `NOWPAYMENTS_API_KEY`, `NOWPAYMENTS_IPN_SECRET`, `NOWPAYMENTS_API_BASE_URL`
  - Usage: Conditional based on `BILLING_PROVIDER` env var ("manual" or "nowpayments")
  - Test mode: Controlled via `BILLING_TEST_MODE` env var
  - Implementation: `apps/account/src/env.ts` defines provider selection

## Data Storage

**Databases:**
- PostgreSQL (primary)
  - Connection: `DATABASE_URL` env var
  - Client: Prisma 7.4.1 with @prisma/adapter-pg
  - Adapter: Native PostgreSQL support via pg driver
  - Connection pooling: Via @prisma/adapter-pg (Prisma accelerate when needed)
  - Database initialization: `packages/db/src/client.ts` - Validates database URL, creates pool, initializes PrismaClient
  - URL validation: Enforces postgres:// or postgresql:// protocol

**Local Storage (Extension):**
- Chrome Storage API
  - `chrome.storage.local` - Persistent cross-session storage for auth, tree data, settings, tags
  - `chrome.storage.session` - Session-scoped storage for graph layout positions
  - Stored items: Auth session, tree data, settings, tags, temporarily selected nodes, thumbnails
  - Storage managers: `extension/src/background/services/tree-storage.ts` (25.6K - main tree persistence)
  - Storage access: Wrapped by WXT storage utilities in `extension/src/shared/config/storage-items.ts`
  - Index: `archiveIndexItem` for tree metadata index with bulk operations via quota-aware manager
  - Quota management: Custom quota-aware storage in `extension/src/background/services/quota-manager.ts` prevents exceeding Chrome's 10MB per app limit

**File Storage:**
- Local filesystem only - No cloud file storage integration detected

**Caching:**
- TanStack React Query - Client-side data caching (via @tanstack/react-query)
- Sanity CDN - Content delivery for CMS assets (useCdn: true in Sanity client)
- Graph layout cache - Session storage for offscreen graph rendering positions
- No Redis or external cache service detected

## Authentication & Identity

**Auth Provider:**
- better-auth 1.4.19 - Custom authentication framework
  - Implementation: `apps/account/src/auth.ts`
  - Adapter: Prisma (stores sessions/users in PostgreSQL)
  - Social provider: Google OAuth
  - JWT plugin: Enabled with 30-day expiration for account app
  - Session storage: httpOnly cookies (bearer token for API calls)

**JWT:**
- Issuer: Account app at configured `APP_BASE_URL`
- Verification: Extension and API verify JWTs using JWKS from auth provider
  - Library: jose 6.1.3
  - Implementation: `apps/account/src/lib/auth.ts` - buildRemoteJWKSet pattern for verifying tokens from account app
  - Client-side JWT handling: jwt-decode 4.0.0

**Extension Auth:**
- Token storage: Chrome storage API
  - Key: `authSessionItem` (custom config item in `extension/src/shared/config/storage-items.ts`)
  - Lifetime: 30 days (from JWT expiration)
  - Storage area: `chrome.storage.local`
- Auth orchestration: `extension/src/background/services/auth-orchestrator.ts` (11.1K)
- Auth policy enforcement: `extension/src/background/services/auth-policy-keeper.ts` (2.6K)
- Feature gating: `TRAIL_EXTENSION_AUTH_REQUIRED` env var controls whether auth is enforced
- Device ID: Stored in `oauthDeviceIdItem` for OAuth device tracking

## Chrome Extension APIs

**Permissions & Manifest:**
- Permissions (defined in `extension/wxt.config.ts`):
  - `sidePanel` - Side panel UI support
  - `storage` - Local and session storage access
  - `tabs` - Tab management and querying
  - `webNavigation` - Navigation event tracking (for tree building)
  - `favicon` - Favicon fetching
  - `alarms` - Scheduled background tasks
  - `scripting` - Content script injection
  - `activeTab` - Access to active tab (limited scope)
  - `search` - Search engine access
  - `bookmarks` - Bookmark access
  - `offscreen` - Offscreen documents for background computation
- Host permissions: Configured match patterns in `extension/src/shared/config/site-origins.js`
- Chrome URL overrides: Custom new tab page (`newtab.html`)
- Content Security Policy: Strict by default, allows only necessary resources

**Core APIs Used:**
- `chrome.runtime.onMessage` - IPC between content, background, and UI contexts
  - Implementation: `extension/src/spotlight/spotlight-ipc.ts` - Message routing with type safety
  - Background listener: `extension/src/background/service-worker.ts` - Handles all incoming messages
- `chrome.offscreen.createDocument` - Offscreen document for graph layout computation
  - Reason: WORKERS - Runs Pixi.js 2D rendering off main thread
  - Usage: `extension/src/background/services/offscreen-graph-manager.ts`
  - Document: `extension/src/entrypoints/offscreen-graph/main.ts`
  - Layout cache retrieval: Stores positions in `chrome.storage.session`
- `chrome.runtime.getURL()` - Get extension asset URLs (for web-accessible resources)
  - Implementation: `extension/src/spotlight/spotlight-ipc.ts` - Resolves graph asset origins
- `chrome.runtime.onStartup` - Startup hook for initialization
  - Implementation: `extension/src/background/service-worker.ts` - Initializes trees on extension reload
- `chrome.runtime.getContexts()` - Chrome 116+ API for context enumeration
  - Implementation: `extension/src/background/services/offscreen-graph-manager.ts` - Checks for existing offscreen docs

**Storage Patterns:**
- `chrome.storage.local.set/get/remove` - Persistent storage for tree data, auth, settings
  - Wrapper: WXT storage utilities with typed `.getValue()` / `.setValue()` / `.watch()` API
  - Key namespacing: `local:trail_*` and `local:trail_auth_*` conventions
- `chrome.storage.session.set/get` - Session-scoped layout cache (cleared on extension reload)
  - Graph positions stored per session to avoid recomputation
  - Cleared on new extension startup

**Communication Patterns:**
- Content → Background: Tree navigation events, tab metadata, page interactions
- Background → Content: Tree state updates, UI commands
- Background → Offscreen: Graph layout requests, TREE_UPDATED broadcast messages
- Offscreen → Background: Computed layout positions returned via postMessage

## Monitoring & Observability

**Error Tracking:**
- None detected - No Sentry, Rollbar, or similar integration

**Logs:**
- Console-based logging only (console.error, console.warn, console.log)
- Service worker: Catches unhandled promise rejections and logs them
  - Implementation: `extension/src/background/service-worker.ts`
- Log level control: `extension/src/shared/lib/logger.ts` - Conditionally logs in dev/test environments

**Analytics:**
- Vercel Analytics
  - Package: @vercel/analytics 1.6.1
  - Integration: `apps/marketing/` (marketing app only)
- Vercel Speed Insights
  - Package: @vercel/speed-insights 1.3.1
  - Integration: `apps/marketing/` (marketing app only)
- No extension-level analytics tracking

## CI/CD & Deployment

**Hosting:**
- Vercel - Primary hosting platform for web apps
  - Detected via: @vercel/analytics, @vercel/speed-insights packages
  - Auto-detection: Falls back to VERCEL_URL for app base URL if APP_BASE_URL not set
  - App ports: Marketing (3000), Account (4001 dev / 3001 prod)

**Extension Distribution:**
- Chrome Web Store - Production distribution channel
- Manual loading from `.wxt/chrome-data` for local development

**CI Pipeline:**
- None detected - No GitHub Actions, GitLab CI, or other CI config files

**Build Process:**
- WXT for extension: `wxt build` command → Manifest V3-compliant output
- Next.js for web apps: Standard `next build`
- Database generation: Prisma code generation (`pnpm db:generate`)

## Environment Configuration

**Required env vars:**
- `DATABASE_URL` - PostgreSQL connection string (postgres:// or postgresql://)
- `BETTER_AUTH_SECRET` - Authentication secret
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `TRAIL_EXTENSION_JWT_SECRET` - Secret for validating extension JWTs

**Optional env vars:**
- `APP_BASE_URL` - Account app base URL (defaults to localhost:4001 in dev)
- `NEXT_PUBLIC_APP_URL` - Public app URL (fallback for APP_BASE_URL)
- `VERCEL_URL` - Vercel deployment URL (auto-used if above not set)
- `BILLING_PROVIDER` - "manual" or "nowpayments" (defaults to "manual")
- `BILLING_TEST_MODE` - Enable test mode for payment processing
- `NOWPAYMENTS_API_KEY` - NOWPayments API key
- `NOWPAYMENTS_IPN_SECRET` - NOWPayments webhook secret
- `NOWPAYMENTS_API_BASE_URL` - NOWPayments API endpoint
- `TRAIL_EXTENSION_AUTH_REQUIRED` - Force authentication in extension
- `SANITY_PROJECT_ID` - Sanity CMS project ID (marketing app)
- `SANITY_DATASET` - Sanity dataset name (defaults to "production")
- `NODE_ENV` - Runtime environment
- `TRAIL_WXT_DEV_PORT` - WXT dev server port (defaults to 3011)

**Secrets location:**
- Environment variables (injected at runtime)
- .env files (local development only, never committed)
- Vercel deployment settings (for production)

## Webhooks & Callbacks

**Incoming:**
- NOWPayments IPN (Instant Payment Notification) - Optional webhook for payment status updates
  - Secret: `NOWPAYMENTS_IPN_SECRET`
  - Implementation: Would be in `apps/account/` API routes (not yet examined in detail)

**Outgoing:**
- None detected - Trail extension/app does not appear to send webhooks to external services

## Backend Configuration

**Backend Preset System:**
- Extension supports multiple backend targets via preset scripts: `extension/scripts/backend-preset.mjs`
- Presets: "local", "gettrail" (production)
- Config: `extension/src/shared/config/backend.js` - buildBackendUrl, BACKEND_CONFIG
- URL resolution: Dynamic based on preset (allows switching backends for different environments)
- Build commands: `pnpm build:local`, `pnpm build:gettrail`

---

*Integration audit: 2026-03-18*
