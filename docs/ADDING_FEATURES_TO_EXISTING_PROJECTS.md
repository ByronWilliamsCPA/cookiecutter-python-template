# Adding Features to Existing Projects

> **Status**: Reference Guide
> **Version**: 1.0.0
> **Last Updated**: 2025-01-17

This guide explains how to add template features to projects that were already generated from this cookiecutter template.

## Table of Contents

- [Understanding Cruft Limitations](#understanding-cruft-limitations)
- [Methods for Adding Features](#methods-for-adding-features)
- [Feature-Specific Guides](#feature-specific-guides)
- [Troubleshooting](#troubleshooting)

## Understanding Cruft Limitations

### What Cruft CAN Do

Cruft is excellent for keeping projects synchronized with template updates:

```bash
# Update existing project with template changes
cd your-project
cruft update

# Check if your project is up-to-date
cruft check

# Show diff between current and template
cruft diff
```

**Cruft handles:**
- ✅ File content updates in non-conditional sections
- ✅ New files added to template (if not in conditional blocks)
- ✅ Deleted files removed from template
- ✅ Changes to files that exist in both project and template

### What Cruft CANNOT Do

**The core limitation**: Cruft cannot change cookiecutter variable values after project generation.

When you generate a project with `include_sonarcloud=no`, cruft stores this choice in `.cruft.json`:

```json
{
    "template": "https://github.com/yourusername/cookiecutter-python-template",
    "commit": "abc123...",
    "context": {
        "cookiecutter": {
            "include_sonarcloud": "no",
            "include_mutation_testing": "no"
        }
    }
}
```

**Running `cruft update` will:**
- ❌ NOT add files/code inside `{% if cookiecutter.include_sonarcloud == "yes" %}` blocks
- ❌ NOT change the stored context values
- ❌ NOT re-evaluate conditional template logic

**This means:**
- Files that were excluded during generation won't appear
- Dependencies that weren't added won't be installed
- Configuration sections that were skipped won't be generated

## Methods for Adding Features

### Method 1: Manual Copy (Recommended for Simple Features)

**Best for**: Single files, small features, well-defined additions

**Steps:**

1. Generate a temporary test project with the feature enabled:
   ```bash
   cd /tmp
   cruft create /path/to/cookiecutter-python-template \
     --config-file <(echo 'default_context: {"project_name": "test", "include_sonarcloud": "yes"}')
   ```

2. Identify files/changes related to the feature:
   ```bash
   cd test
   # Review the generated files
   find . -name "*sonar*"
   git log --all --full-history --oneline
   ```

3. Copy relevant files to your project:
   ```bash
   # Copy workflow file
   cp /tmp/test/.github/workflows/sonarcloud.yml ~/your-project/.github/workflows/

   # Copy configuration
   cp /tmp/test/sonar-project.properties ~/your-project/
   ```

4. Update `pyproject.toml` dependencies if needed:
   ```bash
   # Compare dependencies
   diff /tmp/test/pyproject.toml ~/your-project/pyproject.toml

   # Add missing dependencies
   cd ~/your-project
   uv add pytest-cov  # Example
   ```

5. Update `.cruft.json` to reflect the change:
   ```bash
   cd ~/your-project
   # Edit .cruft.json and change "include_sonarcloud": "no" to "yes"
   ```

6. Clean up:
   ```bash
   rm -rf /tmp/test
   ```

### Method 2: Feature Branch Comparison (Recommended for Complex Features)

**Best for**: Features with many files, complex integrations, multiple dependencies

**Steps:**

1. Create a comparison project:
   ```bash
   cd /tmp
   # Generate with feature disabled (matches your current project)
   cruft create /path/to/template --config-file <(echo 'default_context: {"project_name": "compare-off", "include_mutation_testing": "no"}')

   # Generate with feature enabled
   cruft create /path/to/template --config-file <(echo 'default_context: {"project_name": "compare-on", "include_mutation_testing": "yes"}')
   ```

2. Create git repos to compare:
   ```bash
   cd /tmp/compare-off && git init && git add . && git commit -m "without feature"
   cd /tmp/compare-on && git init && git add . && git commit -m "with feature"
   ```

3. Generate a diff:
   ```bash
   diff -ruN /tmp/compare-off /tmp/compare-on > ~/feature-diff.patch

   # Or use git diff for better output
   cd /tmp/compare-on
   git diff --no-index ../compare-off . > ~/feature-diff.patch
   ```

4. Review and selectively apply changes:
   ```bash
   cd ~/your-project
   # Review the patch first
   less ~/feature-diff.patch

   # Apply specific files or sections manually
   # (full patch application rarely works due to context differences)
   ```

5. Extract specific changes:
   ```bash
   # Example: Extract only workflow files
   cd /tmp/compare-on
   cp -r .github/workflows/*.yml ~/your-project/.github/workflows/

   # Example: Extract dependency additions
   grep -A 50 '\[project.optional-dependencies\]' pyproject.toml > /tmp/new-deps.txt
   ```

### Method 3: Selective File Regeneration

**Best for**: When you want to regenerate specific files while keeping others

**Steps:**

1. Identify files you want to regenerate:
   ```bash
   # List all template files for a specific feature
   find {{cookiecutter.project_slug}} -type f | grep -i sonarcloud
   ```

2. Backup your project:
   ```bash
   cd ~/your-project
   git commit -am "backup before feature addition"
   git tag backup-pre-sonarcloud
   ```

3. Use cookiecutter with `--overwrite-if-exists`:
   ```bash
   cd ~/your-project/..
   cookiecutter /path/to/template \
     --overwrite-if-exists \
     --output-dir . \
     --config-file your-project/.cruft.json

   # When prompted, enable the feature you want
   ```

4. Review changes and selectively keep/discard:
   ```bash
   cd ~/your-project
   git status
   git diff

   # Keep wanted changes
   git add .github/workflows/sonarcloud.yml
   git add sonar-project.properties

   # Discard unwanted changes
   git checkout -- other-file.py
   ```

**⚠️ Warning**: This method can overwrite customizations. Always work from a clean git state.

### Method 4: Manual Implementation (For Understanding)

**Best for**: Learning, highly customized projects, or when automation fails

**Steps:**

1. Read the template source code:
   ```bash
   # Find all conditional blocks for a feature
   cd /path/to/template
   grep -r "include_mutation_testing" {{cookiecutter.project_slug}}
   ```

2. Read generated examples:
   ```bash
   # Generate a test project
   cruft create /path/to/template --config-file <(echo 'default_context: {"include_mutation_testing": "yes"}')
   ```

3. Manually implement each component:
   - Add dependencies to `pyproject.toml`
   - Create configuration files
   - Add workflow files
   - Update documentation

4. Test thoroughly:
   ```bash
   uv sync
   uv run pytest
   # Test the new feature
   ```

## Feature-Specific Guides

### Adding SonarCloud

**Files to add:**
- `.github/workflows/sonarcloud.yml`
- `sonar-project.properties`

**Dependencies**: None (uses GitHub Action)

**Configuration**:
1. Create SonarCloud project at sonarcloud.io
2. Add `SONAR_TOKEN` secret to GitHub repository
3. Update `sonar-project.properties` with your project key

**Steps**:
```bash
# Generate reference project
cd /tmp && cruft create /path/to/template --config-file <(echo 'default_context: {"include_sonarcloud": "yes"}')

# Copy files
cp /tmp/my_project/.github/workflows/sonarcloud.yml ~/your-project/.github/workflows/
cp /tmp/my_project/sonar-project.properties ~/your-project/

# Update .cruft.json
cd ~/your-project
# Edit .cruft.json: "include_sonarcloud": "yes"

# Commit
git add .github/workflows/sonarcloud.yml sonar-project.properties .cruft.json
git commit -m "feat: add SonarCloud integration"
```

### Adding Mutation Testing

**Files to add:**
- Configuration in `pyproject.toml` under `[tool.mutmut]`
- Optionally: `.github/workflows/mutation-testing.yml`

**Dependencies**:
```toml
[project.optional-dependencies]
test = [
    # ... existing
    "mutmut>=2.4.0",
]
```

**Steps**:
```bash
# Add dependency
cd ~/your-project
uv add --optional test mutmut

# Generate reference config
cd /tmp && cruft create /path/to/template --config-file <(echo 'default_context: {"include_mutation_testing": "yes"}')

# Copy configuration section from pyproject.toml
# Extract [tool.mutmut] section and add to your project

# Test it works
uv run mutmut run --paths-to-mutate=src/
```

### Adding MCP Server Support

**Files to add:**
- `src/{{project_slug}}/mcp/` directory structure
- `src/{{project_slug}}/mcp/server.py`
- `src/{{project_slug}}/mcp/__init__.py`
- Entry point in `pyproject.toml`

**Dependencies**:
```toml
[project.dependencies]
mcp = ">=0.9.0"

[project.optional-dependencies]
mcp = [
    "mcp[cli]>=0.9.0",
]
```

**Steps**:
```bash
# Generate reference
cd /tmp && cruft create /path/to/template --config-file <(echo 'default_context: {"include_mcp_server": "yes"}')

# Copy MCP directory
cp -r /tmp/my_project/src/my_project/mcp ~/your-project/src/your_package/

# Add dependencies
cd ~/your-project
uv add "mcp>=0.9.0"
uv add --optional mcp "mcp[cli]>=0.9.0"

# Add entry point to pyproject.toml
# [project.scripts]
# your-package-mcp = "your_package.mcp.server:main"

# Test
uv run your-package-mcp
```

### Adding Fuzzing

**Files to add:**
- `.github/workflows/fuzzing.yml`
- `tests/fuzz/` directory with fuzz tests

**Dependencies**:
```toml
[project.optional-dependencies]
test = [
    "atheris>=2.3.0; platform_system=='Linux'",
    "hypothesis>=6.0.0",
]
```

**Steps**:
```bash
# Generate reference
cd /tmp && cruft create /path/to/template --config-file <(echo 'default_context: {"include_fuzzing": "yes"}')

# Copy workflow and tests
cp /tmp/my_project/.github/workflows/fuzzing.yml ~/your-project/.github/workflows/
cp -r /tmp/my_project/tests/fuzz ~/your-project/tests/

# Add dependencies
cd ~/your-project
uv add --optional test atheris hypothesis

# Run fuzz tests locally
uv run pytest tests/fuzz/
```

## Updating .cruft.json

After adding features manually, update `.cruft.json` to reflect the new state:

```json
{
    "template": "https://github.com/yourusername/cookiecutter-python-template",
    "commit": "latest-commit-hash",
    "context": {
        "cookiecutter": {
            "include_sonarcloud": "yes",  // Changed from "no"
            "include_mutation_testing": "yes",  // Changed from "no"
            "include_mcp_server": "yes"  // Changed from "no"
        }
    }
}
```

**Why update .cruft.json?**
- Keeps your project in sync with template expectations
- Allows future `cruft update` commands to work correctly
- Documents which features are enabled
- Prevents cruft from trying to remove manually added files

## Troubleshooting

### "Cruft update removes my manually added files"

**Cause**: `.cruft.json` context doesn't match actual project state

**Solution**:
```bash
# Update .cruft.json to reflect enabled features
# Edit the "context" section to match your additions

# Verify cruft sees no differences
cruft diff
```

### "Dependencies aren't resolving after adding feature"

**Cause**: Missing or conflicting dependencies

**Solution**:
```bash
# Check for conflicts
uv add --dry-run package-name

# Update lock file
uv lock --upgrade

# If conflicts exist, review version constraints
uv tree
```

### "Feature doesn't work after manual addition"

**Cause**: Missing configuration, incomplete file copy, or version mismatch

**Solution**:
```bash
# Generate complete reference project
cd /tmp && cruft create /path/to/template --config-file <(echo 'default_context: {"include_feature": "yes"}')

# Compare your project to reference
diff -r ~/your-project /tmp/reference-project

# Look for missing files or configuration sections
```

### "Git conflicts during cruft update"

**Cause**: Manual changes conflict with template updates

**Solution**:
```bash
# Commit or stash local changes first
git status
git commit -am "checkpoint before cruft update"

# Run cruft update
cruft update

# Resolve conflicts manually
git status
git mergetool

# Or abort and try selective update
git merge --abort
```

## Best Practices

1. **Always work from clean git state**: Commit changes before adding features
2. **Test in temporary project first**: Generate reference projects to understand changes
3. **Update .cruft.json**: Keep context synchronized with actual project state
4. **Document additions**: Add notes to your project README about manually added features
5. **Use feature branches**: Add complex features in branches, test thoroughly before merging
6. **Check template updates**: Run `cruft check` regularly to stay current with template

## Automation Opportunities

For frequently needed features, consider creating helper scripts:

```bash
#!/usr/bin/env bash
# scripts/add-sonarcloud.sh
set -e

TEMPLATE_PATH="${1:-/path/to/template}"
PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# Generate reference
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
cruft create "$TEMPLATE_PATH" --no-input --config-file <(echo 'default_context: {"include_sonarcloud": "yes"}')

# Copy files
cp my_project/.github/workflows/sonarcloud.yml "$PROJECT_ROOT/.github/workflows/"
cp my_project/sonar-project.properties "$PROJECT_ROOT/"

# Update .cruft.json
cd "$PROJECT_ROOT"
python -c "
import json
with open('.cruft.json', 'r') as f:
    cruft_data = json.load(f)
cruft_data['context']['cookiecutter']['include_sonarcloud'] = 'yes'
with open('.cruft.json', 'w') as f:
    json.dump(cruft_data, f, indent=2)
"

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ SonarCloud added successfully"
echo "Next steps:"
echo "1. Create SonarCloud project"
echo "2. Add SONAR_TOKEN secret to GitHub"
echo "3. Update sonar-project.properties with project key"
```

## Further Reading

- [Cruft Documentation](https://cruft.github.io/cruft/)
- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/)
- [Template CLAUDE.md](../CLAUDE.md) - Project-specific standards
- [Template README.md](../README.md) - Usage instructions

---

**Questions or Issues?**

If you encounter problems adding features, please:
1. Check this guide for relevant feature-specific instructions
2. Review the template source code in `{{cookiecutter.project_slug}}/`
3. Open an issue in the template repository with details
