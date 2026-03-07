# Chat API Documentation

**Version**: 0.1.0
**Base URL**: `/api/v1`
**Authentication**: Session-based (no explicit auth required for MVP)

---

## Overview

The Chat API provides endpoints for querying the Physical AI textbook via a RAG-enabled chatbot. All questions are grounded in the textbook content with IEEE-formatted citations.

### Key Features

- **Grounded Answers**: All responses cite textbook sources; no hallucinations
- **Multi-turn Conversations**: Maintains session history across requests
- **Text Selection Support**: Accept highlighted text for direct context
- **Streaming Responses**: SSE-based streaming for real-time token delivery
- **Citation Tracking**: Every response includes IEEE-formatted citations

---

## Endpoints

### POST /api/v1/chat

Submit a question and receive a grounded response with citations.

**Request**

```json
{
  "question": "What is bipedal locomotion?",
  "session_id": "session_abc123def456",
  "selected_text": null,
  "chapter_path": null,
  "section_id": null,
  "section_title": null,
  "context_before": null,
  "context_after": null
}
```

**Request Fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | User's question (1-2000 characters) |
| `session_id` | string | No | Session ID for conversation persistence; auto-generated if not provided |
| `selected_text` | string | No | Highlighted text from textbook; uses this directly instead of vector search |
| `chapter_path` | string | No | Path to chapter containing selected text (e.g., "module-3/chapter-8") |
| `section_id` | string | No | Section identifier (e.g., "8.2.1") |
| `section_title` | string | No | Section title for citation |
| `context_before` | string | No | Context before selected text |
| `context_after` | string | No | Context after selected text |

**Response (200 OK)**

```json
{
  "answer": "Bipedal locomotion is the ability to walk on two legs. In humanoid robots, this requires precise balance and coordination between the upper and lower body. The robot must continuously calculate the center of mass and adjust joint angles to maintain stability.",
  "citations": [
    {
      "chapter_number": 8,
      "section_id": "8.2",
      "section_title": "Bipedal Locomotion Fundamentals",
      "similarity_score": 0.95,
      "chunk_id": "chunk_abc123"
    }
  ],
  "confidence_score": 0.92,
  "response_time_ms": 1247.5
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Generated answer grounded in textbook |
| `citations` | array | List of source citations |
| `citations[].chapter_number` | integer | Chapter number (1-12) |
| `citations[].section_id` | string | Section identifier |
| `citations[].section_title` | string | Section title for display |
| `citations[].similarity_score` | float | Relevance score (0-1) |
| `citations[].chunk_id` | string | Vector store point ID |
| `confidence_score` | float | Overall confidence in answer (0-1) |
| `response_time_ms` | float | Time to generate response (milliseconds) |

**Error Responses**

| Status | Code | Description | Example |
|--------|------|-------------|---------|
| 400 | Bad Request | Invalid input | `{"detail": "Question cannot be empty"}` |
| 408 | Request Timeout | Response generation exceeded timeout | `{"detail": "LLM request timed out"}` |
| 429 | Rate Limited | User quota exceeded | `{"detail": "Rate limit exceeded. Max 100 requests/hour"}` |
| 503 | Service Unavailable | Vector store or LLM offline | `{"detail": "Vector search unavailable"}` |

**Example Requests**

**Basic Question**

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is bipedal locomotion?"
  }'
```

**With Selected Text**

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain this concept",
    "selected_text": "Bipedal locomotion refers to movement on two legs...",
    "chapter_path": "module-3/chapter-8",
    "section_id": "8.2",
    "section_title": "Bipedal Locomotion Fundamentals"
  }'
```

**With Session ID**

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does this compare to quadrupedal motion?",
    "session_id": "session_user123_conv456"
  }'
```

---

### POST /api/v1/chat/stream

Submit a question and receive streaming response with SSE events.

**Response (200 OK, text/event-stream)**

```
data: {"type": "thinking", "delta": "Processing your question..."}

data: {"type": "retrieving", "delta": "Searching textbook..."}

data: {"type": "retrieval", "chunks": [{"chapter": 8, "section": "Bipedal Locomotion"}]}

data: {"type": "response_start", "timestamp": "2024-01-27T10:00:00Z"}

data: {"type": "text_delta", "delta": "Bipedal "}

data: {"type": "text_delta", "delta": "locomotion "}

data: {"type": "text_delta", "delta": "is..."}

data: {"type": "citation", "ieee": "[Chapter 8, Section 8.2: \"Bipedal Locomotion Fundamentals\"]"}

data: {"type": "response_end", "confidence": 0.92}
```

**Event Types**

| Type | Fields | Description |
|------|--------|-------------|
| `thinking` | `delta` | Internal reasoning/processing message |
| `retrieving` | `delta` | Indicates vector search in progress |
| `retrieval` | `chunks` | Retrieved textbook chunks |
| `response_start` | `timestamp` | LLM generation started |
| `text_delta` | `delta` | Streamed token from LLM |
| `citation` | `ieee` | IEEE-formatted citation |
| `response_end` | `confidence` | Final confidence score |
| `error` | `message` | Error occurred during generation |

**Example (JavaScript/Python)**

```javascript
// JavaScript with fetch
const response = await fetch('/api/v1/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: "What is bipedal locomotion?" })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const lines = decoder.decode(value).split('\n');
  lines.forEach(line => {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));
      console.log('Event:', event);
      // Handle event (render text_delta, show citations, etc.)
    }
  });
}
```

---

### GET /api/v1/chat/history/{session_id}

Retrieve conversation history for a session.

**Response (200 OK)**

```json
{
  "session": {
    "session_id": "session_abc123",
    "message_count": 3,
    "created_at": "2024-01-27T10:00:00Z",
    "updated_at": "2024-01-27T10:15:00Z"
  },
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "What is bipedal locomotion?",
      "citations": null,
      "created_at": "2024-01-27T10:00:00Z"
    },
    {
      "id": "msg_2",
      "role": "assistant",
      "content": "Bipedal locomotion is...",
      "citations": [
        {
          "chapter_number": 8,
          "section_id": "8.2",
          "section_title": "Bipedal Locomotion Fundamentals"
        }
      ],
      "created_at": "2024-01-27T10:00:05Z"
    }
  ]
}
```

**Error Responses**

| Status | Description |
|--------|-------------|
| 404 | Session not found |
| 500 | Server error |

**Example**

```bash
curl http://localhost:8000/api/v1/chat/history/session_abc123
```

---

### POST /api/v1/chat/sessions

Create a new chat session.

**Request**

```
(No request body required)
```

**Response (200 OK)**

```json
{
  "session_id": "session_xyz789",
  "message_count": 0,
  "created_at": "2024-01-27T10:00:00Z",
  "updated_at": "2024-01-27T10:00:00Z"
}
```

**Example**

```bash
curl -X POST http://localhost:8000/api/v1/chat/sessions
```

---

### GET /api/v1/health

Check system health and service connectivity.

**Response (200 OK)**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-27T10:00:00Z",
  "services": {
    "qdrant": {
      "status": "healthy"
    },
    "openai": {
      "status": "healthy"
    },
    "llm": {
      "status": "healthy"
    }
  }
}
```

**Error Responses**

| Status | Description |
|--------|-------------|
| 503 | Service unavailable |

---

### GET /api/v1/health/detailed

Detailed health check with service metrics.

**Response (200 OK)**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-27T10:00:00Z",
  "services": {
    "qdrant": {
      "status": "healthy",
      "collection": {
        "name": "textbook_chunks",
        "vectors_count": 1247,
        "vector_size": 1536
      }
    },
    "openai": {
      "status": "healthy",
      "model": "text-embedding-3-small"
    }
  }
}
```

---

## Response Time Characteristics

### Non-Streaming Endpoint

**Typical Latency Breakdown:**
- Query Embedding: 100-200ms
- Vector Search: 20-50ms
- LLM Generation: 800-1500ms
- Database Write: 50-100ms
- **Total (p95): ~1500ms**

### Streaming Endpoint

**Benefits:**
- First token in 200-300ms (vs. 1500ms for full response)
- Tokens streamed every 50-100ms
- Better UX for users waiting for response

---

## Rate Limiting

**Per-User Limits:**
- 100 requests/hour (per session ID)
- 10 requests/minute (per session ID)

**Global Limits:**
- 1000 requests/minute (per IP)
- 10000 requests/hour (per IP)

**Response:** HTTP 429 with `Retry-After` header

---

## Error Handling

All error responses include a `detail` field with description:

```json
{
  "detail": "Query is empty"
}
```

### Common Errors

| Message | Cause | Solution |
|---------|-------|----------|
| "Question cannot be empty" | Empty query submitted | Provide non-empty question |
| "Question too long" | Query exceeds 2000 characters | Shorten question or split into multiple |
| "Vector search unavailable" | Qdrant offline | Wait or check deployment logs |
| "LLM service unavailable" | OpenAI API unreachable | Check API key and quota |
| "Rate limit exceeded" | Too many requests | Wait and retry after delay |

---

## Citation Format

All citations follow IEEE standard:

```
[Chapter X, Section Y.Z: "Section Title"]
```

**Components:**
- `Chapter X`: Textbook chapter number (1-12)
- `Section Y.Z`: Section identifier (e.g., "2.1", "8.3.2")
- `Section Title`: Human-readable section name

**In API Response:**
```json
{
  "chapter_number": 8,
  "section_id": "8.2.1",
  "section_title": "Bipedal Locomotion: Gait Analysis"
}
```

---

## Best Practices

### Client Implementation

1. **Always provide `session_id`** for better context in multi-turn conversations
2. **Use streaming endpoint** for better UX; first token appears quickly
3. **Handle network errors gracefully** with retry logic (exponential backoff)
4. **Cache frequent questions** locally to reduce API calls
5. **Show loading state** while waiting for response

### Question Phrasing

1. **Be specific**: "Explain bipedal locomotion" vs. "What is walking?"
2. **Use textbook terminology**: Questions using module-specific terms work better
3. **One question at a time**: Keep questions focused
4. **Avoid leading questions**: "Is bipedal locomotion the best?" may get refusals

### Handling Out-of-Scope Responses

If the chatbot cannot answer from textbook material, it responds:

```
I cannot answer this question based on the available textbook material.
Please try rewording your question or consult the relevant textbook chapter directly.
```

**What to do:**
- Rephrase using different terminology
- Select relevant text from textbook and resubmit with `selected_text`
- Ask a more specific question about textbook content

---

## Integration Examples

### React Component

```javascript
const [response, setResponse] = useState(null);
const [loading, setLoading] = useState(false);

const askQuestion = async (question) => {
  setLoading(true);
  try {
    const res = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        session_id: sessionStorage.getItem('sessionId'),
      }),
    });
    const data = await res.json();
    setResponse(data);
  } catch (err) {
    console.error('Error:', err);
  }
  setLoading(false);
};
```

### Python Client

```python
import requests

def ask_question(question, session_id=None):
    response = requests.post(
        'http://localhost:8000/api/v1/chat',
        json={
            'question': question,
            'session_id': session_id,
        },
        timeout=3,
    )
    response.raise_for_status()
    return response.json()

# Usage
answer = ask_question("What is bipedal locomotion?")
print(answer['answer'])
for citation in answer['citations']:
    print(f"Source: {citation['section_title']}")
```

---

## Support & Troubleshooting

### API not responding

1. Check if backend is running: `curl http://localhost:8000/`
2. Check health endpoint: `curl http://localhost:8000/api/v1/health`
3. View server logs for errors

### Slow responses

1. Check latency: `response_time_ms` in API response
2. If LLM generation >1500ms, vector search quality may be low
3. Consider using streaming endpoint for better perceived performance

### No citations in response

1. Check `confidence_score` - may be low confidence
2. Verify Qdrant collection has content
3. Try using text selection for guaranteed context

---

**Last Updated**: 2026-01-27
**Maintainer**: Physical AI Team
