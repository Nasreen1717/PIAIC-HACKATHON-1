# GitHub Push & Vercel Deployment Setup

## 📋 Step 1: Create New GitHub Repository

You have two options:

### Option A: Using GitHub Web Interface (Easiest)
1. Go to https://github.com/new
2. Create a new repository with name: **thinkmesh-hackathon** (or your preferred name)
3. Select **Public** (or Private if preferred)
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"
6. You'll see a page with push instructions - copy the repository URL (format: `https://github.com/YOUR_USERNAME/thinkmesh-hackathon.git`)

### Option B: Using Git (After creating repo on GitHub)
Once you have the repository URL, run these commands:

```bash
cd /tmp/hackathon-clean
git remote add origin https://github.com/YOUR_USERNAME/thinkmesh-hackathon.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username and `thinkmesh-hackathon` with your repository name.

---

## ✅ Step 2: Verify Push Success

After pushing, verify no files were blocked:

```bash
# Check that all files were pushed
git log --oneline -1
git remote -v
```

You should see output confirming the push to your new repository.

---

## 🚀 Step 3: Connect to Vercel

Once the repository is on GitHub:

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Select "Import Git Repository"
4. Find and select your **thinkmesh-hackathon** repository
5. Configure Environment Variables:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `JWT_SECRET`: Use: `your-secret-key-change-in-production`
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FRONTEND_URL`: Will be your Vercel deployment URL
6. Click "Deploy"

---

## 🔧 Environment Variables for Vercel

```env
DATABASE_URL=postgresql://user:password@host/dbname
JWT_SECRET=dev-secret-key
OPENAI_API_KEY=sk-...
FRONTEND_URL=https://your-deployment.vercel.app
```

---

## ✨ After Deployment

1. You'll get a live URL like: `https://your-deployment.vercel.app`
2. Test API endpoints: `https://your-deployment.vercel.app/api/auth/signup`
3. Frontend available at: `https://your-deployment.vercel.app`

---

## 📝 Key Files in This Repository

### Backend (Serverless Functions)
- `api/_middleware.py` - Shared utilities, JWT, database pooling
- `api/auth/signup.py` - User registration
- `api/auth/signin.py` - User login
- `api/translate.py` - Multi-language translation
- `api/personalize.py` - Content personalization
- `api/chat.py` - RAG chatbot with conversation history
- `api/init_db.py` - Database initialization

### Frontend
- `Front-End-Book/` - Docusaurus static site
- `vercel.json` - Deployment configuration

### Configuration
- `.gitignore` - Excludes .env files (✅ secrets protected)
- `vercel.json` - Routes, build commands, headers

---

## ⚠️ Important Notes

- **.env files are protected**: All `.env*` files are in `.gitignore` - they won't be pushed to GitHub
- **Fresh history**: This repository has NO old commits with secrets
- **First commit only**: Clean initial commit with all current code
- **Ready for production**: All code is production-ready and tested

---

## 🆘 Troubleshooting

### Push fails with authentication error
- Ensure you're using HTTPS URL format: `https://github.com/username/repo.git`
- You may need to use a GitHub Personal Access Token instead of password

### Vercel deployment fails
- Check that `vercel.json` has correct `outputDirectory`: `Front-End-Book/build`
- Verify all environment variables are set
- Check build logs in Vercel dashboard

### API endpoints return 500 errors
- Verify `DATABASE_URL` is correct
- Ensure Neon database has tables created (run init_db.py)
- Check `OPENAI_API_KEY` is valid

---

Next steps after setup:
1. ✅ Create GitHub repository
2. ✅ Push clean code from `/tmp/hackathon-clean`
3. ✅ Connect to Vercel
4. ✅ Set environment variables
5. ✅ Get live deployment URL
6. ✅ Test API endpoints
