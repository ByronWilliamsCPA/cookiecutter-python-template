# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `qlty.yml` reusable-workflow caller in generated projects'
  `.github/workflows/` (satisfies CI-013 manifest gap); pins upstream
  `python-qlty-coverage.yml` at SHA `1b2d33c4`; runs on CI workflow_run
  completion and only when CI conclusion is `success`; `QLTY_COVERAGE_TOKEN`
  secret documented in generated project's `docs/PROJECT_SETUP.md` with a
  new `### Qlty Code Quality` subsection and a row in the Required GitHub
  Secrets table
- `docs/planning/index.md` in generated projects: navigation index for the
  four `/plan`-generated planning documents (project-vision, tech-spec,
  roadmap, project-plan-template); previously absent and blocked MkDocs nav
- `include_editorconfig` cookiecutter flag (default `yes`): ships a 4-space Python
  baseline `.editorconfig` with 2-space YAML/JSON/TOML overrides, LF line endings,
  UTF-8 encoding, and tab-indented Makefiles
- `community_health_style` cookiecutter flag (default `full`): selects between a
  full Contributor Covenant 2.1 with a templated `GOVERNANCE.md` (full variant) or
  short pointer files that reference the org's `.github` repo (org_pointer variant);
  pointer variant also adds `CODE_OF_CONDUCT.md` and `GOVERNANCE.md` to
  `[tool.cruft] skip` so `cruft update` preserves the pointer
- `sole_contributor` cookiecutter flag (default `yes`): sets
  `required_approving_review_count` to 0 and disables `require_code_owner_reviews`
  in the generated `scripts/setup_github_protection.py` so the GitHub API does not
  reject the configuration with HTTP 422 for solo-maintained projects
- `auto_setup_branch_protection` cookiecutter flag (default `no`): opt-in
  post-generation auto-run of `scripts/setup_github_protection.py`. Fails non-fatally
  with an actionable hint when `GITHUB_TOKEN` is missing, when the generated repo has
  no `origin` remote, or when the script is missing; never echoes the token value
- Cluster C feasibility check, design spec, and implementation plan under
  `docs/superpowers/`
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
- `.github/known-vulnerabilities.md` and `.github/known-vulnerabilities-template.md` for
  generated projects: tracks accepted-risk CVEs; initial entries cover
  PYSEC-2022-42969 (py/interrogate) and PYSEC-2026-89 (markdown) with reassessment
  dates and release-blocking flags; placed in `.github/` so they survive
  `use_mkdocs=no` post-generation cleanup that removes the `docs/` directory
- `APIErrorContext` dataclass in generated project `core/exceptions.py`: groups optional
  `APIError` parameters for ergonomic multi-field construction; `context=` and
  individual keyword arguments are accepted interchangeably; declared `frozen=True`
  to enforce immutability as a value-object parameter container
- `scripts/_cleanup_shared.py` for generated projects: shared `get_cruft_context()`
  helper centralizes `.cruft.json` loading; returns `dict[str, Any]` to correctly
  reflect mixed-type context values; validates that the parsed JSON is a dict and
  raises `ValueError` with an actionable message when `.cruft.json` contains a
  non-object root value

### Removed

- Root-level `sonar-project.properties` and `.github/workflows/sonarcloud.yml`
  caller workflow. SonarCloud analysis is intentionally skipped on this template
  repository: as Jinja2 meta-code, the template body is not statically
  analyzable as Python, and the analysis was failing with a `curl 403` from the
  SonarCloud quality-gate API. Generated child projects continue to opt into
  their own SonarCloud analysis via the rendered config that ships inside the
  template's rendered output directory.

### Changed

- Cruft skip patterns moved from a runtime-written `.cruft.json` (silently overwritten
  by cruft on create) to `[tool.cruft] skip` in the generated `pyproject.toml`, which
  cruft reads at update time and preserves; removed the dead
  `add_cruft_skip_patterns()` post-gen helper and its three unit tests
- `_detect_origin_url()` helper extracted from `main()` in `hooks/post_gen_project.py`
  for single-responsibility and isolated testability
- Root `pyproject.toml`: line-length 100 to 88; target-version py310 to py312
- Root `pyproject.toml`: replaced `black` and `mypy` with `ruff-format` and `basedpyright`
- Root `pyproject.toml`: added missing Ruff rule groups (BLE, EM, SLF, INP, ISC, PGH,
  RSE, TID, YTT, FA, T10, G)
- Pre-commit: replaced `black` hook with `ruff-format`; `mypy` hook with `basedpyright`
- Pre-commit: interrogate threshold raised from 80% to 85%
- CI workflows: replaced `black` + `mypy` with `ruff format` + `basedpyright`
- CI: coverage threshold changed from 0 to enforced minimum
- SonarCloud quality gate changed from non-blocking to blocking
- CI workflows (root repo): added `step-security/harden-runner@v2.19.1` audit-mode steps
  to all 21 jobs with declared `steps:` across `ci.yml`, `cruft-update.yml`,
  `release-drafter.yml`, `scheduled-validation.yml`, `sonarcloud.yml`,
  `test-template.yml`, and `validate-template.yml`
- CI workflows (root repo): added per-job least-privilege `permissions:` blocks where
  missing; `validate-template.yml` previously had no `permissions:` declaration at any level
- Pre-commit (root repo): SHA-pinned all 9 hook `rev:` fields (previously only
  `detect-secrets` was pinned); trailing tag annotations preserved
- Template-tree workflows: added `step-security/harden-runner@v2.19.3` audit-mode
  steps to all 24 `steps:`-bearing jobs across 12 workflows under
  `{{cookiecutter.project_slug}}/.github/workflows/` (`ci.yml`, `codecov.yml`,
  `dependency-review.yml`, `docs.yml`, `fips-compatibility.yml`,
  `mutation-testing.yml`, `python-compatibility.yml`, `release.yml`, `reuse.yml`,
  `scorecard.yml`, `security-analysis.yml`, `validate-cruft.yml`). Pure
  reusable-workflow callers (`container-security.yml`, `publish-pypi.yml`,
  `sbom.yml`, `sonarcloud.yml`) intentionally excluded since they delegate all
  steps to org-level workflows
- Template-tree workflows: added per-job least-privilege `permissions:` blocks to
  all 24 hardened jobs with appropriately scoped grants (`docs.yml` standalone
  uses `contents: write` only since `mkdocs gh-deploy` does not exercise Pages
  API / OIDC; `security-analysis.yml` standalone uses `contents: read` only
  since Bandit/OSV-Scanner write artifacts not SARIF and post no PR comments)
- Template-tree workflows: `python-compatibility.yml` harden-runner gated on
  `runner.os == 'Linux'` so the macOS/Windows matrix legs' silent no-op is
  visible in the workflow rather than implicit
- Template-tree `.pre-commit-config.yaml`: SHA-pinned 6 hook `rev:` fields
  (`pre-commit/pre-commit-hooks` v4.5.0, `PyCQA/bandit` 1.7.10,
  `compilerla/conventional-pre-commit` v3.4.0, `abravalheri/validate-pyproject`
  v0.20.2, `python-jsonschema/check-jsonschema` 0.29.4, `econchick/interrogate`
  1.7.0); all 7 `rev:` fields now SHA-pinned (existing ruff pin preserved)
- Root `pyproject.toml`: added missing `A` (flake8-builtins) and `PT`
  (flake8-pytest-style) rule sets to `[tool.ruff.lint].select`

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
- Template-tree `scorecard.yml` reusable-workflow caller: removed deprecated
  `publish-results: true` input (upstream contract in `ByronWilliamsCPA/.github`
  hardcodes the behavior; passing the input is a no-op). Mirrors root-repo
  fix from PR #58. The standalone branch retains `publish_results: true` on
  `ossf/scorecard-action` directly since that parameter remains valid and
  enables OpenSSF dashboard publishing for projects not using org workflows
- Claude standards repo references redirected from `williaby/.claude` to
  `ByronWilliamsCPA/.claude` across all live code paths: template tree
  (`{{cookiecutter.project_slug}}/README.md`, `{{cookiecutter.project_slug}}/.claude/README.md`,
  `{{cookiecutter.project_slug}}/scripts/README.md`,
  `{{cookiecutter.project_slug}}/scripts/update-claude-standards.sh`),
  generation hooks (`hooks/post_gen_project.py`), and root `README.md`
  install instructions. Generated projects previously cloned and pulled
  standards from the wrong org. Historical handoff doc
  (`docs/handoff-claude-standards-team.md`) preserved as-is for context
- Generated project `core/exceptions.py`: `_attach_optional_details` helper replaces
  repeated `if field: details[field] = field` pattern; `None`-valued fields skipped,
  falsy-but-not-None values (0, False, empty string) preserved
- Generated project `cli.py` and `utils/logging.py`: BasedPyright strict-mode warnings
  resolved via `CLIContext` dataclass, `_get_context` narrowing helper, and cast-based
  typing for structlog processor stubs
- `check_fips_compatibility.py`: cipher detection switched from substring containment to
  exact set membership, eliminating false positives on method names such as `deserialize`,
  `describe`, or `ideal_*`; removed unused `_in_hashlib_call` state field from
  `FipsCodeVisitor`
- `check_orphaned_files.py` and `cleanup_conditional_files.py`: duplicate `.cruft.json`
  loading consolidated into shared `_cleanup_shared.get_cruft_context()` helper

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
