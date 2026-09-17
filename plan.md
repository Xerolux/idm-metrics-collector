1. **Fix Update Banner Accessibility in `frontend/src/components/Layout.vue`**:
   - The "Update available" banner is currently a `div` with a `@click` handler on line 128, making it inaccessible via keyboard.
   - I will add `role="button"`, `tabindex="0"`, and `aria-label="Zum Update-Bereich wechseln"` to make it semantically correct and focusable.
   - I will add `@keydown.enter.self="goToUpdate"` and `@keydown.space.prevent.self="goToUpdate"` to allow keyboard users to trigger it. The `.self` modifier is crucial to prevent the nested close button's keydown events from bubbling up and unintentionally triggering the banner click.
   - I will add `focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-400 focus-visible:outline-none outline-none` to the banner `div` to provide clear visual feedback when focused via keyboard.
   - I will add `aria-hidden="true"` to the decorative icon `<i class="pi pi-sync text-lg"></i>` and the inner `<i class="pi pi-info-circle mr-1"></i>` to prevent redundant screen reader announcements.
   - The inner dismiss `<button>` on line 144 already has `type="button"`, `@click.stop`, and `aria-label`, but lacks keyboard focus styles. I will add `focus-visible:ring-2 focus-visible:ring-white focus:outline-none` to ensure it is clearly visible when focused via keyboard.

2. **Verify Frontend Build**:
   - I will run `pnpm install` in `frontend/` (if needed) and then run `pnpm build` in the `frontend/` directory to verify that the Vue template changes compile successfully and do not introduce build regressions.

3. **Complete pre-commit steps**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

4. **Submit PR**:
   - Commit the changes and open a PR with the Palette formatting.
