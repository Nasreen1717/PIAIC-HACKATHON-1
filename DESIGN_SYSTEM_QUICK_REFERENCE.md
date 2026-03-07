# 🎨 Design System - Quick Reference Guide

**Last Updated:** 2026-02-27
**Status:** Production Ready
**Purpose:** Fast lookup guide for developers using the new design system

---

## CSS Variables Quick Reference

### Spacing Scale
```css
/* Use for margins, padding, gaps */
--spacing-xs: 4px;      /* Micro */
--spacing-sm: 8px;      /* Small */
--spacing-md: 16px;     /* Standard */
--spacing-lg: 24px;     /* Large */
--spacing-xl: 32px;     /* Extra Large */
--spacing-2xl: 40px;    /* 2X Large */
--spacing-3xl: 48px;    /* 3X Large */
--spacing-4xl: 64px;    /* 4X Large */
--spacing-5xl: 80px;    /* 5X Large */
--spacing-6xl: 96px;    /* 6X Large */
```

**Usage Example:**
```jsx
<div style={{padding: 'var(--spacing-lg)', margin: 'var(--spacing-md)'}}>
  Content with proper spacing
</div>
```

### Typography Scale
```css
/* Use for font-size */
--font-size-xs: 12px;    /* Captions */
--font-size-sm: 14px;    /* Small text */
--font-size-base: 16px;  /* Body (default) */
--font-size-lg: 18px;    /* Large */
--font-size-xl: 20px;    /* Extra Large */
--font-size-2xl: 24px;   /* 2X Large (h3) */
--font-size-3xl: 28px;   /* 3X Large (h2) */
--font-size-4xl: 40px;   /* 4X Large (h1) */
--font-size-5xl: 48px;   /* 5X Large */
```

**Usage Example:**
```jsx
<p style={{fontSize: 'var(--font-size-lg)'}}>
  Larger paragraph text
</p>
```

### Line Heights
```css
--line-height-tight: 1.2;     /* Headings */
--line-height-heading: 1.3;   /* Section headers */
--line-height-normal: 1.5;    /* UI text */
--line-height-body: 1.6;      /* Body text (optimal) */
--line-height-relaxed: 1.75;  /* Articles */
--line-height-loose: 2;       /* Emphasis */
```

### Letter Spacing
```css
--letter-spacing-tight: -0.02em;  /* Large text */
--letter-spacing-normal: 0em;     /* Body */
--letter-spacing-wide: 0.05em;    /* Labels, uppercase */
```

### Colors
```css
/* Primary Teal */
--ifm-color-primary: #0d9488;           /* Dark teal */
--ifm-color-primary-light: #14b8a6;     /* Light teal */
--ifm-color-primary-lighter: #2dd4bf;   /* Lighter */
--ifm-color-primary-lightest: #5eead4;  /* Lightest */

/* Navy Accents */
--color-navy: #1e293b;
--color-navy-light: #334155;
--color-navy-dark: #0f172a;

/* Semantic Colors */
--color-success: #10b981;      /* Green */
--color-warning: #f59e0b;      /* Yellow */
--color-error: #dc2626;        /* Red */
--color-info: #3b82f6;         /* Blue */

/* Text Colors */
--ifm-font-color-base: #0f172a;        /* Main text */
--ifm-font-color-secondary: #475569;   /* Secondary */
--ifm-font-color-tertiary: #94a3b8;    /* Tertiary */

/* Backgrounds */
--ifm-background-color: #ffffff;           /* Main bg */
--ifm-background-surface-color: #f8fafc;   /* Card bg */
--ifm-background-color-hover: #f8fafc;     /* Hover bg */

/* Borders */
--color-border: #e2e8f0;
```

### Transitions
```css
--transition-fast: 0.2s;      /* 200ms - quick feedback */
--transition-smooth: 0.3s;    /* 300ms - standard */
--transition-slow: 0.5s;      /* 500ms - attention */
--transition-easing: cubic-bezier(0.4, 0, 0.2, 1);
```

---

## Button Component Reference

### Button Sizes
```html
<!-- XS: 32px height -->
<button class="button button--xs button--primary">Tiny</button>

<!-- SM: 40px height -->
<button class="button button--sm button--primary">Small</button>

<!-- MD: 48px height (default) -->
<button class="button button--md button--primary">Medium</button>

<!-- LG: 56px height (recommended for touch) -->
<button class="button button--lg button--primary">Large</button>
```

### Button Variants
```html
<!-- Primary: Use for main actions -->
<button class="button button--md button--primary">Get Started</button>

<!-- Secondary: For alternative actions -->
<button class="button button--md button--secondary">Learn More</button>

<!-- Tertiary: For minimal style -->
<button class="button button--md button--tertiary">View Details</button>

<!-- Danger: For destructive actions -->
<button class="button button--md button--danger">Delete</button>

<!-- Warning: For caution actions -->
<button class="button button--md button--warning">Proceed with Care</button>

<!-- Success: For confirmation -->
<button class="button button--md button--success">Confirm</button>
```

### Button States
```html
<!-- Normal: Auto hover/focus states -->
<button class="button button--lg button--primary">Click Me</button>

<!-- Disabled: Can't be clicked -->
<button class="button button--lg button--primary" disabled>Disabled</button>

<!-- Loading: With spinner icon -->
<button class="button button--lg button--primary">
  <span class="spinner"></span>
  Loading...
</button>
```

### Button Groups
```html
<!-- Horizontal group -->
<div class="button-group">
  <button class="button button--md button--primary">Save</button>
  <button class="button button--md button--secondary">Cancel</button>
</div>

<!-- Vertical group (mobile) -->
<div class="button-group button-group--vertical">
  <button class="button button--lg button--primary">Save</button>
  <button class="button button--lg button--secondary">Cancel</button>
</div>
```

---

## Card Component Reference

### Basic Card
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <p class="card-subtitle">Optional subtitle</p>
  </div>

  <div class="card-body">
    <p>Card content goes here...</p>
  </div>

  <div class="card-footer">
    <button class="button button--sm button--primary">Action</button>
  </div>
</div>
```

### Card Variants
```html
<!-- Elevated card (extra shadow) -->
<div class="card card--elevated">
  Content here
</div>

<!-- Flat card (no shadow/border) -->
<div class="card card--flat">
  Content here
</div>
```

---

## Form Component Reference

### Form Group
```html
<div class="form-group">
  <label for="email">Email Address</label>
  <input type="email" id="email" placeholder="Enter email">
</div>
```

### Required Field
```html
<div class="form-group">
  <label for="name" class="required">Full Name</label>
  <input type="text" id="name" required>
</div>
```

### Form States
```html
<!-- Success state -->
<div class="form-group form-group--success">
  <label for="username">Username</label>
  <input type="text" id="username" value="johndoe">
  <p class="form-group__success-message">✓ Available!</p>
</div>

<!-- Error state -->
<div class="form-group form-group--error">
  <label for="password">Password</label>
  <input type="password" id="password">
  <p class="form-group__error-message">Password is too short</p>
</div>
```

### Inline Form Group
```html
<div class="form-group form-group--inline">
  <label for="subscribe">
    <input type="checkbox" id="subscribe">
    Subscribe to updates
  </label>
</div>
```

---

## Alert Component Reference

### Alert Types
```html
<!-- Note -->
<div class="alert alert--note">
  <p class="alert-description">This is a note for reference</p>
</div>

<!-- Tip -->
<div class="alert alert--tip">
  <p class="alert-description">Here's a helpful tip!</p>
</div>

<!-- Warning -->
<div class="alert alert--warning">
  <p class="alert-description">Please be careful with this action</p>
</div>

<!-- Danger/Error -->
<div class="alert alert--danger">
  <p class="alert-description">This action cannot be undone</p>
</div>

<!-- Success -->
<div class="alert alert--success">
  <p class="alert-description">Operation completed successfully!</p>
</div>
```

### Alert with Title
```html
<div class="alert alert--warning">
  <div class="alert-content">
    <h4 class="alert-title">Important Notice</h4>
    <p class="alert-description">Please read this carefully</p>
  </div>
</div>
```

---

## Animation Classes Reference

### Fade-In-Up Animation
```html
<!-- Single element -->
<div class="fade-in-up">Content fades in from bottom</div>

<!-- Staggered multiple elements -->
<div class="fade-in-up fade-in-up--1">First item (0.1s delay)</div>
<div class="fade-in-up fade-in-up--2">Second item (0.2s delay)</div>
<div class="fade-in-up fade-in-up--3">Third item (0.3s delay)</div>
<div class="fade-in-up fade-in-up--4">Fourth item (0.4s delay)</div>
<div class="fade-in-up fade-in-up--5">Fifth item (0.5s delay)</div>
```

### Other Animation Utilities
```html
<!-- Fade in from top -->
<div class="fade-in-down fade-in-down--1">Content</div>

<!-- Slide in from left -->
<div class="slide-in-left slide-in-left--2">Content</div>

<!-- Slide in from right -->
<div class="slide-in-right slide-in-right--1">Content</div>

<!-- Scale in with fade -->
<div class="scale-in scale-in--1">Content</div>

<!-- Loading animations -->
<div class="spinner">Loading...</div>
<div class="pulse">Pulsing content</div>
<div class="bounce">Bouncing content</div>
```

---

## Responsive Design Breakpoints

### Mobile First Approach
```css
/* Mobile: < 480px (default) */
body { font-size: 14px; }

/* Tablet: 480px - 768px */
@media (min-width: 480px) and (max-width: 768px) {
  body { font-size: 15px; }
}

/* Tablet Large: 768px - 1024px */
@media (min-width: 768px) and (max-width: 1024px) {
  body { font-size: 16px; }
}

/* Desktop: > 1024px */
@media (min-width: 1024px) {
  body { font-size: 16px; }
}

/* Extra Large: > 1440px */
@media (min-width: 1440px) {
  body { font-size: 16px; }
}
```

---

## Accessibility Features

### Focus States
All interactive elements automatically get:
- **Outline:** 2px solid primary teal
- **Offset:** 2px spacing
- **Visible on tab:** Yes
- **Visible on click:** No (removed)

### Skip to Main Content
```html
<a href="#main-content" class="skip-to-main">
  Skip to main content
</a>
```

### Touch Targets
All interactive elements have:
- **Minimum size:** 44×44px
- **Mobile size:** 48×48px recommended
- **Padding:** Sufficient whitespace around

### High Contrast Mode
Automatically activates for users with `prefers-contrast: more`

### Reduced Motion
All animations respect `prefers-reduced-motion: reduce` preference

---

## Dark Mode Usage

### Automatic Adaptation
Elements automatically adapt when `[data-theme="dark"]` is set on `<html>`

### Custom Dark Mode Styles
```css
/* Light mode (default) */
.element {
  color: #0f172a;
  background: #ffffff;
}

/* Dark mode (automatic override) */
[data-theme='dark'] .element {
  color: #e2e8f0;
  background: #0f172a;
}
```

---

## Common Patterns

### Hero Section with Button
```html
<section class="hero">
  <h1 class="fade-in-down">Welcome to ThinkMesh</h1>
  <p class="fade-in-down fade-in-down--1">Learn robotics with AI</p>
  <button class="button button--lg button--primary fade-in-down fade-in-down--2">
    Get Started
  </button>
</section>
```

### Feature Grid with Cards
```html
<div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--spacing-lg)'}}>
  <div class="card scale-in scale-in--1">
    <h3 class="card-title">Feature 1</h3>
    <p class="card-subtitle">Description</p>
  </div>
  <div class="card scale-in scale-in--2">
    <h3 class="card-title">Feature 2</h3>
    <p class="card-subtitle">Description</p>
  </div>
</div>
```

### Form with Validation
```html
<div class="form-group">
  <label for="email" class="required">Email</label>
  <input type="email" id="email" required>
  <p class="form-group__error-message" style={{display: 'none'}}>
    Invalid email format
  </p>
</div>
```

### Alert Notification
```html
<div class="alert alert--success" style={{animation: 'slideInLeft 0.3s ease-out'}}>
  <h4 class="alert-title">Success!</h4>
  <p class="alert-description">Your changes have been saved</p>
</div>
```

---

## Best Practices

### ✅ DO

- **Use CSS variables** instead of hardcoding colors/spacing
- **Use semantic spacing** (spacing-sm, spacing-md, etc.)
- **Use button variants** appropriate for the action
- **Use staggered animations** for lists of items
- **Test dark mode** by toggling theme
- **Test accessibility** with keyboard navigation
- **Test mobile** with viewport sizes 375px, 768px, 1200px

### ❌ DON'T

- **Don't hardcode colors** - Use CSS variables
- **Don't create custom spacing** - Use the spacing scale
- **Don't skip focus states** - They're automatic, just verify them
- **Don't disable animations for everyone** - Use prefers-reduced-motion
- **Don't use pixels** for touch targets - Stick to 44×44px minimum
- **Don't ignore contrast** - Verify 4.5:1 ratio for text

---

## Testing Checklist

- [ ] **Colors:** All text readable in light and dark modes
- [ ] **Buttons:** All variants and sizes work correctly
- [ ] **Forms:** All fields are accessible with keyboard
- [ ] **Cards:** Hover effects smooth and visible
- [ ] **Mobile:** All content readable at 375px width
- [ ] **Dark Mode:** All colors adapted properly
- [ ] **Animations:** Smooth and not too fast
- [ ] **Accessibility:** Keyboard navigation works
- [ ] **Focus:** Outline visible on all interactive elements
- [ ] **Touch:** All buttons are 44×44px minimum

---

## Quick Copy-Paste Examples

### Styled Button
```html
<button class="button button--lg button--primary">Click Me</button>
```

### Card with Content
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">
    <p>Content here</p>
  </div>
</div>
```

### Animated List
```html
<ul>
  <li class="fade-in-up fade-in-up--1">Item 1</li>
  <li class="fade-in-up fade-in-up--2">Item 2</li>
  <li class="fade-in-up fade-in-up--3">Item 3</li>
</ul>
```

### Alert Message
```html
<div class="alert alert--success">
  <p class="alert-description">Success message here</p>
</div>
```

---

## Support & Documentation

- **Full Design System:** See `UI_UX_EXPERT_SKILL_CREATED.txt`
- **Transformation Details:** See `UI_UX_TRANSFORMATION_APPLIED.md`
- **Skill Reference:** See `skills/user/ui-ux-expert/SKILL.md`

---

**Last Updated:** 2026-02-27
**Status:** Production Ready
**Version:** 1.0

Happy designing! 🎨

