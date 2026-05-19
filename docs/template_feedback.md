---
title: "Template Feedback"
schema_type: common
status: published
owner: core-maintainer
purpose: "Document template issues for upstream fixes."
tags:
  - feedback
  - template
---

> **Purpose**: Document issues discovered in generated projects that should be addressed in the
> [cookiecutter-python-template](https://github.com/ByronWilliamsCPA/cookiecutter-python-template).
>
> **Source**: Accumulated from generated projects (2025-11-22 through 2026-05-08); audited
> 2026-05-09 against the template tree on `feat/wip-stash-review`.

> **Cleanup 2026-05-09:** ~26 entries were removed in PR `fix/template-post-smoke-cleanup`
> after a smoke test confirmed they are FIXED, REDIRECTED to homelab-infra (NTP, RTC,
> OpenClaw retention), or closed by that PR. Remaining entries align to clusters C, D,
> E of the template-cleanup umbrella at
> `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`.
>
> **Cleanup 2026-05-19:** 4 cluster C entries removed in PR `feat/cluster-C-compliance`:
> `.editorconfig` missing, `community_health_style` variable absent (plus the missing
> CODE_OF_CONDUCT.md and GOVERNANCE.md source files), `sole_contributor` variable
> absent, and branch-protection script undocumented. All addressed by the cluster C PR.

---

## Feedback Items

---

## Cluster D: Code Quality of Generated Code

### Transitive Dependency `py` Has Known Vulnerability (via interrogate)

- **Priority**: Low
- **Cluster**: D
- **Date**: 2025-11-22

**Issue**: `safety check` reports CVE-2022-42969 (ReDoS) in `py<=1.11.0` package
pulled in by `interrogate>=1.7.0`.

**Context**:

```text
Vulnerability found in py version 1.11.0
Vulnerability ID: 51457
ADVISORY: ** DISPUTED ** Py throughout 1.11.0 allows remote attackers
to conduct a ReDoS (Regular expression Denial of Service)...
```

`uv pip tree` shows `interrogate v1.7.0 -> py v1.11.0`. The `py` library is unmaintained
with no fix released. pytest removed this dependency in v7.2.0, but interrogate has not.

**Risk Assessment**: CVE is disputed and only affects Subversion repository parsing.
This project does not interact with Subversion. Only affects dev environment.

**Suggested Fix**:

- Option 1: Remove `interrogate` from dev dependencies (docstring coverage is nice-to-have).
- Option 2: Document as accepted risk since CVE does not affect this use case.
- Option 3: Wait for interrogate to release an update removing the `py` dependency.
- Also: Update `safety check` (deprecated) to `safety scan` command.

**References**:

- [pytest issue #10392](https://github.com/pytest-dev/pytest/issues/10392)
- [NVD CVE-2022-42969](https://nvd.nist.gov/vuln/detail/CVE-2022-42969)

### Template Missing Local SonarCloud Scanning Script

- **Priority**: Medium
- **Cluster**: D
- **Date**: 2025-11-22

**Issue**: Template includes SonarCloud CI workflow but no local scanning capability.
Developers should be able to run SonarCloud analysis locally before committing to catch
issues early. Currently have to wait for CI to run after push.

**Suggested Fix**: Add `scripts/sonar_scan.py` to template with:

- Support for running analysis locally.
- Integration with pytest coverage generation.
- Docker fallback for systems without sonar-scanner CLI.
- Clear documentation on prerequisites (`SONAR_TOKEN`).

Add to `PROJECT_SETUP.md` documentation:

- How to install sonar-scanner CLI.
- How to get `SONAR_TOKEN` from `https://sonarcloud.io/account/security`.
- Usage examples: `python scripts/sonar_scan.py --with-coverage`.

**Reference**: <https://docs.sonarsource.com/sonarqube-cloud/advanced-setup/ci-based-analysis/sonarscanner-cli/>

### Template-Generated Code Has BasedPyright Warnings (DETAILED)

- **Priority**: Critical
- **Cluster**: D
- **Date**: 2025-11-22

**Issue**: Running `uv run basedpyright src/` on a freshly generated project shows type
warnings in `cli.py` and `utils/logging.py`. A freshly generated template should pass type
checking cleanly.

**Note**: Warning count may differ from the original 33 reported here; recent commits touched
`logging.py`. Run a fresh `cruft create` to get the current count before fixing.

**Root Causes**:

1. `structlog.get_logger()` returns `Any` because structlog lacks complete type stubs.
2. `ctx.obj` in Click is typed as `Any` in Click's type stubs.
3. Explicit `Any` usage in `logging.py` function signatures.
4. Lambda functions in `logging.py` lack parameter and return type annotations.

**Suggested Fixes**:

- Use `structlog.stdlib.BoundLogger` for logger typing:

  ```python
  logger: BoundLogger = structlog.get_logger()
  ```

- Type the Click context with a TypedDict or dataclass.
- Replace explicit `Any` in `logging.py` with proper types (`Mapping[str, object]`, etc.).
- Add type annotations to lambda functions in `logging.py`.
- As a fallback, add documented `pyright: ignore[reportAny]` comments where structlog
  genuinely cannot be typed without full stubs.

### Template-Generated Scripts Fail Qlty Code Quality Checks

- **Priority**: Medium
- **Cluster**: D
- **Date**: 2025-12-01

**Issue**: Template-generated utility scripts have high complexity, code duplication, and
deeply nested control flow that fails `qlty check`.

**Issues by File**:

`scripts/check_fips_compatibility.py`:

- Function `visit_Call` complexity: 51 (target: <=10)
- Function `check_pyproject_toml` complexity: 14
- Function `main` complexity: 20
- Deeply nested control flow (level 4) at lines 117, 131, 165
- Duplicate code blocks at lines 257 and 280 (16 lines, mass=88)

`scripts/cleanup_conditional_files.py`:

- Function `cleanup_conditional_files` complexity: 106 (extremely high)
- Identical code duplication with `check_orphaned_files.py` (17 lines, mass=80) at line 50

`scripts/check_orphaned_files.py`:

- Identical code duplication with `cleanup_conditional_files.py` (17 lines, mass=80) at line 46

**Recommendations**:

1. Break down functions with complexity >15 into smaller, focused functions.
2. Extract the 17-line duplicate block in scripts into a shared utility function.
3. Refactor deeply nested control flow using early returns and guard clauses.

### Qlty Configuration Has Invalid Plugin Syntax

- **Priority**: High
- **Cluster**: D
- **Date**: 2025-11-22

**Issue**: `.qlty/qlty.toml` uses attributes like `version = "latest"`, `package_file`,
and `config_files` which are not valid qlty configuration options. This causes
"Plugin definition not found" errors on every `qlty check` run.

**Suggested Fix**: Use correct qlty plugin syntax:

```toml
[[plugin]]
name = "ruff"
drivers = ["lint"]
```

Remove custom plugin configuration attributes. Add `mode = "comment"` for tools that
should report but not block CI. Run `qlty init --dry-run` to see correct default
configuration.

---

## Cluster E: Docs Build and MkDocs

### MD040 Violations: Fenced Code Blocks Without Language Specifier

- **Priority**: Medium
- **Cluster**: E
- **Date**: 2025-12-04

**Issue**: Multiple template-generated documentation files have fenced code blocks
without language specifiers, causing markdownlint MD040 violations.

**Files Affected (from template)**:

| File | Line(s) | Content Type |
|------|---------|--------------|
| `docs/development/architecture.md` | 16 | Diagram/text |
| `docs/development/testing.md` | 14 | Command output |
| `docs/planning/project-plan-template.md` | 78, 120 | Generic text |
| `docs/planning/PROJECT-PLAN.md` | 83 | Generic text |
| `docs/planning/README.md` | 44, 55, 74 | Generic text |
| `docs/planning/index.md` | 20 | Generic text |
| `README.md` | 54, 411, 535 | Various |

**Suggested Fix**: Add appropriate language specifiers to all fenced code blocks:

- Use `text` for plain text, diagrams, or command output.
- Use `bash` for shell commands.
- Use `python`, `yaml`, `json` etc. for code.

### MD051 Link Fragment Violations in docs/PROJECT_SETUP.md

- **Priority**: Low
- **Cluster**: E
- **Date**: 2025-12-04

**Issue**: Table of contents links in `docs/PROJECT_SETUP.md` reference invalid heading
fragments.

**Lines**: 15-21

**Suggested Fix**: Verify that anchor links match actual heading IDs after markdown
rendering.

### Documentation Files Missing YAML Front Matter (Planning Subset)

- **Priority**: Medium
- **Cluster**: E
- **Date**: 2025-11-22

**Issue**: Several planning documents generated by the template do not have valid YAML
front matter required by the `validate-front-matter` pre-commit hook and MkDocs rendering.

**Note**: Most docs files now have front matter (confirmed in 2026-05-09 audit). Only the
planning subset below remains outstanding; `docs/planning/index.md` is the most critical
because it blocks MkDocs nav builds.

**Files Remaining Without Front Matter**:

- `docs/planning/index.md` (file absent entirely; needs creation with front matter)
- `docs/planning/project-plan-template.md`
- `docs/planning/tech-spec.md`
- `docs/planning/roadmap.md`

**Required Front Matter for Planning Files**:

```yaml
---
title: "{{cookiecutter.project_name}} - [Document Type]"
schema_type: planning
status: draft
owner: core-maintainer
purpose: "[One sentence describing document purpose]."
tags: [planning, scope]
component: Strategy  # or Context, Development-Tools as appropriate
source: "/plan command generation"
---
```

**Suggested Fix**: Add front matter stubs to each planning template file. For
`docs/planning/index.md`, generate the file itself (it is currently absent from the
template output).

### CI/CD Workflow Documentation Missing Several Workflows

- **Priority**: Medium
- **Cluster**: E
- **Date**: 2025-11-22

**Issue**: `PROJECT_SETUP.md` Core Workflows table is missing several workflows that
exist in `.github/workflows/`.

**Missing from documentation**:

- `pr-validation.yml` - PR validation checks
- `publish-pypi.yml` - PyPI publishing
- `release.yml` - Release automation

**Suggested Fix**:

- Add all workflows to the Core Workflows table.
- Include brief description of what each workflow does.
- Document any required secrets for each workflow.

### Qlty CLI Not Mentioned in PROJECT_SETUP.md

- **Priority**: Low
- **Cluster**: E
- **Date**: 2025-11-22

**Issue**: Post-generation script mentions Qlty CLI installation but `PROJECT_SETUP.md`
does not document it.

**Context**: The cookiecutter post-gen hook suggests `curl https://qlty.sh | bash` but
this tool is not mentioned in the setup guide or `CLAUDE.md`.

**Suggested Fix**:

- Add Qlty section to `PROJECT_SETUP.md` explaining its purpose and usage.
- Document the relationship between Qlty and other linting tools (Ruff, BasedPyright).
- Or remove from post-gen if not essential.
