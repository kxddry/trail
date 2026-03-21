---
phase: 03-bypass-react-for-animation
plan: 01
subsystem: ui
tags: [react, pixi, animation, raf, imperative-rendering, performance]

requires:
  - phase: 02-split-renderer-api
    provides: "setDynamicState() / setParticles() granular renderer API"
provides:
  - "Imperative animation path bypassing React re-renders during expand/collapse"
  - "onTickRender callback pattern from useGraphAnimation to GraphCanvas"
  - "latestRenderStateRef snapshot for imperative state access"
affects: [04-connection-caching, 05-interaction-optimization, 07-state-architecture]

tech-stack:
  added: []
  patterns:
    - "onTickRender callback: animation hook pushes frames imperatively to renderer via injected callback"
    - "latestRenderStateRef: snapshot ref pattern for accessing React-computed state from RAF callbacks"
    - "React reconciliation deferred to animation end via single invalidateAnimation() call"

key-files:
  created: []
  modified:
    - src/entrypoints/sidepanel/ui/components/graph/useGraphAnimation.ts
    - src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx

key-decisions:
  - "onTickRender callback pattern chosen over direct renderer ref in animation hook — keeps renderer coupling in GraphCanvas only"
  - "Drag reparent preview skipped in imperative path — drag and animation are mutually exclusive interactions"
  - "latestRenderStateRef snapshot assigned after useMemos — RAF callback always reads latest computed state"

patterns-established:
  - "onTickRender callback: animation ticks call injected callback instead of setting React state"
  - "Ref-stored callback: onTickRenderRef.current updated on every render so memoized animateTick reads latest"
  - "End-of-animation reconciliation: invalidateAnimation() + invalidateParticles() called only in !needsLoop branch"

requirements-completed: [RCYC-01]

duration: 18min
completed: 2026-03-18
---

# Phase 3 Plan 1: Bypass React for Animation Summary

**Imperative onTickRender callback bypasses React re-renders during expand/collapse animation, reducing ~9 React re-renders per animation to 1 final reconciliation**

## Performance

- **Duration:** 18 min
- **Started:** 2026-03-18T16:20:00Z
- **Completed:** 2026-03-18T16:38:00Z
- **Tasks:** 2 (1 implementation + 1 verification checkpoint)
- **Files modified:** 2

## Accomplishments

- animateTick now pushes position/openProgress updates directly to the renderer via onTickRender callback without touching React state
- React re-renders during animation eliminated — GraphCanvas only re-renders once at animation end for final reconciliation
- All interactions (expand/collapse, drag, hover, search, pan/zoom, particles) verified working correctly by user
- Performance profiling confirmed reduced React re-renders from ~9/animation to 1/animation

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire imperative renderer updates from animateTick** - `40b5abed` (feat)
2. **Task 2: Visual and performance verification** - checkpoint approved by user (no code changes)

Additional fix commits:
- `aa008fca` (fix) - Resolve TypeScript type errors in imperative tick render path

## Files Created/Modified

- `src/entrypoints/sidepanel/ui/components/graph/useGraphAnimation.ts` - Added onTickRender callback parameter, onTickRenderRef for stable access from animateTick, imperative tick dispatch replacing invalidateAnimation() during active animation, end-of-animation React reconciliation
- `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` - Added latestRenderStateRef snapshot, handleTickRender useCallback that builds NodeRenderModel[] and ConnectionSegment[] imperatively and pushes to renderer via setDynamicState()/setParticles(), wired onTickRender to useGraphAnimation

## Decisions Made

- **onTickRender callback pattern** over direct renderer ref in animation hook: keeps renderer knowledge and DynamicGraphState construction contained in GraphCanvas, while useGraphAnimation remains a pure animation-state manager
- **Skip drag reparent preview in imperative path**: drag and expand/collapse animation are mutually exclusive user interactions, so the imperative path never needs dragReparentTarget logic
- **latestRenderStateRef assigned after useMemos**: ensures the RAF callback (which fires asynchronously) always reads the latest React-computed values for visibleDisplayNodes, positions, search state, etc.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] TypeScript type errors in imperative tick render path**
- **Found during:** Task 1
- **Issue:** Type mismatches in handleTickRender — missing fields in NodeRenderModel construction, incorrect Map types for connectionPositions
- **Fix:** Corrected all type annotations and added missing required fields
- **Files modified:** src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx
- **Verification:** `npx tsc --noEmit` passes cleanly
- **Committed in:** `aa008fca`

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Type fix was necessary for correctness. No scope creep.

## Issues Encountered

None beyond the TypeScript type errors fixed above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 3 complete. The imperative animation path is fully operational.
- Phases 4 (Connection Caching), 5 (Interaction Optimization), and 6 (Object Pooling) are now unblocked and can execute in parallel.
- The onTickRender pattern established here will be relevant for Phase 5's interaction optimization work.

## Self-Check: PASSED

All files verified present, all commits verified in git log.

---
*Phase: 03-bypass-react-for-animation*
*Completed: 2026-03-18*
