
Responsive Forms/Learning/Use `flex-col sm:flex-row` and `w-full sm:w-auto` for form inputs to ensure they stack correctly on mobile while maintaining a horizontal layout on desktop.

## 2026-02-13 - Password Visibility
**Learning:** Password inputs should always offer a visibility toggle using the `p-inputgroup` pattern to prevent typing errors and improve accessibility.
**Action:** Wrap `InputText` in `p-inputgroup` and add a toggle `Button` with `type="button"` and dynamic `aria-label`.
