# UI/UX Expert Skill - Professional Design Standards

## Overview
Comprehensive reference guide for professional UI/UX design decisions, component creation, and quality assurance. Use this skill to ensure consistent, accessible, and beautiful interface design across the entire platform.

---

## 🎯 When to Trigger This Skill

Use the UI/UX Expert skill when:
- **Creating new components** (buttons, cards, forms, navigation)
- **Designing new pages or sections**
- **Implementing color schemes or themes**
- **Making layout or spacing decisions**
- **Adding animations or transitions**
- **Reviewing design quality**
- **Ensuring accessibility compliance**
- **Establishing design systems**
- **Making typography choices**
- **Optimizing user experience**

**Trigger Pattern**: `/ui-ux-expert [task]`

---

# SECTION 1: VISUAL HIERARCHY & DESIGN PRINCIPLES

## 1.1 Visual Hierarchy Principles

### Primary Goal
Guide user attention through intentional size, color, and position emphasis.

### Hierarchy Levels
```
Level 1 (Most Important):    Largest, brightest, most prominent
Level 2 (Important):          Medium size, secondary emphasis
Level 3 (Supporting):         Smaller, lighter, supplementary
Level 4 (Background):         Minimal emphasis, supporting role
```

### Typography Hierarchy
```
H1 (Headline):     2.5rem (40px)   - Primary page title
H2 (Heading):      1.75rem (28px)  - Section headers
H3 (Subheading):   1.25rem (20px)  - Category titles
Body:              1rem (16px)     - Main content
Small:             0.875rem (14px) - Secondary info
Tiny:              0.75rem (12px)  - Captions, labels
```

### Color Hierarchy
```
Primary:    Brand color (#0d9488) - Main actions, emphasis
Secondary:  Gray-600 (#475569)     - Supporting text
Tertiary:   Gray-400 (#94a3b8)    - Subtle info
Disabled:   Gray-300 (#cbd5e1)    - Inactive states
```

### Nielsen's 10 Usability Heuristics
1. **System Status Visibility** - Real-time feedback
2. **Match Real World** - User language & conventions
3. **User Control** - Undo, redo, easy exit
4. **Error Prevention** - Prevent before recovering
5. **Aesthetic & Minimal** - Remove unnecessary elements
6. **Help Documentation** - Searchable, task-focused
7. **Flexibility** - Shortcuts, customization
8. **Consistency** - Patterns, terminology, standards
9. **Error Messages** - Plain language, solutions
10. **Recognition** - Visible options, minimize memory load

---

# SECTION 2: COLOR THEORY & SYSTEMS

## 2.1 Brand Color Palette

### Primary Brand: Teal
```
Light Mode:      #0d9488 (primary), #0f766e (dark), #5eead4 (light)
Dark Mode:       #14b8a6 (primary), #2dd4bf (light), #5eead4 (lightest)
Psychology:      Trust, innovation, technology, calm
Usage:           Primary actions, links, emphasis
```

### Secondary: Navy
```
Light Mode:      #1e293b (secondary), #0f172a (dark)
Dark Mode:       #334155 (navy), #0f172a (background)
Psychology:      Stability, professionalism, authority
Usage:           Headers, text, backgrounds
```

### Semantic Colors
```
Success (Green):  #10b981 on #d1fae5 background
Warning (Amber):  #f59e0b on #fef3c7 background
Error (Red):      #ef4444 on #fee2e2 background
Info (Blue):      #3b82f6 on #dbeafe background
```

## 2.2 The 60-30-10 Color Rule

```
60% - Dominant Color (Background)
  Light Mode: #ffffff (white)
  Dark Mode:  #0f172a (dark navy)

30% - Secondary Color (Surfaces)
  Light Mode: #f8fafc (light gray)
  Dark Mode:  #1e293b (navy)

10% - Accent Color (Highlights)
  Both: #0d9488 / #14b8a6 (teal)
```

## 2.3 WCAG Contrast Compliance

### Minimum Ratios
```
Normal Text:      4.5:1 (AA standard)
Large Text:       3:1 (AA standard)
Graphics/UI:      3:1 (AA standard)
AAA Enhanced:     7:1
```

### Light Mode Examples
```
Black on white:         20:1 ✓ Excellent
Navy on light gray:     10:1 ✓ Excellent
Teal on white:           5:1 ✓ Compliant
```

### Dark Mode Examples
```
Light text on navy:     15:1 ✓ Excellent
Light gray on navy:     10:1 ✓ Excellent
Bright teal on dark:     6:1 ✓ Compliant
```

---

# SECTION 3: TYPOGRAPHY & SPACING

## 3.1 Typographic Scale (8pt Grid)

### Font Sizes
```
Tiny:       12px (0.75rem)  - Captions, labels
Small:      14px (0.875rem) - Secondary text
Base:       16px (1rem)     - Body text, default
Large:      18px (1.125rem) - Larger content
XL:         20px (1.25rem)  - Subheadings
2XL:        28px (1.75rem)  - Section headers
3XL:        40px (2.5rem)   - Page titles
```

### Font Families
```
Primary:     Inter (modern, clean, legible)
Fallback:    -apple-system, BlinkMacSystemFont, 'Segoe UI'
Monospace:   Courier New, Monaco, Consolas
```

### Font Weights
```
Light (300):     Subtle text, captions
Regular (400):   Body text, default
Semibold (600):  Subheadings, important
Bold (700):      Headlines, strong emphasis
```

### Line Heights
```
Headings:        1.2 (tight, strong)
Subheadings:     1.3 (medium, readable)
Body:            1.6 (spacious, easy reading)
Code:            1.5 (clear, scannable)
```

## 3.2 Spacing System (8pt Grid)

### Base Unit: 8px
All spacing must be multiples of 8px.

### Spacing Scale
```
0px    - 0    (no spacing)
4px    - 0.5  (micro-spacing)
8px    - 1    (base unit, padding)
12px   - 1.5  (combined elements)
16px   - 2    (standard spacing)
24px   - 3    (medium spacing)
32px   - 4    (large spacing)
48px   - 6    (extra large)
64px   - 8    (section spacing)
```

### Component Padding
```
Buttons:        8px 16px (vertical × horizontal)
Cards:          16px or 24px
Forms:          16px container, 8px label
Lists:          8px item spacing
Page:           16px mobile, 24px desktop
```

---

# SECTION 4: LAYOUT & GRID SYSTEMS

## 4.1 12-Column Grid System

### Breakpoints
```
Mobile:        320px - 767px   (1 column, 4-column grid)
Tablet:        768px - 1023px  (8-column grid)
Desktop:       1024px - 1279px (12-column grid)
Large:         1280px+         (full 12-column)
```

### Gutter Spacing
```
Mobile:        8px
Tablet:        16px (8px each side)
Desktop:       24px (12px each side)
```

### Container
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
  width: 100%;
  box-sizing: border-box;
}

@media (min-width: 768px) {
  .container { padding: 0 24px; }
}
```

---

# SECTION 5: COMPONENT DESIGN PATTERNS

## 5.1 Button Component

### States
```
Default:  Base color, visible
Hover:    Darker shade, shadow
Active:   Pressed appearance
Focus:    Visible focus ring
Disabled: Gray, no interaction
Loading:  Spinner, disabled
```

### Button Types

**Primary Button**
```css
.button--primary {
  background: #0d9488;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
}

.button--primary:hover {
  background: #0f766e;
}

.button--primary:focus {
  outline: 2px solid #0d9488;
  outline-offset: 2px;
}
```

**Secondary Button**
```css
.button--secondary {
  background: transparent;
  color: #0d9488;
  border: 2px solid #0d9488;
  padding: 6px 14px;
  border-radius: 6px;
  font-weight: 600;
}

.button--secondary:hover {
  background: #0d9488;
  color: white;
}
```

### Button Sizes
```
Small:    8px 12px, 12px text, 16px icon
Regular:  8px 16px, 14px text, 20px icon
Large:    12px 20px, 16px text, 24px icon
XL:       16px 24px, 18px text, 28px icon
```

## 5.2 Input Fields

### Text Input
```css
.input {
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: var(--color-input-bg);
  color: var(--color-text);
  transition: all 0.2s ease;
}

.input:hover {
  border-color: #0d9488;
}

.input:focus {
  outline: none;
  border-color: #0d9488;
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1);
}

.input:disabled {
  background: #f1f5f9;
  cursor: not-allowed;
}
```

### Form Groups
```css
.form-group {
  margin-bottom: 16px;
}

.label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 14px;
}

.help-text {
  margin-top: 4px;
  font-size: 12px;
  color: #94a3b8;
}

.error-message {
  margin-top: 4px;
  font-size: 12px;
  color: #ef4444;
}
```

## 5.3 Cards

### Card Structure
```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-header {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.card-content {
  padding-top: 12px;
}
```

## 5.4 Alerts & Admonitions

### Alert Types
```css
.alert {
  padding: 12px 16px;
  border-left: 4px solid;
  border-radius: 4px;
  margin-bottom: 16px;
}

.alert--success {
  background: #ecfdf5;
  border-color: #10b981;
  color: #047857;
}

.alert--warning {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

.alert--error {
  background: #fee2e2;
  border-color: #ef4444;
  color: #7f1d1d;
}

.alert--info {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1e40af;
}
```

---

# SECTION 6: ANIMATION & MOTION

## 6.1 Animation Timing

### Duration Guidelines
```
Micro-interactions:   0.15s - 0.3s
Transitions:          0.3s - 0.5s
Navigation:           0.3s - 0.6s
Complex animations:   0.6s - 1s+
```

### Easing Functions
```
Quick interactions:   ease-out
Smooth transitions:   ease-in-out
Emphasis:             cubic-bezier(0.34, 1.56, 0.64, 1)
Slow reveal:          ease-in
```

## 6.2 Common Animations

### Fade In
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
```

### Slide Down
```css
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-down {
  animation: slideDown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### Scale Up
```css
@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

## 6.3 Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

# SECTION 7: ACCESSIBILITY STANDARDS (WCAG 2.1 AA)

## 7.1 Color Contrast
```
✓ Normal text:   4.5:1 minimum
✓ Large text:    3:1 minimum (18pt+ or 14pt+ bold)
✓ Graphics/UI:   3:1 minimum
```

## 7.2 Keyboard Navigation
```
✓ Tab order logical
✓ Focus indicators visible
✓ No keyboard traps
✓ Arrow keys for navigation
✓ Enter/Space for activation
✓ Esc to close modals
```

## 7.3 Forms
```
✓ Labels associated with inputs
✓ Required fields marked
✓ Error messages linked
✓ Clear validation feedback
✓ Sufficient spacing
```

## 7.4 Images
```
✓ Meaningful alt text
✓ Decorative images: alt=""
✓ Complex images: description link
✓ Icons: aria-label or title
```

## 7.5 Focus Management

### Visible Focus Indicator
```css
:focus {
  outline: 2px solid #0d9488;
  outline-offset: 2px;
}

:focus-visible {
  outline: 2px solid #0d9488;
  outline-offset: 2px;
}

/* Skip to content link */
.skip-to-content {
  position: absolute;
  top: -40px;
  left: 0;
  background: #0d9488;
  color: white;
  padding: 8px 16px;
}

.skip-to-content:focus {
  top: 0;
}
```

## 7.6 Semantic HTML
```html
<header>     <!-- Page header -->
<nav>        <!-- Navigation -->
<main>       <!-- Main content -->
<article>    <!-- Article -->
<section>    <!-- Section -->
<aside>      <!-- Sidebar -->
<footer>     <!-- Footer -->

<!-- Proper heading hierarchy -->
<h1>Title</h1>
<h2>Section</h2>
<h3>Subsection</h3>

<!-- Form structure -->
<form>
  <label for="input">Label</label>
  <input id="input" type="text">
</form>
```

---

# SECTION 8: DARK MODE BEST PRACTICES

## 8.1 Color Adaptation

### Light Mode → Dark Mode
```
Light Mode:       Dark Mode:
#ffffff    →      #0f172a
#f8fafc    →      #1e293b
#0f172a    →      #e2e8f0
#475569    →      #cbd5e1
#1e293b    →      #0a0f1a (code)
#0d9488    →      #14b8a6 (brighter primary)
```

## 8.2 Component Adaptations

### CSS Variables Approach
```css
:root {
  --color-primary: #0d9488;
  --color-bg: #ffffff;
  --color-text: #0f172a;
}

[data-theme='dark'] {
  --color-primary: #14b8a6;
  --color-bg: #0f172a;
  --color-text: #e2e8f0;
}

/* Components use variables */
button {
  background: var(--color-primary);
  color: white;
}
```

## 8.3 Dark Mode Shadows
```css
/* Light Mode */
.card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

/* Dark Mode - Lighter shadows */
[data-theme='dark'] .card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.40);
}
```

---

# SECTION 9: RESPONSIVE DESIGN

## 9.1 Mobile-First Approach

```css
/* Start mobile */
.container {
  padding: 12px;
  grid-template-columns: 1fr;
}

/* Enhance tablet */
@media (min-width: 768px) {
  .container {
    padding: 16px;
    grid-template-columns: 1fr 1fr;
  }
}

/* Expand desktop */
@media (min-width: 1024px) {
  .container {
    padding: 24px;
    grid-template-columns: 1fr 1fr 1fr;
  }
}
```

## 9.2 Touch-Friendly Design

### Tap Target Size
```
Minimum: 44×44px
Preferred: 48×48px
Spacing: 8px between targets
```

### Touch-Friendly Spacing
```css
.menu-item {
  padding: 12px 16px;  /* More padding */
  margin: 4px 0;       /* More spacing */
  min-height: 44px;
}
```

---

# SECTION 10: QUALITY CHECKLIST

## Design Quality ✓
- [ ] Consistent spacing (8px multiples)
- [ ] Consistent typography scale
- [ ] Color palette matches brand
- [ ] All states defined (hover, focus, active, disabled)
- [ ] Icons consistent style
- [ ] Alignment perfect
- [ ] Whitespace intentional
- [ ] No overly long lines (max 80 chars)
- [ ] Consistent border radius (6px)
- [ ] Shadow hierarchy defined

## Accessibility ✓
- [ ] Contrast >4.5:1 (WCAG AA)
- [ ] Focus indicators visible
- [ ] Keyboard navigation works
- [ ] Semantic HTML
- [ ] Labels for all inputs
- [ ] Alt text for images
- [ ] ARIA labels where needed
- [ ] Skip links present
- [ ] Screen reader compatible

## Responsiveness ✓
- [ ] Mobile layout defined
- [ ] Tablet layout defined
- [ ] Desktop layout defined
- [ ] Touch targets 44×44px+
- [ ] No horizontal scroll
- [ ] Images responsive
- [ ] Text readable all sizes
- [ ] Tested on real devices

## Dark Mode ✓
- [ ] All colors adapt
- [ ] Contrast maintained
- [ ] Shadows appropriate
- [ ] Code blocks styled
- [ ] Links visible
- [ ] Images readable

## Components ✓
- [ ] All states present
- [ ] Consistent styling
- [ ] Well-documented
- [ ] Loading state shown
- [ ] Error state clear
- [ ] Success state visible

---

## 📚 Quick Reference

### Colors
```
Primary:  #0d9488 (light) / #14b8a6 (dark)
Navy:     #1e293b / #0f172a
Success:  #10b981
Warning:  #f59e0b
Error:    #ef4444
```

### Spacing
```
8px: 1 unit
16px: 2 units
24px: 3 units
32px: 4 units
```

### Typography
```
H1: 2.5rem
H2: 1.75rem
H3: 1.25rem
Body: 1rem
```

### Breakpoints
```
Mobile: <768px
Tablet: 768px - 1024px
Desktop: >1024px
```

---

**Status**: ✅ READY FOR REFERENCE

Use this skill file for all UI/UX design work.

