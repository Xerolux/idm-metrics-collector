## 2024-05-22 - Accessibility in Vue Modals
**Learning:** Manually built modals in Vue often miss basic accessibility associations that component libraries handle automatically. In `Alerts.vue`, form labels were not associated with inputs, and icon-only buttons lacked aria-labels.
**Action:** Always check manually implemented forms and interactive elements for explicit `for`/`id` associations and `aria-label` attributes, especially when they are outside the primary UI library's scope.

## 2026-01-22 - Inline Validation Accessibility
**Learning:** Inline form validation often visually communicates errors (red text) without programmatic association. In `Login.vue`, the error message was visible but not linked to the input via `aria-describedby` or flagged with `aria-invalid`.
**Action:** When implementing custom validation, always bind `aria-invalid` to the error state and use `aria-describedby` to point to the error message ID. Ensure the error message has `role="alert"` for immediate announcement.

## 2026-01-30 - Modernizing Alert Interactions
**Learning:** Native browser dialogs (`confirm`, `alert`) interrupt the user workflow and look outdated compared to the rest of the application. Replacing them with PrimeVue's `ConfirmDialog` and `Toast` provides a seamless, non-blocking, and consistent experience.
**Action:** Identify and replace any remaining usages of `window.confirm` or `window.alert` with `useConfirm` and `useToast` services to maintain UI consistency and accessibility.

## 2026-10-18 - Modal Form Submission
**Learning:** When moving form actions to a standardized Dialog footer (outside the `<form>` tag), native validation and submission break.
**Action:** Assign an `id` to the form and use `type="submit" form="form-id"` on the footer button to retain native browser validation and submission behavior without custom JavaScript handlers.

## 2026-02-04 - Accessible Icon-Only Buttons
**Learning:** Icon-only buttons in complex dashboards are frequently overlooked for accessibility. Tooltips (`title`) are insufficient for screen readers.
**Action:** Systematically audit all `Button` components with an `icon` prop but no `label` prop. Add an explicit `aria-label` matching the tooltip text or providing a descriptive action name.

## 2026-03-05 - Implicit Contrast Assumptions
**Learning:** Headers in dark-themed sections (like `bg-surface-900`) without explicit text color classes often rely on inherited styles. This fails when the global text color defaults to a dark value, rendering the text invisible against the dark background.
**Action:** Always explicitly define text color (e.g., `text-gray-100`) for headings within sections that enforce a specific background color, rather than relying on inheritance or dark mode variants alone.

## 2026-03-12 - Clickable Div Anti-Pattern
**Learning:** Found critical actions (adding charts) implemented as clickable `div`s with `@click` but no keyboard support (`tabindex`, `role="button"`, `keydown` handlers). This excludes keyboard-only and screen reader users.
**Action:** Always use native `<button>` elements for actions. If custom styling is needed, use utility classes to remove default button styles (`appearance-none`, `bg-transparent`, etc.) rather than reinventing the wheel with `div`s.
