# Lessons Learned

## 2026-02-26: Always use Agent Teams, not parallel subagents
- **Mistake**: User explicitly asked for Agent Teams (TeamCreate + Task tool with team_name). I launched regular parallel subagents (Task tool without team_name) for UI research instead.
- **Rule**: When user says "agent team" / "команда агентов" — ALWAYS use TeamCreate, TaskCreate, Task with team_name/name params, SendMessage. Never fall back to regular subagents.
- **Why**: Agent Teams allow agents to communicate with each other via SendMessage, share a task list, and coordinate. Regular subagents are isolated and can't talk to each other.

## 2026-03-04: Respect requested naming and flag semantics exactly
- **Mistake**: I kept `spotlight` naming and treated the flag as v1/v2 toggle, while the user required `recency` naming and `off = no feature`, `on = v2`.
- **Rule**: When a user specifies naming and rollout semantics, apply them literally across file names, symbols, flags, and behavior gates.
- **Why**: Naming and feature-gating semantics are part of product/API contracts; partial alignment causes confusing UX and stale persisted settings behavior.

## 2026-03-06: Separate committed selection from transient hover in preview UIs
- **Mistake**: Spotlight graph hover and result-list hover were sharing the same highlight/focus channel, so transient pointer movement triggered recentering and could clear the committed highlight on leave.
- **Rule**: In any preview UI with keyboard focus plus pointer hover, model committed selection and transient hover as separate states and only let committed selection drive camera/view intents.
- **Why**: Hover is ephemeral. If it shares state with committed focus, the UI jitters, loses restore semantics, and creates hard-to-reproduce interaction bugs.

## 2026-04-27: Account switching needs an explicit per-user state wipe
- **Mistake**: New-user registration on a browser that previously held a different signed-in account threw `new row violates row-level security policy (USING expression) for table "trails"`. `signOut` only cleared `authIdentityItem` and `provisionedUsersItem`; local trees, syncStateItem, pendingSyncOpsItem, deviceId, and tombstones survived. The next sign-in's first push hit `INSERT ... ON CONFLICT DO UPDATE` on rows owned by the previous user, so the UPDATE branch failed `USING (user_id = auth.uid())`.
- **Rule**: When a multi-tenant client persists user-scoped state across `signOut`, persist a `lastSignedInUserId` discriminator that survives sign-out, and on every sign-in compare it against the new user; if it differs, wipe every per-user bucket (trees, sync metadata, pending ops, device id, tombstones, undo history) BEFORE notifying listeners that the user is signed-in. Wipe order matters — wipe must complete before the sync engine sees `signed-in`, otherwise it'll backfill stale trees under the new `auth.uid()`. Match the wipe with a defensive 42501 handler in the sync push path that drops cached metadata for orphaned tree ids.
- **Why**: `auth.uid()` is per-session but local storage is per-browser. Without a discriminator, "same browser, different user" cases inherit prior tenant data. Postgres's RLS phrasing `(USING expression)` specifically signals the UPDATE branch of an upsert, which is the diagnostic tell that the row exists under a different `user_id` — distinct from a pure INSERT-with-CHECK failure.

## 2026-04-28: Don't translate JS identifiers when localising HTML
- **Mistake**: A localisation pass on `dashboard.ru.html` translated method names inside `<script>`: `replaceAll(...)` became `replaceВсе(...)` six times, throwing `TypeError: String(...).replaceВсе is not a function` at render. The catch block masked it as a generic "findings unavailable" — easy to misdiagnose as a fetch/CORS problem.
- **Rule**: Localisation passes on HTML must touch text nodes and known text-bearing attributes only. Identifiers, property accesses, method calls, JSON keys, CSS selectors, and `id`/`class` strings are part of the program — never translate them. Skip everything inside `<script>` and `<style>`.
- **Why**: The bug surfaces through a fallback path that looks like a network failure (load-error banner, "недоступны"), so the real cause stays hidden. Translating identifiers also breaks function-name references, event-handler attributes, and DOM lookups by id/selector.

## 2026-04-22: Confirm the product surface before reviewing "onboarding"
- **Mistake**: I interpreted "current onboarding flow" as the account web onboarding and reviewed the wrong surface before the user clarified they meant the extension onboarding.
- **Rule**: When a repo has multiple onboarding surfaces, first map every onboarding implementation in code and confirm the relevant surface from surrounding context before giving recommendations.
- **Why**: "Onboarding" is a product-wide concept, not a unique screen. Reviewing the wrong flow wastes time and produces misleading guidance even if the UX analysis itself is sound.

## 2026-05-27: Porting desktop gestures to a public web page — account for touch
- **Mistake**: Porting the extension graph's pan/zoom to the public `/s/<code>` share page, I mirrored the extension's `zoomOnPinch={false}` (it relies on `useCmdWheelZoom`, which is wheel-only). User corrected: `zoomOnPinch = true`. The extension is desktop-only (side panel), so it never needed real touchscreen pinch; a public web page can be opened on a tablet/touch laptop where pinch is a touch event the wheel handler can't catch.
- **Rule**: When porting interaction code from a desktop-only surface (extension/Electron) to a public web page, re-evaluate touch: enable `zoomOnPinch` (touchscreen pinch) and verify touch pan. Don't blindly copy the desktop prop set. Note that a capture-phase `useCmdWheelZoom` that `stopPropagation()`s the ctrlKey wheel on the container shields d3-zoom from the trackpad pinch, so enabling `zoomOnPinch` adds touch support without double-zoom on trackpads.
- **Why**: "Match the extension" optimizes for the desktop reference, but the share page's audience includes touch devices. Mirroring desktop-only choices silently drops mobile/tablet interactions.

## 2026-05-26: Use Opus 4.7 for subagents, not Sonnet
- **Mistake**: I spawned the share-page exploration and auth-trace subagents on Sonnet 4.6. User corrected: "opus 4.7 not sonnet 4.6".
- **Rule**: When spawning subagents (Agent tool) for this user, set `model="opus"` for any substantive investigation/research/audit. Never haiku, and default to Opus 4.7 over Sonnet for diagnostic work unless told otherwise.
- **Why**: The user prioritizes analysis quality on subtle bugs (e.g. auth-state races) over subagent speed/cost.
