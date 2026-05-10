---
title: "Template Repository Roadmap"
schema_type: common
status: published
owner: core-maintainer
purpose: "Roadmap pointer for the cookiecutter-python-template repository's maintenance work."
tags:
  - planning
  - roadmap
---

# Template Repository Roadmap

This is a meta-repository that generates Python projects. Its own planning artifacts
live alongside the brainstorming and feasibility outputs at:

- **Superpowers specs:** `docs/superpowers/specs/`
- **Feasibility checks:** `docs/superpowers/feasibility/`

## Active maintenance roadmap

The current active body of work is the template feedback cleanup, indexed at
`docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`. That umbrella is the
authoritative roadmap for the in-flight cleanup clusters. This file exists to satisfy
the planning-bridge-gate hook for `writing-plans` invocations and to point newcomers
at the actual planning surface.

Project-style planning artifacts (PVS, ADR, tech spec, full multi-phase roadmap) are
intentionally not maintained here because this repository is a template, not a product.
The `docs/planning/` directory inside `{{cookiecutter.project_slug}}/` does scaffold
those artifacts for generated projects.
