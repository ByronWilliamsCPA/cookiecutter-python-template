# Cluster C: Compliance Scaffolding Design

> **Parent**: `2026-05-09-template-cleanup-umbrella.md`
> **Status**: design approved 2026-05-18
> **Scope**: four compliance items per the cluster C umbrella entry, plus the discovery that `CODE_OF_CONDUCT.md` and `GOVERNANCE.md` source files are missing from the template tree (folded into item 2)

## Goal

Land a single PR adding four compliance scaffolding capabilities to the cookiecutter template: an `.editorconfig` gated by a feature flag, a `community_health_style` flag controlling the content of community-health files, a `sole_contributor` flag controlling the branch-protection approval count, and a `PROJECT_SETUP.md` documentation update plus an opt-in auto-run path for the branch-protection script. Closes 4 of the 13 remaining entries in `docs/template_feedback.md`.

## Items in scope

### 1. `.editorconfig` generation

**Files:**

- New cookiecutter variable in `cookiecutter.json`: `include_editorconfig: ["yes", "no"]` defaulting to `yes`
- New source file: `{{cookiecutter.project_slug}}/.editorconfig`
- Modify `hooks/post_gen_project.py` to delete the file when `include_editorconfig == "no"`

**Content (4-space Python baseline):**

```ini
# EditorConfig: https://editorconfig.org
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{yml,yaml,json,toml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

**Behavior:**

- Default `yes`: file is generated as above.
- `no`: post-gen hook removes the file, mirroring the existing `include_code_of_conduct == "no"` removal pattern.

### 2. `community_health_style` plus missing source files

**Files:**

- New cookiecutter variable in `cookiecutter.json`: `community_health_style: ["full", "org_pointer"]` defaulting to `full`
- New source files (both with Jinja conditionals):
  - `{{cookiecutter.project_slug}}/CODE_OF_CONDUCT.md`
  - `{{cookiecutter.project_slug}}/GOVERNANCE.md`
- Modify `hooks/post_gen_project.py` to append the two files to the generated `.cruft.json` skip list when `community_health_style == "org_pointer"`

**Full variant** (default): a standard Contributor Covenant 2.1 in `CODE_OF_CONDUCT.md` with `{{ cookiecutter.author_email }}` substituted as the contact line; a minimal GOVERNANCE.md template covering:

- Maintainer list (templated with `{{ cookiecutter.author_name }}`)
- Decision model (single-maintainer with consensus on substantive changes)
- Contributor process (points to CONTRIBUTING.md)
- Conflict resolution (escalation path)

**Org_pointer variant**: three-line pointer files. Example for `CODE_OF_CONDUCT.md`:

````markdown
# Code of Conduct

This project follows the
[{{ cookiecutter.github_org_or_user }} organization Code of Conduct](https://github.com/{{ cookiecutter.github_org_or_user }}/.github/blob/main/CODE_OF_CONDUCT.md).
````

GOVERNANCE.md follows the same pattern, pointing to the org's `GOVERNANCE.md`.

**Cruft skip list:** when `community_health_style == "org_pointer"`, the post-gen hook extends the existing `add_cruft_skip_patterns()` flow (see `hooks/post_gen_project.py`) to also include `CODE_OF_CONDUCT.md` and `GOVERNANCE.md`. This uses the same JSON-key conventions the existing function already manipulates so future `cruft update` runs do not overwrite the pointer with the full content.

**Interaction with existing `include_code_of_conduct` flag:** preserved as-is. If `include_code_of_conduct == "no"`, the existing removal logic deletes `CODE_OF_CONDUCT.md` regardless of `community_health_style`. GOVERNANCE.md has no equivalent opt-out flag (always generated, in one of the two variants).

### 3. `sole_contributor` flag for branch protection

**Files:**

- New cookiecutter variable in `cookiecutter.json`: `sole_contributor: ["yes", "no"]` defaulting to `yes`
- Modify `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py`: replace the literal `"required_approving_review_count": 1` (or whatever the current value is) with a Jinja conditional

**Behavior:**

The protection script's `protection` dict literal becomes:

```python
"required_pull_request_reviews": {
    "dismissal_restrictions": {},
    "dismiss_stale_reviews": True,
    "require_code_owner_reviews": True,
    "required_approving_review_count": {% if cookiecutter.sole_contributor == "yes" %}0{% else %}1{% endif %},
    "require_last_push_approval": False,
},
```

Add a comment immediately above the dict explaining the `sole_contributor` branching and why other protection settings are not relaxed (defense in depth even for solo maintainers).

All other protection settings (`enforce_admins=True`, `require_code_owner_reviews=True`, `required_signatures` call) remain unchanged.

### 4. PROJECT_SETUP.md docs plus auto-run

**Files:**

- New cookiecutter variable in `cookiecutter.json`: `auto_setup_branch_protection: ["no", "yes"]` defaulting to `no`
- Update `{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md` Security Configuration section
- Modify `hooks/post_gen_project.py` to invoke the branch-protection script when preconditions hold

**Documentation:**

The Security Configuration section gains a new subsection documenting:

- Manual invocation: `GITHUB_TOKEN=ghp_xxx uv run python scripts/setup_github_protection.py`
- Prerequisites: GitHub repo must exist (created via `gh repo create` or web UI); `GITHUB_TOKEN` must have `admin:repo` scope (or repository admin permission)
- The `auto_setup_branch_protection` flag and what it does
- Recommended first-run sequence (push initial commit, then run the script)

**Auto-run hook logic:**

After the existing post-gen steps, the hook checks three preconditions:

1. `cookiecutter.auto_setup_branch_protection == "yes"`
2. `os.environ.get("GITHUB_TOKEN")` is set
3. `git config --get remote.origin.url` returns a non-empty value (the project has a remote)

If all three hold, the hook invokes the script as a subprocess. On success, it prints a single confirmation line. On failure (any exit code or exception), it prints a single warning line including the script's stderr summary and the manual-invocation command. Failure is non-fatal: post-gen continues so cruft generation succeeds.

## Architecture

Four independent additions. No shared module, no refactor of existing files beyond what each item explicitly touches. The two post-gen-hook extensions (editorconfig removal, cruft-skip-list append, auto-run) are additive blocks at the end of the existing hook; they do not change existing logic.

## Data flow

1. User runs `cruft create` with values (or accepts defaults) for the four new variables.
2. Cookiecutter renders the template; Jinja conditionals select content variants in the new source files.
3. Post-gen hook runs the existing sequence, then the three new actions in order:
   - Remove `.editorconfig` if `include_editorconfig == "no"`
   - Append to `.cruft.json` skip list if `community_health_style == "org_pointer"`
   - Run branch-protection script if all three auto-run preconditions hold

## Error handling

- Branch-protection auto-run is the only step with external side effects. It is non-fatal; failures produce a stdout warning with the manual-invocation command and cruft generation completes successfully.
- `.cruft.json` skip-list append is best-effort: if `.cruft.json` does not exist (unusual but possible), the hook logs a warning and continues without modifying skip-list state.
- Conditional Jinja in the protection script: rendered values are validated by the script's own JSON serialization at runtime; invalid values would surface as Python errors when the user runs the script, not at generation time.

## Testing

Three layers:

### Layer 1: generation smoke tests

Extend `tests/unit/test_generation.py` with parametrized cases for each new flag's variants. Assert:

- `include_editorconfig=yes`: `.editorconfig` exists; contents match expected baseline
- `include_editorconfig=no`: `.editorconfig` absent
- `community_health_style=full`: `CODE_OF_CONDUCT.md` contains "Contributor Covenant"; `GOVERNANCE.md` contains the maintainer name
- `community_health_style=org_pointer`: both files are 3-5 lines and contain a pointer URL; `.cruft.json` skip list includes both filenames
- `sole_contributor=yes`: generated protection script's contexts include `"required_approving_review_count": 0`
- `sole_contributor=no`: generated protection script's contexts include `"required_approving_review_count": 1`
- `auto_setup_branch_protection=no`: no auto-run output; no GitHub API calls (assert via subprocess mock)

### Layer 2: hook unit tests

Add cases to `tests/unit/test_hooks.py` (or `tests/unit/test_post_gen_hooks.py` if separate) covering each new post-gen-hook branch:

- `_remove_editorconfig_if_disabled` is called and removes the file
- `_append_community_health_skips` is called and modifies `.cruft.json`
- `_auto_setup_branch_protection` checks all three preconditions; mocks `os.environ` and `subprocess.run` to verify the invocation path

### Layer 3: quality gates

Pre-commit (ruff, basedpyright, no-em-dash, yamllint, markdownlint) covers the new source files and the hook changes. No additional tooling required.

## Out of scope

- Modifying the **template repo itself** (root-level `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`). The template repo's own community-health posture is unchanged; this design only affects what gets generated for downstream projects.
- Other branch-protection settings beyond approval count. `require_code_owner_reviews`, `require_last_push_approval`, etc. remain at their current values regardless of `sole_contributor`.
- Auto-creating the GitHub repo or pushing the initial commit. The auto-run path assumes the user has already created the repo and added a remote.
- Generating community-health files in the third style (e.g., a hybrid where CODE_OF_CONDUCT is full but GOVERNANCE is a pointer). The two-flavor design is sufficient.

## Acceptance criteria

A PR titled `feat(template): add compliance scaffolding (editorconfig, community health, branch protection)` lands on `main` with:

- [ ] `cookiecutter.json` contains the four new variables with the chosen defaults.
- [ ] `cruft create --no-input` generates a project with `.editorconfig`, `CODE_OF_CONDUCT.md` (Contributor Covenant), `GOVERNANCE.md` (maintainer template), and the protection script's approval count set to 0.
- [ ] `cruft create --no-input --extra-context '{"community_health_style": "org_pointer"}'` generates 3-5 line pointer files for both community-health docs and appends both to the `.cruft.json` skip list.
- [ ] `cruft create --no-input --extra-context '{"sole_contributor": "no"}'` generates a protection script with `"required_approving_review_count": 1`.
- [ ] Test suite passes: existing tests plus new smoke and hook tests.
- [ ] `docs/template_feedback.md` is edited in the same PR to remove the four entries this PR closes (`.editorconfig`, `community_health_style`, `sole_contributor`, branch-protection script docs/auto-run).
- [ ] Umbrella status log gets a new row recording cluster C completion.

## Branch

Branch from `chore/remove-safety-scanner`. PR target main (or whatever the integration branch is at PR-open time). Worktree at `.worktrees/feat-cluster-C-compliance` per project convention.
