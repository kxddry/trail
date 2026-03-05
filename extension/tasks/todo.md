# Todo

- [x] Vendor Inter variable font assets and license into the repo
- [x] Add a shared Inter stylesheet and import it from every extension UI entry stylesheet
- [x] Replace remaining system font stacks with `var(--trail-font-sans)` and update PIXI graph fallback/rerender behavior
- [x] Expose bundled font assets via `web_accessible_resources`
- [x] Run typecheck, tests, and build; record results below

## Review

- `pnpm typecheck`: passed
- `pnpm test`: passed
- `pnpm build`: passed
- Verified build output contains bundled `InterVariable*.woff2`
- Verified generated manifest includes `assets/*.woff2` in `web_accessible_resources`
- Verified built CSS references `--trail-font-sans` and contains no `fonts.googleapis.com` or `fonts.gstatic.com`
- Resolved a Tailwind collision by renaming the shared CSS variable from `--font-sans` to `--trail-font-sans`
