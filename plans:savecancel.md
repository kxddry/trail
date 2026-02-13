# План: Надёжные `Save`/`Cancel` на странице редактирования Trail

## Краткое резюме
Цель: заменить текущий поток выхода из режима редактирования (через `Done`) на явные `Save` и `Cancel`, где:
- `Save` завершает редактирование только после успешного сохранения на бэкенде.
- при ошибке `Save` пользователь остаётся в режиме редактирования и видит ошибку.
- `Cancel` отменяет изменения текущей editor-сессии (rollback к snapshot) и выходит из режима редактирования.
- при ошибке `Cancel` пользователь остаётся в режиме редактирования и видит ошибку.

## Область изменений
1. UI account-приложения:
- `/Users/iv/dev/trail/apps/account/app/(app)/trails/[id]/EditInExtensionButton.tsx`
- `/Users/iv/dev/trail/apps/account/src/lib/trail-extension.ts`

2. Протокол site ↔ extension:
- `/Users/iv/dev/trail/extension/src/shared/schemas/site-messages.ts`
- `/Users/iv/dev/trail/extension/src/content/content-script.ts`
- `/Users/iv/dev/trail/extension/src/background/messaging/handlers/site-message-handlers.ts`

3. Backend-логика extension editor mode:
- `/Users/iv/dev/trail/extension/src/background/messaging/handlers/editor-handlers.ts`
- `/Users/iv/dev/trail/extension/src/background/services/editor-sync.ts`

## Изменения публичных API / интерфейсов / типов
1. Site message protocol:
- Добавить `SAVE_EDITOR_MODE` и `CANCEL_EDITOR_MODE` в whitelist и схемы.
- ACK-ответы для обоих действий должны поддерживать `{ ok: boolean, error?: string }`.

2. Account bridge API (`trail-extension.ts`):
- Добавить `saveEditorMode(): Promise<SendResult<{ ok: boolean; error?: string }>>`.
- Добавить `cancelEditorMode(): Promise<SendResult<{ ok: boolean; error?: string }>>`.
- Сохранить обратную совместимость: старый `exitEditorMode` пометить как deprecated и не использовать в кнопке страницы трейла.

3. Extension editor API:
- В `editor-handlers.ts` разделить логику на:
  - `saveEditorMode` (flush sync + exit only on success),
  - `cancelEditorMode` (rollback snapshot + exit).
- В `editor-sync.ts` изменить `editorSyncFlush()` с `Promise<void>` на результатный контракт (например `{ ok: true } | { ok: false; error: string }`).

## Детальный план реализации
1. UI state machine в `EditInExtensionButton`:
- Состояния: `checking`, `ready`, `entering`, `editing`, `saving`, `cancelling`, `error`.
- В `editing` показывать две кнопки: `Save` и `Cancel`.
- Во время `saving/cancelling` блокировать обе кнопки.
- При успешном `Save`/`Cancel`: перейти в `ready`, вызвать `router.refresh()`.
- При неуспехе `Save`/`Cancel`: вернуться в `editing`, показать error-текст, `router.refresh()` не вызывать.

2. Протокол и мост:
- В `trail-extension.ts` добавить отправку новых message type и ожидание соответствующего ACK.
- В `content-script.ts` добавить новые типы в `KNOWN_SITE_TYPES`, forward без special-case обходов.
- В `site-message-handlers.ts` маршрутизировать:
  - `SAVE_EDITOR_MODE` → новый handler сохранения,
  - `CANCEL_EDITOR_MODE` → новый handler отмены.
- Всегда возвращать явный ACK с `ok/error`.

3. Корень проблемы (backend reliability):
- В `editor-sync.ts`:
  - `performSync`/`editorSyncFlush` должны явно сообщать успех/ошибку после ретраев.
  - Ошибка flush не должна «маскироваться».
- В `editor-handlers.ts`:
  - На `enterEditorMode` сохранить session snapshot дерева (JSON + treeId сессии).
  - `saveEditorMode`: если flush fail, не выходить из editor mode, вернуть ошибку.
  - `cancelEditorMode`: восстановить snapshot, затем завершить editor mode.
  - `broadcastEditorExitToSite` и `notifyTreeUpdate(..., 'editor-exit')` отправлять только при успешном завершении соответствующего действия.

## Тесты и сценарии
1. Unit/Component tests (account):
- Новый файл: `/Users/iv/dev/trail/apps/account/app/(app)/trails/[id]/__tests__/EditInExtensionButton.test.tsx`.
- Кейсы:
  - рендер `Save` и `Cancel` в `editing`;
  - `Save` success: exit + refresh;
  - `Save` fail: остаётся `editing`, ошибка видна;
  - `Cancel` success: exit + refresh;
  - `Cancel` fail: остаётся `editing`, ошибка видна;
  - disabled кнопки при in-flight.

2. Extension tests:
- Обновить `/Users/iv/dev/trail/extension/tests/basic.test.ts`.
- Кейсы:
  - `saveEditorMode` возвращает ошибку при неуспешном PATCH/flush и не выключает editor mode;
  - `cancelEditorMode` восстанавливает snapshot и выключает editor mode;
  - ACK payload содержит `error` при fail.

3. Проверки командами:
- `pnpm -C /Users/iv/dev/trail/apps/account test -- EditInExtensionButton`
- `pnpm -C /Users/iv/dev/trail/apps/account typecheck`
- `pnpm -C /Users/iv/dev/trail/extension test`
- `pnpm -C /Users/iv/dev/trail/extension typecheck:ui`
- `pnpm -C /Users/iv/dev/trail/extension build`

## Критерии приёмки
- На странице трейла в режиме редактирования видны `Save` и `Cancel`.
- Нажатие `Save` не закрывает редактирование при backend-ошибке.
- При backend-ошибке пользователь видит error и может повторить действие.
- `Cancel` откатывает изменения текущей editor-сессии.
- Нет silent-success при неуспешном сохранении.

## Явные допущения и выбранные дефолты
- Лейблы кнопок: английские `Save` и `Cancel` (как вы уточнили).
- `Cancel` означает discard изменений текущей editor-сессии через rollback к snapshot на входе.
- Текущая debounce/auto-sync логика остаётся, но финальное решение о выходе из режима редактирования принимается только по явному результату `Save`/`Cancel`.
- Локализацию и редизайн остальных экранов в этот scope не включаем.
