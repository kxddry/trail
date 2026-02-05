# Settings Sidebar Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the settings sidebar’s narrow-width top bar with a shadcn-style hamburger + overlay while preserving existing styling and avoiding Tailwind preflight regressions.

**Architecture:** Add Tailwind (utilities only) to the extension UI, provide shadcn component structure under `components/ui`, and integrate the provided `Sidebar` component into `SettingsPopover` without changing the existing button markup/styles. Use a small helper in `sidebar-utils.ts` for testable animation sizing logic.

**Tech Stack:** React 18, Vite, Tailwind CSS 4 (no preflight), @motion/react, lucide-react, TypeScript.

---

### Task 1: Add failing test for sidebar sizing helper

**Files:**
- Modify: `extension/tests/basic.test.ts`
- Modify: `extension/src/sidepanel/ui/components/ui/sidebar-utils.ts`

**Step 1: Write the failing test**

Add a unit test for a new helper `getSidebarWidth(open, animate)`.

```ts
import { getSidebarWidth } from '../src/sidepanel/ui/components/ui/sidebar-utils';

test('getSidebarWidth returns expanded width when open and animate', () => {
  expect(getSidebarWidth(true, true)).toBe('300px');
});

test('getSidebarWidth returns collapsed width when closed and animate', () => {
  expect(getSidebarWidth(false, true)).toBe('60px');
});

test('getSidebarWidth returns expanded width when animation disabled', () => {
  expect(getSidebarWidth(false, false)).toBe('300px');
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C extension test`

Expected: FAIL with “getSidebarWidth is not defined”.

**Step 3: Write minimal implementation**

Add `getSidebarWidth` to `extension/src/sidepanel/ui/components/ui/sidebar-utils.ts`.

```ts
export function getSidebarWidth(open: boolean, animate: boolean): '300px' | '60px' {
  if (!animate) return '300px';
  return open ? '300px' : '60px';
}
```

**Step 4: Run tests to verify they pass**

Run: `pnpm -C extension test`

Expected: PASS.

**Step 5: Commit**

```bash
git add extension/tests/basic.test.ts extension/src/sidepanel/ui/components/ui/sidebar-utils.ts
git commit -m "Add sidebar width helper"
```

---

### Task 2: Add Tailwind + shadcn structure (no preflight)

**Files:**
- Create: `extension/tailwind.config.cjs`
- Create: `extension/components.json`
- Create: `extension/src/sidepanel/ui/tailwind.css`
- Modify: `extension/src/sidepanel/ui/sidepanel.css`
- Modify: `extension/vite.config.mts`
- Modify: `extension/tsconfig.app.json`
- Create: `extension/src/sidepanel/ui/lib/utils.ts`

**Step 1: Tailwind config (disable preflight)**

```js
module.exports = {
  content: ["./src/sidepanel/ui/**/*.{ts,tsx,html}"],
  darkMode: ["class", "[data-theme='dark']"],
  corePlugins: { preflight: false },
  theme: { extend: {} },
  plugins: [],
};
```

**Step 2: shadcn config**

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.cjs",
    "css": "src/sidepanel/ui/tailwind.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

**Step 3: Tailwind entry**

`tailwind.css` should include utilities and components only (no base):

```css
@tailwind components;
@tailwind utilities;
```

**Step 4: Import Tailwind first**

Add `@import './tailwind.css';` as the first line in `sidepanel.css`.

**Step 5: Alias setup**

Add `resolve.alias` for `@` in `vite.config.mts` pointing to `src/sidepanel/ui`.

Update `tsconfig.app.json` with:

```json
"baseUrl": ".",
"paths": { "@/*": ["src/sidepanel/ui/*"] }
```

**Step 6: `cn` util**

```ts
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: Array<string | undefined | null | false>) {
  return twMerge(clsx(inputs));
}
```

**Step 7: Commit**

```bash
git add extension/tailwind.config.cjs extension/components.json extension/src/sidepanel/ui/tailwind.css extension/src/sidepanel/ui/sidepanel.css extension/vite.config.mts extension/tsconfig.app.json extension/src/sidepanel/ui/lib/utils.ts
git commit -m "Add Tailwind utilities for extension UI"
```

---

### Task 3: Add Sidebar component files

**Files:**
- Create: `extension/src/sidepanel/ui/components/ui/sidebar.tsx`
- Create: `extension/src/sidepanel/ui/components/ui/demo.tsx`

**Step 1: Add `sidebar.tsx`**

Copy provided component and adapt:
- Use `a` for links (no Next.js `Link`).
- Use `img` for avatar in demo.
- Use `cn` from `@/lib/utils` and `getSidebarLabelState`, `getSidebarWidth` from `sidebar-utils`.

**Step 2: Add `demo.tsx`**

Use an Unsplash image URL for the avatar.

**Step 3: Commit**

```bash
git add extension/src/sidepanel/ui/components/ui/sidebar.tsx extension/src/sidepanel/ui/components/ui/demo.tsx
git commit -m "Add shadcn sidebar component"
```

---

### Task 4: Integrate Sidebar into SettingsPopover

**Files:**
- Modify: `extension/src/sidepanel/ui/components/SettingsPopover.tsx`

**Step 1: Add sidebar state + imports**

```ts
import { Sidebar, SidebarBody } from './ui/sidebar';
```

Add `const [sidebarOpen, setSidebarOpen] = useState(false);`

**Step 2: Replace sidebar markup**

Wrap the existing `<nav className="settings-sidebar">` with:

```tsx
<Sidebar open={sidebarOpen} setOpen={setSidebarOpen} animate={false}>
  <SidebarBody className="settings-sidebar">
    ...existing nav buttons...
  </SidebarBody>
</Sidebar>
```

On nav button click, also call `setSidebarOpen(false)` to close the overlay on mobile.

**Step 3: Commit**

```bash
git add extension/src/sidepanel/ui/components/SettingsPopover.tsx
git commit -m "Use Sidebar component in settings"
```

---

### Task 5: Update settings CSS for new responsive behavior

**Files:**
- Modify: `extension/src/sidepanel/ui/styles/settings-popover.css`

**Step 1: Align breakpoint to 768px**

Change `@media (max-width: 780px)` to `@media (max-width: 768px)`.

**Step 2: Remove horizontal sidebar rules**

Delete rules that turn `.settings-sidebar` into a horizontal scroller at small widths (no longer needed).

**Step 3: Ensure modal body stacks on mobile**

Keep `flex-direction: column` for `.settings-modal-body` at small widths so the mobile sidebar header sits above the panel.

**Step 4: Commit**

```bash
git add extension/src/sidepanel/ui/styles/settings-popover.css
git commit -m "Adjust settings sidebar responsive styles"
```

---

### Task 6: Verification

**Step 1: Run tests**

Run: `pnpm -C extension test`

Expected: PASS.

**Step 2: Build extension**

Run: `make extension`

Expected: Build succeeds and assets emit to `dist/sidepanel`.

---

Plan complete and saved to `docs/plans/2026-02-02-settings-sidebar-implementation.md`.

Two execution options:

1. Subagent-Driven (this session)
2. Parallel Session (separate)

Which approach?
