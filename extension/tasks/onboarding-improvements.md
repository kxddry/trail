# Onboarding — улучшения по паттернам из "How Top Apps Design Onboarding"

Источник: `~/vault/inbox/20260416-Qsq-Sj_rojU-How Top Apps Design Onboarding.txt`
Базовый флоу: `extension/tasks/onboarding-interactive.md` + `src/apps/sidepanel/ui/onboarding/`
Дата анализа: 2026-04-22

Текущий флоу уже покрывает многое из видео (персона, aha-moment через interactive tour, outcome-копи, celebration). Ниже — чего не хватает, строго по паттернам из транскрипта.

> **Sanity-check state API (extension):** `skipOnboarding` в `apps/sidepanel/api/onboarding.ts:68` пишет только `seenWelcome + phase: "done"`, `completeOnboarding` пишет и `completedAt`. То есть skip ≠ complete семантически разведены — это важно держать, когда будут меняться #13 и #14 ниже.

## 1. Персона: multi-select (Headspace → +10% free-trial conversion)

**Проблема:** `wizard/PersonaPickScreen.tsx` — single-select из 4 тайлов. Пользователи приходят с несколькими болями одновременно: «open tabs» + «research threads» почти всегда ходят парой.

**Паттерн (Headspace):** разрешить выбор нескольких целей; всё ещё требовать primary.

**Изменения:**
- `OnboardingPersona` → `{ primary: PersonaId; secondary: PersonaId[] }` в `shared/config/storage-items.ts`
- `PersonaPickScreen`: `aria-pressed` множественный, primary помечается отдельно (long-press / иконка-звёздочка)
- `SolutionScreen`: основной текст по primary, chips подмешивают outcomes из secondary
- `cta/TourCommitments.tsx` tagline — по primary

**Impact/effort:** High / Low.

## 2. «Show what the answers unlocked» (Endos / Bitepal / Brilliant)

**Проблема:** после Persona → `SolutionScreen` показывает абстрактный `SolutionVisual` + текст. Пользователь не видит своей будущей версии Trail.

**Паттерн:** после квиза рисуют **персонализированный план** пользователя — Endos, Bitepal («you'll lose weight by [date]»), Brilliant (homepage уже populated).

**Изменения:**
- `SolutionVisual.tsx` — заменить абстрактный мини-граф на **мок-дерево под конкретный сценарий**:
  - `research` → 3 параллельные ветки сравнения с лейблами типа "Option A / B / C"
  - `article` → дерево + search-overlay «найти ту статью»
  - `learning` → глубокое дерево с подсветкой текущего фокуса
  - `tabs` → широкое дерево-хаб из 12+ узлов
- Подпись: «So будет выглядеть твой Trail через неделю» (или аналог)

Самый недоиспользованный паттерн. Делает «это про меня» ещё до тура.

**Impact/effort:** High / Medium.

## 3. Human / founder touch — отсутствует

**Паттерн:** Base Camp кладёт заметку CEO после account creation. Airbnb — видео CEO на aha-моменте. One year — handwritten signature + handdrawn flower.

**Изменения:**
- После `TourCelebration`, перед `TourCommitments`, вставить 1 экран на 2.5s авто-advance:
  - Короткая заметка от автора (2 строки), подпись SVG-скриптом
  - Пример: «— Иван, твой первый trail сохранён. Удали его и начни настоящий. Спасибо, что попробовал.»
- Кладётся в `onboarding/celebration/FounderNote.tsx`, фаза `phase: "founderNote"` между `celebration` и `cta`

Органично ложится на free/indie-позиционирование продукта.

**Impact/effort:** Medium / Low.

## 4. Post-onboarding checklist — Mural +10% weekly retention

**Проблема:** `finish()` в `TourCommitments` всё закрывает. Онбординг — одноразовый. Mural получил +10% weekly retention, заменив popup-flow на **persistent checklist**.

**Паттерн:** checklist живёт после онбординга, dismiss'ится вручную.

**Изменения:**
- Новый компонент `onboarding/checklist/QuickStart.tsx`, collapsible в сайдпанели:
  - [ ] Создай первое дерево
  - [ ] Сделай первую ветку
  - [ ] Запини расширение в тулбар
  - [ ] Войди, чтобы синхронизировать
- Состояние в `onboardingStateItem`: `quickStart: { dismissed: boolean; completed: string[] }`
- Галочки автоматические через существующие события store (tree created, branch detected via `tour-machine` предикаты, auth state)

**Impact/effort:** High / Medium.

## 5. Hook: show, don't tell (Timo / Front Butts)

**Проблема:** `wizard/HookScreen.tsx` — `TrailLogo` + заголовок + подпись. Статично.

**Паттерн (Timo):** показывают продукт в action на welcome-экране. Front — animation с открытия.

**Изменения:**
- Заменить static logo на **автоплейное мини-демо** (5 сек loop):
  - Строится мини-граф: узел → узел → узел → ветка → подсветка возврата
  - Чистый CSS/SVG, без video
- Читается за 2 секунды, ощущается сильнее слогана
- Оставить заголовок/подпись снизу

**Impact/effort:** Medium / Medium.

## 6. Pre-permission explainer (Brilliant / Cool Center)

**Паттерн:** кастомный экран **перед** нативным permission-промптом сильно поднимает accept-rate. Cool Center даже показывает тизер самой нотификации.

**Изменения:**
- Audit: где в онбординге/туре запрашиваются permissions (history, bookmarks, notifications)?
- Если есть — поставить explainer за 1 экран: «Trail будет следить за твоими переходами, чтобы рисовать trail. Локально, в твоём браузере.»
- Сейчас `handleEnterTour` переключает active tree молча — минимум одна строка «готовим изолированное дерево для тура» не помешает.

**Impact/effort:** Medium / Low (при условии что permission-промпты есть).

## 7. Progressive education вместо frontload (Cake Equity)

**Проблема:** `wizard/FeaturesScreen.tsx` грузит 3 outcome-буллета заранее. Пользователь ещё не видел продукт, копи уходит в пустоту.

**Паттерн (Cake Equity):** объяснение появляется **в момент действия** — tooltips, inline-reassurance.

**Изменения:**
- Удалить `FeaturesScreen` из wizard'а (5 экранов → 4)
- Добавить три contextual tooltip'а во время тура:
  - После первого клика: «Каждый таб — узел, к которому можно вернуться»
  - После branch: «Вот ты вернулся и кликнул другое — обе ветки сохранены» (уже похожее в `celebrateBranch`)
  - После нажатия на abandoned child: «Поиск работает по тому, что ты делал, а не по URL»
- Cадятся в `tour/TourCoach.tsx` `STEP_CONTENT` как `subBodyKey` или отдельные micro-steps

**Impact/effort:** Medium / Medium. Бонус: сокращает wizard на 1 экран.

## 8. Split sign-up (House +15%)

**Проблема:** `TourCommitments` → `[Sign in]` открывает `/login.html` с одной формой.

**Паттерн (House):** разбивка на несколько шагов снижает воспринимаемую friction, +15% conversions.

**Изменения:**
- Audit `/login.html` (login-app): если email+password на одном экране, разделить:
  - Step 1: email
  - Step 2: password
  - Step 3 (опц): carry-over personalization из онбординга («what do you want to sync?»)
- Persona из онбординга передать в login через `chrome.storage.local` → pre-populate

**Impact/effort:** Medium / Medium. Требует правок в login-app, не только онбординге.

## 9. Loading как момент (Bumble)

**Проблема:** в `OnboardingWizard.handleEnterTour` есть `window.setTimeout(..., 3000)` watchdog для ожидания создания tour-tree. Сейчас — невидимый фриз.

**Паттерн (Bumble):** даже «boring» экраны проверки должны быть живыми.

**Изменения:**
- Вставить transition-экран «готовим твой первый trail»
- Мини-прогресс-штрих (или индетерминированный shimmer), спустя 300ms показа — fade в следующий экран
- Превращает невидимое ожидание в anticipation-beat

**Impact/effort:** Low / Low.

## 10. Celebration tagline — персона-specific

**Проблема:** `TourCelebration` показывает «N nodes in S seconds» + общий body. Body — одинаковый для всех персон.

**Изменения:**
- Добавить одну персона-специфичную строку в `celebration.body`:
  - `research`: «Твоё настоящее исследование выглядит так же — только длиннее.»
  - `article`: «Каждая статья, которую ты хотел перечитать — теперь findable.»
  - `learning`: «Следующий раз, когда тема продолжится — продолжишь с этой же точки.»
  - `tabs`: «Можешь закрыть их все. Они никуда не денутся.»
- Ключи `onboarding.celebration.body.research/article/learning/tabs` в `en.json` + `ru.json`

**Impact/effort:** Medium / Low.

## 11. Trust / privacy reassurance в activation-момент

**Проблема:** Trail пишет browsing history. Вопрос приватности критичнее обычного. Сейчас объяснение «что сохраняется, что нет» лежит в Settings, куда пользователь попадает в лучшем случае через неделю. В плане `onboarding-interactive.md` был пункт «Privacy disclosure → screen 5 as a one-liner + expandable details», но в текущих 5 экранах я его не вижу — `FeaturesScreen.tsx` только про outcome-буллеты.

**Изменения:**
- На `FeaturesScreen` (либо между Features и Tour) — одна строка + collapsible `<details>`:
  - Что сохраняется (URL + title + parent-node, **не** cookie / не DOM / не контент страниц)
  - Где живёт (local chrome.storage; sync только для залогиненных, opt-in)
  - Как паузить (toggle в тулбаре)
- Альтернатива: показывать на экране до создания tour-tree, где пользователь первый раз «отдаёт» данные.
- Ключ `onboarding.v2.privacy.*` в `en.json` + `ru.json`.

**Impact/effort:** Medium / Low. Снимает крупный барьер для consumer-продукта с browsing-данными.

## 12. Outcome-first копи — audit для account-карты пользователя внутри extension

**Проблема:** большая часть extension wizard'а уже outcome-focused, но стоит прогнать audit в `en.json` под `onboarding.*` и окрестным UI (empty states в настройках, tree-list placeholder, login-app welcome) на технический жаргон: "graph", "tree structure", "navigation", "nodes", "records".

**Изменения:**
- Grep `en.json` / `ru.json` на `graph|tree|node|navigation|records` и переписать в outcome-виде где уместно.
- Пример из видео: Trail-как-инструмент → «Remember how you got somewhere, not just where you landed» > «records your navigation as tree structures».

**Impact/effort:** Low / Low. Чисто copy-pass, можно прицепом к #1 / #2.

## 13. Skip в туре — resumable dismiss, а не финал

**Проблема:** `TourCoach.handleSkip` пишет `phase: "done"` и `tourTreeId: null`. Пользователь, который закрыл тур случайно или захотел «позже», теряет его навсегда — resume не поддержан (хотя `seenWelcome` + wizard умеют resume).

**Паттерн (Mural):** checklist «sticks around even after the user dismisses the initial flow».

**Изменения:**
- Ввести третий статус между `"tour"` и `"done"`: `"tourDismissed"`. `handleSkip` в `TourCoach` → пишет `phase: "tourDismissed"`, но **не** ставит `completedAt`.
- В sidepanel где-то в углу появляется ненавязчивый chip «Resume tour» (показывается пока `phase === "tourDismissed"` и `completedAt == null`).
- Клик по chip → phase = `"tour"`, tour возобновляется со своего шага (уже работает через `tourStep` в storage).
- `completeOnboarding` остаётся единственным, кто ставит `completedAt` — chip уходит.

**Impact/effort:** Medium / Low. Раскрывает силу уже сделанного resume-механизма, сейчас он заблокирован кнопкой skip.

## 14. «Sticky» quick-start checklist — отложенные CTA из Screen 8

**Проблема:** `TourCommitments` показывает [Sign in] / [Maybe later]. Если пользователь жмёт `Maybe later`, `completeOnboarding` срабатывает сразу и CTA исчезают навсегда. Единственный способ получить их обратно — «replay onboarding» в Settings (который и не провязан, по `onboarding-interactive.md`).

**Паттерн (Mural, +10% weekly retention):** dismissed items остаются доступны через персистентный checklist.

**Изменения:**
- Пересекается с #4 (там я предлагал полноценный QuickStart). Сфокусированный минимум для этого пункта:
  - `[Maybe later]` → `completeOnboarding` остаётся, но `softCtaDismissed: false` в `onboardingStateItem`
  - Пока `softCtaDismissed === false` AND соответствующий action не сделан — в сайдпанеле живёт маленькая dismissible-полоска:
    - «Sign in to sync across devices» (уходит по клику / по реальному login-event)
    - «Pin Trail to toolbar» (уходит по клику; detection через `chrome.action` API если есть)
- Полоска dismissible отдельной кнопкой × (пишет `softCtaDismissed: true`).

**Impact/effort:** Medium / Low. Дешевле полноценного #4, но бьёт в ту же цель — не терять activation-моменты, которые пользователь отложил.

## 15. Сократить wizard до 2–3 экранов (time-to-aha)

**Проблема:** сейчас между установкой и реальной интерактивностью лежат **5 модальных экранов** (`OnboardingWizard.tsx` STEPS HOOK → PROBLEM → PERSONA → SOLUTION → FEATURES) плюс watchdog на создание tour-tree. Для extension это долго — пользователь ещё на старте пути, и сжимать wizard в соло-read-then-next режим значит терять его на второй странице.

**Паттерн (видео):** лучшие onboarding'и для простых продуктов просто не мешают («Maybe the best experience is just to let users get in fast»). Tiktok — «2 вопроса → customize → done».

**Изменения:**
- Резать до Hook → Persona → Tour. Solution+Features мёрджатся в Persona (persona-specific preview прямо на тайле из пункта #2) либо уезжают в tour-coach tooltips (пункт #7).
- Альтернатива помягче: Hook+Persona на одном экране (persona-тайлы под Hook-заголовком), второй экран = Tour-entry с пересказом в одно предложение.
- Wizard state сжимается с 5 шагов до 2–3, `wizardStep` остаётся для resume, но меньше промахнуться.

**Impact/effort:** High / Medium. Пересекается с #7 (там я предлагал срезать только FeaturesScreen) и #2 (persona-preview) — логичный шаг вперёд от обоих.

## 16. «Try it» CTA на первом экране

**Проблема:** `[Let me feel it]` показывается только на 5-м экране (`en.json:160`). До этого — чистый read-only режим. Пользователь читает про продукт дольше, чем пробует его.

**Паттерн (Alma):** «lets you try the core experience before you sign up». Видео явно выделяет это как отдельный и редкий в AI-продуктах паттерн.

**Изменения:**
- На `HookScreen` помимо primary `[Show me]` добавить secondary кнопку `[Try it on this page]` или `[Open guided demo]`:
  - `Try it on this page` → закрывает wizard, активирует trail-capture на текущей вкладке, coach-tooltip через ~3 секунды: «видишь узел в графе? Это ты здесь»
  - `Open guided demo` → пропускает wizard, сразу открывает tour-tree со сгенерированным fixture-деревом (research/article/whatever по default-персоне)
- Primary `[Show me]` остаётся для тех, кто хочет дочитать.

Жёсткий gear shift в скорости до первого aha — часть пользователей не любит wizard'ы вообще, и это их трек.

**Impact/effort:** High / Medium. Требует расщепления entry-путей в `OnboardingWizard.handleEnterTour`.

## 17. Privacy/trust ближе к началу (refinement #11)

**Проблема:** уточнение к #11. Старые ключи `onboarding.privacy.*` в `en.json:36` существуют с текстом про то, что записывается/не записывается — но не используются в v2 wizard (в самом `OnboardingWizard.tsx` нет ни одного упоминания privacy). То есть copy уже написан, но просто висит мёртвым.

**Паттерн:** для extension, который просит trust от браузера, privacy — не secondary tooltip, это **первый** вопрос пользователя. Место ему — в первые 30 секунд, не на 5-м экране.

**Изменения:**
- Компактный trust-block (2 строки + collapsible «что именно») на Hook или Problem screen. Переиспользовать уже существующие ключи `onboarding.privacy.recordedHeader` / `neverHeader` / body.
- Примеры позиционирования:
  - Под Hook-заголовком, мелким шрифтом: «Local-first. Мы видим меньше, чем ты думаешь. [Что именно]»
  - Или как chip-footer у Hook/Problem экранов.

**Impact/effort:** Medium / Low. Copy уже есть, нужна только верстка.

## 18. Complete только после реального aha event (strict refinement #13)

**Проблема:** усиление #13. И wizard-skip, и tour-skip сейчас пишут `phase: "done"` (`api/onboarding.ts:68` — `skipOnboarding`). Tour completion через CTA → `completeOnboarding` с `completedAt`. Но сам **tour** — это сценарий в изолированной «Trail tour» tree, которая удаляется при выходе. Это демонстрация, а не реальная активация.

**Изменения:**
- `completedAt` ставится **не** по факту прохождения тура, а по факту первого реального branch или revisit в **non-tour** tree.
- Добавить observer на `trees.active` (кроме tourTreeId): первый branch → `markActivated()` → пишет `completedAt`.
- Все три «skip» (wizard skip, tour skip, soft-CTA `[Maybe later]`) пишут только `seenWelcome` + `phase: "dismissed"`, но НЕ `completedAt`.
- CTA-полоска из #14 или Resume-chip из #13 продолжают показываться пока `!completedAt`.
- Плюс: появляется реальная activation-метрика («% пользователей, дошедших до первого branch в своей trail после install»), отдельно от «completed onboarding modal».

**Impact/effort:** High / Medium. Меняет семантику completion и добавляет observer, но даёт правильную метрику активации. Скорее всего требует мигрирующего чтения: старым пользователям с `completedAt` в storage не переписывать — только новых считать по-новому.

## 19. Tour: Guided demo + Try-on-my-browsing (два режима)

**Проблема:** текущий tour жёстко требует последовательности: Google → click result → Back → click another result → click abandoned node (`en.json:170`). Умно, но:
- Хрупко: предикаты в `tour-machine.ts` смотрят только на Google-URL-паттерн. Ломается на Яндексе, DuckDuckGo, incognito, если пользователь случайно пошёл не на Google.
- Cognitively expensive: пользователь делает 5 строго определённых действий вместо того, чтобы свободно исследовать.

**Изменения:**
- Ввести два входа с `[Let me feel it]` (или одного из CTA в #16):
  - **Guided demo** (default): текущий флоу, но с pre-seeded tour-tree — открывается не пустой Google, а **fixture-дерево** с уже 4 готовыми узлами (Google + 2 результата + back-return). Coach не ждёт действий, а ведёт пальцем по готовому примеру с подсветкой. Переход — один клик `[Next]`.
  - **Try on my browsing** (для тех кто хочет сразу): просто активирует capture на текущей вкладке, показывает маленький coach-hint «Покажи мне что-нибудь ветвистое» и советует сделать back + выбрать другую ссылку — но не блокирует и не ждёт предикатов. Через ~N узлов (напр. 4) триггерит celebration по факту.
- Tour-machine предикаты мягче: вместо «Google домен» — любой domain + 2 children + back-navigation detected.

**Impact/effort:** Medium-High / High. Это рефакторинг tour-machine. Но убирает хрупкость и уважает пользователя, который уже всё понял.

## 20. Celebration → первое настоящее дерево, а не auth-only CTA

**Проблема:** финальный `TourCommitments` ставит пользователя перед выбором `[Sign in]` / `[Maybe later]` — оба вызывают `finish()` (`cta/TourCommitments.tsx:22`). Оба варианта завершают onboarding и оставляют пользователя с пустым дашбордом trails. Если цель продукта шире чем auth conversion (а она шире), это слабый next step.

**Паттерн (видео):** CTA после aha должен звать в реальное использование, а не в форму.

**Изменения:**
- Перед soft-CTA добавить один короткий экран: «Open something you actually want to remember.» + кнопка `[Start my first real trail]` (активная — primary) + `[Skip for now]` (secondary).
- `[Start my first real trail]` → `disposeTourTree()` + открывает фокусно новую вкладку «New Tab» или оставляет текущую с coach-hint «следующее, что ты откроешь — станет твоим первым настоящим узлом».
- Sign-in как вторичный CTA — либо на следующем экране, либо в persistent полоске (#14), либо в существующем CTA после того как у пользователя есть хотя бы 1 trail.
- Semantically это встраивает #18 (complete-on-real-aha): сейчас после tour `completedAt` не ставится, ставится по первому реальному branch.

**Impact/effort:** Medium / Medium. Меняет последний шаг onboarding + завязан на #18.

## 21. Реальная RU локализация onboarding

**Проблема:** `ru.json:14-40` — `stepTitle`, `primary.letsGo/showMore/gotIt`, `welcome.title`, `welcome.body`, и большинство под-ключей онбординга **оставлены на английском**. По плану `onboarding-interactive.md:223` это было сознательное решение («Language: English only. ru.json mirrors en.json»). Для продукта, просящего доверия у русскоязычного пользователя в браузере — бьёт по ощущению законченности и тону.

**Изменения:**
- Пройтись по всему `onboarding.*` дереву в `ru.json` и перевести строки, которые сейчас просто скопированы с английского:
  - `stepTitle.*`, `primary.*`, `pickOne`, `welcome.*`, `privacy.*` (если #17 использует старые ключи)
  - Все новые ключи под `onboarding.v2.*` — `hook.*`, `problem.*`, `persona.*`, `solution.*.{title,body,imagine,chips.*}`, `features.*`, `tour.*`, `celebration.*`, `cta.*`.
- Тональность: warm, не shouty, как в английской версии. Избегать буквального перевода (`"Let's go"` ≠ `"Давай"`).
- Плюс — добавить `ru.json` в любой audit-скрипт, чтобы впредь не расходились.

**Impact/effort:** Medium / Low. Чистый copy-work, без архитектурных изменений. Но только **после** того, как copy в `en.json` стабилизируется — иначе два раза писать.

---

## Что **не** трогать

- Авто-удаление tour tree на finish — чистое решение.
- Confetti density в celebration — адекватная.
- Persona → tailored Solution-копи — хорошая база, просто расширить по пункту 2.
- Resume-механизм wizard'а через `wizardStep` + `phase === "wizard"` — работает, на нём стоит #13.

> Ранее в этом списке были «Tour-механика» и «Soft CTA с двумя кнопками» — но #19 и #20 эти решения пересматривают (tour хрупок на non-Google, soft CTA слаб как next step). Если #19/#20 не делать — старое решение остаётся рабочим.

## Приоритет

По impact/effort, от самого выгодного:

1. **#18 complete только после реального aha event** — правильная activation-метрика, пересматривает семантику completion
2. **#15 сократить wizard до 2–3 экранов** — самый прямой способ ускорить time-to-aha
3. **#17 privacy early + reuse existing copy** — снимает крупный барьер, copy уже написан, просто вернуть в UI
4. **#2 personalized mock-graph в SolutionScreen** — дешёво, сильный «это про меня» момент
5. **#16 «Try it» CTA с первого экрана** — альтернативный путь для нетерпеливых, дешёвый win
6. **#13 skip → resumable dismiss** — раскрывает уже сделанный resume-механизм
7. **#1 multi-select персона** — измеряется против baseline (Headspace кейс)
8. **#14 sticky CTA-полоска** — не терять отложенные activation-моменты
9. **#20 celebration → первый реальный trail** — сильный next step вместо auth-формы
10. **#4 sticky checklist (полноценный)** — расширение #14 с большим retention-impact
11. **#21 реальный RU перевод** — copy-work, делать после стабилизации en
12. **#10 celebration tagline** — почти бесплатно
13. **#12 outcome-first audit** — copy-pass, прицепом
14. **#3 founder note** — тёплый штрих
15. **#9 loading momentum** — polish
16. **#7 progressive education** — рефакторинг, требует осторожности
17. **#19 guided demo + try-on-browsing** — рефакторинг tour-machine, дорого
18. **#5 hook demo** — визуал, нужен качественный CSS/SVG
19. **#6 pre-permission** — если реально нужно
20. **#8 split sign-up** — требует правок в login-app

## Группировка по темам

Пункты сильно пересекаются — полезно смотреть блоками:

- **Time-to-aha** (#15, #16, #19, #2, #5) — сокращаем путь от «открыл» до «о, понял»
- **Activation vs dismiss** (#18, #13, #14, #4, #20) — правильно считать completion, не терять отложенные CTA
- **Trust / tone** (#17, #21, #12, #3) — copy-work, privacy, founder-touch, перевод
- **Polish** (#9, #10) — микрооптимизация existing UX
- **Persona deepening** (#1, #2, #10) — использовать персону сильнее
- **Out-of-flow** (#6, #8) — зависят от других поверхностей (permissions, login-app)

## Открытые вопросы

- Как измерять? Analytics events уже есть (`onboarding_persona_picked`, `onboarding_tour_branched`, `onboarding_tour_completed`). Для checklist (#4) нужно `quickstart_item_completed`, для multi-select (#1) — `onboarding_persona_picked` с массивом.
- Russian copy: сейчас по плану `ru.json` зеркалит `en.json`. Если будут добавляться персона-specific строки (#10, #2), сразу писать оба языка или держать плейсхолдер?
