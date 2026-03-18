---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts
autonomous: false
requirements: [REND-01]

must_haves:
  truths:
    - "Node titles render correctly with BitmapText at all LOD levels"
    - "Node URLs render correctly with BitmapText when showUrls is enabled"
    - "Tab count badges render correctly with BitmapText and proper sizing"
    - "Text colors respond to theme changes, hover, selection, current/closed states"
    - "Text remains crisp at different zoom levels"
  artifacts:
    - path: "src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts"
      provides: "BitmapFont installation and BitmapText usage"
      contains: "BitmapText"
  key_links:
    - from: "GraphPixiRenderer.init()"
      to: "BitmapFont.install()"
      via: "Font pre-installation during renderer init"
      pattern: "BitmapFont\\.install"
    - from: "NodeVisual fields"
      to: "PIXI.BitmapText"
      via: "Replacement of PIXI.Text with PIXI.BitmapText"
      pattern: "new PIXI\\.BitmapText"
---

<objective>
Replace all PIXI.Text usage in NodeVisual with PIXI.BitmapText for GPU-accelerated text rendering.

Purpose: PIXI.Text rasterizes to a canvas texture on every style/content change, which is expensive when hundreds of nodes update text simultaneously (theme change, zoom, pan revealing new nodes). BitmapText uses pre-generated glyph atlases and renders via the GPU batch pipeline, eliminating per-node canvas rasterization.

Output: GraphPixiRenderer.ts with BitmapFont installation and all three Text instances (titleText, urlText, tabBadgeText) migrated to BitmapText.
</objective>

<execution_context>
@/Users/iv/.claude/get-shit-done/workflows/execute-plan.md
@/Users/iv/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts

<interfaces>
<!-- Key types and patterns the executor needs from the existing file -->

From GraphPixiRenderer.ts (lines 56-57):
```typescript
const TITLE_FONT_SIZE = 12;
const URL_FONT_SIZE = 10;
// Badge font size is inline: 9
```

From NodeVisual constructor (lines 184-188):
```typescript
private readonly titleText = new PIXI.Text({ text: '' });
private readonly urlText = new PIXI.Text({ text: '' });
private readonly tabBadgeText = new PIXI.Text({ text: '' });
```

From updateText (lines 504-511) - style mutations to replace:
```typescript
this.titleText.style.fontFamily = fontFamily;
this.titleText.style.fontWeight = this.fonts.weight;
this.titleText.style.fontSize = TITLE_FONT_SIZE;
this.titleText.style.fill = titleColor;
this.urlText.style.fontFamily = fontFamily;
this.urlText.style.fontWeight = '400';
this.urlText.style.fontSize = URL_FONT_SIZE;
this.urlText.style.fill = urlColor;
```

From updateBadges (lines 609-613) - badge text with measurement:
```typescript
this.tabBadgeText.text = badgeText;
this.tabBadgeText.style.fontSize = 9;
this.tabBadgeText.style.fill = theme.onPrimary;
this.tabBadgeText.style.fontWeight = '700';
const metrics = PIXI.CanvasTextMetrics.measureText(badgeText, this.tabBadgeText.style);
```

From resolution handling (lines 329-333):
```typescript
if (this.state.textResolution !== textResolution) {
  this.titleText.resolution = textResolution;
  this.urlText.resolution = textResolution;
  this.tabBadgeText.resolution = textResolution;
}
```

Renderer fontFamily default (line 825):
```typescript
private fontFamily = '"Inter", system-ui, sans-serif';
```

Pixi v8 BitmapFont.install API:
```typescript
BitmapFont.install({
  name: string,
  style: TextStyleOptions,
  chars?: string | (string | string[])[],
  resolution?: number,
  padding?: number,
  skipKerning?: boolean,
  dynamicFill?: boolean,
});
```

Pixi v8 BitmapText constructor:
```typescript
new PIXI.BitmapText({ text: string, style: { fontFamily: string, fontSize: number, fill: number } });
```

Pixi v8 BitmapFontManager.measureText:
```typescript
BitmapFontManager.measureText(text: string, style: TextStyle, trimEnd?: boolean): { width, height, scale, offsetY };
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Install BitmapFonts and migrate NodeVisual text fields to BitmapText</name>
  <files>src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts</files>
  <action>
**1. Add BitmapFont imports and font name constants (top of file):**

Add to imports: `BitmapFontManager` from pixi.js (already importing `* as PIXI`, so access via `PIXI.BitmapFontManager` or import directly). Remove the `TextStyleFontWeight` type import (no longer needed).

Add constants near the font size constants:
```typescript
const BITMAP_FONT_TITLE = 'TrailTitle';   // 500 weight, size 12
const BITMAP_FONT_URL = 'TrailUrl';       // 400 weight, size 10
const BITMAP_FONT_BADGE = 'TrailBadge';   // 700 weight, size 9
```

**2. Install BitmapFonts during renderer init:**

In `GraphPixiRenderer.init()`, AFTER `this.isReady = true` and BEFORE `this.refreshTheme()`, install three BitmapFonts. Use `dynamicFill: true` so colors can be applied via tint at runtime (fill in style must be white `0xFFFFFF`):

```typescript
const dpr = window.devicePixelRatio || 1;
const fontRes = Math.max(1, Math.ceil(dpr));

PIXI.BitmapFont.install({
  name: BITMAP_FONT_TITLE,
  style: { fontFamily: this.fontFamily, fontSize: TITLE_FONT_SIZE, fontWeight: '500', fill: 0xFFFFFF },
  chars: PIXI.BitmapFontManager.ASCII,
  resolution: fontRes,
  dynamicFill: true,
});

PIXI.BitmapFont.install({
  name: BITMAP_FONT_URL,
  style: { fontFamily: this.fontFamily, fontSize: URL_FONT_SIZE, fontWeight: '400', fill: 0xFFFFFF },
  chars: PIXI.BitmapFontManager.ASCII,
  resolution: fontRes,
  dynamicFill: true,
});

PIXI.BitmapFont.install({
  name: BITMAP_FONT_BADGE,
  style: { fontFamily: this.fontFamily, fontSize: 9, fontWeight: '700', fill: 0xFFFFFF },
  chars: '0123456789x ',
  resolution: fontRes,
  dynamicFill: true,
});
```

Use ASCII charset for title/url (covers all printable ASCII including punctuation, which is sufficient for truncated display titles and URLs). Badge only needs digits + "x" + space.

**3. Add font reinstallation on theme refresh:**

In `refreshTheme()`, after updating `this.fontFamily`, reinstall the BitmapFonts with the new fontFamily. First uninstall old ones, then reinstall:

```typescript
// After this.fontFamily = style.fontFamily || this.fontFamily;
if (this.isReady) {
  this.reinstallBitmapFonts();
}
```

Add a private method `reinstallBitmapFonts()`:
```typescript
private reinstallBitmapFonts() {
  const fontRes = Math.max(1, Math.ceil(window.devicePixelRatio || 1));
  PIXI.BitmapFont.uninstall(BITMAP_FONT_TITLE);
  PIXI.BitmapFont.uninstall(BITMAP_FONT_URL);
  PIXI.BitmapFont.uninstall(BITMAP_FONT_BADGE);
  PIXI.BitmapFont.install({
    name: BITMAP_FONT_TITLE,
    style: { fontFamily: this.fontFamily, fontSize: TITLE_FONT_SIZE, fontWeight: '500', fill: 0xFFFFFF },
    chars: PIXI.BitmapFontManager.ASCII,
    resolution: fontRes,
    dynamicFill: true,
  });
  PIXI.BitmapFont.install({
    name: BITMAP_FONT_URL,
    style: { fontFamily: this.fontFamily, fontSize: URL_FONT_SIZE, fontWeight: '400', fill: 0xFFFFFF },
    chars: PIXI.BitmapFontManager.ASCII,
    resolution: fontRes,
    dynamicFill: true,
  });
  PIXI.BitmapFont.install({
    name: BITMAP_FONT_BADGE,
    style: { fontFamily: this.fontFamily, fontSize: 9, fontWeight: '700', fill: 0xFFFFFF },
    chars: '0123456789x ',
    resolution: fontRes,
    dynamicFill: true,
  });
}
```

**4. Migrate NodeVisual text fields:**

Replace the three field declarations:
```typescript
// OLD:
private readonly titleText = new PIXI.Text({ text: '' });
private readonly urlText = new PIXI.Text({ text: '' });
private readonly tabBadgeText = new PIXI.Text({ text: '' });

// NEW:
private readonly titleText = new PIXI.BitmapText({ text: '', style: { fontFamily: BITMAP_FONT_TITLE, fontSize: TITLE_FONT_SIZE } });
private readonly urlText = new PIXI.BitmapText({ text: '', style: { fontFamily: BITMAP_FONT_URL, fontSize: URL_FONT_SIZE } });
private readonly tabBadgeText = new PIXI.BitmapText({ text: '', style: { fontFamily: BITMAP_FONT_BADGE, fontSize: 9 } });
```

Remove the `fonts` field and its usage in the constructor (`this.fonts = { base: fontFamily, weight: '500' };`). The font family/weight is now baked into the BitmapFont name.

**5. Update `updateText()` method:**

Replace the style mutation block (lines 504-511) with fill-only updates using `style.fill`:
```typescript
this.titleText.style.fill = titleColor;
this.urlText.style.fill = urlColor;
```

Remove these lines (fontFamily, fontWeight, fontSize are baked into the BitmapFont):
- `this.titleText.style.fontFamily = fontFamily;`
- `this.titleText.style.fontWeight = this.fonts.weight;`
- `this.titleText.style.fontSize = TITLE_FONT_SIZE;`
- `this.urlText.style.fontFamily = fontFamily;`
- `this.urlText.style.fontWeight = '400';`
- `this.urlText.style.fontSize = URL_FONT_SIZE;`

Remove the `fontFamily` parameter from `updateText()` signature (no longer needed). Update the call site in `update()` to remove the fontFamily argument.

**6. Update `updateBadges()` method:**

Replace the badge text style mutations:
```typescript
// OLD:
this.tabBadgeText.style.fontSize = 9;
this.tabBadgeText.style.fill = theme.onPrimary;
this.tabBadgeText.style.fontWeight = '700';
const metrics = PIXI.CanvasTextMetrics.measureText(badgeText, this.tabBadgeText.style);

// NEW:
this.tabBadgeText.style.fill = theme.onPrimary;
const metrics = PIXI.BitmapFontManager.measureText(badgeText, this.tabBadgeText.style);
```

The `PIXI.BitmapFontManager.measureText` returns `{ width, height, scale, offsetY }`. Use `metrics.width` and `metrics.height` the same way as before for badge sizing.

**7. Remove per-instance resolution management:**

Delete the resolution block in `update()` (lines 329-333):
```typescript
// DELETE THIS BLOCK -- BitmapText resolution is managed by the BitmapFont, not per-instance
if (this.state.textResolution !== textResolution) {
  this.titleText.resolution = textResolution;
  this.urlText.resolution = textResolution;
  this.tabBadgeText.resolution = textResolution;
}
```

Remove `textResolution` from the `NodeVisualState` type and from the state object initialization. Remove the `textResolution` parameter from the `update()` method signature. Remove `textResolution` from `needsTextUpdate` condition. Update all call sites in `GraphPixiRenderer` that pass `this.textResolution` to `visual.update()` -- remove that argument.

Remove the `syncTextResolution()` method and its calls (in `init`, `syncResolution`, `resizeToHost`, `setView`). Remove the `private textResolution = 1;` field from `GraphPixiRenderer`.

**8. Remove unused import:**

Remove `import type { TextStyleFontWeight } from 'pixi.js';` -- no longer used after removing the `fonts` field.

**9. Clean up needsTextUpdate condition:**

Since `textResolution` is removed, simplify:
```typescript
// OLD:
const needsTextUpdate = themeChanged || this.state.textKey !== textKey || openProgressChanged || this.state.textResolution !== textResolution;

// NEW:
const needsTextUpdate = themeChanged || this.state.textKey !== textKey || openProgressChanged;
```
  </action>
  <verify>
    <automated>cd /Users/iv/dev/trail/extension && pnpm typecheck:ui 2>&1 | tail -20</automated>
  </verify>
  <done>
    - All three PIXI.Text instances replaced with PIXI.BitmapText
    - BitmapFont.install called during init for three font variants (title 12/500, url 10/400, badge 9/700)
    - dynamicFill: true enables runtime color changes via style.fill
    - Per-instance resolution management removed (handled by BitmapFont resolution)
    - CanvasTextMetrics.measureText replaced with BitmapFontManager.measureText for badge sizing
    - Font reinstallation on theme refresh handles fontFamily changes
    - TypeScript compiles cleanly
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Visual verification of BitmapText rendering</name>
  <files>src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts</files>
  <action>Human verifies BitmapText rendering quality and correctness in the running extension.</action>
  <verify>Human visual inspection confirms text renders correctly.</verify>
  <done>All text in graph nodes renders correctly with no visual regression.</done>
  <what-built>Migrated all PIXI.Text to PIXI.BitmapText in the graph renderer for GPU-accelerated text rendering.</what-built>
  <how-to-verify>
    1. Run `pnpm dev` and open the extension sidepanel
    2. Verify node titles render correctly (readable, properly positioned)
    3. Verify URLs show below titles when the display option is enabled
    4. Verify tab count badges (e.g. "2x") render with correct sizing and position
    5. Expand/collapse nodes -- verify text appears/disappears correctly
    6. Zoom in and out -- verify text remains crisp (not blurry)
    7. Switch between light and dark themes -- verify text colors update
    8. Hover over nodes -- verify hover highlight text doesn't break
    9. Search for a node -- verify search match/focused text colors work
    10. Compare overall text rendering quality with main branch (should look identical or better)
  </how-to-verify>
  <resume-signal>Type "approved" or describe any visual issues</resume-signal>
</task>

</tasks>

<verification>
- `pnpm typecheck:ui` passes with no errors
- No PIXI.Text references remain in NodeVisual (only PIXI.BitmapText)
- No CanvasTextMetrics references remain
- No TextStyleFontWeight import remains
- Visual verification: text renders at correct sizes, colors, and positions
</verification>

<success_criteria>
- All node text renders via BitmapText (GPU batched) instead of Text (canvas rasterized)
- Text colors respond correctly to all state changes (theme, hover, selection, current, closed)
- Badge sizing uses BitmapFontManager.measureText instead of CanvasTextMetrics
- No regression in text appearance or positioning
- TypeScript compiles cleanly
</success_criteria>

<output>
After completion, create `.planning/quick/260318-vyz-migrate-pixi-text-to-bitmaptext-for-perf/260318-vyz-SUMMARY.md`
</output>
