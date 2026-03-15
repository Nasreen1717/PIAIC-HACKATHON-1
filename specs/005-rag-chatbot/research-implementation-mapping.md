# RAG Chatbot: Research-to-Implementation Mapping

**Document Date:** January 27, 2026
**Purpose:** Map comprehensive architecture research to feature specification requirements
**Status:** Ready for spec refinement and task generation

---

## Executive Summary

The research document (`research.md`) provides production-ready architectural guidance for all 8 critical systems required by the RAG Chatbot specification. This mapping document:

1. **Cross-references** each research section to specific requirements (FR-001 through FR-013)
2. **Identifies** implementation patterns that directly satisfy acceptance criteria
3. **Flags** decisions that require specification clarification or ADR documentation
4. **Highlights** latency/performance assumptions underlying the 3-second SLO

---

## Requirement-to-Architecture Mapping

### Core Query & Response Loop

| Spec Requirement | Research Section | Key Decision | Acceptance Impact |
|---|---|---|---|
| FR-001: Accept natural language questions | 1. FastAPI | Use FastAPI streaming endpoint with SSE for real-time token delivery | Enables 3s SLO with parallel retrieval |
| FR-002: Search vector database for 5 relevant sections | 2. Qdrant + 3. Chunking | HNSW indexing with 256-512 token chunks; p95 latency < 30ms | 30ms search time budgeted into 3s SLO |
| FR-003: Use OpenAI Agents API for responses | 1. FastAPI | Structured outputs with Pydantic; tools schema validation | Built-in error handling for hallucination prevention |
| FR-004: Enforce grounding (prevent hallucinations) | 1. FastAPI | System prompt injection + retrieval context limiting | Satisfies "cite only textbook material" constraint |
| FR-005: Return response within 3 seconds | 8. Latency Optimization | Parallel retrieval + streaming generation; 3-tier cache | p95 target: 300ms (cached) to 1500ms (cold) |
| FR-006: Accept selected text as context | 1. FastAPI | Bypass vector search when `selected_text` param provided | Reduces latency for text selection queries |

### Citation & Academic Integrity

| Spec Requirement | Research Section | Key Decision | Acceptance Impact |
|---|---|---|---|
| FR-007: Generate IEEE citations | 7. Citation Generation | Preserve metadata (file, heading, subsection) through entire pipeline; format at query time | Citations include chapter number + section title |
| (Edge case) | 3. Chunking | Store `source_id`, `file_path`, `heading`, `subsection` in Qdrant payload | Enables precise citation generation |

### Persistence & Sessions

| Spec Requirement | Research Section | Key Decision | Acceptance Impact |
|---|---|---|---|
| FR-008: Store conversation history in Postgres | 4. Neon Postgres | User → Conversation → Message schema with indexed lookups; PgBouncer pooling | Supports concurrent users without connection exhaustion |
| FR-009: Retrieve previous conversation history | 4. Neon Postgres | Session table with user_id + conversation_id; 24h TTL | Persists across browser restarts |
| FR-013: Multi-turn conversations maintain context | 4. Neon Postgres | Conversation history prepended to system prompt; semantic relevance filtering | Avoids context window explosion |

### Content Ingestion & Embeddings

| Spec Requirement | Research Section | Key Decision | Acceptance Impact |
|---|---|---|---|
| FR-010: Ingest 12 chapters from Physical AI textbook | 6. Content Pipeline | Batch API for embeddings; parse .md/.mdx with header-aware chunking | 75% cost savings on embeddings ($0.50/M tokens) |
| FR-011: Parse markdown/MDX identifying chapters | 3. Chunking + 6. Pipeline | MarkdownHeaderTextSplitter (Langchain) preserves hierarchy | Metadata extraction ensures proper citations |
| (Edge case) | 3. Chunking | MDX preprocessing: strip JSX, preserve frontmatter as metadata | Handles interactive components gracefully |

### UI/UX & Constraints

| Spec Requirement | Research Section | Key Decision | Acceptance Impact |
|---|---|---|---|
| FR-012: Handle out-of-scope questions | 1. FastAPI | Confidence thresholding in system prompt; "cannot answer" signal | Prevents hallucination on off-topic queries |
| (Docusaurus embedding) | 5. ChatKit SDK | ChatKit web component (iframe-less) for static Docusaurus | Zero build overhead; domain-based security |

---

## Architecture Decision Points Requiring Specification Clarity

### 1. **Vector Search Strategy: Dense-Only vs. Hybrid**

**Research Recommendation:** Hybrid search (dense + sparse BM25)
**Rationale:** Balances semantic understanding with exact term matching; improves recall on technical terminology

**Specification Impact:**
- Does the spec allow for both semantic and keyword matching?
- Should students be able to search for specific equations/code snippets (requires sparse)?
- Are we optimizing for conceptual queries or precise term lookup?

**Suggested ADR Title:** "Hybrid Search Strategy for Technical Textbook Content"

---

### 2. **Citation Format & Navigation**

**Research Recommendation:** IEEE format with metadata preservation; optionally link to textbook section
**Specification States:** "IEEE-formatted citation with chapter number and section title"
**Gap:** No specification on what happens when citation is clicked

**Missing Acceptance Criteria:**
- If citation is clickable, should it navigate to the section in Docusaurus?
- Should citations include URL links (e.g., `/docs/module-2/chapter-9/#bipedal-gait`)?
- How to handle citations for equations/code blocks within sections?

**Suggested ADR Title:** "Citation Linking Strategy for Docusaurus Navigation"

---

### 3. **Latency SLO & Caching Assumptions**

**Research Findings:**
- p95 latency: 1500ms (cold retrieval + generation)
- p50 latency: 300ms (cached query)
- Assumes 3-tier caching strategy

**Specification States:** "Return responses within 3 seconds"

**Risk Assessment:**
- **Achievable IF** caching hit rate is >40% OR average query complexity is low
- **At Risk IF** corpus is highly specific and cache misses are frequent
- **Recommendation:** Add SLO measurement to implementation; track cache hit rates

**Suggested Metrics to Add to Spec:**
- p95 latency for cache misses (cold): < 2000ms
- p50 latency for cache hits: < 500ms
- Cache hit rate target: 40%

---

### 4. **Chunk Size & Retrieval Count**

**Research Recommendation:** 256-512 token chunks; retrieve top 5
**Specification States:** FR-002 "up to 5 most relevant textbook sections"

**Alignment:** ✅ Direct match

**Implementation Detail:**
- 256-512 tokens ≈ 1-2 KB per chunk for English prose
- 50-token overlap between chunks for context continuity
- No specification on how "relevance" is determined (similarity threshold?)

**Suggested Clarification:**
- Should retrieve stop at N=5 or continue if confidence is low?
- What's the minimum similarity threshold for a result to be considered relevant?

---

### 5. **Text Selection Flow (FR-006)**

**Research Recommendation:** When `selected_text` is provided, skip vector search entirely
**Specification States:** "bypass vector search when selection provided"

**Implementation Assumption:**
- Selected text is passed as separate parameter to backend
- System treats selected text as sufficient context (no expansion search)
- Cites the selection source, not expanded results

**Missing from Spec:**
- How is selected text passed from ChatKit to backend? (Copy-paste? API call with text range?)
- Should the chatbot be aware of what's selected in real-time, or only when user submits query?
- What happens if selected text is too short to provide sufficient context?

---

### 6. **Conversation Context Management**

**Research Recommendation:** Store last 10 messages in session; prepend to system prompt
**Specification States:** FR-013 "multi-turn conversations maintain context"

**Risk:** Context window explosion
- GPT-4 Turbo has 128k token context; but RAG pipeline also adds retrieval results
- At typical message length (200 tokens), 10 messages = 2K tokens (safe)
- If messages grow larger, may need to summarize older exchanges

**Suggested Addition to Spec:**
- Maximum conversation depth before summarization: 10 messages per session
- Conversation session TTL: 24 hours (research recommendation)
- Option to start new conversation vs. continue existing

---

### 7. **Handling Multimedia Content**

**Specification Edge Case:** "What happens when a student asks about figures, diagrams, or code snippets?"
**Research Gap:** No guidance on vision/multimodal support

**Current Research Assumption:**
- Code snippets are extracted as text and embedded
- Figures/diagrams are referenced by caption only
- System acknowledges limitation and directs student to review visual directly

**This is an implicit constraint:** Chatbot is text-only, not multimodal

**Suggested Clarification:**
- Should code be embedded separately (language-specific)?
- Should figures have searchable captions or alt-text indexed?

---

## Performance & SLO Deep Dive

### Latency Budget for 3-Second SLO

| Component | p95 Latency | % of Budget | Research Basis |
|---|---|---|---|
| Network overhead (request + TLS) | 50ms | 1.7% | Typical AWS/cloud |
| Vector embedding generation | 20ms | 0.7% | OpenAI text-embedding-3-small |
| Vector search (Qdrant HNSW) | 30ms | 1% | Qdrant @ millions of vectors |
| LLM generation (GPT-4 Turbo) | 1000ms | 33% | First token latency + completion |
| Streaming overhead | 100ms | 3.3% | Network + serialization |
| Buffer (tail latency) | 700ms | 23% | Unaccounted variance |
| **TOTAL** | **1900ms** | **63%** | **Headroom to 3s** |

**Cache Hit Case (Query Cache):**
- Skip embedding + search: save 50ms
- Return from Redis: 10ms
- Total: 300ms ✅

**Conservative Estimate:** p95 achievable if cache hit rate > 35%

**Monitoring Recommendations:**
- Track all 6 latency components separately
- Alert if p95 > 2000ms (indicates cache degradation or LLM slowdown)
- Weekly SLO review against edge cases (large documents, complex queries)

---

## Cost Analysis

### Embeddings (per 12-chapter ingestion)

| Method | Cost | Speed | Quality |
|---|---|---|---|
| Batch API (research rec.) | $0.02 (100K @ $0.50/M) | 6 hours | Highest (OpenAI) |
| On-demand API | $0.10 (100K @ $2/M) | Real-time | Highest (OpenAI) |
| Local (BAAI/bge-small) | $0 | 1 hour | 5-10% lower recall |

**Recommendation:** Batch API for initial ingestion; on-demand only for updates

### API Costs (per 1,000 queries, 3-month run)

Assuming 100 students × 30 queries = 3,000 queries/month

| Component | Calls | Cost/M | Monthly |
|---|---|---|---|
| Embeddings (on-demand) | 3K | $2 | $0.01 |
| GPT-4 Turbo (completion) | 3K × 1500 tokens avg | $0.03/K | $0.14 |
| Qdrant (cloud, 10GB) | Storage | $0.30/GB | $3.00 |
| Neon Postgres (compute) | Serverless | $0.14/hour | $2.80 |
| **TOTAL** | | | **$5.95/month** |

**Note:** Batch caching (query + semantic) can reduce API costs 30-40%

---

## Implementation Risk Matrix

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Cache miss rate > 60% | Medium | High (SLO miss) | Load testing; semantic cache tuning | Backend engineer |
| Vector search no results | Low | Medium (user frustration) | Fallback to keyword search; better chunking | ML engineer |
| Citation link broken (updated chapters) | Medium | Medium (academic integrity) | Test citation links in CI/CD; versioning | Content manager |
| Hallucination on out-of-scope questions | Medium | High (academic integrity) | System prompt + confidence thresholding + human review | QA + product |
| Context window explosion (long conversations) | Low | Low (edge case) | Conversation summarization; 10-msg limit | Backend engineer |
| Neon connection pooling saturated | Very Low | High (service down) | Connection pool monitoring; auto-scaling | DevOps |

---

## Architectural Decision Records (ADRs) to Create

Based on research findings and specification gaps:

### ADR-001: Hybrid Search vs. Dense-Only Vector Search
**Decision:** Implement hybrid search (dense semantic + sparse BM25)
**Justification:** Improves recall on technical terminology; minimal latency overhead

### ADR-002: Citation Linking Strategy
**Decision:** Citations include clickable links to Docusaurus sections (if available)
**Justification:** Enhances academic integrity and student navigation; leverages static site structure

### ADR-003: Session & Conversation Persistence Architecture
**Decision:** Neon Postgres for conversations; localStorage for ChatKit session state
**Justification:** Balances scalability (serverless) with synchronous session data

### ADR-004: Caching Layering Strategy
**Decision:** Three-tier: query-level (Redis) + semantic (Qdrant) + document (in-process)
**Justification:** Balances cache hit rate (40%+) with implementation complexity

### ADR-005: Content Ingestion & Versioning
**Decision:** Batch API for embeddings; incremental updates via re-embedding changed chunks
**Justification:** 75% cost savings; handles textbook edits without full re-ingest

---

## Specification Refinements Recommended

### 1. Add Latency Metrics
```markdown
### Performance Requirements (NFR)

- **NFR-001**: System SHALL return 95% of queries in < 2000ms (cold) and < 500ms (cached)
- **NFR-002**: System SHALL maintain >35% cache hit rate on typical usage patterns
- **NFR-003**: Vector search latency SHALL be < 100ms for 99th percentile
```

### 2. Add Citation Linking
```markdown
### Functional Requirements (Additional)

- **FR-014**: When a student clicks on a citation, the system SHALL navigate to the cited section in the Docusaurus textbook (if section URL is resolvable)
- **FR-015**: Citations SHALL include ISO date stamps indicating when the textbook was last updated
```

### 3. Clarify Text Selection Flow
```markdown
### Functional Requirements (Clarification)

- **FR-006a**: When a student selects text in the textbook and submits a query with that selection active, the chatbot SHALL use only the selected text as context (no vector search)
- **FR-006b**: The selected text SHALL be passed to the backend as a query parameter or request body field
- **FR-006c**: Response time for text selection queries SHALL be < 1500ms (skip vector search overhead)
```

### 4. Add Conversation Limits
```markdown
### Functional Requirements (Additional)

- **FR-014**: Conversation history SHALL display the 10 most recent user-assistant exchanges
- **FR-015**: Sessions SHALL auto-expire after 24 hours of inactivity
- **FR-016**: Students SHALL be able to manually start a new conversation or resume the previous one
```

### 5. Add Monitoring Requirements
```markdown
### Operational Requirements (NFR)

- **OPS-001**: System SHALL track and expose (via Prometheus) the following metrics:
  - Vector search latency (p50, p95, p99)
  - LLM generation latency (p50, p95, p99)
  - Cache hit rate by cache layer
  - Total end-to-end latency
- **OPS-002**: System SHALL alert if p95 latency exceeds 2000ms for 5+ minutes
```

---

## Next Steps

### Phase 1: Specification Refinement (Owner: Product)
- [ ] Clarify citation linking behavior
- [ ] Define text selection API contract
- [ ] Set concrete cache hit rate targets
- [ ] Review edge cases (multimedia, complex queries)
- [ ] Add SLO monitoring requirements

### Phase 2: Architecture & ADR Reviews (Owner: Tech Lead)
- [ ] Review and approve 5 proposed ADRs
- [ ] Create ADR-002 (Citation Linking) with stakeholder review
- [ ] Create ADR-004 (Caching) with performance engineer sign-off
- [ ] Document fallback strategies (vector search no results, hallucination detection)

### Phase 3: Implementation Planning (Owner: Tech Lead + Backend Lead)
- [ ] Generate detailed tasks.md from research + refined spec
- [ ] Identify dependencies (ChatKit SDK, OpenAI API key management)
- [ ] Plan testing strategy (load testing, citation accuracy, edge cases)
- [ ] Allocate engineering resources

### Phase 4: Development Setup (Owner: DevOps + Backend)
- [ ] Provision Neon Postgres cluster
- [ ] Configure Qdrant Cloud instance (create collections with HNSW + quantization)
- [ ] Set up OpenAI Batch API for embeddings
- [ ] Configure monitoring (Prometheus, Grafana, SLO dashboards)

---

## Research Validation Checklist

- [x] FastAPI patterns validated against OpenAI docs (2025)
- [x] Qdrant hybrid search patterns tested in examples (academic + industry)
- [x] Chunking strategies benchmarked (NVIDIA 2024, Pinecone, LangChain)
- [x] Neon Postgres features current as of Jan 2025
- [x] ChatKit SDK constraints documented (no official iframe)
- [x] Batch API pricing verified (OpenAI Jan 2026)
- [x] Latency baselines from peer-reviewed sources (CSAIL, USENIX, arXiv)
- [x] Citation generation patterns from IEEE standards

**Confidence Level:** HIGH (30+ authoritative sources, 2025-current documentation)

---

## Appendix: Research Sources

See `/specs/005-rag-chatbot/research.md` for complete reference list (30+ sources).

Key categories:
- Official APIs: OpenAI, Qdrant, Neon, LangChain
- Academic: arXiv (latency optimization, RAG surveys)
- Production patterns: GitHub (langgraph, llmware, azure-search-openai-demo)
- Benchmarks: NVIDIA, Pinecone, Weaviate, academic papers

---

**Document prepared for:** Feature review & ADR approval
**Recommended reviewers:** Product Manager, Tech Lead, Backend Engineer, DevOps
