"""Every advisory must have valid, complete frontmatter."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest


REQUIRED = {"id", "title", "severity", "status", "date_disclosed", "last_updated"}
SEVERITIES = {"critical", "high", "medium", "low"}
STATUSES = {"active", "contained", "patched", "mitigated", "ongoing", "historical"}
DATE_OR_PARTIAL = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
DATE_FULL = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def test_every_advisory_has_required_keys(parsed_advisories):
    for path, fm, _ in parsed_advisories:
        missing = REQUIRED - set(fm.keys())
        assert not missing, f"{path.name}: missing required frontmatter keys: {sorted(missing)}"


def test_severity_is_valid_enum(parsed_advisories):
    for path, fm, _ in parsed_advisories:
        assert str(fm["severity"]) in SEVERITIES, (
            f"{path.name}: severity={fm['severity']!r} not in {sorted(SEVERITIES)}"
        )


def test_status_is_valid_enum(parsed_advisories):
    for path, fm, _ in parsed_advisories:
        assert str(fm["status"]) in STATUSES, (
            f"{path.name}: status={fm['status']!r} not in {sorted(STATUSES)}"
        )


def test_date_disclosed_format(parsed_advisories):
    for path, fm, _ in parsed_advisories:
        v = str(fm["date_disclosed"])
        assert DATE_OR_PARTIAL.match(v), f"{path.name}: date_disclosed={v!r} not YYYY[-MM[-DD]]"


def test_last_updated_is_full_date(parsed_advisories):
    for path, fm, _ in parsed_advisories:
        v = str(fm["last_updated"])
        assert DATE_FULL.match(v), f"{path.name}: last_updated={v!r} must be YYYY-MM-DD"


def test_last_updated_not_in_future(parsed_advisories):
    today = date.today()
    for path, fm, _ in parsed_advisories:
        # parse just YYYY-MM-DD
        y, m, d = (int(x) for x in str(fm["last_updated"]).split("-"))
        when = date(y, m, d)
        assert when <= today, f"{path.name}: last_updated={when} is in the future (today={today})"


def test_advisory_id_matches_filename(parsed_advisories):
    """The frontmatter id should equal the filename stem."""
    for path, fm, _ in parsed_advisories:
        assert str(fm["id"]) == path.stem, (
            f"{path.name}: id={fm['id']!r} doesn't match filename stem {path.stem!r}"
        )


def test_advisory_ids_are_unique(parsed_advisories):
    ids = [str(fm["id"]) for _, fm, _ in parsed_advisories]
    duplicates = {x for x in ids if ids.count(x) > 1}
    assert not duplicates, f"Duplicate advisory ids: {sorted(duplicates)}"


def test_id_pattern_matches_schema(parsed_advisories, advisory_schema):
    pattern = advisory_schema["properties"]["id"]["pattern"]
    compiled = re.compile(pattern)
    for path, fm, _ in parsed_advisories:
        assert compiled.match(str(fm["id"])), (
            f"{path.name}: id={fm['id']!r} doesn't match schema pattern {pattern!r}"
        )


def test_ecosystems_are_lowercase_strings(parsed_advisories):
    for path, fm, _ in parsed_advisories:
        for eco in fm.get("ecosystems", []) or []:
            assert isinstance(eco, str), f"{path.name}: ecosystem must be string: {eco!r}"
            assert eco == eco.lower(), f"{path.name}: ecosystem must be lowercase: {eco!r}"


def test_advisory_has_tldr_section(parsed_advisories):
    """Every advisory should open with a ## TL;DR section."""
    for path, _, body in parsed_advisories:
        assert re.search(r"^##\s+TL;DR", body, re.MULTILINE), (
            f"{path.name}: missing '## TL;DR' section"
        )


def test_advisory_has_sources_section(parsed_advisories):
    """Every advisory should end with a ## Sources section linking out."""
    for path, _, body in parsed_advisories:
        assert re.search(r"^##\s+Sources?\s*$", body, re.MULTILINE), (
            f"{path.name}: missing '## Sources' section"
        )
        # Must have at least one https:// link in sources area
        sources_match = re.search(
            r"^##\s+Sources?\s*$(.*)", body, re.MULTILINE | re.DOTALL
        )
        sources_text = sources_match.group(1) if sources_match else ""
        assert "https://" in sources_text, (
            f"{path.name}: Sources section has no https:// links"
        )
