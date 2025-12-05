# Cookiecutter Template Supply Chain Security Handoff

> **Last Updated:** 2025-12-04  
> **Status:** Ready for Implementation

## Overview

This document provides everything needed to implement supply chain security in the ByronWilliamsCPA Python cookiecutter template. Projects generated from this template will:

1. **Consume third-party packages** from Google Assured OSS (SLSA Level 3)
2. **Consume internal packages** from `python-libs` (GCP Artifact Registry)
3. **Fall back to PyPI** for packages not in Assured OSS
4. **Manage secrets** via Infisical (not GitHub Secrets)
5. **Generate SBOMs** with attestation

### Infrastructure Status ✅

| Component | Status | Details |
|-----------|--------|---------|
| Google Assured OSS | ✅ Ready | GCP Project: `assured-oss-457903` |
| python-libs Registry | ✅ Ready | `us-central1-python.pkg.dev/assured-oss-457903/python-libs` |
| Infisical | ✅ Ready | https://infisical.williamshome.family |
| Service Account | ✅ Ready | `assured-oss-accessor@assured-oss-457903.iam.gserviceaccount.com` |

---

## Part 1: pyproject.toml Configuration

### 1.1 UV Index Configuration

Add this to the template's `pyproject.toml`:

```toml
# =============================================================================
# SUPPLY CHAIN SECURITY - Package Index Configuration
# =============================================================================
# Priority order:
#   1. Assured OSS (Google-verified, SLSA Level 3) - third-party packages
#   2. Internal (python-libs) - internal shared packages
#   3. PyPI (fallback) - packages not in Assured OSS
#
# Documentation: https://cloud.google.com/assured-open-source-software/docs
# =============================================================================

[[tool.uv.index]]
name = "assured-oss"
url = "https://us-python.pkg.dev/cloud-aoss/cloud-aoss-python/simple"
# Google Assured OSS - curated packages with SLSA Level 3 provenance
# Includes: numpy, pandas, tensorflow, requests, flask, django, etc.
# Full list: https://cloud.google.com/assured-open-source-software/docs/supported-packages

[[tool.uv.index]]
name = "internal"
url = "https://us-central1-python.pkg.dev/assured-oss-457903/python-libs/simple"
explicit = true
# Internal packages from ByronWilliamsCPA/python-libs
# Packages: byronwilliamscpa-cloudflare-auth, byronwilliamscpa-gcs-utilities
# explicit = true means packages must be explicitly directed here via [tool.uv.sources]

[[tool.uv.index]]
name = "pypi"
url = "https://pypi.org/simple"
default = true
# PyPI fallback for packages not in Assured OSS

# =============================================================================
# Package Sources - Direct specific packages to specific indexes
# =============================================================================

[tool.uv.sources]
# Internal packages (from python-libs)
byronwilliamscpa-cloudflare-auth = { index = "internal" }
byronwilliamscpa-gcs-utilities = { index = "internal" }

# Add other internal packages as they're created:
# byronwilliamscpa-new-package = { index = "internal" }
```

### 1.2 Supply Chain Dependencies

Add an optional dependency group for supply chain tools:

```toml
[project.optional-dependencies]
# ... existing groups ...

supply-chain = [
    "cyclonedx-bom>=4.6.0",      # SBOM generation
    "pip-audit>=2.7.0",          # Vulnerability scanning
    "safety>=3.7.0",             # Additional vuln scanning
    "pip-licenses>=4.0.0",       # License compliance
    "keyrings.google-artifactregistry-auth>=1.1.0",  # GCP auth for indexes
]
```

### 1.3 Vulnerability Tracking Comments

Document known CVE fixes in dependencies:

```toml
[project]
dependencies = [
    # Security: CVE-2025-XXXX fixed in 2.9.0+
    "some-package>=2.9.0",
    
    # Security: ReDoS vulnerability fixed in 0.115.0
    "fastapi>=0.115.0",
    
    # Security: CVE-2024-7776 fixed in 1.17.0
    "onnx>=1.17.0",
]
```

---

## Part 2: Infisical Integration

### 2.1 Project Configuration File

Add `.infisical.json` to the template root:

```json
{
  "workspaceId": "",
  "defaultEnvironment": "dev",
  "gitBranchToEnvironmentMapping": {
    "main": "prod",
    "develop": "staging",
    "*": "dev"
  }
}
```

> **Note:** `workspaceId` is populated when running `infisical init` in a project.

### 2.2 GitHub Workflow Integration

Update workflow templates to fetch secrets from Infisical instead of GitHub Secrets:

```yaml
env:
  INFISICAL_DOMAIN: https://secrets.byronwilliamscpa.com

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Fetch all secrets from Infisical
      - name: Fetch secrets from Infisical
        uses: Infisical/secrets-action@v1.0.7
        with:
          client-id: ${{ secrets.INFISICAL_CLIENT_ID }}
          client-secret: ${{ secrets.INFISICAL_CLIENT_SECRET }}
          env-slug: prod  # or use github.ref mapping
          project-slug: ${{ github.event.repository.name }}
          domain: ${{ env.INFISICAL_DOMAIN }}
      
      # Secrets are now available as environment variables
      # e.g., $GCP_SA_KEY_BASE64, $MODAL_TOKEN_ID, etc.
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ env.GCP_SA_KEY_BASE64 }}
```

### 2.3 Per-Project Secrets Schema

Document expected secrets for different project types:

**Standard Python Project:**
```
GCP_SA_KEY_BASE64    # For Artifact Registry access (Assured OSS + python-libs)
```

**ML/GPU Project:**
```
GCP_SA_KEY_BASE64    # Artifact Registry access
MODAL_TOKEN_ID       # Modal.com compute
MODAL_TOKEN_SECRET   # Modal.com compute
HF_TOKEN             # Hugging Face (optional)
```

**Azure Project:**
```
GCP_SA_KEY_BASE64    # Artifact Registry access
AZURE_CLIENT_ID
AZURE_CLIENT_SECRET
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
```

---

## Part 3: GitHub Actions Workflows

### 3.1 Enhanced CI Workflow

Update the CI workflow template to use Assured OSS:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

permissions:
  contents: read
  security-events: write  # For SARIF upload

env:
  INFISICAL_DOMAIN: https://secrets.byronwilliamscpa.com

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Fetch secrets from Infisical
        uses: Infisical/secrets-action@v1.0.7
        with:
          client-id: ${{ secrets.INFISICAL_CLIENT_ID }}
          client-secret: ${{ secrets.INFISICAL_CLIENT_SECRET }}
          env-slug: prod
          project-slug: {{ cookiecutter.project_slug }}
          domain: ${{ env.INFISICAL_DOMAIN }}

      - name: Authenticate to GCP (for Artifact Registry)
        uses: google-github-actions/auth@71f986410dfbc7added4569d411d040a91dc6935 # v2.1.8
        with:
          credentials_json: ${{ env.GCP_SA_KEY_BASE64 }}

      - name: Install uv
        uses: astral-sh/setup-uv@6b9c6063abd6010835644d4c2e1bef4cf5cd0fca # v6.0.1
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install keyring for Artifact Registry
        run: pip install keyrings.google-artifactregistry-auth

      - name: Verify lockfile is up to date
        run: uv lock --check

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest --cov

      - name: Type checking
        run: uv run basedpyright

      - name: Linting
        run: uv run ruff check .
```

### 3.2 SBOM Workflow

The org-level `python-sbom.yml` already exists. Call it from project CI:

```yaml
# .github/workflows/sbom.yml
name: SBOM

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  sbom:
    uses: ByronWilliamsCPA/.github/.github/workflows/python-sbom.yml@main
    with:
      python-version: '3.12'
      severity-threshold: 'HIGH'
    secrets:
      INFISICAL_CLIENT_ID: ${{ secrets.INFISICAL_CLIENT_ID }}
      INFISICAL_CLIENT_SECRET: ${{ secrets.INFISICAL_CLIENT_SECRET }}
```

### 3.3 Dependency Review (PRs)

Add dependency review for pull requests:

```yaml
# .github/workflows/dependency-review.yml
name: Dependency Review

on:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: write

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high
          deny-licenses: GPL-3.0, AGPL-3.0
          allow-licenses: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC
```

---

## Part 4: Local Development Setup

### 4.1 Setup Script

Add `scripts/setup-supply-chain.sh` to the template:

```bash
#!/bin/bash
# Setup supply chain security for local development
set -e

echo "🔐 Setting up supply chain security..."

# Check for gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Authenticate to GCP
echo "📝 Authenticating to Google Cloud..."
gcloud auth login
gcloud auth application-default login

# Install keyring for Artifact Registry
echo "📦 Installing Artifact Registry keyring..."
pip install keyrings.google-artifactregistry-auth

# Verify access to Assured OSS
echo "✅ Verifying Assured OSS access..."
pip index versions numpy \
    --index-url https://us-python.pkg.dev/cloud-aoss/cloud-aoss-python/simple \
    2>/dev/null && echo "  Assured OSS: OK" || echo "  Assured OSS: FAILED"

# Verify access to python-libs
echo "✅ Verifying python-libs access..."
pip index versions byronwilliamscpa-gcs-utilities \
    --index-url https://us-central1-python.pkg.dev/assured-oss-457903/python-libs/simple \
    2>/dev/null && echo "  python-libs: OK" || echo "  python-libs: FAILED (may not have packages yet)"

# Install Infisical CLI (optional)
if ! command -v infisical &> /dev/null; then
    echo ""
    echo "💡 Optional: Install Infisical CLI for local secret management:"
    echo "   curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash"
    echo "   sudo apt-get install infisical"
fi

echo ""
echo "✅ Supply chain setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run 'uv sync' to install dependencies from secure indexes"
echo "  2. For secrets, use 'infisical run -- <command>' or set up .env"
```

### 4.2 Environment Template

Add `.env.example` to the template:

```bash
# .env.example
# Copy to .env and fill in values (or use Infisical CLI)

# =============================================================================
# GCP / Artifact Registry (required for package installation)
# =============================================================================
# Leave empty if using 'gcloud auth application-default login'
# GCP_SA_KEY_BASE64=

# =============================================================================
# Cloudflare Access (if using cloudflare-auth package)
# =============================================================================
CLOUDFLARE_TEAM_DOMAIN=
CLOUDFLARE_AUDIENCE_TAG=
CLOUDFLARE_ENABLED=true

# =============================================================================
# Project-specific secrets (fetch from Infisical for production values)
# =============================================================================
# MODAL_TOKEN_ID=
# MODAL_TOKEN_SECRET=
# HF_TOKEN=
```

### 4.3 UV Configuration

Add `uv.toml` to the template (optional, for user-level settings):

```toml
# uv.toml - UV configuration
# This file can override pyproject.toml settings

[pip]
# Increase timeout for slower package indexes
timeout = 60
```

---

## Part 5: Documentation Updates

### 5.1 README Section

Add this section to the template README:

```markdown
## Supply Chain Security

This project uses secure package indexes:

| Index | Purpose | Packages |
|-------|---------|----------|
| [Assured OSS](https://cloud.google.com/assured-open-source-software) | Third-party (SLSA Level 3) | numpy, pandas, requests, etc. |
| python-libs | Internal shared | cloudflare-auth, gcs-utilities |
| PyPI | Fallback | Everything else |

### Local Development Setup

```bash
# One-time setup
./scripts/setup-supply-chain.sh

# Install dependencies
uv sync
```

### Secrets Management

Secrets are managed via [Infisical](https://secrets.byronwilliamscpa.com), not GitHub Secrets.

For local development:
```bash
# Option 1: Use Infisical CLI
infisical run --env=dev -- uv run python main.py

# Option 2: Export to .env
infisical export --env=dev > .env
```
```

### 5.2 Contributing Guide Section

Add to CONTRIBUTING.md:

```markdown
## Adding Dependencies

When adding new dependencies:

1. **Check Assured OSS first**: https://cloud.google.com/assured-open-source-software/docs/supported-packages
2. **Add with version constraint**: `uv add "package>=1.0.0"`
3. **Document CVE fixes**: If a minimum version is for security, add a comment in pyproject.toml

### Using Internal Packages

To use packages from python-libs:

1. Add to `[project.dependencies]`:
   ```toml
   "byronwilliamscpa-cloudflare-auth>=0.1.0",
   ```

2. Ensure it's in `[tool.uv.sources]`:
   ```toml
   byronwilliamscpa-cloudflare-auth = { index = "internal" }
   ```

3. Run `uv lock` to update lockfile
```

---

## Part 6: New Project Setup Checklist

When creating a new project from the template, follow this checklist:

### 6.1 Infisical Setup

1. [ ] Go to https://secrets.byronwilliamscpa.com
2. [ ] Create project with same name as GitHub repo
3. [ ] Add required secrets to `prod` environment
4. [ ] Create machine identity: `github-actions-{project-name}`
5. [ ] Add Universal Auth to machine identity
6. [ ] Grant machine identity access to project (prod environment)
7. [ ] Add `INFISICAL_CLIENT_ID` and `INFISICAL_CLIENT_SECRET` to GitHub repo secrets

### 6.2 GitHub Configuration

1. [ ] Add repository secrets:
   - `INFISICAL_CLIENT_ID`
   - `INFISICAL_CLIENT_SECRET`
2. [ ] Enable GitHub Actions
3. [ ] Configure branch protection (require CI to pass)

### 6.3 Local Development

1. [ ] Run `./scripts/setup-supply-chain.sh`
2. [ ] Run `uv sync` to verify package installation
3. [ ] Run `infisical init` to connect to project

---

## Part 7: Package Index Priority Explained

```
Request for "numpy" package:
    │
    ▼
┌─────────────────────────────────┐
│ 1. Check Assured OSS            │
│    (cloud-aoss-python)          │
│                                 │
│    ✅ Found? → Install from     │
│       Assured OSS (SLSA L3)     │
│                                 │
│    ❌ Not found? → Continue     │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ 2. Check python-libs            │
│    (internal packages only)     │
│                                 │
│    ⚠️ Only checked if package   │
│       is in [tool.uv.sources]   │
│       with index = "internal"   │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ 3. Check PyPI (fallback)        │
│    (pypi.org)                   │
│                                 │
│    ✅ Found? → Install          │
│    ❌ Not found? → Error        │
└─────────────────────────────────┘
```

**Key Points:**
- Assured OSS is checked first for ALL packages
- Internal packages MUST be listed in `[tool.uv.sources]` with `index = "internal"`
- PyPI is the fallback for packages not in Assured OSS
- The `explicit = true` on internal index prevents it from being checked for all packages

---

## Quick Reference

### URLs

| Resource | URL |
|----------|-----|
| Assured OSS Index | `https://us-python.pkg.dev/cloud-aoss/cloud-aoss-python/simple` |
| python-libs Index | `https://us-central1-python.pkg.dev/assured-oss-457903/python-libs/simple` |
| Infisical | https://secrets.byronwilliamscpa.com |
| Assured OSS Package List | https://cloud.google.com/assured-open-source-software/docs/supported-packages |

### Service Account

```
assured-oss-accessor@assured-oss-457903.iam.gserviceaccount.com
```

### Internal Packages

| Package | Import Name | Description |
|---------|-------------|-------------|
| `byronwilliamscpa-cloudflare-auth` | `cloudflare_auth` | Cloudflare Access middleware |
| `byronwilliamscpa-gcs-utilities` | `gcs_utilities` | GCS client utilities |

### GitHub Secrets (Per-Repo)

| Secret | Source | Description |
|--------|--------|-------------|
| `INFISICAL_CLIENT_ID` | Infisical UI | Machine identity client ID |
| `INFISICAL_CLIENT_SECRET` | Infisical UI | Machine identity client secret |

---

## Contacts

- **Supply Chain Questions:** Byron Williams
- **Infisical Issues:** Check https://infisical.williamshome.family
- **Assured OSS Issues:** Check GCP Console for `assured-oss-457903`
- **python-libs Issues:** Check [ByronWilliamsCPA/python-libs](https://github.com/ByronWilliamsCPA/python-libs)