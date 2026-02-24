# Feature Flags / A-B Toggles System — Design Plan

**Status**: Plan review  
**Date**: 2026-02-22

---

## Decision: Library vs. Internal

**Internal solution, no library.** Reasoning:

- Feature flag SaaS (LaunchDarkly, Flagsmith, etc.) assumes server-side evaluation and network calls — wrong model for a local Chrome extension.
- The extension already has an established pattern for typed storage (`SettingsManager`), RPC contracts, and Zustand hydration. Flags should follow the exact same architecture.
- Total implementation is ~200 lines of typed code. A library adds dependency weight, API surface, and a removal cost that exceeds the effort of writing it.
- Fallback if we ever need remote flags: swap the storage backend from `chrome.storage.local` to a fetch-from-server layer. The consumer API stays identical.

---

## 1. Data Model

### Core principle: **definitions in code, overrides in storage**

Flag definitions (types, defaults, metadata) live in source code. Storage only persists user overrides. This means:

- Adding a new flag = one line in the registry. Zero migration.
- Removing a flag = delete the line. Stale overrides are silently ignored.
- Defaults are always code-defined and type-safe.

```typescript
// src/shared/types/flags.ts

type BooleanFlagDef = {
  type: 'boolean';
  default: boolean;
  label: string;
  description: string;
};

type VariantFlagDef<V extends string = string> = {
  type: 'variant';
  default: V;
  variants: readonly V[];
  label: string;
  description: string;
};

type FlagDef = BooleanFlagDef | VariantFlagDef;

// ── Registry (single source of truth) ──

const FLAG_DEFS = {
  fullView: {
    type: 'boolean',
    default: false,
    label: 'Full View',
    description: 'Show the "Open full view" button and enable fullview.html.',
  },
  // Future examples:
  // newRenderer: { type: 'boolean', default: false, label: '...', description: '...' },
  // searchMode: { type: 'variant', default: 'fuzzy', variants: ['fuzzy', 'exact', 'semantic'], label: '...', description: '...' },
} as const satisfies Record<string, FlagDef>;

type FlagKey = keyof typeof FLAG_DEFS;

// Derived types — value type is inferred from the definition:
// - boolean flags → boolean
// - variant flags → union of their variant literals
type FlagValue<K extends FlagKey> = ...;

// Resolved snapshot: { fullView: false, ... }
type ResolvedFlags = { [K in FlagKey]: FlagValue<K> };
```

### Storage schema

```typescript
// chrome.storage.local key: 'trail_flags'
type PersistedFlagState = {
  v: 1;                                    // schema version for future migration
  overrides: Partial<Record<string, unknown>>; // only non-default values
};
```

- Separate key from `trail_settings` — flags and settings have different lifecycles.
- `chrome.storage.local` (not sync) — experiments are per-installation.
- `v: 1` for future-proofing. Today: ignored. Tomorrow: migration path.

---

## 2. API Layer

### Background service: `FlagManager`

Mirrors `SettingsManager` pattern exactly:

```
src/background/services/flags.ts     — FlagManager class
src/shared/types/flags.ts            — types + FLAG_DEFS registry
```

```typescript
class FlagManager {
  private overrides: Record<string, unknown> = {};

  async init(): Promise<void>;                           // load from storage
  
  get<K extends FlagKey>(key: K): FlagValue<K>;          // resolve: override ?? default
  isEnabled(key: BooleanFlagKey): boolean;               // sugar for boolean flags
  
  getAll(): ResolvedFlags;                               // full resolved snapshot
  
  async setOverride<K extends FlagKey>(key: K, value: FlagValue<K>): Promise<void>;
  async resetOverride(key: FlagKey): Promise<void>;
  async resetAll(): Promise<void>;
}

export const flagManager = new FlagManager();
```

### RPC contracts

Add to `contracts.ts`:

| Method | Input | Response |
|--------|-------|----------|
| `GET_FLAGS` | — | `ResolvedFlags` |
| `SET_FLAG` | `{ key: FlagKey, value: unknown }` | `ResolvedFlags` |
| `RESET_FLAGS` | — | `ResolvedFlags` |

Three methods is sufficient. No `RESET_FLAG` for single key — YAGNI for now. `SET_FLAG` with the default value has the same effect.

### Sidepanel API

```
src/sidepanel/api/flags.ts
```

```typescript
export async function getFlags(): Promise<ResolvedFlags> { ... }
export async function setFlag(key: FlagKey, value: unknown): Promise<ResolvedFlags> { ... }
export async function resetFlags(): Promise<ResolvedFlags> { ... }
```

### React consumption

```
src/sidepanel/ui/hooks/useFlags.ts
```

Two patterns, both thin:

```typescript
// Option A: from Zustand store (hydrated at boot alongside settings)
const flags = useStore(s => s.flags);
const fullViewEnabled = flags?.fullView ?? false;

// Option B: standalone hook (if we want flags outside the main store)
function useFlag<K extends FlagKey>(key: K): FlagValue<K>;
```

**Recommendation: Option A** — add `flags: ResolvedFlags | null` to the existing Zustand store, hydrate alongside settings on panel open. This is consistent with how settings already work and avoids a parallel state system.

---

## 3. UX: Hidden Menu Access

### Unlock mechanism: **settings gear rapid-click (7×) + keyboard shortcut**

**Primary — 7 rapid clicks on the settings gear icon:**
- Matches the Android "Developer Options" pattern — universally understood by power users.
- On 7th click within 3 seconds, unlock the Experiments section.
- Show a brief toast: "Experiments unlocked".
- Unlock state persisted in `chrome.storage.local` (`trail_flags_unlocked: true`) so it survives restarts.

**Secondary — keyboard shortcut:**
- `Ctrl+Shift+.` (or `Cmd+Shift+.` on Mac) while settings popover is open.
- Toggles the Experiments section visibility.

### Where it lives: **bottom of SettingsPopover**

- Rendered as a new section at the bottom of `SettingsDropdown` in `SettingsPopover.tsx`.
- Only shown when unlocked.
- Separated by a dashed `<hr>` to visually distinguish from normal settings.
- Each flag rendered as a toggle (boolean) or segmented control (variant), using the existing `Seg` component.
- "Reset all" button at the bottom.
- Label: "experiments" (lowercase, matching existing section labels like "layout mode", "dashboard").

Why not a separate overlay:
- The settings dropdown already has the scroll, keyboard handling, and overlay infrastructure.
- Adding a separate overlay means duplicating that code. The experiments section is a natural extension.
- If it ever grows too large, we can move it to a sub-panel (like "theme studio" already does).

---

## 4. Gating the Full View Feature

### Button visibility (`GraphZoomControls.tsx`)

```tsx
// Before: always shown
<button onClick={onOpenFullView}>...</button>

// After: conditionally rendered
{flags.fullView && (
  <button onClick={onOpenFullView}>...</button>
)}
```

Pass flags down from `GraphCanvas.tsx` (which already reads from the store), or read directly from the store in `GraphZoomControls`.

### The `fullview.html` page itself

The page is always included in the build (WXT entrypoint). Two options:

- **Option A**: Do nothing — if someone navigates to `fullview.html` directly while the flag is off, they get the full app. This is fine; they're clearly a developer.
- **Option B**: Check the flag on fullview mount and show a "Feature not available" screen.

**Recommendation: Option A.** The flag's purpose is UX gating (hide the button from normal users), not security. Anyone who types `chrome-extension://…/fullview.html` deserves what they get.

### Background-side gating

Not needed. There's no background handler for "open full view" — the sidepanel opens it directly via `chrome.tabs.create`. The button gate is sufficient.

---

## 5. Testing Strategy & Rollout Safety

### Unit tests

- `FlagManager` in isolation: defaults, overrides, reset, unknown keys ignored, type safety.
- Can run with the existing `node --import tsx tests/basic.test.ts` pattern.

### Manual QA checklist

- [ ] Settings gear 7-click unlock shows experiments section
- [ ] Toggle fullView flag → button appears/disappears in zoom controls
- [ ] Flag state survives extension restart
- [ ] Resetting all flags returns to defaults
- [ ] New flag added to registry appears in UI without migration

### Rollout safety

- All flags default to `false` / conservative value → no behavior change for existing users.
- Flags are **local-only** — no server-side rollout to manage.
- The `v: 1` schema version allows future migration if we change flag shapes.
- If we ever want remote flag control: add a `fetchRemoteOverrides()` that merges server values with local overrides. The consumer API doesn't change.

---

## 6. File Changes Summary

| File | Change |
|------|--------|
| `src/shared/types/flags.ts` | **New** — flag types, registry, resolved types |
| `src/background/services/flags.ts` | **New** — `FlagManager` class |
| `src/shared/rpc/contracts.ts` | Add `GET_FLAGS`, `SET_FLAG`, `RESET_FLAGS` methods |
| `src/background/messaging/handlers/flags-handlers.ts` | **New** — RPC handlers |
| `src/background/messaging/handlers/index.ts` (or equivalent) | Register flag handlers |
| `src/sidepanel/api/flags.ts` | **New** — sidepanel API |
| `src/sidepanel/ui/state/store.ts` | Add `flags: ResolvedFlags \| null` + setter |
| `src/sidepanel/ui/components/SettingsPopover.tsx` | Add experiments section + unlock logic |
| `src/sidepanel/ui/components/graph/GraphZoomControls.tsx` | Conditional full-view button |
| `src/sidepanel/ui/components/graph/GraphCanvas.tsx` | Pass flags / read from store |

~10 files touched, ~200-300 lines of new code. Zero external dependencies.

---

## Resolved Questions

1. **Unlock persistence**: Persists across extension updates. Stored in `chrome.storage.local` as `trail_flags_unlocked`.
2. **Full view default**: `false`. Button hidden until user enables via experiments.
3. **Flag change broadcast**: No broadcast. Refresh-to-pick-up-changes. Acceptable for experiments.

## Implementation Status: COMPLETE

### Files created
- [x] `src/shared/types/flags.ts` — Flag types, registry, resolveFlags()
- [x] `src/background/services/flags.ts` — FlagManager class
- [x] `src/background/messaging/handlers/flags-handlers.ts` — RPC handlers
- [x] `src/sidepanel/api/flags.ts` — Sidepanel API

### Files modified
- [x] `src/shared/rpc/contracts.ts` — Added GET_FLAGS, SET_FLAG, RESET_FLAGS
- [x] `src/background/messaging/router.ts` — Registered flagsHandlers
- [x] `src/sidepanel/ui/state/store.ts` — Added flags state + setFlags action
- [x] `src/sidepanel/ui/hooks/useBootstrap.ts` — Hydrates flags on boot
- [x] `src/sidepanel/ui/components/SettingsPopover.tsx` — 7-click unlock + experiments section
- [x] `src/sidepanel/ui/components/graph/GraphZoomControls.tsx` — Conditional full-view button
- [x] `src/sidepanel/ui/components/graph/GraphCanvas.tsx` — Passes fullViewEnabled prop
- [x] `src/sidepanel/ui/components/graph/GraphArea.tsx` — Reads flags from store
- [x] `src/sidepanel/ui/styles/settings-popover.css` — Experiments section styles

### TypeScript: Clean (only pre-existing errors in TreeDropdown.tsx and oauth-auth-handlers.ts)
