# Template Cleanup Umbrella

> **Status**: living tracking doc; update as clusters land
> **Created**: 2026-05-09
> **Source feedback**: `docs/template_feedback.md`
> **Companion audit**: `2026-05-09-template-cleanup-audit.md`

## Purpose

The template feedback file describes 47 issues spanning seven problem domains. This
umbrella decomposes them into five clusters that ship as independent designs and PRs.
Three items are redirected as out of scope (VM/infra concerns).

This is the index. Each cluster gets its own design file when its turn comes.

## Cluster index

| # | Order | Cluster | Open + Verify | Status | Design file |
|---|---|---|---|---|---|
| BA | 1 | Post-smoke-test cleanup (merged B+A) | 3 | design pending | `2026-05-09-template-cleanup-cluster-BA-post-smoke.md` |
| C | 2 | Compliance scaffolding | 4 | not started | `2026-05-09-template-cleanup-cluster-C-compliance.md` |
| D | 3 | Code quality of generated code | 5 | not started | `2026-05-09-template-cleanup-cluster-D-quality.md` |
| E | 4 | Docs build and MkDocs | 6 | not started | `2026-05-09-template-cleanup-cluster-E-docs.md` |

Total in-scope work: 18 items across 4 clusters (after smoke-test reductions). The
original B+A clusters were merged into a single "BA" PR after a `cruft create` smoke
test resolved 6 items as already-FIXED. See `Status log` below for details and the
audit for the original 24-item list.

## Ordering rationale (revised after smoke test)

1. **BA first (post-smoke-test cleanup)**: a single small PR covering the only bugs that survived the smoke test. Dockerfile README copy fix (manifests when `include_docker=yes`), fence terminator with `text` language tag at `.claude/context/python-standards.md:67`, and a one-time spot-verification of branch-protection status check name alignment. Tiny, fast, low risk.
2. **C second (compliance scaffolding)**: mostly additive (`.editorconfig`, `community_health_style`, `sole_contributor`, missing `planning/index.md`, document the branch-protection script in `PROJECT_SETUP.md`).
3. **D third (code quality of generated code)**: most invasive. `interrogate` replacement, `sonar_scan.py`, basedpyright cleanup (20 warnings confirmed in generated code), script complexity refactors.
4. **E last (docs build and MkDocs)**: residual MD040/MD051/front-matter on planning docs; smallest after the other clusters land.

## Dependencies between clusters

- BA unblocks D: D's basedpyright cleanup needs a clean Dockerfile build path for the optional Docker test. Cluster BA also normalizes any remaining generation-correctness state.
- C unblocks E: front matter on planning files in E may need the schema additions C might introduce.
- D and E are largely independent; D first because it touches more files and tests.

## Out-of-scope items (redirected)

| Original feedback item | New home |
|---|---|
| VM provisioning NTP drop-in | refile in `homelab-infra` repo or future VM template |
| OpenClaw session checkpoint retention | refile in `homelab-infra` repo (consumer-specific) |
| VM RTC mode set post-provision | refile in `homelab-infra` repo or future VM template |

The action for these is: at the end of cluster A or C (whichever lands first), edit
`docs/template_feedback.md` to remove these three items with a note that they were
redirected to homelab-infra. No work happens here.

## Working agreements

- Each cluster gets its own brainstorming session, design file, and implementation PR.
- The audit file (`2026-05-09-template-cleanup-audit.md`) is a snapshot and is not edited. If a re-audit is needed mid-stream, it gets a new dated file.
- After each cluster's PR merges, edit `docs/template_feedback.md` to remove the items that cluster closed. This umbrella's table is updated to reflect status.
- VERIFY items get resolved early in cluster B's smoke test; their statuses are then frozen in the umbrella and treated as OPEN or FIXED in subsequent cluster designs.

## Status log

| Date | Event |
|---|---|
| 2026-05-09 | Umbrella + audit created on `feat/wip-stash-review`. Clusters not started. |
| 2026-05-09 | Smoke test (`cruft create . --no-input` and again with `include_docker=yes`) resolved 6 items as already-FIXED: unparsed `{{cookiecutter.*}}` in `.claude/`, trailing newlines, master/main default branch, `.cruft.json` URL local-path, trufflehog YAML quoting (parses cleanly), `python-compatibility.yml` GITHUB_OUTPUT format (now uses YAML matrix literal). One item REDIRECTED: cruft check default lives in external org `.github` reusable workflow, not this template. |
| 2026-05-09 | Clusters B and A merged into single cluster "BA" (3 in-scope items: Dockerfile README copy, fence terminator at `.claude/context/python-standards.md:67`, spot-verification of branch-protection status check name alignment for 3 contexts). Cluster ordering revised. |

Append new rows here as clusters move through brainstorm to merge.
