# Cluster E: Docs Build and MkDocs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 9 MD040 violations, create the missing `docs/planning/index.md`, add the `qlty.yml` CI workflow to generated projects, document Qlty in `PROJECT_SETUP.md`, and annotate three stale feedback entries as resolved; this closes the template-cleanup umbrella.

**Architecture:** All changes are template file edits (files under `{{cookiecutter.project_slug}}/`) plus repo-level docs updates. No Python code changes. The `qlty.yml` addition requires no cleanup hook changes because `include_github_actions == "no"` already removes the entire `.github/workflows/` directory. Changes ship as a single PR from branch `feat/cluster-E-docs`.

**Tech Stack:** Cookiecutter, Jinja2 templating, GitHub Actions (reusable workflow caller), MkDocs Material, markdownlint (MD040)

**Spec:** `docs/superpowers/specs/2026-05-23-template-cleanup-cluster-E-docs.md`

---

## Task 0: Worktree Setup

**Files:**
- Create: `.worktrees/cluster-E-docs/` (git worktree)

- [ ] **Step 1: Create the worktree and branch**

```bash
git worktree add .worktrees/cluster-E-docs -b feat/cluster-E-docs
```

Expected: `Preparing worktree (new branch 'feat/cluster-E-docs')`

- [ ] **Step 2: Sync dependencies in the worktree**

```bash
cd .worktrees/cluster-E-docs && uv sync
```

Expected: `All packages are already installed` (or brief install output)

---

## Task 1: MD040 Fix `docs/development/` Files

**Files:**
- Modify: `{{cookiecutter.project_slug}}/docs/development/architecture.md:16`
- Modify: `{{cookiecutter.project_slug}}/docs/development/testing.md:40`

- [ ] **Step 1: Confirm violations exist**

```bash
cd .worktrees/cluster-E-docs
python3 -c "
import re
for path in [
    '{{cookiecutter.project_slug}}/docs/development/architecture.md',
    '{{cookiecutter.project_slug}}/docs/development/testing.md',
]:
    with open(path) as f: lines = f.readlines()
    in_block = False
    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if s == '\`\`\`':
            if not in_block: print(f'{path}:{i} VIOLATION')
            in_block = not in_block
        elif re.match(r'\`\`\`\w', s): in_block = True if not in_block else in_block; in_block = True
"
```

Expected output:
```
{{cookiecutter.project_slug}}/docs/development/architecture.md:16 VIOLATION
{{cookiecutter.project_slug}}/docs/development/testing.md:40 VIOLATION
```

- [ ] **Step 2: Fix `architecture.md`: add `text` tag at line 16**

Edit `{{cookiecutter.project_slug}}/docs/development/architecture.md`.

Find (line 16, the unlabeled opening fence that starts the directory-tree block):
```
```
```
Replace with:
```
```text
```

- [ ] **Step 3: Fix `testing.md`: add `text` tag at line 40**

Edit `{{cookiecutter.project_slug}}/docs/development/testing.md`.

Find (line 40, the unlabeled opening fence that starts the test-directory tree):
```
```
```
Replace with:
```
```text
```

- [ ] **Step 4: Verify both violations are gone**

```bash
python3 -c "
import re
for path in [
    '{{cookiecutter.project_slug}}/docs/development/architecture.md',
    '{{cookiecutter.project_slug}}/docs/development/testing.md',
]:
    with open(path) as f: lines = f.readlines()
    in_block = False
    violations = []
    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if s == '\`\`\`':
            if not in_block: violations.append(i)
            in_block = not in_block
        elif re.match(r'\`\`\`\w', s):
            if not in_block: in_block = True
    if violations: print(f'FAIL {path}: violations at {violations}')
    else: print(f'PASS {path}')
"
```

Expected:
```
PASS {{cookiecutter.project_slug}}/docs/development/architecture.md
PASS {{cookiecutter.project_slug}}/docs/development/testing.md
```

- [ ] **Step 5: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add '{{cookiecutter.project_slug}}/docs/development/architecture.md' \
        '{{cookiecutter.project_slug}}/docs/development/testing.md'
git commit -m "fix(template): add text language tag to unlabeled fences in development docs"
```

---

## Task 2: MD040 Fix `docs/planning/` Files

**Files:**
- Modify: `{{cookiecutter.project_slug}}/docs/planning/project-plan-template.md:78,115`
- Modify: `{{cookiecutter.project_slug}}/docs/planning/README.md:46,57,75`

- [ ] **Step 1: Confirm violations exist**

```bash
python3 -c "
import re
for path in [
    '{{cookiecutter.project_slug}}/docs/planning/project-plan-template.md',
    '{{cookiecutter.project_slug}}/docs/planning/README.md',
]:
    with open(path) as f: lines = f.readlines()
    in_block = False
    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if s == '\`\`\`':
            if not in_block: print(f'{path}:{i} VIOLATION')
            in_block = not in_block
        elif re.match(r'\`\`\`\w', s):
            if not in_block: in_block = True
"
```

Expected output:
```
{{cookiecutter.project_slug}}/docs/planning/project-plan-template.md:78 VIOLATION
{{cookiecutter.project_slug}}/docs/planning/project-plan-template.md:115 VIOLATION
{{cookiecutter.project_slug}}/docs/planning/README.md:46 VIOLATION
{{cookiecutter.project_slug}}/docs/planning/README.md:57 VIOLATION
{{cookiecutter.project_slug}}/docs/planning/README.md:75 VIOLATION
```

- [ ] **Step 2: Fix `project-plan-template.md` line 78, ASCII component-box diagram**

Edit `{{cookiecutter.project_slug}}/docs/planning/project-plan-template.md`.

Find (line 78):
```
```
[Describe the overall system design]
```
Replace the opening fence with:
```
```text
[Describe the overall system design]
```

- [ ] **Step 3: Fix `project-plan-template.md` line 115, arrow data-flow diagram**

In the same file, find (line 115, after the edit in Step 2 line numbers may shift by 0; the fence is the one that opens the `Input → Processing → Output` block):

```
```
Input → Processing → Output
```
Replace the opening fence with:
```
```text
Input → Processing → Output
```

- [ ] **Step 4: Fix `planning/README.md` line 46, Claude prompt template**

Edit `{{cookiecutter.project_slug}}/docs/planning/README.md`.

Find (line 46, the fence that opens the `Load context from:` block):
```
```
Load context from:
```
Replace the opening fence with:
```
```text
Load context from:
```

- [ ] **Step 5: Fix `planning/README.md` line 57, second Claude prompt template**

In the same file, find (line 57, the fence that opens the `Review this code against:` block):
```
```
Review this code against:
```
Replace the opening fence with:
```
```text
Review this code against:
```

- [ ] **Step 6: Fix `planning/README.md` line 75, document-relationships ASCII diagram**

In the same file, find (line 75, the fence that opens the `┌─────────────────────────────┐` block):
```
```
┌─────────────────────────────┐
```
Replace the opening fence with:
```
```text
┌─────────────────────────────┐
```

- [ ] **Step 7: Verify all five violations are gone**

```bash
python3 -c "
import re
for path in [
    '{{cookiecutter.project_slug}}/docs/planning/project-plan-template.md',
    '{{cookiecutter.project_slug}}/docs/planning/README.md',
]:
    with open(path) as f: lines = f.readlines()
    in_block = False
    violations = []
    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if s == '\`\`\`':
            if not in_block: violations.append(i)
            in_block = not in_block
        elif re.match(r'\`\`\`\w', s):
            if not in_block: in_block = True
    if violations: print(f'FAIL {path}: violations at {violations}')
    else: print(f'PASS {path}')
"
```

Expected:
```
PASS {{cookiecutter.project_slug}}/docs/planning/project-plan-template.md
PASS {{cookiecutter.project_slug}}/docs/planning/README.md
```

- [ ] **Step 8: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add '{{cookiecutter.project_slug}}/docs/planning/project-plan-template.md' \
        '{{cookiecutter.project_slug}}/docs/planning/README.md'
git commit -m "fix(template): add text language tag to unlabeled fences in planning docs"
```

---

## Task 3: MD040 Fix `README.md`

**Files:**
- Modify: `{{cookiecutter.project_slug}}/README.md:465,587`

- [ ] **Step 1: Confirm violations exist**

```bash
python3 -c "
import re
path = '{{cookiecutter.project_slug}}/README.md'
with open(path) as f: lines = f.readlines()
in_block = False
for i, line in enumerate(lines, 1):
    s = line.rstrip()
    if s == '\`\`\`':
        if not in_block: print(f'{path}:{i} VIOLATION')
        in_block = not in_block
    elif re.match(r'\`\`\`\w', s):
        if not in_block: in_block = True
"
```

Expected:
```
{{cookiecutter.project_slug}}/README.md:465 VIOLATION
{{cookiecutter.project_slug}}/README.md:587 VIOLATION
```

- [ ] **Step 2: Fix line 465, `.claude/` directory tree**

Edit `{{cookiecutter.project_slug}}/README.md`.

Find (line 465, the fence opening a `.claude/` directory listing):
```
```
.claude/
```
Replace the opening fence with:
```
```text
.claude/
```

- [ ] **Step 3: Fix line 587, project structure tree**

In the same file, find (line 587, the fence opening the `{{cookiecutter.project_slug}}/` directory listing):
```
```
{{cookiecutter.project_slug}}/
```
Replace the opening fence with:
```
```text
{{cookiecutter.project_slug}}/
```

- [ ] **Step 4: Verify no violations remain**

```bash
python3 -c "
import re
path = '{{cookiecutter.project_slug}}/README.md'
with open(path) as f: lines = f.readlines()
in_block = False; violations = []
for i, line in enumerate(lines, 1):
    s = line.rstrip()
    if s == '\`\`\`':
        if not in_block: violations.append(i)
        in_block = not in_block
    elif re.match(r'\`\`\`\w', s):
        if not in_block: in_block = True
print('FAIL violations at', violations) if violations else print('PASS')
"
```

Expected: `PASS`

- [ ] **Step 5: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add '{{cookiecutter.project_slug}}/README.md'
git commit -m "fix(template): add text language tag to unlabeled fences in README"
```

---

## Task 4: Create `docs/planning/index.md`

**Files:**
- Create: `{{cookiecutter.project_slug}}/docs/planning/index.md`

- [ ] **Step 1: Confirm the file does not exist**

```bash
ls '{{cookiecutter.project_slug}}/docs/planning/index.md' 2>/dev/null \
  && echo "EXISTS: stop, investigate" \
  || echo "CONFIRMED ABSENT: proceed"
```

Expected: `CONFIRMED ABSENT: proceed`

- [ ] **Step 2: Create the file**

Create `{{cookiecutter.project_slug}}/docs/planning/index.md` with this exact content:

````markdown
---
title: "{{ cookiecutter.project_name }} - Planning"
schema_type: planning
status: draft
owner: core-maintainer
purpose: "Index and navigation for project planning documents."
tags: [planning, index]
component: Strategy
source: "/plan command generation"
---

> **Status**: Awaiting Generation

---

## Planning Documents

This directory contains the four core planning documents generated by the `/plan`
Claude Code skill. Together they form the complete project blueprint for
`{{ cookiecutter.project_name }}`.

| Document | Purpose |
|----------|---------|
| [project-vision.md](project-vision.md) | Project vision, scope, and success metrics |
| [tech-spec.md](tech-spec.md) | Technical architecture and implementation details |
| [roadmap.md](roadmap.md) | Phased development roadmap and milestones |
| [project-plan-template.md](project-plan-template.md) | Synthesized project plan with phase breakdown |

See the [Project Setup Guide](../PROJECT_SETUP.md#project-planning-with-claude-code)
for instructions on generating these documents.
````

- [ ] **Step 3: Verify front matter is valid**

```bash
python3 -c "
import yaml, re
with open('{{cookiecutter.project_slug}}/docs/planning/index.md') as f:
    content = f.read()
# Strip Jinja2 before parsing
cleaned = re.sub(r'\{\{.*?\}\}', 'PLACEHOLDER', content)
match = re.match(r'^---\n(.*?)\n---', cleaned, re.DOTALL)
if not match: raise SystemExit('FAIL: no front matter found')
fm = yaml.safe_load(match.group(1))
required = {'title', 'schema_type', 'status', 'owner', 'purpose', 'tags', 'component', 'source'}
missing = required - set(fm.keys())
if missing: raise SystemExit(f'FAIL: missing keys {missing}')
print('PASS: front matter valid, keys:', list(fm.keys()))
"
```

Expected: `PASS: front matter valid, keys: ['title', 'schema_type', 'status', 'owner', 'purpose', 'tags', 'component', 'source']`

- [ ] **Step 4: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add '{{cookiecutter.project_slug}}/docs/planning/index.md'
git commit -m "feat(template): add missing docs/planning/index.md with front matter"
```

---

## Task 5: Add `qlty.yml` Workflow to Generated Project

**Files:**
- Create: `{{cookiecutter.project_slug}}/.github/workflows/qlty.yml`

No cleanup-hook changes are needed: when `include_github_actions == "no"`, the post-gen hook already removes the entire `.github/workflows/` directory, so `qlty.yml` is automatically excluded.

- [ ] **Step 1: Confirm the file does not exist in the template**

```bash
ls '{{cookiecutter.project_slug}}/.github/workflows/qlty.yml' 2>/dev/null \
  && echo "EXISTS: stop, investigate" \
  || echo "CONFIRMED ABSENT: proceed"
```

Expected: `CONFIRMED ABSENT: proceed`

- [ ] **Step 2: Create `qlty.yml`**

Create `{{cookiecutter.project_slug}}/.github/workflows/qlty.yml` with this exact content:

```yaml
name: Qlty

on:
  workflow_run:
    workflows: ["CI"]
    types:
      - completed

permissions: read-all

concurrency:
  group: qlty-coverage-${{ github.event.workflow_run.head_branch }}
  cancel-in-progress: true

jobs:
  qlty:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    uses: ByronWilliamsCPA/.github/.github/workflows/python-qlty-coverage.yml@1b2d33c47cc11a96b9757b49f41873c54e75f57c  # main
    permissions:
      contents: read
      actions: read
    with:
      coverage-artifact-name: coverage-reports
      coverage-file-path: coverage.xml
      coverage-format: cobertura
      workflow-run-id: ${{ github.event.workflow_run.id }}
    secrets:
      QLTY_COVERAGE_TOKEN: ${{ secrets.QLTY_COVERAGE_TOKEN }}
```

- [ ] **Step 3: Verify the file is valid YAML**

```bash
python3 -c "
import yaml
with open('{{cookiecutter.project_slug}}/.github/workflows/qlty.yml') as f:
    doc = yaml.safe_load(f)
assert doc['name'] == 'Qlty', 'name field wrong'
assert 'CI' in doc['on']['workflow_run']['workflows'], 'trigger wrong'
assert 'qlty' in doc['jobs'], 'job missing'
print('PASS: qlty.yml is valid YAML with correct structure')
"
```

Expected: `PASS: qlty.yml is valid YAML with correct structure`

- [ ] **Step 4: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add '{{cookiecutter.project_slug}}/.github/workflows/qlty.yml'
git commit -m "feat(template): add qlty.yml coverage workflow to generated project"
```

---

## Task 6: Update `PROJECT_SETUP.md` with Qlty Documentation

**Files:**
- Modify: `{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md`

Two additions: one row in the secrets table, one new subsection.

- [ ] **Step 1: Add `QLTY_COVERAGE_TOKEN` row to the secrets table**

Edit `{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md`.

Find the line (it is the last unconditional row in the `### Required GitHub Secrets` table):
```
| `SCORECARD_TOKEN` | Scorecard (optional) | GitHub PAT with repo scope |
```
Replace with:
```
| `SCORECARD_TOKEN` | Scorecard (optional) | GitHub PAT with repo scope |
| `QLTY_COVERAGE_TOKEN` | Qlty coverage upload | qlty.sh > project Settings > Coverage token |
```

- [ ] **Step 2: Add the `### Qlty Code Quality` subsection**

In the same file, find the closing `{%- endif %}` that terminates the entire `include_github_actions` block. It appears as the last `{%- endif %}` in the CI/CD section, just before `---` and `## Badge Configuration`. Find:

```
{%- endif %}

---

## Badge Configuration
```

Insert the new subsection immediately before that `{%- endif %}`:

```
### Qlty Code Quality

Qlty aggregates code quality metrics (complexity scores, code smell detection, and
coverage trends) and surfaces them as PR comments via the `qlty.yml` workflow. It does
not replace Ruff, BasedPyright, or pytest; those tools run directly in CI and Qlty
consumes their output to build trend data.

**Setup**:

1. Create a project at [qlty.sh](https://qlty.sh) and link your GitHub repository.
2. Copy the `QLTY_COVERAGE_TOKEN` from the Qlty project Settings page.
3. Add it as a repository secret named `QLTY_COVERAGE_TOKEN` (see [Required GitHub Secrets](#required-github-secrets)).

The `.qlty/qlty.toml` configuration file is already generated; no manual tool
configuration is required beyond the token.

{%- endif %}

---

## Badge Configuration
```

- [ ] **Step 3: Verify the secrets table now contains both new and old rows**

```bash
grep -n "QLTY_COVERAGE_TOKEN\|SCORECARD_TOKEN" \
  '{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md'
```

Expected (two lines, SCORECARD before QLTY):
```
437:| `SCORECARD_TOKEN` | Scorecard (optional) | GitHub PAT with repo scope |
438:| `QLTY_COVERAGE_TOKEN` | Qlty coverage upload | qlty.sh > project Settings > Coverage token |
```

- [ ] **Step 4: Verify the subsection is present**

```bash
grep -n "Qlty Code Quality" '{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md'
```

Expected: one hit, the heading line.

- [ ] **Step 5: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add '{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md'
git commit -m "docs(template): document Qlty secret and code quality subsection in PROJECT_SETUP"
```

---

## Task 7: Annotate Stale Feedback Entries

**Files:**
- Modify: `docs/template_feedback.md`

Three entries confirmed resolved by audit. Each gets a `> **Status**: Resolved` blockquote added immediately after its heading line.

- [ ] **Step 1: Annotate the MD051 entry (heading at line 75)**

Edit `docs/template_feedback.md`.

Find (the heading line):
```
### MD051 Link Fragment Violations in docs/PROJECT_SETUP.md
```
Replace with:
```
### MD051 Link Fragment Violations in docs/PROJECT_SETUP.md

> **Status**: Resolved (2026-05-23): Python anchor-check confirmed all 8 ToC links in
> `PROJECT_SETUP.md` match actual heading IDs exactly. No action required.
```

- [ ] **Step 2: Annotate the front-matter entry (heading at line 89, shifted by 3 after Step 1)**

In the same file, find:
```
### Documentation Files Missing YAML Front Matter (Planning Subset)
```
Replace with:
```
### Documentation Files Missing YAML Front Matter (Planning Subset)

> **Status**: Resolved (2026-05-23): `roadmap.md`, `tech-spec.md`, and
> `project-plan-template.md` confirmed to have valid YAML front matter (2026-05-09 audit).
> `docs/planning/index.md` created in Cluster E (previously absent from template output).
```

- [ ] **Step 3: Annotate the workflow-table entry (heading at line 128, shifted after Steps 1–2)**

In the same file, find:
```
### CI/CD Workflow Documentation Missing Several Workflows
```
Replace with:
```
### CI/CD Workflow Documentation Missing Several Workflows

> **Status**: Resolved (2026-05-23): `pr-validation.yml`, `release.yml`, and
> `publish-pypi.yml` are all present in the Core Workflows table in `PROJECT_SETUP.md`,
> conditionally rendered by `include_github_actions` and `include_semantic_release`.
```

- [ ] **Step 4: Verify all three annotations are present**

```bash
grep -c "Status.*Resolved.*2026-05-23" docs/template_feedback.md
```

Expected: `3`

- [ ] **Step 5: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add docs/template_feedback.md
git commit -m "docs: annotate three stale Cluster E feedback entries as resolved"
```

---

## Task 8: Update Umbrella Spec and Mark Cluster E Shipped

**Files:**
- Modify: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

- [ ] **Step 1: Mark Cluster E as shipped in the cluster table**

Edit `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`.

Find (the Cluster E row in the status table):
```
| E | 4 | Docs build and MkDocs | 6 | not started | `2026-05-09-template-cleanup-cluster-E-docs.md` |
```
Replace with:
```
| E | 4 | Docs build and MkDocs | 6 | shipped | `2026-05-09-template-cleanup-cluster-E-docs.md` |
```

- [ ] **Step 2: Append Cluster E row to the status log**

In the same file, find the last existing status-log row (the Cluster D entry):
```
| 2026-05-21 | Cluster D shipped: ...
```
Add a new row immediately after it:
```
| 2026-05-23 | Cluster E shipped: fixed 9 MD040 violations (unlabeled fenced code blocks) across 5 template files; created `docs/planning/index.md` (previously absent from template output); added `qlty.yml` reusable-workflow caller to generated project workflows (satisfies CI-013); documented `QLTY_COVERAGE_TOKEN` and Qlty Code Quality subsection in `PROJECT_SETUP.md`; annotated 3 stale Cluster E feedback entries as resolved. Umbrella complete. |
```

- [ ] **Step 3: Verify the table row and log row are updated**

```bash
grep "shipped" docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md
```

Expected: at least two lines containing `shipped`, the Cluster D and Cluster E entries.

- [ ] **Step 4: Pre-commit and commit**

```bash
uv run pre-commit run --all-files
git add docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md
git commit -m "docs(planning): mark cluster E shipped, close template-cleanup umbrella"
```

---

## Task 9: Smoke Test: Generated Project Verification

No files modified. This task verifies the template generates correctly with the changes applied.

- [ ] **Step 1: Generate a default project (GitHub Actions enabled)**

```bash
cd /tmp
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/cluster-E-docs --no-input
```

Expected: generation completes with no errors. The generated directory is `/tmp/my_python_project`.

- [ ] **Step 2: Verify `qlty.yml` exists in the generated project**

```bash
ls /tmp/my_python_project/.github/workflows/qlty.yml
```

Expected: file listed with no error.

- [ ] **Step 3: Verify no unlabeled fenced code blocks in generated project docs**

```bash
python3 -c "
import re, glob
violations = []
for path in glob.glob('/tmp/my_python_project/docs/**/*.md', recursive=True) + \
            ['/tmp/my_python_project/README.md']:
    with open(path) as f: lines = f.readlines()
    in_block = False
    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if s == '\`\`\`':
            if not in_block: violations.append(f'{path}:{i}')
            in_block = not in_block
        elif re.match(r'\`\`\`\w', s):
            if not in_block: in_block = True
if violations:
    print('FAIL: violations:', violations)
else:
    print('PASS: no unlabeled fences')
"
```

Expected: `PASS: no unlabeled fences`

- [ ] **Step 4: Verify `docs/planning/index.md` exists in generated project**

```bash
ls /tmp/my_python_project/docs/planning/index.md
```

Expected: file listed with no error.

- [ ] **Step 5: Generate a project with GitHub Actions disabled and confirm `qlty.yml` is absent**

```bash
cd /tmp
# Use a config file to override include_github_actions
cat > /tmp/no-gha-config.yaml <<'EOF'
default_context:
  include_github_actions: "no"
EOF
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/cluster-E-docs \
  --config-file /tmp/no-gha-config.yaml --no-input \
  --output-dir /tmp/no-gha-test/
ls /tmp/no-gha-test/my_python_project/.github/workflows/qlty.yml 2>/dev/null \
  && echo "FAIL: file should not exist" \
  || echo "PASS: qlty.yml correctly absent"
```

Expected: `PASS: qlty.yml correctly absent`

- [ ] **Step 6: Clean up generated test projects**

```bash
rm -rf /tmp/my_python_project /tmp/no-gha-test /tmp/no-gha-config.yaml
```

---

## Task 10: Open Pull Request

- [ ] **Step 1: Push the branch**

```bash
cd .worktrees/cluster-E-docs
git push -u origin feat/cluster-E-docs
```

- [ ] **Step 2: Open the PR**

```bash
gh pr create \
  --title "fix(template): cluster E docs build and MkDocs (MD040, index.md, qlty workflow)" \
  --body "$(cat <<'EOF'
## Summary

- Fix 9 MD040 violations (unlabeled fenced code blocks) across 5 template files, all tagged `text`
- Create `{{cookiecutter.project_slug}}/docs/planning/index.md` (was absent from template output; blocked MkDocs nav)
- Add `{{cookiecutter.project_slug}}/.github/workflows/qlty.yml` reusable-workflow caller (satisfies CI-013)
- Document `QLTY_COVERAGE_TOKEN` secret and Qlty Code Quality subsection in `PROJECT_SETUP.md`
- Annotate 3 stale Cluster E feedback entries as resolved in `docs/template_feedback.md`
- Mark Cluster E shipped in umbrella spec, closing the template-cleanup umbrella

## Template Testing

- [x] Generated with default configuration (`--no-input`, `include_github_actions=yes`)
- [x] `qlty.yml` present in generated project
- [x] Zero unlabeled fenced code blocks in generated docs
- [x] `docs/planning/index.md` present in generated project
- [x] Generated with `include_github_actions=no`: `qlty.yml` correctly absent

## Breaking Changes

- [ ] None

Closes template-cleanup umbrella (all clusters A–E shipped).
EOF
)" \
  --base main
```

- [ ] **Step 3: Record the PR URL**

Copy the URL printed by `gh pr create` for reference.

---

## Post-Merge Cleanup

After the PR is merged, clean up the worktree from the main workspace:

```bash
# Run from the template repo root (not the worktree)
git worktree remove .worktrees/cluster-E-docs
git worktree prune
git pull origin main
```
