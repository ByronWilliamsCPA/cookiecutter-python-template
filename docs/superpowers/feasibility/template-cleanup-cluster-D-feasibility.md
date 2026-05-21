---
title: "Feasibility: Template Cleanup Cluster D (Code Quality)"
schema_type: common
status: published
owner: core-maintainer
purpose: "Feasibility assessment for cluster D of the template cleanup, covering interrogate CVE, BasedPyright typing, and script complexity refactors."
tags:
  - planning
---

# Feasibility: Template Cleanup Cluster D (Code Quality)

**Date:** 2026-05-20
**Verdict:** CONDITIONAL GO

## Analysis

**Core assumption:** The spec assumes all five BasedPyright warnings still exist and that `CLIContext` needs to become a `TypedDict`. This is verifiable right now: `CLIContext` is already a `@dataclass` (not a bare class), `BoundLogger` is already imported in both `cli.py` and `logging.py`, and `logging.py` already uses explicit `BoundLogger` annotations with `# pyright: ignore` suppression comments. The actual warning count and locations should be re-measured before implementation begins, since the files may already be partially fixed.

**Blocking dependencies:** None. All files exist, pip-audit 2.10.0 is installed, the worktree path convention is documented, and `_cleanup_shared.py` is a new file with no external dependency. The `py` package CVE suppression key (`ignore-vulns`) matches the installed pip-audit version.

**Minimum buildable version:** Component 1 (the pip-audit allowlist entry in `pyproject.toml`) is a single-line config change that independently eliminates a noisy audit failure and can ship as a standalone commit with no regression risk.

## Verdict rationale

CONDITIONAL GO. Build as scoped, but re-run `uv run basedpyright` on `cli.py` and `logging.py` before writing any typing code: `CLIContext` is already a dataclass with typed fields and both files already import `BoundLogger`, so components 2 and 3 may require only suppression-comment removal or minor annotation adjustments rather than the structural changes described. Confirm the actual residual warning list first to avoid over-engineering the typing fixes.

## Conditions for full GO

1. **Re-measure baseline before typing work.** Run `uv run basedpyright src/<slug>/cli.py src/<slug>/utils/logging.py` in a fresh generation and capture the exact line numbers and rule codes. Adjust the implementation plan's typing tasks to match what's actually needed (likely smaller scope than the spec described).
2. **Read existing CLIContext definition.** If it's already a dataclass with the right fields, the fix becomes "cast ctx.obj at access sites" rather than "introduce CLIContext from scratch."
3. **Read existing logging.py annotations and ignore comments.** Identify whether the residual warnings are mis-targeted ignores (wrong rule code) or genuine gaps.

These conditions add ~10 minutes of discovery to writing-plans; they do not block the cluster.
