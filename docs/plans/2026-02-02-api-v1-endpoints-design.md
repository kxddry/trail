# API v1 Endpoints Design

**Goal:** Implement API v1 route handlers in `apps/api/app/v1` to match the public OpenAPI contract for devices, account settings, trails, account snapshot, and billing endpoints.

## Architecture
- Implement Next.js route handlers under `apps/api/app/v1` following existing patterns (`auth/portal`, `extension/connect`, `wishlist`).
- Responses use `jsonNoStore` and errors use `jsonError` with consistent codes/messages.
- Authentication is explicit per endpoint: `userAuth` uses `verifyUserToken` + `ensureUser`; `extensionAuth` uses `verifyExtensionToken`.
- Use existing services where available (`claimDevice`, `syncTrails`, `buildAccountSnapshot`, `listPlans`).
- For routes without services, use direct Prisma reads/writes in the route handler to keep behavior deterministic and aligned with the OpenAPI shapes.

## Data Mapping
- Device session TTL mapping:
  - Prisma enum `DeviceSessionTtlDays` ⇄ API numeric days `{7,30,90,180,365}`.
  - Return numeric days in responses; accept numeric days in PATCH.
- Trail label source mapping:
  - Prisma enum `TrailLabelSource` (`USER|AUTO|SYSTEM`) ⇄ API enum (`user|auto|system`).
- Date fields are serialized as ISO strings.

## Endpoint Behavior Summary
- `POST /v1/devices/claim`: validate `metadata.os`; call `claimDevice`; return `{ device, session, sessionTtlDays }`.
- `GET /v1/devices`: list devices and include latest active session if present.
- `POST /v1/devices/{id}/revoke`: ensure device belongs to user; set status `REVOKED`; revoke active sessions; return device.
- `GET /v1/account/settings`: read or default settings; return `{ deviceSessionTtlDays }`.
- `PATCH /v1/account/settings`: validate `deviceSessionTtlDays`; upsert; return updated settings.
- `GET /v1/trails`: pagination with `limit` + `cursor` (updatedAt cursor), `includeDeleted` filter; return `{ items, nextCursor }`.
- `POST /v1/trails/sync`: validate body, map enums/dates, call `syncTrails`, return sync payload.
- `PATCH /v1/trails/{id}`: update label/labelSource/deletedAt; return full trail record; 404 if missing.
- `DELETE /v1/trails/{id}`: soft delete by setting `deletedAt` (now), return trail record; 404 if missing.
- `POST /v1/trails/{id}/restore`: clear `deletedAt`, return trail record; 404 if missing.
- `GET /v1/account`: uses `buildAccountSnapshot` with extension token and user; returns account snapshot.
- Billing (strict OpenAPI shapes):
  - `GET /v1/plans`: returns `listPlans()`.
  - `GET /v1/subscription`: if no DB record, return stub `free` subscription object (planId `free`, status `active`, interval `month`, dates derived from user.createdAt and +30d).
  - `GET /v1/billing`: `{ state: "none" }`.
  - `POST /v1/subscription/checkout` and `POST /v1/billing/portal`: return stub `{ url, expiresAt }` using provided success/return URL or fallback to account billing page.

## Error Handling
- `401` for missing/invalid auth or missing user.
- `404` for missing device/trail in user scope.
- `400` for invalid payloads (missing required fields or invalid enums).

## Testing Strategy
- Add Vitest tests under `apps/api/app/v1/__tests__` mirroring existing patterns.
- Mock auth helpers, services, and database interactions as needed to validate:
  - auth failures return `401`.
  - happy paths return expected payloads and ISO date strings.
  - edge cases (invalid input, missing record) return correct status + code.
