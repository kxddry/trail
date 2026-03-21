# Phase 4: Stability & Concurrency - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Rapid user actions (quick open/close, double-clicks, panel restarts) never produce duplicate requests, stale UI, or silent auth failures. Covers: bootstrap re-entry, double-submit prevention, SESSION_EXPIRED in all surfaces, editorMode persistence, sync status indicator.

</domain>

<decisions>
## Implementation Decisions

### Bootstrap Re-entry Guard (STAB-02)
- Add `bootstrapInFlight` ref to useBootstrap — skip if already running
- Prevents duplicate critical-path fetches on rapid sidepanel open/close
- Existing `mounted` ref is insufficient — it doesn't prevent overlapping Promise.all calls

### Double-Submit Prevention (STAB-03)
- Add `isPending` state guard to 4 unprotected mutating actions: rename, node-delete, bulk-delete, archive-delete
- Pattern: `const [isPending, setIsPending] = useState(false)` + early return if pending + disabled prop on trigger
- Auth submit and create tree already have guards — leave untouched

### SESSION_EXPIRED in Newtab (STAB-06)
- Show inline banner similar to sidepanel — "Session expired, sign in to sync"
- Reuse SessionExpiredBanner component or create lightweight variant
- Mount in newtab app root, driven by same authSessionItem storage watch

### SESSION_EXPIRED in Spotlight (STAB-06)
- After 3 failed recovery retries, show small "sign in" link in search results area
- Current recovery logic (exponential backoff) stays — just add final fallback UI
- Link opens auth portal flow via existing useAuthPortalFlow

### editorMode Persistence (STAB-08)
- Persist editorState to `chrome.storage.session` (not localStorage — session storage survives SW restart within browser session)
- On SW restart, read from storage.session instead of in-memory default
- On bootstrap, editorMode restored from background snapshot as before — but now the snapshot reads from durable storage

### Sync Status Indicator (HYG-04)
- Small dot/icon in Header bar next to settings gear
- States: syncing (spinner), offline (orange dot), error (red dot), idle (hidden/green)
- Reads from existing `syncStatus` and `network` store fields — already set by useRuntimeMessages and useAccount
- Remove "degraded" network status from store since it's never set — keep only online/offline

### Claude's Discretion
- Exact placement of sync indicator within Header layout
- Whether to show "saved" state briefly (flash green then hide) or keep always hidden when idle
- SessionExpiredBanner component reuse strategy for newtab

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Auth orchestrator already has single-flight via `this.inFlight` — no changes needed
- Spotlight search has `requestSeqRef` stale-response guard — no changes needed
- `syncStatus` Zustand field already set by useRuntimeMessages, just never consumed in UI
- `network` online/offline already set by useAccount via window events
- SessionExpiredBanner exists in sidepanel — can be extracted or duplicated for newtab
- editorState in `editor-handlers.ts` is module-level variable — needs chrome.storage.session wrapper

### Established Patterns
- `isPending` + `disabled` for double-submit (see TreeDropdown create tree, SessionExpiredBanner auth)
- `chrome.storage.session` used for layout cache — same pattern for editorMode
- `useRuntimeMessages` listens for background broadcasts — used for sync status updates

### Integration Points
- `useBootstrap.ts` — re-entry guard
- `TreeDropdown.tsx` — rename isPending
- `ContextMenus.tsx` — delete isPending
- `editor-handlers.ts` — chrome.storage.session persistence
- `Header.tsx` or `FloatingControls.tsx` — sync status indicator
- `newtab/App.tsx` or equivalent — SESSION_EXPIRED banner
- `useSpotlightSearch.ts` — sign-in link fallback after recovery failure

</code_context>

<specifics>
## Specific Ideas

User specified: dedup single-flight/cancellation, double-submit prevention everywhere, SESSION_EXPIRED in spotlight/newtab, editorMode restore after SW restart, explicit sync status UI.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>
