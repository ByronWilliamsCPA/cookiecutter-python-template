# CLAUDE.md

Guidance for Claude Code when working with this repository.

> **Context**: Extends global CLAUDE.md from `~/.claude/CLAUDE.md`. Only project-specific configurations below.

## Project Overview

**Name**: {{cookiecutter.project_name}}
**Description**: {{cookiecutter.project_short_description}}
**Author**: {{cookiecutter.author_name}} <{{cookiecutter.author_email}}>
**Repository**: {{cookiecutter.repo_url}}

## Core Principles

1. **Security First**: Validate keys, encrypt secrets, scan dependencies before commits
2. **Code Quality**: Maintain {{cookiecutter.code_coverage_target}}% test coverage, pass all linters
3. **Documentation**: Keep docs current, use clear docstrings
4. **Testing**: High coverage, comprehensive test suites

## Development Workflow

### Quick Start
```bash
# Setup
poetry install --with dev
poetry run pre-commit install

# Development cycle
poetry run pytest -v              # Run tests
poetry run ruff format .          # Format code
poetry run ruff check . --fix     # Lint and fix
poetry run mypy src/              # Type check
```

### Before Commit (MANDATORY)
```bash
# All must pass:
poetry run pytest --cov=src --cov-fail-under={{cookiecutter.code_coverage_target}}
poetry run ruff check .
poetry run mypy src/
poetry run bandit -r src
pre-commit run --all-files        # Or: git commit (runs automatically)
```

## Code Standards

### Naming Conventions
- **Modules/Functions**: `snake_case` (e.g., `data_loader`, `process_file`)
- **Classes**: `PascalCase` (e.g., `DataProcessor`, `ModelConfig`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_PORT`)
- **Files**: `snake_case.py`, test files: `test_*.py`
- **Branches**: `feature/description`, `fix/description`, `docs/description`

### Docstrings (Google Style)
```python
def process_data(input_path: str, max_rows: int = 1000) -> dict[str, Any]:
    """Process data from input file.

    Args:
        input_path: Path to input file
        max_rows: Maximum rows to process (default: 1000)

    Returns:
        Dictionary with processing results

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file format is invalid
    """
```

## Project Structure

```
src/{{cookiecutter.project_slug}}/
├── __init__.py              # Package initialization
{% if cookiecutter.include_cli == "yes" -%}
├── cli.py                   # CLI entry point
{% endif -%}
├── core/                    # Core business logic
│   ├── __init__.py
│   └── config.py           # Configuration
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── logging.py
{% if cookiecutter.use_decimal_precision == "yes" -%}
│   └── financial.py        # Financial utilities (Decimal precision)
{% endif -%}
└── schemas.py              # Pydantic models

tests/
├── unit/                   # Unit tests
├── integration/            # Integration tests
└── conftest.py            # Pytest fixtures
```

## Testing Guidelines

### Coverage Requirements
- **Minimum Coverage**: {{cookiecutter.code_coverage_target}}%
- **Focus**: Core logic, edge cases, error paths
- **Exclude**: CLI entry points, simple getters/setters

### Test Structure
```python
def test_function_name_should_expected_behavior():
    """Test that function_name produces expected_behavior."""
    # Arrange
    input_data = ...

    # Act
    result = function_name(input_data)

    # Assert
    assert result == expected_value
```

## Security Requirements

### Pre-Commit Security Checks
```bash
poetry run bandit -r src         # Python security analysis
poetry run safety check          # Dependency vulnerabilities
{% if cookiecutter.include_gitleaks == "yes" -%}
gitleaks detect --no-git        # Secrets detection
{% endif -%}
```

### Key Management
- **Never commit**: API keys, passwords, tokens, certificates
- **Use**: `.env` files (in `.gitignore`) with `python-dotenv`
- **Example**:
  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      api_key: str

      class Config:
          env_file = ".env"
  ```

{% if cookiecutter.use_decimal_precision == "yes" -%}
## Financial Calculations (CRITICAL)

**Always use `Decimal` for money** - never use `float`:

```python
from decimal import Decimal

# CORRECT
price = Decimal('19.99')
quantity = Decimal('3')
total = price * quantity  # Decimal('59.97')

# WRONG - floating point errors
price = 19.99  # float
total = price * 3  # 59.97000000000001
```

See `src/{{cookiecutter.project_slug}}/utils/financial.py` for utilities.
{% endif -%}

## Git Workflow

### Commit Messages (Conventional Commits)
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
- `feat(api): add user authentication endpoint`
- `fix(parser): handle empty input files correctly`
- `docs(readme): update installation instructions`

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch (if using)
- `feature/*`: New features
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

## CI/CD Pipeline

### GitHub Actions Workflows
{% if cookiecutter.include_github_actions == "yes" -%}
1. **CI** (`.github/workflows/ci.yml`): Testing, linting, type checking
2. **Security** (`.github/workflows/security-analysis.yml`): CodeQL, Bandit, Safety, OSV
{% if cookiecutter.use_mkdocs == "yes" -%}
3. **Docs** (`.github/workflows/docs.yml`): Build and deploy documentation
{% endif -%}
4. **Publish** (`.github/workflows/publish-pypi.yml`): PyPI release automation
{% endif -%}

### Quality Gates (Must Pass)
- ✅ All tests pass ({{cookiecutter.code_coverage_target}}% coverage)
- ✅ Ruff linting (no errors)
- ✅ MyPy type checking (src/ only)
- ✅ Security scans (no high/critical issues)
- ✅ Pre-commit hooks pass

## Configuration Management

Use Pydantic Settings for environment-based config:

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    project_name: str = "{{cookiecutter.project_name}}"
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## Common Tasks

### Add New Dependency
```bash
poetry add package-name              # Production dependency
poetry add --group dev package-name  # Development dependency
```

### Update Dependencies
```bash
poetry update                        # Update all
poetry update package-name           # Update specific package
```

### Run Tests with Coverage
```bash
poetry run pytest -v --cov=src --cov-report=html
open htmlcov/index.html              # View coverage report
```

{% if cookiecutter.use_mkdocs == "yes" -%}
### Build Documentation
```bash
poetry run mkdocs serve              # Local preview
poetry run mkdocs build              # Build static site
```
{% endif -%}

## Troubleshooting

### Pre-commit Hooks Failing
```bash
pre-commit run --all-files           # Run all hooks manually
pre-commit clean                     # Clean cache
pre-commit install --install-hooks   # Reinstall hooks
```

### Poetry Lock Issues
```bash
poetry lock --no-update              # Regenerate lock file
poetry install                       # Reinstall dependencies
```

### MyPy Type Errors
```bash
poetry run mypy src/ --show-error-codes  # See error codes
# Add `# type: ignore[error-code]` for specific issues
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Test Suite | <30s | Full suite with coverage |
| CI Pipeline | <5min | All checks |
| Code Coverage | {{cookiecutter.code_coverage_target}}% | Enforced in CI |

*Update with project-specific targets as needed*

## Additional Resources

- **Poetry Docs**: https://python-poetry.org/docs/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Ruff Docs**: https://docs.astral.sh/ruff/
- **Conventional Commits**: https://www.conventionalcommits.org/
{% if cookiecutter.use_mkdocs == "yes" -%}
- **MkDocs Material**: https://squidfunk.github.io/mkdocs-material/
{% endif -%}

---

**Last Updated**: {% now 'utc', '%Y-%m-%d' %}
**Template Version**: {{cookiecutter.version}}
