# Trail Edit Save/Cancel Reliability Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Добавить на страницу редактирования трейла явные `Save` и `Cancel`, где `Save` завершает режим редактирования только после подтверждённого сохранения на бэкенде, а при ошибках пользователь остаётся в режиме редактирования с понятным сообщением.

**Architecture:** Текущее место управления — `EditInExtensionButton` в account-приложении + postMessage bridge (`apps/account/src/lib/trail-extension.ts`) + extension background handler (`site-message-handlers.ts` / `editor-handlers.ts`) + сервис синхронизации (`editor-sync.ts`). Меняем контракт выхода из editor mode: вместо «вышли в любом случае» вводим явные действия `save` и `cancel` с результатом `ok/error`. Для `cancel` добавляем откат к снимку, сделанному при входе в editor mode, чтобы не оставлять «полусохранённое» состояние.

**Tech Stack:** Next.js 16, React 19, TypeScript, postMessage bridge (site/content/background), Chrome Extension background services, Vitest (account), extension `tests/basic.test.ts`.

---

### Task 1: Зафиксировать поведение Save/Cancel как контракт

**Files:**
- Modify: `docs/plans/2026-02-13-trail-edit-save-cancel-implementation-plan.md`

**Step 1: Зафиксировать бизнес-правила в этом документе**
- `Save`: завершает редактирование только если backend sync завершился успешно.
- `Cancel`: отменяет изменения текущей editor-сессии и выходит из режима редактирования без коммита изменений этой сессии.
- При любой ошибке `Save/Cancel`: не выходим из editing, показываем error.

**Step 2: Зафиксировать UX-состояния кнопок**
- `editing-idle`, `saving`, `cancelling`, `error`.
- Во время `saving/cancelling` обе кнопки disabled.

**Step 3: Commit**
```bash
git add docs/plans/2026-02-13-trail-edit-save-cancel-implementation-plan.md
git commit -m "Define save/cancel contract for trail editor"
```

### Task 2: Написать падающие тесты для UI-контракта на стороне account

**Files:**
- Create: `apps/account/app/(app)/trails/[id]/__tests__/EditInExtensionButton.test.tsx`
- Modify: `apps/account/app/(app)/trails/[id]/EditInExtensionButton.tsx`
- Modify: `apps/account/src/lib/trail-extension.ts`

**Step 1: Написать тест `shows Save and Cancel in editing state`**
- Проверить, что вместо текущего `Done` рендерятся две кнопки: `Save` и `Cancel`.

**Step 2: Написать тест `save success exits editing and refreshes`**
- Мокнуть bridge-вызов `saveEditorMode()` как success.
- Проверить: состояние выходит из editing, `router.refresh()` вызван ровно 1 раз.

**Step 3: Написать тест `save failure keeps editing and shows error`**
- Мокнуть `saveEditorMode()` как error.
- Проверить: статус остаётся editing, ошибка видна в UI, `router.refresh()` не вызывается.

**Step 4: Написать тест `cancel failure keeps editing and shows error`**
- Мокнуть `cancelEditorMode()` как error.
- Проверить: остаёмся в editing, показываем ошибку.

**Step 5: Запустить тесты и зафиксировать падение до реализации**
Run: `pnpm -C apps/account test -- EditInExtensionButton`
Expected: FAIL из-за отсутствия новой логики/методов.

**Step 6: Commit**
```bash
git add apps/account/app/(app)/trails/[id]/__tests__/EditInExtensionButton.test.tsx
git commit -m "Add failing tests for editor save cancel flow"
```

### Task 3: Расширить postMessage-протокол для явных Save/Cancel результатов

**Files:**
- Modify: `apps/account/src/lib/trail-extension.ts`
- Modify: `extension/src/shared/schemas/site-messages.ts`
- Modify: `extension/src/content/content-script.ts`
- Modify: `extension/src/background/messaging/handlers/site-message-handlers.ts`

**Step 1: Добавить bridge API**
- В `trail-extension.ts` добавить `saveEditorMode()` и `cancelEditorMode()`.
- Нормализовать ответ к виду `SendResult<{ ok: boolean; error?: string }>`.

**Step 2: Обновить allowed message types в content-script**
- Добавить новые типы сообщений для `SAVE_EDITOR_MODE` и `CANCEL_EDITOR_MODE`.

**Step 3: Обновить background site handler**
- Развести обработчики на два сценария: save и cancel.
- Возвращать в ACK поле `error` при неуспехе (вместо молчаливого успеха).

**Step 4: Добавить валидацию схем протокола**
- Расширить `site-messages.ts`, чтобы схема ACK позволяла переносить `error` для выхода из editor mode.

**Step 5: Commit**
```bash
git add apps/account/src/lib/trail-extension.ts extension/src/shared/schemas/site-messages.ts extension/src/content/content-script.ts extension/src/background/messaging/handlers/site-message-handlers.ts
git commit -m "Add explicit save cancel editor mode protocol"
```

### Task 4: Исправить корневую проблему в extension backend (надежный flush + cancel rollback)

**Files:**
- Modify: `extension/src/background/services/editor-sync.ts`
- Modify: `extension/src/background/messaging/handlers/editor-handlers.ts`

**Step 1: Сделать `editorSyncFlush` результативным**
- Вернуть структурированный результат (`ok/error`), а не `Promise<void>`.
- Ошибки PATCH/timeout/retry exhaustion должны возвращаться наверх.

**Step 2: В `editor-handlers.ts` добавить два явных пути**
- `saveEditorMode`: вызывает flush, при ошибке не выключает `editorState.active`.
- `cancelEditorMode`: откатывает дерево к snapshot на момент `enterEditorMode`, после чего закрывает editing.

**Step 3: Сохранить snapshot при входе в editing**
- На `enterEditorMode` сохранить JSON снимок, чтобы `cancel` мог выполнить rollback.

**Step 4: Гарантировать правильные события и cleanup**
- `broadcastEditorExitToSite()` и `notifyTreeUpdate(..., 'editor-exit')` отправлять только при успешном завершении `save` или успешной отмене `cancel`.

**Step 5: Commit**
```bash
git add extension/src/background/services/editor-sync.ts extension/src/background/messaging/handlers/editor-handlers.ts
git commit -m "Make editor exit depend on sync success and add cancel rollback"
```

### Task 5: Реализовать UI-кнопки Save/Cancel и обработку ошибок без выхода из editing

**Files:**
- Modify: `apps/account/app/(app)/trails/[id]/EditInExtensionButton.tsx`

**Step 1: Заменить текущий single-action editing UI**
- Удалить `Done`.
- Добавить две кнопки: `Save` и `Cancel`.

**Step 2: Подключить новые действия**
- `Save` вызывает `saveEditorMode()`.
- `Cancel` вызывает `cancelEditorMode()`.

**Step 3: Обновить state machine кнопки**
- Добавить состояния `saving` и `cancelling`.
- При error возвращаться в `editing` и показывать текст ошибки.

**Step 4: Защитить UX от гонок**
- Блокировать повторные клики во время in-flight запроса.
- Не вызывать `router.refresh()` на failed `Save/Cancel`.

**Step 5: Запустить тесты account**
Run: `pnpm -C apps/account test -- EditInExtensionButton`
Expected: PASS.

**Step 6: Commit**
```bash
git add apps/account/app/(app)/trails/[id]/EditInExtensionButton.tsx apps/account/app/(app)/trails/[id]/__tests__/EditInExtensionButton.test.tsx
git commit -m "Add save cancel controls with non-exit error handling"
```

### Task 6: Полная верификация и регрессии

**Files:**
- Modify (if needed): `extension/tests/basic.test.ts`

**Step 1: Добавить/обновить extension тесты**
- Проверить: `save` при backend failure возвращает ошибку и не выключает editor mode.
- Проверить: `cancel` восстанавливает snapshot и выключает editor mode.

**Step 2: Прогнать extension тесты**
Run: `pnpm -C extension test`
Expected: PASS.

**Step 3: Прогнать типизацию и сборку изменённых пакетов**
Run: `pnpm -C apps/account typecheck`
Expected: PASS.

Run: `pnpm -C extension typecheck:ui`
Expected: PASS.

Run: `pnpm -C extension build`
Expected: PASS.

**Step 4: Прогнать точечный smoke сценарий вручную**
- Открыть страницу `/trails/[id]`.
- Войти в editing.
- Смоделировать backend fail (offline/invalid token).
- Нажать `Save` и убедиться, что UI остаётся в editing + показывает ошибку.
- Нажать `Cancel` и убедиться, что редактирование завершается корректно.

**Step 5: Commit**
```bash
git add extension/tests/basic.test.ts
git commit -m "Cover save cancel editor flow with tests"
```

