# Phase 2: CI/CD - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Every pull request is automatically validated and dependency vulnerabilities are surfaced without manual effort. Extension releases are automated to the Chrome Web Store. 6 of 7 requirements (CICD-01 through CICD-06) already have working implementations — the primary new work is CICD-07 (automated extension publishing).

</domain>

<decisions>
## Implementation Decisions

### Release trigger
- Git tag push triggers Chrome Web Store upload
- Tag pattern: `chrome-v*` (e.g., `chrome-v0.9.2`)
- Workflow should also include `workflow_dispatch` for manual re-runs
- Run full CI (typecheck, test, build) before uploading — belt-and-suspenders

### Publishing mode
- Upload as **draft** to Chrome Web Store — user manually clicks Publish in the Chrome Developer Dashboard
- Create a **GitHub Release** with the built extension `.zip` attached

### CWS API credentials
- Chrome Web Store API credentials (client_id, client_secret, refresh_token) need to be set up via Google Cloud Console
- Credentials stored as GitHub repository secrets

### Claude's Discretion
- Version bump strategy (manual bump then tag vs. extract from tag) — pick the simplest
- Exact GitHub Action for Chrome Web Store upload
- GitHub Release body format

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for Chrome Web Store automation.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ci-extension.yml`: Already runs typecheck, test, build — release workflow can mirror these steps
- `wxt zip` command: WXT's built-in zip for creating distributable extension packages
- Extension version in `extension/package.json` at `0.9.1`

### Established Patterns
- All workflows use `pnpm/action-setup@v4` with version `10.29.3` and Node 20
- Extension workflows set `working-directory: extension` and cache via `extension/pnpm-lock.yaml`
- Concurrency groups with `cancel-in-progress: true` on CI workflows

### Integration Points
- Extension build: `pnpm build` (runs `wxt build`) in the extension directory
- Extension zip: `pnpm zip` (runs `wxt zip`) for distributable package
- Existing CICD files already complete:
  - `ci-web.yml` (CICD-01): lint, test, typecheck, build on PRs
  - `ci-extension.yml` (CICD-02): typecheck, test, build on PRs
  - `dependabot.yml` (CICD-03): root, extension, github-actions ecosystems
  - `PULL_REQUEST_TEMPLATE.md` (CICD-04): What/Why/Testing/Checklist sections
  - `security.yml` (CICD-05): weekly + PR-triggered `pnpm audit --prod`
  - `labeler.yml` workflow + config (CICD-06): extension, web, database, ui, ci, dependencies labels

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-ci-cd*
*Context gathered: 2026-02-28*
