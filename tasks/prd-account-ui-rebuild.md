# PRD: Ребилд UI приложения Account

> Версия: 1.0
> Дата: 2026-04-02
> Статус: Draft

---

## 1. Обзор

### Цель

Полный ребилд пользовательского интерфейса приложения `apps/account`. Старый UI был удален — остались только API-роуты (`/api/v1/*`) и backend-сервисы. Нужно построить новый веб-интерфейс с нуля, используя современный стек и паттерн "Golden Path".

### Архитектурные решения

- **Golden Path**: единый канонический подход к каждому типу файла (см. секцию 4). Никаких "альтернативных способов" — одна правильная реализация для page, action, client component.
- **REST + Server Actions**: существующие REST API (`/api/v1/*`) остаются для extension. Веб-UI использует **Server Actions** для мутаций, а данные загружает **напрямую из Supabase** в Server Components (не через REST).
- **Разделение**: API-роуты обслуживают extension, Server Actions обслуживают веб-UI. Общая бизнес-логика живет в `src/server/backend/`.

### Текущее состояние

Сохранившийся backend:

| Модуль | Путь | Назначение |
|--------|------|------------|
| Auth | `src/lib/auth.ts` | `getAuthSession()` — Supabase cookie-сессия |
| Supabase Server | `src/lib/supabase/server.ts` | `createSupabaseServerClient()` |
| Supabase Client | `src/lib/supabase/client.ts` | `createSupabaseBrowserClient()` |
| Supabase Middleware | `src/lib/supabase/middleware.ts` | `updateSession()` — refresh cookie |
| User | `src/server/backend/user.ts` | CRUD пользователей, onboarding |
| Subscription | `src/server/backend/subscription-access.ts` | Проверка тиров, snapshot подписки |
| Account Snapshot | `src/server/backend/account-snapshot.ts` | `buildAccountSnapshot()` |
| Trail Serializers | `src/server/backend/trail-serializers.ts` | `toTrailSummary()`, `toTrailRecord()` |
| Onboarding | `src/server/onboarding.ts` | `buildOnboardingState()` |
| Plans | `packages/content/src/plans.ts` | `trailPlans` — определения планов |
| Billing | `src/server/backend/billing/provider.ts` | `getBillingProvider()` |

---

## 2. Стек

| Технология | Версия | Роль |
|-----------|--------|------|
| Next.js | 16 (App Router) | Фреймворк |
| React | 19 | UI-библиотека |
| TypeScript | 5.x | Типизация |
| Tailwind CSS | v4 | Стилизация |
| shadcn/ui | latest | Компонентная библиотека (reinit через CLI) |
| Supabase | — | Auth (Google OAuth + Magic Link), PostgreSQL |
| Zod | 3.x | Валидация (уже используется в schemas.ts) |

### Инициализация shadcn/ui

```bash
cd apps/account
npx shadcn@latest init --defaults
```

Минимальный набор компонентов для старта:

```bash
npx shadcn@latest add button card input label separator skeleton tabs badge dialog dropdown-menu avatar sheet sidebar toast
```

---

## 3. Страницы

### 3.1. `/login` — Авторизация

**Описание**: Страница входа. Два способа: Google OAuth и Magic Link (email). Незалогиненный пользователь перенаправляется сюда middleware. После успешной авторизации — redirect на `/trails` (или `returnTo`).

**Data flow**:
- Server Component проверяет `getAuthSession()` — если сессия есть, redirect на `/trails`
- Google OAuth: `supabase.auth.signInWithOAuth({ provider: "google" })`  — клиентский вызов
- Magic Link: `supabase.auth.signInWithOtp({ email })` — клиентский вызов
- Callback: `/auth/callback` (уже реализован) обменивает code на сессию

**Acceptance criteria**:
- [ ] Страница отображается по `/login`
- [ ] Кнопка "Sign in with Google" запускает OAuth flow через Supabase
- [ ] Поле email + кнопка "Send magic link" отправляет OTP
- [ ] После отправки magic link показывается сообщение "Проверьте почту"
- [ ] Ошибки авторизации отображаются inline (toast или alert)
- [ ] Если пользователь уже авторизован — redirect на `/trails`
- [ ] `returnTo` query param пробрасывается через весь flow
- [ ] Responsive: корректно выглядит на мобильных (centered card)
- [ ] Нет flash of unauthenticated content (проверка на сервере)

---

### 3.2. `/onboarding` — Онбординг

**Описание**: 4-шаговый flow для новых пользователей. Показывается один раз (после первой авторизации, если `onboarding_seen_at IS NULL`). Шаги: (1) Welcome, (2) Install extension, (3) Create first trail, (4) Done.

**Data flow**:
- Server Component: `getAuthSession()` + `getUserById(userId)` — проверка `onboardingSeenAt`
- Если `onboardingSeenAt !== null` — redirect на `/trails`
- Прогресс по шагам: клиентский state (не сохраняется на сервере между шагами)
- Завершение: Server Action вызывает `markUserOnboardingSeen(userId)`

**Backend**:
- `GET /api/v1/onboarding` — текущий статус (`buildOnboardingState`)
- `POST /api/v1/onboarding` — body: `{ action: "complete" | "skip" }` → `markUserOnboardingSeen()`

**Acceptance criteria**:
- [ ] Redirect на `/onboarding` при первом входе (onboarding не пройден)
- [ ] 4 шага отображаются как stepper (progress indicator)
- [ ] Шаг "Install Extension" содержит ссылку на Chrome Web Store
- [ ] Кнопка "Skip" доступна на каждом шаге
- [ ] Завершение (или Skip) вызывает Server Action → `markUserOnboardingSeen`
- [ ] После завершения — redirect на `/trails`
- [ ] Повторный заход на `/onboarding` при пройденном онбординге — redirect на `/trails`

---

### 3.3. `/trails` — Список деревьев

**Описание**: Основная страница. Показывает все деревья пользователя с cursor-based пагинацией. Поддержка фильтрации и soft-delete (архив).

**Data flow**:
- Server Component: `getAuthSession()` → `userId`
- Данные: **прямой запрос в Supabase** (аналогично логике из `GET /api/v1/trails`):
  ```
  db.from("trails").select("*").eq("user_id", userId).is("deleted_at", null)
    .order("updated_at", { ascending: false }).limit(limit + 1)
  ```
- Cursor-based пагинация: `updatedAt|id` — клиентская навигация загружает следующую порцию через Server Action
- Total count: отдельный `select("*", { count: "exact", head: true })`

**Zod-схема ответа** (из `schemas.ts`):
```typescript
trailsListQuerySchema = {
  limit: number (1..200, default 50),
  cursor: string | null,
  includeDeleted: boolean (default false),
}
```

**Формат элемента списка** (из `toTrailSummary()`):
```typescript
{
  id: string,
  userId: string,
  deviceId: string,
  label: string,
  labelSource: "user" | "auto" | "system",
  labelUpdatedAt: string (ISO),
  createdAt: string (ISO),
  updatedAt: string (ISO),
  savedAt: string (ISO),
  nodeCount: number,
  rootUrl: string | null,
  rootTitle: string | null,
  rootFavicon: string | null,
  deletedAt: string | null,
}
```

**Acceptance criteria**:
- [ ] Список деревьев загружается при открытии страницы
- [ ] Каждый элемент показывает: label, nodeCount, rootUrl (favicon если есть), updatedAt (относительное время)
- [ ] Cursor-based пагинация: кнопка "Load more" / infinite scroll
- [ ] Показан totalCount ("X деревьев")
- [ ] Фильтр "Show archived" (includeDeleted toggle)
- [ ] Soft-delete: кнопка "Archive" на каждом элементе → PATCH `{ deletedAt: now }` через Server Action
- [ ] Restore: для архивных — кнопка "Restore" → PATCH `{ deletedAt: null }` через Server Action
- [ ] Inline rename: клик на label → editable field → PATCH `{ label, labelSource: "user" }` через Server Action
- [ ] Клик на элемент → переход на `/trails/[id]`
- [ ] Empty state: сообщение + ссылка на установку extension
- [ ] Loading state: skeleton cards
- [ ] Responsive: на мобильных — single column

---

### 3.4. `/trails/[id]` — Детальный вид дерева

**Описание**: Полный вид одного дерева. Показывает метаданные, дерево нод (payload), node inspector, экспорт.

**Data flow**:
- Server Component: `getAuthSession()` → проверка авторизации
- Данные: прямой запрос в Supabase (аналогично `GET /api/v1/trails/[id]`):
  ```
  db.from("trails").select("*").eq("id", id).eq("user_id", userId)
    .is("deleted_at", null).maybeSingle()
  ```
- Полный `payload` (tree structure) включен в ответ

**Формат ответа** (из `toTrailRecord()`):
```typescript
{
  // все поля из TrailSummary +
  payload: unknown, // { root: TreeNode, nodeCount: number }
}
```

**Структура payload** (из `treeNodeSchema`):
```typescript
type TreeNode = {
  data?: Record<string, unknown>,  // { url, title, favicon, ... }
  children?: TreeNode[],
}

type TreePayload = {
  root: TreeNode,
  nodeCount: number,
}
```

**Acceptance criteria**:
- [ ] Страница загружает и показывает метаданные дерева (label, nodeCount, dates)
- [ ] Дерево отрисовывается как интерактивная структура (раскрываемые ноды)
- [ ] Клик на ноду показывает node inspector (sidebar/panel): url, title, favicon
- [ ] Кнопка "Export" — скачивает JSON в формате `trail.export.v1`
- [ ] Кнопка "Rename" — inline edit label → Server Action PATCH
- [ ] Кнопка "Archive" → Server Action DELETE (soft-delete) → redirect на `/trails`
- [ ] 404 page если дерево не найдено
- [ ] Breadcrumb: "Trails > [label]"
- [ ] Loading state: skeleton
- [ ] Responsive: tree и inspector переключаются tab-ами на мобильных

---

### 3.5. `/settings` — Настройки аккаунта

**Описание**: Профиль пользователя, управление сессиями, привязанные устройства.

**Data flow**:
- Server Component: `getAuthSession()` → `getUserById(userId)`
- Профиль: `name`, `email`, `imageUrl`, `createdAt`
- Подписка (краткая): `getSubscriptionSnapshotForUser()` → показ текущего плана
- Onboarding reset: `resetUserOnboarding(userId)` через Server Action

**Acceptance criteria**:
- [ ] Секция "Profile": аватар, имя, email (read-only из Supabase)
- [ ] Секция "Subscription": текущий план (badge), ссылка на `/billing`
- [ ] Секция "Danger Zone": кнопка "Reset Onboarding" (вызывает `resetUserOnboarding`)
- [ ] Кнопка "Sign Out" → redirect на `/auth/logout`
- [ ] Responsive layout

---

### 3.6. `/billing` — Планы и подписка

**Описание**: Управление подпиской. Показ доступных планов, текущей подписки, checkout/cancel/resume.

**Data flow**:
- Server Component: `getAuthSession()` → userId
- Планы: `listPlans()` (прямой вызов, не через REST)
- Подписка: `getSubscriptionSnapshotForUser({ userId, fallbackCreatedAt })`
- Checkout: Server Action → вызывает `getBillingProvider().createCheckoutSession()`
- Cancel: Server Action → DB update `cancel_at_period_end = true` (логика из `POST /api/v1/subscription/cancel`)
- Resume: Server Action → DB update `cancel_at_period_end = false` (логика из `POST /api/v1/subscription/resume`)
- Billing Portal: Server Action → `getBillingProvider().createBillingPortalSession()` → redirect

**Данные планов** (из `packages/content/src/plans.ts`):
```typescript
type TrailPlanDefinition = {
  id: "free" | "pro" | "teams",
  name: string,
  tier: string,
  priceMonthly: number,
  priceYearly: number,
  currency: "USD",
  features: string[],
  limits: { maxTrees: number, maxDevices: number, maxHistoryDays: number },
  highlight?: boolean,
  rank?: number,
}
```

**Данные подписки** (из `SubscriptionSnapshot`):
```typescript
{
  id: string,
  planId: "free" | "pro" | "teams",
  status: "trialing" | "active" | "past_due" | "paused" | "expired",
  interval: "month" | "year" | null,
  pendingInterval: "month" | "year" | null,
  currentPeriodStart: string | null,
  currentPeriodEnd: string | null,
  cancelAtPeriodEnd: boolean,
  trialEndsAt: string | null,
  canceledAt: string | null,
}
```

**Checkout body** (из `subscriptionCheckoutBodySchema`):
```typescript
{
  planId: "pro" | "teams",
  interval: "month" | "year",
  successUrl?: string,
  cancelUrl?: string,
}
```

**Acceptance criteria**:
- [ ] Pricing table: 3 колонки (Free / Pro / Teams) с features и ценами
- [ ] Toggle "Monthly / Yearly" переключает цены
- [ ] Текущий план выделен badge-ем "Current"
- [ ] Кнопка "Upgrade" на планах выше текущего → checkout flow
- [ ] Кнопка "Downgrade" при переходе на Free → cancel flow
- [ ] Если `cancelAtPeriodEnd === true`: показать "Cancels on [date]" + кнопка "Resume"
- [ ] Если `status === "past_due"`: warning banner "Payment overdue"
- [ ] Если `status === "trialing"`: badge "Trial ends [date]"
- [ ] Ссылка "Manage billing" → billing portal (redirect на Stripe/провайдер)
- [ ] Responsive: карточки планов — stack на мобильных

---

### 3.7. `/activity` — Лог активности

**Описание**: Хронологический лог действий пользователя. Источник данных: таблица trails (сортировка по `updated_at`), а в будущем — отдельная таблица audit log.

**Data flow**:
- Server Component: `getAuthSession()` → userId
- Данные (Phase 1): последние N деревьев с метаданными, сгруппированные по дате
  ```
  db.from("trails").select("id, label, updated_at, created_at, node_count, root_url")
    .eq("user_id", userId).order("updated_at", { ascending: false }).limit(50)
  ```
- Phase 2 (future): отдельная таблица `user_activity_log`

**Acceptance criteria**:
- [ ] Timeline: список событий, сгруппированных по дням
- [ ] Каждое событие: icon + description + timestamp
- [ ] Типы событий Phase 1: "Trail updated", "Trail created"
- [ ] Клик на событие → переход на `/trails/[id]`
- [ ] Empty state при отсутствии активности
- [ ] Loading state: skeleton timeline

---

## 4. Golden Path шаблоны

### 4.1. Server Component Page

```typescript
// app/trails/page.tsx
import { redirect } from "next/navigation";
import { getAuthSession } from "@/src/lib/auth";
import { db } from "@trail/db";
import { TrailsList } from "./trails-list";

export default async function TrailsPage() {
  const session = await getAuthSession();
  if (!session) {
    redirect("/login");
  }

  const { data: trails, count } = await db
    .from("trails")
    .select("*", { count: "exact" })
    .eq("user_id", session.user.id)
    .is("deleted_at", null)
    .order("updated_at", { ascending: false })
    .limit(50);

  return (
    <main className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Your Trails</h1>
      <TrailsList
        initialTrails={trails ?? []}
        totalCount={count ?? 0}
      />
    </main>
  );
}
```

### 4.2. Server Action (mutations.ts)

```typescript
// app/trails/mutations.ts
"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { getAuthSession } from "@/src/lib/auth";
import { db } from "@trail/db";

const renameSchema = z.object({
  trailId: z.string().uuid(),
  label: z.string().min(1).max(200),
});

export type RenameState = {
  error?: string;
  success?: boolean;
};

export async function renameTrail(
  _prev: RenameState,
  formData: FormData,
): Promise<RenameState> {
  const session = await getAuthSession();
  if (!session) {
    return { error: "Unauthorized" };
  }

  const parsed = renameSchema.safeParse({
    trailId: formData.get("trailId"),
    label: formData.get("label"),
  });

  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }

  const { trailId, label } = parsed.data;
  const now = new Date().toISOString();

  const result = await db
    .from("trails")
    .update({
      label,
      label_source: "USER",
      label_updated_at: now,
      updated_at: now,
    })
    .eq("id", trailId)
    .eq("user_id", session.user.id);

  if (result.error) {
    return { error: "Failed to rename trail" };
  }

  revalidatePath("/trails");
  return { success: true };
}
```

### 4.3. Client Component

```typescript
// app/trails/trails-list.tsx
"use client";

import { useActionState, useTransition } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { archiveTrail, loadMoreTrails } from "./mutations";

type Trail = {
  id: string;
  label: string;
  nodeCount: number;
  updatedAt: string;
  rootUrl: string | null;
  rootFavicon: string | null;
};

type Props = {
  initialTrails: Trail[];
  totalCount: number;
};

export function TrailsList({ initialTrails, totalCount }: Props) {
  const [isPending, startTransition] = useTransition();

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        {totalCount} trails
      </p>

      {initialTrails.map((trail) => (
        <Card key={trail.id}>
          <CardHeader>
            <CardTitle className="text-base">{trail.label}</CardTitle>
            <CardDescription>
              {trail.nodeCount} nodes
              {trail.rootUrl && (
                <span className="ml-2 text-xs">{trail.rootUrl}</span>
              )}
            </CardDescription>
          </CardHeader>
        </Card>
      ))}

      {initialTrails.length < totalCount && (
        <Button
          variant="outline"
          disabled={isPending}
          onClick={() => startTransition(() => { /* load more */ })}
        >
          {isPending ? "Loading..." : "Load more"}
        </Button>
      )}
    </div>
  );
}
```

### 4.4. Loading / Error / Not-Found States

```typescript
// app/trails/loading.tsx
import { Skeleton } from "@/components/ui/skeleton";

export default function TrailsLoading() {
  return (
    <main className="container mx-auto py-8">
      <Skeleton className="h-8 w-48 mb-6" />
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-lg" />
        ))}
      </div>
    </main>
  );
}
```

```typescript
// app/trails/error.tsx
"use client";

import { Button } from "@/components/ui/button";

export default function TrailsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="container mx-auto py-8 text-center">
      <h2 className="text-xl font-semibold mb-4">Something went wrong</h2>
      <p className="text-muted-foreground mb-6">{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </main>
  );
}
```

```typescript
// app/trails/[id]/not-found.tsx
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function TrailNotFound() {
  return (
    <main className="container mx-auto py-8 text-center">
      <h2 className="text-xl font-semibold mb-4">Trail not found</h2>
      <p className="text-muted-foreground mb-6">
        This trail doesn't exist or has been deleted.
      </p>
      <Button asChild>
        <Link href="/trails">Back to trails</Link>
      </Button>
    </main>
  );
}
```

---

## 5. API контракт

### Таблица: страница -> источники данных

| Страница | Тип | Источник данных | Метод |
|----------|-----|----------------|-------|
| `/login` | Read | `getAuthSession()` | Server Component (redirect check) |
| `/login` | Mutation | `supabase.auth.signInWithOAuth()` | Client-side Supabase SDK |
| `/login` | Mutation | `supabase.auth.signInWithOtp()` | Client-side Supabase SDK |
| `/onboarding` | Read | `getUserById(userId)` → `onboardingSeenAt` | Server Component |
| `/onboarding` | Mutation | `markUserOnboardingSeen(userId)` | Server Action |
| `/trails` | Read | `db.from("trails").select(*)` | Server Component |
| `/trails` | Mutation | `db.from("trails").update({ label })` | Server Action (rename) |
| `/trails` | Mutation | `db.from("trails").update({ deleted_at })` | Server Action (archive/restore) |
| `/trails` | Read | Load more (cursor pagination) | Server Action (fetch next page) |
| `/trails/[id]` | Read | `db.from("trails").select(*).eq("id", id)` | Server Component |
| `/trails/[id]` | Mutation | `db.from("trails").update({ label })` | Server Action (rename) |
| `/trails/[id]` | Mutation | `db.from("trails").update({ deleted_at })` | Server Action (archive) |
| `/settings` | Read | `getUserById(userId)` | Server Component |
| `/settings` | Read | `getSubscriptionSnapshotForUser()` | Server Component |
| `/settings` | Mutation | `resetUserOnboarding(userId)` | Server Action |
| `/billing` | Read | `listPlans()` | Server Component |
| `/billing` | Read | `getSubscriptionSnapshotForUser()` | Server Component |
| `/billing` | Mutation | `getBillingProvider().createCheckoutSession()` | Server Action → redirect |
| `/billing` | Mutation | Cancel subscription (DB update) | Server Action |
| `/billing` | Mutation | Resume subscription (DB update) | Server Action |
| `/billing` | Mutation | `getBillingProvider().createBillingPortalSession()` | Server Action → redirect |
| `/activity` | Read | `db.from("trails").select(subset)` | Server Component |

### REST API (используются extension-ом, НЕ веб-UI)

| Endpoint | Method | Назначение |
|----------|--------|------------|
| `/api/v1/account` | GET | Account snapshot (для extension) |
| `/api/v1/trails` | GET | Список деревьев (cursor pagination) |
| `/api/v1/trails/[id]` | GET | Детали дерева |
| `/api/v1/trails/[id]` | PUT | Full upsert (extension sync) |
| `/api/v1/trails/[id]` | PATCH | Partial update |
| `/api/v1/trails/[id]` | DELETE | Soft delete |
| `/api/v1/trails/[id]/restore` | POST | Restore from archive |
| `/api/v1/trails/sync` | POST | Bulk sync |
| `/api/v1/trails/import` | POST | Import trail bundle |
| `/api/v1/plans` | GET | Список планов (public) |
| `/api/v1/subscription` | GET | Текущая подписка |
| `/api/v1/subscription/checkout` | POST | Создать checkout сессию |
| `/api/v1/subscription/cancel` | POST | Отменить подписку |
| `/api/v1/subscription/resume` | POST | Возобновить подписку |
| `/api/v1/billing` | GET | Billing status |
| `/api/v1/billing/portal` | POST | Billing portal ссылка |
| `/api/v1/onboarding` | GET | Статус онбординга |
| `/api/v1/onboarding` | POST | Отметить онбординг пройденным |
| `/api/v1/oauth/*` | * | OAuth flow для extension |

---

## 6. Дизайн

### 6.1. Инициализация shadcn/ui

```bash
# Из корня apps/account:
npx shadcn@latest init

# Ответы:
# Style: Default
# Base color: Neutral
# CSS variables: yes
# Tailwind CSS: v4
# React Server Components: yes
```

### 6.2. Цветовая схема

Использовать стандартную neutral palette от shadcn с кастомным accent:

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --color-background: hsl(0 0% 100%);
  --color-foreground: hsl(0 0% 3.9%);
  --color-muted: hsl(0 0% 96.1%);
  --color-muted-foreground: hsl(0 0% 45.1%);
  --color-primary: hsl(0 0% 9%);
  --color-primary-foreground: hsl(0 0% 98%);
  --color-accent: hsl(142 71% 45%); /* Trail green */
  --color-destructive: hsl(0 84.2% 60.2%);
}

.dark {
  --color-background: hsl(0 0% 3.9%);
  --color-foreground: hsl(0 0% 98%);
  --color-muted: hsl(0 0% 14.9%);
  --color-muted-foreground: hsl(0 0% 63.9%);
  --color-primary: hsl(0 0% 98%);
  --color-primary-foreground: hsl(0 0% 9%);
}
```

### 6.3. Layout система

**Sidebar + Main Content** — классический dashboard layout.

```
+--------------------------------------------------+
| Sidebar (240px)  |  Main Content                  |
|                  |                                 |
| Logo             |  Page Header                   |
| ──────────       |  ───────────                    |
| Trails           |                                 |
| Activity         |  [Page Content]                 |
| ──────────       |                                 |
| Settings         |                                 |
| Billing          |                                 |
| ──────────       |                                 |
| User Avatar      |                                 |
| Sign Out         |                                 |
+--------------------------------------------------+
```

На мобильных: sidebar скрывается, открывается через Sheet (hamburger menu).

**Файловая структура layout**:

```
app/
├── layout.tsx              # Root: html, body, fonts
├── login/
│   └── page.tsx            # Без sidebar (standalone)
├── onboarding/
│   └── page.tsx            # Без sidebar (standalone, fullscreen stepper)
├── (dashboard)/
│   ├── layout.tsx          # Sidebar + main content wrapper
│   ├── trails/
│   │   ├── page.tsx
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   ├── mutations.ts
│   │   ├── trails-list.tsx
│   │   └── [id]/
│   │       ├── page.tsx
│   │       ├── loading.tsx
│   │       ├── not-found.tsx
│   │       ├── mutations.ts
│   │       └── trail-detail.tsx
│   ├── settings/
│   │   ├── page.tsx
│   │   └── mutations.ts
│   ├── billing/
│   │   ├── page.tsx
│   │   ├── mutations.ts
│   │   └── pricing-table.tsx
│   └── activity/
│       ├── page.tsx
│       └── loading.tsx
├── auth/
│   ├── callback/route.ts   # (существует)
│   ├── login/route.ts      # (существует)
│   ├── logout/route.ts     # (существует)
│   └── extension-relay/
│       └── page.tsx         # (существует)
└── api/
    └── v1/                  # (все существует, не трогаем)
```

### 6.4. Dashboard Layout Component

```typescript
// app/(dashboard)/layout.tsx
import { redirect } from "next/navigation";
import { getAuthSession } from "@/src/lib/auth";
import { getUserById } from "@/src/server/backend/user";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getAuthSession();
  if (!session) {
    redirect("/login");
  }

  const user = await getUserById(session.user.id);
  if (user && !user.onboardingSeenAt) {
    redirect("/onboarding");
  }

  return (
    <SidebarProvider>
      <AppSidebar user={session.user} />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </SidebarProvider>
  );
}
```

### 6.5. Middleware (Auth Guard)

Создать `apps/account/middleware.ts`:

```typescript
import { type NextRequest, NextResponse } from "next/server";
import { updateSession } from "@/src/lib/supabase/middleware";

const PUBLIC_PATHS = [
  "/login",
  "/auth/",
  "/api/",
];

export async function middleware(request: NextRequest) {
  const { supabaseResponse, user } = await updateSession(request);
  const { pathname } = request.nextUrl;

  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));

  if (!user && !isPublic) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("returnTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return supabaseResponse;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|brand/|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
```

---

## 7. Промпт для AI

### 7.1. Шаблон промпта

```
Реализуй страницу `{PAGE_PATH}` для приложения Trail Account.

## Контекст
- Next.js 16 App Router, React 19, Tailwind CSS v4, shadcn/ui
- Auth: Supabase (cookie session через `getAuthSession()` из `@/src/lib/auth`)
- DB: Supabase client через `db` из `@trail/db`
- Мутации: Server Actions с Zod-валидацией
- Стилизация: shadcn/ui компоненты + Tailwind utility classes

## Что создать

### Файлы:
{LIST_OF_FILES}

### Данные:
{DATA_SOURCE_DESCRIPTION}

### Server Actions:
{MUTATIONS_DESCRIPTION}

### UI требования:
{ACCEPTANCE_CRITERIA}

## Golden Path правила:
1. Page — async Server Component. Проверяет `getAuthSession()`, redirect если нет.
2. Данные загружаются напрямую из Supabase в Server Component (не через fetch к API).
3. Мутации — отдельный файл `mutations.ts` с "use server". Каждая функция принимает `(prevState, formData)` для `useActionState`.
4. Валидация входных данных — Zod schema, `safeParse`.
5. Client Components — отдельные файлы с "use client". Минимум клиентского кода.
6. Loading state — `loading.tsx` с Skeleton.
7. Error state — `error.tsx` с кнопкой retry.
8. Not Found — `not-found.tsx` где применимо.
9. `revalidatePath()` после каждой мутации.
10. Никаких `console.log` в продакшен-коде.

## Доступные backend-функции:
- `getAuthSession()` → `{ user: { id, email, name, imageUrl } } | null`
- `getUserById(userId)` → `{ id, email, name, imageUrl, createdAt, onboardingSeenAt } | null`
- `getSubscriptionSnapshotForUser({ userId, fallbackCreatedAt })` → `SubscriptionSnapshot | null`
- `listPlans()` → `TrailPlanDefinition[]`
- `markUserOnboardingSeen(userId)` → `Date | null`
- `resetUserOnboarding(userId)` → `boolean`
- `getBillingProvider().createCheckoutSession({...})` → checkout URL
- `getBillingProvider().createBillingPortalSession({...})` → portal URL
- `db.from("trails")...` → Supabase query builder
```

### 7.2. Пример заполненного промпта для `/trails`

```
Реализуй страницу `/trails` для приложения Trail Account.

## Контекст
- Next.js 16 App Router, React 19, Tailwind CSS v4, shadcn/ui
- Auth: Supabase (cookie session через `getAuthSession()` из `@/src/lib/auth`)
- DB: Supabase client через `db` из `@trail/db`
- Мутации: Server Actions с Zod-валидацией
- Стилизация: shadcn/ui компоненты + Tailwind utility classes

## Что создать

### Файлы:
- `app/(dashboard)/trails/page.tsx` — Server Component, загрузка списка деревьев
- `app/(dashboard)/trails/loading.tsx` — Skeleton-загрузка (5 карточек)
- `app/(dashboard)/trails/error.tsx` — Обработка ошибок с кнопкой retry
- `app/(dashboard)/trails/mutations.ts` — Server Actions: archiveTrail, restoreTrail, renameTrail, loadMoreTrails
- `app/(dashboard)/trails/trails-list.tsx` — Client Component: список с пагинацией и inline edit

### Данные:
Основной запрос (Server Component):
```ts
const { data: trails, count } = await db
  .from("trails")
  .select("id, user_id, device_id, label, label_source, label_updated_at, created_at, updated_at, saved_at, node_count, root_url, root_title, root_favicon, deleted_at", { count: "exact" })
  .eq("user_id", session.user.id)
  .is("deleted_at", null)
  .order("updated_at", { ascending: false })
  .limit(50);
```

Load more (Server Action):
```ts
// Cursor-based: получаем cursor = "updatedAt|id" от клиента
const cursor = parseCursor(cursorString);
let query = db.from("trails").select("*")
  .eq("user_id", userId).is("deleted_at", null)
  .order("updated_at", { ascending: false })
  .order("id", { ascending: false })
  .limit(limit + 1);

if (cursor) {
  query = query.or(
    `updated_at.lt.${cursor.updatedAt.toISOString()},and(updated_at.eq.${cursor.updatedAt.toISOString()},id.lt.${cursor.id})`
  );
}
```

Тип элемента:
```ts
type TrailSummary = {
  id: string;
  label: string;
  labelSource: "user" | "auto" | "system";
  updatedAt: string;    // ISO
  createdAt: string;    // ISO
  nodeCount: number;
  rootUrl: string | null;
  rootFavicon: string | null;
  deletedAt: string | null;
};
```

### Server Actions (`mutations.ts`):

1. `renameTrail(prev, formData)` — обновляет label + label_source="USER" + label_updated_at
2. `archiveTrail(prev, formData)` — устанавливает deleted_at = now
3. `restoreTrail(prev, formData)` — устанавливает deleted_at = null
4. `loadMoreTrails(prev, formData)` — возвращает следующую страницу по cursor

Все Server Actions:
- Проверяют `getAuthSession()`
- Валидируют input через Zod
- Возвращают `{ error?: string; success?: boolean; data?: T }`
- Вызывают `revalidatePath("/trails")` после мутации

### UI требования:
- [ ] Список деревьев в виде карточек (Card из shadcn)
- [ ] Каждая карточка: favicon (если есть) + label + nodeCount + relative time (updatedAt)
- [ ] Header страницы: "Your Trails" + badge с totalCount
- [ ] Cursor-based пагинация: кнопка "Load more" внизу списка
- [ ] Toggle "Show archived" — переключает includeDeleted
- [ ] Inline rename: double-click на label → Input → Enter/Blur = save
- [ ] Dropdown menu на каждой карточке: Rename, Archive (или Restore для archived)
- [ ] Empty state: иллюстрация + текст "No trails yet" + ссылка на extension
- [ ] Skeleton loader: 5 карточек-скелетонов при загрузке
- [ ] Клик на карточку → `router.push(\`/trails/${trail.id}\`)`
- [ ] Responsive: 1 колонка на mobile, 2-3 на desktop (grid)

## Golden Path правила:
1. Page — async Server Component. Проверяет `getAuthSession()`, redirect если нет.
2. Данные загружаются напрямую из Supabase в Server Component.
3. Мутации — `mutations.ts` с "use server". Функция = `(prevState, formData) => Promise<State>`.
4. Валидация — Zod, `safeParse`.
5. Client Components — `trails-list.tsx` с "use client".
6. `revalidatePath("/trails")` после каждой мутации.
7. Никаких `console.log`.

## Доступные backend-функции:
- `getAuthSession()` из `@/src/lib/auth`
- `db` из `@trail/db` (Supabase client)
```

---

## Приложение A: Порядок реализации

Рекомендуемая последовательность для пошаговой реализации:

1. **shadcn/ui init** + `globals.css` + fonts
2. **Middleware** (`middleware.ts`) — auth guard
3. **Root layout** (`app/layout.tsx`) — обновить с провайдерами
4. **Dashboard layout** (`app/(dashboard)/layout.tsx`) — sidebar
5. **`/login`** — standalone page, не требует sidebar
6. **`/onboarding`** — standalone page
7. **`/trails`** — основная страница, тестирует весь pipeline
8. **`/trails/[id]`** — деталь дерева
9. **`/billing`** — pricing + subscription management
10. **`/settings`** — профиль
11. **`/activity`** — лог (можно отложить)

Каждый шаг — отдельный PR, проверяемый изолированно.
