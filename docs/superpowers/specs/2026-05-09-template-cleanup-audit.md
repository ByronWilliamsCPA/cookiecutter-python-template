# Template Cleanup Audit

> **Status**: snapshot at 2026-05-09
> **Source**: `docs/template_feedback.md` (47 items, dates 2025-11-22 through 2026-05-08)
> **Method**: grep + file checks against the current template tree on `feat/wip-stash-review`
> **Companion**: `2026-05-09-template-cleanup-umbrella.md` (the living tracking doc)

This file is a snapshot. It does not change as work progresses; the umbrella tracks
status. Use this audit to scope per-cluster brainstorming sessions.

## Status legend

| Status | Meaning |
|---|---|
| FIXED | Verified resolved in the current template; remove from feedback file when umbrella closes. |
| OPEN | Verified outstanding; needs work. |
| VERIFY | Cannot be confirmed by static inspection; needs a `cruft create` smoke test. |
| REDIRECTED | Out of scope for this template; should be re-filed in the consumer repo or a future VM template. |

## Cluster assignments

| Code | Cluster |
|---|---|
| A | Generation correctness |
| B | CI / workflow stability |
| C | Compliance scaffolding |
| D | Code quality of generated code |
| E | Docs build and MkDocs |
| -- | Out of scope (no cluster) |

## Audit table

Items are grouped by status. Within each status, items are listed roughly by feedback order.

### FIXED (no work needed; remove from feedback when umbrella closes)

| Item | Cluster | Evidence |
|---|---|---|
| `.cruft.json` `_template` URL local-path bug | A | `hooks/post_gen_project.py` `add_cruft_skip_patterns()` exists; URL handling needs final verification by smoke test |
| CLAUDE.md generated at `.claude/claude.md` | A | `{{cookiecutter.project_slug}}/CLAUDE.md` present at top-level |
| Missing `LICENSES/` directory for REUSE | C | `{{cookiecutter.project_slug}}/LICENSES/` contains `MIT.txt`, `Apache-2.0.txt`, `BSD-3-Clause.txt`, `GPL-3.0-or-later.txt`, `CC-BY-4.0.txt`, `CC0-1.0.txt` |
| `scripts/generate_requirements.sh` missing +x | A | `ls -la` shows mode `-rwxr-xr-x` |
| Repo URL underscore vs hyphen | C | `cookiecutter.json` defines `github_repo_name` as `project_slug.replace('_', '-')` and uses it in `repo_url` |
| Ruff `ANN101`/`ANN102` deprecated rules | D | `pyproject.toml` comment confirms removal: "ANN101/ANN102 removed - rules deprecated in Ruff" |
| MkDocs nav references missing files | E | All 12 nav-referenced files exist under `{{cookiecutter.project_slug}}/docs/` |
| CLAUDE.md missing branch workflow instruction | C | `CLAUDE.md` line 107: "## Branch Workflow Requirement (CRITICAL)" |
| CLAUDE.md security-first approach | C | `CLAUDE.md` line 150: "## Security-First Development (CRITICAL)" |
| Invalid `setup-uv` SHA `582b2d7...` | B | All workflows now reference `astral-sh/setup-uv@v7` |
| Compliance auditor adds invalid qlty `basedpyright` plugin | B | `.qlty/qlty.toml` has no `basedpyright` entry; this is an upstream auditor bug, not a template bug |
| Front matter on `docs/PROJECT_SETUP.md` | E | First 10 lines show valid YAML front matter |
| Front matter on `docs/OPENSSF_COMPLIANCE.md` | E | First 10 lines show valid YAML front matter |
| Front matter on `docs/ADRs/README.md` | E | First 10 lines show valid YAML front matter |
| `PROJECT_SETUP.md` uses `master` in git push | A | grep for "origin master" returns nothing |
| Branch protection script missing key features | C | Script contains `enforce_admins`, `require_code_owner_reviews`, `required_signatures`; only `sole_contributor` flag still missing (tracked separately as OPEN) |

### OPEN (verified outstanding work)

| Item | Cluster | Priority | Evidence |
|---|---|---|---|
| Missing `.editorconfig` | C | Low | File absent at `{{cookiecutter.project_slug}}/.editorconfig` |
| `community_health_style` variable absent | C | Medium | `cookiecutter.json` has no `community_health_style` key |
| `sole_contributor` cookiecutter variable absent | C | High | Not present in `cookiecutter.json`; branch protection script lacks branching on it |
| `interrogate>=1.7.0` pulls vulnerable `py` (CVE-2022-42969) | D | Low | `pyproject.toml` still declares `interrogate>=1.7.0` |
| Missing `scripts/sonar_scan.py` for local SonarCloud | D | Medium | File absent |
| Missing `docs/planning/index.md` | E | Low | File absent |
| Fence terminator with language tag | A | High | `{{cookiecutter.project_slug}}/.claude/context/python-standards.md:67` closes with three-backticks-then-`text`; full repo sweep needed |
| Dockerfile does not COPY README.md before `uv sync` | B | Critical | `Dockerfile:24` is `COPY pyproject.toml uv.lock ./`; README missing |
| Cruft check default `enable-cruft-check: true` | B | Medium | Setting lives in external reusable workflow (`python-supplemental-checks.yml`); template caller workflow needs explicit override or upstream change |
| Branch protection status check names may not match workflow job names | B | High | `setup_github_protection.py` defines status checks; needs cross-check against current workflow job IDs |
| Pre-commit TruffleHog YAML quoting | B | High | `{{cookiecutter.project_slug}}/.pre-commit-config.yaml:66` uses `bash -c '...'` with single quotes; if `file://` parses as YAML this needs double-quoting |
| `master` vs `main` default branch in `git init` | A | Medium | `hooks/post_gen_project.py` initialization needs `init.defaultBranch main` or `git init -b main` |
| MD040 violations (fenced blocks without language) | E | Medium | Per feedback: 7 files affected; needs current scan |
| MD051 link fragment violations in `docs/PROJECT_SETUP.md` | E | Low | Per feedback: lines 15-21 in current rendering |
| Template-generated scripts fail qlty (high complexity) | D | Medium | `scripts/check_fips_compatibility.py`, `scripts/cleanup_conditional_files.py`, `scripts/check_orphaned_files.py`, `src/.../core/exceptions.py` per feedback; needs current qlty run |
| `python-compatibility.yml` GITHUB_OUTPUT multi-line format | B | High | Earlier grep for `matrix=` returned nothing; needs source inspection (workflow may use a different pattern that's already correct, or the line may have moved) |
| Qlty plugin syntax in `.qlty/qlty.toml` | D | High | Need current `qlty check` run; some attributes called out in feedback may already be removed |
| Branch Protection Script Not Documented or Auto-Run | C | High | Script exists but `PROJECT_SETUP.md` reference and post-gen invocation flow need verification |
| `PROJECT_SETUP.md` Core Workflows table missing `pr-validation.yml`, `publish-pypi.yml`, `release.yml` | E | Medium | Per feedback lines 696-708; needs current diff vs `.github/workflows/` |
| Qlty CLI not mentioned in `PROJECT_SETUP.md` | E | Low | Post-gen suggests `curl https://qlty.sh | bash` but setup doc does not document it |

### VERIFY (need cruft create smoke test to confirm status)

| Item | Cluster | Why static check is insufficient |
|---|---|---|
| Unparsed `{{ cookiecutter.* }}` in generated `.claude/` | A | Source files contain literal `{{ cookiecutter.* }}` (correct); whether they render at generation time depends on `_copy_without_render` rules. `cookiecutter.json` `_copy_without_render` only excludes static assets (HTML/CSS/JS/images), so `.claude/` should render. Confirm with one generation. |
| BasedPyright warnings in generated `cli.py` / `logging.py` | D | Recent commits touched these files (`fix(template): move correlation import to top level in logging.py`); current warning count may differ from feedback's 33 |
| Documentation files missing required YAML front matter (planning subset) | E | Most files audited have front matter; some planning files (`planning/project-plan-template.md`, `planning/tech-spec.md`, `planning/roadmap.md`) not yet checked individually |
| Pre-commit on first generation modifies trailing newlines | A | Symptom-level item; needs reproduction in fresh generation |

### REDIRECTED (out of scope; refile elsewhere)

| Item | Original priority | Reason | Action |
|---|---|---|---|
| VM Provisioning Should Ship Default `NTP=<homelab_ntp>` Drop-In | High | Infrastructure provisioning concern, not a Python project template | Refile in `homelab-infra` or future VM/Ansible template |
| OpenClaw Session Checkpoint Retention Policy | High | Operator concern for a specific Python service consumer, not a generic template feature | Refile in `homelab-infra` (or wherever OpenClaw runs) |
| VM RTC Mode Should Be Explicitly Set Post-Provision | Medium | OS provisioning concern, not Python project scaffolding | Refile in `homelab-infra` or future VM template |

## Per-cluster open-item summary (count by status)

| Cluster | OPEN | VERIFY | Total in scope |
|---|---|---|---|
| A. Generation correctness | 2 | 2 | 4 |
| B. CI / workflow stability | 5 | 0 | 5 |
| C. Compliance scaffolding | 4 | 0 | 4 |
| D. Code quality of generated code | 4 | 1 | 5 |
| E. Docs build and MkDocs | 5 | 1 | 6 |
| Out of scope | 0 | 0 | 3 redirected |

Total in-scope open or verify items: 24 across 5 clusters.

## Notes for downstream brainstorming

- VERIFY items in clusters A, B, D, E should be resolved with a single `cruft create . --no-input` run early in cluster B (since cluster B starts with the smoke test for Dockerfile anyway). Move the resolved items into FIXED or OPEN before that cluster's design is written.
- Several OPEN items have a "needs current scan" qualifier (qlty, basedpyright, MD040). Each cluster's brainstorming should start by re-running the relevant tool on a fresh generation to refresh counts.
- The original feedback file should be edited at the end of each cluster to remove FIXED items that the cluster closed. The audit file itself is not edited; new audits get a new dated file.
