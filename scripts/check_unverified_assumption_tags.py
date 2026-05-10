#!/usr/bin/env python3
"""Count #CRITICAL / #ASSUME tags in hooks/ that lack a paired #VERIFY directive.

A tag is "verified" when a #VERIFY directive appears within the next N lines
(default 5) of the same file. Tags that are paired with #VERIFY are
considered fully documented per the RAD (Response-Aware Development) methodology
and do NOT count as production-risk debt.

Usage:
    python3 scripts/check_unverified_assumption_tags.py [--root hooks] [--window 5]

Exit code 0 always; the count is printed to stdout for the caller to use.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TAG_RE = re.compile(r"#(CRITICAL|ASSUME)\b")
VERIFY = "#VERIFY"


def count_unverified(root: Path, window: int) -> tuple[int, list[str]]:
    """Return (unverified_count, list of violator descriptions)."""
    unverified = 0
    violators: list[str] = []
    for path in root.rglob("*.py"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if not TAG_RE.search(line):
                continue
            # Skip docstring/prose mentions: tag must be in a comment line
            # whose first non-whitespace token is "#" (i.e. an actual code
            # comment, not narrative prose inside a docstring).
            stripped = line.lstrip()
            if not stripped.startswith("#"):
                continue
            window_lines = lines[i + 1 : i + 1 + window]
            if not any(VERIFY in w for w in window_lines):
                unverified += 1
                violators.append(f"{path}:{i + 1}: {line.strip()[:120]}")
    return unverified, violators


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="hooks", help="Root directory to scan.")
    parser.add_argument(
        "--window",
        type=int,
        default=5,
        help="Number of lines to look ahead for a #VERIFY pairing.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each unverified tag location to stderr.",
    )
    args = parser.parse_args()

    count, violators = count_unverified(Path(args.root), args.window)
    if args.verbose:
        for v in violators:
            print(v, file=sys.stderr)
    print(count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
