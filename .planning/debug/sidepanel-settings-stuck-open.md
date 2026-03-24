---
status: investigating
trigger: "sidepanel-settings-stuck-open — settings panel is automatically open, settings button shifted, cannot close settings"
created: 2026-03-20T00:00:00Z
updated: 2026-03-20T00:00:00Z
---

## Current Focus

hypothesis: Prettier reformatting in commit 4308d970 stripped the leading space from two conditional class name template literals, breaking CSS class matching for both settings-dropdown visibility and floating-controls compact mode.
test: Confirmed by diffing commit 4308d970 for both affected files.
expecting: Restoring the leading space fixes all three reported symptoms.
next_action: AWAITING HUMAN DECISION — root cause confirmed, ready to fix.

## Symptoms

expected: Settings closed by default; settings button in correct position; clicking settings button toggles open/closed.
actual: Settings panel is always visible (stuck open). Settings button position may be affected. Cannot close settings.
errors: None
reproduction: Open sidepanel — settings immediately visible and cannot be closed.
started: After commit 4308d970 (docs/prettier reformatting, Thu Mar 19 2026)

## Eliminated

- hypothesis: State initialization bug in store (settingsOpen starts as true)
  evidence: store.ts line 292 — ui.settingsOpen initializes to false
  timestamp: 2026-03-20

- hypothesis: setSettingsOpen toggle logic broken
  evidence: store.ts lines 540-545 — toggle logic is correct
  timestamp: 2026-03-20

- hypothesis: CSS .settings-dropdown.hidden rule missing
  evidence: settings-popover.css lines 47-56 — rule exists and is correct
  timestamp: 2026-03-20

## Evidence

- timestamp: 2026-03-20
  checked: SettingsPopover.tsx line 287 (current)
  found: className={`settings-dropdown${settingsOpen ? "" : "hidden"}`}
  implication: When settingsOpen=false, class resolves to "settings-dropdownhidden" — not "settings-dropdown hidden". The CSS rule .settings-dropdown.hidden never matches, so the panel is always visible.

- timestamp: 2026-03-20
  checked: commit 4308d970 diff for SettingsPopover.tsx
  found: Before: `settings-dropdown${settingsOpen ? '' : ' hidden'}` → After: `settings-dropdown${settingsOpen ? "" : "hidden"}`
  implication: Prettier reformatted single quotes to double quotes AND removed the leading space from ' hidden', making the class concatenation incorrect.

- timestamp: 2026-03-20
  checked: FloatingControls.tsx line 91 (current)
  found: className={`floating-controls${controlsCompact ? "is-compact" : ""}`}
  implication: Same bug pattern. When compact, class resolves to "floating-controlsis-compact" instead of "floating-controls is-compact". The .floating-controls.is-compact CSS rules never fire.

- timestamp: 2026-03-20
  checked: commit 4308d970 diff for FloatingControls.tsx
  found: Before: `floating-controls${controlsCompact ? ' is-compact' : ''}` → After: `floating-controls${controlsCompact ? "is-compact" : ""}`
  implication: Same prettier issue — leading space stripped from ' is-compact'.

- timestamp: 2026-03-20
  checked: Other dropdowns in commit 4308d970 (pinned-dropdown, trees-dropdown, tag-filter-dropdown, search-results)
  found: These all have the space in the BASE string e.g. `"pinned-dropdown "` — so they were unaffected by prettier reformatting.
  implication: Only settings-dropdown and floating-controls were affected because their leading space was inside the conditional expression, not the base string.

## Resolution

root_cause: commit 4308d970 (prettier reformatting) stripped the leading space from two conditional class name template literals:
  1. SettingsPopover.tsx: `settings-dropdown${settingsOpen ? '' : ' hidden'}` → `settings-dropdown${settingsOpen ? "" : "hidden"}` — class becomes "settings-dropdownhidden" when closed, CSS rule never fires, panel always visible
  2. FloatingControls.tsx: `floating-controls${controlsCompact ? ' is-compact' : ''}` → `floating-controls${controlsCompact ? "is-compact" : ""}` — class becomes "floating-controlsis-compact", compact mode CSS rules never fire

fix: (not yet applied)
  File 1: extension/src/apps/sidepanel/ui/components/SettingsPopover.tsx, line 287
    Change: className={`settings-dropdown${settingsOpen ? "" : "hidden"}`}
    To:     className={`settings-dropdown${settingsOpen ? "" : " hidden"}`}
    (restore the leading space before "hidden")

  File 2: extension/src/apps/sidepanel/ui/components/FloatingControls.tsx, line 91
    Change: className={`floating-controls${controlsCompact ? "is-compact" : ""}`}
    To:     className={`floating-controls${controlsCompact ? " is-compact" : ""}`}
    (restore the leading space before "is-compact")

verification: empty
files_changed: []
