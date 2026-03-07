# Theme Toggle (Light/Dark Mode) Guide

## 📍 Location

The **Light/Dark Mode Toggle** icon is located in the **top-right corner of the navbar**, next to the user menu.

### Visual Position:
```
┌─────────────────────────────────────────────────┐
│ Logo │ HOME MODULE 1 MODULE 2 MODULE 3 MODULE 4 │  ☀️/🌙  Test User⚙️ │
└─────────────────────────────────────────────────┘
                                                    ↑
                                             Theme Toggle
```

## 🎨 What You'll See

### Light Mode (Default)
- **Icon:** ☀️ (Sun symbol)
- **Color:** Teal (#0d9488)
- **Tooltip:** "Switch to dark mode" (on hover)

### Dark Mode
- **Icon:** 🌙 (Moon symbol)
- **Color:** Amber/Yellow (#fbbf24)
- **Tooltip:** "Switch to light mode" (on hover)

## ✨ Features

### Hover Effects
- Icon grows slightly (scale 1.1)
- Background becomes semi-transparent with theme color
- Smooth animation (0.3s)

### Click Behavior
- Instant theme switch
- All elements update immediately
- Preference saved in browser

### Keyboard Navigation
- **Tab:** Focus on toggle
- **Enter/Space:** Toggle theme
- **Focus Outline:** 2px solid teal

### Mobile Responsive
- Same position on all screen sizes
- Touch-friendly (44x44px minimum)
- Works on tablets and phones

## 🔧 Configuration

### Location in Code:
- **Configuration:** `/Front-End-Book/docusaurus.config.js`
  - Lines 196-200: `colorMode` settings
  - `disableSwitch: false` → Toggle enabled
  - `defaultMode: 'light'` → Starts in light mode

- **Styling:** `/Front-End-Book/src/css/navbar.css`
  - Lines 578-627: Complete toggle styling
  - Light mode colors: Teal (#0d9488)
  - Dark mode colors: Amber (#fbbf24)

### CSS Classes:
```css
.navbar__item.navbar__item--colorModeToggle {
  /* Container for toggle button */
}

[class*='toggle'][class*='button'] {
  /* Toggle button styles */
}
```

## 🎯 Styling Details

### Light Mode Theme
```css
Background Color: #ffffff (white)
Text Color: #0f172a (dark navy)
Primary Color: #0d9488 (teal)
Accent: #14b8a6 (light teal)
```

### Dark Mode Theme
```css
Background Color: #0f172a (dark navy)
Text Color: #e2e8f0 (light gray)
Primary Color: #0d9488 (teal - stays same)
Accent: #fbbf24 (yellow)
```

## 🚀 How It Works

### 1. **User Clicks Toggle**
   - JavaScript detects click
   - Theme preference updates in browser storage
   - `data-theme` attribute changes on `<html>`

### 2. **CSS Responds**
   - Light mode: Default CSS variables apply
   - Dark mode: `[data-theme='dark']` selector activates
   - All colors update instantly

### 3. **Persistence**
   - Preference saved in `localStorage`
   - Persists across browser sessions
   - Respects system preference if not explicitly set

## ✅ Testing Checklist

- [ ] Click toggle in top-right navbar
- [ ] Light mode → Dark mode transition works
- [ ] Dark mode → Light mode transition works
- [ ] Icon changes (☀️ ↔️ 🌙)
- [ ] Colors update on all pages
- [ ] Hover effect works (icon scales + background changes)
- [ ] Works on desktop (>996px)
- [ ] Works on tablet (768-996px)
- [ ] Works on mobile (<768px)
- [ ] Keyboard navigation (Tab → Focus → Enter)
- [ ] Preference persists after page reload
- [ ] Preference persists after browser close/reopen

## 🎨 Theme Colors Applied

### Light Mode Elements
- Navbar: White background
- Text: Dark navy (#0f172a)
- Links: Teal (#0d9488)
- Buttons: Teal with hover effects
- Cards: Light backgrounds
- Code blocks: Dark theme on light background

### Dark Mode Elements
- Navbar: Dark navy (#1e293b)
- Text: Light gray (#e2e8f0)
- Links: Teal (#0d9488)
- Buttons: Teal with hover effects
- Cards: Dark backgrounds
- Code blocks: Light theme on dark background

## 📱 Responsive Behavior

### Desktop (>996px)
- Toggle positioned in navbar right section
- Full-size 44x44px
- Visible alongside auth items

### Tablet (768-996px)
- Toggle remains visible
- Same size and positioning
- Adjusts with responsive navbar

### Mobile (<768px)
- Toggle remains accessible
- May move into mobile menu if space constrained
- Touch-friendly (44x44px minimum)

## 🐛 Troubleshooting

### Toggle Not Visible
1. Check if `disableSwitch: false` in docusaurus.config.js
2. Clear browser cache
3. Check CSS isn't hidden: `.navbar__item.navbar__item--colorModeToggle { display: flex !important; }`

### Theme Not Changing
1. Ensure JavaScript is enabled
2. Check browser console for errors
3. Try clearing localStorage: `localStorage.clear()`

### Styling Issues
1. Check navbar.css imports
2. Verify CSS variables in custom.css
3. Look for conflicting CSS rules

## 📚 Related Files

- **Config:** `Front-End-Book/docusaurus.config.js` (Lines 196-200)
- **Styling:** `Front-End-Book/src/css/navbar.css` (Lines 578-627)
- **Theme Colors:** `Front-End-Book/src/css/custom.css` (Lines 16-100)
- **Dark Mode Variables:** `Front-End-Book/src/css/custom.css` (Lines 280+)

---

**Status:** ✅ **WORKING & FULLY STYLED**

The theme toggle is fully functional, accessible, and provides a smooth user experience across all devices!
