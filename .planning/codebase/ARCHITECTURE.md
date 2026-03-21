# Architecture

**Analysis Date:** 2025-03-18

## Pattern Overview

**Overall:** Monorepo with event-driven RPC messaging between browser extension and web applications, unified through tRPC API layer and PostgreSQL database.

**Key Characteristics:**
- Extension owns local state (navigation tree, tabs, session history) with bidirectional sync to backend
- Web apps (account, marketing) serve user accounts and content management
- Message passing via versioned RPC envelopes with Zod validation
- Single source of truth in extension background state, synced to cloud via sync engine
- Security-first content script bridge between web app (account.gettrail.net) and extension
- Immutable state updates throughout (no mutation patterns)

## Layers

**Extension Background Service Worker:**
- Purpose: Central orchestrator for all extension operations, lifecycle management, event handling
- Location: `extension/src/entrypoints/background.ts`, `extension/src/background/service-worker.ts`, `extension/src/background/messaging/`
- Contains: Message routing, tab tracking, tree state management (nav-tree.ts), sync engine, auth orchestration, event listeners
- Depends on: Chrome APIs (tabs, storage, runtime, webNavigation), local state modules, sync API client
- Used by: All UI layers (sidepanel, newtab, spotlight), content scripts, web apps (via postMessage bridge)

**Extension UI Layers (Presentational):**
- Purpose: Render and interact with browsing history visualization and features
- Location: `extension/src/entrypoints/sidepanel/`, `extension/src/entrypoints/newtab/`, `extension/src/entrypoints/spotlight-graph/`, `extension/src/entrypoints/fullview/`
- Contains: React components, TanStack React Query for server state, Zustand for local UI state, Pixi.js rendering (graph visualization)
- Depends on: Background RPC client, React Query hooks, UI component library (@trail/ui)
- Used by: End users via browser UI

**Content Script Bridge:**
- Purpose: Security layer between web app (account.gettrail.net) and extension via postMessage
- Location: `extension/src/entrypoints/content.ts`, `extension/src/content/bridge/runtime.ts`
- Contains: postMessage validation, nonce anti-replay tracking, TTL enforcement (30s), request/response relay, origin allowlist enforcement
- Depends on: RPC schema, site-origins.ts allowlist
- Used by: Account app running on trusted origin, communicates with background via browser.runtime.sendMessage

**Web Apps (Next.js):**
- Purpose: User account management, subscription, authentication, content management
- Location: `apps/account/`, `apps/marketing/`, `apps/video/` (excluded from builds)
- Contains: Server components, tRPC client integration, auth middleware (Better Auth), Next.js routes
- Depends on: @trail/trpc, @trail/db, @trail/ui components, @trail/content
- Used by: Browser users, extension via postMessage bridge for authenticated features

**Shared Packages:**
- `packages/trpc/`: tRPC router definitions, type-safe API contracts, JWT extension token handling
- `packages/db/`: Prisma client, PostgreSQL schema, migrations (users, sessions, trails, devices)
- `packages/ui/`: React component library (Radix UI, Tailwind, custom components)
- `packages/content/`: Copywriting and constants for all apps

## Data Flow

**Navigation Event (User clicks link):**

1. Browser triggers `browser.webNavigation.onCommitted` (detected in `extension/src/background/navigation/webnavigation.ts`)
2. Background extracts URL, title, favicon, tab metadata via `navigation-handler.ts`
3. Tree state updates via `nav-tree.ts` (creates new node, updates current, maintains parent/child edges)
4. Node recency tracked in `node-recency.ts` (LRU scoring)
5. Tab manager updates bidirectional mapping in `tab-manager.ts`
6. All UI layers subscribed to tree changes receive `TREE_UPDATED` notification via RPC
7. If sync enabled, dirty tracker marks tree as modified in `sync/dirty-tracker.ts`, sync engine batches to backend on next tick
8. Account app receives update via postMessage if open on allowed origin (RELAY_TO_SITE from background)

**Spotlight Search (User triggers Cmd+Shift+K):**

1. `extension/src/entrypoints/spotlight-command.ts` detects keyboard shortcut via `browser.commands.onCommand`
2. Launches spotlight modal (`extension/src/entrypoints/spotlight-graph/`)
3. Spotlight requests bootstrap data via `SPOTLIGHT_BOOTSTRAP` RPC call to background
4. Background aggregates:
   - Current tree with all nodes from `nav-tree.ts`
   - Open tab counts per node from `tab-manager.ts`
   - Node recency scores from `node-recency.ts`
   - Pinned status from `pinned.ts`
   - All wrapped in `SpotlightBootstrapData` type
5. Spotlight creates in-memory search index via `minisearch` on bootstrap
6. User types → incremental search in UI (no background calls, runs in UI thread)
7. User selects result → `SPOTLIGHT_EXECUTE_ACTION` triggers navigation, pin, close, delete, etc.
8. Action handler in background updates state, broadcasts `TREE_UPDATED` to all listeners

**Authentication Flow (User logs in):**

1. User initiates login on account app (account.gettrail.net via postMessage OPEN_TRAIL_PANEL)
2. Account app uses Better Auth for OAuth session management
3. Account app posts auth message to extension via `window.postMessage` (source "trail-site")
4. Content script (`extension/src/content/bridge/runtime.ts`) validates:
   - Origin (must be allowed via site-origins.ts)
   - TTL (30s window, must be recent)
   - Nonce (anti-replay, max 100 in flight)
   - Known message type (PING, OPEN_TRAIL_PANEL, ENTER_EDITOR_MODE, AUTH_REVOKED, etc.)
5. Forwards to background via `browser.runtime.sendMessage`
6. Background auth-orchestrator (`extension/src/background/services/auth-orchestrator.ts`) processes
7. auth-policy-keeper stores auth tokens/policy in extension storage
8. Sync engine activates: cloud trees load via API, merge with local state
9. All UI layers notified of auth state change via `SYNC_TREES` or `OAUTH_SILENT_SYNC`

**Sync Engine Tick (Periodic or triggered):**

1. Dirty tracker identifies modified nodes (set when tree updated)
2. Constructs minimal delta payload (changed nodes only, not full tree)
3. Sends to backend via API call in `extension/src/background/services/sync/api.ts`
4. Server applies mutations via Prisma, stores sync metadata
5. Server broadcasts `TREES_UPDATED` back to all connections (if available)
6. Extension receives update via `TREES_UPDATED` RPC, merges with local state
7. Conflict resolution: server always wins on timestamp collision (server is authority)

**State Management:**

- **Extension Local State:** Immutable tree structure in `nav-tree.ts`, updates create new tree objects (structural sharing via tree-node.ts operations)
- **Sync State:** Dirty tracking in `extension/src/background/services/sync/dirty-tracker.ts`, batched sends on 5s debounce or explicit trigger
- **UI State:** React Query cache for server state, Zustand stores for UI ephemeral state (modals, selections)
- **Auth State:** Better Auth session on web app (HttpOnly cookies), extension storage for auth policy on background

## Key Abstractions

**RPC Message System:**
- Purpose: Type-safe, versioned request/response communication across extension boundaries
- Examples: `extension/src/shared/rpc/contracts.ts`, `extension/src/shared/rpc/schema.ts`
- Pattern: Message envelopes with version (RPC_VERSION=2), ID (UUID), method (string), input (record), success flag, data/error
- Zod validation on all RPC boundaries, request handlers return typed responses
- All internal communication uses this (background ↔ UI layers, content ↔ background)

**Navigation Tree:**
- Purpose: In-memory hierarchical representation of user's browsing session
- Examples: `extension/src/background/state/nav-tree.ts`, `extension/src/background/state/tree-node.ts`
- Pattern: Immutable tree operations (always return new instances), parent/child relationships preserved via edge pointers
- Node ID branded type (NodeId) prevents accidental ID mixing
- Used by: All visualization, search, layout calculation, sync engine

**Tab Manager:**
- Purpose: Tracks relationship between browser tabs and tree nodes
- Examples: `extension/src/background/state/tab-manager.ts`, `extension/src/background/state/tab-index.ts`, `extension/src/background/state/tab-lru.ts`
- Pattern: LRU tracking for tab recency, bidirectional tab↔node mapping, deduplication of tab states
- Used by: Node preview, tab close operations, visualization, spotlight search ranking

**Sync Engine:**
- Purpose: Bidirectional sync between local state and cloud backend
- Examples: `extension/src/background/services/sync/engine.ts`, `extension/src/background/services/sync/api.ts`, `extension/src/background/services/sync/dirty-tracker.ts`
- Pattern: Dirty tracking + polling, exponential backoff on conflict (200ms, 800ms, 2000ms), mutation-only (no full replaces), server authority on collision
- Used by: Background on auth success, periodic tick (5s debounce), manual sync trigger

**Message Handler Router:**
- Purpose: Dispatch RPC requests to appropriate handlers based on method
- Examples: `extension/src/background/messaging/router.ts`, `extension/src/background/messaging/handlers/`
- Pattern: Handler registry by RPC method name, async/sync support, error wrapping in response envelope
- 15+ handler files organized by domain (tab-handlers, tree-handlers, spotlight-handlers, etc.)
- Used by: Background service worker main event loop

**Content UI Mount System:**
- Purpose: Inject UI overlay into content pages (account app)
- Examples: `extension/src/entrypoints/content-ui/mount.ts`
- Pattern: Shadow DOM isolation, style injection, React portal mounting
- Used by: Content script to add Trail features/UI to gettrail.net

## Entry Points

**Background Service Worker:**
- Location: `extension/src/entrypoints/background.ts` (delegates to `extension/src/background/service-worker.ts`)
- Triggers: Browser startup, extension enabled
- Responsibilities: Initialize all subsystems (messaging, sync, auth, tabs, navigation), listen for all RPC requests, manage lifecycle events

**Content Script:**
- Location: `extension/src/entrypoints/content.ts`
- Triggers: Page load on allowed origins (ALLOWED_SITE_MATCH_PATTERNS from site-origins.ts)
- Responsibilities: Bridge between page and extension, validate postMessage, relay RPC calls, handle site messages, establish runtime connection

**Sidepanel:**
- Location: `extension/src/entrypoints/sidepanel/main.tsx`
- Triggers: User clicks extension icon or toggles panel (configured in manifest)
- Responsibilities: Display tree visualization (Pixi.js), handle user edits, subscribe to tree updates, show settings/tags

**New Tab:**
- Location: `extension/src/entrypoints/newtab/main.tsx`
- Triggers: User opens new tab (replaces Chrome default via chrome_url_overrides in manifest)
- Responsibilities: Show tree overview, recent nodes, open tabs, quick actions

**Spotlight Graph:**
- Location: `extension/src/entrypoints/spotlight-graph/main.tsx`
- Triggers: User presses Cmd+Shift+K (registered in manifest.commands)
- Responsibilities: Search interface, results ranking via minisearch, action execution, tree preview on hover

**Fullview Editor:**
- Location: `extension/src/entrypoints/fullview/main.tsx`
- Triggers: User enters edit mode from sidepanel
- Responsibilities: Full-screen tree editor, drag-drop reorganization, node creation/deletion

**Account App (Web):**
- Location: `apps/account/app/layout.tsx` (Next.js)
- Triggers: User navigates to account.gettrail.net
- Responsibilities: Auth via Better Auth, subscription management, settings, trail imports, communicate with extension via postMessage bridge

**Marketing App:**
- Location: `apps/marketing/app/layout.tsx`
- Triggers: User navigates to gettrail.net
- Responsibilities: Landing page, blog, documentation (read-only, no extension interaction)

## Error Handling

**Strategy:** Errors caught at every boundary, wrapped in RPC response envelope with success flag and error string. User-friendly messages in UI, detailed logging on server.

**Patterns:**

- Extension RPC calls use `try/catch` and return `err(message)` or `ok(data)` helpers
- Content script validates every postMessage, silently drops invalid messages (no error response needed)
- Auth failures trigger logout, clear session, redirect to login, notify UI
- Sync errors with exponential backoff (max retry limit before marking error)
- UI layers show toast notifications for user-facing errors (sonner toast)
- Service worker catches unhandled promise rejections globally via addEventListener('unhandledrejection')
- Malformed RPC envelopes rejected by Zod, returns error to caller

## Cross-Cutting Concerns

**Logging:** Console-based, includes context (sender, method, timing). Module-prefixed for grepping. No log aggregation in local builds.

**Validation:** Zod schemas on all RPC boundaries (rpcRequestEnvelopeSchema, rpcResponseEnvelopeSchema), lightweight validation in content script (no external deps), type-safe handlers ensure proper inputs

**Authentication:** Better Auth on web app (OAuth + password), extension session storage for auth tokens, policy keeper enforces auth state, silent sync on boot, interactive login flow for expired sessions

**Security:**
- Content script: origin validation (ALLOWED_SITE_MATCH_PATTERNS), nonce anti-replay (100-message LRU), TTL (30s), lightweight schema check
- Extension storage: No secrets, only session metadata and public user data
- postMessage: Strict source checking (event.source === window), origin must match, nonce prevents replay
- CORS: Account app restricted to allowed origins only via content script

---

*Architecture analysis: 2025-03-18*
