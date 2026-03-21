# Requirements: Trail

**Defined:** 2026-03-20
**Core Value:** Users can see and understand their browsing patterns through a visual tree

## v1.2 Requirements

Requirements for Release Readiness milestone. Each maps to roadmap phases.

### Hygiene & Release-Critical

- [x] **HYG-01**: logs/ removed from package root; dev-log write locations documented and enforced by test
- [x] **HYG-02**: AuthGate/WelcomeGate either wired into sidepanel flow or dead code removed
- [x] **HYG-03**: Unified error → toast/banner layer surfaces errors from rename/export/open/sync/auth operations
- [x] **HYG-04**: UI shows explicit sync status indicator (syncing / offline / degraded / error)
- [x] **HYG-05**: ErrorBoundary offers Copy diagnostics and Reload with safe mode actions
- [x] **HYG-06**: Stub archives show user-visible explanation ("tree unloaded due to quota, will load on demand")

### UX Polish

- [x] **UXP-01**: All dropdown/modal components share unified behavior (Esc, click-outside, focus return, inert management)
- [x] **UXP-02**: Sidepanel search UI shows keyboard shortcuts (Enter/Up/Down/Esc) inline, not just in tooltip
- [x] **UXP-03**: FloatingSearch preserves draft text on accidental blur instead of collapsing
- [ ] **UXP-04**: TreeDropdown shows last synced time, node count, and archived/stub status per tree
- [ ] **UXP-05**: Tag filter offers quick presets: all tagged, untagged, selected tags only
- [x] **UXP-06**: New tab shows reason and fallback CTA when bookmarks are unavailable
- [ ] **UXP-07**: Settings includes "Privacy & data" section explaining what goes to cloud vs stays local
- [ ] **UXP-08**: First-run layer shows 3-4 micro-hints for key gestures (search, tree switch, tag filter, spotlight)
- [x] **UXP-09**: SessionExpiredBanner dismiss is persistent until next meaningful state change; critical state never hidden
- [ ] **UXP-10**: Destructive action confirmations show what exactly will be lost and how to recover

### Stability

- [x] **STAB-01**: Bootstrap has explicit recovery path — critical fetch failure shows degraded state, not half-mounted UI
- [x] **STAB-02**: Single-flight and cancellation patterns deduplicated for auth/bootstrap/search (no races on quick open/close)
- [x] **STAB-03**: Double-submit prevented on all mutating actions (create tree, rename, export, auth)
- [x] **STAB-04**: Corrupted layout cache/localStorage auto-resets with recoverable toast notification
- [x] **STAB-05**: Offscreen layout computation failure falls back gracefully ("opened with basic layout")
- [x] **STAB-06**: SESSION_EXPIRED handled in spotlight and newtab, not just account flow
- [x] **STAB-07**: navigateTo failure from dropdown/context menu leaves user in clear state, not just logged
- [x] **STAB-08**: editorMode restores correctly after panel close / service worker restart
- [x] **STAB-09**: Quota eviction shows user notice when archives begin stubbing

### Security & Privacy

- [x] **SEC-01**: Manifest permission audit complete — unused permissions (chrome.scripting, browser.search) removed
- [x] **SEC-02**: activeTab necessity verified given existing host permissions and injection-free flow
- [x] **SEC-03**: Prod domains locked down; dev allowlist confirmed excluded from release builds
- [x] **SEC-04**: External search suggestions have user-visible toggle and privacy note (Google requests)
- [x] **SEC-05**: Structured logger replaces raw console.* on critical path (auth/sync/storage/search)
- [x] **SEC-06**: emitRuntimeLog either wired to critical failures or dead diagnostic code removed
- [x] **SEC-07**: Redaction policy applied to URL/title/token payloads in logs and reports
- [x] **SEC-08**: Protocol boundary site<->extension: payload validation tightened beyond envelope level
- [x] **SEC-09**: pixi.js/unsafe-eval CSP requirement documented with rationale

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
- [x] **QA-04**: Root artifact hygiene test prevents logs/, tasks/, dist/ from appearing in package root
- [ ] **QA-05**: Cold profile and dirty returning user tested separately
- [x] **QA-06**: Dead code / orphaned UX surface audit completed before release

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

| Requirement | Phase | Status |
|-------------|-------|--------|
| HYG-01 | Phase 2 | Complete |
| HYG-02 | Phase 2 | Complete |
| HYG-03 | Phase 3 | Complete |
| HYG-04 | Phase 4 | Complete |
| HYG-05 | Phase 3 | Complete |
| HYG-06 | Phase 3 | Complete |
| UXP-01 | Phase 5 | Complete |
| UXP-02 | Phase 5 | Complete |
| UXP-03 | Phase 5 | Complete |
| UXP-04 | Phase 5 | Pending |
| UXP-05 | Phase 5 | Pending |
| UXP-06 | Phase 5 | Complete |
| UXP-07 | Phase 5 | Pending |
| UXP-08 | Phase 5 | Pending |
| UXP-09 | Phase 5 | Complete |
| UXP-10 | Phase 5 | Pending |
| STAB-01 | Phase 3 | Complete |
| STAB-02 | Phase 4 | Complete |
| STAB-03 | Phase 4 | Complete |
| STAB-04 | Phase 3 | Complete |
| STAB-05 | Phase 3 | Complete |
| STAB-06 | Phase 4 | Complete |
| STAB-07 | Phase 3 | Complete |
| STAB-08 | Phase 4 | Complete |
| STAB-09 | Phase 3 | Complete |
| SEC-01 | Phase 6 | Complete |
| SEC-02 | Phase 6 | Complete |
| SEC-03 | Phase 6 | Complete |
| SEC-04 | Phase 6 | Complete |
| SEC-05 | Phase 6 | Complete |
| SEC-06 | Phase 2 | Complete |
| SEC-07 | Phase 6 | Complete |
| SEC-08 | Phase 6 | Complete |
| SEC-09 | Phase 6 | Complete |
| PERF-01 | Phase 7 | Pending |
| PERF-02 | Phase 7 | Pending |
| PERF-03 | Phase 7 | Pending |
| PERF-04 | Phase 7 | Pending |
| PERF-05 | Phase 7 | Pending |
| QA-01 | Phase 8 | Pending |
| QA-02 | Phase 8 | Pending |
| QA-03 | Phase 8 | Pending |
| QA-04 | Phase 2 | Complete |
| QA-05 | Phase 8 | Pending |
| QA-06 | Phase 2 | Complete |

**Coverage:**
- v1.2 requirements: 45 total
- Mapped to phases: 45
- Unmapped: 0

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-20 after roadmap creation*
