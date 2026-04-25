# Contributing

Thank you for your interest in contributing to cookiecutter-python-template.

## Before You Start

- Check [open issues](https://github.com/ByronWilliamsCPA/cookiecutter-python-template/issues)
  to avoid duplicating work.
- For significant changes, open an issue first to discuss the approach.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/ByronWilliamsCPA/cookiecutter-python-template.git
cd cookiecutter-python-template

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install --install-hooks
```

## Branching Strategy

| Type | Prefix | Example |
|------|--------|---------|
| New feature | `feat/` | `feat/add-fastapi-support` |
| Bug fix | `fix/` | `fix/post-gen-hook-error` |
| Documentation | `docs/` | `docs/update-readme` |
| Refactor | `refactor/` | `refactor/split-hook-helpers` |
| CI/CD | `ci/` | `ci/add-python-3-14` |
| Chore | `chore/` | `chore/update-dependencies` |

- Never commit directly to `main` or `develop`.
- Branch names use hyphens, lowercase, no underscores.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

<optional body: wrap at 72 characters>

<optional footer>
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `ci`, `chore`, `style`, `perf`

**Scopes for this repo**: `template`, `hooks`, `config`, `docs`, `ci`, `tests`

Examples:

```
feat(template): add pytest-randomly to generated project dependencies
fix(hooks): split cleanup_conditional_files into focused helpers
docs(readme): add cruft update workflow instructions
ci: pin SonarCloud action to SHA hash
```

All commits must be GPG signed. Configure signing:

```bash
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true
```

## Pull Request Process

1. Create a feature branch from `main`.
2. Make your changes and write or update tests as needed.
3. Run the full pre-commit suite:
   ```bash
   pre-commit run --all-files
   ```
4. Run the test suite:
   ```bash
   uv run pytest tests/unit/ -v
   uv run basedpyright hooks/
   ```
5. Test template generation manually:
   ```bash
   cd /tmp
   cruft create /path/to/cookiecutter-python-template --no-input
   cd my_project && uv sync --all-extras
   uv run ruff format --check . && uv run ruff check . && uv run basedpyright src/ && uv run pytest -v
   cd /tmp && rm -rf my_project
   ```
6. Open a pull request with a clear description of the change and why it is needed.
7. Address any feedback from automated reviewers (CodeRabbit, SonarCloud) before
   requesting human review.

## Coding Standards

- **Python**: Ruff (88-char line length), BasedPyright strict mode
- **Type annotations**: Required on all public functions
- **Docstrings**: Google style, required on all public functions
- **Function length**: Under 60 statements preferred; hard limit 100
- **Complexity**: Cyclomatic complexity target 10 or below
- **Tests**: Maintain coverage above 80% for hook files

See `pyproject.toml` for the full tool configuration.

## Template Testing Requirements

Before submitting any change to `{{cookiecutter.project_slug}}/`:

- Test generation with default values (`--no-input`)
- Test generation with CLI enabled
- Test generation with all optional features enabled
- Verify the generated project passes its own quality checks

## Reporting Bugs

Open an issue with:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Template version and Python version
- Relevant error output

## Security Vulnerabilities

Do not open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md).
