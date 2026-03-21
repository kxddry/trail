# Coding Conventions

**Analysis Date:** 2026-03-17

## Naming Patterns

**Files:**
- React components (PascalCase): `OnboardingGate.tsx`, `SignOutButton.tsx`, `BillingPlansClient.tsx`
- API route files: `page.tsx` for Next.js routes, `route.ts` for API handlers
- Utility/helper functions (camelCase): `json.ts`, `user.ts`, `url-utils.ts`
- Test files: co-located with implementation using `__tests__` directories or `.test.ts` suffix
  - Example: `src/server/backend/__tests__/json.test.ts` for `src/server/backend/json.ts`

**Functions:**
- camelCase for all functions: `ensureUser`, `getUserById`, `mergeTrailUpdates`, `resolveImageUrl`
- Async functions named clearly: `markUserOnboardingSeen`, `resetUserOnboarding`, `handleComplete`
- Event handlers prefixed with `handle` or `go`: `handleComplete`, `goNext`, `goPrev`, `dismiss`
- Hook functions prefixed with `use`: `useCallback`, `useEffect`, `useRef`, `useState`
- Custom React hooks: `useMediaQuery` (see `packages/ui/src/marketing/hooks/use-media-query.ts`)

**Variables:**
- Local state: camelCase for most variables: `currentStep`, `direction`, `busy`, `error`, `status`
- Boolean prefixes: `is*`, `should*`: `isFirst`, `isLast`, `isCycleOrderValid`, `shouldSuppressTouch`
- Refs end with `Ref`: `pollRef`, `previousNodeId`
- Maps/collections often use descriptive names: `suppressActivateForTabId`, `cycleOrderByNode`, `ignoredTabs`
- Constants (top-level): UPPER_SNAKE_CASE: `TOMBSTONE_RETENTION_DAYS`, `POLL_INTERVAL_MS`, `AUTH_COOKIE_NAME`, `TOTAL`

**Types:**
- PascalCase for types and interfaces: `AuthUser`, `UserSummary`, `OnboardingState`, `TrailUpsertInput`
- Type aliases placed near their usage site
- Generic type parameters: uppercase single letters (`T`, `U`) or descriptive names
- Type-only imports using `import type`: `import type { AppUser } from "@trail/trpc"`
- Union types for status enums: `type OnboardingStatus = "pending" | "completed"`

## Code Style

**Formatting:**
- ESLint used via `eslint.config.mjs` (flat config format with Next.js core web vitals)
- Prettier not enforced globally but defined in package scripts via `pnpm format`
- Indentation: 2 spaces (observed throughout codebase)
- Line length: wrap at reasonable boundaries (observed ~100 chars)
- Imports organized in groups (no explicit require file, follows Next.js defaults)

**Linting:**
- ESLint runs via `npm run lint` (root) and per-app with `pnpm lint`
- Config file: `/Users/iv/dev/trail/eslint.config.mjs` (uses `eslint-config-next/core-web-vitals`)
- Ignores: `node_modules`, `.next`, `out`, `build`, `dist`, `coverage`, Prisma generated code, extension
- Build failure on lint errors recommended per `/Users/iv/dev/trail/CLAUDE.md`

## Import Organization

**Order:**
1. Node.js standard library imports (`crypto`, `path`, etc.)
2. Third-party packages (`react`, `next/`, `@radix-ui/`, etc.)
3. Type-only imports (`import type { ... }`)
4. Internal absolute path imports (`@/`, `@trail/`, `@shared/`)
5. Relative imports (rare, use absolute paths preferred)

**Path Aliases:**
- `@/` - Root of current app (see `vitest.config.ts` aliases)
- `@trail/` - Monorepo packages (`@trail/db`, `@trail/trpc`, `@trail/ui`, `@trail/config`)
- `@shared/` - Extension shared code
- Configured in `tsconfig.json` per app (e.g., `apps/account` maps `@` to `.`)

**Barrel Files:**
- Limited use of barrel files (`index.ts`)
- `packages/ui/src/index.ts` exports components
- `packages/ui/src/icons/index.ts` exports icon mappings
- Generally avoid to prevent circular dependencies

## Error Handling

**Patterns:**
- Explicit null checking: `if (!record) { return null; }`
- Null coalescing operator: `value ?? defaultValue`
- Try-catch with meaningful errors: See `apps/account/src/lib/auth.ts` with fallback to extension auth on JWT failure
- Logging errors for debugging: `console.warn("[auth] JWT verification failed", { error })`
- API responses: See `apps/account/src/server/backend/error-response.ts` for consistent error envelope
- No silent error swallowing - errors logged or returned
- Type guards for validation: `isJsonValue()` function checks structure before processing

## Logging

**Framework:** `console` (direct logging, no logging library imported)

**Patterns:**
- Server-side logging prefixed with context: `console.warn("[auth] JWT verification failed")`
- Logs include error details for debugging: `error: error instanceof Error ? error.message : String(error)`
- No logging in production UI code observed
- Errors logged before fallback mechanisms trigger

## Comments

**When to Comment:**
- Explain "why" not "what" (code is readable enough)
- Complex merge logic gets section comments: `/* ---- Merge logic ---- */`
- Type definitions documented with JSDoc for public APIs
- Environment notes in setup files

**JSDoc/TSDoc:**
- Vitest environment comments: `/** @vitest-environment node */`
- Function return types documented via TypeScript signatures
- Minimal JSDoc bloat, types speak for themselves

## Function Design

**Size:** Functions kept small and focused
- `resolveImageUrl`: 3 lines
- `isJsonValue`: 26 lines with detailed logic
- `getUserFromToken`: ~45 lines for complex async flow
- Threshold: Keep under 50 lines, extract helpers for complex branches

**Parameters:**
- Explicit parameters preferred: `register(nodeId: NodeId, tabId: TabId, options?: {...})`
- Options objects for optional grouped parameters
- Named parameters in descriptions for clarity

**Return Values:**
- Null for "not found" scenarios (no exceptions thrown for missing data)
- Promise types explicit: `async function foo(): Promise<Type | null>`
- Union types for multiple outcomes: `{ applied: boolean }`
- Type narrowing via type guards: `value is JsonValue`

## Module Design

**Exports:**
- Named exports standard: `export function ensureUser(...)`
- Type exports: `export type AuthUser = { ... }`
- Default exports used for React components: `export default function OnboardingGate(...)`
- Server-only directive used for backend modules: `import "server-only"` at top of file

**File Organization:**
- Type definitions at top of file (before implementations)
- Helper functions above primary exports
- Comments separating logical sections
- Constants declared at module level
- Monorepo structure:
  - `apps/*/src/server/` - Backend/API code
  - `apps/*/app/` - Next.js app router pages and layouts
  - `packages/*/src/` - Shared packages
  - `extension/src/` - Browser extension code

## Import Patterns

**Absolute imports required:**
- Use `@/` for app-relative, `@trail/` for monorepo packages
- Never relative imports like `../../../`
- Exception: Within same directory may be minimal (not observed in practice)

**TypeScript-specific:**
- Always use `import type` for type-only imports
- Never re-export types without `export type`
- Avoid circular dependencies (monorepo packages split carefully)

---

*Convention analysis: 2026-03-17*
