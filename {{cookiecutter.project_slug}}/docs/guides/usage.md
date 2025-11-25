---
title: "Usage"
schema_type: common
status: published
owner: core-maintainer
purpose: "Usage guide for {{ cookiecutter.project_name }}."
tags:
  - guide
  - usage
---

This guide covers common usage patterns for {{ cookiecutter.project_name }}.

## Installation

### From PyPI

```bash
pip install {{ cookiecutter.pypi_package_name }}
```

### From Source

```bash
git clone {{ cookiecutter.repo_url }}
cd {{ cookiecutter.project_slug }}
uv sync --all-extras
```

{% if cookiecutter.include_cli == "yes" -%}
## Command Line Interface

### Available Commands

```bash
# Show help
{{ cookiecutter.cli_tool_name }} --help

# Hello command
{{ cookiecutter.cli_tool_name }} hello --name "World"

# Show configuration
{{ cookiecutter.cli_tool_name }} config
```

### Debug Mode

Enable debug logging:

```bash
{{ cookiecutter.cli_tool_name }} --debug hello --name "Test"
```
{% endif -%}

## Library Usage

### Basic Import

```python
from {{ cookiecutter.project_slug }} import __version__

print(f"Version: {__version__}")
```

### Logging

```python
from {{ cookiecutter.project_slug }}.utils.logging import get_logger, setup_logging

# Setup logging
setup_logging(level="DEBUG", json_logs=False)

# Get a logger
logger = get_logger(__name__)
logger.info("Hello from {{ cookiecutter.project_name }}")
```
