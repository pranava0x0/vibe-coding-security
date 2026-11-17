"""Prose gate: AI-slop patterns, and plain style on new advisories.

The pattern list is tools/slop_patterns.tsv. It grows: when review finds a
slop sentence the scanner missed, add a pattern there and fix the corpus.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import slop_scan  # noqa: E402

# Style rules (no em-dash, no semicolon-joined clauses, sentences of at most
# slop_scan.MAX_WORDS words, an inline link in the TL;DR) apply to advisories
# disclosed on or after this date. Older files predate the rule.
STYLE_CUTOFF = date(2026, 11, 17)


def _disclosed(fm) -> date | None:
    raw = fm.get("date_disclosed")
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    parts = [int(x) for x in str(raw)[:10].split("-")] + [1, 1]
    return date(parts[0], parts[1], parts[2])


def test_no_slop_patterns_in_corpus(repo_root):
    patterns = slop_scan.load_patterns()
    files = sorted((repo_root / "advisories").glob("*.md")) + [repo_root / "ALERTS.md"]
    hits = []
    for f in files:
        p_hits, _ = slop_scan.scan_text(f.read_text(encoding="utf-8"), patterns)
        hits += [f"{f.name}:{no}: [{name}] '{m}' -> {fix}" for no, name, m, fix in p_hits]
    assert not hits, "AI-slop phrasing (tools/slop_patterns.tsv):\n" + "\n".join(hits[:20])


def test_new_advisories_use_plain_style(parsed_advisories):
    bad = []
    for path, fm, body in parsed_advisories:
        d = _disclosed(fm)
        if d is None or d < STYLE_CUTOFF:
            continue
        _, s_hits = slop_scan.scan_text(path.read_text(encoding="utf-8"))
        bad += [f"{path.name}:{no}: {name} -> {fix}" for no, name, fix in s_hits]
        tldr = re.search(r"^## TL;DR\n(.*?)(?=^## |\Z)", body, re.S | re.M)
        if tldr and not re.search(r"\]\(https?://", tldr.group(1)):
            bad.append(f"{path.name}: TL;DR has no inline citation; link the primary source in the sentence it supports")
    assert not bad, "\n".join(bad[:20])


def test_scanner_catches_known_slop_and_skips_quotes():
    sample = (
        "---\ntitle: x\n---\n"
        "The reports draw on each other, and Report URI sells monitoring, which its post promotes.\n"
        "It is worth noting that this underscores the need for care.\n"
        'The vendor said it is "a robust, seamless fix".\n'
        "The fix is in `robust-lib` 2.0.\n"
    )
    p_hits, _ = slop_scan.scan_text(sample)
    names = {name for _, name, _, _ in p_hits}
    assert {"source-interdependence", "source-motive", "worth-noting", "filler-verbs"} <= names
    assert all(no in (4, 5) for no, *_ in p_hits), p_hits


def test_scanner_skips_blockquotes_and_joins_soft_breaks():
    p_hits, _ = slop_scan.scan_text("> A robust fix is now available.\n>\n> [@a on X](https://x.com/a/status/1)\n")
    assert not p_hits
    p_hits, s_hits = slop_scan.scan_text("It is worth\nnoting this.\n\n" + " ".join(["w"] * 20) + "\n" + " ".join(["w"] * 20) + ".\n")
    assert any(name == "worth-noting" for _, name, _, _ in p_hits)
    assert any(name.startswith("long-sentence") for _, name, _ in s_hits)


def test_scanner_flags_style_on_long_sentences():
    long = " ".join(["word"] * (slop_scan.MAX_WORDS + 1)) + "."
    _, s_hits = slop_scan.scan_text(f"A short one. {long}\nX — Y.\n")
    kinds = {name.split(" ")[0] for _, name, _ in s_hits}
    assert {"long-sentence", "em-dash"} <= kinds


# ALERTS.md entries dated on or after STYLE_CUTOFF: short, and cited inline.
ALERT_MAX_WORDS = 50
ALERT_MAX_SENTENCES = 3
_ALERT = re.compile(r"^### (\d{4}-\d{2}-\d{2}) [^\n]*\n(.*?)(?=^### |^## |\Z)", re.S | re.M)


def _alert_entries(text: str):
    for m in _ALERT.finditer(text):
        body = "\n".join(l for l in m.group(2).strip().splitlines() if not l.startswith("→"))
        yield date.fromisoformat(m.group(1)), body


def test_new_alerts_are_short_and_cited(repo_root):
    bad = []
    for d, body in _alert_entries((repo_root / "ALERTS.md").read_text(encoding="utf-8")):
        if d < STYLE_CUTOFF:
            continue
        plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)
        words = len(plain.split())
        sentences = len([s for s in slop_scan._SENTENCE.split(plain.strip()) if s])
        if words > ALERT_MAX_WORDS or sentences > ALERT_MAX_SENTENCES:
            bad.append(f"{d}: {words} words, {sentences} sentences (max {ALERT_MAX_WORDS}, {ALERT_MAX_SENTENCES})")
        if not re.search(r"\]\(https?://", body):
            bad.append(f"{d}: no inline link to the primary source")
    assert not bad, "ALERTS.md entries:\n" + "\n".join(bad[:20])
