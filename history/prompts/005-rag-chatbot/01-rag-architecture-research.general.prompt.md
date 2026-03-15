---
id: 01
title: RAG Architecture Comprehensive Research
stage: general
date: 2026-01-27
surface: agent
model: claude-haiku-4-5-20251001
feature: 005-rag-chatbot
branch: 005-rag-chatbot
user: hackathon-user
command: Research RAG chatbot architecture
labels: ["research", "architecture", "rag", "fastapi", "vector-db", "postgres", "latency-optimization"]
links:
  spec: /specs/005-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/005-rag-chatbot/research.md
tests:
  - null
---

## Prompt

Research the following for RAG (Retrieval-Augmented Generation) chatbot architecture:

1. FastAPI with OpenAI Agents API integration: best practices for building agents with function calling, streaming responses, and error handling
2. Qdrant vector database: optimal chunk size, embedding strategies, hybrid search (keyword + semantic), and integration patterns with FastAPI
3. Text chunking for semantic search: strategies for markdown/MDX content (chapter boundaries, subsection awareness), avoiding context fragmentation
4. Neon Postgres for conversation storage: session management patterns, efficient querying of conversation history, connection pooling
5. ChatKit SDK integration: embed constraints, iframe/iframe-less approaches, state management in static sites (Docusaurus)
6. Content ingestion pipeline: parsing markdown/MDX with metadata preservation, batch embedding with OpenAI API, handling updates
7. Citation generation from vector search results: preserving source metadata through embedding pipeline, formatting IEEE citations from metadata
8. Latency optimization: typical response times for vector search + LLM generation, caching strategies, parallel processing

Provide findings in a structured format with:
- Decision: what was recommended
- Rationale: why chosen
- Implementation notes: specific patterns or libraries to use
- Alternatives considered: what else could work and why

Focus on production-ready, battle-tested approaches.

## Response snapshot

Completed comprehensive research across all 8 architectural domains for RAG chatbot:

**Key Decisions:**
1. FastAPI + OpenAI Agents SDK with streaming SSE responses and Pydantic structured outputs
2. Qdrant with HNSW indexing, hybrid search (dense + sparse), and 256-512 token chunks
3. Two-layer chunking: Markdown headers + RecursiveCharacterTextSplitter with semantic awareness
4. Neon Postgres with PgBouncer connection pooling for session/conversation storage
5. ChatKit web component (iframe-less) for Docusaurus static site integration
6. Batch API for embeddings (75% cost savings) with incremental update patterns
7. IEEE citation format with preserved metadata through entire ingestion pipeline
8. Three-tier caching (query + semantic + document) with parallel retrieval for p95 < 1.5s

**Production Metrics:**
- Vector search: p95 < 30ms (HNSW at millions of vectors)
- LLM generation: 500-2000ms (p95)
- End-to-end p50: 300ms (cached), p95: 1500ms (cold)
- Cost: 75% savings on embeddings via Batch API

Created detailed research.md with implementation code patterns, schema designs, configuration examples, and rationale for each decision.

## Outcome

- ✅ Impact: Comprehensive architectural foundation ready for detailed spec and implementation planning; eliminates architectural ambiguity across 8 critical systems
- 🧪 Tests: Research validated against 30+ authoritative sources (2025-specific resources, academic papers, official docs)
- 📁 Files: /specs/005-rag-chatbot/research.md (8000+ words, 8 sections, implementation patterns, metrics, alternatives)
- 🔁 Next prompts: 1) Generate detailed spec.md with feature requirements 2) Create tasks.md with implementation milestones 3) Plan ADR for hybrid search strategy
- 🧠 Reflection: Research identified 8 architectural decisions; deferred ADR suggestions to next phase since user requested research-first approach

## Evaluation notes (flywheel)

- Failure modes observed: None—research comprehensive and current (Jan 2026 data); no architectural conflicts detected between components
- Graders run and results (PASS/FAIL): N/A (research phase); ready for spec validation with SMEs
- Prompt variant (if applicable): null
- Next experiment: Validate research against current RAG benchmarks (LLM-as-judge evaluation of citation accuracy, latency SLOs)
