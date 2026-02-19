
Responsive Forms/Learning/Use `flex-col sm:flex-row` and `w-full sm:w-auto` for form inputs to ensure they stack correctly on mobile while maintaining a horizontal layout on desktop.

## 2026-02-19 - Accessible Icon Buttons
**Learning:** Custom chart components (`ChartCard`, etc.) implement overlay controls using raw HTML `<button>` elements which lack accessible names, making them invisible to screen readers.
**Action:** Always add `aria-label` to icon-only buttons, especially when building custom overlay interfaces that don't use the component library's button component.
