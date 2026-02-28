# Architecture

**Analysis Date:** 2026-02-28

## Pattern Overview

**Overall:** Extension-based browser history visualization with MVC-inspired separation: background service worker (model/state), content script (bridge), and React UI (view). Uses RPC-style message routing between layers.

**Key Characteristics:**
- Service Worker-driven state management with centralized tree and tab tracking
- Message-based IPC between background, content scripts, and UI
- Type-safe RPC contracts with enveloped request/response pattern
- Zustand-based client state for UI layer
- Graph visualization with layout engines (pixi.js + custom math)
- Multi-tree support with persistence and sync capabilities

## Layers

**Background Service Worker (State/Business Logic):**
- Purpose: Manages browser state, navigation history tree, tab lifecycle, and user data persistence
- Location: `src/background/`
- Contains: Service worker entry, state managers, event handlers, messaging router, services, utilities
- Depends on: Chrome APIs, shared types/schemas, local storage, backend APIs
- Used by: Content scripts, sidepanel UI (via RPC), fullview

**Content Script (Security Bridge):**
- Purpose: Enforces origin-gated communication between Trail account site and extension background
- Location: `src/content/content-script.ts`
- Contains: postMessage validation, nonce-based anti-replay, RPC envelope handling, relay logic
- Depends on: Lightweight validation functions, shared config (site origins)
- Used by: External Trail account website (via postMessage)

**Sidepanel UI (View/Client):**
- Purpose: Main interactive UI for visualizing and managing navigation trees
- Location: `src/sidepanel/ui/`
- Contains: React components, graph rendering, hooks, state store, API layer
- Depends on: React, TanStack Query, Zustand, Pixi.js, Zod, Chrome APIs
- Used by: Browser sidepanel interface

**Fullview (Secondary UI):**
- Purpose: Full-page visualization of trees (optional/secondary view)
- Location: `src/fullview/ui/`
- Contains: Full-page React app, graph components, layout
- Depends on: Same stack as sidepanel (React, queries, graph libs)
- Used by: Extension popup or separate tab

**Shared Layer (Types, RPC, Utilities):**
- Purpose: Common code for background and UIs; type definitions, RPC contracts, helper functions
- Location: `src/shared/`
- Contains: Type definitions, RPC method enums/handlers, validation schemas, utilities, config
- Depends on: Zod, MiniSearch
- Used by: All other layers

## Data Flow

**Browser Navigation → Background → UI:**

1. User navigates in browser
2. `chrome.webNavigation` event fires in background
3. Background updates `NavigationTree` state, manages tabs via `TabManager`
4. Background broadcasts `TREE_UPDATED` RPC to all connected UIs
5. Sidepanel UI receives update, Zustand store updates
6. React re-renders graph view with new tree structure

**UI Action → Background → Chrome API:**

1. User clicks node in sidepanel graph
2. Component calls `rpc.navigateTo({ url, nodeId })`
3. RPC client envelopes message and sends to background via `chrome.runtime.sendMessage`
4. Background router dispatches to handler (e.g., `navigationHandlers`)
5. Handler performs action (e.g., `chrome.tabs.update`, updates tree)
6. Background responds with result; UI receives `ResponseMessage`

**External Site ↔ Extension Bridge:**

1. Trail account site calls `postMessage` with signed payload (timestamp, nonce, type)
2. Content script validates origin, TTL, nonce, known type
3. Content script converts postMessage to RPC envelope
4. Content script sends to background via `chrome.runtime.sendMessage`
5. Background processes (e.g., OAuth flow, panel open)
6. Background (or caller) responds with relay, content script posts back to site

**State Management:**
- Background: `NavigationTree` (immutable updates), `TabManager`, persisted via Chrome storage
- UI: Zustand store with derived selectors; syncs via RPC broadcasts from background

## Key Abstractions

**NavigationTree:**
- Purpose: In-memory tree representation of browsing history; supports navigation, search, layout
- Examples: `src/background/state/nav-tree.ts`, `src/shared/lib/mapper.ts`
- Pattern: Immutable node updates; MiniSearch index for full-text search; lazy layout computation

**TabManager:**
- Purpose: Tracks which tabs are open for each tree node; manages tab recency, cycle ordering, suppression
- Examples: `src/background/state/tab-manager.ts`
- Pattern: Index-based lookups (tab→node, node→tabs); LRU tracking for recency-based tab cycling

**RPC Router:**
- Purpose: Centralized message dispatch with type-safe handler registration
- Examples: `src/background/messaging/router.ts`, `src/shared/rpc/contracts.ts`
- Pattern: Envelope-based RPC (version, id, method, input); handler map merged from multiple domains

**Zustand Store:**
- Purpose: Client-side state container for UI; syncs tree, tabs, user, settings from background
- Examples: `src/sidepanel/ui/state/store.ts`
- Pattern: Single store with slices for tree, account, ui state; selectors for derived data

**Message Handlers (by domain):**
- Location: `src/background/messaging/handlers/`
- Pattern: Each handler file (e.g., `tree-handlers.ts`, `navigation-handlers.ts`) exports handler map
- Examples: `treeHandlers`, `navigationHandlers`, `tagHandlers`, `siteMessageHandlers`

## Entry Points

**Background Service Worker:**
- Location: `src/background/service-worker.ts`
- Triggers: Extension startup, persistent background execution
- Responsibilities: Initialize all subsystems (messaging, navigation, tabs, sync, auth), catch unhandled rejections

**Content Script:**
- Location: `src/content/content-script.ts`
- Triggers: Page load on allowed origins (via manifest host_permissions)
- Responsibilities: Bridge postMessage from site to RPC; validate security; relay responses

**Sidepanel Main:**
- Location: `src/sidepanel/ui/main.tsx`
- Triggers: Browser opens sidepanel
- Responsibilities: Mount React app with QueryClient, Zustand provider, error boundary

**Fullview Main:**
- Location: `src/fullview/ui/main.tsx`
- Triggers: Full-page view opened (optional)
- Responsibilities: Mount React app for full-screen graph view

## Error Handling

**Strategy:** Graceful degradation; errors logged to console; UI shows toast notifications for user-facing failures

**Patterns:**

- Background: Try-catch in message handlers with `err(message)` response
- UI: Error boundaries wrap major sections; failed RPC calls trigger toast notifications
- Content Script: Validation failures silently ignored; connection errors non-fatal
- Navigation: `chrome.webNavigation` errors logged but don't crash state; fallbacks to other sources

## Cross-Cutting Concerns

**Logging:** `console.log/error` in background; structured during debug mode; no persistence by default

**Validation:** Zod schemas for API/RPC payloads; lightweight validation in content script (no Zod to keep bundle small)

**Authentication:** OAuth flow via background auth orchestrator; session stored in Chrome storage; content script enforces origin before relaying

**Persistence:** Chrome `storage.local` for tree snapshots, settings, tags; sync to backend via `SyncEngine` when authenticated

**Sync:** Background `syncEngine` periodically pushes/pulls tree state to backend; dirty tracking to minimize traffic
