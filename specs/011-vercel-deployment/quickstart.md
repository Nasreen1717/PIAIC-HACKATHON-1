# Quickstart: Local Development & Testing

**Phase**: 1 (Design)
**Purpose**: Get developers up and running locally before Vercel deployment

## Prerequisites

- Node.js 18+ and npm installed
- Python 3.9+ and pip installed
- Vercel CLI: `npm install -g vercel`
- Git repository cloned
- `.env.local` file with credentials (see setup below)

## Initial Setup

### 1. Install Dependencies

```bash
# Install frontend dependencies
cd Front-End-Book
npm install
cd ..

# Install backend dependencies
pip install -r api/requirements.txt
```

### 2. Create Local Environment File

Create `.env.local` in repository root:

```bash
# Database (from Neon)
DATABASE_URL=postgresql://user:password@your-neon-host/database

# JWT Secret (can be any string for local testing)
JWT_SECRET=dev-secret-key-change-in-production

# OpenAI API Key (for translation and chatbot)
OPENAI_API_KEY=sk-...

# Frontend URL (for CORS in serverless functions)
FRONTEND_URL=http://localhost:3000

# Python path for Vercel emulation
PYTHONPATH=/var/task
```

### 3. Verify Database Connection

Test Neon connection from command line:

```bash
# Using psycopg2
python3 -c "
import psycopg2
import os
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
print('✅ Database connected')
conn.close()
"
```

## Local Development Workflow

### Start Vercel Development Server

Emulates Vercel Functions and frontend build locally:

```bash
# From repository root
vercel dev

# Output:
# ✓ Preview: http://localhost:3000
# ✓ API: http://localhost:3000/api
```

This will:
- Build Docusaurus frontend
- Start Python runtime for serverless functions
- Watch for file changes and hot-reload

### Test Endpoints Locally

In another terminal, test the API:

```bash
# 1. Test signup with any email
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@gmail.com",
    "password": "Test123",
    "full_name": "Test User",
    "software_background": "beginner",
    "learning_goal": "career"
  }'

# Expected response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "expires_in": 604800
# }

# 2. Copy the access_token from response, then test signin
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@gmail.com",
    "password": "Test123",
    "remember_me": false
  }'

# 3. Save token in a variable for protected endpoint tests
TOKEN="<access_token_from_response>"

# 4. Test protected endpoint (e.g., get profile)
curl -X GET http://localhost:3000/api/me \
  -H "Authorization: Bearer $TOKEN"

# 5. Test translation (with OpenAI)
curl -X POST http://localhost:3000/api/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "text": "Hello world",
    "target_language": "ur"
  }'

# 6. Test chat/RAG
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is ROS 2?",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

## Testing CORS Headers

Verify CORS headers are returned correctly:

```bash
# Check CORS headers with -i flag
curl -i -X OPTIONS http://localhost:3000/api/auth/signup

# Should show:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: POST,GET,OPTIONS
```

## Testing Frontend

### 1. Navigate to local frontend

Open browser to `http://localhost:3000`

Should see:
- Docusaurus documentation site
- Navigation bar with HOME, MODULE 1-4
- Sign In / Sign Up buttons in navbar
- Theme toggle (light/dark mode)

### 2. Test signup flow

1. Click "Sign Up" button in navbar
2. Fill form with any email (gmail.com, yahoo.com, etc.)
3. Enter password: `Test123` (6+ chars with letter + number)
4. Select learning background options
5. Click Sign Up
6. Should be redirected to dashboard / profile page

### 3. Test features

After signup:
- **Profile Page**: View user info and saved preferences
- **Translation**: Select text and translate to Urdu (if translation feature enabled)
- **Personalization**: Content should adjust based on learning level
- **RAG Chatbot**: Ask questions about the course content (if chatbot enabled)

## Debugging

### View Vercel Dev Logs

Logs appear in the terminal where `vercel dev` is running:

```
[api/auth/signup.py] Incoming request: POST /api/auth/signup
[api/auth/signup.py] Email validation passed
[api/auth/signup.py] User created: user_id=5
[api/auth/signup.py] JWT token generated
```

### Debug Database Issues

```bash
# Connect to Neon database directly
psql "$DATABASE_URL"

# Inside psql prompt:
SELECT * FROM users;
SELECT * FROM conversation_histories;
```

### Check Environment Variables

```bash
# Verify env vars are loaded
python3 -c "import os; print(os.getenv('DATABASE_URL'))"
python3 -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

## Production Build Locally

Test the production build before deploying:

```bash
# Build frontend
cd Front-End-Book
npm run build
cd ..

# This creates Front-End-Book/build/ directory

# Verify build artifacts
ls Front-End-Book/build/
# Should show index.html, assets/, etc.
```

## Git Workflow Before Deploying

```bash
# Create feature branch
git checkout -b feature/vercel-deployment

# Make changes to api/ and Front-End-Book/

# Commit changes
git add .
git commit -m "feat: Add serverless API functions and deployment config"

# Push to GitHub
git push origin feature/vercel-deployment

# Create PR and merge to main (when ready to deploy)
```

## Ready for Vercel Deployment

When satisfied with local testing:

```bash
# Push to main branch on GitHub
git checkout main
git merge feature/vercel-deployment
git push origin main

# Then run:
vercel --prod

# Vercel will:
# 1. Detect pushes from GitHub
# 2. Build frontend (npm run build)
# 3. Bundle serverless functions (api/*.py)
# 4. Deploy to CDN and Vercel Functions
# 5. Print production URL
```

## Common Issues & Solutions

### Issue: "MODULE NOT FOUND" for imports

**Cause**: Python dependencies not installed

**Solution**:
```bash
pip install -r api/requirements.txt
export PYTHONPATH=/var/task
```

### Issue: "DATABASE CONNECTION TIMEOUT"

**Cause**: DATABASE_URL is incorrect or Neon is unreachable

**Solution**:
```bash
# Verify connection string
psql "$DATABASE_URL" -c "SELECT 1"

# Check if credentials are correct
# Copy fresh DATABASE_URL from Neon dashboard
```

### Issue: "CORS ERROR" in browser

**Cause**: Frontend URL doesn't match CORS configuration

**Solution**:
- Verify `FRONTEND_URL` in `.env.local` matches browser origin
- For localhost: `FRONTEND_URL=http://localhost:3000`
- For production: `FRONTEND_URL=https://your-project.vercel.app`

### Issue: "401 UNAUTHORIZED" on protected endpoints

**Cause**: Token is expired or invalid

**Solution**:
```bash
# Generate new token via signup
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"new@test.com","password":"Test123","full_name":"Test"}'

# Use the access_token from response in Authorization header
```

## Next Steps

1. ✅ Local development complete
2. 📋 Push to GitHub (`git push origin main`)
3. 🚀 Deploy to Vercel (`vercel --prod` or via GitHub integration)
4. ✅ Test production endpoints
5. 📹 Record demo video

---

## Useful Commands Reference

```bash
# Development
npm install                    # Install frontend deps
pip install -r api/requirements.txt  # Install backend deps
vercel dev                    # Start local dev server
npm run build                 # Build Docusaurus

# Testing
curl -X POST http://localhost:3000/api/auth/signup ...
curl -i http://localhost:3000/api/auth/signup        # With headers
curl -H "Authorization: Bearer $TOKEN" ...            # With auth

# Deployment
vercel --prod                 # Deploy to production
vercel rollback              # Rollback to previous deployment
git push origin main         # Trigger GitHub webhook for auto-deploy

# Debugging
psql "$DATABASE_URL"         # Connect to Neon database
python3 -c "import os; print(os.getenv('var_name'))"  # Check env vars
tail -f /tmp/vercel-dev.log  # View dev server logs
```

---

**Ready for development!** Start with `vercel dev` and test endpoints above.
