# Trail Extension MVP Rewrite — 2026-04-12

## What happened

Stripped the Trail extension from ~47K LOC to ~15K LOC. Replaced Pixi.js graph with React Flow + elkjs. Removed all cloud features. Rewrote the hub as a settings page.

## Commit

`6b6d1f1e` on `dev` — 200 files changed, +1,937 / -32,459 lines.

## What was removed

- **Pixi.js graph** (~13K LOC) — WebGL renderer, LOD system, spatial index, deferred hydration, quality policy, 3 custom layout algorithms
- **Spotlight search** — full-text search with DSL parser, scoring, live index, content overlay, graph preview
- **Auth/OAuth** — orchestrator, token refresh, session management, account keeper, auth policy
- **Sync engine** — cloud push/pull, dirty tracker, migration
- **Account/Billing** — subscription, plans, billing portal, onboarding
- **UI surfaces**: Fullview editor, NewTab page, Spotlight content UI, Spotlight graph, Offscreen graph
- **Dependencies**: pixi.js, recharts

## What was built

### React Flow graph (`src/features/graph/`)
- `types.ts` — TrailNodeData, TrailNode, TrailEdge, TrailGraphProps
- `transforms.ts` — treeToNodes, treeToEdges (pure functions)
- `layout.ts` + `elk-graph.ts` — elkjs layout for all 3 modes
- `components/TrailGraph.tsx` — ReactFlow wrapper with pan/zoom/pinch
- `components/TrailNode.tsx` — shadcn-styled node (favicon, title, URL, tab count, collapse badge)
- `components/GraphControls.tsx` — zoom + layout mode toggle
- `hooks/useGraphLayout.ts` — async layout computation with race condition handling

### elkjs layout modes
| Mode | Algorithm | Direction |
|------|-----------|-----------|
| Tree | `org.eclipse.elk.mrtree` | DOWN |
| Mindmap | `org.eclipse.elk.mrtree` | RIGHT |
| Radial | `org.eclipse.elk.radial` | center-out |

### Settings page (`src/apps/settings/`)
- `SettingsApp.tsx` — sidebar nav (Trees, Appearance, Behavior)
- `TreesPage.tsx` — tree list + CRUD (new, open, rename, archive, delete, export)
- `AppearancePage.tsx` — layout mode, density, truncation, display toggles
- `BehaviorPage.tsx` — shortcuts, confirm new tree, keep tabs, adaptive perf

### Tests
- 14 graph layout tests (transforms + elkjs integration)
- All 17 tests pass (basic, graph-layout, architecture-boundaries, rpc-schema)

## Decisions made

1. **React Flow over Pixi.js** — user wanted it, despite Pixi.js being more performant. DOM-based nodes enable shadcn styling directly inside nodes.
2. **elkjs for all 3 layouts** — covers tree, mindmap, and radial natively. No custom layout math.
3. **No code extracted from Pixi.js** — clean break, git history preserves old code.
4. **Local-only** — all cloud features removed. Extension stores everything in IndexedDB.
5. **Settings page replaces Hub** — entrypoint renamed from `hub/` to `settings/`, URL is `settings.html`.

## Known issues / follow-up

- Edges sometimes don't render (React Flow handle sizing)
- Node design is functional but basic — needs polish
- Double-click to collapse is not discoverable — needs a visible toggle
- No search (Spotlight removed) — will need a simpler replacement
- No import UI yet on settings page (API exists, UI doesn't)
- Some shadcn components have pre-existing `exactOptionalPropertyTypes` type errors
- `proOptions={{ hideAttribution: true }}` may need React Flow Pro license
- Old floating controls (pinned dropdown, tree dropdown) still use pre-shadcn design

## Code review findings (fixed)

- CRITICAL: `hsl(var(--border))` on oklch variables → fixed to `var(--border)`
- HIGH: dead `onNodeDelete` prop, unused `isLayouting` state, stale closure in useSettings
- MEDIUM: `space-y-*` → `flex flex-col gap-*`, missing SelectGroup, swallowed errors, static vs dynamic import

## Architecture after rewrite

```
Entry points:  sidepanel.html + settings.html + background.js + content.js
Graph:         @xyflow/react + elkjs
UI:            shadcn/ui + Tailwind v4
State:         Zustand (sidepanel) + hooks (settings)
Storage:       IndexedDB (local only)
Build:         WXT + Vite, 3.43 MB total
```
