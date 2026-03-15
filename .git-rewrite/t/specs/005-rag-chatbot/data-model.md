# Data Model: RAG Chatbot for Physical AI Textbook

**Date**: 2026-01-27 | **Scope**: Entity definitions, relationships, validation rules, and state transitions for chatbot backend

---

## Entity Relationship Diagram

```
┌─────────────────────┐
│  Conversation       │
├─────────────────────┤
│ id (PK)             │ 1
│ user_id             │ ├─────── N ┌──────────────────┐
│ session_id (unique) │           │  Message         │
│ created_at          │           ├──────────────────┤
│ updated_at          │           │ id (PK)          │
│ title               │           │ conversation_id  │
│ metadata (JSONB)    │           │ role             │
└─────────────────────┘           │ content          │
                                  │ embedding        │
                                  │ metadata         │
                                  │ created_at       │
                                  └────────┬─────────┘
                                           │
                                           │ 1
                                           ├─────── N ┌──────────────────┐
                                           │           │  Citation        │
                                           │           ├──────────────────┤
                                           │           │ id (PK)          │
                                           │           │ message_id (FK)  │
                                           │           │ chapter_number   │
                                           │           │ section_title    │
                                           │           │ subsection       │
                                           │           │ docusaurus_url   │
                                           │           │ ieee_text        │
                                           │           │ confidence       │
                                           │           └──────────────────┘
                                           │
                                           └─────── references ┌──────────────────┐
                                                               │ TextbookChunk    │
                                                               ├──────────────────┤
                                                               │ (Qdrant payload) │
                                                               │ id (point id)    │
                                                               │ chapter_number   │
                                                               │ section_title    │
                                                               │ content          │
                                                               │ source_file      │
                                                               │ embedding        │
                                                               └──────────────────┘

┌─────────────────────────────┐
│  EmbeddingBatch             │
├─────────────────────────────┤
│ id (PK)                     │
│ batch_id (OpenAI API ID)    │
│ status (enum)               │
│ chapters_included (array)   │
│ submitted_at                │
│ completed_at                │
│ cost_usd                    │
└─────────────────────────────┘
```

---

## Entity Definitions

### 1. Conversation

**Purpose**: Encapsulates a user session with the chatbot, containing multiple Q&A exchanges over time.

**Storage**: Neon Postgres

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|---|---|
| id | UUID | PRIMARY KEY | System-generated unique identifier |
| user_id | VARCHAR(255) | NOT NULL, INDEXED | Identifier from Docusaurus (user account or hashed IP) |
| session_id | VARCHAR(255) | NOT NULL, UNIQUE, INDEXED | HTTP session cookie or browser fingerprint; enables multi-device support |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Conversation start time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last message timestamp (auto-updated on INSERT to messages) |
| title | VARCHAR(500) | NULLABLE | Auto-generated from first question; e.g., "Understanding ROS 2 Actions" |
| metadata | JSONB | DEFAULT {} | Custom extensible attributes: `{"module_context": 1, "model_version": "gpt-4-turbo-preview"}` |

**Validation Rules**:
- `user_id` must not be empty
- `session_id` must not contain spaces or special characters (RFC 4648 base64 recommended)
- `created_at` must be ≤ `updated_at`
- `title` max 500 characters; auto-generated from first question

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE on `session_id` (enables fast lookup by session)
- INDEX on `user_id` (for listing user's conversations)
- INDEX on `updated_at DESC` (for "recent conversations" queries)

**Relationships**:
- **1-to-many** with `messages` (1 conversation has N messages)

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "student@example.com",
  "session_id": "browser_session_abc123xyz",
  "created_at": "2026-01-27T10:00:00Z",
  "updated_at": "2026-01-27T10:05:30Z",
  "title": "Bipedal Locomotion Q&A",
  "metadata": {
    "module_context": 3,
    "device": "desktop",
    "model_version": "gpt-4-turbo-preview"
  }
}
```

---

### 2. Message

**Purpose**: Individual Q&A exchange within a conversation. Stores both user queries and chatbot responses.

**Storage**: Neon Postgres

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|---|---|
| id | UUID | PRIMARY KEY | System-generated identifier |
| conversation_id | UUID | NOT NULL, FK, INDEXED | Foreign key to `conversations.id`; enables multi-turn tracking |
| role | ENUM | NOT NULL, CHECK IN ('user', 'assistant') | Distinguishes user query from chatbot response |
| content | TEXT | NOT NULL | Full text of question (role='user') or response (role='assistant') |
| embedding | VECTOR(1536) | NULLABLE | OpenAI text-embedding-3-small for semantic similarity cache |
| metadata | JSONB | DEFAULT {} | Role-specific: `{"selected_text": "...", "retrieval_chunks": 5}` for user; `{"generation_time_ms": 1200, "token_count": 128}` for assistant |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Message timestamp |

**Validation Rules**:
- `conversation_id` must exist in `conversations` table
- `content` must not be empty
- `role` must be 'user' or 'assistant' (enforced by CHECK constraint)
- For role='user': `content` length 1-2000 characters (OpenAI Agents API limit)
- For role='assistant': `content` length ≤ 4000 characters (ensure response fits context)
- `embedding` if present must be 1536 dimensions (text-embedding-3-small)

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `conversation_id` (for sorting within conversation)
- INDEX on `role` (for filtering user vs. assistant messages)
- INDEX on `created_at DESC` (for reverse chronological queries)
- INDEX on `embedding USING ivfflat` (for semantic similarity search with pgvector)

**Relationships**:
- **Many-to-one** with `conversations` (N messages belong to 1 conversation)
- **One-to-many** with `citations` (1 assistant message has N citations)

**Example**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "user",
  "content": "What is bipedal locomotion and how is it different from quadrupedal motion?",
  "embedding": [0.012, -0.045, ..., 0.089],  # 1536-dim vector
  "metadata": {
    "selected_text": null,
    "char_count": 82
  },
  "created_at": "2026-01-27T10:00:05Z"
}
```

---

### 3. Citation

**Purpose**: Structured reference to textbook source material (chapter, section, page). Provides academic integrity and traceability.

**Storage**: Neon Postgres (normalized) OR embedded in `messages.metadata` (denormalized)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|---|---|
| id | UUID | PRIMARY KEY | System-generated identifier |
| message_id | UUID | NOT NULL, FK, INDEXED | Foreign key to `messages.id` where role='assistant' |
| chapter_number | INT | NOT NULL, CHECK > 0 AND ≤ 12 | Reference to Physical AI textbook chapter (1-12 for Modules 1-4) |
| section_title | VARCHAR(500) | NOT NULL | Section heading; e.g., "Bipedal Locomotion Fundamentals" |
| subsection | VARCHAR(500) | NULLABLE | Sub-heading if applicable |
| page_reference | INT | NULLABLE | Physical or PDF page number (if available) |
| docusaurus_url | VARCHAR(1024) | NOT NULL | Direct link to section in published book; e.g., `/docs/module-3/chapter-8#bipedal-locomotion` |
| confidence_score | FLOAT | CHECK ≥ 0 AND ≤ 1 | Confidence in citation match (1.0 = direct quote, 0.7 = topic relevance) |
| ieee_formatted_text | TEXT | NOT NULL | Pre-formatted IEEE citation; e.g., "[1] Chapter 8, Section 3, pp. 245-250" |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Citation generation timestamp |

**Validation Rules**:
- `message_id` must reference an assistant message (role='assistant')
- `chapter_number` must be 1-12 (Physical AI textbook has 12 chapters across 4 modules)
- `section_title` must not be empty
- `docusaurus_url` must start with `/docs/` and be valid UTF-8
- `confidence_score` must be between 0.0 and 1.0
- `ieee_formatted_text` must follow IEEE citation format: "[N] Chapter X, Section Y" or "[N] Chapter X, pp. AA-BB"

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `message_id` (for retrieving citations per message)
- INDEX on `chapter_number` (for analytics: which chapters are most cited)

**Relationships**:
- **Many-to-one** with `messages` (N citations cite 1 assistant message)

**Example**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "chapter_number": 8,
  "section_title": "Bipedal Locomotion Fundamentals",
  "subsection": "Physics of Gait Cycles",
  "page_reference": 245,
  "docusaurus_url": "/docs/module-3/chapter-8#bipedal-locomotion",
  "confidence_score": 0.95,
  "ieee_formatted_text": "[1] Chapter 8, Section 2, pp. 245-250",
  "created_at": "2026-01-27T10:00:10Z"
}
```

---

### 4. TextbookChunk (Qdrant Vector Collection)

**Purpose**: Indexed unit of textbook content for semantic and keyword search. Stored as Qdrant point with metadata payload.

**Storage**: Qdrant Cloud vector database

**Fields (Qdrant Payload)**:

| Field | Type | Qdrant Type | Constraints | Description |
|-------|------|---|---|---|
| id | UUID | String | PRIMARY / Point ID | Unique point identifier in Qdrant |
| content | Text | String | NOT NULL | Actual chunk text (256-512 tokens) |
| module_number | Integer | Integer | 1-4 | Textbook module: 1=Fundamentals, 2=Simulation, 3=Isaac, 4=VLA |
| chapter_number | Integer | Integer | 1-12 | Chapter within module |
| section_title | String | String | NOT NULL | Heading of section containing chunk |
| subsection | String | String | NULLABLE | Sub-heading if applicable |
| heading_hierarchy | Array(String) | Keyword | e.g., ["Chapter 8", "Bipedal Locomotion", "Gait Analysis"] | Breadcrumb trail for context |
| content_type | Enum | Keyword | 'text' \| 'code' \| 'equation' | Content classification for response generation |
| chunk_index | Integer | Integer | ≥ 0 | Sequential index within section (for ordering multi-chunk responses) |
| token_count | Integer | Integer | 256-512 | Token count for budget tracking |
| source_file | String | String | e.g., "chapter-8.mdx" | Original .md/.mdx filename |
| file_hash | String | String | SHA256 | Version control hash for detecting updates |
| embedded_at | DateTime | String | ISO 8601 | When embedding was generated |

**Vectors**:

| Vector Name | Dimension | Type | Purpose |
|---|---|---|---|
| dense_vector | 1536 | Vector | OpenAI text-embedding-3-small for semantic search |
| sparse_vector | N/A | Sparse | BM25 keyword representation for hybrid search |

**Payload Metadata Example**:
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "content": "Bipedal locomotion refers to movement using two legs. In humanoid robots, this requires precise balance and coordination...",
  "module_number": 3,
  "chapter_number": 8,
  "section_title": "Bipedal Locomotion Fundamentals",
  "subsection": "Physics of Gait Cycles",
  "heading_hierarchy": ["Chapter 8: Motion Planning", "Bipedal Locomotion Fundamentals", "Physics of Gait Cycles"],
  "content_type": "text",
  "chunk_index": 0,
  "token_count": 128,
  "source_file": "chapter-8.mdx",
  "file_hash": "abc123def456...",
  "embedded_at": "2026-01-27T08:00:00Z"
}
```

**Validation Rules**:
- `module_number` must be 1-4
- `chapter_number` must be 1-12
- `section_title` must not be empty
- `token_count` must be 256-512 (enforced during ingestion)
- `content` must not be empty
- `dense_vector` must be exactly 1536 dimensions
- `source_file` must reference a .md or .mdx file

**Qdrant Indexing**:
- HNSW algorithm for dense vector search (p95 latency <30ms at scale)
- Quantization: int8 (8x storage reduction)
- Multi-vector indexing for dense + sparse

**Relationships**:
- **Referenced by** `citations` (Citation.chapter_number + section_title → TextbookChunk lookup)
- **Referenced by** `messages` (retrieval_chunks stored in metadata)

---

### 5. EmbeddingBatch

**Purpose**: Tracking for batch embedding jobs submitted to OpenAI Batch API. Enables monitoring, retry logic, and cost tracking.

**Storage**: Neon Postgres

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|---|---|
| id | UUID | PRIMARY KEY | System-generated identifier |
| batch_id | VARCHAR(255) | NULLABLE, UNIQUE, INDEXED | OpenAI Batch API job ID; e.g., "batch_abc123xyz" |
| status | ENUM | NOT NULL, CHECK IN ('submitted', 'processing', 'completed', 'failed') | Job status; determines retry logic |
| chunk_count | INT | ≥ 0 | Number of chunks in batch |
| chapters_included | INT[] | Array of 1-12 | Chapters processed in this batch |
| submitted_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When batch was submitted to OpenAI |
| completed_at | TIMESTAMP | NULLABLE | When batch completed (status='completed' or 'failed') |
| error_message | TEXT | NULLABLE | If status='failed', reason for failure |
| cost_usd | DECIMAL(10, 4) | ≥ 0 | Calculated cost of embeddings generated |

**Validation Rules**:
- `status` must be one of: 'submitted', 'processing', 'completed', 'failed'
- `completed_at` must be NULL if status='submitted' or 'processing'
- `completed_at` must be NOT NULL if status='completed' or 'failed'
- `error_message` should be populated if status='failed'
- `cost_usd` calculated as: (total_tokens / 1M) * $0.02 (OpenAI Batch API rate)

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `batch_id` (for OpenAI API callback lookups)
- INDEX on `status` (for polling incomplete batches)
- INDEX on `submitted_at DESC` (for audit trail)

**Relationships**:
- None (audit/tracking table)

**Example**:
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "batch_id": "batch_6716b6d6b00b0f01e5d8c8e6d4c2a1f0",
  "status": "completed",
  "chunk_count": 1247,
  "chapters_included": [1, 2, 3, 4, 5, 6, 7, 8],
  "submitted_at": "2026-01-26T22:00:00Z",
  "completed_at": "2026-01-27T04:30:00Z",
  "error_message": null,
  "cost_usd": 25.89
}
```

---

## State Transitions

### Conversation States

```
┌──────────────┐
│   ACTIVE     │ ← Initial state when created
└──────┬───────┘
       │ (user sends message)
       ▼
┌──────────────┐
│   IN_CHAT    │ ← Actively exchanging messages
└──────┬───────┘
       │ (user closes / inactivity >7 days)
       ▼
┌──────────────┐
│   ARCHIVED   │ ← Historical conversation (read-only)
└──────────────┘
```

**Transitions**:
- ACTIVE → IN_CHAT: On first message
- IN_CHAT → ARCHIVED: After 7 days of inactivity OR user explicitly archives
- ARCHIVED → IN_CHAT: User resumes conversation

---

### Message States

```
┌──────────────┐
│ USER_SENT    │ ← User submits query
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ RETRIEVING   │ ← Vector search in progress
└──────┬───────┘
       │
       ├─ (found) ─────┐
       │                ▼
       │          ┌──────────────┐
       │          │ GENERATING   │ ← LLM generation in progress
       │          └──────┬───────┘
       │                 │
       │                 ▼
       │          ┌──────────────┐
       └─ (not found)  │ RESPONDING  │ ← Streaming response to client
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  COMPLETED   │ ← Response delivered and stored
                  └──────────────┘
```

**Retry Logic**:
- RETRIEVING: If timeout >30s, retry once; if fails, respond with "I couldn't retrieve relevant sections. Try rephrasing."
- GENERATING: If timeout >60s or rate limited, respond with "Service temporarily unavailable. Please try again."

---

## Validation Rules

### Conversation-Level Validation

1. **User Isolation**: User can only view/modify their own conversations
   - Query: `WHERE user_id = current_user_id`

2. **Session Uniqueness**: One session_id per conversation (no duplicates)
   - Constraint: UNIQUE(session_id)

3. **Temporal Ordering**: created_at ≤ updated_at
   - Trigger: Auto-update updated_at on message insert

### Message-Level Validation

1. **Query Length**: 1-2000 characters (OpenAI Agents API hard limit)
   - Check: `LENGTH(content) BETWEEN 1 AND 2000`

2. **Response Length**: ≤4000 characters (fit in context window)
   - Check: For role='assistant', `LENGTH(content) ≤ 4000`

3. **Conversation Existence**: message.conversation_id must exist
   - Constraint: FOREIGN KEY (conversation_id) REFERENCES conversations(id)

4. **Role Enum**: Only 'user' or 'assistant'
   - Constraint: `role IN ('user', 'assistant')`

### Citation-Level Validation

1. **Chapter Range**: 1-12 (Physical AI textbook chapters)
   - Check: `chapter_number BETWEEN 1 AND 12`

2. **URL Format**: Must start with `/docs/` and be valid
   - Regex: `^/docs/[a-z0-9-]+(/[a-z0-9-]+)*$`

3. **Confidence Score**: 0.0-1.0
   - Check: `confidence_score BETWEEN 0.0 AND 1.0`

4. **IEEE Format**: Must contain "Chapter" and section reference
   - Regex: `^\[\\d+\\] Chapter \\d+.*$`

5. **Message Exists**: citation.message_id must reference an assistant message
   - Constraint: `FOREIGN KEY (message_id) REFERENCES messages(id) WHERE role='assistant'`

---

## Indexing Strategy

### Postgres Indexes

| Index | Table | Columns | Type | Rationale |
|-------|-------|---------|------|-----------|
| pk_conversations | conversations | id | PRIMARY | Fast lookup by conversation ID |
| uk_session_id | conversations | session_id | UNIQUE | Ensure session uniqueness |
| idx_conversations_user_id | conversations | user_id | BTREE | List user's conversations (filter by user_id) |
| idx_conversations_updated_at | conversations | updated_at DESC | BTREE | Recent conversations first (ORDER BY updated_at DESC) |
| pk_messages | messages | id | PRIMARY | Fast message lookup |
| fk_conversation_id | messages | conversation_id | BTREE | Retrieve messages for conversation |
| idx_messages_role | messages | role | BTREE | Filter user vs. assistant (optional optimization) |
| idx_messages_created_at | messages | created_at DESC | BTREE | Sort within conversation chronologically |
| idx_messages_embedding_ivfflat | messages | embedding | IVFFLAT | Semantic similarity search (pgvector) |
| pk_citations | citations | id | PRIMARY | Fast citation lookup |
| fk_message_id | citations | message_id | BTREE | Retrieve citations for message |
| idx_citations_chapter | citations | chapter_number | BTREE | Analytics: most-cited chapters |
| pk_embedding_batches | embedding_batches | id | PRIMARY | Fast batch lookup |
| uk_batch_id | embedding_batches | batch_id | UNIQUE | OpenAI API callback lookups |
| idx_batch_status | embedding_batches | status | BTREE | Poll incomplete batches |
| idx_batch_submitted_at | embedding_batches | submitted_at DESC | BTREE | Audit trail |

### Qdrant Indexes

- **HNSW** (Hierarchical Navigable Small World):
  - m=16 (connections per node)
  - ef_construct=200 (construction parameter for quality)
  - Achieves <30ms p95 latency at millions of vectors

- **Quantization**: int8 (reduce storage 8x, <2% recall loss)

- **Multi-vector**: Support both dense (semantic) and sparse (keyword) for hybrid search

---

## Data Retention & Cleanup

### Message Archive Policy

- **Active**: Messages kept in `messages` table indefinitely
- **Manual Deletion**: Users can delete conversations via `/conversations/{id}` DELETE endpoint
  - Cascade delete: messages and citations also deleted
- **GDPR Compliance**: Provide data export (JSON) and deletion on request

### Embedding Batch Cleanup

- **Retention**: Keep completed batches for 30 days (audit trail)
- **Deletion**: Drop records with status='failed' after 7 days (no data loss, already in Qdrant)
- **Cost Tracking**: Aggregate monthly cost_usd for reporting

### Vector Database (Qdrant) Updates

- **Content Refresh**: When textbook is updated, full re-ingestion is required
  - Mark old embeddings obsolete (set embedded_at < refresh_date)
  - Upload new embeddings alongside (no downtime)
  - Atomic switchover (point all queries to new collection)
- **Retention**: Archive old collection for 1 week, then delete

---

## Migration & Schema Versioning

### Initial Schema (v1.0)

- Deploy all tables and indexes as defined above
- Run migrations in order: conversations → messages → citations → embedding_batches
- Seed data: empty (no pre-existing conversations)

### Future Migrations (Versioning Strategy)

Use Alembic (Python DB migration tool) with semantic versioning:

```
migrations/
├── versions/
│   ├── 001_initial_schema.py (v1.0)
│   ├── 002_add_conversation_title.py (v1.1)
│   └── 003_add_embedding_batch_tracking.py (v1.2)
└── script.py.mako
```

Each migration file includes:
- `upgrade()`: Forward migration
- `downgrade()`: Rollback for safety

---

## Compliance & Audit

### User Privacy

- PII: Minimize storage (user_id, session_id only; no email in messages)
- GDPR: Provide export and deletion endpoints
- Retention: Keep conversations indefinitely (user-controlled deletion available)

### Audit Logging

- Track all changes to conversations/messages (optional: separate `audit_log` table)
- Log: who (user_id), what (operation), when (timestamp), where (resource_id)

### Data Integrity

- Foreign key constraints enforce referential integrity
- Check constraints validate enum values and ranges
- Unique constraints prevent duplicates
- Indexes ensure query performance and consistency

---

**Schema Status**: ✅ Ready for implementation
**Migration Tool**: Alembic (Python)
**Database**: Neon Postgres with pgvector extension
**Vector DB**: Qdrant Cloud
