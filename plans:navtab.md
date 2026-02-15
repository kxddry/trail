# План: отключить nav/tab в `editor mode` и оставить выделение нод

## Кратко
Я использую `writing-plans` skill для подготовки implementation plan.  
Цель: в `editor mode` полностью убрать действия с ссылками/вкладками, при этом оставить режим `select` и выделение рамкой; одиночный клик по ноде должен делать `replace selection` (выделять ноду), а не открывать вкладку.

## Scope
- In scope:
  - В `editor mode` отключить открытие/фокус/создание/закрытие/mute вкладок из UI и background-хендлеров.
  - Клик по ноде в графе переводится в выделение (single-node selection).
  - Сохранить рамочное выделение (box selection) и drag/reparent.
  - Скрыть `Pinned` и `Tag filter` в `editor mode`.
- Out of scope:
  - Переписывание протокола site↔extension (`NODE_SELECTED` и т.п.).
  - Изменение поведения вне `editor mode`.

## Изменения по шагам

### 1. Зафиксировать guard на уровне background (чтобы UI-обходы не ломали ожидания)
**Файлы:**
- `/Users/iv/dev/trail/extension/src/background/messaging/handlers/navigation-handlers.ts`
- `/Users/iv/dev/trail/extension/src/background/messaging/handlers/tab-handlers.ts`
- `/Users/iv/dev/trail/extension/src/background/messaging/handlers/editor-handlers.ts` (только импорт `getEditorState`, если нужно)

**Что сделать:**
- Добавить проверку `getEditorState().active` в `navigation-handlers`.
- В `editor mode`:
  - `MSG.NAVIGATE_TO`: не трогать вкладки; только `tree.setCurrentById(...)` + `treeStorage.cacheTree(...)` + `notifyTreeUpdate(..., 'set-current', ...)`.
  - `MSG.SET_CURRENT`: то же поведение (без tab focus/create).
  - `MSG.PREVIEW_NODE`: no-op `ok()`.
  - `MSG.OPEN_IN_NEW_TAB`: no-op `ok()` (без создания вкладки).
- В `tab-handlers` в `editor mode`:
  - `MSG.TOGGLE_MUTE`, `MSG.CLOSE_TAB`, `MSG.BULK_CLOSE_TABS`: no-op `ok()` (без side effects).

**Почему так:**
- Это root-level защита: даже если где-то останется вызов навигации, вкладки не будут трогаться в `editor mode`.

---

### 2. Перевести клик по ноде в выделение, не в навигацию
**Файл:**
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/graph/GraphCanvas.tsx`

**Что сделать:**
- Обновить `handleNodeClick`:
  - Если `editorActive && tool === 'select'`: `onSelectedNodeIdsChange(new Set([node.id]))`.
  - Не вызывать `navigateTo(node)` в `editor mode`.
- Поведение `pickTarget` оставить как есть.
- `hand` не использовать как обходной путь (режим `select` остаётся основным).
- Рамочное выделение (`selectionBox`, `queryNodesInWorldRect`) не трогать.

**Ожидаемый результат:**
- Клик по ноде в `editor mode` выделяет ноду.
- Никакого открытия/фокуса вкладок.

---

### 3. Скрыть nav/tab UI в `editor mode`
**Файлы:**
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/FloatingControls.tsx`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/ContextMenus.tsx`

**Что сделать:**
- В `FloatingControls`:
  - Читать `editorMode.active` из store.
  - Не рендерить `PinnedDropdown` и `TagFilterDropdown` при `editorMode.active === true`.
- В `ContextMenus`:
  - Node menu: скрыть `Open in this tab`, `Open in new tab`, блок “open tabs”, `Close tab/Close all tabs` в `editor mode`.
  - Bulk menu: скрыть `Close selected tabs` в `editor mode`.
- Остальные editor-операции (tags/pin/delete/reparent/collapse/expand) оставить доступными.

---

### 4. Отключить nav/tab shortcuts в `editor mode`
**Файл:**
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/hooks/useShortcuts.ts`

**Что сделать:**
- В `editor mode` блокировать:
  - `Enter` (open current selection),
  - `Cmd/Ctrl+Enter` (open in new tab),
  - `Shift+P` и `Shift+F` (если соответствующие dropdown’ы скрыты).
- Undo/redo, selection, delete, layout-related shortcuts оставить.

---

### 5. Документация поведения editor mode
**Файл:**
- `/Users/iv/dev/trail/docs/extension/graph.md`

**Что обновить:**
- Добавить явное правило: в `editor mode` клик по ноде = selection, nav/tab actions disabled.
- Отдельно отметить, что box selection сохранён.

## Важные изменения в интерфейсах/контрактах
- Новых message types не добавляем.
- Меняем семантику существующих сообщений **только** при `editorMode.active === true`:
  - `MSG.NAVIGATE_TO`, `MSG.SET_CURRENT`, `MSG.PREVIEW_NODE`, `MSG.OPEN_IN_NEW_TAB`,
  - `MSG.TOGGLE_MUTE`, `MSG.CLOSE_TAB`, `MSG.BULK_CLOSE_TABS`.
- Вне `editor mode` поведение остаётся прежним.

## Тесты и сценарии проверки

### Автоматические
- `pnpm -C /Users/iv/dev/trail/extension typecheck:ui`
- `pnpm -C /Users/iv/dev/trail/extension test`
- `pnpm -C /Users/iv/dev/trail/extension build`

### Ручные (обязательные)
1. В обычном режиме:
   - Клик по ноде по-прежнему открывает/фокусит вкладку.
   - Context menu tab actions работают.
2. В `editor mode`:
   - Клик по ноде выделяет её (single selection), вкладки не открываются.
   - Box selection работает как раньше (replace/add/remove).
   - `Enter` и `Cmd/Ctrl+Enter` не открывают вкладки.
   - `Pinned` и `Tag filter` не видны.
   - В context menu нет tab/nav пунктов.
   - Попытка tab action через background message не приводит к side effects.
3. Регрессии editor операций:
   - drag-reparent, duplicate target picking, delete, undo/redo работают.

## Assumptions и принятые defaults
- `editor mode` определяется только флагом `state.editorMode.active`.
- Одиночный клик в editor mode: `replace selection` (по вашему выбору).
- `hand` не является workaround; основной режим остаётся `select`.
- В editor mode убираем весь `nav/tab` функционал (по вашему выбору), включая UI и background safety guard.
- `NODE_SELECTED` bridge для account site не трогаем в этой задаче.
