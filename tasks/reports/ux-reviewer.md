# UX Review Report -- Trail Extension + Web App

**Date:** 2026-02-25
**Reviewer:** UX Audit Agent
**Scope:** Extension sidepanel, account web app (apps/account), shared UI (packages/ui)

---

## Executive Summary

Trail is a functional product with solid core mechanics (graph visualization, tree management, tagging). However, several UX gaps make it feel like a beta rather than a polished, shipping product. The most critical issues are: (1) the session-expiry experience silently kicks users to the auth gate with no explanation, (2) most web app pages lack loading and error states, (3) destructive actions in the extension have no confirmation dialogs, and (4) accessibility gaps across both surfaces.

---

## 1. Error States & Feedback

### 1.1 CRITICAL -- Silent auth expiration in extension (the main bug)

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/App.tsx` (lines 29-31, 37-40)
**File:** `/Users/iv/dev/trail/extension/src/background/services/auth-orchestrator.ts` (lines 179-195)
**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/hooks/useAccount.ts` (lines 88-99)

When the session expires or the refresh token becomes invalid, the extension clears auth storage (`clearAuth`) and the UI transitions from the full graph view to the bare `AuthGate` screen with "Sign in to start." There is no intermediate state, no explanation of what happened, and the user's in-progress context vanishes instantly.

**What the user sees:** They are staring at their browsing tree, and suddenly it disappears and they see a cold "Sign in to start" screen. They have no idea why they were kicked out.

**Fix:**
- Add a transient "Session expired" notice to the AuthGate when the user was previously authenticated. The `resetAccount` action in `useAccount.ts` (line 98) should set a `sessionExpired: true` flag in the store.
- AuthGate should check this flag and display: "Your session has expired. Sign in again to continue." instead of "Sign in to get started."
- Consider an auto-reconnect attempt before showing the gate -- the silent sync mechanism already exists in `useAuthPortalFlow` but only runs once on mount.

### 1.2 HIGH -- Web app has no error.tsx boundary

**Missing files:**
- `apps/account/app/(app)/error.tsx` -- does not exist
- `apps/account/app/error.tsx` -- does not exist
- `apps/account/app/(app)/not-found.tsx` -- does not exist

If any server component throws, the user sees Next.js's default error page (unstyled, unhelpful). The trail detail page (`/trails/[id]/page.tsx`, line 15) calls `notFound()` but there is no custom `not-found.tsx` to catch it.

**Fix:** Create `error.tsx` and `not-found.tsx` at both `app/` and `app/(app)/` levels with branded, helpful error pages that include a retry button and a link back to `/trails`.

### 1.3 HIGH -- Root loading state is bare text

**File:** `/Users/iv/dev/trail/apps/account/app/loading.tsx` (lines 1-7)

The root loading fallback is literally:
```tsx
<div className="...">loading</div>
```
No spinner, no skeleton, no branding. This is the first thing users see during page transitions.

**Fix:** Replace with a centered TrailLogo with `animated` prop and a proper loading indicator, consistent with the login page's visual treatment.

### 1.4 MEDIUM -- Most pages lack loading.tsx

Only `dashboard/loading.tsx` has a skeleton loading state. The following pages have no loading state:
- `/trails` (the main page)
- `/trails/[id]`
- `/settings`
- `/activity`
- `/billing`

Since these are server components that fetch data, navigation to them from client-side will show the bare root loading state.

**Fix:** Add `loading.tsx` with appropriate skeletons to `/trails/`, `/trails/[id]/`, and `/settings/`.

### 1.5 MEDIUM -- Extension error boundary is functional but generic

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/ErrorBoundary.tsx`

The error boundary shows a decent message ("Trail ran into an unexpected error") but exposes the raw `error.message` to users (line 59). Raw error messages can be cryptic or contain internal details.

**Fix:** Hide the raw error behind a collapsible "Details" section. Show a user-friendly summary by default.

### 1.6 LOW -- Copy URL/Title actions have no success feedback

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/ContextMenus.tsx` (lines 573-599)

When a user clicks "Copy URL" or "Copy title" in the context menu, the operation completes silently. If `navigator.clipboard.writeText` fails, the error is logged to console but the user sees nothing.

**Fix:** Add a sonner toast on success ("URL copied") and on failure ("Failed to copy URL"). The Toaster is already mounted in App.tsx.

### 1.7 LOW -- Export actions have no feedback

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/trails/[id]/ExportButton.tsx`
**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/TreeDropdown.tsx` (lines 224-231)

Export triggers a download but provides no toast/confirmation. If the export fails, the error is only logged to console.

**Fix:** Add success/error toast notifications.

---

## 2. Auth Flow UX

### 2.1 CRITICAL -- Session expiry (covered in 1.1 above)

### 2.2 HIGH -- LoginView in packages/ui uses inline styles

**File:** `/Users/iv/dev/trail/packages/ui/src/auth/LoginView.tsx`

This component uses hardcoded `CSSProperties` objects with hex colors (`#111827`, `#4b5563`, `#b91c1c`) instead of theme tokens. It does not support dark mode.

**Fix:** Migrate to Tailwind classes using the project's design tokens. This view appears unused (the actual login uses `LoginClient.tsx`), so consider removing it entirely.

### 2.3 MEDIUM -- Extension relay page has ambiguous status

**File:** `/Users/iv/dev/trail/apps/account/app/auth/extension-relay/page.tsx`

The "Connecting to Trail extension..." state has no spinner or progress indicator. After a 5-second timeout, it shows "extension connected" regardless of whether the relay actually succeeded.

**Fix:** Add a spinner to the connecting state. Differentiate between "connected" (ACK received) and "timeout" (relay may have failed). Show guidance if timeout: "If the extension did not connect, try reopening the side panel."

### 2.4 MEDIUM -- Login page Suspense fallback is empty

**File:** `/Users/iv/dev/trail/apps/account/app/login/page.tsx` (line 6)

```tsx
<Suspense fallback={<div />}>
```

The Suspense boundary for the login page renders an empty div, causing a flash of blank content.

**Fix:** Add a minimal fallback with the TrailLogo or a skeleton.

### 2.5 LOW -- No account-switch UX

The web app layout shows the user's name in settings but offers no way to switch accounts directly. The sign-out flow (`SignOutButton.tsx`) silently swallows errors (line 37-38: `catch { setPending(false); }`) -- if logout fails, the user sees the button reset to "sign out" with no explanation.

**Fix:** Show an error toast when sign-out fails. Consider a "sign in with different account" option.

---

## 3. Responsive Design & Accessibility

### 3.1 HIGH -- Context menus use div-based items without ARIA roles

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/ContextMenus.tsx`

Context menu items are `<div>` elements with `onClick` handlers, not `<button>` or elements with `role="menuitem"`. The entire context menu lacks `role="menu"`. Items are not focusable via keyboard (no `tabIndex`, no arrow-key focus management within the menu).

**What this means:** Screen reader users cannot interact with context menus. Keyboard-only users who somehow trigger the menu cannot navigate its items.

**Fix:**
- Add `role="menu"` to the context menu container.
- Use `role="menuitem"` or `<button>` for each item.
- Implement arrow-key focus management within the menu.
- Add `tabIndex={0}` or `tabIndex={-1}` with focus management.

### 3.2 HIGH -- Delete actions in context menu lack confirmation

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/ContextMenus.tsx` (lines 615-650)

"Delete node," "Delete children," and "Delete with children" (for non-root nodes) execute immediately with no confirmation dialog. Only "Delete tree" (root node) triggers a confirmation. Bulk "Delete nodes" and "Delete nodes recursively" also fire immediately.

**What this means:** A misclick on a destructive action permanently removes data with no undo (the command stack does support undo, but users may not know about Ctrl+Z).

**Fix:** Add a confirmation step for all destructive actions, or at minimum add a toast with an "Undo" button that persists for a few seconds.

### 3.3 HIGH -- Minimal ARIA usage across the product

Across the entire codebase, only 52 `aria-*` attributes exist across 20 files, and only 9 `role` attributes across 8 files. Key gaps:
- Dropdowns (`PinnedDropdown`, `TreeDropdown`, `SettingsPopover`, `TagFilterDropdown`) lack `role="menu"` or `role="listbox"`.
- `DeleteTreeConfirmModal` and `TagEditorModal` lack `role="dialog"` and `aria-modal="true"`.
- The onboarding gate overlay (`OnboardingGate.tsx`) lacks `role="dialog"` and focus trapping.
- The extension search input lacks `role="combobox"` and result announcements.

**Fix:** Systematically add ARIA roles and properties to all interactive overlays.

### 3.4 MEDIUM -- No focus trapping in modals

**Files:**
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/DeleteTreeConfirmModal.tsx`
- `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/tags/TagEditorModal.tsx`
- `/Users/iv/dev/trail/apps/account/app/(app)/OnboardingGate.tsx`

All modals handle Escape to close, but none implement focus trapping. Tab key will move focus behind the modal to the graph/page underneath.

**Fix:** Use a focus-trap library or implement manual focus trapping (capture first/last focusable elements and cycle Tab between them).

### 3.5 MEDIUM -- No skip-to-content or landmark roles in web app

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/layout.tsx`

The web app layout uses semantic `<header>`, `<main>`, and `<nav>` elements (good), but the `<nav>` has no `aria-label`. There is no skip-to-content link.

**Fix:** Add `aria-label="Main navigation"` to nav. Add a visually hidden skip link: `<a href="#main-content" className="sr-only focus:not-sr-only">Skip to content</a>`.

### 3.6 MEDIUM -- Extension icons in buttons lack consistent accessible names

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/FloatingControls.tsx`

The undo/redo buttons have good `aria-label` attributes with shortcut info. However, many extension buttons rely solely on `data-tooltip` for their label (which is not exposed to assistive technology). The `aria-label` is present on these buttons (confirmed in FloatingControls, PinnedDropdown, TreeDropdown, SettingsPopover) -- this is consistent and good.

**Status:** Mostly good. Minor gap: the `data-tooltip` duplicates `aria-label` which is appropriate.

### 3.7 LOW -- Web app layout not responsive below 320px

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/layout.tsx`

The layout uses `max-w-4xl` with `px-4` which works for most screens. The trails grid uses `sm:grid-cols-2` which degrades gracefully. However, the trail detail page's action buttons (Export JSON + Edit in Extension) can overflow on very narrow viewports.

**Fix:** Wrap the button group in a flex-wrap container.

---

## 4. Consistency

### 4.1 HIGH -- Two different Button component systems

**File:** `/Users/iv/dev/trail/apps/account/components/ui/button.tsx` (shadcn/cva-based, `rounded-md`)
**File:** `/Users/iv/dev/trail/packages/ui/src/components/Button.tsx` (custom, `rounded-full`)

The account app uses a shadcn-style Button with `rounded-md` corners and variants: `default`, `outline`, `ghost`, `secondary`, `link`, `destructive`. The shared UI package uses a different Button with `rounded-full` corners and variants: `primary`, `outline`, `ghost`, `subtle`.

This leads to visual inconsistency between the billing page (which uses `@trail/ui` Button through `BillingPlansClient`) and the rest of the account app (which uses the shadcn Button). Buttons on the billing page are pill-shaped; buttons elsewhere are standard rounded-md.

**Fix:** Unify on one Button system. If both need to coexist, ensure they share the same border-radius and sizing tokens.

### 4.2 MEDIUM -- Inconsistent inline SVG vs lucide-react icons

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/trails/page.tsx` (lines 24-37, inline SVG for upload icon)
**File:** `/Users/iv/dev/trail/apps/account/app/(app)/trails/[id]/page.tsx` (lines 27-38, inline SVG for back arrow)
**File:** `/Users/iv/dev/trail/apps/account/app/(app)/trails/[id]/EditInExtensionButton.tsx` (lines 360-425, inline SVGs for pencil, check, spinner, external)
**File:** `/Users/iv/dev/trail/apps/account/app/(app)/trails/import/page.tsx` (lines 173-186, inline SVG for upload)

The account app hand-writes SVG icons inline while the extension uses a centralized `Icon.ts` module wrapping lucide-react. The marketing app and billing page use `@trail/ui/icons`.

**Fix:** Import from `lucide-react` or create a shared icon module for the account app.

### 4.3 MEDIUM -- Inconsistent casing in headings and labels

- Web app: all-lowercase ("trails", "settings", "sign out", "no trails yet")
- Extension: Mixed case ("Delete this tree", "Create new tree", "Settings", "Copy URL")
- Billing: lowercase ("monthly", "yearly", "save 17% with yearly")

The lowercase style is a deliberate brand choice but is inconsistently applied.

**Fix:** Establish and document casing rules. Apply consistently.

### 4.4 LOW -- No toast/notification system in web app

The extension has Sonner set up and actively uses it. The web app has no `<Toaster>` component mounted anywhere. Actions like "profile updated successfully" display as inline text next to the submit button (`AccountSettingsForm.tsx` line 98-109), while billing errors display as red text below the plans grid.

**Fix:** Add `<Toaster />` to the account app layout and convert inline status messages to toasts for consistency.

### 4.5 LOW -- Delete tree in TreeDropdown has no confirmation

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/TreeDropdown.tsx` (lines 216-222, 469-479)

Clicking the trash icon on an archived tree immediately calls `deleteArchivedTree()` with no confirmation. This contrasts with the active tree which has `DeleteTreeConfirmModal`.

**Fix:** Add a confirmation dialog or inline confirm pattern (e.g., "Are you sure?" that replaces the icon on first click).

---

## 5. Polish Gaps

### 5.1 HIGH -- No page transitions in web app

The web app uses standard Next.js page navigation with no transition animations. Navigating between `/trails` and `/trails/[id]` is an abrupt content swap.

The OnboardingGate has nice slide animations (motion/react), showing the capability exists.

**Fix:** Add subtle fade transitions using Next.js `<ViewTransition>` or wrap page content in a motion.div with opacity/y animation.

### 5.2 HIGH -- TrailLogo loading state in web app is missing

**File:** `/Users/iv/dev/trail/apps/account/components/TrailLogo.tsx`

The web app loading page shows bare text "loading" -- no TrailLogo. The login and extension-relay pages properly use TrailLogo.

**Fix:** Use TrailLogo with `animated` prop in the loading state.

### 5.3 MEDIUM -- Settings form does not reset after save

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/settings/AccountSettingsForm.tsx`

After saving, the success/error message persists indefinitely. The form fields keep `defaultValue` so they show the old values even after a successful update (since `useActionState` does not update `defaultValue`).

**Fix:** Either revalidate the page data after save (so the server provides updated values) or switch to controlled inputs that update on success. Auto-dismiss the success message after a few seconds or on the next input change.

### 5.4 MEDIUM -- Empty states could be more actionable

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/trails/page.tsx` (lines 97-108)

The trails empty state says "start browsing in the extension" but provides no CTA to install or open the extension. There is an "Import" button in the header but no prominent action in the empty state.

The shared `EmptyState` component (`packages/ui/src/components/EmptyState.tsx`) supports `action` and `secondaryAction` slots, but the trails page uses a custom inline empty state instead.

**Fix:** Use the shared EmptyState component with:
- Primary action: "Install Extension" (linking to gettrail.net) or "Import a Trail"
- Helpful description of what trails are

### 5.5 MEDIUM -- Billing page redirects to /trails

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/billing/page.tsx`

The billing page is a hard redirect to `/trails`. Users who navigate to `/billing` see nothing. The `BillingPlansClient` component exists and is fully implemented but is not used.

**Fix:** Either wire up the billing page to show plans, or remove the dead code. A "billing" route that silently redirects is confusing.

### 5.6 MEDIUM -- Multiple dead redirect pages

- `apps/account/app/(app)/dashboard/page.tsx` -- redirects to `/trails`
- `apps/account/app/(app)/activity/page.tsx` -- redirects to `/trails`
- `apps/account/app/(app)/getting-started/page.tsx` -- redirects to `/trails`
- `apps/account/app/(app)/billing/page.tsx` -- redirects to `/trails`

These create redirect chains and dead routes. If a user bookmarks `/dashboard`, they silently end up at `/trails`.

**Fix:** Either implement these pages or remove them. If they are planned-but-not-built, show a "Coming soon" page instead of a silent redirect.

### 5.7 LOW -- Extension search has no "no results" guidance

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/FloatingSearch.tsx` (line 153)

When search returns zero results, the counter shows "No results" but offers no suggestions (e.g., "Try a different search term" or "Search in all trees").

**Fix:** Minor, but adding a brief hint would polish the experience.

### 5.8 LOW -- Onboarding silently swallows poll errors

**File:** `/Users/iv/dev/trail/apps/account/app/(app)/OnboardingGate.tsx` (lines 146-148)

Poll errors are silently ignored (`catch { }`). If the user is offline, the onboarding modal will remain visible with no feedback.

**Fix:** After multiple consecutive failures, show a subtle notice: "Having trouble connecting. Check your internet connection."

### 5.9 LOW -- Tree rename and tag operations lack optimistic UI

**File:** `/Users/iv/dev/trail/extension/src/sidepanel/ui/components/TreeDropdown.tsx` (lines 183-198)

Renaming a tree commits on blur but shows no loading indicator. If the rename API call fails, the console logs the error but the UI already shows the new name.

**Fix:** Add optimistic update with rollback on error, or show a brief loading state.

---

## 6. Priority Summary

| Priority | Count | Key Issues |
|----------|-------|------------|
| CRITICAL | 2 | Silent session expiry, no error.tsx boundaries |
| HIGH     | 8 | Missing loading states, no destructive action confirmations, dual button systems, no page transitions, context menu accessibility |
| MEDIUM   | 12 | Focus trapping, settings form behavior, empty states, dead routes, icon inconsistency |
| LOW      | 7 | Toast feedback for copy/export, search hints, LoginView dead code, casing inconsistency |

---

## 7. Recommended Fix Order

1. **Session expiry UX** (1.1) -- This is the main reported bug. Add a "session expired" state to AuthGate.
2. **Error boundaries** (1.2) -- Create `error.tsx` and `not-found.tsx` for the web app.
3. **Loading states** (1.3, 1.4) -- Add loading.tsx to key routes with proper skeletons.
4. **Destructive action confirmations** (3.2, 4.5) -- Add confirmation for delete operations.
5. **Context menu accessibility** (3.1) -- Add ARIA roles and keyboard navigation.
6. **Button unification** (4.1) -- Pick one system and apply consistently.
7. **Page transitions** (5.1) -- Add subtle fade/slide animations.
8. **Everything else** -- Toast notifications, empty states, dead routes, focus trapping.
