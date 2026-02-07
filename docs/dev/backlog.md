# Trail Backlog (orchestrated)

> Single source of truth for autonomous work batches.
> Default flow: each item becomes a separate git worktree + branch + PR.

## Lanes
- **Marketing** (apps/marketing)
- **Extension** (extension/)
- **Account/API** (apps/account, apps/api, packages/*)
- **Infra/DX** (tooling, CI, lint/typecheck, migrations)

## Active batch (WIP)

### Marketing
- [ ] (TBD) 

### Extension
- [ ] URL normalization + merge duplicate nodes after delete (auth-branch cleanup case)
- [ ] Prototype: NavigationGraph model + tree projection for UI (dedupe by canonical URL)

### Account/API
- [ ] Minimal account app UI: no sidebar, shadcn-only primitives, trails-first home, Google-only auth

### Infra/DX
- [ ] (TBD)

## Done
- [x] Pricing nav → `/pricing` (merged into main)

## Notes / rules
- Big tasks should be split into 1–3 hour deliverables.
- Each PR should include: what changed, how to test, screenshots if UI.
