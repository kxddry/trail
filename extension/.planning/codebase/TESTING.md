# Testing Patterns

**Analysis Date:** 2026-02-28

## Test Framework

**Runner:**
- Node.js native `assert/strict` module
- No external test framework (Jest, Vitest, etc.)
- Custom test runner via `node --import tsx tests/basic.test.ts`

**Run Commands:**
```bash
npm test                    # Run all tests (executes tests/basic.test.ts)
node --import tsx tests/basic.test.ts  # Run tests directly
```

**Assertion Library:**
- Node.js built-in `assert/strict` module: `import assert from 'node:assert/strict'`
- Methods: `assert.equal()`, `assert.ok()`, `assert.deepEqual()`, `assert.notEqual()`

## Test File Organization

**Location:**
- All tests in `/Users/iv/dev/trail/extension/tests/` directory (separate from source)
- Tests are co-located in a tests directory, not alongside source files

**Naming:**
- Pattern: `[name].test.ts`
- Examples: `basic.test.ts`, `security-audit.test.ts`, `notifications-sonner-adapter.test.ts`

**Structure:**
```
tests/
├── basic.test.ts                    # Main test suite with 20+ test functions
├── security-audit.test.ts           # Security-focused tests (exported as runner)
└── notifications-sonner-adapter.test.ts  # Notification adapter tests (exported as runner)
```

## Test Structure

**Suite Organization:**
- Named test functions: `function testNavigationTreeDeletion(): void { ... }`
- Test grouping by importing and calling test runner functions
- Central runner pattern: individual test modules export test functions, main suite calls them
- No describe/it blocks; test functions are standalone

**Pattern Example from `basic.test.ts` (lines 50-69):**
```typescript
function testNavigationTreeDeletion(): void {
  const tree = new NavigationTree();
  const root = tree.navigate(data('https://root.test' as Url));
  const child = tree.navigate(data('https://child.test' as Url));
  tree.setCurrent(root);
  const sibling = tree.navigate(data('https://sibling.test' as Url));
  tree.setCurrent(child);
  const grand = tree.navigate(data('https://grand.test' as Url));

  const removed = tree.deleteNode(child.id);
  assert.equal(removed.removed.length, 1);
  assert.equal(tree.findNodeById(child.id), null);
  assert.equal(tree.findNodeById(grand.id)?.getParent()?.id, root.id);

  const removedChildren = tree.deleteChildren(root.id);
  assert.equal(removedChildren.length, 2);
  assert.equal(tree.findNodeById(sibling.id), null);
  assert.equal(tree.findNodeById(grand.id), null);
  assert.equal(tree.size(), 1);
}
```

**Test Runner Pattern:**
Tests are executed via try/catch in main execution block at end of file:

```typescript
try {
  testNavigationTreeDeletion();
  testNavigationTreeDeleteMergesDuplicateReparentedNodes();
  testNavigationTreeSubtree();
  testCommandManagerUndoRedo();
  // ... more tests
  runNotificationsSonnerAdapterTests();
  runSecurityAuditTests();
  console.log('All tests passed');
} catch (error) {
  console.error('Test failure:', error);
  process.exit(1);
}
```

**Patterns:**
- Arrange-Act-Assert flow within each test function
- Setup helper functions for common data: `function data(url: Url, title?: Title): NodeData { ... }`
- Direct assertions without intermediate variables (inline assertions preferred)

## Mocking

**Framework:** Manual/custom mocking

**Patterns:**
- Mock objects created as plain TypeScript objects with matching interface signatures
- Factory functions generate mock instances: `function createFakeToastApi(): FakeToastApi { ... }`

**Example from `notifications-sonner-adapter.test.ts` (lines 23-44):**
```typescript
function createFakeToastApi(): FakeToastApi {
  const calls: ToastCall[] = [];

  const push = (kind: ToastCall['kind']) => (
    message: string,
    options?: { duration?: number },
  ) => {
    calls.push({
      kind,
      message,
      duration: options?.duration ?? -1,
    });
  };

  return {
    calls,
    success: push('success'),
    error: push('error'),
    info: push('info'),
    default: push('default'),
  };
}
```

**What to Mock:**
- External APIs (toast notifications, storage)
- Platform-specific APIs (chrome APIs in tests)
- Heavy dependencies

**What NOT to Mock:**
- Business logic classes (`NavigationTree`, `TreeNode`, `CommandManager`)
- Pure utility functions
- Data structures being tested

## Fixtures and Factories

**Test Data:**
- Helper functions create domain objects: `function data(url: Url, title?: Title): NodeData`
- Factories for complex objects: `createFakeToastApi()`
- Schema objects constructed directly for validation tests

**Example from `security-audit.test.ts` (lines 68-88):**
```typescript
function testSiteMessageAcceptsValidPing(): void {
  const result = SiteMessage.safeParse({
    source: SITE_SOURCE,
    type: SiteMessageType.PING,
    requestId: '11111111-1111-4111-8111-111111111111',
    timestamp: Date.now(),
  });
  assert.equal(result.success, true);
}
```

**Location:**
- Fixture functions defined at module level in same test file
- Shared fixtures can be extracted to separate utility files if needed
- No separate fixtures directory (all in test files)

## Coverage

**Requirements:** Not enforced (no coverage config detected)

**View Coverage:** Not applicable (no coverage tooling configured)

## Test Types

**Unit Tests:**
- Scope: Individual classes and functions (`NavigationTree`, `CommandManager`, layout calculators)
- Approach: Direct instantiation and method calls
- Examples: Tree deletion tests, layout calculation tests, sidebar utility tests

**Integration Tests:**
- Scope: Multi-component workflows (tree operations with command history, schema validation with origin checks)
- Approach: Combine multiple classes and verify interactions
- Examples:
  - `testNavigationTreeDeleteMergesDuplicateReparentedNodes()` - tree deletion + node reparenting
  - `testBackendConfigOverride()` - backend config resolution with overrides

**E2E Tests:**
- Framework: Not used
- Coverage: Functional requirements tested at unit/integration level instead

## Common Patterns

**Async Testing:**
No async/await tests observed. Codebase uses synchronous operations in test layer.

**Error Testing:**
- Validation errors tested via `.safeParse()` result checking: `assert.equal(result.success, false)`
- Business logic errors tested via direct assertions
- Security errors tested by verifying schema rejection

**Example from `security-audit.test.ts` (lines 19-27):**
```typescript
function testSiteMessageRejectsInvalidSource(): void {
  const result = SiteMessage.safeParse({
    source: 'evil-source',
    type: 'PING',
    requestId: '11111111-1111-4111-8111-111111111111',
    timestamp: Date.now(),
  });
  assert.equal(result.success, false);
}
```

## Test Assertions

**Common Assertions:**
- `assert.equal(actual, expected)` - equality check
- `assert.notEqual(actual, expected)` - inequality check
- `assert.ok(value)` - truthiness check
- `assert.deepEqual(actual, expected)` - deep object equality

**Example from `basic.test.ts` (lines 186-221):**
```typescript
function testGraphLayouts(): void {
  const tree = new NavigationTree();
  const root = tree.navigate(data('https://root.test'));
  const child = tree.navigate(data('https://child.test'));
  tree.setCurrent(root);
  const sibling = tree.navigate(data('https://sibling.test'));

  const layoutConfig: LayoutConfig = {
    nodeWidth: 120,
    nodeHeight: 60,
    verticalGap: 40,
    horizontalGap: 20,
  };
  const radialConfig: RadialLayoutConfig = {
    angleWeightExp: 0.6,
    minSpanFactor: 0.6,
    minSpanAbs: 0.12,
    requiredScale: 0.6,
    depthGapBase: 70,
    depthGapGrowth: 0.1,
    effectiveWidth: layoutConfig.nodeWidth + layoutConfig.horizontalGap,
  };

  const treeLayout = calculateLayout(root, layoutConfig);
  assert.equal(treeLayout.positions.size, 3);
  const treeBounds = getCanvasBounds(treeLayout.positions, layoutConfig.nodeWidth, layoutConfig.nodeHeight);
  assert.ok(treeBounds.width >= layoutConfig.nodeWidth);
  assert.ok(treeBounds.height >= layoutConfig.nodeHeight);

  const mindmapLayout = calculateMindmapLayout(root, layoutConfig);
  assert.equal(mindmapLayout.positions.size, 3);

  const radialLayout = calculateRadialLayout(root, radialConfig, layoutConfig);
  assert.equal(radialLayout.positions.size, 3);
  assert.ok(radialLayout.width > 0);
}
```

## Test Isolation

**Setup/Teardown:**
- Minimal setup/teardown patterns observed
- `CommandManager.clearHistory()` used to reset state between tests
- State classes instantiated fresh per test function

**Example from `basic.test.ts` (lines 111-126):**
```typescript
function testCommandManagerUndoRedo(): void {
  CommandManager.clearHistory();  // Reset state

  const rootNode: NavigationNodeJSON = {
    id: 1 as NodeId,
    timestamp: 1 as Timestamp,
    data: data('https://root.test'),
    children: [],
  };
  // ... rest of test
}
```

## Test Organization by Domain

**Navigation Tree Tests:** Lines 50-177 in `basic.test.ts`
- Deletion operations
- Node merging on delete
- Subtree operations
- Search indexing

**Command Manager Tests:** Lines 111-154 in `basic.test.ts`
- Undo/redo operations
- Snapshot saving and restoration

**Layout Tests:** Lines 186-221 in `basic.test.ts`
- Tree layout calculation
- Mindmap layout
- Radial layout
- Canvas bounds computation
- Grid transform computation

**Security Tests:** `security-audit.test.ts`
- Message schema validation
- Origin allowlist
- Config injection prevention

**Notification Tests:** `notifications-sonner-adapter.test.ts`
- Toast duration normalization
- Icon-to-toast-kind mapping
- Variant fallback behavior

---

*Testing analysis: 2026-02-28*
