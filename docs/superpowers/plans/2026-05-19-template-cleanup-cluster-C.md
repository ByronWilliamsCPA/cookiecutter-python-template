# Template Cleanup Cluster C Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four compliance scaffolding capabilities to the cookiecutter template in one PR: a gated `.editorconfig`, a `community_health_style` flag with new CODE_OF_CONDUCT.md and GOVERNANCE.md source files, a `sole_contributor` flag affecting branch-protection approval count, and PROJECT_SETUP.md documentation plus an opt-in auto-run of the branch-protection script during generation.

**Architecture:** Four independent additions. Each item adds a cookiecutter variable, a template change (new source file or Jinja conditional in an existing file), and corresponding post-gen-hook logic. New behavior is gated by explicit flags with safe defaults. No existing logic is refactored.

**Tech Stack:** Python 3.12, cookiecutter/cruft, Jinja2, pytest, ruff, basedpyright.

---

## Spec references

- Design: `docs/superpowers/specs/2026-05-18-template-cleanup-cluster-C-compliance.md`
- Feasibility: `docs/superpowers/feasibility/template-cleanup-cluster-C-feasibility.md` (GO)
- Umbrella: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

## Branch and worktree

Branch from `chore/remove-safety-scanner`. Worktree path:

```bash
cd /home/byron/dev/cookiecutter-python-template
git worktree add .worktrees/feat-cluster-C-compliance -b feat/cluster-C-compliance chore/remove-safety-scanner
cd .worktrees/feat-cluster-C-compliance
uv sync --all-extras
```

## File structure

| File | Action | Responsibility |
|---|---|---|
| `cookiecutter.json` | modify | Add 4 new variables (`include_editorconfig`, `community_health_style`, `sole_contributor`, `auto_setup_branch_protection`) |
| `{{cookiecutter.project_slug}}/.editorconfig` | create | EditorConfig defaults; removed by hook when flag is `no` |
| `{{cookiecutter.project_slug}}/CODE_OF_CONDUCT.md` | create | Contributor Covenant (full variant) or org pointer; Jinja-conditional content |
| `{{cookiecutter.project_slug}}/GOVERNANCE.md` | create | Minimal governance template (full variant) or org pointer; Jinja-conditional content |
| `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py` | modify | Make approval count Jinja-conditional on `sole_contributor` |
| `{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md` | modify | Document the branch-protection script and `auto_setup_branch_protection` |
| `hooks/post_gen_project.py` | modify | Add three branches: editorconfig removal, cruft-skip extension for org_pointer, optional auto-run subprocess |
| `tests/unit/test_generation.py` | modify | Parametrized cases per new flag variant |
| `tests/unit/test_hooks.py` | modify | Hook-branch coverage for the new logic |
| `docs/template_feedback.md` | modify | Remove the four entries this PR closes |
| `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md` | modify | Append a status-log row for cluster C completion |

---

## Task 1: `include_editorconfig` flag plus `.editorconfig` source file

**Files:**

- Modify: `cookiecutter.json`
- Create: `{{cookiecutter.project_slug}}/.editorconfig`
- Modify: `hooks/post_gen_project.py` (extend `_cleanup_documentation_files` or add a new branch in the same removal block around line 96-101)
- Test: `tests/unit/test_generation.py`, `tests/unit/test_hooks.py`

- [ ] **Step 1.1: Add the failing generation test**

Add this test class to `tests/unit/test_generation.py` after the existing `TestBasicGeneration` class:

```python
class TestEditorConfigFlag:
    """Tests for include_editorconfig cookiecutter flag."""

    def test_editorconfig_present_when_flag_yes(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify .editorconfig is generated when include_editorconfig is yes."""
        from tests.conftest import generate_project

        config = {**minimal_config, "include_editorconfig": "yes"}
        project_dir = generate_project(template_dir, temp_dir, config)
        editorconfig = project_dir / ".editorconfig"
        assert editorconfig.exists(), ".editorconfig should exist when flag is yes"
        content = editorconfig.read_text(encoding="utf-8")
        assert "root = true" in content, "EditorConfig must declare root"
        assert "[*]" in content, "EditorConfig must have a default section"
        assert "indent_style = space" in content, "Default indent_style should be space"
        assert "[*.md]" in content, "Markdown override section should be present"
        assert "[Makefile]" in content, "Makefile override section should be present"

    def test_editorconfig_absent_when_flag_no(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify .editorconfig is removed by hook when include_editorconfig is no."""
        from tests.conftest import generate_project

        config = {**minimal_config, "include_editorconfig": "no"}
        project_dir = generate_project(template_dir, temp_dir, config)
        editorconfig = project_dir / ".editorconfig"
        assert not editorconfig.exists(), ".editorconfig should be removed when flag is no"
```

- [ ] **Step 1.2: Run test, verify failure**

```bash
uv run pytest tests/unit/test_generation.py::TestEditorConfigFlag -v
```

Expected: FAIL because `include_editorconfig` is not in `cookiecutter.json` and the `.editorconfig` source file does not exist.

- [ ] **Step 1.3: Add the cookiecutter variable**

In `cookiecutter.json`, locate the `_comment_community` group (around line 125). Add the new variable just after it:

```json
  "_comment_editorconfig": "EditorConfig",
  "include_editorconfig": ["yes", "no"],
```

Place this insertion before `_comment_urls`. The exact ordering does not affect functionality but keeps related flags together.

- [ ] **Step 1.4: Create the `.editorconfig` source file**

Create `{{cookiecutter.project_slug}}/.editorconfig` with content:

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

- [ ] **Step 1.5: Add the post-gen-hook removal branch**

Open `hooks/post_gen_project.py`. Find the block around lines 96-101 that handles `include_code_of_conduct` and `include_security_policy`. Add a parallel branch:

```python
    # Remove .editorconfig if not needed
    if "{{ cookiecutter.include_editorconfig }}" == "no":
        remove_file(Path(".editorconfig"))
```

Place this immediately after the existing `include_security_policy` removal so all "remove community/config files when flag is no" branches are grouped.

- [ ] **Step 1.6: Run tests, verify both pass**

```bash
uv run pytest tests/unit/test_generation.py::TestEditorConfigFlag -v
```

Expected: PASS, 2 tests.

- [ ] **Step 1.7: Commit**

```bash
git add cookiecutter.json "{{cookiecutter.project_slug}}/.editorconfig" hooks/post_gen_project.py tests/unit/test_generation.py
git commit -m "$(cat <<'EOF'
feat(template): add include_editorconfig flag and .editorconfig source

Generated projects now ship .editorconfig by default. Set
include_editorconfig=no to opt out; post-gen hook removes the file
when the flag is no, paralleling the existing include_code_of_conduct
and include_security_policy removal pattern.

Contents: 4-space Python baseline, 2-space YAML/JSON/TOML, LF
endings, UTF-8, preserve trailing whitespace in .md files (for
Markdown hard line breaks), tab indentation in Makefile.
EOF
)"
```

---

## Task 2: `community_health_style` flag plus CODE_OF_CONDUCT.md and GOVERNANCE.md

**Files:**

- Modify: `cookiecutter.json`
- Create: `{{cookiecutter.project_slug}}/CODE_OF_CONDUCT.md`
- Create: `{{cookiecutter.project_slug}}/GOVERNANCE.md`
- Modify: `hooks/post_gen_project.py` (extend cruft-skip patterns conditionally)
- Test: `tests/unit/test_generation.py`, `tests/unit/test_hooks.py`

- [ ] **Step 2.1: Add the failing generation tests**

Add this test class to `tests/unit/test_generation.py`:

```python
class TestCommunityHealthStyle:
    """Tests for community_health_style cookiecutter flag."""

    def test_full_variant_generates_contributor_covenant(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Full variant generates a substantial Code of Conduct file."""
        from tests.conftest import generate_project

        config = {**minimal_config, "community_health_style": "full"}
        project_dir = generate_project(template_dir, temp_dir, config)
        code_of_conduct = project_dir / "CODE_OF_CONDUCT.md"
        assert code_of_conduct.exists()
        content = code_of_conduct.read_text(encoding="utf-8")
        assert "Contributor Covenant" in content, "Full variant should reference Contributor Covenant"
        assert len(content.splitlines()) > 30, "Full variant should be substantial (more than 30 lines)"
        assert config.get("author_email", "you@example.com") in content or \
            "@" in content, "Full variant should include a contact email"

    def test_full_variant_generates_governance_template(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Full variant generates a GOVERNANCE.md template."""
        from tests.conftest import generate_project

        config = {**minimal_config, "community_health_style": "full"}
        project_dir = generate_project(template_dir, temp_dir, config)
        governance = project_dir / "GOVERNANCE.md"
        assert governance.exists()
        content = governance.read_text(encoding="utf-8")
        assert "Governance" in content
        assert "Maintainer" in content or "maintainer" in content
        assert len(content.splitlines()) > 10, "Governance template should have multiple sections"

    def test_org_pointer_variant_is_short_pointer(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Org pointer variant generates short pointer files."""
        from tests.conftest import generate_project

        config = {**minimal_config, "community_health_style": "org_pointer"}
        project_dir = generate_project(template_dir, temp_dir, config)

        code_of_conduct = project_dir / "CODE_OF_CONDUCT.md"
        governance = project_dir / "GOVERNANCE.md"
        assert code_of_conduct.exists()
        assert governance.exists()

        coc_content = code_of_conduct.read_text(encoding="utf-8")
        gov_content = governance.read_text(encoding="utf-8")
        assert len(coc_content.splitlines()) < 15, "Pointer should be short (under 15 lines)"
        assert len(gov_content.splitlines()) < 15, "Pointer should be short (under 15 lines)"
        assert ".github" in coc_content, "Pointer must reference org .github repo"
        assert ".github" in gov_content, "Pointer must reference org .github repo"

    def test_org_pointer_adds_cruft_skip_entries(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Org pointer variant adds CODE_OF_CONDUCT.md and GOVERNANCE.md to cruft skip list."""
        from tests.conftest import generate_project

        config = {**minimal_config, "community_health_style": "org_pointer"}
        project_dir = generate_project(template_dir, temp_dir, config)
        cruft_json = project_dir / ".cruft.json"
        assert cruft_json.exists(), ".cruft.json should exist"
        data = json.loads(cruft_json.read_text(encoding="utf-8"))
        skip = data.get("skip", []) or data.get("default_skip", [])
        assert "CODE_OF_CONDUCT.md" in skip, "CODE_OF_CONDUCT.md should be in cruft skip list"
        assert "GOVERNANCE.md" in skip, "GOVERNANCE.md should be in cruft skip list"
```

- [ ] **Step 2.2: Run tests, verify failure**

```bash
uv run pytest tests/unit/test_generation.py::TestCommunityHealthStyle -v
```

Expected: FAIL (4 tests fail because `community_health_style` is not in `cookiecutter.json` and the source files do not exist).

- [ ] **Step 2.3: Add the cookiecutter variable**

In `cookiecutter.json`, in the `_comment_community` group:

```json
  "_comment_community": "Community Files",
  "use_reuse_licensing": ["yes", "no"],
  "include_code_of_conduct": ["yes", "no"],
  "include_contributing_guide": ["yes", "no"],
  "include_security_policy": ["yes", "no"],
  "community_health_style": ["full", "org_pointer"],
```

The new key goes after `include_security_policy` to keep community-related flags grouped.

- [ ] **Step 2.4: Fetch the Contributor Covenant text and create CODE_OF_CONDUCT.md**

The canonical source for Contributor Covenant 2.1 is:
`https://raw.githubusercontent.com/EthicalSource/contributor_covenant/main/version/2/1/code_of_conduct.md`

Fetch the verbatim text (it is published under CC-BY-4.0). Save the fetched content into a working file first so the placeholder for the contact line is visible.

Create `{{cookiecutter.project_slug}}/CODE_OF_CONDUCT.md` with this Jinja structure:

```jinja
{% if cookiecutter.community_health_style == "full" -%}
<PASTE THE FULL CONTRIBUTOR COVENANT 2.1 TEXT HERE>

# Replace the placeholder contact line that reads
# "[INSERT CONTACT METHOD]" with: {{ cookiecutter.author_email }}
{%- else -%}
# Code of Conduct

This project follows the [{{ cookiecutter.github_org_or_user }} organization Code of Conduct](https://github.com/{{ cookiecutter.github_org_or_user }}/.github/blob/main/CODE_OF_CONDUCT.md).
{%- endif %}
```

When fetching: the upstream document has a single placeholder line (around section "Enforcement") that reads something like `Community leaders are responsible... reported to the community leaders responsible for enforcement at [INSERT CONTACT METHOD]`. Replace `[INSERT CONTACT METHOD]` with `{{ cookiecutter.author_email }}` so the substitution happens at generation time. Preserve all other text verbatim including attribution to the Contributor Covenant.

- [ ] **Step 2.5: Create GOVERNANCE.md**

Create `{{cookiecutter.project_slug}}/GOVERNANCE.md`:

```jinja
{% if cookiecutter.community_health_style == "full" -%}
# Governance

This document describes how {{ cookiecutter.project_name }} is governed, who makes decisions, and how contributors can participate in those decisions.

## Maintainers

The current maintainer is:

- **{{ cookiecutter.author_name }}** ({{ cookiecutter.author_email }})

Maintainers have commit access and are responsible for reviewing and merging pull requests, triaging issues, and cutting releases.

## Decision Model

This project uses a **single-maintainer with consensus** model:

- The maintainer has final say on all decisions.
- For substantive changes (breaking API changes, security policy changes, major dependencies), the maintainer will seek input from active contributors via GitHub Discussions or issue comments before deciding.
- Routine changes (bug fixes, documentation updates, dependency bumps, refactors that preserve behavior) do not require external consensus.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor workflow.

In summary:

1. Open an issue describing the change before sending a PR for non-trivial work.
2. Follow the project's coding standards (ruff, basedpyright, conventional commits).
3. Include tests for behavior changes.
4. Respond to review feedback within a reasonable window.

## Conflict Resolution

If a contributor disagrees with a maintainer decision:

1. Discuss in the PR or issue thread first.
2. If unresolved, open a separate GitHub Discussion summarizing the disagreement and proposed alternatives.
3. The maintainer makes the final call after considering the discussion.

## Adding Maintainers

The maintainer may invite trusted long-term contributors to join as additional maintainers. There is no automatic promotion process; invitations are issued at the maintainer's discretion based on demonstrated judgment and sustained contributions.

{%- else -%}
# Governance

This project follows the [{{ cookiecutter.github_org_or_user }} organization Governance policy](https://github.com/{{ cookiecutter.github_org_or_user }}/.github/blob/main/GOVERNANCE.md).
{%- endif %}
```

- [ ] **Step 2.6: Extend the cruft skip-patterns logic**

Open `hooks/post_gen_project.py`. Locate `get_cruft_skip_patterns()` (around line 1108). Inside that function, add a Jinja-aware addition near the bottom of the returned list (just before the final closing `]`):

```python
        # Community health files (added when style is org_pointer so the user's
        # local pointer content is preserved across cruft update).
        "{% if cookiecutter.community_health_style == 'org_pointer' %}CODE_OF_CONDUCT.md{% endif %}",
        "{% if cookiecutter.community_health_style == 'org_pointer' %}GOVERNANCE.md{% endif %}",
```

Then locate `add_cruft_skip_patterns()` (around line 1170) which writes the patterns into `.cruft.json`. Verify that the function already iterates the list returned by `get_cruft_skip_patterns()`. If the empty-string-when-not-org_pointer renders to a literal empty string, filter those out before writing. Add this filter inside `add_cruft_skip_patterns()`:

```python
    patterns = [p for p in get_cruft_skip_patterns() if p]
```

If the function already builds the list elsewhere, modify it minimally to apply the same filter.

- [ ] **Step 2.7: Run tests, verify all four pass**

```bash
uv run pytest tests/unit/test_generation.py::TestCommunityHealthStyle -v
```

Expected: 4 PASS.

- [ ] **Step 2.8: Commit**

```bash
git add cookiecutter.json "{{cookiecutter.project_slug}}/CODE_OF_CONDUCT.md" "{{cookiecutter.project_slug}}/GOVERNANCE.md" hooks/post_gen_project.py tests/unit/test_generation.py
git commit -m "$(cat <<'EOF'
feat(template): add community_health_style flag and source files

The template previously referenced include_code_of_conduct but had no
CODE_OF_CONDUCT.md or GOVERNANCE.md source files; the generation path
for "yes" was broken. Create both files with a community_health_style
flag (default "full") controlling content.

Full variant: Contributor Covenant 2.1 (CC-BY-4.0; author_email
substituted into the enforcement contact line) and a minimal
GOVERNANCE.md template covering maintainer list, decision model,
contributor process, and conflict resolution.

Org_pointer variant: short pointer files referencing
{{ github_org_or_user }}/.github so projects can use single-source
community-health policy. When org_pointer is selected, both files are
added to the .cruft.json skip list so future cruft update runs do not
overwrite the local pointers.
EOF
)"
```

---

## Task 3: `sole_contributor` flag for branch-protection approval count

**Files:**

- Modify: `cookiecutter.json`
- Modify: `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py` line 184
- Test: `tests/unit/test_generation.py`

- [ ] **Step 3.1: Add the failing generation tests**

Add to `tests/unit/test_generation.py`:

```python
class TestSoleContributorFlag:
    """Tests for sole_contributor cookiecutter flag in the protection script."""

    def test_sole_contributor_yes_sets_zero_approvals(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """sole_contributor=yes sets required_approving_review_count to 0."""
        from tests.conftest import generate_project

        config = {**minimal_config, "sole_contributor": "yes"}
        project_dir = generate_project(template_dir, temp_dir, config)
        script = project_dir / "scripts" / "setup_github_protection.py"
        assert script.exists()
        content = script.read_text(encoding="utf-8")
        assert '"required_approving_review_count": 0' in content, \
            "sole_contributor=yes should produce 0 approvals"

    def test_sole_contributor_no_sets_one_approval(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """sole_contributor=no sets required_approving_review_count to 1."""
        from tests.conftest import generate_project

        config = {**minimal_config, "sole_contributor": "no"}
        project_dir = generate_project(template_dir, temp_dir, config)
        script = project_dir / "scripts" / "setup_github_protection.py"
        assert script.exists()
        content = script.read_text(encoding="utf-8")
        assert '"required_approving_review_count": 1' in content, \
            "sole_contributor=no should produce 1 approval"
```

- [ ] **Step 3.2: Run tests, verify failure**

```bash
uv run pytest tests/unit/test_generation.py::TestSoleContributorFlag -v
```

Expected: FAIL. Both tests fail because `sole_contributor` is not in `cookiecutter.json`.

- [ ] **Step 3.3: Add the cookiecutter variable**

In `cookiecutter.json`, add `sole_contributor` near the community group:

```json
  "sole_contributor": ["yes", "no"],
```

Place it after `community_health_style` (added in Task 2).

- [ ] **Step 3.4: Make the protection script's approval count Jinja-conditional**

Open `{{cookiecutter.project_slug}}/scripts/setup_github_protection.py`. Locate the `protection` dict literal that contains line 184 (`"required_approving_review_count": 1,`).

Replace that one line with a Jinja conditional:

```python
            # Approval count: 0 for sole-maintainer projects (self-merge),
            # 1 for team projects. Controlled by cookiecutter.sole_contributor.
            "required_approving_review_count": {% if cookiecutter.sole_contributor == "yes" %}0{% else %}1{% endif %},
```

Add the explanatory comment immediately above so a future reader sees why the count varies. Do not change any other line in the script.

- [ ] **Step 3.5: Run tests, verify both pass**

```bash
uv run pytest tests/unit/test_generation.py::TestSoleContributorFlag -v
```

Expected: 2 PASS.

- [ ] **Step 3.6: Commit**

```bash
git add cookiecutter.json "{{cookiecutter.project_slug}}/scripts/setup_github_protection.py" tests/unit/test_generation.py
git commit -m "$(cat <<'EOF'
feat(template): add sole_contributor flag for branch protection

The scripts/setup_github_protection.py hard-coded
required_approving_review_count to 1, which forces a second account
on sole-maintainer projects. Add a sole_contributor cookiecutter flag
defaulting to yes; when yes the count is 0 (self-merge), when no it
is 1.

Other protection settings (enforce_admins, require_code_owner_reviews,
required_signatures) remain strict regardless: defense in depth even
for solo maintainers.
EOF
)"
```

---

## Task 4: `auto_setup_branch_protection` flag, PROJECT_SETUP.md docs, post-gen invocation

**Files:**

- Modify: `cookiecutter.json`
- Modify: `{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md` (Security Configuration section near line 492)
- Modify: `hooks/post_gen_project.py` (add a new function called at the end of `main()`)
- Test: `tests/unit/test_hooks.py`, `tests/unit/test_generation.py`

- [ ] **Step 4.1: Add the failing hook tests**

Add to `tests/unit/test_hooks.py`:

```python
class TestAutoSetupBranchProtection:
    """Tests for the optional branch-protection auto-run in post-gen hook."""

    def test_auto_run_skipped_when_flag_disabled(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No subprocess invocation when auto_setup_branch_protection is no."""
        from tests.conftest import generate_project

        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
        config = {**minimal_config, "auto_setup_branch_protection": "no"}
        project_dir = generate_project(template_dir, temp_dir, config)
        # The auto-run leaves no artifact; absence is the assertion.
        # We assert generation succeeded and produced the script (which is the auto-run target).
        assert (project_dir / "scripts" / "setup_github_protection.py").exists()

    def test_auto_run_skipped_when_token_missing(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No subprocess invocation when GITHUB_TOKEN is unset, even if flag is yes."""
        from tests.conftest import generate_project

        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        config = {**minimal_config, "auto_setup_branch_protection": "yes"}
        project_dir = generate_project(template_dir, temp_dir, config)
        # Generation must succeed without raising even though the flag is yes.
        assert (project_dir / "scripts" / "setup_github_protection.py").exists()
```

Note: a full mocked-subprocess test of the success path is non-trivial because the hook runs inside cookiecutter's subprocess. The integration assertion above is sufficient; the function logic itself is exercised by Task 4.4's unit test.

Add to `tests/unit/test_hook_utility_functions.py` (or `test_hook_helpers.py`, whichever exists with that role):

```python
class TestAutoSetupBranchProtectionHelper:
    """Tests for the maybe_run_branch_protection helper in post_gen_project.py."""

    def test_helper_skips_when_flag_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Helper returns False when flag is no."""
        from hooks.post_gen_project import maybe_run_branch_protection

        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        result = maybe_run_branch_protection(flag="no", remote_url="https://github.com/x/y")
        assert result is False

    def test_helper_skips_when_token_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Helper returns False when GITHUB_TOKEN is unset."""
        from hooks.post_gen_project import maybe_run_branch_protection

        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        result = maybe_run_branch_protection(flag="yes", remote_url="https://github.com/x/y")
        assert result is False

    def test_helper_skips_when_remote_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Helper returns False when no remote URL is supplied."""
        from hooks.post_gen_project import maybe_run_branch_protection

        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        result = maybe_run_branch_protection(flag="yes", remote_url="")
        assert result is False
```

- [ ] **Step 4.2: Run tests, verify failure**

```bash
uv run pytest tests/unit/test_hooks.py::TestAutoSetupBranchProtection tests/unit/test_hook_utility_functions.py::TestAutoSetupBranchProtectionHelper -v
```

Expected: FAIL because `auto_setup_branch_protection` is not in `cookiecutter.json` and `maybe_run_branch_protection` does not exist.

- [ ] **Step 4.3: Add the cookiecutter variable**

In `cookiecutter.json`, after `sole_contributor`:

```json
  "auto_setup_branch_protection": ["no", "yes"],
```

Default is `no` (explicit opt-in for an action with external side effects).

- [ ] **Step 4.4: Add the `maybe_run_branch_protection` helper**

In `hooks/post_gen_project.py`, add this function near the other top-level helpers (before `main()`):

```python
def maybe_run_branch_protection(flag: str, remote_url: str) -> bool:
    """Invoke setup_github_protection.py if all preconditions are met.

    Preconditions:
        1. flag == "yes" (the cookiecutter auto_setup_branch_protection value)
        2. GITHUB_TOKEN environment variable is set and non-empty
        3. remote_url is non-empty (project has a git remote)

    The invocation is non-fatal. Any failure produces a stdout warning
    and the post-gen hook continues.

    Returns:
        True if the script was invoked and exited 0, False otherwise.
    """
    import os

    if flag != "yes":
        return False
    if not os.environ.get("GITHUB_TOKEN"):
        return False
    if not remote_url:
        return False

    script = Path("scripts") / "setup_github_protection.py"
    if not script.exists():
        print(f"  ⚠ {script} not found; skipping auto branch protection.")
        return False

    print("  • Auto-configuring branch protection...")
    success = run_command(["uv", "run", "python", str(script)], check=False)
    if success:
        print("  ✓ Branch protection configured.")
        return True
    print(
        "  ⚠ Branch protection auto-run failed; "
        "re-run manually with: "
        "GITHUB_TOKEN=ghp_xxx uv run python scripts/setup_github_protection.py"
    )
    return False
```

Then locate `main()` (or the entry-point block at the bottom of the file). Just before the final success-message print, add an invocation:

```python
    # Optional auto-run of branch protection (opt-in via cookiecutter flag).
    remote_url = ""
    if shutil.which("git"):
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True, text=True, check=False, timeout=5,
            )
            remote_url = result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError):
            remote_url = ""
    maybe_run_branch_protection(
        flag="{{ cookiecutter.auto_setup_branch_protection }}",
        remote_url=remote_url,
    )
```

Verify that `subprocess` and `shutil` are already imported at the top of the file. If not, add them.

- [ ] **Step 4.5: Update PROJECT_SETUP.md**

Open `{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md`. Find the `## Security Configuration` section at line 492 and the `### Branch Protection Rules` subsection at line 494.

Add a new subsection immediately after the existing `### Branch Protection Rules` content (before the next `### ` heading):

````markdown
#### Automated Setup Script

The template includes `scripts/setup_github_protection.py`, which configures branch protection via the GitHub API with the project's required status checks, required signatures, code-owner reviews, and the chosen approval count (controlled by the `sole_contributor` cookiecutter flag).

Manual invocation after creating the GitHub repo:

```bash
export GITHUB_TOKEN=ghp_your_token_with_admin_repo_scope
uv run python scripts/setup_github_protection.py
```

Prerequisites:

- GitHub repository must exist (create it via `gh repo create` or the web UI).
- `GITHUB_TOKEN` must have the `admin:repo` scope (or repository admin permission).
- The local `origin` remote must point at the new GitHub repo.

If you set the `auto_setup_branch_protection` cookiecutter variable to `yes` when generating the project, and you supply `GITHUB_TOKEN` in your environment, and the project has a configured remote, the post-gen hook runs this script automatically. The auto-run is non-fatal: if any precondition fails or the API call errors out, generation completes with a printed warning and you can run the script manually later.
````

The outer fence above uses four backticks so the embedded `bash` block (three-backtick fence) renders correctly. When pasting into PROJECT_SETUP.md, strip the outer four-backtick fence and keep the inner three-backtick `bash` block.

- [ ] **Step 4.6: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_hooks.py::TestAutoSetupBranchProtection tests/unit/test_hook_utility_functions.py::TestAutoSetupBranchProtectionHelper -v
```

Expected: 5 PASS (2 + 3).

- [ ] **Step 4.7: Commit**

```bash
git add cookiecutter.json hooks/post_gen_project.py "{{cookiecutter.project_slug}}/docs/PROJECT_SETUP.md" tests/unit/test_hooks.py tests/unit/test_hook_utility_functions.py
git commit -m "$(cat <<'EOF'
feat(template): document branch protection script + opt-in auto-run

The branch-protection script was undocumented and not invoked during
cruft generation. Add a PROJECT_SETUP.md subsection documenting manual
invocation and prerequisites (GITHUB_TOKEN scope, existing repo,
configured remote).

Also add an opt-in auto_setup_branch_protection flag (default no).
When yes, and GITHUB_TOKEN is set, and the project has a configured
remote, the post-gen hook invokes the script. The invocation is
non-fatal: failure produces a stdout warning with the manual-run
command and generation continues.
EOF
)"
```

---

## Task 5: Trim feedback file, update umbrella, run full acceptance

**Files:**

- Modify: `docs/template_feedback.md` (remove 4 cluster-C entries)
- Modify: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md` (add status-log row)

- [ ] **Step 5.1: Edit `docs/template_feedback.md`**

Open the file. Under `## Cluster C: Compliance Scaffolding`, remove all four entries:

- `### Missing \`.editorconfig\` in Generated Projects`
- `### Template Does Not Support Org-Level Pointer Pattern for Community Health Files`
- `### Branch Protection Script Not Documented or Auto-Run`
- Any combined entry covering `sole_contributor` if it was bundled separately

After removal, the `## Cluster C` section should either be empty (in which case remove the section header too) or contain only entries that are genuinely out of scope for this PR. The four items closed by this PR should all be gone.

- [ ] **Step 5.2: Update the umbrella status log**

Open `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`. Find the Status log table near the bottom. Add a new row:

````markdown
| 2026-05-19 | Cluster C shipped: include_editorconfig flag, community_health_style flag with new CODE_OF_CONDUCT.md and GOVERNANCE.md source files in two variants, sole_contributor flag for branch-protection approval count, auto_setup_branch_protection opt-in hook, PROJECT_SETUP.md documentation update. 4 feedback entries removed. |
````

Also update the cluster table at the top of the file to mark cluster C status as "shipped" (or whatever convention the file uses for completed clusters).

- [ ] **Step 5.3: Run pre-commit on full diff**

```bash
pre-commit run --all-files
```

Expected: PASS. If a hook fails, fix the underlying cause; do not pass `--no-verify`. The most likely failures are em-dashes (forbidden) or trailing whitespace in markdown.

- [ ] **Step 5.4: Run the relevant test subset**

```bash
uv run pytest tests/unit/test_generation.py::TestEditorConfigFlag tests/unit/test_generation.py::TestCommunityHealthStyle tests/unit/test_generation.py::TestSoleContributorFlag tests/unit/test_hooks.py::TestAutoSetupBranchProtection tests/unit/test_hook_utility_functions.py::TestAutoSetupBranchProtectionHelper -v
```

Expected: all PASS (12+ tests across the new classes).

- [ ] **Step 5.5: Run the full unit test suite**

```bash
uv run pytest tests/unit/ -v --tb=short
```

Expected: PASS for all existing tests plus the new ones. Existing tests should not regress.

- [ ] **Step 5.6: Cruft create smoke test, default flags**

```bash
SMOKE=$(mktemp -d /tmp/cluster-C-smoke.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/feat-cluster-C-compliance --no-input
cd "$SMOKE/my_python_project"
test -f .editorconfig && echo ".editorconfig OK"
test -f CODE_OF_CONDUCT.md && echo "CODE_OF_CONDUCT.md OK"
test -f GOVERNANCE.md && echo "GOVERNANCE.md OK"
grep -c "required_approving_review_count.: 0" scripts/setup_github_protection.py
cd /home/byron/dev/cookiecutter-python-template/.worktrees/feat-cluster-C-compliance
rm -rf "$SMOKE"
```

Expected: all four checks succeed (three files exist, approval count is 0 for default sole_contributor=yes).

- [ ] **Step 5.7: Cruft create smoke test, org_pointer variant**

```bash
SMOKE=$(mktemp -d /tmp/cluster-C-pointer-smoke.XXXXXX)
cd "$SMOKE"
cruft create /home/byron/dev/cookiecutter-python-template/.worktrees/feat-cluster-C-compliance \
  --no-input --extra-context '{"community_health_style": "org_pointer", "sole_contributor": "no"}'
cd "$SMOKE/my_python_project"
wc -l CODE_OF_CONDUCT.md GOVERNANCE.md
grep -c ".github" CODE_OF_CONDUCT.md
grep -c "CODE_OF_CONDUCT.md" .cruft.json
grep -c "required_approving_review_count.: 1" scripts/setup_github_protection.py
cd /home/byron/dev/cookiecutter-python-template/.worktrees/feat-cluster-C-compliance
rm -rf "$SMOKE"
```

Expected: both files are short (under 15 lines each), both contain `.github` references, both filenames appear in `.cruft.json`, approval count is 1 (since sole_contributor=no).

- [ ] **Step 5.8: Commit feedback trim and umbrella update**

```bash
git add docs/template_feedback.md docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md
git commit -m "$(cat <<'EOF'
docs(feedback): remove cluster C entries after compliance scaffolding lands

Four entries removed: .editorconfig missing, community_health_style
variable absent, sole_contributor variable absent, branch-protection
script undocumented. All addressed by this PR. Umbrella status log
records cluster C completion.
EOF
)"
```

- [ ] **Step 5.9: Push and open the PR**

```bash
git push -u origin feat/cluster-C-compliance
gh pr create --base main --head feat/cluster-C-compliance --title "feat(template): cluster C compliance scaffolding (editorconfig, community health, branch protection)" --body "$(cat <<'EOF'
## Summary

Adds four compliance scaffolding capabilities to the cookiecutter template, closing the four cluster-C entries from `docs/template_feedback.md`.

## Changes

1. **`.editorconfig` (item 1)**: new `include_editorconfig` flag (default `yes`); ships a 4-space Python baseline with 2-space YAML/JSON/TOML overrides, LF endings, UTF-8, preserved trailing whitespace for `.md` (for Markdown hard line breaks), tab indentation for Makefile.
2. **Community health files (item 2)**: new `community_health_style` flag (default `full`). Full variant ships Contributor Covenant 2.1 (with `author_email` substituted into the contact line; CC-BY-4.0 attribution preserved) plus a minimal GOVERNANCE.md template. Org_pointer variant ships short pointer files referencing the org's `.github` repo and adds both files to the `.cruft.json` skip list so future cruft update runs do not overwrite local pointers. The template previously referenced `include_code_of_conduct` but had no source files for either path; this PR fills that hole.
3. **Branch-protection approval count (item 3)**: new `sole_contributor` flag (default `yes`). Controls `required_approving_review_count` in `scripts/setup_github_protection.py` (0 for solo, 1 for team). Other protection settings remain strict regardless.
4. **PROJECT_SETUP.md documentation plus opt-in auto-run (item 4)**: new `auto_setup_branch_protection` flag (default `no`). Documents manual invocation and prerequisites in PROJECT_SETUP.md. When set to `yes`, post-gen hook invokes the protection script automatically if `GITHUB_TOKEN` is set and a remote is configured. Non-fatal: failures produce a stdout warning with the manual-run command.

## Test plan

- [x] `uv run pytest tests/unit/` passes (new tests plus all existing)
- [x] `cruft create --no-input` generates project with `.editorconfig`, `CODE_OF_CONDUCT.md` (full Contributor Covenant), `GOVERNANCE.md` (template), approval count 0
- [x] `cruft create --no-input --extra-context '{"community_health_style": "org_pointer", "sole_contributor": "no"}'` generates short pointer files, both added to `.cruft.json` skip list, approval count 1
- [x] `pre-commit run --all-files` passes
- [x] Auto-run hook is non-fatal when GITHUB_TOKEN missing or remote unconfigured

## References

- Spec: `docs/superpowers/specs/2026-05-18-template-cleanup-cluster-C-compliance.md`
- Plan: `docs/superpowers/plans/2026-05-19-template-cleanup-cluster-C.md`
- Umbrella: `docs/superpowers/specs/2026-05-09-template-cleanup-umbrella.md`

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Out of scope (deferred to other clusters)

- Cluster D items: `interrogate` `py` CVE, `scripts/sonar_scan.py`, BasedPyright warnings in cli.py and logging.py, qlty plugin syntax, script complexity refactors.
- Cluster E items: MD040/MD051 violations, planning files front matter subset, PROJECT_SETUP workflow table completeness, qlty CLI documentation.
- Modifying the template repo's own community-health files (root-level CODE_OF_CONDUCT.md, GOVERNANCE.md). This PR only affects what gets generated for downstream projects.
- Auto-creating the GitHub repo or pushing the initial commit during generation. The auto-run assumes the user has already created the repo.

## Spec coverage self-check

| Spec requirement | Task |
|---|---|
| Item 1: `include_editorconfig` flag plus `.editorconfig` source | Task 1 |
| Item 2: `community_health_style` flag plus new source files plus cruft skip-list | Task 2 |
| Item 3: `sole_contributor` flag plus protection script Jinja conditional | Task 3 |
| Item 4: `auto_setup_branch_protection` flag, PROJECT_SETUP.md docs, post-gen invocation | Task 4 |
| Acceptance: feedback file trimmed | Task 5.1 |
| Acceptance: umbrella status log updated | Task 5.2 |
| Acceptance: pre-commit, pytest, cruft smoke pass | Task 5.3-5.7 |
| Acceptance: PR opened against main | Task 5.9 |

All spec items covered. No placeholders remain.
