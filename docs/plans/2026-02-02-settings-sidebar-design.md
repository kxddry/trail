# Settings Sidebar Mobile Overlay Design

## Goal
Replace the current narrow-width settings sidebar behavior (which collapses into a horizontal top bar) with a Miro-style mobile sidebar experience: a compact header with a hamburger button that opens a full-height overlay menu. Preserve all existing settings content, theme picker behavior, and graph rendering.

## Scope
- Settings modal only: sidebar navigation and its responsive behavior.
- No changes to settings content panels, theme picker logic, or graph rendering.
- Introduce a shadcn-style `Sidebar` component to handle mobile overlay behavior.

## Constraints
- Extension UI is a Vite + React app with existing CSS-driven styling.
- Use the provided component structure and `framer-motion` for animation.
- Avoid Tailwind preflight to prevent global style regressions in theme picker and graph.
- No Next.js APIs; adapt `Link`/`Image` usage to standard anchor/image elements.

## Approach
1. Add Tailwind configuration scoped to the extension UI and import Tailwind layers via a new `tailwind.css` file. Omit preflight (`@tailwind base`) or explicitly disable it in `tailwind.config.cjs`.
2. Add shadcn-compatible structure under `extension/src/sidepanel/ui/components/ui` and provide a `cn` utility at `extension/src/sidepanel/ui/lib/utils.ts`.
3. Copy the sidebar component into `components/ui/sidebar.tsx` and the demo into `components/ui/demo.tsx`, adapting imports to the extension environment.
4. Integrate `Sidebar`, `SidebarBody`, and `MobileSidebar` into `SettingsPopover.tsx`. Keep the existing button-based navigation markup and styles to preserve the visual system. Close the mobile overlay after selecting a section.
5. Update `settings-popover.css` to remove the “horizontal top bar” behavior at small widths and align breakpoints with Tailwind `md` (768px).

## Data Flow
- `SettingsPopover` owns `sidebarOpen` state.
- Desktop: sidebar stays visible; state toggles on hover only if `animate` is enabled.
- Mobile: hamburger button toggles overlay. Selecting a section sets `activeSection` and closes the overlay.

## Risks and Mitigations
- **Global CSS regressions from Tailwind preflight**: mitigate by disabling preflight or omitting `@tailwind base`.
- **Visual drift from component defaults**: mitigate by relying on existing CSS classes (e.g., `settings-sidebar`, `settings-nav-item`) to override Tailwind defaults.

## Testing
- Add a small unit test for any new helper logic used by the sidebar (e.g., width/label state helpers).
- Run `pnpm -C extension test` and `make extension` to confirm extension build integrity.
