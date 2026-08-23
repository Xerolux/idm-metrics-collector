## 2025-04-05 - Missing Tooltips on Icon-Only UI Elements
**Learning:** We consistently use PrimeVue's `<Button>` component for icon-only actions (like "Delete", "Edit"). While many had an `aria-label` attribute (mostly correct for screen readers), most were missing a native `title` attribute or a `v-tooltip` directive, which means sighted mouse users had no visual hover text explaining the icon's purpose. In `Layout.vue`, an edit mode toggle lacked both.
**Action:** When adding new icon-only PrimeVue buttons, always include both `aria-label="<Description>"` (for screen readers) and `title="<Description>"` (for mouse hover tooltips). For elements with dynamic states, ensure these attributes are correctly bound to those states (e.g., `:title="..."`).
## 2024-05-19 - Adding ARIA labels to Vue/PrimeVue icon-only buttons
**Learning:** In the Vue/PrimeVue framework used in this app, adding `v-tooltip` or a standard `title` to an icon-only `<Button>` is visually helpful but does not consistently expose the element's purpose to screen readers. We must explicitly apply `aria-label` directly to the `<Button>` component for proper keyboard navigation and screen reader accessibility.
**Action:** When creating or reviewing icon-only UI elements, always verify that `aria-label` is present alongside visual hints like `v-tooltip` or `title`.
## 2024-05-19 - Error Display Tooltip
**Learning:** Dismiss buttons on error banners lacked tooltip attributes, which are helpful for sighted users as well as visual accessibility.
**Action:** Always verify that icon-only buttons include `title` attributes matching their `aria-label`.
