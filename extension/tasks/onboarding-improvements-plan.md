# Onboarding improvements — execution plan (2026-04-24)

Source: `tasks/onboarding-improvements.md` (21 proposals). Post-critic scope below.

## Selected for this pass

Three items, merged where they collide:

- **#10** Persona-specific celebration body copy
- **#17** Privacy disclosure on FeaturesScreen (NOT Hook — critic correction)
- **#13 + #14 merged** into ONE sticky onboarding hint strip with priority ordering

## Rejected (for this pass)

- #1 multi-select persona — cascades through ≥4 files, no A/B signal
- #2 personalized mock-graph — already done in `SolutionVisual.tsx`
- #3 founder note — tonally risky (off-register for the wizard's warm voice)
- #5 hook demo animation — design-heavy, needs quality CSS/SVG
- #7 progressive education — overlaps with #15, refactor-heavy
- #9 loading momentum — solving perception that may not exist; measure first
- #15 reduce wizard to 2–3 screens — reorganization, kills other items
- #16 "try it" CTA — alternative entry path, high complexity
- #18 complete only on real aha — migration concerns + new observer
- #19 guided demo + try-on-browsing — rewrite tour-machine
- #20 real trail before auth — depends on #18
- #21 Russian translation — premature until en stabilizes
- #6 #8 #12 — low ratio or out-of-flow

## Architecture

### Phase model extension

```ts
OnboardingPhase = "wizard" | "tour" | "tourDismissed" | "celebration" | "cta" | "done"
                                       ↑ new
```

`tourDismissed` meaning: user hit Skip in tour. Tour tree is preserved
(not deleted), active tree is switched back to `priorActiveTreeId`.
`tourStep` + anchors are preserved. Sidepanel shows a persistent
"Resume tour" hint.

`completedAt` is NOT set by dismiss — it's still only set by
`completeOnboarding` (called from `TourCommitments.finish()`).

### State shape extension

```ts
OnboardingState {
  ...existing,
  softCtaDismissed?: { signin?: boolean; pin?: boolean };
}
```

Defaults to `undefined`. Strip predicates use `?.signin !== true`.

### Hint strip priority (one at a time)

1. `phase === "tourDismissed"` → Resume tour chip
2. `completedAt != null && softCtaDismissed?.signin !== true && !signedIn` → Sign in strip
3. `completedAt != null && softCtaDismissed?.pin !== true` → Pin toolbar strip
4. else → hidden

Mutex with TourCoach/Celebration/CTA by construction:
- Strip hidden while `phase === "wizard" | "tour" | "celebration" | "cta"`
- TourCoach hidden while `phase !== "tour"`
- Celebration/CTA hidden while `phase !== "celebration" | "cta"`

### New API (api/onboarding.ts)

```ts
dismissTour()     // phase: "tourDismissed"; openTree(priorActive); preserve tourTreeId+step+anchors
resumeTour()      // phase: "tour"; openTree(tourTreeId)
dismissSoftCta(surface: "signin" | "pin")
```

### Files touched

1. `src/shared/config/storage-items.ts` — types + fallback
2. `src/apps/sidepanel/api/onboarding.ts` — new APIs
3. `src/apps/sidepanel/ui/onboarding/tour/TourCoach.tsx` — skip → dismissTour
4. `src/apps/sidepanel/ui/onboarding/OnboardingWizard.tsx` — tourDismissed in "don't reopen" list
5. `src/apps/sidepanel/ui/onboarding/celebration/TourCelebration.tsx` — bodyByPersona read
6. `src/apps/sidepanel/ui/onboarding/wizard/FeaturesScreen.tsx` — add `<details>` privacy block
7. `src/apps/sidepanel/ui/onboarding/hint-strip/OnboardingHintStrip.tsx` — NEW
8. `src/apps/sidepanel/ui/App.tsx` — mount strip
9. `src/apps/sidepanel/ui/state/store.ts` — slice gets `softCtaDismissed`
10. `src/apps/settings/pages/AboutPage.tsx` — full-reset wipes new fields
11. `src/shared/lib/observability.ts` — new event names
12. `src/locales/en.json` + `src/locales/ru.json` — new keys

## Risks & mitigations

- **Tour tree leak on dismiss** — since we preserve it, user sees "Trail tour" in tree list while dismissed. Acceptable — Resume chip is visible, guiding them back. Final CTA still runs `disposeTourTree`.
- **Phase union exhaustiveness** — TS will flag unhandled `tourDismissed` in consumer switches once the union is updated. Audit all `phase ===` sites.
- **Auth state for sign-in auto-dismiss** — read `useStore((s) => s.authState)` or equivalent. Auto-hide strip when signed-in, but don't mark dismissed (so if they sign out, strip comes back? Design call: auto-dismiss on sign-in AND mark `softCtaDismissed.signin = true` so it stays gone).
- **Pin detection is impossible** — no `chrome.action.isPinned()` API. Pin CTA only dismisses on × or CTA click (show instructions toast).
- **ru.json keys must mirror** — even though text stays English per project convention, keys must exist to avoid runtime i18n misses.

## Verification

1. TypeScript: `pnpm run typecheck` — CLEAN
2. ESLint on touched files — CLEAN (only pre-existing warnings elsewhere)
3. `pnpm run build` (WXT production) — PASSES, 3.02 MB bundle
4. Manual (deferred to user session): wizard flow → tour → dismiss → Resume chip → resume → celebrate → CTA → Maybe later → Sign-in strip → dismiss → Pin strip → dismiss

## Built (2026-04-24)

- [x] `OnboardingPhase` + `softCtaDismissed` + `OnboardingSoftCtaKey` types
- [x] `INITIAL_ONBOARDING_STATE` exported so AboutPage stays in lock-step
- [x] `switchAwayFromTourTree()` helper, `dismissTour()`, `resumeTour()`, `dismissSoftCta()`
- [x] `dismissTour()` defensive no-op when `completedAt` set (corrupt-state safety)
- [x] `resumeTour()` orphan-fallback both on caller snapshot + on `openTree` throw
- [x] `disposeTourTree()` now clears tour anchors too (no stale leftover)
- [x] TourCoach skip → `dismissTour` (not `skipOnboarding`)
- [x] OnboardingWizard mount guard: `tourDismissed` added to "don't reopen" list
- [x] TourCommitments finish writes `completedAt` to store
- [x] TourCelebration reads persona-specific body key with fallback
- [x] FeaturesScreen has collapsible `<details>` reusing `onboarding.privacy.*` copy (a11y: focus-visible ring)
- [x] `useTourObserver` re-applies spotlight on phase re-entry to "tour" (Resume visual restore)
- [x] New `OnboardingHintStrip` component with Resume/Signin/Pin priority
  - Explicit overlay mutex in predicate (phase != wizard/tour/celebration/cta)
  - Resume gated on `completedAt == null` (belt-and-braces against corrupt state)
  - Auth-resolved check suppresses flash during bootstrap
  - Auto-hide on signed-in is predicate-level (no write) so strip returns on sign-out
  - × button at 24px target (p-1.5)
- [x] App.tsx mounts the strip next to other overlays
- [x] AboutPage full reset: disposes tour tree + resets via canonical constant
- [x] Analytics: `onboarding_tour_dismissed/resumed/resume_orphan`, `onboarding_soft_cta_shown/clicked/dismissed`
- [x] i18n: `celebration.bodyByPersona.*` + `onboarding.hintStrip.*` in en.json + ru.json (ru text mirrors en per project convention)

## Not done (intentional)

- Multi-window concurrent-write lock on `saveOnboardingState` — single-sidepanel assumption holds; annotate later if multi-sidepanel becomes real.
- Renaming tour tree to "(Tour in progress)" during dismiss — low value, skip.
- Russian translation of the new copy — premature until en stabilizes (per project convention).
