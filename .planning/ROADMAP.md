# Roadmap: Trail

## Milestones

- ✅ **v1.0 Initial Build** - Pre-GSD (shipped)
- ✅ **v1.1 Adultify** - Phases 1-4 (shipped 2026-03-19)

## Phases

<details>
<summary>✅ v1.0 Initial Build — SHIPPED (pre-GSD)</summary>

Pre-GSD milestone. Extension core, tree visualization, auth, sync, dashboard, marketing site, CMS, video generation.

</details>

<details>
<summary>✅ v1.1 Adultify (Phases 1-4) — SHIPPED 2026-03-19</summary>

- [x] Phase 1: Data Integrity & Auth Cleanup (2/2 plans) — completed 2026-02-28
- [x] Phase 2: CI/CD (1/1 plans) — completed 2026-02-28
- [x] Phase 3: UX Polish (3/3 plans) — completed 2026-02-28
- [x] Phase 4: Graph Startup Optimization (3/3 plans) — completed 2026-03-19

Full details: [milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md)

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Data Integrity & Auth Cleanup | v1.1 | 2/2 | Complete | 2026-02-28 |
| 2. CI/CD | v1.1 | 1/1 | Complete | 2026-02-28 |
| 3. UX Polish | v1.1 | 3/3 | Complete | 2026-02-28 |
| 4. Graph Startup Optimization | v1.1 | 3/3 | Complete | 2026-03-19 |

### Phase 1: Budgeted Rich-Content Restoration After Pan/Zoom

**Goal:** Replace synchronous burst rich-content restoration with frame-budgeted progressive hydration after pan/zoom gesture ends. Priority-sorted restore queue, LRU favicon cache, badge measurement caching, and restore telemetry.
**Requirements**: TBD
**Depends on:** Phase 0
**Plans:** 3 plans

Plans:
- [ ] 01-01-PLAN.md — Prioritized restore queue with budgeting and textResolution freeze
- [ ] 01-02-PLAN.md — Favicon LRU cache, batched invalidation, badge measureText cache
- [ ] 01-03-PLAN.md — Extend GraphRenderMetrics with restore telemetry
