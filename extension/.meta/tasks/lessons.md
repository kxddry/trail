# Lessons

- When the user asks for a constrained visual tweak, preserve the existing design tokens and make the smallest direct change instead of introducing a new visual treatment.
- When migrating fonts in shadow-DOM UI, explicitly reset `button`, `input`, `select`, and `textarea` to inherit fonts; native form controls will otherwise keep browser control fonts and bypass the root stack.
