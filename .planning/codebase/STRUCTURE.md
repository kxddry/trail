# Codebase Structure

**Analysis Date:** 2025-03-18

## Directory Layout

```
trail/
├── apps/                          # Web applications (Next.js)
│   ├── account/                   # Account dashboard & auth
│   │   ├── app/                   # Next.js app router
│   │   ├── src/
│   │   │   ├── app/               # Pages (routing)
│   │   │   ├── api/               # API routes & tRPC handler
│   │   │   ├── components/        # React components
│   │   │   ├── lib/               # Utilities & helpers
│   │   │   └── server/            # Server-side logic
│   │   └── package.json
│   ├── marketing/                 # Public marketing site
│   │   ├── app/                   # Next.js app router
│   │   ├── src/
│   │   │   ├── app/               # Pages
│   │   │   ├── lib/               # Sanity client, utilities
│   │   │   └── components/        # Marketing components
│   │   └── package.json
│   └── video/                     # (excluded from most builds)
│
├── extension/                     # Browser extension (primary client)
│   ├── src/
│   │   ├── entrypoints/           # WXT entry points (UI pages & workers)
│   │   │   ├── background.ts      # Service worker entry
│   │   │   ├── content.ts         # Content script entry
│   │   │   ├── sidepanel/         # Side panel UI
│   │   │   ├── newtab/            # New tab page
│   │   │   ├── spotlight-graph/   # Spotlight modal
│   │   │   ├── fullview/          # Full-screen editor
│   │   │   ├── account/           # Account iframe
│   │   │   ├── content-ui/        # Content page overlay
│   │   │   └── offscreen-graph/   # Offscreen document (graph processing)
│   │   ├── background/            # Service worker logic
│   │   │   ├── service-worker.ts  # Initialization hub
│   │   │   ├── messaging/         # RPC routing
│   │   │   │   ├── router.ts      # Message dispatcher
│   │   │   │   ├── handlers/      # 15+ handler files (tabs, tree, tags, etc.)
│   │   │   │   └── rpc-router.ts  # RPC envelope parsing
│   │   │   ├── navigation/        # Chrome webNavigation listeners
│   │   │   ├── tabs/              # Chrome tabs API & lifecycle
│   │   │   ├── services/          # Long-running services
│   │   │   │   ├── sync/          # Bidirectional sync engine
│   │   │   │   ├── auth-orchestrator.ts
│   │   │   │   ├── account-keeper.ts
│   │   │   │   └── auth-policy-keeper.ts
│   │   │   ├── state/             # In-memory state modules
│   │   │   │   ├── nav-tree.ts    # Navigation tree
│   │   │   │   ├── tree-node.ts   # Node operations
│   │   │   │   ├── tab-manager.ts # Tab tracking
│   │   │   │   ├── pinned.ts      # Pinned nodes
│   │   │   │   └── node-recency.ts # LRU recency
│   │   │   └── utils/             # Helpers
│   │   │
│   │   ├── ui-core/               # Core UI infrastructure
│   │   │   ├── panel/             # Panel bootstrap
│   │   │   ├── components/        # Shared UI components
│   │   │   ├── hooks/             # Shared hooks
│   │   │   ├── providers/         # React providers
│   │   │   ├── query/             # React Query setup
│   │   │   └── styles/            # Base styles
│   │   │
│   │   ├── content/               # Content script bridge
│   │   │   ├── bridge/            # postMessage bridge logic
│   │   │   ├── messaging/         # Content messaging
│   │   │   └── security/          # Validation
│   │   │
│   │   ├── features/              # Feature modules
│   │   │   ├── account/
│   │   │   ├── auth/
│   │   │   ├── settings/
│   │   │   ├── tags/
│   │   │   ├── themes/
│   │   │   └── tree/
│   │   │
│   │   ├── shared/                # Extension-wide utilities & types
│   │   │   ├── rpc/               # RPC contracts & schemas
│   │   │   │   ├── contracts.ts   # Message types (87 RPC methods)
│   │   │   │   ├── schema.ts      # Zod validation schemas
│   │   │   │   └── client.ts      # RPC client
│   │   │   ├── types/             # Type definitions
│   │   │   │   ├── ids.ts         # Branded types (NodeId, TabId)
│   │   │   │   ├── tree.ts        # Navigation tree JSON schema
│   │   │   │   ├── tabs.ts        # Tab types
│   │   │   │   ├── settings.ts    # User settings
│   │   │   │   ├── tags.ts        # Tag definitions
│   │   │   │   ├── flags.ts       # Feature flags
│   │   │   │   └── export.ts      # Export format
│   │   │   ├── platform/          # Chrome API abstractions
│   │   │   │   └── webext.ts      # Typed Chrome APIs
│   │   │   ├── config/            # Configuration
│   │   │   │   ├── backend.ts     # Backend URL config
│   │   │   │   └── site-origins.ts # Allowed origins
│   │   │   ├── lib/               # Libraries
│   │   │   │   ├── commands.ts    # Undo/redo command history
│   │   │   │   └── ...
│   │   │   ├── schemas/           # Data schemas
│   │   │   ├── styles/            # Global styles
│   │   │   └── utils/             # Utilities
│   │   │
│   │   ├── assets/                # Images, fonts
│   │   └── vendor/                # Vendored libraries
│   │
│   ├── public/                    # Static assets (icons, images)
│   │   └── icons/                 # Extension icons (16, 32, 48, 128)
│   │
│   ├── tests/                     # Node-based tests
│   │   ├── basic.test.ts
│   │   ├── architecture-boundaries.test.ts
│   │   ├── spotlight-search.test.ts
│   │   └── rpc-schema.test.ts
│   │
│   ├── wxt.config.ts              # WXT build configuration
│   ├── tsconfig.json
│   ├── package.json
│   └── components.json            # Shadcn components config
│
├── packages/                      # Shared libraries
│   ├── db/                        # Prisma ORM & database client
│   │   ├── prisma/
│   │   │   ├── schema.prisma      # Database schema (users, trails, devices)
│   │   │   └── migrations/        # Database migrations
│   │   ├── src/
│   │   │   ├── client.ts          # Singleton PrismaClient
│   │   │   └── index.ts           # Exports
│   │   └── package.json
│   │
│   ├── trpc/                      # tRPC router & procedures
│   │   ├── src/
│   │   │   ├── index.ts           # Main exports
│   │   │   ├── trpc.ts            # tRPC factory & router
│   │   │   ├── router.ts          # App router
│   │   │   ├── context.ts         # tRPC context setup
│   │   │   └── extension-token.ts # JWT token signing
│   │   └── package.json
│   │
│   ├── ui/                        # React component library
│   │   ├── src/
│   │   │   ├── index.ts           # Main component exports
│   │   │   ├── icons/             # Icon components (generated)
│   │   │   ├── components/        # UI components (Radix + custom)
│   │   │   ├── marketing/         # Marketing components
│   │   │   ├── auth/              # Auth UI components
│   │   │   ├── styles/            # Stylesheets
│   │   │   ├── tailwind-preset.ts # TailwindCSS preset
│   │   │   └── hooks/             # Custom hooks
│   │   ├── styles/                # CSS files
│   │   └── package.json
│   │
│   ├── content/                   # Content type definitions
│   │   ├── src/
│   │   │   └── index.ts           # Copy & type exports
│   │   └── package.json
│   │
│   └── config/                    # Configuration utilities
│       ├── src/
│       └── package.json
│
├── sanity/                        # Sanity CMS schema
│   ├── schemaTypes/
│   ├── scripts/
│   ├── static/
│   └── package.json
│
├── cypress/                       # E2E tests
│   ├── e2e/
│   ├── support/
│   └── cypress.config.ts
│
├── docs/                          # Documentation
│   ├── apps/
│   ├── dev/
│   ├── extension/
│   ├── packages/
│   └── plans/
│
├── tasks/                         # Task management
│   └── *.md files
│
├── .planning/                     # GSD planning documents
│   └── codebase/                  # This directory
│
├── .github/                       # GitHub Actions
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
│
├── .cursor/                       # Cursor IDE settings
├── .vscode/                       # VS Code settings
├── .claude/                       # Claude Code settings
│
├── package.json                   # Root monorepo config
├── pnpm-workspace.yaml            # pnpm workspaces
├── tsconfig.json                  # Root TypeScript config
├── .eslintrc.cjs                  # ESLint config
├── .prettierrc                    # Prettier config
└── wxt.config.ts                  # (appears at root, actually in extension/)
```

## Directory Purposes

**apps/account:**
- Purpose: User account dashboard, authentication UI, subscription management
- Contains: Next.js pages, API routes, server components, React components
- Key files: `src/app/` (file-based routing), `src/server/` (backend logic), `src/api/trpc/[trpc].ts`
- Entry: `src/app/layout.tsx` (root layout)
- API routes: `/api/trpc` (tRPC handler), `/api/auth/*` (Better Auth), `/api/v1/*` (REST endpoints)

**apps/marketing:**
- Purpose: Public website to promote Trail, showcase features, link to signup
- Contains: Next.js pages, static content, Sanity CMS integration
- Key files: `src/app/` (landing page, blog), `src/lib/sanity.ts` (CMS client)
- Entry: `src/app/page.tsx` (homepage)
- No extension communication (read-only content)

**extension/src/entrypoints:**
- Purpose: WXT entry points—each defines a UI surface or worker
- Contains: Component roots, initialization code, page templates
- Key files:
  - `background.ts`: Service worker (long-lived, no UI)
  - `content.ts`: Content script on allowed origins
  - `sidepanel/main.tsx`: Side panel UI root, index.html template
  - `newtab/main.tsx`: New tab page UI root
  - `spotlight-graph/main.tsx`: Spotlight search modal
  - `fullview/main.tsx`: Full-screen graph editor
  - `account/main.tsx`: Account page iframe
  - `offscreen-graph/main.tsx`: Offscreen document for graph processing

**extension/src/background:**
- Purpose: Service worker logic—persists across tab closes, manages all state
- Contains: Messaging router, navigation tracking, tab sync, auth orchestration, state modules
- Key files:
  - `service-worker.ts`: Initialization (imports all subsystems)
  - `messaging/router.ts`: Message dispatch system, Zod validation
  - `messaging/handlers/*.ts`: ~15 handler files (tabs, tree, tags, spotlight, etc.)
  - `navigation/webnavigation.ts`: Chrome API listener for page transitions
  - `navigation/history-api.ts`: History API wrapping
  - `navigation/redirect-detection.ts`: Redirect tracking
  - `tabs/lifecycle.ts`: Chrome tabs API listener (onCreated, onUpdated, onRemoved)
  - `tabs/sync-open-tabs.ts`: Initialize open tabs on boot
  - `state/nav-tree.ts`: Main navigation tree (immutable updates)
  - `state/tree-node.ts`: Node operations, structural sharing
  - `state/tab-manager.ts`: Tab-to-node mapping, bidirectional
  - `state/tab-index.ts`: Tab ID indexing
  - `state/tab-lru.ts`: Tab recency tracking
  - `state/pinned.ts`: Pinned node tracking
  - `state/node-recency.ts`: Node recency scores (LRU)
  - `services/sync/engine.ts`: Bidirectional sync with server
  - `services/sync/api.ts`: Sync API calls (fetch wrapper)
  - `services/sync/dirty-tracker.ts`: Mark modified nodes
  - `services/sync/migration.ts`: Handle sync format changes
  - `services/auth-orchestrator.ts`: Manage auth state, trigger sync on login
  - `services/account-keeper.ts`: Track account/user state
  - `services/auth-policy-keeper.ts`: Manage auth policy
  - `services/offscreen-graph-manager.ts`: Manage offscreen document

**extension/src/ui-core:**
- Purpose: Core UI rendering infrastructure shared across entrypoints
- Contains: React root setup, panel bootstrap logic, providers, hooks
- Key files:
  - `panel/bootstrap.tsx`: React root initialization with RPC client setup
  - `panel/styles.css`: Global panel styles
  - `components/`: Shared UI components
  - `hooks/`: Custom React hooks (useRpc, useBackground, etc.)
  - `providers/`: React context providers
  - `query/`: React Query client setup

**extension/src/content:**
- Purpose: Content script bridge—runs on web pages (account.gettrail.net)
- Contains: Bridge to service worker via Chrome messaging, security validation
- Key files:
  - `bridge/runtime.ts`: Main bridge logic (postMessage validation, nonce tracking, TTL enforcement)
  - `messaging/`: Content messaging utilities
  - `security/`: Input validation

**extension/src/shared/rpc:**
- Purpose: Type-safe RPC contracts between extension components
- Contains: 87 RPC method definitions, Zod schemas, response types
- Key files:
  - `contracts.ts`: All message types (RequestMessage, ResponseMessage, handlers)
  - `schema.ts`: Zod validation schemas (RPC_VERSION=2)
  - `client.ts`: RPC client (sendMessage wrapper)

**extension/src/shared/types:**
- Purpose: Type definitions used throughout extension
- Contains: Branded types, tree schema, tab types, settings
- Key files:
  - `ids.ts`: Branded types (NodeId, TabId, Tag, etc.) prevent ID confusion
  - `tree.ts`: NavigationTreeJSON schema, TreeMeta, TreeNode types
  - `tabs.ts`: TabState, Tab types
  - `settings.ts`: User Settings type
  - `tags.ts`: TagDefinition type
  - `flags.ts`: FeatureFlags type
  - `export.ts`: TrailExportBundle type

**packages/db:**
- Purpose: Prisma ORM setup and database client
- Contains: Prisma schema, generated client, migration files
- Key files:
  - `prisma/schema.prisma`: All models (User, Session, Trail, Device, etc.)
  - `prisma/migrations/`: Timestamped migration files
  - `src/client.ts`: Singleton PrismaClient with connection pooling

**packages/trpc:**
- Purpose: tRPC router for type-safe RPC to web apps
- Contains: Router definition, context setup, authentication middleware
- Key files:
  - `src/trpc.ts`: Router factory and tRPC instance
  - `src/router.ts`: App router (public + protected procedures)
  - `src/context.ts`: Request context (auth, user)
  - `src/extension-token.ts`: JWT signing/verification for extension auth

**packages/ui:**
- Purpose: Shared React component library (Radix UI + custom)
- Contains: Component library, TailwindCSS styling, icons
- Exports: Main components, icons, marketing components, auth UI, TailwindCSS preset
- Key files:
  - `src/index.ts`: Main component exports
  - `src/icons/index.ts`: Icon components (generated from lucide-react)
  - `src/tailwind-preset.ts`: TailwindCSS configuration preset

**extension/src/features:**
- Purpose: Feature-specific logic organized by domain
- Contains: Account features, auth, settings, tags, themes, tree operations
- Key files: Feature-specific modules (account, auth, settings, tags, themes, tree)

## Key File Locations

**Entry Points:**
- Extension background: `extension/src/entrypoints/background.ts`
- Extension side panel: `extension/src/entrypoints/sidepanel/main.tsx`
- Extension new tab: `extension/src/entrypoints/newtab/main.tsx`
- Extension spotlight: `extension/src/entrypoints/spotlight-graph/main.tsx`
- Extension content script: `extension/src/entrypoints/content.ts`
- Account web app: `apps/account/app/layout.tsx`
- Marketing web app: `apps/marketing/app/page.tsx`

**Configuration:**
- Extension build: `extension/wxt.config.ts` (WXT configuration, aliases, manifest)
- Extension TypeScript: `extension/tsconfig.json`, `extension/tsconfig.app.json`
- Account app: `apps/account/next.config.ts`
- Marketing app: `apps/marketing/next.config.ts`
- Prisma: `packages/db/prisma/schema.prisma`
- Tailwind: `packages/ui/src/tailwind-preset.ts`

**Core Logic:**
- Navigation tree state: `extension/src/background/state/nav-tree.ts`
- Message routing: `extension/src/background/messaging/router.ts`
- RPC contracts: `extension/src/shared/rpc/contracts.ts` (87 methods)
- Sync engine: `extension/src/background/services/sync/engine.ts`
- Tab manager: `extension/src/background/state/tab-manager.ts`
- Content bridge: `extension/src/content/bridge/runtime.ts` (security layer)
- tRPC router: `packages/trpc/src/router.ts`

**Testing:**
- Extension tests: `extension/tests/*.test.ts` (Node-based, no browser needed)
- Account app tests: `apps/account/src/**/__tests__/*.test.ts` (Vitest)
- E2E tests: `cypress/e2e/**/*.cy.ts`

## Naming Conventions

**Files:**
- Component files: PascalCase (e.g., `SearchBar.tsx`, `NewTabApp.tsx`)
- Utility/logic files: kebab-case or camelCase (e.g., `url-utils.ts`, `tree-storage.ts`, `debounce.ts`)
- Type/interface files: lowercase with no suffix (e.g., `contracts.ts`, `schema.ts`)
- Test files: `.test.ts` or `.spec.ts` suffix
- Handler files: `*-handlers.ts` (e.g., `tab-handlers.ts`, `tree-handlers.ts`)

**Directories:**
- Feature/feature-domain directories: kebab-case (e.g., `spotlight-graph`, `tag-handlers`, `sync`)
- Conceptual groupings: lowercase plural (e.g., `services`, `handlers`, `state`, `types`)
- Entrypoints: kebab-case or with dots (e.g., `sidepanel`, `newtab`, `spotlight-graph`, `spotlight.content`)

**Functions & Variables:**
- Hooks: `use*` prefix (e.g., `useSpotlightSearch`, `useRpc`)
- Handlers: `*Handler` or `handle*` pattern (e.g., `navigationHandler`, `handleTabCreated`)
- State getters/setters: `get*` or `set*` prefix (e.g., `getTree`, `setCurrentNode`)
- Utilities: camelCase, descriptive (e.g., `parseRpcRequestEnvelope`, `createMessageRouter`)
- Constants: UPPER_SNAKE_CASE (e.g., `RPC_METHOD`, `MESSAGE_TTL_MS`)

**Types:**
- Interfaces/Types: PascalCase (e.g., `TreeNode`, `SearchResult`, `RequestMessage`)
- Branded types: PascalCase (e.g., `NodeId`, `TabId`, `Tag`)
- Unions: Descriptive PascalCase (e.g., `RpcRequestEnvelope`, `SpotlightMode`)

## Where to Add New Code

**New Feature (Extension):**
- Main feature logic: `extension/src/features/<feature-name>/` for isolated features
- Background service logic: `extension/src/background/services/<service-name>/` for long-running services
- State module: `extension/src/background/state/<state-name>.ts` for state management
- RPC types: Add to `extension/src/shared/rpc/contracts.ts`
- RPC handler: Create `extension/src/background/messaging/handlers/<feature>-handlers.ts`
- UI components: `extension/src/entrypoints/<entrypoint>/ui/components/<feature>/`
- Tests: `extension/tests/<feature>.test.ts`

**New Web App Component (Account):**
- Page: `apps/account/src/app/<path>/page.tsx` (Next.js file-based routing)
- Layout: `apps/account/src/app/<path>/layout.tsx` (for grouping pages)
- Shared component: `apps/account/src/components/<section>/<ComponentName>.tsx`
- Server logic: `apps/account/src/server/<module>.ts`
- API route: `apps/account/src/app/api/<path>/route.ts`
- Tests: `apps/account/src/**/__tests__/<file>.test.ts`

**New Shared Component (UI Package):**
- Component: `packages/ui/src/components/<ComponentName>.tsx`
- Export in: `packages/ui/src/index.ts`
- Styles: Inline Tailwind classes or `packages/ui/styles/components.css`

**New Database Model:**
- Add model definition in: `packages/db/prisma/schema.prisma`
- Run migration: `pnpm db:migrate` (generates migration file, updates generated client)
- Access via: `extension/src/` imports `db` from `@trail/db`

**New RPC Handler:**
1. Add method to `RPC_METHOD` in `extension/src/shared/rpc/contracts.ts`
2. Define request/response types in same file
3. Create handler in `extension/src/background/messaging/handlers/<domain>-handlers.ts`
4. Register in router via `defineRpcHandlers()`
5. Add test case in `extension/tests/rpc-schema.test.ts`

**Utilities/Helpers:**
- Shared extension utils: `extension/src/shared/lib/` or `extension/src/shared/utils/`
- Background-specific: `extension/src/background/utils/`
- App-specific: `apps/account/src/lib/` (Next.js convention)

## Special Directories

**extension/src/entrypoints:**
- Purpose: WXT entry point files that define UI surfaces
- Generated: No (hand-written)
- Committed: Yes
- Note: Each file/directory becomes one UI page/worker in the built extension

**packages/db/prisma/migrations:**
- Purpose: Versioned database migration files
- Generated: Yes (by `prisma migrate dev`)
- Committed: Yes
- Update: Run `pnpm db:migrate` after modifying schema.prisma

**extension/src/shared/rpc:**
- Purpose: RPC contract definitions (87 methods)
- Generated: No (hand-written)
- Committed: Yes
- Note: Central source of truth for all extension-to-extension communication

**.planning/codebase:**
- Purpose: GSD codebase analysis documents
- Generated: Yes (by GSD tools)
- Committed: Yes
- Files: ARCHITECTURE.md, STRUCTURE.md, STACK.md, INTEGRATIONS.md, CONVENTIONS.md, TESTING.md, CONCERNS.md

**docs/**
- Purpose: Architecture docs, API docs, setup guides
- Generated: No (hand-written)
- Committed: Yes

---

*Structure analysis: 2025-03-18*
