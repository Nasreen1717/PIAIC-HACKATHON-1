/**
 * POST /api/auth/signup - User registration endpoint
 *
 * Allows public signup with email, password, and optional background information.
 * Returns JWT token on success (HTTP 201).
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
const MIN_PASSWORD_LENGTH = 6;
const MAX_NAME_LENGTH = 255;

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

function hashPassword(password) {
  const salt = bcrypt.genSaltSync(10);
  return bcrypt.hashSync(password, salt);
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

function validatePassword(password) {
  if (!password || password.length < MIN_PASSWORD_LENGTH) {
    return `Password must be at least ${MIN_PASSWORD_LENGTH} characters`;
  }

  if (!/[a-zA-Z]/.test(password)) {
    return 'Password must contain at least 1 letter';
  }

  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least 1 number';
  }

  return '';
}

function validateRequest(body) {
  const email = (body.email || '').trim();
  const password = (body.password || '').trim();
  const fullName = (body.full_name || '').trim();

  if (!email) {
    return 'Email is required';
  }
  if (!validateEmail(email)) {
    return 'Invalid email format';
  }

  if (!password) {
    return 'Password is required';
  }
  const pwdError = validatePassword(password);
  if (pwdError) {
    return pwdError;
  }

  if (!fullName) {
    return 'Full name is required';
  }
  if (fullName.length > MAX_NAME_LENGTH) {
    return `Full name cannot exceed ${MAX_NAME_LENGTH} characters`;
  }

  return '';
}

async function handleSignupRequest(body) {
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
    const fullName = (body.full_name || '').trim();

    // Optional background fields
    const softwareBackground = (body.software_background || 'beginner').toLowerCase();
    const hardwareBackground = (body.hardware_background || 'none').toLowerCase();
    const rosExperience = (body.ros_experience || 'none').toLowerCase();
    const pythonLevel = (body.python_level || 'beginner').toLowerCase();
    const learningGoal = (body.learning_goal || 'career').toLowerCase();
    const availableHardware = body.available_hardware || '';

    const dbPool = getPool();

    // Check if email already exists
    const existingUserResult = await dbPool.query(
      'SELECT id FROM users WHERE email = $1',
      [email]
    );

    if (existingUserResult.rows.length > 0) {
      return {
        body: JSON.stringify({ detail: 'Email already registered' }),
        status: 409,
        headers: getCorsHeaders(),
      };
    }

    // Hash password
    const passwordHash = hashPassword(password);

    // Create user
    const userResult = await dbPool.query(
      `INSERT INTO users (email, password_hash, full_name, is_active)
       VALUES ($1, $2, $3, true)
       RETURNING id, email`,
      [email, passwordHash, fullName]
    );

    const userId = userResult.rows[0].id;

    // Create user background profile (optional)
    try {
      await dbPool.query(
        `INSERT INTO user_backgrounds
         (user_id, software_background, hardware_background, ros_experience,
          python_level, learning_goal, available_hardware)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [userId, softwareBackground, hardwareBackground, rosExperience, pythonLevel, learningGoal, availableHardware]
      );
    } catch (e) {
      // Log but don't fail - background is optional
      console.warn(`⚠️  Failed to create user background: ${e.message}`);
    }

    // Generate JWT token
    const tokenData = generateJwtToken(userId, email, false);

    // Success response
    const responseData = {
      access_token: tokenData.access_token,
      token_type: tokenData.token_type,
      expires_in: tokenData.expires_in,
      user_id: userId,
      email: email,
    };

    return {
      body: JSON.stringify(responseData),
      status: 201,
      headers: getCorsHeaders(),
    };
  } catch (error) {
    console.error(`❌ Signup error: ${error.message}`);
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
    const result = await handleSignupRequest(req.body);
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
