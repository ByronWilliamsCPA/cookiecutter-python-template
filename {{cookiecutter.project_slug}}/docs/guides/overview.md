---
title: "Overview"
schema_type: common
status: published
owner: core-maintainer
purpose: "Overview of {{ cookiecutter.project_name }} features and capabilities."
tags:
  - guide
  - overview
---

{{ cookiecutter.project_short_description }}

## Key Features

### Modern Python Development

- **Python {{ cookiecutter.python_version }}+** with full type annotations
- **UV** for fast dependency management
- **Ruff** for linting and formatting
- **BasedPyright** for strict type checking

### Quality Assurance

- **pytest** with comprehensive coverage
- **Pre-commit hooks** for automated checks
- **GitHub Actions** CI/CD pipeline

{% if cookiecutter.include_cli == "yes" -%}
### Command Line Interface

Built with Click for a robust CLI experience:

```bash
{{ cookiecutter.cli_tool_name }} --help
```
{% endif -%}

## Getting Started

1. **Installation**: See the [Configuration Guide](configuration.md)
2. **Usage**: Check the [Usage Guide](usage.md)
3. **API**: Browse the [API Reference](../api-reference.md)

## Architecture

For details on the project architecture, see [Architecture](../development/architecture.md).
