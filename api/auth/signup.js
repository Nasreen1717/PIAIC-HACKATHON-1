/**
 * POST /api/auth/signup - User registration endpoint
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
    const { email, password, full_name } = req.body || {};

    if (!email || !password || !full_name) {
      res.status(400).json({ detail: 'Email, password, and full_name are required' });
      return;
    }

    // For now, return success - in production would hash password and save to DB
    res.status(201).json({
      message: 'User registered successfully',
      email: email,
      user_id: Math.floor(Math.random() * 10000),
      access_token: 'token_' + Math.random().toString(36).substr(2, 9),
      token_type: 'bearer',
      expires_in: 604800, // 7 days
    });
  } catch (error) {
    console.error(`❌ Signup error: ${error.message}`);
    res.status(500).json({ detail: 'Internal server error' });
  }
};
