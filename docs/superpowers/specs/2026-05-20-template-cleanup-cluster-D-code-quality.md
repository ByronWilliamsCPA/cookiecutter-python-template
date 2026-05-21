# Cluster D: Code Quality of Generated Code Design

> **Parent**: `2026-05-09-template-cleanup-umbrella.md`
> **Status**: design approved 2026-05-20
> **Scope**: 3 in-scope code-quality items (items 1, 3, 5 from the original umbrella list) plus a feedback-file housekeeping fix. Items 2 and 4 dropped (REDIRECTED and already-FIXED respectively).

## Goal

Land a single PR that resolves the three confirmed code-quality issues in the generated project: document interrogate's transitive `py` CVE as accepted risk via pip-audit allowlist, eliminate the remaining 5 BasedPyright warnings in `cli.py` and `logging.py` through proper typing, and refactor four high-complexity files for maintainability. Also moves 5 mis-categorized feedback entries from the `## Cluster D` section to a new `## Cluster E` section in `docs/template_feedback.md`.

## In-scope items

The umbrella's cluster D originally listed 5 items. After the 2026-05-20 status check:

| Item | Status | Disposition |
|---|---|---|
| 1. interrogate transitive `py` CVE-2022-42969 | open | this PR (component 1) |
| 2. scripts/sonar_scan.py missing | REDIRECTED | dropped; PR #54 migrated sonarcloud to org reusable workflow |
| 3. BasedPyright warnings in cli.py and logging.py | open (5 warnings) | this PR (components 2 and 3) |
| 4. qlty plugin syntax | already-FIXED | dropped; .qlty/qlty.toml no longer has [[plugin]] blocks |
| 5. Script complexity (4 files) | open | this PR (component 4) |

## Components

### Component 1: pip-audit allowlist for interrogate's `py` CVE

**Files:**

- Modify: `{{cookiecutter.project_slug}}/pyproject.toml` to add `PYSEC-2022-42969` to the pip-audit ignore list.

**Behavior:**

Add (or extend) the `[tool.pip-audit]` section in the generated `pyproject.toml`:

```toml
[tool.pip-audit]
# PYSEC-2022-42969: ReDoS in `py` package (pulled in transitively by interrogate).
# DISPUTED CVE: only affects parsing of malicious Subversion repository info data.
# This project does not interact with Subversion. interrogate has not released a
# fix that drops the `py` dependency. Accepted risk; dev-only impact.
ignore-vulns = ["PYSEC-2022-42969"]
```

Verify the section's exact key (`ignore-vulns` vs `ignore` vs similar) matches the pip-audit version pinned in the template. If the section already exists, append the CVE to the existing ignore list.

### Component 2: Click context typing in cli.py

**Files:**

- Modify: `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/cli.py`

**Behavior:**

Add a `CLIContext` `TypedDict` near the top of the file capturing the actual shape passed via `ctx.obj`. Based on existing usage, the shape is approximately:

```python
from typing import TypedDict
from structlog.stdlib import BoundLogger
from {{cookiecutter.project_slug}}.core.config import Settings  # actual import path verified at impl


class CLIContext(TypedDict):
    settings: Settings
    logger: BoundLogger
```

At the entry-point where `ctx.obj` is first assigned, construct a `CLIContext` literal. On the two access sites (currently lines 56 and 85 reporting `Type of "obj" is Any`), use direct typed access:

```python
ctx_obj: CLIContext = ctx.obj
settings = ctx_obj["settings"]
```

Or annotate the local variable explicitly. The exact approach should preserve current runtime behavior while satisfying BasedPyright.

Target: 2 warnings → 0.

### Component 3: structlog typing in logging.py

**Files:**

- Modify: `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/utils/logging.py`

**Behavior:**

Replace `Any` type annotations on the three offending lines:

- Line 84:9: parameter `_logger: Any` → `_logger: BoundLogger`
- Line 84:19: explicit `Any` in signature → concrete `BoundLogger` type
- Line 147:5: `result: Any` → narrow to concrete return type (likely `BoundLogger` or `dict[str, object]`; verify at implementation time)

Import `from structlog.stdlib import BoundLogger` at module top if not already present.

Target: 3 warnings → 0.

### Component 4: Script complexity refactor

**Files:**

- Modify: `{{cookiecutter.project_slug}}/scripts/check_fips_compatibility.py` (484 lines, `visit_Call` complexity 51)
- Modify: `{{cookiecutter.project_slug}}/scripts/cleanup_conditional_files.py` (313 lines, complexity 106)
- Modify: `{{cookiecutter.project_slug}}/scripts/check_orphaned_files.py` (195 lines, 17-line duplicate with cleanup_conditional)
- Create: `{{cookiecutter.project_slug}}/scripts/_cleanup_shared.py` (new module for the shared block)
- Modify: `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/core/exceptions.py` (485 lines, similar blocks at 186 and 294, 7-param __init__)

**Behavior:**

Each file gets a focused refactor:

- **check_fips_compatibility.py**: split the `visit_Call` method (currently a long switch on call types) into smaller methods grouped by check category: `_visit_hashlib_call`, `_visit_ssl_call`, `_visit_crypto_call`, etc. The original `visit_Call` becomes a dispatcher (≤ 10 statements). Target: each method ≤ complexity 10.
- **cleanup_conditional_files.py**: extract the conditional-cleanup logic into per-feature helpers (one helper per `include_*` flag handled). The top-level `cleanup_conditional_files` becomes a dispatcher that calls each helper. Target: complexity 106 → each helper ≤ 15, dispatcher ≤ 10.
- **check_orphaned_files.py + _cleanup_shared.py**: the 17-line shared block (per the original feedback, the `_load_cookiecutter_context` or similar duplicate) moves to `_cleanup_shared.py`. Both scripts import the function. Net: no behavioral change, single source of truth.
- **exceptions.py**: the 37-39 line similar blocks at lines 186 and 294 (per feedback) are common exception-formatting logic. Extract into a `_format_exception_dict` helper or a shared base-class method. The 7-parameter `__init__` is replaced with a dataclass (`ExceptionContext` or similar) that groups related parameters. Constructor backwards compatibility is preserved via keyword arguments.

**Backwards compatibility for exceptions.py**: any code that currently instantiates exceptions positionally would break. The refactor must preserve keyword-argument support and ideally keep the same positional argument order for the first 2-3 parameters (typical usage: `ValidationError("message", field="email")`).

### Component 5: Feedback file mis-categorization fix

**Files:**

- Modify: `docs/template_feedback.md`

**Behavior:**

The current `## Cluster D: Code Quality of Generated Code` section in the feedback file contains 10 entries. Of those, 5 belong to cluster E (per the umbrella):

- MD040 Violations: Fenced Code Blocks Without Language Specifier
- MD051 Link Fragment Violations in docs/PROJECT_SETUP.md
- Documentation Files Missing YAML Front Matter (Planning Subset)
- CI/CD Workflow Documentation Missing Several Workflows
- Qlty CLI Not Mentioned in PROJECT_SETUP.md

Move those 5 entries to a new `## Cluster E: Documentation and MkDocs` section in the feedback file. Leave the remaining cluster D entries in their section.

Also remove the entries this PR closes:

- "Transitive Dependency `py` Has Known Vulnerability (via interrogate)" — closed by component 1
- "Template Missing Local SonarCloud Scanning Script" — REDIRECTED, remove
- "Template-Generated Code Has BasedPyright Warnings (DETAILED)" — closed by components 2 and 3
- "Template-Generated Scripts Fail Qlty Code Quality Checks" — closed by component 4
- "Qlty Configuration Has Invalid Plugin Syntax" — already-FIXED, remove

Add a cleanup blockquote near the existing 2026-05-19 cleanup note:

```markdown
> **Cleanup 2026-05-20:** 5 cluster D entries closed (interrogate CVE allowlisted,
> BasedPyright warnings eliminated, script complexity refactored). Items 2
> (sonar_scan.py) and 4 (qlty plugin syntax) dropped as REDIRECTED and
> already-FIXED respectively. Mis-categorized cluster E entries (5) moved to a
> dedicated section.
```

## Architecture

Three independent code-quality improvements plus a documentation hygiene change. No new cookiecutter variables. No changes to existing flags. Generated project behavior is unchanged at runtime; only static-analysis output and code structure improve.

The complexity refactor is the only component with non-trivial regression risk. Mitigation: existing tests must pass after the refactor; the changes preserve the original control flow.

## Data flow

No runtime data-flow changes. All changes are:

- Configuration (pip-audit allowlist entry)
- Type annotations (no runtime effect; TypedDict is structural)
- Code structure (refactor preserves behavior, splits into smaller units)

## Error handling

No new error paths. The pip-audit allowlist suppresses one specific advisory without affecting other vulnerability detection. The typing changes add no runtime checks. The complexity refactor preserves the original control flow exactly.

## Testing

Three layers:

### Layer 1: existing test suite

Run `uv run pytest tests/unit/` after each component lands. All 90+ existing tests must continue to pass. Per-file unit tests for the refactored scripts (in `tests/unit/`) catch regressions.

### Layer 2: quality-gate measurements

Captured in PR description as evidence:

- `uv run basedpyright src/<slug>/cli.py src/<slug>/utils/logging.py`: target 0 warnings (was 5).
- `uv run pip-audit`: target 0 unsuppressed vulnerabilities (PYSEC-2022-42969 now in ignore list).
- Manual or qlty-driven complexity check on the four refactored files: max method complexity ≤ 10.
- `grep -c "py.*1.11" uv.lock` is unchanged (the `py` package is still pulled in; we are not removing it, just suppressing its CVE).

### Layer 3: cruft smoke test

`cruft create --no-input` followed by `cd my_python_project && uv sync && uv run basedpyright src/` verifies the generated project still generates cleanly and the type checker is happy.

## Out of scope

- Item 2 (sonar_scan.py): dropped, PR #54's org reusable workflow handles SonarCloud scanning.
- Item 4 (qlty plugin syntax): already FIXED; qlty.toml uses `[smells]` sections with no `[[plugin]]` blocks.
- The 5 cluster E items currently mis-categorized in the feedback file: moved to a `## Cluster E` section in this PR, but the actual work is deferred to cluster E.
- Removing the `py` package from the dependency tree. The package is a transitive dependency of interrogate, which has not released a fix. Replacing interrogate is out of scope; this PR accepts the disputed CVE.

## Acceptance criteria

A PR titled `fix(template): cluster D code quality (interrogate, basedpyright, script complexity)` lands on `main` with:

- [ ] `[tool.pip-audit]` ignore list in the generated `pyproject.toml` includes `PYSEC-2022-42969` with an inline comment.
- [ ] Fresh `uv run basedpyright src/<slug>/cli.py src/<slug>/utils/logging.py` reports 0 warnings.
- [ ] Each refactored script's max method complexity ≤ 10 (measured manually or via qlty).
- [ ] The 17-line duplicate between `cleanup_conditional_files.py` and `check_orphaned_files.py` lives in `_cleanup_shared.py`; both files import the helper.
- [ ] `exceptions.py` no longer has 37-39 line similar blocks; `__init__` uses ≤ 4 parameters or a dataclass.
- [ ] `cruft create --no-input` smoke test produces a project whose test suite passes (or at least: the existing template test suite remains green).
- [ ] `docs/template_feedback.md` is trimmed (5 cluster D entries removed) and re-categorized (5 cluster E entries moved to a new section).
- [ ] Umbrella status log gets a row recording cluster D shipment.

## Branch

Branch from `main`. Worktree at `.worktrees/fix-cluster-D-code-quality` per project convention.
