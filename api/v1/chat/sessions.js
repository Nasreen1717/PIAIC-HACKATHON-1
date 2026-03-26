/**
 * POST /api/v1/chat/sessions - Create chat session
 *
 * Creates a new chat session for a user to maintain conversation history.
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
    // Generate new session ID
    const sessionId = 'session_' + Math.random().toString(36).substr(2, 16);

    console.log(`✅ Chat session created: ${sessionId}`);

    res.status(201).json({
      session_id: sessionId,
      created_at: new Date().toISOString(),
      message: 'Chat session created successfully',
    });
  } catch (error) {
    console.error(`❌ Session creation error: ${error.message}`);
    res.status(500).json({ detail: 'Failed to create session' });
  }
};
