<!--
SPDX-FileCopyrightText: 2025 Byron Williams <byron@byronwilliams.dev>
SPDX-License-Identifier: MIT
-->

# Cruft Manager

Automated template update orchestration for cookiecutter/cruft-managed repositories.

## Overview

This service tracks all repositories created from the `cookiecutter-python-template` and automatically creates PRs when template updates are available.

## Components

```
services/cruft-manager/
├── README.md                 # This file
├── cruft_registry.yaml       # Registry of managed repositories
├── cruft_manager.py          # Main orchestration script
├── cruft-update.yml          # GitHub Actions workflow (copy to .github/workflows/)
├── docker-compose.yml        # Docker deployment for homelab
└── Dockerfile                # Container image for scheduled runs
```

## Usage

### Manual Check (Dry Run)

```bash
# Check all repos for available updates without applying them
python cruft_manager.py --dry-run --verbose

# Generate a report
python cruft_manager.py --dry-run --report updates.md
```

### Apply Updates

```bash
# Apply updates and create PRs
python cruft_manager.py --verbose
```

### Scan for Unregistered Repos

```bash
# Find repos using the template that aren't in the registry
python cruft_manager.py --scan
```

## Registry Configuration

Edit `cruft_registry.yaml` to add or remove repositories:

```yaml
repositories:
  my_new_project:
    template: python-template
    github: "ByronWilliamsCPA/my-new-project"
    auto_update: true  # Set to false to skip auto-updates
```

## Deployment Options

### 1. GitHub Actions (Recommended)

Copy `cruft-update.yml` to `.github/workflows/` in this repository:

```bash
cp services/cruft-manager/cruft-update.yml .github/workflows/
```

The workflow runs daily at 6 AM UTC and creates PRs when updates are found.

### 2. Docker Cron Job (Homelab)

Run as a scheduled container:

```bash
cd services/cruft-manager
docker-compose up -d
```

This uses ofelia (cron scheduler for Docker) to run updates on schedule.

### 3. System Cron

Add to crontab:

```bash
# Run daily at 6 AM
0 6 * * * cd /home/byron/dev/homelab_infra/services/cruft-manager && python cruft_manager.py >> /var/log/cruft-manager.log 2>&1
```

## How It Works

1. **Registry Check**: Reads `cruft_registry.yaml` for list of managed repos
2. **Clone/Access**: Either clones repos or uses local paths if available
3. **Cruft Check**: Runs `cruft check` to detect available updates
4. **Apply Updates**: If updates available, runs `cruft update`
5. **Create PR**: Commits changes and creates a PR via GitHub CLI
6. **Report**: Generates a summary report of all actions taken

## Requirements

- Python 3.12+
- `cruft` package
- `pyyaml` package
- GitHub CLI (`gh`) configured with authentication
- Git configured with commit signing (optional)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GH_TOKEN` | GitHub token for API access | Yes (for PRs) |
| `SLACK_WEBHOOK` | Slack webhook for notifications | No |

## Troubleshooting

### "No .cruft.json found"

The repository wasn't created with cruft or the file was deleted. Re-link with:

```bash
cruft link https://github.com/ByronWilliamsCPA/cookiecutter-python-template
```

### "Failed to push branch"

Ensure the GitHub token has write access to the repository.

### "Merge conflicts"

Cruft couldn't automatically merge changes. Manual intervention required:

1. Check out the update branch
2. Run `cruft update` manually
3. Resolve conflicts
4. Push and update the PR
