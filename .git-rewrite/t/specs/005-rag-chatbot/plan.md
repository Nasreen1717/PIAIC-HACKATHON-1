# Implementation Plan: RAG Chatbot for Physical AI Textbook

**Branch**: `005-rag-chatbot` | **Date**: 2026-01-27 | **Spec**: [Feature Specification](./spec.md)
**Input**: FastAPI backend, Qdrant indexing, ChatKit integration, content ingestion, OpenAI Agents config, Neon Postgres schema

## Summary

Build a production-ready RAG (Retrieval-Augmented Generation) chatbot embedded in Docusaurus that answers questions grounded exclusively in the Physical AI textbook content. The system combines FastAPI backend for streaming chat, Qdrant Cloud for semantic vector search with hybrid retrieval, OpenAI Agents API (GPT-4) for grounded response generation, and Neon Postgres for conversation history. ChatKit SDK provides seamless embedded UI. Content ingestion uses batch embeddings with OpenAI's Batch API for cost efficiency. All responses include IEEE-formatted citations with source chapter/section references.

**Architecture Pillars:**
1. **Grounding First**: Responses strictly limited to textbook material; hallucination prevention through system prompts and citation validation
2. **Streaming & Performance**: SSE-based streaming responses achieving p95 latency <1.5s (within 3s SLO)
3. **Academic Integrity**: Every response includes IEEE citations with chapter/section provenance
4. **Scalability**: Supports 100-1000 concurrent students with <100ms query latency via vector search

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI SDK, Qdrant Python client, Neon Postgres adapter, LangChain (text splitting)
**Storage**: Neon Postgres (conversation history, user sessions), Qdrant Cloud (vector embeddings)
**Testing**: pytest, hypothesis (property-based), integration tests against Qdrant/OpenAI mocks
**Target Platform**: Cloud deployment (Linux server, scalable to AWS/GCP); frontend embeds in Docusaurus v2+
**Project Type**: Backend API + CLI ingestion tools + Frontend integration
**Performance Goals**: p95 latency 1500ms cold start, p50 300ms with caching; 95% of in-scope questions answered with citations
**Constraints**: 3-second response time SLO (FR-005); 100% citation accuracy (SC-002); <30ms vector search latency (p95)
**Scale/Scope**: 12 chapters (~500K tokens total), 10k+ unique queries per semester, 100-1000 concurrent users

---

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

Per `.specify/memory/constitution.md`:

### I. Technical Accuracy and Sourcing ✅
- **Status**: Compliant
- **Evidence**: All research findings cite official documentation (OpenAI, Qdrant, FastAPI docs), validated with 30+ sources
- **Commitment**: Response generation enforces grounding constraint; citations generated from indexed textbook metadata with full lineage traceability

### II. Hands-On Learning Through Working Code ✅
- **Status**: Compliant
- **Evidence**: Implementation plan includes working examples, test patterns, and end-to-end demo code
- **Commitment**: All server code production-ready; batch ingestion tested against real textbook content; integration tests validate grounding

### III. Spec-Driven Development and Full Documentation ✅
- **Status**: Compliant
- **Evidence**: This plan, data model, and API contracts follow spec-driven approach; all features mapped to acceptance criteria
- **Commitment**: Tasks will break into testable units; zero-hallucination tolerance enforced via automated tests

### IV. Modular, Progressive Content Architecture ✅
- **Status**: Compliant
- **Evidence**: Chatbot surfaces only Modules 1-4 (12 chapters); no external knowledge injection
- **Commitment**: Content ingestion respects module boundaries; citations link to chapter metadata

### V. Safety, Simulation-First, and Hardware Flexibility ✅
- **Status**: Compliant (N/A for chatbot, applies to robotics content)
- **Evidence**: Chatbot does not execute code or control hardware
- **Commitment**: No impact on robotics modules; textbook content unmodified

**Overall Gate Result: ✅ PASSED**

---

## Project Structure

### Documentation (this feature)

```text
specs/005-rag-chatbot/
├── plan.md                    # This file (implementation plan)
├── spec.md                    # Feature specification
├── research.md                # Phase 0 output (architecture research, 30+ sources)
├── data-model.md              # Phase 1 output (entities, schema)
├── contracts/                 # Phase 1 output (API contracts)
│   ├── openapi.yaml
│   ├── postgres-schema.sql
│   └── qdrant-config.json
├── quickstart.md              # Phase 1 output (developer guide)
├── tasks.md                   # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
└── artifacts/
    ├── architecture-diagram.md
    ├── latency-budget.md
    └── cost-analysis.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py    # Conversation, Message, Citation models
│   │   ├── qdrant_config.py   # Vector DB schemas
│   │   └── requests.py        # Pydantic request/response models
│   ├── services/
│   │   ├── chat_service.py    # Core agent orchestration
│   │   ├── retrieval_service.py # Qdrant hybrid search
│   │   ├── embedding_service.py # OpenAI embeddings, batch processing
│   │   └── citation_service.py  # IEEE citation formatting
│   ├── api/
│   │   ├── routes.py          # FastAPI endpoints (/chat, /history, /health)
│   │   └── middleware.py      # Request logging, error handling
│   ├── config.py              # Configuration (env vars, constants)
│   └── main.py                # FastAPI app initialization
├── tests/
│   ├── unit/
│   │   ├── test_chat_service.py
│   │   ├── test_retrieval.py
│   │   └── test_citations.py
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   └── test_qdrant_postgres.py
│   └── conftest.py            # Shared fixtures
├── scripts/
│   ├── ingest_content.py      # Batch ingestion from MDX files
│   ├── seed_embeddings.py     # Vector embedding generation
│   └── migrate_db.py          # Neon Postgres migration
├── requirements.txt
├── Dockerfile
└── docker-compose.yml         # Local dev: Qdrant + Postgres

frontend/
├── src/
│   ├── components/
│   │   └── ChatbotWidget.tsx  # ChatKit wrapper component
│   └── pages/
│       └── chatbot-integration.md # Docusaurus sidebar integration
└── tests/
    └── integration.test.ts

docs/
├── ARCHITECTURE.md            # Architecture overview
├── DEPLOYMENT.md              # Production deployment guide
└── TROUBLESHOOTING.md         # Common issues and debugging
```

**Structure Decision**: Web application pattern with separate backend API and frontend integration. Backend handles all AI/retrieval logic independently; frontend uses ChatKit SDK for minimal build overhead. This separation enables:
- Independent scaling of API
- Replacement of ChatKit UI without backend changes
- Clear contract boundaries (OpenAPI spec)
- Easier testing and debugging

---

## Architecture Overview

### Component Diagram

```
[Docusaurus Sidebar]
        ↓ (ChatKit SDK)
[Chat UI Component]
        ↓ HTTP/SSE
[FastAPI Backend]
        ├─→ [OpenAI Agents API] (GPT-4, function calling)
        ├─→ [Qdrant Cloud] (vector search, hybrid retrieval)
        ├─→ [Neon Postgres] (conversation history, sessions)
        └─→ [Monitoring: Prometheus + Grafana]
```

### Key Design Decisions

| Decision | Chosen | Why | Alternatives |
|----------|--------|-----|--------------|
| **API Framework** | FastAPI | Async/await, streaming, auto-docs | Flask, Django (slower) |
| **Agent Orchestration** | OpenAI Agents SDK | Native function calling, structured outputs | LangChain (more boilerplate), LangGraph (overly complex) |
| **Vector Search** | Qdrant hybrid (dense + sparse) | Multi-vector support, HNSW, quantization | Pinecone (lock-in), Weaviate (steeper learning curve) |
| **Session DB** | Neon Postgres | Serverless, instant compute, pooling | Firebase/Firestore (vendor lock-in), MongoDB (not relational) |
| **Embedding Model** | OpenAI text-embedding-3-small | Cost-optimized, 1536 dims, high quality | open-source BERT (lower quality on technical terms) |
| **UI Integration** | ChatKit Web Component | Zero build, iframe-less, OpenAI-native | Custom React component (more code), iframe (security) |
| **Content Ingestion** | OpenAI Batch API + LangChain splitting | Cost savings (75%), reliability | Real-time API calls (10x cost), naive chunking (loses context) |
| **Caching Strategy** | 3-tier (query cache, semantic cache, in-process LRU) | Hit rate >35%, reduces latency | Single-tier (miss rate too high), distributed Redis (cost) |

---

## Data Model

### Core Entities

#### 1. **Conversation**
- **Purpose**: User session enclosing multiple Q&A exchanges
- **Storage**: Neon Postgres
- **Schema**:
  ```
  id (UUID)           # Primary key
  user_id (VARCHAR)   # Docusaurus user or browser cookie hash
  session_id (VARCHAR)# HTTP session identifier
  created_at (TIMESTAMP)
  updated_at (TIMESTAMP)
  title (VARCHAR, optional) # Auto-generated from first question
  metadata (JSONB)    # Custom fields (module context, model version)
  ```

#### 2. **Message**
- **Purpose**: Individual user query or chatbot response
- **Storage**: Neon Postgres
- **Schema**:
  ```
  id (UUID)
  conversation_id (UUID, FK) # Foreign key to Conversation
  role (ENUM: 'user' | 'assistant')
  content (TEXT)      # Question or response text
  embedding (VECTOR, optional) # Query embedding for semantic cache
  metadata (JSONB)    # For assistant: model_version, generation_time_ms
  created_at (TIMESTAMP)
  ```

#### 3. **Citation**
- **Purpose**: IEEE-formatted reference to textbook source
- **Storage**: Nested in Message metadata or separate table
- **Schema**:
  ```
  id (UUID)
  message_id (UUID, FK)
  chapter_number (INT)
  section_title (VARCHAR)
  subsection (VARCHAR, optional)
  page_reference (INT, optional)
  docusaurus_url (VARCHAR) # Link to book section
  confidence_score (FLOAT 0-1) # Metadata preservation quality
  ieee_formatted_text (TEXT) # Pre-formatted IEEE citation
  ```

#### 4. **TextbookChunk** (Qdrant-side metadata)
- **Purpose**: Indexed unit of textbook content
- **Storage**: Qdrant point payload
- **Schema**:
  ```
  id (UUID)           # Point ID in Qdrant
  content (TEXT)      # Chunk text
  module_number (INT) # 1-4
  chapter_number (INT)# 1-12
  section_title (VARCHAR)
  subsection (VARCHAR)
  heading_hierarchy (ARRAY) # [Chapter, Section, Subsection]
  content_type (ENUM: 'text' | 'code' | 'equation')
  chunk_index (INT)   # Sequential position in section
  token_count (INT)   # For budget tracking
  source_file (VARCHAR) # Original .md/.mdx file
  file_hash (VARCHAR) # Version control
  embedded_at (TIMESTAMP)

  # Vectors
  dense_vector (VECTOR, 1536) # OpenAI text-embedding-3-small
  sparse_vector (VECTOR, optional) # BM25 for keyword search
  ```

#### 5. **EmbeddingBatch** (Ingestion tracking)
- **Purpose**: Track batch embedding jobs for monitoring and retry
- **Storage**: Neon Postgres
- **Schema**:
  ```
  id (UUID)
  batch_id (VARCHAR)  # OpenAI Batch API ID
  status (ENUM: 'submitted' | 'processing' | 'completed' | 'failed')
  chunk_count (INT)
  chapters_included (ARRAY INT)
  submitted_at (TIMESTAMP)
  completed_at (TIMESTAMP, optional)
  error_message (TEXT, optional)
  cost_usd (DECIMAL)
  ```

---

## API Contracts

### REST Endpoints (OpenAPI 3.0)

#### 1. **POST /chat**
- **Purpose**: Submit user query and receive streaming response
- **Request**:
  ```json
  {
    "query": "What is bipedal locomotion?",
    "conversation_id": "uuid or null (creates new)",
    "selected_text": "From chapter 8...",  # Optional
    "system_context": "Module 3: Advanced Perception"  # Optional
  }
  ```
- **Response** (Server-Sent Events, 200 OK):
  ```
  data: {"type": "thinking", "delta": "Searching textbook..."}
  data: {"type": "retrieval", "chunks": [{"chapter": 8, ...}]}
  data: {"type": "response_start", "timestamp": "..."}
  data: {"type": "text_delta", "delta": "Bipedal locomotion is..."}
  data: {"type": "citation", "ieee": "..."}
  data: {"type": "response_end", "confidence": 0.92}
  ```
- **Errors**:
  - 400: Invalid query (empty, too long)
  - 408: Timeout (vector search or LLM generation >30s)
  - 429: Rate limited (user or OpenAI quota exceeded)
  - 503: Qdrant or OpenAI service unavailable

#### 2. **GET /conversations/{conversation_id}**
- **Purpose**: Retrieve conversation history
- **Response** (200 OK):
  ```json
  {
    "id": "uuid",
    "user_id": "...",
    "messages": [
      {
        "role": "user",
        "content": "Question?",
        "timestamp": "2026-01-27T10:00:00Z"
      },
      {
        "role": "assistant",
        "content": "Answer with context...",
        "citations": [
          {
            "ieee": "[1] Chapter 8, Section 3",
            "url": "/docs/module-3/chapter-8#section-3"
          }
        ],
        "timestamp": "2026-01-27T10:00:03Z"
      }
    ],
    "created_at": "2026-01-27T09:00:00Z",
    "updated_at": "2026-01-27T10:05:00Z"
  }
  ```
- **Errors**:
  - 404: Conversation not found or unauthorized access

#### 3. **GET /conversations**
- **Purpose**: List user's recent conversations
- **Query Parameters**: `limit=10`, `offset=0`
- **Response** (200 OK):
  ```json
  {
    "conversations": [
      {
        "id": "uuid",
        "title": "Understanding ROS 2 Actions",
        "preview": "Q: What are ROS 2 actions? A: Actions are...",
        "message_count": 5,
        "updated_at": "2026-01-27T10:05:00Z"
      }
    ],
    "total": 47,
    "limit": 10,
    "offset": 0
  }
  ```

#### 4. **DELETE /conversations/{conversation_id}**
- **Purpose**: Delete a conversation (user data privacy)
- **Response**: 204 No Content
- **Errors**: 404, 403 Forbidden (not conversation owner)

#### 5. **POST /ingest** (Admin endpoint)
- **Purpose**: Trigger content ingestion from textbook files
- **Request**:
  ```json
  {
    "chapters": [1, 2, 3, 4],  # Chapter numbers to ingest
    "force_refresh": false,
    "chunk_size": 512,  # Tokens per chunk
    "overlap": 50       # Token overlap between chunks
  }
  ```
- **Response** (202 Accepted):
  ```json
  {
    "batch_id": "openai_batch_123456",
    "status": "submitted",
    "estimated_completion": "2026-01-27T12:00:00Z",
    "estimated_cost_usd": 2.50
  }
  ```
- **Errors**: 403 Forbidden (unauthorized), 400 Bad Request

#### 6. **GET /health**
- **Purpose**: Health check endpoint
- **Response** (200 OK):
  ```json
  {
    "status": "healthy",
    "qdrant": "connected",
    "postgres": "connected",
    "openai": "responsive",
    "cache": {"hit_rate": 0.38, "items": 1024},
    "timestamp": "2026-01-27T10:00:00Z"
  }
  ```

---

## Database Schema

### Neon Postgres (SQL)

```sql
-- Conversations table
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255) NOT NULL,
  session_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  title VARCHAR(500),
  metadata JSONB DEFAULT '{}',
  UNIQUE(session_id)
);

-- Messages table
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  embedding VECTOR(1536),  -- For semantic similarity search
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Citations table
CREATE TABLE citations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  chapter_number INT NOT NULL,
  section_title VARCHAR(500) NOT NULL,
  subsection VARCHAR(500),
  page_reference INT,
  docusaurus_url VARCHAR(1024),
  confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
  ieee_formatted_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- Embedding batch tracking
CREATE TABLE embedding_batches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_id VARCHAR(255) UNIQUE,
  status VARCHAR(50) NOT NULL CHECK (status IN ('submitted', 'processing', 'completed', 'failed')),
  chunk_count INT,
  chapters_included INT[],
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,
  error_message TEXT,
  cost_usd DECIMAL(10, 4),

  INDEX idx_batch_id (batch_id),
  INDEX idx_status (status)
);

-- Indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_citations_message_id ON citations(message_id);
CREATE INDEX idx_citations_chapter ON citations(chapter_number);

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;
```

### Qdrant Configuration

```yaml
# qdrant-config.json
{
  "collection_name": "textbook_chunks",
  "vectors": {
    "dense": {
      "size": 1536,
      "distance": "Cosine",
      "quantization": {
        "scalar": {
          "type": "int8",
          "quantile": 0.99
        }
      }
    },
    "sparse": {
      "index": {
        "on_disk": true
      }
    }
  },
  "payload_schema": {
    "module_number": { "type": "integer" },
    "chapter_number": { "type": "integer" },
    "section_title": { "type": "text" },
    "content_type": { "type": "keyword" },
    "source_file": { "type": "text" },
    "embedded_at": { "type": "date" }
  },
  "hnsw_config": {
    "m": 16,
    "ef_construct": 200,
    "max_indexing_threads": 4,
    "payload_m": 8
  }
}
```

---

## Deployment Architecture

### Cloud Infrastructure

```
┌─────────────────────────────────────────┐
│  Docusaurus (GitHub Pages)              │
│  ├─ Markdown content (12 chapters)      │
│  └─ ChatKit widget embed                │
└──────────────┬──────────────────────────┘
               │ HTTP/SSE
┌──────────────▼──────────────────────────┐
│  FastAPI Backend (Cloud Run / Lambda)   │
│  ├─ Async chat endpoints                │
│  └─ Content ingestion CLI               │
└──────┬──────────────────┬───────────────┘
       │                  │
       │                  │
   ┌───▼─────┐        ┌───▼─────────┐
   │  Qdrant │        │  Neon Postgres
   │  Cloud  │        │  (Serverless)
   │ (vectors)        │  (sessions/msgs)
   └─────────┘        └───────────────┘
       ▲                  ▲
       │                  │
       └──────┬───────────┘
              │
       ┌──────▼──────┐
       │ OpenAI API  │
       │ (GPT-4,     │
       │ embeddings) │
       └─────────────┘
```

---

## Latency Budget & Performance

### Target Response Time: 3 seconds (SLO)

| Component | Latency (p95) | % of Budget | Notes |
|-----------|---|---|---|
| Network + parsing | 100ms | 7% | Client-to-server, JSON parse |
| Vector search (Qdrant) | 30ms | 2% | Hybrid search with 5 top-k results |
| LLM generation (streaming) | 1000ms | 67% | GPT-4 stream initiation + tokens |
| Citation generation | 50ms | 3% | Metadata lookup and formatting |
| Response serialization | 50ms | 3% | JSON encoding + SSE framing |
| **Buffer (safety margin)** | 320ms | 18% | Network jitter, retries, cache misses |
| **Total** | **1550ms** | **100%** | **Within 3s SLO ✓** |

### Caching Strategy for Latency Improvement

**3-Tier Cache** (hit rate target: >35%):

1. **Query Cache (L1)**: Exact match, 1-hour TTL
   - Store full responses for identical queries
   - Hit rate: 5-10% (student repetition)

2. **Semantic Cache (L2)**: Qdrant-integrated, 7-day TTL
   - Store responses for queries with >95% embedding similarity
   - Hit rate: 15-20% (paraphrasing, follow-ups)

3. **In-Process LRU (L3)**: Document chunks, 1-hour TTL
   - Most-recently-used textbook sections in memory
   - Hit rate: 15-25% (focused study)

**Expected Performance with Caching:**
- Cold start (no cache): p95 = 1550ms
- Warm (L2/L3 hits): p50 = 300ms, p95 = 800ms
- Query cache hit (L1): p95 = 50ms

---

## Risk Analysis & Mitigation

### Top 3 Risks

| Risk | Blast Radius | Mitigation |
|------|---|---|
| **Hallucination**: LLM generates answers not in textbook | High (academic integrity violation) | System prompt enforcement, citation validation, automated testing, confidence scoring |
| **Vector search misses**: Relevant textbook sections not retrieved | Medium (user frustration, incomplete answers) | Hybrid search (dense + sparse BM25), ensemble retrieval, low-confidence fallback messages |
| **Latency SLO violations**: >3s responses | Medium (poor UX, student churn) | 3-tier caching, connection pooling, rate limiting, graceful degradation |

### Guardrails Implemented

1. **Grounding Enforcement**: System prompt + post-generation validation
2. **Citation Validation**: Automated check that all claims cite retrieved chunks
3. **Low-Confidence Handling**: If retrieval confidence <0.70, respond: "I'm not confident in this answer. Try reviewing Section X directly."
4. **Rate Limiting**: Per-user (100 queries/hour), per-IP (1000/hour)
5. **Circuit Breaker**: If OpenAI API errors exceed threshold, failover to cached responses only
6. **Monitoring**: SLO dashboards, hallucination detectors, cost tracking

---

## Success Criteria Mapping

| Success Criterion | Acceptance Threshold | Measurement Method |
|---|---|---|
| **SC-001**: In-scope Q&A success rate | 95% with citations within 3s | Sample 100+ diverse questions; manual review + automated grounding check |
| **SC-002**: 100% citation accuracy | Zero hallucinated citations | Automated test: cross-reference every citation with indexed chunks |
| **SC-003**: Text selection latency improvement | ≥30% reduction vs. vector search | Compare response times: text selection path vs. vector search path |
| **SC-004**: Conversation persistence | 99% accuracy across sessions | Store/retrieve 100 conversations; verify no data loss |
| **SC-005**: Embedding quality | ≥90% of test queries retrieve relevant sections | Run 200 test queries; measure relevance (Precision@5) |
| **SC-006**: Out-of-scope handling | ≥95% correctly identified | Test 50 out-of-scope queries; verify graceful rejection |
| **SC-007**: Multi-turn context preservation | 90% accuracy in follow-ups | Test 50 multi-turn conversations; verify context continuity |
| **SC-008**: ChatKit integration | Loads in <2s, no page blocking | Measure load time with Lighthouse; test concurrent chatbot usage |

---

## Implementation Phases

### Phase 1: Backend Scaffolding (Week 1)
- [ ] FastAPI app structure, Pydantic models
- [ ] Neon Postgres schema migration
- [ ] Qdrant collection setup and client initialization
- [ ] OpenAI client configuration

### Phase 2: Core Chat Engine (Week 2)
- [ ] Retrieval service (Qdrant hybrid search)
- [ ] Agent orchestration (OpenAI Agents API)
- [ ] Streaming response handler (SSE)
- [ ] Citation generation from retrieved chunks

### Phase 3: Content Ingestion (Week 2-3)
- [ ] Markdown/MDX parsing and chunking
- [ ] Batch embedding with OpenAI Batch API
- [ ] Qdrant upsert pipeline
- [ ] Admin ingestion endpoint

### Phase 4: Persistence & Caching (Week 3)
- [ ] Postgres conversation storage
- [ ] Query and semantic caching
- [ ] Session management
- [ ] History retrieval endpoints

### Phase 5: Frontend Integration (Week 4)
- [ ] ChatKit SDK embed in Docusaurus
- [ ] Error boundary and fallback UI
- [ ] Analytics event tracking
- [ ] Accessibility (a11y) testing

### Phase 6: Testing & Optimization (Week 4)
- [ ] End-to-end integration tests
- [ ] Latency benchmarking and tuning
- [ ] Hallucination detection and mitigation
- [ ] Load testing (100+ concurrent users)

### Phase 7: Deployment & Monitoring (Week 5)
- [ ] Cloud Run / Lambda deployment
- [ ] Prometheus metrics and Grafana dashboards
- [ ] SLO alerting
- [ ] Runbooks for common failures

---

## Follow-Up & Next Steps

After plan approval:

1. **Specification Refinement**: Clarify any ambiguous acceptance criteria or performance targets
2. **Task Generation**: Run `/sp.tasks` to break plan into granular, testable work units
3. **Architecture Decision Records**: Document significant choices (vector DB selection, caching strategy) via `/sp.adr`
4. **Quickstart Generation**: Create developer guide with setup instructions, local dev environment, and integration examples

---

**Plan Status**: ✅ Ready for team review and approval
**Estimated Effort**: 5 weeks (4-5 full-time engineers)
**Risk Level**: Medium (new integrations with OpenAI Agents, Qdrant; but well-researched patterns)
