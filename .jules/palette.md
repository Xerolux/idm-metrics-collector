## 2024-03-24 - PrimeVue PassThrough Props
**Learning:** When using PrimeVue 4 components in a Tailwind environment, the `pt` (PassThrough) prop is essential for applying conditional classes to internal elements (like the input inside a Password wrapper) without fighting the component structure.
**Action:** Use `:pt="{ input: { class: [...] } }"` instead of `class` or deprecated `inputClass` props when fine-grained styling control is needed.
