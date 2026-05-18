# Firefox build — task plan

> Started: 2026-05-18

## Goal

Fully working Firefox version of the Trail extension, alongside Chrome.

## Plan

### 1. WXT config — make manifest browser-aware
- Drop Chrome-only permissions (`sidePanel`, `favicon`) for Firefox
- Add `browser_specific_settings.gecko.id` + `strict_min_version`
- Add `data_collection_permissions` (Firefox AMO requirement)
- Skip the `key` field for Firefox unconditionally (Chrome-only)

### 2. Service worker — Firefox sidebar opener
- Add `browser_action` `onClicked` handler that toggles Firefox's sidebar
  (Chrome's `setPanelBehavior` handles this; Firefox has no equivalent)

### 3. Favicon — Firefox fallback
- `getFaviconUrl` returns `${origin}/favicon.ico` in Firefox builds
  since `chrome://_favicon/` is Chrome-only

### 4. Build scripts
- Add `dev:firefox`, `build:firefox`, `zip:firefox` to package.json

### 5. Verify
- `wxt build -b firefox` succeeds
- `web-ext lint` passes (no errors)
- `wxt build` (Chrome) still succeeds
- Tests, lint, typecheck still pass
