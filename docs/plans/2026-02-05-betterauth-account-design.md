# Better Auth для account-приложения (через auth-сервис)

Дата: 2026-02-05

## Контекст
В проекте уже есть `apps/auth`, использующий Better Auth. В `apps/account` ещё встречаются следы Auth0 (импорты `@/src/lib/auth0` и ссылки на Auth0-профиль). Нужен единый источник сессии: Better Auth в `apps/auth`, а `apps/account` должен читать пользователя через существующий bridge‑токен `trail_auth_session` и локальные helpers `src/lib/auth`.

## Цели
- Полностью убрать зависимости от Auth0 в `apps/account`.
- Оставить `apps/auth` единственным auth‑сервисом (Better Auth).
- Сохранить bridge‑флоу для SSO: `apps/auth` → code → `apps/account` → access token cookie.
- Не ломать текущие страницы и тесты, минимальные изменения.

## Не‑цели
- Не меняем API обмена кодов/токенов.
- Не добавляем прямой cross‑subdomain cookie с Better Auth (можно позже).
- Не меняем базовые модели Better Auth или схемы БД.

## Архитектура и поток данных
1. Пользователь логинится в `apps/auth` (Better Auth), получает сессию.
2. `apps/auth` генерирует bridge‑код и редиректит обратно на `apps/account`.
3. `apps/account/app/auth/callback/route.ts` обменивает код через `TRAIL_API_BASE_URL` и сохраняет `trail_auth_session` (access token) в cookie.
4. Все защищённые страницы `apps/account` читают `trail_auth_session` через `src/lib/auth`, декодируют пользователя и вызывают `ensureUser`.

## Изменения в коде
- Удалить использование `@/src/lib/auth0` в `apps/account`.
- Страницы `settings` и `extension` переключить на `getAuthTokenFromCookies`, `getAuthUserFromToken`, `getDevUser`, `isAuthBypassed`.
- Удалить/заменить `apps/account/src/lib/auth0.ts` (если есть).
- Ссылки “manage profile / change password” направить в `apps/auth` (или через bridge) вместо Auth0.

## Обработка ошибок
- Если токен отсутствует/невалиден → редирект на `/auth/login`.
- Если `ensureUser` возвращает `null` → редирект на `/auth/login`.
- В dev режиме `ACCOUNT_AUTH_BYPASS=1` возвращает dev‑пользователя.

## Тестирование
- Обновить unit‑тесты страниц `settings` и `extension`, моки с `@/src/lib/auth`.
- Прогнать `pnpm -C apps/account typecheck` и `pnpm -C apps/account test`.

## Риски
- Возможны несоответствия между токеном в cookie и ожиданиями `ensureUser`.
- При отсутствии зависимостей в worktree типизация может упасть (нужен `pnpm install`).

## Примечания
- Лучше не вводить отдельные ошибки/страницы, чтобы UX оставался простым.
- Позже можно рассмотреть direct Better Auth cookies с `crossSubDomainCookies`.
