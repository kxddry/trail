# Requirements: Trail

**Defined:** 2026-03-20
**Core Value:** Users can see and understand their browsing patterns through a visual tree

## v1.2 Requirements

Requirements for Release Readiness milestone. Each maps to roadmap phases.

### Hygiene & Release-Critical

- [ ] **HYG-01**: logs/ removed from package root; dev-log write locations documented and enforced by test
- [ ] **HYG-02**: AuthGate/WelcomeGate either wired into sidepanel flow or dead code removed
- [ ] **HYG-03**: Unified error → toast/banner layer surfaces errors from rename/export/open/sync/auth operations
- [ ] **HYG-04**: UI shows explicit sync status indicator (syncing / offline / degraded / error)
- [ ] **HYG-05**: ErrorBoundary offers Copy diagnostics and Reload with safe mode actions
- [ ] **HYG-06**: Stub archives show user-visible explanation ("tree unloaded due to quota, will load on demand")

### UX Polish

- [ ] **UXP-01**: All dropdown/modal components share unified behavior (Esc, click-outside, focus return, inert management)
- [ ] **UXP-02**: Sidepanel search UI shows keyboard shortcuts (Enter/Up/Down/Esc) inline, not just in tooltip
- [ ] **UXP-03**: FloatingSearch preserves draft text on accidental blur instead of collapsing
- [ ] **UXP-04**: TreeDropdown shows last synced time, node count, and archived/stub status per tree
- [ ] **UXP-05**: Tag filter offers quick presets: all tagged, untagged, selected tags only
- [ ] **UXP-06**: New tab shows reason and fallback CTA when bookmarks are unavailable
- [ ] **UXP-07**: Settings includes "Privacy & data" section explaining what goes to cloud vs stays local
- [ ] **UXP-08**: First-run layer shows 3-4 micro-hints for key gestures (search, tree switch, tag filter, spotlight)
- [ ] **UXP-09**: SessionExpiredBanner dismiss is persistent until next meaningful state change; critical state never hidden
- [ ] **UXP-10**: Destructive action confirmations show what exactly will be lost and how to recover

### Stability

- [ ] **STAB-01**: Bootstrap has explicit recovery path — critical fetch failure shows degraded state, not half-mounted UI
- [ ] **STAB-02**: Single-flight and cancellation patterns deduplicated for auth/bootstrap/search (no races on quick open/close)
- [ ] **STAB-03**: Double-submit prevented on all mutating actions (create tree, rename, export, auth)
- [ ] **STAB-04**: Corrupted layout cache/localStorage auto-resets with recoverable toast notification
- [ ] **STAB-05**: Offscreen layout computation failure falls back gracefully ("opened with basic layout")
- [ ] **STAB-06**: SESSION_EXPIRED handled in spotlight and newtab, not just account flow
- [ ] **STAB-07**: navigateTo failure from dropdown/context menu leaves user in clear state, not just logged
- [ ] **STAB-08**: editorMode restores correctly after panel close / service worker restart
- [ ] **STAB-09**: Quota eviction shows user notice when archives begin stubbing

### Security & Privacy

- [ ] **SEC-01**: Manifest permission audit complete — unused permissions (chrome.scripting, browser.search) removed
- [ ] **SEC-02**: activeTab necessity verified given existing host permissions and injection-free flow
- [ ] **SEC-03**: Prod domains locked down; dev allowlist confirmed excluded from release builds
- [ ] **SEC-04**: External search suggestions have user-visible toggle and privacy note (Google requests)
- [ ] **SEC-05**: Structured logger replaces raw console.* on critical path (auth/sync/storage/search)
- [ ] **SEC-06**: emitRuntimeLog either wired to critical failures or dead diagnostic code removed
- [ ] **SEC-07**: Redaction policy applied to URL/title/token payloads in logs and reports
- [ ] **SEC-08**: Protocol boundary site↔extension: payload validation tightened beyond envelope level
- [ ] **SEC-09**: pixi.js/unsafe-eval CSP requirement documented with rationale

### Performance

- [ ] **PERF-01**: Three release budget metrics tracked: first sidepanel paint, first graph interactive, spotlight query latency
- [ ] **PERF-02**: blur/LOD/animation degrade aggressively on weak machines and heavy trees
- [ ] **PERF-03**: Derived search/index data cached on idle
- [ ] **PERF-04**: Long lists (trees/tags/results) use virtualization or chunked render where needed
- [ ] **PERF-05**: Heavy loading states show skeletons instead of empty canvas/null suspense fallback

### QA & Release Discipline

- [ ] **QA-01**: Smoke e2e tests cover 8 scenarios: first install, guest mode, auth, session expired, sync fail, tree switch, export/import, quota eviction
- [ ] **QA-02**: UI interaction tests cover: dropdown keyboard, modal escape, search navigation, auth banner
- [ ] **QA-03**: Release checklist covers: permissions, offline mode, empty states, corrupted cache, worker restart
- [ ] **QA-04**: Root artifact hygiene test prevents logs/, tasks/, dist/ from appearing in package root
- [ ] **QA-05**: Cold profile and dirty returning user tested separately
- [ ] **QA-06**: Dead code / orphaned UX surface audit completed before release

## v2 Requirements

Deferred to future release.

- **RATE-01**: Rate limiting on API endpoints
- **AUTH-R01**: Refresh token replay detection
- **MOBILE-01**: Mobile app

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time collaboration | Single-user product |
| Mobile app | Web-first, mobile later |
| New feature development | This milestone is hardening only |
| Marketing site changes | Not release-blocking |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| (populated by roadmapper) | | |

**Coverage:**
- v1.2 requirements: 45 total
- Mapped to phases: 0
- Unmapped: 45

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-20 after initial definition*
