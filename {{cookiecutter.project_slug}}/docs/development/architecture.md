---
title: "Architecture"
schema_type: common
status: published
owner: core-maintainer
purpose: "Architecture documentation for {{ cookiecutter.project_name }}."
tags:
  - development
  - architecture
---

# Architecture

This document describes the architecture and design decisions for {{ cookiecutter.project_name }}.

## Project Structure

```
{{ cookiecutter.project_slug }}/
├── src/
│   └── {{ cookiecutter.project_slug }}/
│       ├── __init__.py          # Package initialization
│       ├── core/                # Core functionality
│       │   ├── config.py        # Configuration with Pydantic
│       │   └── ...
│       ├── utils/               # Utility modules
│       │   ├── logging.py       # Structured logging
│       │   └── ...
{% if cookiecutter.include_cli == "yes" -%}
│       └── cli.py               # CLI entry point
{% endif -%}
├── tests/                       # Test suite
├── docs/                        # Documentation
└── pyproject.toml               # Project configuration
```

## Design Principles

### 1. Type Safety

All code is fully typed with BasedPyright strict mode validation.

### 2. Structured Logging

Uses structlog for structured, JSON-formatted logs in production.

### 3. Configuration Management

Pydantic Settings for type-safe configuration from environment variables.

{% if cookiecutter.include_cli == "yes" -%}
### 4. CLI Design

Click framework for robust command-line interface with subcommands.
{% endif -%}

## Dependencies

See `pyproject.toml` for the complete dependency list.

## Architecture Decision Records

See the [ADRs directory](../ADRs/README.md) for documented architecture decisions.
