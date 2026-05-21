# React Flow Antipatterns Audit — 2026-05-20

**Scope:** `extension/src/features/graph/**` — единственный потребитель `@xyflow/react ^12.10.2` во всём монорепо (подтверждено grep'ом). CSS, layout, transforms, motion — всё в одном пакете, нет рассеяных консьюмеров.

**TL;DR.** Слой React Flow в этом коде **очень аккуратно оптимизирован**: модульные `nodeTypes` / `defaultEdgeOptions`, контролируемая селекция, изолированный `useStore` subscriber для Background, LOD через CSS-атрибут (а не per-node subscription), `useEffectEvent` для wheel-handler, identity-сохраняющие мемо-цепочки. Большинство «канонических» антипаттернов (новые `nodeTypes` на каждый ререндер, `nodes` без мемоизации, вложенные `<ReactFlowProvider>`, `useReactFlow` вне провайдера, тяжёлые объекты в `node.data`) — **отсутствуют**.

Найдено **5 настоящих** антипаттернов разной критичности и ~4 «спорных» паттерна, которые работают, но создают долг.

---

## Критические

### 1. `useMemo` мутирует рефы (нарушение чистоты)
**Файл:** `extension/src/features/graph/motion/useNodeLifecycle.ts:66-200`

В теле `useMemo` (строки 66-200):
- читается `performance.now()` (строка 78, `// eslint-disable-next-line react-hooks/purity`),
- мутируются **4 рефа**: `annotationsRef.current` (89, 108, 127, 134, 143, 167), `lastSnapshotRef.current` (89, 155, 158), `recentlyDepartedRef.current` (118, 164), `prevIdsRef.current` (71, 90, 198).

`useMemo` контрактуально **чистая функция от deps**. React 18 в Strict Mode сегодня не double-invoke'ит `useMemo` (только `useState`-инициализаторы и эффекты), поэтому код работает. Но:
- React Compiler **не пропустит** такую функцию через свой optimizer — она будет помечена как side-effectful и оптимизация выпадет.
- React 19+/Strict Mode может ужесточить инвариант (RFC обсуждался). Тогда мутации произойдут дважды и `prevIdsRef` зашьётся на «текущем» вместо «предыдущего» → диф сломается, exit-/enter-анимации потеряются.
- Concurrent rendering (Suspense, useTransition): рендер может быть **выброшен**, но мутации в рефах останутся. Тогда «следующий» рендер сравнит prevIds с уже-применённым state'ом → пропуск событий.

Это намеренное решение (eslint-disable), но архитектурно — антипаттерн. Корректный путь: `useReducer` + `useEffect` для диффа, либо `useSyncExternalStore` (как уже сделано в `motion/store.ts:50`).

### 2. Запись в ref во время рендера
**Файл:** `extension/src/features/graph/components/TrailGraph.tsx:564-565`

```tsx
const displayNodesRef = useRef(displayNodes);
displayNodesRef.current = displayNodes;
```

Присваивание в `.current` происходит **в теле рендера** (не в effect). React-доки разрешают это как escape-hatch, но:
- При concurrent-rendering рендер может быть **выброшен** — ref всё равно зашьётся на «выброшенном» значении.
- Используется только в одном rAF-колбэке внутри эффекта `collapseAction` (518) — там можно прочитать `displayNodes` прямо через замыкание эффекта, если перенести объявление эффекта ниже.

Антипаттерн на грани с устоявшейся практикой. Под React 19 безопаснее заменить на `useEffect` (для синхронизации) + читать `latest`-style.

---

## Заметные

### 3. Inline-литерал `proOptions={{ hideAttribution: true }}`
**Файл:** `TrailGraph.tsx:850`

Единственный inline object literal в props у `<ReactFlow>` — новый объект на каждый ререндер `TrailGraphInner`. Внутри RF (`packages/system/src/store/index.ts`) `proOptions` не входит в shallow-compare ререндера, поэтому **визуально безболезненно**, но это нарушает собственный паттерн файла: `nodeTypes` (38), `defaultEdgeOptions` (42), `MULTI_SELECT_KEYS` (40) — все вынесены в модуль. `proOptions` забыт.

**Фикс:** добавить рядом с строкой 49:
```ts
const proOptions = { hideAttribution: true } as const;
```

### 4. Identity-churn на уровне layout-output
**Файлы:** `layout.ts` (`applyNodeMetadata`), `transforms.ts:49-117` (`treeToNodes`), `transforms.ts:75-91` (`data` объект)

`applyNodeMetadata` пересоздаёт **весь массив узлов + объекты `data`** при любом изменении `metadata` (`currentNodeId`, `openNodeIds`, `nodeTabCounts`, `badgeExpandedIds`, `inlineRenameTargetId`). На дереве в 5к узлов это ~5000 аллокаций объектов на каждый focus-change таба.

Это **не катастрофа**, потому что:
- `TrailNode.tsx:252-276` — мемо-компаратор по полям `data` — реальный React-ререндер не происходит.
- RF v12 внутри диффит контент, не identity.
- `displayNodes` (`TrailGraph.tsx:305-350`) частично восстанавливает identity: возвращает **тот же** объект `n`, если `selected/spotlight/dragRole/draggable` совпали (строки 325-332).

Но: пик GC + лишняя работа в RF-store при больших деревьях. Канонический фикс — **per-node memoization** в `applyNodeMetadata`: возвращать ровно тот же node-объект, если все его merged-поля совпали с предыдущим вызовом.

### 5. `onNodesChange` слушает только `position+dragging`
**Файл:** `TrailGraph.tsx:212-221`

```ts
const handleNodesChange = useCallback((changes: NodeChange[]) => {
  for (const change of changes) {
    if (change.type !== "position" || !change.dragging || !change.position) continue;
    ...
  }
}, []);
```

Игнорируются `select`, `add`, `remove`, `dimensions`. Это работает потому, что **режим полностью контролируемый**: selection живёт в parent state, позиции — в layout. Но контракт RF v12 ожидает, что controlled-консьюмер либо применит `applyNodeChanges`, либо обоснованно проигнорирует. Здесь — второе, но **без комментария, объясняющего "почему игнорируем"** (в отличие от других мест файла, где комменты подробные).

Риск:
- RF v13 (или внутреннее изменение в minor-апдейте `^12.x.x`) может добавить тип change'а, который ОБЯЗАН быть обработан для корректности (например, `dimensions` для измерения handles → пересчёт edge `d`).
- Сейчас `measured.width/height` читается в `handleNodeDrag` (253-254) с фолбэком на константы — фолбэк сработает, но silently.

Не критично, но добавить комментарий — must.

---

## Спорные / minor

### 6. `displayNodes.find` × 2 за рендер
**Файл:** `TrailGraph.tsx:376, 387`

Два O(N) линейных скана `displayNodes` ради позиций `currentNodeId` и `fallbackFocusId`. На 5к узлов — 10к сравнений за каждое изменение `displayNodes` (≈ каждый tick metadata). Можно построить `Map<NodeId, Position>` один раз в layout-слое (там в `geometry.positions` он уже есть) и читать оттуда.

### 7. `smoothCenter` идентичность зависит от viewport-размера
**Файл:** `motion/useCameraControls.ts:85-135`

`smoothCenter` пересоздаётся при изменении `viewportWidth`/`viewportHeight` (deps на строке 134). В `TrailGraph.tsx:400-403` это смягчено через `useLatest`, но прямые консьюмеры — `handleCenterCurrent` (570-575) — зависят от `smoothCenter` напрямую и получают новую identity на каждом resize окна. Не катастрофа, но `GraphControls` (852) дёргается лишним ререндером.

### 8. `getIntersectingNodes` каждый drag-frame
**Файл:** `TrailGraph.tsx:244`

`getIntersectingNodes(node, true)` на каждый pointermove во время drag. Внутри xyflow (`packages/react/src/store/useStore.ts`) это O(N) по nodeLookup. На 5к узлов × 120Hz drag ≈ 600k сравнений/сек. С учётом `onlyRenderVisibleElements` (836) реально проверяются только видимые узлы внутри store'а — но lookup всё ещё проходит весь массив. Не блокер, но горячая точка.

### 9. `useUpdateNodeInternals` в каждом узле
**Файл:** `TrailNode.tsx:86-92`

`useUpdateNodeInternals` вызывается на пер-нодовый effect. На layout-switch (tree↔mindmap) handles меняются у многих узлов одновременно → N independent зовов в один frame. Защита `firstHandlesKeyRef` (87, 89) **исключает mount-cascade** (это и было задокументировано в TrailGraph 822-830), но не helping при массовом layout-switch'е. Можно скоординировать через parent: один `updateNodeInternals(allChangedIds[])` вызов вместо N. Не блокер.

---

## ✅ Что сделано **правильно** (для контекста — много)

| Pattern | Где | Почему хорошо |
|---|---|---|
| Module-level `nodeTypes`, `defaultEdgeOptions`, `MULTI_SELECT_KEYS` | `TrailGraph.tsx:38,40,42` | Не пересоздаются → RF не пересчитывает |
| `<ReactFlowProvider>` один раз на корне | `TrailGraph.tsx:866-871` | Нет дубликатов / разрывов контекста |
| Изолированный `useStore` в leaf-компоненте | `GraphBackground` 57-61, `LodController` 18-25 | Zoom-threshold flip не будит `TrailGraphInner` |
| LOD через CSS-атрибут на parent | `LodController.tsx:23`, `pane.css:156-171` | 0 React-subscription'ов вместо ~1808 |
| Identity-preserving мемо-цепочка | `displayNodes` (305-350), `lifecycleNodes` (353), `finalNodes` (361-365) | Только реально изменённые узлы получают новый ref |
| `handleNodesChange` no-op для unchanged positions | 217-219 | Не триггерит setState на каждый pointermove |
| `useEffectEvent` для wheel-handler | `useCmdWheelZoom.ts:39-62` | Стабильная identity → подписка mount'ится один раз |
| Deferred-center при viewport=0 | `useCameraControls.ts:65-69, 144-155` | Решает initial-mount race |
| `useLatest` для read-без-refire | `TrailGraph.tsx:400, 588` | Эффекты не рефайрят на churn callback'ов |
| Memo comparator на `TrailNode` | `TrailNode.tsx:252-276` | RF v12 не использует React.memo автоматически — это критично |
| `selectShowBackground` / `selectLod` — boolean/enum | `lod.ts:32, 41` | Object.is default equality корректна для примитивов |
| CSS containment без `paint` | `pane.css:38-40` | Сохраняет hover glow / spotlight за пределами node |
| Edge `pointer-events: none` | `pane.css:19-23` | Маркизный drag проходит через edges |
| `panOnScroll` + `graph--panning` pointer-events kill | `TrailGraph.tsx:785, hover.css:47-49` | N×hover cascade выключен на время pan |
| `dragging` class clears relayout transition | `relayout.css:36-38` | Драг tight-to-cursor |
| `deleteKeyCode={null}` | `TrailGraph.tsx:814` | RF не глотает Backspace до tinykeys |

---

## Приоритезированный фикс-лист (если решите править)

1. **#3 (`proOptions` literal)** — 1 строка, нулевой риск. Сделать первым.
2. **#5 (комментарий к `handleNodesChange`)** — задокументировать "почему игнорируем не-position changes", добавить TODO на ревизию при RF v13.
3. **#1 (`useNodeLifecycle` purity)** — переписать на `useReducer` + `useEffect`. **Сложно**: текущая логика "пометить exit'ы + render их как ghosts в том же frame, не дожидаясь useEffect" требует переосмысления. Не делать без аппетита.
4. **#4 (identity churn в layout)** — per-node memoization в `applyNodeMetadata`. Средний риск (нужно сохранить кэш с предыдущего вызова). Выгода — на тяжёлых деревьях.
5. **#2, #6, #7, #8, #9** — minor, делать только если профиль покажет проблему.

---

## Цитаты — индекс file:line

| Антипаттерн | Точка |
|---|---|
| useMemo мутирует refs | `motion/useNodeLifecycle.ts:66-200` |
| eslint-disable purity | `motion/useNodeLifecycle.ts:77` |
| Ref-write во время рендера | `components/TrailGraph.tsx:564-565` |
| `proOptions` inline literal | `components/TrailGraph.tsx:850` |
| Identity-churn `treeToNodes` | `transforms.ts:49-117` |
| Identity-churn `data` объект | `transforms.ts:75-91` |
| Identity-churn `applyNodeMetadata` | `layout.ts:158-201` |
| `onNodesChange` без комментария | `components/TrailGraph.tsx:212-221` |
| `displayNodes.find` × 2 | `components/TrailGraph.tsx:376, 387` |
| `smoothCenter` identity-churn | `motion/useCameraControls.ts:134` |
| `getIntersectingNodes` per-frame | `components/TrailGraph.tsx:244` |
| Per-node `useUpdateNodeInternals` | `components/TrailNode.tsx:86-92` |
