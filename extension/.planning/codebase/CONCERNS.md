# Codebase Concerns

**Analysis Date:** 2026-02-28

## Tech Debt

**Chrome API Type Safety:**
- Issue: Multiple `as any` casts required for Chrome API compatibility across browser versions
- Files: `src/background/messaging/handlers/panel-handlers.ts` (lines 46, 51, 55, 57)
- Impact: Side panel API has different signatures (promise vs callback) across Chrome versions, requires runtime detection and type coercion
- Fix approach: Create a proper type wrapper abstraction that normalizes both promise and callback patterns. Consider generating types from a browser compatibility matrix.

**Navigation Tree `setRoot` Not Implemented:**
- Issue: `setRoot` logic referenced but not implemented in navigation tree core
- Files: `src/background/state/nav-tree.ts` (line 68: `// todo: implement setRoot logic`)
- Impact: Tree reconstruction/loading may bypass proper initialization logic if called directly
- Fix approach: Implement or remove the reference. If needed, define the algorithm for safely replacing the entire tree state.

**Unstubbing Archives on Demand:**
- Issue: Archive entries can be "stubbed" (metadata-only) when quota fills, requiring on-demand reconstruction
- Files: `src/background/services/tree-storage.ts` (method `unstubArchiveEntry`), `src/background/services/quota-manager.ts`
- Impact: Users may experience latency when accessing archived trees that were evicted. No feedback to user about this process.
- Fix approach: Add UI feedback when unstubbing in progress. Consider eager unstubbing during idle time, or implement a "hydration queue".

**Generic Type Assertions:**
- Issue: Multiple `as unknown as` and `as number` assertions to work around type system constraints
- Files: `src/background/services/tree-storage.ts` (lines 51-52, 82-83, 159-160, 89-90), `src/sidepanel/ui/graph/layout/calculator.ts` (lines 42, 408)
- Impact: Reduces type safety around storage and layout serialization
- Fix approach: Create branded types for storage values (e.g., `type StoredTimestamp = number & { readonly __storedTimestamp: true }`) to eliminate assertions.

**RPC Response Data Casting:**
- Issue: RPC response data cast to `any` after envelope validation
- Files: `src/shared/rpc/client.ts` (line 55)
- Impact: Loss of type safety for actual response payload after transport layer
- Fix approach: Use generic parameter to properly type response data through the envelope parsing chain.

## Known Bugs

**Silent Navigation Errors:**
- Bug: Navigation handler errors are silently ignored
- Symptoms: Navigation events fail to create tree nodes, user sees no indication
- Files: `src/background/navigation/webnavigation.ts` (lines 9-11)
- Trigger: When `handleNavigation` throws, the error is caught and discarded
- Workaround: None. Errors are completely hidden.
- Fix: Implement structured error logging and user-facing notifications for navigation failures

**Graph Canvas Cleanup Defer Pattern:**
- Bug: Layout update cleanup deferred to handleUp instead of being synchronous
- Symptoms: Potential state inconsistency if multiple drags occur in quick succession
- Files: `src/sidepanel/ui/components/graph/GraphCanvas.tsx` (line 2280 comment)
- Trigger: When user completes a drag operation
- Impact: Race condition possible if UI state diverges from component state
- Fix: Review drag state machine to ensure cleanup happens in predictable order

## Security Considerations

**Chrome Extension Permissions:**
- Risk: Extension uses broad `<all_urls>` and `webNavigation` permissions
- Files: `src/background/navigation/webnavigation.ts`, `src/background/tabs/lifecycle.ts`
- Current mitigation: Extension is first-party code; limited to recording navigation history
- Recommendations: Document permission necessity. Consider using content script injection only on demand rather than all origins.

**Storage Security:**
- Risk: Tree data and auth tokens stored in `chrome.storage.local` which is accessible to other extensions with storage permission
- Files: `src/background/services/tree-storage.ts`, `src/background/services/sync/api.ts` (auth token loading)
- Current mitigation: User's device isolation
- Recommendations: Consider encrypting sensitive tree data at rest. Audit token expiry handling (`TOKEN_EXPIRY_BUFFER_MS = 30_000`).

**Session Storage Quota Handling:**
- Risk: Silent failures when `sessionStorage.setItem` is called with quota exceeded
- Files: `src/sidepanel/ui/shared/apply-theme.ts` (theme cache)
- Current mitigation: `catch { /* quota / security */ }` — intentional silent fail
- Recommendations: This is acceptable but document why theme cache is non-critical.

**RPC Message Type Coercion:**
- Risk: RPC messages cast to `Record<string, unknown>` during envelope creation, losing type information
- Files: `src/shared/rpc/client.ts` (line 24)
- Current mitigation: Schema validation via Zod on envelope
- Recommendations: Ensure all handlers validate input schemas independently. Don't rely solely on envelope validation.

## Performance Bottlenecks

**GraphCanvas Component Size (2528 lines):**
- Problem: Single React component handling graph rendering, interaction, layout, and state management
- Files: `src/sidepanel/ui/components/graph/GraphCanvas.tsx`
- Cause: Mixed concerns — canvas rendering (Pixi), React state management, interaction handlers, layout calculations
- Impact: Difficult to test, hard to optimize individual concerns, high re-render costs
- Improvement path:
  1. Extract interaction state machine into separate hooks
  2. Extract layout calculation into a custom hook
  3. Separate Pixi renderer logic into a usePixiRenderer hook
  4. Use React.memo for subcomponents if any
  5. Consider using useReducer for complex state instead of multiple useState calls

**Store State Centralization (689 lines):**
- Problem: All UI state centralized in single Zustand store with 50+ state fields
- Files: `src/sidepanel/ui/state/store.ts`
- Cause: Avoids prop drilling but increases coupling
- Impact: All components re-render when any store value changes; selectors help but still causes excessive subscriptions
- Improvement path:
  1. Split into domain-specific stores (graph store, ui store, sync store, account store)
  2. Use store composition to avoid multiple provider nesting
  3. Profile render costs with React DevTools to identify hot paths

**Layout Calculator Complexity (701 lines):**
- Problem: Tidy tree algorithm implementation mixed with radial and mindmap layouts
- Files: `src/sidepanel/ui/graph/layout/calculator.ts`
- Cause: Multiple layout algorithms in single file
- Impact: Hard to maintain, hard to optimize individual layout modes
- Improvement path: Extract each layout algorithm into separate module with consistent interface

**MiniSearch Integration (2005 lines):**
- Problem: Entire MiniSearch library vendored rather than imported
- Files: `src/shared/vendor/minisearch.ts`
- Cause: Likely to support tree node search without extra dependencies
- Impact: Large bundle, difficult to upgrade, hard to optimize
- Improvement path: Profile whether MiniSearch is actually faster than alternative search. Consider if built-in filtering would suffice for typical tree sizes.

**Pixi Renderer Complexity (1596 lines):**
- Problem: WebGL rendering, LOD system, favicon loading, and shape rendering all in single class
- Files: `src/sidepanel/ui/graph/render/GraphPixiRenderer.ts`
- Cause: Custom rendering pipeline required for high-performance graph visualization
- Impact: Hard to debug rendering issues, difficult to add new node types
- Improvement path:
  1. Extract favicon loading into separate texture manager
  2. Extract LOD decision logic into strategy classes
  3. Extract icon rendering into reusable shape builders
  4. Use Pixi's layer system for better rendering organization

**Tab Cycle Computation on Every Access:**
- Problem: Tab cycle order computed dynamically on each `getNextTabForNode` call
- Files: `src/background/state/tab-manager.ts` (lines 58-62)
- Cause: Tab order might change between calls
- Impact: O(n) search through tab set on every tab cycle
- Improvement path: Cache cycle order more aggressively, only invalidate on actual tab changes

**Storage Quota Eviction on Write:**
- Problem: When quota is exceeded, oldest archive is evicted synchronously during write
- Files: `src/background/services/quota-manager.ts`
- Cause: Blocking operation to free space
- Impact: Variable latency on tree saves; user sees jank
- Improvement path: Implement background eviction process triggered on quota threshold rather than on write failure

## Fragile Areas

**Tree Deletion with Merge Logic:**
- Files: `src/background/state/nav-tree.ts` (method `mergeDuplicateChildren`)
- Why fragile: Complex logic for detecting duplicate children by URL key and merging their data. If URL key calculation changes, orphans result.
- Safe modification: Only change `createUrlKey` with comprehensive tests. Tree deletion is tested (`tests/basic.test.ts`) but edge cases around duplicate detection may not be covered.
- Test coverage: Unit tests exist but need explicit coverage of URL collision scenarios

**Auth Token Expiry Buffer:**
- Files: `src/background/services/sync/api.ts` (line 110: `TOKEN_EXPIRY_BUFFER_MS = 30_000`)
- Why fragile: Hard-coded 30-second buffer. If sync takes longer than 30s, token may expire mid-sync.
- Safe modification: Test with slow networks. Consider making buffer configurable based on network latency.
- Test coverage: No integration tests for token expiry during sync

**RPC Routing with Unknown Message Types:**
- Files: `src/background/messaging/router.ts`
- Why fragile: Routes messages by type field. If new message types added without corresponding handlers, they silently fail or error
- Safe modification: Add TypeScript exhaustiveness check when adding new RPC methods. Router should error on unknown method.
- Test coverage: No tests for unknown method handling

**Navigation Handler Frame Filtering:**
- Files: `src/background/navigation/navigation-handler.ts` (line 29: try-catch around tab lookup)
- Why fragile: Tab may be closed between webNavigation event and handler execution
- Safe modification: Explicit handle of "tab not found" vs other errors. Current error is swallowed without logging.
- Test coverage: No tests for edge case of tab closed during navigation

**Search Index Consistency:**
- Files: `src/background/state/nav-tree.ts` (search index updates on navigate/delete)
- Why fragile: MiniSearch index can become out of sync if updates are missed
- Safe modification: Add invariant checks on tree mutation to ensure search doc exists for every node
- Test coverage: Only basic search tested in `basic.test.ts`; no stress tests

## Scaling Limits

**Storage Quota (10MB Chrome Storage):**
- Current capacity: ~10MB with compression for Chrome storage.local
- Limit: Typical large tree with 10k nodes + 20 archived trees hits quota
- Scaling path:
  1. Implement tree size limits with warnings
  2. Auto-archive trees older than N days
  3. Implement differential/delta sync instead of full tree push
  4. Consider IndexedDB for cold storage of archived trees

**Graph Rendering (Visible Nodes):**
- Current capacity: ~1000-2000 visible nodes depending on hardware
- Limit: Rendering performance degrades below 30fps when viewport contains >3000 nodes at high zoom
- Scaling path:
  1. More aggressive LOD thresholds below which nodes are hidden entirely
  2. Viewport-based culling (already implemented but may need tuning)
  3. Consider layer-based rendering if trees grow beyond 10k nodes
  4. Profile with real large trees to find exact bottleneck

**Tab Management (Per Node):**
- Current capacity: No hard limit but search becomes O(n) as tabs per node increases
- Limit: Likely OK up to 100 tabs per node; search degradation beyond
- Scaling path: Index tabs by node more aggressively to support thousands per node

**Search Index (MiniSearch):**
- Current capacity: Tree loading time grows with tree size
- Limit: Indexes all nodes; no incremental search index updates
- Scaling path: Lazy index loading for archived trees; delta indexing on tree updates

## Dependencies at Risk

**Pixi.js (8.16.0):**
- Risk: Custom WebGL rendering dependency. High complexity, frequent updates, potential breaking changes
- Impact: Graph rendering breaks if Pixi API changes; hard to debug rendering issues
- Migration plan: Consider Canvas 2D fallback or switch to Babylon.js if WebGL becomes problematic. Keep detailed Pixi API documentation.

**MiniSearch (7.2.0) [Vendored]:**
- Risk: Vendored library means no upstream security patches. Full library bundled even if subset is used.
- Impact: Outdated if MiniSearch is updated; bundle size includes unused features
- Migration plan: Evaluate whether built-in Array.filter() would suffice. If search becomes slow, consider Lunr.js or FuseJS as alternatives.

**Zustand (5.0.11):**
- Risk: State library that could be replaced; large store may cause performance issues
- Impact: If store gets too large, performance degrades. Zustand is lightweight but no built-in devtools
- Migration plan: Consider Redux Toolkit if debugging becomes necessary. Profile store performance before replacing.

**React Query (5.90.5):**
- Risk: Async state management for sync operations. If sync engine changes, React Query usage may need refactor
- Impact: Currently only used minimally; risk is low
- Migration plan: None needed unless async pattern becomes dominant

## Missing Critical Features

**Error Telemetry:**
- Problem: Navigation errors, sync failures, storage quota issues all fail silently
- Blocks: Can't diagnose user issues; can't detect bugs in production
- Recommendation: Implement error telemetry to sentry or similar. Add user-facing error toasts for critical failures.

**Offline Sync Queue:**
- Problem: Sync engine can't queue mutations while offline; changes made offline may be lost
- Blocks: Reliable offline-first usage; trust in data persistence
- Recommendation: Implement mutation queue in IndexedDB with replay on reconnect

**Tree Size Monitoring:**
- Problem: No warnings when trees approach quota
- Blocks: Users get surprised when trees fail to save
- Recommendation: Monitor total storage size, show warnings at 70% and 90% quota

**Sync Status Transparency:**
- Problem: Sync engine state is opaque; users don't know if their changes are synced
- Blocks: Users don't know if it's safe to close the extension
- Recommendation: Add detailed sync status UI showing pending operations, last sync time, errors

**Performance Monitoring:**
- Problem: No perf metrics in production; can't identify slow users
- Blocks: Can't optimize for real-world conditions
- Recommendation: Integrate Web Vitals reporting; track tree load time, sync duration, render frame rate

## Test Coverage Gaps

**Tab Synchronization Edge Cases:**
- What's not tested: Tab close during navigation, tab duplicate detection, tab cycle ordering under concurrent operations
- Files: `src/background/tabs/`, `src/background/state/tab-manager.ts`
- Risk: Tab state can diverge from browser state if edge cases fail silently
- Priority: High — tab management is critical to correctness

**Sync Conflict Resolution:**
- What's not tested: Multiple device sync, local vs remote timestamp conflicts, concurrent tree updates
- Files: `src/background/services/sync/engine.ts`
- Risk: Data loss or corruption if conflict resolution fails
- Priority: High — sync is critical for multi-device usage

**Storage Quota and Eviction:**
- What's not tested: Eviction during concurrent writes, recovery from failed evictions, archive unstubbing with quota constraints
- Files: `src/background/services/quota-manager.ts`, `src/background/services/tree-storage.ts`
- Risk: Data loss if eviction fails
- Priority: High

**Graph Layout Algorithms:**
- What's not tested: Large trees (5000+ nodes), extremely wide trees (1000+ children on single node), deeply nested trees (100+ depth)
- Files: `src/sidepanel/ui/graph/layout/calculator.ts`
- Risk: Layout algorithm may produce invalid layouts or infinite loops on edge case trees
- Priority: Medium — will only hit with large trees

**RPC Error Handling:**
- What's not tested: Unknown message types, missing handlers, timeout behavior, message order guarantees
- Files: `src/shared/rpc/`, `src/background/messaging/router.ts`
- Risk: RPC failures may hang indefinitely or crash handlers
- Priority: Medium

**Content Script Communication:**
- What's not tested: Content script injection failures, cross-origin communication, script sandboxing edge cases
- Files: `src/content/content-script.ts`, `src/background/messaging/handlers/`
- Risk: If content script fails to inject, critical tracking features fail silently
- Priority: Medium

---

*Concerns audit: 2026-02-28*
