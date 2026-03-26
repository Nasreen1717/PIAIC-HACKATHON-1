/**
 * GET /api/v1/chat/history/:sessionId - Get conversation history
 *
 * Retrieves the conversation history for a specific chat session.
 */

module.exports = async (req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.status(204).end();
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ detail: 'Method not allowed' });
    return;
  }

  try {
    // Get session ID from dynamic route parameter
    const sessionId = req.query.sessionId;

    if (!sessionId) {
      res.status(400).json({ detail: 'Session ID is required' });
      return;
    }

    // For now, return empty conversation history
    // In production, would fetch from database
    const conversationHistory = {
      session_id: sessionId,
      messages: [],
      created_at: new Date().toISOString(),
    };

    console.log(`✅ Retrieved conversation history for session: ${sessionId}`);

    res.status(200).json(conversationHistory);
  } catch (error) {
    console.error(`❌ History fetch error: ${error.message}`);
    res.status(500).json({ detail: 'Failed to fetch conversation history' });
  }
};
