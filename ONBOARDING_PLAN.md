# Unified First-Login Onboarding For Web + Extension

## Summary
Сделать единый блокирующий onboarding после первого логина, который одновременно работает в `apps/account` и в extension, с одним серверным источником истины (`User.onboardingSeenAt`) и синхронизацией закрытия между клиентами за 2–3 секунды.

## Implementation Plan

### 1. Расширить серверный контракт onboarding в snapshot (единая truth-model)
1. Добавить новый тип onboarding в snapshot:  
`onboarding: { flowId: "activation-v1"; status: "pending" | "completed"; seenAt: string | null }`.
2. Обновить типы и билдеры snapshot в:
`/Users/iv/dev/trail/extension/src/shared/types/account.ts`  
`/Users/iv/dev/trail/apps/api/src/server/account-snapshot.ts`  
`/Users/iv/dev/trail/apps/account/src/server/account-snapshot.ts`
3. Пробросить `onboardingSeenAt` в user-объекты, из которых строится snapshot:
`/Users/iv/dev/trail/apps/api/src/server/user.ts`  
`/Users/iv/dev/trail/apps/api/app/api/internal/users/[id]/route.ts`  
`/Users/iv/dev/trail/apps/api/src/server/auth-bridge.ts`  
`/Users/iv/dev/trail/apps/api/src/server/portal-sessions.ts`  
`/Users/iv/dev/trail/apps/api/app/api/internal/extension/portal/[id]/route.ts`
4. Обновить места, где snapshot отдается после логина/проверки сессии:
`/Users/iv/dev/trail/apps/api/app/api/v1/account/route.ts`  
`/Users/iv/dev/trail/apps/api/app/api/v1/auth/portal/[id]/route.ts`  
`/Users/iv/dev/trail/apps/api/app/api/v1/auth/bridge/exchange/route.ts`  
`/Users/iv/dev/trail/apps/account/app/api/v1/account/route.ts`  
`/Users/iv/dev/trail/apps/account/app/api/v1/auth/portal/[id]/route.ts`

### 2. Добавить endpoint завершения onboarding для extension-клиента
1. Реализовать API endpoint в `apps/api`:
`POST /api/v1/onboarding` (Bearer extension token, body `{ action: "complete" | "skip", source: "extension" | "web" }`, ответ с `onboarding` state).
Файл: `/Users/iv/dev/trail/apps/api/app/api/v1/onboarding/route.ts`.
2. Добавить прокси в `apps/account`:
`/Users/iv/dev/trail/apps/account/app/api/v1/onboarding/route.ts`.
3. Использовать существующую server-логику onboarding (`onboardingSeenAt`) в:
`/Users/iv/dev/trail/apps/api/src/server/user.ts`.
4. Оставить cookie-based web endpoint `/api/onboarding`, но унифицировать payload до `onboarding` state:
`/Users/iv/dev/trail/apps/account/app/api/onboarding/route.ts`  
`/Users/iv/dev/trail/apps/api/app/api/internal/users/[id]/onboarding/route.ts`

### 3. Web: блокирующий OnboardingGate во всем `/(app)` shell
1. Добавить client overlay-компонент:
`/Users/iv/dev/trail/apps/account/app/(app)/OnboardingGate.tsx`
2. Подключить gate в layout для всех app-страниц:
`/Users/iv/dev/trail/apps/account/app/(app)/layout.tsx`
3. Добавить серверный helper чтения onboarding state для initial render:
`/Users/iv/dev/trail/apps/account/src/server/onboarding.ts`
4. Поведение gate:
- рендерится только для авторизованных пользователей;
- блокирует UI пока `status === "pending"`;
- кнопки `Done` и `Skip` вызывают `POST /api/onboarding` и закрывают gate;
- пока pending, делает polling `GET /api/onboarding` раз в 2500ms (чтобы закрыться, если пользователь завершил flow в extension).

### 4. Extension: блокирующий OnboardingGate + sync polling
1. Добавить onboarding endpoint в backend config:
`/Users/iv/dev/trail/extension/src/shared/config/backend.ts` (`endpoints.onboarding = "/onboarding"`).
2. Расширить account API клиента методом завершения onboarding:
`/Users/iv/dev/trail/extension/src/sidepanel/api/account.ts`  
`/Users/iv/dev/trail/extension/src/sidepanel/api/account/remote.ts`  
`/Users/iv/dev/trail/extension/src/sidepanel/ui/query/useAuthMutations.ts`
3. Добавить onboarding state в zustand account store:
`/Users/iv/dev/trail/extension/src/sidepanel/ui/state/store.ts`
4. Включить polling snapshot раз в 2500ms, пока onboarding pending:
`/Users/iv/dev/trail/extension/src/sidepanel/ui/query/useAccountSnapshotQuery.ts`
5. Добавить блокирующий UI gate:
`/Users/iv/dev/trail/extension/src/sidepanel/ui/components/OnboardingGate.tsx`  
`/Users/iv/dev/trail/extension/src/sidepanel/ui/App.tsx`
6. Поведение extension gate:
- показывается только когда пользователь authenticated и `snapshot.onboarding.status === "pending"`;
- `Done/Skip` -> `POST /api/v1/onboarding` -> invalidate snapshot query;
- при network/error не закрывается, показывает retry/error state.

### 5. Удалить legacy локальный onboarding state в extension (чтобы не было двух truth sources)
1. Убрать неиспользуемый `onboardingSeen` из settings type/default merge:
`/Users/iv/dev/trail/extension/src/shared/types/settings.ts`  
`/Users/iv/dev/trail/extension/src/background/services/settings.ts`
2. Убедиться, что onboarding контролируется только server snapshot.

### 6. Dev-only reset для QA
1. Добавить dev-only reset на internal onboarding route (`DELETE`), запрещенный в production:
`/Users/iv/dev/trail/apps/api/app/api/internal/users/[id]/onboarding/route.ts`
2. Добавить удобный web reset endpoint для локальной отладки:
`/Users/iv/dev/trail/apps/account/app/api/onboarding/reset/route.ts`
3. Reset делает `onboardingSeenAt = NULL` только для текущего юзера, только в dev/test.

### 7. Документация API
1. Обновить OpenAPI c новым endpoint и новым snapshot-полем:
`/Users/iv/dev/trail/apps/api/public/api/openapi.yml`

## Public API / Interface Changes
1. `AccountSnapshot` (extension/shared contract): добавляется обязательное поле `onboarding`.
2. Новый endpoint: `POST /api/v1/onboarding`.
3. `GET/POST /api/onboarding` в account app возвращают `onboarding` object (вместо только `{ seen }`).
4. Internal user payload расширяется полем `onboardingSeenAt` (для snapshot pipeline).

## Test Cases and Scenarios
1. API unit tests (`apps/api`):
- snapshot routes содержат `onboarding` (`account`, `auth/portal/[id]`, `auth/bridge/exchange`);
- `POST /api/v1/onboarding` возвращает `completed` и timestamp;
- unauthorized extension token -> 401;
- internal onboarding route: GET/POST/DELETE (dev-only reset).
2. Account proxy tests (`apps/account`):
- `api/v1/onboarding` корректно проксирует upstream и авторизацию;
- `api/onboarding` для cookie-auth корректно читает/ставит onboarding state.
3. Web UI tests:
- pending -> `OnboardingGate` блокирует layout;
- `Done`/`Skip` вызывают POST и скрывают gate;
- polling скрывает gate, если state изменился извне.
4. Extension checks:
- typecheck + existing tests проходят с новым `AccountSnapshot`;
- при pending gate показывается, main UI скрыт;
- completion вызывает endpoint и после refetch gate закрывается.
5. Manual e2e:
- завершить onboarding в web -> extension закрывает gate <= 3s;
- завершить onboarding в extension -> web закрывает gate <= 3s;
- existing user (`onboardingSeenAt != null`) не видит gate;
- offline/error при completion не снимает блокировку, есть retry.

## Rollout and Monitoring
1. Катить без миграций БД (поле уже есть), но с полным type-safe контрактом snapshot.
2. Добавить server-side лог события completion (`source`, `userId`, `action`) в endpoint `POST /api/v1/onboarding`.
3. Проверить staging сценарии “web-first”, “extension-first”, “parallel open”.

## Assumptions and Defaults
1. Scope сайта: только `apps/account` (не `apps/auth` UI).
2. Блокирующий onboarding обязателен до `Done` или `Skip`.
3. Shared sync только по terminal state (`pending/completed`), без shared step-index.
4. `Done` и `Skip` одинаково ставят `onboardingSeenAt`.
5. Синхронизация между клиентами: polling 2500ms пока onboarding pending.
6. Единый сценарий flow: `flowId = "activation-v1"` на обеих сторонах.
