"""Accuracy guard: CVE / GHSA identifiers in advisories must be well-formed.

Automated sweeps have shipped malformed/placeholder IDs that read as real but
aren't — e.g. `GHSA-langgraph-27794` (real GHSA IDs are GHSA-xxxx-xxxx-xxxx),
`GHSA-XXXX` placeholders, and yearless `CVE-44789` shorthand. A malformed ID is
almost always a fabricated or half-remembered one. This lint makes that class a
deterministic build failure instead of a citation a reader has to catch.

It does NOT verify the ID actually exists (that needs the network) — only that
the *format* is valid. Pair it with `tools/check-external-links.py` (liveness +
Wayback) when authoring, per the sweep skill's accuracy checklist.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ADVISORIES = sorted((Path(__file__).resolve().parent.parent / "advisories").glob("*.md"))

# A token that *looks like an attempt* at an ID: "CVE-" / "GHSA-" followed by a digit.
# This deliberately ignores English prose like "CVE-based" or product names like
# "CVE-Detector" (CVE- followed by a letter), which are not ID attempts.
CVE_ATTEMPT = re.compile(r"\bCVE-\d[\w-]*")
GHSA_ATTEMPT = re.compile(r"\bGHSA-[\w-]*")

CVE_VALID = re.compile(r"^CVE-\d{4}-\d{4,}$")
GHSA_VALID = re.compile(r"^GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}$", re.IGNORECASE)


@pytest.mark.parametrize("path", ADVISORIES, ids=lambda p: p.name)
def test_cve_ids_well_formed(path: Path):
    text = path.read_text(encoding="utf-8")
    bad = sorted({m.group(0) for m in CVE_ATTEMPT.finditer(text) if not CVE_VALID.match(m.group(0))})
    assert not bad, (
        f"{path.name}: malformed CVE id(s) {bad} — expected CVE-YYYY-NNNN (>=4-digit "
        f"sequence). Use the full canonical id; don't abbreviate or fabricate."
    )


@pytest.mark.parametrize("path", ADVISORIES, ids=lambda p: p.name)
def test_ghsa_ids_well_formed(path: Path):
    text = path.read_text(encoding="utf-8")
    bad = sorted({m.group(0) for m in GHSA_ATTEMPT.finditer(text) if not GHSA_VALID.match(m.group(0))})
    assert not bad, (
        f"{path.name}: malformed GHSA id(s) {bad} — expected GHSA-xxxx-xxxx-xxxx "
        f"(4-4-4 base32). A malformed GHSA id is almost always fabricated; look up the real one."
    )
