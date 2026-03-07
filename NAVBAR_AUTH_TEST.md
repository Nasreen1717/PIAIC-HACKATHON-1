# Navbar Authentication UI - End-to-End Test Checklist

## Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000` (or dev server)
- Database connected and migrations applied

## Setup Instructions

### 1. Start Backend
```bash
cd /mnt/d/code/Hackathon-1/backend
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend (in new terminal)
```bash
cd /mnt/d/code/Hackathon-1/Front-End-Book
npm run start
```

The frontend will open at `http://localhost:3000`

---

## Test Cases

### ✅ Test 1: Initial Load (Not Authenticated)
**Location**: Navbar top-right corner
**Expected**:
- "Sign In" link (blue text)
- "Sign Up" button (purple gradient)

**Steps**:
1. Load the app in browser
2. Look at navbar top-right
3. Verify buttons are visible and properly styled

**Pass Criteria**: Both buttons visible and clickable

---

### ✅ Test 2: Sign Up Flow
**Location**: Sign Up Page → Navbar
**Expected**: Navbar updates after signup

**Steps**:
1. Click "Sign Up" button in navbar
2. Fill form:
   - Email: `test@example.com`
   - Password: `TestPassword123`
   - Name: `Test User`
3. Submit
4. Check navbar

**Pass Criteria**:
- After signup, navbar shows "Test User" or email instead of Sign In/Sign Up
- User data saved to localStorage
- No console errors

---

### ✅ Test 3: User Menu Dropdown
**Location**: Navbar user button
**Expected**: Dropdown menu appears

**Steps**:
1. Click on user name in navbar
2. Observe dropdown menu

**Pass Criteria**:
- Dropdown appears below user button
- Shows user email
- Shows "View Profile" link
- Shows "Sign Out" button
- Dropdown has proper styling and shadow

---

### ✅ Test 4: View Profile
**Location**: User menu → View Profile
**Expected**: Navigate to profile page

**Steps**:
1. Open user menu dropdown
2. Click "View Profile"

**Pass Criteria**:
- Navigates to profile page
- Profile page loads correctly
- Shows user information

---

### ✅ Test 5: Sign Out
**Location**: User menu → Sign Out
**Expected**: Return to unauthenticated state

**Steps**:
1. Open user menu dropdown
2. Click "Sign Out"

**Pass Criteria**:
- Redirects to home page
- Navbar shows "Sign In" and "Sign Up" buttons again
- localStorage cleared (no auth_token, no auth_user)
- No console errors

---

### ✅ Test 6: Dark Mode Toggle
**Location**: Navbar theme toggle
**Expected**: Dropdown styling adapts

**Steps**:
1. Click dark/light mode toggle in navbar
2. Click on user name to open dropdown

**Pass Criteria**:
- Dropdown background adapts to theme
- Text remains readable
- Colors match Docusaurus dark theme
- No layout shift or styling issues

---

### ✅ Test 7: Responsive Design
**Location**: Navbar (mobile view)
**Expected**: Auth UI adapts to mobile

**Steps**:
1. Open DevTools
2. Toggle device toolbar (mobile view)
3. Resize to different breakpoints:
   - 375px (iPhone SE)
   - 768px (Tablet)
   - 1024px (Tablet landscape)

**Pass Criteria**:
- Auth buttons remain visible and clickable
- Text truncates appropriately (email max-width: 100px on mobile)
- Dropdown menu doesn't overflow screen
- No layout shift

---

### ✅ Test 8: Sign In Flow
**Location**: Sign In Page → Navbar
**Expected**: Login with existing user

**Steps**:
1. Sign out (from Test 5)
2. Click "Sign In" in navbar
3. Enter credentials:
   - Email: `test@example.com`
   - Password: `TestPassword123`
4. Submit
5. Check navbar

**Pass Criteria**:
- Successfully logs in
- Navbar shows user name/email
- Redirects to home page after login

---

### ✅ Test 9: Remember Me Functionality
**Location**: Sign In Page
**Expected**: Token expiration based on checkbox

**Steps**:
1. Sign out
2. Go to Sign In
3. Check "Remember me for 30 days"
4. Sign in
5. Check token in localStorage

**Pass Criteria**:
- Token stored in localStorage
- Token remains after page refresh
- Without "Remember me": token expires after 7 days
- With "Remember me": token expires after 30 days

---

### ✅ Test 10: Page Refresh Persistence
**Location**: Any page when authenticated
**Expected**: User stays logged in after refresh

**Steps**:
1. Sign up and login
2. Verify user appears in navbar
3. Refresh page (F5)
4. Check navbar

**Pass Criteria**:
- User data restored from localStorage
- Navbar still shows user name/email
- No "Loading..." spinner (or very brief)
- AuthContext state maintained

---

### ✅ Test 11: Console Error Check
**Location**: DevTools Console
**Expected**: No errors

**Steps**:
1. Open DevTools Console (F12)
2. Go through all tests above
3. Look for errors (red items)

**Pass Criteria**:
- No red errors in console
- No CORS errors
- No async/await errors
- Only info/warn messages from app

---

### ✅ Test 12: Different Screen Sizes
**Location**: Navbar across all sizes
**Expected**: Auth UI adapts gracefully

**Breakpoints**:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

**Pass Criteria**:
- Navbar doesn't overflow at any size
- Text is readable
- Buttons are clickable with appropriate touch targets (min 44px)
- Dropdown doesn't cut off edges

---

## Debugging Tips

### If buttons don't show:
1. Check browser console for errors
2. Verify AuthProvider is wrapping the app (Root.js)
3. Verify navbarItem type is registered in ComponentTypes.js
4. Check docusaurus.config.js has auth item

### If dropdown doesn't appear:
1. Verify UserMenu state management
2. Check CSS z-index (should be 1000)
3. Verify parent container has `position: relative`

### If dark mode doesn't work:
1. Check `html[data-theme='dark']` selectors in CSS
2. Verify dark mode toggle exists in theme
3. Check CSS file loaded (check Network tab)

### If auth doesn't persist:
1. Check localStorage in DevTools (Application tab)
2. Verify auth_token and auth_user are stored
3. Check AuthContext initialization in Root.js

### If API calls fail:
1. Verify backend is running on port 8000
2. Check CORS headers in backend response
3. Check network tab for actual error response

---

## Test Results Summary

```
Test 1:  Initial Load                    [ ]
Test 2:  Sign Up Flow                    [ ]
Test 3:  User Menu Dropdown              [ ]
Test 4:  View Profile                    [ ]
Test 5:  Sign Out                        [ ]
Test 6:  Dark Mode                       [ ]
Test 7:  Responsive Design               [ ]
Test 8:  Sign In Flow                    [ ]
Test 9:  Remember Me                     [ ]
Test 10: Page Refresh Persistence        [ ]
Test 11: Console Error Check             [ ]
Test 12: Different Screen Sizes          [ ]

Overall Status: [ ] PASS [ ] NEEDS FIXES
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| NavbarItem not recognized | Add type to ComponentTypes.js and restart dev server |
| UserMenu component not rendering | Verify AuthProvider wraps Root component |
| Dropdown styling broken | Check CSS module imports and Docusaurus theme context |
| Auth not persisting | Check localStorage.getItem('auth_token') in console |
| Backend API errors | Ensure backend is running and CORS is enabled |
| Dark mode colors wrong | Verify `html[data-theme='dark']` selectors in CSS |
| Mobile buttons overflow | Check responsive CSS media queries |
| Token expired errors | Check JWT expiration and refresh logic |

---

## Performance Checklist

- [ ] No unnecessary re-renders
- [ ] Dropdown opens immediately (< 100ms)
- [ ] Page refresh doesn't cause flash
- [ ] localStorage operations are synchronous (no lag)
- [ ] API calls show loading state

---

## Accessibility Checklist

- [ ] Links have proper focus styles
- [ ] Buttons have proper contrast
- [ ] Hover states indicate interactivity
- [ ] Mobile touch targets > 44px
- [ ] Keyboard navigation works (Tab, Enter)

---

## Next Steps After Testing

1. ✅ All tests pass → Ready for production
2. ❌ Some tests fail → Debug using tips above
3. ⚠️ Design issues → Update CSS modules
4. 🔧 Performance issues → Check React DevTools Profiler

Happy testing! 🚀
