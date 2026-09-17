## 2025-04-05 - Missing Tooltips on Icon-Only UI Elements
**Learning:** We consistently use PrimeVue's `<Button>` component for icon-only actions (like "Delete", "Edit"). While many had an `aria-label` attribute (mostly correct for screen readers), most were missing a native `title` attribute or a `v-tooltip` directive, which means sighted mouse users had no visual hover text explaining the icon's purpose. In `Layout.vue`, an edit mode toggle lacked both.
**Action:** When adding new icon-only PrimeVue buttons, always include both `aria-label="<Description>"` (for screen readers) and `title="<Description>"` (for mouse hover tooltips). For elements with dynamic states, ensure these attributes are correctly bound to those states (e.g., `:title="..."`).
## 2024-05-19 - Adding ARIA labels to Vue/PrimeVue icon-only buttons
**Learning:** In the Vue/PrimeVue framework used in this app, adding `v-tooltip` or a standard `title` to an icon-only `<Button>` is visually helpful but does not consistently expose the element's purpose to screen readers. We must explicitly apply `aria-label` directly to the `<Button>` component for proper keyboard navigation and screen reader accessibility.
**Action:** When creating or reviewing icon-only UI elements, always verify that `aria-label` is present alongside visual hints like `v-tooltip` or `title`.
## 2024-03-24 - Interactive Banner Accessibility
**Learning:** Adding keyboard interactability to composite UI elements (like banners that contain both a main action and a close button) requires careful event handling. If you just add `@keydown.enter="mainAction"`, pressing enter on the nested close button will bubble up and accidentally trigger the main action as well.
**Action:** Always use the `.self` modifier (`@keydown.enter.self="mainAction"`) on the parent container's keyboard events when there are nested interactive elements, to ensure keyboard actions don't bubble unintentionally.
## 2024-03-24 - GitHub Actions CI
**Learning:** `pnpm install` in a directory running in GitHub Actions with a newer node version might encounter issues with workspaces if a monorepo structure is implied but `pnpm-workspace.yaml` misses a definition.
**Action:** Always create a `pnpm-workspace.yaml` with `packages: ['.']` inside the frontend directory if encountering `packages field missing or empty` error during `pnpm install` in CI environments.
