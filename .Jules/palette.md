## 2024-05-22 - Accessibility in Vue Modals
**Learning:** Manually built modals in Vue often miss basic accessibility associations that component libraries handle automatically. In `Alerts.vue`, form labels were not associated with inputs, and icon-only buttons lacked aria-labels.
**Action:** Always check manually implemented forms and interactive elements for explicit `for`/`id` associations and `aria-label` attributes, especially when they are outside the primary UI library's scope.

## 2026-01-22 - Inline Validation Accessibility
**Learning:** Inline form validation often visually communicates errors (red text) without programmatic association. In `Login.vue`, the error message was visible but not linked to the input via `aria-describedby` or flagged with `aria-invalid`.
**Action:** When implementing custom validation, always bind `aria-invalid` to the error state and use `aria-describedby` to point to the error message ID. Ensure the error message has `role="alert"` for immediate announcement.

## 2026-01-30 - Modernizing Alert Interactions
**Learning:** Native browser dialogs (`confirm`, `alert`) interrupt the user workflow and look outdated compared to the rest of the application. Replacing them with PrimeVue's `ConfirmDialog` and `Toast` provides a seamless, non-blocking, and consistent experience.
**Action:** Identify and replace any remaining usages of `window.confirm` or `window.alert` with `useConfirm` and `useToast` services to maintain UI consistency and accessibility.

## 2026-02-04 - Dangerous Action Confirmation
**Learning:** Immediate execution of destructive actions (like delete) on icon-only buttons is a high-risk pattern. In `Schedule.vue`, clicking the trash icon deleted the job instantly, which is error-prone.
**Action:** Wrap all destructive actions in `confirm.require` using PrimeVue's `ConfirmDialog`. Ensure the dialog has clear 'Accept'/'Reject' labels and visual urgency (e.g., `p-button-danger`).
