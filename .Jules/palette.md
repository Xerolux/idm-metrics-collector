## 2024-05-22 - Accessibility in Vue Modals
**Learning:** Manually built modals in Vue often miss basic accessibility associations that component libraries handle automatically. In `Alerts.vue`, form labels were not associated with inputs, and icon-only buttons lacked aria-labels.
**Action:** Always check manually implemented forms and interactive elements for explicit `for`/`id` associations and `aria-label` attributes, especially when they are outside the primary UI library's scope.
