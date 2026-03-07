#!/bin/bash

# Vercel Deployment - Push to GitHub Script
# Usage: ./push-to-github.sh <github-url>
# Example: ./push-to-github.sh https://github.com/Nasreen1717/thinkmesh-hackathon.git

set -e

if [ -z "$1" ]; then
    echo "❌ Error: GitHub repository URL required"
    echo ""
    echo "Usage: ./push-to-github.sh <github-url>"
    echo ""
    echo "Example:"
    echo "  ./push-to-github.sh https://github.com/Nasreen1717/thinkmesh-hackathon.git"
    echo ""
    exit 1
fi

GITHUB_URL="$1"

echo "🔗 Adding remote: $GITHUB_URL"
git remote add origin "$GITHUB_URL" 2>/dev/null || git remote set-url origin "$GITHUB_URL"

echo "📌 Renaming branch to main..."
git branch -M main

echo "📤 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Success! Your code has been pushed to GitHub"
echo ""
echo "Repository: $GITHUB_URL"
echo "Branch: main"
echo ""
echo "Next steps:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Click 'Add New' → 'Project'"
echo "3. Import your GitHub repository"
echo "4. Set environment variables:"
echo "   - DATABASE_URL"
echo "   - JWT_SECRET"
echo "   - OPENAI_API_KEY"
echo "   - FRONTEND_URL"
echo "5. Click Deploy"
echo ""
echo "📖 For detailed instructions, see: GITHUB_PUSH_SETUP.md"
