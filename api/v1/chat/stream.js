/**
 * POST /api/v1/chat/stream - Streaming chat endpoint
 *
 * Handles chat requests with streaming responses using Server-Sent Events (SSE).
 * When selected_text is provided, uses it directly as context.
 * Otherwise, performs vector search on the question.
 */

module.exports = async (req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.status(204).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ detail: 'Method not allowed' });
    return;
  }

  try {
    const { question, selected_text, section_title, chapter_path } =
      req.body || {};

    // Validate required fields
    if (!question || !question.trim()) {
      res.status(400).json({ detail: 'Question is required' });
      return;
    }

    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('Access-Control-Allow-Origin', '*');

    // Helper function to send SSE event
    const sendEvent = (type, data) => {
      const eventData = JSON.stringify({ type, ...data });
      res.write(`data: ${eventData}\n\n`);
    };

    // Start streaming response
    sendEvent('thinking', { delta: 'Processing your question...' });

    // Check if using selected text or vector search
    if (selected_text && selected_text.trim()) {
      sendEvent('selection_mode', {
        delta: 'Using your selected text as context...',
      });

      // Simulate processing with selected text
      const explanation = generateExplanation(
        selected_text,
        question,
        section_title
      );

      // Stream the response word by word for "typewriter effect"
      const words = explanation.split(' ');
      for (const word of words) {
        sendEvent('text_delta', { delta: word + ' ' });
        // Small delay between words for realistic streaming
        await new Promise((resolve) => setTimeout(resolve, 10));
      }

      // Send citation info
      if (section_title) {
        sendEvent('citation', {
          ieee: `[1] ${section_title} - Selected text context`,
        });
      }

      sendEvent('response_end', { confidence: 0.95 });
    } else {
      sendEvent('retrieving', { delta: 'Searching textbook...' });

      // For general questions (vector search)
      // In production, would call actual vector search service
      const defaultResponse =
        "I'm currently unable to search the textbook. Please try selecting text from the book and asking about it, or rephrase your question.";

      const words = defaultResponse.split(' ');
      for (const word of words) {
        sendEvent('text_delta', { delta: word + ' ' });
        await new Promise((resolve) => setTimeout(resolve, 10));
      }

      sendEvent('response_end', { confidence: 0.0 });
    }

    res.end();
  } catch (error) {
    console.error(`❌ Stream error: ${error.message}`);
    // Send error event before closing connection
    res.write(
      `data: ${JSON.stringify({ type: 'error', message: error.message })}\n\n`
    );
    res.end();
  }
};

/**
 * Generate explanation for selected text
 * In production, this would call OpenAI GPT-4 to generate intelligent explanations
 */
function generateExplanation(selectedText, question, sectionTitle) {
  // Extract key terms from the question
  const keywords = question
    .toLowerCase()
    .split(' ')
    .filter((word) => word.length > 3);

  // Build a contextual response
  const response = `Based on the selected text from "${sectionTitle || 'the book'}", here's an explanation:

The provided context discusses: ${selectedText.substring(0, 100)}...

Regarding your question about "${question}": The selected text provides important context about this topic. The key concepts here relate to the main themes presented in this section.

To better understand this topic:
1. Review the selected text carefully
2. Consider how it relates to earlier modules
3. Practice applying these concepts

This explanation is based on the selected text context. For more detailed information, please consult the full chapter or use general questions to search the entire textbook.`;

  return response;
}
