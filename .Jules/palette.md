
Responsive Forms/Learning/Use `flex-col sm:flex-row` and `w-full sm:w-auto` for form inputs to ensure they stack correctly on mobile while maintaining a horizontal layout on desktop.

## 2024-05-28 - Accessible Icon-only Buttons
**Learning:** Icon-only buttons (e.g., in SensorSidebar.vue or LineChartCard.vue) without text are completely invisible to screen readers and often lack clear keyboard focus indicators.
**Action:** Always include `aria-label` and `title` (localized to German as appropriate, e.g., 'Sensoren aktualisieren') for screen readers and tooltips, and add explicit `focus-visible` classes (like `focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-gray-500`) to ensure they are visually distinct when navigated via keyboard.
