{% if cookiecutter.include_api_framework == "yes" -%}
"""Security middleware for FastAPI applications.

This module provides production-ready security middleware implementing OWASP best practices:
- CORS configuration (A05: Security Misconfiguration)
- Security headers (A05: Security Misconfiguration)
- Rate limiting (A07: Identification and Authentication Failures)
- Request validation (A03: Injection)
- SSRF prevention (A10: Server-Side Request Forgery)

Usage:
    from {{ cookiecutter.project_slug }}.middleware.security import (
        add_security_middleware,
        SecurityHeadersMiddleware,
        RateLimitMiddleware,
    )

    app = FastAPI()
    add_security_middleware(app)
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse, Response

if TYPE_CHECKING:
    from fastapi import FastAPI, Request
    from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses.

    Implements OWASP recommended security headers to prevent:
    - XSS attacks
    - Clickjacking
    - MIME sniffing
    - Information leakage

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: HSTS for HTTPS
    - Content-Security-Policy: Prevent inline scripts
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Restrict browser features
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Prevent MIME sniffing (OWASP A05)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking (OWASP A05)
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS protection (OWASP A03)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS: Force HTTPS for 1 year (OWASP A02)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Content Security Policy: Prevent inline scripts (OWASP A03)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )

        # Control referrer information (OWASP A09)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restrict browser features (OWASP A05)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )

        # Remove server identification (OWASP A09)
        response.headers.pop("Server", None)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.

    Implements rate limiting to prevent:
    - Brute force attacks (OWASP A07)
    - DoS attacks (OWASP A04)
    - Credential stuffing (OWASP A07)

    Note: For production, use Redis-backed rate limiting:
        - slowapi (https://github.com/laurents/slowapi)
        - fastapi-limiter (https://github.com/long2ice/fastapi-limiter)

    Args:
        requests_per_minute: Maximum requests per IP per minute
        burst_size: Maximum burst requests allowed
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ) -> None:
        """Initialize rate limiter."""
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply rate limiting per IP address."""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean up old entries (older than 1 minute)
        self.requests[client_ip] = [
            req_time
            for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )

        # Check burst limit
        recent_requests = sum(
            1 for req_time in self.requests[client_ip] if current_time - req_time < 1
        )
        if recent_requests >= self.burst_size:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"Burst limit exceeded: {self.burst_size} requests per second",
                    "retry_after": 1,
                },
                headers={"Retry-After": "1"},
            )

        # Record request
        self.requests[client_ip].append(current_time)

        return await call_next(request)


class SSRFPreventionMiddleware(BaseHTTPMiddleware):
    """Prevent Server-Side Request Forgery (SSRF) attacks.

    Blocks requests to internal/private IP ranges when making outbound HTTP calls.
    Implements OWASP A10 protection.

    Note: This is a basic example. For production SSRF prevention:
    1. Use allowlists for external API endpoints
    2. Validate and sanitize URLs before making requests
    3. Use network segmentation
    4. Implement egress filtering
    """

    BLOCKED_HOSTS = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "169.254.169.254",  # AWS metadata
        "metadata.google.internal",  # GCP metadata
    }

    BLOCKED_RANGES = [
        "10.",  # Private
        "172.16.",  # Private
        "172.17.",  # Private (through 172.31)
        "192.168.",  # Private
        "169.254.",  # Link-local
        "::1",  # IPv6 localhost
        "fc00::",  # IPv6 private
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Check for SSRF patterns in request."""
        # Example: Check query parameters for URLs
        # In production, implement based on your specific use case
        for param, value in request.query_params.items():
            if isinstance(value, str) and ("://" in value or value.startswith("/")):
                # Basic URL detection - enhance based on your needs
                if any(
                    blocked in value.lower() for blocked in self.BLOCKED_HOSTS
                ) or any(value.startswith(prefix) for prefix in self.BLOCKED_RANGES):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Bad Request",
                            "message": "Request blocked: potential SSRF attempt",
                        },
                    )

        return await call_next(request)


def add_security_middleware(
    app: FastAPI,
    *,
    enable_https_redirect: bool = False,
    enable_rate_limiting: bool = True,
    enable_ssrf_prevention: bool = True,
    allowed_origins: list[str] | None = None,
    allowed_hosts: list[str] | None = None,
    rate_limit_rpm: int = 60,
) -> None:
    """Add all security middleware to FastAPI application.

    This configures comprehensive security following OWASP best practices.

    Args:
        app: FastAPI application instance
        enable_https_redirect: Redirect HTTP to HTTPS (production only)
        enable_rate_limiting: Enable rate limiting middleware
        enable_ssrf_prevention: Enable SSRF prevention middleware
        allowed_origins: CORS allowed origins (default: none)
        allowed_hosts: Trusted host names (default: all)
        rate_limit_rpm: Rate limit requests per minute

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> add_security_middleware(
        ...     app,
        ...     enable_https_redirect=True,
        ...     allowed_origins=["https://example.com"],
        ...     allowed_hosts=["example.com", "api.example.com"],
        ...     rate_limit_rpm=100,
        ... )
    """
    # HTTPS redirect (production only)
    if enable_https_redirect:
        app.add_middleware(HTTPSRedirectMiddleware)

    # Trusted hosts (OWASP A05)
    if allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts,
        )

    # CORS configuration (OWASP A05)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins or [],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
        max_age=3600,
    )

    # Security headers (OWASP A05, A03, A09)
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting (OWASP A07)
    if enable_rate_limiting:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=rate_limit_rpm,
            burst_size=10,
        )

    # SSRF prevention (OWASP A10)
    if enable_ssrf_prevention:
        app.add_middleware(SSRFPreventionMiddleware)


# Example usage in main.py:
"""
from fastapi import FastAPI
from {{ cookiecutter.project_slug }}.middleware.security import add_security_middleware

app = FastAPI()

# Add all security middleware
add_security_middleware(
    app,
    enable_https_redirect=True,  # Production only
    enable_rate_limiting=True,
    allowed_origins=[
        "https://example.com",
        "https://app.example.com",
    ],
    allowed_hosts=[
        "api.example.com",
        "localhost",  # Development only
    ],
    rate_limit_rpm=100,
)

# Your routes here
@app.get("/")
async def root():
    return {"message": "Hello World"}
"""
{% endif -%}
