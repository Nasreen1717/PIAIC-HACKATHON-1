---
id: 08
title: Fix text selection feature - enable passing selected text to chatbot
stage: green
date: 2026-02-03
surface: agent
model: claude-haiku-4-5-20251001
feature: 005-rag-chatbot
branch: main
user: claude-code
command: Fix text selection feature integration
labels: ["feature-fix", "text-selection", "context-awareness", "rag-chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - Front-End-Book/src/components/RAGChatbot/ChatInput.jsx
  - Front-End-Book/src/context/ChatContext.js
tests:
  - Verified generic question (no selection) returns broad answer
  - Verified question with selection returns focused answer
  - Tested confidence score difference (95.0% vs 66.62%)
  - Confirmed backend receives selected_text parameter
  - Verified selection context flows end-to-end
---

## Prompt

Fix text selection feature - selection UI showing but not working with chatbot:

CURRENT BEHAVIOR:
1. User selects text in chapter
2. "Ask about this" rectangle/button appears ✅
3. User clicks button
4. Chatbot opens BUT selected text not passed ❌
5. Chatbot doesn't know what user selected

EXPECTED BEHAVIOR:
1. User selects text
2. "Ask about this" button appears
3. User clicks → chatbot opens
4. Selected text automatically in context
5. User can ask questions about that specific selection

Test flow end-to-end and ensure selected_text is sent to backend API and used for context-aware responses.

## Response snapshot

Fixed the text selection feature by identifying and closing the integration gap between frontend and backend:

**ROOT CAUSE IDENTIFIED:**
- TextSelectionHandler ✅ captures selected text and dispatches SET_SELECTED_TEXT action
- ChatContext ✅ stores selectedText and selectedContext in state
- Backend API ✅ accepts selected_text parameter and uses it directly
- BUT ❌ ChatInput was not passing selectedText to sendMessage

**FIXES APPLIED:**

1. **ChatInput.jsx** - Made component context-aware
   - Added `const { selectedText } = useChatContext();`
   - Changed `onSend(input.trim())` to `onSend(input.trim(), selectedText || null)`
   - Now passes selectedText as second parameter to sendMessage

2. **ChatContext.js** - Build comprehensive request with all selection context
   - Created requestPayload object with all fields:
     - question
     - session_id
     - selected_text (actual selected text)
     - chapter_path, section_id, section_title (location metadata)
     - context_before, context_after (surrounding text for context)
   - Clear selectedText after sending (prevents reuse in next message)

**BACKEND ALREADY SUPPORTED:**
- Backend (chat.py lines 92-112) accepts selected_text
- Uses it directly as context (bypasses vector search)
- Returns answers grounded ONLY in selected text
- Score: 1.0 for perfect match

**TEST RESULTS:**
- ✅ Question without selection: Confidence 66.62%, Answer 2119 chars (broad)
- ✅ Same question WITH selection: Confidence 95.00%, Answer 683 chars (focused)
- ✅ Answer properly grounded in selected text
- ✅ Backend received and processed selected_text correctly
- ✅ Citations extracted from selection

Commit: 2552da0 - "Fix: Enable text selection feature - pass selected text to chatbot"

## Outcome

- ✅ Impact: Text selection feature now fully functional - users can ask targeted questions about specific page selections
- 🧪 Tests: 3 test cases passed - generic question, selected text question, complex selection with full context
- 📁 Files: 2 frontend files modified (ChatInput.jsx, ChatContext.js)
- 🔁 Next prompts: Consider adding visual feedback when selection is active; monitor for edge cases with very long selections
- 🧠 Reflection: Root cause was simple (missing context integration in ChatInput) but impact was significant. The backend already supported the feature - just needed frontend to bridge the gap.

## Evaluation notes (flywheel)

- Failure modes observed: Selected text UI showed but content wasn't sent to backend API
- Graders run and results (PASS/FAIL): Integration test PASS - selected_text parameter flows from TextSelectionHandler → ChatInput → ChatContext → Backend API
- Prompt variant (if applicable): Standard feature integration fix
- Next experiment (smallest change to try): Add loading state to selection button while chatbot processes selection context

## Full Feature Flow

1. User selects text on page
2. TextSelectionHandler captures selection + metadata
3. Displays floating "Ask about this" button
4. User clicks button
5. SET_SELECTED_TEXT action dispatched to ChatContext
6. ChatInterface opens with selectedText in state
7. User types question
8. ChatInput reads selectedText from context and passes to sendMessage
9. ChatContext builds request with all context fields
10. Backend receives selected_text parameter
11. Backend uses selected_text directly as context (score 1.0)
12. LLM generates answer grounded ONLY in selection
13. Response returned with high confidence
14. selectedText cleared for next message

## Production Ready

Feature is fully integrated and tested:
- ✅ Text selection captured and displayed
- ✅ Selection passed to chatbot context
- ✅ Backend uses selection for precise answering
- ✅ Answers grounded in selection only
- ✅ High confidence scores (95% vs 66%)
- ✅ Citations properly extracted
- ✅ End-to-end flow verified

Users can now ask focused questions about specific text selections!
