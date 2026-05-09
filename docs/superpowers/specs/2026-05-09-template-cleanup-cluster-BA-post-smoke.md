# Cluster BA: Post-Smoke-Test Cleanup Design

> **Parent**: `2026-05-09-template-cleanup-umbrella.md`
> **Status**: design pending review
> **Scope**: 3 items merged from original clusters B (CI stability) and A (generation correctness) after the 2026-05-09 smoke test reduced both clusters to one bug each.

## Goal

Land a small, low-risk PR that closes the only confirmed-OPEN items from clusters B and A. After this PR merges, the template's CI-blocking and generation-blocking bugs surfaced in `docs/template_feedback.md` are exhausted, and remaining work is concentrated in clusters C, D, E (compliance, code quality, docs).

## Items in scope

### 1. Dockerfile missing `README.md` in `COPY` line

**File**: `{{cookiecutter.project_slug}}/Dockerfile` line 23

**Current**:

```dockerfile
COPY pyproject.toml uv.lock ./
```

**Problem**: When `include_docker=yes`, `pyproject.toml` declares the project's README via dynamic metadata or `[project] readme = "README.md"`, and `RUN uv sync --frozen --no-dev` (line 34, second sync, installs the project itself) fails with `OSError: Readme file does not exist: README.md`. The first sync at line 28 has `--no-install-project` so it's unaffected; the failure is specifically the second sync.
**Fix**: change to `COPY pyproject.toml uv.lock README.md ./`. Also remove `README.md` from `.dockerignore` (or add a comment explaining it must remain in build context). Do **not** add `README.md` to a separate COPY line: keeping it on the same line preserves Docker's layer caching for dependency resolution.
**Original feedback dates**: 2025-12-01

### 2. Fence terminator with `text` language tag

**File**: `{{cookiecutter.project_slug}}/.claude/context/python-standards.md:67` (and possibly more files)
**Current**: line 67 closes a fenced code block with three-backticks-then-`text`.
**Problem**: Closing fences in CommonMark must be a bare three-backticks. A closing fence with a language tag opens a new nested block, breaking parser rendering and Claude Code context loading.
**Fix**: replace any closing fence that has a language tag with a bare three-backticks. Approach:

- Run a repo-wide grep for `^.{3}[a-z]+$` (regex anchoring three-backticks then lowercase identifier then end-of-line) across `{{cookiecutter.project_slug}}/.claude/`, `{{cookiecutter.project_slug}}/docs/`, and any other rendered markdown.
- For each match, inspect context: if it is closing a previously-opened fence, replace with bare three-backticks. If it is opening a new fence, leave alone.
- The `text` case is the most common; the same audit will catch any `bash`, `python`, etc. that snuck in as a fence terminator.

**Original feedback date**: 2026-04-14

### 3. Branch-protection status check name spot-verification

**File**: `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py` lines 173-180
**Current**: defines four required status check contexts: `"CI Gate"`, `"Security Gate Validation"`, `"Dependency & Standards Validation"`, `"Check REUSE Compliance"`.
**Problem**: feedback (2025-01-22) reported these names did not match actual workflow job display names. The `ci.yml` job `ci-gate` confirms `name: CI Gate` already, suggesting the script author rewrote the contexts since the feedback. The other three need confirmation.
**Fix**: load the generated workflows under `{{cookiecutter.project_slug}}/.github/workflows/` and read the `jobs.<id>.name` field for the gate jobs in `security-analysis.yml`, `pr-validation.yml`, and `reuse.yml`. Compare to the four contexts. If any mismatch:

- Prefer renaming the workflow `name:` field if the new name is more descriptive.
- Otherwise update the script's `contexts` list.
- Add a one-line comment in the script citing the workflow file each context comes from.

If all four match: this item is FIXED with no code change; record verification in the PR description.

**Original feedback date**: 2025-01-22

## Architecture

No architectural changes. Three independent edits, no shared state, no new abstractions. Each item is a fix-in-place.

## Testing

- **Item 1 (Dockerfile)**: `cruft create` with `include_docker=yes`, then `docker build .` in the generated project. Expect successful build through stage-1 `RUN uv sync --frozen --no-dev` at line 34. Revert the fix and confirm the failure mode reproduces (regression evidence).
- **Item 2 (fence terminator)**: regex sweep before and after the fix. After fix, expect zero matches. Render the affected file in a markdown previewer and confirm no nested-block artifacts.
- **Item 3 (status check names)**: read-only verification. If any rename is made, regenerate the project and re-grep both `protection["required_status_checks"]["contexts"]` and the workflows' `name:` fields to confirm string equality.

No new tests. The existing `tests/test_post_gen_hooks.py` covers the post-generation behavior; this PR does not change post-gen logic.

## Implementation order within the PR

1. Sweep for fence terminators (item 2): reading-only first to enumerate all sites, then a single batched edit pass.
2. Dockerfile fix (item 1): single line change plus `.dockerignore` annotation.
3. Status check name verification (item 3): read-only first; only edit if a mismatch is found.

This order minimizes risk: item 2 may touch many files but is mechanical; item 1 is a one-line change that the smoke test validates immediately; item 3 may be a no-op.

## Out of this PR (deferred to other clusters)

- Cruft check default in external reusable workflow (REDIRECTED to org `.github` repo).
- All cluster C items (`.editorconfig`, `community_health_style`, `sole_contributor`, missing `planning/index.md`, branch-protection script docs in `PROJECT_SETUP.md`).
- All cluster D items (`interrogate` replacement, `sonar_scan.py`, basedpyright warning cleanup, script complexity refactors).
- All cluster E items (MD040/MD051, front matter on planning subset, PROJECT_SETUP workflow table completeness, qlty CLI mention).

## Acceptance criteria

A PR titled `fix(template): post-smoke-test cleanup (Dockerfile README + fence terminator + status checks)` lands on `main` with:

- [ ] `cruft create --no-input --extra-context '{"include_docker": "yes"}'` followed by `docker build .` succeeds.
- [ ] `grep -rEn '^.{3}[a-z]+$' {{cookiecutter.project_slug}}/.claude/ {{cookiecutter.project_slug}}/docs/` returns zero matches that are closing fences (matches that are opening fences are fine).
- [ ] PR description includes the verification result for each of the four branch-protection status check contexts.
- [ ] `docs/template_feedback.md` is edited in the same PR to remove (a) the three items closed by this PR, (b) the six items confirmed FIXED by the 2026-05-09 smoke test (per umbrella `Status log`), (c) the one item REDIRECTED to the org `.github` repo, and (d) the 16 items the audit already marked FIXED. Total removable: ~26 entries plus the three out-of-template VM items already redirected. The remaining feedback file should be aligned to clusters C, D, E only.

## Notes for the implementing session

- The `docs/template_feedback.md` cleanup at the end is part of the working agreement in the umbrella; do not skip it.
- The smoke-test resolution evidence for the 16 already-FIXED items is in the umbrella's `Status log` and the audit table; reference those rather than re-running the smoke test.
- If item 3 (status check names) turns out to need an edit, prefer the workflow-rename direction over the script-edit direction: workflow names are user-facing in GitHub's UI.
