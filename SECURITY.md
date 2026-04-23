# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately through one of these channels:

1. **GitHub Security Advisories**: Use the "Report a vulnerability" button on the
   [Security tab](https://github.com/ByronWilliamsCPA/cookiecutter-python-template/security)
   of this repository.
2. **Email**: Send details to the repository owner via the email listed on the
   [GitHub profile](https://github.com/ByronWilliamsCPA).

Include the following in your report:

- Description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept code if applicable)
- Affected versions
- Any suggested remediation

## Response Timeline

| Step | Target |
|------|--------|
| Initial acknowledgment | Within 72 hours |
| Severity assessment | Within 7 days |
| Fix or mitigation | Within 30 days for high/critical |
| Public disclosure | After fix is released |

## Scope

This repository is a Cookiecutter template. The security policy covers:

- The template generation hooks (`hooks/`)
- The GitHub Actions workflows (`.github/workflows/`)
- The generated project templates (`{{cookiecutter.project_slug}}/`)

Vulnerabilities in generated project configurations (for example, insecure defaults
in generated `pyproject.toml` or workflow files) are in scope.

## Security Measures in This Template

Generated projects include the following security tooling by default:

- `bandit` for static analysis of Python code
- `pip-audit` for dependency vulnerability scanning
- `detect-secrets` for secret scanning
- SHA-pinned GitHub Actions to prevent supply chain attacks
- Semgrep rules for security-focused static analysis
- OSV Scanner for open-source vulnerability detection

## Known Vulnerabilities

See [docs/known-vulnerabilities.md](docs/known-vulnerabilities.md) for any
currently tracked, unfixed CVEs with remediation timelines.
