# Technology Stack

**Analysis Date:** 2026-02-28

## Languages

**Primary:**
- TypeScript 5.9.3 - All backend services, UI components, content scripts
- JavaScript (JSX/TSX) 19.2.4 - React UI layer

**Secondary:**
- Node.js (runtime) - Build scripts, CLI tools

## Runtime

**Environment:**
- Node.js (development)
- Chrome/Chromium browser (production execution)

**Package Manager:**
- pnpm 10.29.3
- Lockfile: `pnpm-lock.yaml` (present)

## Frameworks

**Core:**
- React 19.2.4 - UI components and state management
- WXT 0.20.18 - Browser extension framework and build tool

**Graphics & Visualization:**
- Pixi.js 8.16.0 - WebGL-based graph rendering engine with CSP-safe eval polyfill

**UI & Styling:**
- Tailwind CSS 4.2.1 - Utility-first CSS framework
- PostCSS 8.5.6 - CSS processing pipeline
- Autoprefixer 10.4.27 - CSS vendor prefix generation

**State Management:**
- Zustand 5.0.11 - Lightweight client state management
- React Query (@tanstack/react-query) 5.90.21 - Server state and data fetching

**Animations & Motion:**
- Motion 12.34.3 - React animation library

**Icons & UI Components:**
- Lucide React 0.575.0 - SVG icon library
- Radix UI (react-slot) 1.2.4 - Primitives for accessible UI

**Data & Validation:**
- Zod 4.3.6 - TypeScript-first schema validation
- minisearch 7.2.0 - Full-text search for client-side indexing

**Toast Notifications:**
- Sonner 2.0.7 - Toast notification component library

**CSS Utilities:**
- class-variance-authority 0.7.1 - Type-safe CSS variant patterns
- clsx 2.1.1 - Conditional className utility
- tailwind-merge 3.5.0 - Merge Tailwind CSS classes intelligently

**Data Compression:**
- fflate 0.8.2 - Fast DEFLATE compression for export bundles

## Build & Development Tools

**Build System:**
- Vite 7.3.1 - Fast module bundler for UI
- @vitejs/plugin-react 5.1.4 - React plugin for Vite

**Code Quality:**
- ESLint 9.39.2 - JavaScript/TypeScript linting
- @typescript-eslint/parser 8.56.1 - TypeScript parser for ESLint
- @typescript-eslint/eslint-plugin 8.56.1 - TypeScript ESLint rules

**Code Generation:**
- sharp 0.34.5 - Image processing for icon generation
- tsx 4.21.0 - TypeScript execution for Node.js scripts

**Type Checking:**
- @types/chrome 0.1.37 - Chrome Extension API types
- @types/node 25.3.2 - Node.js type definitions
- @types/react 19.2.14 - React type definitions
- @types/react-dom 19.2.3 - React DOM type definitions

## Key Dependencies

**Critical Infrastructure:**
- WXT 0.20.18 - Handles manifest generation, bundling, content scripts, background workers for MV3
- Pixi.js 8.16.0 - Performance-critical WebGL rendering with CSP-safe polyfills for graph visualization

**Data Layer:**
- React Query 5.90.21 - Server state synchronization and caching
- Zustand 5.0.11 - UI state (tree navigation, editor mode, selections)

**UI/UX:**
- React 19.2.4 - Component framework
- Tailwind CSS 4.2.1 - Styling system
- Motion 12.34.3 - Animation effects

**Search & Indexing:**
- minisearch 7.2.0 - Client-side full-text search for navigation trees

**Utilities:**
- Zod 4.3.6 - Runtime validation for API responses and config
- fflate 0.8.2 - Compression for tree exports/archives
- Lucide React 0.575.0 - Icon assets

## Configuration

**Environment:**
- Configuration: `wxt.config.ts` (manifest, dev server, browser profiles)
- Backend: `src/shared/config/backend.ts` (switchable: production/staging/local)
- Storage keys: `src/shared/config/storage-keys.ts` (Chrome storage keys)
- Site origins: `src/shared/config/site-origins.js` (host permissions)

**Build:**
- TypeScript configs:
  - `tsconfig.json` - Main backend/extension TypeScript config
  - `tsconfig.app.json` - UI-specific config (excludes TSX files from main compilation)
- PostCSS: `postcss.config.cjs`
- Tailwind: `tailwind.config.cjs` (content targeting UI components)
- ESLint: Not committed (uses ESLint 9 flat config pattern)

**Runtime Configuration:**
- Backend config: Resolved from `src/shared/config/backend.ts` with overrides from:
  - Build preset: `backend-preset.json` (tag: 'production', 'gettrail', 'local')
  - Chrome storage: Persisted overrides via `initBackendConfig()`
  - Environment: production/staging/local support

## Platform Requirements

**Development:**
- Node.js 18+ (for tsx, esbuild, sharp)
- pnpm 10.29.3
- macOS/Linux/Windows with npm/pnpm support
- Chrome/Chromium for extension testing

**Production:**
- Chrome/Chromium 91+ (Manifest V3 support)
- Firefox 109+ (Manifest V2 via wxt transpilation)
- 10MB+ local storage quota (Chrome storage.local)
- Background service worker support

**Deployment Target:**
- Chrome Web Store (MV3)
- Firefox Add-ons (MV2 via wxt)

## Special Build Notes

**Sharp Polyfill:**
- `"sharp"` in `onlyBuiltDependencies` - Native binary dependency, must be installed with build tools

**Pixi.js CSP Compatibility:**
- Imports `pixi.js/unsafe-eval` polyfill at `src/sidepanel/ui/graph/pixi-no-eval-bootstrap.ts`
- Required for MV3 Content Security Policy compliance

**Manifest V3 Structure:**
- Service worker entrypoint: `src/background/service-worker.ts`
- Content scripts: `src/content/content-script.ts`
- UI panels: `src/sidepanel/ui/main.tsx`, `src/fullview/ui/main.tsx`

---

*Stack analysis: 2026-02-28*
