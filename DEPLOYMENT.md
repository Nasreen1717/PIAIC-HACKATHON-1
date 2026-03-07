# Vercel Deployment Guide

**Project**: ThinkMesh - Humanoid Robotics Learning Platform
**Architecture**: Monorepo with Docusaurus frontend + Python serverless backend
**Platform**: Vercel (static + functions)
**Database**: Neon (serverless PostgreSQL)

## Quick Start

1. **Deploy Frontend**: Push to GitHub → Vercel auto-deploys
2. **Configure Backend**: Add environment variables in Vercel dashboard
3. **Test APIs**: Use curl commands to verify endpoints

## Prerequisites

- [Neon](https://neon.tech) database with tables initialized
- [OpenAI API key](https://platform.openai.com) for translation/chat
- [Vercel account](https://vercel.com) connected to GitHub

## Deployment Steps

### 1. Initialize Neon Database

```bash
export DATABASE_URL="postgresql://user:password@host/dbname"
python3 api/init_db.py
# Verify: psql "$DATABASE_URL" -c "\dt"
```

### 2. Deploy to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import GitHub repository: `Hackathon-1`
3. Configure:
   - Build: `cd Front-End-Book && npm run build`
   - Output: `Front-End-Book/build`
   - Install: `npm install --prefix Front-End-Book && pip install --target ./api/lib -r ./api/requirements.txt`

### 3. Add Environment Variables

In Vercel Settings → Environment Variables:

```
DATABASE_URL=postgresql://...
JWT_SECRET=<openssl rand -base64 32>
OPENAI_API_KEY=sk-...
FRONTEND_URL=https://your-vercel-url.vercel.app
PYTHONPATH=/var/task
```

### 4. Deploy

Click "Deploy" and wait 2-3 minutes for build completion.

## Testing APIs

```bash
export API_URL="https://your-deployment.vercel.app"

# Signup
curl -X POST "$API_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"Test123","full_name":"Test"}'

# Signin
curl -X POST "$API_URL/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"Test123"}'

# Save token, then test authenticated endpoint
TOKEN="<access_token>"
curl -X POST "$API_URL/api/translate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"text":"Hello","target_language":"ur"}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database timeout | Verify DATABASE_URL in Vercel env vars |
| Module not found | Ensure requirements.txt complete |
| CORS error | Check FRONTEND_URL matches deployment |
| 401 Unauthorized | Generate fresh JWT token |
| OpenAI error | Verify OPENAI_API_KEY is set |

## Rollback

Vercel dashboard → Deployments → Previous deployment → Promote to Production

## Performance Targets

- Frontend load: < 3 seconds (FCP)
- API response: < 2 seconds (p95)
- Signup/Signin: < 5 seconds
- Zero downtime deployments

## Documentation

- [Vercel Docs](https://vercel.com/docs)
- [Neon Docs](https://neon.tech/docs)
- [OpenAI API](https://platform.openai.com/docs)

---
Status: Production Ready ✅
