# Architecture

**Analysis Date:** 2026-03-17

## Pattern Overview

**Overall:** Multi-tier distributed system with three primary layers: Browser Extension (desktop client), Web Applications (account/marketing), and Backend Services (database, API).

**Key Characteristics:**
- Message-based IPC between extension components
- RPC protocol for extension-to-web communication
- Monorepo with shared packages (ui, db, trpc, content)
- Headless Postgres database accessed through Prisma ORM
- Next.js full-stack applications for account and marketing sites

## Layers

**Browser Extension (Client):**
- Purpose: Captures and visualizes user navigation history as an interactive graph/tree
- Location: `extension/src/`
- Contains: Service worker, UI components, state management, RPC client
- Depends on: None externally, communicates via Chrome extension APIs
- Used by: Direct browser interaction, user-facing UI

**Backend Services Layer:**
- Purpose: Handles authentication, data persistence, billing, and API endpoints
- Location: `packages/trpc/src/`, `apps/account/src/server/`
- Contains: tRPC router, Prisma models, auth logic, sync engines
- Depends on: `@trail/db` (Prisma client), PostgreSQL database
- Used by: Extension (via RPC), Web applications (via Next.js)

**Web Applications Layer:**
- Purpose: Account dashboard, marketing site, user settings/billing
- Location: `apps/account/`, `apps/marketing/`
- Contains: React components, Next.js server routes, tRPC client
- Depends on: `@trail/ui`, `@trail/trpc`, `@trail/content`, `@trail/db`
- Used by: Browser users via HTTP/HTTPS

**Shared Packages:**
- Purpose: Reusable components, styling, database schema, RPC definitions
- Location: `packages/`
- Contains: UI components (`@trail/ui`), database client (`@trail/db`), tRPC server setup (`@trail/trpc`), content primitives (`@trail/content`)
- Depends on: Framework libraries (React, Prisma, Radix UI)
- Used by: Extension, account app, marketing app

## Data Flow

**User Navigation Capture:**

1. Service worker monitors `chrome.webNavigation` events
2. Navigation events create/update nodes in the navigation tree (in-memory state)
3. Changes trigger persistence to local storage via `tree-storage.ts`
4. UI components subscribed to tree state updates re-render
5. Sync engine debounces and batches updates to backend

**Search & Spotlight:**

1. User opens spotlight (CMD+K in extension)
2. `useSpotlightSearch` hook calls `searchSpotlight()` RPC to background
3. Background worker queries in-memory tree with `minisearch` index
4. Results streamed back to UI components
5. User interactions (click, keyboard) routed through `executeSpotlightAction()` RPC

**Sync Engine (Bidirectional):**

1. Local changes debounced in `sync/engine.ts`
2. Dirty tracker identifies changed nodes
3. Sync payload sent to account server via RPC
4. Server applies to Prisma database
5. Server broadcasts updates back via message passing
6. Extension receives `TREES_UPDATED` notification
7. Local state merged with server state (with conflict resolution)

**Authentication Flow:**

1. User opens account page → handled by Next.js
2. `better-auth` library manages OAuth/credentials
3. JWT tokens issued and stored in secure cookies
4. Extension calls RPC with signed extension tokens (JWT-based)
5. Backend validates token signature and checks auth policy
6. Request processed with user context from JWT payload

**State Management:**

- **In-Memory State (Background Worker):**
  - `nav-tree.ts`: Current navigation tree structure
  - `tab-manager.ts`: Open browser tabs and their relationships
  - `pinned.ts`: User-pinned nodes
  - `node-recency.ts`: LRU tracking for "recent" nodes
  - All state persisted to browser storage on change

- **Server State (PostgreSQL):**
  - User data, authentication tokens, subscriptions (Prisma models)
  - Trails (complete navigation trees)
  - Sync status, billing info, feature flags

- **UI State (React Hooks):**
  - Component-level state (search query, selected nodes, modals)
  - Cached data via React Query (account/marketing apps)

## Key Abstractions

**Navigation Tree:**
- Purpose: Hierarchical model of user's browsing session
- Examples: `extension/src/background/state/tree-node.ts`, `extension/src/shared/types/tree.ts`
- Pattern: Immutable updates, structural sharing for diffing

**RPC Schema:**
- Purpose: Type-safe contract between extension and background worker
- Examples: `extension/src/shared/rpc/contracts.ts`, `extension/src/shared/rpc/schema.ts`
- Pattern: Zod schemas for runtime validation, TypeScript inference for compile-time safety

**Message Routing:**
- Purpose: Centralized handler registry for all inter-worker messages
- Examples: `extension/src/background/messaging/router.ts`, `extension/src/background/messaging/handlers/*.ts`
- Pattern: Factory function creates router, handlers registered via `.merge()`, dispatch validates and executes

**Spotlight Search:**
- Purpose: Fast in-memory full-text search over navigation tree
- Examples: `extension/src/spotlight/useSpotlightSearch.ts`, `extension/src/shared/vendor/minisearch.ts`
- Pattern: LRU cache for preview data, session-based state, connection error recovery with backoff

**Sync Engine:**
- Purpose: Bidirectional tree synchronization with conflict resolution
- Examples: `extension/src/background/services/sync/engine.ts`, `extension/src/background/services/sync/dirty-tracker.ts`
- Pattern: Debounced local changes, dirty tracking, transaction-aware server syncing

**Tab Manager:**
- Purpose: Unified view of open browser tabs and their lifecycle
- Examples: `extension/src/background/state/tab-manager.ts`, `extension/src/background/tabs/lifecycle.ts`
- Pattern: Tab ID-based indexing, state normalized (no duplication)

## Entry Points

**Background Service Worker:**
- Location: `extension/src/entrypoints/background.ts`
- Triggers: Extension loads, persists until unload
- Responsibilities: Initializes all background modules, listens for messages, manages tabs/navigation lifecycle

**Side Panel UI:**
- Location: `extension/src/entrypoints/sidepanel/main.tsx`
- Triggers: User clicks extension icon or manually opens side panel
- Responsibilities: Renders tree graph, handles search, manages tags

**New Tab Page:**
- Location: `extension/src/entrypoints/newtab/main.tsx`
- Triggers: User opens new tab
- Responsibilities: Shows dashboard, recent/bookmarked pages, search defaults

**Spotlight Command:**
- Location: `extension/src/entrypoints/spotlight.content/index.tsx`
- Triggers: User presses CMD+K or configured hotkey
- Responsibilities: Renders modal search interface with live results

**Account Web App:**
- Location: `apps/account/src/` (Next.js with file-based routing under `app/` directory)
- Triggers: User navigates to account.gettrail.com
- Responsibilities: User dashboard, settings, billing, trail management, authentication

**Marketing Site:**
- Location: `apps/marketing/src/` (Next.js)
- Triggers: User navigates to gettrail.com
- Responsibilities: Public landing page, feature showcase, documentation links

## Error Handling

**Strategy:** Defensive with user-friendly messaging in UI, detailed logging on server side.

**Patterns:**
- **Network errors:** Retry with exponential backoff (200ms, 800ms, 2000ms) for recoverable errors; session expiry triggers re-auth flow
- **RPC errors:** Validation errors from Zod reject malformed payloads; handler exceptions caught, logged, and returned as error envelopes
- **Sync conflicts:** Server-side transaction logic merges changes; dirty tracker prevents re-sending failed updates
- **Missing state:** UI gates display on auth status, shows loading states during data fetch, renders fallback UI if data unavailable

## Cross-Cutting Concerns

**Logging:** Console-based in extension (prefixed with module name for grepping), server-side request logging in Next.js

**Validation:** Zod schemas at all RPC boundaries; Prisma enforces database constraints; input validation in handlers before state mutations

**Authentication:** JWT tokens with expiry, extension tokens signed server-side, auth policy evaluated per request, refresh flow via better-auth

---

*Architecture analysis: 2026-03-17*
