# Template Testing Guide

Comprehensive guide for testing the cookiecutter-python-template.

## Overview

This template includes a robust testing infrastructure to validate:
- Template generation across various configurations
- Generated project quality and correctness
- Integration with quality tools (QLTY, SonarCloud, etc.)
- CI/CD workflows in generated projects

## Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run all tests
uv run pytest -v

# Run specific test categories
uv run pytest tests/test_hooks.py -v                    # Hook tests
uv run pytest tests/test_generation.py -v               # Generation tests
uv run pytest tests/integration/ -v -m integration      # Integration tests
uv run pytest tests/quality_tools/ -v                   # Quality tool tests

# Run tests with coverage
uv run pytest --cov=hooks --cov-report=html --cov-report=term-missing
```

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and utilities
├── test_hooks.py                    # Hook file unit tests
├── test_generation.py               # Template generation tests
├── test_generated_content.py        # Generated file content validation
├── fixtures/
│   └── configs/                     # Test configuration files
│       ├── minimal.json
│       ├── cli-app.json
│       ├── api-service.json
│       ├── ml-project.json
│       └── full-featured.json
├── integration/
│   ├── test_ci_workflows.py         # CI/CD integration tests
│   └── conftest.py
└── quality_tools/
    ├── test_qlty.py                 # QLTY integration tests
    ├── test_sonarcloud.py           # SonarCloud integration tests
    └── conftest.py
```

## Test Categories

### 1. Hook Tests (`test_hooks.py`)

Tests for pre/post generation hook files.

**What's tested:**
- Hook files exist and have valid Python syntax
- Hooks can be imported without errors
- Hooks pass code quality checks (ruff, black, mypy)

**Run:**
```bash
uv run pytest tests/test_hooks.py -v
```

### 2. Generation Tests (`test_generation.py`)

Tests for template generation with various configurations.

**What's tested:**
- Generation succeeds with different configs
- Invalid inputs are handled gracefully
- Feature combinations generate correctly

**Run:**
```bash
# Test all configurations
uv run pytest tests/test_generation.py -v

# Test specific configuration
uv run pytest tests/test_generation.py -k "cli_generation" -v
```

### 3. Content Validation Tests (`test_generated_content.py`)

Tests for validating generated file contents.

**What's tested:**
- No unreplaced Jinja2 variables (`{{ }}`)
- No hardcoded template author info
- Correct file structure and content
- License files generated correctly
- Python version configured correctly

**Run:**
```bash
uv run pytest tests/test_generated_content.py -v
```

### 4. Integration Tests (`integration/`)

Tests that run CI/CD checks on generated projects.

**What's tested:**
- Pre-commit hooks pass
- Ruff linting passes
- Type checking passes
- Tests run successfully
- Package builds correctly
- CLI entrypoints work

**Run:**
```bash
# Run all integration tests (slow)
uv run pytest tests/integration/ -v -m integration

# Run specific integration tests
uv run pytest tests/integration/test_ci_workflows.py::TestGeneratedProjectCI -v
```

### 5. Quality Tool Tests (`quality_tools/`)

Tests for quality tool integrations.

**What's tested:**
- QLTY configuration and execution
- SonarCloud configuration
- CodeRabbit configuration

**Run:**
```bash
uv run pytest tests/quality_tools/ -v
```

## Test Fixtures and Configurations

### Predefined Test Configurations

Located in `tests/fixtures/configs/`:

**minimal.json** - Bare minimum project:
- No optional features
- Basic Python package structure
- Suitable for libraries

**cli-app.json** - CLI application:
- CLI framework (Typer/Click)
- Nox for task automation
- Pre-commit hooks

**api-service.json** - API service:
- API framework (FastAPI/Flask)
- Database (SQLAlchemy)
- Health checks
- CodeCov integration

**ml-project.json** - ML/data science project:
- ML dependencies (NumPy, Pandas, etc.)
- Docker support
- Nox for experiments
- CodeCov integration

**full-featured.json** - All features enabled:
- CLI + API + ML dependencies
- Docker + Nox
- Full CI/CD (SonarCloud, semantic-release, mutation testing)
- MkDocs documentation

### Creating Custom Test Configurations

Create a new JSON file in `tests/fixtures/configs/`:

```json
{
  "default_context": {
    "project_name": "My Custom Test",
    "project_slug": "my_custom_test",
    "author_name": "Test Author",
    "author_email": "test@example.com",
    "include_cli": "yes",
    "include_database": "sqlalchemy_migrations",
    ...
  }
}
```

Then test it:

```bash
uv run pytest tests/test_generation.py::TestConfigurationVariations::test_predefined_configs[your-config-name] -v
```

## Validation Scripts

### validate-generated-project.sh

Comprehensive validation of a generated project.

**Usage:**
```bash
./scripts/validate-generated-project.sh <project_directory>
```

**Checks:**
- Directory structure
- Python syntax
- TOML/YAML validity
- No template variables
- No hardcoded values
- Ruff linting
- UV dependency resolution
- Pre-commit hooks
- Test execution

**Example:**
```bash
# Generate a test project
cookiecutter . --no-input --output-dir /tmp/test
cd /tmp/test/my_python_project

# Validate it
/path/to/cookiecutter-python-template/scripts/validate-generated-project.sh .
```

### test-feature-combination.sh

Test a complete feature combination end-to-end.

**Usage:**
```bash
./scripts/test-feature-combination.sh --config <config_name> [--python-version <version>] [--keep]
```

**Options:**
- `--config`: Configuration name (minimal, cli-app, api-service, ml-project, full-featured)
- `--python-version`: Python version to use (default: 3.12)
- `--keep`: Keep generated project after testing (for inspection)

**Example:**
```bash
# Test CLI app configuration
./scripts/test-feature-combination.sh --config cli-app

# Test with specific Python version and keep output
./scripts/test-feature-combination.sh --config ml-project --python-version 3.11 --keep
```

## CI/CD Integration

### GitHub Actions Workflows

#### test-template.yml

Comprehensive testing workflow with multiple jobs:

**Jobs:**
1. **test-hooks** - Test hook files
2. **test-generation** - Test generation with matrix of configs and Python versions
3. **test-integration** - Integration tests for each config
4. **test-quality-tools** - Quality tool integration tests
5. **validate-generated-ci** - Validate generated project CI
6. **test-content** - Content validation tests
7. **test-summary** - Overall test summary

**Matrix Strategy:**
- Python versions: 3.11, 3.12, 3.13
- Configurations: minimal, cli-app, api-service, ml-project, full-featured

**Triggers:**
- Pull requests to main
- Pushes to main
- Manual workflow dispatch

#### validate-template.yml (Legacy)

Basic validation workflow (still useful for quick checks):
- Validates hook files
- Tests basic generation
- Checks for hardcoded values

## pytest Markers

Tests are organized with pytest markers:

```python
@pytest.mark.integration  # Integration tests (slower)
@pytest.mark.slow        # Slow tests (>5s)
```

**Usage:**
```bash
# Run only integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"

# Run fast tests only
uv run pytest -m "not slow and not integration"
```

## Adding New Tests

### 1. Adding a Hook Test

```python
# tests/test_hooks.py

class TestMyNewHook:
    """Tests for my new hook functionality."""

    def test_new_hook_validation(self, template_dir: Path) -> None:
        """Test that new hook validates correctly."""
        hook_file = template_dir / "hooks" / "my_new_hook.py"
        assert hook_file.exists()
        # Add validation logic
```

### 2. Adding a Generation Test

```python
# tests/test_generation.py

def test_my_new_feature_generation(
    self, template_dir: Path, temp_dir: Path
) -> None:
    """Test generation with new feature."""
    config = {
        "project_name": "Test",
        "project_slug": "test",
        "my_new_feature": "yes",
    }

    from tests.conftest import generate_project
    project_dir = generate_project(template_dir, temp_dir, config)

    # Assert feature files exist
    assert (project_dir / "feature_file.py").exists()
```

### 3. Adding an Integration Test

```python
# tests/integration/test_ci_workflows.py

@pytest.mark.integration
@pytest.mark.slow
def test_my_integration(
    self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
) -> None:
    """Test my integration."""
    from tests.conftest import generate_project

    project_dir = generate_project(template_dir, temp_dir, minimal_config)

    # Run integration checks
    result = subprocess.run(
        ["my_tool", "check"],
        cwd=project_dir,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
```

### 4. Adding a Quality Tool Test

```python
# tests/quality_tools/test_my_tool.py

@pytest.mark.integration
class TestMyToolIntegration:
    """Tests for MyTool integration."""

    def test_mytool_config_exists(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify MyTool config is generated."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_mytool": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        assert (project_dir / ".mytool.yml").exists()
```

## Troubleshooting

### Test Failures

**Symptom:** Tests fail with "cookiecutter not found"

**Solution:**
```bash
pip install cookiecutter
# or
uv tool install cookiecutter
```

**Symptom:** Integration tests timeout

**Solution:**
- Skip slow tests: `pytest -m "not slow"`
- Or increase timeout: `pytest --timeout=300`

**Symptom:** Generated project has unreplaced template variables

**Solution:**
- Check your config has all required variables
- Verify Jinja2 syntax in template files
- Check for conditional blocks that might be missing values

### Performance Optimization

**Speed up test execution:**

```bash
# Use pytest-xdist for parallel execution
pip install pytest-xdist
uv run pytest -n auto

# Run only fast tests
uv run pytest -m "not slow"

# Run specific test categories
uv run pytest tests/test_hooks.py tests/test_generation.py
```

## Coverage

Target: 80%+ coverage for `hooks/` directory

**Generate coverage report:**
```bash
uv run pytest --cov=hooks --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

**Check coverage threshold:**
```bash
uv run pytest --cov=hooks --cov-fail-under=80
```

## Best Practices

### Writing Tests

1. **Use descriptive names:** `test_cli_entrypoint_exists` not `test_1`
2. **One assertion per test:** Makes failures easier to diagnose
3. **Use fixtures:** Reuse common setup logic
4. **Mark slow tests:** Use `@pytest.mark.slow` for tests >5s
5. **Clean up resources:** Use fixtures with yield for cleanup
6. **Test both positive and negative cases:** Success and failure scenarios

### Test Organization

1. **Group related tests:** Use test classes
2. **Use markers:** Organize by speed/type
3. **Separate unit and integration:** Different directories
4. **Parametrize similar tests:** Use `@pytest.mark.parametrize`

### Configuration Management

1. **Use fixtures for configs:** Reusable and maintainable
2. **Store complex configs in JSON files:** Easy to share and version
3. **Document config purposes:** Add comments explaining feature combinations
4. **Test edge cases:** Empty values, invalid combinations

## Reference

### Pytest Documentation
- https://docs.pytest.org/

### Cookiecutter Testing
- https://cookiecutter.readthedocs.io/en/latest/advanced/testing.html

### Related Files
- `pyproject.toml` - pytest configuration
- `tests/conftest.py` - Shared fixtures
- `.github/workflows/test-template.yml` - CI workflow
- `tmp_cleanup/.tmp-template-testing-strategy-20251124.md` - Detailed strategy

## Support

For issues or questions:
1. Check this documentation
2. Review existing tests for examples
3. Check CI logs for failure patterns
4. Open an issue with test output and configuration

---

**Last Updated:** 2025-11-24
**Maintainer:** Template Team
