"""Pytest fixtures for the vibe-coding-security test suite.

Triggers a full site build once per session, then exposes:
  - repo_root: Path to repo root
  - dist_dir:  Path to dist/ (build output)
  - advisory_files: list of advisory markdown paths
  - all_md_files: every authored markdown file in the repo
  - all_html_files: every built HTML file
  - parsed_advisories: list of (path, frontmatter dict, body)
  - sitemap_root: parsed sitemap.xml ElementTree root
  - llms_txt: contents of dist/llms.txt
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DIST = REPO_ROOT / "dist"
ADVISORIES = REPO_ROOT / "advisories"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def dist_dir(repo_root: Path) -> Path:
    """Run the build once per test session. Subsequent tests reuse dist/."""
    # Always rebuild to ensure tests reflect current source
    result = subprocess.run(
        [sys.executable, "site/build.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"build.py failed:\n{result.stdout}\n{result.stderr}"
    assert DIST.exists(), "dist/ not created"
    return DIST


@pytest.fixture(scope="session")
def advisory_files(repo_root: Path) -> list[Path]:
    return sorted(
        p for p in (repo_root / "advisories").glob("*.md") if p.name != "README.md"
    )


@pytest.fixture(scope="session")
def all_md_files(repo_root: Path) -> list[Path]:
    """Every markdown source file we author (excludes dist/, .claude/, .git/)."""
    return sorted(
        p for p in repo_root.rglob("*.md")
        if not any(part.startswith((".git", ".claude")) or part == "dist" or part == "node_modules"
                   for part in p.parts)
    )


@pytest.fixture(scope="session")
def all_html_files(dist_dir: Path) -> list[Path]:
    return sorted(dist_dir.rglob("*.html"))


@pytest.fixture(scope="session")
def parsed_advisories(advisory_files: list[Path]) -> list[tuple[Path, dict, str]]:
    out = []
    for p in advisory_files:
        fm, body = _parse_frontmatter(p.read_text(encoding="utf-8"))
        out.append((p, fm, body))
    return out


@pytest.fixture(scope="session")
def sitemap_root(dist_dir: Path):
    return ET.parse(dist_dir / "sitemap.xml").getroot()


@pytest.fixture(scope="session")
def atom_feed_root(dist_dir: Path):
    return ET.parse(dist_dir / "feed.xml").getroot()


@pytest.fixture(scope="session")
def llms_txt(dist_dir: Path) -> str:
    return (dist_dir / "llms.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def llms_full_txt(dist_dir: Path) -> str:
    return (dist_dir / "llms-full.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def llms_ctx_txt(dist_dir: Path) -> str:
    return (dist_dir / "llms-ctx.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def advisories_json(dist_dir: Path) -> dict:
    return json.loads((dist_dir / "advisories.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def advisory_schema(dist_dir: Path) -> dict:
    return json.loads((dist_dir / "advisory-schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def search_json(dist_dir: Path) -> dict:
    return json.loads((dist_dir / "search.json").read_text(encoding="utf-8"))
