"""Generate a reader-friendly PDF of the tree-tracking bug audit.

Groups 74+ bugs by user-visible impact (not code layer), with plain-language
scenarios and severity tags.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, HRFlowable,
)

OUTPUT = "/Users/iv/dev/active/trail/extension/tasks/tree-tracking-bugs.pdf"

# ---- Styles -----------------------------------------------------------------
styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "Title", parent=styles["Title"],
    fontSize=26, leading=32, spaceAfter=8, alignment=TA_LEFT,
    textColor=colors.HexColor("#111111"),
)
SUBTITLE = ParagraphStyle(
    "Sub", parent=styles["Normal"],
    fontSize=12, leading=16, spaceAfter=18, textColor=colors.HexColor("#666666"),
)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontSize=18, leading=22, spaceBefore=18, spaceAfter=8,
    textColor=colors.HexColor("#111111"),
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontSize=14, leading=18, spaceBefore=14, spaceAfter=6,
    textColor=colors.HexColor("#1f2937"),
)
H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"],
    fontSize=11, leading=15, spaceBefore=10, spaceAfter=4,
    textColor=colors.HexColor("#374151"), fontName="Helvetica-Bold",
)
BODY = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10, leading=14, spaceAfter=6, alignment=TA_JUSTIFY,
    textColor=colors.HexColor("#1f2937"),
)
LABEL = ParagraphStyle(
    "Label", parent=styles["Normal"],
    fontSize=9, leading=12, spaceAfter=2,
    textColor=colors.HexColor("#6b7280"), fontName="Helvetica-Oblique",
)
CODE = ParagraphStyle(
    "Code", parent=styles["Code"],
    fontSize=8.5, leading=11, spaceAfter=4,
    textColor=colors.HexColor("#374151"), fontName="Courier",
    backColor=colors.HexColor("#f3f4f6"),
    leftIndent=6, rightIndent=6, borderPadding=4,
)
SMALL = ParagraphStyle(
    "Small", parent=styles["Normal"],
    fontSize=9, leading=12, spaceAfter=4,
    textColor=colors.HexColor("#4b5563"),
)

# ---- Severity pills ---------------------------------------------------------
SEV_STYLE = {
    "P0": ("#dc2626", "#fef2f2"),  # red
    "P1": ("#ea580c", "#fff7ed"),  # orange
    "P2": ("#ca8a04", "#fefce8"),  # yellow
    "P3": ("#6b7280", "#f3f4f6"),  # gray
}
SEV_LABEL = {
    "P0": "P0 · Critical",
    "P1": "P1 · High",
    "P2": "P2 · Medium",
    "P3": "P3 · Low",
}

def sev_pill(sev):
    fg, bg = SEV_STYLE[sev]
    style = ParagraphStyle(
        f"sev_{sev}", parent=BODY, fontSize=9, leading=11,
        textColor=colors.HexColor(fg), fontName="Helvetica-Bold",
        backColor=colors.HexColor(bg), borderPadding=(2, 6, 2, 6),
        alignment=TA_CENTER,
    )
    return Paragraph(SEV_LABEL[sev], style)

# ---- Bug data (human-readable) ---------------------------------------------

# Each bug: (number, severity, title, what_user_sees, technical_cause, file_hint)
BUGS = [
    # ========== 1. WRONG PARENT — tree shape doesn't match browsing ==========
    ("group", "Category 1: The tree shape doesn't match how you actually browse",
     "The extension decides which node becomes the parent of the new one using a single global pointer (the sidepanel's 'current' selection). It never looks at which tab opened which. So the tree shape is shaped by your sidepanel attention, not by your browsing flow."),

    (1, "P0", "Every new tab attaches under your sidepanel's current selection — not under the tab that opened it",
     "You're reading article A in Tab 1. You glance at Tab 2 (unrelated research) to copy a URL, then return to Tab 1 and Ctrl-click a link. The new tab appears as a child of the research you glanced at, not of article A.",
     "`tree.navigate(data)` always attaches to `this.current`, which is mutated by 15+ call sites. `tab.openerTabId` — which Chrome provides for free — is referenced zero times in the entire codebase.",
     "nav-tree.ts:168; navigation-handler.ts:220"),

    (2, "P0", "Background-tab navigations silently reparent under the sidepanel",
     "You're looking at node X in the sidepanel. A background tab in a different window refreshes or redirects. That redirect becomes a child of X.",
     "Global `tree.current` is shared across all tabs and windows; no per-tab last-node tracking.",
     "nav-tree.ts:12, 58"),

    (3, "P1", "Multiple windows fight over one 'current' pointer",
     "Two Chrome windows open. Window 2 (background) has an auto-refresh tab. That refresh stomps window 1's current. Your next nav in window 1 becomes a child of window 2's page.",
     "`NavigationTree.current` is a single mutable field, written on every activation and navigation across all windows.",
     "nav-tree.ts:12; lifecycle.ts:139"),

    (4, "P1", "Session restore: parents decided by a parallel race",
     "Chrome restores 10 tabs at startup. Tab 7 does a JS redirect after 500ms. At that moment `tree.current` is whatever tab happened to activate last — often unrelated. Tab 7's redirect becomes a child of that tab.",
     "`onTabActivated` fires in parallel during restore; every firing writes `tree.current`.",
     "sync-open-tabs.ts:60; lifecycle.ts:130"),

    (5, "P1", "Ctrl+click to open the same URL in a new tab: no new branch is created",
     "You want to explore a docs page from two angles — you middle-click it twice. Expected: two branches. Got: both tabs share one node.",
     "`findByUrl` returns the first DFS hit and the new tab is registered to it.",
     "navigation-handler.ts:197; lifecycle.ts:37"),

    (6, "P1", "'Duplicate tab' loses the duplication signal",
     "Right-click a tab → Duplicate. You expected a separate branch. No new node is created; the tree shows a single visit.",
     "Duplicate tab has `openerTabId` set — but it's ignored. URL match routes to the same node.",
     "navigation-handler.ts:197"),

    (7, "P2", "Pinned tabs accumulate unrelated children over time",
     "You pin Gmail. You click 50 different marketing links from Gmail over a week. Gmail's node ends up with 50 unrelated children because it was always `tree.current` when you clicked.",
     "No special-case for pinned tabs in parent inference.",
     "navigation-handler.ts:98"),

    (8, "P1", "Redirect chains leave dead nodes everywhere",
     "An OAuth login does 3 redirects (login.microsoft.com → aad.xyz → app). You end up on the real app, but the tree now has 3 useless intermediate nodes.",
     "`redirectDetector.recordTabUrl` is called, but `redirectDetector.isRedirect` has zero call sites. The collected signal is thrown away.",
     "navigation-handler.ts:105; redirect-detection.ts:21"),

    (9, "P1", "Server vs client redirects, typed URLs, form submits — all treated identically",
     "Chrome classifies every navigation via `transitionType` + `transitionQualifiers`. The extension ignores all of it.",
     "Handler parameter is literally named `_transitionType` (underscore = intentionally unused).",
     "navigation-handler.ts:32"),

    (10, "P1", "SPA navigation (Gmail/Linear/GitHub) creates duplicate siblings",
     "A single SPA click fires up to 3 webNavigation events (committed + historyStateUpdated + referenceFragmentUpdated) — all handled the same way. Depending on timing, you get a duplicate sibling node.",
     "All three listeners share one handler, no deduplication via `documentId`.",
     "webnavigation.ts:14"),

    # ========== 2. DATA LOSS ==========
    ("group", "Category 2: Silent data loss",
     "State that should persist — your pins, layouts, titles, undo history, recent navigations — sometimes disappears without a trace."),

    (11, "P0", "Deleting one node can silently delete hundreds of nested branches",
     "You delete node N, expecting to remove N (and maybe its direct subtree). Instead, N's 500 descendants are lifted up to N's parent; any URLs that now share a key with siblings quietly merge, cascading recursively. Pin state, layout positions, child ordering — all lost with no confirmation.",
     "`TreeNode.remove()` reparents children to grandparent; `mergeDuplicateChildren` then collapses URL duplicates recursively.",
     "tree-node.ts:80; nav-tree.ts:194"),

    (12, "P0", "OAuth popup can overwrite your tree's root node",
     "A popup opens (window.open) on about:blank — tab maps to root. The popup then navigates to a real URL. The extension's 'if the old URL was untrackable, rewrite it in place' branch kicks in and overwrites your root's URL/title/favicon with whatever that popup visited.",
     "The existing-node-with-untrackable-URL branch rewrites `node.data` in place without caring that the node is the tree's root.",
     "navigation-handler.ts:136–153"),

    (13, "P0", "Service worker dies within the 1.5s save window — up to 1.5s of navigations vanish",
     "You open 5 tabs in quick succession; Chrome evicts the MV3 service worker before the debounced save timer fires. The timer dies with the worker. Nothing was persisted.",
     "`cacheTree()` arms `setTimeout(1500)` but nothing calls `flushSaveNow` from `chrome.runtime.onSuspend`.",
     "tree-storage.ts:262; service-worker.ts has no onSuspend handler"),

    (14, "P0", "Cross-device sync loses edits when clocks disagree",
     "Device B's clock is 10 min behind device A. B writes first but carries an older `savedAt` timestamp. On pull, A's conflict check uses `savedAt` as a vector clock — B's newer write is ignored, then on next push from A it silently clobbers B's changes.",
     "Sync compares `savedAt` (client-generated) instead of server `updated_at`.",
     "sync-engine.ts:412"),

    (15, "P0", "NodeId collision after service worker restart",
     "Service worker sleeps. Counter resets to 0. During async hydration, a navigation can create a new node with ID 6 that collides with a node about to be deserialized. `nodeMap.set(6, ...)` silently overwrites one. One node becomes unreachable via `findNodeById`.",
     "`nodeIdCounter` is module-global and race-prone across async boundaries.",
     "tree-node.ts:2–22"),

    (16, "P1", "Renames and in-place URL rewrites break search silently",
     "You rename a node. Searching by the new name returns nothing. Searching by the old name returns it.",
     "Multiple paths do `node.data = {...}` without calling `refreshSearchEntry`. The MiniSearch index goes stale.",
     "navigation-handler.ts:137; editor-handlers.ts:341"),

    (17, "P0", "Your pinned-state and hand-arranged layout are lost during auto-merge",
     "You've arranged positions and pinned node A. A duplicate collides (e.g. from session restore). The merge picks `base.layout ?? incoming.layout` and `Boolean(base.pinned || incoming.pinned)` — if `base` has no layout, incoming's is kept, but otherwise layout may vanish; pins stick permanently (you can't unpin once merged).",
     "`mergeNodeData` uses boolean-OR for pin and left-wins for layout, no timestamp-based LWW.",
     "nav-tree.ts:72, 78"),

    (18, "P1", "Entering editor mode immediately erases the undo history it just created",
     "Enter editor mode, make several edits, try to Undo back past the first edit — nothing happens.",
     "`enterEditorMode` calls `snapshot(...)` then `CommandManager.clearHistory()` on the next line, wiping the snapshot.",
     "editor-handlers.ts:153–156"),

    (19, "P1", "Undo/redo strands tabs — your tabs lose their node mappings",
     "You hit Undo on a branch you just created. Tabs that were mapped to nodes in that branch are now mapped to nothing. Next activation creates a brand-new node — your history duplicates.",
     "`applyTree` calls `syncOpenTabs()` which does `tabManager.reset()` and then re-registers only tabs whose URL matches in the restored tree. Also, `syncOpenTabs` runs before `cacheTree(tree)`, so it sees the OLD tree.",
     "undo-handlers.ts:7–13"),

    (20, "P1", "'Tree doesn't follow my click' after temporary selection",
     "You temporarily hover/preview a node, then click a tab. The tree doesn't move.",
     "The temp-selection fallback queues `suppressNextActivate` for every tab in a recency list, but only clears the one it managed to focus. The rest stay suppressed until session end.",
     "tab-manager.ts:139–145; temporary-selection.ts:96–215"),

    (21, "P1", "Title stuck as URL forever",
     "You load a page fast, navigate away before the title arrives. The node stores the URL as its title permanently — because the title-sync handler gates on URL-key match, which now fails.",
     "`tab-sync.ts:30` requires `createUrlKey(node.data.url) === createUrlKey(tabUrl)` to fix the title.",
     "navigation-handler.ts:115; tab-sync.ts:30"),

    (22, "P1", "Orphan tab: after deleting a node, the mapped tab keeps no node",
     "You delete a node N. A tab was mapped to N. The tab keeps browsing; every navigation in it silently does nothing because `tabManager.nodeByTab(tab)` still returns the dead id and `findNodeById(deadId)` returns null.",
     "`deleteNode` in nav-tree.ts:194 never notifies `tabManager`.",
     "navigation-handler.ts:130–191"),

    # ========== 3. RACES / CONCURRENCY ==========
    ("group", "Category 3: Concurrency — two handlers collide",
     "Every handler (navigation, tab activated, tab removed, tab updated) mutates shared tree state with no lock, awaits multiple times, and Chrome freely interleaves events. Result: the tree's shape depends on microsecond-level timing."),

    (23, "P0", "Concurrent navigations in different tabs: parents get swapped",
     "Two tabs commit a navigation in the same event-loop tick. Both handlers read `tree.current`, both call `setCurrentById` then `navigate()`. Between those two lines, the other handler slips in. The new node is attached to the wrong parent.",
     "`setCurrentById + navigate` is a non-atomic compound. `treeMutex` exists but only guards persistence, not mutation.",
     "navigation-handler.ts:156–158, 218–230"),

    (24, "P0", "Service-worker boot race: registrations wiped mid-flight",
     "SW wakes. `syncOpenTabs()` calls `tabManager.reset()` then `await browser.tabs.query({})`. Between those two, a webNav event fires, a handler registers a tab. `syncOpenTabs` then overwrites or erases that registration.",
     "`reset()` also clears `ignoredTabs` and `suppressActivate` — unrelated in-flight intent is lost.",
     "sync-open-tabs.ts:17–47"),

    (25, "P1", "`syncOpenTabs` creates a dangling node on every service-worker wake",
     "If your active tab's URL has session params (OAuth callbacks, shopping-cart IDs, Gmail `#inbox/...`), it doesn't match `findByUrl` on wake. `syncOpenTabs` calls `tree.navigate(data)` without setting current first — the new node attaches to the persisted current from last session, wherever that was. Tree slowly bloats with mis-parented nodes.",
     "`sync-open-tabs.ts:80` does not set current before navigate.",
     "sync-open-tabs.ts:67–88"),

    (26, "P1", "Tab closed mid-handler — handler re-registers a dead tab id",
     "Handler calls `await browser.tabs.get(tabId)`; the user closes the tab; `onTabRemoved` unregisters. Handler resumes, happily calls `tabManager.register(nodeId, deadTabId)`. Phantom tab entry persists until SW restart.",
     "Multiple awaits between tab read and tree mutation.",
     "navigation-handler.ts:57, 214, 222"),

    (27, "P1", "Suppressed tab-activation still mutates the tree",
     "`shouldSuppressActivate` is checked AFTER the tree is already navigated and the tab is already registered. Suppression doesn't prevent the mutation it was supposed to hide.",
     "Lines 93–110 mutate before line 121 checks suppression.",
     "lifecycle.ts:86–123"),

    (28, "P2", "Sidepanel sees tree snapshots out of order",
     "`notifyTreeUpdate` is awaited mid-handler. A concurrent handler can interleave, mutating the tree while the previous notify is still serializing. Sidepanel receives snapshots in a nondeterministic order.",
     "No snapshot-then-broadcast separation; the broadcast reads live state.",
     "navigation-handler.ts:82, 246; lifecycle.ts:44, 65, 133"),

    (29, "P1", "Concurrent temp-selection `begin()` calls leave stranded suppressions",
     "Two sessions start nearly together. Both see `activeSessionId === null` across the `await getActiveTab()`. Both write, second overwrites first; first's suppressions are never cleared.",
     "`begin()` is not atomic.",
     "temporary-selection.ts:56–77"),

    # ========== 4. SPECIAL URLS / PRIVACY ==========
    ("group", "Category 4: Special URLs and privacy",
     "Incognito, blob:, file://, and about:blank URLs, plus URLs with credentials — the extension's handling of edge-case URLs leaks private data, misroutes real pages, and creates ghost nodes."),

    (30, "P0", "Incognito URLs leak into the public tree",
     "Setting `privacy.skipIncognito` is honored ONLY in the navigation handler. The lifecycle handlers (onCreated, onActivated, onUpdated, focus-changed) all ignore `tab.incognito`. Your incognito URL becomes the active node and gets synced to Supabase.",
     "Lifecycle handlers never check `tab.incognito` or `settingsManager.get().privacy.skipIncognito`.",
     "lifecycle.ts:18–149"),

    (31, "P1", "Pages with 'new tab' in their title hijack the root",
     "Open a Stack Overflow thread titled 'How do I open a new tab...'. The extension detects 'new tab' in the title and routes it to your tree's root node.",
     "`isNewTabContext` substring-matches the title.",
     "url-utils.ts:38–42"),

    (32, "P1", "Custom new-tab-page extensions are tracked as regular pages",
     "Flip side of #31. A custom NTP with a title like 'Start page' doesn't match 'new tab' and gets tracked as if it were a normal site.",
     "Same substring logic.",
     "url-utils.ts:38–42"),

    (33, "P2", "blob: / file:// / chrome-untrusted:// URLs silently skipped, stale mappings persist",
     "You open a PDF from a blob: URL. The tab has no node. But the tab's PRIOR mapping (from an earlier http page) persists. Next meta-patch for that tab updates the WRONG URL's title.",
     "`shouldTrackUrl` filters but doesn't un-register stale mappings.",
     "url-utils.ts:45–52; navigation-handler.ts:93"),

    (34, "P2", "SPA hash-routing sites are invisible in the tree",
     "Older Angular / docsites using `site.com/#/intro` → `/#/install`. The handler strips the hash during URL-key computation, so every route change is a no-op. Your entire in-app navigation doesn't appear in the tree.",
     "`createUrlKey` sets `url.hash = \"\"`.",
     "url-key.ts:50"),

    (35, "P3", "URLs with auth credentials may be stored",
     "`https://user:pass@site.com` — if Chrome doesn't strip before handoff, credentials land in your tree and sync payload.",
     "No credential-stripping in the URL normalization.",
     "url-utils.ts"),

    # ========== 5. STORAGE / QUOTA / PERF ==========
    ("group", "Category 5: Storage, quota, performance",
     "Writes aren't atomic, migrations race, stub-archives re-download every time, and startup stalls grow linearly with tree size."),

    (36, "P1", "Synced archives re-download from Supabase every time you open them",
     "Another device wrote an archive. You open it once: extension downloads, caches blob locally. You open it again: it downloads again. And again.",
     "`fetchRemoteTreePayload` saves the blob but never calls `unstubArchiveEntry`. That function has zero call sites.",
     "sync-engine.ts:444–479; tree-storage.ts:716–745"),

    (37, "P1", "First-boot migration race can expose legacy-shape data",
     "`ensureMigrated` sets `migrated = true` BEFORE the migration read. A concurrent caller sees 'done', reads legacy-shape data, caches it, then real migration overwrites. The window is brief but real on slow first boots after upgrade.",
     "Flag set before await instead of after.",
     "tree-storage.ts:900–936"),

    (38, "P2", "Archive deletion can leak blob data (quota growth)",
     "Extension writes index (removing archive X), then removes the blob. Crash between = index says 'gone', blob stays. Over time: quota fills.",
     "Multi-key writes aren't crash-atomic; no startup GC.",
     "tree-storage.ts:703–710"),

    (39, "P2", "Startup stalls for large trees",
     "Power users with 10k+ nodes: every service-worker wake blocks on MiniSearch index rebuild. MV3 wakes are frequent — every tab event, every RPC.",
     "`constructFromRoot` does `searchIndex.addAll(docs)` on every hydration; index isn't persisted.",
     "nav-tree.ts:27–44"),

    (40, "P2", "Close-oldest picks your first-opened 'anchor' tab on a fresh profile",
     "Fresh Chrome profile: every tab has `lastAccessed=0`. When you hit the tab limit, close-oldest sorts by `lastUsed - 0` ties, picks whichever got into the data structure first. That's usually the tab you care most about.",
     "`getLastUsed` uses `|| 0` collapsing 'untracked' with epoch.",
     "tab-lru.ts:43; tab-manager.ts:207"),

    # ========== 6. UX DRIFT ==========
    ("group", "Category 6: Behavior drift",
     "Smaller issues that accumulate: stale counts, spurious focus jumps, unnecessary writes."),

    (41, "P2", "Visit count inflates 2× on active tabs",
     "`markNodeVisited` is called twice on the same navigation in the active-tab path.",
     "Redundant call sites at lines 146 and 188–189.",
     "navigation-handler.ts:146, 163, 186–190"),

    (42, "P2", "`setCurrentById` silently no-ops on missing ids",
     "The sidepanel says 'set current to X'. If X was merged away by a background cleanup, nothing happens — silently. The sidepanel thinks it succeeded.",
     "Method returns void, 10+ call sites never check.",
     "nav-tree.ts:321–325"),

    (43, "P2", "Alt-tab amplifies write pressure",
     "Every window focus change fires `tabManager.touch + markNodeVisited + setCurrentById + cacheTree + notifyTreeUpdate` — even when the active tab hasn't changed.",
     "No short-circuit for unchanged active tab.",
     "lifecycle.ts:139–149"),

    (44, "P2", "Focus jumps unexpectedly after deleting a node during background load",
     "`prevCurrentId` is snapshotted early. If a concurrent delete merges that node away, `setCurrentById(prevCurrentId)` no-ops — current stays on the newly-created background node, violating the 'only-move-on-active-tab' invariant.",
     "Stale ID used after merge.",
     "navigation-handler.ts:127, 148–167, 226–227"),

    (45, "P2", "Pin state doesn't sync when you pin a tab in Chrome",
     "You manually pin a tab in Chrome. The tree's node stays unpinned because the same-URL navigation branch uses `metaPatch = {title, favicon}` only.",
     "`pinned` never applied in the same-URL branch.",
     "navigation-handler.ts:113–184"),

    (46, "P3", "Canonical URL display stays stale",
     "You navigate to `https://example.com/Path/`, then later `Example.com/Path`. Same URL-key, so same node. But display URL stays whatever the first visit was.",
     "`metaPatch` omits URL, even when case/slash differs.",
     "navigation-handler.ts:120"),

    (47, "P3", "CSS bug: `getChildren` allocates frozen copy per call",
     "Tree renders on a 5k-node tree → 20k allocations per render.",
     "`Object.freeze([...this.children])` on every call, in hot paths.",
     "tree-node.ts:112–114"),

    (48, "P2", "`tabsByNode` returns an ephemeral empty Set for missing keys",
     "Consumer might think they're mutating the live set; they mutate a throwaway.",
     "API smell: `?? new Set()` conflates missing with empty.",
     "tab-index.ts:45–47"),

    # ========== 7. LATENT / EDGE CASES ==========
    ("group", "Category 7: Latent and edge cases",
     "Issues that are real but only bite in rare configurations, or that set up future regressions."),

    (49, "P0", "Drag-drop reparent with ancestor-as-child creates a cycle → infinite loop",
     "If a reparent RPC is ever called with an ancestor as the child, `attachChild` accepts it. DFS iteration then infinite-loops. SW hangs until Chrome kills it.",
     "No ancestry check in `TreeNode.attachChild` beyond `child === this`.",
     "tree-node.ts:42–63"),

    (50, "P2", "`lru.remove()` leaves `latestNodeId` stale",
     "When a replacement is found, only `latestTabId` is updated. A consumer reading both gets inconsistent pairs.",
     "Known invariant violation with an apologetic code comment.",
     "tab-lru.ts:46–64"),

    (51, "P2", "`suppressNextTouch` is single-token; rapid-fire overwrites",
     "Two near-simultaneous suppression requests: the second overwrites, the first's touch goes through.",
     "Single field vs the Map used for `suppressActivate`.",
     "tab-manager.ts:15, 115"),

    (52, "P3", "`nodeCount` bandaged with `Math.max(0, …)` — hides double-decrements",
     "`tree.size()` under-reports until next reconstruction; UI badges show wrong counts.",
     "Clamping hides bugs instead of asserting invariants.",
     "nav-tree.ts:205, 267"),

    (53, "P3", "No `onDetached` / `onAttached` listeners — dragging tabs between windows is latent",
     "Works today only because `windowId` isn't stored. Any future window-scoped feature silently drifts.",
     "Grep: zero matches for these listeners.",
     "lifecycle.ts:168–174"),

    (54, "P3", "Dead file: `navigation/history-api.ts` is 0 bytes",
     "Empty module left over from earlier work. Confusing to readers; potential import issue.",
     "File is empty.",
     "navigation/history-api.ts"),

    (55, "P3", "`clearArchivesOnly` / `clearAllTrees` use one `try` wrapping the whole loop",
     "One failed `removeItem` aborts the rest; partial state is left.",
     "try{} around loop = all-or-nothing, but cleanup is supposed to be best-effort.",
     "tree-storage.ts:787–820"),

    (56, "P3", "`dirty=false` set before the save's `await` resolves",
     "If SW dies mid-save, `dirty` is already lowered. `catch` resets it on error, but not on termination.",
     "Flag order problem.",
     "tree-storage.ts:437–439"),

    (57, "P2", "Temp-selection `preview`/`cancel`/`accept` unregister tabs on focus failure",
     "`browser.tabs.update` throws on transient failure (window closing, OS denies focus). Code interprets as 'tab gone' and unregisters — but the tab still exists and its user mapping was just destroyed.",
     "Speculative cleanup masquerading as real cleanup.",
     "temporary-selection.ts:102–124, 172–173, 222–227"),

    (58, "P2", "`archiveActiveTree → switchTree` doesn't flush in-flight saves first",
     "Pending `cacheTree` debounce sees a different tree than the archive write. Also, `tabManager.reset()` runs before `setActiveTree` commits — if that throws, tabs are orphaned across all nodes.",
     "No `flushSaveNow()` before archive/switch.",
     "tree-storage.ts:660; tree-handlers.ts:240"),

    (59, "P3", "Editor auto-exit not idempotent under rapid activation",
     "Two concurrent `onTabActivated` both see `editor active`, both await save. Depending on impl, either double-saves or throws.",
     "No 'already saving' guard.",
     "lifecycle.ts:74–81"),

    (60, "P3", "`mergeNodeData` left-wins on layout — hand-arranged positions can vanish",
     "Merge picks `base.layout ?? incoming.layout`. If `base` has no layout but `incoming` does, fine. Otherwise incoming's hand-arranged positions are discarded.",
     "No timestamp-based LWW.",
     "nav-tree.ts:72"),

    (61, "P3", "Pinned-once stays pinned forever",
     "`pinned = Boolean(base.pinned || incoming.pinned)`. Any history of pinning wins during merges; you can't unpin.",
     "Boolean-OR instead of LWW.",
     "nav-tree.ts:78"),

    (62, "P2", "Back-forward cache restores may be invisible",
     "Browser back button from BFCache may not fire webNav. Your history doesn't reflect going back.",
     "Platform-dependent, browser-level.",
     "platform"),

    (63, "P3", "`createUrlKey` catch-branch produces keys in a different namespace than the try-branch",
     "Malformed URLs caught by `try { new URL(...) } catch {}` get keys without `https://` prefix. Parallel duplicates can exist.",
     "Different normalization on success vs failure path.",
     "url-key.ts:44–67"),

    (64, "P3", "No `onErrorOccurred` listener — aborted navigations can still create nodes",
     "URL aborts mid-flight. Later `pushState` on a 'retry' button creates a node as if the initial nav succeeded.",
     "Webnav lifecycle half-wired.",
     "webnavigation.ts"),

    (65, "P1", "`onTabRemoved` queries wrong window",
     "Close a tab in a background window. `currentWindow:true` returns last-focused window's active tab. Your tree's current yanks to the unrelated foreground tab.",
     "`currentWindow:true` is wrong scope.",
     "lifecycle.ts:47–67"),

    (66, "P2", "`onTabRemoved` notifies before caching",
     "Sidepanel sees pre-mutation state; concurrent `cacheTree` can land the old view into persistence.",
     "Order inverted vs other handlers.",
     "lifecycle.ts:65–66"),

    (67, "P1", "`onTabUpdated` ignores `changeInfo.url`",
     "Same-document URL changes delivered by `tabs.update` (not webNav) never flow into tree state. Title/favicon drift.",
     "Handler only checks audio/title/favicon.",
     "lifecycle.ts:151–166"),

    (68, "P2", "`onTabActivated` sets current without `shouldTrackUrl` check",
     "Tab with stale mapping to a chrome:// URL still triggers focus jump to the old node.",
     "Gate only exists in the `nodeId === undefined` branch.",
     "lifecycle.ts:83–136"),

    (69, "P2", "`ignoredTabs` never garbage-collected for tabs that never register",
     "Slow leak. More worryingly: when Chrome eventually reuses TabIds, the reused id is silently ignored.",
     "No cleanup path.",
     "tab-manager.ts:17, 147"),

    (70, "P1", "`register()` accepts any nodeId without tree validation",
     "If a caller passes a deleted node id, `TabIndex` happily creates a ghost node entry. `openNodes()` returns phantoms.",
     "TabManager doesn't know about the tree.",
     "tab-manager.ts:43–58"),

    (71, "P1", "`touch` ignores its `_nodeId` param, trusts the index instead",
     "The param is prefixed `_` to advertise 'unused'. Caller intent diverges from reality; no warning logged.",
     "Parameter is a lie.",
     "tab-manager.ts:34–39"),

    (72, "P3", "`touch` overwrites intentionally-old `lastUsed` with `Date.now()`",
     "`syncOpenTabs` sets accurate timestamps from `tab.lastAccessed`. Any later `touch()` without a `lastUsed` arg clobbers to now. All tabs eventually cluster.",
     "Overwrite semantics.",
     "tab-manager.ts:34; tab-lru.ts:12"),

    (73, "P2", "`findByUrl` picks arbitrary DFS winner on URL duplicates",
     "Two subtrees share a URL. `findByUrl` always returns the leftmost-DFS hit. One subtree becomes a black hole for all re-visits to that URL.",
     "No proximity heuristic.",
     "nav-tree.ts:311–319"),

    (74, "P3", "`findByUrl` is O(n) per new tab; 10k-node tree stalls",
     "Linear scan runs on every first-nav of every new tab. Perceptible at scale.",
     "No URL-key → node map.",
     "nav-tree.ts:311; navigation-handler.ts:197"),

    (75, "P2", "`closeOldest` throws but Chrome actually closed the tab",
     "`onTabRemoved` fires second unregister; `closeOldestUntil` over-closes. You asked to keep N tabs; lose N+1.",
     "`try { tabs.remove(); unregister() } catch { return null }` — catch doesn't clean up.",
     "tab-manager.ts:237–243"),

    (76, "P2", "Editor snapshot taken mid-mutation window",
     "Between `loadTree(treeId)` and `structuredClone(toJSON(tree))`, nav events can mutate the live tree. Rollback captures a partially-mutated state.",
     "No lock around snapshot.",
     "editor-handlers.ts:135–151"),

    (77, "P1", "`saveEditorMode` coalescing drops intermediate work",
     "Concurrent callers share one in-flight promise. Second navigation proceeds thinking editor exited, but active tree is about to be swapped — node lands in wrong tree.",
     "Coalescing doesn't preserve ordering vs navigation side effects.",
     "editor-handlers.ts:221–237"),

    # ========== 8. SETTINGS / RECENCY / MIGRATION ==========
    ("group", "Category 8: Settings, blocklist, recency",
     "Settings propagation has gaps — blocklist effectively off during the first 50-200ms of every service-worker wake, settings changes from other contexts don't reach the background, and visit counts are quietly dropped by a flawed timestamp guard."),

    (78, "P0", "Blocklist is off for 50–200ms on every service-worker wake — privacy leak",
     "You blocklisted `*.bank.com`. Chrome evicts the service worker (every few minutes of inactivity). You then open a banking tab. During the brief window before `settingsManager.init()` resolves and the blocklist is compiled, navigation handlers fire with `shouldTrackUrl` returning true — the banking URL gets tracked.",
     "`cachedBlocklist = () => false` as the default (track everything). `settingsManager.init()` is fire-and-forget; `loadSettings → import → setUrlBlocklist` is a chained async cascade.",
     "url-utils.ts:57; settings.ts:218–233; service-worker.ts:42–49"),

    (79, "P1", "Visit count drops silently when clocks mix",
     "Callers pass two clocks interchangeably: `Date.now()` vs `tab.lastAccessed`. These aren't synchronized sub-ms; `lastAccessed` can trail. Writing `Date.now()` then `tab.lastAccessed` no-ops because the guard is `<= prevAt`. `visitCount` is undercounted; `lastVisitedAt` freezes at the wrong value.",
     "`markNodeVisited` uses `if (nextAtRaw <= prevAtRaw) return false;` — strict-equal collapses rapid calls too.",
     "node-recency.ts:19"),

    (80, "P1", "Tree-switch permanently deletes restore-URLs on partial restore",
     "You switch trees with 30 saved-open-tabs. Restore opens 12, then the service worker dies or `browser.tabs.create` fails. The other 18 URLs are deleted from storage forever — no recovery path.",
     "`getOpenTabs` deletes the saved map entry before it returns. Loop in tree-handlers.ts:264 catches+continues on throws; SW termination also loses the URLs.",
     "tab-restoration.ts:19–26; tree-handlers.ts:251, 264–281"),

    (81, "P2", "Settings/flags changes from other contexts don't propagate until SW restart",
     "Settings UI writes through RPC — works. But any direct write from onboarding, sidepanel, or popup (via `settingsItem.setValue`) doesn't update the in-memory state in the background.",
     "No `storage.onChanged` / `.watch()` listener in the background. In-memory state only refreshed on SW boot.",
     "settings.ts; flags.ts"),

    (82, "P2", "Future default-settings fields will overwrite user overrides",
     "`saveSettings` spreads `{...defaultSettings, ...next}`. Any field added to `defaultSettings` in a later version will stomp a user's saved override when they patch any other field — because `next` was loaded under the old defaults.",
     "Merge semantics: new defaults applied AFTER old saved values in the spread.",
     "settings.ts:203"),

    (83, "P3", "Migration fails silently on out-of-order entries",
     "If a contributor appends `{from:2,to:3}` before `{from:1,to:2}` in the `MIGRATIONS` array, `{2→3}` is skipped during that session.",
     "Single-pass `for` loop filtered by `m.from !== current`. No `while (current < CURRENT_VERSION)` guard.",
     "migrations.ts:54–69"),

    # ========== 9. SIDEPANEL / UI SYNC ==========
    ("group", "Category 9: Sidepanel and UI sync",
     "The sidepanel receives tree updates via a custom pub-sub with debouncing. Several reasons are missing from the immediate-broadcast list, transient state leaks across unrelated updates, and bootstrap can overwrite live state with a stale snapshot."),

    (84, "P0", "Delete / Backspace fires while Rename or confirm dialogs are open — silent deletion",
     "You open the Rename dialog. You tab out of the input onto the Cancel button, then hit Backspace. The shortcut handler thinks you're not in an overlay (it doesn't check `renameTarget` or `deleteTreeConfirm.open`) and deletes the selected node.",
     "`overlayOpen` check is incomplete — doesn't cover rename, delete-confirm, command palette, sync-conflict dialogs.",
     "useShortcuts.ts:55–56, 293–308"),

    (85, "P1", "Rename doesn't show up in the sidepanel for up to 200ms",
     "You rename a node. Dialog closes. Tree display still shows the old title briefly (longer if another debounced update coalesces).",
     "`rename` is not in `IMMEDIATE_REASONS` — falls into the 200ms debounce bucket.",
     "notifications.ts:44–57"),

    (86, "P1", "Click-to-navigate feels sluggish — 200ms debounce",
     "Clicking a link and the sidepanel's current-indicator update feels laggy. `navigate` is the default reason; also debounced. But `set-current` (sidepanel-driven) is immediate — inconsistent perceived latency.",
     "`IMMEDIATE_REASONS` misses `navigate`, `tabs`, `temp-selection`, `sync`.",
     "notifications.ts:215"),

    (87, "P1", "Stale `viewIntent` leaks across unrelated tree updates",
     "You rename a node (which emits a focus-to-node intent). Then a background tab fires a `tabs`-reason update. The stale `viewIntent` from the rename is still in store state — the graph re-focuses/zooms to the renamed node.",
     "`applyTreeState` resolves `nextViewIntent = payload.view ?? state.graph.viewIntent`. `clearViewIntent` has zero callers.",
     "store.ts:310–315, 632–635"),

    (88, "P1", "Bootstrap races the first broadcast and overwrites live state",
     "`getTreeState()` RPC resolves with snapshot T0. Before the React effect commits, a navigation fires `TREE_UPDATED` with snapshot T1 — which is applied. Then `bootstrapGraph(T0)` runs and clobbers T1 with stale data.",
     "No timestamp guard or 'already bootstrapped' flag.",
     "useBootstrap.ts:63–78; useRuntimeMessages.ts:16–24"),

    (89, "P2", "Retry re-seeds store, wipes live tab state",
     "User hits 'retry' after a transient glitch. `bootstrapGraph` replaces tree/pins/openNodes but leaves `collapsedNodeIds`/`search`/`selectedNodeIds` alone. Mismatch with `applyTreeState`'s tree-switch semantics → inconsistent state.",
     "Two different reducers for 'apply snapshot' with different reset rules.",
     "useBootstrap.ts:97–101; store.ts:283–302"),

    (90, "P2", "Every tree update allocates new Sets, Maps, PinnedManagers → cascading re-renders",
     "`applyTreeState` returns fresh `Set` / `Map` / `PinnedManager` instances on every payload, even when contents haven't changed. `TrailGraph` and `PinnedDropdown` re-render on every tab-count ping.",
     "No structural-equality diff before allocation.",
     "store.ts:305–383; PinnedDropdown.tsx:46"),

    (91, "P2", "Debounced `view` intent discarded on coalesce",
     "Two debounced calls arrive. The second omits `view`. The first's `view` (with `focusNodeId`) is dropped because `pendingArgs = { ..., ...(view ? { view } : {}) }` replaces wholesale.",
     "No merge semantics for pendingArgs.",
     "notifications.ts:229–239"),

    (92, "P3", "`Shift+Delete` double-fires recursive delete",
     "With tinykeys, `Shift+Delete` matches BOTH the `\"Delete\"` binding (with `shiftKey` branching) AND the separate `\"Shift+Delete\"` binding. Both handlers call `deleteNodes(..., true)` → RPC fires twice.",
     "Redundant bindings.",
     "useShortcuts.ts:293–308"),

    # ========== 10. ADDITIONAL DISTINCT BUGS ==========
    ("group", "Category 10: Additional distinct bugs",
     "Bugs that overlap thematically with earlier categories but have unique mechanics worth calling out separately."),

    (93, "P0", "Activating a pre-existing untracked tab creates a false child of your current node",
     "You install the extension or the service worker wakes up. You have 20 tabs already open, none tracked yet. You click tab #7 — extension creates a brand-new node for it as a CHILD of whatever you're currently viewing in the sidepanel. All 20 pre-existing tabs get false parent edges based on the order you happen to click them.",
     "`onTabActivated`'s fallback branch calls `tree.navigate(data)` which uses `this.current` as the parent. Should attach as a root or skip until a real navigation happens.",
     "lifecycle.ts:101–112"),

    (94, "P1", "Merge leaves `tree.current` as a zombie pointer",
     "After `mergeDuplicateChildren` collapses a subtree, if `tree.current` was a DESCENDANT of the merged-away subtree (not a direct child), the code doesn't catch it. `tree.current` stays pointing at a node that's still in `nodeMap` but unreachable via DFS from root — invisible to serialization but `getCurrentId()` still returns its id. On save and reload, current silently resets to root.",
     "Cursor-patch at nav-tree.ts:108 only checks `this.current.id === child.id`, not ancestor-chain intersection.",
     "nav-tree.ts:84–117"),

    (95, "P3", "`syncOpenTabs` refreshes LRU but not `node.lastVisited`",
     "Service worker restarts. `tabManager` recency is refreshed from `tab.lastAccessed`. But the tree's own `node.lastVisited` is stale — UI ordering by 'recent' drifts after every boot until nodes get re-visited.",
     "No `markNodeVisited` pass after `tabManager.touch` loop in syncOpenTabs.",
     "sync-open-tabs.ts:49–53"),

    (96, "P3", "`WINDOW_ID_NONE` check is insufficient for transient hidden windows",
     "Devtools pop-outs, picture-in-picture hosts, macOS workspace transitions fire `onFocusChanged` for hidden-type windows. Extension doesn't filter on `windows.get(id).type === 'normal'`.",
     "Only `WINDOW_ID_NONE` is filtered.",
     "lifecycle.ts:140"),

    (97, "P3", "`setUrlBlocklist` cache key is semantically fragile",
     "Key is `patterns.join('\\n')`. Reordering `['a.com', 'b.com']` → `['b.com', 'a.com']` is semantically identical but recompiles. `['a\\nb']` (pathological) collides with `['a', 'b']`.",
     "String-join hashing has no canonicalization.",
     "url-utils.ts:60–62"),
]

# ---- Build document ---------------------------------------------------------
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Trail — Tree Tracking Bug Audit",
        author="Opus 4.7 parallel audit (11 agents)",
    )
    story = []

    # Cover
    story.append(Paragraph("Trail extension", LABEL))
    story.append(Paragraph("Tree tracking — bug audit", TITLE))
    story.append(Paragraph(
        "97 distinct bugs found by 11 parallel forensic audits "
        "(Opus 4.7). Grouped by user-visible impact, with plain-language "
        "scenarios and severity tags.",
        SUBTITLE,
    ))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#e5e7eb"), spaceAfter=12))

    # Stats
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for b in BUGS:
        if b[0] == "group":
            continue
        counts[b[1]] += 1

    story.append(Paragraph("At a glance", H2))
    stat_data = [[
        Paragraph(f"<b>{counts['P0']}</b>", ParagraphStyle("n", parent=BODY, alignment=TA_CENTER, fontSize=24, leading=28, textColor=colors.HexColor("#dc2626"))),
        Paragraph(f"<b>{counts['P1']}</b>", ParagraphStyle("n", parent=BODY, alignment=TA_CENTER, fontSize=24, leading=28, textColor=colors.HexColor("#ea580c"))),
        Paragraph(f"<b>{counts['P2']}</b>", ParagraphStyle("n", parent=BODY, alignment=TA_CENTER, fontSize=24, leading=28, textColor=colors.HexColor("#ca8a04"))),
        Paragraph(f"<b>{counts['P3']}</b>", ParagraphStyle("n", parent=BODY, alignment=TA_CENTER, fontSize=24, leading=28, textColor=colors.HexColor("#6b7280"))),
    ], [
        Paragraph("P0 · Critical<br/>Data loss, privacy, silent corruption", ParagraphStyle("c", parent=SMALL, alignment=TA_CENTER)),
        Paragraph("P1 · High<br/>Wrong tree structure, incorrect behavior", ParagraphStyle("c", parent=SMALL, alignment=TA_CENTER)),
        Paragraph("P2 · Medium<br/>Behavior drift, UX decay", ParagraphStyle("c", parent=SMALL, alignment=TA_CENTER)),
        Paragraph("P3 · Low<br/>Latent, cosmetic, perf", ParagraphStyle("c", parent=SMALL, alignment=TA_CENTER)),
    ]]
    stat_table = Table(stat_data, colWidths=[4.1*cm]*4)
    stat_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (0,1), colors.HexColor("#fef2f2")),
        ("BACKGROUND", (1,0), (1,1), colors.HexColor("#fff7ed")),
        ("BACKGROUND", (2,0), (2,1), colors.HexColor("#fefce8")),
        ("BACKGROUND", (3,0), (3,1), colors.HexColor("#f3f4f6")),
        ("ROUNDEDCORNERS", [6,6,6,6]),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 16))

    # Root causes
    story.append(Paragraph("The 5 root causes behind everything", H2))
    for i, (t, d) in enumerate([
        ("The tree's parent pointer is one global field",
         "`tree.current` is a single mutable field, written from 15+ call sites (sidepanel clicks, tab activations, window focus, every navigation). Every new node is attached to whatever last wrote to it — not to the tab or link that caused the navigation."),
        ("`openerTabId` is referenced zero times in the entire codebase",
         "Chrome tells us which tab opened which — for free. We throw it away. This is the single highest-impact, lowest-effort fix."),
        ("Mutations happen without a lock",
         "The `treeMutex` exists but only protects bulk persistence. Every handler awaits 2–4 times before mutating and Chrome freely interleaves events. Combined with (1), every concurrent navigation can swap parents."),
        ("URL is the only identity",
         "Duplicate tabs, middle-clicks, and multi-window use all collide into one node because `findByUrl` merges them."),
        ("MV3 service-worker lifecycle is ignored",
         "Debounced 1.5s saves die with the worker. No `onSuspend` flush. Migration flags set before the async work completes."),
    ], start=1):
        story.append(Paragraph(f"<b>{i}.</b> {t}", H3))
        story.append(Paragraph(d, BODY))

    story.append(PageBreak())

    # Bugs by category
    story.append(Paragraph("The bugs, grouped by impact", H1))
    story.append(Paragraph(
        "Each card shows what the user sees, what's happening in the code, "
        "severity, and where to look.",
        SMALL,
    ))
    story.append(Spacer(1, 10))

    for b in BUGS:
        if b[0] == "group":
            _, title, desc = b
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=1,
                                    color=colors.HexColor("#d1d5db")))
            story.append(Paragraph(title, H2))
            story.append(Paragraph(desc, BODY))
            story.append(Spacer(1, 6))
            continue

        num, sev, title, user, tech, loc = b
        # Card
        card_rows = [
            [
                Paragraph(f"<b>#{num}</b>", ParagraphStyle("n", parent=BODY, fontSize=11, textColor=colors.HexColor("#6b7280"))),
                sev_pill(sev),
                Paragraph(f"<b>{title}</b>", ParagraphStyle("t", parent=BODY, fontSize=10.5, leading=14)),
            ],
            [
                "",
                Paragraph("What you see", LABEL),
                Paragraph(user, BODY),
            ],
            [
                "",
                Paragraph("Why", LABEL),
                Paragraph(tech, BODY),
            ],
            [
                "",
                Paragraph("Where", LABEL),
                Paragraph(f"<font face='Courier' size='8.5'>{loc}</font>", BODY),
            ],
        ]
        card = Table(card_rows, colWidths=[0.8*cm, 2.5*cm, 13.3*cm])
        card.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#fafafa")),
            ("LINEBELOW", (0,0), (-1,0), 0.5, colors.HexColor("#e5e7eb")),
            ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
            ("SPAN", (0,1), (0,3)),  # merge number column
        ]))
        story.append(KeepTogether([card, Spacer(1, 8)]))

    story.append(PageBreak())

    # Top fixes
    story.append(Paragraph("The 5 highest-leverage fixes", H1))
    story.append(Paragraph(
        "Most of the 97 bugs collapse into these five architectural changes.",
        SMALL,
    ))
    story.append(Spacer(1, 10))

    fixes = [
        ("Use `tab.openerTabId` as the primary parent signal",
         "Fall back to `tree.current` only when there's no opener. "
         "Kills bugs #1, #2, #4, #5, #6, #7, #23, #73.",
         "Low effort · Huge impact"),
        ("Wrap every mutating handler in `withTreeLock`",
         "Export it from tree-storage.ts. Serializes all mutations behind "
         "the same mutex as persistence. Kills bugs #23, #24, #26, #28, #29, "
         "and the whole concurrency class.",
         "Low effort · Huge impact"),
        ("Consume `details.transitionType` and `documentId`",
         "Chrome already classifies redirects and dedupes SPA events. Use "
         "the browser's own signals instead of our broken `redirectDetector`. "
         "Kills bugs #8, #9, #10, #12.",
         "Medium effort · High impact"),
        ("Stop using the module-global `nodeIdCounter` — switch to uuidv7",
         "`uuidv7` is already imported in tree-storage.ts. Kills bug #15 and "
         "the whole ID-race class.",
         "Medium effort · High impact"),
        ("Encapsulate all mutations behind `NavigationTree` methods",
         "Make `TreeNode.data` externally readonly. Expose "
         "`tree.updateNodeData(id, patch)` that refreshes the search index "
         "and emits change events. Kills bugs #16, #31, #44, #45, #42.",
         "Medium effort · High impact"),
    ]
    for i, (t, d, effort) in enumerate(fixes, start=1):
        story.append(Paragraph(f"<b>{i}. {t}</b>", H3))
        story.append(Paragraph(d, BODY))
        story.append(Paragraph(
            f"<i>{effort}</i>",
            ParagraphStyle("e", parent=SMALL, textColor=colors.HexColor("#059669")),
        ))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#e5e7eb")))
    story.append(Paragraph(
        "Compiled from 11 parallel Opus 4.7 forensic audits covering: race "
        "conditions, navigation handler, tab lifecycle, tree integrity, tab "
        "manager, SPA / redirects, storage, parent inference, sidepanel UI "
        "sync, undo / editor, and settings / recency / blocklist.",
        SMALL,
    ))

    doc.build(story)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
