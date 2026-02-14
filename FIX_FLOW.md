# Fix Logout Propagation + Real Shared Onboarding Flow (Web + Extension)

## Summary
Нужно закрыть два реальных дефекта:

1. `logout` на сайте не выводит из аккаунта в extension.
Причина: сайт не шлет `AUTH_REVOKED`, а extension-sidepanel держит auth в in-memory кеше (`authCache`) и не сбрасывает UI от внешних изменений storage.

2. `Get started` в onboarding сейчас просто завершает flow.
Причина: нет серверного `currentStep` и нет step-by-step сценария, только terminal action `complete/skip`.

Решение: сделать shared step-state в БД + новый action-based onboarding API + stepper UI на web/extension, и отдельно исправить logout propagation + snapshot cache semantics.

## Important API / Interface Changes
1. Расширить onboarding contract (web + extension):
- Было: `onboarding: { flowId, status, seenAt }`
- Станет: `onboarding: { flowId, status, currentStep, totalSteps, seenAt }`

2. Новый action protocol для onboarding:
- `POST /api/v1/onboarding` body:
  - `{ action: "advance", source, step }`
  - `{ action: "complete", source }`
  - `{ action: "skip", source }`
- `GET /api/v1/onboarding` возвращает полный onboarding state.

3. В `User` добавить серверный shared step state:
- `onboardingStep Int @default(0)` (0..3 для v1)
- использовать текущий `onboardingSeenAt` как completion marker.

## Implementation Plan

### 1) Data model + migration (shared step-state)
1. Обновить Prisma schema:
- `/Users/iv/dev/trail/packages/db/prisma/schema.prisma`
  - добавить `onboardingStep Int @default(0)` в `User`.
2. Добавить migration:
- `/Users/iv/dev/trail/packages/db/prisma/migrations/<timestamp>_add_user_onboarding_step/migration.sql`
  - `ADD COLUMN "onboardingStep" INTEGER NOT NULL DEFAULT 0;`
  - backfill: где `onboardingSeenAt IS NOT NULL`, поставить `onboardingStep = 3`.

### 2) Server onboarding service (single source of truth)
1. Добавить/расширить функции в:
- `/Users/iv/dev/trail/apps/api/src/server/user.ts`
  - `getUserOnboardingState(userId)`
  - `advanceUserOnboardingStep(userId, step)`
  - `completeUserOnboarding(userId)` (ставит `onboardingSeenAt`, `onboardingStep=3`)
  - `resetUserOnboarding(userId)` (dev-only).
2. Правила v1:
- `totalSteps = 3`
- шаги: `connect_extension`, `capture_first_trail`, `review_first_trail`
- `status=completed`, если `onboardingSeenAt != null` или `onboardingStep >= 3`.

### 3) API routes onboarding (internal + extension-auth)
1. Переписать internal route на полный state/action:
- `/Users/iv/dev/trail/apps/api/app/api/internal/users/[id]/onboarding/route.ts`
  - `GET` -> полный onboarding объект
  - `POST` -> action-based update
  - `DELETE` -> dev-only reset (сохранить).
2. Обновить extension-auth route:
- `/Users/iv/dev/trail/apps/api/app/api/v1/onboarding/route.ts`
  - `GET` state
  - `POST` with `advance|complete|skip`.
3. Обновить web proxy route:
- `/Users/iv/dev/trail/apps/account/app/api/onboarding/route.ts`
  - проксировать action body и возвращать полный onboarding state.
4. Обновить extension proxy:
- `/Users/iv/dev/trail/apps/account/app/api/v1/onboarding/route.ts`
  - сохранить passthrough, но зафиксировать action schema.

### 4) Logout propagation (web -> extension)
1. Добавить fire-and-forget API в site bridge:
- `/Users/iv/dev/trail/apps/account/src/lib/trail-extension.ts`
  - `notifyAuthRevoked()`: `postMessage({ type: "AUTH_REVOKED", requestId, timestamp })`.
2. Добавить клиентский logout trigger:
- создать `LogoutLink` client component (например):
  - `/Users/iv/dev/trail/apps/account/app/components/LogoutLink.tsx`
  - `onClick` -> `notifyAuthRevoked()` -> переход на `/auth/logout`.
3. Заменить текущие logout `<a>`:
- `/Users/iv/dev/trail/apps/account/app/(app)/layout.tsx`
- `/Users/iv/dev/trail/apps/account/app/(app)/settings/page.tsx`
4. В extension sidepanel синхронизировать auth cache с storage changes:
- `/Users/iv/dev/trail/extension/src/sidepanel/api/account/remote.ts`
  - подписка на `chrome.storage.onChanged` для `trail_auth_session`, обновлять `authCache/authLoaded`.
5. В sidepanel UI реагировать на revoke моментально:
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/hooks/useAccount.ts`
  - слушать `chrome.storage.onChanged` и при удалении `trail_auth_session`:
    - `resetAccount()`
    - invalidate/remove `accountKeys.snapshot()`.

### 5) Fix stale snapshot behavior (regression guard)
1. Добавить `cache-control: no-store` для account snapshot proxy:
- `/Users/iv/dev/trail/apps/account/app/api/v1/account/route.ts`
2. Проставить `no-store` там, где snapshot-like auth state может кешироваться:
- `/Users/iv/dev/trail/apps/account/app/api/v1/auth/portal/[id]/route.ts`
- проверить связанные auth routes на consistent no-store.

### 6) Replace “button-only onboarding” with shared stepper UX
1. Web stepper gate:
- `/Users/iv/dev/trail/apps/account/app/(app)/OnboardingGate.tsx`
  - показать 3 шага, прогресс, `Next`, `Skip`.
  - `Get started` -> `advance` (не `complete`).
  - финальный шаг -> `complete`.
2. Layout wiring:
- `/Users/iv/dev/trail/apps/account/app/(app)/layout.tsx`
  - передавать initial onboarding state (с `currentStep`) в gate.
3. Success page replacement:
- `/Users/iv/dev/trail/apps/account/app/(app)/extension/page.tsx`
  - ветку `You're all set` заменить на stepper-секцию (или reuse gate content), как согласовано.
4. Extension stepper gate:
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/OnboardingGate.tsx`
  - тот же 3-step сценарий.
  - авто-шаг `connect_extension` (hybrid): если `currentStep===0` и клиент extension, один раз шлем `advance(connect_extension)`.
5. Store/types update:
- `/Users/iv/dev/trail/extension/src/shared/types/account.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/state/store.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/query/useAuthMutations.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/query/useAccountSnapshotQuery.ts`
  - polling оставить для pending onboarding (2.5s), но step updates применять сразу после mutation success.

### 7) OpenAPI + docs consistency
1. Обновить schema:
- `/Users/iv/dev/trail/apps/api/public/api/openapi.yml`
  - onboarding object + action enum + examples.
2. Удалить устаревшие комментарии про “Get started closes onboarding”.

## Test Cases and Scenarios

1. API unit tests (`apps/api`):
- `/Users/iv/dev/trail/apps/api/app/api/v1/__tests__/auth-portal.test.ts`
- `/Users/iv/dev/trail/apps/api/app/api/v1/__tests__/auth-bridge.test.ts`
- новые тесты для `/api/v1/onboarding`:
  - `advance` двигает `currentStep`,
  - `complete/skip` ставят `onboardingSeenAt`, `status=completed`.
- обновить failing test:
  - `/Users/iv/dev/trail/apps/api/app/api/internal/users/[id]/onboarding/route.test.ts`
  - мок `markUserOnboardingSeen` должен возвращать `Date`, не `boolean`.

2. Account tests (`apps/account`):
- тесты `/api/onboarding` route на action passthrough.
- тест на `cache-control: no-store` у `/api/v1/account`.
- UI test для `OnboardingGate`:
  - `Get started` -> шаг +1,
  - final complete -> gate закрывается.

3. Extension checks:
- `/Users/iv/dev/trail/extension`:
  - `pnpm -C extension typecheck`
  - `pnpm -C extension test`
- добавить regression-тест на storage revoke:
  - sidepanel state сбрасывается после удаления `trail_auth_session`.

4. Manual E2E:
- web logout при открытом sidepanel:
  - extension переходит в auth gate без перезагрузки.
- onboarding:
  - шаги синхронизируются между web/extension,
  - completion на одной стороне закрывает gate на другой <= 2.5s.

## Assumptions / Defaults
1. Logout scope: `web logout -> extension logout` обязателен.
2. Onboarding v1: shared linear 3-step flow.
3. Step sync: серверный shared `currentStep`.
4. Completion policy: `complete` и `skip` оба terminal.
5. Step completion policy (hybrid):
- `connect_extension` auto-complete из extension,
- `capture/review` подтверждаются пользователем в stepper.
6. Existing onboarded users (`onboardingSeenAt != null`) не видят gate.
