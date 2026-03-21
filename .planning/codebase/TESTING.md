# Testing Patterns

**Analysis Date:** 2026-03-17

## Test Framework

**Runner:**
- Vitest [version via package.json dependencies]
- Config: `apps/account/vitest.config.ts` and `apps/marketing/vitest.config.ts`
- Projects: Dual configuration for client (jsdom) and server (node) test environments

**Assertion Library:**
- Vitest built-in `expect` API
- Testing Library matchers extended via `@testing-library/jest-dom/matchers`
- Setup: `apps/account/vitest.setup.ts` extends expect globally

**Run Commands:**
```bash
pnpm test                  # Run tests once (passes with no tests)
pnpm test:watch          # Watch mode (from individual app root)
vitest --passWithNoTests  # Default in account app (returns 0 even if no tests)
```

## Test File Organization

**Location:**
- Co-located in `__tests__/` directories alongside implementation
- Naming: `[module].test.ts` or `[module].test.tsx`

**Examples:**
- `apps/account/src/server/backend/__tests__/json.test.ts` tests `json.ts` in same directory
- `apps/account/src/lib/__tests__/auth.test.ts` tests `auth.ts` in parent directory
- `apps/account/app/(app)/activity/__tests__/activity-page.test.tsx` tests `activity/page.tsx`

**Naming Patterns:**
- Test suites describe the module: `describe("getUserFromToken", ...)`
- Test cases use `it("...")` blocks: `it("returns the user for a valid token", ...)`
- Descriptive test names explain behavior, not implementation

## Test Structure

**Suite Organization:**
```typescript
// From apps/account/src/server/backend/__tests__/json.test.ts
import { describe, expect, it } from "vitest";
import { isJsonValue, toPrismaJsonInput } from "../json";

describe("isJsonValue", () => {
  it("accepts JSON primitives and structures", () => {
    // Test implementation
  });

  it("rejects non-JSON values", () => {
    // Test implementation
  });
});

describe("toPrismaJsonInput", () => {
  it("maps null to Prisma.JsonNull", () => {
    // Test implementation
  });
});
```

**Patterns:**
- No setup/teardown in simple tests (single responsibility)
- `beforeAll` for expensive setup (key generation in auth tests)
- `beforeEach` for mocking resets
- `afterAll` for cleanup (stub cleanup)
- Test isolation enforced with mock resets between tests

## Mocking

**Framework:** `vi` (Vitest)

**Patterns:**

```typescript
// From apps/account/src/lib/__tests__/auth.test.ts
const extensionAuthMocks = vi.hoisted(() => ({
  verifyExtensionToken: vi.fn(async () => null as unknown),
}));

vi.mock("@/src/server/backend/auth/extension-auth", () => ({
  ...extensionAuthMocks,
}));

// In test:
extensionAuthMocks.verifyExtensionToken.mockResolvedValue({
  sub: "user-ext-1",
  iat: 100,
  exp: 200,
} as unknown);
```

**Key Techniques:**
- `vi.hoisted()` - Hoist mock declarations to top for hoisting
- `vi.mock()` - Mock entire modules
- `.mockResolvedValue()` - Mock promise resolution
- `.mockReset()` - Clear mock history between tests
- `vi.stubGlobal()` - Stub global functions (e.g., `fetch`)
- `vi.unstubAllGlobals()` - Clean up global stubs

**What to Mock:**
- External dependencies: auth services, database, API calls
- Environment configuration (`vi.mock("@/src/env")`)
- Time-dependent logic (explicit mocking not required; tests are fast)

**What NOT to Mock:**
- Internal helper functions (test the full path)
- React Testing Library internals
- System/platform-level APIs except in isolation tests

## Fixtures and Factories

**Test Data:**
```typescript
// From apps/account/src/lib/__tests__/auth.test.ts
const issuer = "https://auth.example.com";

beforeAll(async () => {
  const { publicKey, privateKey } = await generateKeyPair("RS256");
  // Setup test keys
});

it("returns the user for a valid token", async () => {
  const token = await new SignJWT({
    email: "alex@trail.net",
    name: "Alex Trail",
  })
    .setProtectedHeader({ alg: "RS256", kid: "test-key" })
    .setIssuer(issuer)
    .setSubject("uuid-dev-1234")
    .setExpirationTime("2h")
    .sign(privateKey);

  const user = await getUserFromToken(token);
  expect(user).toEqual({...});
});
```

**Location:**
- Test data inline in test files (no separate fixtures directory observed)
- Complex setup in `beforeAll` blocks
- Factories created ad-hoc as needed

## Coverage

**Requirements:** Not explicitly enforced (no coverage threshold in config)

**View Coverage:**
- Not configured in `vitest.config.ts`
- Can run via: `vitest --coverage` (if configured)

## Test Types

**Unit Tests:**
- Scope: Individual functions and type guards
- Approach: Pure function testing with explicit inputs/outputs
- Example: `isJsonValue()` tests all JSON type variants
- Location: `src/server/backend/__tests__/`, `src/lib/__tests__/`

**Integration Tests:**
- Scope: API endpoints, auth flows, database operations
- Approach: Mock external services, test full business logic
- Example: `apps/account/src/lib/__tests__/auth.test.ts` tests JWT verification + fallback to extension auth
- Pattern: Setup mocks, execute function, assert side effects

**E2E Tests:**
- Framework: Cypress
- Config: `cypress.config.ts` (root level)
- Run: `pnpm test:e2e` (run headless), `pnpm test:e2e:open` (interactive)
- Scope: Not detailed in config file (see `/cypress` directory for tests)

## Common Patterns

**Async Testing:**
```typescript
// Async functions tested with async/await
it("falls back to extension token and resolves db user", async () => {
  extensionAuthMocks.verifyExtensionToken.mockResolvedValue({
    sub: "user-ext-1",
  });

  const user = await getUserFromToken("invalid.jwt.token");

  expect(user).toEqual({...});
});
```

**Error Testing:**
```typescript
// Errors tested via rejection or error log verification
it("returns undefined when the issuer is invalid", async () => {
  const token = await new SignJWT({...})
    .setIssuer("https://evil.example.com") // Invalid issuer
    .sign(privateKey);

  await expect(getUserFromToken(token)).resolves.toBeUndefined();
});
```

## Vitest Configuration Details

**Server Tests:**
```typescript
// From apps/account/vitest.config.ts
{
  name: "server",
  globals: true,
  environment: "node",
  setupFiles: "./vitest.setup.ts",
  include: [
    "app/api/**/*.test.ts",
    "src/server/**/*.test.ts",
    "src/lib/**/*.test.ts",
    "src/**/*.test.ts",
  ],
}
```

**Client Tests:**
```typescript
{
  name: "client",
  globals: true,
  environment: "jsdom",
  setupFiles: "./vitest.setup.ts",
  include: [
    "app/**/__tests__/**/*.test.tsx",
    "app/components/**/__tests__/**/*.test.tsx",
  ],
}
```

**Setup File:** `vitest.setup.ts`
- Extends expect with Testing Library matchers
- Sets default environment variables for tests (secrets use test defaults)
- No database reset between tests (mocking preferred)

## Test Isolation

**Environment Variables:**
```typescript
// From apps/account/vitest.setup.ts
process.env.BETTER_AUTH_SECRET = process.env.BETTER_AUTH_SECRET ?? "0123456789abcdef0123456789abcdef";
process.env.DATABASE_URL = process.env.DATABASE_URL ?? "postgresql://postgres:postgres@localhost:5432/trail?schema=public";
```

- Defaults allow tests to run without `.env` files
- Can be overridden via environment before test run
- Test database typically same as dev (use separate DB for CI)

**Mock Resets:**
- Manual `.mockReset()` in `beforeEach` blocks
- Global stub cleanup via `vi.unstubAllGlobals()`
- Each test starts with clean mock state

## Best Practices Observed

1. **Test names describe behavior**: "accepts JSON primitives" vs "test JSON"
2. **One assertion per test**: Each `it()` block tests one thing
3. **Descriptive variable names**: `server`, `client`, `result` make intent clear
4. **No test interdependencies**: Tests can run in any order
5. **Minimal mocking**: Only mock what's external to the unit
6. **Explicit expectations**: Always assert what changed
7. **Arrange-Act-Assert pattern**: Setup, execute, verify in order

---

*Testing analysis: 2026-03-17*
