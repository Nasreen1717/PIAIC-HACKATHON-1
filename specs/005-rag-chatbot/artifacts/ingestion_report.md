# Content Ingestion Report

**Date**: 2026-02-03T00:47:00.995388
**Duration**: 54.0 seconds
**Status**: ✅ SUCCESS

## Summary

| Metric | Value |
|--------|-------|
| Chapters Parsed | 19 |
| Sections Extracted | 569 |
| Chunks Created | 702 |
| Embeddings Generated | 702 |
| Points Uploaded | 420 |
| Embedding Dimension | 1536 |
| Total Vectors in Qdrant | 420 |

## Statistics

### Chunk Quality
- Average tokens per chunk: 151
- Min tokens: 1
- Max tokens: 434

### Embedding Quality
- Dimension: 1536 (expected: 1536)

## Steps Completed

- ✅ **Parse Content**: success
- ✅ **Chunk Content**: success
- ✅ **Generate Embeddings**: success
- ✅ **Upload to Qdrant**: success

## Warnings

- ⚠️  Found 252 chunks with <100 tokens

## Sample Test Queries

### In-Scope Queries (Should be answered)

- What is ROS 2 and what are its main features?
- Explain the difference between Gazebo and Isaac Sim
- What is bipedal locomotion in humanoid robotics?
- How does NVIDIA Isaac handle real-time perception?
- What are Vision-Language Actions (VLA)?

### Out-of-Scope Queries (Should be rejected)

- What is the weather today?
- Tell me a joke about robots
- What is the capital of France?
- How do I cook pasta?
- Explain quantum computing basics

---

**Generated**: 2026-01-27
