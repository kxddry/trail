# Codebase Structure

**Analysis Date:** 2026-03-17

## Directory Layout

```
trail/
├── apps/                          # Web applications (Next.js)
│   ├── account/                   # Account dashboard & auth
│   ├── marketing/                 # Public marketing site
│   └── video/                     # (excluded from most builds)
├── extension/                     # Browser extension (primary client)
│   ├── src/
│   │   ├── entrypoints/           # WXT entry points (UI pages & workers)
│   │   ├── background/            # Service worker logic
│   │   ├── spotlight/             # Search modal components & logic
│   │   ├── shared/                # Extension-wide utilities & types
│   │   ├── features/              # Feature-specific logic
│   │   ├── ui-core/               # Core UI utilities
│   │   └── content/               # Content script bridge
│   └── public/                    # Static assets (icons)
├── packages/                      # Shared libraries
│   ├── db/                        # Prisma ORM & database client
│   ├── trpc/                      # tRPC router & procedures
│   ├── ui/                        # React component library
│   ├── content/                   # Content type definitions
│   └── config/                    # Configuration utilities
├── sanity/                        # Sanity CMS schema (marketing content)
├── cypress/                       # E2E tests
├── docs/                          # Documentation
├── tasks/                         # Task management & notes
├── .planning/                     # GSD planning documents
└── .github/                       # GitHub Actions workflows
```

## Directory Purposes

**apps/account:**
- Purpose: User account dashboard, authentication UI, subscription management
- Contains: Next.js pages, API routes, server components, React components
- Key files: `src/app/` (file-based routing), `src/server/` (backend logic)
- Entry: `src/app/layout.tsx` (root layout), pages in `src/app/**/**/page.tsx`

**apps/marketing:**
- Purpose: Public website to promote Trail, showcase features, link to signup
- Contains: Next.js pages, static content, Sanity CMS integration
- Key files: `src/app/` (landing page, blog), Sanity client connection
- Entry: `src/app/page.tsx` (homepage)

**extension/src/entrypoints:**
- Purpose: WXT entry points—each defines a UI surface or worker
- Contains: Component roots, initialization code
- Key files:
  - `background.ts`: Service worker initializer
  - `sidepanel/main.tsx`: Side panel UI root
  - `newtab/main.tsx`: New tab page UI root
  - `spotlight.content/index.tsx`: Spotlight search modal
  - `account/main.tsx`: Account page inside extension
  - `fullview/main.tsx`: Full-screen graph view

**extension/src/background:**
- Purpose: Service worker logic—persists across tab closes, manages state
- Contains: Messaging router, navigation tracking, tab sync, auth orchestration
- Key files:
  - `service-worker.ts`: Initialization hub
  - `messaging/router.ts`: Message dispatch system
  - `messaging/handlers/*.ts`: ~15 handler files (tab, navigation, settings, tree, tags, etc.)
  - `navigation/webnavigation.ts`: Chrome API listener for page transitions
  - `tabs/lifecycle.ts`: Chrome tabs API listener
  - `state/*.ts`: In-memory state modules (tree, tabs, pinned, recency)
  - `services/sync/engine.ts`: Bidirectional sync with server

**extension/src/spotlight:**
- Purpose: Search UI and interaction logic (components reusable across entrypoints)
- Contains: React hooks, UI components for search modal
- Key files:
  - `useSpotlightSearch.ts`: Hook managing search sessions and results
  - `useSpotlightKeyboard.ts`: Keyboard navigation logic
  - `useSpotlightActions.ts`: Action execution (navigate, tag, delete)
  - `SpotlightApp.tsx`: Component tree for modal

**extension/src/shared:**
- Purpose: Utilities, types, and helpers used across background and UI code
- Contains: RPC schema/client, type definitions, browser API abstractions
- Key files:
  - `rpc/contracts.ts`: Message type definitions and handler signatures
  - `rpc/schema.ts`: Zod schemas for envelope validation
  - `rpc/client.ts`: Send RPC messages from content/UI to background
  - `types/tree.ts`: Navigation tree JSON schema and TypeScript types
  - `types/ids.ts`: Type-safe ID branding (NodeId, TabId, etc.)
  - `platform/webext.ts`: Chrome API abstractions
  - `config/backend.ts`: Backend URL configuration (local/production/gettrail)
  - `lib/commands.ts`: Command history (undo/redo)

**extension/src/features:**
- Purpose: Feature flags and feature-specific modules
- Contains: Flag definitions and feature-gated code paths

**extension/src/ui-core:**
- Purpose: Core UI rendering infrastructure
- Contains: React root setup, panel bootstrap logic
- Key files: `panel/bootstrap.tsx`: Initializes React app with RPC client

**extension/src/content:**
- Purpose: Content script bridge—runs on web pages
- Contains: Bridge to service worker via Chrome messaging
- Key file: `bridge/runtime.ts`: Establishes port connection

**packages/db:**
- Purpose: Prisma ORM setup and database client
- Contains: Prisma schema, generated client, migration files
- Key files:
  - `prisma/schema.prisma`: All models (User, Session, Trail, Device, etc.)
  - `src/client.ts`: Singleton PrismaClient with connection pooling

**packages/trpc:**
- Purpose: tRPC router for type-safe RPC to web apps
- Contains: Router definition, context, authentication middleware
- Key files:
  - `src/trpc.ts`: Router and procedure factory
  - `src/router.ts`: App router (currently simple, extends with auth routes)
  - `src/extension-token.ts`: JWT signing/verification for extension auth

**packages/ui:**
- Purpose: Shared React components (Radix UI + custom)
- Contains: Component library, TailwindCSS styling, icons
- Exports: Main components, icons, marketing components, auth UI components, TailwindCSS preset
- Key files:
  - `src/index.ts`: Main component exports
  - `src/icons/`: Icon components (generated from lucide-react)
  - `styles/`: Global CSS, component styles

**packages/content:**
- Purpose: Content type definitions and utilities
- Contains: Type definitions for content, structured data schemas
- Used by: UI components for type safety

## Key File Locations

**Entry Points:**
- Extension background: `extension/src/entrypoints/background.ts`
- Extension side panel: `extension/src/entrypoints/sidepanel/main.tsx`
- Extension new tab: `extension/src/entrypoints/newtab/main.tsx`
- Account web app: `apps/account/src/app/layout.tsx` + page files
- Marketing web app: `apps/marketing/src/app/page.tsx`

**Configuration:**
- Extension build: `extension/wxt.config.ts` (WXT configuration)
- Account app: `apps/account/next.config.ts`
- Marketing app: `apps/marketing/next.config.ts`
- Prisma: `packages/db/prisma/schema.prisma`
- Tailwind: `packages/ui/src/tailwind-preset.ts`

**Core Logic:**
- Navigation tree state: `extension/src/background/state/nav-tree.ts`
- Message routing: `extension/src/background/messaging/router.ts`
- Sync engine: `extension/src/background/services/sync/engine.ts`
- Tab manager: `extension/src/background/state/tab-manager.ts`
- Spotlight search: `extension/src/spotlight/useSpotlightSearch.ts`
- RPC contracts: `extension/src/shared/rpc/contracts.ts`

**Testing:**
- Extension tests: `extension/tests/*.test.ts` (Node-based)
- Account app tests: `apps/account/src/**/__tests__/*.test.ts` (Vitest)
- E2E tests: `cypress/e2e/**/*.cy.ts`

## Naming Conventions

**Files:**
- Component files: PascalCase (e.g., `SearchBar.tsx`, `NewTabApp.tsx`)
- Utility/logic files: camelCase (e.g., `url-utils.ts`, `tree-storage.ts`, `debounce.ts`)
- Type/interface files: Sometimes camelCase prefix (e.g., `contracts.ts`), explicit types in exports
- Test files: `.test.ts` or `.spec.ts` suffix

**Directories:**
- Feature/feature-domain directories: kebab-case (e.g., `spotlight-graph`, `tag-handlers`)
- Conceptual groupings: lowercase plural (e.g., `services`, `handlers`, `state`, `types`)
- Entrypoints: lowercase with hyphens (e.g., `sidepanel`, `newtab`, `spotlight.content`)

**Functions & Variables:**
- Hooks: `use*` prefix (e.g., `useSpotlightSearch`, `useSearch`)
- Handlers: `*Handler` or `*Handlers` suffix (e.g., `navigationHandlers`, `tagHandlers`)
- State setters: `set*` prefix (e.g., `setQuery`, `setSelectedKey`)
- Utilities: camelCase, descriptive names (e.g., `parseRpcRequestEnvelope`, `createMessageRouter`)

**Types:**
- Interfaces: PascalCase (e.g., `TreeNode`, `SearchResult`)
- Branded types: PascalCase (e.g., `NodeId`, `TabId`)
- Unions: Descriptive PascalCase (e.g., `RpcRequestEnvelope`)

## Where to Add New Code

**New Feature (Extension):**
- Main feature logic: `extension/src/features/<feature-name>/` or `extension/src/background/services/<service-name>/`
- UI components: `extension/src/entrypoints/<entrypoint>/ui/components/<feature>/`
- RPC types: Add to `extension/src/shared/rpc/contracts.ts`
- RPC handler: Create `extension/src/background/messaging/handlers/<feature>-handlers.ts`
- Tests: `extension/tests/<feature>.test.ts`

**New Web App Component (Account):**
- Page: `apps/account/src/app/<path>/page.tsx` (Next.js file-based routing)
- Layout: `apps/account/src/app/<path>/layout.tsx` (if grouping pages)
- Shared component: `apps/account/src/components/<section>/<ComponentName>.tsx`
- Server logic: `apps/account/src/server/<module>.ts`
- Tests: `apps/account/src/**/__tests__/<file>.test.ts`

**New Shared Component (UI Package):**
- Component: `packages/ui/src/components/<ComponentName>.tsx`
- Export in: `packages/ui/src/index.ts`
- Styles: Inline Tailwind classes or `packages/ui/styles/components.css`

**New Database Model:**
- Add model definition in: `packages/db/prisma/schema.prisma`
- Run migration: `pnpm db:migrate` (generates migration file, updates client)
- Access via: `extension/src/` code imports `db` from `@trail/db`

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

**packages/db/src/generated:**
- Purpose: Auto-generated Prisma client
- Generated: Yes (by `prisma generate`)
- Committed: No (in .gitignore)
- Update: Run after modifying `schema.prisma`

**extension/src/spotlight:**
- Purpose: Reusable spotlight search logic used in multiple entrypoints
- Generated: No
- Committed: Yes
- Note: Components and hooks extracted from entrypoint-specific code for reuse

**docs/**:**
- Purpose: Architecture docs, API docs, setup guides
- Generated: No (hand-written)
- Committed: Yes
- Note: Some auto-generated docs (e.g., from JSDoc)

**.planning/**:**
- Purpose: GSD planning documents and analysis
- Generated: Yes (by GSD tools)
- Committed: Yes
- Note: Contains analysis of codebase, implementation plans, phase tracking

---

*Structure analysis: 2026-03-17*
