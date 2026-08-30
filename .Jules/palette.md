## 2025-04-05 - Missing Tooltips on Icon-Only UI Elements
**Learning:** We consistently use PrimeVue's `<Button>` component for icon-only actions (like "Delete", "Edit"). While many had an `aria-label` attribute (mostly correct for screen readers), most were missing a native `title` attribute or a `v-tooltip` directive, which means sighted mouse users had no visual hover text explaining the icon's purpose. In `Layout.vue`, an edit mode toggle lacked both.
**Action:** When adding new icon-only PrimeVue buttons, always include both `aria-label="<Description>"` (for screen readers) and `title="<Description>"` (for mouse hover tooltips). For elements with dynamic states, ensure these attributes are correctly bound to those states (e.g., `:title="..."`).
## 2024-05-19 - Adding ARIA labels to Vue/PrimeVue icon-only buttons
**Learning:** In the Vue/PrimeVue framework used in this app, adding `v-tooltip` or a standard `title` to an icon-only `<Button>` is visually helpful but does not consistently expose the element's purpose to screen readers. We must explicitly apply `aria-label` directly to the `<Button>` component for proper keyboard navigation and screen reader accessibility.
**Action:** When creating or reviewing icon-only UI elements, always verify that `aria-label` is present alongside visual hints like `v-tooltip` or `title`.

## 2025-02-13 - Add aria-hidden to decorative PrimeIcons
**Learning:** Decorative icons (like PrimeIcons) used inside buttons or UI elements that already have text labels or `aria-label` attributes must explicitly declare `aria-hidden="true"`. Without this, screen readers might unnecessarily announce the icon classes or internal text representation, causing redundant or confusing audio output for visually impaired users.
**Action:** When adding icons to buttons or alongside descriptive text, ensure that if they serve purely decorative or supportive visual purposes, they are hidden from screen readers using `aria-hidden="true"`.
