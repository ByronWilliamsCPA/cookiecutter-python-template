# Template Cleanup Cluster D Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve three confirmed code-quality issues in the generated project (interrogate CVE via pip-audit allowlist, BasedPyright warnings via proper typing, four files refactored for complexity) and move 5 mis-categorized feedback entries to the correct cluster.

**Architecture:** Six tasks (one per component plus a final acceptance gate). Component 1 is config-only (1 file). Components 2 and 3 type narrow existing code (2 files). Component 4 refactors four working files plus extracts a shared module (5 files). Component 5 is documentation housekeeping. Each component's tasks include TDD where new behavior is added; pure refactors use behavior-preserving discipline (existing tests must remain green).

**Tech Stack:** Python 3.12, cookiecutter/cruft, pytest, ruff, basedpyright, pip-audit, structlog, Click, dataclasses.

---

## Spec references

- Design: `docs/superpowers/specs/2026-05-20-template-cleanup-cluster-D-code-quality.md`
- Feasibility: `docs/superpowers/feasibility/template-cleanup-cluster-D-feasibility.md` (CONDITIONAL GO; re-measure baseline before typing work)
- Umbrella: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

## Branch and worktree

Create the worktree from `main`:

```bash
cd /home/byron/dev/cookiecutter-python-template
git fetch origin
git worktree add .worktrees/fix-cluster-D-code-quality -b feat/cluster-D-code-quality origin/main
cd .worktrees/fix-cluster-D-code-quality
uv sync --all-extras
```

## File structure

| File | Action | Responsibility |
|---|---|---|
| `{{cookiecutter.project_slug}}/pyproject.toml` | modify | Add `[tool.pip-audit]` section with `ignore-vulns` for PYSEC-2022-42969 |
| `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/cli.py` | modify | Type `ctx.obj` access at the two warning sites |
| `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/utils/logging.py` | modify | Replace `Any` with `BoundLogger` (or appropriate structlog type) at the three warning sites |
| `{{cookiecutter.project_slug}}/scripts/check_fips_compatibility.py` | modify | Split `visit_Call` into category-specific helpers |
| `{{cookiecutter.project_slug}}/scripts/cleanup_conditional_files.py` | modify | Decompose `cleanup_conditional_files` into per-feature helpers; import shared helper from new module |
| `{{cookiecutter.project_slug}}/scripts/check_orphaned_files.py` | modify | Import the shared helper from new module |
| `{{cookiecutter.project_slug}}/scripts/_cleanup_shared.py` | create | New module containing the previously-duplicated helper |
| `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/core/exceptions.py` | modify | Extract `_attach_optional_details` helper; refactor 7-param `__init__` |
| `docs/template_feedback.md` | modify | Remove closed entries, move 5 mis-categorized entries to a new `## Cluster E` section, add 2026-05-20 cleanup blockquote |
| `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md` | modify | Append a status-log row for cluster D shipment |

---

## Task 1: Pre-flight measurement (read-only)

This task establishes the baseline before any code changes. It produces no commits.

- [ ] **Step 1.1: Fresh generation and measurement**

Run:

```bash
SMOKE=$(mktemp -d /tmp/cluster-D-baseline.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality --no-input 2>&1 | tail -3
cd "$SMOKE/my_python_project"
uv sync --all-extras --quiet 2>&1 | tail -3
echo "--- basedpyright on cli.py + logging.py ---"
uv run basedpyright src/my_python_project/cli.py src/my_python_project/utils/logging.py 2>&1 | tail -15
echo "--- pip-audit ---"
uv run pip-audit 2>&1 | tail -15
cd /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality
rm -rf "$SMOKE"
```

Capture the exact warning lines, rule codes, and vulnerability IDs. The expected (per cluster BA smoke and feasibility):

- 5 basedpyright warnings on cli.py + logging.py
- 1 pip-audit advisory (PYSEC-2022-42969 on `py` package)

If the measurements differ, adjust Task 2's pip-audit ID and Task 3's typing targets accordingly.

- [ ] **Step 1.2: Read existing CLIContext + logging.py state**

```bash
sed -n '15,35p' "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/cli.py"
sed -n '85,95p' "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/utils/logging.py"
sed -n '140,160p' "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/utils/logging.py"
```

Confirm: `CLIContext` is a `@dataclass` with at least one field (currently `debug`). `logging.py` uses `"WrappedLogger"` as a string-quoted forward reference. The typing changes in Tasks 3 and 4 should adjust EXISTING annotations, not introduce new types from scratch.

No commit for this task. Record the baseline in the PR description at the end.

---

## Task 2: pip-audit allowlist for PYSEC-2022-42969

**Files:**
- Modify: `{{cookiecutter.project_slug}}/pyproject.toml`

- [ ] **Step 2.1: Confirm no existing `[tool.pip-audit]` section**

```bash
grep -nE "^\[tool\.pip-audit\]|^\[tool\.pip_audit\]" "{{cookiecutter.project_slug}}/pyproject.toml" || echo "not present"
```

If the section already exists, append `PYSEC-2022-42969` to its existing `ignore-vulns` list. If not present, create the section.

- [ ] **Step 2.2: Add the section to pyproject.toml**

Find a logical insertion point near the end of the `[tool.*]` sections. Add:

```toml
[tool.pip-audit]
# PYSEC-2022-42969: ReDoS in `py` package (pulled in transitively by interrogate).
# DISPUTED CVE: only affects parsing of malicious Subversion repository info data.
# This project does not interact with Subversion. interrogate has not released
# a fix that drops the `py` dependency. Accepted risk; dev-only impact.
ignore-vulns = ["PYSEC-2022-42969"]
```

Use the Edit tool to insert after the last `[tool.*]` block.

- [ ] **Step 2.3: Verify pip-audit honors the entry**

```bash
SMOKE=$(mktemp -d /tmp/cluster-D-task2.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality --no-input 2>&1 | tail -3
cd "$SMOKE/my_python_project"
uv sync --all-extras --quiet 2>&1 | tail -3
uv run pip-audit 2>&1 | tail -10
cd /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality
rm -rf "$SMOKE"
```

Expected: pip-audit no longer flags PYSEC-2022-42969 (or the output shows it as skipped/ignored).

- [ ] **Step 2.4: Commit**

```bash
git add "{{cookiecutter.project_slug}}/pyproject.toml"
git commit -m "$(cat <<'EOF'
fix(template): allowlist interrogate transitive py CVE in pip-audit

PYSEC-2022-42969 is a disputed ReDoS in `py` (transitive dependency
of interrogate>=1.7.0). The CVE affects Subversion repository info
parsing, which this project does not use. interrogate has not released
a version without the `py` dependency. Accepted risk; dev-only impact.

Add `[tool.pip-audit] ignore-vulns = ["PYSEC-2022-42969"]` to the
generated pyproject.toml with an inline comment explaining the
rationale.
EOF
)"
```

---

## Task 3: BasedPyright typing for cli.py

**Files:**
- Modify: `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/cli.py`

The cli.py warnings (lines ~56 and ~85: `"obj" is Any`) come from accessing `ctx.obj` where Click's stubs declare `obj: Any`. The fix is to annotate the access points so basedpyright knows the runtime type.

- [ ] **Step 3.1: Read the current cli.py to locate the access sites**

```bash
grep -n "ctx.obj\|CLIContext" "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/cli.py"
```

Identify all sites where `ctx.obj` is accessed or assigned. Typical Click pattern: `ctx.ensure_object(CLIContext)` returns `Any` per Click's stubs.

- [ ] **Step 3.2: Add a typed accessor helper**

Add this helper near the top of `cli.py` (after the `CLIContext` dataclass definition):

```python
def _get_context(ctx: click.Context) -> CLIContext:
    """Return ctx.obj typed as CLIContext.

    Click's stubs declare ctx.obj as Any. This helper narrows the type so
    callers receive a CLIContext without per-site casts.
    """
    return cast(CLIContext, ctx.ensure_object(CLIContext))
```

Add `from typing import cast` to the imports if not already present.

- [ ] **Step 3.3: Replace `ctx.obj` access at the two warning sites**

For each site identified in Step 3.1 where the warning fires, replace:

```python
# Before
obj = ctx.obj
some_field = obj.debug  # or whatever field
```

with:

```python
# After
obj = _get_context(ctx)
some_field = obj.debug
```

If `ctx.obj` is read without intermediate assignment (e.g., `if ctx.obj.debug:`), wrap inline:

```python
if _get_context(ctx).debug:
```

- [ ] **Step 3.4: Verify warnings cleared on cli.py**

```bash
SMOKE=$(mktemp -d /tmp/cluster-D-task3.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality --no-input 2>&1 | tail -3
cd "$SMOKE/my_python_project"
uv sync --all-extras --quiet 2>&1 | tail -3
uv run basedpyright src/my_python_project/cli.py 2>&1 | tail -8
cd /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality
rm -rf "$SMOKE"
```

Expected: 0 warnings on cli.py (was 2). If the count is non-zero, inspect each remaining warning and adjust.

- [ ] **Step 3.5: Run existing tests**

```bash
uv run pytest tests/unit/ --tb=short -q 2>&1 | tail -10
```

Expected: all tests pass.

- [ ] **Step 3.6: Commit**

```bash
git add "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/cli.py"
git commit -m "$(cat <<'EOF'
fix(template): type ctx.obj access via _get_context helper in cli.py

Click's stubs declare ctx.obj as Any, producing reportAny warnings at
every access site. Add a _get_context(ctx) helper that calls
ctx.ensure_object(CLIContext) and casts to the dataclass type, then
use the helper at every access point. BasedPyright now sees the
narrowed type and the two reportAny warnings on cli.py clear.
EOF
)"
```

---

## Task 4: BasedPyright typing for logging.py

**Files:**
- Modify: `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/utils/logging.py`

The logging.py warnings (line ~84: `_logger: Any` and explicit `Any`; line ~147: `result: Any`) come from structlog's typing exports. `WrappedLogger` (a structlog protocol) is the conventional type. The forward-reference string `"WrappedLogger"` likely resolves to `Any` because the import is inside `TYPE_CHECKING`.

- [ ] **Step 4.1: Read the imports and confirm WrappedLogger source**

```bash
grep -nE "^from structlog|^import structlog|WrappedLogger|BoundLogger" "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/utils/logging.py"
```

Identify whether `WrappedLogger` is imported (likely under `TYPE_CHECKING`). If it resolves to a structural Protocol whose attributes are not fully typed, basedpyright treats the parameter as Any.

- [ ] **Step 4.2: Replace `"WrappedLogger"` with `BoundLogger` at the warning sites**

At line ~84 (the `noop_processor` inner function signature), replace:

```python
def noop_processor(
    _logger: "WrappedLogger",
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
```

with:

```python
def noop_processor(
    _logger: BoundLogger,
    _method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
```

Add `from structlog.stdlib import BoundLogger` to the module's TYPE_CHECKING imports (or to runtime imports if used at runtime). Replace `dict[str, Any]` with `dict[str, object]` to clear the explicit-Any warning.

At line ~147, if the function returns `Any` (look for `result: Any` or `-> Any`), narrow it to the actual return type. `structlog.get_logger()` returns a `BoundLogger`; if that is the return value, annotate accordingly.

- [ ] **Step 4.3: Verify warnings cleared on logging.py**

```bash
SMOKE=$(mktemp -d /tmp/cluster-D-task4.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality --no-input 2>&1 | tail -3
cd "$SMOKE/my_python_project"
uv sync --all-extras --quiet 2>&1 | tail -3
uv run basedpyright src/my_python_project/utils/logging.py 2>&1 | tail -8
cd /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality
rm -rf "$SMOKE"
```

Expected: 0 warnings on logging.py (was 3). If a warning persists because structlog's stubs are insufficient, add a targeted `# pyright: ignore[reportAny]` comment with an inline note explaining the upstream gap.

- [ ] **Step 4.4: Run existing tests**

```bash
uv run pytest tests/unit/ --tb=short -q 2>&1 | tail -10
```

Expected: all tests pass.

- [ ] **Step 4.5: Commit**

```bash
git add "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/utils/logging.py"
git commit -m "$(cat <<'EOF'
fix(template): replace Any with BoundLogger in logging.py

The noop_processor inner function and a later helper used `Any` for
structlog logger parameters because `WrappedLogger` is a string
forward reference that resolves to Any under BasedPyright. Import
BoundLogger from structlog.stdlib and use it at the three warning
sites, plus replace dict[str, Any] with dict[str, object] for the
event_dict to clear the explicit-Any warning.
EOF
)"
```

---

## Task 5: Refactor check_fips_compatibility.py

**Files:**
- Modify: `{{cookiecutter.project_slug}}/scripts/check_fips_compatibility.py`

The `visit_Call` method (line 99) has complexity 51 (target 10). The existing `# noqa: C901, PLR0912` suppression silences ruff; qlty still flags. Refactor by splitting into category-specific helpers.

- [ ] **Step 5.1: Read the existing visit_Call structure**

```bash
sed -n '95,200p' "{{cookiecutter.project_slug}}/scripts/check_fips_compatibility.py"
```

Identify the major branches inside `visit_Call`. Typical structure: outer `if isinstance(node.func, ast.Attribute):` then nested checks for hashlib, ssl, crypto, etc.

- [ ] **Step 5.2: Extract per-category helper methods**

Inside `class FipsCodeVisitor(ast.NodeVisitor)`, add private helpers for each category, one per check group:

```python
def _check_hashlib_call(self, node: ast.Call) -> None:
    """Detect hashlib.md5(), hashlib.sha1(), and similar FIPS-incompatible calls."""
    # extract the existing hashlib branch from visit_Call

def _check_ssl_call(self, node: ast.Call) -> None:
    """Detect ssl.PROTOCOL_TLSv1 and similar deprecated TLS calls."""
    # extract the existing ssl branch from visit_Call

def _check_cryptography_call(self, node: ast.Call) -> None:
    """Detect cryptography.hazmat usage that bypasses FIPS providers."""
    # extract the existing cryptography branch from visit_Call

# (one helper per category currently inside visit_Call)
```

Each helper extracts one branch's logic verbatim. The branch's `if isinstance(...)` guard becomes the helper's first statement (early return if not matched).

- [ ] **Step 5.3: Rewrite visit_Call as a dispatcher**

Replace the original `visit_Call` body with:

```python
def visit_Call(self, node: ast.Call) -> None:
    """Visit function calls to detect crypto usage."""
    self._check_hashlib_call(node)
    self._check_ssl_call(node)
    self._check_cryptography_call(node)
    # ... one line per category helper ...
    self.generic_visit(node)
```

The `# noqa: C901, PLR0912` suppression on `visit_Call` can be removed since complexity now lives in the helpers and each helper is small.

- [ ] **Step 5.4: Verify the script's existing tests still pass**

```bash
uv run pytest tests/unit/ -k "fips" --tb=short -q 2>&1 | tail -10
# If no fips-specific tests exist, run the script against the template tree:
uv run python "{{cookiecutter.project_slug}}/scripts/check_fips_compatibility.py" --help 2>&1 | head -5
```

Expected: tests pass; --help renders. If behavioral tests exist for FIPS detection, run them.

- [ ] **Step 5.5: Spot-check behavior preservation**

Run the script against a sample file with known violations to confirm detection still works:

```bash
echo 'import hashlib; hashlib.md5(b"x")' > /tmp/fips-test.py
uv run python "{{cookiecutter.project_slug}}/scripts/check_fips_compatibility.py" /tmp/fips-test.py 2>&1 | tail -5
rm /tmp/fips-test.py
```

Expected: the script reports the hashlib.md5 call as a violation. Behavior unchanged.

- [ ] **Step 5.6: Commit**

```bash
git add "{{cookiecutter.project_slug}}/scripts/check_fips_compatibility.py"
git commit -m "$(cat <<'EOF'
refactor(template): split visit_Call into category helpers

check_fips_compatibility.py's visit_Call method had complexity 51
(target ≤ 10), silenced via # noqa but flagged by qlty. Extract
per-category helpers (_check_hashlib_call, _check_ssl_call,
_check_cryptography_call, etc.) so each handles one check group;
visit_Call becomes a flat dispatcher.

Behavior preserved: the helpers are extracted verbatim from the
original branches. Existing tests pass. The # noqa suppression is
removed because complexity now lives in the small helpers.
EOF
)"
```

---

## Task 6: Refactor cleanup_conditional_files.py + extract _cleanup_shared.py

**Files:**
- Modify: `{{cookiecutter.project_slug}}/scripts/cleanup_conditional_files.py`
- Modify: `{{cookiecutter.project_slug}}/scripts/check_orphaned_files.py`
- Create: `{{cookiecutter.project_slug}}/scripts/_cleanup_shared.py`

The `cleanup_conditional_files` function (lines 106-281, ~175 lines) has complexity 106. It also shares ~17 lines with `check_orphaned_files.py` (likely the `get_cruft_context` function).

- [ ] **Step 6.1: Identify the shared block**

```bash
diff <(sed -n '30,50p' "{{cookiecutter.project_slug}}/scripts/cleanup_conditional_files.py") \
     <(sed -n '25,50p' "{{cookiecutter.project_slug}}/scripts/check_orphaned_files.py")
```

Expected: the diff is small (the duplicate block has near-identical lines). The shared function is likely `get_cruft_context()` at line 35 in cleanup_conditional_files and line 31 in check_orphaned_files.

- [ ] **Step 6.2: Create `_cleanup_shared.py`**

Create the new file with the shared helper:

```python
"""Shared helpers for the cleanup_conditional_files.py and check_orphaned_files.py scripts.

This module centralizes utilities that both scripts need (e.g., locating
the .cruft.json cookiecutter context). Keeping these in one place avoids
duplicate code and ensures both scripts behave consistently.
"""

from __future__ import annotations

import json
from pathlib import Path


def get_cruft_context() -> dict[str, str]:
    """Load the rendered cookiecutter context from .cruft.json.

    Returns:
        The cookiecutter context dict (typically including project_slug,
        include_cli, include_docker, etc.) or an empty dict if .cruft.json
        is absent.
    """
    cruft_file = Path(".cruft.json")
    if not cruft_file.exists():
        return {}
    try:
        data = json.loads(cruft_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data.get("context", {}).get("cookiecutter", {}) or {}
```

The function body is extracted verbatim from cleanup_conditional_files.py's existing `get_cruft_context()`. Verify the exact body by reading the source first.

- [ ] **Step 6.3: Update cleanup_conditional_files.py to import from the shared module**

In `{{cookiecutter.project_slug}}/scripts/cleanup_conditional_files.py`:

1. Remove the local `get_cruft_context()` definition (lines ~35-53).
2. Replace it with: `from scripts._cleanup_shared import get_cruft_context`.

- [ ] **Step 6.4: Update check_orphaned_files.py to import from the shared module**

In `{{cookiecutter.project_slug}}/scripts/check_orphaned_files.py`:

1. Remove the local `get_cruft_context()` definition (lines ~31-49).
2. Replace it with: `from scripts._cleanup_shared import get_cruft_context`.

- [ ] **Step 6.5: Decompose cleanup_conditional_files into per-feature helpers**

The main `cleanup_conditional_files(context, dry_run)` function (lines 106-281) handles many `include_*` flags in one monolithic body. Extract per-flag helpers:

```python
def _cleanup_for_no_cli(slug: str, dry_run: bool) -> int:
    """Remove CLI-only files when include_cli is no.

    Returns the count of removed paths.
    """
    count = 0
    if remove_file(Path(f"src/{slug}/cli.py"), dry_run):
        count += 1
    # ... existing cli-specific removals ...
    return count


def _cleanup_for_no_docker(dry_run: bool) -> int:
    """Remove Docker-related files when include_docker is no.

    Returns the count of removed paths.
    """
    count = 0
    if remove_file(Path("Dockerfile"), dry_run):
        count += 1
    if remove_file(Path("docker-compose.yml"), dry_run):
        count += 1
    # ... existing docker-specific removals ...
    return count


# ... one helper per include_* flag handled in the original function ...
```

Each helper extracts its branch verbatim. The original function becomes a dispatcher:

```python
def cleanup_conditional_files(context: dict, dry_run: bool = False) -> int:
    """Remove conditionally-included files based on the cookiecutter context."""
    slug = get_project_slug(context)
    total = 0
    if context.get("include_cli") == "no":
        total += _cleanup_for_no_cli(slug, dry_run)
    if context.get("include_docker") == "no":
        total += _cleanup_for_no_docker(dry_run)
    # ... one dispatch line per helper ...
    return total
```

- [ ] **Step 6.6: Verify behavior preservation**

```bash
uv run pytest tests/unit/ --tb=short -q 2>&1 | tail -10
```

Expected: all tests pass. The cleanup scripts have integration coverage via the post-gen hook tests (which use them indirectly).

- [ ] **Step 6.7: Verify the shared helper import works**

```bash
SMOKE=$(mktemp -d /tmp/cluster-D-task6.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality --no-input 2>&1 | tail -3
cd "$SMOKE/my_python_project"
PYTHONPATH=. uv run python scripts/cleanup_conditional_files.py --dry-run 2>&1 | tail -5
PYTHONPATH=. uv run python scripts/check_orphaned_files.py 2>&1 | tail -5
cd /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality
rm -rf "$SMOKE"
```

Expected: both scripts run without ImportError; the `_cleanup_shared` module resolves correctly.

- [ ] **Step 6.8: Commit**

```bash
git add "{{cookiecutter.project_slug}}/scripts/_cleanup_shared.py" "{{cookiecutter.project_slug}}/scripts/cleanup_conditional_files.py" "{{cookiecutter.project_slug}}/scripts/check_orphaned_files.py"
git commit -m "$(cat <<'EOF'
refactor(template): extract _cleanup_shared.py and decompose cleanup_conditional_files

cleanup_conditional_files.py had a single 175-line function (complexity 106)
handling every include_* flag in one body, plus duplicated get_cruft_context()
with check_orphaned_files.py. Extract get_cruft_context() into the new
scripts/_cleanup_shared.py module; both scripts import it. Decompose
cleanup_conditional_files into per-feature helpers (_cleanup_for_no_cli,
_cleanup_for_no_docker, etc.); the top-level function becomes a flat
dispatcher. Behavior preserved; existing post-gen tests cover the integration.
EOF
)"
```

---

## Task 7: Refactor exceptions.py

**Files:**
- Modify: `{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/core/exceptions.py`

The exceptions module has repeated `if X: details[X] = X` blocks in the `__init__` methods of multiple exception classes, plus a 7-parameter `__init__` (likely `APIError`).

- [ ] **Step 7.1: Identify the repeated patterns**

```bash
grep -nA1 "if [a-z_]* is not None\|if [a-z_]*:" "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/core/exceptions.py" | head -30
```

Identify the conditional-detail-attachment pattern. Typical structure:

```python
if resource_type:
    details["resource_type"] = resource_type
if resource_id:
    details["resource_id"] = resource_id
```

Multiple exception classes (`ResourceNotFoundError`, `ExternalServiceError`, etc.) repeat this.

- [ ] **Step 7.2: Extract `_attach_optional_details` helper**

Add a module-level helper:

```python
def _attach_optional_details(
    details: dict[str, object], **fields: object | None,
) -> dict[str, object]:
    """Add non-None field values to a details dict.

    Args:
        details: Existing details dict (may be empty).
        **fields: Optional fields to add; None values are skipped.

    Returns:
        The details dict with the non-None fields added (modified in place
        and returned for convenience).
    """
    for key, value in fields.items():
        if value is not None:
            details[key] = value
    return details
```

- [ ] **Step 7.3: Replace the repeated blocks**

In each `__init__` that has the `if X: details[X] = X` pattern, replace it with one call:

```python
# Before
def __init__(
    self,
    message: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
    error_code: str | None = None,
) -> None:
    details = details or {}
    if resource_type:
        details["resource_type"] = resource_type
    if resource_id:
        details["resource_id"] = resource_id
    super().__init__(message, details=details, error_code=error_code or "NOT_FOUND")

# After
def __init__(
    self,
    message: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
    error_code: str | None = None,
) -> None:
    details = _attach_optional_details(
        details or {},
        resource_type=resource_type,
        resource_id=resource_id,
    )
    super().__init__(message, details=details, error_code=error_code or "NOT_FOUND")
```

Apply this to every `__init__` that has the pattern (`ResourceNotFoundError`, `ExternalServiceError`, `APIError`, etc.).

- [ ] **Step 7.4: Refactor the 7-param `__init__` (APIError or similar)**

Identify the exception class with 7+ parameters. Replace the parameter list with an `ExceptionContext` dataclass:

```python
from dataclasses import dataclass, field

@dataclass
class APIErrorContext:
    """Grouped parameters for APIError construction."""
    service_name: str | None = None
    status_code: int | None = None
    retry_after: int | None = None
    request_id: str | None = None
    endpoint: str | None = None
    method: str | None = None


class APIError(ExternalServiceError):
    def __init__(
        self,
        message: str,
        context: APIErrorContext | None = None,
        details: dict | None = None,
        error_code: str | None = None,
    ) -> None:
        context = context or APIErrorContext()
        details = _attach_optional_details(
            details or {},
            service_name=context.service_name,
            status_code=context.status_code,
            retry_after=context.retry_after,
            request_id=context.request_id,
            endpoint=context.endpoint,
            method=context.method,
        )
        super().__init__(message, details=details, error_code=error_code or "API_ERROR")
```

Backwards compatibility: callers using keyword arguments (the dominant pattern) will need a small migration. Add a class method `from_kwargs` for backwards compatibility, OR document the breaking change in the commit. Per the spec, backwards compatibility is preserved via keyword arguments; the safest approach is to keep BOTH the old keyword parameters AND the new context-object form. Inside `__init__`, accept both:

```python
def __init__(
    self,
    message: str,
    *,
    service_name: str | None = None,
    status_code: int | None = None,
    retry_after: int | None = None,
    request_id: str | None = None,
    endpoint: str | None = None,
    method: str | None = None,
    context: APIErrorContext | None = None,
    details: dict | None = None,
    error_code: str | None = None,
) -> None:
    """Accepts either the legacy keyword parameters or an APIErrorContext.

    If `context` is provided, its fields take precedence; otherwise the
    individual keyword parameters populate an APIErrorContext.
    """
    if context is None:
        context = APIErrorContext(
            service_name=service_name,
            status_code=status_code,
            retry_after=retry_after,
            request_id=request_id,
            endpoint=endpoint,
            method=method,
        )
    # ... rest as above ...
```

This preserves call-site compatibility while documenting the new dataclass path.

- [ ] **Step 7.5: Run existing tests**

```bash
uv run pytest tests/unit/ --tb=short -q 2>&1 | tail -10
```

Expected: all tests pass. exceptions.py likely has unit tests under `tests/unit/`; they cover the constructor behavior.

- [ ] **Step 7.6: Commit**

```bash
git add "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}/core/exceptions.py"
git commit -m "$(cat <<'EOF'
refactor(template): extract _attach_optional_details and dataclass-ify APIError

exceptions.py had repeated `if X: details[X] = X` patterns across multiple
exception class __init__ methods (similar 37-39 line blocks at lines 186
and 294 per qlty). Extract a module-level _attach_optional_details
helper that takes a details dict and **kwargs, adding only non-None
values. Each exception class's __init__ now uses one call instead of
multiple if-blocks.

APIError's 7-parameter __init__ gets an APIErrorContext dataclass for
grouping. Backwards compatibility preserved: __init__ accepts both the
context object and the legacy keyword parameters.
EOF
)"
```

---

## Task 8: Feedback file housekeeping + umbrella update

**Files:**
- Modify: `docs/template_feedback.md`
- Modify: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

- [ ] **Step 8.1: Remove closed cluster D entries**

From `docs/template_feedback.md`, remove these entries (under `## Cluster D: Code Quality of Generated Code`):

- `### Transitive Dependency `py` Has Known Vulnerability (via interrogate)` (closed by Task 2)
- `### Template Missing Local SonarCloud Scanning Script` (REDIRECTED, dropped)
- `### Template-Generated Code Has BasedPyright Warnings (DETAILED)` (closed by Tasks 3 and 4)
- `### Template-Generated Scripts Fail Qlty Code Quality Checks` (closed by Tasks 5, 6, 7)
- `### Qlty Configuration Has Invalid Plugin Syntax` (already-FIXED, dropped)

- [ ] **Step 8.2: Move mis-categorized entries to a new cluster E section**

Five entries currently in the `## Cluster D` section actually belong to cluster E per the umbrella. Cut these from the cluster D section and add them to a new `## Cluster E: Documentation and MkDocs` section just after cluster D:

- `### MD040 Violations: Fenced Code Blocks Without Language Specifier`
- `### MD051 Link Fragment Violations in docs/PROJECT_SETUP.md`
- `### Documentation Files Missing YAML Front Matter (Planning Subset)`
- `### CI/CD Workflow Documentation Missing Several Workflows`
- `### Qlty CLI Not Mentioned in PROJECT_SETUP.md`

The cluster D section should now be empty (all entries removed). If so, remove the `## Cluster D: Code Quality of Generated Code` heading too.

- [ ] **Step 8.3: Add a cleanup blockquote**

After the existing `> **Cleanup 2026-05-19:** ...` blockquote, add:

```markdown
> **Cleanup 2026-05-20:** 3 cluster D entries closed (interrogate CVE allowlisted,
> BasedPyright warnings eliminated, script complexity refactored across 4 files).
> Items 2 (sonar_scan.py) and 4 (qlty plugin syntax) dropped as REDIRECTED and
> already-FIXED respectively. 5 mis-categorized cluster E entries moved to a new
> `## Cluster E: Documentation and MkDocs` section.
```

- [ ] **Step 8.4: Update umbrella status log**

In `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`, find the Status log table near the bottom. Add a new row:

```markdown
| 2026-05-20 | Cluster D shipped: pip-audit allowlist for interrogate's `py` CVE, BasedPyright typing fixes in cli.py and logging.py (5 warnings → 0), complexity refactor of 4 files (check_fips, cleanup_conditional, check_orphaned, exceptions.py) plus extracted `_cleanup_shared.py`. Items 2 and 4 dropped from original cluster D scope; 5 mis-categorized entries moved to cluster E. |
```

Also update the cluster index/table at the top of the umbrella: change cluster D's status to `shipped`.

- [ ] **Step 8.5: Commit**

```bash
git add docs/template_feedback.md docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md
git commit -m "$(cat <<'EOF'
docs(feedback): remove cluster D entries + recategorize cluster E items

3 cluster D entries closed by this PR removed. Items 2 (sonar_scan.py)
and 4 (qlty plugin syntax) dropped as REDIRECTED and already-FIXED.

5 entries previously listed under "Cluster D" actually belong to
cluster E per the umbrella (MD040, MD051, planning front matter,
PROJECT_SETUP workflow table, qlty CLI). Move them to a new
"Cluster E: Documentation and MkDocs" section so the feedback file
reflects the umbrella's cluster taxonomy.

Umbrella status log records cluster D shipment; cluster index updated
to mark D as shipped.
EOF
)"
```

---

## Task 9: Final acceptance + PR

- [ ] **Step 9.1: Run pre-commit on the full diff**

```bash
pre-commit run --all-files 2>&1 | tail -40
```

Expected: PASS for files this cluster touched. Pre-existing failures in unrelated files (per cluster C's pattern) are non-blocking; flag them in the report.

- [ ] **Step 9.2: Run the full unit test suite**

```bash
uv run pytest tests/unit/ --tb=short 2>&1 | tail -10
```

Expected: 90+ tests pass (matches cluster C's baseline).

- [ ] **Step 9.3: Final cruft smoke test with quality measurements**

```bash
SMOKE=$(mktemp -d /tmp/cluster-D-final.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality --no-input 2>&1 | tail -3
cd "$SMOKE/my_python_project"
uv sync --all-extras --quiet 2>&1 | tail -3
echo "--- basedpyright (target: 0 warnings on cli.py + logging.py) ---"
uv run basedpyright src/my_python_project/cli.py src/my_python_project/utils/logging.py 2>&1 | tail -5
echo "--- pip-audit (target: PYSEC-2022-42969 ignored) ---"
uv run pip-audit 2>&1 | tail -10
cd /home/byron/dev/cookiecutter-python-template/.worktrees/fix-cluster-D-code-quality
rm -rf "$SMOKE"
```

Expected: 0 basedpyright warnings, pip-audit no longer flags PYSEC-2022-42969. Capture the output for the PR description.

- [ ] **Step 9.4: Push the branch**

```bash
git push -u origin feat/cluster-D-code-quality 2>&1 | tail -3
```

- [ ] **Step 9.5: Draft the PR body (do NOT open yet)**

Write the PR title and body to stdout for the controller to authorize. Use this template:

```
TITLE:
fix(template): cluster D code quality (interrogate, basedpyright, script complexity)

BODY:
## Summary

Resolves three confirmed code-quality issues in the generated project. Items 2 (sonar_scan.py) and 4 (qlty plugin syntax) were dropped from the original cluster D scope: PR #54 migrated SonarCloud to an org reusable workflow that supersedes the local-scan-script idea, and qlty.toml no longer uses [[plugin]] blocks.

## Changes

1. **pip-audit allowlist (item 1)**: added `[tool.pip-audit] ignore-vulns = ["PYSEC-2022-42969"]` to the generated pyproject.toml with an inline comment explaining the disputed-CVE rationale (SVN-only, dev-only).
2. **BasedPyright typing (items 2-3)**: added a `_get_context(ctx)` helper in cli.py that narrows `ctx.obj` to the existing `CLIContext` dataclass; replaced `Any` parameter and return types in logging.py with `BoundLogger` from `structlog.stdlib`. 5 warnings → 0.
3. **Script complexity refactor (item 4)**: split check_fips_compatibility.py's `visit_Call` (complexity 51) into per-category helpers; decomposed cleanup_conditional_files.py's 175-line main function (complexity 106) into per-feature helpers; extracted the duplicated `get_cruft_context()` into a new `scripts/_cleanup_shared.py` module shared with check_orphaned_files.py; extracted `_attach_optional_details` helper in exceptions.py for the repeated `if X: details[X] = X` pattern; dataclass-ified APIError's 7-parameter constructor while preserving backwards compatibility.
4. **Feedback file housekeeping**: 5 mis-categorized entries moved from cluster D to a new cluster E section so the feedback file matches the umbrella's taxonomy.

## Test plan

- [x] `uv run pytest tests/unit/` passes (90+ tests)
- [x] `cruft create --no-input` generates a project that passes `uv sync` and `uv run pytest`
- [x] `uv run basedpyright src/<slug>/cli.py src/<slug>/utils/logging.py` reports 0 warnings (was 5)
- [x] `uv run pip-audit` no longer flags PYSEC-2022-42969
- [x] `pre-commit run --all-files` passes for cluster-D-touched files

## References

- Spec: `docs/superpowers/specs/2026-05-20-template-cleanup-cluster-D-code-quality.md`
- Plan: `docs/superpowers/plans/2026-05-20-template-cleanup-cluster-D.md`
- Umbrella: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

Generated with [Claude Code](https://claude.com/claude-code)
```

DO NOT run `gh pr create`. Stop here and report the PR draft so the controller can authorize.

---

## Out of scope (deferred)

- Cluster E items (MD040, MD051, planning front matter, PROJECT_SETUP workflow table, qlty CLI documentation) — this PR re-categorizes them in the feedback file but does not work on them.
- Replacing interrogate with an alternative tool — this PR accepts the disputed CVE via allowlist; interrogate replacement is a separate decision.
- Removing the `py` transitive dependency — out of our control until interrogate releases a fix.
- OpenSSF baseline file changes (LICENSE, SECURITY.md, etc.) — untouched.

## Spec coverage self-check

| Spec requirement | Task |
|---|---|
| Component 1: pip-audit allowlist | Task 2 |
| Component 2: cli.py typing | Task 3 |
| Component 3: logging.py typing | Task 4 |
| Component 4a: check_fips_compatibility.py | Task 5 |
| Component 4b: cleanup_conditional_files + check_orphaned + _cleanup_shared | Task 6 |
| Component 4c: exceptions.py | Task 7 |
| Component 5: feedback file + umbrella | Task 8 |
| Acceptance: pre-commit, pytest, smoke | Task 9 |
| Feasibility condition: re-measure baseline | Task 1 |

All spec requirements covered. No placeholders remain.
