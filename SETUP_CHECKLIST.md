# 🎬 Hero Section Video Background - Quick Setup Checklist

## Phase 1: Code Implementation ✅ COMPLETE

- [x] Updated `Front-End-Book/src/pages/index.js` with video element and overlay
- [x] Updated `Front-End-Book/src/pages/index.module.css` with video and overlay styling
- [x] Added responsive design (desktop, tablet, mobile)
- [x] Enhanced text visibility with colors and shadows
- [x] Preserved all animations
- [x] Added accessibility features

## Phase 2: Prepare Video File 🎯 TODO

### Video Preparation
- [ ] Obtain/record your robot/robotics demonstration video
- [ ] Convert to MP4 format if needed:
  ```bash
  ffmpeg -i input.mov -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k output.mp4
  ```
- [ ] Verify compression (target <5MB):
  ```bash
  ls -lh output.mp4
  ```
- [ ] Place file at: `Front-End-Book/static/videos/hero-video.mp4`

### Poster Image
- [ ] Extract first frame from video:
  ```bash
  ffmpeg -i Front-End-Book/static/videos/hero-video.mp4 \
    -ss 00:00:00 -vframes 1 \
    -vf scale=1920:1080 \
    Front-End-Book/static/img/hero-poster.jpg
  ```
- [ ] Place file at: `Front-End-Book/static/img/hero-poster.jpg`

## Phase 3: Testing 🔍 TODO

### Local Testing
- [ ] Navigate to project: `cd Front-End-Book`
- [ ] Start development server: `npm run start`
- [ ] Check video loads (allow time for first play)
- [ ] Verify text is readable over video
- [ ] Check that no audio plays (muted)
- [ ] Test responsive behavior:
  - [ ] Desktop view (>1024px)
  - [ ] Tablet view (768-1024px)
  - [ ] Mobile view (<768px)
- [ ] Test animations:
  - [ ] Title fades in + slides down
  - [ ] Subtitle fades in + slides up
  - [ ] Description fades in + slides up
  - [ ] Buttons fade in + slide up
  - [ ] Floating circles pulse smoothly
- [ ] Test button interactions:
  - [ ] Primary button ("Start Learning")
  - [ ] Secondary button ("Explore Modules")
  - [ ] Hover effects work
  - [ ] Click actions work

### Browser Testing (if possible)
- [ ] Chrome/Edge (desktop)
- [ ] Firefox (desktop)
- [ ] Safari (desktop)
- [ ] Safari (iOS)
- [ ] Chrome (Android)

### Accessibility Testing
- [ ] Check text contrast (white on dark background)
- [ ] Verify keyboard navigation works
- [ ] Test with screen reader (teal subtitle should be visible)
- [ ] Check reduced motion support:
  ```
  Preferences > Accessibility > Display > Reduce motion (macOS)
  ```

## Phase 4: Customization (Optional) 🎨 TODO

### If Video is Too Dark
- [ ] Increase brightness filter in CSS:
  ```css
  filter: brightness(0.9);  /* from 0.8 */
  ```

### If Video is Too Bright
- [ ] Decrease brightness filter in CSS:
  ```css
  filter: brightness(0.7);  /* from 0.8 */
  ```

### If Text is Not Readable Enough
- [ ] Increase overlay opacity:
  ```css
  background: linear-gradient(
    to right,
    rgba(15, 23, 42, 0.90) 0%,    /* increased from 0.85 */
    rgba(15, 23, 42, 0.85) 40%,   /* increased from 0.75 */
    rgba(15, 23, 42, 0.75) 100%   /* increased from 0.65 */
  );
  ```

### If Video Causes Performance Issues on Mobile
- [ ] Add in `index.module.css`:
  ```css
  @media (max-width: 768px) {
    .heroBackgroundVideo {
      display: none;
    }
    .heroBanner {
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
  }
  ```

## Phase 5: Final Review ✅ TODO

- [ ] Code review:
  - [ ] No syntax errors
  - [ ] No console warnings
  - [ ] Proper CSS naming conventions
  - [ ] Responsive breakpoints work
- [ ] Visual review:
  - [ ] Matches reference design (ui.jpg)
  - [ ] Text colors are correct
  - [ ] Overlay opacity is appropriate
  - [ ] Animations are smooth
  - [ ] No layout shifts
- [ ] Performance review:
  - [ ] Video loads quickly
  - [ ] No stuttering on animation
  - [ ] Mobile performance acceptable
  - [ ] Network tab shows <5MB video

## Phase 6: Deployment 🚀 TODO

- [ ] Commit changes:
  ```bash
  git add Front-End-Book/src/pages/
  git add Front-End-Book/static/videos/
  git add Front-End-Book/static/img/
  git commit -m "feat: Add background video to hero section with dark overlay"
  ```
- [ ] Push to remote:
  ```bash
  git push origin 010-content-personalization
  ```
- [ ] Create Pull Request on GitHub
- [ ] Review and merge to main
- [ ] Deploy to production

---

## 📝 File Checklist

### Code Files (Already Updated)
- [x] `Front-End-Book/src/pages/index.js`
- [x] `Front-End-Book/src/pages/index.module.css`

### Video Assets (Need to Add)
- [ ] `Front-End-Book/static/videos/hero-video.mp4` (your video file)
- [ ] `Front-End-Book/static/img/hero-poster.jpg` (first frame image)

### Documentation (Already Created)
- [x] `HERO_SECTION_SETUP.md` - Complete setup guide
- [x] `IMPLEMENTATION_SUMMARY.md` - Overview of changes
- [x] `SETUP_CHECKLIST.md` - This file
- [x] `/static/videos/README.md` - Video specifications

---

## 🎬 Video File Commands Quick Reference

### Convert MOV to MP4 (Optimized)
```bash
ffmpeg -i input.mov \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -c:a aac \
  -b:a 128k \
  -vf scale=1920:1080 \
  Front-End-Book/static/videos/hero-video.mp4
```

### Extract Poster Image (First Frame)
```bash
ffmpeg -i Front-End-Book/static/videos/hero-video.mp4 \
  -ss 00:00:00 \
  -vframes 1 \
  -vf scale=1920:1080 \
  Front-End-Book/static/img/hero-poster.jpg
```

### Check File Size
```bash
ls -lh Front-End-Book/static/videos/hero-video.mp4
# Should be <5MB
```

### Verify Video Codec
```bash
ffmpeg -i Front-End-Book/static/videos/hero-video.mp4
# Look for: Video: h264, Video: libx264
```

---

## ⚠️ Troubleshooting

### Video doesn't play
1. Check file path is correct: `/Front-End-Book/static/videos/hero-video.mp4`
2. Verify MP4 codec: `ffmpeg -i hero-video.mp4 2>&1 | grep Video`
3. Ensure file size <5MB: `ls -lh hero-video.mp4`

### Text not readable
1. Check overlay opacity is 0.85 (dark enough)
2. Verify text colors:
   - Title: #ffffff (white)
   - Subtitle: #14b8a6 (teal)
   - Description: #e2e8f0 (light gray)
3. Try increasing overlay opacity to 0.90

### Video stutters
1. Reduce video bitrate: Add `-b:v 2M` to ffmpeg command
2. Reduce resolution: Change `scale=1280:720`
3. Increase compression: Use `-crf 25` instead of `-crf 23`

### Animation not smooth
1. Check browser DevTools Performance tab
2. Reduce floating circles animation complexity
3. Check for JS errors in console

---

## 📞 Support

For more details:
- **Setup Instructions:** See `HERO_SECTION_SETUP.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Video Specs:** See `/static/videos/README.md`
- **Design Reference:** See `ui.jpg` in project root

---

## ✨ Key Points to Remember

1. **Video Format:** MP4 with H.264 codec (maximum compatibility)
2. **File Size:** Keep <5MB for fast loading
3. **Duration:** 10-30 seconds recommended
4. **Muted:** Must be muted (autoplay requirement)
5. **Aspect Ratio:** 16:9 (1920x1080 preferred)
6. **Text Colors:** White, Teal, Light Gray (optimized for video)
7. **Overlay:** Dark gradient ensures readability
8. **Mobile:** Responsive design with darker overlay on small screens

---

## 🎯 Success Criteria

Your implementation is complete when:
- ✅ Video loads and plays automatically
- ✅ Text is clearly readable over video
- ✅ No audio plays (muted)
- ✅ Video loops seamlessly
- ✅ Responsive on mobile (buttons stack, text resizes)
- ✅ All animations run smoothly
- ✅ No console errors or warnings
- ✅ Matches reference design (ui.jpg)
- ✅ Page loads in <3 seconds on 4G

---

**Last Updated:** 2026-02-19
**Status:** Code implementation complete, awaiting video file
