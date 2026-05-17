"""Unit tests for the rewrite_links function (no full build needed)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "site"))

from build import rewrite_links, REPO_URL  # noqa: E402


def test_external_link_unchanged():
    out = rewrite_links('<a href="https://example.com">x</a>')
    assert 'href="https://example.com"' in out


def test_md_to_html_rewrite():
    out = rewrite_links('<a href="foo.md">x</a>')
    assert 'href="foo.html"' in out


def test_readme_md_to_index_html():
    out = rewrite_links('<a href="README.md">x</a>')
    assert 'href="index.html"' in out


def test_subdir_readme_to_index():
    out = rewrite_links('<a href="advisories/README.md">x</a>')
    assert 'href="advisories/index.html"' in out


def test_anchor_preserved():
    out = rewrite_links('<a href="foo.md#section">x</a>')
    assert 'href="foo.html#section"' in out


def test_mailto_unchanged():
    out = rewrite_links('<a href="mailto:a@b.c">x</a>')
    assert 'href="mailto:a@b.c"' in out


def test_anchor_only_unchanged():
    out = rewrite_links('<a href="#top">x</a>')
    assert 'href="#top"' in out


def test_source_to_output_map_overrides_default():
    """When a path is in the src_map, use the mapped output (handles case
    sensitivity and READMEs)."""
    src_map = {Path("ALERTS.md"): Path("alerts.html")}
    out = rewrite_links(
        '<a href="ALERTS.md">x</a>',
        current_relpath=Path("README.md"),
        source_to_output=src_map,
    )
    assert 'href="alerts.html"' in out


def test_repo_only_path_becomes_github_blob_url():
    """A link to .github/ or .claude/ — files not built into the site —
    should become a GitHub blob URL."""
    src_map = {}
    out = rewrite_links(
        '<a href=".github/workflows/deploy-site.yml">x</a>',
        current_relpath=Path("README.md"),
        source_to_output=src_map,
    )
    assert f"{REPO_URL}/blob/main/.github/workflows/deploy-site.yml" in out
    assert 'rel="noopener"' in out


def test_repo_only_path_via_parent_dir():
    src_map = {}
    out = rewrite_links(
        '<a href="../.github/ISSUE_TEMPLATE/new-advisory.yml">x</a>',
        current_relpath=Path("advisories/some-advisory.md"),
        source_to_output=src_map,
    )
    assert f"{REPO_URL}/blob/main/.github/ISSUE_TEMPLATE/new-advisory.yml" in out
