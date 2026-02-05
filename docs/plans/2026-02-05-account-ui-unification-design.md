# Account UI Unification Design

Date: 2026-02-05

## Summary
Unify the UI layer for `apps/account` using a single source of truth in `packages/ui`. The goal is maximum reuse with minimal duplication, while preserving existing UX and business logic. We will keep Tailwind + Radix and standardize tokens to the marketing look-and-feel, allowing small visual shifts for consistency.

## Goals
- Single UI source of truth in `packages/ui`.
- Maximum component reuse and minimum repeated styling.
- Preserve current UX and data flow in `apps/account`.
- Allow small visual changes for consistency.

## Non-goals
- No UX flow redesign.
- No data/API changes.
- No new bespoke CSS per page.

## Architecture & Scope
- `packages/ui/src/components`: base UI primitives + reusable compositions.
- `packages/ui/src/utils`: shared class helpers and variants.
- `packages/ui/src/tailwind-preset.ts`: tokens and theme values.
- `apps/account`: consumes `@trail/ui` components and tokens only.

Scope: migrate all pages under `apps/account/app/(app)` in one pass without changing logic.

## Component Strategy
Create or extend the following core components to cover account UI patterns:
- Form elements: `Input`, `Textarea`, `Select`, `Checkbox`, `Radio`, `Switch`, `Label`, `Field`, `FormMessage`.
- Layout: `Card`, `SectionHeader`, `PageHeader`, `Tabs`.
- Data: `Table`, `Badge`, `Pill`.
- Feedback: `Toast`, `Callout/Banner`, `InlineError`, `EmptyState`, `Skeleton`.
- Overlays: `Dialog/Modal`, `Drawer`, `Dropdown`, `Tooltip`.

Use CVA for `variants` (`size`, `variant`, `tone`, `state`, `align`). Use Radix primitives for interactive elements to reduce behavioral bugs and improve accessibility.

## Tokens
Adopt marketing tokens in `tailwind-preset` as the canonical palette and typography. Use token classes (`bg-surface`, `text-ink`, `border-stroke`, `shadow-elev-1`) instead of ad-hoc classes. Page-level utilities are allowed only for layout (grid, gaps, max-width), not for color or typography.

## Migration Flow
1. Inventory common patterns in `apps/account`.
2. Implement/extend components in `packages/ui` to cover those patterns.
3. Replace UI on all account pages with `@trail/ui` components, preserving logic and data flow.

## Data Flow & Error Handling
No change to existing data fetching or mutations. Standardize UI states:
- Loading: `Skeleton`.
- Empty: `EmptyState`.
- Errors: `Callout/Banner` and `InlineError` for form fields.

## Testing & Rollout
Minimum checks:
- `pnpm --filter @trail/account typecheck`
- `pnpm --filter @trail/account lint` (if configured)
- `pnpm --filter @trail/account test` (if present)

Manual smoke-check for dashboard, settings, billing, sessions, activity, getting-started, extension.

## Risks & Mitigations
- Risk: drift between account and marketing styles.
  - Mitigation: use shared tokens and ban local color/typography overrides.
- Risk: component gaps causing one-off styling.
  - Mitigation: expand `packages/ui` before modifying pages.

## Next Steps
- Create implementation plan.
- Execute component-first migration in a dedicated branch.
