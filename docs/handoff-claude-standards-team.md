# Handoff: Claude Standards Repository Updates

**Date**: 2025-11-29
**From**: Cookiecutter Python Template
**To**: Global Claude Standards Team (williaby/.claude)
**Priority**: Medium

---

## Executive Summary

This document outlines proposed additions and updates to the `williaby/.claude` repository to improve standards coverage across all projects using the Claude configuration subtree.

---

## 1. New Standard: FIPS 140-2/140-3 Compliance

### Background

Many enterprise deployments run on FIPS-enabled systems (Ubuntu LTS with `fips-updates`, government systems, healthcare/HIPAA, financial services). Code that works in development may fail in production due to FIPS restrictions on cryptographic algorithms.

### Proposed File

**Location**: `standards/fips-compliance.md`

**Content should cover**:

#### Prohibited Algorithms (will fail in FIPS mode)
- MD5, MD4, SHA-1 (for security purposes)
- DES, 3DES, RC2, RC4, Blowfish, IDEA, CAST5
- Non-approved key exchange methods

#### Approved Algorithms
- AES (128, 192, 256-bit)
- SHA-256, SHA-384, SHA-512
- RSA (2048-bit minimum)
- ECDSA (P-256, P-384, P-521)
- HMAC with approved hash functions

#### Python Code Patterns

```python
# ✗ WRONG - Will fail on FIPS systems
import hashlib
h = hashlib.md5(data)

# ✓ CORRECT - Non-security use is allowed
h = hashlib.md5(data, usedforsecurity=False)

# ✓ CORRECT - Use FIPS-approved algorithms for security
h = hashlib.sha256(data)
```

#### Problematic Packages

| Package | Issue | Alternative |
|---------|-------|-------------|
| `pycrypto` | Deprecated, not FIPS-compliant | `pycryptodome` with FIPS mode |
| `bcrypt` | bcrypt is not FIPS-approved | `passlib` with PBKDF2, or `argon2-cffi` |
| `m2crypto` | May use non-FIPS OpenSSL | Verify FIPS module active |
| `paramiko` | Depends on crypto backend | Ensure FIPS-compliant backend |

#### Packages Requiring Verification

| Package | Notes |
|---------|-------|
| `cryptography` | Require version >= 3.4.6 with OpenSSL FIPS provider |
| `requests`/`urllib3` | Ensure TLS 1.2+ with FIPS cipher suites |
| `boto3` | Use FIPS endpoints for AWS GovCloud |
| `pyjwt` | Use RS256/ES256 (not HS256 with weak keys) |

#### Verification Script Reference

Projects should include a FIPS compatibility check script. Reference implementation available in cookiecutter-python-template.

---

## 2. Enhancement: Ruff Pylint Complexity Limits

### Background

The current `standards/linting.md` covers Ruff basics but doesn't specify complexity limits that align with maintainability best practices.

### Proposed Addition to `standards/linting.md`

Add a section on complexity configuration:

```toml
# pyproject.toml additions

[tool.ruff.lint.mccabe]
max-complexity = 10  # Cyclomatic complexity limit

[tool.ruff.lint.pylint]
max-statements = 100   # Function length hard limit
max-branches = 12      # Nesting/branching limit
max-nested-blocks = 4  # Explicit nesting limit
max-returns = 6        # Return statement limit
```

**Rationale**:
- `max-complexity = 10` aligns with Google/Pylint standards
- `max-statements = 100` prevents overly long functions
- `max-branches = 12` limits decision tree complexity
- `max-nested-blocks = 4` prevents deeply nested code
- `max-returns = 6` encourages single-exit-point patterns

---

## 3. New Standard: Copy-Paste Detection (CPD)

### Background

Duplicated code increases maintenance burden and bug surface area. CPD should be a standard quality check.

### Proposed Addition

Either add to `standards/linting.md` or create `standards/code-quality.md`:

#### Qlty Configuration

```toml
# .qlty/qlty.toml
[[plugin]]
name = "cpd"
# Copy-Paste Detector for identifying duplicated code
```

#### Guidelines

- **Threshold**: Default 100 tokens (approximately 6-10 lines)
- **Action**: Refactor duplicated code into shared functions/modules
- **Exceptions**: Test fixtures, boilerplate (with documented reason)

---

## 4. Enhancement: Testing Standards

### Background

The current `standards/python.md` has a brief testing section. Consider creating a dedicated `standards/testing.md` with comprehensive patterns.

### Proposed Content for `standards/testing.md`

#### Test Organization
```
tests/
├── unit/           # Fast, isolated tests (<1s each)
├── integration/    # Service integration tests
├── e2e/            # End-to-end scenarios
└── conftest.py     # Shared fixtures
```

#### Coverage Requirements
- Minimum: 80% line coverage
- Branch coverage: Enabled
- Critical paths: 100%

#### Test Patterns

**AAA Pattern (Arrange-Act-Assert)**:
```python
def test_user_creation():
    # Arrange
    user_data = {"name": "Test", "email": "test@example.com"}

    # Act
    user = User.create(user_data)

    # Assert
    assert user.name == "Test"
```

**Factory Fixtures**:
```python
@pytest.fixture
def user_factory():
    def create_user(**kwargs):
        defaults = {"name": "Test", "email": "test@example.com"}
        return User(**{**defaults, **kwargs})
    return create_user
```

**Parametrized Tests**:
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

**Property-Based Testing**:
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_encode_decode_roundtrip(text):
    assert decode(encode(text)) == text
```

---

## 5. Structure Recommendation

### Current Structure (from API inspection)
```
williaby/.claude/
├── standards/
│   ├── git-workflow.md
│   ├── git-worktree.md
│   ├── linting.md
│   ├── python.md
│   └── security.md
├── agents/
├── commands/
├── skills/
└── ...
```

### Proposed Additions
```
williaby/.claude/
├── standards/
│   ├── git-workflow.md      # Existing
│   ├── git-worktree.md      # Existing
│   ├── linting.md           # Existing (enhance with complexity limits)
│   ├── python.md            # Existing
│   ├── security.md          # Existing
│   ├── fips-compliance.md   # NEW
│   ├── testing.md           # NEW
│   └── code-quality.md      # NEW (CPD, metrics, maintainability)
```

---

## 6. Implementation Notes

### For Template Integration

Once changes are made to `williaby/.claude`, projects using the subtree can update via:

```bash
git subtree pull --prefix .claude/standard \
    https://github.com/williaby/.claude.git main --squash
```

Or using the helper script:
```bash
./scripts/update-claude-standards.sh
```

### Backwards Compatibility

All additions are new files or additive sections to existing files. No breaking changes expected.

### Testing Recommendation

Before merging:
1. Create a test project using the subtree
2. Verify all standards files load correctly
3. Test that Claude Code recognizes and uses the standards

---

## 7. Questions for Standards Team

1. **FIPS Standard Scope**: Should FIPS compliance be a separate file or integrated into `security.md`?

2. **Testing Standard**: Is a dedicated `testing.md` preferred, or should testing patterns be expanded in `python.md`?

3. **Code Quality Metrics**: Should CPD and complexity metrics be in `linting.md` or a new `code-quality.md`?

4. **Language Coverage**: Should standards cover non-Python languages (TypeScript, Go, Rust) in separate files or combined?

---

## Contact

For questions about this handoff or the cookiecutter-python-template integration:
- Repository: `ByronWilliamsCPA/cookiecutter-python-template`
- Related PR: (link to PR when created)

---

*Generated from cookiecutter-python-template standards review*
