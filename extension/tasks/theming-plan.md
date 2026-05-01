# Theming — Phase 1 Plan (v2)

> Started: 2026-04-26
> Goal: pick a color theme at runtime + add the missing light/dark/system mode picker. Live swap, no reload, syncs across devices via existing `Settings`/Supabase pipeline.
> v1 of this plan was wrong (assumed next-themes would be a new dep, missed that it's already wired). This document supersedes it.
> Phase 2 (separate plan, not now): user-picked accent color, custom theme editor, import/export, sushify themes.

---

## Existing architecture (verified, not assumed)

- **next-themes is already in use.** [ui/providers/theme-provider.tsx](../src/ui/providers/theme-provider.tsx) wraps all three apps via [bootstrap.tsx](../src/ui/panel/bootstrap.tsx) (sidepanel) and [settings/main.tsx](../src/entrypoints/settings/main.tsx), [login/main.tsx](../src/entrypoints/login/main.tsx). Config: `attribute="class"`, `storageKey="trail_theme_choice"`, `enableSystem`.
- **Settings → next-themes bridge already exists**: [useThemeSync.ts](../src/apps/sidepanel/ui/hooks/useThemeSync.ts) — `Settings.theme` is canonical, next-themes mirrors. Currently called only in sidepanel `App.tsx`.
- **MV3-CSP-compliant FOUC script**: [public/apply-theme-early.js](../public/apply-theme-early.js) reads `localStorage["trail_theme_choice"]` synchronously before React, sets `<html class="dark">` and `style.colorScheme`/`backgroundColor`.
- **All three apps share one `tailwind.css`** via `main.tsx → @ui/panel/styles.css → sidepanel.css → tailwind.css`.
- **Current `:root`/`.dark` blocks in `tailwind.css`** hold the user's manual tweakcn green theme (radix-maia style + green primary `oklch(0.8348 0.1302 160.9080)`). This becomes the implicit "Default" preset.
- **`Settings.theme` field exists, normalized, read by `useThemeSync` — but never written.** No UI for it. User confirmed: add the missing UI as part of this scope.
- **`settingsItem.watch(...)`** is currently used **only** in [background/services/settings.ts:185](../src/background/services/settings.ts#L185); UI never subscribes. We will introduce the pattern. Backed by `chrome.storage.local`, propagation across extension contexts is native — but unverified in this codebase. Verify experimentally during dev (changing preset on settings page must reflect in open sidepanel within 1s).

## Source format findings (verified, not assumed)

- **tweakcn-theme-picker** ships per-theme `.css` files in [registry/themes/](https://github.com/BankkRoll/tweakcn-theme-picker/tree/main/registry/themes), 44 themes. Selectors: `[data-theme="<name>-light"]` and `[data-theme="<name>-dark"]`. Full shadcn variable set + chart/sidebar/shadow/font tokens. **Drop-in after a mechanical regex selector rewrite.**
- **sushify** uses bare `:root`/`.dark` selectors + its own `@theme` block + `@utility` Tailwind extensions + extra variables (`--color-success`, `--highlight`). **Not drop-in**, would conflict with current `tailwind.css`. Deferred.

---

## Architecture decision

Two orthogonal channels on `<html>`:

| Channel | Owner | DOM target | Source of truth |
|---|---|---|---|
| Mode (light/dark/system) | next-themes | `class="dark"` (or absent) | `Settings.theme` via `useThemeSync` |
| Preset (palette) | Trail (new) | `data-theme="supabase"` | `Settings.themePreset` via `useThemePresetSync` (NEW) |

CSS pattern after vendoring + rewrite:

```css
:root[data-theme="supabase"] { --primary: oklch(...); /* light vars */ }
.dark[data-theme="supabase"] { --primary: oklch(...); /* dark vars */ }
```

- "Default" preset = no `data-theme` attribute → tailwind.css `:root`/`.dark` blocks drive (current user's green look preserved).
- next-themes' [issue #292](https://github.com/pacocoursey/next-themes/issues/292) (single-class limitation) does not bite: we use a separate attribute, not a second class.
- Selector specificity: `:root[data-theme=X]` and `.dark[data-theme=X]` both weigh `0,2,0` — tie. Light blocks must be written before dark blocks in the concatenated CSS so cascade order resolves dark over light when both could apply (e.g., during transitions). Order in `theme-presets.css`: for each preset, light block first, then dark.

---

## Plan

### 1. Data model — `Settings.themePreset`

- [ ] Add `themePreset: string` field to `Settings` in `shared/types/settings.ts`.
- [ ] Default: `"default"`.
- [ ] In `mergeDefaults` ([background/services/settings.ts](../src/background/services/settings.ts)): if missing or not a known id, fall back to `"default"`. Validate against the curated list.

### 2. Vendor + rewrite preset CSS

- [ ] Fetch the 10 curated themes from `https://raw.githubusercontent.com/BankkRoll/tweakcn-theme-picker/main/registry/themes/<name>.css`:
  - graphite, mono, catppuccin, vercel, claude, supabase, ocean-breeze, t3-chat, claymorphism, doom-64
- [ ] For each: regex rewrite selectors:
  - `[data-theme="<name>-light"]` → `:root[data-theme="<name>"]`
  - `[data-theme="<name>-dark"]` → `.dark[data-theme="<name>"]`
- [ ] Concatenate to `extension/src/apps/sidepanel/ui/theme-presets.css`. Order: `<name>` light block then dark block, repeated.
- [ ] Add `@import "./theme-presets.css";` in `sidepanel.css`.
- [ ] Measure `.output/chrome-mv3` chunk sizes after build. If theme CSS pushes a chunk over a hard threshold (TBD, judgment call), trim further or split out to a lazily-loaded sheet.

### 3. Preset list metadata

- [ ] `extension/src/shared/styles/theme-presets.ts` — minimal:
  ```ts
  export type ThemePresetMeta = { id: string; name: string };
  export const THEME_PRESETS: ThemePresetMeta[] = [
    { id: "default", name: "Default" },
    { id: "graphite", name: "Graphite" },
    // ...
  ];
  ```
  Used by the picker UI. Actual CSS lives in `theme-presets.css`.

### 4. Sync hook — `useThemePresetSync`

- [ ] New hook `extension/src/apps/sidepanel/ui/hooks/useThemePresetSync.ts`:
  - Reads `settings.themePreset` from store.
  - Effect: set `documentElement.dataset.theme = preset` (or remove the attribute if preset is `"default"`).
  - Effect: mirror to `localStorage["trail_theme_preset"]` for FOUC.
- [ ] Call it in:
  - [apps/sidepanel/ui/App.tsx](../src/apps/sidepanel/ui/App.tsx) — next to `useThemeSync()`.
  - Settings and login apps need the same mirror. Decide: factor out the store/settings subscription into a small shared hook callable from all three apps, OR add `useThemePresetSync()` calls in their components. Prefer the former — read the existing pattern and replicate.

### 5. FOUC — extend `apply-theme-early.js`

- [ ] In [public/apply-theme-early.js](../public/apply-theme-early.js): also read `localStorage["trail_theme_preset"]` and set `documentElement.dataset.theme = preset` synchronously (skip if `"default"`/missing).
- [ ] Update header comment with the new key name.

### 6. UI — `AppearancePage`

Two new fields (top grid alongside layout/density/truncation):

- [ ] **Mode picker** (NEW — fixes the missing UI for `Settings.theme`):
  - `<Select>` bound to `settings.theme`, options: light / dark / system.
  - Calls `onUpdate({ theme: v })`.
  - i18n keys: `settings.appearance.modeLabel`, `settings.appearance.modeLight/Dark/System`.
- [ ] **Theme preset picker**:
  - `<Select>` bound to `settings.themePreset`, options from `THEME_PRESETS`.
  - Calls `onUpdate({ themePreset: v })`.
  - i18n key: `settings.appearance.themePresetLabel`.
- [ ] Add all keys to both `locales/en.json` and `locales/ru.json`.

### 7. Test/preview fixtures

- [ ] [tests/graph-layout.test.ts](../tests/graph-layout.test.ts): add `themePreset: "default"` to DEFAULT_SETTINGS.
- [ ] [preview/fake-tree.ts](../preview/fake-tree.ts): add `themePreset: "default"` to `fakeSettings()`.
- [ ] (Pre-existing drift in those files re: `privacy.collapselist`/`trackedSchemes`/`cleanup` — out of scope for this work.)

### 8. Verify

- [ ] `pnpm -C extension typecheck` — clean.
- [ ] `pnpm -C extension build` — clean. Note bundle size delta.
- [ ] **Manual smoke (must pass before declaring done)**:
  - Open settings page → pick "supabase" → sidepanel (already open) reflects within ~1s. *Verifies cross-context propagation.*
  - Pick "Default" → revert to current green tailwind.css look.
  - Switch mode (light/dark/system) → palette stays consistent within selected preset.
  - Reload sidepanel after picking non-default preset → no flash of default colors before preset paints. *Verifies FOUC mirror.*

---

## Open risks (accepted)

- **Cross-context propagation unverified.** No existing UI subscribes to `settingsItem.watch(...)`. Native `chrome.storage.onChanged` should propagate, but verify via smoke test. Fallback: explicit message-passing or window-focus reload.
- **Bundle size.** 10 themes ≈ 30–40 KB CSS uncompressed. Acceptable but measured at step 8.
- **No accessibility check.** Some tweakcn presets may have weak contrast (e.g., neon, bubblegum). Curated 10 are leaner; if any is unreadable in dark mode, drop and replace.

## Phase 2 (deferred)

- User-picked accent (`react-colorful` + `culori` for OKLCH derivation).
- Custom theme save (`Settings.customThemes`), JSON import/export.
- Add sushify themes (requires AST/regex normalizer).
- Live preview swatch in the picker.

## Process

- **Foreground only**, file by file. No background agents — that pattern got the v1 plan wrong.
- After each step, show the diff and confirm before continuing.
- Plan changes go through this file first, code second.

## Status

- 2026-04-26: plan v2 written. Approved.
- 2026-04-26: Phase 1 implemented (steps 1–8). Typecheck clean, build clean (5.2s, 2.73 MB total). Awaiting manual smoke test in browser.

### Files added
- `extension/src/shared/styles/theme-presets.ts` — preset id/name catalog + validator.
- `extension/src/apps/sidepanel/ui/theme-presets.css` — vendored CSS, 9 themes, ~42 KB.
- `extension/src/apps/sidepanel/ui/hooks/useThemePresetSync.ts` — DOM `data-theme` writer.

### Files modified
- `extension/src/shared/types/settings.ts` — `themePreset: string` field.
- `extension/src/background/services/settings.ts` — default + normalizer with `isKnownPresetId` validation.
- `extension/src/apps/sidepanel/ui/hooks/useThemeSync.ts` — refactored to take `theme` argument.
- `extension/src/apps/sidepanel/ui/App.tsx` — call sites updated, both hooks wired.
- `extension/src/apps/settings/SettingsApp.tsx` — both hooks wired (was missing entirely).
- `extension/src/apps/sidepanel/ui/sidepanel.css` — `@import "./theme-presets.css"`.
- `extension/src/apps/settings/pages/AppearancePage.tsx` — Theme section with mode + preset selectors.
- `extension/public/apply-theme-early.js` — reads `trail_theme_preset` from localStorage and sets `data-theme` synchronously to prevent FOUC.
- `extension/src/locales/en.json`, `ru.json` — 7 new keys under `settings.appearance`.
- `extension/tests/graph-layout.test.ts`, `extension/preview/fake-tree.ts` — `themePreset: "default"` in fixtures.

### Manual smoke test (run before declaring done)
- Open Settings → Appearance: Theme section with Mode and Color Theme selects appears.
- Change Mode to Dark / Light / System — entire UI flips immediately.
- Change Color Theme through each preset — palette swaps live.
- Change preset on Settings page → open sidepanel: should reflect (via React Query refetch on remount or storage event).
- Reload sidepanel after picking a non-default preset — no flash of green-default before preset paints.
