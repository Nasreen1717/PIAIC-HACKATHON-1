/**
 * Simple test endpoint to verify Vercel serverless functions are working
 */

module.exports = (req, res) => {
  res.status(200).json({
    message: 'API is working!',
    timestamp: new Date().toISOString(),
    endpoint: '/api/test'
  });
};
