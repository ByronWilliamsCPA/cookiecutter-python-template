# Testing Addendum - Zero-Issues & Scheduled Validation

> **Supplement to TESTING.md**
> **Added:** 2025-11-24

## Zero-Issues Testing

### Overview

The `test_zero_issues.py` test suite ensures **ZERO issues** in generated projects by validating ALL checks that run in the template repository's CI/CD.

### What's Tested

**Formatting & Linting:**
- ✅ Black formatter compliance
- ✅ Ruff linter compliance
- ✅ MyPy type checking

**Pre-commit Hooks (23 checks):**
- ✅ Trailing whitespace
- ✅ End-of-file fixer
- ✅ YAML syntax validation
- ✅ TOML syntax validation
- ✅ JSON syntax validation
- ✅ Merge conflict detection
- ✅ Private key detection
- ✅ Large files check
- ✅ Case conflicts
- ✅ Mixed line endings

**Security:**
- ✅ Bandit security scan
- ✅ Safety dependency audit
- ✅ No hardcoded secrets
- ✅ No private keys in code

**Code Quality:**
- ✅ Docstring coverage (80%+)
- ✅ No spelling errors (codespell)
- ✅ Shell script quality (shellcheck)
- ✅ Markdown quality (markdownlint)

**LLM Governance:**
- ✅ No unverified #CRITICAL tags
- ✅ No unverified #ASSUME tags
- ✅ No #LLM-MOCK tags
- ✅ No #LLM-PLACEHOLDER tags
- ✅ No other LLM debt tags

### Running Zero-Issues Tests

```bash
# Run all zero-issues tests
uv run pytest tests/test_zero_issues.py -v

# Run specific test class
uv run pytest tests/test_zero_issues.py::TestFormattingAndLinting -v
uv run pytest tests/test_zero_issues.py::TestPreCommitHooks -v
uv run pytest tests/test_zero_issues.py::TestSecurityScans -v
uv run pytest tests/test_zero_issues.py::TestCodeQuality -v

# Run comprehensive validation on all configs (SLOW)
uv run pytest tests/test_zero_issues.py::TestAllConfigsCombined -v

# Run for specific configuration
uv run pytest tests/test_zero_issues.py -k "cli-app" -v
```

### Test Coverage Matrix

The `TestAllConfigsCombined` class runs ALL validation checks on each configuration:

| Configuration | Checks Run | Expected Outcome |
|---------------|------------|------------------|
| minimal | 10+ checks | ✅ All pass |
| cli-app | 10+ checks | ✅ All pass |
| api-service | 10+ checks | ✅ All pass |
| ml-project | 10+ checks | ✅ All pass |
| full-featured | 10+ checks | ✅ All pass (skipped in fast mode) |

## Scheduled Validation

### Overview

Automated weekly testing runs every Monday at 9:00 AM UTC to catch regressions and dependency issues early.

### Workflow: `scheduled-validation.yml`

**Schedule:** `cron: '0 9 * * 1'` (Every Monday 9 AM UTC)

**Jobs:**
1. **comprehensive-validation** - Full test matrix (4 Python versions × 5 configs)
2. **dependency-audit** - Security scanning with Safety and pip-audit
3. **test-latest-tools** - Compatibility with latest tool versions
4. **notify-results** - Create/update GitHub issues on failure

### Matrix Coverage

```
Python Versions: 3.10, 3.11, 3.12, 3.13
Configurations: minimal, cli-app, api-service, ml-project, full-featured
Total Combinations: 20
```

### Notification System

**On Failure:**
1. Creates GitHub issue titled "🚨 Weekly Template Validation Failed"
2. Issue includes:
   - Failed job details
   - Workflow run link
   - Recommended actions
   - Auto-labels: `scheduled-validation`, `automated`, `bug`

**On Success:**
1. Comments on open validation issue
2. Automatically closes the issue
3. Updates step summary with success status

**Issue Management:**
- Only ONE issue created per validation failure
- Subsequent failures update existing issue
- Issue auto-closes when validation passes
- View all validation issues: [Issues → Label: scheduled-validation](../../issues?q=label%3Ascheduled-validation)

### Manual Triggering

**Via GitHub UI:**
1. Navigate to: Actions → Scheduled Template Validation
2. Click: "Run workflow"
3. Select branch (usually `main`)
4. Click: "Run workflow"

**Via GitHub CLI:**
```bash
gh workflow run scheduled-validation.yml
```

### Customizing Schedule

Edit `.github/workflows/scheduled-validation.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Change this line
```

**Common Schedules:**
```yaml
# Daily at 9 AM UTC
- cron: '0 9 * * *'

# Twice weekly (Monday & Thursday)
- cron: '0 9 * * 1,4'

# Monthly (1st of month)
- cron: '0 9 1 * *'

# Every 6 hours
- cron: '0 */6 * * *'
```

## Python 3.10 Support

### Why Python 3.10?

Python 3.10 is tested explicitly because:
1. Common source of compatibility issues
2. Still widely used in production environments
3. Type hint syntax differences (e.g., `X | Y` vs `Union[X, Y]`)
4. Structural pattern matching not available
5. Some modern syntax features not supported

### Testing Python 3.10

**Locally:**
```bash
# Using pyenv
pyenv shell 3.10
uv run pytest tests/test_zero_issues.py -v

# Using Docker
docker run -v $(pwd):/app python:3.10 sh -c "cd /app && uv run pytest -v"
```

**In CI:**
Both `test-template.yml` and `scheduled-validation.yml` test Python 3.10 automatically.

### Common Python 3.10 Issues

**Issue:** Type hints using `|` operator
```python
# ❌ Python 3.10 incompatible
def foo(x: str | int) -> str | None:
    pass

# ✅ Python 3.10 compatible
from typing import Union, Optional

def foo(x: Union[str, int]) -> Optional[str]:
    pass
```

**Issue:** Match statements
```python
# ❌ Python 3.10 incompatible (< 3.10)
match value:
    case 1:
        print("one")

# ✅ Use if/elif
if value == 1:
    print("one")
```

## Integration with CI/CD

### Relationship Between Workflows

```
┌─────────────────────────────────────┐
│   test-template.yml                 │
│   (On every PR/push)                │
│   - Hook tests                      │
│   - Generation tests                │
│   - Integration tests               │
│   - Quality tool tests              │
│   - Zero-issues tests               │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   scheduled-validation.yml          │
│   (Weekly Monday 9 AM UTC)          │
│   - Full matrix (20 combinations)   │
│   - Dependency audit                │
│   - Latest tools test               │
│   - Automatic issue creation        │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   GitHub Issues                     │
│   - Failure notifications           │
│   - Automated tracking              │
│   - Auto-close on success           │
└─────────────────────────────────────┘
```

### Quality Gates

**Pre-Merge (Required):**
- ✅ `test-template.yml` must pass
- ✅ All zero-issues tests must pass
- ✅ All configurations must generate successfully
- ✅ No CI/CD check failures

**Post-Merge (Monitoring):**
- 📊 Weekly validation provides safety net
- 🐛 Catches dependency regressions
- 🔄 Validates against latest tool versions
- 📬 Notifications keep team informed

## Troubleshooting

### Scheduled Validation Failures

**Symptom:** Weekly validation creates issue

**Steps:**
1. Click workflow run link in issue
2. Identify failed job(s)
3. Review test output for specific failures
4. Run locally: `uv run pytest tests/test_zero_issues.py -v`
5. Fix issues and push to main
6. Wait for next scheduled run (or trigger manually)

**Common Causes:**
- Dependency updates with breaking changes
- External tool updates (Black, Ruff, etc.)
- Template changes that broke generated projects
- Python version incompatibilities

### Zero-Issues Test Failures

**Symptom:** `test_zero_issues.py` fails locally

**Debug:**
```bash
# Run with verbose output
uv run pytest tests/test_zero_issues.py -v -s

# Run specific failing test
uv run pytest tests/test_zero_issues.py::TestFormattingAndLinting::test_black_formatting -vv

# Keep generated project for inspection
uv run pytest tests/test_zero_issues.py -k "minimal" --keep-failed
```

**Fix Pattern:**
1. Generate test project manually
2. Run failing check on generated project
3. Identify template file causing issue
4. Fix template file
5. Regenerate and verify
6. Commit fix

### Notification Issues

**Symptom:** Not receiving GitHub issue notifications

**Solutions:**
1. Check GitHub notification settings: Settings → Notifications
2. Ensure "Issues" is enabled for the repository
3. Check email spam folder
4. Add webhook for Slack/Discord (see below)

**Adding Slack Webhook:**
```yaml
# In scheduled-validation.yml, add to notify-results job:
- name: Notify Slack
  if: steps.status.outputs.status == 'failed'
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "🚨 Weekly Template Validation Failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Weekly validation failed. <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Best Practices

### Before Committing Template Changes

1. ✅ Run zero-issues tests: `uv run pytest tests/test_zero_issues.py -v`
2. ✅ Validate with script: `./scripts/validate-generated-project.sh`
3. ✅ Test critical configurations manually
4. ✅ Check pre-commit hooks pass
5. ✅ Review diff for hardcoded values

### Monitoring Scheduled Validation

1. 📅 Check GitHub Issues every Monday afternoon
2. 🔔 Enable GitHub notifications for the repository
3. 📊 Review workflow runs monthly for patterns
4. 🔄 Update dependencies proactively before they break

### Handling Breaking Changes

**When external tools release breaking changes:**

1. **Detect:** Scheduled validation fails
2. **Investigate:** Review release notes of updated tools
3. **Test:** Run locally with updated tool versions
4. **Fix:** Update template files to accommodate changes
5. **Document:** Add notes to CHANGELOG.md
6. **Verify:** Run full test suite before merging

## Quick Reference

### Test Commands

```bash
# Zero-issues validation
uv run pytest tests/test_zero_issues.py -v

# Specific test class
uv run pytest tests/test_zero_issues.py::TestFormattingAndLinting -v

# All configurations (slow)
uv run pytest tests/test_zero_issues.py::TestAllConfigsCombined -v

# Specific configuration
uv run pytest tests/test_zero_issues.py -k "cli-app" -v

# Manual validation script
./scripts/validate-generated-project.sh /path/to/generated/project

# Feature combination test
./scripts/test-feature-combination.sh --config api-service --keep
```

### Workflow Management

```bash
# Trigger scheduled validation manually
gh workflow run scheduled-validation.yml

# List recent validation runs
gh run list --workflow=scheduled-validation.yml --limit 10

# View specific run
gh run view <run-id>

# List validation issues
gh issue list --label scheduled-validation
```

### Monitoring URLs

- **Scheduled Workflow Runs:** `https://github.com/<org>/<repo>/actions/workflows/scheduled-validation.yml`
- **Validation Issues:** `https://github.com/<org>/<repo>/issues?q=label%3Ascheduled-validation`
- **Latest Run Summary:** Click any run → Summary tab

---

**Related Files:**
- `tests/test_zero_issues.py` - Zero-issues test suite
- `.github/workflows/scheduled-validation.yml` - Scheduled validation workflow
- `.github/workflows/test-template.yml` - PR/push testing workflow
- `scripts/validate-generated-project.sh` - Validation script

**See Also:**
- [TESTING.md](TESTING.md) - Main testing documentation
- [tmp_cleanup/.tmp-template-testing-strategy-20251124.md](../tmp_cleanup/.tmp-template-testing-strategy-20251124.md) - Detailed strategy
