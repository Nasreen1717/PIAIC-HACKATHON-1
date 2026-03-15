"""
Middleware for request/response logging, timing, and error handling.

**T030**: Add response timing middleware to track latency and log performance metrics.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Track request/response timing and log performance metrics.

    Logs:
    - Request method, path, status code
    - Response time (total, percentile)
    - Payload sizes
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and track timing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response with timing headers
        """
        start_time = time.time()
        request_body_size = 0

        try:
            # Estimate request body size
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    request_body_size = int(request.headers.get("content-length", 0))
                except ValueError:
                    request_body_size = 0

            # Call next middleware/route
            response = await call_next(request)

        except Exception as e:
            # Log error and re-raise
            elapsed = (time.time() - start_time) * 1000
            logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)} (elapsed: {elapsed:.1f}ms)"
            )
            raise

        # Calculate timing
        elapsed = (time.time() - start_time) * 1000

        # Get response size from content-length header if available
        response_size = 0
        if "content-length" in response.headers:
            try:
                response_size = int(response.headers["content-length"])
            except ValueError:
                response_size = 0

        # Log performance metrics
        log_level = "warning" if elapsed > 2000 else "info" if elapsed > 1000 else "debug"
        logger.log(
            getattr(logging, log_level.upper()),
            f"{request.method} {request.url.path} - {response.status_code} "
            f"(latency: {elapsed:.1f}ms, req_size: {request_body_size}B, res_size: {response_size}B)",
        )

        # Add timing header to response
        response.headers["X-Response-Time-Ms"] = f"{elapsed:.1f}"

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Centralized error handling middleware.

    Catches unhandled exceptions and returns appropriate error responses.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with centralized error handling."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            # FastAPI's global exception handlers will catch this
            raise
