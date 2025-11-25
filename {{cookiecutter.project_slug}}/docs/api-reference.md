---
title: "API Reference"
schema_type: common
status: published
owner: core-maintainer
purpose: "API documentation for {{ cookiecutter.project_name }}."
tags:
  - api
  - reference
---

Complete API documentation for {{ cookiecutter.project_name }}.

## Core Module

::: {{ cookiecutter.project_slug }}.core.config
    options:
      show_root_heading: true
      members_order: source

## Utils Module

### Logging

::: {{ cookiecutter.project_slug }}.utils.logging
    options:
      show_root_heading: true
      members_order: source

{% if cookiecutter.use_decimal_precision == "yes" -%}
### Financial

::: {{ cookiecutter.project_slug }}.utils.financial
    options:
      show_root_heading: true
      members_order: source
{% endif -%}

{% if cookiecutter.include_cli == "yes" -%}
## CLI Module

::: {{ cookiecutter.project_slug }}.cli
    options:
      show_root_heading: true
      members_order: source
{% endif -%}
