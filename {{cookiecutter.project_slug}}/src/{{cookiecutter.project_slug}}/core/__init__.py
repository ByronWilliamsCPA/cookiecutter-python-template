"""Core configuration, settings, and exception modules."""

from {{ cookiecutter.project_slug }}.core.config import Settings
from {{ cookiecutter.project_slug }}.core.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    ExternalServiceError,
{% if cookiecutter.use_decimal_precision == "yes" -%}
    FinancialCalculationError,
{% endif -%}
    ProjectBaseError,
    ResourceNotFoundError,
    ValidationError,
)

__all__ = [
    # Configuration
    "Settings",
    # Exceptions
    "ProjectBaseError",
    "ConfigurationError",
    "ValidationError",
    "ResourceNotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ExternalServiceError",
    "APIError",
    "DatabaseError",
    "BusinessLogicError",
{% if cookiecutter.use_decimal_precision == "yes" -%}
    "FinancialCalculationError",
{% endif -%}
]
