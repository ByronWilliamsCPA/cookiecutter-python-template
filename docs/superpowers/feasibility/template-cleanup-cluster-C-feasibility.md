---
title: "Feasibility: Template Cleanup Cluster C (Compliance Scaffolding)"
schema_type: common
status: published
owner: core-maintainer
purpose: "Feasibility assessment for cluster C of the template cleanup, covering .editorconfig, community_health_style, sole_contributor, and PROJECT_SETUP documentation plus auto-run."
tags:
  - planning
---

# Feasibility: Template Cleanup Cluster C (Compliance Scaffolding)

**Date:** 2026-05-19
**Verdict:** GO

## Analysis

**Core assumption:** The spec assumes that `setup_github_protection.py` in the template tree is a plain `.py` file with a literal `"required_approving_review_count": 1` that Jinja2 will render at generation time. The file does contain that literal at line 184 and is already a template-rendered file, so this is verifiable now and confirmed true.

**Blocking dependencies:** None for items 1, 2, and 3 (all purely local file generation). Item 4's auto-run path depends on a live GitHub repo with `admin:repo`-scoped `GITHUB_TOKEN` existing in the user's environment at cruft-create time, but the spec correctly makes this non-fatal and opt-in (default `no`), so it cannot block the build. The `github_org_or_user` cookiecutter variable the org-pointer variant needs already exists in `cookiecutter.json`.

**Minimum buildable version:** The `.editorconfig` flag (item 1) alone delivers immediate, standalone user value with zero external dependencies and a three-file change (cookiecutter.json, new `.editorconfig` source, one hook addition). It can be shipped independently and validates the flag-plus-hook-removal pattern the other items also use.

## Verdict rationale

All four items are internally consistent, no external blockers exist, the existing hook and script patterns are already in place and confirmed compatible, and the spec's error-handling choices (non-fatal auto-run, best-effort cruft-skip) correctly contain the only risky surface area (item 4). No conditions need to be resolved before starting.
