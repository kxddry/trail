# Phase 3: UX Polish - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Users encounter branded, helpful UI for every error and loading state instead of raw Next.js defaults or blank screens. Covers: branded error pages (UX-01, UX-02), loading states (UX-03, UX-05), destructive action confirmations in extension (UX-04), extension context menu accessibility (UX-06), and page transition animations (UX-07).

</domain>

<decisions>
## Implementation Decisions

### Error pages (UX-01, UX-02)
- Minimalist style with animated TrailLogo — clean and professional, consistent with existing app aesthetic
- Tone and copy: Claude's discretion, matching existing app voice
- CTA buttons: Claude's discretion per error type (404 vs 500)

### Loading states (UX-03, UX-05)
- Skeleton loaders preferred over spinners — improve existing skeleton patterns on /trails, /settings
- Root loading (UX-03) should use branded TrailLogo loader instead of plain text
- Enhance existing pulse-animated skeletons where needed

### Destructive action confirmations (UX-04)
- Use shadcn AlertDialog component for confirmation dialogs in extension context menu
- Which actions need confirmation and dialog copy: Claude's discretion
- DeleteTreeConfirmModal already exists — align new confirmations with its pattern or replace with shadcn

### Extension accessibility (UX-06)
- Use shadcn components where they improve ARIA roles and keyboard navigation
- Specific ARIA implementation: Claude's discretion based on existing context menu structure

### Page transitions (UX-07)
- Use Motion library (v12, already installed) instead of CSS animations
- Transition style and intensity: Claude's discretion
- Respect existing `prefers-reduced-motion` media query pattern

### Claude's Discretion
- Error page copy and CTA choices per error type
- Which extension actions require confirmation before executing
- Exact skeleton layout improvements
- Motion transition style (fade, slide, etc.)
- ARIA role implementation details
- Whether to replace DeleteTreeConfirmModal with shadcn AlertDialog or keep both

</decisions>

<specifics>
## Specific Ideas

- Motion library should replace CSS animation patterns — not add a parallel system
- shadcn components can be used within the extension for confirmations (UX-04) and accessibility (UX-06), but full extension migration to shadcn is out of scope

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `TrailLogo.Animated` (packages/ui/src/components/TrailLoader.tsx) — branded animated loader, already used in root loading.tsx
- `Skeleton` component (packages/ui/src/components/Skeleton.tsx) — pulse animation with `bg-surface-high`
- `AlertDialog` (apps/account/components/ui/alert-dialog.tsx) — Radix-based with Tailwind animations
- `DeleteTreeConfirmModal` (extension/src/sidepanel/ui/components/DeleteTreeConfirmModal.tsx) — existing confirmation pattern
- Context menu system (extension/src/sidepanel/ui/components/ContextMenus.tsx) — full context menu with animations, keyboard nav, danger states

### Established Patterns
- CSS custom properties for theming (light/dark/system via `data-theme`)
- Tailwind CSS v4.2 + shared preset from packages/ui
- Radix UI primitives for accessible components in web app
- `prefers-reduced-motion` media query already handled for TrailLogo
- Skeleton loaders on /trails, /settings, /dashboard loading.tsx files

### Integration Points
- Error pages: `apps/account/app/error.tsx`, `apps/account/app/not-found.tsx`, `apps/account/app/(app)/not-found.tsx`
- Root loading: `apps/account/app/loading.tsx`
- Route loading: `apps/account/app/(app)/trails/loading.tsx`, `apps/account/app/(app)/settings/loading.tsx`
- Extension context menu: `extension/src/sidepanel/ui/components/ContextMenus.tsx`
- Motion library: v12.34.3 installed, minimal usage currently

</code_context>

<deferred>
## Deferred Ideas

- **Full extension migration to shadcn components** — refactor entire extension UI system to use shadcn/Radix primitives. Separate phase, not UX polish.

</deferred>

---

*Phase: 03-ux-polish*
*Context gathered: 2026-02-28*
