# Graph Dot Grid Motion & Zoom Sync

## Summary
Make the dotted background in the graph view move and scale in sync with the graph’s pan/zoom. The dot grid should feel anchored to the same world coordinates as nodes, similar to Miro.

## Goals
- Dotted grid moves with pan.
- Dotted grid scales with zoom.
- Behavior is smooth and stable across resize and reset.
- Changes are localized to the graph view only.

## Non‑Goals
- No changes to Pixi renderer or node rendering.
- No animation unrelated to user pan/zoom.
- No changes to the rest of the sidepanel background.

## Architecture
- **CSS** (`extension/src/sidepanel/ui/styles/graph.css`):
  - Introduce CSS variables for grid size, dot size, and offsets.
  - `::before` radial‑gradient uses the variables for `background-size` and `background-position`.
- **React** (`extension/src/sidepanel/ui/components/graph/GraphCanvas.tsx`):
  - Derive CSS variable values from `ViewState` (`translateX`, `translateY`, `scale`).
  - Apply them on the `.graph-wrapper` element via `style.setProperty`.
  - Update on all view changes (pan, zoom, fit, reset).

## Data Flow
- `ViewState` is the source of truth.
- Every view update calls `applyGridTransform(view)`.
- CSS variables are updated on the wrapper element only.

## Behavior Details
- Base cell size: `20px`.
- Grid scale: `gridSize = baseSize * scale`.
- Dot radius: `dotSize = 1.5px * max(scale, 0.5)` (prevents vanishing dots on far zoom).
- Offsets: `translateX % gridSize`, `translateY % gridSize` to keep values bounded.
- Optional clamp of `gridSize` to avoid extreme noise or sparse dots.

## Error Handling / Edge Cases
- If wrapper ref is missing, no-op.
- If `gridSize` is invalid or too small, clamp to safe min/max.
- Resizes are handled automatically since the pattern repeats.

## Testing
- Manual:
  - Pan (hand tool): dots move with the canvas.
  - Zoom (wheel/controls): dots scale with nodes.
  - Fit/Reset view: dots remain stable with no visible jump.

## Rollout
- No feature flag required; minimal isolated change.
