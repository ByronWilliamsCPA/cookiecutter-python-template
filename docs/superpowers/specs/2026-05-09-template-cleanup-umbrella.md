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
| B | 1 | CI / workflow stability | 5 | not started | `2026-05-09-template-cleanup-cluster-B-ci-stability.md` |
| A | 2 | Generation correctness | 4 | not started | `2026-05-09-template-cleanup-cluster-A-generation.md` |
| C | 3 | Compliance scaffolding | 4 | not started | `2026-05-09-template-cleanup-cluster-C-compliance.md` |
| D | 4 | Code quality of generated code | 5 | not started | `2026-05-09-template-cleanup-cluster-D-quality.md` |
| E | 5 | Docs build and MkDocs | 6 | not started | `2026-05-09-template-cleanup-cluster-E-docs.md` |

Total in-scope work: 24 items across 5 clusters. See audit for the full list.

## Ordering rationale

1. **B first (CI stability)**: the Dockerfile bug and TruffleHog quoting break downstream consumers immediately. A cruft-create smoke test happens at the start of this cluster, which simultaneously resolves all 7 VERIFY items in the audit. Lowest risk, highest unblock value.
2. **A second (generation correctness)**: cluster B's smoke test exposes any remaining generation-time issues (master vs main, trailing newlines, fence terminator); cluster A consolidates the fixes in `hooks/post_gen_project.py` and the template tree.
3. **C third (compliance scaffolding)**: mostly additive (`.editorconfig`, `community_health_style`, `sole_contributor`, missing `planning/index.md`). Low risk; lands while the generation surface is still warm.
4. **D fourth (code quality of generated code)**: most invasive. `interrogate` replacement, `sonar_scan.py`, basedpyright cleanup in `cli.py`/`logging.py`, script complexity refactors. Bigger test surface.
5. **E last (docs build and MkDocs)**: residual MD040/MD051/front-matter on planning docs; smallest after the other clusters land.

## Dependencies between clusters

- B unblocks A: smoke test in B converts VERIFY items in A to OPEN or FIXED.
- A unblocks C: master/main fix in A means C's branch protection work assumes `main` consistently.
- D depends on A: basedpyright cleanup needs a clean generation (no more trailing-newline pre-commit churn) for stable output.
- E depends on C: front matter on planning files in E may need the schema additions C might introduce.

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

Append new rows here as clusters move through brainstorm to merge.
