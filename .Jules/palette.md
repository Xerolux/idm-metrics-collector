
Responsive Forms/Learning/Use `flex-col sm:flex-row` and `w-full sm:w-auto` for form inputs to ensure they stack correctly on mobile while maintaining a horizontal layout on desktop.
## 2024-05-18 - PrimeVue Select Accessibility Labeling
**Learning:** Standard `<label>` tags enclosing PrimeVue `Select` and `MultiSelect` components do not consistently apply accessible names for screen readers because these components construct their own internal DOM.
**Action:** When labeling complex PrimeVue components like `Select` or `MultiSelect`, use a standard `<div>` (styled as a label) with a unique `id`, and explicitly link the component using the `:aria-labelledby` prop. This guarantees screen reader compatibility without relying on PrimeVue internal structures.
