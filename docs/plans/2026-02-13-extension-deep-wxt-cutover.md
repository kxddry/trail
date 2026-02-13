# Extension Deep WXT Cutover Plan

## Goal
Migrate `extension/` to WXT-native build/runtime, introduce RPC v2 transport envelopes, and remove legacy state/build/message layers in one integration batch.

## Scope
1. WXT entrypoints + manifest config.
2. Remove legacy build scripts and Vite-only sidepanel manifest pipeline.
3. Move message contracts to `shared/rpc/*` and adopt RPC v2 envelopes on request/response path.
4. Remove `PanelState` and dead background window lifecycle file.
5. Use one origin policy source (`site-origins.ts`) for content + config.
6. Add TanStack Query for account server-state in sidepanel.
7. Remove direct `pixi.js/unsafe-eval` import from main bootstrap.

## Verification
1. `pnpm -C extension typecheck`
2. `pnpm -C extension test`
3. `pnpm -C extension build`
4. `pnpm -C extension audit --prod`
