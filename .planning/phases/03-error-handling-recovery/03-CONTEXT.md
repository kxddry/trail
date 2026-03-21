# Phase 3: Error Handling & Recovery - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Every failure the user can encounter produces a clear, actionable UI state instead of a broken or half-mounted screen. Covers: transient operation errors (toast), crash recovery (ErrorBoundary), bootstrap failure (degraded state), cache corruption (auto-reset), offscreen fallback, navigation failure recovery, and quota eviction notice.

</domain>

<decisions>
## Implementation Decisions

### Error Surface Pattern
- Transient errors surface via `toast.error()` from sonner (already wired, consistent with existing `toast.success()`)
- Error toasts auto-dismiss in 8s (same as success toasts) — not persistent
- Add `closeButton` to sonner `<Toaster>` config so users can dismiss early
- Create centralized `showOperationError(op: string, error: unknown)` helper that wraps `toast.error` with operation context (e.g. "Rename failed: network error")
- Apply to all currently-silent error paths: sync, rename, export, open, create tree, delete archive, navigateTo

### ErrorBoundary Crash Screen
- "Copy diagnostics" button copies: error.message + componentStack + extension version (from manifest) + user agent + ISO timestamp
- "Reload with safe mode" clears layout cache (`chrome.storage.session`) + clears known localStorage keys, then reloads
- Stack trace shown in collapsible `<details>` element — hidden by default, expandable for power users
- Keep existing "Reload Trail" and "Contact Support" buttons

### Bootstrap Recovery
- Critical-path `Promise.all` gets 10s timeout — if exceeded, show degraded UI
- Degraded UI: centered message "Could not load Trail" with "Retry" button and "Report issue" link
- Auto-retry once after 5s, then show permanent degraded state with retry button
- Deferred fetches (tags, trees, commands) continue to catch independently — they already do

### Cache Corruption Recovery
- Wrap `hydrateFromCache` in try/catch — if stored value is malformed JSON or missing fields, auto-delete that cache entry
- Show toast: "Layout cache was corrupted and has been reset"
- No full localStorage wipe — surgical removal of the broken entry only

### Offscreen Layout Fallback
- If offscreen document creation fails, continue with synchronous layout (existing behavior)
- Add toast.warning: "Using basic layout mode" so user knows performance may differ
- No retry — offscreen failure is typically persistent (quota, API unavailable)

### navigateTo Recovery
- Wrap all `navigateTo` call sites in try/catch
- On failure: `toast.error("Could not open page: {reason}")` + keep UI in current state (don't close dropdown/menu)
- Special-case: if error contains "tab" or "window", suggest "Try opening manually"

### Quota Eviction & Stub Archives
- When `evictOldestArchive()` runs, show `toast.warning("Archived tree '{name}' moved to cloud to save space")`
- In TreeDropdown, stub trees show cloud icon + muted "(cloud)" label
- If `ensureTreeLoaded` fails for a stub, show `toast.error("Could not load tree from cloud")` + mark entry as "unavailable" (don't remove from list)

### Claude's Discretion
- Exact wording of error messages — keep concise and non-technical
- Whether to group rapid-fire errors into a single toast or show individually
- Implementation of the centralized error helper — function signature and location

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `sonner` package with `<Toaster>` already mounted in App.tsx — `toast.success()` used in 2 places
- `ErrorBoundary.tsx` exists with basic crash screen (logo, reload, support)
- `useBootstrap.ts` has critical/deferred fetch split already implemented
- `chrome.storage.session` used for layout cache with signature-based validation
- `offscreen-graph-manager.ts` handles offscreen document lifecycle
- `quota-manager.ts` has `evictOldestArchive()` with retry logic

### Established Patterns
- `sendMessage(rpc.X(...))` → `{ success, data, error }` response envelope for all RPC calls
- `navigateTo()` in `src/apps/sidepanel/api/tree.ts` throws on `!res.success`
- TreeDropdown already reads `stub` flag and has `loadingTreeId` spinner state
- Error handling is currently `console.error` only — no toast.error anywhere

### Integration Points
- `App.tsx` — Toaster config update (closeButton)
- `ErrorBoundary.tsx` — crash screen enhancement
- `useBootstrap.ts` — timeout + degraded state
- `ContextMenus.tsx` — navigateTo error handling
- `PinnedDropdown.tsx` — navigateTo error handling
- `TreeDropdown.tsx` — sync/rename/export/delete/stub error handling + stub UI
- `cache.ts` / `GraphCanvas.tsx` — cache corruption handling
- `offscreen-graph-manager.ts` — fallback toast
- `quota-manager.ts` — eviction toast

</code_context>

<specifics>
## Specific Ideas

User specified: unified error → toast/banner layer, ErrorBoundary with Copy diagnostics and Reload with safe mode, bootstrap recovery, localStorage auto-reset, offscreen fallback, navigateTo recovery, stub archive explanation, quota eviction notice.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>
