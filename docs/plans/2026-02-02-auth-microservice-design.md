# Auth Microservice + BetterAuth Design

Date: 2026-02-02

## Goals
- Перейти с Auth0 на BetterAuth.
- Вынести авторизацию в отдельный сервис `apps/auth` на домене `auth.gettrail.net`.
- Оставить единую доменную модель пользователя (`User`) в общей БД.
- Валидация пользователя в API через JWT (Bearer), выдаваемый BetterAuth.
- Поддержать email OTP (6 цифр) и OAuth (Google, GitHub).
- Сохранить текущий extension JWT (HMAC) для расширения.

## Non-goals
- Backward compatibility с Auth0.
- Passkeys, SSO, multi-tenant orgs на этом этапе.
- Миграция старых Auth0‑сессий.

## Архитектура
- `apps/auth` — отдельный микросервис:
  - UI авторизации (`/login`, `/otp`, `/oauth/*`).
  - BetterAuth API на `/api/auth/*`.
  - `baseURL = https://auth.gettrail.net`.
- `apps/api`:
  - `/v1/*` API для продукта.
  - Валидация пользователя по Bearer JWT (BetterAuth JWT plugin + JWKS).
- `apps/account`:
  - Клиент BetterAuth, редирект на `auth.gettrail.net`.
  - После входа принимает одноразовый код и обменивает на JWT в API.

## Auth Flow (redirect → code → exchange → JWT)
1. Пользователь нажимает Sign In в `app.gettrail.net`.
2. Редирект на `https://auth.gettrail.net/login?returnTo=https://app.gettrail.net/auth/callback`.
3. В `apps/auth` происходит login (OTP/OAuth).
4. `apps/auth` создаёт одноразовый `AuthBridgeCode` (TTL 60 сек), связывает с userId, JWT и редиректит на:
   `https://app.gettrail.net/auth/callback?code=...`.
5. `apps/account` вызывает `POST /v1/auth/bridge/exchange` в API:
   - API валидирует код, помечает использованным, возвращает `AccountSnapshot`.
6. Дальше `apps/account` ходит в API с `Authorization: Bearer <jwt>`.

## Email OTP
- BetterAuth email OTP plugin.
- OTP длиной 6 цифр (дефолт).
- Отправка через абстракцию `EmailProvider` (первый провайдер — Mailgun).
- Провайдер легко заменить на SMTP/SES/Resend без изменений в auth логике.

## OAuth
- BetterAuth socialProviders: Google, GitHub.
- Redirect URI и callback живут в `auth.gettrail.net`.

## Data Model (Prisma)
- Удалить `User.auth0Id`.
- Добавить модели BetterAuth (CLI `@better-auth/cli generate`):
  - `Account`, `Session`, `Verification` (могут включать `User` — мерджим с текущей моделью).
- Добавить `AuthBridgeCode`:
  - `id`, `code`, `userId`, `jwt`, `expiresAt`, `usedAt`, `createdAt`.
- Настроить BetterAuth `modelName` на существующие Prisma модели.

## API Changes
- Заменить `verifyUserToken`:
  - проверка BetterAuth JWT по JWKS (`https://auth.gettrail.net/api/auth/jwks`).
- В endpoints `auth/portal` и `extension/connect` использовать BetterAuth JWT.
- Добавить `POST /v1/auth/bridge/exchange`.
- Удалить legacy internal routes, связанные с extension login code.

## Migration Plan (high-level)
1. Ввести `apps/auth` и BetterAuth конфиг.
2. Добавить нужные таблицы и миграции.
3. Заменить Auth0 middleware в `apps/account` и `apps/api`.
4. Включить новые login flows.
5. Удалить Auth0 переменные и старые internal routes.

## Risks
- Несоответствие моделей BetterAuth и существующей схемы — решается аккуратным мержем.
- OAuth redirect URI mismatch — решается через `auth.gettrail.net`.
- Смена токенов может затронуть extension портал/коннект — нужно обновить фронт и API синхронно.

## Testing
- Unit tests для `auth/bridge/exchange`.
- Интеграция: login → code exchange → API calls.
- Smoke‑тесты для OAuth callback (manual).
