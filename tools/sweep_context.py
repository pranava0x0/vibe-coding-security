#!/usr/bin/env python3
"""Generate the compact state files a sweep reads at Step 0.

Why this exists
---------------
Step 0 of the `vibe-security-update` skill used to require reading `ALERTS.md`
(~68K tokens), `advisories/README.md` (~10K), and the full
`source-priorities.json` (~26K) on every run — ~104K tokens of prose to answer
two questions the sweep actually asks:

  1. "Is this incident already tracked?"  → a set-membership lookup
  2. "Which sources are worth prepending to a query?" → the top ~25 by weight

Reading two human-facing documents to answer a set-membership question is the
wrong data structure. This script emits two small machine-readable files
instead, cutting that ~104K down to ~7K:

  - advisory-index.json      one compact row per advisory (id, dates, status,
                             severity, ecosystems, tools, tags, and every
                             CVE/GHSA id found anywhere in the body)
  - source-priorities.top.json  the top-N sources by weight, nothing else

Both are regenerated from source on every run, so they cannot drift. They are
committed so a diff shows what a sweep changed.

Usage:
    python3 tools/sweep_context.py           # write both files
    python3 tools/sweep_context.py --check   # exit 1 if either is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
ADVISORIES_DIR = REPO_ROOT / "advisories"
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "vibe-security-update"
SOURCE_PRIORITIES = SKILL_DIR / "source-priorities.json"

ADVISORY_INDEX_OUT = SKILL_DIR / "advisory-index.jsonl"
SOURCE_TOP_OUT = SKILL_DIR / "source-priorities.top.json"

# How many sources the query-building step actually uses. Step 1 prepends the
# "top 10 by weight" to queries and rotates subsets; 25 leaves room to rotate
# without loading all ~4,900 lines of the full file.
TOP_SOURCES_N = 25

# Title is only here so a human can eyeball a diff — the sweep matches on ids,
# aliases, and CVE/GHSA numbers, not on prose. Truncated to keep the file small.
TITLE_MAX = 120

CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b")
GHSA_RE = re.compile(r"\bGHSA-[23456789cfghjmpqrvwx]{4}-[23456789cfghjmpqrvwx]{4}-[23456789cfghjmpqrvwx]{4}\b")

# Inline code spans in an advisory body are where package, product, and campaign
# names live (`chalk-tempalte`, `proc-macro1`, `@scope/pkg`). Without them the
# index answers "not tracked" for a name that is only in the prose — and Step 2
# treats a miss as proof a finding is new, so that becomes a duplicate advisory.
# This is the fast path only: it cannot catch a name that never appears in
# backticks (e.g. "SiYuan"), which is why Step 2 also requires a corpus grep
# before concluding anything is new.
CODE_SPAN_RE = re.compile(r"`([^`\n]{2,60})`")
# Identifier-shaped only: no whitespace, and not a shell/path/flag fragment.
NAME_RE = re.compile(r"^[A-Za-z0-9@][A-Za-z0-9._@/+-]*$")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a `---`-delimited YAML frontmatter block off the body."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}, body
    return (data if isinstance(data, dict) else {}), body


def extract_names(body: str) -> list[str]:
    """Identifier-shaped inline code spans from an advisory body.

    Package, product, and campaign names that appear nowhere in the frontmatter
    are the index's main blind spot; nearly all of them are written in
    backticks. Filtered to identifier shapes so command lines, paths with
    spaces, and prose fragments don't land in the index."""
    names = {
        span.strip()
        for span in CODE_SPAN_RE.findall(body)
        if NAME_RE.match(span.strip()) and not span.strip().startswith((".", "/", "-"))
    }
    return sorted(names)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def build_advisory_index() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(ADVISORIES_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        title = str(fm.get("title") or path.stem)
        rows.append(
            {
                # `file` is deliberately absent — it is always advisories/<id>.md.
                "id": str(fm.get("id") or path.stem),
                "title": title[:TITLE_MAX],
                "date_disclosed": str(fm.get("date_disclosed") or ""),
                "last_updated": str(fm.get("last_updated") or fm.get("date_disclosed") or ""),
                "severity": str(fm.get("severity") or ""),
                "status": str(fm.get("status") or ""),
                "ecosystems": _as_list(fm.get("ecosystems")),
                "tools": _as_list(fm.get("tools_affected")),
                "tags": _as_list(fm.get("tags")),
                # Every vuln id mentioned anywhere in the file. This is the
                # field that answers "already tracked?" for a CVE-shaped
                # candidate without reading a single advisory body.
                "cve": sorted(set(CVE_RE.findall(body))),
                "ghsa": sorted(set(GHSA_RE.findall(body))),
                # Body-only package/product/campaign names — see extract_names.
                "names": extract_names(body),
            }
        )
    # Most recently updated first — matches how a sweep scans for overlap.
    rows.sort(key=lambda r: (r["last_updated"], r["id"]), reverse=True)
    return rows


def build_top_sources() -> list[dict[str, Any]]:
    if not SOURCE_PRIORITIES.exists():
        return []
    data = json.loads(SOURCE_PRIORITIES.read_text(encoding="utf-8"))
    sources = data.get("sources", data) if isinstance(data, dict) else data
    if isinstance(sources, dict):
        items = [{"domain": k, **(v if isinstance(v, dict) else {"weight": v})} for k, v in sources.items()]
    else:
        items = list(sources)

    def weight(entry: dict[str, Any]) -> float:
        for key in ("weight", "score", "priority", "hits"):
            if isinstance(entry.get(key), (int, float)):
                return float(entry[key])
        return 0.0

    items.sort(key=lambda e: (-weight(e), str(e.get("domain", ""))))
    # `ecosystems` is deliberately dropped — it is most of the 105KB in the
    # full file and the query-building step never reads it.
    return [
        {
            "domain": e.get("domain", ""),
            "weight": weight(e),
            "hits": e.get("hits", 0),
            "last_hit": str(e.get("last_hit") or ""),
        }
        for e in items[:TOP_SOURCES_N]
        if e.get("domain")
    ]


def render() -> dict[Path, str]:
    index = build_advisory_index()
    top = build_top_sources()
    # JSONL, one advisory per line: this file is meant to be *grepped*, not
    # read. A sweep never loads it into context — it runs one grep per
    # candidate incident ("is this CVE / package / campaign already tracked?")
    # and only the matching lines cost anything. That is why completeness
    # matters here more than byte count.
    index_text = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in index
    )
    return {
        ADVISORY_INDEX_OUT: index_text,
        SOURCE_TOP_OUT: json.dumps(
            {"count": len(top), "note": f"top {TOP_SOURCES_N} by weight; regenerate with tools/sweep_context.py",
             "sources": top},
            indent=1,
            ensure_ascii=False,
        )
        + "\n",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 1 if any output is stale")
    args = ap.parse_args()

    outputs = render()
    stale = [p for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]

    if args.check:
        for path in stale:
            print(f"stale: {path.relative_to(REPO_ROOT)} — run `python3 tools/sweep_context.py`", file=sys.stderr)
        return 1 if stale else 0

    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        size = len(text.encode("utf-8"))
        print(f"  + {path.relative_to(REPO_ROOT)} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
