# API normalization + sync workflows

Date: 2026-02-02

## Goals
- All backend processes go through `apps/api` and `/v1` endpoints.
- Support wishlist email collection from marketing, account, and extension.
- Implement extension ↔ backend sync for trails, plus a dashboard view and edits.
- Provide device session management with user-configured TTL.
- Support two authentication confirmation flows (extension→site, dashboard→extension).

## Non-goals
- Backward compatibility with existing internal API routes.
- Real-time sync; polling is sufficient.

## Architecture
Clients (extension, account dashboard, marketing) talk only to `api.gettrail.net/v1`. The account site is responsible for user-facing confirmation UI, but the approval call goes to the API.

Authentication modes:
- User tokens (Better Auth) for dashboard actions.
- Extension token for sync and device operations.

## Data model (Prisma)
Wishlist lead:
- `WishlistLead`: `email` unique, `sources` aggregated, optional `userId`, and marketing metadata (`utm_*`, `referrer`, `pagePath`, `userAgent`, `ip`, `country`).

Device + sessions:
- `Device`: per-install identity, metadata about browser/OS, `lastSeenAt`, `status`.
- `DeviceSession`: TTL-based session, `expiresAt`, `lastSeenAt`, `revokedAt`.
- `AccountSettings`: `deviceSessionTtlDays` (7/30/90/180/365).

Trails (hybrid + tombstones):
- `Trail`: hybrid storage with summary fields + `payload` JSON.
- `deletedAt` used as tombstone, retained for 30 days.

## Device identity (best-effort)
- Extension stores `deviceId` in `chrome.storage.sync`.
- If `deviceId` is missing, API creates a new device (no reuse heuristic).

## Sync strategy (full sync + LWW)
- Extension sends full list (active + deleted) every 5 minutes, at startup, and on user action (Cmd/Ctrl+S or menu).
- Server applies LWW by `updatedAt`.
- If `deletedAt` is set, updates older than `deletedAt` are ignored to prevent resurrection.
- Server returns updates since `clientSyncAt`, including tombstones.
- Trash view is supported via `deletedAt` and `restore` endpoint.

## Auth flows
Extension → site:
- Extension starts portal session → opens account site → user approves on site → extension polls for approval and receives `AccountSnapshot` + token.

Dashboard → extension:
- Dashboard starts connect session → sends message to open extension → user confirms inside extension → dashboard polls for approval.

## API surface (summary)
- `POST /v1/wishlist`
- `POST /v1/auth/portal`, `GET /v1/auth/portal/{id}`, `POST /v1/auth/portal/{id}/approve`
- `POST /v1/extension/connect`, `GET /v1/extension/connect/{id}`, `POST /v1/extension/connect/{id}/approve`
- `POST /v1/devices/claim`, `GET /v1/devices`, `POST /v1/devices/{id}/revoke`
- `GET/PATCH /v1/account/settings`
- `POST /v1/trails/sync`, `GET /v1/trails`, `PATCH /v1/trails/{id}`, `DELETE /v1/trails/{id}`, `POST /v1/trails/{id}/restore`

## Errors and retries
- Standard error payload: `code`, `message`, `retryable`, `details`.
- Polling endpoints return `pending/approved/expired` without throwing on timeout.

## Testing
- API typecheck: `pnpm --filter @trail/api typecheck`.
- Follow-up implementation will need integration tests for sync and auth flows.
