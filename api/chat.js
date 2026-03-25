/**
 * POST /api/chat - AI chat endpoint
 */

module.exports = async (req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ detail: 'Method not allowed' });
    return;
  }

  try {
    const { message } = req.body || {};

    if (!message) {
      res.status(400).json({ detail: 'Message is required' });
      return;
    }

    // Return chat session
    res.status(200).json({
      message: 'Chat session created successfully. Ready to answer questions about the textbook.',
      session_id: 'session_' + Math.random().toString(36).substr(2, 9),
    });
  } catch (error) {
    console.error(`❌ Chat error: ${error.message}`);
    res.status(500).json({ detail: 'Internal server error' });
  }
};
