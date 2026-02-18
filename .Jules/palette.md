
Responsive Forms/Learning/Use `flex-col sm:flex-row` and `w-full sm:w-auto` for form inputs to ensure they stack correctly on mobile while maintaining a horizontal layout on desktop.
## 2025-10-27 - Clickable Divs
**Learning:** Large call-to-action areas implemented as `div` with `@click` create keyboard traps.
**Action:** Replace with `<button type="button" class="w-full ...">` and add `focus-visible` styles to restore keyboard accessibility without breaking layout.
