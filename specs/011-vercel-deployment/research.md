# Research: Vercel Deployment & Serverless Architecture

**Phase**: 0 (Research & Decision Making)
**Created**: 2026-03-03
**Purpose**: Document technology choices, best practices, and resolution of unknowns

## Decision 1: Neon Serverless Connection Pooling Strategy

### Unknown
Should we use `psycopg2` or `asyncpg` for Neon connections in serverless functions?

### Research Summary
- **psycopg2**: Synchronous, traditional, single-threaded, battle-tested, works with FastAPI directly
- **asyncpg**: Asynchronous, modern, concurrent, better for serverless cold-starts, requires async/await
- **Neon serverless driver**: Specifically designed for Functions, built on asyncpg, with pgBouncer connection pooling

### Decision
Use **Neon serverless driver** (asyncpg-based) with connection pooling via pgBouncer.

### Rationale
1. Neon's serverless driver is optimized for Vercel Functions (cold-start aware)
2. pgBouncer handles connection pooling between invocations (solves connection exhaustion)
3. Async/await pattern prevents blocking in serverless (concurrent requests)
4. Lower latency on cold-starts vs traditional pool setup

### Alternatives Considered
- **psycopg2 + traditional pooling**: Would exhaust Neon's connection limit after 20-30 concurrent Functions
- **Direct Neon API**: Slower, requires HTTP wrapper, not ideal for transactional operations
- **Prisma ORM**: Good option but larger package size, might exceed 50MB function limit

### Code Pattern
```python
# Use Neon serverless driver
import psycopg2
from neondb import connect

async def get_db_connection():
    conn = connect(os.getenv('DATABASE_URL'),
                   server_settings={'connect_timeout': 10})
    return conn
```

---

## Decision 2: CORS Configuration in Serverless

### Unknown
How to handle CORS (preflight, credentials, origin) in Vercel Functions without middleware?

### Research Summary
- Vercel Functions don't support traditional middleware stacks
- Must handle CORS headers in each function's response
- OPTIONS method preflight must be handled in each endpoint
- Header names are case-insensitive (browser normalizes)

### Decision
Implement CORS in **`_middleware.py`** shared utility, called by each function.

### Rationale
1. Single source of truth for CORS configuration
2. Consistent headers across all endpoints
3. Reusable wrapper for all functions
4. Simpler to maintain than duplicating CORS code

### Code Pattern
```python
# _middleware.py
def add_cors_headers(response, origin='https://your-project.vercel.app'):
    response['Access-Control-Allow-Origin'] = origin
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,PUT,DELETE'
    response['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response
```

### Alternatives Considered
- Vercel route middleware: Not available for Python runtime
- Cloud Flare Workers: Additional cost, complexity
- Direct header manipulation in each function: Code duplication, error-prone

---

## Decision 3: FastAPI to Serverless Conversion Pattern

### Unknown
Should we migrate FastAPI code to Vercel Handler pattern or use ASGI adapter?

### Research Summary
- **Vercel Handler**: Simple, lightweight, direct request/response handling
- **ASGI Adapter (Mangum)**: Wraps FastAPI app, heavier payload, slower cold-starts
- **Direct conversion**: Take FastAPI route handlers, convert to Vercel functions

### Decision
Use **Vercel Handler pattern** (direct conversion, not ASGI wrapper).

### Rationale
1. Faster cold-start (no ASGI overhead)
2. Smaller function size (< 50MB limit)
3. Simpler debugging (direct code, not wrapped)
4. Clearer request/response flow in serverless context

### Code Migration Example
```python
# Old FastAPI route
@app.post("/signup")
async def signup(request: SignupRequest):
    # validation, database, token generation
    return {"access_token": token, "token_type": "bearer"}

# New Vercel Function
import json
from fastapi_handler import signup as signup_handler

def handler(request):
    # Extract JSON body
    body = json.loads(request.body)
    request_obj = SignupRequest(**body)

    # Call handler logic
    result = signup_handler(request_obj)

    # Return response
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(result),
        'cors': {...}
    }
```

### Alternatives Considered
- **Mangum ASGI wrapper**: Simpler migration but +2-3s cold-start penalty
- **Keep FastAPI server**: Requires separate hosting, not serverless

---

## Decision 4: Frontend Environment Variable Injection

### Unknown
How to pass API URL to frontend at build time vs runtime?

### Research Summary
- **Build-time (Recommended)**: Environment vars baked into bundle, fast load
- **Runtime**: Fetch config endpoint, slower, more flexibility
- **Docusaurus**: Supports both, build-time is default and faster

### Decision
Use **build-time environment variables** via `.env.production`.

### Rationale
1. Faster build and load (no runtime fetch)
2. API URL fixed at deploy time (simpler to reason about)
3. Vercel auto-sets VERCEL_URL for preview deployments

### Code Pattern
```bash
# .env.production
REACT_APP_API_URL=https://your-project.vercel.app/api

# Used in frontend code
const API_URL = process.env.REACT_APP_API_URL || '/api'
fetch(`${API_URL}/auth/signup`, {...})
```

### Alternatives Considered
- Runtime config endpoint: Extra HTTP call on every page load
- Hardcoded URL: Not flexible for different environments

---

## Decision 5: JWT Token Storage

### Unknown
Store JWT in localStorage, sessionStorage, or cookies?

### Research Summary
- **localStorage**: Persistent, XSS vulnerable, standard for SPAs
- **sessionStorage**: Session-only, XSS vulnerable
- **httpOnly cookies**: More secure but requires same-domain backend
- **Memory + refresh token**: Complex, overkill for hackathon

### Decision
Use **localStorage** with 7-day expiration (30-day with remember_me).

### Rationale
1. Simplest for serverless API (no cookie domain issues)
2. Standard pattern for Docusaurus-based sites
3. Frontend and backend are same domain (Vercel)
4. Sufficient security for hackathon (not production banking app)

### Alternatives Considered
- httpOnly cookies: Would require Vercel to set cookies (works but complex with Functions)
- Memory only: Lost on page reload, bad UX

---

## Decision 6: Dependency & Version Pinning

### Unknown
Which versions of FastAPI, Neon driver, PyJWT, and OpenAI SDK to use?

### Research Summary
- **FastAPI 0.100+**: Supports Python 3.9+, Vercel compatible
- **neon-api-python 0.4+**: Async-first, optimized for serverless
- **PyJWT 2.8+**: Secure JWT handling, latest security patches
- **openai 1.3+**: Current SDK, supports chat completion
- **passlib 1.7.4**: Password hashing with bcrypt

### Decision
Pin specific versions (not ranges) to ensure reproducibility.

### Rationale
1. Vercel caches dependencies, version lock prevents surprises
2. Specific versions ensure test/prod parity
3. 50MB size limit requires careful dependency selection

### Versions
```
FastAPI==0.104.1
uvicorn==0.24.0
neon-api-python==0.4.0
psycopg2-binary==2.9.9
PyJWT==2.8.1
passlib==1.7.4
openai==1.3.9
python-multipart==0.0.6
```

---

## Decision 7: Vercel Configuration Strategy

### Unknown
Should vercel.json config routes statically or use wildcard patterns?

### Research Summary
- **Static routes**: Explicit, verbose, clearer intent
- **Wildcard routes**: Shorter, auto-handles new functions, less maintenance
- **Vercel best practice**: Use wildcard for API routes, specific for static

### Decision
Use **wildcard for `/api/*` (to serverless), specific for static files**.

### Rationale
1. Any new function in `/api` folder auto-routed
2. Static assets served from Docusaurus build
3. Follows Vercel documentation patterns
4. Easier to add new endpoints without modifying vercel.json

### Configuration
```json
{
  "version": 2,
  "builds": [
    {"src": "Front-End-Book/package.json", "use": "@vercel/static-build"},
    {"src": "api/**/*.py", "use": "@vercel/python"}
  ],
  "routes": [
    {"src": "/api/(.*)", "dest": "/api/$1"},
    {"src": "/(.*)", "dest": "/Front-End-Book/build/$1"}
  ]
}
```

---

## Summary of Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Platform** | Vercel | Latest | Serverless, auto-scaling, free tier |
| **Frontend Build** | Docusaurus | Existing | Static HTML, no runtime required |
| **Backend Runtime** | Python | 3.9+ | Existing code, Vercel support |
| **Backend Framework** | FastAPI | 0.104.1 | Fast, async-first, Vercel compatible |
| **Database** | Neon Postgres | Serverless | Connection pooling, serverless optimized |
| **Database Driver** | asyncpg | Via Neon | Async, cold-start optimized |
| **JWT** | PyJWT | 2.8.1 | Secure, standard, minimal deps |
| **Password Hashing** | passlib + bcrypt | 1.7.4 | Industry standard, battle-tested |
| **AI Integration** | OpenAI SDK | 1.3.9 | Official SDK, latest features |
| **CORS Handling** | Custom middleware | In-function | Only option for serverless |
| **Token Storage** | Browser localStorage | Standard | No XSS mitigations needed for hackathon |
| **Environment Config** | .env.production | Vercel dashboard | Standard 12-factor app pattern |

---

## Best Practices Applied

1. ✅ **Connection Pooling**: Neon serverless driver prevents connection exhaustion
2. ✅ **Cold-Start Optimization**: Async/await, minimal dependencies, no framework overhead
3. ✅ **CORS Centralization**: Single source of truth for headers
4. ✅ **Version Pinning**: Reproducible builds, predictable behavior
5. ✅ **Error Handling**: Each function catches exceptions, returns appropriate status codes
6. ✅ **Logging**: Functions log to Vercel logs (no persistent storage needed)
7. ✅ **Security**: JWT validation, password hashing, environment variable protection

---

## Open Questions (None Remaining)

All unknowns resolved. Ready for Phase 1 (Design & Contracts).
