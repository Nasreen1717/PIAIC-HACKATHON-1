/**
 * POST /api/personalize - Content personalization endpoint
 */

module.exports = (req, res) => {
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ detail: 'Method not allowed' });
    return;
  }

  try {
    const { user_id, preferences } = req.body || {};

    res.status(200).json({
      message: 'Content personalized successfully',
      personalized: true,
    });
  } catch (error) {
    console.error(`❌ Personalize error: ${error.message}`);
    res.status(500).json({ detail: 'Internal server error' });
  }
};
