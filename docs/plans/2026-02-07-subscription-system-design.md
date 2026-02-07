# Subscription System Design (User-Level, Provider-Agnostic)

Date: 2026-02-07

## Goal

Build a production-grade subscription lifecycle similar to iCloud/Cursor:

- Plans: `Free`, `Pro`, `Teams`.
- Intervals: `monthly`, `yearly`.
- Auto-renew enabled by default.
- Cancel turns off auto-renew, but access remains until the end of the current paid period.
- Upgrade is immediate.
- Interval changes are restricted: users cannot change `monthly <-> yearly` inside an active subscription. They must cancel auto-renew, wait until expiry, then subscribe again.

This design is provider-agnostic and supports current providers (Manual, NOWPayments) while keeping the core subscription state model stable.

Out of scope (for now): workspaces, membership, seats enforcement. `Teams` is treated as a paid tier at the user level until a future workspace model exists.

## Product Rules (Source of Truth)

### Plan changes

- Upgrade (`Free -> Pro`, `Free -> Teams`, `Pro -> Teams`): immediate access.
- Downgrade to paid tiers is not supported.
- Downgrade to `Free`: by canceling auto-renew; takes effect at period end.

### Interval changes

- Disallow interval changes within an active subscription.
- Exception: upgrades may request a new interval; it is applied on the next renewal (see `pendingInterval`).

### Renewal date and proration

- Upgrade proration is supported.
- Renewal date does not change when upgrading mid-cycle.
- Proration is computed on the remaining part of the current period.

## Data Model

### Prisma enums

Add/adjust:

- `SubscriptionPlan`: `FREE | PRO | TEAMS` (already exists).
- New `SubscriptionInterval`: `MONTH | YEAR`.

### `UserSubscription` (authoritative fields)

Replace synthetic fields with true persisted fields:

- `plan: SubscriptionPlan` (current access tier).
- `interval: SubscriptionInterval` (current billing interval).
- `pendingInterval: SubscriptionInterval?` (upgrade may request interval change, applied at renewal).
- `currentPeriodStart: DateTime?` (inclusive).
- `currentPeriodEnd: DateTime?` (exclusive).
- `cancelAtPeriodEnd: Boolean @default(false)` (auto-renew off when true).
- `canceledAt: DateTime?`.
- `status: SubscriptionStatus` (payment health, not auto-renew state).

Notes:

- `status` should reflect payment state (`ACTIVE`, `PAST_DUE`, `UNPAID`, etc.).
- Do not encode cancel/auto-renew using `status=CANCELED`.

### Invariants

- If `plan != FREE`, then `currentPeriodStart` and `currentPeriodEnd` must be non-null.
- If `currentPeriodEnd <= now`, subscription access is treated as `Free` regardless of stored `plan`.
- Auto-renew state is `cancelAtPeriodEnd`.

## State Transitions

### Subscribe (from Free)

- Create or update `UserSubscription`:
  - `plan = targetPlan`
  - `interval = chosenInterval`
  - `pendingInterval = null`
  - `currentPeriodStart = now`
  - `currentPeriodEnd = addMonths(now, 1)` or `addYears(now, 1)`
  - `cancelAtPeriodEnd = false`
  - `status = ACTIVE`

### Upgrade (mid-period)

Given an existing active paid subscription and `targetPlan` higher tier:

- Access changes immediately: `plan = targetPlan`.
- Keep renewal date and current interval:
  - `currentPeriodStart` and `currentPeriodEnd` unchanged.
  - `interval` unchanged.
- If user selected a different interval during upgrade:
  - set `pendingInterval = selectedInterval`.

### Cancel auto-renew

- Set:
  - `cancelAtPeriodEnd = true`
  - `canceledAt = now`
- Do not modify `plan`, `interval`, or period boundaries.

### Resume auto-renew

- Set:
  - `cancelAtPeriodEnd = false`
  - `canceledAt = null`

### Renewal

When a successful renewal payment is confirmed:

- Apply `pendingInterval` if present:
  - `interval = pendingInterval ?? interval`
  - `pendingInterval = null`
- Advance period:
  - `currentPeriodStart = currentPeriodEnd`
  - `currentPeriodEnd = addMonths(currentPeriodEnd, 1)` or `addYears(currentPeriodEnd, 1)` based on `interval`
- Set `status = ACTIVE`.
- `cancelAtPeriodEnd` remains as-is.

If `cancelAtPeriodEnd = true`, the system must avoid initiating a renewal and should treat expiry as final.

## Proration Model (Upgrade)

Compute proration for the remaining part of the current period.

Definitions:

- `periodMs = currentPeriodEnd - currentPeriodStart`
- `remainingMs = max(0, currentPeriodEnd - now)`
- `remainingRatio = clamp(remainingMs / periodMs, 0..1)`

Prices are for the current interval:

- `oldPrice = price(plan=oldPlan, interval=currentInterval)`
- `newPrice = price(plan=targetPlan, interval=currentInterval)`

Amounts:

- `credit = oldPrice * remainingRatio`
- `charge = newPrice * remainingRatio - credit`

Rules:

- If `charge <= 0`, upgrade proceeds without charging.
- Provider may require rounding to cents; rounding strategy must be stable and tested.

## API Contracts

### `GET /v1/subscription`

Returns authoritative subscription snapshot:

- `planId: free|pro|teams`
- `interval: month|year`
- `pendingInterval: month|year|null`
- `currentPeriodStart: ISO`
- `currentPeriodEnd: ISO`
- `cancelAtPeriodEnd: boolean`
- `status: active|past_due|unpaid|grace|expired|paused` (payment health + computed expiry)

### `POST /v1/subscription/checkout`

Input:

- `planId`
- `interval`
- `successUrl`
- `cancelUrl`

Semantics:

- If no active paid subscription, create a new one starting now.
- If upgrading, apply plan immediately and compute proration charge.
- If upgrading with a different interval, set `pendingInterval`, do not change renewal date.

Returns:

- `{ url, expiresAt }`

### `POST /v1/subscription/cancel`

- Sets `cancelAtPeriodEnd=true`, returns updated snapshot.

### `POST /v1/subscription/resume`

- Clears `cancelAtPeriodEnd`, returns updated snapshot.

## Provider Abstraction

Billing provider layer should support these operations:

- `createCheckoutSession` capable of:
  - New subscription checkout.
  - Upgrade checkout with optional proration amount.
- Webhook processing:
  - Confirm payment and call "renewal" or "activation" logic.

Providers may have different capabilities. The core subscription model must not depend on provider-specific concepts (e.g. portal session ids).

## UI/UX in Account Billing

Billing page should reflect subscription lifecycle:

- If `plan=Free`:
  - Primary CTA: "Upgrade to Pro" / "Upgrade to Teams".
- If `plan=Pro/Teams` and `cancelAtPeriodEnd=false`:
  - Show "Renews on <date>".
  - Show "Cancel subscription".
- If `plan=Pro/Teams` and `cancelAtPeriodEnd=true`:
  - Show "Expires on <date>".
  - Show "Resume auto-renew".

Important: avoid presenting `Free` as a selectable paid tier; it is the absence of a paid subscription.

## Migration Plan

1. Add new fields (`interval`, `pendingInterval`, `currentPeriodStart`, `cancelAtPeriodEnd`, `canceledAt`).
2. Backfill:
   - `currentPeriodStart = createdAt`.
   - `interval = MONTH`.
   - If `plan != FREE` and `currentPeriodEnd` is null, set `currentPeriodEnd = addMonths(currentPeriodStart, 1)`.
   - If legacy rows use `status=CANCELED` while still in the paid period: translate to `cancelAtPeriodEnd=true` and set `status=ACTIVE`.
3. Update snapshot logic, cancel/resume, provider activation/renewal logic.

## Test Matrix

- Subscribe Free -> Pro monthly/yearly.
- Cancel auto-renew: remains paid until `currentPeriodEnd`.
- Resume: clears cancel flag.
- Upgrade Pro -> Teams mid-period with proration charge.
- Upgrade with different interval sets `pendingInterval` and keeps renewal date.
- Expiry turns effective plan to Free.
- Rounding stability tests for proration.

