---
name: frontend-standards
description: Frontend development standards — accessibility, component design, CSS methodology, responsive design. Use when building or modifying UI components, styles, or layouts.
---

# Frontend Standards

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival — consolidates 4 disabled skills

## Scope

- Frontend components in `cmd/flext-control-panel/`
- HTML templates, CSS/SCSS files, JavaScript/TypeScript components
- UI accessibility and responsive behavior

## References

- <https://www.w3.org/WAI/WCAG21/quickref/>
- <https://developer.mozilla.org/en-US/docs/Learn/Accessibility>

## Rules

- Use semantic HTML elements (`nav`, `main`, `article`, `section`) before adding ARIA attributes.
- Ensure keyboard navigability for all interactive elements.
- Maintain minimum 4.5:1 color contrast ratio for text (WCAG AA).
- Design mobile-first — start with mobile styles, add complexity via `min-width` media queries.
- Keep components single-responsibility with explicit prop interfaces.
- Prefer project CSS methodology (Tailwind, BEM, CSS Modules) — don't mix approaches.

## Instructions

### Accessibility

**Semantic HTML**:

```html
<!-- Good: semantic -->
<nav aria-label="Main navigation">
  <ul><li><a href="/home">Home</a></li></ul>
</nav>
<main><article><h1>Title</h1><p>Content</p></article></main>

<!-- Bad: div soup -->
<div class="nav"><div class="link" onclick="go()">Home</div></div>
```

**Keyboard navigation**:

```html
<button type="button" onclick="toggle()">Menu</button>
<!-- NOT: <div onclick="toggle()">Menu</div> — not keyboard accessible -->
```

**Form labels**:

```html
<label for="email">Email</label>
<input id="email" type="email" required aria-describedby="email-help">
<span id="email-help">We'll never share your email.</span>
```

**Image alt text**:

```html
<img src="chart.png" alt="Monthly revenue chart showing 15% growth in Q4">
<img src="decorative-line.svg" alt="" role="presentation">
```

### Component Design

**Single responsibility** — each component does one thing:

```tsx
// Good: focused component
function UserAvatar({ name, imageUrl, size = "md" }: AvatarProps) {
  return <img src={imageUrl} alt={name} className={`avatar-${size}`} />;
}

// Bad: kitchen-sink component with too many responsibilities
function UserCard({ user, onEdit, onDelete, showAdmin, theme, layout }) { ... }
```

**Explicit prop types**:

```tsx
interface ButtonProps {
  label: string;
  variant?: "primary" | "secondary" | "danger";
  disabled?: boolean;
  onClick: () => void;
}
```

### CSS / Styling

**Design tokens**:

```css
:root {
  --color-primary: #2563eb;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --font-size-base: 1rem;
}

.button { background: var(--color-primary); padding: var(--spacing-sm) var(--spacing-md); }
```

**Avoid `!important`** — fix specificity issues instead.

### Responsive Design

**Mobile-first breakpoints**:

```css
/* Base: mobile */
.container { padding: 1rem; }

/* Tablet */
@media (min-width: 768px) { .container { padding: 2rem; max-width: 720px; } }

/* Desktop */
@media (min-width: 1024px) { .container { max-width: 960px; } }
```

**Touch targets** — minimum 44x44px for interactive elements on mobile.

**Relative units** — use `rem` for typography and spacing, `%` or `fr` for layouts.

## Workflow

1. Start with semantic HTML structure.
2. Add styles mobile-first using design tokens.
3. Build components with explicit props and single responsibility.
4. Test keyboard navigation and screen reader compatibility.
5. Verify responsive behavior across breakpoints.
6. Run accessibility audit (axe, Lighthouse).

## Examples

Good:

```html
<button type="button" aria-expanded="false" aria-controls="menu">
  Toggle Menu
</button>
<nav id="menu" hidden>...</nav>
```

Why good: semantic button, ARIA state management, keyboard accessible by default.

Bad:

```html
<div class="btn" onclick="toggleMenu()" style="color: #999; font-size: 11px;">
  ☰
</div>
```

Why bad: not keyboard accessible, poor contrast, no ARIA, inline styles, icon-only without label.

## Verification

```bash
rg -n "<div.*onclick\|<span.*onclick" --glob "*.html" --glob "*.tsx" --glob "*.jsx"
rg -n "!important" --glob "*.css" --glob "*.scss"
rg -n 'alt=""' --glob "*.html" --glob "*.tsx" | head -10
```
