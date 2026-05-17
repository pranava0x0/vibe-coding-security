"""The build must succeed, produce expected outputs, and be deterministic."""

from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REQUIRED_OUTPUTS = [
    "index.html",
    "alerts.html",
    "contributing.html",
    "security.html",
    "changelog.html",
    "backlog.html",
    "issues.html",
    "advisories/index.html",
    "playbooks/index.html",
    "prevention/index.html",
    "sources/index.html",
    "tools/index.html",
    "style.css",
    ".nojekyll",
    "llms.txt",
    "llms-full.txt",
    "llms-ctx.txt",
    "advisories/llms.txt",
    "playbooks/llms.txt",
    "prevention/llms.txt",
    "sources/llms.txt",
    "tools/llms.txt",
    "feed.xml",
    "sitemap.xml",
    "robots.txt",
    "advisories.json",
    "advisory-schema.json",
    "search.json",
    "api/index.json",
    "api/v1/index.json",
    "api/v1/advisories.json",
    ".well-known/security.txt",
]


def test_all_required_outputs_exist(dist_dir: Path):
    missing = [name for name in REQUIRED_OUTPUTS if not (dist_dir / name).exists()]
    assert not missing, f"Missing build outputs: {missing}"


def test_every_html_has_a_markdown_mirror(dist_dir: Path):
    """Mintlify pattern: foo.html should have foo.md alongside it."""
    for html in dist_dir.rglob("*.html"):
        md = html.with_suffix(".md")
        assert md.exists(), f"missing markdown mirror: {md.relative_to(dist_dir)}"


def test_markdown_mirrors_are_non_empty(dist_dir: Path):
    for md in dist_dir.rglob("*.md"):
        # The CHANGELOG mirror might be small but never empty
        assert md.stat().st_size > 0, f"empty markdown mirror: {md.relative_to(dist_dir)}"


def test_build_is_deterministic(repo_root: Path, dist_dir: Path, tmp_path: Path):
    """Two consecutive builds should produce identical HTML output.

    (Files that embed today's date in unrelated places are expected to match
    because we use date.today() which is stable within a test session.)"""
    # Snapshot the first build
    snapshot = tmp_path / "snapshot"
    shutil.copytree(dist_dir, snapshot)

    # Rebuild
    result = subprocess.run(
        [sys.executable, "site/build.py"],
        cwd=repo_root, capture_output=True, text=True,
    )
    assert result.returncode == 0

    # Compare
    mismatched = []
    for path in snapshot.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(snapshot)
        other = dist_dir / rel
        if not other.exists():
            mismatched.append(str(rel))
            continue
        if not filecmp.cmp(path, other, shallow=False):
            mismatched.append(str(rel))

    assert not mismatched, f"Non-deterministic build — these files differ between runs: {mismatched[:5]}"


def test_no_dist_in_repo_after_clean_build(repo_root: Path):
    """dist/ is .gitignored — make sure it isn't accidentally tracked."""
    result = subprocess.run(
        ["git", "check-ignore", "-q", "dist/"],
        cwd=repo_root, capture_output=True,
    )
    # check-ignore returns 0 if path is ignored
    assert result.returncode == 0, "dist/ is not in .gitignore"
