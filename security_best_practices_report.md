# Security Best Practices Report

## Executive Summary
Reviewed the Next.js/React code in `apps/account`, `apps/api`, and `apps/marketing` using the Next.js and React security specs. No critical, high, or medium findings were identified. Two informational items were noted where `dangerouslySetInnerHTML` is used with currently static data. Ensure these remain non-user-controlled or add sanitization if they become dynamic.

## Informational Findings

### INFO-1 (REACT-XSS-001)
- Severity: Low (Informational)
- Location: `apps/marketing/app/theme-init.tsx:23`
- Evidence: `return <script dangerouslySetInnerHTML={{ __html: code }} />;`
- Impact: If `code` ever becomes user-controlled, this becomes an XSS sink.
- Fix: Keep `code` static and internal-only. If it must be dynamic, sanitize before use.
- Mitigation: Add comments/tests to guard against user-provided input reaching this script.
- False positive notes: Current `code` is a hard-coded string.

### INFO-2 (REACT-XSS-001)
- Severity: Low (Informational)
- Location: `apps/marketing/app/layout.tsx:88-89`
- Evidence: `dangerouslySetInnerHTML={{ __html: JSON.stringify(videoSchema) }}`
- Impact: If `videoSchema` were derived from untrusted input, this could enable XSS.
- Fix: Keep `videoSchema` static. If dynamic, sanitize and validate input fields.
- Mitigation: Ensure the data source is trusted and schema fields are validated.
- False positive notes: `videoSchema` is built from static constants in the same file.

## Notes
- Auth token handling in `apps/account` now verifies JWT signatures using remote JWKS; ensure `TRAIL_AUTH_BASE_URL` or `BETTER_AUTH_URL` is set in production.
