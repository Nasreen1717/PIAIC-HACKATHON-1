# RAG Chatbot Implementation Quick Start

**For:** Engineering teams beginning implementation
**References:** `/specs/005-rag-chatbot/research.md` (detailed patterns)
**Status:** Ready for development sprint planning

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    Docusaurus Frontend                       │
│  (ChatKit Web Component iframe-less)                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/SSE
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Streaming)                     │
│  • OpenAI Agents API (function calling)                      │
│  • Request → Pydantic validation                             │
│  • Response → SSE streaming (real-time tokens)               │
└──┬─────────────────┬──────────────────────────┬──────────────┘
   │                 │                          │
   ↓                 ↓                          ↓
┌──────────┐  ┌────────────────┐  ┌──────────────────┐
│ Qdrant   │  │ Neon Postgres  │  │ Redis Cache      │
│ (Vector  │  │ (Sessions +    │  │ (Query cache,    │
│  Search) │  │  History)      │  │ Semantic cache)  │
└──────────┘  └────────────────┘  └──────────────────┘
   ↑
   │ Content Ingestion (Batch API)
   │
┌──────────────────────────────────┐
│ Markdown/MDX Files (Textbook)     │
│ → Chunking (2-layer)              │
│ → Batch Embeddings (OpenAI)       │
│ → Upsert with metadata            │
└──────────────────────────────────┘
```

---

## Technology Stack (Validated)

| Layer | Technology | Why | Key Pattern |
|-------|-----------|-----|------------|
| **API** | FastAPI | Async, auto-docs, streaming | StreamingResponse + SSE |
| **LLM** | OpenAI Agents API (GPT-4 Turbo) | Function calling, structured outputs | tools schema + Pydantic |
| **Vector DB** | Qdrant (Cloud) | Hybrid search, HNSW, quantization | Multi-vector (dense + sparse) |
| **Session DB** | Neon Postgres | Serverless, pooling, instant compute | PgBouncer (10k connections) |
| **Cache L1** | Redis | Query cache (exact match) | 1-hour TTL |
| **Cache L2** | Qdrant | Semantic cache (similarity > 0.95) | 7-day TTL |
| **Embed L3** | In-process | Document chunks (LRU) | 1-hour TTL |
| **UI Embed** | ChatKit Web Component | Zero build, OpenAI-native | `<openai-chatkit>` custom element |
| **Monitoring** | Prometheus + Grafana | Latency tracking, SLO dashboards | Track 6 latency components |

---

## Implementation Phases

### Phase 0: Setup (1-2 days)
```bash
# 1. Provision infrastructure
- [ ] Qdrant Cloud instance (10GB, HNSW)
- [ ] Neon Postgres (serverless branch)
- [ ] Redis (local or Cloud)
- [ ] OpenAI API key (Batch API enabled)

# 2. Clone repo & install deps
- [ ] python3.11+ venv
- [ ] pip install fastapi uvicorn openai qdrant-client asyncpg sqlalchemy redis
- [ ] pip install langchain-text-splitters pydantic

# 3. Environment setup
- [ ] Copy .env.example → .env
- [ ] Fill: OPENAI_API_KEY, QDRANT_URL, DATABASE_URL, REDIS_URL
```

### Phase 1: Content Ingestion (2-3 days)
**Owner: Data Engineer**

```bash
# 1. Parse & chunk textbook
- [ ] Load 12 chapters from /docs
- [ ] Use MarkdownHeaderTextSplitter (by chapter → section)
- [ ] Apply RecursiveCharacterTextSplitter (512 tokens, 50 overlap)
- [ ] Extract metadata (file_path, heading, subsection)

# 2. Batch embed with OpenAI
- [ ] Create batch requests (custom_id: source#chunk_index)
- [ ] Submit via Batch API (100K chunks → $0.02 cost)
- [ ] Poll for completion (6 hours typical)

# 3. Upsert to Qdrant
- [ ] Create collection: docs (dense + sparse vectors)
- [ ] Upsert points with metadata payload
- [ ] Test hybrid search retrieval

# Code reference: research.md Section 6 (Content Ingestion Pipeline)
```

### Phase 2: Backend API (3-4 days)
**Owner: Backend Engineer**

```bash
# 1. FastAPI scaffold
- [ ] Main app: @app.post("/chat")
- [ ] Request model: ChatRequest (query, selected_text?, conversation_id)
- [ ] Response: StreamingResponse (SSE format)

# 2. Retrieval pipeline
- [ ] Vector search (Qdrant hybrid search)
- [ ] Query-level cache check (Redis)
- [ ] Semantic cache check (Qdrant cache collection)
- [ ] Fallback to keyword search if no results

# 3. Generation pipeline
- [ ] System prompt with grounding + context
- [ ] OpenAI Agents API call with function definitions
- [ ] Stream tokens via SSE
- [ ] Extract citations from metadata
- [ ] Handle errors (timeout, rate limit, hallucination)

# 4. Session management
- [ ] AsyncSession with Neon (asyncpg)
- [ ] Get-or-create conversation
- [ ] Append messages (user + assistant)
- [ ] Retrieve history (last 10 messages)

# Code reference: research.md Section 1 (FastAPI) + Section 4 (Neon)
```

### Phase 3: Caching & Optimization (2-3 days)
**Owner: Backend Engineer + SRE**

```bash
# 1. Query cache (Redis)
- [ ] Hash query string → cache key
- [ ] TTL: 1 hour
- [ ] Return full response if cache hit

# 2. Semantic cache (Qdrant)
- [ ] Embed query → search cache collection
- [ ] Similarity threshold: 0.95
- [ ] TTL: 7 days
- [ ] Store query + cached_results as payload

# 3. Document cache (in-process)
- [ ] LRU cache for recently retrieved chunks
- [ ] TTL: 1 hour

# 4. Parallel execution
- [ ] Retrieve documents concurrently with LLM streaming
- [ ] Don't wait for retrieval to start generation
- [ ] Yield tokens as they arrive

# Code reference: research.md Section 8 (Latency Optimization)
```

### Phase 4: Database Schema (1-2 days)
**Owner: Backend Engineer**

```sql
-- Phase 4a: Create schema
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_user_conv (user_id, created_at DESC)
);

CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB,  -- {chunk_ids, citations, tokens_used}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_conv_msg (conversation_id, created_at)
);

-- Phase 4b: Test queries
- [ ] GET /api/conversations/:user_id (retrieve all)
- [ ] GET /api/conversations/:conv_id/messages?limit=10
- [ ] POST /api/conversations/:conv_id/messages (append)
- [ ] Verify latency < 50ms for typical queries
```

### Phase 5: ChatKit Integration (2-3 days)
**Owner: Frontend Engineer**

```jsx
// Phase 5a: Docusaurus component
import ChatBot from '@components/ChatBot';

export default function DocusaurusWithChat() {
  return (
    <>
      <DocusaurusPage />
      <ChatBot
        apiEndpoint="/api/chat"
        conversationId={localStorage.getItem('conv_id')}
        onThreadChange={(id) => localStorage.setItem('conv_id', id)}
      />
    </>
  );
}

// Phase 5b: Web component
<openai-chatkit
  config={{
    apiKey: OPENAI_API_KEY,
    threadId: conversationId,
    onThreadChange: (id) => saveThreadId(id)
  }}
/>

// Code reference: research.md Section 5 (ChatKit SDK)
```

### Phase 6: Citation Generation (1-2 days)
**Owner: Backend Engineer**

```python
# Phase 6a: Generate IEEE citations
def generate_citation(metadata):
    return f'"{metadata["title"]}," Section {metadata["section"]}, [Online]. Available: {metadata["url"]}'

# Phase 6b: Deduplicate by source
seen_sources = set()
for result in search_results:
    source = result.payload["source_file"]
    if source not in seen_sources:
        citations.append(generate_citation(result.payload))
        seen_sources.add(source)

# Phase 6c: Include in response
system_prompt = f"""Answer using these sources:
{citation_list}

Context:
{context_text}"""

# Code reference: research.md Section 7 (Citation Generation)
```

### Phase 7: Monitoring & SLO (1-2 days)
**Owner: SRE + Backend Engineer**

```python
# Phase 7a: Instrument latency
from prometheus_client import Histogram

retrieval_latency = Histogram(
    'rag_retrieval_seconds',
    'Vector search latency',
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5]
)

generation_latency = Histogram(
    'rag_generation_seconds',
    'LLM generation latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Phase 7b: Create dashboards
- [ ] p50/p95/p99 latency by component
- [ ] Cache hit rates (query, semantic, document)
- [ ] Vector search recall (quality metric)
- [ ] Error rate by type (timeout, rate limit, hallucination)
- [ ] SLO dashboard (p95 < 2s target)

# Phase 7c: Set alerts
- [ ] Alert if p95 > 2000ms for 5+ min
- [ ] Alert if cache hit rate < 30%
- [ ] Alert if LLM generation timeout (>60s)

# Code reference: research.md Section 8 (Latency Optimization)
```

### Phase 8: Testing & Validation (2-3 days)
**Owner: QA + Backend Engineer**

```bash
# Phase 8a: Unit tests
- [ ] Chunking: verify 512 token chunks with 50 overlap
- [ ] Citation generation: IEEE format validation
- [ ] Cache: hit rate, TTL expiration
- [ ] Error handling: timeout, rate limit, no results

# Phase 8b: Integration tests
- [ ] End-to-end: query → retrieval → generation → citation
- [ ] Text selection: bypass vector search
- [ ] Conversation history: append & retrieve
- [ ] Multiple users: concurrent requests without connection issues

# Phase 8c: Load testing
- [ ] 10 concurrent users, 100 queries
- [ ] Measure p95 latency (target: < 2000ms cold, < 500ms cached)
- [ ] Verify cache hit rate > 35%
- [ ] Check database connection pooling (PgBouncer)

# Phase 8d: Accuracy testing
- [ ] 20 ground-truth questions (known answers in textbook)
- [ ] Verify LLM responses match textbook content (no hallucination)
- [ ] Verify citations point to correct chapters/sections
- [ ] Test edge case: out-of-scope questions (should decline)
```

---

## Dependency Graph

```
Phase 0 (Setup)
    ↓
Phase 1 (Content Ingestion) ← Phase 2 (Backend API)
    ↓                               ↓
    └─────────────────────→ Phase 3 (Caching)
                                    ↓
    Phase 4 (Database Schema) ←────┤
                                    ↓
                            Phase 5 (ChatKit)
                                    ↓
                            Phase 6 (Citations)
                                    ↓
                            Phase 7 (Monitoring)
                                    ↓
                            Phase 8 (Testing)
```

**Critical Path:** Phases 0 → 1 → 2 → 7 (monitoring must be instrumented early)

---

## Key Configuration Constants

```python
# Chunking
CHUNK_SIZE = 512  # tokens
CHUNK_OVERLAP = 50  # tokens
HEADER_SPLITTER = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "chapter"), ("##", "section"), ("###", "subsection")]
)

# Vector Search
TOP_K = 5  # retrieve top 5 sections
SIMILARITY_THRESHOLD = 0.7  # minimum relevance score
HYBRID_SEARCH = True  # dense + sparse

# Caching
QUERY_CACHE_TTL = 3600  # 1 hour
SEMANTIC_CACHE_TTL = 604800  # 7 days
SEMANTIC_CACHE_THRESHOLD = 0.95  # similarity for cache hit

# Session Management
CONVERSATION_LIMIT = 10  # messages per session
SESSION_TTL = 86400  # 24 hours
MESSAGE_RETENTION = 90  # days (for analytics)

# LLM Generation
LLM_MODEL = "gpt-4-turbo-preview"
LLM_MAX_TOKENS = 1024
LLM_TEMPERATURE = 0.7
LLM_TIMEOUT = 60  # seconds

# SLO Targets
P95_LATENCY_TARGET = 2000  # milliseconds
CACHE_HIT_RATE_TARGET = 0.35  # 35%
VECTOR_SEARCH_P95 = 100  # milliseconds
LLM_GENERATION_P95 = 1500  # milliseconds
```

---

## Failure Mode Checklist

- [ ] **Hallucination:** LLM generates answer not in textbook
  - Mitigation: System prompt grounding + retrieval context limiting
  - Test: Out-of-scope questions should decline politely

- [ ] **Cache Miss + Slow LLM:** p95 latency spike
  - Mitigation: Monitor cache hit rate; increase semantic cache threshold
  - Test: Load testing with varied query patterns

- [ ] **Vector Search Returns Nothing:** Low relevance results
  - Mitigation: Fallback to keyword search; suggest query rephrasing
  - Test: Edge case queries from academic textbooks

- [ ] **Citation Link Broken:** Textbook section was deleted
  - Mitigation: Version metadata; test links in CI/CD
  - Test: Update textbook; verify old conversations still cite correctly

- [ ] **Connection Pooling Saturated:** 10k concurrent users limit
  - Mitigation: Monitor connection pool; scale Neon compute
  - Test: Load test with 100+ concurrent connections

- [ ] **Embedding Cost Explosion:** Batch API quota exceeded
  - Mitigation: Use Batch API for bulk; throttle real-time embeddings
  - Test: Capacity planning for 12 chapters + updates

---

## Testing Checklist (Pre-Launch)

### Functional Tests
- [ ] Q: "What is bipedal locomotion?" → Answer cites Chapter 9, Section 3
- [ ] Q: "What is the weather?" → "Cannot answer from textbook" (no hallucination)
- [ ] Q: Select text from Chapter 5 → Answer uses selection as context
- [ ] Q: Multi-turn conversation → History preserved, context maintained
- [ ] Citation click → Docusaurus navigation to section (if available)

### Performance Tests
- [ ] p50 latency (cached): < 500ms
- [ ] p95 latency (cold): < 2000ms
- [ ] p99 latency (cold): < 3000ms
- [ ] Cache hit rate: > 35%
- [ ] Vector search latency: < 100ms

### Reliability Tests
- [ ] Restart Qdrant → System recovers gracefully
- [ ] Restart Neon → Conversations persist, no data loss
- [ ] Rate limit hit (OpenAI) → Graceful error, no crash
- [ ] LLM timeout (>60s) → Return error, don't hang
- [ ] Concurrent 10 users → No connection pool exhaustion

### Accuracy Tests
- [ ] 20 ground-truth Q&A pairs → All answers correct
- [ ] Citation accuracy → All citations point to correct sections
- [ ] No hallucination → Out-of-scope questions decline

---

## Deployment Checklist

- [ ] Environment variables configured (OPENAI_API_KEY, DATABASE_URL, QDRANT_URL, REDIS_URL)
- [ ] Qdrant collections created (docs, query_cache)
- [ ] Neon database schema migrated (users, conversations, messages)
- [ ] Redis initialized (query + semantic cache)
- [ ] Monitoring dashboards created (Prometheus + Grafana)
- [ ] Alerting rules configured (p95 latency, cache hit rate, errors)
- [ ] Load balancer configured (health checks, scaling policies)
- [ ] ChatKit web component embedded in Docusaurus
- [ ] Tests pass (unit, integration, load, accuracy)
- [ ] Documentation updated (API docs, runbooks, troubleshooting)
- [ ] Rollout plan prepared (canary, progressive rollout, rollback)

---

## Quick Troubleshooting

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| p95 latency > 3s | Check LLM latency via logs | Increase LLM timeout; check OpenAI quota |
| Cache hit rate < 20% | Query patterns too varied | Increase semantic cache threshold |
| "Vector search returns no results" | Chunk quality too low | Re-chunk with better overlap; test query |
| Hallucination on out-of-scope | System prompt too loose | Strengthen prompt grounding |
| Connection pool exhausted | Too many concurrent users | Scale Neon compute; check connection leaks |
| Citation links broken | Textbook section renamed/deleted | Regenerate embeddings for updated files |

---

## Reference Implementation Patterns

All code patterns in this document are derived from:
- `/specs/005-rag-chatbot/research.md` (8 sections with detailed code)
- `/specs/005-rag-chatbot/research-implementation-mapping.md` (spec ↔ architecture mapping)

For full production-ready patterns:
1. **FastAPI + Streaming:** See research.md Section 1
2. **Qdrant Hybrid Search:** See research.md Section 2
3. **Chunking:** See research.md Section 3
4. **Neon Sessions:** See research.md Section 4
5. **ChatKit Integration:** See research.md Section 5
6. **Content Pipeline:** See research.md Section 6
7. **Citation Generation:** See research.md Section 7
8. **Latency Optimization:** See research.md Section 8

---

**Last Updated:** January 27, 2026
**Ready for:** Engineering kickoff, sprint planning, task assignment
