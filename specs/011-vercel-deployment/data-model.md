# Data Model: Vercel Deployment Backend

**Phase**: 1 (Design)
**Created**: 2026-03-03
**Purpose**: Define database schema, entities, relationships, and validation rules

## Database: Neon Postgres

Schema optimized for Vercel serverless (minimal transactions, efficient queries).

---

## Entity: User

**Purpose**: Store user account information and authentication credentials

**Table**: `users`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User email (login identifier) |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hash of password |
| `full_name` | VARCHAR(255) | NULLABLE | User's full name |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account active flag |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
```

**Validation Rules**:
- **email**: Must be valid email format (contains @ and .), unique in database, case-insensitive storage
- **password_hash**: Never empty, must be bcrypt hash (60 chars, $2b$ prefix)
- **full_name**: 2-255 characters, optional
- **is_active**: Boolean flag, defaults to TRUE

**Example Record**:
```json
{
  "id": 1,
  "email": "student@example.com",
  "password_hash": "$2b$12$...",
  "full_name": "Jane Doe",
  "is_active": true,
  "created_at": "2026-03-03T10:00:00Z",
  "updated_at": "2026-03-03T10:00:00Z"
}
```

---

## Entity: UserBackground

**Purpose**: Store user profile answers from background questionnaire (learning preferences, experience level)

**Table**: `user_backgrounds`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique background record ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Reference to user |
| `software_background` | VARCHAR(50) | NULLABLE | Level: beginner, intermediate, advanced |
| `hardware_background` | VARCHAR(50) | NULLABLE | Level: none, some, robotics-specific |
| `ros_experience` | VARCHAR(50) | NULLABLE | ROS experience: none, basic, proficient |
| `python_level` | VARCHAR(50) | NULLABLE | Python skill: beginner, intermediate, advanced |
| `learning_goal` | VARCHAR(100) | NULLABLE | Goal: career, research, hobby, certification |
| `available_hardware` | VARCHAR(100) | NULLABLE | Hardware available: simulation-only, robotarm, humanoid, custom |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

**Indexes**:
```sql
CREATE INDEX idx_user_backgrounds_user_id ON user_backgrounds(user_id);
```

**Relationships**:
- **1:1 with User**: Each user has one background record (but can be NULL if not filled)
- Cascade delete: If user deleted, background deleted

**Validation Rules**:
- **software_background**: Enum (beginner, intermediate, advanced) or NULL
- **hardware_background**: Enum (none, some, robotics-specific) or NULL
- **ros_experience**: Enum (none, basic, proficient) or NULL
- **python_level**: Enum (beginner, intermediate, advanced) or NULL
- **learning_goal**: Enum (career, research, hobby, certification) or NULL
- **available_hardware**: Text (can be custom), max 100 chars, optional

**Example Record**:
```json
{
  "id": 1,
  "user_id": 1,
  "software_background": "beginner",
  "hardware_background": "none",
  "ros_experience": "none",
  "python_level": "intermediate",
  "learning_goal": "career",
  "available_hardware": "simulation-only",
  "created_at": "2026-03-03T10:01:00Z",
  "updated_at": "2026-03-03T10:01:00Z"
}
```

---

## Entity: ConversationHistory

**Purpose**: Store RAG chatbot conversation history for each user (messages and responses)

**Table**: `conversation_histories`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique message ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Reference to user |
| `conversation_id` | VARCHAR(36) | NOT NULL | UUID for conversation grouping |
| `role` | VARCHAR(20) | NOT NULL (user/assistant) | Who sent message |
| `message` | TEXT | NOT NULL | Message content |
| `tokens_used` | INTEGER | NULLABLE | OpenAI tokens consumed |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was created |

**Indexes**:
```sql
CREATE INDEX idx_conversation_user_id ON conversation_histories(user_id);
CREATE INDEX idx_conversation_conversation_id ON conversation_histories(conversation_id);
CREATE INDEX idx_conversation_created_at ON conversation_histories(created_at);
```

**Relationships**:
- **N:1 with User**: Each user can have many conversations
- Cascade delete: If user deleted, conversation history deleted

**Validation Rules**:
- **role**: Must be 'user' or 'assistant'
- **message**: Non-empty text, max 10,000 characters (OpenAI limit)
- **conversation_id**: UUID format (uuid4), groups related messages
- **tokens_used**: Optional, for cost tracking

**Example Records**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "user",
    "message": "What is ROS 2?",
    "tokens_used": 15,
    "created_at": "2026-03-03T10:05:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "assistant",
    "message": "ROS 2 is a middleware platform... [from textbook]",
    "tokens_used": 150,
    "created_at": "2026-03-03T10:05:05Z"
  }
]
```

---

## Entity: Session/JWT Token

**Purpose**: Represents authenticated session (stored in browser localStorage, not database)

**Not persisted in database**: Tokens are generated on signup/signin, validated in-memory.

**Token Payload** (JWT):
```json
{
  "sub": "student@example.com",
  "exp": 1704067200,
  "iat": 1703462400,
  "type": "access"
}
```

**Token Storage**:
- Generated by: `/api/auth/signup` and `/api/auth/signin`
- Stored in: Browser localStorage
- Transmitted in: Authorization header (`Authorization: Bearer <token>`)
- Validated by: All protected endpoints (via JWT signature verification)

**Validation Rules**:
- **Algorithm**: HS256 (HMAC-SHA256)
- **Secret**: Stored in Vercel environment variable `JWT_SECRET`
- **Expiration**: 7 days (604,800 seconds) for normal login
- **Expiration**: 30 days for "remember me" login
- **Signature**: Must match secret to be valid

---

## State Transitions

### User Authentication Flow

```
[No Token]
    ↓
[User registers via /api/auth/signup]
    ↓
[User record created in database]
    ↓
[JWT token generated, returned to browser]
    ↓
[Token stored in localStorage]
    ↓
[Token sent in Authorization header to protected endpoints]
    ↓
[Server validates token signature + expiration]
    ↓ (Token valid)
[Request processed, returns user data]
    ↓ (Token expired/invalid)
[Server returns 401 Unauthorized]
    ↓
[Browser redirects to signin]
```

### User Logout Flow

```
[Token in localStorage]
    ↓
[User clicks Sign Out]
    ↓
[POST /api/auth/signout with token]
    ↓
[Server validates token (just logging action)]
    ↓
[Returns success response]
    ↓
[Browser removes token from localStorage]
    ↓
[Client redirects to homepage]
    ↓
[No token in localStorage - user logged out]
```

---

## Database Schema Creation

```sql
-- Create users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Create user_backgrounds table
CREATE TABLE user_backgrounds (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  software_background VARCHAR(50),
  hardware_background VARCHAR(50),
  ros_experience VARCHAR(50),
  python_level VARCHAR(50),
  learning_goal VARCHAR(100),
  available_hardware VARCHAR(100),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_backgrounds_user_id ON user_backgrounds(user_id);

-- Create conversation_histories table
CREATE TABLE conversation_histories (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  conversation_id VARCHAR(36) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
  message TEXT NOT NULL,
  tokens_used INTEGER,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation_histories(user_id);
CREATE INDEX idx_conversation_conversation_id ON conversation_histories(conversation_id);
CREATE INDEX idx_conversation_created_at ON conversation_histories(created_at);
```

---

## Query Performance Considerations

**Optimization Strategies**:
1. **Indexes on foreign keys**: user_id columns indexed for JOIN operations
2. **Timestamp indexes**: created_at indexed for sorting/filtering
3. **Single-user queries**: Email lookup (indexed) for signin
4. **Conversation retrieval**: Use conversation_id for grouping messages
5. **Pagination**: SELECT with LIMIT/OFFSET for long conversation histories

**Typical Query Patterns**:
```sql
-- Signup: Check duplicate email
SELECT id FROM users WHERE email = $1;

-- Signin: Get user by email
SELECT id, password_hash FROM users WHERE email = $1;

-- Get user profile
SELECT * FROM users WHERE id = $1;

-- Get user background
SELECT * FROM user_backgrounds WHERE user_id = $1;

-- Get conversation history
SELECT * FROM conversation_histories
  WHERE user_id = $1 AND conversation_id = $2
  ORDER BY created_at ASC;

-- Save chat message
INSERT INTO conversation_histories
  (user_id, conversation_id, role, message, tokens_used)
  VALUES ($1, $2, $3, $4, $5);
```

**Estimated Query Times**:
- Email lookup (indexed): < 10ms
- User profile fetch (PK): < 5ms
- Conversation history fetch (indexed): < 50ms for 100 messages
- Insert chat message: < 20ms

---

## Data Retention & Cleanup

**Retention Policies**:
- **User records**: Indefinite (or until account deletion request)
- **Conversation history**: Indefinite (users can export/delete)
- **Backups**: Neon provides automatic daily backups

**No automated cleanup**: Neon stores all data indefinitely (within free tier limits)

---

## Security Considerations

1. ✅ **Password**: Bcrypt hash (never stored plaintext), cost factor 12
2. ✅ **Email uniqueness**: Enforced at database level (UNIQUE constraint)
3. ✅ **Foreign key constraints**: Prevent orphaned records
4. ✅ **JWT secret**: Never stored in code, only in environment variables
5. ✅ **Conversation privacy**: User_id indexed to ensure users can only see own conversations
6. ✅ **No plaintext sensitive data**: All endpoints use HTTPS (Vercel enforces)

---

## Migration Strategy

When deploying to Vercel:

1. **Test schema locally**: Run CREATE TABLE statements on Neon test instance
2. **Version schema**: Tag schema version with deployment (v1.0, v1.1, etc.)
3. **No migrations on deploy**: Schema created once, then stable
4. **Backup before changes**: Neon auto-backs up, but manual backup before major changes recommended

Example migration in code:
```python
async def ensure_schema_exists():
    """Create tables if they don't exist (idempotent)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # CREATE TABLE IF NOT EXISTS for all tables
    # This runs on every function cold-start but is idempotent
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        ...
      );
    """)
    conn.commit()
    cursor.close()
```

---

## Summary

**3 Main Tables**:
1. **users** (core account data)
2. **user_backgrounds** (profile questionnaire)
3. **conversation_histories** (RAG chatbot messages)

**Relationships**:
- 1:1 (User ↔ UserBackground)
- 1:N (User → ConversationHistory)

**Key Features**:
- ✅ Indexes for performance
- ✅ Foreign keys for data integrity
- ✅ Timestamps for audit trail
- ✅ JWT stored client-side (no session table needed)
- ✅ Optimized for serverless (minimal transactions, simple queries)

**Ready for implementation**: Schema can be created in Neon with provided SQL scripts.
