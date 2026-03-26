/**
 * POST /api/v1/translate - Translation endpoint
 *
 * Translates text to Urdu using OpenAI API.
 */

module.exports = async (req, res) => {
  // Enable CORS
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ detail: 'Method not allowed' });
    return;
  }

  try {
    const { text, target_lang, source_lang, session_id } = req.body || {};

    // Validate required fields
    if (!text || !text.trim()) {
      res.status(400).json({ detail: 'Text is required' });
      return;
    }

    if (!target_lang) {
      res.status(400).json({ detail: 'target_lang is required' });
      return;
    }

    // Only Urdu is supported
    if (target_lang !== 'ur') {
      res.status(400).json({ detail: 'Only Urdu (ur) translation is supported' });
      return;
    }

    // Check for OpenAI API key
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      console.error('❌ OpenAI API key not configured');
      res.status(503).json({
        detail: 'Translation service not configured',
        code: 'service_error',
      });
      return;
    }

    // Call OpenAI API for translation
    const translatedText = await translateWithOpenAI(text, apiKey);

    res.status(200).json({
      translated_text: translatedText,
      detected_lang: source_lang || 'en',
      confidence: 0.95,
      session_id: session_id || null,
    });
  } catch (error) {
    console.error(`❌ Translate error: ${error.message}`);

    // Return appropriate error response
    if (error.code === 'auth_error') {
      res.status(401).json({ detail: 'Authentication failed' });
    } else if (error.code === 'validation_error') {
      res.status(400).json({ detail: error.message });
    } else {
      res.status(503).json({
        detail: 'Translation service error. Please try again later.',
        error: error.message,
      });
    }
  }
};

/**
 * Translate text to Urdu using OpenAI API
 */
async function translateWithOpenAI(text, apiKey) {
  const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';

  const systemPrompt = `You are a professional translator. Translate the provided English text to Urdu.
Important:
- Maintain the original meaning and tone
- PRESERVE ALL HTML TAGS EXACTLY as they appear (<h1>, <h2>, <h3>, <p>, <ul>, <li>, <strong>, <em>, <code>, <pre>, etc.)
- Only translate the text content INSIDE the tags, never modify or remove tags
- Preserve any formatting, code blocks, code placeholders [CODE_BLOCK_*], or special characters
- Translate only the text content, not code or technical terms where English is standard
- Keep the exact same HTML structure and layout
- Respond ONLY with the translated HTML, no explanations or additional content`;

  const userMessage = `Translate the following English text to Urdu:\n\n${text}`;

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage },
        ],
        temperature: 0.3,
        max_tokens: Math.min(text.length * 2, 4000),
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('OpenAI API error:', errorData);

      if (response.status === 401) {
        throw {
          code: 'auth_error',
          message: 'Invalid API key',
        };
      }

      throw {
        code: 'api_error',
        message: errorData.error?.message || 'OpenAI API error',
      };
    }

    const data = await response.json();
    const translatedText = data.choices[0]?.message?.content?.trim();

    if (!translatedText) {
      throw {
        code: 'validation_error',
        message: 'Empty response from translation service',
      };
    }

    return translatedText;
  } catch (error) {
    if (error.code) {
      throw error;
    }
    console.error('Translation fetch error:', error);
    throw {
      code: 'network_error',
      message: 'Failed to connect to translation service',
    };
  }
}
