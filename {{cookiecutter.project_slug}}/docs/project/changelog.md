---
title: "Changelog"
schema_type: common
status: published
owner: core-maintainer
purpose: "Changelog for {{ cookiecutter.project_name }}."
tags:
  - project
  - changelog
---

All notable changes to {{ cookiecutter.project_name }} will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure from cookiecutter template
- Core configuration with Pydantic Settings
- Structured logging with structlog and rich
{% if cookiecutter.include_cli == "yes" -%}
- CLI interface with Click
{% endif -%}
- Comprehensive test infrastructure
- Documentation with MkDocs Material

### Changed

- None

### Deprecated

- None

### Removed

- None

### Fixed

- None

### Security

- None

## [{{ cookiecutter.version }}] - {{ cookiecutter.copyright_year }}

### Added

- Initial release of {{ cookiecutter.project_name }}

---

[Unreleased]: {{ cookiecutter.repo_url }}/compare/v{{ cookiecutter.version }}...HEAD
[{{ cookiecutter.version }}]: {{ cookiecutter.repo_url }}/releases/tag/v{{ cookiecutter.version }}
