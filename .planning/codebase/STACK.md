# Technology Stack

**Analysis Date:** 2026-03-17

## Languages

**Primary:**
- TypeScript 5.9.3 - Used across all web apps, packages, and extension
- CommonJS/ES Modules - Extension uses commonjs, other packages use module type

**Secondary:**
- HTML/CSS (Tailwind CSS) - UI styling
- JavaScript (tsx runtime for test execution)

## Runtime

**Environment:**
- Node.js (specified via packageManager pnpm@10.29.3)
- Chrome/Chromium (browser extension target)

**Package Manager:**
- pnpm 10.29.3 - Monorepo package manager
- Lockfile: pnpm-lock.yaml (present)
- Built dependencies: `@prisma/engines`, `cypress`, `esbuild`, `prisma`, `sharp`, `unrs-resolver`

## Frameworks

**Core Web:**
- Next.js 16.1.6 - App framework for `@trail/marketing` and `@trail/account` apps
- React 19.2.4 - UI library with React DOM

**Extension:**
- WXT 0.20.18 - Extension framework (`extension/`)
- Vite 7.3.1 - Build tool (dev dependency across extension and apps)

**Testing:**
- Vitest 4.0.18 - Unit test framework for apps
- Cypress 15.11.0 - E2E testing framework
- Testing Library (@testing-library/react@16.3.2, @testing-library/user-event@14.6.1) - Component testing utilities

**Build/Dev:**
- ESLint 9.39.2 - Code linting
- Prettier 3.8.1 - Code formatting (via root .prettierignore)
- TypeScript 5.9.3 - Type checking
- PostCSS 8.5.6 - CSS processing
- Tailwind CSS 4.2.1 - Utility-first CSS framework (with @tailwindcss/postcss@4.2.1)

## Key Dependencies

**Critical:**
- @prisma/client 7.4.1 - Database ORM
- @prisma/adapter-pg 7.4.1 - PostgreSQL adapter for Prisma
- @trpc/server 11.9.0 - Backend API framework
- @trpc/client 11.9.0 - Client library for API calls
- @trpc/react-query 11.9.0 - React integration for tRPC
- better-auth 1.4.19 - Authentication framework
- @tanstack/react-query 5.90.20 - Data fetching and caching
- zod 4.3.6 - Schema validation (used across auth, APIs)
- jose 6.1.3 - JWT handling

**UI Components & Styling:**
- @radix-ui/* - 15+ UI components (react-dialog, react-dropdown-menu, react-select, etc.)
- lucide-react 0.575.0 - Icon library
- motion 12.34.3 - Animation library
- sonner 2.0.7 - Toast notifications
- class-variance-authority 0.7.1 - CSS-in-JS variant management
- clsx 2.1.1 - Utility for conditional CSS classes
- tailwind-merge 3.5.0 - Tailwind class merger

**Backend/Database:**
- pg 8.19.0 - PostgreSQL client driver
- dotenv 17.2.3 - Environment variable loader

**CMS:**
- @sanity/client 7.16.0 - Sanity CMS client (for marketing app)
- @sanity/image-url 2.0.3 - Sanity image URL builder

**Utilities & Serialization:**
- superjson 2.2.6 - Enhanced JSON serialization (handles Dates, Maps, Sets)
- jwt-decode 4.0.0 - JWT decoding (client-side)

**Analytics & Monitoring:**
- @vercel/analytics 1.6.1 - Vercel analytics integration
- @vercel/speed-insights 1.3.1 - Vercel speed monitoring

**Graphics/3D:**
- three 0.183.1 - 3D graphics library (used in marketing app)
- pixi.js 8.16.0 - 2D WebGL renderer (used in extension)

**Data & Search:**
- minisearch 7.2.0 - Lightweight full-text search (extension local search)
- @tanstack/react-virtual 3.13.22 - Virtual scrolling for large lists

**Type Safety:**
- server-only 0.0.1 - Runtime check to ensure code runs server-side

## Configuration

**Environment:**
- Environment variables validated at startup in `apps/account/src/env.ts`
- Required vars for account app: `BETTER_AUTH_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `TRAIL_EXTENSION_JWT_SECRET`, `DATABASE_URL`
- Optional vars: `APP_BASE_URL`, `NEXT_PUBLIC_APP_URL`, `VERCEL_URL`, `BILLING_PROVIDER`, `BILLING_TEST_MODE`, `NOWPAYMENTS_API_KEY`, `NOWPAYMENTS_IPN_SECRET`, `NOWPAYMENTS_API_BASE_URL`, `TRAIL_EXTENSION_AUTH_REQUIRED`

**Build:**
- ESLint config: `eslint.config.mjs` (flat config format)
- Prettier ignore: `.prettierignore`
- Next.js config: Per-app (implicit, standard Next.js patterns)
- Cypress config: `cypress.config.ts` - E2E test configuration
- TypeScript: `tsconfig.json` in root (inherited/extended per workspace)

## Platform Requirements

**Development:**
- Node.js with pnpm 10.29.3
- TypeScript 5.9.3 compatible environment
- PostgreSQL database for local development (DATABASE_URL env var)
- Chrome/Chromium for extension testing

**Production:**
- **Web:** Vercel (implied by @vercel/* packages and VERCEL_URL in env resolution)
- **Database:** PostgreSQL with connection pooling support (via @prisma/adapter-pg)
- **CMS:** Sanity (for marketing content)
- **Auth:** Google OAuth provider integration
- **Hosting:** Supports deployment to Vercel (analytics and speed-insights packages)

---

*Stack analysis: 2026-03-17*
