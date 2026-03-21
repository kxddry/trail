# Phase 6: Security & Privacy Audit - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Extension manifest, logging, and cross-boundary communication are locked down for public Chrome Web Store submission. Covers: permission audit, domain lockdown, search suggestions privacy, structured logging, redaction, protocol hardening, CSP documentation.

</domain>

<decisions>
## Implementation Decisions

### Permission Audit (SEC-01, SEC-02)
- CRITICAL: Verify each permission removal won't break runtime behavior before removing
- `scripting`: confirmed 0 calls to `chrome.scripting.*` — remove after build verification
- `search`: confirmed 0 calls to `browser.search.*` — Google Suggest uses raw fetch(), not browser.search API. Remove after build verification.
- `activeTab`: verify whether tab operations depend on it. If removing breaks anything, KEEP it and document why.
- User explicitly warned: "убедись, что расширение будет работать так, как надо, потому что оно сломаться просто может"
- After removal: do a full `pnpm build` and verify extension loads cleanly in Chrome

### Domain Lockdown (SEC-03)
- Dev origins already stripped at build time via `NODE_ENV !== "production"` dead code elimination
- Verify prod manifest contains only `https://gettrail.net/*` and `https://app.gettrail.net/*`
- Add a build-time assertion or architecture-boundaries test to verify no localhost in prod manifest

### Search Suggestions Toggle (SEC-04)
- Add toggle in SettingsPopover: "Search suggestions" (default: on)
- One-line note below: "When enabled, queries are sent to Google for suggestions"
- When off, skip the fetch to `google.com/complete/search` — return empty array
- Persist toggle to `chrome.storage.local`

### Structured Logger Migration (SEC-05)
- Replace raw `console.*` with `createLogger(namespace)` on critical path: auth, sync, storage, search
- Scope: ~30 files with raw console.* on these paths
- Leave debug/trace console.log in other files as-is
- Logger already exists at `src/shared/lib/logger.ts` — just needs adoption

### Redaction Policy (SEC-07)
- Add `redact` utility to logger: URLs shortened to domain-only, titles omitted, tokens replaced with `[redacted]`
- Apply automatically in logger.error() and logger.warn() output
- Pattern: `redactSensitive(data: unknown): unknown` — recursively processes objects
- Fields to redact: `url` → domain only, `title` → omitted, `token`/`accessToken`/`refreshToken` → `[redacted]`

### Protocol Boundary Hardening (SEC-08)
- Add Zod parse at background ingress in `site-message-handlers.ts`
- Parse incoming payload through existing Zod schemas from `shared/schemas/site-messages.ts`
- Currently payload arrives as `Record<string, unknown>` with manual typeof guards — replace with full Zod validation
- Reject messages that don't match schema (log warning, return error response)

### CSP Documentation (SEC-09)
- Rename comment in `pixi-no-eval-bootstrap.ts` to clearly explain: "This import REMOVES eval usage, making PixiJS CSP-compliant. The module name is misleading."
- Create brief `extension/CSP-RATIONALE.md` explaining: MV3 default strict CSP, pixi.js/unsafe-eval polyfill removes eval, no actual unsafe-eval in manifest

### Claude's Discretion
- Exact redaction implementation (regex vs field-name matching)
- Which specific files to migrate to structured logger (prioritize highest-traffic paths)
- Whether to add ESLint rule banning raw console.* in background/ directory (optional, not required)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `createLogger(namespace)` in `src/shared/lib/logger.ts` — exists, has dev/prod gating, 0 adoption
- Zod schemas in `shared/schemas/site-messages.ts` — cover all message types, just not used at background ingress
- `site-origins.ts` — dev/prod domain switch already compile-time gated
- Architecture-boundaries test — can be extended to verify prod manifest

### Integration Points
- `wxt.config.ts` — permissions list
- `SettingsPopover.tsx` — search suggestions toggle
- `search-suggestions.ts` — Google Suggest fetch, needs toggle check
- `site-message-handlers.ts` — payload validation
- ~30 files with raw console.* on critical paths

</code_context>

<specifics>
## Specific Ideas

Permission removal is the highest-risk item. Executor must verify with actual build + manifest inspection after each permission removal.

</specifics>

<deferred>
## Deferred Ideas

None

</deferred>
