# Share page perfected — `/s/<code>`

Goal: make the public shared-trail viewer (1) not lag, (2) look like the extension's
graph, (3) use the best shadcn primitives, (4) fix the "can't import your own trail"
one-line bug, (5) make "Import to my Trail" open the sidepanel with a confirmation
prompt instead of blindly importing.

## Root-cause diagnosis
- Marketing shadcn primitives reference standard tokens (`--card`, `--muted`, `--border`,
  `--ring`, `--accent`, `--secondary`, `--destructive`, `--input`) that are **not defined**
  in `globals.css` (bespoke ember palette only). `bg-card` → transparent,
  `text-muted-foreground` → full-bright → share graph looks flat/unstyled.
- Share graph omits the extension's documented anti-lag techniques (`graph--panning`
  pointer-events kill, per-node `contain: layout style`, CSS-LOD, isolated Background).
  `panOnScroll` → every node toggles `:hover` transitions per pan frame → lag. 2349-node
  trails exist.
- Self-import bug: `page.tsx` renders the helper `<p>` as a flex-row sibling of the button;
  terminal states ("can't import your own trail") sit beside the helper → contradictory
  one-liner.

## Plan (A→B→C→D→E in marketing, then F across extension+marketing)

- [ ] **A. Token foundation** — add standard shadcn tokens to `globals.css :root` mapped to
      ember palette; `--color-border` → `--border-subtle` (matches existing `*` base rule).
      Expose via `@theme inline`. Don't touch button/input/avatar.
- [ ] **B. Primitives** — add `ui/card.tsx` + `ui/badge.tsx` (v0-style, forwardRef + cn).
- [ ] **C. Node fidelity** — rewrite share graph node = extension TrailNode: shadcn Card
      `min-h-[60px] w-[160px]` flex-row, Globe (favicons stripped), title+url, Pin badge,
      current-node ring, hover-lift, matching edges + dotted bg.
- [ ] **D. Anti-lag** — `contain: layout style`, `graph--panning` kill, CSS-LOD + tiny zoom
      subscriber, drag-to-pan + ctrl/pinch zoom (no scroll hijack), isolated Background.
- [ ] **E. Self-import bug** — move helper copy into button idle state; drop sibling `<p>`.
- [ ] **F. Import prompt** — button stashes code + opens panel (no blind import); extension
      handler stashes+opens for both auth states; `consumePendingShareImport` stops
      auto-importing (prompt is sole consumer); sidepanel prompt component + hook.

## Verify
- [ ] typecheck marketing + extension; build marketing (flush Tailwind v4 tokens); tests;
      landing spot-check; trace F flow.

## Review

**Done (all workstreams):**
- **A.** Wired the full shadcn token set into `globals.css` (`:root` raw tokens + `@theme inline`
  `--color-*`), mapped onto the ember palette. `--border`→`--border-subtle` (matches the
  existing `*` base rule → no landing shift). Built CSS confirms `--card`/`--muted-foreground`/
  `--border`/`--ring`/`--destructive` now emit and `bg-card`/`bg-muted`/`text-muted-foreground`/
  `ring-primary` utilities are generated (they weren't before — that was the "unstyled" cause).
- **B.** Added `ui/card.tsx` + `ui/badge.tsx`, ported from the extension (Slot import +
  radius adapted for marketing). Left button/input/avatar untouched.
- **C.** Rewrote the graph node to mirror the extension's TrailNode: shadcn Card `160×60`,
  Globe (favicons stripped for privacy), title link + `text-[6px]` URL, Pin badge for pinned,
  `ring-primary` on the snapshot's current node, hover-lift. `tree-layout` dims → 160×60.
- **D.** Ported the extension's anti-lag stack into `share-graph.css`: `contain: layout style`,
  `share-graph--panning` pointer-events kill, CSS-LOD via `data-lod` + a tiny `LodSync` zoom
  subscriber, isolated `GraphBackground`. Swapped `panOnScroll` (page-scroll hijack) → drag-to-pan
  + Cmd/Ctrl-wheel + pinch zoom (`useCmdWheelZoom`).
- **E.** Self-import one-line bug fixed: the generic helper `<p>` was a flex-row sibling of the
  button; moved the copy into the button's idle state so terminal states replace it. (The "self"
  state is gone from the page entirely — see F.)
- **F.** "Import to my Trail" now opens the sidepanel with a confirmation prompt instead of
  blind-importing. Bridge queues the code (+label/nodeCount hints) and opens the panel;
  `share-from-site-handler` no longer imports inline; `consumePendingShareImport` auto-import
  removed (prompt is sole consumer; per-user wipe still clears the slot); new `ShareImportPrompt`
  (sidepanel) confirms → `treeService.importSharedTrail` (new proxy method) → import + sync pull.
  Self-import / unavailable / sign-in now surface in the prompt, which knows the user's identity.

**Verified:** marketing typecheck ✓, marketing build ✓ (tokens emit), marketing tests 11/11 ✓,
extension typecheck ✓, extension tests 160/160 ✓, lint clean on all changed files. Landing
unaffected (no landing component consumes the new tokens; `--border` unchanged).

**Pre-existing (not mine):** `eslint .` flags `app/components/landing/Hero.tsx:37`
(`react-hooks/set-state-in-effect`) — untouched by this work (no diff vs main).

**Not done (out of scope / can't run here):** live click-through of the full extension↔page
import flow (needs a browser + loaded extension + real share code); reasoned through instead.
