# API Contract: OpenAI GPT-4 Integration

**Purpose**: Define interface between frontend translation component and OpenAI API

**Client Library**: openai@^4.x (JavaScript SDK)

---

## Function Signature

```typescript
async function translateContent(
  content: string,
  targetLanguage: 'ur',
  options?: {
    maxTokens?: number;
    temperature?: number;
    timeout?: number;
  }
): Promise<{
  translated: string;
  tokensUsed: {
    input: number;
    output: number;
  };
  duration: number;
}>
```

---

## Request

### Initialization

```typescript
import { OpenAI } from 'openai';

const openai = new OpenAI({
  apiKey: process.env.REACT_APP_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true  // Required for client-side usage
});
```

**Environment Variable**:
- `REACT_APP_OPENAI_API_KEY`: OpenAI API key (from .env.local or build environment)
- Must be set before build or at runtime

### API Call

```typescript
const response = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [
    {
      role: "system",
      content: `You are a professional technical translator specializing in robotics and AI education.

Translate the following content from English to Urdu, preserving:
1. All code block syntax - do NOT translate code blocks
2. Technical terms (ROS 2, node, topic, etc.) - translate to Urdu, include English in parentheses on first occurrence
3. All formatting (headings, lists, emphasis, links)
4. Educational tone (clear, encouraging, accessible to students)
5. Links and references (preserve URLs, translate link text)

OUTPUT RULES:
- Return ONLY the translated text in clean Urdu
- Do NOT add explanations, notes, or metadata
- Do NOT include placeholder markers for code blocks
- Preserve the exact structure of the input`
    },
    {
      role: "user",
      content: content  // Cleaned HTML/plaintext chapter content
    }
  ],
  temperature: 0.3,    // Low temperature ensures consistency
  max_tokens: 4000,    // Sufficient for typical chapter (~2000 words)
  top_p: 0.95
});
```

### Input Constraints

| Parameter | Type | Requirement | Notes |
|-----------|------|-------------|-------|
| `content` | string | Max 12,000 tokens (~3000 words) | Larger chapters chunked by caller |
| `targetLanguage` | 'ur' | Required | Only Urdu supported in MVP |
| `model` | "gpt-4" | Required | GPT-4 only (not GPT-3.5) for quality |
| `temperature` | number | 0.3 (fixed) | Low: consistency over creativity |
| `max_tokens` | number | 4000 (default) | Adjustable per content length |
| `timeout` | number | 30000ms (30s) | API call timeout |

---

## Response

### Success Response

```json
{
  "id": "chatcmpl-8SXYZ...",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[Translated Urdu text here]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 2500,
    "completion_tokens": 2600,
    "total_tokens": 5100
  }
}
```

### Parsed Response (Frontend)

```typescript
{
  translated: "[Urdu text]",
  tokensUsed: {
    input: 2500,
    output: 2600
  },
  duration: 3200  // milliseconds
}
```

### Validation

```typescript
if (!response.choices?.[0]?.message?.content) {
  throw new TranslationError({
    code: 'INVALID_RESPONSE',
    message: 'OpenAI API returned empty response',
    severity: 'error',
    retryable: true
  });
}

if (!response.usage) {
  throw new TranslationError({
    code: 'MISSING_USAGE_DATA',
    message: 'Failed to track token usage',
    severity: 'warning',  // Non-fatal
    retryable: false
  });
}
```

---

## Error Handling

### Error Codes

| Code | HTTP Status | User Message | Retryable | Cause |
|------|------------|--------------|-----------|-------|
| `OPENAI_API_KEY_INVALID` | 401 | "Invalid API key. Please check configuration." | No | Missing/invalid API key |
| `OPENAI_QUOTA_EXCEEDED` | 429 | "Rate limit exceeded. Please try again in a moment." | Yes (with backoff) | Too many requests or quota exceeded |
| `OPENAI_CONTENT_BLOCKED` | 400 | "Content could not be translated due to safety filters." | No | OpenAI safety filters triggered |
| `NETWORK_TIMEOUT` | N/A | "Translation request timed out. Please try again." | Yes | Network timeout after 30s |
| `NETWORK_ERROR` | N/A | "Network error. Please check your connection." | Yes | Generic network failure |
| `PARSE_ERROR` | N/A | "Failed to parse translation response." | No | Malformed response from API |

### Retry Strategy

```typescript
async function translateWithRetry(
  content: string,
  maxRetries: number = 3,
  initialDelayMs: number = 1000
): Promise<TranslationResult> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await translateContent(content, 'ur');
    } catch (error) {
      if (!error.retryable) throw error;
      if (attempt === maxRetries) throw error;

      // Exponential backoff: 1s, 2s, 4s
      const delayMs = initialDelayMs * Math.pow(2, attempt - 1);
      await sleep(delayMs);
    }
  }
}
```

---

## Performance Characteristics

### Latency

| Metric | Target | Notes |
|--------|--------|-------|
| API response time | < 3 seconds | Success criteria SC-002 |
| Average chapter | 2-3 seconds | Typical 2000-word chapter |
| Large chapter (4000+ words) | 4-6 seconds | May need chunking |
| Network overhead | < 500ms | RTT to OpenAI |

### Token Usage

| Content | Avg Input Tokens | Avg Output Tokens | Approx Cost |
|---------|-----------------|------------------|------------|
| Small chapter (500 words) | 625 | 650 | $0.038 |
| Medium chapter (2000 words) | 2500 | 2600 | $0.15 |
| Large chapter (4000 words) | 5000 | 5200 | $0.30 |

**Cost Model**: At 20 chapters × 2 translations/month = 40 API calls/month ≈ $6/month (modest)

### Rate Limits

**OpenAI Free Tier**:
- 3 requests/minute (default)
- 40,000 tokens/minute

**Client-side mitigation**:
- Implement request debouncing (500ms minimum between requests)
- Queue requests if limit approached
- Display "too many requests" error with backoff guidance

---

## Integration Example

```typescript
// translationApi.ts

import { OpenAI, APIError, RateLimitError, APIConnectionError } from 'openai';

const openai = new OpenAI({
  apiKey: process.env.REACT_APP_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true
});

export async function translateContent(
  content: string,
  targetLanguage: 'ur' = 'ur'
): Promise<TranslationResult> {
  if (!content.trim()) {
    throw new TranslationError({
      code: 'EMPTY_CONTENT',
      message: 'No content to translate',
      severity: 'error',
      retryable: false
    });
  }

  try {
    const startTime = performance.now();

    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: SYSTEM_PROMPT  // Defined in constants
        },
        {
          role: "user",
          content: content
        }
      ],
      temperature: 0.3,
      max_tokens: 4000,
      top_p: 0.95
    });

    const duration = performance.now() - startTime;

    if (!response.choices?.[0]?.message?.content) {
      throw new TranslationError({
        code: 'INVALID_RESPONSE',
        message: 'OpenAI returned empty response',
        severity: 'error',
        retryable: true
      });
    }

    return {
      translated: response.choices[0].message.content,
      tokensUsed: {
        input: response.usage?.prompt_tokens || 0,
        output: response.usage?.completion_tokens || 0
      },
      duration
    };

  } catch (error) {
    if (error instanceof RateLimitError) {
      throw new TranslationError({
        code: 'OPENAI_QUOTA_EXCEEDED',
        message: 'Rate limit exceeded. Please try again in a moment.',
        severity: 'error',
        retryable: true
      });
    } else if (error instanceof APIConnectionError) {
      throw new TranslationError({
        code: 'NETWORK_ERROR',
        message: 'Network error. Please check your connection.',
        severity: 'error',
        retryable: true
      });
    } else if (error instanceof APIError) {
      throw new TranslationError({
        code: 'OPENAI_API_KEY_INVALID',
        message: 'Invalid API key. Please check configuration.',
        severity: 'error',
        retryable: false
      });
    } else {
      throw new TranslationError({
        code: 'UNKNOWN_ERROR',
        message: 'Translation failed. Please try again.',
        severity: 'error',
        retryable: true
      });
    }
  }
}
```

---

## Testing Strategy

### Unit Tests

```typescript
describe('translateContent', () => {
  it('should translate English to Urdu', async () => {
    const content = 'Hello, this is a test chapter.';
    const result = await translateContent(content);

    expect(result.translated).toBeTruthy();
    expect(result.tokensUsed.input).toBeGreaterThan(0);
    expect(result.duration).toBeLessThan(10000);  // 10 seconds max
  });

  it('should preserve code blocks', async () => {
    const content = `
## Code Example
Here is Python code:
\`\`\`python
print("Hello, World!")
\`\`\`
    `;
    const result = await translateContent(content);

    expect(result.translated).toContain('python');
    expect(result.translated).toContain('Hello, World!');
  });

  it('should handle rate limit errors', async () => {
    // Mock OpenAI client to throw RateLimitError
    await expect(translateContent('test')).rejects.toThrow(TranslationError);
  });
});
```

### Integration Tests

- Test with real OpenAI API (limited calls to avoid quota)
- Validate Urdu output against human review baseline (95% accuracy)
- Measure response time and token usage

### Load Testing

- Simulate 10 concurrent requests → verify no data corruption
- Measure API quota consumption

---

## Deprecation & Versioning

**Current Version**: 1.0 (OpenAI GPT-4)

**Future**: If OpenAI releases GPT-5 or pricing changes, update:
1. `model` parameter to "gpt-5"
2. `system_prompt` if needed for new capabilities
3. Test and validate accuracy before rollout

**Backward Compatibility**: Not applicable (client-side only)

---

## References

- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat/create)
- [OpenAI JavaScript SDK](https://github.com/openai/node-sdk)
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
