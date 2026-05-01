# Interactive onboarding — 8-screen plan

Uses the Cal AI / Opal / Rise framework: **Hook → Agitate → Personalize → Solution → Features-as-outcomes → Magic → Quick Win → Soft CTA**. Adapted for Trail (browser extension, free, productivity-not-entertainment).

Reference mental model: Cal AI's screens 1–5, then Wispr Flow's "feel the thing" moment for screen 6.

## Framework translation for Trail

| # | Cal AI framework | Trail screen |
|---|-----------------|--------------|
| 1 | Hook | "Where did I read that thing?" — rotating pain statements |
| 2 | Agitate | "Your browser forgets everything." |
| 3 | Personalize | "What do you lose in your browser?" — pick 1 of 4 |
| 4 | Solution | Tailored to their pick |
| 5 | Features as outcomes | 3 outcome-bullets, not feature-bullets |
| 6 | **Magic** | **Interactive Google-branching tour** (the payoff) |
| 7 | Quick win | "4 nodes in 45 seconds." Celebration of their tour tree |
| 8 | Soft CTA | "Pin Trail" / "Create account to sync" / "Start trailing" |

Screens 1–5 = modal wizard (sequential, guided, non-interactive except personalization on 3).
Screen 6 = persistent coach over real browser activity.
Screens 7–8 = sidepanel celebration + soft commitment.

## Tone calibration (important)

The user's reference examples (Cal AI) yell benefits because they fight for attention in the App Store. Trail is **already installed**. The user is at "give me a reason to keep it" not "stop scrolling." Hook should be **warm recognition**, not capslock.

Good: "Lost 47 tabs this week? You're not the only one."
Bad: "WINNER WINNER WINNER. Tired of bad browsing?"

Cal AI tone works for fitness/diet because those have visceral pain. Trail's pain is low-grade but constant — "huh, where was that tab." Match that register.

## Screen-by-screen

### Screen 1 — Hook (modal, no input)
Rotating headline, crossfade every 1.2s, 4 lines:
- "Where did I read that thing yesterday?"
- "How did I even get to this tab?"
- "I went back. I lost it."
- "47 tabs. I don't remember why."

After 4 rotations, settles on: **"Your browser forgets. Trail remembers."**
Single button: `[Show me]`.

**Why it works for Trail:** every person who installs a tab-management extension already feels this. Validation = commitment.

### Screen 2 — Agitate / reframe (modal)
Quiet screen, one sentence centered:
> Chrome's history is a chronological dump. You don't think chronologically.

Subhead: "You think in threads, branches, 'that thing I was looking at before'."
Button: `[Keep going]`.

**Why:** sets up that the SOLUTION isn't "better history" but "different shape of history." Primes the branch concept.

### Screen 3 — Personalize (modal, interactive — THE pick)
H1: "What do you lose in your browser?"

Four options as `Card` tiles, single-select:
- 🔍 **Research threads** — "I compare 5 things at once and get lost"
- 📰 **That one article** — "I meant to come back. I didn't"
- 🧵 **Learning paths** — "I was deep in something last week. Now it's gone"
- 🗂️ **Open tabs** — "I keep them open because I'm scared to close them"

Store pick in `onboardingStateItem.persona`. Drives next screen's copy AND the final recommendation.

### Screen 4 — Solution (modal, tailored to pick)
One-sentence promise based on persona:

| Persona | Copy |
|---|---|
| Research threads | "Trail keeps every path you explored. Click back, try another — both are saved. Nothing dies when you change your mind." |
| That one article | "Every click becomes a searchable node. That thing from Tuesday is two letters away." |
| Learning paths | "Your learning is a tree, not a list. Trail draws the tree so you can pick up where you left off." |
| Open tabs | "Close your tabs. Trail keeps them addressable. Open any node from yesterday like it's still a tab." |

Button: `[I'm in]`.

### Screen 5 — Features as outcomes (modal)
Three bullets, **outcomes not mechanics**:
- "Every tab you open is a node you can return to." *(not: graph visualization)*
- "Go back + click somewhere else? Both paths are saved, side by side." *(not: branching algorithm)*
- "Search what you actually did, not just URLs you typed." *(not: full-text index)*

Button: `[Let me feel it]` — hands off to the tour.

### Screen 6 — Magic: the interactive tour (coach, NOT modal)
This is where the modal closes and a **persistent coach card** appears at the bottom of the sidepanel. A dedicated "Trail tour" tree is created and made active. Full scenario:

**6a.** Coach: "Search Google for anything. I'll watch."
Button: `[Open Google for me]` (optional shortcut) | User can also manually open any tab.
Wait for: tree gets a Google-search URL node.

**6b.** Coach: "Nice. Click any result."
Wait for: new child node under Google.

**6c.** Coach: "Now press **Back**." `<Kbd>⌘ ←</Kbd>` hint shown.
Wait for: `currentNodeId` → Google search node again, child node still present.

**6d.** Coach: "Click a **different** result." (The payoff sentence.)
Wait for: Google node has ≥2 children.
**On transition:** spring animation fires, Google node gets `spotlight: "pulse"` ring, coach card swaps to:
> ✨ You branched. Both paths are saved.

Hold that state for 2s. Auto-advance.

**6e.** Coach: "See the other result in the graph? Click it." (Spotlight: "target" ring on the abandoned child node.)
Wait for: `currentNodeId` matches spotlit node via `navigateToNodeId`.

### Screen 7 — Quick Win (coach → celebration)
Full-sidepanel celebration overlay (not modal, uses existing `Empty` primitive with a twist):
- Their tour tree rendered mini, nodes pulsing
- Headline: "4 nodes in 45 seconds."
- Sub: "This is what every browsing session could look like."
- Background: subtle confetti (CSS keyframes, no library)

**Why:** progress = dopamine. They FEEL the receipt.

### Screen 8 — Soft CTA (Trail is free, so no trial)
Three commitments, pick any or skip — all dismissible:

1. **Pin Trail to your toolbar** — primary. Small animated arrow pointing to where the pin icon should be. Click opens the extensions menu deep link if possible, otherwise shows instructions with screenshot.
2. **Sync across devices** — secondary. Opens login page in new tab. Optional.
3. **Theme pick** — tertiary. Dark/light/system toggle. Low-stakes commitment that makes them feel ownership.

Then, closing CTA:
> `[Delete tour tree, I'm ready]` / `[Keep it — start new tree]`

Closes onboarding. Sets `completedAt`.

## Architecture (unchanged from prior plan, expanded)

### Modal vs coach split
- **Modal wizard** (`OnboardingWizard.tsx`, heavily rewritten): screens 1–5. Rotates Welcome/Privacy/Branch content into the new 5-screen structure. Privacy disclosure moves into screen 5 as a one-liner + expandable details (still before any tracking starts on the tour tree).
- **Persistent coach** (new `TourCoach.tsx`): screens 6a–6e. Bottom-anchored, non-blocking, always dismissible.
- **Celebration + CTA** (new `TourCelebration.tsx` + `TourCommitments.tsx`): screens 7–8.

### State
```ts
// In sidepanel Zustand store
onboarding: {
  phase: "wizard" | "tour" | "celebration" | "cta" | null;  // null = done/skipped
  wizardStep: 0..4;       // screens 1–5
  tourStep: 0..4;         // screens 6a–6e
  persona: "research" | "article" | "learning" | "tabs" | null;
  tourTreeId: TreeId | null;
  spotlightNodeId: NodeId | null;
  spotlightKind: "pulse" | "target" | null;
};

// In chrome.storage.local via existing onboardingStateItem
{
  seenWelcome: boolean;
  phase?: same as above;
  wizardStep?: number;
  tourStep?: number;
  persona?: string;
  tourTreeId?: string;
  startedAt?: number;
  completedAt?: number;
}
```

### New files
```
src/apps/sidepanel/ui/onboarding/
  OnboardingWizard.tsx             # rewritten (screens 1–5)
  wizard/
    HookScreen.tsx                 # rotating pain statements
    AgitateScreen.tsx              # reframe
    PersonaPickScreen.tsx          # 4-tile personalization
    SolutionScreen.tsx             # tailored copy by persona
    FeaturesScreen.tsx             # 3 outcome bullets
    pain-statements.ts             # i18n-keyed rotation list
  tour/
    TourCoach.tsx                  # persistent card
    tour-machine.ts                # step → predicate map
    useTourObserver.ts             # subscribes to store, advances
    tour.css                       # spotlight keyframes
  celebration/
    TourCelebration.tsx            # screen 7
    confetti.css                   # lightweight CSS confetti
  cta/
    TourCommitments.tsx            # screen 8
    PinInstructions.tsx
```

### Graph changes
Add `spotlight?: "pulse" | "target"` to `TrailNodeData` in `src/features/graph/types.ts`. Layout transform merges from store. Trail node renders ring overlay. Spring animation on branch detection via existing `motion/` folder.

### i18n
All copy in `en.json` + `ru.json` from day one, under `onboarding.v2.*` (keep old `onboarding.*` keys alive during migration, delete after confirming the new flow sticks).

## Scope cuts (explicit no-go for v1)

- Multiple scenarios (pin demo, command palette demo, sync demo). **Only the Google branching scenario for screen 6.** Framework says one magic moment, not five.
- Gamification beyond screen 7 (streaks, achievements, etc).
- A/B testing the wizard copy. Ship one version, measure later.
- Video/animation imports. All motion is CSS or existing Framer/motion.

## Build order (so nothing ships half-built)

1. **Storage + state slice** — `onboardingStateItem` grows, Zustand slice added. No UI yet.
2. **`spotlight` on `TrailNodeData`** + visual treatment on node component. Testable in isolation.
3. **Tour machine + observer** — pure logic, unit-testable.
4. **`TourCoach.tsx`** — the hardest component, build before screens 1–5 so the "payoff" works first.
5. **Rewrite `OnboardingWizard.tsx`** — screens 1–5 with new copy.
6. **Celebration + CTA** — screens 7–8.
7. **Wire end-to-end** — first-run trigger, persistence, resume, skip.
8. **i18n pass** — en + ru copy in one go.
9. **Polish pass** — spring timing, confetti density, kbd hint alignment.

Approx ~2–2.5 days for a solid v1. The framework adds screens 1–5 on top of the coach work, so slightly more than the prior estimate.

## Confirmed decisions (2026-04-21)

1. **Tone**: warm, not shouty.
2. **Screen 1 (Hook)**: single crisp value promise, not rotating pain. Template: Cal AI's "Count calories with just a photo" — one sentence, stops scrolling.
3. **Screen 2 (Problem)**: this is where pain statements live — user nods, feels understood. Three short questions max.
4. **Persona** affects screen 4 copy AND the tagline above screen 8's CTA.
5. **Screen 8** is dead simple: one primary `[Sign in]`, one secondary `[Skip]`. No "pin toolbar," no theme pick, no tree-delete choice. Minimal.
6. **Tour tree**: auto-delete on completion. User will create their own tree next.
7. **Language**: English only. `ru.json` mirrors `en.json` — no Russian translation shipping.

## Hook copy candidates (pick on i18n pass)

Three options to try — final call at copy-polish step:
- **"Never lose a tab again."** — loss aversion, 4 words, concrete.
- **"Every tab you've ever opened, one click away."** — completeness promise.
- **"Your browser, finally mapped."** — metaphor-forward, 4 words.

Starting first build step now — storage + state slice is independent of copy.

## Build log (2026-04-21)

- [x] Storage + state slice (`OnboardingState` extended in `storage-items.ts:96`, Zustand `onboarding` slice added in `store.ts`)
- [x] API extensions: `setWizardStep`, `setTourStep`, `setOnboardingPhase`, `setOnboardingPersona`, `startTourTree`, `bindTourTreeId`, `disposeTourTree` in `api/onboarding.ts`
- [x] `spotlight?: "pulse" | "target"` on `TrailNodeData` + ring keyframes in `features/graph/pane.css`
- [x] `TrailGraph` accepts `spotlight` prop; App.tsx threads from store
- [x] Tour state machine (`tour/tour-machine.ts`) with 5 steps: arm / clickResult / goBack / branch / returnToAbandoned — predicates test the tree model, not raw browser events
- [x] `useTourObserver` — subscribes to Zustand transitions, advances step on match, captures `firstResultChildId` + `branchParentId` across ticks
- [x] `TourCoach` bottom-anchored card: per-step prompt, optional `[Open Google for me]` CTA, Kbd hint on back-step, always-visible `[Skip]`, Esc with confirm
- [x] 5 wizard screens: Hook / Problem / PersonaPick / Solution / Features
- [x] Rewritten `OnboardingWizard` — uses new screens, persona auto-advance, primary CTA on Features creates "Trail tour" tree and flips phase → "tour"
- [x] `TourCelebration` with CSS confetti + node count + seconds elapsed, auto-advances to CTA in 3.2s
- [x] `TourCommitments` — persona-tailored tagline + `[Sign in]` / `[Maybe later]`, both dispose tour tree and complete onboarding
- [x] All copy in `en.json` + `ru.json` under `onboarding.v2.*`, `onboarding.tour.*`, `onboarding.celebration.*`, `onboarding.cta.*`
- [x] First-run wiring in `OnboardingWizard` useMount: hydrates store from storage, opens wizard when `!seenWelcome`, resumes mid-wizard if `phase === "wizard"`, skips modal if `phase` is tour/celebration/cta (coach / celebration / cta take over)
- [x] All new analytics events added: `onboarding_phase_entered`, `onboarding_persona_picked`, `onboarding_tour_tree_created`, `onboarding_tour_branched`, `onboarding_tour_completed`
- [x] TypeScript clean (`tsc -p tsconfig.app.json --noEmit` — 0 errors)
- [x] ESLint clean on all touched files
- [x] WXT production build passes

## Deferred / not done

- Deep unit tests on `tour-machine` predicates — the fixtures require typed `NavigationTreeJSON`/`NavigationNodeJSON` scaffolding; skipped for v1, should add before merge
- **Interactive smoke-test in Chrome — NOT DONE.** See "Manual test checklist" below.
- Hook copy A/B: three candidates written into the plan but only the "Never lose a tab again" variant is wired
- Settings → About "replay onboarding" button (mentioned in wizard — subscription wired in place, but no visible UI knob to trigger it)

## Advisor-driven bug fixes (post-build)

Second-pass review caught three real issues I missed on the first build:

1. **Tour anchors lost on sidepanel close.** `firstResultChildIdRef` / `branchParentIdRef` were refs only. After sidepanel remount mid-tour, step 4's predicate became un-satisfiable. Fixed: added `tourFirstResultChildId` + `tourBranchParentId` to `OnboardingState`, observer writes them at capture time via `saveTourAnchors` and rehydrates on mount.
2. **Tour-tree id race.** `handleEnterTour` used a 120ms `setTimeout` to wait for the background's tree-updated broadcast. On slow machines this missed and `tourTreeId` stayed null, leaking the tour tree into the user's real tree list. Fixed: replaced with a `useStore.subscribe` that resolves when `trees.active.id` actually changes, with a 3s watchdog.
3. **Active-tree deletion.** The background's `DELETE_TREE` handler throws "Cannot delete active tree" — my `disposeTourTree` was calling it on the currently-active tour tree. Fixed: added `priorActiveTreeId` to `OnboardingState`, capture it before creating the tour tree, restore it (via `openTree`) before deleting. Fresh-install users with no prior tree get a new "My trail" empty tree instead.

## Manual test checklist (BLOCKING before "done")

Per project `CLAUDE.md`: "Never mark a task complete without proving it works. For UI or frontend changes, start the dev server and use the feature in a browser before reporting the task as complete." I built `wxt build` successfully but did NOT load the artifact in Chrome. User needs to run `pnpm dev` (or load `.output/chrome-mv3`) and walk through:

- [ ] First-run with fresh storage shows the Hook screen
- [ ] Enter advances Hook → Problem → Persona
- [ ] Persona tile pick auto-advances to Solution, text matches pick
- [ ] Back from Solution preserves the pick on Persona screen
- [ ] "Let me feel it" (Features primary) creates a "Trail tour" tree, switches to it, opens coach
- [ ] Coach "Open Google for me" opens a Google search tab
- [ ] Clicking a result under Google → advances to "Press Back" step with kbd hint
- [ ] ⌘← (or Alt←) back to Google → advances to branch step
- [ ] Clicking a DIFFERENT Google result → spotlight pulse appears on Google node, coach shows "You branched"
- [ ] Clicking the abandoned-result node in the graph (target ring) → advances to celebration
- [ ] Celebration shows "$N nodes in $S seconds" with confetti, auto-advances to CTA after ~3s
- [ ] CTA tagline matches persona pick
- [ ] [Sign in] opens login tab AND disposes tour tree (check tree list) AND switches back to prior tree (or creates "My trail" for fresh installs)
- [ ] [Maybe later] same disposal flow without opening login
- [ ] Close sidepanel mid-tour, reopen → coach resumes at same step with anchors intact
- [ ] Skip tour mid-flow → tour tree deleted, prior tree restored, onboarding marked complete

If any of these fails, the fix goes here, not a new PR.

