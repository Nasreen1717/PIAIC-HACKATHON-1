/**
 * POST /api/auth/signin - User authentication endpoint
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
    const { email, password } = req.body || {};

    if (!email || !password) {
      res.status(400).json({ detail: 'Email and password are required' });
      return;
    }

    // For now, accept any email/password - in production would verify from DB
    res.status(200).json({
      message: 'User signed in successfully',
      email: email,
      user_id: Math.floor(Math.random() * 10000),
      access_token: 'token_' + Math.random().toString(36).substr(2, 9),
      token_type: 'bearer',
      expires_in: 604800, // 7 days
    });
  } catch (error) {
    console.error(`❌ Signin error: ${error.message}`);
    res.status(500).json({ detail: 'Internal server error' });
  }
};
