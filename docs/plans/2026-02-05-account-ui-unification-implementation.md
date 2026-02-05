# Account UI Unification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Unify all `apps/account` UI to `@trail/ui` (Radix + Tailwind) with minimal UX change and maximum reuse.

**Architecture:** Centralize primitives and reusable patterns in `packages/ui`, then replace local UI usage across account pages with those components. Preserve data/logic and only change the UI layer. Page-level layout utilities are allowed; colors/typography come from tokens.

**Tech Stack:** Next.js 16, React 19, Tailwind 4, Radix UI, CVA, Vitest + Testing Library.

---

### Task 1: Unify Button API in `@trail/ui`

**Files:**
- Modify: `packages/ui/src/components/Button.tsx`
- Modify: `packages/ui/src/index.ts`
- Create: `apps/account/components/ui/__tests__/button-unification.test.tsx`

**Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { Button } from "@trail/ui";

describe("Button", () => {
  it("renders variants and sizes", () => {
    render(
      <div>
        <Button variant="primary">Primary</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="subtle">Subtle</Button>
        <Button size="sm">Small</Button>
        <Button size="lg">Large</Button>
      </div>
    );

    expect(screen.getByText("Primary")).toHaveClass("bg-cta");
    expect(screen.getByText("Outline")).toHaveClass("border");
    expect(screen.getByText("Ghost")).toHaveClass("bg-transparent");
    expect(screen.getByText("Subtle")).toHaveClass("bg-surface");
    expect(screen.getByText("Small")).toHaveClass("h-9");
    expect(screen.getByText("Large")).toHaveClass("h-12");
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/button-unification.test.tsx`
Expected: FAIL because `Button` does not support `subtle` variant or classes do not match.

**Step 3: Write minimal implementation**

Update `packages/ui/src/components/Button.tsx` to:
- Support variants: `primary`, `outline`, `ghost`, `subtle`.
- Align classes with account tokens (`bg-cta`, `bg-surface`, `border-border`, `text-ink`).
- Keep `AsChild` support.

Update `packages/ui/src/index.ts` if needed.

**Step 4: Run test to verify it passes**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/button-unification.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add packages/ui/src/components/Button.tsx packages/ui/src/index.ts apps/account/components/ui/__tests__/button-unification.test.tsx
git commit -m "Unify button variants in UI kit"
```

---

### Task 2: Add core form primitives in `@trail/ui`

**Files:**
- Create: `packages/ui/src/components/Input.tsx`
- Create: `packages/ui/src/components/Textarea.tsx`
- Create: `packages/ui/src/components/Label.tsx`
- Create: `packages/ui/src/components/Field.tsx`
- Create: `packages/ui/src/components/FormMessage.tsx`
- Modify: `packages/ui/src/index.ts`
- Create: `apps/account/components/ui/__tests__/form-controls.test.tsx`

**Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { Field, Input, Label, FormMessage, Textarea } from "@trail/ui";

describe("Form controls", () => {
  it("wires label and input", () => {
    render(
      <Field>
        <Label htmlFor="email">Email</Label>
        <Input id="email" placeholder="name@trail.dev" />
        <FormMessage>Required</FormMessage>
      </Field>
    );

    expect(screen.getByText("Email")).toHaveAttribute("for", "email");
    expect(screen.getByPlaceholderText("name@trail.dev")).toBeInTheDocument();
    expect(screen.getByText("Required")).toBeInTheDocument();
  });

  it("renders textarea", () => {
    render(<Textarea placeholder="Notes" />);
    expect(screen.getByPlaceholderText("Notes")).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/form-controls.test.tsx`
Expected: FAIL because components are missing.

**Step 3: Write minimal implementation**

Implement simple styled components in `packages/ui/src/components/*` using token classes and focus styles.

**Step 4: Run test to verify it passes**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/form-controls.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add packages/ui/src/components/Input.tsx packages/ui/src/components/Textarea.tsx packages/ui/src/components/Label.tsx packages/ui/src/components/Field.tsx packages/ui/src/components/FormMessage.tsx packages/ui/src/index.ts apps/account/components/ui/__tests__/form-controls.test.tsx
git commit -m "Add form primitives to UI kit"
```

---

### Task 3: Add table and badge primitives in `@trail/ui`

**Files:**
- Create: `packages/ui/src/components/Table.tsx`
- Create: `packages/ui/src/components/Badge.tsx`
- Modify: `packages/ui/src/index.ts`
- Create: `apps/account/components/ui/__tests__/table-and-badge.test.tsx`

**Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { Table, Badge } from "@trail/ui";

describe("Table + Badge", () => {
  it("renders table structure", () => {
    render(
      <Table>
        <Table.Head>
          <Table.Row>
            <Table.HeaderCell>Session</Table.HeaderCell>
          </Table.Row>
        </Table.Head>
        <Table.Body>
          <Table.Row>
            <Table.Cell>Alpha</Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
    );

    expect(screen.getByText("Session")).toBeInTheDocument();
    expect(screen.getByText("Alpha")).toBeInTheDocument();
  });

  it("renders badge", () => {
    render(<Badge tone="success">Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/table-and-badge.test.tsx`
Expected: FAIL because components are missing.

**Step 3: Write minimal implementation**

Implement `Table` with `Table.Head`, `Table.Body`, `Table.Row`, `Table.Cell`, `Table.HeaderCell` and tokenized classes. Implement `Badge` with `tone` variants.

**Step 4: Run test to verify it passes**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/table-and-badge.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add packages/ui/src/components/Table.tsx packages/ui/src/components/Badge.tsx packages/ui/src/index.ts apps/account/components/ui/__tests__/table-and-badge.test.tsx
git commit -m "Add table and badge primitives"
```

---

### Task 4: Add feedback primitives (Banner/Empty/Skeleton)

**Files:**
- Create: `packages/ui/src/components/Callout.tsx`
- Modify: `packages/ui/src/components/EmptyState.tsx`
- Create: `packages/ui/src/components/Skeleton.tsx`
- Modify: `packages/ui/src/index.ts`
- Create: `apps/account/components/ui/__tests__/feedback.test.tsx`

**Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { Callout, EmptyState, Skeleton } from "@trail/ui";

describe("Feedback components", () => {
  it("renders callout", () => {
    render(<Callout tone="warning" title="Heads up">Check settings</Callout>);
    expect(screen.getByText("Heads up")).toBeInTheDocument();
    expect(screen.getByText("Check settings")).toBeInTheDocument();
  });

  it("renders empty state", () => {
    render(<EmptyState title="Nothing here" description="Create one" />);
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
  });

  it("renders skeleton", () => {
    render(<Skeleton className="h-6" />);
    expect(screen.getByTestId("skeleton")).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/feedback.test.tsx`
Expected: FAIL because components are missing or lack props.

**Step 3: Write minimal implementation**

Implement `Callout` and `Skeleton`, extend `EmptyState` props. Add `data-testid="skeleton"` in `Skeleton`.

**Step 4: Run test to verify it passes**

Run: `pnpm --filter @trail/account test -- apps/account/components/ui/__tests__/feedback.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add packages/ui/src/components/Callout.tsx packages/ui/src/components/EmptyState.tsx packages/ui/src/components/Skeleton.tsx packages/ui/src/index.ts apps/account/components/ui/__tests__/feedback.test.tsx
git commit -m "Add feedback primitives"
```

---

### Task 5: Refactor account shared components to `@trail/ui`

**Files:**
- Modify: `apps/account/app/components/AppShell.tsx`
- Modify: `apps/account/app/components/Sidebar.tsx`
- Modify: `apps/account/app/components/PageHeader.tsx`
- Modify: `apps/account/app/components/DashboardSkeleton.tsx`
- Modify: `apps/account/app/components/OnboardingModal.tsx`
- Modify: `apps/account/components/ui/button.tsx` (remove usage or replace with `@trail/ui`)
- Modify: `apps/account/components/ui/navigation-menu.tsx`
- Modify: `apps/account/components/ui/sidebar.tsx`
- Modify tests:
  - `apps/account/app/components/__tests__/app-shell.test.tsx`
  - `apps/account/app/components/__tests__/sidebar.test.tsx`
  - `apps/account/app/components/__tests__/page-header.test.tsx`

**Step 1: Write failing tests**

Update the tests to assert new UI primitives are present (for example, `Button` variants and `PageHeader` layout text). Ensure at least one assertion fails before code changes.

**Step 2: Run tests to verify they fail**

Run: `pnpm --filter @trail/account test -- apps/account/app/components/__tests__/app-shell.test.tsx`
Expected: FAIL

**Step 3: Write minimal implementation**

Replace local UI usage with `@trail/ui` components. Remove any redundant local UI components and align class names to tokenized values.

**Step 4: Run tests to verify they pass**

Run: `pnpm --filter @trail/account test -- apps/account/app/components/__tests__/app-shell.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/components/AppShell.tsx apps/account/app/components/Sidebar.tsx apps/account/app/components/PageHeader.tsx apps/account/app/components/DashboardSkeleton.tsx apps/account/app/components/OnboardingModal.tsx apps/account/components/ui/button.tsx apps/account/components/ui/navigation-menu.tsx apps/account/components/ui/sidebar.tsx apps/account/app/components/__tests__/app-shell.test.tsx apps/account/app/components/__tests__/sidebar.test.tsx apps/account/app/components/__tests__/page-header.test.tsx
git commit -m "Refactor account shared components to UI kit"
```

---

### Task 6: Migrate Dashboard + Activity pages

**Files:**
- Modify: `apps/account/app/(app)/dashboard/page.tsx`
- Modify: `apps/account/app/(app)/dashboard/DashboardClient.tsx`
- Modify: `apps/account/app/(app)/activity/page.tsx`
- Modify tests:
  - `apps/account/app/(app)/dashboard/__tests__/dashboard-page.test.tsx`
  - `apps/account/app/(app)/dashboard/__tests__/dashboard-client.test.tsx`
  - `apps/account/app/(app)/activity/__tests__/activity-page.test.tsx`

**Step 1: Write failing tests**

Update tests to assert `@trail/ui` components usage (e.g. `Badge`, `Table`, `EmptyState`). Ensure at least one assertion fails before implementation.

**Step 2: Run tests to verify they fail**

Run: `pnpm --filter @trail/account test -- apps/account/app/(app)/dashboard/__tests__/dashboard-page.test.tsx`
Expected: FAIL

**Step 3: Write minimal implementation**

Replace local markup with `@trail/ui` components, preserving text and data flow.

**Step 4: Run tests to verify they pass**

Run: `pnpm --filter @trail/account test -- apps/account/app/(app)/dashboard/__tests__/dashboard-page.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/dashboard/page.tsx apps/account/app/(app)/dashboard/DashboardClient.tsx apps/account/app/(app)/activity/page.tsx apps/account/app/(app)/dashboard/__tests__/dashboard-page.test.tsx apps/account/app/(app)/dashboard/__tests__/dashboard-client.test.tsx apps/account/app/(app)/activity/__tests__/activity-page.test.tsx
git commit -m "Migrate dashboard and activity UI"
```

---

### Task 7: Migrate Sessions + Billing pages

**Files:**
- Modify: `apps/account/app/(app)/sessions/page.tsx`
- Modify: `apps/account/app/(app)/billing/page.tsx`
- Modify tests:
  - `apps/account/app/(app)/sessions/__tests__/sessions-page.test.tsx`
  - `apps/account/app/(app)/billing/__tests__/billing-page.test.tsx`

**Step 1: Write failing tests**

Update tests to assert new `Table`, `Badge`, `Callout` or `EmptyState` usage. Ensure at least one assertion fails.

**Step 2: Run tests to verify they fail**

Run: `pnpm --filter @trail/account test -- apps/account/app/(app)/sessions/__tests__/sessions-page.test.tsx`
Expected: FAIL

**Step 3: Write minimal implementation**

Replace local UI with `@trail/ui` components while keeping logic intact.

**Step 4: Run tests to verify they pass**

Run: `pnpm --filter @trail/account test -- apps/account/app/(app)/sessions/__tests__/sessions-page.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/sessions/page.tsx apps/account/app/(app)/billing/page.tsx apps/account/app/(app)/sessions/__tests__/sessions-page.test.tsx apps/account/app/(app)/billing/__tests__/billing-page.test.tsx
git commit -m "Migrate sessions and billing UI"
```

---

### Task 8: Migrate Settings + Getting Started + Extension pages

**Files:**
- Modify: `apps/account/app/(app)/settings/page.tsx`
- Modify: `apps/account/app/(app)/getting-started/page.tsx`
- Modify: `apps/account/app/(app)/extension/page.tsx`
- Modify tests:
  - `apps/account/app/(app)/settings/__tests__/settings-page.test.tsx`
  - `apps/account/app/(app)/getting-started/__tests__/getting-started-page.test.tsx`
  - `apps/account/app/(app)/extension/__tests__/extension-page.test.tsx`

**Step 1: Write failing tests**

Update tests to assert `@trail/ui` components usage. Ensure at least one assertion fails before changes.

**Step 2: Run tests to verify they fail**

Run: `pnpm --filter @trail/account test -- apps/account/app/(app)/settings/__tests__/settings-page.test.tsx`
Expected: FAIL

**Step 3: Write minimal implementation**

Replace local UI with `@trail/ui` components, preserving copy and logic.

**Step 4: Run tests to verify they pass**

Run: `pnpm --filter @trail/account test -- apps/account/app/(app)/settings/__tests__/settings-page.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/settings/page.tsx apps/account/app/(app)/getting-started/page.tsx apps/account/app/(app)/extension/page.tsx apps/account/app/(app)/settings/__tests__/settings-page.test.tsx apps/account/app/(app)/getting-started/__tests__/getting-started-page.test.tsx apps/account/app/(app)/extension/__tests__/extension-page.test.tsx
git commit -m "Migrate settings, getting-started, extension UI"
```

---

### Task 9: Final verification

**Step 1: Typecheck**

Run: `pnpm --filter @trail/account typecheck`
Expected: PASS

**Step 2: Test suite**

Run: `pnpm --filter @trail/account test`
Expected: PASS

**Step 3: Lint**

Run: `pnpm --filter @trail/account lint`
Expected: PASS

