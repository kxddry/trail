# Lessons Learned — Trail Extension

## 2026-04-16: `exactOptionalPropertyTypes` incompatible with shadcn/Radix prop patterns
- **Mistake**: Enabled `exactOptionalPropertyTypes: true` alongside shadcn/Radix components. Radix passes optional props through spread where target types expect non-optional — causes TS2375 on calendar, context-menu, dropdown-menu, menubar, slider, sonner.
- **Rule**: Keep `strict: true` and `noUncheckedIndexedAccess: true`, but turn off `exactOptionalPropertyTypes` when using shadcn/Radix. Document the trade-off in a tsconfig comment.
- **Why**: shadcn rule of "never modify base component files" means we can't fix the issue at the component layer. Disabling the one compiler knob preserves 95% of strictness.

## 2026-04-16: Dead refs/selectors silently break UX without crashes
- **Mistake**: `OnboardingHints` referenced `#searchBtn` selector that no longer existed in the DOM; `focusSearch()` pointed at a `searchInputRef` that was never rendered. No runtime error — just broken ⌘K with no feedback.
- **Rule**: When removing a UI element, grep for DOM selectors (`#id`, `[data-*]`) and ref hooks that targeted it. If the feature is deferred, delete the orphan code path entirely rather than leave it pointing at nothing.
- **Why**: Silent UX breakage is harder to spot than a loud error. Better to delete now and rebuild in a later wave than leave a broken feature available via shortcut.
