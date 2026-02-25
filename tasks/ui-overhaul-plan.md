# UI Overhaul Plan — Trail Adultification

## Vision
Transform Trail from "working MVP" to "polished product you'd pay for".
Prepare architecture for future features (split-view, multi-window).

## Scope

### 1. Design System Foundation
- Install full shadcn/ui component set in account app
- Unify Button, Card, Input, Badge, Dialog, Dropdown, Tabs, Toast, Tooltip
- Shared color tokens between extension and web app
- Consistent typography scale
- Animation system (motion/react for web, CSS for extension)

### 2. Account App — Full Redesign
**Layout:**
- Sidebar navigation (not just a header link)
- Command palette (Cmd+K) for power users
- Toast notification system (sonner)
- Page transitions with ViewTransition or motion

**Trails Page (main hub):**
- Search bar with filters
- Sort by: date, name, size
- Grid/list view toggle
- Trail cards with previews (favicon strip, node count, time range)
- Pagination or infinite scroll
- Bulk actions (delete, export)

**Trail Detail Page:**
- Better visualization preview
- Metadata cards redesign
- Timeline view of browsing session
- Quick actions toolbar

**Settings Page:**
- Tabbed interface (Profile, Appearance, Devices, Data)
- Avatar upload
- Theme picker (light/dark/system + accent colors)
- Connected devices list
- Data export/import section

**New Pages:**
- Activity/analytics dashboard with charts
- Billing page with plans comparison

### 3. Extension — Visual Upgrade
**Design:**
- Refined color palette (more personality, less generic)
- Better empty states with micro-illustrations or icons
- Improved context menu design
- Polished loading/transition animations
- Better node rendering in graph (favicons, truncated titles)

**UX:**
- Confirmation dialogs for all destructive actions
- Undo toast for delete operations
- Better search results with context snippets
- Improved tag editor with color swatches grid

### 4. Shared Infrastructure
- Toast system in web app (sonner already in extension)
- Consistent icon library (lucide-react everywhere)
- Shared animation tokens
- Responsive breakpoint system

## Agent Team Structure

### Team: ui-overhaul

**design-lead** (research + planning):
- Create design tokens and component inventory
- Define visual language
- Review other agents' work

**account-builder** (implementation):
- shadcn/ui installation and configuration
- Layout redesign (sidebar, command palette)
- Page redesigns (trails, settings, detail)

**extension-builder** (implementation):
- Extension visual refinements
- Empty states, confirmations, polish
- Color palette update

**qa-tester** (verification):
- Typecheck all changes
- Run all tests
- Visual review
- Catch regressions
