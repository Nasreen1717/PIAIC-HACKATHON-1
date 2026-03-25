/**
 * POST /api/translate - Translation endpoint
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
    const { text, target_language } = req.body || {};

    if (!text || !target_language) {
      res.status(400).json({ detail: 'Text and target_language are required' });
      return;
    }

    res.status(200).json({
      original_text: text,
      translated_text: text, // In production, would use translation API
      target_language: target_language,
    });
  } catch (error) {
    console.error(`❌ Translate error: ${error.message}`);
    res.status(500).json({ detail: 'Internal server error' });
  }
};
