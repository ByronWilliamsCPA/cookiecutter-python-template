# Code Quality Tools Integration Plan
## qlty CLI, qlty Cloud, and SonarCloud

**Purpose**: Integrate three powerful code quality and security analysis tools into the cookiecutter template.

**Tools Overview**:
1. **qlty CLI** - Local code quality analysis and linting orchestration
2. **qlty Cloud** - Cloud-based code quality dashboard and trending
3. **SonarCloud** - Comprehensive continuous code quality and security platform

---

## Tool Descriptions

### 1. qlty CLI (https://qlty.sh/)

**What it is**: A unified CLI that orchestrates multiple linters and quality tools in one command.

**Benefits**:
- **Single command** to run all quality checks
- **Faster than running tools individually** (parallel execution)
- **Consistent configuration** across team
- **Pre-commit integration** for fast feedback
- **Smart caching** to avoid re-analyzing unchanged code

**Features**:
- Runs Ruff, MyPy, Bandit, and other tools in parallel
- SARIF output for GitHub integration
- Local results or push to qlty Cloud
- Configuration via `.qlty.toml`

### 2. qlty Cloud (https://qlty.sh/cloud)

**What it is**: Cloud platform for tracking code quality trends over time.

**Benefits**:
- **Quality dashboards** showing trends
- **Team collaboration** on quality issues
- **PR comments** with quality feedback
- **Historical tracking** of technical debt
- **Integration with CI/CD**

**Features**:
- Quality gate enforcement
- Issue tracking and prioritization
- Team analytics
- Slack/email notifications

### 3. SonarCloud (https://sonarcloud.io/)

**What it is**: Industry-standard continuous code quality and security platform.

**Benefits**:
- **Comprehensive analysis** (bugs, vulnerabilities, code smells, coverage)
- **Quality gates** to prevent merging bad code
- **Security hotspots** detection
- **Technical debt** estimation
- **IDE integrations** (SonarLint)

**Features**:
- 30+ languages supported
- OWASP Top 10 coverage
- Security review workflow
- Pull request decoration
- Historical metrics and trends

---

## Proposed Template Integration

### 1. Cookiecutter Options

Add to `cookiecutter.json`:

```json
{
  "_comment_code_quality": "Code Quality and Analysis Tools",
  "include_qlty": ["no", "yes"],
  "qlty_cloud_enabled": ["no", "yes"],
  "include_sonarcloud": ["no", "yes"],

  "_comment_quality_config": "Quality Tool Configuration",
  "qlty_organization": "your-org",
  "sonarcloud_organization": "your-org",
  "sonarcloud_project_key": "{{ cookiecutter.github_org_or_user }}_{{ cookiecutter.project_slug }}",

  "_comment_quality_gates": "Quality Gate Enforcement",
  "enforce_quality_gates": ["no", "yes"],
  "block_pr_on_quality_issues": ["no", "yes"]
}
```

### 2. File Structure

```
{{cookiecutter.project_slug}}/
├── .qlty.toml                          # qlty configuration (if include_qlty=yes)
├── sonar-project.properties            # SonarCloud config (if include_sonarcloud=yes)
├── .github/
│   └── workflows/
│       ├── qlty.yml                    # qlty CLI + Cloud workflow
│       ├── sonarcloud.yml              # SonarCloud analysis workflow
│       └── quality-gate.yml            # Combined quality gate check
└── .env.example
    └── # Add QLTY_TOKEN, SONAR_TOKEN
```

### 3. Pre-commit Integration

Add to `.pre-commit-config.yaml`:

```yaml
{% if cookiecutter.include_qlty == "yes" %}
  # qlty - Fast local quality checks
  - repo: https://github.com/qltysh/qlty
    rev: v0.7.0
    hooks:
      - id: qlty
        name: qlty check
        entry: qlty check --skip-cache
        language: system
        pass_filenames: false
{% endif %}
```

### 4. GitHub Actions Workflows

#### Workflow 1: qlty.yml

```yaml
{% if cookiecutter.include_qlty == "yes" -%}
name: qlty Code Quality

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write  # For PR comments
  {% if cookiecutter.qlty_cloud_enabled == "yes" -%}
  checks: write  # For check runs
  {% endif -%}

jobs:
  qlty:
    name: qlty Analysis
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '{{ cookiecutter.python_version }}'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --frozen

      - name: Install qlty CLI
        run: |
          curl -sSL https://get.qlty.sh | sh
          echo "$HOME/.qlty/bin" >> $GITHUB_PATH

      - name: Run qlty check
        run: |
          qlty check \
            --format sarif \
            --output qlty-results.sarif
        {% if cookiecutter.qlty_cloud_enabled == "yes" -%}
        env:
          QLTY_TOKEN: {% raw %}${{ secrets.QLTY_TOKEN }}{% endraw %}
        {% endif -%}

      - name: Upload SARIF to GitHub
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: qlty-results.sarif
          category: qlty

      {% if cookiecutter.qlty_cloud_enabled == "yes" -%}
      - name: Upload results to qlty Cloud
        if: always()
        run: |
          qlty upload
        env:
          QLTY_TOKEN: {% raw %}${{ secrets.QLTY_TOKEN }}{% endraw %}

      - name: Comment on PR (qlty Cloud)
        if: github.event_name == 'pull_request'
        uses: qltysh/qlty-action@v1
        with:
          token: {% raw %}${{ secrets.QLTY_TOKEN }}{% endraw %}
          github-token: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}
      {% endif -%}

      - name: Check quality gate
        {% if cookiecutter.enforce_quality_gates == "yes" -%}
        if: always()
        {% else -%}
        if: false  # Quality gate disabled
        {% endif -%}
        run: |
          # Fail if critical issues found
          qlty check --fail-on critical
{% endif -%}
```

#### Workflow 2: sonarcloud.yml

```yaml
{% if cookiecutter.include_sonarcloud == "yes" -%}
name: SonarCloud Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main, develop]
  push:
    branches: [main, develop]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write

jobs:
  sonarcloud:
    name: SonarCloud Scan
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Shallow clones disabled for SonarCloud

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '{{ cookiecutter.python_version }}'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --frozen

      - name: Run tests with coverage
        run: |
          uv run pytest --cov=src/{{ cookiecutter.project_slug }} \
            --cov-report=xml:coverage.xml \
            --cov-report=html \
            --cov-report=term

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}
          SONAR_TOKEN: {% raw %}${{ secrets.SONAR_TOKEN }}{% endraw %}
        with:
          args: >
            -Dsonar.organization={{ cookiecutter.sonarcloud_organization }}
            -Dsonar.projectKey={{ cookiecutter.sonarcloud_project_key }}
            -Dsonar.python.coverage.reportPaths=coverage.xml
            -Dsonar.sources=src/
            -Dsonar.tests=tests/
            -Dsonar.python.version={{ cookiecutter.python_version }}
            {% if cookiecutter.enforce_quality_gates == "yes" -%}
            -Dsonar.qualitygate.wait=true
            {% endif -%}

      {% if cookiecutter.block_pr_on_quality_issues == "yes" -%}
      - name: Check Quality Gate
        if: github.event_name == 'pull_request'
        run: |
          # SonarCloud quality gate status is in previous step
          # This step will fail if quality gate failed
          echo "Quality gate check completed"
      {% endif -%}
{% endif -%}
```

#### Workflow 3: quality-gate.yml (Combined)

```yaml
{% if cookiecutter.enforce_quality_gates == "yes" and (cookiecutter.include_qlty == "yes" or cookiecutter.include_sonarcloud == "yes") -%}
name: Quality Gate

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write
  statuses: write

jobs:
  quality-summary:
    name: Quality Summary
    runs-on: ubuntu-latest
    needs:
      {% if cookiecutter.include_qlty == "yes" -%}
      - qlty
      {% endif -%}
      {% if cookiecutter.include_sonarcloud == "yes" -%}
      - sonarcloud
      {% endif -%}

    steps:
      - name: Quality Gate Summary
        run: |
          echo "### Quality Gate Results" >> $GITHUB_STEP_SUMMARY
          {% if cookiecutter.include_qlty == "yes" -%}
          echo "- qlty: {% raw %}${{ needs.qlty.result }}{% endraw %}" >> $GITHUB_STEP_SUMMARY
          {% endif -%}
          {% if cookiecutter.include_sonarcloud == "yes" -%}
          echo "- SonarCloud: {% raw %}${{ needs.sonarcloud.result }}{% endraw %}" >> $GITHUB_STEP_SUMMARY
          {% endif -%}

      - name: Enforce Quality Gate
        if: {% raw %}${{ contains(needs.*.result, 'failure') }}{% endraw %}
        run: |
          echo "::error::Quality gate failed - PR cannot be merged"
          exit 1
{% endif -%}
```

### 5. Configuration Files

#### .qlty.toml

```toml
{% if cookiecutter.include_qlty == "yes" -%}
[project]
name = "{{ cookiecutter.project_name }}"
language = "python"

# Tools to run
[tools]
# Python linters
ruff = { enabled = true }
mypy = { enabled = true }
bandit = { enabled = true }
{% if cookiecutter.include_security_scanning == "yes" -%}
semgrep = { enabled = true }
{% endif -%}

# Formatters (check mode)
black = { enabled = false }  # Using ruff for formatting

# Additional checks
pylint = { enabled = false }  # Too slow, ruff covers most rules

[tools.ruff]
config = "pyproject.toml"
args = ["--output-format=json"]

[tools.mypy]
config = "pyproject.toml"
args = ["--show-error-codes", "--no-error-summary"]

[tools.bandit]
args = ["-f", "json", "-c", "pyproject.toml"]

# Ignore patterns
[ignore]
paths = [
    ".venv/",
    "__pycache__/",
    "*.pyc",
    ".git/",
    "dist/",
    "build/",
    "*.egg-info/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
]

# Quality gates (for qlty Cloud)
{% if cookiecutter.qlty_cloud_enabled == "yes" -%}
[quality_gates]
block_on_critical = {{ "true" if cookiecutter.block_pr_on_quality_issues == "yes" else "false" }}
warn_on_high = true

[quality_gates.thresholds]
critical = 0
high = 5
medium = 20
{% endif -%}

# Cache settings
[cache]
enabled = true
directory = ".qlty_cache"
{% endif -%}
```

#### sonar-project.properties

```properties
{% if cookiecutter.include_sonarcloud == "yes" -%}
# SonarCloud Configuration
sonar.organization={{ cookiecutter.sonarcloud_organization }}
sonar.projectKey={{ cookiecutter.sonarcloud_project_key }}
sonar.projectName={{ cookiecutter.project_name }}
sonar.projectVersion={{ cookiecutter.version }}

# Source and test paths
sonar.sources=src/
sonar.tests=tests/
sonar.python.version={{ cookiecutter.python_version }}

# Coverage
sonar.python.coverage.reportPaths=coverage.xml

# Exclusions
sonar.exclusions=\
  **/*_test.py,\
  **/test_*.py,\
  **/__pycache__/**,\
  **/.venv/**,\
  **/migrations/**,\
  **/dist/**,\
  **/build/**

sonar.test.exclusions=\
  **/tests/**,\
  **/*_test.py,\
  **/test_*.py

# Language-specific settings
sonar.python.pylint.reportPaths=pylint-report.txt
sonar.python.bandit.reportPaths=bandit-report.json

# Quality gate
{% if cookiecutter.enforce_quality_gates == "yes" -%}
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
{% else -%}
sonar.qualitygate.wait=false
{% endif -%}

# Issue filtering
sonar.issue.ignore.multicriteria=e1,e2

# Ignore test files for duplication
sonar.issue.ignore.multicriteria.e1.ruleKey=python:S1192
sonar.issue.ignore.multicriteria.e1.resourceKey=**/tests/**

# Ignore specific patterns
sonar.issue.ignore.multicriteria.e2.ruleKey=python:S*
sonar.issue.ignore.multicriteria.e2.resourceKey=**/__init__.py

# New code definition (for PR analysis)
sonar.newCode.referenceBranch=main
{% endif -%}
```

### 6. Environment Variables (.env.example)

```bash
# ============================================================================
# Code Quality Tools (qlty and SonarCloud)
# ============================================================================

{% if cookiecutter.include_qlty == "yes" -%}
# qlty Configuration
# Get your token from: https://cloud.qlty.sh/settings/tokens
{% if cookiecutter.qlty_cloud_enabled == "yes" -%}
QLTY_TOKEN=your-qlty-token-here
{% else -%}
# QLTY_TOKEN not needed for local qlty CLI only
{% endif -%}

{% endif -%}
{% if cookiecutter.include_sonarcloud == "yes" -%}
# SonarCloud Configuration
# Get your token from: https://sonarcloud.io/account/security
SONAR_TOKEN=your-sonarcloud-token-here
SONAR_ORGANIZATION={{ cookiecutter.sonarcloud_organization }}
SONAR_PROJECT_KEY={{ cookiecutter.sonarcloud_project_key }}

{% endif -%}
```

### 7. Documentation Updates

#### README.md section

```markdown
## Code Quality

This project uses multiple code quality tools to ensure high standards:

{% if cookiecutter.include_qlty == "yes" -%}
### qlty CLI

Run all quality checks locally:

\`\`\`bash
# Install qlty
curl -sSL https://get.qlty.sh | sh

# Run checks
qlty check

# Run checks on changed files only
qlty check --changed

# Auto-fix issues where possible
qlty check --fix
\`\`\`

{% if cookiecutter.qlty_cloud_enabled == "yes" -%}
**qlty Cloud Dashboard**: View quality trends at https://cloud.qlty.sh/{{ cookiecutter.qlty_organization }}/{{ cookiecutter.project_slug }}
{% endif -%}

{% endif -%}
{% if cookiecutter.include_sonarcloud == "yes" -%}
### SonarCloud

Continuous code quality and security analysis.

**Dashboard**: https://sonarcloud.io/dashboard?id={{ cookiecutter.sonarcloud_project_key }}

SonarCloud analyzes:
- Code smells and technical debt
- Security vulnerabilities and hotspots
- Test coverage
- Duplications
- Complexity metrics

{% if cookiecutter.enforce_quality_gates == "yes" -%}
**Quality Gate**: PRs are blocked if quality gate fails.
{% endif -%}

{% endif -%}
### Quality Standards

{% if cookiecutter.enforce_quality_gates == "yes" -%}
- **Quality gates enforced**: PRs must pass all quality checks
{% else -%}
- **Quality gates advisory**: Issues reported but PRs not blocked
{% endif -%}
- **Code coverage target**: {{ cookiecutter.code_coverage_target }}%
- **Security**: No critical or high severity issues
- **Complexity**: Cyclomatic complexity < 15
```

### 8. Post-Generation Hook Updates

Add to `hooks/post_gen_project.py`:

```python
# Remove qlty config if not needed
if "{{ cookiecutter.include_qlty }}" == "no":
    remove_file(Path(".qlty.toml"))
    remove_file(Path(".github/workflows/qlty.yml"))

# Remove SonarCloud config if not needed
if "{{ cookiecutter.include_sonarcloud }}" == "no":
    remove_file(Path("sonar-project.properties"))
    remove_file(Path(".github/workflows/sonarcloud.yml"))

# Remove quality gate workflow if no tools enabled
if "{{ cookiecutter.enforce_quality_gates }}" == "no":
    remove_file(Path(".github/workflows/quality-gate.yml"))
```

---

## Benefits Summary

### With qlty CLI

**Developer Experience**:
- ✅ Single command runs all quality checks
- ✅ 3-5x faster than running tools individually
- ✅ Pre-commit hook integration (fast feedback)
- ✅ Smart caching (only check changed code)

**Team Benefits**:
- ✅ Consistent quality checks across team
- ✅ Easy onboarding (one tool to learn)
- ✅ SARIF output integrates with GitHub

### With qlty Cloud

**Visibility**:
- ✅ Quality trends over time
- ✅ Team dashboard showing who needs help
- ✅ Issue prioritization

**Collaboration**:
- ✅ PR comments with actionable feedback
- ✅ Slack notifications for quality issues
- ✅ Historical tracking

### With SonarCloud

**Comprehensive Analysis**:
- ✅ Industry-standard quality metrics
- ✅ Security vulnerability detection (OWASP Top 10)
- ✅ Technical debt estimation
- ✅ Duplication detection

**Enterprise Features**:
- ✅ Quality gate enforcement
- ✅ Branch analysis
- ✅ Historical comparisons
- ✅ IDE integration (SonarLint)

---

## Tool Comparison Matrix

| Feature | qlty CLI | qlty Cloud | SonarCloud | Current Template |
|---------|----------|------------|------------|------------------|
| **Local execution** | ✅ Fast | N/A | ⚠️ Slow | ✅ Individual tools |
| **Pre-commit hooks** | ✅ Yes | N/A | ❌ No | ✅ Yes |
| **CI/CD integration** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Security scanning** | ✅ Via Bandit | ✅ Yes | ✅ Yes | ✅ CodeQL, Bandit |
| **Code smells** | ✅ Via Ruff | ✅ Yes | ✅ Yes | ✅ Ruff |
| **Coverage tracking** | ❌ No | ✅ Trends | ✅ Yes | ✅ Codecov |
| **PR decoration** | ⚠️ Basic | ✅ Rich | ✅ Rich | ⚠️ Basic |
| **Quality gates** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Historical trends** | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Limited |
| **Tech debt estimation** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **IDE integration** | ❌ No | ❌ No | ✅ SonarLint | ⚠️ Via tools |
| **Cost** | 💰 Free | 💰💰 Paid | 💰 Free (OSS) | 💰 Free |

---

## Recommended Configuration

### For Small Teams (< 10 developers)

```json
{
  "include_qlty": "yes",
  "qlty_cloud_enabled": "no",  // Use free CLI only
  "include_sonarcloud": "yes",  // Free for open source
  "enforce_quality_gates": "yes",
  "block_pr_on_quality_issues": "yes"
}
```

**Why**: qlty CLI for fast local checks, SonarCloud for comprehensive analysis. Both free for open source.

### For Medium Teams (10-50 developers)

```json
{
  "include_qlty": "yes",
  "qlty_cloud_enabled": "yes",  // Paid but worth it
  "include_sonarcloud": "yes",
  "enforce_quality_gates": "yes",
  "block_pr_on_quality_issues": "yes"
}
```

**Why**: qlty Cloud adds team collaboration features. SonarCloud provides enterprise-grade analysis.

### For Large Organizations (50+ developers)

```json
{
  "include_qlty": "yes",
  "qlty_cloud_enabled": "yes",
  "include_sonarcloud": "yes",
  "enforce_quality_gates": "yes",
  "block_pr_on_quality_issues": "yes"
}
```

**Why**: Both tools provide value at scale. qlty for fast feedback, SonarCloud for governance.

### For Solo Developers / Open Source

```json
{
  "include_qlty": "yes",
  "qlty_cloud_enabled": "no",  // CLI is enough
  "include_sonarcloud": "yes",  // Free for OSS
  "enforce_quality_gates": "no",  // Don't block yourself
  "block_pr_on_quality_issues": "no"
}
```

**Why**: Both free, low maintenance, high value.

---

## Implementation Checklist

- [ ] Update `cookiecutter.json` with quality tool options
- [ ] Create `.qlty.toml` template configuration
- [ ] Create `sonar-project.properties` template
- [ ] Add `qlty.yml` GitHub Actions workflow
- [ ] Add `sonarcloud.yml` GitHub Actions workflow
- [ ] Add `quality-gate.yml` combined workflow
- [ ] Update `.env.example` with tokens
- [ ] Add pre-commit hook for qlty
- [ ] Update post-generation hook for cleanup
- [ ] Update README with quality tools section
- [ ] Create quality tools documentation (`docs/QUALITY_TOOLS.md`)
- [ ] Add badge support to README template
- [ ] Test qlty CLI integration locally
- [ ] Test qlty Cloud integration (if applicable)
- [ ] Test SonarCloud integration
- [ ] Update 12_FACTOR_COMPLIANCE.md (observability factor)

---

## Next Steps

1. **Add to cookiecutter.json** - New quality tool options
2. **Create configuration files** - .qlty.toml and sonar-project.properties
3. **Add GitHub Actions workflows** - qlty.yml, sonarcloud.yml, quality-gate.yml
4. **Update documentation** - README and dedicated quality tools guide
5. **Test integration** - Verify all tools work correctly

---

**Status**: Proposal (ready for implementation)
**Estimated Effort**: 6-8 hours
**Priority**: MEDIUM-HIGH (enhances quality and security)
**Value**: High (industry-standard tooling, better code quality)
