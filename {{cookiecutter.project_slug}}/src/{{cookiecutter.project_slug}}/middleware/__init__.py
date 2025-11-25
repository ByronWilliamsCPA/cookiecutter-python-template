{% if cookiecutter.include_api_framework == "yes" -%}
"""Middleware for API applications.

This package provides production-ready middleware implementing:
- OWASP security best practices
- Request correlation for distributed tracing
- Rate limiting and SSRF prevention
"""

from __future__ import annotations

from {{ cookiecutter.project_slug }}.middleware.correlation import (
    CORRELATION_ID_HEADER,
    REQUEST_ID_HEADER,
    SPAN_ID_HEADER,
    TRACE_ID_HEADER,
    CorrelationMiddleware,
    correlation_context_processor,
    generate_correlation_id,
    get_correlation_id,
    get_request_id,
    get_span_id,
    get_trace_id,
    set_correlation_id,
{% if cookiecutter.include_sentry == "yes" -%}
    configure_sentry_correlation,
{% endif -%}
)
from {{ cookiecutter.project_slug }}.middleware.security import (
    RateLimitMiddleware,
    SSRFPreventionMiddleware,
    SecurityHeadersMiddleware,
    add_security_middleware,
)

__all__ = [
    # Security Middleware
    "SecurityHeadersMiddleware",
    "RateLimitMiddleware",
    "SSRFPreventionMiddleware",
    "add_security_middleware",
    # Correlation Middleware
    "CorrelationMiddleware",
    "correlation_context_processor",
    "get_correlation_id",
    "get_request_id",
    "get_trace_id",
    "get_span_id",
    "set_correlation_id",
    "generate_correlation_id",
    "CORRELATION_ID_HEADER",
    "REQUEST_ID_HEADER",
    "TRACE_ID_HEADER",
    "SPAN_ID_HEADER",
{% if cookiecutter.include_sentry == "yes" -%}
    "configure_sentry_correlation",
{% endif -%}
]
{% endif -%}
