# Lessons Learned

## 2026-02-26: Always use Agent Teams, not parallel subagents
- **Mistake**: User explicitly asked for Agent Teams (TeamCreate + Task tool with team_name). I launched regular parallel subagents (Task tool without team_name) for UI research instead.
- **Rule**: When user says "agent team" / "команда агентов" — ALWAYS use TeamCreate, TaskCreate, Task with team_name/name params, SendMessage. Never fall back to regular subagents.
- **Why**: Agent Teams allow agents to communicate with each other via SendMessage, share a task list, and coordinate. Regular subagents are isolated and can't talk to each other.
