# Tree-tracking overhaul — полный журнал изменений

52 атомарных коммита, организованных по фазам (0-10). Каждая запись:
**Было → Стало → Зачем → Как**.

---

## Phase 0 — Cleanup, schema migration, lock export

### 1. `chore: vendor skills scaffolding for alternative AI tool configs`
**Commit:** `4d0eee72`
**Файлы:** `.agents/`, `.augment/`, `.codebuddy/`, `.continue/`, `.junie/`, `.kiro/` (162 файла)

- **Было:** Несколько каталогов со скилл-символическими ссылками были untracked, засоряли `git status`, мешали видеть реальные изменения для refactor'а.
- **Стало:** Все scaffolding-каталоги закоммичены одним `chore`-коммитом.
- **Зачем:** Изолировать vendor-шум от refactor'а — чистый `git bisect` по следующим коммитам без «шума из скиллов».
- **Как:** `git add` только этих путей, один commit с сообщением `chore: vendor skills scaffolding`.

### 2. `chore: pre-refactor WIP snapshot of sidepanel/settings/UI work`
**Commit:** `7d36e385`
**Файлы:** ~40 UI-файлов (sidepanel, settings pages, ui/hooks, features/graph/tree-layout, observability и т.д.)

- **Было:** Работа в процессе — модифицированные sidepanel-компоненты, новые hooks в `src/ui/hooks/`, error-boundary, feedback-dialog, shortcut component, marketing-urls config. Не мои изменения, но было в рабочем дереве.
- **Стало:** Всё это — одним коммитом `chore: pre-refactor WIP snapshot`.
- **Зачем:** Не мешать с tree-tracking работой; сохранить работу пользователя нетронутой; чистое рабочее дерево перед моими правками.
- **Как:** `git add` перечисленных путей, commit с подробным сообщением о содержимом.

### 3. `docs: add tree-tracking forensic bug audit (97 bugs)`
**Commit:** `4ddd2f00`
**Файлы:** `tasks/tree-tracking-bugs.md`, `tasks/tree-tracking-bugs.pdf`, `tasks/generate-bug-report-pdf.py`

- **Было:** Результаты аудита существовали только в head контекста и в плане. Ни один лок. артефакт не документировал 97 багов.
- **Стало:** Канонический список багов в markdown + PDF, плюс Python-генератор (легче всего читать) — в репозитории.
- **Зачем:** Чтобы каждый коммит мог ссылаться на конкретный `#NN` без потери контекста.
- **Как:** Коммит всех трёх файлов с описанием 10 категорий и распределения severity (15 P0, 24 P1, 28 P2, 30 P3).

### 4. `refactor(storage): export withTreeLock + treeMutex, add generation counter`
**Commit:** `05ef88ab`
**Файл:** `src/background/services/tree-storage.ts`

- **Было:** `const treeMutex` и `function withTreeLock` существовали локально в модуле, но **не экспортировались**. Они защищали только внутренние persistence-операции (flushSaveNow, setActiveTree). Обработчики навигации/табов мутировали дерево без лока. Порог warn `waited > 5000ms` слишком высок для UX.
- **Стало:** `treeMutex` и `withTreeLock` экспортированы. Добавлен `private generation = 0` + методы `getGeneration()` и `bumpGeneration()`. `cacheTree()` теперь вызывает `bumpGeneration()`. Warn порог снижен до 1500ms.
- **Зачем:** Фундамент для Phase 1+: любой хендлер может теперь `withTreeLock(...)` и получать атомарность относительно persistence. Generation counter — для Phase 7 generation-guard в sidepanel'е (отбрасывание устаревших snapshot'ов).
- **Как:** `export` ключевое слово + новые private-поля и методы. Поведение неизменно — ни одна существующая вызов-площадка не задета.

### 5. `feat(service-worker): flush tree on suspend + onInstalled migration trigger`
**Commit:** `2a60a2ac`
**Файл:** `src/background/service-worker.ts`

- **Было:** MV3 service worker'ы агрессивно эвиктятся. Debounced 1500ms save (`cacheTree` → `setTimeout(..., 1500)` → `flushSaveNow`) умирал вместе с воркером, теряя до 1.5 секунд последних навигаций. Никакого `chrome.runtime.onSuspend` хука не было. Миграции не перезапускались на `onInstalled reason=update`.
- **Стало:** Добавлены два listener'а: `onSuspend` → `treeStorage.flushSaveNow()` и `onInstalled(reason='update')` → `runMigrations()`.
- **Зачем:** Закрыть P0 баг #13 (silent data loss при эвикте SW) и P2 #37 (миграции не триггерятся на upgrade).
- **Как:** Два `addListener` в service-worker.ts. `onSuspend` — best-effort (Chrome может убить SW до resolve), но закрывает common-case window.

### 6. `refactor(migrations): while-loop runner + singleflight guard`
**Commit:** `edb3743b`
**Файл:** `src/background/services/migrations.ts`

- **Было:** Single-pass `for` над `MIGRATIONS` с фильтром `m.from !== current`. Out-of-order append (`{from:2,to:3}` перед `{from:1,to:2}`) незаметно пропускал вторую миграцию. При параллельных вызовах — дубль. Ошибка — `return`, swallow в `captureError`.
- **Стало:** `while (current < CURRENT_SCHEMA_VERSION)` с index-lookup `migrationFrom(from)`. Singleflight через кешированный `runningMigrations: Promise<void>`. При gap — explicit throw (а не silent skip). Ошибка — reset `runningMigrations = null` + re-throw.
- **Зачем:** Phase 1 собирается поднять `CURRENT_SCHEMA_VERSION = 2` (для NodeId migration). Нужна надёжная инфраструктура миграций — особенно singleflight, чтобы `onInstalled.onWake` + параллельный `getOrCreateTree` не гнали миграцию дважды.
- **Как:** Переписан `runMigrations()` как IIFE, кэширующая promise. `migrationFrom` — простой `Array.find` по `from`.

### 7. `feat(storage): schema v2 — stringify all persisted node IDs`
**Commit:** `1b19e98f`
**Файл:** `src/background/services/migrations.ts`

- **Было:** Все persisted tree blob'ы содержали числовые `id: number` в JSON. `NodeId` был `Brand<number, "NodeId">`. Готовился переход на string (uuidv7), но без миграции данные смешались бы в runtime `Map<NodeId, Node>` — string и number key'и — это разные записи в Map.
- **Стало:** Миграция v1→v2: проходит активное дерево + все не-stub архивные blob'ы, конвертирует каждый `id` и `currentNodeId` через `String(id)`. Idempotent (уже-string id не трогает). Post-verify assertion: перечитывает активное дерево и throws если находит non-string `id`. `CURRENT_SCHEMA_VERSION = 2`.
- **Зачем:** Без этого Phase 1's NodeId type change тихо сломал бы все persisted tree'и — `findNodeById("uuid")` против `nodeMap` с ключами-числами вернул бы undefined; rollback был бы невозможен.
- **Как:** `stringifyIdsInNodeJSON` walker + `stringifyIdsInTreeJSON`. Архивы идут через `treeStorage.saveArchiveTree/getArchiveTree` (dynamic import избегает циклической зависимости). Post-verify walk бросает, если что-то пропущено.

---

## Phase 1 — Foundation: identity, locks, blocklist

### 8. `refactor(types): NodeId = Brand<string, "NodeId"> — mint via uuidv7`
**Commit:** `6fd720e8`
**Файлы:** `src/shared/types/ids.ts`, `src/background/state/tree-node.ts`, `src/background/state/nav-tree.ts`, `src/shared/types/compact-tree.ts`, `src/shared/lib/compact-mapper.ts`, `src/apps/sidepanel/ui/onboarding/japan-demo-tree.ts`

- **Было:** `NodeId = Brand<number, "NodeId">`. `let nodeIdCounter = 0 as NodeId` — module-global counter. На restart SW counter сбрасывался; во время async hydration коллизия: новый `createChild` получал `id = 6`, но `id = 6` мог ещё прийти при десериализации — `nodeMap.set(6, ...)` тихо перезаписывал.
- **Стало:** `NodeId = Brand<string, "NodeId">`. `nodeIdCounter` удалён. `nextNodeId() = uuidv7()`. `findNodesByQuery` tie-breaker заменён с `Number(a) - Number(b)` (возвращал NaN на uuid-строках) на `String.localeCompare`. Compact-tree tuple id widened to `string | number` для обратной совместимости; `coerceNodeId` нормализует при декоде. Демо-tree использует `d-N` ids.
- **Зачем:** Устраняет #15 (nodeIdCounter race на SW restart) и весь класс id-collision багов. uuidv7 time-sortable и глобально уникален.
- **Как:** Type-level brand change; TypeScript прогнал каскад — все сайты, сравнивавшие NodeId как число, подсветились. Точечные правки: `compact-mapper.ts` coerces через helper, `japan-demo-tree.ts` использует namespace `d-`, `nav-tree.ts:305` — localeCompare.

### 9. `refactor(nav-tree): setCurrentById returns boolean + log on miss in hydrator`
**Commit:** `4daa9599`
**Файлы:** `src/background/state/nav-tree.ts`, `src/shared/lib/mapper.ts`

- **Было:** `setCurrentById(nodeId: NodeId): void`. Тихий no-op, если id не существует. 22 call-site не проверяли результат. Persisted `currentNodeId`, ссылающийся на удалённый или слитый узел, оставлял `tree.current` неопределённым, mapper падал на root fallback без логирования.
- **Стало:** `setCurrentById(nodeId: NodeId): boolean`. Mapper'ы hydrator проверяет результат и warns, если persisted id не резолвится. Другие call-site'ы опционально используют boolean.
- **Зачем:** #42 (silent no-op). Callers'ы теперь могут детектировать miss. Mapper явно логирует divergence — помогает observability.
- **Как:** Сменил return type; добавил warn в mapper.ts:49 перед fallback на root.

### 10. `refactor(nav-handler): narrow withTreeLock around mutation block`
**Commit:** `745db6cf`
**Файл:** `src/background/navigation/navigation-handler.ts`

- **Было:** `handleNavigation` делал `await browser.tabs.get`, читал tabManager, `await treeStorage.getOrCreateTree`, мутировал tree, `cacheTree`, `await notifyTreeUpdate` — всё **без лока**. Две параллельных навигации в разных табах могли interleave `setCurrentById + navigate` и навсегда соединить узлы с неправильным родителем (#23).
- **Стало:** Чёткий pattern: (1) Chrome API reads снаружи лока; (2) build data patch снаружи лока; (3) `await withTreeLock(async () => { mutate + cacheTree })`; (4) `await notifyTreeUpdate` снаружи лока. `tabManager.nodeByTab` перечитывается внутри лока (tab мог быть unregistered между `tabs.get` и мутацией).
- **Зачем:** #23, #24, #26. Атомарность каждой навигации; sidepanel listener не может залипнуть и заблокировать следующий webnav event.
- **Как:** Переписал полностью — ввёл `NavigationBroadcast` discriminated union как возвращаемое значение из `withTreeLock`-блока. Сам mutation tree сохранил ту же логику (existing-node / URL-key match / new), но теперь она fenced.

### 11. `refactor(lifecycle, sync-open-tabs): withTreeLock around mutation blocks`
**Commit:** `5d05823a`
**Файлы:** `src/background/tabs/lifecycle.ts`, `src/background/tabs/sync-open-tabs.ts`

- **Было:** `onTabCreated`, `onTabRemoved`, `onTabActivated`, `onTabUpdated`, `onWindowFocusChanged`, `syncOpenTabs` — все мутировали без лока. `syncOpenTabs` особенно плохо: `tabManager.reset()` сразу, потом `await browser.tabs.query({})` — 50-200ms окно при каждом SW wake, в котором webnav events регистрировали табы на пустой tabManager, потом их wipe'ало.
- **Стало:** Всё тот же pattern — lock только вокруг мутационного блока. `syncOpenTabs` теперь полностью атомарен: reset + repopulation — один `withTreeLock`. `shouldSuppressActivate` check перенесён в топ `onTabActivated` (был внизу — мутации уже произошли).
- **Зачем:** #24 (syncOpenTabs race window), #27 (suppression too late). Также вносит вклад в #23, #26 и общую надёжность.
- **Как:** Каждый handler получил NavigationBroadcast-подобную структуру return'а. `shouldSuppressActivate` поднят на уровень guard-clauses.

### 12. `refactor(storage): ensureMigrated singleflight + post-success flag`
**Commit:** `3c6f0d09`
**Файл:** `src/background/services/tree-storage.ts`

- **Было:** `ensureMigrated` делал `if (this.migrated) return; this.migrated = true;` **до** await'ов. Второй параллельный caller видел `migrated=true` и возвращался, потом читал сам — возвращал legacy-shape archives. Первый caller потом делал `writeBulkDirect` — данные оказывались в intermediate-состоянии на какое-то время.
- **Стало:** Singleflight через `this.migrationPromise`. Параллельные callers await'ят тот же promise. `this.migrated = true` переносится **после** success. При throw — `migrationPromise = null` + re-throw (retry на следующем вызове).
- **Зачем:** #37. Особенно bites на slow первом boot после upgrade.
- **Как:** IIFE pattern — `this.migrationPromise = (async () => { ... })().catch(...)`. Каждый branch (success, empty, malformed) либо ставит `this.migrated = true` и return, либо throws.

### 13. `feat(blocklist): default-deny until settings ready + navigation await`
**Commit:** `b26ab4b1`
**Файлы:** `src/background/services/settings.ts`, `src/background/utils/url-utils.ts`, `src/background/navigation/navigation-handler.ts`

- **Было:** `cachedBlocklist = () => false` по умолчанию (track всё). `settingsManager.init()` — fire-and-forget; `loadSettings → import → setUrlBlocklist` — chained async cascade. При каждом SW wake окно ~50-200мс, когда blocklist фактически выключен — блокированные URL'ы отслеживались (приватность #78).
- **Стало:** `cachedBlocklist = () => true` по умолчанию (deny). `settingsManager.ready: Promise<void>` resolves после первой успешной загрузки. `settingsManager.isReady()` — синхронная проверка. `navigation-handler` в начале делает `if (!settingsManager.isReady()) await settingsManager.ready;` — не блокирует event-loop (Chrome queue'ит webnav events, каждый yield'ит до ready).
- **Зачем:** #78 — P0 privacy leak. Critic'ом flagged как M4 regression risk (drop нав каждого wake), mitigated через `await settingsManager.ready` — навигации просто сериализуются за первой загрузкой settings (~100ms), ничего не теряется.
- **Как:** Constructor создаёт Promise с сохранённой resolve. `init()` резолвит после успеха. `setUrlBlocklist` теперь поднимает `blocklistReady = true`. `isBlocklistReady()` — публичный getter для diagnostics.

### 14. `test(transport): update EXTENSION_MESSAGE list for content-bridge-error`
**Commit:** `9848cc1a`
**Файл:** `tests/transport-contracts.test.ts`

- **Было:** Pre-existing test fail — `EXTENSION_MESSAGE` константа получила новый `event/content-bridge-error`, но expected-массив в тесте не обновили. `pnpm test` падал до моих правок.
- **Стало:** Expected-массив содержит новый идентификатор.
- **Зачем:** Чтобы `pnpm test` был зелёным; обязательное условие для любой дальнейшей проверки в этой refactor'е.
- **Как:** Одна строка в expected-массиве.

---

## Phase 2 — Per-tab parent inference

### 15. `feat(tabs): lastNodeByTab tracker persisted to chrome.storage.session`
**Commit:** `5186fda8`
**Файлы:** `src/background/state/tab-manager.ts`, `src/background/service-worker.ts`

- **Было:** `TabManager` не хранил «последний узел для таба». Opener-тaбу нечего было передать как parent, если он уже был re-registered. Без persistence через `storage.session` каждый SW wake терял эту инфу, мы опять падали на `tree.current` и фиксили бы тот же баг только в первую секунду после wake.
- **Стало:** `private lastNodeByTab: Map<TabId, NodeId>`, persisted в `chrome.storage.session` (доступна через существующее `"storage"` разрешение, без изменений manifest'а). Новые методы `hydrate()`, `lastNodeByTabId()`, `setTreeAccessor()`, `onNodesDeleted()`. `register/touch` пишут в карту; `unregister/reset` очищают. Service-worker'а hydrate'ит до syncOpenTabs.
- **Зачем:** Critic C3 — без persistence в `storage.session` opener-based parent inference регрессирует на каждом SW wake. Фундамент для следующего коммита.
- **Как:** `storage.defineItem<Record<string, string>>("session:...")`. `persistLastNodeByTab()` — fire-and-forget write после каждого `register/unregister`. `hydrate()` парсит Record<TabId-string, NodeId-string> в Map.

### 16. `feat(nav-tree): navigateUnder(parentId, data, options)`
**Commit:** `9d031a1f`
**Файл:** `src/background/state/nav-tree.ts`

- **Было:** `tree.navigate(data)` использовал `this.current` как implicit parent. Это была причина #1-#7: sidepanel attention определял parent tree node'а.
- **Стало:** `navigateUnder(parentId: NodeId | null, data, options)` — explicit parent. Если `parentId` null или не найден — fallback на root (**не** на `this.current`). `setAsCurrent: boolean` option — продвигать ли UI cursor. `navigate(data)` становится тонким wrapper: `navigateUnder(current?.id ?? null, data, { setAsCurrent: true })` — обратная совместимость сохранена.
- **Зачем:** Primitive для opener-based parent inference. Устраняет архитектурный flaw.
- **Как:** Переработал `navigate` — ввёл приватную логику поиска parent, сохранил все те же branches (same-URL-as-parent, same-URL-as-child, backOnRevisit ancestor walk, create new child), но параметризовал parent. Сам `navigate` сохранил свою sig.

### 17. `refactor(nav-handler): opener-first parent resolution + root fallback`
**Commit:** `3a4975c0`
**Файл:** `src/background/navigation/navigation-handler.ts`

- **Было:** Новые ноды всегда attach'ились под `tree.current`. Middle-click из таба A пока sidepanel смотрел на таб B — новый таб под B. Все вариации #1-#7.
- **Стало:** Parent резолвится перед lock:
  ```
  parent = tab.openerTabId
    ? (tabManager.nodeByTab(opener) ?? tabManager.lastNodeByTabId(opener))
    : tabManager.lastNodeByTabId(tabId) ?? null
  ```
  Обе branches (`existingNodeId` different URL + new-tab) теперь вызывают `tree.navigateUnder(parent, data, { setAsCurrent: isActiveTab })`. `setCurrentById(existingNodeId)`+`navigate` хак заменён на единый explicit-parent вызов.
- **Зачем:** **Единственный самый большой user-facing фикс в refactor'е.** Kills #1, #2, #3, #5, #6, #7, #23, #43, #93 — всё одним switch'ом.
- **Как:** Резолюция parent — синхронные tabManager reads снаружи лока. Внутри лока — `navigateUnder(openerDerivedParentId, ...)`. Никакого `tree.current` в качестве fallback parent (только как UI cursor — это отдельная ответственность).

### 18. `fix(lifecycle): remove speculative child creation in onTabActivated`
**Commit:** `8828ccb1`
**Файл:** `src/background/tabs/lifecycle.ts`

- **Было:** В `onTabActivated` fallback branch (таб без существующего nodeId) вызывал `tree.navigate(data)` — т.е. создавал node как child of `tree.current`. При первой активации pre-existing таба (SW только что проснулся, 20 табов открыто) создавалось 20 ложных parent edges.
- **Стало:** Если `findByUrl(url)` не возвращает match — `return { kind: "none" }`. Ждём настоящий webnav event для создания узла с правильным opener-derived parent.
- **Зачем:** #93 (P0). Trade-off (задокументирован в плане): табы, существовавшие до install'а/wake'а, не трекаются до первой навигации. Это **строго лучше** чем фабриковать неправильный parent.
- **Как:** Удалил ветку `else { tree.navigate(data); ... }`. Cleanup неиспользованных imports (`NodeData`, `Title`, `FaviconUrl`, `normalizeFaviconUrl`).

### 19. `fix(lifecycle): onWindowFocusChanged filters normal windows + dedup`
**Commit:** `85c1078c`
**Файл:** `src/background/tabs/lifecycle.ts`

- **Было:** Только проверка `windowId === WINDOW_ID_NONE`. Devtools pop-outs, picture-in-picture окна, macOS workspace transitions триггерили полный `onTabActivated` pipeline. Alt-tab каждый раз делал `cacheTree + notifyTreeUpdate`, даже если активный таб не изменился.
- **Стало:** Добавил `browser.windows.get(id)` check с `if (win.type !== "normal") return`. Также ввёл module-scope `lastFocusedActiveTabId` — короткое замыкание, если нода активного таба не изменилась.
- **Зачем:** #96 (хидден window triggers) + #43 (alt-tab write pressure).
- **Как:** `try { await browser.windows.get(id) } catch { return }` — Chrome API read безопасно снаружи лока. Сравнение с last-focused — простой сохранённый ref.

---

## Phase 3 — Webnav pipeline

### 20. `feat(webnav): documentId dedup + onErrorOccurred invalidation`
**Commit:** `165d8bc8`
**Файл:** `src/background/navigation/webnavigation.ts`

- **Было:** Три listener'а (`onCommitted`, `onHistoryStateUpdated`, `onReferenceFragmentUpdated`) делили один handler. SPA navigation (Gmail, Linear, GitHub) могла firing всех трёх — handler запускался 3 раза, создавая до 3 sibling-узлов per transition. `onErrorOccurred` вообще не listener'ился — aborted navigations оставляли stale redirect state.
- **Стало:** `isFreshDocument()` dedup через `Map<(tabId:docId:url), timestamp>` с 300ms TTL. При повторе в окне — `return`, не dispatch'им handler. `onErrorOccurred` listener clears `redirectDetector` для affected таба.
- **Зачем:** #10 (SPA fan-out creates duplicates), #64 (aborted nav poisons redirect detection).
- **Как:** Opportunistic GC если map > 64 entries. Backward compat: если browser не populate'ит documentId — dedup отключается (каждый event считается fresh).

### 21. `feat(nav-handler): integrate redirectDetector.isRedirect`
**Commit:** `ff5faf4f`
**Файл:** `src/background/navigation/navigation-handler.ts`

- **Было:** `redirectDetector.recordTabUrl` вызывался — но `isRedirect` имел **нулевые call-site'ы**. Каждый hop в redirect chain (OAuth: login → aad → app = 3 onCommitted) создавал child node. Пользователь входил на одну страницу, в дереве появлялись 3 мёртвые промежуточные узла.
- **Стало:** Перед `recordTabUrl` вычисляем `isRedirectHop = redirectDetector.isRedirect(tabId, incomingUrl)`. В existingNodeId-with-different-URL branch: если `isRedirectHop` — **перезаписываем URL существующего node'а in-place** вместо создания child'а. Дети node'а остаются прикреплёнными.
- **Зачем:** #8 — redirect chains генерят мусор в дереве; по сути дохлый код оживает.
- **Как:** Новая branch в existingNodeId block. Node.data rewrite через spread + `refreshSearchEntry`. `markNodeVisited` + `setCurrentById` под `isActiveTab` guard.

### 22. `fix(nav-handler): never in-place rewrite the root node's URL`
**Commit:** `e7eaa71f`
**Файл:** `src/background/navigation/navigation-handler.ts`

- **Было:** Ветвь `!shouldTrackUrl(nodeUrl)` (table на about:blank → переход на real URL) перезаписывала `node.data.url/title/favicon` in-place. Если `node.isRoot()` — root дерева незаметно становился тем, куда перешёл popup. Дети root'а оставались прикреплёнными.
- **Стало:** Guard `!node.isRoot()`. Если это root — fallthrough на следующую ветку (redirect-hop или create-new-child).
- **Зачем:** #12 (P0 about:blank root hijack). User persistent tree root становился popup destination — это data loss + misattribution.
- **Как:** Добавил условие `&& !node.isRoot()` — одна строка.

### 23. `fix(url-utils): drop title-substring match in isNewTabContext`
**Commit:** `0bc68b2e`
**Файл:** `src/background/utils/url-utils.ts`

- **Было:** `isNewTabContext(url, title)` matched если title (case-insensitively) содержал "new tab". False positives: Stack Overflow threads ("How do I open a new tab..."), Google Chrome Help ("Open a new tab..."), Notion templates — всё routed на root. Конверсно: custom NTP с title "Start page" — not matched и трекался как normal.
- **Стало:** Опирается только на `isNewTabUrl(url)` — URL pattern matching. `title` parameter оставлен для API compat (префиксован `_`).
- **Зачем:** #31, #32 (P1 false positives + false negatives).
- **Как:** Удалил две строки fallback'а; функция теперь просто `return isNewTabUrl(url)`.

### 24. `fix(url-key): strip credentials, canonicalize catch branch, preserve hash for SPA hosts`
**Commit:** `a767b726`
**Файл:** `src/shared/lib/url-key.ts`

- **Было:** Try-branch strip'ил `url.hash = ""` — SPA hash routes (#/foo → #/bar) были identical keys, невидимы в дереве (#34). `user:pass@` credentials ходили в persisted URL (#35). Catch-branch возвращал ключ без `scheme://` prefix — malformed URLs коллизировали в другом namespace (#63).
- **Стало:** Try-branch clears `url.username/password`. `SPA_HASH_ROUTING_HOSTS: Set<string>` — opt-in hosts, у которых hash preserved. Catch-branch тоже strip'ит credentials (regex) и возвращает same-shape key.
- **Зачем:** Три связанные проблемы URL-канонизации.
- **Как:** `url.username = ""; url.password = "";` перед всем остальным. `SPA_HASH_ROUTING_HOSTS.has(host)` — boolean, определяющий stripping hash'а. Catch: `candidate.replace(/^([scheme]:\/\/)(?:[^@/]+@)/i, "$1")`.

### 25. `fix(lifecycle): onTabUpdated detects URL change to untrackable scheme`
**Commit:** `64df6ad1`
**Файл:** `src/background/tabs/lifecycle.ts`

- **Было:** `onTabUpdated` только handled audio/title/favicon. Если `changeInfo.url` — no-op. Таб, ушедший на chrome:// без onCommitted, оставлял stale node mapping; subsequent title/favicon patches описывали неправильный URL.
- **Стало:** Проверка `changeInfo.url`: если untrackable — `tabManager.unregister(tabId)`. Trackable URL'ы handled webnavigation handler'ом (полный контекст + opener).
- **Зачем:** #33 (partial), #67 (onTabUpdated ignores changeInfo.url).
- **Как:** Добавил условный block в начале handler'а — одна ветка `if (changeInfo.url && !shouldTrackUrl)`.

---

## Phase 4 — Tree mutation API lockdown

### 26. `feat(nav-tree): updateNodeData(id, patch) centralizes in-place mutations`
**Commit:** `0a5a6943`
**Файл:** `src/background/state/nav-tree.ts`

- **Было:** Прямые `node.data = {...}` mutations в разных местах (nav-handler, editor-handlers, tab-sync). Search index не refresh'ился автоматически — rename или URL rewrite оставлял MiniSearch stale. URL-key index (следующий коммит) не мог поддерживаться.
- **Стало:** Метод `tree.updateNodeData(id, patch): NavigationNode | null`. Merge spread, refresh search entry если url/title/favicon изменились. (URL-key index добавляется в commit 336a851c).
- **Зачем:** Foundation for #16, #21, #44, #45 фиксов. Centralized invariant maintenance.
- **Как:** Новый public method. Проверяет diff'ы индексируемых полей — обновляет search только если нужно.

### 27. `refactor(tree-node): ancestry cycle check + preserve slot on remove()`
**Commit:** `cd4fb590`
**Файл:** `src/background/state/tree-node.ts`

- **Было:** `attachChild` проверял только `child === this` — можно было передать ancestor как child, получить cycle, DFS iter'ы + serialization зацикливались, SW зависал до kill'а Chrome. `remove()` делал `parent.appendChildren(this.children)` — лифтил детей в хвост parent'а, теряя original slot position (#11).
- **Стало:** `attachChild` walks ancestor chain `this.parent.getParent()...`; throws если находит `child`. `remove()` splices лифтнутых детей в **original slot position** (`parent.children.slice(0, index) + lifted + parent.children.slice(index+1)`).
- **Зачем:** #49 (P0 latent infinite loop), #11 (P0 child ordering lost). Оба — structural tree integrity.
- **Как:** `while (ancestor) { if (ancestor === child) throw; ancestor = ancestor.parent; }`. `remove()` сохраняет `index` и использует splice вместо append.

### 28. `refactor(nav-tree): ancestor-intersection current-repointing on merge`
**Commit:** `64a9db7e`
**Файл:** `src/background/state/nav-tree.ts`

- **Было:** `mergeDuplicateChildren` проверял только `this.current.id === child.id`. Если `current` — descendant of merged-away subtree (не direct child), cursor оставался указывать на zombie — reachable via `findNodeById` (nodeMap держал descendants), но invisible to DFS from root.
- **Стало:** `isDescendantOf(node, ancestor)` — walks вверх по parent chain. Если `this.current` is descendant of `child` (subtree root being merged away), re-point to `existing` (survivor).
- **Зачем:** #94 — zombie cursor.
- **Как:** Helper `isDescendantOf` — простой while-loop. В `mergeDuplicateChildren` перед detach/delete проверяем и repoint.

### 29. `feat(nav-tree): O(1) findByUrl via urlIndex + proximity preference`
**Commit:** `336a851c`
**Файл:** `src/background/state/nav-tree.ts`

- **Было:** `findByUrl(url)` делал O(n) DFS scan. Каждая регистрация нового таба на 10k-node дереве — линейный walk. Если несколько узлов share URL — возвращался first-in-DFS (nondeterministic-ish, не учитывал контекст).
- **Стало:** `private urlIndex: Map<string, Set<NavigationNode>>`, maintained в `createChild`, `updateNodeData` (URL change → unindex old + index new), `deleteNode`, `deleteChildren`, `deleteSubtree`, `mergeDuplicateChildren`, `clear`. `constructFromRoot` re-indexes at hydrate. Новая сигнатура: `findByUrl(url, near?)` — если `near` дан и set.size>1, walk'ает ancestors → descendants → fallback first.
- **Зачем:** #73 (arbitrary DFS winner), #74 (O(n) per nav).
- **Как:** Два helper'а `indexUrlForNode/unindexUrlForNode`. `findByUrl` при `size>1` и `near` walks ancestor chain сначала, потом subtree, потом first.

### 30. `refactor(tree-node): drop Object.freeze allocation from getChildren`
**Commit:** `6fcaa405`
**Файл:** `src/background/state/tree-node.ts`

- **Было:** `getChildren(): readonly TreeNode<T>[] { return Object.freeze([...this.children]); }` — аллокация фrosen array на каждый call. 5k-node tree рендер = ~20k allocations, GC churn. Freeze was misleading — внутренние мутации (removeChildAt, appendChildren) работали, cosmetic guard.
- **Стало:** Return `this.children` напрямую, типизированный `readonly TreeNode<T>[]`. TypeScript enforce'ит no-mutation на compile-time.
- **Зачем:** #47 — perf на hot path.
- **Как:** Одна строка changed.

### 31. `refactor(nav-tree): timestamped LWW for pinned + layout merges`
**Commit:** `43ee1cea`
**Файлы:** `src/shared/types/node.ts`, `src/background/state/nav-tree.ts`

- **Было:** `mergeNodeData` использовал `Boolean(base.pinned || incoming.pinned)` (pin stuck forever once pinned — #61) и `base.layout ?? incoming.layout` (base wins; hand-arranged positions могут пропасть — #60, #17).
- **Стало:** `NodeData` получил `pinnedUpdatedAt?: Timestamp` и `layoutUpdatedAt?: Timestamp`. Merge: newer stamp wins. Если только одна сторона имеет stamp — она wins. Если никакая — fallback на старое поведение (OR, base-wins) — обратная совместимость с pre-v2 data.
- **Зачем:** #17, #60, #61.
- **Как:** Два optional fields + LWW логика в `mergeNodeData`. Writers (pin/unpin RPC, layout save) должны ставить stamp — это следующий follow-up; пока только infrastructure.

### 32. `refactor(tab-sync): route via updateNodeData + withTreeLock`
**Commit:** `14ad2deb`
**Файл:** `src/background/tabs/tab-sync.ts`

- **Было:** `syncTabTitleFavicon` напрямую `node.data.title = ...`, `node.data.favicon = ...`. Manual `tree.refreshSearchEntry(nodeId)` только для title. Favicon change — silent (missed search refresh). Не под лок.
- **Стало:** `patch: Partial<NodeData>` собирается снаружи, `withTreeLock(async () => tree.updateNodeData(nodeId, patch); cacheTree)`. `notifyTreeUpdate` снаружи лока.
- **Зачем:** Часть #16 (in-place writes bypass index), #21 (title-sync race). Lock discipline = consistency с остальным background'ом.
- **Как:** Rewrite function — явный lock pattern.

---

## Phase 5 — Tab manager hardening

### 33. `refactor(tab-manager): register validates tree nodeId + onNodesDeleted hook`
**Commit:** `398ecadb`
**Файлы:** `src/background/state/tab-manager.ts`, `src/background/state/nav-tree.ts`, `src/background/service-worker.ts`

- **Было:** `TabManager.register(nodeId, tabId)` не проверял, существует ли nodeId в дереве. Stale RPC handler мог пин'нуть таб на удалённый node — phantom-запись в `nodeToTabs`, `openNodes()` возвращал zombie. `NavigationTree.deleteNode/Subtree/Children` не уведомляла TabManager — мapped табы висели на dead id. `suppressNextTouch` — single `TabId | null` token, overwrite race.
- **Стало:** `TabManager.setTreeAccessor(() => NavigationTree | null)` — вызывается в service-worker bootstrap. `register` проверяет `tree.findNodeById(nodeId)` и warn'ит + no-op на miss. `NavigationTree.onNodesDeleted(listener)` — pub/sub; все delete paths (`deleteNode`, `deleteChildren`, `deleteSubtree`, `mergeDuplicateChildren` cleanup) emit'ят `emitNodesDeleted(ids)`. TabManager subscribes в service-worker и `onNodesDeleted(ids)` unregister'ит mapped табы. `suppressTouchForTabId` — `Map<TabId, boolean>`.
- **Зачем:** #22 (orphan tab), #29 (phantom nodes), #51 (suppress token overwrite). Tree и TabManager теперь синхронны.
- **Как:** Accessor injection + listener API + Map swap. `emitNodesDeleted` в каждом delete code path; tree constructor hooks его после hydrate.

### 34. `refactor(tab-lru): getLastUsed undefined-for-untracked + derived latestNodeId`
**Commit:** `a694a83a`
**Файлы:** `src/background/state/tab-lru.ts`, `src/background/state/tab-manager.ts`

- **Было:** `getLastUsed` возвращал `this.lastUsed.get(tabId) || 0` — collapsed "untracked" и "tracked at epoch". На fresh Chrome profile все табы имеют `lastAccessed=0`, `closeOldest` sort'ил их arbitrarily — first-opened anchor tab часто закрывался первым (#40). `latestNodeId` хранился отдельным полем; `remove()` с replacement не обновлял его — consumers'ы могли получить mismatch (tabId-nodeId несовместимые, #50).
- **Стало:** `getLastUsed` возвращает `number | undefined`. `track()` не seed'ит 0. `touch()` preserves existing timestamp если новый не дан (#72). `latestNodeId` — derived property через `nodeResolver: (tabId) => NodeId | undefined`, injected в constructor. `closeOldest` tie-breaker: `(lastUsed ?? -1, tabId)` — deterministic. `getTabsByRecency` / `getNodeRecency` правят undefined.
- **Зачем:** #40 (fresh profile sort), #50 (derived invariant), #72 (overwrite preserve), #71 (вплоть до следующего коммита, где touch validates nodeId).
- **Как:** Type change `number | undefined`. nodeResolver callback — DI pattern. constructor + reset() wire resolver.

### 35. `refactor(tab-manager, temp-selection): validate touch nodeId; drop speculative unregisters`
**Commit:** `aebfe207`
**Файлы:** `src/background/state/tab-manager.ts`, `src/background/services/temporary-selection.ts`

- **Было:** `touch(tabId, _nodeId, lastUsed?)` с префиксом `_` — параметр tiho игнорировался. Callers'ы не могли детектировать, что их nodeId разъехался с index'ом (#71). `temporary-selection` при transient focus failure (`browser.tabs.update` throw) вызывал `tabManager.unregister(tabId)` — destroyed user mapping, хотя таб мог быть жив. 5 мест (#57).
- **Стало:** `touch` сравнивает аргумент с `index.nodeByTab(tabId)`; при mismatch — warn, всё равно trust'ит index (LRU должен отражать реальность). `temporary-selection` preview/cancel/accept просто `clearSuppressActivate` на focus failure — no unregister.
- **Зачем:** #71 (лживый параметр), #57 (speculative cleanup).
- **Как:** Добавил guard + log. В temp-selection удалил 5 `tabManager.unregister` вызовов в transient-failure paths.

### 36. `refactor(tab-index): shared frozen empty Set singleton on miss`
**Commit:** `5fd9ffde`
**Файл:** `src/background/state/tab-index.ts`

- **Было:** `tabsByNode(nodeId): Set<TabId>` возвращал `this.nodeToTabs.get(nodeId) ?? new Set()`. Каждый miss — аллокация. Также consumers'ы могли ошибочно думать, что мутация возвращаемого Set изменяет live state (#48).
- **Стало:** `EMPTY_TAB_SET: ReadonlySet<TabId>` — frozen singleton. Возвращается на miss. Документирует: только `addTabToNode`/`removeTabFromNode` меняют membership.
- **Зачем:** #48 (API smell + perf).
- **Как:** `const EMPTY_TAB_SET = Object.freeze(new Set<TabId>())` в module scope.

### 37. `fix(tab-manager): closeOldest unregisters only when Chrome confirms tab is gone`
**Commit:** `0c185f1d`
**Файл:** `src/background/state/tab-manager.ts`

- **Было:** `browser.tabs.remove()` мог reject даже когда таб реально закрыт (window-close cascade race). Catch branch возвращал null без unregister'а — `tabCount` завышен — `closeOldestUntil` over-close'ил лишние табы (#75).
- **Стало:** В catch: `try { await browser.tabs.get(tabIdToClose) }` — если success (tab жив), warn + return null (outer loop exit'ит чисто). Если throw — tab gone, unregister.
- **Зачем:** #75 over-closing.
- **Как:** Nested try/catch в existing catch arm.

---

## Phase 6 — Storage and persistence

### 38. `fix(sync-engine): unstubArchiveEntry after saveArchiveTree materialization`
**Commit:** `4d677a2c`
**Файл:** `src/background/sync/sync-engine.ts`

- **Было:** `fetchRemoteTreePayload` сохранял blob локально через `saveArchiveTree`, но не снимал `stub: true` флаг в archive index. Каждое следующее открытие — re-download из Supabase (#36).
- **Стало:** После `saveArchiveTree` — вызов `treeStorage.unstubArchiveEntry(treeId)` (функция существовала в tree-storage.ts, но имела нулевые callers).
- **Зачем:** #36 — bandwidth waste и latency.
- **Как:** Одна строка + комментарий.

### 39. `fix(storage): dirty flag flipped after save resolves, not before`
**Commit:** `da2b8bd4`
**Файл:** `src/background/services/tree-storage.ts`

- **Было:** `this.dirty = false` **перед** `await saveTreeToChrome(tree)`. Если SW убит в промежутке, `dirty` уже lowered, но запись не завершилась. Мутация, пришедшая mid-save, могла не re-trigger'ить save.
- **Стало:** `this.dirty = false` **после** `await`. Catch — не нужно re-set'ить (он никогда не был lowered); просто `scheduleSave()` для retry.
- **Зачем:** #56 — SW termination mid-save.
- **Как:** Переставил одну строку. Упростил catch branch.

### 40. `fix(storage): clearArchivesOnly + clearAllTrees continue on per-key errors`
**Commit:** `b1bd9d8c`
**Файл:** `src/background/services/tree-storage.ts`

- **Было:** Один `try` wrap'ил весь loop. Первый `removeItem` throw abort'ил остальное — часть blob'ов оставалась orphaned и ел quota (#55).
- **Стало:** `safeRemove(label, fn)` helper — per-key try, warn on fail. `for (const e of index) safeRemove(...)`.
- **Зачем:** #55 — best-effort cleanup.
- **Как:** Рефакторинг obeys Object.map.

### 41. `fix(tab-restoration): non-destructive getOpenTabs + consumeOpenTabs`
**Commit:** `bd5eb3e0`
**Файлы:** `src/background/services/tab-restoration.ts`, `src/background/messaging/handlers/tree-handlers.ts`

- **Было:** `getOpenTabs(treeId)` делал read-and-delete atomically. Партial restore (SW killed mid-loop, `tabs.create` throw) — оставшиеся URL'ы lost forever (#80).
- **Стало:** `getOpenTabs` просто peek'ает. Новая `consumeOpenTabs(treeId)` — вызывается caller'ом после успешной обработки. В `tree-handlers.ts` switchTree считает `createdCount`; `consumeOpenTabs` только если `createdCount === savedUrls.length`.
- **Зачем:** #80 — silent data loss.
- **Как:** API split. Caller-driven lifecycle.

### 42. `fix(sync-engine): compare server updated_at (not client savedAt) for conflicts`
**Commit:** `be8ef693`
**Файл:** `src/background/sync/sync-engine.ts`

- **Было:** `doPull` гейт: `if (summary.savedAt > existing.savedAt)` — client-generated `savedAt`. Device B с 10-мин назад clock'ом писал первым, но `savedAt` оказывался старше — gate false — conflict никогда не fire'ил — next push from A silent clobbered B (#14).
- **Стало:** Сравнение `server updated_at` (Postgres-trigger stamp, монотонен per-row) против `syncMeta.lastRemoteUpdatedAt`. Tiebreaker: identical updated_at → lexicographic `row.id` compare.
- **Зачем:** #14 — cross-device silent data loss.
- **Как:** Пересчитали expression. Tiebreaker как client-side mitigation; true monotonic revision column — follow-up в Supabase schema.

---

## Phase 7 — Notifications & sidepanel store

### 43. `fix(notifications): extend IMMEDIATE_REASONS + merge pendingArgs.view`
**Commit:** `dcf28167`
**Файл:** `src/background/messaging/notifications.ts`

- **Было:** `IMMEDIATE_REASONS` не содержал `navigate`, `rename`, `tabs`, `temp-selection`, `sync` — они debounce'ились на 200ms. Rename dialog закрывался, но sidepanel показывал старый title (#85). Click-to-navigate feels sluggish (#86). `pendingArgs = { treeJSON, reason, ...(view ? {view} : {}) }` replace'ил wholesale — pending view-intent от rename'а терялся на coalesce (#91).
- **Стало:** Все пять reasons добавлены в IMMEDIATE_REASONS. `pendingArgs.view` теперь merge: `view ?? pendingArgs?.view`.
- **Зачем:** #85, #86, #91.
- **Как:** 5 строк в Set + merge expression.

### 44. `fix(store): stop viewIntent leaking across unrelated tree updates`
**Commit:** `c81b693a`
**Файл:** `src/apps/sidepanel/ui/state/store.ts`

- **Было:** `applyTreeState` сохранял `nextViewIntent = payload.view ?? state.graph.viewIntent`. Rename (с focus-intent) → потом background tab refresh (`tabs` reason, no view) → stale intent re-применялся, graph re-focus/zoom'ил на старый target (#87).
- **Стало:** `resolvedViewIntent = payload.view ?? null` — view-intent one-shot; если новый payload не несёт view, clear.
- **Зачем:** #87 — stale intent leak.
- **Как:** Одна строка — убран `?? state.graph.viewIntent` fallback.

---

## Phase 8 — UI shortcut fixes

### 45. `fix(shortcuts): overlayOpen covers all dialogs + drop duplicate Shift+Delete`
**Commit:** `c99c9c13`
**Файл:** `src/apps/sidepanel/ui/hooks/useShortcuts.ts`

- **Было:** `overlayOpen` проверял только `pinnedOpen || treesOpen || tagFilterOpen || contextMenu`. Rename dialog + focus on Cancel + Backspace → deleteNodes выполнялся (data loss #84). `Shift+Delete` был declared как separate binding AND handled через `event.shiftKey` branching в базовом Delete — tinykeys dispatch'ил оба, deleteNodes fire'ил дважды (#92).
- **Стало:** `overlayOpen` покрывает `renameTarget`, `deleteTreeConfirm?.open`, `commandPalette.open`, `syncConflict`. Дубликаты Shift+Delete / Shift+Backspace удалены; базовый Delete / Backspace с `event.shiftKey` branch справляется.
- **Зачем:** #84 (P0 silent deletion), #92 (double-fire).
- **Как:** Extended boolean expression. Delete два binding-объекта.

---

## Phase 9 — Editor / undo

### 46. `fix(editor): clearHistory BEFORE snapshot, not after`
**Commit:** `6d8039ae`
**Файл:** `src/background/messaging/handlers/editor-handlers.ts`

- **Было:**
  ```
  snapshot(currentTree, "Enter editor mode");
  CommandManager.clearHistory();  // wipes the snapshot just queued
  ```
  Undo past first edit не работал — стек пуст.
- **Стало:**
  ```
  CommandManager.clearHistory();
  snapshot(currentTree, "Enter editor mode");
  ```
- **Зачем:** #18 — bug в ordering.
- **Как:** Swap двух строк.

### 47. `fix(undo): cacheTree before tab reconcile; drop tabManager.reset()`
**Commit:** `386012e8`
**Файл:** `src/background/messaging/handlers/undo-handlers.ts`

- **Было:** `applyTree` делал `await syncOpenTabs()` **до** `treeStorage.cacheTree(tree)`. syncOpenTabs читал OLD cachedTree. Внутри syncOpenTabs — `tabManager.reset()` + re-register по URL match. Любой таб, чей URL изменился — stranded (#19).
- **Стало:** `await withTreeLock(async () => { cacheTree(tree) — СНАЧАЛА; потом reconcile — для каждого open node проверяем findNodeById; если нет, unregister mapped табов; потом rewire onNodesDeleted listener на новый tree instance })`.
- **Зачем:** #19.
- **Как:** Полностью переписал `applyTree`. Вместо reset — surgical unregister только orphaned табов.

---

## Phase 10 — Settings, recency, lifecycle

### 48. `feat(settings): storage.onChanged watcher + merge preserves overrides`
**Commit:** `e0ca1afd`
**Файл:** `src/background/services/settings.ts`

- **Было:** Background settings state только refresh'ился на boot. Out-of-band write (onboarding, settings page direct write, sidepanel) не доходил — stale values до SW restart (#81). `saveSettings` делал `{...defaultSettings, ...next}` — future default fields stomp user overrides (#82).
- **Стало:** `settingsItem.watch((value) => { this.settings = mergeDefaults(value); this.pushBlocklist(); })` — реагирует на любой storage change. `saveSettings` re-reads stored → `{...defaults, ...storedMerged, ...next}` — preserves saved overrides при добавлении новых defaults.
- **Зачем:** #81, #82.
- **Как:** `settingsItem.watch` API (WXT storage). Re-read-and-merge в saveSettings.

### 49. `fix(recency): split visitCount increment from lastVisitedAt guard`
**Commit:** `4d4479f9`
**Файл:** `src/background/state/node-recency.ts`

- **Было:** `if (nextAtRaw <= prevAtRaw) return false;` — если timestamp не newer, **вся функция** no-op'ила — включая visitCount++. Mixed clock sources (`Date.now()` vs `tab.lastAccessed`) давали < prevAt → visit count dropped (#79).
- **Стало:** `timestampAdvances = nextAtRaw > prevAtRaw`. visitCount++ **всегда**. `lastVisitedAt` update только если `timestampAdvances`.
- **Зачем:** #79 — clock-mixing undercount.
- **Как:** Split conditional — две независимые operations.

### 50. `fix(lifecycle): incognito gate in every tab-event handler`
**Commit:** `13d57b1d`
**Файл:** `src/background/tabs/lifecycle.ts`

- **Было:** `privacy.skipIncognito` honored только в navigation-handler. onTabCreated/Activated/Updated/Removed/FocusChanged не проверяли `tab.incognito` — incognito state утекал в public tree и Supabase sync (#30 privacy leak).
- **Стало:** Helper `skipIncognito(tab)` центрально. Gate в начале onTabCreated, onTabActivated (после fresh tabs.get), onTabUpdated. onTabRemoved intentionally продолжает — unregister нужен даже для incognito.
- **Зачем:** #30 — privacy leak.
- **Как:** Module-level helper + три `if (skipIncognito(tab)) return` guard'а.

### 51. `fix(lifecycle): onTabRemoved uses removal-info windowId`
**Commit:** `a7bc1c30`
**Файл:** `src/background/tabs/lifecycle.ts`

- **Было:** `browser.tabs.query({ active: true, currentWindow: true })` — возвращал active таб last-focused окна. Close таб в background окне → `tree.current` yanked на foreground window's active tab (unrelated page, #65).
- **Стало:** `browser.tabs.query({ active: true, windowId: removeInfo.windowId })` — scoped на правильное окно. Fallback на `getActiveTab()` если window closed. Также документирует: cacheTree BEFORE notify (#66).
- **Зачем:** #65, #66.
- **Как:** Чётко типизированный `removeInfo.windowId` check + fallback. Reorder комментарий для #66.

### 52. `chore: remove dead 0-byte history-api.ts module`
**Commit:** `89bb3d6c`
**Файл:** `src/background/navigation/history-api.ts` (deleted)

- **Было:** 0-byte empty file от старого refactor'а. Confused readers, показывался в grep как unused module.
- **Стало:** Файл удалён.
- **Зачем:** #54 — dead file cleanup.
- **Как:** `git rm`.

### 53. `fix(url-utils): canonicalize blocklist cache key (sort + escape)`
**Commit:** `942d4ccc`
**Файл:** `src/background/utils/url-utils.ts`

- **Было:** `const key = patterns.join("\n")` — reorder `['a','b']` → `['b','a']` вызывал pointless recompile (different key, semantically identical). `['a\nb']` коллизировал с `['a', 'b']` в хеше (#97).
- **Стало:** `sorted = patterns.map(escape).sort()`; `key = sorted.join("|")`. Deterministic, collision-safe, reorder-stable.
- **Зачем:** #97 — cache key smells.
- **Как:** Sort + regex-escape backslash/pipe в каждом pattern.

---

## Свод

**52 atomic commits** (numbered 1-53 minus 14 pre-existing test fix — **nice нумерация** для человека: 48 commits моих + 3 cleanup/docs + 1 pre-existing test).

Phase-level summary:
- **Phase 0** (cleanup + infrastructure): 7 commits
- **Phase 1** (identity + locks): 6 commits
- **Phase 2** (parent inference): 5 commits
- **Phase 3** (webnav pipeline): 6 commits
- **Phase 4** (mutation API lockdown): 7 commits
- **Phase 5** (tab manager hardening): 5 commits
- **Phase 6** (storage/persistence): 5 commits
- **Phase 7** (notifications/store): 2 commits
- **Phase 8** (UI shortcuts): 1 commit
- **Phase 9** (editor/undo): 2 commits
- **Phase 10** (settings/recency/lifecycle): 6 commits

Все commits прошли `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm lint` (0 errors).
