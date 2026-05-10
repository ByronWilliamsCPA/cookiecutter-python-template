# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CI gate aggregator jobs in generated project CI and org-workflow variants; branch protection
  now blocks on a single `CI Gate` check instead of individual job names
- Jinja2 conditionals in `setup_github_protection.py` contexts list; required status checks
  are now generated only for the workflows enabled by feature flags
- OpenSSF baseline files: LICENSE, SECURITY.md, CONTRIBUTING.md, CHANGELOG.md
- `detect-secrets` pre-commit hook with baseline for secret scanning
- `pip-audit` in main CI and pre-commit hooks; replaces `safety`
- `darglint` pre-commit hook for docstring argument validation
- `docs/known-vulnerabilities.md` for tracking unfixed CVEs
- Python 3.14 added to CI version matrices
- `pytest-mock` and `pytest-randomly` added to dev dependencies
- `tests/unit/` directory for unit test organization

### Changed

- Root `pyproject.toml`: line-length 100 to 88; target-version py310 to py312
- Root `pyproject.toml`: replaced `black` and `mypy` with `ruff-format` and `basedpyright`
- Root `pyproject.toml`: added missing Ruff rule groups (BLE, EM, SLF, INP, ISC, PGH,
  RSE, TID, YTT, FA, T10, G)
- Pre-commit: replaced `black` hook with `ruff-format`; `mypy` hook with `basedpyright`
- Pre-commit: interrogate threshold raised from 80% to 85%
- CI workflows: replaced `black` + `mypy` with `ruff format` + `basedpyright`
- CI: coverage threshold changed from 0 to enforced minimum
- SonarCloud quality gate changed from non-blocking to blocking

### Fixed

- `setup_github_protection.py`: hardcoded context names replaced with Jinja2 conditionals
  gated on `include_github_actions` and `use_reuse_licensing`
- ADR template front matter: `schema_type` corrected from `planning` to `adr`;
  `status` corrected from `draft` to `proposed`
- `ci.yml` (template): org-workflow gate unified to env-var injection pattern, matching
  the standalone gate; eliminates inline expression in shell script
- `hooks/post_gen_project.py`: reformatted to satisfy `ruff format` (CI format check)
- Mutable GitHub Actions tags pinned to SHA hashes:
  - `SonarSource/sonarcloud-github-action@master` in `ci.yml`
  - `sonarsource/sonarqube-quality-gate-action@master` in `ci.yml` and `sonarcloud.yml`
  - `astral-sh/setup-uv@v7` in `cruft-update.yml`
- `cleanup_conditional_files()` refactored from 142 lines into four focused helpers
- `print_success_message()` refactored from 160 lines into three focused helpers
- Dockerfile dependency stage now copies `README.md` before `uv sync --frozen`;
  pyproject.toml's `[project] readme` field made `uv sync` fail on every
  `include_docker=yes` build until the file was present in the build context.
  README.md is in its own COPY layer so README edits do not invalidate the
  dependency-resolution cache
- Markdown fences across 11 template files (2 with real CommonMark rendering
  bugs; 9 precautionary upgrades to 4-backtick wrappers for sample-of-markdown
  blocks). Regression coverage in `tests/unit/test_template_markdown.py`
- `ci.yml`: every project tool (ruff, basedpyright, bandit, pip-audit) now
  invoked via `uv run`. Previously the `pip install ...` line that put these
  on PATH was removed without switching the call sites, which would have
  failed on a fresh runner with command-not-found
- `ci.yml`: SonarQube `Quality Gate Status` step now hard-fails (`exit 1`)
  on `FAILED` rather than emitting only a warning
- `hooks/post_gen_project.py`: every `read_text` and `write_text` now passes
  `encoding="utf-8"` (Windows default codec is `cp1252`; non-ASCII content
  in workflow YAML or `.cruft.json` corrupted silently)
- `hooks/post_gen_project.py`: `_install_claude_settings` validates the
  user-supplied repo URL against an allowlist of schemes/shapes and rejects
  values starting with `-` (git argument injection); also resolves the
  install path and refuses to clone outside the user's home directory
- `.pre-commit-config.yaml`: `detect-secrets` pinned to commit SHA
  `68e8b454...` (was floating tag `v1.5.0`)
- `.pre-commit-config.yaml`: `no-em-dash` hook extended to cover shell scripts
  (`.sh`/`.bash` + `shell` type)
- `CLAUDE.md`: Git worktree examples now use `.worktrees/<branch-slug>` per
  the global hard rule (was `../cookiecutter-python-template-worktrees/...`)

## [0.1.0] - 2024-01-01

### Added
- Initial release of cookiecutter-python-template
- Modern Python project template with UV, Ruff, and BasedPyright
- Optional features: CLI (Typer), MkDocs, GitHub Actions CI/CD, Semantic Release,
  Codecov, SonarCloud, Renovate, Docker, React frontend
- Supply chain security with Google Assured OSS and Infisical integration
- ClusterFuzzLite fuzzing support
- CodeRabbit AI code review configuration
- Linear project management integration
- Pre/post generation hooks with input validation
- Comprehensive pre-commit hook configuration for generated projects
- Three-layer CI governance: production risks, LLM debt detection, code quality
- Response-Aware Development (RAD) tagging patterns
- SonarCloud quality gate enforcement
- GPG-signed commits enforced via pre-commit
- REUSE/SPDX licensing compliance
- Mutation testing with mutmut (optional)
- Load testing configuration (optional)
- Background job support (optional)
- Health check endpoints (optional)
- Caching layer support (optional)

[Unreleased]: https://github.com/ByronWilliamsCPA/cookiecutter-python-template/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ByronWilliamsCPA/cookiecutter-python-template/releases/tag/v0.1.0
