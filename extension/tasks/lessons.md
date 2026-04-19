# Lessons Learned — Trail Extension

## 2026-04-16: `exactOptionalPropertyTypes` incompatible with shadcn/Radix prop patterns
- **Mistake**: Enabled `exactOptionalPropertyTypes: true` alongside shadcn/Radix components. Radix passes optional props through spread where target types expect non-optional — causes TS2375 on calendar, context-menu, dropdown-menu, menubar, slider, sonner.
- **Rule**: Keep `strict: true` and `noUncheckedIndexedAccess: true`, but turn off `exactOptionalPropertyTypes` when using shadcn/Radix. Document the trade-off in a tsconfig comment.
- **Why**: shadcn rule of "never modify base component files" means we can't fix the issue at the component layer. Disabling the one compiler knob preserves 95% of strictness.

## 2026-04-18: Auth-state broadcasts can unmount the form that needs to stay mounted
- **Mistake**: Wired password recovery as `verifyOtp(type:"recovery")` → setStage("set-password"). Supabase issues a real session on recovery OTP verify, `notify({status:"signed-in"})` fires synchronously, the parent re-renders into the signed-in branch, and SignInPanel unmounts before the user ever sees the new-password form — leaving the old password active.
- **Rule**: When a multi-step flow depends on a transient auth state, gate the global broadcast. Added `recoveryInProgress` + `pendingRecoveryIdentity` in the orchestrator that suppresses signed-in broadcasts until `updatePassword` completes (or UI cancels via `cancelPasswordRecovery()` on unmount / "use a different email").
- **Why**: State machines that span multiple components must own their lifetime explicitly; "the listener will sort it out" is wishful thinking.

## 2026-04-18: `signInWithOtp({ shouldCreateUser:false })` leaks account existence by default
- **Mistake**: Original orchestrator JSDoc claimed Supabase silently succeeds for non-existent emails. False — modern Supabase returns `user_not_found` / `signups_disabled` errors which `toUserError` would surface in the UI, confirming or denying account existence.
- **Rule**: For auth endpoints with anti-enumeration semantics, swallow specific "user-not-found-class" errors in the orchestrator and always return success to the UI. Surface only true infra errors (network, rate limit). Same applies to `resetPasswordForEmail`.
- **Why**: "Very secure" requires defending against account enumeration even if the attacker has email lists; the whole password-strength story is moot otherwise.

## 2026-04-16: Dead refs/selectors silently break UX without crashes
- **Mistake**: `OnboardingHints` referenced `#searchBtn` selector that no longer existed in the DOM; `focusSearch()` pointed at a `searchInputRef` that was never rendered. No runtime error — just broken ⌘K with no feedback.
- **Rule**: When removing a UI element, grep for DOM selectors (`#id`, `[data-*]`) and ref hooks that targeted it. If the feature is deferred, delete the orphan code path entirely rather than leave it pointing at nothing.
- **Why**: Silent UX breakage is harder to spot than a loud error. Better to delete now and rebuild in a later wave than leave a broken feature available via shortcut.
