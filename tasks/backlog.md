# Trail - Prioritized Backlog

## P0 - Critical (Must Fix Now)

(none - all P0 items resolved)

## P1 - High Priority

### ARCH-001: GraphCanvas.tsx decomposition (in progress)
- Phase 1: Types extraction — DONE
- Phase 2: useGraphSelection — DONE
- Phase 3: useGraphAnimation — TODO (animation loop, particles, enter/exit/move)
- Phase 4: useGraphView — TODO (pan/zoom, grid CSS, fit-to-view, camera)
- Phase 5: useGraphLayout — TODO (recency, positions, bounds, renderNodes)
- Phase 6: useGraphDrag — TODO (drag state machine, reparent, layout flush)
- Phase 7: useGraphRenderer — TODO (PixiJS lifecycle, resize, theme)
- **Detailed blueprint available from architect agent**

### TEST-001: Extension test coverage critically low
- 37K lines of code, 3 test files
- **Fix**: TDD approach — write tests for RPC, auth, sync, navigation, spotlight

### TEST-002: Marketing app tests (partial)
- 11 tests added for feedback API — DONE
- TODO: SectionRenderer, revalidation, Sanity queries

### ARCH-002: 4 files over 800 lines (besides GraphCanvas)
- GraphPixiRenderer.ts (1,682), spotlight.ts (1,193), ContextMenus.tsx (976), ThemePalette.tsx (885)
- contracts.ts (884) — split plan available from architect agent

## P2 - Medium Priority

### LOG-001: ~159 console.* statements — no structured logging
- **Fix**: Logging service wrapper

### RATE-001: In-memory rate limiting in marketing API
- **Fix**: Migrate to Vercel KV or edge rate limiting

### UI-001: Close tab in context menu has no confirmation
- **Fix**: Add confirmation for destructive tab actions

## P3 - Nice to Have

- Rate limiting on all API endpoints
- Refresh token replay detection
- Focus trapping in modals
- Button system unification
- Empty state improvements
- Toast system in web app
- Page transitions in web app

## Resolved (2026-03-14)

- ~~BUG-001: Auth session persistence~~ — uses browser.alarms + expiry check
- ~~BUG-002: Race condition in upsertTrail~~ — db.$transaction()
- ~~BUG-003: Import device-user collision~~ — wrapped in transaction
- ~~BUG-004: ensureSyncDevices race condition~~ — wrapped in transaction
- ~~BUG-005: Webhook handler lacks transaction~~ — already uses db.$transaction()
- ~~BUG-006: Sync engine no retry limit~~ — 6-attempt exponential backoff
- ~~BUG-007: Silent error swallowing in nav handler~~ — errors are logged
- ~~SEC-001: .env.prod secrets~~ — Not in git, gitignored
- ~~SEC-002: AUTH_STORAGE_KEY 6 duplicates~~ — centralized in storage-items.ts
- ~~SEC-003: ACCOUNT_AUTH_BYPASS~~ — Does not exist in codebase
- ~~UX-001: No error.tsx / not-found.tsx~~ — branded pages exist
- ~~UX-002: Bare loading text~~ — animated TrailLogo
- ~~UX-003: Delete without confirmation~~ — two-step confirmation (nodes + tags)
- ~~CI-001 through CI-007~~ — All present in .github/
- ~~TYPE-001: as any in RPC client~~ — proper typed assertion
- ~~TYPE-002: any in marketing sections~~ — typed Sanity schemas
- ~~SANITY-001 through SANITY-003~~ — seed.ts rewritten, validation added
- ~~ENV-001: Marketing env centralization~~ — readOptionalEnv() pattern
- ~~STORAGE-001: localStorage in extension~~ — migrated to WXT storage
- ~~DB-001: .env fallback in db client~~ — removed
- ~~CI-008: Security audit continue-on-error~~ — now blocks
- ~~UI-002: LoginView inline styles~~ — migrated to Tailwind
- ~~ICON-001: Duplicate aliases~~ — deduplicated with @deprecated markers
- ~~UI-003: Type exports from @trail/ui~~ — 21 Props types exported
- ~~JSON-001 through JSON-004~~ — Zod validation for webhook, fetchJson, auth policy, extension token
- ~~SUPPORT-BOT: Missing source~~ — deleted
