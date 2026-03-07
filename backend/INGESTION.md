# Content Ingestion Pipeline

This document describes the process for ingesting the Physical AI textbook into the RAG Chatbot system.

## Overview

The ingestion pipeline orchestrates four main steps:

1. **Content Parsing**: Extract chapters, sections, and text from markdown/MDX files
2. **Semantic Chunking**: Split content into optimal-sized chunks (300-600 tokens) with metadata
3. **Embedding Generation**: Create vector embeddings for each chunk using OpenAI API
4. **Vector Store Upload**: Index embeddings in Qdrant for semantic search

## Prerequisites

- FastAPI backend running (`python -m uvicorn app.main:app --reload`)
- Qdrant instance accessible (local or cloud)
- PostgreSQL database available
- OpenAI API key with access to:
  - `text-embedding-3-small` model
  - `gpt-4` model

## Configuration

Before running ingestion, configure `.env`:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your credentials:

```
OPENAI_API_KEY=sk-...
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rag_chatbot
```

## Step-by-Step Usage

### 1. Validate Setup

First, verify all services are working:

```bash
cd backend
python -m scripts.validate_setup
```

Expected output:

```
🔍 RAG Chatbot Setup Validation
============================================================

✓ Checking Qdrant Vector Database...
  ✅ Healthy

✓ Checking OpenAI Embeddings API...
  ✅ Healthy

✓ Checking OpenAI GPT-4 API...
  ✅ Healthy

✓ Checking PostgreSQL Database...
  ✅ Healthy

============================================================
VALIDATION SUMMARY
============================================================
qdrant           ✅ Healthy
embeddings       ✅ Healthy
llm              ✅ Healthy
database         ✅ Healthy

✅ All services are healthy and ready!
```

### 2. Run Content Ingestion

Execute the main ingestion script:

```bash
cd backend
python -m scripts.ingest_content
```

This will:

1. **Parse** all chapters from `Front-End-Book/docs/`:
   - Extract module and chapter metadata
   - Identify sections (## headers)
   - Preserve source references

2. **Chunk** content semantically:
   - Split by sections and paragraphs
   - Target 300-600 tokens per chunk
   - Add overlap for context continuity
   - Generate chunk metadata

3. **Embed** chunks:
   - Batch process through OpenAI API
   - Generate 1536-dimensional vectors
   - Handle API rate limits

4. **Upload** to Qdrant:
   - Upsert points with metadata
   - Create collection if missing
   - Verify upload success

Expected output:

```
============================================================
📚 RAG Chatbot Content Ingestion Pipeline
============================================================

📖 Step 1: Parsing textbook chapters...
✅ Parsed 12 chapters from textbook

✂️ Step 2: Chunking content semantically...
✅ Created 245 chunks from textbook
   Average tokens per chunk: 425
   Min/Max tokens: 280/580

🔮 Step 3: Initializing Qdrant collection...
✅ Created Qdrant collection: physical_ai_textbook

⚡ Step 4: Generating embeddings and uploading to Qdrant...
🔄 Embedding batch 1/5
🔄 Embedding batch 2/5
...
✅ Ingestion Complete!
   Chunks processed: 245
   Points uploaded: 245
   Vector dimension: 1536

🔍 Step 5: Verifying Qdrant collection...
   Collection: physical_ai_textbook
   Total vectors: 245
   Vector size: 1536

🚀 RAG Chatbot is ready to serve!
============================================================
```

## Component Details

### Content Parser (`content_parser.py`)

Extracts structured data from markdown files:

```python
from scripts.content_parser import parse_textbook

chapters = parse_textbook()
# Returns:
# [
#   {
#     "file_path": "Front-End-Book/docs/module-1/chapter-1-intro.md",
#     "module_number": 1,
#     "chapter_number": 1,
#     "title": "Introduction to Robotics",
#     "sections": [
#       {
#         "section_id": "1.1",
#         "title": "What is Robotics?",
#         "content": "...",
#         "chapter_number": 1
#       },
#       ...
#     ]
#   },
#   ...
# ]
```

### Chunking Strategy (`chunking_strategy.py`)

Implements semantic chunking:

```python
from scripts.chunking_strategy import chunk_textbook

chunks = chunk_textbook(chapters, target_tokens=300, overlap_tokens=100)
# Returns:
# [
#   {
#     "chunk_id": "1.1_chunk1",
#     "chapter_number": 1,
#     "section_id": "1.1",
#     "section_title": "What is Robotics?",
#     "content": "...",
#     "token_count": 425,
#     "order": 1
#   },
#   ...
# ]
```

Configuration options:

- `target_tokens`: Aim for this many tokens (default: 300)
- `overlap_tokens`: Overlap between chunks (default: 100)

### Embedding Pipeline (`embedding_pipeline.py`)

Generates and uploads embeddings:

```python
import asyncio
from scripts.embedding_pipeline import embed_and_upload
from app.services.vector_store import vector_store_service

stats = asyncio.run(embed_and_upload(
    chunks,
    openai_api_key="sk-...",
    vector_store_service=vector_store_service
))
# Returns:
# {
#   "chunks_processed": 245,
#   "points_uploaded": 245,
#   "vector_dimension": 1536
# }
```

## Validation Steps

### 1. Check Chunk Quality

Verify chunks are properly formed:

```bash
python -c "
from scripts.content_parser import parse_textbook
from scripts.chunking_strategy import chunk_textbook

chapters = parse_textbook()
chunks = chunk_textbook(chapters)

print(f'Total chunks: {len(chunks)}')
print(f'Chunk sizes: min={min(c[\"token_count\"] for c in chunks)}, '
      f'max={max(c[\"token_count\"] for c in chunks)}, '
      f'avg={sum(c[\"token_count\"] for c in chunks) / len(chunks):.0f}')

# Check for duplicates
ids = [c['chunk_id'] for c in chunks]
print(f'Unique chunks: {len(set(ids))}/{len(ids)}')
"
```

### 2. Verify Vector Store

Check embeddings in Qdrant:

```bash
python -c "
import asyncio
from app.services.vector_store import vector_store_service

async def check():
    info = await vector_store_service.get_collection_info()
    print(f'Collection: {info[\"name\"]}')
    print(f'Vector count: {info[\"vectors_count\"]}')
    print(f'Vector size: {info[\"vector_size\"]}')

asyncio.run(check())
"
```

### 3. Test Search

Query the system manually:

```bash
python -c "
import asyncio
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store_service

async def test_search():
    query = 'What is bipedal locomotion?'
    query_vector = await embedding_service.embed_text(query)
    results = await vector_store_service.search(query_vector, limit=3)

    for result in results:
        print(f'Score: {result[\"score\"]:.3f}')
        print(f'Section: {result[\"payload\"][\"section_title\"]}')
        print(f'Content: {result[\"payload\"][\"content\"][:100]}...')
        print()

asyncio.run(test_search())
"
```

## Troubleshooting

### Issue: "Qdrant connection refused"

**Solution**: Ensure Qdrant is running and accessible:

```bash
# Local Qdrant with Docker
docker run -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant

# Or use Qdrant Cloud and update QDRANT_URL
```

### Issue: "OpenAI API error: Rate limit exceeded"

**Solution**: Ingestion automatically batches requests. To reduce rate:

```python
# In ingest_content.py, reduce batch size
pipeline = EmbeddingPipeline(openai_api_key, batch_size=10)  # Slower, safer
```

### Issue: "PostgreSQL connection error"

**Solution**: Verify database credentials and run migrations:

```bash
python -c "
import asyncio
from app.services.database import db_service

async def init():
    await db_service.create_tables()
    print('✅ Tables created')

asyncio.run(init())
"
```

### Issue: "No chapters found"

**Solution**: Check textbook path structure:

```bash
# Should look like:
Front-End-Book/
  docs/
    module-1/
      chapter-1-name.md
      chapter-2-name.md
    module-2/
      chapter-3-name.md
      ...
```

Files must:
- Start with `chapter-` prefix
- Have `.md` or `.mdx` extension
- Contain `## Section Title` headers

## Cost Estimation

For 245 chunks (~100,000 tokens):

- **Embeddings** (text-embedding-3-small): ~$0.02
- **LLM grounding** (GPT-4, per query): ~$0.01-$0.05 depending on context
- **Vector storage** (Qdrant Cloud): ~$20-50/month

See OpenAI pricing: https://openai.com/pricing

## Next Steps

After successful ingestion:

1. **Start the backend**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test the API**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

3. **Implement chat endpoints** (Phase 3-6)

4. **Integrate frontend** (Phase 7)

## Re-ingestion

To re-ingest after textbook updates:

```bash
# Clear collection (optional)
python -c "
import asyncio
from app.services.vector_store import vector_store_service

# This will be added in future
# await vector_store_service.clear_collection()
"

# Re-run ingestion
python -m scripts.ingest_content
```

## Support

For issues:

1. Check logs: `logs/app.log`
2. Verify `.env` configuration
3. Run `validate_setup.py`
4. Check Qdrant dashboard (if available)
