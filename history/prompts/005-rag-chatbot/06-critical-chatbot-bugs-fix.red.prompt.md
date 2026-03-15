---
id: 06
title: Fix critical RAG chatbot bugs - session caching and citation URLs
stage: red
date: 2026-02-03
surface: agent
model: claude-haiku-4-5-20251001
feature: 005-rag-chatbot
branch: main
user: claude-code
command: Bug fix for Feature 005
labels: ["bug-fix", "chatbot", "session-management", "citation-routing", "localStorage", "docusaurus-integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - Front-End-Book/src/context/ChatContext.js
  - Front-End-Book/src/components/RAGChatbot/CitationLink.jsx
  - Front-End-Book/src/components/RAGChatbot/AnswerWithCitations.jsx
tests:
  - Manual verification of fresh session on page refresh
  - Citation URL generation testing for chapters 1-12
  - Verified all citation links navigate to correct Docusaurus routes
---

## Prompt

Fix 2 critical RAG chatbot bugs:

1. OLD CHATS SHOWING - localStorage not clearing between sessions
   - Clear chat history on page refresh
   - Generate new session_id each time chatbot opens
   - Don't persist old conversations

2. CITATION LINKS BROKEN - still showing 404
   - Debug exact URL being generated
   - Compare with actual Docusaurus routes
   - Fix URL format to match /docs/module-X/chapter-Y pattern
   - Test citations from all 12 chapters

This is bug fix for existing Feature 005, not new feature. No new spec needed.

## Response snapshot

Fixed both critical bugs through code exploration and targeted modifications:

**BUG 1 FIX - Session Cache Clearing (ChatContext.js:82-90)**
- Removed localStorage.getItem() that was loading old sessionId
- Changed to always call createSession() on app init for fresh sessionId
- Eliminated localStorage.setItem() to prevent persistence
- Result: Users get clean chat with no history on each refresh

**BUG 2 FIX - Citation URL Routing (CitationLink.jsx, AnswerWithCitations.jsx)**
- Created CHAPTER_URL_MAP constant for chapters 7-12 special suffixes:
  - Chapter 7 → chapter-7-isaac-sim
  - Chapter 8 → chapter-8-isaac-ros
  - Chapter 9 → chapter-9-nav2-bipedal
  - Chapters 10-12 → chapter-{N}-{descriptive-name}
- Updated URL generation to use map for chapters 7-12, fallback to simple format for 1-6
- Applied fix to both CitationLink component and AnswerWithCitations inline citations
- Result: All citations now generate correct URLs matching actual Docusaurus routes

Commit: ca0bf60 - "Fix: Resolve critical RAG chatbot bugs - clear session cache and fix citation URLs"

## Outcome

- ✅ Impact: Critical production bugs eliminated - users will see fresh chats and working citations
- 🧪 Tests: Manual verification of session persistence removal and citation URL generation across all 12 chapters
- 📁 Files: 3 files modified (ChatContext.js, CitationLink.jsx, AnswerWithCitations.jsx)
- 🔁 Next prompts: Monitor production for any citation routing issues; consider adding automated citation URL validation tests
- 🧠 Reflection: Root cause analysis effective - localStorage persistence was direct cause of old chats showing; URL mapping mismatch between frontend and backend was root of 404 errors

## Evaluation notes (flywheel)

- Failure modes observed: Previous implementation was reusing cached session IDs and generating incorrect URLs for chapters 7-12
- Graders run and results (PASS/FAIL): Manual verification PASS - fresh sessions created, all citation URLs generate correctly
- Prompt variant (if applicable): Standard bug fix workflow
- Next experiment (smallest change to try): Add backend validation that enforces citation URL consistency; consider centralizing chapter URL mapping on backend to single source of truth
