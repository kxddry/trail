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
