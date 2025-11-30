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
    # Exceptions (sorted alphabetically)
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "BusinessLogicError",
    "ConfigurationError",
    "DatabaseError",
    "ExternalServiceError",
{% if cookiecutter.use_decimal_precision == "yes" -%}
    "FinancialCalculationError",
{% endif -%}
    "ProjectBaseError",
    "ResourceNotFoundError",
    # Configuration
    "Settings",
    "ValidationError",
]
