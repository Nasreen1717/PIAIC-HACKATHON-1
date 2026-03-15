/**
 * POST /api/auth/signin - User authentication endpoint
 *
 * Authenticates user with email and password.
 * Returns JWT token on success (HTTP 200).
 * Supports remember_me for extended expiration (30 days vs 7 days).
 */

const { Pool } = require('pg');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Configuration
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-key-change-in-production';
const JWT_ALGORITHM = 'HS256';
const JWT_EXPIRATION_DAYS = 7;
const DATABASE_URL = process.env.DATABASE_URL || '';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// Email validation regex
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

// Database pool
let pool = null;

function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: DATABASE_URL,
      max: 10,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });
  }
  return pool;
}

function getCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': FRONTEND_URL,
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Max-Age': '86400',
    'Content-Type': 'application/json',
  };
}

function verifyPassword(plaintext, hashed) {
  return bcrypt.compareSync(plaintext, hashed);
}

function generateJwtToken(userId, email, rememberMe = false) {
  const expirationDays = rememberMe ? 30 : JWT_EXPIRATION_DAYS;
  const expiresIn = `${expirationDays}d`;

  const payload = {
    user_id: userId,
    email: email,
  };

  const accessToken = jwt.sign(payload, JWT_SECRET, {
    algorithm: JWT_ALGORITHM,
    expiresIn: expiresIn,
  });

  const expiresInSeconds = expirationDays * 24 * 60 * 60;

  return {
    access_token: accessToken,
    token_type: 'bearer',
    expires_in: expiresInSeconds,
  };
}

function validateEmail(email) {
  return EMAIL_REGEX.test(email);
}

function validateRequest(body) {
  const email = (body.email || '').trim();
  const password = (body.password || '').trim();

  if (!email) {
    return 'Email is required';
  }
  if (!validateEmail(email)) {
    return 'Invalid email format';
  }

  if (!password) {
    return 'Password is required';
  }

  return '';
}

async function handleSigninRequest(body) {
  try {
    // Validate request
    const validationError = validateRequest(body);
    if (validationError) {
      return {
        body: JSON.stringify({ detail: validationError }),
        status: 400,
        headers: getCorsHeaders(),
      };
    }

    const email = (body.email || '').trim();
    const password = (body.password || '').trim();
    const rememberMe = body.remember_me || false;

    const dbPool = getPool();

    // Find user by email
    const userResult = await dbPool.query(
      'SELECT id, email, password_hash FROM users WHERE email = $1 AND is_active = true',
      [email]
    );

    if (userResult.rows.length === 0) {
      return {
        body: JSON.stringify({ detail: 'Invalid email or password' }),
        status: 401,
        headers: getCorsHeaders(),
      };
    }

    const user = userResult.rows[0];

    // Verify password
    if (!verifyPassword(password, user.password_hash)) {
      return {
        body: JSON.stringify({ detail: 'Invalid email or password' }),
        status: 401,
        headers: getCorsHeaders(),
      };
    }

    // Generate JWT token
    const tokenData = generateJwtToken(user.id, user.email, rememberMe);

    // Success response
    const responseData = {
      access_token: tokenData.access_token,
      token_type: tokenData.token_type,
      expires_in: tokenData.expires_in,
      user_id: user.id,
      email: user.email,
    };

    return {
      body: JSON.stringify(responseData),
      status: 200,
      headers: getCorsHeaders(),
    };
  } catch (error) {
    console.error(`❌ Signin error: ${error.message}`);
    return {
      body: JSON.stringify({ detail: 'Internal server error' }),
      status: 500,
      headers: getCorsHeaders(),
    };
  }
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
    const result = await handleSigninRequest(req.body);
    res.status(result.status)
      .set(result.headers)
      .send(result.body);
  } catch (error) {
    console.error(`❌ Handler error: ${error.message}`);
    res.status(500)
      .set(getCorsHeaders())
      .json({ detail: 'Internal server error' });
  }
};
