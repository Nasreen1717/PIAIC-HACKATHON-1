# Hero Background Video

This directory contains the background video for the hero section.

## Video Setup

### File: `hero-video.mp4`

**Location:** `/static/videos/hero-video.mp4`

**Requirements:**
- Format: MP4 (H.264 codec) - Most compatible format
- Resolution: 1920x1080 or higher (will be scaled with `object-fit: cover`)
- Size: < 5MB recommended (compress using ffmpeg or similar tools)
- Duration: 10-30 seconds recommended
- Frame rate: 24-30 fps
- Audio: Muted (required for autoplay)

**Specifications:**
- Recommended aspect ratio: 16:9
- Color profile: sRGB
- Will be displayed with:
  - `brightness(0.8)` filter applied
  - Dark overlay gradient (rgba(15, 23, 42, 0.65) to 0.85) for text readability
  - `object-fit: cover` - fills the entire hero section

## Adding Your Video

1. Place your robot/robotics video file as `hero-video.mp4` in this directory
2. The video will automatically:
   - Loop continuously
   - Play with autoplay (no sound needed)
   - Scale to fill the hero section (1920x1080 max)
   - Display with optimized brightness for text overlay

## Video Compression Tips

If your video is too large, compress it using ffmpeg:

```bash
# Basic compression
ffmpeg -i input.mov -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k hero-video.mp4

# For better quality/smaller file size
ffmpeg -i input.mov -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 96k -vf scale=1920:1080 hero-video.mp4
```

## Poster Image

**File:** `/static/img/hero-poster.jpg`

This is a still image shown while the video loads.
- Should be the first frame of your video
- Resolution: 1920x1080
- Size: ~200-300KB
- Format: JPEG or PNG

## Browser Compatibility

The video format is optimized for:
- Chrome/Edge (H.264)
- Firefox (with H.264 support)
- Safari (native H.264 support)
- Mobile browsers (iOS/Android)

Fallback text is provided for older browsers.

## Styling Notes

The video is styled with:
- Z-index: 0 (background layer)
- Brightness filter: 0.8 (darkened)
- Dark overlay: rgba(15, 23, 42, 0.85) gradient (left) to 0.65 (right)
- This ensures text remains readable regardless of video content

## Performance

- Video uses `contain: layout` for better performance
- Muted/no audio stream (faster loading)
- Lazy loading can be enabled if video is below the fold
- Typical load time: < 2 seconds on 4G

---

For more details about the hero section design, see the design specification document.
