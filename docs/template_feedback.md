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
>
> **Cleanup 2026-05-21:** 5 cluster D entries removed in PR `feat/cluster-D-code-quality`.
> Three closed by this PR: interrogate transitive `py` CVE (documented as accepted risk
> in generated project's `docs/known-vulnerabilities.md`); BasedPyright warnings in
> generated cli.py and logging.py (5 warnings cleared via typed accessors); script
> complexity in `check_fips_compatibility.py`, `cleanup_conditional_files.py`,
> `check_orphaned_files.py`, and `core/exceptions.py` (refactored into per-feature
> helpers plus a new `_cleanup_shared.py` module). Two dropped: local SonarCloud scan
> script REDIRECTED to the org reusable workflow (PR #54), and the qlty plugin syntax
> entry was already FIXED before audit. Discovered finding (not addressed by this PR):
> upstream `markdown` PYSEC-2026-89 also documented in generated `known-vulnerabilities.md`.
>
> **Cleanup 2026-05-23:** 5 cluster E entries removed in PR `feat/cluster-E-docs`:
> MD040 violations fixed (unlabeled fenced blocks in `architecture.md`, `testing.md`,
> `planning/README.md`, `planning/project-plan-template.md`, and planning sub-docs);
> `docs/planning/index.md` created (was absent from template output); MD051 link
> fragments confirmed already-valid (no action needed); YAML front matter on planning
> docs confirmed already-present; CI/CD workflow table in `PROJECT_SETUP.md` updated
> with `pr-validation.yml`, `release.yml`, and `publish-pypi.yml`; Qlty documented in
> `PROJECT_SETUP.md` and `qlty.yml` reusable-workflow caller added to generated project.
> All clusters complete. No remaining feedback items.

---

## Feedback Items

No open items. All clusters (BA, C, D, E) have shipped. See cleanup blockquotes above
for a summary of what each cluster addressed.
