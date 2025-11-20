# Qlty Configuration Reference

**Purpose**: This document clarifies what plugins are configured in `.qlty/qlty.toml` and which are conditional vs. always-included.

**Key Change**: Since this is a **Python project template**, all core Python quality and security tools are **ALWAYS included** (no conditionals). Only platform-specific tools (Docker, etc.) remain conditional.

## Plugin Configuration Summary

### Always-Included Plugins (Core to Python Development)

Since this is a Python project template, these plugins are **ALWAYS** present in every generated project:

#### Core Python Quality Tools (ALWAYS INCLUDED)

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "ruff"
version = "latest"
package_file = "pyproject.toml"
config_files = ["pyproject.toml", "ruff.toml", ".ruff.toml"]
triggers = ["pre-commit", "pre-push", "ide", "build"]
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "mypy"
version = "latest"
package_file = "pyproject.toml"
config_files = ["pyproject.toml", "mypy.ini", ".mypy.ini"]
triggers = ["pre-push", "build"]  # Slower, so not on every commit
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "bandit"
version = "latest"
package_file = "pyproject.toml"
config_files = ["pyproject.toml", ".bandit"]
triggers = ["pre-push", "build"]
```

#### Security Tools (ALWAYS INCLUDED)

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "gitleaks"
version = "latest"
triggers = ["pre-commit", "pre-push", "build"]
```

```toml
# ALWAYS INCLUDED - No conditionals
# NOTE: This REPLACES the old "safety" tool
[[plugin]]
name = "osv_scanner"
version = "latest"
package_file = "requirements.txt"
triggers = ["pre-push", "build"]
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "semgrep"
version = "latest"
config_files = [".semgrep.yml", ".semgrep.yaml"]
triggers = ["pre-push", "build"]
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "trufflehog"
version = "latest"
triggers = ["pre-commit", "pre-push", "build"]
```

#### File & Configuration Tools (ALWAYS INCLUDED)

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "markdownlint"
# ... configuration ...
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "yamllint"
# ... configuration ...
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "actionlint"
# ... configuration ...
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "shellcheck"
# ... configuration ...
```

```toml
# ALWAYS INCLUDED - No conditionals
[[plugin]]
name = "prettier"
# ... configuration ...
```

### Conditional Plugins (Platform-Specific Only)

These plugins are **ONLY** included when specific platforms/features are enabled:

#### Container & Infrastructure Tools (Docker-specific)

```toml
# Included when: include_docker == "yes" (default: no)
[[plugin]]
name = "hadolint"
version = "latest"
triggers = ["pre-push", "build"]
```

```toml
# Included when: include_docker == "yes" (default: no)
[[plugin]]
name = "trivy"
version = "latest"
triggers = ["pre-push", "build"]
```

```toml
# Included when: include_docker == "yes" (default: no)
[[plugin]]
name = "checkov"
version = "latest"
triggers = ["pre-push", "build"]
```

## Why OSV Scanner Instead of "safety"?

**Question**: "I also dont see safety"

**Answer**: We intentionally replaced `safety` with `osv_scanner` because:

1. **Better Coverage**: OSV Scanner uses Google's Open Source Vulnerabilities database, which aggregates:
   - GitHub Security Advisories
   - PyPI advisories
   - National Vulnerability Database (NVD)
   - Multiple other sources

2. **Industry Standard**: OSV Scanner is the recommended tool by Google and widely adopted in the Python ecosystem

3. **Free Tier Limitations**: Safety's free tier has become more restrictive, while OSV Scanner is fully open source

4. **Better Integration**: OSV Scanner works seamlessly with Poetry, UV, and other modern dependency managers

5. **More Accurate**: Fewer false positives and better vulnerability detection

## Default Configuration (Every Python Project)

**ALL Python projects** generated from this template include these **12 core plugins**:

**Core Python Quality (3):**

- ✅ Ruff (linting + formatting)
- ✅ Mypy (type checking)
- ✅ Bandit (security linting)

**Security & Secrets (4):**

- ✅ Gitleaks (secrets detection)
- ✅ OSV Scanner (dependency vulnerabilities) **← Replaces safety**
- ✅ Semgrep (advanced SAST)
- ✅ TruffleHog (entropy-based secrets)

**File & Configuration (5):**

- ✅ Markdownlint (Markdown linting)
- ✅ Yamllint (YAML validation)
- ✅ Actionlint (GitHub Actions validation)
- ✅ Shellcheck (shell script analysis)
- ✅ Prettier (JSON/YAML/Markdown formatting)

**Total: 12 plugins** (ALWAYS included for Python projects)

## Full Configuration (With Docker Support)

When you generate a project with `include_docker=yes`, you get:

**All 12 core plugins PLUS 3 Docker-specific tools:**

- ✅ Hadolint (Dockerfile linting)
- ✅ Trivy (container scanning)
- ✅ Checkov (IaC security)

**Total: 15 plugins** (with Docker support)

## How to Verify Your Configuration

### 1. Check Rendered Configuration

After generating a project with cruft/cookiecutter:

```bash
cd your-generated-project
cat .qlty/qlty.toml | grep -A 3 "^\[\[plugin\]\]"
```

This will show all active plugins (with Jinja2 conditionals evaluated).

### 2. Verify Qlty Detection

```bash
cd your-generated-project
qlty plugins list
```

This shows which plugins Qlty actually detected and will run.

### 3. Check Tool Availability

```bash
qlty check --dry-run
```

This shows what Qlty would run without actually executing the checks.

## Cookiecutter Variables Reference

**Note**: Core Python and security tools are now ALWAYS included. Only platform-specific tools remain conditional.

| Variable | Default | Controls |
|----------|---------|----------|
| `include_docker` | `no` | Docker-specific tools: Hadolint, Trivy, Checkov |

**Removed Variables** (tools now always included):

- ~~`use_ruff`~~ - Ruff is always included
- ~~`use_mypy`~~ - Mypy is always included
- ~~`include_security_scanning`~~ - Bandit, OSV Scanner, Semgrep, TruffleHog always included
- ~~`include_gitleaks`~~ - Gitleaks is always included

## Complete Tool List

### Core Tools (12) - ALWAYS INCLUDED

#### Python Quality (3)

1. **Ruff** - Fast linting and formatting (replaces Black, Flake8, isort, pyupgrade)
2. **Mypy** - Static type checking
3. **Bandit** - Python security linter

#### Security & Secrets (4)

4. **Gitleaks** - Git secrets scanner
5. **TruffleHog** - Entropy-based secrets detection
6. **OSV Scanner** - Dependency vulnerability scanning (replaces safety)
7. **Semgrep** - Advanced SAST with OWASP rulesets

#### File & Configuration (5)

8. **Markdownlint** - Markdown linting
9. **Yamllint** - YAML validation
10. **Prettier** - JSON/YAML/Markdown formatting
11. **Actionlint** - GitHub Actions workflow validation
12. **Shellcheck** - Shell script analysis

### Platform-Specific Tools (3) - Conditional on Docker

13. **Hadolint** - Dockerfile linting (only when `include_docker=yes`)
14. **Trivy** - Container vulnerability scanner (only when `include_docker=yes`)
15. **Checkov** - Infrastructure as Code security (only when `include_docker=yes`)

---

**Document Version**: 2.0
**Last Updated**: 2025-11-19
**Breaking Change**: Core Python and security tools are now ALWAYS included (no conditionals)
**Maintained By**: cookiecutter-python-template maintainers
