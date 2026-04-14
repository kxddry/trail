# TODO

- [x] Add `@webext-core/messaging` and `@webext-core/proxy-service` and wire shared transport primitives under `src/shared`.
- [x] Define the new `ExtensionProtocolMap`, `WebsiteProtocolMap`, page namespace constant, and proxy-service keys/interfaces.
- [x] Migrate sidepanel -> background request/response APIs from `rpc.*` wrappers to proxy services.
- [x] Migrate content/background sender-aware flows to `@webext-core/messaging`.
- [x] Migrate background push events (`TREE_UPDATED`, `TREES_UPDATED`, `NOTIFY`, site relays) to typed extension messages.
- [x] Replace the content/site bridge with `defineWindowMessaging` and remove the old envelope, TTL, nonce, and relay plumbing.
- [x] Remove legacy RPC transport files and generic router code after all call sites are cut over.
- [x] Replace RPC schema tests with transport-contract coverage and add focused bridge tests.
- [x] Run `pnpm run typecheck`, `pnpm run test`, and `pnpm build`.

## Review

- Added `@webext-core/messaging` and `@webext-core/proxy-service`, then introduced the new transport layer under `src/shared/transport` with typed extension messages, window messaging, and proxy-service contracts/clients.
- Migrated sidepanel request/response APIs to proxy services, moved sidepanel runtime subscriptions to `onExtensionMessage`, and rewired background push notifications plus the editor-exit relay to typed extension events.
- Replaced the content/site bridge with the new `trail-bridge-v1` window messaging contract and a thin runtime adapter, removing the old envelope-based relay path and the legacy RPC router/client/schema files.
- Removed the exported `rpc.*` message factory API and deleted the remaining dead `SITE_MESSAGE_FORWARD` transport contract pieces from `src/shared/rpc/contracts.ts`; the file still retains internal handler typing used by existing background handler maps.
- Added `tests/transport-contracts.test.ts` and `tests/content-bridge-runtime.test.ts`, and updated smoke coverage to document the new site ping/open-panel/editor/event flows.
- Verification:
  - `pnpm run test` passed.
  - `pnpm build` passed.
  - `pnpm run typecheck` still fails on pre-existing unrelated issues in `src/features/graph/elk-graph.ts` and `src/ui/components/ui/{calendar,context-menu,dropdown-menu,menubar,slider,sonner,spinner}.tsx`.
