{% if cookiecutter.include_api_framework == "yes" -%}
"""Security middleware for API applications.

This package provides production-ready security middleware implementing
OWASP best practices for web applications.
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
)
from {{ cookiecutter.project_slug }}.middleware.security import (
    RateLimitMiddleware,
    SSRFPreventionMiddleware,
    SecurityHeadersMiddleware,
    add_security_middleware,
)

__all__ = [
    "CORRELATION_ID_HEADER",
    "CorrelationMiddleware",
    "REQUEST_ID_HEADER",
    "RateLimitMiddleware",
    "SPAN_ID_HEADER",
    "SSRFPreventionMiddleware",
    "SecurityHeadersMiddleware",
    "TRACE_ID_HEADER",
    "add_security_middleware",
    "correlation_context_processor",
    "generate_correlation_id",
    "get_correlation_id",
    "get_request_id",
    "get_span_id",
    "get_trace_id",
    "set_correlation_id",
]
{% endif -%}
