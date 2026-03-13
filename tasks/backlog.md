# Trail - Prioritized Backlog

## P0 - Critical (Must Fix Now)

(none - all P0 items resolved)

## P1 - High Priority

### ARCH-001: GraphCanvas.tsx — 2,728 lines, needs decomposition
- **Fix**: Extract useGraphLayout, useGraphInteraction, useGraphAnimation hooks
- **Status**: Planned for dedicated refactoring session

### ARCH-002: 5 files over 800 lines
- GraphPixiRenderer.ts (1,682), spotlight.ts (1,193), ContextMenus.tsx (976), ThemePalette.tsx (885), contracts.ts (884)
- **Fix**: Split by domain/concern

### TEST-001: Extension test coverage critically low
- 37K lines of code, 3 test files
- **Fix**: TDD approach — write tests for RPC, auth, sync, navigation, spotlight

### TEST-002: Marketing app — zero tests
- **Fix**: Add tests for API routes, SectionRenderer, components

## P2 - Medium Priority

### LOG-001: ~159 console.* statements — no structured logging
- **Fix**: Logging service wrapper

### RATE-001: In-memory rate limiting in marketing API
- **Fix**: Migrate to Vercel KV or edge rate limiting

### UI-001: LoginView uses inline styles instead of Tailwind
- **Fix**: Migrate to Tailwind for consistency

### UI-002: Tag deletion has no confirmation dialog
- **Fix**: Add two-step confirmation (matches node delete pattern)

### UI-003: Close tab in context menu has no confirmation
- **Fix**: Add confirmation for destructive tab actions

## P3 - Nice to Have

- Rate limiting on all API endpoints
- Refresh token replay detection
- Focus trapping in modals
- Button system unification
- Icon alias deduplication in @trail/ui
- Empty state improvements
- Toast system in web app
- Page transitions in web app

## Resolved (2026-03-13)

- ~~BUG-001: Auth session persistence~~ — Fixed: uses browser.alarms + expiry check
- ~~BUG-002: Race condition in upsertTrail~~ — Fixed: db.$transaction()
- ~~BUG-003: Import device-user collision~~ — Fixed: wrapped in transaction
- ~~BUG-004: ensureSyncDevices race condition~~ — Fixed: wrapped in transaction
- ~~BUG-005: Webhook handler lacks transaction~~ — Fixed: already uses db.$transaction()
- ~~BUG-006: Sync engine no retry limit~~ — Fixed: 6-attempt exponential backoff
- ~~BUG-007: Silent error swallowing in nav handler~~ — Fixed: errors are logged
- ~~SEC-001: .env.prod secrets~~ — Not in git, gitignored
- ~~SEC-002: AUTH_STORAGE_KEY 6 duplicates~~ — Fixed: centralized in storage-items.ts
- ~~SEC-003: ACCOUNT_AUTH_BYPASS~~ — Does not exist in codebase
- ~~UX-001: No error.tsx / not-found.tsx~~ — Fixed: branded pages exist
- ~~UX-002: Bare loading text~~ — Fixed: animated TrailLogo
- ~~UX-003: Delete without confirmation~~ — Fixed: two-step confirmation on all node deletes
- ~~CI-001: Add lint + test to ci-web.yml~~ — Present in workflow
- ~~CI-002: Add typecheck to ci-extension.yml~~ — Present in workflow
- ~~CI-003: Create dependabot.yml~~ — Present in .github/
- ~~CI-004: Create PR template~~ — Present in .github/
- ~~CI-005: Create security audit workflow~~ — Present in .github/workflows/security.yml
- ~~CI-006: Create PR auto-labeler~~ — Present in .github/labeler.yml
