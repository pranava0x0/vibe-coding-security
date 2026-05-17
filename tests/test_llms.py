"""llms.txt / llms-full.txt / llms-ctx.txt format + completeness."""

from __future__ import annotations

import re
from pathlib import Path


# Mintlify recommendation
LLMS_FULL_MAX_BYTES = 200 * 1024  # ~200KB, well within token limits
LLMS_CTX_MAX_BYTES = 50 * 1024
LLMS_TXT_MAX_BYTES = 50 * 1024


def test_llms_txt_starts_with_title(llms_txt):
    assert llms_txt.startswith("# "), "llms.txt must start with '# Title'"


def test_llms_txt_has_summary_blockquote(llms_txt):
    """Per llmstxt.org spec, the summary should be on a '> ' line near the top."""
    head = "\n".join(llms_txt.splitlines()[:5])
    assert "\n> " in head, "llms.txt missing '> summary' line near top"


def test_llms_txt_has_required_sections(llms_txt):
    for section in ["## Active alerts", "## Advisories", "## Playbooks", "## Prevention", "## Optional"]:
        assert section in llms_txt, f"llms.txt missing section: {section}"


def test_llms_txt_size_reasonable(dist_dir):
    size = (dist_dir / "llms.txt").stat().st_size
    assert size < LLMS_TXT_MAX_BYTES, f"llms.txt is {size} bytes — too large for an index"


def test_llms_full_txt_size_reasonable(dist_dir):
    size = (dist_dir / "llms-full.txt").stat().st_size
    assert size < LLMS_FULL_MAX_BYTES, (
        f"llms-full.txt is {size} bytes — exceeds Mintlify recommended {LLMS_FULL_MAX_BYTES}"
    )


def test_llms_ctx_txt_size_reasonable(dist_dir):
    size = (dist_dir / "llms-ctx.txt").stat().st_size
    assert size < LLMS_CTX_MAX_BYTES, (
        f"llms-ctx.txt is {size} bytes — should be compact (~10-20KB)"
    )


def test_llms_full_contains_every_advisory(parsed_advisories, llms_full_txt):
    """Every advisory's body should be in llms-full.txt."""
    missing = []
    for path, fm, body in parsed_advisories:
        # Title from frontmatter is a stable signal
        title = str(fm.get("title", "")).strip()
        if title and title not in llms_full_txt:
            missing.append(path.name)
    assert not missing, f"Advisories missing from llms-full.txt: {missing}"


def test_llms_ctx_contains_every_advisory(parsed_advisories, llms_ctx_txt):
    missing = []
    for path, fm, _ in parsed_advisories:
        title = str(fm.get("title", "")).strip()
        if title and title not in llms_ctx_txt:
            missing.append(path.name)
    assert not missing, f"Advisories missing from llms-ctx.txt: {missing}"


def test_llms_txt_lists_every_advisory(parsed_advisories, llms_txt):
    missing = []
    for path, fm, _ in parsed_advisories:
        title = str(fm.get("title", "")).strip()
        if title and title not in llms_txt:
            missing.append(path.name)
    assert not missing, f"Advisories missing from llms.txt: {missing}"


def test_per_section_llms_txt_exist(dist_dir):
    for section in ["advisories", "playbooks", "prevention", "sources", "tools"]:
        p = dist_dir / section / "llms.txt"
        assert p.exists(), f"{section}/llms.txt missing"
        text = p.read_text(encoding="utf-8")
        assert text.startswith("# "), f"{section}/llms.txt must start with '# Title'"


def test_llms_full_links_to_md_mirrors(llms_full_txt):
    """llms-full.txt should reference per-page .md URLs in its content (canonical comments)."""
    # canonical: URL comments should appear
    assert "canonical:" in llms_full_txt, "llms-full.txt should include canonical: comments per advisory"


def test_llms_txt_optional_section_links_to_alternates(llms_txt):
    """Spec: 'Optional' section should point to expanded files."""
    optional_idx = llms_txt.find("## Optional")
    assert optional_idx >= 0
    tail = llms_txt[optional_idx:]
    for url_suffix in ["llms-full.txt", "llms-ctx.txt", "advisory-schema.json"]:
        assert url_suffix in tail, f"Optional section missing reference to {url_suffix}"
