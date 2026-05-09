"""Regression tests for malformed markdown fence terminators in the template tree.

A CommonMark closing fence must be exactly three backticks with no language tag.
A closing fence that carries a language tag (e.g. ``` text) opens a new nested
block instead of closing the previous one, which corrupts rendering and Claude
Code context loading.

A second class of bug: a tagged opener whose backtick count equals an inner
fence's backtick count is closed prematurely by that inner fence. The canonical
fix is to lengthen the outer fence (e.g. ```` outer with ``` inner).

Only backtick fences are scanned; tilde fences (``~~~``) are out of scope.
"""

from __future__ import annotations

import re
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "{{cookiecutter.project_slug}}"
SCAN_DIRS = [TEMPLATE_ROOT / ".claude", TEMPLATE_ROOT / "docs"]
# Matches fences with an info string of [A-Za-z0-9_+-]. Does not match exotic
# info strings (C#, text/html, {.python}); none appear in the scanned trees.
FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]+)\s*$")
PLAIN_CLOSE_RE = re.compile(r"^```\s*$")
GENERIC_FENCE_RE = re.compile(r"^(`{3,})(\S*)\s*$")
MARKDOWN_FENCE_RE = re.compile(r"^(`{3,})markdown\s*$")
# Markdown sample blocks must use at least this many backticks so inner
# 3-backtick fences cannot close them prematurely.
MIN_MARKDOWN_FENCE_BACKTICKS = 4


def _closing_fences_with_language_tag(path: Path) -> list[tuple[int, str]]:
    """Return (line_number, line_text) for closing fences that carry a language tag."""
    inside_block = False
    bad: list[tuple[int, str]] = []
    for lineno, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if PLAIN_CLOSE_RE.match(raw):
            inside_block = False
            continue
        match = FENCE_RE.match(raw)
        if not match:
            continue
        if not inside_block:
            inside_block = True
            continue
        bad.append((lineno, raw))
        inside_block = False
    return bad


def _scan_inside_block(
    lines: list[str], start: int, outer_len: int
) -> tuple[int, bool]:
    """Walk lines from `start` until the proper close of an opener with `outer_len` backticks.

    Returns (next_index, has_conflicting_inner). The proper close is the first
    plain fence with length >= outer_len. A conflicting-inner is a tagged child
    fence whose length is >= outer_len: it would close the outer prematurely if
    it were plain, and indicates the outer fence is too short to safely contain
    inner fenced content.
    """
    has_conflicting_inner = False
    i = start
    while i < len(lines):
        child = GENERIC_FENCE_RE.match(lines[i])
        if not child:
            i += 1
            continue
        child_len = len(child.group(1))
        child_info = child.group(2)
        if not child_info and child_len >= outer_len:
            # proper close
            return i + 1, has_conflicting_inner
        # Tagged child with length >= outer_len would force the outer to close
        # prematurely if the tag were stripped; flag the outer as fragile.
        if child_info and child_len >= outer_len:
            has_conflicting_inner = True
        i += 1
    return i, has_conflicting_inner


def _outer_fences_with_premature_close(path: Path) -> list[tuple[int, str]]:
    """Return (line_number, line_text) for fence openers with a premature close.

    The outer backtick count must exceed every inner fence inside the block.
    CommonMark closes a fenced block at the first plain fence with at least as
    many backticks as the opener, so an opener with N backticks containing a
    child fence with M backticks where M >= N is prematurely closed.

    This detector walks every fence; when it sees an opener (line with a
    language tag), it scans forward to find the proper close (a plain fence
    of length >= opener) but flags the opener if it encounters any child
    fence with length >= opener before the proper close arrives.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    bad: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        match = GENERIC_FENCE_RE.match(lines[i])
        if not match:
            i += 1
            continue
        outer_info = match.group(2)
        if not outer_info:
            # plain fence at top level: ignore (we only flag tagged openers)
            i += 1
            continue
        outer_len = len(match.group(1))
        outer_lineno = i + 1
        outer_text = lines[i]
        i, premature = _scan_inside_block(lines, i + 1, outer_len)
        if premature:
            bad.append((outer_lineno, outer_text))
    return bad


def test_no_closing_fence_has_language_tag() -> None:
    """No closing markdown fence in `.claude/` or `docs/` carries a language tag."""
    offenders: list[str] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for md_path in scan_dir.rglob("*.md"):
            for lineno, text in _closing_fences_with_language_tag(md_path):
                offenders.append(f"{md_path}:{lineno}: {text}")
    assert not offenders, "Closing fences with language tag:\n" + "\n".join(offenders)


def test_no_outer_fence_premature_close() -> None:
    """No tagged fence opener contains an inner 3-backtick fence that would close it prematurely."""
    offenders: list[str] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for md_path in scan_dir.rglob("*.md"):
            for lineno, text in _outer_fences_with_premature_close(md_path):
                offenders.append(f"{md_path}:{lineno}: {text}")
    assert not offenders, (
        "Outer fence too short to contain inner fences:\n" + "\n".join(offenders)
    )


def _three_backtick_markdown_openers(path: Path) -> list[tuple[int, str]]:
    """Return (line_number, line_text) for ```markdown openers at exactly 3 backticks.

    Precautionary policy: markdown sample blocks should use 4+ backticks for the
    outer fence so that any inner 3-backtick fences (ASCII diagrams, tagged code,
    plain content fences) cannot prematurely close the outer block via CommonMark's
    "first plain fence with len >= opener" close rule.
    """
    bad: list[tuple[int, str]] = []
    for lineno, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        m = MARKDOWN_FENCE_RE.match(raw)
        if m and len(m.group(1)) < MIN_MARKDOWN_FENCE_BACKTICKS:
            bad.append((lineno, raw))
    return bad


def test_markdown_fence_uses_four_backticks() -> None:
    """Markdown sample blocks must use 4+ backticks to safely contain inner fences."""
    offenders: list[str] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for md_path in scan_dir.rglob("*.md"):
            for lineno, text in _three_backtick_markdown_openers(md_path):
                offenders.append(f"{md_path}:{lineno}: {text}")
    assert not offenders, (
        "```markdown openers must use 4+ backticks (precautionary; prevents "
        "premature close by inner 3-backtick fences):\n" + "\n".join(offenders)
    )
