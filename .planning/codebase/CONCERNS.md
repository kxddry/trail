# Codebase Concerns

**Analysis Date:** 2026-03-17

## Tech Debt

**Type-unsafe RPC layer casting:**
- Issue: Unsafe `as any` type casts in `SpotlightRoot.tsx` line 113 when building batch action targets. The type system allows `nodeId?: any` and `treeId?: string` which defeats the type safety provided elsewhere in the codebase.
- Files: `extension/src/spotlight/SpotlightRoot.tsx:113`, `extension/src/spotlight/rpc.ts:106`
- Impact: Runtime errors possible when batch actions receive malformed targets. Type safety is circumvented, making refactoring and debugging harder.
- Fix approach: Create a proper discriminated union type for batch action targets that matches `SpotlightActionTarget` contract exactly. Remove `any` types and validate targets before sending RPC.

**Dead callback implementations:**
- Issue: Two empty no-op callbacks in `NewTabApp.tsx` lines 321-322 are passed to `useSpotlightKeyboard` but do nothing.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:321-322`
- Impact: `toggleGraphPanel` and `stepSnapPoint` are not implemented for the newtab view, but the hook still tries to use them. Graph panel resizing and snap-point stepping won't work in newtab context.
- Fix approach: Either implement these features for newtab or create a separate hook variant for newtab that doesn't require them. Consider if newtab should have graph panel resizing at all.

**Overly broad error recovery in search:**
- Issue: `useSpotlightSearch` (line 27-42) catches connection errors broadly with string matching (`isConnectionError` checks for `Could not establish connection`, `Extension context invalidated`, `Receiving end does not exist`).
- Files: `extension/src/spotlight/useSpotlightSearch.ts:27-42`
- Impact: Different types of connection failures are treated identically. Extension reloads, popup closures, and genuine network errors all trigger the same retry logic, potentially masking specific issues.
- Fix approach: Distinguish between recoverable connection errors (popup close) vs. extension invalidation. Log error codes separately for observability.

**Manual memory management with timers:**
- Issue: Multiple refs managing drilldown scope memory with manual timers across `SpotlightRoot.tsx` (lines 48-49, 142-145) and `NewTabApp.tsx` (implicit same pattern). Timer cleanup is error-prone and depends on useEffect discipline.
- Files: `extension/src/spotlight/SpotlightRoot.tsx:48-49,142-145`, `extension/src/entrypoints/newtab/ui/NewTabApp.tsx`
- Impact: Memory leaks possible if component unmounts before timer fires. Duplicate code creates maintenance burden. State restoration logic is fragile.
- Fix approach: Extract drilldown scope memory management into a custom hook (`useDrilldownMemory`). Consolidate timer logic with proper cleanup guarantees.

## Known Issues

**Spotlight Root and NewTab App code duplication:**
- Symptoms: `SpotlightRoot.tsx` (365 lines) and `NewTabApp.tsx` (554 lines) have nearly identical state management, effects, and render logic. Same patterns for search, selection, drilldown, preview, and keyboard handling.
- Files: `extension/src/spotlight/SpotlightRoot.tsx`, `extension/src/entrypoints/newtab/ui/NewTabApp.tsx`
- Trigger: Any change to spotlight behavior must be made twice. Bug fixes in one don't automatically apply to the other.
- Workaround: None. Requires architectural refactoring to consolidate.

**No web search hint in newtab footer:**
- Symptoms: `SpotlightFooter` in newtab doesn't show the "search the web with Enter" hint even when there's a query.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:523`
- Trigger: The `showWebSearchHint` prop is hardcoded to `search.query.trim().length > 0`, but newtab footer may need different visibility rules.
- Workaround: Users can still search the web by pressing Cmd+Enter, hint just doesn't appear.

**Focus auto-grab with excessive retries:**
- Symptoms: Aggressive focus-stealing on newtab load with timers at [0, 50, 150, 300]ms (line 129-131).
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:129-131`
- Trigger: Works around Chrome address bar stealing focus, but may cause accessibility issues if screen reader is reading the page.
- Workaround: None. This is by design to make search snappy.

## Security Considerations

**RPC response validation gaps:**
- Risk: `sendRpc` function (line 50 in `rpc.ts`) casts response data directly without schema validation. If backend sends malformed tree data or action responses, client accepts it as valid.
- Files: `extension/src/spotlight/rpc.ts:50-54`
- Current mitigation: TypeScript casts at client side, assumes backend is trusted.
- Recommendations: Add runtime schema validation using zod or similar for critical RPC responses (search results, preview data). Validate node IDs, URLs, and action responses before using them.

**LocalStorage drag position XSS risk:**
- Risk: `loadDragPos` in NewTabApp (lines 54-69) parses JSON from localStorage without validation. If localStorage is compromised, malicious x/y values could be written.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:54-69`
- Current mitigation: Values are used only for CSS transforms, numeric bounds checked (lines 61-63).
- Recommendations: This is low risk since localStorage is same-origin, but consider using structured clone or explicit validation for all storage reads.

**Clipboard API error handling:**
- Risk: `handleBatchExecute` in NewTabApp (line 255) and SpotlightRoot (line 107) call `navigator.clipboard.writeText()` but don't handle rejection. If clipboard API is blocked by permissions, error is silent.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:255`, `extension/src/spotlight/SpotlightRoot.tsx:107`
- Current mitigation: Action is wrapped in `void` operator, user won't see error.
- Recommendations: Catch clipboard errors and show status text like "Clipboard access denied". Fall back to showing URLs in a modal.

## Performance Bottlenecks

**Unoptimized graph parallax on mousemove:**
- Problem: `NewTabApp` lines 156-204 runs parallax effect on every `mousemove` with requestAnimationFrame loop that recalculates and applies CSS transforms at 60fps. Heavy mouse movement = sustained CPU use.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:156-204`
- Cause: No throttling on mousemove, animation loop doesn't batch DOM updates. Easing calculation (0.12 factor) is smooth but expensive.
- Improvement path: Use CSS 3D transforms with `will-change` hint. Consider switching to CSS variables and letting browser animate instead of JS loop. Or throttle mousemove to 30fps updates.

**Search results memoization incomplete:**
- Problem: `flatItems`, `itemByKey`, and `visibleFlatItems` are memoized (useMemo), but `sections` dependency causes full recalculation even when sections structure hasn't changed, just items within sections reordered.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:102-108`, `extension/src/spotlight/SpotlightRoot.tsx:60-61`
- Cause: No granular section dependency tracking. All consumers re-render when any section changes.
- Improvement path: Consider normalizing sections into a hashmap keyed by section ID to detect structural changes. Memoize per-section item lists separately.

**LRU cache map size is arbitrary:**
- Problem: `useSpotlightSearch` hardcodes LRU cache size to 16 (line 89). No metrics on hit rate or memory usage.
- Files: `extension/src/spotlight/useSpotlightSearch.ts:89`
- Cause: No observability into cache performance. Size was probably chosen arbitrarily.
- Improvement path: Add cache hit/miss metrics. Monitor memory of stored preview data. Consider adaptive sizing or TTL-based eviction instead of pure LRU.

## Fragile Areas

**Drilldown scope memory persistence:**
- Files: `extension/src/spotlight/SpotlightRoot.tsx:48-49,126-148`, `extension/src/entrypoints/newtab/ui/NewTabApp.tsx`
- Why fragile: Drilldown state is saved to a ref on close and restored on open if within 3-minute window. Manual state management with refs and timers is error-prone. If useEffect dependency arrays are wrong, cleanup doesn't happen.
- Safe modification: Extract to dedicated hook with built-in cleanup guarantees. Add tests for ref lifecycle. Document timeout constants (3 minutes hardcoded in two places).
- Test coverage: No tests visible for drilldown scope restoration. Session memory should have unit tests covering: save on close, restore on open, TTL expiration, cleanup on unmount.

**Spotlight keyboard event system:**
- Files: `extension/src/spotlight/useSpotlightKeyboard.ts` (not examined in detail)
- Why fragile: Hook receives 30+ props. Any prop change can trigger unintended keyboard behavior changes. Complex state transitions for command mode, graph mode, drilldown mode are not visually documented.
- Safe modification: Reduce prop count by grouping related state into context objects. Add state machine diagram or comments showing mode transitions. Test each keyboard shortcut in isolation.
- Test coverage: Unclear. Keyboard behavior should have integration tests for: Tab navigation, Cmd+Enter, Esc handling, graph toggle (Cmd+G), Enter to activate, etc.

**Section collapse/expand with selection recovery:**
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:292-313`, `extension/src/spotlight/SpotlightRoot.tsx:157-182`
- Why fragile: When collapsing a section, code searches for the nearest non-collapsed section to move selection to. The search logic (nested loops with offset/direction) is O(N) and could fail if all sections are collapsed.
- Safe modification: Add guard: if no non-collapsed section found, clear selection explicitly instead of leaving selectedKey in inconsistent state. Add comment explaining the "nearest key" search algorithm.
- Test coverage: Need tests for: collapse active section, collapse multiple sections, collapse all sections, restore selection is in valid section after collapse.

## Scaling Limits

**Single global RPC counter for ID generation:**
- Current capacity: `rpcCounter` in `rpc.ts` (line 18) is a module-level mutable number. No reset mechanism visible.
- Limit: After ~9 billion RPC calls, the number could theoretically overflow (though JavaScript numbers are safe to ~2^53).
- Scaling path: No immediate concern for single-user extension, but if RPC traffic ever multiplies, add timestamp prefix and consider distributed ID generation scheme if cross-device sync ever happens.

**LRU cache fixed at 16 entries:**
- Current capacity: 16 tree preview graph states cached.
- Limit: For users with many trails, preview data for older trails is evicted. Cache miss means round-trip RPC to regenerate.
- Scaling path: Monitor actual cache hit rates in production. If below 80%, increase size or implement smarter eviction (recency + access frequency). If above 90%, can reduce size to save memory.

**Drilldown memory only lasts 3 minutes:**
- Current capacity: One drilldown scope saved in memory.
- Limit: If user closes spotlight and reopens after 3+ minutes, drilldown context is lost. Only affects user experience, not correctness.
- Scaling path: Make TTL configurable. Consider storing last drilldown to localStorage (with validation) for persistence across sessions.

## Dependencies at Risk

**`cmdk` for command palette:**
- Risk: Heavy dependency (Command component from cmdk used in both SpotlightRoot and NewTabApp). If cmdk has a breaking change or is abandoned, refactor needed across multiple components.
- Impact: Currently stable, but ties UI to external library behavior.
- Migration plan: If needed, cmdk provides a minimal abstraction. Could be replaced with native HTML `<input>` + custom selection logic. Estimated effort: medium (2-3 days).

**`motion/react` for animations:**
- Risk: Framer Motion dependency for parallax and modal animations. Updates could change animation performance characteristics.
- Impact: Newtab parallax effect and Spotlight scale-in transitions depend on motion library.
- Migration plan: Could migrate to CSS animations (simpler) or Web Animations API. Effort: medium (1-2 days per animation).

**`lucide-react` icon library:**
- Risk: Low risk. Icons are simple and stable. If needed, could switch to any other icon library with minimal changes (just import path changes).
- Impact: Icons are used throughout for UI affordances. Breaking change is unlikely.
- Migration plan: Straightforward search-replace if icon library changes.

## Missing Critical Features

**No error boundary for spotlight content:**
- Problem: If graph rendering fails or search service crashes, entire spotlight modal breaks silently with no fallback UI.
- Blocks: User can't recover without closing and reopening spotlight.

**No progress indicator for long searches:**
- Problem: `search.loading` flag exists but NewTabApp doesn't show it (SpotlightRoot shows it, NewTabApp doesn't consistently).
- Blocks: Users can't tell if search is hung or still loading.

**No keyboard shortcut display for commands:**
- Problem: `SpotlightFooter` shows hints but command shortcuts aren't discoverable without typing `>` first.
- Blocks: Users unfamiliar with spotlight syntax can't find commands easily.

**No test coverage visible:**
- Problem: No `.test.ts` or `.spec.ts` files found in spotlight or newtab code.
- Blocks: Refactoring is risky. Keyboard behavior changes are untested.

## Test Coverage Gaps

**Spotlight search RPC contract:**
- What's not tested: RPC request/response serialization, error handling for timeout/network failure, session expiration recovery.
- Files: `extension/src/spotlight/rpc.ts`, `extension/src/spotlight/useSpotlightSearch.ts`
- Risk: Changes to RPC format or error codes could break silently at runtime.
- Priority: High

**Keyboard navigation and shortcuts:**
- What's not tested: Tab order, Cmd+G toggle, Esc to close, Enter to activate, multi-select toggle, hint suggestion.
- Files: `extension/src/spotlight/useSpotlightKeyboard.ts`, `extension/src/entrypoints/newtab/ui/NewTabApp.tsx`
- Risk: Keyboard interaction is brittle and prone to regression on prop changes.
- Priority: High

**Batch actions execution:**
- What's not tested: Multi-select state management, batch copy URLs, batch delete, action rollback on error.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:251-267`, `extension/src/spotlight/SpotlightRoot.tsx:103-116`
- Risk: Batch actions could partially fail or corrupt state if not tested thoroughly.
- Priority: Medium

**Graph preview data loading and caching:**
- What's not tested: LRU cache eviction, cache hit/miss on repeated opens, preview data validation, fallback UI when preview fails.
- Files: `extension/src/spotlight/useSpotlightPreview.ts`
- Risk: Cache misses or invalid preview data could cause graph to render blank or crash.
- Priority: Medium

**Drilldown scope state transitions:**
- What's not tested: Save/restore on open/close, 3-minute TTL expiration, cleanup on unmount, edge cases with multiple drilldown operations.
- Files: `extension/src/spotlight/SpotlightRoot.tsx:126-148`, `extension/src/entrypoints/newtab/ui/NewTabApp.tsx`
- Risk: State corruption if transitions are not handled correctly, memory leaks if cleanup fails.
- Priority: Medium

---

*Concerns audit: 2026-03-17*
