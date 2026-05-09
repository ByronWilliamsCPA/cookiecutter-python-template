# Template Cleanup Cluster BA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land a single small PR that closes the three confirmed bugs surviving the 2026-05-09 smoke test: Dockerfile missing README.md in COPY, closing markdown fences with language tags across `.claude/`, and a stale branch-protection status check context expectation.

**Architecture:** Three independent fix-in-place edits plus one regression test for the fence-terminator class of bug. No new abstractions. The status check finding is documented as a deferred action for cluster C since the fix touches workflow names (a cluster-C concern) rather than just the protection script.

**Tech Stack:** Python 3.12, pytest, cruft/cookiecutter, Docker, ruff, basedpyright. The plan uses pytest for the regression test and standard markdown parsing (no external dependencies) for the fence-terminator detector.

---

## Spec references

- Design: `docs/superpowers/specs/2026-05-09-template-cleanup-cluster-BA-post-smoke.md`
- Feasibility: `docs/superpowers/feasibility/template-cleanup-cluster-BA-feasibility.md` (GO)
- Umbrella: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

## File structure

| File | Action | Responsibility |
|---|---|---|
| `tests/unit/test_template_markdown.py` | create | Regression test asserting no template-rendered markdown file has a closing fence with a language tag |
| `{{cookiecutter.project_slug}}/.claude/context/python-standards.md` | modify | Fix line 67 closing fence; possibly other lines after audit |
| Other files under `{{cookiecutter.project_slug}}/.claude/` and `{{cookiecutter.project_slug}}/docs/` | modify | Fix any closing fences with language tags found by the audit |
| `{{cookiecutter.project_slug}}/Dockerfile` | modify | Add `README.md` to the dependency COPY line at line 23 |
| `{{cookiecutter.project_slug}}/.dockerignore` | modify | Annotate the `README.md` line (already commented as required, but confirm wording) |
| `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py` | modify (comment only) | Document the verified context-to-workflow mapping; flag the "Dependency & Standards Validation" mismatch as a cluster-C TODO |
| `docs/template_feedback.md` | modify | Remove ~26 entries closed by this PR plus the smoke-test FIXED items |

## Branch and worktree

This PR should land on a fresh feature branch named `fix/template-post-smoke-cleanup`. If the implementing session is currently on `feat/wip-stash-review` (or any other working branch), create the cleanup branch from `main`:

```bash
git checkout main
git pull --ff-only origin main
git checkout -b fix/template-post-smoke-cleanup
```

If a worktree is desired (recommended), create one inside the project per the project CLAUDE.md convention:

```bash
git worktree add .worktrees/fix-template-post-smoke-cleanup -b fix/template-post-smoke-cleanup main
cd .worktrees/fix-template-post-smoke-cleanup
uv sync --all-extras
```

---

## Task 1: Fence terminator regression test and audit

**Files:**

- Create: `tests/unit/test_template_markdown.py`
- Modify: any files under `{{cookiecutter.project_slug}}/.claude/` or `{{cookiecutter.project_slug}}/docs/` whose closing fences have language tags

- [ ] **Step 1.1: Write the failing test**

Create `tests/unit/test_template_markdown.py`:

```python
"""Regression test for malformed markdown fence terminators in the template tree.

A CommonMark closing fence must be exactly three backticks with no language tag.
A closing fence that carries a language tag (e.g. ``` text) opens a new nested
block instead of closing the previous one, which corrupts rendering and Claude
Code context loading.
"""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "{{cookiecutter.project_slug}}"
SCAN_DIRS = [TEMPLATE_ROOT / ".claude", TEMPLATE_ROOT / "docs"]
FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]+)\s*$")


def _closing_fences_with_language_tag(path: Path) -> list[tuple[int, str]]:
    """Return (line_number, line_text) for closing fences that carry a language tag."""
    inside_block = False
    bad: list[tuple[int, str]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = FENCE_RE.match(raw)
        if not match:
            continue
        if not inside_block:
            inside_block = True
            continue
        bad.append((lineno, raw))
        inside_block = False
    return bad


def test_no_closing_fence_has_language_tag() -> None:
    offenders: list[str] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for md_path in scan_dir.rglob("*.md"):
            for lineno, text in _closing_fences_with_language_tag(md_path):
                offenders.append(f"{md_path}:{lineno}: {text}")
    assert not offenders, "Closing fences with language tag:\n" + "\n".join(offenders)
```

- [ ] **Step 1.2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_template_markdown.py -v`

Expected: FAIL with at least one offender at `{{cookiecutter.project_slug}}/.claude/context/python-standards.md:67` and possibly more.

- [ ] **Step 1.3: Capture the full offender list**

Run: `uv run pytest tests/unit/test_template_markdown.py -v 2>&1 | tee /tmp/fence-offenders.txt`

Expected: a single failed test whose assertion message lists every closing fence with a language tag in the template tree. Use this list as the work queue for Step 1.4.

- [ ] **Step 1.4: Fix each offender**

For every line in the offender list, open the file at the reported line number and replace the closing-fence-with-language-tag line with bare three-backticks:

```text
- ```text
+ ```
```

Use the Edit tool one file at a time. The first known offender is `{{cookiecutter.project_slug}}/.claude/context/python-standards.md:67`. The other offenders are determined at runtime from Step 1.3's output.

- [ ] **Step 1.5: Re-run the test to verify it passes**

Run: `uv run pytest tests/unit/test_template_markdown.py -v`

Expected: PASS.

- [ ] **Step 1.6: Commit**

```bash
git add tests/unit/test_template_markdown.py "{{cookiecutter.project_slug}}/.claude/" "{{cookiecutter.project_slug}}/docs/"
git commit -m "fix(template): repair closing markdown fences with language tags

A CommonMark closing fence with a language tag opens a nested block instead
of closing the previous one. This corrupts Claude Code context loading for
files under .claude/. Add a regression test that scans .claude/ and docs/
for the pattern, and repair the offending lines.
"
```

---

## Task 2: Dockerfile README copy

**Files:**

- Modify: `{{cookiecutter.project_slug}}/Dockerfile:23`
- Modify: `{{cookiecutter.project_slug}}/.dockerignore:159` (comment only)
- Test: smoke test via `cruft create` and `docker build`

- [ ] **Step 2.1: Edit the Dockerfile to include README.md in the dependency COPY**

Replace `{{cookiecutter.project_slug}}/Dockerfile` line 23:

```dockerfile
- COPY pyproject.toml uv.lock ./
+ # README.md is required because pyproject.toml references it via [project] readme
+ COPY pyproject.toml uv.lock README.md ./
```

Both files stay on the same `COPY` instruction so Docker's layer cache for the dependency resolution remains keyed off `pyproject.toml + uv.lock + README.md`. README.md changes invalidate the layer (acceptable for releases) but keep the cached layer intact for code-only changes.

- [ ] **Step 2.2: Annotate `.dockerignore` so future maintainers do not re-add README.md**

Open `{{cookiecutter.project_slug}}/.dockerignore` and find line 159. If the existing entry is a bare `README.md` line, replace with a commented form that explains why it is intentionally NOT excluded:

```dockerignore
- README.md
+ # README.md - intentionally not excluded; required by pyproject.toml [project] readme
+ # so `uv sync --frozen --no-dev` (Dockerfile:34) can install the project itself.
```

If `.dockerignore` already contains the explanatory comment from a prior partial fix, leave it alone and verify the comment matches the wording above.

- [ ] **Step 2.3: Smoke test the change with cruft + docker build**

Run:

```bash
SMOKE=$(mktemp -d /tmp/template-docker-smoke.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template --no-input \
  --extra-context '{"include_docker": "yes"}'
cd "$SMOKE/my_python_project"
grep -n "README\|COPY pyproject" Dockerfile
# expected: COPY pyproject.toml uv.lock README.md ./
docker build -t template-smoke-test:cluster-BA .
```

Expected: docker build completes through `RUN uv sync --frozen --no-dev` (Dockerfile line 34) without `OSError: Readme file does not exist`.

If docker is unavailable on the implementing machine, fall back to:

```bash
cd "$SMOKE/my_python_project"
test -f README.md && echo "README.md present in generated project"
grep -n "README" Dockerfile
```

This minimum check confirms the COPY line includes README.md. Note in the PR description that `docker build` was not run locally and CI will verify.

- [ ] **Step 2.4: Clean up the smoke directory**

Run: `rm -rf "$SMOKE"`

- [ ] **Step 2.5: Commit**

```bash
git add "{{cookiecutter.project_slug}}/Dockerfile" "{{cookiecutter.project_slug}}/.dockerignore"
git commit -m "fix(template): copy README.md into Docker build context

uv sync --frozen --no-dev (Dockerfile line 34) installs the project itself
and reads pyproject.toml's [project] readme reference. Without README.md in
the build context, the install fails with OSError: Readme file does not
exist. Include README.md on the same COPY line as pyproject.toml + uv.lock
to preserve dependency-resolution layer caching, and annotate .dockerignore
so future maintainers do not re-exclude README.md.
"
```

---

## Task 3: Branch-protection status check verification (read-only)

**Files:**

- Modify (comment only): `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py`

The protection script declares four required status check contexts: `"CI Gate"`, `"Security Gate Validation"`, `"Dependency & Standards Validation"`, `"Check REUSE Compliance"`. Cluster BA's design specifies a one-time spot-verification of the three names other than `"CI Gate"` (which the project's discovery already confirmed matches `ci.yml`'s `ci-gate` job).

The 2026-05-09 discovery already established:

- `security-analysis.yml` has a job `name: Security Gate Validation`. **MATCHES.**
- `reuse.yml` has a job `name: Check REUSE Compliance`. **MATCHES.**
- `pr-validation.yml` jobs are named "Core Validation", "Dead Code Check", "Changelog Check", "Documentation Links". **NO match for "Dependency & Standards Validation".**

The mismatch resolution requires a decision (rename a workflow job, add a new aggregation job, or drop the context). Cluster C owns the wider branch-protection compliance scope (`sole_contributor`, `PROJECT_SETUP.md` documentation of the script). Cluster BA records the finding and defers the resolution to cluster C.

- [ ] **Step 3.1: Re-run the verification grep against the current template state**

Run:

```bash
echo "=== ci.yml (expected: CI Gate) ==="
grep -E "^\s+name:" "{{cookiecutter.project_slug}}/.github/workflows/ci.yml" | head -10
echo ""
echo "=== security-analysis.yml (expected: Security Gate Validation) ==="
grep -E "^\s+name:" "{{cookiecutter.project_slug}}/.github/workflows/security-analysis.yml" | head -10
echo ""
echo "=== pr-validation.yml (expected: Dependency & Standards Validation) ==="
grep -E "^\s+name:" "{{cookiecutter.project_slug}}/.github/workflows/pr-validation.yml" | head -15
echo ""
echo "=== reuse.yml (expected: Check REUSE Compliance) ==="
grep -E "^\s+name:" "{{cookiecutter.project_slug}}/.github/workflows/reuse.yml" | head -10
```

Capture the output. Expected: three matches and one mismatch (pr-validation.yml has no "Dependency & Standards Validation" job).

- [ ] **Step 3.2: Annotate the protection script with the verification result**

Open `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py` and find the existing comment block above the `protection = {` literal (around line 162-168). Replace the comment block with verification dates and explicit mismatch flag:

```python
# Status check contexts match the job name: field in each workflow file.
# GitHub Actions records checks using the job display name (not "Workflow / Job").
#
# Verified 2026-05-09 against generated workflows:
#   - ci.yml -> "CI Gate" (job ci-gate). MATCHES.
#   - security-analysis.yml -> "Security Gate Validation". MATCHES.
#   - reuse.yml -> "Check REUSE Compliance". MATCHES.
#   - pr-validation.yml -> "Dependency & Standards Validation". NO MATCH;
#     pr-validation.yml currently has Core Validation, Dead Code Check,
#     Changelog Check, Documentation Links. Resolution deferred to cluster
#     C (see docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md).
#
# To re-verify: run the steps in
# docs/superpowers/plans/2026-05-09-template-cleanup-cluster-BA.md Task 3.
```

Do NOT change the `contexts` list itself in this PR. Cluster C will choose between renaming a pr-validation.yml job and editing the script's contexts.

- [ ] **Step 3.3: Commit**

```bash
git add "{{cookiecutter.project_slug}}/scripts/setup_github_protection.py"
git commit -m "docs(scripts): record branch-protection status check verification

Document the 2026-05-09 verification of required_status_checks.contexts
against generated workflow job names. Three contexts match. The fourth
('Dependency & Standards Validation' against pr-validation.yml) does not
match any current job name. Resolution deferred to cluster C of the
template-cleanup umbrella, which owns wider branch-protection scope.
"
```

---

## Task 4: Trim the feedback file

**Files:**

- Modify: `docs/template_feedback.md`

This task removes feedback entries that are now FIXED or REDIRECTED, leaving the file aligned to clusters C, D, E only.

- [ ] **Step 4.1: List the entries to remove**

Reference: `docs/superpowers/specs/2026-05-09-template-cleanup-audit.md` (FIXED and REDIRECTED tables) plus the umbrella's Status log entry for the smoke-test reductions.

Entries to remove from `docs/template_feedback.md`:

Already-FIXED at the time of audit (16 entries):

- VM RTC Mode Should Be Explicitly Set Post-Provision (REDIRECT, leaves file with note)
- VM Provisioning Should Ship Default `NTP=...` Drop-In (REDIRECT)
- OpenClaw Session Checkpoint Retention Policy (REDIRECT)
- Compliance Auditor Adds Invalid qlty Plugin (basedpyright)
- Pre-commit TruffleHog Entry Causes YAML Syntax Error
- Documentation Files Missing Required YAML Front Matter (DETAILED) -- partial; keep "planning subset" reference for cluster E
- Qlty Plugin Definition Not Found for Ruff -- superseded by cluster D's qlty plugin syntax item
- CLAUDE.md Should Enforce Security-First Approach
- Unparsed Cookiecutter Variables in .claude/ Directory Files
- PROJECT_SETUP.md Uses `master` in Git Push Command
- Repository URL Uses Underscore Instead of Hyphen
- Ruff Configuration Includes Deprecated Rules
- CLAUDE.md Missing Branch Workflow Instruction
- Template Uses `master` Instead of `main` as Default Branch
- CLAUDE.md Generated in Wrong Location
- Missing LICENSES/ Directory for REUSE Compliance
- scripts/generate_requirements.sh Missing Execute Permission
- MkDocs Nav References Non-Existent Documentation Files
- CI Failures: Invalid setup-uv SHA and Local Template Path -- both fixes (SHA pinning to @v7 and .cruft.json URL handling) confirmed
- Python Compatibility Matrix Workflow Has JSON Output Format Error -- workflow now uses YAML matrix literal
- Generated Files Missing Trailing Newlines -- smoke test confirmed FIXED

Closed by this PR:

- Broken Fenced Code Block Closings: "text" Tag Used as Fence Terminator
- Dockerfile Build Fails: README.md Not Available During uv sync
- Branch Protection Status Check Names Don't Match Workflows -- partial close: documented; resolution deferred

REDIRECTED for items already separately listed: ensure the three VM/infra items are removed and the file's preamble contains a note pointing to homelab-infra for those.

- [ ] **Step 4.2: Edit `docs/template_feedback.md` to remove the listed entries**

Use the Edit tool. For each entry to remove, locate its `### ...` header and delete from that header through the next `### ...` header (exclusive). Do not delete the file's front matter or the top-level `## Feedback Items` header and intro.

After deletion, the file should retain only entries for cluster C (community_health_style, sole_contributor, .editorconfig, branch-protection script documentation, and the deferred "Dependency & Standards Validation" mismatch as a cross-reference), cluster D (interrogate replacement, sonar_scan.py, basedpyright warnings, script complexity, qlty plugin syntax), and cluster E (planning/index.md, MD040, MD051, planning front matter subset, PROJECT_SETUP workflow table, qlty CLI mention).

- [ ] **Step 4.3: Add a brief preamble note documenting the 2026-05-09 cleanup**

Insert this note immediately after the `> This file captures...` blockquote (before `## Feedback Items`):

````markdown
> **Cleanup 2026-05-09:** ~26 entries were removed in PR `fix/template-post-smoke-cleanup`
> after a smoke test confirmed they are FIXED, REDIRECTED to homelab-infra (NTP, RTC,
> OpenClaw retention), or closed by that PR. Remaining entries align to clusters C, D,
> E of the template-cleanup umbrella at
> `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`.
````

- [ ] **Step 4.4: Commit**

```bash
git add docs/template_feedback.md
git commit -m "docs(feedback): remove FIXED and REDIRECTED entries after cluster BA

26 entries are now closed: 16 confirmed FIXED in the 2026-05-09 audit, 6
confirmed FIXED by the smoke test, 1 REDIRECTED (cruft check default lives
in external org workflow), and 3 closed by this PR (Dockerfile README copy,
fence terminators, status check verification). 3 VM/infra items are
redirected to homelab-infra. Remaining entries align to clusters C, D, E.
"
```

---

## Task 5: Final acceptance checks

- [ ] **Step 5.1: Run pre-commit on the full diff**

```bash
pre-commit run --all-files
```

Expected: PASS. If anything fails, fix the underlying cause (do NOT pass `--no-verify`).

- [ ] **Step 5.2: Run the new regression test plus the existing test suite**

```bash
uv run pytest tests/unit/test_template_markdown.py tests/unit/test_hooks.py tests/unit/test_generation.py -v
```

Expected: PASS for all three files.

- [ ] **Step 5.3: Run a final cruft create smoke test for sanity**

```bash
SMOKE=$(mktemp -d /tmp/template-final-smoke.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template --no-input
cd "$SMOKE/my_python_project"
test -f CLAUDE.md && echo "CLAUDE.md OK"
git symbolic-ref --short HEAD
cd /home/byron/dev/cookiecutter-python-template
rm -rf "$SMOKE"
```

Expected: CLAUDE.md present, default branch is `main`, no Jinja errors during generation.

- [ ] **Step 5.4: Push and open the PR**

```bash
git push -u origin fix/template-post-smoke-cleanup
gh pr create --title "fix(template): post-smoke-test cleanup (Dockerfile README + fence terminators + status check verification)" --body "$(cat <<'EOF'
## Summary

Closes the three confirmed bugs surviving the 2026-05-09 smoke test that resolved 6
items from `docs/template_feedback.md` as already-FIXED.

## Changes

1. **Fence terminators**: regression test in `tests/unit/test_template_markdown.py`
   plus repairs to closing fences with language tags across `.claude/` and `docs/`
   in the template tree.
2. **Dockerfile**: `COPY pyproject.toml uv.lock ./` -> `COPY pyproject.toml uv.lock README.md ./`
   with `.dockerignore` annotation explaining why README.md must remain in the build
   context.
3. **Branch-protection status checks**: documented in `setup_github_protection.py` that
   three of four contexts match generated workflow job names. The fourth
   ("Dependency & Standards Validation" vs `pr-validation.yml`) does not match; the
   resolution is deferred to cluster C of the template-cleanup umbrella.
4. **Feedback file**: 26 entries removed (16 audit-FIXED, 6 smoke-test-FIXED, 1
   REDIRECTED, 3 closed by this PR), 3 VM/infra items redirected to homelab-infra.

## Test plan

- [x] `uv run pytest tests/unit/test_template_markdown.py` passes
- [x] `cruft create --extra-context '{"include_docker": "yes"}'` followed by
      `docker build .` succeeds
- [x] `cruft create --no-input` produces a valid project on `main` branch
- [x] `pre-commit run --all-files` passes
- [x] No closing markdown fence in `.claude/` or `docs/` carries a language tag

## References

- Spec: `docs/superpowers/specs/2026-05-09-template-cleanup-cluster-BA-post-smoke.md`
- Plan: `docs/superpowers/plans/2026-05-09-template-cleanup-cluster-BA.md`
- Umbrella: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: PR opens with the body above and the four-commit history (Task 1, 2, 3, 4) plus optional Task 5 amendments visible.

---

## Out of scope (deferred to other clusters)

- All other items in `docs/template_feedback.md` not closed above.
- Cruft check default in external `python-supplemental-checks.yml` (REDIRECTED to org `.github` repo).
- Resolution of the "Dependency & Standards Validation" status check name mismatch (cluster C).
- BasedPyright cleanup, `interrogate` replacement, sonar_scan.py, script complexity (cluster D).
- MD040, MD051, planning front matter, PROJECT_SETUP workflow table completeness (cluster E).
