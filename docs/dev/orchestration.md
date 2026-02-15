# Autonomous development (Orchestrator playbook)

This repo is often worked on by an orchestrator agent (G) that coordinates multiple implementation agents in parallel.

## Goals
- Keep Ivan unblocked: the main chat stays responsive while work runs in background.
- Avoid mixing changes: isolate tasks so results are reviewable and reversible.
- Ship continuously: small PRs, clear testing notes.

## Core workflow
1. **Intake**
   - Convert the request into 1–4 small deliverables (ideally 30–120 min each).
   - Record them in `docs/dev/backlog.md`.

2. **Isolation (required)**
   - Use **one git worktree per task**.
   - Never run autonomous work directly in a dirty working tree.

3. **Parallel execution**
   - Spawn one background agent per worktree.
    - Typical lanes:
      - Marketing (`apps/marketing`)
      - Extension (`extension`)
      - Account (`apps/account`, `packages/*`)
      - Infra/DX (tooling/CI/build)

4. **Integration**
   - Orchestrator reviews diffs, resolves conflicts, runs the relevant checks.
   - Push branch + open PR by default.

5. **Merge policy**
   - Default: **PRs only**.
   - Merge/push to `origin/main` only when Ivan explicitly asks (e.g. “пуши в мейн”).

## Worktree recipe
From repo root:

```bash
# Always sync first
git fetch origin --prune

# Create isolated worktree
slug=pricing-link
path=/tmp/trail-$slug

git worktree add -b feat/$slug "$path" origin/main

# Work in the task directory
cd "$path"

# When done
git status
```

Cleanup after merge:

```bash
# from repo root
git worktree remove /tmp/trail-pricing-link
```

## Checks (pick the smallest relevant one)
- Marketing changes:
  - `pnpm --filter @trail/marketing typecheck`
  - `pnpm --filter @trail/marketing lint` (if configured)
- Account changes:
  - `pnpm --filter @trail/account typecheck`

## Releases
- Release checklist + commands: `docs/dev/release.md`

## Status updates (chat)
- If Ivan ends a message with **"фон"**, run in background and post periodic updates:
  - “Found the file(s)” → “Implemented” → “Ran checks” → “Pushed PR”.

## Safety rules
- Don’t edit generated files unless the framework expects it (e.g. Next may update `next-env.d.ts`).
- Prefer minimal changes and keep PRs small.
- Avoid "quick hacks"; fix root cause.
