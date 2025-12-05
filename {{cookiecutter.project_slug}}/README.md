# {{cookiecutter.project_name}}

## Quality & Security

{%- if cookiecutter.include_github_actions == "yes" %}
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/badge)](https://securityscorecards.dev/viewer/?uri=github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}})
{%- endif %}
{%- if cookiecutter.include_codecov == "yes" %}
[![codecov](https://codecov.io/gh/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/graph/badge.svg)](https://codecov.io/gh/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}})
{%- endif %}
{%- if cookiecutter.include_sonarcloud == "yes" %}
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project={{cookiecutter.github_org_or_user}}_{{cookiecutter.project_slug}}&metric=alert_status)](https://sonarcloud.io/summary/new_code?id={{cookiecutter.github_org_or_user}}_{{cookiecutter.project_slug}})
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project={{cookiecutter.github_org_or_user}}_{{cookiecutter.project_slug}}&metric=security_rating)](https://sonarcloud.io/summary/new_code?id={{cookiecutter.github_org_or_user}}_{{cookiecutter.project_slug}})
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project={{cookiecutter.github_org_or_user}}_{{cookiecutter.project_slug}}&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id={{cookiecutter.github_org_or_user}}_{{cookiecutter.project_slug}})
{%- endif %}
{%- if cookiecutter.use_reuse_licensing == "yes" and cookiecutter.include_github_actions == "yes" %}
[![REUSE Compliance](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/reuse.yml/badge.svg)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/reuse.yml)
{%- endif %}

## CI/CD Status

{%- if cookiecutter.include_github_actions == "yes" %}
[![CI Pipeline](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/ci.yml?query=branch%3Amain)
[![Security Analysis](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/security-analysis.yml/badge.svg?branch=main)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/security-analysis.yml?query=branch%3Amain)
{%- endif %}
{%- if cookiecutter.use_mkdocs == "yes" and cookiecutter.include_github_actions == "yes" %}
[![Documentation](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/docs.yml?query=branch%3Amain)
{%- endif %}
{%- if cookiecutter.include_fuzzing == "yes" %}
[![ClusterFuzzLite](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/cifuzzy.yml/badge.svg?branch=main)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/cifuzzy.yml?query=branch%3Amain)
{%- endif %}
{%- if cookiecutter.include_github_actions == "yes" %}
[![SBOM & Security Scan](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/sbom.yml?query=branch%3Amain)
[![PR Validation](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/pr-validation.yml/badge.svg)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/pr-validation.yml)
{%- endif %}
{%- if cookiecutter.include_semantic_release == "yes" and cookiecutter.include_github_actions == "yes" %}
[![Release](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/release.yml/badge.svg)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/release.yml)
{%- endif %}
{%- if cookiecutter.include_github_actions == "yes" %}
[![PyPI Publish](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/{{cookiecutter.github_org_or_user}}/{{cookiecutter.project_slug}}/actions/workflows/publish-pypi.yml)
{%- endif %}

## Project Info

[![Python {{cookiecutter.python_version}}](https://img.shields.io/badge/python-{{cookiecutter.python_version}}-blue.svg)](https://www.python.org/downloads/)
[![License: {{cookiecutter.license}}](https://img.shields.io/badge/License-{{cookiecutter.license}}-yellow.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/{{ cookiecutter.github_org_or_user }}/.github/blob/main/CODE_OF_CONDUCT.md)

| | |
|---|---|
| **Author** | {{cookiecutter.author_name}} |
| **Created** | __PROJECT_CREATION_DATE__ |
| **Repository** | [{{cookiecutter.github_org_or_user}}/{{cookiecutter.github_repo_name}}]({{cookiecutter.repo_url}}) |

---

## Overview

{{cookiecutter.project_short_description}}

This project provides:
- Core functionality for {{cookiecutter.project_short_description.lower()}}
- Production-ready code with comprehensive testing
- Well-documented API and architecture
- Security-first development practices

## Features

- **High Quality**: {{cookiecutter.code_coverage_target}}%+ test coverage enforced via CI
- **Type Safe**: Full type hints with BasedPyright strict mode
- **Well Documented**: Clear docstrings and comprehensive guides
- **Developer Friendly**: Pre-commit hooks, automated formatting, linting
- **Security First**: Dependency scanning, security analysis, SBOM generation
{%- if cookiecutter.include_cli == "yes" %}
- **CLI Tool**: Command-line interface via {{cookiecutter.cli_tool_name}}
{%- endif %}
{%- if cookiecutter.include_ml_dependencies == "yes" %}
- **ML Ready**: Optional ML dependencies with PyTorch support
{%- endif %}

## Quick Start

### Prerequisites

- Python 3.10+ (tested with {{cookiecutter.python_version}})
- [UV](https://docs.astral.sh/uv/) for dependency management

**Install UV**:

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip/pipx
pip install uv
# or
pipx install uv
```

### Installation

```bash
# Clone repository
git clone {{cookiecutter.repo_url}}.git
cd {{cookiecutter.project_slug}}

# Install dependencies (includes dev tools - REQUIRED for development)
uv sync --all-extras

{%- if cookiecutter.include_ml_dependencies == "yes" %}
# Install with ML dependencies
uv sync --all-extras,ml
{%- endif %}

# Setup pre-commit hooks (required)
uv run pre-commit install
```

### Basic Usage

```python
# Import and use the package
from {{cookiecutter.project_slug}} import YourModule

# Example: Create an instance and use it
module = YourModule()
result = module.process()
print(result)
```

{%- if cookiecutter.include_cli == "yes" %}

### CLI Usage

```bash
# Display help
uv run {{cookiecutter.cli_tool_name}} --help

# Use the CLI tool
uv run {{cookiecutter.cli_tool_name}} command --option value

# Example: Process input file
uv run {{cookiecutter.cli_tool_name}} process input.txt --output result.json
```

{%- endif %}

{%- if cookiecutter.include_frontend == "react" %}

## Frontend Development

The frontend is a React + TypeScript application built with Vite.

### Quick Start

```bash
cd frontend
{{ cookiecutter.frontend_package_manager }} install
{{ cookiecutter.frontend_package_manager }} run dev
```

Frontend runs at http://localhost:3000 with hot reload.

### Available Scripts

| Command | Description |
|---------|-------------|
| `{{ cookiecutter.frontend_package_manager }} run dev` | Start dev server with HMR |
| `{{ cookiecutter.frontend_package_manager }} run build` | Build for production |
| `{{ cookiecutter.frontend_package_manager }} run test` | Run tests in watch mode |
| `{{ cookiecutter.frontend_package_manager }} run lint` | Lint code |
| `{{ cookiecutter.frontend_package_manager }} run typecheck` | Run TypeScript type checking |
| `{{ cookiecutter.frontend_package_manager }} run generate-client` | Generate API client from OpenAPI |

### API Client Generation

Generate a type-safe TypeScript client from the FastAPI OpenAPI schema:

```bash
# Start backend first
uv run uvicorn {{ cookiecutter.project_slug }}.main:app &

# Generate client
cd frontend && {{ cookiecutter.frontend_package_manager }} run generate-client
```

This creates typed API functions in `frontend/src/client/`.

{%- if cookiecutter.include_docker == "yes" %}

### Docker

```bash
# Development (with hot reload)
docker-compose up frontend

# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up frontend
```

{%- endif %}

{%- endif %}

{%- if cookiecutter.include_supply_chain_security == "yes" %}

## Supply Chain Security

This project implements enterprise-grade supply chain security with a multi-tier package index strategy and centralized secrets management.

### Security Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Package Index Priority                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Google Assured OSS (SLSA Level 3) - Third-party packages    │
│  2. Internal Artifact Registry - Organization packages           │
│  3. PyPI (fallback) - Packages not in tier 1 or 2               │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Start

```bash
# Run the setup script
./scripts/setup-supply-chain.sh

# Or manually configure
gcloud auth login
gcloud auth application-default login
pip install keyrings.google-artifactregistry-auth
```

### Package Indexes

| Priority | Index | SLSA Level | Purpose |
|----------|-------|------------|---------|
| 1 | Google Assured OSS | 3 | Verified third-party packages |
| 2 | Internal Registry | 2+ | Organization-maintained packages |
| 3 | PyPI | - | Fallback for remaining packages |

**Why This Matters:**

- **SLSA Level 3**: Build integrity, provenance, and tamper-proof artifacts
- **Supply Chain Protection**: Reduced risk of dependency confusion attacks
- **Compliance**: Meets enterprise security and audit requirements
- **Automatic Fallback**: UV seamlessly falls back when packages aren't available

### Secrets Management with Infisical

Secrets are managed via [Infisical](https://infisical.com/) instead of environment variables or GitHub Secrets.

**Local Development:**

```bash
# Login to Infisical
infisical login

# Initialize project connection
infisical init

# Run commands with secrets injected
infisical run --env=dev -- uv run python main.py

# Or export secrets to local file
infisical export --env=dev > .env.local
```

**CI/CD Integration:**

- GitHub Actions use Infisical's Machine Identity authentication
- Secrets are injected at runtime, never stored in repositories
- Environment mapping: `main` → `prod`, `develop` → `staging`, `*` → `dev`

### SBOM & Attestation

Software Bill of Materials (SBOM) is generated on every release:

```bash
# Generate SBOM locally
uv run cyclonedx-py environment -o sbom.json

# Verify package attestation
pip-audit --require-hashes
```

**Automated via CI:**

- CycloneDX SBOM generated in JSON and XML formats
- Attestation attached to GitHub releases
- Vulnerability scanning with OSV database

### Setup Instructions

1. **Run the setup script** (recommended):

   ```bash
   ./scripts/setup-supply-chain.sh
   ```

2. **Or configure manually**:

   **Google Cloud Authentication:**

   ```bash
   gcloud auth login
   gcloud auth application-default login
   pip install keyrings.google-artifactregistry-auth
   ```

   **Infisical Setup:**

   ```bash
   # Install Infisical CLI
   # macOS
   brew install infisical/get-cli/infisical

   # Linux
   curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash
   sudo apt-get install infisical

   # Connect to project
   infisical login
   infisical init
   ```

3. **Configure CI/CD secrets in Infisical:**

   - `GCP_SA_KEY_BASE64`: Base64-encoded GCP service account key
   - `CODECOV_TOKEN`: Codecov upload token (if using Codecov)
   - `SONAR_TOKEN`: SonarCloud token (if using SonarCloud)

### Required GCP Permissions

| Role | Purpose |
|------|---------|
| `roles/artifactregistry.reader` | Read from Assured OSS and internal registry |
| `roles/artifactregistry.writer` | Publish to internal registry (CI only) |

### Troubleshooting

**Q: Packages not found in Assured OSS?**

- UV automatically falls back to PyPI - no action needed
- Check available packages: [Assured OSS Supported Packages](https://cloud.google.com/assured-open-source-software/docs/supported-packages)

**Q: Authentication errors with Artifact Registry?**

- Run `gcloud auth application-default login` to refresh credentials
- Verify service account has `Artifact Registry Reader` role
- Check keyring is installed: `pip install keyrings.google-artifactregistry-auth`

**Q: Infisical connection issues?**

- Verify `.infisical.json` has correct `workspaceId`
- Check your Infisical organization permissions
- For CI: Ensure `INFISICAL_CLIENT_ID` and `INFISICAL_CLIENT_SECRET` are set

**Q: How to verify supply chain setup?**

```bash
# Test package index access
./scripts/setup-supply-chain.sh  # Re-run to verify all checks pass
```

{%- else %}

## Google Assured OSS Integration

This project can use **Google Assured OSS** as the primary package source for enhanced supply chain security.

### Enabling Supply Chain Security

To enable full supply chain security features, regenerate this project with:
```bash
cruft update
# Select include_supply_chain_security: yes
```

Or manually configure by following the [Google Assured OSS documentation](https://cloud.google.com/assured-open-source-software/docs).
{%- endif %}

## Development

### Setup Development Environment

```bash
# Install all dependencies including dev tools
uv sync --all-extras

# Setup pre-commit hooks
uv run pre-commit install

# Install Qlty CLI for unified code quality checks
curl https://qlty.sh | bash

# Run tests
uv run pytest -v

# Run with coverage
uv run pytest --cov={{cookiecutter.project_slug}} --cov-report=html

# Run all quality checks (using Qlty)
qlty check

# Or use pre-commit
uv run pre-commit run --all-files
```

### Code Quality Standards

All code must meet these requirements:

- **Formatting**: Ruff (88 char limit)
- **Linting**: Ruff with PyStrict-aligned rules (see below)
- **Type Checking**: BasedPyright strict mode
- **Testing**: Pytest with {{cookiecutter.code_coverage_target}}%+ coverage
- **Security**: Bandit + dependency scanning
- **Documentation**: Docstrings on all public APIs

**Unified Quality Tool**: This project uses [Qlty](https://qlty.sh) to consolidate all quality checks into a single fast tool. See [`.qlty/qlty.toml`](.qlty/qlty.toml) for configuration.

### PyStrict-Aligned Ruff Configuration

This project uses **PyStrict-aligned Ruff rules** for stricter code quality enforcement beyond standard Python linting:

| Rule | Category | Purpose |
|------|----------|---------|
| **BLE** | Blind except | Prevent bare `except:` clauses |
| **EM** | Error messages | Enforce descriptive error messages |
| **SLF** | Private access | Prevent access to private members |
| **INP** | Implicit packages | Require explicit `__init__.py` |
| **ISC** | Implicit concatenation | Prevent implicit string concatenation |
| **PGH** | Pygrep hooks | Advanced pattern-based checks |
| **RSE** | Raise statement | Proper exception raising |
| **TID** | Tidy imports | Clean import organization |
| **YTT** | sys.version | Safe version checking |
| **FA** | Future annotations | Modern annotation syntax |
| **T10** | Debugger | No debugger statements in production |
| **G** | Logging format | Safe logging string formatting |

These rules catch bugs that standard linting misses and enforce production-quality code patterns.

### Claude Code Standards

This project includes standardized Claude Code configuration via git subtree:

**Directory Structure**:
```
.claude/
├── claude.md          # Project-specific Claude guidelines
└── standard/          # Standard Claude configuration (git subtree)
    ├── CLAUDE.md      # Universal development standards
    ├── commands/      # Custom slash commands
    ├── skills/        # Reusable skills
    └── agents/        # Specialized agents
```

**Updating Standards**:
```bash
# Pull latest standards from upstream
./scripts/update-claude-standards.sh

# Or manually
git subtree pull --prefix .claude/standard \
    https://github.com/williaby/.claude.git main --squash
```

**What's Included**:
- Universal development best practices
- Response-Aware Development (RAD) system for assumption tagging
- Agent assignment patterns and workflow
- Security requirements and pre-commit standards
- Git workflow and commit conventions

**Project-Specific Overrides**: Edit `.claude/claude.md` for project-specific guidelines. See [`.claude/README.md`](.claude/README.md) for details.

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_module.py -v

# Run with coverage report
uv run pytest --cov={{cookiecutter.project_slug}} --cov-report=term-missing

# Run tests in parallel
uv run pytest -n auto
```

### Quality Checks with Qlty

**Recommended**: Use Qlty CLI for unified code quality checks.

```bash
# Run all quality checks (fast!)
qlty check

# Run checks on only changed files (fastest)
qlty check --filter=diff

# Run specific plugins only
qlty check --plugin ruff --plugin pyright

# Auto-format code
qlty fmt

# View current configuration
qlty config show
```

**Qlty runs all these tools in a single pass:**

**Python Quality:**

- Ruff (linting + formatting)
- BasedPyright (type checking)
- Bandit (security scanning)

**Security & Secrets:**

- Gitleaks (secrets detection)
- TruffleHog (entropy-based secrets detection)
- OSV Scanner (dependency vulnerabilities)
- Semgrep (advanced SAST)

**File & Configuration:**

- Markdownlint (markdown linting)
- Yamllint (YAML linting)
- Prettier (JSON, YAML, Markdown formatting)
- Actionlint (GitHub Actions workflows)
- Shellcheck (shell script linting)

**Container & Infrastructure** (if Docker enabled):

- Hadolint (Dockerfile linting)
- Trivy (container security scanning)
- Checkov (infrastructure as code security)

**Code Quality Metrics:**

- Complexity analysis (cyclomatic, cognitive)
- Code smells detection
- Maintainability scoring

### Individual Tool Commands (if needed)

```bash
# Format code
uv run ruff format src tests

# Lint and auto-fix
uv run ruff check --fix src tests

# Type checking
uv run basedpyright src

# Security scanning
uv run bandit -r src

# Dependency vulnerabilities
qlty check --plugin osv_scanner
```

## Project Structure

```
{{cookiecutter.project_slug}}/
├── src/{{cookiecutter.project_slug}}/     # Main package
│   ├── __init__.py
│   ├── core.py                           # Core functionality
│   └── utils/                            # Utility modules
├── tests/                                # Test suite
│   ├── unit/                             # Unit tests
│   └── integration/                      # Integration tests
├── docs/                                 # Documentation
│   ├── ADRs/                             # Architecture Decision Records
│   ├── planning/                         # Project planning docs
│   └── guides/                           # User guides
├── pyproject.toml                        # Dependencies & tool config
├── README.md                             # This file
├── CONTRIBUTING.md                       # Contribution guidelines
└── LICENSE                               # License
```

## Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to contribute to the project
- **[docs/ADRs/README.md](docs/ADRs/README.md)**: Architecture Decision Records documentation
- **[docs/planning/project-plan-template.md](docs/planning/project-plan-template.md)**: Project planning guide

### Writing Documentation

- Use Markdown for all documentation
- Include code examples for clarity
- Update README.md when adding major features
- Maintain architecture documentation (see [docs/ADRs/](docs/ADRs/))

## Testing

### Testing Policy

All new functionality must include tests:

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Coverage**: Maintain {{cookiecutter.code_coverage_target}}%+ coverage
- **Markers**: Use pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

### Test Guidelines

```bash
# Run all tests
uv run pytest -v

# Run only unit tests
uv run pytest -v -m unit

# Run only integration tests
uv run pytest -v -m integration

# Run with coverage requirements
uv run pytest --cov={{cookiecutter.project_slug}} --cov-fail-under={{cookiecutter.code_coverage_target}}
```

## Security

### Security-First Development

- Validate all inputs
- Use secure defaults
- Scan dependencies regularly
- Report vulnerabilities responsibly

### Reporting Security Issues

Please report security vulnerabilities to {{cookiecutter.author_email}} rather than using the public issue tracker.

See the [{{ cookiecutter.github_org_or_user }} Security Policy](https://github.com/{{ cookiecutter.github_org_or_user }}/.github/blob/main/SECURITY.md) for complete disclosure policy and response timelines.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code quality standards
- Testing requirements
- Git workflow and commit conventions
- Pull request process

### Quick Checklist Before Submitting PR

- [ ] Code follows style guide (Ruff format + lint)
- [ ] All tests pass with {{cookiecutter.code_coverage_target}}%+ coverage
- [ ] BasedPyright type checking passes
- [ ] Docstrings added for new public APIs
- [ ] CHANGELOG.md updated (if significant change)
- [ ] Commits follow conventional commit format

## Versioning

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backwards-compatible functionality additions
- **PATCH** version: Backwards-compatible bug fixes

Current version: **{{cookiecutter.version}}**

### Automated Releases with Semantic Release

This project uses [python-semantic-release](https://python-semantic-release.readthedocs.io/) for automated versioning based on [Conventional Commits](https://www.conventionalcommits.org/).

**How it works:**

1. **Commit messages determine version bumps:**
   - `fix:` commits trigger a **PATCH** release (1.0.0 → 1.0.1)
   - `feat:` commits trigger a **MINOR** release (1.0.0 → 1.1.0)
   - `BREAKING CHANGE:` in commit body or `!` after type triggers **MAJOR** release (1.0.0 → 2.0.0)

2. **On merge to main:**
   - Analyzes commits since last release
   - Determines appropriate version bump
   - Updates version in `pyproject.toml`
   - Generates/updates `CHANGELOG.md`
   - Creates Git tag and GitHub Release
   - Publishes to PyPI (if configured)

**Commit message examples:**

```bash
# Patch release (bug fix)
git commit -m "fix: resolve null pointer in data parser"

# Minor release (new feature)
git commit -m "feat: add CSV export functionality"

# Major release (breaking change)
git commit -m "feat!: redesign API for better ergonomics

BREAKING CHANGE: API has been redesigned for improved usability.
See migration guide in docs/migration/v2.0.0.md"
```

**Configuration:** See `[tool.semantic_release]` in `pyproject.toml` for settings.

## Template Maintenance

This project was generated from a cookiecutter template and is managed with cruft.

### Updating from Template

To sync with the latest template changes:

```bash
# Preview changes first
cruft diff

# Apply updates (recommended: use the wrapper script)
./scripts/cruft-update.sh

# Or use cruft directly (requires manual cleanup)
cruft update
python scripts/cleanup_conditional_files.py
```

### Important: Cruft Update Limitations

**Cruft only syncs file contents** - it does NOT re-run post-generation hooks that clean up conditional files.

When you change feature flags in `.cruft.json` (e.g., disabling `include_api_framework`), the corresponding files are NOT automatically removed. You must run the cleanup script:

```bash
# Check for orphaned files
python scripts/check_orphaned_files.py

# Remove orphaned files
python scripts/cleanup_conditional_files.py

# Or preview what would be removed
python scripts/cleanup_conditional_files.py --dry-run
```

### Conditional Files

Files that may need cleanup when features are disabled:

| Feature | Files to Remove |
|---------|-----------------|
| `include_api_framework: no` | `src/*/api/`, `src/*/middleware/` |
| `include_sentry: no` | `src/*/core/sentry.py` |
| `include_background_jobs: no` | `src/*/jobs/` |
| `include_caching: no` | `src/*/core/cache.py` |
| `include_docker: no` | `Dockerfile`, `docker-compose*.yml` |
| `use_mkdocs: no` | `mkdocs.yml`, `docs/` |

The CI pipeline includes automated checks for orphaned files to prevent this issue.

## License

{{cookiecutter.license}} License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues]({{cookiecutter.repo_url}}/issues)
{%- if cookiecutter.include_github_actions == "yes" %}
- **Discussions**: [GitHub Discussions]({{cookiecutter.repo_url}}/discussions)
{%- endif %}
- **Email**: {{cookiecutter.author_email}}

## Acknowledgments

Thank you to all contributors and the open-source community!

---

**Made with by [{{cookiecutter.author_name}}](https://github.com/{{cookiecutter.github_username}})**
