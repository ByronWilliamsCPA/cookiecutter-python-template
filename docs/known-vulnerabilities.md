# Known Vulnerabilities

This document tracks CVEs and security advisories that have been identified but cannot
be immediately remediated. Entries must be reviewed within 60 days of the Discovered
date. Any entry older than 60 days without reassessment blocks releases per the OpenSSF
release gate policy.

For the template, see [known-vulnerabilities-template.md](known-vulnerabilities-template.md).

## Active Entries

## PYSEC-2022-42969 | py | Medium

| Field | Value |
|-------|-------|
| **CVE ID** | PYSEC-2022-42969 |
| **Package** | py |
| **Affected Version** | 1.11.0 |
| **Fixed Version** | No fix available |
| **Severity** | Medium |
| **CVSS Score** | 7.5 |
| **Discovered** | 2026-04-24 |
| **Reassessment Due** | 2026-06-23 |
| **Blocking Release** | No |

### Description

ReDoS (Regular Expression Denial of Service) vulnerability in the `py` package's
`path.LocalPath` function via crafted input to the `svnwc.status` method.

### Impact on This Project

The `py` package is a transitive dependency of `pytest` and `pre-commit` in the CI
testing environment only. It is never present in production or in generated project
dependencies. The vulnerable `svnwc.status` code path is not exercised in any test
or template generation context in this repository.

### Remediation Plan

- [ ] Monitor upstream `py` package for a fix release (package is largely unmaintained)
- [ ] Evaluate removing the direct `pytest` dependency from the CI pip install step
  in favour of `uv run pytest` which pins versions in the lock file (Byron Williams,
  due 2026-06-23)

### Why Not Fixed Yet

The `py` package has no released fix version. The package is largely unmaintained and
the `pytest` team migrated away from it in pytest 7+, but `py` is still a transitive
install dependency on some platforms. No upgrade path is available.

### References

- [PYSEC-2022-42969](https://osv.dev/vulnerability/PYSEC-2022-42969)
- [GitHub Advisory GHSA-w596-4wvx-j9j6](https://github.com/advisories/GHSA-w596-4wvx-j9j6)

## Resolved Entries

| CVE | Package | Resolved Date | Resolution |
|-----|---------|---------------|------------|

## Review History

| Review Date | Reviewer | Notes |
|-------------|----------|-------|
| 2026-04-12 | Byron Williams | Initial creation; no known CVEs. |
