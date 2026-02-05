# Account App Auth Plumbing Migration (BetterAuth) Design

Date: 2026-02-03

## Goals
- Убрать Better Auth из `apps/account` и перейти на BetterAuth bridge flow (code → exchange → JWT).
- Хранить JWT в httpOnly cookie на `app.gettrail.net`.
- Перенести проверку авторизации в middleware + обновить TRPC proxy headers.
- Оставить API ключ `x-trail-internal-key` как есть.

## Non-goals
- Валидация JWT в `apps/account` (только декодирование для UI).
- Изменения в API/BetterAuth (только client-side plumbing).
- Обновление extension auth flow.

## Архитектура
- Новый helper `apps/account/src/lib/auth.ts`:
  - `isAuthBypassed()` читает `ACCOUNT_AUTH_BYPASS`.
  - `getDevUser()` возвращает dev пользователя.
  - `getAuthTokenFromCookies()` читает токен из httpOnly cookie (server-only).
  - `getAuthUserFromToken()` декодирует JWT (jose `decodeJwt`) и маппит `sub`, `email`, `name`, `picture|image`.
- Better Auth helper удаляется, все импорты заменяются на новый helper.

## Login Flow
1. Пользователь на защищенном маршруте без cookie → редирект на `/auth/login?next=<path+search>`.
2. `/auth/login` строит URL `TRAIL_AUTH_BASE_URL/login?returnTo=<callbackUrl>`.
3. BetterAuth редиректит обратно на `/auth/callback?code=...&next=...`.
4. `/auth/callback` вызывает `POST /v1/auth/bridge/exchange` в API с `{ code }`.
5. Берет `snapshot.session.accessToken`, ставит cookie и редиректит на `next` (по умолчанию `/dashboard`).

## Logout Flow
- `/auth/logout` очищает cookie и редиректит на `/`.

## Middleware
- `apps/account/proxy.ts`:
  - Если `ACCOUNT_AUTH_BYPASS=1` → allow.
  - Иначе для `/dashboard`, `/settings`, `/billing`, `/extension` требует cookie.
  - Если нет cookie → редирект на `/auth/login?next=<path+search>`.

## TRPC Proxy
- Всегда посылает `x-trail-internal-key`.
- Если `ACCOUNT_AUTH_BYPASS=1` → `x-trail-user` с dev user.
- Иначе, если cookie есть → `Authorization: Bearer <token>`.

## Cookies
- Имя: `trail_auth_session` (единое для app domain).
- Опции: `httpOnly`, `path=/`, `sameSite=lax`, `secure` в production.

## Env
- Удалить Better Auth переменные из `apps/account/.env.example`.
- Добавить `TRAIL_AUTH_BASE_URL=https://auth.gettrail.net` (если нужно) и убедиться, что `TRAIL_API_BASE_URL` остается.

## Testing
- По запросу пользователя тесты не добавляются. Ручная проверка: login → callback → cookie → защищенные страницы → logout.
