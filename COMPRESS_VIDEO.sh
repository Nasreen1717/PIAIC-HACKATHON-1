#!/bin/bash

# Video Compression Script for Hero Background
# Reduces 12MB video to ~3-4MB while maintaining quality

echo "🎬 Video Compression Tool"
echo "=========================="
echo ""

INPUT_VIDEO="Front-End-Book/static/videos/hero-video.mp4"
OUTPUT_VIDEO="Front-End-Book/static/videos/hero-video-compressed.mp4"

if [ ! -f "$INPUT_VIDEO" ]; then
    echo "❌ Error: Video file not found at $INPUT_VIDEO"
    exit 1
fi

echo "📊 Current video info:"
ls -lh "$INPUT_VIDEO"
echo ""

echo "⏳ Compressing video (this may take 1-2 minutes)..."
echo ""

# Compression command: reduces file size while maintaining quality
ffmpeg -i "$INPUT_VIDEO" \
  -c:v libx264 \
  -preset fast \
  -crf 28 \
  -c:a aac \
  -b:a 64k \
  "$OUTPUT_VIDEO"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Compression successful!"
    echo ""
    echo "📊 Before:"
    ls -lh "$INPUT_VIDEO"
    echo ""
    echo "📊 After:"
    ls -lh "$OUTPUT_VIDEO"
    echo ""
    echo "🔄 Replacing original with compressed version..."
    mv "$OUTPUT_VIDEO" "$INPUT_VIDEO"
    echo ""
    echo "✅ Done! Video compressed and ready to deploy."
    ls -lh "$INPUT_VIDEO"
else
    echo ""
    echo "❌ Compression failed. Please check ffmpeg is installed."
    exit 1
fi
