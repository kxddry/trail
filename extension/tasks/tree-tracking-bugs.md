# Tree Tracking — Forensic Bug Audit

Aggregated findings from 8 parallel Opus 4.7 architect audits covering every angle of the link/tree tracking system. **74 unique bugs** after dedup, organized below by category. Severity scale: **P0 = data loss / privacy**, **P1 = wrong tree structure**, **P2 = behavior drift / UX decay**, **P3 = cosmetic / latent**.

---

## Root-cause themes (why so many bugs)

1. **`tree.current` is a single mutable global used as the parent for every new node** — mutated from 15+ sites, shared across all tabs and windows. The sidepanel's UI cursor, tab activations, window focus, and navigation all write to it.
2. **`openerTabId` is referenced ZERO times in the entire codebase** — Chrome hands us the correct parent for free, we throw it away.
3. **Mutex guards persistence, not mutation** — `treeMutex` in `tree-storage.ts:234` only protects bulk save/migrate ops. Every `handleNavigation`/`onTabActivated`/`onTabRemoved`/`onTabUpdated` mutates shared state with no lock, multiple awaits per handler, and Chrome freely interleaves events.
4. **URL is the only identity** — conflates distinct tabs, merges unrelated user intents (duplicate tab, middle-click, multi-window).
5. **`nodeIdCounter` is module-global, resets on SW restart, mutated during async hydration** — collision risk.
6. **Client clock drives sync ordering** — `savedAt` is a client timestamp used as a vector clock across devices.
7. **MV3 service-worker termination ignored** — debounced 1500ms saves silently dropped when SW dies; no `onSuspend` flush.
8. **3 webNav listeners share one handler** with no dedup by `documentId`/`transitionType`.

---

## P0 — Critical (data loss, silent corruption, privacy)

| # | Bug | File:line | Why |
|---|-----|-----------|-----|
| 1 | **Global `tree.current` as parent anchor** — every new node's parent depends on sidepanel attention, not browsing causality | [nav-tree.ts:168](src/background/state/nav-tree.ts) | Root architectural flaw. Background-tab navigations attach under unrelated sidepanel selection |
| 2 | **`openerTabId` never consulted** — middle-clicks, duplicates, popups all parent wrong | [navigation-handler.ts:57,220](src/background/navigation/navigation-handler.ts), [lifecycle.ts:18](src/background/tabs/lifecycle.ts) | Zero grep hits in entire codebase |
| 3 | **about:blank root hijack** — OAuth/popup lands on about:blank (maps to root), then navigates to real URL → `!shouldTrackUrl(nodeUrl)` branch **overwrites** root's url/title/favicon | [navigation-handler.ts:136-153](src/background/navigation/navigation-handler.ts) | User's persistent tree root becomes whatever a popup visited; children now misattributed |
| 4 | **setCurrentById + navigate compound op is non-atomic** — concurrent handlers interleave between setCurrentById and navigate, new node parents off wrong node | [navigation-handler.ts:156-158,218-230](src/background/navigation/navigation-handler.ts), [nav-tree.ts:119-170](src/background/state/nav-tree.ts) | Wrong parent edges permanently wired in; "parent roulette" under load |
| 5 | **`syncOpenTabs` reset-then-populate race** — `tabManager.reset()` wipes state mid-flight while webNav events stream; in-flight `handleNavigation` registrations lost | [sync-open-tabs.ts:17-47](src/background/tabs/sync-open-tabs.ts) | 50-200ms window every SW wake; also clears `ignoredTabs` and `suppressActivate` |
| 6 | **`onTabActivated` reparents pre-existing tabs as children of current** — activating any old tab that has no node creates one as child of sidepanel's current | [lifecycle.ts:101-112](src/background/tabs/lifecycle.ts) | Pre-existing tabs get false parent edges; misrepresents browsing history |
| 7 | **`syncOpenTabs` creates dangling node off arbitrary parent every SW boot** — active-tab branch calls `tree.navigate(data)` without setting current first | [sync-open-tabs.ts:67-88](src/background/tabs/sync-open-tabs.ts) | URLs with session params (OAuth callbacks, cart-ids, Gmail inbox fragments) create fresh mis-parented nodes every wake |
| 8 | **Incognito leaks into public tree** — `privacy.skipIncognito` honored only in nav-handler; lifecycle events ignore it | [lifecycle.ts:18-149](src/background/tabs/lifecycle.ts) vs [navigation-handler.ts:62-65](src/background/navigation/navigation-handler.ts) | Incognito URLs/titles flow into the public tree and get synced to Supabase |
| 9 | **NodeId collision on SW restart during async hydration** — module-level `nodeIdCounter` resets to 0; concurrent `new TreeNode()` between hydration and navigation collides | [tree-node.ts:2-22](src/background/state/tree-node.ts), [mapper.ts:10-12](src/shared/lib/mapper.ts) | Two nodes share the same id, one unreachable via `findNodeById`; search index has ghost docs |
| 10 | **`remove()` + `mergeDuplicateChildren` silently merges hundreds of branches** — deleting one node lifts all children to grandparent, then URL-duplicate siblings collapse recursively | [tree-node.ts:80-95](src/background/state/tree-node.ts), [nav-tree.ts:194-217](src/background/state/nav-tree.ts) | "Delete one node" = silent delete of deeply-nested duplicate branches; layout, ordering, pin state lost |
| 11 | **Service-worker terminates inside 1500ms save debounce window** — no `chrome.runtime.onSuspend` flush; `cacheTree` arms `setTimeout` that dies with the worker | [tree-storage.ts:262,412-416](src/background/services/tree-storage.ts), [service-worker.ts:1-74](src/background/service-worker.ts) | Up to 1.5s of recent navs/pins/renames lost on every SW eviction |
| 12 | **Sync conflict detection uses client `savedAt` as vector clock** — device B with 10min clock skew writes with older `savedAt`, conflict gate never fires | [sync-engine.ts:174,412](src/background/sync/sync-engine.ts) | Cross-device edits with modest clock skew silently lose one side |
| 13 | **`attachChild` doesn't check ancestry cycle** — reparent RPC with ancestor as child creates cycle; DFS infinite-loops | [tree-node.ts:42-63](src/background/state/tree-node.ts) | Service worker hang / OOM on drag-drop reparent |
| 14 | **In-place `node.data` URL rewrite bypasses search index** — `node.data = {...url, title, favicon}` without `refreshSearchEntry` | [navigation-handler.ts:137-142](src/background/navigation/navigation-handler.ts), [editor-handlers.ts:341](src/background/messaging/handlers/editor-handlers.ts) | Search stale: finds by old URL/domain/title; misses new |
| 15 | **closeOldest on fresh profile — `lastUsed=0` tie makes sort arbitrary** — `getLastUsed` uses `\|\| 0` collapsing "untracked" with epoch; fresh tabs get closed in insertion order | [tab-lru.ts:43](src/background/state/tab-lru.ts), [tab-manager.ts:207-233](src/background/state/tab-manager.ts) | User's "anchor" tab (first opened) is the first victim when hitting limit |

## P1 — High (wrong tree structure, incorrect behavior)

| # | Bug | File:line | Why |
|---|-----|-----------|-----|
| 16 | **Orphan tab when existing node was deleted** — `tabManager.nodeByTab` still returns dead nodeId; `findNodeById` returns null; silent fall-through, no node created for current URL | [navigation-handler.ts:130-191](src/background/navigation/navigation-handler.ts), [nav-tree.ts:194](src/background/state/nav-tree.ts) | `deleteNode` never notifies tabManager; entire subsequent browsing session in that tab untracked |
| 17 | **Redirects create dead-node chains** — `redirectDetector.recordTabUrl` called but `isRedirect` has zero call sites | [navigation-handler.ts:105-108](src/background/navigation/navigation-handler.ts), [redirect-detection.ts:21-26](src/background/navigation/redirect-detection.ts) | 3-hop OAuth login = 3 useless intermediate nodes per login |
| 18 | **3 webNav listeners share one handler → fan-out** — `onCommitted` + `onHistoryStateUpdated` + `onReferenceFragmentUpdated` all fire for one nav; no dedup via `documentId` or `transitionType` | [webnavigation.ts:14-16](src/background/navigation/webnavigation.ts), [navigation-handler.ts:32](src/background/navigation/navigation-handler.ts) | Duplicate children on SPA nav (Gmail/Linear/GitHub) |
| 19 | **`transitionType`/`transitionQualifiers` thrown away** — handler literally names the param `_transitionType` | [navigation-handler.ts:32](src/background/navigation/navigation-handler.ts) | Server redirects, client redirects, form submits, typed links all indistinguishable |
| 20 | **`tab.active` is a racy proxy for user-vs-programmatic intent** — sampled at handler entry after multiple awaits | [navigation-handler.ts:57,98](src/background/navigation/navigation-handler.ts) | Middle-click: new tab not active, user intent lost. Also tab may become active between awaits |
| 21 | **`findByUrl` linear DFS per new tab — O(n) per nav; picks arbitrary winner on URL duplicates** | [nav-tree.ts:311-319](src/background/state/nav-tree.ts), [navigation-handler.ts:197](src/background/navigation/navigation-handler.ts) | New tab attached to arbitrary duplicate subtree; perf at 10k+ nodes |
| 22 | **Same-URL branch drops `tab.pinned` updates** — metaPatch = `{title, favicon}` only; user pinning tab in Chrome never syncs to node | [navigation-handler.ts:113-184](src/background/navigation/navigation-handler.ts) | Pin state diverges between tree and browser |
| 23 | **Title stays as URL forever when first-load title sync misses** — `tab-sync.ts` gates on `urlKey` match; fast nav breaks fix-up | [navigation-handler.ts:115](src/background/navigation/navigation-handler.ts), [tab-sync.ts:30](src/background/tabs/tab-sync.ts) | Tree entries with ugly URLs-as-titles permanently |
| 24 | **`onTabRemoved` queries wrong window** — `currentWindow:true` may not be the window the close happened in | [lifecycle.ts:47-67](src/background/tabs/lifecycle.ts) | Closing tab in background window yanks `current` to foreground window's active tab |
| 25 | **`onTabRemoved` notify-then-cache is inverted** — sidepanel sees pre-mutation state; concurrent cacheTree can land old view | [lifecycle.ts:65-66](src/background/tabs/lifecycle.ts) | Swap order fix trivial |
| 26 | **`shouldSuppressActivate` runs AFTER mutations** — tree already navigated/registered before suppression check | [lifecycle.ts:86-123](src/background/tabs/lifecycle.ts) | Suppressed activations still leave orphaned nodes |
| 27 | **`onTabUpdated` ignores `changeInfo.url`** — URL changes not via webNavigation (`tabs.update`, same-doc) desync | [lifecycle.ts:151-166](src/background/tabs/lifecycle.ts) | Title/favicon drift from URL |
| 28 | **`onTabActivated` sets current without `shouldTrackUrl` gate** — stale `tabManager` entry on chrome:// tab still triggers focus jump to old node | [lifecycle.ts:83-136](src/background/tabs/lifecycle.ts) | Sidepanel focus jumps to unrelated page |
| 29 | **`register()` doesn't validate nodeId exists in tree** — phantom nodes in `nodeToTabs` map; `openNodes()` reports ghosts | [tab-manager.ts:43-58](src/background/state/tab-manager.ts), [tab-index.ts:37-43](src/background/state/tab-index.ts) | "Phantom open indicator" bugs after node deletion |
| 30 | **`touch` overwrites intentionally-old `lastUsed` on subsequent register** — syncOpenTabs sets accurate timestamps, any later `touch()` clobbers to `now()` | [tab-manager.ts:34-39](src/background/state/tab-manager.ts), [tab-lru.ts:12-20](src/background/state/tab-lru.ts) | closeOldest correctness decays; all tabs eventually cluster at "now" |
| 31 | **`mergeDuplicateChildren` cursor zombie** — `this.current` can be descendant of merged-away subtree; code only checks direct-child id match | [nav-tree.ts:84-117](src/background/state/nav-tree.ts) | current becomes reachable via findNodeById but invisible to DFS/serialization |
| 32 | **`onErrorOccurred` never listened** — aborted navigations create tree nodes via subsequent `onHistoryStateUpdated` | [webnavigation.ts](src/background/navigation/webnavigation.ts) | Dead navigations appear in tree |
| 33 | **Multi-window shared `tree.current`** — background window's active tab navigating can stomp foreground window's current | [nav-tree.ts:12](src/background/state/nav-tree.ts), [lifecycle.ts:139-149](src/background/tabs/lifecycle.ts) | Foreground user's next nav becomes child of background window's node |
| 34 | **Session restore: tabs race for `tree.current`** — 10 tabs restore in parallel, redirects create children off random ancestor | [sync-open-tabs.ts:60-65](src/background/tabs/sync-open-tabs.ts), [lifecycle.ts](src/background/tabs/lifecycle.ts) | Non-deterministic tree shape after restore |
| 35 | **Stub archive never materialized** — `fetchRemoteTreePayload` saves blob but never clears stub flag; every open re-downloads from Supabase | [sync-engine.ts:444-479](src/background/sync/sync-engine.ts), [tree-storage.ts:716-745](src/background/services/tree-storage.ts) | `unstubArchiveEntry` has zero call sites |
| 36 | **Migration race: `migrated=true` set BEFORE async read** — concurrent caller sees migrated=true, returns with legacy-shape cached data | [tree-storage.ts:900-936](src/background/services/tree-storage.ts) | UI sees summaries referencing blobs that don't yet exist |
| 37 | **`notifyTreeUpdate` mid-handler sees inconsistent tree state** — mutation-then-notify is awaited; concurrent mutation can interleave | [navigation-handler.ts:82,246](src/background/navigation/navigation-handler.ts), [lifecycle.ts:44,65,133-136](src/background/tabs/lifecycle.ts) | UI flicker, wrong focused node, stale breadcrumb |
| 38 | **`lru.remove()` leaves `latestNodeId` stale** — when replacement found, only `latestTabId` updated; invariant broken by comment | [tab-lru.ts:46-64](src/background/state/tab-lru.ts) | Consumers reading both get mismatched pairs |
| 39 | **Session-scoped suppression has no TTL; only focused tab cleared** — fallback loop queues suppression for all recency tabs but only clears the actually-focused one | [tab-manager.ts:139-145](src/background/state/tab-manager.ts), [temporary-selection.ts:96-215](src/background/services/temporary-selection.ts) | "Tree doesn't follow my click" for minutes after temp-selection |
| 40 | **New-tab title hijack via substring match** — any page with "new tab" in title (Stack Overflow threads, Notion docs, Google Chrome Help) routes to root | [url-utils.ts:38-42](src/background/utils/url-utils.ts) | False positives map real pages to root; conversely custom NTPs with different titles are tracked as normal |
| 41 | **Destructive URL rewrite keeps children attached** — `about:blank` node with children becomes real URL, children silently re-attributed | [navigation-handler.ts:136-153](src/background/navigation/navigation-handler.ts) | `google.com → [Twitter children]` misattribution |
| 42 | **closeOldest throws but Chrome actually closed tab** — `onTabRemoved` fires second unregister; `closeOldestUntil` over-closes | [tab-manager.ts:237-243](src/background/state/tab-manager.ts) | User loses N+1 tabs when N was the limit |

## P2 — Medium (behavior drift, UX decay)

| # | Bug | File:line | Why |
|---|-----|-----------|-----|
| 43 | **Double `markNodeVisited` in existing-same-URL path** — called at line 146 AND line 188-189 | [navigation-handler.ts:146,163,186-190](src/background/navigation/navigation-handler.ts) | Visit count inflated 2× on active tabs |
| 44 | **`prevCurrentId` can point at merged-away node** — `setCurrentById(prevCurrentId)` silent-fails; current jumps unexpectedly | [navigation-handler.ts:127,148-149,166-167,226-227](src/background/navigation/navigation-handler.ts), [nav-tree.ts:321-325](src/background/state/nav-tree.ts) | Intermittent focus jumps after delete during background load |
| 45 | **`setCurrentById` silent no-op when id missing** — 10+ call sites never check return; UI intent lost | [nav-tree.ts:321-325](src/background/state/nav-tree.ts) | Sidepanel says "set current to X", tree keeps old current |
| 46 | **SPA hash routing (`#/foo → #/bar`) invisible in tree** — `createUrlKey` strips hash; every route = no-op | [url-key.ts:50](src/shared/lib/url-key.ts) | Angular/docsite hash routes don't appear in history |
| 47 | **`onWindowFocusChanged` amplifies write pressure** — every alt-tab fires tabManager.touch + markNodeVisited + setCurrentById + cacheTree + notifyTreeUpdate | [lifecycle.ts:139-149](src/background/tabs/lifecycle.ts) | Throttles storage writes; unnecessary sidepanel updates |
| 48 | **Middle-click to same URL merges into shared node** — user wants separate branch, gets same node with multiple tabs | [navigation-handler.ts:197-217](src/background/navigation/navigation-handler.ts), [lifecycle.ts:37-44](src/background/tabs/lifecycle.ts) | "Duplicate tab" also loses signal — no new node |
| 49 | **Pinned tabs accumulate unrelated children** — navigating from pinned Gmail makes every email link a child of Gmail | [navigation-handler.ts:98](src/background/navigation/navigation-handler.ts) | Gmail pinned → 50 unrelated children/day |
| 50 | **Non-http(s) URLs (blob:, file://, chrome-untrusted://) silently dropped** — tab has no node, but stale registration persists | [url-utils.ts:45-52](src/background/utils/url-utils.ts), [navigation-handler.ts:93](src/background/navigation/navigation-handler.ts) | Meta-patches on stale node describe wrong URL |
| 51 | **`mergeNodeData` pins once, never unpins** — `Boolean(base.pinned \|\| incoming.pinned)` | [nav-tree.ts:78](src/background/state/nav-tree.ts) | User can't unpin a URL with any history of pinning once duplicate merge happens |
| 52 | **`mergeNodeData` drops layout on merge** — `base.layout ?? incoming.layout` — incoming's hand-arranged positions lost | [nav-tree.ts:72](src/background/state/nav-tree.ts) | Silent loss of user-arranged positions |
| 53 | **Multi-key writes not crash-atomic** — `takeArchivedTree`: writes index, then removes blob; crash between = orphan blob | [tree-storage.ts:703-710,633-652](src/background/services/tree-storage.ts) | Storage quota leak; "ghost archive" bugs |
| 54 | **`suppressNextTouch` is single-token** — two concurrent suppressions overwrite; first suppression leaks | [tab-manager.ts:15,115-123](src/background/state/tab-manager.ts) | Mismatch with `suppressActivateForTabId` (a Map) |
| 55 | **MiniSearch index rebuild on every SW wake** — O(n log n) per wake, not persisted | [nav-tree.ts:27-44](src/background/state/nav-tree.ts), [mapper.ts:28-56](src/shared/lib/mapper.ts) | Multi-second startup stall for power users with 10k nodes |
| 56 | **`touch`'s `_nodeId` param is a lie** — prefixed with `_`, silently trusts index not caller | [tab-manager.ts:34-39](src/background/state/tab-manager.ts) | Caller intent and LRU reality diverge without warning |
| 57 | **syncOpenTabs does not refresh tree-side recency** — only tabManager LRU refreshed; tree's node.lastVisited lags | [sync-open-tabs.ts:49-53](src/background/tabs/sync-open-tabs.ts) | UI ordering by "recent" drifts after reboot |
| 58 | **`createUrlKey` catch-branch produces keys in different namespace** — malformed URLs get non-canonical keys; parallel duplicates | [url-key.ts:44-67](src/shared/lib/url-key.ts) | Same logical URL under different keys depending on parse success |

## P3 — Low (latent, cosmetic, performance)

| # | Bug | File:line | Why |
|---|-----|-----------|-----|
| 59 | **`metaPatch` omits url — canonical case/trailing-slash never updated** | [navigation-handler.ts:120,174-179](src/background/navigation/navigation-handler.ts) | Display URL stays stale |
| 60 | **`ignoredTabs` never GC'd for tabs that never register** — Chrome TabId reuse can cause silent-ignore of reused id | [tab-manager.ts:17,147-151](src/background/state/tab-manager.ts) | Slow memory creep; rare correctness risk via TabId reuse |
| 61 | **`tabsByNode` returns ephemeral empty Set for missing keys** — ambiguous API, caller might think they mutate live set | [tab-index.ts:45-47](src/background/state/tab-index.ts) | API smell; could confuse future callers |
| 62 | **`WINDOW_ID_NONE` insufficient for transient hidden windows** — devtools pop-outs, PiP hosts trigger activation ripples | [lifecycle.ts:140](src/background/tabs/lifecycle.ts) | Write pressure on focus cycles |
| 63 | **Editor auto-exit not idempotent under rapid activation** — two concurrent `onTabActivated` both see editor active, both await save | [lifecycle.ts:74-81](src/background/tabs/lifecycle.ts) | Double-save or throw |
| 64 | **`getChildren` freezes shallow copy on every call** — 20k allocations per render on 5k-node tree | [tree-node.ts:112-114](src/background/state/tree-node.ts) | GC churn; false sense of immutability |
| 65 | **Nodes with long URLs (>2KB) can silently collide in MiniSearch** — token truncation collapses distinct URLs | [nav-tree.ts](src/background/state/nav-tree.ts) | Edge case, rare |
| 66 | **URL with auth credentials `user:pass@`** — may or may not be stripped by Chrome; privacy leak in tree if stored | [url-utils.ts](src/background/utils/url-utils.ts) | Rare but real |
| 67 | **`empty history-api.ts` file** — 0 bytes, dangling module | [navigation/history-api.ts](src/background/navigation/history-api.ts) | Dead file, confusing |
| 68 | **Search index stale after in-place data mutations elsewhere** — any path that updates node.data without refreshSearchEntry | multiple | Covered by #14 but variants exist |
| 69 | **No `onDetached`/`onAttached` listeners** — tab drag between windows "works" only because windowId not stored; latent | [lifecycle.ts:168-174](src/background/tabs/lifecycle.ts) | Amplifies #33 |
| 70 | **`nodeCount` uses `Math.max(0, n-k)` bandage** — hides double-decrements | [nav-tree.ts:205,267](src/background/state/nav-tree.ts) | `tree.size()` under-reports until reconstruction |
| 71 | **`dirty=false` set before `saveTreeToChrome` await** — if SW dies during the await, dirty is already lowered | [tree-storage.ts:437-439](src/background/services/tree-storage.ts) | Catch re-sets it, but not on termination |
| 72 | **`clearArchivesOnly` / `clearAllTrees` single try wrapping loop** — one removeItem throw aborts remaining removals | [tree-storage.ts:787-820](src/background/services/tree-storage.ts) | Partial state |
| 73 | **Back-forward cache restores may not fire webNav** — browser history navigations invisible to tracking | browser-level | Platform-dependent |
| 74 | **`redirectDetector.recordTabUrl` races across awaits** — two concurrent records can interleave, stale URL returned | [redirect-detection.ts:9-13](src/background/navigation/redirect-detection.ts) | Moot since `isRedirect` is never called (#17), but would bite if wired up |

---

## Top 5 architectural fixes that resolve most bugs

1. **Use `tab.openerTabId` as primary parent signal**, fall back to `tree.current` only when no opener exists. Kills bugs 1, 2, 7, 20, 33, 34, 48, 49.
2. **Wrap every mutating handler in `withTreeLock`** (export from tree-storage.ts:236). Kills bugs 4, 5, 37, plus most race conditions.
3. **Consume `details.transitionType`/`transitionQualifiers`/`documentId`** — Chrome already classifies redirects and dedupe tokens. Kills bugs 17, 18, 19, 41.
4. **Stop using mutable module-global `nodeIdCounter`** — switch to uuidv7 (already imported in tree-storage.ts:16). Kills bug 9, eliminates the whole ID-race class.
5. **Encapsulate mutations behind `NavigationTree` methods** that refresh the search index and emit change events. Make `TreeNode.data` externally readonly. Kills bugs 14, 31, 44, 45, 68.

## Other high-impact fixes

- `chrome.runtime.onSuspend` → `flushSaveNow()` (bug 11).
- `tabManager.nodeByTab` should validate against the tree (bug 29).
- Use server `updated_at` not client `savedAt` for sync ordering (bug 12).
- `attachChild` ancestry check (bug 13).
- Call `unstubArchiveEntry` after `saveArchiveTree` (bug 35).
- Lifecycle handlers must check `tab.incognito` + `settingsManager.get().privacy.skipIncognito` (bug 8).
- Fix about:blank root overwrite — never mutate root's URL in place (bug 3).
- Persist MiniSearch index via `toJSON`/`loadJSON` (bug 55).
