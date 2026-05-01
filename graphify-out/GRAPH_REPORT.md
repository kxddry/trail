# Graph Report - extension/src + apps/account  (2026-04-10)

## Corpus Check
- 452 files · ~184,233 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1890 nodes · 2722 edges · 207 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `GraphPixiRenderer` - 47 edges
2. `MiniSearch` - 44 edges
3. `TreeStorageService` - 35 edges
4. `NavigationTree` - 30 edges
5. `TabManager` - 27 edges
6. `SpotlightService` - 20 edges
7. `SearchableMap` - 19 edges
8. `TreeNode` - 17 edges
9. `GET()` - 15 edges
10. `POST()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Inter Typeface` --conceptually_related_to--> `Trail Brand Identity`  [INFERRED]
  extension/src/assets/fonts/inter/LICENSE.txt → apps/account/public/brand/trail-fork-light.svg
- `Trail Logo - Fork Light Variant` --semantically_similar_to--> `Trail Logo - Fork Dark Variant`  [INFERRED] [semantically similar]
  apps/account/public/brand/trail-fork-light.svg → apps/account/public/brand/trail-fork-dark.svg
- `Trail Logo - Fork Light Variant` --semantically_similar_to--> `Trail Logo - Monochrome Mark`  [INFERRED] [semantically similar]
  apps/account/public/brand/trail-fork-light.svg → apps/account/public/brand/trail-mark.svg
- `GET()` --calls--> `base64Url()`  [EXTRACTED]
  apps/account/app/api/v1/onboarding/route.ts → apps/account/app/auth/callback/route.ts
- `GET()` --calls--> `resolveUser()`  [EXTRACTED]
  apps/account/app/api/v1/onboarding/route.ts → apps/account/app/api/v1/trails/route.ts

## Hyperedges (group relationships)
- **Trail Logo Theme Variants (Light, Dark, Mono)** — trail_fork_light, trail_fork_dark, trail_mark, graph_network_motif [INFERRED 0.90]
- **Trail Brand Asset System** — trail_brand_identity, trail_fork_light, trail_fork_dark, trail_mark, inter_font [INFERRED 0.70]

## Communities

### Community 0 - "UI Component Library"
Cohesion: 0.01
Nodes (4): CarouselNext(), useCarousel(), getTabsForNode(), getTabsForNodeMessage()

### Community 1 - "App Shell & Auth"
Cohesion: 0.02
Nodes (28): typed(), verifyExtensionToken(), getCallbackUrl(), handleGoogleSignIn(), handleMagicLink(), buildOnboardingState(), finish(), handleNext() (+20 more)

### Community 2 - "MiniSearch Engine"
Cohesion: 0.06
Nodes (20): assignUniqueTerm(), calcBM25Score(), cleanup(), createPath(), fuzzySearch(), getOwnProperty(), last(), last$1() (+12 more)

### Community 3 - "Graph PixiJS Renderer"
Cohesion: 0.05
Nodes (26): buildLucideSvg(), cacheFaviconTexture(), clamp8(), colorToHex(), computeZIndex(), desaturateColor(), drawDashedArc(), drawDashedLine() (+18 more)

### Community 4 - "Account Tests"
Cohesion: 0.04
Nodes (54): normalizeInternalPath(), resolveSafeNextPath(), corsHeaders(), optionsResponse(), isJsonValue(), isPlainObject(), sig(), sortObject() (+46 more)

### Community 5 - "Account Snapshot & Env"
Cohesion: 0.05
Nodes (42): buildAccountSnapshot(), toAccountUser(), billingUrl(), link(), assertNowPaymentsConfig(), assertPaidPlanId(), billingUrl(), createFallbackPortalLink() (+34 more)

### Community 6 - "Tree Storage Layer"
Cohesion: 0.07
Nodes (11): extractSummary(), normalizeIndexEntry(), normalizeLabel(), normalizeLabelSource(), normalizeLegacyRecord(), normalizeMeta(), serializeBlob(), toUint8Array() (+3 more)

### Community 7 - "Spotlight Command Palette"
Cohesion: 0.09
Nodes (24): actionTargetKey(), appendSectionIfAny(), buildCommandActionsForCurrentNode(), buildContextualActions(), buildExternalActions(), buildGlobalActions(), buildScopedTreeActions(), buildTreeWhyChips() (+16 more)

### Community 8 - "Extension Bootstrap"
Cohesion: 0.06
Nodes (25): getCurrentNodeId(), getCurrentTab(), createRequestId(), fireAndForgetRpcMessage(), sendRpcMessage(), toRpcRequestEnvelope(), bootstrap(), computeAndCache() (+17 more)

### Community 9 - "Dialog & Dropdown UI"
Cohesion: 0.05
Nodes (9): clamp(), clampPosition(), computeArrowOffset(), computeBasePosition(), computePreferredPosition(), fitsWithin(), downloadBundle(), handleExport() (+1 more)

### Community 10 - "Navigation Tree"
Cohesion: 0.12
Nodes (1): NavigationTree

### Community 11 - "Tab Manager"
Cohesion: 0.11
Nodes (1): TabManager

### Community 12 - "Tree CRUD Operations"
Cohesion: 0.08
Nodes (0): 

### Community 13 - "Spotlight Live Index"
Cohesion: 0.16
Nodes (12): buildHaystack(), buildTreeNodeRecencyMap(), collectPaths(), computeGraphBoosts(), computeTreeRelation(), createNodeDoc(), createPreviewData(), createTreeDoc() (+4 more)

### Community 14 - "Auth Orchestrator"
Cohesion: 0.18
Nodes (7): AuthOrchestrator, exchangeAuthorizationCode(), isAccessTokenExpired(), loadAuth(), logAuth(), refreshWithToken(), saveAuth()

### Community 15 - "Backend Config"
Cohesion: 0.17
Nodes (19): applyBackendConfig(), buildBackendUrl(), getBackendConfig(), getBackendServerPreset(), hasLocalBaseUrl(), isLocalHostName(), isRecord(), mergeOverrides() (+11 more)

### Community 16 - "Tree Node Model"
Cohesion: 0.16
Nodes (1): TreeNode

### Community 17 - "Graph Canvas Interaction"
Cohesion: 0.16
Nodes (9): getPointerNodeId(), getPointerTarget(), handleBackgroundClick(), handlePointerCancel(), handlePointerDown(), handlePointerMove(), handlePointerUp(), isGraphUiTarget() (+1 more)

### Community 18 - "Command Undo/Redo"
Cohesion: 0.16
Nodes (1): CommandManager

### Community 19 - "OAuth Token Flow"
Cohesion: 0.29
Nodes (17): base64Url(), buildTokenSet(), createCode(), createOAuthAuthorizationCode(), createRefreshToken(), exchangeOAuthAuthorizationCode(), issueAccessToken(), normalizeClientId() (+9 more)

### Community 20 - "Extension Messaging"
Cohesion: 0.19
Nodes (13): buildMessage(), cancelEditorMode(), createRequestId(), ensurePanelOpen(), enterEditorMode(), exitEditorMode(), notifyAuthRevoked(), openTrailPanel() (+5 more)

### Community 21 - "Sync Engine"
Cohesion: 0.25
Nodes (5): getRecordUpdatedAt(), metaToSummary(), normalizeLabelSource(), SyncEngine, toIso()

### Community 22 - "Account Client API"
Cohesion: 0.2
Nodes (10): completeOnboarding(), createBillingPortalLink(), createDefaultClient(), getAccountSnapshot(), getActiveAccountClient(), getBillingStatus(), getProfile(), getSubscription() (+2 more)

### Community 23 - "Tree Event Handlers"
Cohesion: 0.24
Nodes (10): buildNodeDataFromTab(), buildTreesSnapshot(), closeTabs(), closeTabsForNodes(), collectTabIdsForNodes(), ensureRootForTab(), openTreeAndFocusNode(), registerTabForNode() (+2 more)

### Community 24 - "Editor Mode Handlers"
Cohesion: 0.22
Nodes (10): broadcastEditorExitToSite(), cancelEditorMode(), cloneSubtree(), doSaveEditorMode(), enterEditorMode(), finalizeEditorExit(), registerCloneInTree(), saveEditorMode() (+2 more)

### Community 25 - "Editor Sync"
Cohesion: 0.29
Nodes (12): broadcastStatus(), clearTimer(), editorSyncFlush(), editorSyncMarkDirty(), editorSyncRetry(), editorSyncStart(), editorSyncStop(), flushSyncWithRetries() (+4 more)

### Community 26 - "Runtime Message Bus"
Cohesion: 0.24
Nodes (10): createRpcId(), handleSiteMessage(), hasSeenNonce(), isRecord(), isValidUUID(), recordNonce(), sendMessage(), toResponseMessage() (+2 more)

### Community 27 - "Settings Management"
Cohesion: 0.23
Nodes (5): clamp(), clamp01(), mergeDefaults(), normalizeCustomTheme(), SettingsManager

### Community 28 - "Spatial Index"
Cohesion: 0.26
Nodes (1): SpatialIndex

### Community 29 - "Message Router"
Cohesion: 0.2
Nodes (4): createMessageRouter(), initMessaging(), matchRoute(), useRoute()

### Community 30 - "Temporary Tab Selection"
Cohesion: 0.32
Nodes (3): focusTab(), getActiveTab(), TemporaryTabSelectionManager

### Community 31 - "Feature Flags"
Cohesion: 0.23
Nodes (7): getAllFlags(), getFlag(), persistFlags(), resetAllFlags(), resolveFlags(), resolveSingleFlag(), setFlagOverride()

### Community 32 - "Usage Statistics"
Cohesion: 0.32
Nodes (7): emptySpotlightUsageStats(), getSelectionTokenAffinityBoost(), normalizeUsageQueryTokens(), pruneSpotlightUsageStats(), recordSpotlightSelection(), sanitizeSpotlightUsageStats(), sanitizeTokenCounts()

### Community 33 - "Mock Test Fixtures"
Cohesion: 0.24
Nodes (7): addDays(), buildMockOnboarding(), buildPortalLink(), buildSubscription(), nowIso(), snapshot(), updateBilling()

### Community 34 - "New Tab Page"
Cohesion: 0.23
Nodes (7): getGreeting(), getTarget(), getTime(), onMove(), startLoop(), tick(), update()

### Community 35 - "Spotlight Usage Stats"
Cohesion: 0.29
Nodes (1): SpotlightUsageStatsService

### Community 36 - "Account Keeper"
Cohesion: 0.31
Nodes (6): AccountKeeper, buildGuestSnapshot(), fetchJson(), fetchSnapshot(), loadAuth(), saveToStorage()

### Community 37 - "Graph Profiler"
Cohesion: 0.24
Nodes (2): GraphProfiler, profileSync()

### Community 38 - "Tab LRU Cache"
Cohesion: 0.2
Nodes (1): LruManager

### Community 39 - "Tab Index"
Cohesion: 0.2
Nodes (1): TabIndex

### Community 40 - "Snapshot Cache"
Cohesion: 0.36
Nodes (7): getSessionStorage(), invalidateLayoutCache(), loadCachedSnapshot(), loadCachedSnapshotWithAge(), readLayoutCache(), storageKey(), writeLayoutCache()

### Community 41 - "Theme Application"
Cohesion: 0.27
Nodes (5): applyTheme(), applyThemeTokens(), resolveEffective(), closeUiPopups(), openUiPopup()

### Community 42 - "Remote Account Client"
Cohesion: 0.31
Nodes (6): buildHttpError(), buildNetworkError(), getAccessToken(), loadAuth(), normalizeErrorCode(), requestJson()

### Community 43 - "Spotlight Action Handlers"
Cohesion: 0.22
Nodes (0): 

### Community 44 - "Spotlight IPC"
Cohesion: 0.22
Nodes (0): 

### Community 45 - "Layout Calculator"
Cohesion: 0.36
Nodes (5): buildTidyTree(), calculateLayout(), computeSubtreeSpans(), computeTidyBreadths(), createTidyTree()

### Community 46 - "Tab Lifecycle"
Cohesion: 0.32
Nodes (4): getActiveTab(), onTabActivated(), onTabRemoved(), onWindowFocusChanged()

### Community 47 - "Sync API Client"
Cohesion: 0.36
Nodes (5): apiRequest(), getAccessToken(), isAuthenticated(), loadAuthSession(), SyncApiError

### Community 48 - "Search Scoring"
Cohesion: 0.5
Nodes (7): clampScore(), computeRecencyScore(), hasDomainBoost(), hasUrlBoost(), normalizeTextScore(), normalizeUrl(), scoreSpotlightCandidate()

### Community 49 - "Tree Mapper"
Cohesion: 0.29
Nodes (2): NavigationTreeMapper, TreeNodeMapper

### Community 50 - "Compact Tree Mapper"
Cohesion: 0.5
Nodes (7): fromCompact(), nodeToTuple(), parseLayout(), toCompact(), tupleToNodeV1(), tupleToNodeV2(), tupleToNodeV3()

### Community 51 - "Brand Assets"
Cohesion: 0.39
Nodes (8): Graph/Network Visual Motif (7 nodes, 5 edges), Inter Typeface, Inter Font License (SIL OFL 1.1), SIL Open Font License v1.1, Trail Brand Identity, Trail Logo - Fork Dark Variant, Trail Logo - Fork Light Variant, Trail Logo - Monochrome Mark

### Community 52 - "Thumbnail Cache"
Cohesion: 0.33
Nodes (1): ThumbnailCache

### Community 53 - "LRU Map"
Cohesion: 0.33
Nodes (1): LRUMap

### Community 54 - "Node Recency Scoring"
Cohesion: 0.38
Nodes (3): balancedCenterOrder(), incrementalCenterReorder(), recencySortChildrenV2()

### Community 55 - "Redirect Detection"
Cohesion: 0.33
Nodes (1): RedirectDetector

### Community 56 - "URL Utilities"
Cohesion: 0.47
Nodes (4): isNewTabContext(), isNewTabUrl(), isTrackableUrl(), shouldTrackUrl()

### Community 57 - "Pinned Manager"
Cohesion: 0.33
Nodes (1): PinnedManager

### Community 58 - "Storage Quota Manager"
Cohesion: 0.53
Nodes (4): isQuotaError(), quotaAwareSet(), withEvictionLock(), writeBulk()

### Community 59 - "Auth Policy Keeper"
Cohesion: 0.4
Nodes (1): AuthPolicyKeeper

### Community 60 - "Spotlight Search Hook"
Cohesion: 0.47
Nodes (3): isConnectionError(), isRecoverableError(), isSessionExpired()

### Community 61 - "Query DSL Parser"
Cohesion: 0.53
Nodes (4): parseFieldToken(), parseSpotlightQuery(), splitRawTokens(), tokenizeSpotlightQuery()

### Community 62 - "Animation Utilities"
Cohesion: 0.53
Nodes (3): clamp(), easeOutCubic(), getAnimationProgress()

### Community 63 - "Quality Policy"
Cohesion: 0.53
Nodes (4): percentile(), qualityPolicyFromState(), toResult(), updateQualityPolicy()

### Community 64 - "Tree Favicon Resolver"
Cohesion: 0.6
Nodes (5): createGoogleFaviconUrl(), extractDomain(), findBestTrailFavicon(), isPublicFaviconUrl(), traverseNode()

### Community 65 - "Entitlements & Tiers"
Cohesion: 0.6
Nodes (5): getFeatureAccess(), getFeatureMinTier(), hasTierAccess(), resolveCurrentTier(), tierRank()

### Community 66 - "Account Profile"
Cohesion: 0.47
Nodes (3): buildDisplayName(), normalizeSpacing(), splitDisplayName()

### Community 67 - "Tree Notifications"
Cohesion: 0.6
Nodes (3): getTabStates(), notifyTreeUpdate(), sendTreeNotification()

### Community 68 - "RPC Router"
Cohesion: 0.4
Nodes (0): 

### Community 69 - "Spotlight Preview Hook"
Cohesion: 0.4
Nodes (0): 

### Community 70 - "Spotlight Hint Row"
Cohesion: 0.4
Nodes (0): 

### Community 71 - "Spotlight Actions Hook"
Cohesion: 0.5
Nodes (2): downloadBundle(), sanitizeFilename()

### Community 72 - "View Invalidation"
Cohesion: 0.7
Nodes (4): decideViewInvalidation(), expandWorldRect(), rectContainsRect(), worldRectFromView()

### Community 73 - "Graph Path Utilities"
Cohesion: 0.4
Nodes (0): 

### Community 74 - "URL Key Normalization"
Cohesion: 0.6
Nodes (3): buildQueryKey(), createUrlKey(), stripTrailingSlash()

### Community 75 - "RPC Contracts"
Cohesion: 0.4
Nodes (0): 

### Community 76 - "Local Trails Hook"
Cohesion: 0.6
Nodes (3): fetchTrails(), mergeTrails(), toTrailSummary()

### Community 77 - "Search Suggestions"
Cohesion: 0.83
Nodes (3): fetchSearchSuggestions(), getCached(), pruneStaleEntries()

### Community 78 - "Tab Restoration"
Cohesion: 0.5
Nodes (0): 

### Community 79 - "Offscreen Graph Manager"
Cohesion: 0.83
Nodes (3): ensureOffscreenDocument(), hasOffscreenDocument(), initOffscreenGraphManager()

### Community 80 - "Tree Loader"
Cohesion: 0.83
Nodes (3): fetchFromCloud(), loadTree(), remoteToTreeRecord()

### Community 81 - "Spotlight Action Menu"
Cohesion: 0.67
Nodes (2): buildClientContextActions(), toActionResult()

### Community 82 - "Restore Policy"
Cohesion: 0.5
Nodes (0): 

### Community 83 - "Selection Utilities"
Cohesion: 0.5
Nodes (0): 

### Community 84 - "Logger"
Cohesion: 0.67
Nodes (2): domainOnly(), redactSensitive()

### Community 85 - "Format Utilities"
Cohesion: 0.5
Nodes (0): 

### Community 86 - "Bookmarks Hook"
Cohesion: 0.67
Nodes (2): hostnameOf(), mapNode()

### Community 87 - "Spotlight Command Init"
Cohesion: 0.67
Nodes (0): 

### Community 88 - "Tab Sync"
Cohesion: 0.67
Nodes (0): 

### Community 89 - "Send Message Helper"
Cohesion: 0.67
Nodes (0): 

### Community 90 - "Dirty Tracker"
Cohesion: 0.67
Nodes (0): 

### Community 91 - "Spotlight Row Actions"
Cohesion: 1.0
Nodes (2): fire(), stop()

### Community 92 - "Spotlight Row Icon"
Cohesion: 0.67
Nodes (0): 

### Community 93 - "Layout Types"
Cohesion: 0.67
Nodes (0): 

### Community 94 - "Spotlight Batch Bar"
Cohesion: 1.0
Nodes (2): buildBatchActions(), SpotlightBatchBar()

### Community 95 - "Spotlight Theme Hook"
Cohesion: 0.67
Nodes (0): 

### Community 96 - "Spotlight Resize Hook"
Cohesion: 0.67
Nodes (0): 

### Community 97 - "External Query Normalize"
Cohesion: 0.67
Nodes (0): 

### Community 98 - "Collapse Utilities"
Cohesion: 0.67
Nodes (0): 

### Community 99 - "Layout Options"
Cohesion: 1.0
Nodes (2): clamp(), deriveLayoutOptions()

### Community 100 - "Graph Snapshot Diff"
Cohesion: 0.67
Nodes (0): 

### Community 101 - "Graph Theme"
Cohesion: 1.0
Nodes (2): parseColor(), readGraphTheme()

### Community 102 - "Graph Area"
Cohesion: 0.67
Nodes (0): 

### Community 103 - "Graph Canvas Utilities"
Cohesion: 0.67
Nodes (0): 

### Community 104 - "Grid Transform"
Cohesion: 1.0
Nodes (2): computeGraphGridTransform(), normalizeModulo()

### Community 105 - "Graph Layout Compute"
Cohesion: 0.67
Nodes (0): 

### Community 106 - "ID Utilities"
Cohesion: 0.67
Nodes (0): 

### Community 107 - "Node Data Update"
Cohesion: 0.67
Nodes (0): 

### Community 108 - "Tree Codec"
Cohesion: 0.67
Nodes (0): 

### Community 109 - "Perf Metrics"
Cohesion: 0.67
Nodes (0): 

### Community 110 - "Background Messaging"
Cohesion: 1.0
Nodes (2): fireAndForget(), sendMessage()

### Community 111 - "Range Utilities"
Cohesion: 0.67
Nodes (0): 

### Community 112 - "Overlay Effects"
Cohesion: 1.0
Nodes (2): nextOverlayId(), useOverlayEffects()

### Community 113 - "Keyboard Shortcuts"
Cohesion: 0.67
Nodes (0): 

### Community 114 - "Bootstrap Hook"
Cohesion: 0.67
Nodes (0): 

### Community 115 - "Hub Sidebar"
Cohesion: 0.67
Nodes (0): 

### Community 116 - "Import Trail Hook"
Cohesion: 0.67
Nodes (0): 

### Community 117 - "Trail Detail Hook"
Cohesion: 0.67
Nodes (0): 

### Community 118 - "Sync Open Tabs"
Cohesion: 1.0
Nodes (0): 

### Community 119 - "Web Navigation"
Cohesion: 1.0
Nodes (0): 

### Community 120 - "Navigation Handler"
Cohesion: 1.0
Nodes (0): 

### Community 121 - "New Tab Handler"
Cohesion: 1.0
Nodes (0): 

### Community 122 - "Tree Node Utilities"
Cohesion: 1.0
Nodes (0): 

### Community 123 - "Tab URL Utilities"
Cohesion: 1.0
Nodes (0): 

### Community 124 - "Node Recency Tracker"
Cohesion: 1.0
Nodes (0): 

### Community 125 - "UI Notifications"
Cohesion: 1.0
Nodes (0): 

### Community 126 - "Undo Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 127 - "Panel Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 128 - "Content Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 129 - "Site Auth Handler"
Cohesion: 1.0
Nodes (0): 

### Community 130 - "Tab Node Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 131 - "Navigation Focus"
Cohesion: 1.0
Nodes (0): 

### Community 132 - "Data Migration"
Cohesion: 1.0
Nodes (0): 

### Community 133 - "Aspect Ratio"
Cohesion: 1.0
Nodes (0): 

### Community 134 - "Direction Provider"
Cohesion: 1.0
Nodes (0): 

### Community 135 - "Collapsible"
Cohesion: 1.0
Nodes (0): 

### Community 136 - "Spotlight Graph Frame"
Cohesion: 1.0
Nodes (0): 

### Community 137 - "Drilldown Memory"
Cohesion: 1.0
Nodes (0): 

### Community 138 - "Text Highlight"
Cohesion: 1.0
Nodes (0): 

### Community 139 - "Spotlight Quick Look"
Cohesion: 1.0
Nodes (0): 

### Community 140 - "Spotlight Keyboard"
Cohesion: 1.0
Nodes (0): 

### Community 141 - "Platform Detection"
Cohesion: 1.0
Nodes (0): 

### Community 142 - "Spotlight Help"
Cohesion: 1.0
Nodes (0): 

### Community 143 - "Spotlight Results"
Cohesion: 1.0
Nodes (0): 

### Community 144 - "Selection Indicator"
Cohesion: 1.0
Nodes (0): 

### Community 145 - "Spotlight App"
Cohesion: 1.0
Nodes (0): 

### Community 146 - "Vitest Config"
Cohesion: 1.0
Nodes (0): 

### Community 147 - "Graph Animation Hook"
Cohesion: 1.0
Nodes (0): 

### Community 148 - "Graph Selection Hook"
Cohesion: 1.0
Nodes (0): 

### Community 149 - "Graph View Hook"
Cohesion: 1.0
Nodes (0): 

### Community 150 - "Layout Send Hook"
Cohesion: 1.0
Nodes (0): 

### Community 151 - "Compute Layout"
Cohesion: 1.0
Nodes (0): 

### Community 152 - "Storage Items"
Cohesion: 1.0
Nodes (0): 

### Community 153 - "Icon Generation"
Cohesion: 1.0
Nodes (0): 

### Community 154 - "Favicon URL"
Cohesion: 1.0
Nodes (0): 

### Community 155 - "UUID Generator"
Cohesion: 1.0
Nodes (0): 

### Community 156 - "Tree Deletion"
Cohesion: 1.0
Nodes (0): 

### Community 157 - "Theme Definitions"
Cohesion: 1.0
Nodes (0): 

### Community 158 - "Icon Component"
Cohesion: 1.0
Nodes (0): 

### Community 159 - "Auth Portal Flow"
Cohesion: 1.0
Nodes (0): 

### Community 160 - "Account Hook"
Cohesion: 1.0
Nodes (0): 

### Community 161 - "Search Hook"
Cohesion: 1.0
Nodes (0): 

### Community 162 - "Runtime Messages Hook"
Cohesion: 1.0
Nodes (0): 

### Community 163 - "Auth Policy Hook"
Cohesion: 1.0
Nodes (0): 

### Community 164 - "Auth Mutations Hook"
Cohesion: 1.0
Nodes (0): 

### Community 165 - "Account Snapshot Query"
Cohesion: 1.0
Nodes (0): 

### Community 166 - "Spotlight Graph App"
Cohesion: 1.0
Nodes (0): 

### Community 167 - "Quick Actions"
Cohesion: 1.0
Nodes (0): 

### Community 168 - "Hub App"
Cohesion: 1.0
Nodes (0): 

### Community 169 - "Hub Layout"
Cohesion: 1.0
Nodes (0): 

### Community 170 - "Hub Auth Hook"
Cohesion: 1.0
Nodes (0): 

### Community 171 - "Next Headers Mock"
Cohesion: 1.0
Nodes (0): 

### Community 172 - "CORS Test"
Cohesion: 1.0
Nodes (0): 

### Community 173 - "Cookie Utilities"
Cohesion: 1.0
Nodes (0): 

### Community 174 - "Service Worker"
Cohesion: 1.0
Nodes (0): 

### Community 175 - "History API"
Cohesion: 1.0
Nodes (0): 

### Community 176 - "Flags Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 177 - "Pin Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 178 - "OAuth Auth Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 179 - "Account Page Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 180 - "Settings Handlers"
Cohesion: 1.0
Nodes (0): 

### Community 181 - "Spotlight Root"
Cohesion: 1.0
Nodes (0): 

### Community 182 - "Spotlight Footer"
Cohesion: 1.0
Nodes (0): 

### Community 183 - "PixiJS Bootstrap"
Cohesion: 1.0
Nodes (0): 

### Community 184 - "Graph Canvas Types"
Cohesion: 1.0
Nodes (0): 

### Community 185 - "Data Model"
Cohesion: 1.0
Nodes (0): 

### Community 186 - "Content Script"
Cohesion: 1.0
Nodes (0): 

### Community 187 - "ForEach Utility"
Cohesion: 1.0
Nodes (0): 

### Community 188 - "Export Module"
Cohesion: 1.0
Nodes (0): 

### Community 189 - "Compact Tree"
Cohesion: 1.0
Nodes (0): 

### Community 190 - "Defaults"
Cohesion: 1.0
Nodes (0): 

### Community 191 - "Debounce"
Cohesion: 1.0
Nodes (0): 

### Community 192 - "Assert"
Cohesion: 1.0
Nodes (0): 

### Community 193 - "Log"
Cohesion: 1.0
Nodes (0): 

### Community 194 - "Site Messages"
Cohesion: 1.0
Nodes (0): 

### Community 195 - "Render"
Cohesion: 1.0
Nodes (0): 

### Community 196 - "Schema"
Cohesion: 1.0
Nodes (0): 

### Community 197 - "Account Keys"
Cohesion: 1.0
Nodes (0): 

### Community 198 - "Dashboard View"
Cohesion: 1.0
Nodes (0): 

### Community 199 - "Search Defaults"
Cohesion: 1.0
Nodes (0): 

### Community 200 - "Query Client"
Cohesion: 1.0
Nodes (0): 

### Community 201 - "Activity Page"
Cohesion: 1.0
Nodes (0): 

### Community 202 - "Billing Page"
Cohesion: 1.0
Nodes (0): 

### Community 203 - "Global Types"
Cohesion: 1.0
Nodes (0): 

### Community 204 - "Server-Only Guard"
Cohesion: 1.0
Nodes (0): 

### Community 205 - "Tailwind Config"
Cohesion: 1.0
Nodes (0): 

### Community 206 - "Vitest Setup"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **1 isolated node(s):** `SIL Open Font License v1.1`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Sync Open Tabs`** (2 nodes): `sync-open-tabs.ts`, `syncOpenTabs()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web Navigation`** (2 nodes): `webnavigation.ts`, `initWebNavigation()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Navigation Handler`** (2 nodes): `navigation-handler.ts`, `handleNavigation()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `New Tab Handler`** (2 nodes): `new-tab.ts`, `handleNewTabTab()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tree Node Utilities`** (2 nodes): `tree-utils.ts`, `createNode()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tab URL Utilities`** (2 nodes): `tab-utils.ts`, `resolveTabUrl()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Node Recency Tracker`** (2 nodes): `node-recency.ts`, `markNodeVisited()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Notifications`** (2 nodes): `ui-notifications.ts`, `notifyUi()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Undo Handlers`** (2 nodes): `undo-handlers.ts`, `applyTree()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Panel Handlers`** (2 nodes): `panel-handlers.ts`, `isSidepanelAlive()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Content Handlers`** (2 nodes): `content-handlers.ts`, `getSenderTabId()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Site Auth Handler`** (2 nodes): `site-message-handlers.ts`, `isAuthenticated()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tab Node Handlers`** (2 nodes): `tab-handlers.ts`, `unregisterTabForNode()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Navigation Focus`** (2 nodes): `navigation-handlers.ts`, `focusTab()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Data Migration`** (2 nodes): `migration.ts`, `migrateV2ToV3()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Aspect Ratio`** (2 nodes): `aspect-ratio.tsx`, `AspectRatio()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Direction Provider`** (2 nodes): `direction.tsx`, `DirectionProvider()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Collapsible`** (2 nodes): `collapsible.tsx`, `Collapsible()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Graph Frame`** (2 nodes): `SpotlightGraphFrame.tsx`, `SpotlightGraphFrame()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Drilldown Memory`** (2 nodes): `useDrilldownMemory.ts`, `useDrilldownMemory()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Text Highlight`** (2 nodes): `highlight.tsx`, `highlightText()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Quick Look`** (2 nodes): `SpotlightQuickLook.tsx`, `handler()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Keyboard`** (2 nodes): `useSpotlightKeyboard.ts`, `useSpotlightKeyboard()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Platform Detection`** (2 nodes): `platform.ts`, `isMac()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Help`** (2 nodes): `SpotlightHelp.tsx`, `SpotlightHelp()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Results`** (2 nodes): `SpotlightResults.tsx`, `flattenSections()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Selection Indicator`** (2 nodes): `useSelectionIndicator.ts`, `useSelectionIndicator()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight App`** (2 nodes): `SpotlightApp.tsx`, `SpotlightApp()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vitest Config`** (2 nodes): `config.ts`, `vitest.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graph Animation Hook`** (2 nodes): `useGraphAnimation.ts`, `useGraphAnimation()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graph Selection Hook`** (2 nodes): `useGraphSelection.ts`, `useGraphSelection()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graph View Hook`** (2 nodes): `useGraphView.ts`, `useGraphView()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Layout Send Hook`** (2 nodes): `useLayoutSend.ts`, `useLayoutSend()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Compute Layout`** (2 nodes): `compute-layout.ts`, `computeLayoutFromTree()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Storage Items`** (2 nodes): `storage-items.ts`, `archiveBlobKey()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Icon Generation`** (2 nodes): `generate-icons.ts`, `generateIcons()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Favicon URL`** (2 nodes): `favicon.ts`, `getFaviconUrl()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UUID Generator`** (2 nodes): `uuid.ts`, `uuidv7()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tree Deletion`** (2 nodes): `delete-tree.ts`, `getIncludedRootId()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Theme Definitions`** (2 nodes): `themes.ts`, `getThemes()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Icon Component`** (2 nodes): `Icon.tsx`, `icon()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Auth Portal Flow`** (2 nodes): `useAuthPortalFlow.ts`, `useAuthPortalFlow()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Account Hook`** (2 nodes): `useAccount.ts`, `useAccount()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Search Hook`** (2 nodes): `useSearch.ts`, `useSearch()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Runtime Messages Hook`** (2 nodes): `useRuntimeMessages.ts`, `useRuntimeMessages()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Auth Policy Hook`** (2 nodes): `useAuthPolicy.ts`, `useAuthPolicy()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Auth Mutations Hook`** (2 nodes): `useAuthMutations.ts`, `useAuthMutations()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Account Snapshot Query`** (2 nodes): `useAccountSnapshotQuery.ts`, `useAccountSnapshotQuery()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Graph App`** (2 nodes): `SpotlightGraphApp.tsx`, `SpotlightGraphApp()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Quick Actions`** (2 nodes): `QuickActions.tsx`, `QuickActions()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Hub App`** (2 nodes): `HubApp.tsx`, `HubApp()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Hub Layout`** (2 nodes): `HubLayout.tsx`, `HubLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Hub Auth Hook`** (2 nodes): `useHubAuth.ts`, `useHubAuth()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Next Headers Mock`** (2 nodes): `vitest.next-headers.ts`, `cookies()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `CORS Test`** (2 nodes): `cors.test.ts`, `loadModule()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cookie Utilities`** (2 nodes): `cookies.ts`, `getCookieValue()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Service Worker`** (1 nodes): `service-worker.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `History API`** (1 nodes): `history-api.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Flags Handlers`** (1 nodes): `flags-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pin Handlers`** (1 nodes): `pin-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `OAuth Auth Handlers`** (1 nodes): `oauth-auth-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Account Page Handlers`** (1 nodes): `account-page-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Settings Handlers`** (1 nodes): `settings-handlers.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Root`** (1 nodes): `SpotlightRoot.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Spotlight Footer`** (1 nodes): `SpotlightFooter.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PixiJS Bootstrap`** (1 nodes): `pixi-no-eval-bootstrap.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graph Canvas Types`** (1 nodes): `graph-canvas-types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Data Model`** (1 nodes): `model.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Content Script`** (1 nodes): `content-script.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ForEach Utility`** (1 nodes): `foreach.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Export Module`** (1 nodes): `export.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Compact Tree`** (1 nodes): `compact-tree.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Defaults`** (1 nodes): `defaults.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Debounce`** (1 nodes): `debounce.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Assert`** (1 nodes): `assert.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Log`** (1 nodes): `log.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Site Messages`** (1 nodes): `site-messages.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Render`** (1 nodes): `render.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Schema`** (1 nodes): `schema.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Account Keys`** (1 nodes): `account-keys.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard View`** (1 nodes): `DashboardView.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Search Defaults`** (1 nodes): `SearchDefaults.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Query Client`** (1 nodes): `query-client.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Activity Page`** (1 nodes): `ActivityPage.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Billing Page`** (1 nodes): `BillingPage.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Global Types`** (1 nodes): `globals.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Server-Only Guard`** (1 nodes): `vitest.server-only.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tailwind Config`** (1 nodes): `tailwind.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vitest Setup`** (1 nodes): `vitest.setup.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `SIL Open Font License v1.1` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `UI Component Library` be split into smaller, more focused modules?**
  _Cohesion score 0.01 - nodes in this community are weakly interconnected._
- **Should `App Shell & Auth` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._
- **Should `MiniSearch Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._
- **Should `Graph PixiJS Renderer` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `Account Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Account Snapshot & Env` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._