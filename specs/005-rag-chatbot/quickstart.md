# Quickstart: RAG Chatbot Backend Development

**Date**: 2026-01-27 | **Audience**: Backend engineers, DevOps, QA | **Status**: Development-ready

This guide provides hands-on instructions for local development, testing, and deployment of the RAG chatbot backend.

---

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for local Qdrant + Postgres)
- Git
- OpenAI API key (for GPT-4 and embeddings)
- Qdrant Cloud account (or local instance)
- Neon Postgres account (or local Postgres 14+)

---

## Project Setup

### 1. Clone and Install Dependencies

```bash
# Clone repository
git clone https://github.com/anthropics/Hackathon-1.git
cd Hackathon-1

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt  # Dev dependencies (pytest, black, etc.)
```

### 2. Configure Environment Variables

Create `backend/.env`:

```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Qdrant
QDRANT_URL=http://localhost:6333  # Local dev
QDRANT_API_KEY=  # Leave empty for local; set for cloud

# Neon Postgres
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_dev

# FastAPI
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Start Local Services

```bash
# Terminal 1: Start Qdrant (vector DB)
docker run -p 6333:6333 -p 6334:6334 \
  -v ./qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Terminal 2: Start Postgres
docker run -p 5432:5432 \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=chatbot_dev \
  -v ./postgres_data:/var/lib/postgresql/data \
  postgres:15

# Alternative: Use docker-compose
docker-compose -f backend/docker-compose.yml up -d
```

### 4. Initialize Database

```bash
cd backend

# Run migrations
alembic upgrade head

# Seed test data (optional)
python scripts/seed_test_data.py
```

### 5. Start FastAPI Development Server

```bash
# Terminal 3: Start API
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

---

## Testing the API Locally

### 1. Health Check

```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "qdrant": "connected",
#   "postgres": "connected",
#   "openai": "responsive",
#   "cache": {"hit_rate": 0.0, "items": 0}
# }
```

### 2. Chat Endpoint (Streaming)

```bash
# Start streaming chat
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is bipedal locomotion?"
  }' \
  | sed 's/^data: //' \
  | grep -v '^$' \
  | jq .

# Expected events:
# {"type": "thinking", "delta": "..."}
# {"type": "retrieval", "chunks": [...]}
# {"type": "response_start", ...}
# {"type": "text_delta", "delta": "Bipedal locomotion..."}
# {"type": "citation", "ieee": "[1] Chapter 8, Section 2"}
# {"type": "response_end", ...}
```

### 3. Conversation History

```bash
# List user's conversations
curl http://localhost:8000/conversations \
  -H "Authorization: Bearer user123" \
  -H "Content-Type: application/json"

# Retrieve specific conversation
curl http://localhost:8000/conversations/{conversation_id} \
  -H "Authorization: Bearer user123"
```

### 4. Test with Selected Text

```bash
# Chat with highlighted text as context
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain this passage",
    "selected_text": "Bipedal locomotion refers to movement on two legs...",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

## Content Ingestion Workflow

### 1. Prepare Textbook Content

```bash
# Copy chapter .md/.mdx files to inputs/
mkdir -p backend/inputs/chapters
cp Front-End-Book/docs/module-*/chapter-*.mdx backend/inputs/chapters/
```

### 2. Run Ingestion Pipeline

```bash
cd backend

# Option 1: Ingest single chapter
python scripts/ingest_content.py --chapters 1 --chunk-size 512

# Option 2: Ingest all chapters
python scripts/ingest_content.py --chapters all --force-refresh

# Output: Batch job ID from OpenAI, stored in embedding_batches table
# Status: submitted → processing → completed
```

### 3. Monitor Batch Job

```bash
# Check status
python scripts/check_batch_status.py --batch-id batch_6716b6d6b00b0f01e5d8c8e6d4c2a1f0

# Expected output:
# Status: completed
# Chunks embedded: 1247
# Cost: $25.89
# Embeddings uploaded to Qdrant
```

### 4. Test Search After Ingestion

```bash
# Query should now return relevant textbook chunks
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is bipedal locomotion?"}'

# Should return grounded answer with citations
```

---

## Testing & Quality Assurance

### 1. Run Unit Tests

```bash
cd backend

# Run all tests
pytest tests/unit -v

# Run specific test file
pytest tests/unit/test_chat_service.py -v

# Run with coverage
pytest tests/unit --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### 2. Run Integration Tests

```bash
# Requires local Qdrant + Postgres running
pytest tests/integration -v

# Test end-to-end flow
pytest tests/integration/test_end_to_end.py::test_chat_with_grounded_response -v
```

### 3. Test Grounding (No Hallucination)

```bash
# Test that out-of-scope questions are rejected
pytest tests/integration/test_grounding.py -v

# Example test:
# - Query: "What is the weather?" (not in textbook)
# - Expected: Graceful rejection message
# - NOT: Hallucinated answer from external knowledge
```

### 4. Latency Benchmarking

```bash
# Run load test
pytest tests/performance/test_latency.py -v

# Expected results:
# - Cold start (no cache): p95 ~1500ms
# - With cache: p50 ~300ms
# - Cache hit rate: >35%
```

### 5. Linting and Code Quality

```bash
# Format code
black backend/src backend/tests

# Lint
flake8 backend/src --max-line-length=120

# Type checking
mypy backend/src --ignore-missing-imports

# Run pre-commit hooks
pre-commit run --all-files
```

---

## Development Workflow

### Adding a New Feature

1. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write spec and plan** (if significant):
   ```bash
   # Use /sp.specify, /sp.plan commands
   ```

3. **Implement feature**:
   ```bash
   # Update relevant service files in src/
   # Follow existing patterns (Pydantic models, async/await, error handling)
   ```

4. **Write tests**:
   ```bash
   # Add unit test to tests/unit/
   # Add integration test to tests/integration/ if needed
   pytest tests/ -v
   ```

5. **Code review**:
   ```bash
   git push origin feature/my-feature
   # Create PR, get review
   ```

6. **Merge**:
   ```bash
   git merge feature/my-feature
   ```

### Debugging

**Enable debug logging**:
```bash
# In .env
LOG_LEVEL=DEBUG

# In code:
import logging
logger = logging.getLogger(__name__)
logger.debug("Message", extra={"context": "value"})
```

**Inspect Qdrant vectors**:
```python
# Python REPL
from qdrant_client import QdrantClient
client = QdrantClient("http://localhost:6333")
points = client.scroll("textbook_chunks", limit=5)
for point in points[0]:
    print(f"ID: {point.id}, Chapter: {point.payload['chapter_number']}")
```

**Inspect Postgres**:
```bash
# Connect to local database
psql postgresql://user:password@localhost:5432/chatbot_dev

# Useful queries:
SELECT * FROM conversations LIMIT 5;
SELECT COUNT(*) FROM messages;
SELECT * FROM citations WHERE confidence_score < 0.7;
```

---

## Deployment

### 1. Cloud Run (Google Cloud)

```bash
# Build Docker image
docker build -t gcr.io/my-project/rag-chatbot:latest backend/

# Push to registry
docker push gcr.io/my-project/rag-chatbot:latest

# Deploy to Cloud Run
gcloud run deploy rag-chatbot \
  --image gcr.io/my-project/rag-chatbot:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars "OPENAI_API_KEY=sk-proj-...,DATABASE_URL=postgresql://..."
```

### 2. AWS Lambda (with API Gateway)

```bash
# Install serverless framework
npm install -g serverless

# Deploy
serverless deploy function -f chat -r us-east-1

# Test
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/chat
```

### 3. Docker Compose (Production)

```bash
# Create production docker-compose.yml
docker-compose -f backend/docker-compose.prod.yml up -d

# Logs
docker-compose logs -f fastapi
```

### 4. Monitoring

**Set up Prometheus**:
```bash
# Add to docker-compose
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"
```

**Set up Grafana dashboards**:
- Import dashboard: Grafana → Dashboards → Import → `grafana-dashboard.json`
- Configure SLO alerts: Response time p95 <1500ms

---

## Common Issues & Troubleshooting

### Issue: "Vector database not connected"

**Cause**: Qdrant service not running or wrong URL
**Solution**:
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Check URL in .env (should be http://localhost:6333 for local)
curl http://localhost:6333/health

# Restart if needed
docker restart <qdrant_container_id>
```

### Issue: "Rate limited by OpenAI API"

**Cause**: Too many concurrent requests or quota exceeded
**Solution**:
```bash
# Increase rate limit in config
MAX_REQUESTS_PER_MINUTE = 3000  # Adjust based on quota

# Implement exponential backoff (already in code)
# Or use batch API for bulk embeddings
```

### Issue: "Citations not matching textbook content"

**Cause**: Low confidence score in retrieval or citation generation bug
**Solution**:
```bash
# Check retrieved chunks
python -c "
from src.services.retrieval_service import RetrievalService
svc = RetrievalService()
chunks = svc.retrieve('your query')
for c in chunks:
    print(f'Score: {c.score}, Chapter: {c.chapter}, Content: {c.content[:100]}...')
"

# Increase retrieval top-k (default 5):
chunks = svc.retrieve(query, top_k=10)
```

### Issue: "Tests failing with "no embeddings found"

**Cause**: Test data not ingested or using wrong collection
**Solution**:
```bash
# Seed test data
python scripts/seed_test_data.py

# Verify embeddings in Qdrant
curl http://localhost:6333/collections/textbook_chunks/points/count
```

---

## Architecture & Design Patterns

### FastAPI Patterns

**Streaming responses**:
```python
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def stream_chat(query: str):
    async def event_generator():
        async for event in agent.stream(query):
            yield f"data: {json.dumps(event)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Dependency injection**:
```python
async def get_db():
    async with sessionmaker()() as session:
        yield session

@app.post("/chat")
async def chat(query: str, db: AsyncSession = Depends(get_db)):
    # db is injected automatically
    pass
```

### Qdrant Patterns

**Multi-vector search**:
```python
# Hybrid search: semantic + keyword
results = client.search_batch(
    collection_name="textbook_chunks",
    requests=[
        SearchRequest(
            vector=dense_embedding,  # Semantic
            filter=models.Filter(...),
            limit=5
        ),
        SearchRequest(
            vector=sparse_bm25,  # Keyword
            filter=models.Filter(...),
            limit=5
        )
    ]
)
```

### Caching Patterns

```python
# Query cache (L1)
@functools.lru_cache(maxsize=1024)
def get_cached_response(query: str):
    return generate_response(query)

# Semantic cache (L2, via Qdrant)
def check_semantic_cache(embedding: List[float], threshold=0.95):
    similar = client.search(
        collection_name="responses",
        query_vector=embedding,
        limit=1,
        score_threshold=threshold
    )
    if similar:
        return similar[0].payload["response"]
    return None
```

---

## Performance Tuning

### Optimize Vector Search Latency

1. **Increase Qdrant prefetch** in qdrant-config.json:
   ```json
   "hnsw_config": {
     "ef_construct": 300,  # Higher = more accurate but slower
     "ef": 100             # Increase for faster queries
   }
   ```

2. **Enable quantization** (8x storage reduction):
   ```json
   "quantization": {
     "scalar": {
       "type": "int8",
       "quantile": 0.99
     }
   }
   ```

3. **Connection pooling** for Qdrant:
   ```python
   client = QdrantClient(
       url="http://localhost:6333",
       prefer_grpc=True,  # gRPC is faster than REST
       grpc_options={"grpc.max_receive_message_length": 41943040}
   )
   ```

### Optimize LLM Latency

1. **Use `gpt-4-turbo-preview`** instead of full `gpt-4` (20% faster)
2. **Reduce max_tokens** if possible (fewer tokens = faster generation)
3. **Implement response caching** (3-tier: query → semantic → LRU)

### Optimize Database Queries

1. **Use connection pooling** (Neon: PgBouncer):
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       poolclass=NullPool,  # Neon handles pooling
       connect_args={"timeout": 5}
   )
   ```

2. **Add indexes** (already defined in data-model.md):
   ```sql
   CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
   ```

---

## Next Steps

1. **Run `/sp.tasks`** to generate granular task list for implementation
2. **Start Phase 2**: Implement core chat engine (retrieval + agent orchestration)
3. **Set up CI/CD**: GitHub Actions for testing on each commit
4. **Deploy to staging**: Test with real Docusaurus integration
5. **Create ADRs**: Document significant architectural decisions

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Qdrant Docs](https://qdrant.tech)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Neon Postgres Docs](https://neon.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs)

**Contact**: For setup issues or questions, open an issue on the repository or reach out to the team.
