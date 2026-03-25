/**
 * POST /api/chat - AI chat endpoint
 * Handles chat messages and returns AI responses
 */

function getCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Content-Type': 'application/json',
  };
}

module.exports = async (req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.status(204).set(getCorsHeaders()).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).set(getCorsHeaders()).json({ detail: 'Method not allowed' });
    return;
  }

  try {
    const { message, context } = req.body || {};

    if (!message) {
      res.status(400).set(getCorsHeaders()).json({ detail: 'Message is required' });
      return;
    }

    // For now, return a simple response
    // In production, this would call OpenAI API
    const response = {
      message: 'Chat session created successfully. Ready to answer questions about the textbook.',
      session_id: Math.random().toString(36).substr(2, 9),
    };

    res.status(200)
      .set(getCorsHeaders())
      .json(response);
  } catch (error) {
    console.error(`❌ Chat error: ${error.message}`);
    res.status(500)
      .set(getCorsHeaders())
      .json({ detail: 'Internal server error' });
  }
};
