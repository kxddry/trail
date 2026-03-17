# Codebase Concerns

**Analysis Date:** 2026-03-18

## Backend/Service Worker Issues (Extension-Focused Analysis)

### Critical: Race Conditions & Data Loss

**1. Tree Cache Synchronization Gap**
- **Files:** `src/background/services/tree-storage.ts:180-189` (cachedTree, cachedMeta, cachedIndex with separate loading promises)
- **Issue:** `cachedTree`, `cachedMeta`, and `cachedIndex` are managed independently with separate loading promises. Multiple operations (navigation, tabs, sync, editor) call `getOrCreateTree()` concurrently without locking. If sync engine modifies archive while editor is active, state diverges. `_editingNonActiveTree` flag (line 198) suggests known race condition but only partially mitigates.
- **Impact:** Concurrent tree mutations lose updates (last-write-wins on cache). Archive index diverges from on-disk state. Editor mode persists stale tree if sync happens simultaneously.
- **Fix:** Implement single tree lock (Promise-based queue) for all tree operations. Ensure `getOrCreateTree()` returns consistent snapshot across meta/tree/index. Add queue depth metrics.

**2. Concurrent Storage Quota Eviction**
- **Files:** `src/background/services/quota-manager.ts:31-46,65-96`
- **Issue:** `quotaAwareSet()` catches QUOTA_BYTES error, evicts oldest archive, retries. If multiple parallel writes hit quota, both may try to evict same archive. `evictOldestArchive()` reads index, modifies it, writes it back — not atomic. Between read (line 66) and write (line 92), sync could modify index.
- **Impact:** Multiple concurrent quota errors could cause data loss. Metadata index corruption. Extension crash if both writes fail.
- **Fix:** Use pessimistic locking on index before eviction read. Implement atomic index updates (single storage.setItem). Add retry backoff with jitter.

**3. Tree Mutation Without Immutability Guarantees**
- **Files:** `src/background/state/nav-tree.ts:100`, `src/background/state/tree-node.ts:37,62,73,92`
- **Issue:** Direct mutation of node data: `existing.data = this.mergeNodeData(...)`. TreeNode uses mutable .push/.splice instead of returning new arrays. `attachChild()`, `transferChildrenTo()`, `remove()` all mutate in-place.
- **Impact:** Undo snapshots may not capture all intermediate states. Sync dirty tracking could miss mutations if cache not flushed immediately.
- **Fix:** Create `updateNodeData(node, updates)` returning new NodeData. Make TreeNode children immutable (return frozen copies).

---

### High Priority: Error Handling & Logging

**1. Silent Catch Blocks in Critical Paths**
- **Files:**
  - `src/background/messaging/handlers/editor-handlers.ts:122,132` (tab content script unavailable)
  - `src/background/services/search-suggestions.ts:57` (search fetch failure)
  - `src/background/services/auth-policy-keeper.ts:82`
  - `src/background/services/spotlight-live-index.ts:538`
  - `src/background/services/temporary-selection.ts:32`
- **Issue:** 8+ empty catch blocks silently swallow errors. Some errors (quota exceeded, network failures) deserve logging. No way to debug production issues.
- **Impact:** Silent failures in critical paths (auth, sync, storage). No visibility into degradation patterns.
- **Fix:** Log all errors with context. Distinguish between expected (tab has no content script) and unexpected errors. For quota errors, log with tree ID and size info.

**2. Missing Error Context in Tab Lifecycle**
- **Files:** `src/background/state/tab-manager.ts:209` (comment "self-remova"), `src/background/tabs/lifecycle.ts:100-101` (silent catch)
- **Issue:** Line 209 has typo comment "self-remova" with no logging. Line 100-101 catches but doesn't log context. No indication why tab registration failed.
- **Impact:** Silent failures in tab lifecycle. Impossible to debug missing tabs or tracking failures.
- **Fix:** Log all unexpected errors with context: `console.error('Tab lifecycle failed:', { tabId, nodeId, error })`

**3. Unvalidated Message Passing**
- **Files:** `src/background/messaging/rpc-router.ts:14-20` (parseRpcRequestEnvelope returns null)
- **Issue:** `parseRpcRequestEnvelope()` returns null for invalid input. Caller doesn't distinguish "no message" from "bad message". No type guard for discriminated union types.
- **Impact:** Malformed messages silently dropped. No audit trail of failed requests. Silent desync between UI and extension.
- **Fix:** Create `parseRpcRequestEnvelope()` that throws on failure with detailed error. Add validation in each handler. Log all RPC failures.

---

### High Priority: Type Safety Issues

**1. Type-Unsafe `as unknown` Casts**
- **Files:** `src/background/service-worker.ts:36`, `src/background/services/tree-storage.ts:20,89-90`, `src/background/services/offscreen-graph-manager.ts:16`, `src/spotlight/useSpotlightTheme.ts:31`, `src/entrypoints/sidepanel/ui/graph/layout/calculator.ts:42,427`, `src/entrypoints/spotlight-graph/main.tsx:16`
- **Issue:** 12 instances of `as unknown as` bypassing TypeScript safety. Work around incomplete Chrome API types (browser.sidePanel, chrome.runtime.getContexts) and type transformation issues.
- **Impact:** Silent type violations. Future refactoring introduces bugs. Maintenance burden.
- **Fix:** Create proper wrapper types extending Chrome APIs. Use discriminated unions instead of type assertions. Consider `types/chrome-extensions.ts`.

**2. NodeId Type Not Distinct**
- **Files:** Throughout codebase (NodeId used as opaque type but actually just number)
- **Issue:** `NodeId = number` makes it easy to mix with TabId, window IDs. No compile-time protection. `as NodeId`, `as TabId` casts common.
- **Impact:** Bug-prone refactoring. Hard to audit correctness of ID usage.
- **Fix:** Use branded types: `type NodeId = number & { readonly __brand: 'NodeId' }`. Create helper constructors: `function nodeId(n: number): NodeId`.

---

### Medium Priority: Performance & Resource Issues

**1. Search Index Rebuild on Every Mutation**
- **Files:** `src/background/services/spotlight-live-index.ts`
- **Issue:** Every tree mutation rebuilds search index entry immediately. No batching or debouncing despite mutations happening in rapid succession during bulk import or editor operations.
- **Impact:** Bulk import (100+ nodes) triggers 100+ index updates sequentially. Spotlight slow during active editing. High CPU during sync.
- **Fix:** Batch index updates — queue mutations, flush every 100ms. Make updates async. Lazy rebuild on demand.

**2. Graph Layout Cache Not Persistent**
- **Files:** `src/entrypoints/sidepanel/ui/graph/layout/calculator.ts`, `src/entrypoints/spotlight-graph/main.tsx:16`
- **Issue:** Layout cache stored in `chrome.storage.session` (volatile) and globalThis (not shared across contexts). No way to share computed layout between newtab and sidepanel.
- **Impact:** Graph rendering slow on first load (500+ nodes). No perceptible improvement from caching between tabs. Layout thrashing.
- **Fix:** Persist layout to `chrome.storage.local` with versioning. Use content hash as cache key. Pre-compute in offscreen document.

**3. Tree Mutations Debounced 1500ms Before Flush**
- **Files:** `src/background/services/tree-storage.ts:189-190` (saveTimer debounce), `src/background/services/tree-storage.ts:41`
- **Issue:** Mutations debounced 1500ms before flush. If extension crashes or service worker stops, pending mutations lost. No crash recovery mechanism.
- **Impact:** User adds nodes for 10 seconds, extension crashes, all lost. Sync may not have current state.
- **Fix:** Flush immediately after critical mutations (add/delete/move). Use 100ms debounce for metadata only. Implement WAL (write-ahead log).

---

## Security Considerations

**1. Missing Input Validation on Tab URLs**
- **Files:** `src/background/tabs/lifecycle.ts:76,89-91`
- **Issue:** Tab URL passed directly to `tree.navigate()` without validation. Favicon URL normalized but not validated for data: URIs or javascript: URIs. `shouldTrackUrl()` validates but called AFTER tree operations in some paths.
- **Impact:** Malicious content script could inject javascript: URLs into tree. Stored URLs could execute code if rendered unsafely. data: URIs could bloat storage.
- **Fix:** Validate URL origin before tree.navigate(): `new URL(url).protocol in ['http:', 'https:']`. Reject favicon URLs with unsafe protocols.

**2. Auth Token Persistence Without Encryption**
- **Files:** `src/background/services/auth-orchestrator.ts`
- **Issue:** Auth tokens stored in chrome.storage.local (encrypted by browser but not extension). No in-flight encryption for sync API. No token refresh logic.
- **Impact:** Extension compromise leaks all auth tokens. No way to revoke without user action. Sync data vulnerable if token exposed.
- **Fix:** Store tokens in chrome.storage.session (cleared on disable) instead of local. Implement token rotation on every sync cycle. Add expiry validation.

**3. Missing CSRF Protection on Tree Mutations**
- **Files:** `src/background/messaging/router.ts`, `src/background/messaging/handlers/tree-handlers.ts`
- **Issue:** RPC messages contain `id` field but no session/nonce validation. No check message came from same extension context. Offscreen document could spoof if compromised.
- **Impact:** Compromised content script could mutate tree. Sync conflicts could corrupt data.
- **Fix:** Add sessionId/nonce to RPC pairs. Validate sender context in service worker. Use chrome.runtime.connect() instead of sendMessage.

---

## Data Loss Risks

**1. Archive Eviction Silently Drops Stubs**
- **Files:** `src/background/services/quota-manager.ts:86-89`
- **Issue:** When archive evicted, blob deleted, index replaced with stub. If user never opens archived tree, stub with no data left. No restore mechanism.
- **Impact:** Data loss appears as "corrupted" tree. Stubs accumulate confusing archive list.
- **Fix:** Before evicting, compress aggressively or migrate to backend. Mark stubs with "evicted at" timestamp. Notify user when archive would evict.

**2. Service Worker Crash Without Recovery**
- **Files:** `src/background/service-worker.ts:16-20`
- **Issue:** `unhandledrejection` handler logs to console but doesn't persist errors. Service worker can suspend without warning. No watchdog/heartbeat. Periodic sync relies on service worker not terminating.
- **Impact:** Initialization failure causes state inconsistency. Sync stops silently. No visibility into service worker lifecycle issues.
- **Fix:** Send unhandled rejections to error collector (backend API). Implement initialization healthcheck. Add service worker wake-up on tab activity.

---

## Test Coverage Gaps

**1. No Tests for Concurrency**
- **Files:** `tests/basic.test.ts`, `tests/spotlight-search.test.ts` (covers recency, search only)
- **Issue:** Zero tests for concurrent `getOrCreateTree()` calls. No tests for sync + tab lifecycle interaction. No tests for quota eviction under concurrent writes. No tests for editor conflicts with sync.
- **Risk:** High-confidence bugs in multi-threaded scenarios go undetected.
- **Fix:** Add `tests/concurrency.test.ts`. Mock browser storage for quota errors mid-write. Test sync/edit/navigation simultaneously.

**2. No Integration Tests for RPC**
- **Files:** `tests/rpc-schema.test.ts` (validates schemas only)
- **Issue:** Handlers tested in isolation, not message flow. No tests for error propagation. No tests for message ordering (delete then navigate).
- **Risk:** Silent message drops, race conditions in UI.
- **Fix:** Add integration tests mocking messaging layer. Test error cases: malformed messages, handler exceptions. Test concurrent message handling.

---

## Fragile Patterns

**1. TreeNode Mutation Without Indication**
- **Files:** `src/background/state/tree-node.ts:88` (this.parent.getChildren().splice())
- **Issue:** `getChildren()` returns reference. `.splice()` mutates directly. No indication to caller. Easy to double-delete if splice called twice.
- **Impact:** Hidden mutations hard to trace. Potential data corruption.
- **Fix:** Make children truly immutable — return frozen copy. Explicit mutation methods: `removeChildAt(index)`.

**2. Editor Snapshot Shallow Copy**
- **Files:** `src/background/messaging/handlers/editor-handlers.ts:35-38,171`
- **Issue:** `editorSessionSnapshot` holds shallow copy of tree JSON. If tree mutated after snapshot, snapshot stale (no deep copy). `cacheTree()` called with mutated tree could persist incomplete state if interrupted.
- **Impact:** Undo may not restore. Editor exits with corrupted tree on crash. Backup differs from live tree.
- **Fix:** Deep clone: `JSON.parse(JSON.stringify(tree))`. Flush immediately after creation. Add version number to snapshots.

---

## Original UI/Spotlight Issues (2026-03-17)

### Tech Debt

**Type-unsafe RPC layer casting:**
- Issue: Unsafe `as any` type casts in `SpotlightRoot.tsx` line 113 when building batch action targets.
- Files: `extension/src/spotlight/SpotlightRoot.tsx:113`, `extension/src/spotlight/rpc.ts:106`
- Impact: Runtime errors possible. Type safety circumvented.
- Fix: Create proper discriminated union type for batch action targets. Remove `any` types.

**Dead callback implementations:**
- Issue: Empty no-op callbacks in `NewTabApp.tsx` lines 321-322.
- Files: `extension/src/entrypoints/newtab/ui/NewTabApp.tsx:321-322`
- Impact: Graph panel resizing and snap-point stepping don't work in newtab.
- Fix: Implement features or create separate hook variant.

**Manual memory management with timers:**
- Issue: Drilldown scope memory with manual timers across `SpotlightRoot.tsx` and `NewTabApp.tsx`. Timer cleanup error-prone.
- Files: `extension/src/spotlight/SpotlightRoot.tsx:48-49,142-145`, `extension/src/entrypoints/newtab/ui/NewTabApp.tsx`
- Impact: Memory leaks if component unmounts before timer fires.
- Fix: Extract to custom hook `useDrilldownMemory()`. Consolidate timer logic.

### Known Issues

**Spotlight Root and NewTab App code duplication:**
- `SpotlightRoot.tsx` (365 lines) and `NewTabApp.tsx` (554 lines) have nearly identical state management, effects, render logic.
- Any change must be made twice. Bug fixes in one don't apply to other.

**Unoptimized graph parallax on mousemove:**
- `NewTabApp` lines 156-204 runs parallax on every `mousemove` with requestAnimationFrame. Heavy mouse movement = sustained CPU use.
- No throttling, no DOM update batching.
- Solution: Use CSS 3D transforms with `will-change`. Consider CSS variables letting browser animate.

**Search index rebuild on mutations:**
- Every tree mutation triggers search index update immediately.
- No batching despite rapid succession mutations during bulk import/editing.

### Test Coverage Gaps

**No tests for:** RPC contract serialization, keyboard navigation, batch actions, graph preview caching, drilldown state transitions, section collapse with selection recovery.

---

## Recommendations Priority

**Critical (Fix before release):**
1. Race condition in tree cache synchronization — data loss risk
2. Concurrent storage quota eviction — data loss risk
3. Missing input validation on URLs — security issue

**High (Fix soon):**
1. Silent error swallowing in critical paths
2. Type safety gaps with `as unknown` casts
3. Editor state snapshot corruption risk
4. Service worker crash handling
5. Auth token persistence without encryption

**Medium (Improve robustness):**
1. Undo/redo persistence (currently in-memory only)
2. Test coverage for concurrency
3. Branded types for ID types
4. Search result error handling
5. Code duplication between Spotlight/NewTab UI

**Low (Nice to have):**
1. Performance optimization for search indexing (batching/debouncing)
2. Drag position threshold documentation
3. Archive eviction user notifications
4. LRU cache size metrics and optimization

---

*Concerns audit: 2026-03-18 (Extension backend analysis) + 2026-03-17 (UI/spotlight analysis)*
