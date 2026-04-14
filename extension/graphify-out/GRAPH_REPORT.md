# Graph Report - .  (2026-04-13)

## Corpus Check
- Large corpus: 216 files · ~73,478 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 897 nodes · 1110 edges · 118 communities detected
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `TreeStorageService` - 35 edges
2. `NavigationTree` - 30 edges
3. `TabManager` - 27 edges
4. `TreeNode` - 17 edges
5. `withTreeLock()` - 14 edges
6. `CommandManager` - 14 edges
7. `run()` - 11 edges
8. `send()` - 11 edges
9. `makeNode()` - 10 edges
10. `Release Checklist - Trail v1.0.0` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Trail App Icon (SVG, node graph on dark background)` --conceptually_related_to--> `PixiJS 8.x for 2D WebGL Tree Visualization`  [INFERRED]
  public/icons/trail.svg → CSP-RATIONALE.md
- `Inter Font - SIL Open Font License 1.1` --semantically_similar_to--> `Geist Font Build Fix (vendored woff2 fonts)`  [INFERRED] [semantically similar]
  src/assets/fonts/inter/LICENSE.txt → tasks/todo.md
- `CSP Rationale for Chrome Web Store Review` --rationale_for--> `Permissions Check (manifest permissions audit)`  [INFERRED]
  CSP-RATIONALE.md → RELEASE-CHECKLIST.md
- `MV3 Default Strict CSP (no unsafe-eval, no unsafe-inline)` --conceptually_related_to--> `Manifest V3`  [INFERRED]
  CSP-RATIONALE.md → RELEASE-CHECKLIST.md
- `CSP Rationale for Chrome Web Store Review` --references--> `Chrome Web Store Submission`  [EXTRACTED]
  CSP-RATIONALE.md → RELEASE-CHECKLIST.md

## Hyperedges (group relationships)
- **Release Verification Flow (all checklist sections)** — release_checklist_trail_v1, release_checklist_build_verification, release_checklist_permissions_check, release_checklist_offline_mode, release_checklist_empty_states, release_checklist_corrupted_cache, release_checklist_service_worker_restart, release_checklist_cold_profile, release_checklist_dirty_returning, release_checklist_pre_submission [EXTRACTED 1.00]
- **Trail Extension Icon Set (all sizes + SVG source)** — trail_icon_svg, trail_icon_128, trail_icon_48, trail_icon_32, trail_icon_16 [INFERRED 0.95]
- **CSP + PixiJS Resolution (strict CSP, shader polyfill, bootstrap)** — csp_rationale_strict_csp, csp_rationale_pixijs, csp_rationale_shader_polyfill, csp_rationale_pixi_no_eval [EXTRACTED 1.00]

## Communities

### Community 0 - "UI Component Library"
Cohesion: 0.02
Nodes (2): getTabsForNode(), getTabsForNodeMessage()

### Community 1 - "App Shell & Dialogs"
Cohesion: 0.02
Nodes (2): CarouselNext(), useCarousel()

### Community 2 - "Tree Storage & Serialization"
Cohesion: 0.07
Nodes (11): extractSummary(), normalizeIndexEntry(), normalizeLabel(), normalizeLabelSource(), normalizeLegacyRecord(), normalizeMeta(), serializeBlob(), toUint8Array() (+3 more)

### Community 3 - "Context Menus & Popovers"
Cohesion: 0.07
Nodes (6): mapIconToToastKind(), normalizeToastDuration(), showUiToast(), downloadBundle(), handleExport(), sanitizeFilename()

### Community 4 - "Navigation Tree Core"
Cohesion: 0.12
Nodes (1): NavigationTree

### Community 5 - "Tab Manager"
Cohesion: 0.11
Nodes (1): TabManager

### Community 6 - "CSP & Release Process"
Cohesion: 0.08
Nodes (27): CSP Rationale for Chrome Web Store Review, pixi-no-eval-bootstrap.ts (removes unsafe-eval need), PixiJS 8.x for 2D WebGL Tree Visualization, PixiJS pixi.js/unsafe-eval Polyfill (static shader paths), MV3 Default Strict CSP (no unsafe-eval, no unsafe-inline), Grain Background Texture (noise overlay), Build Verification (pnpm build/test/typecheck/lint), Chrome Web Store Submission (+19 more)

### Community 7 - "Tree State Management"
Cohesion: 0.08
Nodes (0): 

### Community 8 - "Backend Configuration"
Cohesion: 0.17
Nodes (19): applyBackendConfig(), buildBackendUrl(), getBackendConfig(), getBackendServerPreset(), hasLocalBaseUrl(), isLocalHostName(), isRecord(), mergeOverrides() (+11 more)

### Community 9 - "Tree Node Model"
Cohesion: 0.16
Nodes (1): TreeNode

### Community 10 - "Command History (Undo/Redo)"
Cohesion: 0.16
Nodes (1): CommandManager

### Community 11 - "Unit Tests"
Cohesion: 0.44
Nodes (14): asNav(), ids(), makeNode(), run(), testAddRemoveChildren(), testClusterEqualScores(), testClusterSortsDescending(), testConvergence() (+6 more)

### Community 12 - "Tooltip Positioning"
Cohesion: 0.18
Nodes (6): clamp(), clampPosition(), computeArrowOffset(), computeBasePosition(), computePreferredPosition(), fitsWithin()

### Community 13 - "Editor Mode Handlers"
Cohesion: 0.22
Nodes (10): broadcastEditorExitToSite(), cancelEditorMode(), cloneSubtree(), doSaveEditorMode(), enterEditorMode(), finalizeEditorExit(), registerCloneInTree(), saveEditorMode() (+2 more)

### Community 14 - "Tree-Tab Handlers"
Cohesion: 0.26
Nodes (10): buildNodeDataFromTab(), buildTreesSnapshot(), closeTabs(), closeTabsForNodes(), collectTabIdsForNodes(), ensureRootForTab(), openTreeAndFocusNode(), registerTabForNode() (+2 more)

### Community 15 - "Runtime Messaging"
Cohesion: 0.24
Nodes (10): createRpcId(), handleSiteMessage(), hasSeenNonce(), isRecord(), isValidUUID(), recordNonce(), sendMessage(), toResponseMessage() (+2 more)

### Community 16 - "Settings Management"
Cohesion: 0.23
Nodes (5): clamp(), clamp01(), mergeDefaults(), normalizeCustomTheme(), SettingsManager

### Community 17 - "Temporary Tab Selection"
Cohesion: 0.32
Nodes (3): focusTab(), getActiveTab(), TemporaryTabSelectionManager

### Community 18 - "Feature Flags"
Cohesion: 0.23
Nodes (7): getAllFlags(), getFlag(), persistFlags(), resetAllFlags(), resolveFlags(), resolveSingleFlag(), setFlagOverride()

### Community 19 - "Public API"
Cohesion: 0.32
Nodes (11): archiveActiveTree(), deleteArchivedTree(), exportTree(), getSettings(), getTrees(), importTrail(), newTree(), openTree() (+3 more)

### Community 20 - "E2E Smoke Tests"
Cohesion: 0.38
Nodes (9): run(), testAuth(), testExportImport(), testFirstInstall(), testGuestMode(), testQuotaEviction(), testSessionExpired(), testSyncFail() (+1 more)

### Community 21 - "Tab LRU Cache"
Cohesion: 0.2
Nodes (1): LruManager

### Community 22 - "Tab-Node Index"
Cohesion: 0.2
Nodes (1): TabIndex

### Community 23 - "Bootstrap & RPC Client"
Cohesion: 0.27
Nodes (4): createRequestId(), fireAndForgetRpcMessage(), sendRpcMessage(), toRpcRequestEnvelope()

### Community 24 - "Theme Application & Store"
Cohesion: 0.27
Nodes (5): applyTheme(), applyThemeTokens(), resolveEffective(), closeUiPopups(), openUiPopup()

### Community 25 - "Drawer Component"
Cohesion: 0.22
Nodes (0): 

### Community 26 - "Browser Tab Utilities"
Cohesion: 0.31
Nodes (5): getCurrentNodeId(), getCurrentTab(), hasRuntimeGetURL(), resolveRuntimeGetURL(), runtimeGetURL()

### Community 27 - "Architecture Boundary Tests"
Cohesion: 0.46
Nodes (7): listFiles(), listSourceFiles(), run(), testEntrypointsStayThin(), testLegacyImportsAreGone(), testPackageRootHygiene(), testProdManifestNoDev()

### Community 28 - "Tab Lifecycle Events"
Cohesion: 0.32
Nodes (4): getActiveTab(), onTabActivated(), onTabRemoved(), onWindowFocusChanged()

### Community 29 - "Tree JSON Mapper"
Cohesion: 0.29
Nodes (2): NavigationTreeMapper, TreeNodeMapper

### Community 30 - "Compact Tree Mapper"
Cohesion: 0.5
Nodes (7): fromCompact(), nodeToTuple(), parseLayout(), toCompact(), tupleToNodeV1(), tupleToNodeV2(), tupleToNodeV3()

### Community 31 - "Recency Scoring & Layout"
Cohesion: 0.38
Nodes (3): balancedCenterOrder(), incrementalCenterReorder(), recencySortChildrenV2()

### Community 32 - "RPC Schema Tests"
Cohesion: 0.33
Nodes (0): 

### Community 33 - "UI Interaction Tests"
Cohesion: 0.6
Nodes (5): run(), testAuthBanner(), testDropdownKeyboard(), testModalEscape(), testSearchNavigation()

### Community 34 - "Redirect Detection"
Cohesion: 0.33
Nodes (1): RedirectDetector

### Community 35 - "URL Utilities"
Cohesion: 0.47
Nodes (4): isNewTabContext(), isNewTabUrl(), isTrackableUrl(), shouldTrackUrl()

### Community 36 - "Pinned Nodes Manager"
Cohesion: 0.33
Nodes (1): PinnedManager

### Community 37 - "Content Script & WXT Config"
Cohesion: 0.33
Nodes (0): 

### Community 38 - "Favicon Resolution"
Cohesion: 0.6
Nodes (5): createGoogleFaviconUrl(), extractDomain(), findBestTrailFavicon(), isPublicFaviconUrl(), traverseNode()

### Community 39 - "Tree Notifications"
Cohesion: 0.6
Nodes (3): getTabStates(), notifyTreeUpdate(), sendTreeNotification()

### Community 40 - "RPC Router"
Cohesion: 0.4
Nodes (0): 

### Community 41 - "Graph Edge Layout"
Cohesion: 0.7
Nodes (4): assignEdgeHandles(), computeLayout(), getSpacing(), nearestSide()

### Community 42 - "ELK Graph Layout"
Cohesion: 0.6
Nodes (3): getLayoutOptions(), treeToElkGraph(), walkNode()

### Community 43 - "Radial Layout"
Cohesion: 0.6
Nodes (3): computeRadialPositions(), placeChildren(), radiusAtDepth()

### Community 44 - "URL Key Normalization"
Cohesion: 0.6
Nodes (3): buildQueryKey(), createUrlKey(), stripTrailingSlash()

### Community 45 - "RPC Contracts"
Cohesion: 0.4
Nodes (0): 

### Community 46 - "Message Router"
Cohesion: 0.67
Nodes (2): createMessageRouter(), initMessaging()

### Community 47 - "Tab Restoration"
Cohesion: 0.5
Nodes (0): 

### Community 48 - "Trail Graph Component"
Cohesion: 0.5
Nodes (0): 

### Community 49 - "Logger"
Cohesion: 0.67
Nodes (2): domainOnly(), redactSensitive()

### Community 50 - "Formatting Utilities"
Cohesion: 0.5
Nodes (0): 

### Community 51 - "Graph Layout Tests"
Cohesion: 0.67
Nodes (0): 

### Community 52 - "Tab Audio/Title Sync"
Cohesion: 0.67
Nodes (0): 

### Community 53 - "Runtime Message Sending"
Cohesion: 0.67
Nodes (0): 

### Community 54 - "Tree-Graph Transforms"
Cohesion: 0.67
Nodes (0): 

### Community 55 - "ID Generation"
Cohesion: 0.67
Nodes (0): 

### Community 56 - "Node Data Updates"
Cohesion: 0.67
Nodes (0): 

### Community 57 - "Sidebar Navigation Keys"
Cohesion: 0.67
Nodes (0): 

### Community 58 - "Tree Encode/Decode"
Cohesion: 0.67
Nodes (0): 

### Community 59 - "Performance Metrics"
Cohesion: 0.67
Nodes (0): 

### Community 60 - "Background Messaging"
Cohesion: 1.0
Nodes (2): fireAndForget(), sendMessage()

### Community 61 - "Range Utilities"
Cohesion: 0.67
Nodes (0): 

### Community 62 - "Overlay Effects"
Cohesion: 1.0
Nodes (2): nextOverlayId(), useOverlayEffects()

### Community 63 - "Keyboard Shortcuts"
Cohesion: 0.67
Nodes (0): 

### Community 64 - "Bootstrap Hook"
Cohesion: 0.67
Nodes (0): 

### Community 65 - "Font Management"
Cohesion: 0.67
Nodes (3): Inter Font - SIL Open Font License 1.1, Geist Font Build Fix (vendored woff2 fonts), Root Cause: fontsource-variable/geist URLs unresolved in WXT/Tailwind pipeline

### Community 66 - "Open Tab Sync"
Cohesion: 1.0
Nodes (0): 

### Community 67 - "WebNavigation Listener"
Cohesion: 1.0
Nodes (0): 

### Community 68 - "Navigation Handler"
Cohesion: 1.0
Nodes (0): 

### Community 69 - "New Tab Handler"
Cohesion: 1.0
Nodes (0): 

### Community 70 - "Tree Node Factory"
Cohesion: 1.0
Nodes (0): 

### Community 71 - "Tab URL Resolution"
Cohesion: 1.0
Nodes (0): 

### Community 72 - "Node Recency Tracking"
Cohesion: 1.0
Nodes (0): 

### Community 73 - "UI Notifications"
Cohesion: 1.0
Nodes (0): 

### Community 74 - "Undo Apply"
Cohesion: 1.0
Nodes (0): 

### Community 75 - "Panel Lifecycle"
Cohesion: 1.0
Nodes (0): 

### Community 76 - "Content Handler"
Cohesion: 1.0
Nodes (0): 

### Community 77 - "Auth Check"
Cohesion: 1.0
Nodes (0): 

### Community 78 - "Tab Unregister"
Cohesion: 1.0
Nodes (0): 

### Community 79 - "Focus Tab Handler"
Cohesion: 1.0
Nodes (0): 

### Community 80 - "Tree Loader"
Cohesion: 1.0
Nodes (0): 

### Community 81 - "Aspect Ratio"
Cohesion: 1.0
Nodes (0): 

### Community 82 - "Direction Provider"
Cohesion: 1.0
Nodes (0): 

### Community 83 - "Collapsible Component"
Cohesion: 1.0
Nodes (0): 

### Community 84 - "Graph Layout Hook"
Cohesion: 1.0
Nodes (0): 

### Community 85 - "Archive Storage Keys"
Cohesion: 1.0
Nodes (0): 

### Community 86 - "Icon Generation"
Cohesion: 1.0
Nodes (0): 

### Community 87 - "Platform Detection"
Cohesion: 1.0
Nodes (0): 

### Community 88 - "Favicon URL"
Cohesion: 1.0
Nodes (0): 

### Community 89 - "UUID Generation"
Cohesion: 1.0
Nodes (0): 

### Community 90 - "Theme Definitions"
Cohesion: 1.0
Nodes (0): 

### Community 91 - "Trees Hook"
Cohesion: 1.0
Nodes (0): 

### Community 92 - "Settings Hook"
Cohesion: 1.0
Nodes (0): 

### Community 93 - "Tree Deletion"
Cohesion: 1.0
Nodes (0): 

### Community 94 - "Icon Component"
Cohesion: 1.0
Nodes (0): 

### Community 95 - "Runtime Messages Hook"
Cohesion: 1.0
Nodes (0): 

### Community 96 - "Early Theme Application"
Cohesion: 1.0
Nodes (0): 

### Community 97 - "Service Worker Entry"
Cohesion: 1.0
Nodes (0): 

### Community 98 - "History API"
Cohesion: 1.0
Nodes (0): 

### Community 99 - "Flags Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 100 - "Pin Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 101 - "Settings Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 102 - "Type Definitions"
Cohesion: 1.0
Nodes (0): 

### Community 103 - "Module Index"
Cohesion: 1.0
Nodes (0): 

### Community 104 - "Data Model"
Cohesion: 1.0
Nodes (0): 

### Community 105 - "Content Script Entry"
Cohesion: 1.0
Nodes (0): 

### Community 106 - "Collection Iteration"
Cohesion: 1.0
Nodes (0): 

### Community 107 - "Export Utilities"
Cohesion: 1.0
Nodes (0): 

### Community 108 - "Theme Types"
Cohesion: 1.0
Nodes (0): 

### Community 109 - "Compact Tree"
Cohesion: 1.0
Nodes (0): 

### Community 110 - "Default Values"
Cohesion: 1.0
Nodes (0): 

### Community 111 - "Debounce Utility"
Cohesion: 1.0
Nodes (0): 

### Community 112 - "Assertion Utility"
Cohesion: 1.0
Nodes (0): 

### Community 113 - "Logging Entry"
Cohesion: 1.0
Nodes (0): 

### Community 114 - "Site Messages"
Cohesion: 1.0
Nodes (0): 

### Community 115 - "Render Entry"
Cohesion: 1.0
Nodes (0): 

### Community 116 - "Schema Definitions"
Cohesion: 1.0
Nodes (0): 

### Community 117 - "Claude Skills Index"
Cohesion: 1.0
Nodes (1): CLAUDE.md Skills Index (autoskills summary)

## Knowledge Gaps
- **17 isolated node(s):** `Offline Mode Testing`, `Empty States Testing`, `Corrupted Cache Recovery Testing`, `Service Worker Restart Testing`, `Extension Entrypoints (sidepanel, newtab, background, account, fullview, offscreen-graph, spotlight-graph, content-scripts)` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Open Tab Sync`** (2 nodes): `sync-open-tabs.ts`, `syncOpenTabs()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `WebNavigation Listener`** (2 nodes): `webnavigation.ts`, `initWebNavigation()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Navigation Handler`** (2 nodes): `navigation-handler.ts`, `handleNavigation()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `New Tab Handler`** (2 nodes): `new-tab.ts`, `handleNewTabTab()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tree Node Factory`** (2 nodes): `tree-utils.ts`, `createNode()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tab URL Resolution`** (2 nodes): `tab-utils.ts`, `resolveTabUrl()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Node Recency Tracking`** (2 nodes): `node-recency.ts`, `markNodeVisited()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Notifications`** (2 nodes): `ui-notifications.ts`, `notifyUi()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Undo Apply`** (2 nodes): `undo-handlers.ts`, `applyTree()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Panel Lifecycle`** (2 nodes): `panel-handlers.ts`, `isSidepanelAlive()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Content Handler`** (2 nodes): `content-handlers.ts`, `getSenderTabId()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Auth Check`** (2 nodes): `site-message-handlers.ts`, `isAuthenticated()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tab Unregister`** (2 nodes): `tab-handlers.ts`, `unregisterTabForNode()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Focus Tab Handler`** (2 nodes): `navigation-handlers.ts`, `focusTab()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tree Loader`** (2 nodes): `tree-loader.ts`, `loadTree()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Aspect Ratio`** (2 nodes): `aspect-ratio.tsx`, `AspectRatio()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Direction Provider`** (2 nodes): `direction.tsx`, `DirectionProvider()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Collapsible Component`** (2 nodes): `collapsible.tsx`, `Collapsible()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graph Layout Hook`** (2 nodes): `useGraphLayout.ts`, `useGraphLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Archive Storage Keys`** (2 nodes): `storage-items.ts`, `archiveBlobKey()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Icon Generation`** (2 nodes): `generate-icons.ts`, `generateIcons()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Platform Detection`** (2 nodes): `platform.ts`, `isMac()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Favicon URL`** (2 nodes): `favicon.ts`, `getFaviconUrl()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UUID Generation`** (2 nodes): `uuid.ts`, `uuidv7()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Theme Definitions`** (2 nodes): `themes.ts`, `getThemes()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Trees Hook`** (2 nodes): `useTrees.ts`, `useTrees()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Settings Hook`** (2 nodes): `useSettings.ts`, `useSettings()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tree Deletion`** (2 nodes): `delete-tree.ts`, `getIncludedRootId()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Icon Component`** (2 nodes): `Icon.tsx`, `icon()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Runtime Messages Hook`** (2 nodes): `useRuntimeMessages.ts`, `useRuntimeMessages()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Early Theme Application`** (1 nodes): `apply-theme-early.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Service Worker Entry`** (1 nodes): `service-worker.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `History API`** (1 nodes): `history-api.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Flags Handlers`** (1 nodes): `flags-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pin Handlers`** (1 nodes): `pin-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Settings Handlers`** (1 nodes): `settings-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Type Definitions`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module Index`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Data Model`** (1 nodes): `model.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Content Script Entry`** (1 nodes): `content-script.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Collection Iteration`** (1 nodes): `foreach.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Export Utilities`** (1 nodes): `export.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Theme Types`** (1 nodes): `theme.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Compact Tree`** (1 nodes): `compact-tree.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Default Values`** (1 nodes): `defaults.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Debounce Utility`** (1 nodes): `debounce.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Assertion Utility`** (1 nodes): `assert.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Logging Entry`** (1 nodes): `log.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Site Messages`** (1 nodes): `site-messages.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Render Entry`** (1 nodes): `render.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Schema Definitions`** (1 nodes): `schema.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Claude Skills Index`** (1 nodes): `CLAUDE.md Skills Index (autoskills summary)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Offline Mode Testing`, `Empty States Testing`, `Corrupted Cache Recovery Testing` to the rest of the system?**
  _17 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `UI Component Library` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._
- **Should `App Shell & Dialogs` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._
- **Should `Tree Storage & Serialization` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Context Menus & Popovers` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Navigation Tree Core` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `Tab Manager` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._