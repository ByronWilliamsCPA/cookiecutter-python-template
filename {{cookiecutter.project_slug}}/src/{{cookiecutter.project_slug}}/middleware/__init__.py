{% if cookiecutter.include_api_framework == "yes" -%}
"""Security middleware for API applications.

This package provides production-ready security middleware implementing
OWASP best practices for web applications.
"""

from __future__ import annotations

from {{ cookiecutter.project_slug }}.middleware.security import (
    RateLimitMiddleware,
    SSRFPreventionMiddleware,
    SecurityHeadersMiddleware,
    add_security_middleware,
)

__all__ = [
    "SecurityHeadersMiddleware",
    "RateLimitMiddleware",
    "SSRFPreventionMiddleware",
    "add_security_middleware",
]
{% endif -%}
