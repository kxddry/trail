# Trail Adultify - Prioritized Backlog

## P0 - Critical (Must Fix Now)

### BUG-001: Auth session persistence - users logged out after sleep
- **Root cause**: `AuthOrchestrator` uses `setTimeout` instead of `chrome.alarms` for token refresh. Service worker dies after ~30s idle, killing the timer. 5-min access token expires, no refresh happens.
- **Fix 1**: Add `chrome.alarms`-based proactive refresh to AuthOrchestrator
- **Fix 2**: Make `isAuthenticated()` in `sync/api.ts` check token expiry, not just existence
- **Fix 3**: Add "session expired" UX to AuthGate instead of silent logout
- **Files**: `extension/src/background/services/auth-orchestrator.ts`, `extension/src/background/services/sync/api.ts`, `extension/src/sidepanel/ui/App.tsx`
- **Source**: Security Architect + UX Reviewer

### SEC-001: Production secrets in repo (.env.prod, .env.e2e)
- **Action**: Add to .gitignore, remove from tracking (NOT from git history - user must rotate secrets separately)
- **Source**: DevOps Engineer

## P1 - High Priority

### BUG-002: Race condition in upsertTrail - no transaction
- **File**: `apps/account/src/server/backend/trails-sync.ts` (lines 283-352)
- **Fix**: Wrap find + conditional create/update in `db.$transaction()`
- **Source**: QA Engineer (C1)

### BUG-003: Import endpoint device-user ownership collision
- **File**: `apps/account/app/api/v1/trails/import/route.ts` (lines 84-88)
- **Fix**: Change `update: {}` to `update: { userId }`
- **Source**: QA Engineer (C2)

### BUG-004: ensureSyncDevices silently reassigns devices across users
- **File**: `apps/account/src/server/backend/trails-sync.ts` (lines 148-159)
- **Fix**: Scope device ID per user or reject conflicting ownership
- **Source**: QA Engineer (C3)

### CI-001: Add lint + test to ci-web.yml
- **Source**: DevOps Engineer

### CI-002: Add typecheck to ci-extension.yml
- **Source**: DevOps Engineer

### CI-003: Create dependabot.yml for vulnerability scanning
- **Source**: DevOps Engineer

### UX-001: No error.tsx or not-found.tsx in web app
- **Fix**: Create branded error and not-found pages
- **Source**: UX Reviewer

### UX-002: Root loading.tsx is bare "loading" text
- **Fix**: Replace with proper loading component
- **Source**: UX Reviewer

### UX-003: Delete actions in extension have no confirmation
- **Fix**: Add confirmation for destructive context menu actions
- **Source**: UX Reviewer

## P2 - Medium Priority

### CI-004: Create PR template
### CI-005: Create security audit workflow
### CI-006: Create PR auto-labeler
### CI-007: Create extension release workflow
### SEC-002: Consolidate AUTH_STORAGE_KEY into shared constant (6 duplicates)
### SEC-003: Add production guard for ACCOUNT_AUTH_BYPASS
### BUG-005: Webhook handler lacks database transaction
### BUG-006: Sync engine has no retry limit
### BUG-007: Silent error swallowing in navigation handler
### UX-004: Missing loading states for /trails, /settings
### UX-005: Context menus lack ARIA roles
### UX-006: No page transitions in web app

## P3 - Nice to Have (defer to future PRs)
- Rate limiting on API endpoints
- Refresh token replay detection
- Focus trapping in modals
- Button system unification
- Icon system unification
- Empty state improvements
- Toast system in web app
