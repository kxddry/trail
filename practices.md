Below is a **large, practical, opinionated markdown checklist** you can actually use when building or reviewing a **React SPA**. It’s framework-agnostic (works with Vite / CRA / Next in SPA mode) and reflects modern React (hooks, concurrent features, 18+).

---

# ✅ React SPA Best Practices

---

## 🧠 Architecture & Project Structure

* Prefer **feature-based** structure over type-based

  ```
  src/
    features/
      auth/
        components/
        hooks/
        api.ts
        slice.ts
      dashboard/
    shared/
      ui/
      hooks/
      utils/
  ```
* Avoid deep relative imports (`../../../../`)
* Use **barrel files** (`index.ts`) carefully (don’t overuse)
* Keep business logic **out of components**
* Separate:

  * UI
  * domain logic
  * API layer
* Make components **replaceable and isolated**
* Avoid global state unless truly shared
* Prefer composition over inheritance

---

## ⚛️ Component Design

* Keep components **small and focused**
* One responsibility per component
* Prefer **function components**
* Avoid god-components
* Extract logic into **custom hooks**
* Keep JSX clean:

  * move conditionals out
  * avoid inline complex expressions
* Use **controlled components** for forms
* Avoid passing too many props (prop drilling smell)
* Prefer children over config props where possible

---

## 🪝 Hooks Best Practices

* Follow the **Rules of Hooks**
* One hook = one concern
* Prefix custom hooks with `use`
* Avoid side effects in render
* Use `useEffect` only for **effects**, not logic
* Split effects by responsibility
* Always define **dependencies correctly**
* Use `useRef` for:

  * mutable values
  * DOM access
  * previous values
* Prefer `useCallback` / `useMemo` **only when needed**
* Never silence ESLint hook rules blindly

---

## 🧵 State Management

* Prefer **local state first**
* Lift state only when required
* Use global state for:

  * auth
  * user
  * theme
  * app-wide flags
* Avoid overusing Redux
* If using Redux:

  * use Redux Toolkit
  * avoid thunks for complex flows → use sagas / effects libs
* Consider:

  * Zustand
  * Jotai
  * Recoil
* Never store derived state
* Normalize large collections
* Avoid duplicating server state

---

## 🌐 Server State & Data Fetching

* Use **React Query / TanStack Query**
* Treat server state as **cache**
* Always handle:

  * loading
  * error
  * empty
* Use query keys consistently
* Invalidate queries intentionally
* Avoid fetching in components directly
* Keep API logic in separate layer
* Use pagination / infinite queries
* Cancel requests on unmount
* Handle retries explicitly
* Never assume network success

---

## 🚦 Routing

* Use React Router / TanStack Router
* Lazy-load routes
* Keep routes flat where possible
* Avoid logic inside route definitions
* Protect routes with wrappers (auth guards)
* Sync URL with state when relevant
* Avoid deeply nested routes
* Handle 404 properly
* Don’t use router as global state

---

## 🎨 Styling

* Choose **one** styling strategy:

  * CSS Modules
  * Tailwind
  * Styled Components
* Avoid mixing multiple systems
* Prefer **utility-first** or **design tokens**
* Avoid inline styles (except dynamic values)
* Use CSS variables for theming
* Keep styles close to components
* Avoid global CSS leaks
* Use responsive units (`rem`, `%`)
* Avoid magic numbers

---

## 🧪 Testing

* Test behavior, not implementation
* Prefer **React Testing Library**
* Avoid shallow rendering
* Test:

  * user flows
  * edge cases
  * error states
* Mock network requests
* Don’t mock React internals
* Use test IDs sparingly
* Snapshot tests only for stable UI
* Keep tests fast and deterministic
* Run tests in CI

---

## ⚡ Performance

* Use code splitting (`lazy`, dynamic imports)
* Avoid unnecessary re-renders
* Memoize only hot paths
* Use `key` correctly in lists
* Avoid inline functions in render loops
* Virtualize large lists
* Defer non-critical work
* Avoid blocking main thread
* Measure before optimizing
* Use React DevTools Profiler

---

## ♿ Accessibility (A11y)

* Use semantic HTML
* Always label inputs
* Support keyboard navigation
* Ensure focus management
* Provide ARIA only when needed
* Ensure sufficient contrast
* Don’t rely on color only
* Test with screen readers
* Avoid div-buttons
* Respect reduced motion

---

## 🔐 Security

* Never trust client input
* Sanitize user content
* Protect against XSS
* Avoid `dangerouslySetInnerHTML`
* Store tokens securely (httpOnly cookies preferred)
* Avoid localStorage for auth
* Validate API responses
* Use CSP headers
* Avoid exposing secrets in build

---

## 🧩 Forms

* Use form libraries for complex forms
* Prefer controlled inputs
* Validate both client and server
* Debounce expensive validation
* Show clear error messages
* Handle submit loading state
* Prevent double submit
* Keep form logic separate
* Reset state intentionally

---

## 🧰 Tooling & DX

* Use TypeScript
* Enable strict mode
* Use ESLint + Prettier
* Enforce consistent imports
* Use absolute imports
* Configure path aliases
* Fail build on lint errors
* Use environment variables correctly
* Avoid console logs in prod

---

## 📦 Build & Deployment

* Use Vite or modern bundlers
* Enable tree-shaking
* Analyze bundle size
* Split vendor chunks
* Use environment-specific configs
* Enable gzip / brotli
* Use cache headers
* Avoid huge initial bundles
* Version assets

---

## 🧼 Code Quality

* Prefer clarity over cleverness
* Remove dead code
* Keep commits small
* Name things clearly
* Avoid comments that explain “what”
* Document “why”
* Avoid premature abstractions
* Refactor regularly
* Enforce code reviews

---

## 🧭 Error Handling

* Use Error Boundaries
* Handle async errors explicitly
* Show user-friendly messages
* Log errors centrally
* Fail gracefully
* Retry when reasonable
* Never swallow errors silently
* Handle edge cases

---

## 🧱 Reusability & Design Systems

* Build reusable UI primitives
* Avoid premature generalization
* Keep components composable
* Document component APIs
* Version shared components
* Avoid coupling UI to business logic
* Use Storybook when scale grows

---

## 🧠 Mental Models

* UI is a function of state
* Side effects are exceptional
* Global state is expensive
* Abstractions have cost
* Simplicity scales better
* Measure, don’t guess
* Consistency beats perfection

---
