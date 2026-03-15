# Team Development Setup Guide

## Overview
Everyone uses their **own unique email address** to sign up and create their own account in a shared database.

## Shared Database (Everyone Uses This)

```
postgresql+asyncpg://neondb_owner:npg_59mhtfFQpbxC@ep-quiet-water-ahgur4ec-pooler.c-3.us-east-1.aws.neon.tech/neondb
```

## Local Setup Instructions

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd Hackathon-1
```

### Step 2: Backend Setup

```bash
cd backend

# Create .env file with shared database
cat > .env << 'ENVEOF'
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_59mhtfFQpbxC@ep-quiet-water-ahgur4ec-pooler.c-3.us-east-1.aws.neon.tech/neondb
JWT_SECRET=dev-secret-key-change-in-production
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
QDRANT_URL=https://88dc26ed-7317-479b-9a92-c5ccaa7a0e5b.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.H51a3VyJte1rRYxS7kH97RLIv9c7SbtTTMqQo2Dt36Q
ENVIRONMENT=development
DEBUG=false
ENVEOF

# Activate virtual environment
source venv/bin/activate

# Start backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 3: Frontend Setup (new terminal)

```bash
cd Front-End-Book
npm start

# Visit: http://localhost:3000
```

## Sign Up / Sign In

**Each person creates their own account with their own email:**

✅ **Person 1:**
- Email: alice@company.com
- Password: MyPassword123
- Full Name: Alice Developer

✅ **Person 2:**
- Email: bob@company.com
- Password: MyPassword123
- Full Name: Bob Developer

**All data goes to the SAME shared database** ✓

## Vercel Deployment (Production)

Once local development is complete:

```bash
git push origin main
```

Vercel will automatically build and deploy!

**Live App:** https://your-app.vercel.app

Everyone can sign up there with their own email.

## Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (need 3.10+)
- Check .env exists in backend directory
- Check DATABASE_URL is correct

**Frontend can't connect?**
- Make sure backend runs on port 8000
- Check browser console (F12) for errors

**Signup shows error?**
- Password: min 6 chars, 1 letter, 1 number
- Email must be valid format
- Email must not already exist

## Questions?
Check README.md or ask the project lead.
