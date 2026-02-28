# Codebase Structure

**Analysis Date:** 2026-02-28

## Directory Layout

```
extension/
├── .agents/                    # AI agent skill definitions (auto-generated)
├── .claude/                    # Claude workspace config
├── .planning/                  # Planning and documentation
│   └── codebase/              # This codebase analysis
├── .wxt/                       # WXT build cache and profiles
├── dist/                       # Build output (committed for releases)
├── entrypoints/                # WXT entry point definitions
│   ├── background.ts          # Service worker entry
│   ├── content.ts             # Content script entry
│   ├── fullview/main.tsx      # Fullview UI entry
│   └── sidepanel/main.tsx     # Sidepanel UI entry
├── extension/                  # Extension manifest files (deprecated structure)
├── public/                     # Static assets (icons, images)
│   └── icons/                 # PNG icons for manifest
├── scripts/                    # Build and utility scripts
├── src/                        # Main source code
│   ├── background/            # Service worker + state
│   ├── content/               # Content script
│   ├── fullview/              # Full-page UI (optional)
│   ├── shared/                # Shared types, RPC, utilities
│   └── sidepanel/             # Main sidepanel UI
├── tasks/                      # Project planning and lessons
├── tests/                      # Test files
├── package.json               # Root dependencies
├── pnpm-lock.yaml             # Lock file
├── tsconfig.json              # Base TypeScript config
├── tsconfig.app.json          # UI-specific TypeScript config
├── wxt.config.ts              # WXT framework config
├── postcss.config.cjs         # Tailwind/CSS config
└── tailwind.config.cjs        # Tailwind CSS config
```

## Directory Purposes

**`src/background/`** - Service Worker (Model/State):
- Purpose: Core extension logic; state management; event handlers
- Contains: Service worker initialization, navigation tracking, tab management, messaging router
- Key files: `service-worker.ts` (entry), `messaging/router.ts` (RPC dispatch)

**`src/background/state/`** - State Containers:
- Purpose: In-memory data structures for trees, tabs, navigation state
- Contains: `NavigationTree`, `TabManager`, `TabIndex`, `LRU`, `PinnedManager`, tree nodes
- Key files: `nav-tree.ts` (tree), `tab-manager.ts` (tabs), `tree-node.ts` (node structure)

**`src/background/messaging/`** - RPC Routing & Handlers:
- Purpose: Message dispatch and domain-specific handlers
- Contains: Router, RPC envelope parsing, handler maps for each domain
- Key files: `router.ts` (dispatch), `rpc-router.ts` (envelope), `handlers/` (domain handlers)

**`src/background/messaging/handlers/`** - Handler Modules:
- Purpose: RPC method implementations organized by domain
- Contains: tree, navigation, tab, pin, tag, settings, panel, content, editor, auth, flags handlers
- Pattern: Each file exports named handler map (e.g., `treeHandlers`, `navigationHandlers`)
- Key files:
  - `tree-handlers.ts` - Tree CRUD, navigation
  - `navigation-handlers.ts` - URL navigation
  - `tab-handlers.ts` - Tab close, mute, restore
  - `pin-handlers.ts` - Node pinning
  - `tag-handlers.ts` - Tag add/remove
  - `site-message-handlers.ts` - External site bridge

**`src/background/services/`** - Singletons & Side Effects:
- Purpose: Long-lived services for persistence, sync, auth, settings
- Contains: Persisted state managers, backend sync, auth flows, settings
- Key files:
  - `tree-storage.ts` - Tree persistence to Chrome storage
  - `sync/engine.ts` - Bidirectional sync with backend
  - `auth-orchestrator.ts` - OAuth and session management
  - `settings.ts` - Settings persistence
  - `tab-restoration.ts` - Tab state recovery on startup

**`src/background/navigation/`** - Navigation Tracking:
- Purpose: Intercept and track browser navigation events
- Contains: WebNavigation API handlers, redirect detection, history tracking
- Key files: `webnavigation.ts` (listener), `navigation-handler.ts` (logic)

**`src/background/tabs/`** - Tab Lifecycle:
- Purpose: Handle tab open/close/update events; sync with tree
- Contains: Tab lifecycle listeners, open tabs sync, tab updates
- Key files: `lifecycle.ts` (listeners), `sync-open-tabs.ts` (startup sync)

**`src/background/utils/`** - Utilities:
- Purpose: Helper functions for background layer
- Contains: URL parsing, tab utilities, tree utilities, new-tab detection
- Key files: `url-utils.ts`, `tab-utils.ts`, `tree-utils.ts`

**`src/content/`** - Content Script:
- Purpose: Security bridge between external site and extension
- Contains: postMessage validation, nonce tracking, origin enforcement, relay logic
- Key file: `content-script.ts` (single file, ~450 lines)

**`src/sidepanel/ui/`** - Sidepanel React UI:
- Purpose: Main interactive graph visualization and controls
- Contains: React components, state, hooks, graph rendering, API layer
- Key files: `App.tsx` (root), `main.tsx` (entry)

**`src/sidepanel/ui/components/`** - React Components:
- Purpose: UI building blocks organized by feature
- Contains: Graph (canvas, zoom, interactive), tags, theme, sidebar, context menus
- Subdirs:
  - `graph/` - Graph-specific components (canvas, zoom, area)
  - `tags/` - Tag management UI
  - `theme/` - Theme/appearance controls
  - `ui/` - Radix-based base components (button, dialog, etc.)

**`src/sidepanel/ui/graph/`** - Graph Visualization Engine:
- Purpose: Layout algorithms, rendering pipeline, interaction handling
- Contains: Graph layout, radial/tree layout, render loop, mouse/zoom interactions
- Subdirs:
  - `layout/` - Layout algorithms (radial, tree)
  - `render/` - Pixi.js rendering (nodes, edges, labels)

**`src/sidepanel/ui/state/`** - Client State:
- Purpose: Zustand store for UI state, synced from background
- Contains: Tree, tabs, user, settings, editor mode state
- Key files: `store.ts` (main store), `overlay-effects.ts` (modal/dropdown state)

**`src/sidepanel/ui/hooks/`** - Custom Hooks:
- Purpose: React hooks for background sync, shortcuts, auth, bootstrap
- Key files:
  - `useBootstrap.ts` - Initial state load
  - `useAccount.ts` - Auth state sync
  - `useChromeMessages.ts` - Listen for RPC broadcasts
  - `useShortcuts.ts` - Keyboard shortcuts

**`src/sidepanel/ui/query/`** - React Query Setup:
- Purpose: TanStack Query client configuration and hooks
- Contains: Query client, hooks for RPC calls
- Key file: `client.ts` (QueryClient with defaults)

**`src/sidepanel/ui/api/`** - API Client Layer:
- Purpose: Request builders for background RPC calls
- Contains: Account/auth API, tree API, settings API
- Key files: `account/` (auth endpoints)

**`src/fullview/ui/`** - Fullview UI (Secondary):
- Purpose: Full-page graph view (optional, mirrors sidepanel)
- Contains: Same structure as sidepanel (components, graph, state)
- Key file: `main.tsx` (entry)

**`src/shared/types/`** - Type Definitions:
- Purpose: Shared TypeScript interfaces for all layers
- Contains: IDs, tree structure, tab state, account, settings, flags
- Key files:
  - `ids.ts` - Opaque type aliases (NodeId, TabId, Url, etc.)
  - `tree.ts` - Tree metadata, navigation options
  - `node.ts` - Node data structure
  - `tabs.ts` - Tab state enum
  - `account.ts` - User, subscription, billing types
  - `settings.ts` - User settings interface

**`src/shared/rpc/`** - RPC Contract & Schema:
- Purpose: Type-safe RPC method definitions and message envelopes
- Contains: RPC method enum, message types, response types, handler types
- Key files:
  - `contracts.ts` - RPC_METHOD enum, all message types, handlers
  - `schema.ts` - RPC envelope validation schema (Zod)
  - `client.ts` - RPC client utility for making calls

**`src/shared/schemas/`** - Zod Validation Schemas:
- Purpose: Runtime validation for API payloads, settings, etc.
- Contains: Zod schemas for types defined in `types/`

**`src/shared/lib/`** - Core Utilities:
- Purpose: Reusable logic for tree operations, mapping, searching
- Contains: NavigationTree operations, tree codec, mapper (compact/full), commands (undo/redo)
- Key files:
  - `mapper.ts` - Map tree to JSON and vice versa
  - `tree-favicon.ts` - Favicon resolution
  - `commands.ts` - Undo/redo command system
  - `url-key.ts` - URL deduplication

**`src/shared/config/`** - Configuration:
- Purpose: Runtime and build-time configuration
- Contains: Backend URL selection (local/gettrail), allowed site origins
- Key files: `backend.ts`, `site-origins.ts`

**`src/shared/data/`** - Static Data:
- Purpose: Constants and static reference data
- Contains: Default settings, app metadata

**`src/shared/utils/`** - Utility Functions:
- Purpose: General-purpose helpers
- Contains: UUID generation, icon generation, string utilities

**`src/shared/vendor/`** - Third-party Code:
- Purpose: Vendored or wrapped third-party libraries
- Contains: MiniSearch wrapper for full-text search

**`entrypoints/`** - WXT Framework Entry Points:
- Purpose: Framework-specific entry point files that WXT uses to build different contexts
- Pattern: Thin wrappers that import actual source code
- Key files:
  - `background.ts` → imports `src/background/service-worker.ts`
  - `content.ts` → imports `src/content/content-script.ts`
  - `sidepanel/main.tsx` → imports `src/sidepanel/ui/main.tsx`
  - `fullview/main.tsx` → imports `src/fullview/ui/main.tsx`

## Key File Locations

**Entry Points:**
- `entrypoints/background.ts` - Service worker entry (WXT hook)
- `entrypoints/content.ts` - Content script entry (WXT hook)
- `entrypoints/sidepanel/main.tsx` - Sidepanel UI entry (WXT hook)
- `src/background/service-worker.ts` - Service worker initialization
- `src/sidepanel/ui/main.tsx` - Sidepanel React mount
- `src/content/content-script.ts` - Content script logic

**Configuration:**
- `wxt.config.ts` - WXT framework config (manifest, dev server, permissions)
- `tsconfig.json` - Base TypeScript (background/shared)
- `tsconfig.app.json` - UI TypeScript (excludes UI from base check)
- `package.json` - Dependencies and scripts

**Core Logic:**
- `src/background/state/nav-tree.ts` - Navigation tree (model)
- `src/background/state/tab-manager.ts` - Tab tracking
- `src/background/messaging/router.ts` - RPC router dispatch
- `src/shared/rpc/contracts.ts` - RPC method definitions
- `src/sidepanel/ui/state/store.ts` - Client state store

**Testing:**
- `tests/basic.test.ts` - Basic tests
- (No formal test structure; basic.test.ts imports and tests key modules)

## Naming Conventions

**Files:**
- Directories: `kebab-case` (e.g., `background`, `sidepanel`, `tab-manager.ts`)
- Components: PascalCase for React (e.g., `GraphArea.tsx`, `App.tsx`)
- Utilities/modules: camelCase (e.g., `tab-manager.ts`, `nav-tree.ts`)
- Handlers: `{domain}-handlers.ts` (e.g., `tree-handlers.ts`, `tag-handlers.ts`)
- Types: separate `types/` directory with domain names (e.g., `types/tree.ts`, `types/ids.ts`)

**Directories:**
- Feature domains: `kebab-case` singular or plural (e.g., `background`, `messages`, `handlers`)
- Component organization: Subdirectories by feature area (e.g., `components/graph/`, `components/theme/`)
- Utilities: `lib/`, `utils/`, `helpers/` conventions used consistently

**Code:**
- Functions: `camelCase` (e.g., `handleNavigation`, `createUrlKey`)
- Types: `PascalCase` (e.g., `NavigationTree`, `TabManager`)
- Constants: `SCREAMING_SNAKE_CASE` for global constants (e.g., `RPC_METHOD`, `DEFAULT_DEV_SERVER_PORT`)
- Enums: `PascalCase` names, `SCREAMING_SNAKE_CASE` values
- React hooks: `useXxxName` (e.g., `useBootstrap`, `useChromeMessages`)

## Where to Add New Code

**New Feature (Backend Logic):**
- Primary code: `src/background/services/{feature}.ts` or `src/background/{layer}/{feature}.ts`
- Handlers: `src/background/messaging/handlers/{feature}-handlers.ts`
- Types: `src/shared/types/{feature}.ts`
- RPC methods: Add to `src/shared/rpc/contracts.ts` (RPC_METHOD enum and message types)
- Tests: `tests/{feature}.test.ts`

**New React Component:**
- Implementation: `src/sidepanel/ui/components/{feature}/ComponentName.tsx` (or `src/fullview/ui/components/...`)
- Hooks: `src/sidepanel/ui/hooks/useFeatureName.ts` if custom hook needed
- Styles: Co-locate as `.module.css` or use Tailwind classes inline

**Shared Utility/Type:**
- Utility function: `src/shared/lib/{feature}.ts` or `src/shared/utils/{feature}.ts`
- Type definition: `src/shared/types/{domain}.ts`
- Validation schema: `src/shared/schemas/{domain}.ts`

**Global State (Zustand):**
- Add to store slices in `src/sidepanel/ui/state/store.ts`
- Keep slices organized by domain (tree, account, ui, etc.)

**New Handler Domain:**
- Create: `src/background/messaging/handlers/{domain}-handlers.ts`
- Export: Named handler map (e.g., `export const featureHandlers: HandlerMap = { ... }`)
- Register: Add merge in `src/background/messaging/router.ts` initMessaging()

## Special Directories

**`.wxt/`**
- Purpose: WXT build artifacts and Chrome profile data
- Generated: Yes (on every `wxt dev`/`wxt build`)
- Committed: No (git-ignored)

**`dist/`**
- Purpose: Built extension package for distribution
- Generated: Yes (on `wxt build`/`wxt zip`)
- Committed: Yes (for release tags, but not during development)

**`.output/`**
- Purpose: Multi-platform build outputs (chrome, firefox)
- Generated: Yes (on `wxt build`)
- Committed: No (git-ignored)

**`node_modules/`**
- Purpose: Dependency packages
- Generated: Yes (on `pnpm install`)
- Committed: No (git-ignored)

**`.planning/`**
- Purpose: Project planning, agent skills, codebase documentation
- Committed: Yes
- Structure: `codebase/` for architectural docs, `tasks/` for planning

## Import Paths

**Path aliases (from `tsconfig.json`):**
- `@` → `src/sidepanel/ui` (UI only, set in `wxt.config.ts`)

**Module resolution:**
- All imports use `.js` extensions (ES modules, no bundler magic)
- Relative imports: `../shared/types/ids.js`
- Absolute imports: `src/background/service-worker.js` (from entrypoints)

**Import organization order:**
1. External libraries (react, zustand, chrome APIs)
2. Internal absolute paths (src/...)
3. Internal relative paths (../../)
4. Type-only imports marked with `type` keyword

## Adjacent Systems (Not in src/)

**`public/`** - Static assets:
- `icons/` - PNG icons for manifest (16x16, 32x32, 48x48, 128x128)
- No other static assets (styles are Tailwind; fonts are system)

**`scripts/`** - Build utilities:
- `backend-preset.mjs` - Backend config switcher (local vs gettrail)

**`tests/`** - Test suite:
- `basic.test.ts` - Basic integration tests with node --import tsx
- No test framework config; uses manual assertions or similar

**`tasks/`** - Project planning:
- `todo.md` - Current phase tracking
- `lessons.md` - Learned patterns and fixes

**`openapi-html/`** - Generated OpenAPI docs:
- Auto-generated from backend API spec
- Not part of extension code
