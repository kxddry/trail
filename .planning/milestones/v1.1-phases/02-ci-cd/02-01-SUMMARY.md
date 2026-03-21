---
phase: 02-ci-cd
plan: 01
subsystem: infra
tags: [github-actions, chrome-web-store, wxt, pnpm, cicd, release-automation]

# Dependency graph
requires: []
provides:
  - Automated extension release pipeline triggered by chrome-v* tags
  - Chrome Web Store draft upload via CWS OAuth secrets
  - GitHub Release creation with zip artifact and auto-generated notes
  - Verified pre-existing CI: web lint/test, extension typecheck, dependabot, PR template, security audit, auto-labeler
affects: [extension-releases, chrome-web-store-publishing]

# Tech tracking
tech-stack:
  added:
    - nicolo-ribaudo/chrom-webstore-upload@v1 (CWS draft upload action)
    - softprops/action-gh-release@v2 (GitHub Release creation)
  patterns:
    - Release workflow mirrors ci-extension.yml setup steps exactly (checkout, pnpm 10.29.3, node 20, frozen lockfile)
    - Belt-and-suspenders: CI steps (typecheck, test, build) run before packaging in release workflow
    - Tag-as-version-source: chrome-v* tag name is the single source of truth for version
    - Draft upload: CWS upload with publish=false requires manual publish from Chrome Developer Dashboard

key-files:
  created:
    - .github/workflows/release-extension.yml
  modified: []

key-decisions:
  - "Tag chrome-v* is the version source of truth — strip prefix to get semver, no separate version extraction needed"
  - "CWS upload uses publish=false (draft) — manual publish from Chrome Developer Dashboard gives release control"
  - "cancel-in-progress=false on concurrency group — never cancel an in-progress release"
  - "nicolo-ribaudo/chrom-webstore-upload@v1 selected as widely adopted, simple CWS upload action"

patterns-established:
  - "Release workflow: mirror CI setup steps, add packaging + upload steps after build"
  - "Concurrency group without ref suffix for releases (unlike CI which uses github.ref)"

requirements-completed:
  - CICD-01
  - CICD-02
  - CICD-03
  - CICD-04
  - CICD-05
  - CICD-06
  - CICD-07

# Metrics
duration: 4min
completed: 2026-02-28
---

# Phase 2 Plan 01: CI/CD Release Automation Summary

**GitHub Actions release workflow for Chrome extension: chrome-v* tag triggers typecheck/test/build/zip, uploads draft to Chrome Web Store, and creates a GitHub Release with zip attached.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-02-28T15:35:43Z
- **Completed:** 2026-02-28T15:36:43Z
- **Tasks:** 2 of 2
- **Files modified:** 1 (created)

## Accomplishments

- Verified all 6 pre-existing CI/CD requirements (CICD-01 through CICD-06) are intact and correctly configured
- Created `.github/workflows/release-extension.yml` (79 lines, valid YAML) implementing CICD-07
- Release workflow runs full CI gate (typecheck, test, build) before packaging — consistent with existing CI patterns
- CWS secrets referenced correctly (CWS_EXTENSION_ID, CWS_CLIENT_ID, CWS_CLIENT_SECRET, CWS_REFRESH_TOKEN)

## Task Commits

Each task was committed atomically:

1. **Task 1: Verify pre-existing CI/CD configurations (CICD-01 through CICD-06)** - No commit (read-only verification, no files changed)
2. **Task 2: Create extension release workflow (CICD-07)** - `156a52ad` (feat)

**Plan metadata:** (final docs commit follows)

## Files Created/Modified

- `.github/workflows/release-extension.yml` - Extension release pipeline: chrome-v* tag trigger, CI steps, pnpm zip, CWS draft upload, GitHub Release

## Decisions Made

- Used `nicolo-ribaudo/chrom-webstore-upload@v1` as the CWS upload action — widely adopted, straightforward interface
- `publish: false` ensures draft-only upload; manual publish from Chrome Developer Dashboard preserves release control
- Tag name (`chrome-v0.9.2`) is the version source of truth — `VERSION=${GITHUB_REF_NAME#chrome-v}` strips prefix cleanly
- `cancel-in-progress: false` on the release concurrency group — a release in flight must never be interrupted
- File path for zip uses `extension/` prefix (e.g., `extension/.output/trail-0.9.1-chrome.zip`) since actions run from repo root but working-directory only affects `run` steps, not action `with` inputs

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

**External services require manual configuration before the release workflow can succeed.** Four GitHub repository secrets must be added:

| Secret | Source |
|--------|--------|
| `CWS_EXTENSION_ID` | Chrome Developer Dashboard -> Your extension -> ID from the URL |
| `CWS_CLIENT_ID` | Google Cloud Console -> APIs & Services -> Credentials -> OAuth 2.0 Client ID |
| `CWS_CLIENT_SECRET` | Google Cloud Console -> APIs & Services -> Credentials -> OAuth 2.0 Client Secret |
| `CWS_REFRESH_TOKEN` | Generated via OAuth flow with `chrome_webstore` scope (see https://developer.chrome.com/docs/webstore/using-api) |

Additionally:
1. Enable Chrome Web Store API in Google Cloud Console -> APIs & Services -> Library
2. Add secrets at GitHub -> Settings -> Secrets and variables -> Actions

## Next Phase Readiness

- Phase 2 (CI/CD) is complete — all 7 CI/CD requirements satisfied
- To release: push a `chrome-v{semver}` tag (e.g., `git tag chrome-v0.9.2 && git push origin chrome-v0.9.2`)
- After the workflow completes, manually publish the draft from the Chrome Developer Dashboard

## Self-Check: PASSED

- FOUND: `.github/workflows/release-extension.yml`
- FOUND: `.planning/phases/02-ci-cd/02-01-SUMMARY.md`
- FOUND: commit `156a52ad` (feat: extension release workflow)

---
*Phase: 02-ci-cd*
*Completed: 2026-02-28*
