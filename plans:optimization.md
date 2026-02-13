# Обновлённый план оптимизации производительности Trail на больших деревьях (без фикс-порога нод)

## Кратко
Цель: убрать лаги при `pan/zoom/drag` на обзорном масштабе больших деревьев, не привязываясь к конкретному числу нод, и не ломая UX в `radial`.

Ключевые ограничения:
- Не использовать фикс-порог типа `2308`.
- Не делать глобальное “жёсткое скрытие” связей через `LOD_CONN_HIDE_PX` (оставляем идею `-1` как базовую).

## Решение (принятые решения)
- Адаптация качества по **контроллеру frame-time** (EWMA + hysteresis), а не по количеству нод.
- Для `radial` связи **не скрываем**, но под нагрузкой переводим в дешёвый режим рендера (упрощение геометрии/стиля).

## Шаги реализации

## 1) Ввести измеримость рендера
Файлы:
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/graph/render/GraphPixiRenderer.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/graph/GraphCanvas.tsx`

Что делаем:
- Добавляем внутренние метрики: `updateVisibleMs`, `connectionsMs`, `renderMs`, `visibleNodes`, `visibleConnections`.
- Сэмплируем кадры и считаем EWMA + p95-подобный rolling индикатор.
- Добавляем dev-only флаг/лог для проверки политики (без обязательного UI).

## 2) Контроллер качества по frame-time
Новые/изменяемые файлы:
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/graph/render/quality-policy.ts` (новый)
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/graph/GraphArea.tsx`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/graph/GraphCanvas.tsx`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/graph/render/GraphPixiRenderer.ts`

Что делаем:
- Вводим policy-режимы: `full | low | dot` для нод и `full | simplified | thin` для связей.
- Переключение режимов по frame budget (например 16–18ms) с гистерезисом, чтобы не “дребезжало”.
- Без привязки к node count: решение только по фактической нагрузке и текущему состоянию viewport.

## 3) Layout-aware стратегия связей (особенно radial)
Файл:
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/graph/render/GraphPixiRenderer.ts`

Что делаем:
- `tree/mindmap`: под тяжёлой нагрузкой можно агрессивно упрощать/ограничивать связи.
- `radial`: связи не выключаем; вместо этого:
- упрощаем кривые (дешёвый путь),
- снижаем стоимость стиля (alpha/толщина/без дорогих эффектов),
- сохраняем читаемость структуры.
- `LOD_CONN_HIDE_PX` не используем как главный рычаг деградации.

## 4) Убрать лишние полные пересчёты на каждый pan
Файлы:
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/graph/render/GraphPixiRenderer.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/graph/render/view-invalidation.ts` (новый)

Что делаем:
- Разделяем invalidate-path:
- `translate-only` без значимых изменений масштаба -> только transform + render.
- Полный `updateVisible()` только при:
- изменении scale/LOD-policy,
- выходе за границу cached culling rect,
- изменениях data/theme/selection.
- Это снимает основную CPU-нагрузку в “движении камеры”.

## 5) Упростить update-path в NodeVisual
Файл:
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/graph/render/GraphPixiRenderer.ts`

Что делаем:
- Fast-path для `dot/low`: не пересчитывать текст, favicon, badge, tags, если режим не требует.
- Минимизировать пересчёты ключей и `CanvasTextMetrics` на кадрах движения.
- Сократить количество объектов/операций в горячем пути.

## 6) Батчить сохранение layout при drag
Файлы:
- `/Users/iv/dev/trail/extension/src/shared/types/messages.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/api/tree.ts`
- `/Users/iv/dev/trail/extension/src/background/messaging/handlers/tree-handlers.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/graph/GraphCanvas.tsx`

Что делаем:
- Добавляем `SET_NODE_LAYOUT_BATCH`.
- Вместо последовательных одиночных `setNodeLayout` отправляем пачки (throttle + финальный flush на `pointerup`).
- Сохраняем текущее поведение без лишних `TREE_UPDATED` в процессе drag.

## 7) Настройка пользователя: авто + toggle
Файлы:
- `/Users/iv/dev/trail/extension/src/shared/types/settings.ts`
- `/Users/iv/dev/trail/extension/src/background/services/settings.ts`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/SettingsPopover.tsx`

Что делаем:
- Добавляем `adaptivePerformance: boolean` (default `true`).
- Toggle в Settings: пользователь может отключить авто-политику.

## Публичные интерфейсы / типы
- `Settings`: новое поле `adaptivePerformance`.
- Messaging API: новый message `SET_NODE_LAYOUT_BATCH` с массивом layout-обновлений.
- Внутренний render-contract: quality policy (`detailMode + connectionQuality`), зависящий от frame-time.

## Тесты и сценарии
- Unit:
- policy-переходы и hysteresis (`quality-policy.ts`),
- invalidate-логика (`view-invalidation.ts`),
- batch layout handler.
- Интеграционные:
- drag/reparent не ломается при batch-апдейтах.
- Performance acceptance (без фикс-числа нод):
- на “большом дереве” при обзоре всего графа `pan/zoom` визуально плавные,
- p95 кадра в целевом диапазоне (ориентир: около 16–18ms на целевом железе),
- в `radial` связи остаются видимыми под нагрузкой.

## Проверка перед завершением
- `pnpm -C /Users/iv/dev/trail/extension typecheck:ui`
- `pnpm -C /Users/iv/dev/trail/extension test`
- `pnpm -C /Users/iv/dev/trail/extension build`

## Допущения
- Оптимизация только в extension sidepanel графе.
- UX-приоритет: структурная читаемость в `radial` важнее полного отключения связей.
- KPI формулируется через frame-time и плавность, а не через конкретное количество нод.
