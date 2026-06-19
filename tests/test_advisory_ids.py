"""Accuracy guard: CVE / GHSA identifiers in advisories must be well-formed.

Automated sweeps have shipped malformed/placeholder/abbreviated IDs that read as
real but aren't — e.g. `GHSA-langgraph-27794` (real GHSA IDs are
GHSA-xxxx-xxxx-xxxx), `GHSA-XXXX` placeholders, yearless `CVE-44789` shorthand,
and slash-compressed lists like `CVE-2026-44789/44790/44791` where only the first
id is canonical (the rest are yearless and invisible to search / the LLM
mirrors). A malformed or compressed ID is almost always fabricated or
half-remembered. This lint makes that class a deterministic build failure.

It does NOT verify the ID actually exists (that needs the network) — only that
the *format* is canonical. Pair it with `tools/check-external-links.py`
(liveness + Wayback) when authoring, per the sweep skill's accuracy checklist.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ADVISORIES = sorted((Path(__file__).resolve().parent.parent / "advisories").glob("*.md"))

# A token that *looks like an attempt* at an id: "CVE-" / "GHSA-" followed by a digit.
# This deliberately ignores English prose like "CVE-based" or product names like
# "CVE-Detector" (CVE- followed by a letter), which are not id attempts.
CVE_ATTEMPT = re.compile(r"\bCVE-\d[\w-]*")
GHSA_ATTEMPT = re.compile(r"\bGHSA-[\w-]*")

CVE_VALID = re.compile(r"^CVE-\d{4}-\d{4,}$")
GHSA_VALID = re.compile(r"^GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}$", re.IGNORECASE)

# Slash-compressed CVE lists: a valid id followed by one or more "/NN+" groups,
# e.g. CVE-2026-44789/44790/44791 or CVE-2026-3059/3060. The CVE_ATTEMPT regex
# stops at the first "/", so the trailing yearless sequences slip past the
# per-token check — this catches them directly. (A trailing URL path like
# ".../CVE-2026-1234/details" has letters after the slash and is NOT matched.)
CVE_COMPRESSED = re.compile(r"\bCVE-\d{4}-\d{4,}(?:/\d{2,})+")


def find_bad_cves(text: str) -> list[str]:
    bad = {m.group(0) for m in CVE_ATTEMPT.finditer(text) if not CVE_VALID.match(m.group(0))}
    bad |= {m.group(0) for m in CVE_COMPRESSED.finditer(text)}
    return sorted(bad)


def find_bad_ghsas(text: str) -> list[str]:
    return sorted({m.group(0) for m in GHSA_ATTEMPT.finditer(text) if not GHSA_VALID.match(m.group(0))})


@pytest.mark.parametrize("path", ADVISORIES, ids=lambda p: p.name)
def test_cve_ids_well_formed(path: Path):
    bad = find_bad_cves(path.read_text(encoding="utf-8"))
    assert not bad, (
        f"{path.name}: malformed/abbreviated CVE id(s) {bad} — write each canonical "
        f"CVE-YYYY-NNNN in full (no yearless shorthand, no slash-compressed lists)."
    )


@pytest.mark.parametrize("path", ADVISORIES, ids=lambda p: p.name)
def test_ghsa_ids_well_formed(path: Path):
    bad = find_bad_ghsas(path.read_text(encoding="utf-8"))
    assert not bad, (
        f"{path.name}: malformed GHSA id(s) {bad} — expected GHSA-xxxx-xxxx-xxxx "
        f"(4-4-4 base32). A malformed GHSA id is almost always fabricated; look up the real one."
    )


# --- Adversarial self-tests: prove the lint catches the forms it documents ---

def test_lint_catches_known_bad_forms():
    bad_samples = {
        "CVE-44789": "yearless",
        "CVE-2026-44789/44790/44791": "slash-compressed list",
        "CVE-2026-3059/3060": "two-segment compressed",
        "CVE-2026-447": "too-few sequence digits",
    }
    for sample, why in bad_samples.items():
        assert find_bad_cves(f"see {sample} here"), f"lint missed {why}: {sample}"
    assert find_bad_ghsas("see GHSA-langgraph-27794 here"), "lint missed malformed GHSA"
    assert find_bad_ghsas("see GHSA-XXXX here"), "lint missed GHSA placeholder"


def test_lint_allows_valid_forms_and_prose():
    clean = (
        "CVE-2026-44789 / CVE-2026-44790 / CVE-2026-44791 and CVE-2014-0160 "
        "fixed per GHSA-mhr3-j7m5-c7c9. This is CVE-based analysis from CVE-Detector. "
        "See https://nvd.nist.gov/vuln/detail/CVE-2026-5223 and "
        "https://github.com/advisories/GHSA-c67j-w6g6-q2cm for details."
    )
    assert find_bad_cves(clean) == [], find_bad_cves(clean)
    assert find_bad_ghsas(clean) == [], find_bad_ghsas(clean)
