# Coding Conventions

**Analysis Date:** 2026-02-28

## Naming Patterns

**Files:**
- kebab-case for TypeScript files: `url-key.ts`, `nav-tree.ts`, `quality-policy.ts`
- Component files in camelCase with `.tsx` extension: `TrailLogo.tsx`, `GraphZoomControls.tsx`, `FloatingControls.js`
- Utility files descriptive with domain prefix: `grid-transform.ts`, `selection-utils.ts`, `tag-palette.ts`
- Handler files named by concern: `content-handlers.ts`, `navigation-handlers.ts`, `pin-handlers.ts`

**Functions:**
- camelCase for regular functions: `calculateLayout()`, `createFakeToastApi()`, `normalizeToastDuration()`
- PascalCase for constructor/factory functions: `NavigationTree()`, `TreeNode()`, `CommandManager`
- Getter functions follow `get` prefix pattern: `getBackendServerPreset()`, `getFeatureAccess()`, `getSidebarWidth()`
- Private methods prefixed with underscore (in older code) or use private visibility modifier
- Internal/private helper functions sometimes use underscore: `nextNodeId()`, `nextLeft()`, `moveSubtree()`

**Variables:**
- camelCase for local variables and function parameters: `layoutConfig`, `treeLayout`, `parentNode`
- CONSTANT_UPPERCASE for module-level constants: `MAX_HISTORY`, `HISTORY_KEY`, `PADDING`
- Boolean variables often prefixed with `is` or `has`: `isRoot()`, `isAuthenticated`, `hasCapacityApi`
- Type aliases descriptive and specific: `NodePosition`, `ViewState`, `CanvasBounds`, `RadialLayoutConfig`

**Types:**
- PascalCase for interfaces and types: `LayoutConfig`, `ViewState`, `NavigationNode`
- Branded types using `as` for semantic type safety: `NodeId`, `Timestamp`, `Url` (from `ids.ts`)
- Local type variables in functions: `type iter = 'dfs' | 'bfs'`

## Code Style

**Formatting:**
- No visible ESLint or Prettier config enforced; appears to use natural formatting
- Consistent indentation with 2-4 spaces observed
- Import statements grouped with proper spacing
- Type imports separated: `import type { ... }`

**Linting:**
- TypeScript with strict mode enabled (`"strict": true` in tsconfig.json)
- `noUncheckedIndexedAccess: true` - requires array access safety
- `exactOptionalPropertyTypes: true` - strict optional property checking
- `useUnknownInCatchVariables: true` - catch variables default to `unknown`

## Import Organization

**Order:**
1. Node.js built-in imports: `import assert from 'node:assert/strict'`
2. Type imports first: `import type { NodeId, ... }`
3. Regular imports by layer (shared → specific domain → local)
4. File extension required: all imports use `.js` extension

**Path Aliases:**
- No visible path aliases; uses relative imports throughout
- Consistent relative paths: `../../shared/types/ids.js`, `./nav-tree.js`
- Benefits from named imports for clarity

**Example from `basic.test.ts` (lines 1-8):**
```typescript
import assert from 'node:assert/strict';

import type { NodeData, NavigationNodeJSON } from '../src/shared/types/node.js';
import type { Description, NodeId, Timestamp, Url, Title } from '../src/shared/types/ids.js';
import type { NavigationTreeJSON } from '../src/shared/types/tree.js';
import { NavigationTree } from '../src/background/state/nav-tree.js';
```

## Error Handling

**Patterns:**
- Try/catch blocks for async operations and API calls
- Silent catch patterns common: `catch { }` or `catch (error) { /* handle */ }`
- Error logging via `console.error()` with context: `console.error('CommandManager.persistNow: Failed to persist history', error)`
- Schema validation using `.safeParse()`: `const parsed = rpcRequestEnvelopeSchema.safeParse(raw)`
- Explicit error throws with descriptive messages: `throw new Error("Cannot attach node to itself")`

**Example from `nav-tree.ts`:**
```typescript
try {
  await chrome.storage.local.set({ ... });
} catch (error) {
  console.error('CommandManager.persistNow: Failed to persist history', error);
}
```

**Example from `rpc-router.ts`:**
```typescript
export function parseRpcRequestEnvelope(raw: unknown): RpcRequestEnvelope | null {
  const parsed = rpcRequestEnvelopeSchema.safeParse(raw);
  if (!parsed.success) return null;
  return parsed.data;
}
```

## Logging

**Framework:** console (native)

**Patterns:**
- `console.error()` for failures with context prefix: `'CommandManager.init: Failed to load history'`
- Errors always logged with the error object: `console.error(message, error)`
- No structured logging framework detected
- Context prefixes follow `ClassName.methodName: message` pattern

## Comments

**When to Comment:**
- Complex algorithms documented with flow description: see `calculator.ts` Tidy Tree algorithm
- Type layout documentation: UUID generation comment block in `uuid.ts` (lines 1-13)
- Business logic guards explained: `// Sanity: link2a is under link1, link2b is direct child of root.` in `basic.test.ts`
- TODO comments flagged but rare: `// todo: make this configurable by the user`, `// todo: check code for correctness`

**JSDoc/TSDoc:**
- Minimal JSDoc usage observed
- Function comments focus on parameter and return documentation
- Complex types have brief inline documentation

**Example from `uuid.ts`:**
```typescript
/**
 * Generate a UUID v7 (RFC 9562) identifier.
 *
 * Layout (128 bits):
 *   Bits  0–47 : unix_ts_ms  (48-bit millisecond timestamp)
 *   Bits 48–51 : version     (0111)
 *   Bits 52–63 : rand_a      (12 bits random)
 *   Bits 64–65 : variant     (10)
 *   Bits 66–127: rand_b      (62 bits random)
 *
 * The embedded timestamp makes IDs time-ordered and lexicographically
 * sortable, which is ideal for database primary keys.
 */
export function uuidv7(): string { ... }
```

## Function Design

**Size:**
- Typical functions 10-30 lines
- Layout algorithms reach 50-100 lines (acceptable for mathematical functions)
- Complex private helpers extracted to reduce main function size

**Parameters:**
- Single configuration object preferred over many parameters
- Type-safe: all parameters typed explicitly
- Optional parameters use `?` with defaults via destructuring

**Return Values:**
- Explicit return types annotated
- Nullable returns documented: `NodeId | null`, `Snapshot[] | null`
- Success/failure patterns use discriminated unions: `{ success: true; data: T } | { success: false; error: string }`

**Example from `calendar.ts` (lines 209-211):**
```typescript
const treeLayout = calculateLayout(root, layoutConfig);
assert.equal(treeLayout.positions.size, 3);
const treeBounds = getCanvasBounds(treeLayout.positions, layoutConfig.nodeWidth, layoutConfig.nodeHeight);
```

## Module Design

**Exports:**
- Named exports strongly preferred: `export class NavigationTree { ... }`
- Default exports for components: `export default function TrailLogo(...) { ... }`
- Type exports separate: `export type NodeRedirect = { ... }`

**Barrel Files:**
- Not widely used; direct imports from files preferred
- Component directories may export index files (not verified but standard pattern)

**Class Methods:**
- Static factory methods for state management: `CommandManager.init()`, `CommandManager.saveSnapshot()`
- Instance methods for operations: `TreeNode.addChild()`, `TreeNode.attachChild()`
- Getters for data access: `node.getParent()`, `node.getChildren()`

**Example from `tree-node.ts` (lines 12-28):**
```typescript
export class TreeNode<T> implements Timestamped {
    readonly id: NodeId;
    readonly timestamp: Timestamp;
    data: T;
    private parent: TreeNode<T> | null;
    private children: TreeNode<T>[];

    constructor(data: T, parent?: TreeNode<T>, id: NodeId = nextNodeId()) {
        this.id = id;
        if (this.id > nodeIdCounter) {
            nodeIdCounter = this.id;
        }
        this.timestamp = now();
        this.data = data;
        this.parent = parent ?? null;
        this.children = [];
    }
}
```

## React Conventions

**Component Structure:**
- Functional components with `function ComponentName()` or `export default function ComponentName()`
- Props typed via `type ComponentProps = { ... }` or inline interface
- No hooks rules issues observed
- Props destructuring in function signature: `function GraphZoomControls({ tool, onToolChange, onZoom, ... })`

**Component Naming:**
- PascalCase: `TrailLogo`, `GraphZoomControls`, `FloatingControls`
- Descriptive purpose-based names
- File name matches component name (with .tsx extension)

**Styling:**
- className strings with conditional logic: `className={`graph-control-btn ${tool === 'select' ? 'active' : ''}`}`
- data attributes for styling hooks: `data-tool="select"`, `data-graph-ui="true"`
- CSS variable references in style props: `style={{ '--trail-logo-delay': '0ms' } as React.CSSProperties}`

**Example from `GraphZoomControls.tsx` (lines 4-31):**
```typescript
type GraphZoomControlsProps = {
  tool: 'hand' | 'select';
  onToolChange: (tool: 'hand' | 'select') => void;
  onZoom: (direction: 'in' | 'out' | 'reset') => void;
  onOpenFullView: () => void;
  fullViewEnabled: boolean;
};

export default function GraphZoomControls({ tool, onToolChange, onZoom, onOpenFullView, fullViewEnabled }: GraphZoomControlsProps) {
  return (
    <div className="graph-zoom-controls" data-graph-ui="true">
        <button
          className={`graph-control-btn ${tool === 'select' ? 'active' : ''}`}
          data-tool="select"
          aria-label="Select tool (V) - Select nodes"
          data-tooltip="Select tool (V)"
          type="button"
          onClick={() => onToolChange('select')}
        >
          <Icons.MousePointer2 size={18} />
        </button>
```

---

*Convention analysis: 2026-02-28*
