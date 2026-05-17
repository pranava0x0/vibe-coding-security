"""Per-page .md mirror correctness (Mintlify/Anthropic pattern)."""

from __future__ import annotations

import re
from pathlib import Path


def test_index_md_matches_readme(dist_dir: Path, repo_root: Path):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    index_md = (dist_dir / "index.md").read_text(encoding="utf-8")
    assert index_md == readme, "dist/index.md should be the raw README.md"


def test_advisory_md_mirror_matches_source(dist_dir: Path, advisory_files):
    for src in advisory_files:
        mirror = dist_dir / "advisories" / src.name.replace(".md", ".md")
        # Same name as source under advisories/
        mirror = dist_dir / "advisories" / src.name
        assert mirror.exists(), f"missing mirror for advisory {src.name}"
        assert mirror.read_text(encoding="utf-8") == src.read_text(encoding="utf-8"), (
            f"mirror for {src.name} doesn't match source"
        )


def test_playbook_md_mirrors_exist(dist_dir: Path, repo_root: Path):
    for src in (repo_root / "playbooks").glob("*.md"):
        if src.name == "README.md":
            mirror_name = "index.md"
        else:
            mirror_name = src.name
        mirror = dist_dir / "playbooks" / mirror_name
        assert mirror.exists(), f"missing mirror for playbook {src.name}"


def test_prevention_md_mirrors_exist(dist_dir: Path, repo_root: Path):
    for src in (repo_root / "prevention").glob("*.md"):
        if src.name == "README.md":
            mirror_name = "index.md"
        else:
            mirror_name = src.name
        mirror = dist_dir / "prevention" / mirror_name
        assert mirror.exists(), f"missing mirror for prevention doc {src.name}"


def test_md_mirror_has_frontmatter_intact(dist_dir: Path, advisory_files):
    """The mirror should preserve YAML frontmatter exactly."""
    for src in advisory_files:
        mirror = dist_dir / "advisories" / src.name
        text = mirror.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{src.name}: mirror missing frontmatter"


def test_md_alternate_url_in_html_actually_resolves(dist_dir: Path):
    """The 'View raw markdown' link in each page must point to a real .md."""
    for html in dist_dir.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        # The page-action link is rel="alternate"
        m = re.search(r'<a href="([^"]+)" class="page-action" rel="alternate"', text)
        assert m, f"{html.relative_to(dist_dir)}: missing 'View raw markdown' action"
        md_href = m.group(1)
        target = (html.parent / md_href).resolve()
        assert target.exists(), (
            f"{html.relative_to(dist_dir)}: View-raw href {md_href!r} doesn't resolve"
        )
