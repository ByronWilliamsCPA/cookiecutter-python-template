"""Configuration settings for {{ cookiecutter.project_name }}.

Settings are loaded from environment variables with the prefix '{{ cookiecutter.project_slug|upper }}_'.
Pydantic-settings handles the parsing and validation.
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the application, loaded from environment variables.

    Attributes:
        model_config: Pydantic settings configuration (env prefix, casing).
        log_level (Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]):
            The logging level for the application.
        json_logs (bool): Flag to enable or disable JSON formatted logs.
        include_timestamp (bool): Flag to include timestamps in logs.
{%- if cookiecutter.include_database != "none" %}
        database_url (str): Async SQLAlchemy connection URL for the database.
{%- endif %}
    """

    model_config = SettingsConfigDict(
        env_prefix="{{ cookiecutter.project_slug }}_",
        case_sensitive=False,
        extra="ignore",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    json_logs: bool = False
    include_timestamp: bool = True
{%- if cookiecutter.include_database != "none" %}
{%- if cookiecutter.database_dialect == "postgresql" %}
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/{{ cookiecutter.project_slug }}"
    )
{%- elif cookiecutter.database_dialect == "mysql" %}
    database_url: str = (
        "mysql+aiomysql://root:root@localhost:3306/{{ cookiecutter.project_slug }}"
    )
{%- else %}
    database_url: str = "sqlite+aiosqlite:///./{{ cookiecutter.project_slug }}.db"
{%- endif %}
{%- endif %}


# A single, global instance of the settings
settings = Settings()
