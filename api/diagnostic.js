/**
 * GET /api/diagnostic - Diagnostic endpoint to check environment
 */

module.exports = (req, res) => {
  try {
    // Try to require the modules
    let pg_status = 'not loaded';
    let jwt_status = 'not loaded';
    let bcryptjs_status = 'not loaded';

    try {
      require('pg');
      pg_status = 'loaded ✓';
    } catch (e) {
      pg_status = `error: ${e.message}`;
    }

    try {
      require('jsonwebtoken');
      jwt_status = 'loaded ✓';
    } catch (e) {
      jwt_status = `error: ${e.message}`;
    }

    try {
      require('bcryptjs');
      bcryptjs_status = 'loaded ✓';
    } catch (e) {
      bcryptjs_status = `error: ${e.message}`;
    }

    res.status(200).json({
      node_version: process.version,
      env_vars: {
        DATABASE_URL: process.env.DATABASE_URL ? 'set' : 'missing',
        JWT_SECRET: process.env.JWT_SECRET ? 'set' : 'missing',
        FRONTEND_URL: process.env.FRONTEND_URL ? 'set' : 'missing',
        OPENAI_API_KEY: process.env.OPENAI_API_KEY ? 'set' : 'missing',
      },
      dependencies: {
        pg: pg_status,
        jsonwebtoken: jwt_status,
        bcryptjs: bcryptjs_status,
      },
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
