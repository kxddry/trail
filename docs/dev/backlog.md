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
- [ ] Deep migration: WXT-native build + RPC v2 transport + full legacy removal (plan: 2026-02-13-extension-deep-wxt-cutover.md)
- [ ] URL normalization + merge duplicate nodes after delete (auth-branch cleanup case)
- [ ] Prototype: NavigationGraph model + tree projection for UI (dedupe by canonical URL)
- [ ] Editor mode nav/tab disablement with preserved selection behavior (plans:navtab.md)
- [ ] Large-tree performance optimization with adaptive quality policy (plans:optimization.md)

### Account/API
- [ ] (TBD)
- [ ] Reliable Save/Cancel trail editor flow with explicit backend ACK (plans:savecancel.md)

### Infra/DX
- [ ] (TBD)

## Done
- [x] Pricing nav → `/pricing` (merged into main)

## Notes / rules
- Big tasks should be split into 1–3 hour deliverables.
- Each PR should include: what changed, how to test, screenshots if UI.
