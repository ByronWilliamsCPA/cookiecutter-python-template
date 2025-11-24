---
title: "{{ cookiecutter.project_name }}"
schema_type: common
status: published
owner: core-maintainer
purpose: "Documentation home page for {{ cookiecutter.project_name }}."
tags:
  - documentation
  - home
---

# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}

## Quick Start

```bash
# Install the package
pip install {{ cookiecutter.pypi_package_name }}

# Or install with development dependencies
uv sync --all-extras
```

{% if cookiecutter.include_cli == "yes" -%}
## CLI Usage

```bash
# Show help
{{ cookiecutter.cli_tool_name }} --help

# Example command
{{ cookiecutter.cli_tool_name }} hello --name "World"
```
{% endif -%}

## Features

- Modern Python {{ cookiecutter.python_version }}+ support
- Type-safe with BasedPyright strict mode
- Comprehensive test coverage
- Structured logging with structlog
{% if cookiecutter.include_cli == "yes" -%}
- CLI interface with Click
{% endif -%}
{% if cookiecutter.include_docker == "yes" -%}
- Docker support
{% endif -%}

## Documentation

- [User Guide](guides/overview.md) - Getting started and usage
- [API Reference](api-reference.md) - Complete API documentation
- [Development](development/architecture.md) - Architecture and contributing
- [Project](project/roadmap.md) - Roadmap and changelog

## License

This project is licensed under the {{ cookiecutter.license }} License - see the [LICENSE](project/license.md) file for details.
