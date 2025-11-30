#!/usr/bin/env python3
"""Cruft Manager - Automated template update orchestration.

This script manages cruft-based template updates across multiple repositories,
creating PRs when template updates are available.

SPDX-FileCopyrightText: 2025 Byron Williams
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cruft-manager")


@dataclass
class Repository:
    """Represents a repository managed by cruft."""

    name: str
    template: str
    github: str
    local_path: str | None = None
    auto_update: bool = True
    branch_prefix: str = "cruft/template-update"


@dataclass
class UpdateResult:
    """Result of a cruft update operation."""

    repo: Repository
    success: bool
    needs_update: bool = False
    old_commit: str | None = None
    new_commit: str | None = None
    pr_url: str | None = None
    error: str | None = None
    changes: list[str] = field(default_factory=list)


class CruftManager:
    """Manages cruft updates across multiple repositories."""

    def __init__(self, registry_path: str | Path) -> None:
        """Initialize the manager with a registry file."""
        self.registry_path = Path(registry_path)
        self.config = self._load_registry()
        self.templates = self.config.get("templates", {})
        self.settings = self.config.get("settings", {})
        self.repositories = self._parse_repositories()

    def _load_registry(self) -> dict[str, Any]:
        """Load the cruft registry YAML file."""
        if not self.registry_path.exists():
            msg = f"Registry file not found: {self.registry_path}"
            raise FileNotFoundError(msg)

        with self.registry_path.open() as f:
            return yaml.safe_load(f)

    def _parse_repositories(self) -> list[Repository]:
        """Parse repository configurations from the registry."""
        repos = []
        for name, config in self.config.get("repositories", {}).items():
            repos.append(
                Repository(
                    name=name,
                    template=config.get("template", ""),
                    github=config.get("github", ""),
                    local_path=config.get("local_path"),
                    auto_update=config.get("auto_update", True),
                    branch_prefix=config.get(
                        "branch_prefix",
                        self.settings.get("branch_prefix", "cruft/template-update"),
                    ),
                )
            )
        return repos

    def _run_command(
        self, cmd: list[str], cwd: str | Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        """Run a shell command and return the result."""
        logger.debug(f"Running: {' '.join(cmd)}")
        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def _clone_repo(self, repo: Repository, target_dir: Path) -> bool:
        """Clone a repository to a target directory."""
        url = f"https://github.com/{repo.github}.git"
        result = self._run_command(["git", "clone", "--depth=1", url, str(target_dir)])
        return result.returncode == 0

    def _get_cruft_info(self, repo_path: Path) -> dict[str, Any] | None:
        """Read .cruft.json from a repository."""
        cruft_file = repo_path / ".cruft.json"
        if not cruft_file.exists():
            return None
        with cruft_file.open() as f:
            return json.load(f)

    def check_for_updates(self, repo: Repository, repo_path: Path) -> UpdateResult:
        """Check if a repository needs cruft updates."""
        result = UpdateResult(repo=repo, success=True, needs_update=False)

        # Get current cruft info
        cruft_info = self._get_cruft_info(repo_path)
        if not cruft_info:
            result.success = False
            result.error = "No .cruft.json found - not a cruft-managed repo"
            return result

        result.old_commit = cruft_info.get("commit", "unknown")

        # Run cruft check
        check_result = self._run_command(["cruft", "check"], cwd=repo_path)

        if check_result.returncode != 0:
            # Non-zero exit means updates are available
            result.needs_update = True
            logger.info(f"Updates available for {repo.name}")

            # Get diff to see what changed
            diff_result = self._run_command(["cruft", "diff"], cwd=repo_path)
            if diff_result.stdout:
                result.changes = diff_result.stdout.split("\n")[:50]  # Limit lines

        return result

    def apply_update(self, repo: Repository, repo_path: Path) -> UpdateResult:
        """Apply cruft update to a repository."""
        result = self.check_for_updates(repo, repo_path)

        if not result.needs_update:
            logger.info(f"No updates needed for {repo.name}")
            return result

        if not repo.auto_update:
            logger.info(f"Auto-update disabled for {repo.name}, skipping")
            return result

        # Create update branch
        branch_name = f"{repo.branch_prefix}-{datetime.now().strftime('%Y%m%d')}"

        # Checkout new branch
        self._run_command(["git", "checkout", "-b", branch_name], cwd=repo_path)

        # Apply cruft update
        update_result = self._run_command(
            ["cruft", "update", "--skip-apply-ask", "-y"],
            cwd=repo_path,
        )

        if update_result.returncode != 0:
            result.success = False
            result.error = f"Cruft update failed: {update_result.stderr}"
            return result

        # Get new commit info
        new_cruft_info = self._get_cruft_info(repo_path)
        if new_cruft_info:
            result.new_commit = new_cruft_info.get("commit", "unknown")

        # Check if there are changes to commit
        status_result = self._run_command(["git", "status", "--porcelain"], cwd=repo_path)

        if not status_result.stdout.strip():
            logger.info(f"No changes after update for {repo.name}")
            result.needs_update = False
            return result

        # Commit changes
        self._run_command(["git", "add", "-A"], cwd=repo_path)

        commit_msg = f"""chore(deps): update from cookiecutter template

Template commit: {result.old_commit[:8] if result.old_commit else 'unknown'} → {result.new_commit[:8] if result.new_commit else 'unknown'}

🤖 Generated with cruft-manager
"""
        self._run_command(["git", "commit", "-m", commit_msg], cwd=repo_path)

        # Push branch
        push_result = self._run_command(
            ["git", "push", "-u", "origin", branch_name],
            cwd=repo_path,
        )

        if push_result.returncode != 0:
            result.success = False
            result.error = f"Failed to push branch: {push_result.stderr}"
            return result

        # Create PR using gh CLI
        pr_body = self.settings.get("pr_body_template", "Template update").format(
            template_name=repo.template,
            old_commit=result.old_commit or "unknown",
            new_commit=result.new_commit or "unknown",
            changes="\n".join(result.changes[:20]) if result.changes else "See diff",
        )

        pr_result = self._run_command(
            [
                "gh",
                "pr",
                "create",
                "--title",
                self.settings.get("pr_title_template", "chore: template update"),
                "--body",
                pr_body,
                "--base",
                "main",
            ],
            cwd=repo_path,
        )

        if pr_result.returncode == 0:
            result.pr_url = pr_result.stdout.strip()
            logger.info(f"Created PR for {repo.name}: {result.pr_url}")
        else:
            result.error = f"Failed to create PR: {pr_result.stderr}"

        return result

    def scan_github_for_repos(self, template_url: str) -> list[str]:
        """Scan GitHub for repos using a specific template.

        Uses GitHub search to find repos with .cruft.json pointing to the template.
        """
        # This is a simplified version - in practice you might use GitHub API
        logger.info(f"Scanning GitHub for repos using template: {template_url}")

        # Use gh CLI to search
        result = self._run_command(
            [
                "gh",
                "search",
                "code",
                f"cookiecutter-python-template in:file filename:.cruft.json",
                "--json",
                "repository",
                "--limit",
                "100",
            ]
        )

        if result.returncode != 0:
            logger.warning(f"GitHub search failed: {result.stderr}")
            return []

        try:
            results = json.loads(result.stdout)
            return list({r["repository"]["nameWithOwner"] for r in results})
        except (json.JSONDecodeError, KeyError):
            return []

    def run_updates(self, dry_run: bool = False) -> list[UpdateResult]:
        """Run updates for all registered repositories."""
        results = []

        for repo in self.repositories:
            logger.info(f"Processing {repo.name} ({repo.github})")

            with tempfile.TemporaryDirectory() as tmp_dir:
                repo_path = Path(tmp_dir) / repo.name

                # Use local path if available, otherwise clone
                if repo.local_path and Path(repo.local_path).exists():
                    # Work on a copy to avoid modifying the original
                    import shutil

                    shutil.copytree(repo.local_path, repo_path)
                else:
                    if not self._clone_repo(repo, repo_path):
                        results.append(
                            UpdateResult(
                                repo=repo,
                                success=False,
                                error="Failed to clone repository",
                            )
                        )
                        continue

                if dry_run:
                    result = self.check_for_updates(repo, repo_path)
                    logger.info(
                        f"[DRY RUN] {repo.name}: "
                        f"{'needs update' if result.needs_update else 'up to date'}"
                    )
                else:
                    result = self.apply_update(repo, repo_path)

                results.append(result)

        return results

    def generate_report(self, results: list[UpdateResult]) -> str:
        """Generate a summary report of update results."""
        lines = [
            "# Cruft Update Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Total repositories: {len(results)}",
            f"- Updates available: {sum(1 for r in results if r.needs_update)}",
            f"- Successful updates: {sum(1 for r in results if r.success and r.pr_url)}",
            f"- Errors: {sum(1 for r in results if not r.success)}",
            "",
            "## Details",
        ]

        for result in results:
            status = "✅" if result.success else "❌"
            update_status = "📦 needs update" if result.needs_update else "✓ up to date"

            lines.append(f"\n### {result.repo.name} {status}")
            lines.append(f"- Status: {update_status}")

            if result.pr_url:
                lines.append(f"- PR: {result.pr_url}")

            if result.error:
                lines.append(f"- Error: {result.error}")

            if result.old_commit and result.new_commit:
                lines.append(
                    f"- Commits: `{result.old_commit[:8]}` → `{result.new_commit[:8]}`"
                )

        return "\n".join(lines)


def main() -> None:
    """Main entry point for cruft-manager."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage cruft template updates across repositories"
    )
    parser.add_argument(
        "--registry",
        "-r",
        default="cruft_registry.yaml",
        help="Path to registry file",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Check for updates without applying them",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan GitHub for repos using the template",
    )
    parser.add_argument(
        "--report",
        "-o",
        help="Output report to file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Find registry file
    registry_path = Path(args.registry)
    if not registry_path.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent
        registry_path = script_dir / args.registry

    manager = CruftManager(registry_path)

    if args.scan:
        # Scan mode - find repos using the template
        for template_name, template_config in manager.templates.items():
            repos = manager.scan_github_for_repos(template_config["url"])
            logger.info(f"Found {len(repos)} repos using {template_name}:")
            for repo in repos:
                logger.info(f"  - {repo}")
    else:
        # Update mode
        results = manager.run_updates(dry_run=args.dry_run)
        report = manager.generate_report(results)

        if args.report:
            with open(args.report, "w") as f:
                f.write(report)
            logger.info(f"Report written to {args.report}")
        else:
            print(report)


if __name__ == "__main__":
    main()
