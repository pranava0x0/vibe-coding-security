"""llms.txt / llms-full.txt / llms-ctx.txt format + completeness."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "site"))
import build as _build  # type: ignore  # noqa: E402


# ─── llms.txt size budget policy ────────────────────────────────────────────
# These caps are a CONTRACT, not a high-water mark. They are not to be raised to
# make a failing build pass. That loop ran nine times between 2026-05-30 and
# 2026-08-05, with the interval collapsing from ~3 weeks to ~2 days. Broadened
# age-trimming (2026-07-14/17/29) lowered the slope but left it positive; by
# 2026-08-05 all three files were back at 94-97% of cap, and the very next
# sweep (2026-08-06) breached llms.txt outright.
#
# The outputs are now two-tier and count-bounded (site/build.py, 2026-08-06):
# the N most recent advisories plus all active/ongoing ones appear in full,
# everything older is a one-line pointer. Size is therefore O(1) in corpus
# size, not O(n) — see LLMS_TXT_TIER1 / LLMS_CTX_TIER1 / LLMS_FULL_TIER1 in
# site/build.py. Note the active/ongoing set itself has no upper bound (58 of
# 176 advisories as of 2026-08-06) and is usually the dominant term in Tier 1;
# if these caps start failing again, check whether the active/ongoing count
# has grown before assuming the N-most-recent knob needs to shrink further.
#
# If a cap is breached, the correct fixes, in order:
#   1. Lower the Tier-1 "N most recent" count in site/build.py. That is the
#      intended control surface.
#   2. Tighten per-advisory truncation limits (also in site/build.py).
#   3. Triage stale `status: active`/`ongoing` advisories back to
#      patched/historical — every one of them is a mandatory Tier-1 entry
#      regardless of age, so a growing active count inflates all three files.
#   4. Only then, and only with a written rationale here, raise a cap.
#
# HEADROOM_FRACTION makes the test fail while there is still room to think. A
# build at 85% of budget is a warning; the previous regime only reported
# failure at 100%, one advisory too late.
LLMS_TXT_MAX_BYTES = 80 * 1024
LLMS_CTX_MAX_BYTES = 152 * 1024
LLMS_FULL_MAX_BYTES = 1152 * 1024
HEADROOM_FRACTION = 0.15  # must stay under 85% of cap


def test_llms_txt_starts_with_title(llms_txt):
    assert llms_txt.startswith("# "), "llms.txt must start with '# Title'"


def test_llms_txt_has_summary_blockquote(llms_txt):
    """Per llmstxt.org spec, the summary should be on a '> ' line near the top."""
    head = "\n".join(llms_txt.splitlines()[:5])
    assert "\n> " in head, "llms.txt missing '> summary' line near top"


def test_llms_txt_has_required_sections(llms_txt):
    for section in ["## Active alerts", "## Advisories", "## Playbooks", "## Prevention", "## Optional"]:
        assert section in llms_txt, f"llms.txt missing section: {section}"


@pytest.mark.parametrize("name,cap", [
    ("llms.txt", LLMS_TXT_MAX_BYTES),
    ("llms-ctx.txt", LLMS_CTX_MAX_BYTES),
    ("llms-full.txt", LLMS_FULL_MAX_BYTES),
])
def test_llms_output_within_budget(dist_dir, name, cap):
    size = (dist_dir / name).stat().st_size
    budget = int(cap * (1 - HEADROOM_FRACTION))
    assert size <= budget, (
        f"{name} is {size:,} B — over the {budget:,} B budget ({size/cap:.0%} of the "
        f"{cap:,} B cap). Lower the Tier-1 count; do not raise the cap. "
        f"See the budget policy at the top of this file."
    )


def test_llms_outputs_are_count_bounded():
    """Tier-1 counts are what bound these files. If this fails, someone removed
    the bound and the caps became load-bearing again."""
    assert _build.LLMS_TXT_TIER1 <= 60
    assert _build.LLMS_CTX_TIER1 <= 40
    assert _build.LLMS_FULL_TIER1 <= 60


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
