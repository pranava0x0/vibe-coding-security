#!/usr/bin/env python3
"""Check finding/CVE mappings and attributed scores against saved registry data.

Offline by default. --live checks for upstream changes without writing files;
--refresh explicitly replaces snapshots, never advisory prose or severity.
Only fixed registry endpoints are fetched; reference URLs are data, not targets.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path("sources/cve-evidence")
CVE = re.compile(r"CVE-\d{4}-\d{4,}")
FINDING = re.compile(r"(?<![A-Za-z0-9])F-\d+(?![A-Za-z0-9])")
START = "<!-- cve-metrics:start -->"
END = "<!-- cve-metrics:end -->"
ENDPOINTS = {
    "cve": "https://cveawg.mitre.org/api/cve/",
    "nvd": "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=",
    "osv": "https://api.osv.dev/v1/vulns/",
}
USER_AGENT = "vibe-coding-security-evidence/1.0 (+https://github.com/pranava0x0/vibe-coding-security)"
# Space out live requests. NVD allows 5 requests per rolling 30 seconds without
# an API key and recommends about six seconds between calls; requests go out in
# cve, nvd, osv order, so this spacing keeps consecutive NVD calls six seconds apart.
REQUEST_DELAY = 2.0
_last_request = float("-inf")


def require(condition, message):
    """Raise on a failed check. Not `assert`: `python -O` strips assert
    statements, which would silently switch these checks off."""
    if not condition:
        raise ValueError(message)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("registry redirect refused; review endpoint manually")


def fetch(kind, cve):
    global _last_request
    if not CVE.fullmatch(cve):
        raise ValueError(f"invalid CVE: {cve}")
    wait = REQUEST_DELAY - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    request = urllib.request.Request(ENDPOINTS[kind] + cve, headers={
        "User-Agent": USER_AGENT, "Accept": "application/json",
    })
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            data = response.read(2_000_001)
    finally:
        _last_request = time.monotonic()
    if len(data) > 2_000_000:
        raise ValueError("registry response exceeds 2 MB")
    result = json.loads(data)
    check_identity(kind, cve, result)
    return result


def check_identity(kind, cve, record):
    if kind == "cve":
        require(record["cveMetadata"]["cveId"] == cve, "CVE identity mismatch")
        require(record["cveMetadata"]["state"] == "PUBLISHED", "CVE is not published")
    elif kind == "nvd":
        require(len(record["vulnerabilities"]) == 1, "expected one NVD record")
        require(record["vulnerabilities"][0]["cve"]["id"] == cve, "NVD identity mismatch")
    else:
        require(record["id"] == cve, "OSV identity mismatch")
        require(not record.get("withdrawn"), "OSV record withdrawn")


def semantic_record(kind, record):
    # Ignore NVD response timestamps, but retain all vulnerability fields.
    return record["vulnerabilities"] if kind == "nvd" else record


def reference_finding(record, prefix):
    refs = [r["url"] for r in record["containers"]["cna"]["references"]
            if r["url"].startswith(prefix)]
    findings = {m.group() for url in refs for m in FINDING.finditer(url[len(prefix):])}
    if len(findings) != 1:
        raise ValueError("CNA references must identify exactly one finding; review ambiguity")
    return findings.pop()


def metrics(record):
    containers = record["containers"]
    out = []
    for container in [containers["cna"], *containers.get("adp", [])]:
        provider = container["providerMetadata"]
        for metric in container.get("metrics", []):
            for key, value in metric.items():
                if key.startswith("cvssV"):
                    out.append((provider["shortName"], value["version"],
                                value["baseScore"], value["baseSeverity"],
                                value["vectorString"], provider["dateUpdated"][:10]))
    return sorted(out)


def score_block(records, prefix, checked_at):
    lines = [START, f"Registry scores checked {checked_at}. Scores belong to the named provider.", "",
             "| CVE | Finding | Provider / CVSS | Vector | Provider updated |",
             "|---|---|---|---|---|"]
    for cve, record in sorted(records.items()):
        finding = reference_finding(record, prefix)
        values = metrics(record)
        if not values:
            lines.append(f"| {cve} | {finding} | No CVSS supplied | — | — |")
        for provider, version, score, severity, vector, updated in values:
            lines.append(f"| {cve} | {finding} | {provider} / {version}: {score:.1f} {severity.title()} | `{vector}` | {updated} |")
    return "\n".join([*lines, END])


def finding_rows(text):
    """Read ID-first Markdown tables, including bold/code-formatted IDs."""
    rows = {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
        first = cells[0].strip().strip("*` ")
        if not FINDING.fullmatch(first):
            continue
        if first in rows:
            raise ValueError(f"duplicate finding row: {first}")
        if len(cells) != 4:
            raise ValueError(f"{first}: expected ID, finding, reviewed range, CVE columns")
        rows[first] = set(CVE.findall(cells[-1]))
    return rows


def version_conflicts(cve_record, osv_record):
    """Flag OSV inferred fixes that equal an explicitly inclusive affected end.

    This deliberately handles only the 'through X' description pattern. Other
    range grammars and vendor patch claims still require source review.
    """
    descriptions = " ".join(d["value"] for d in cve_record["containers"]["cna"].get("descriptions", []))
    ends = set(re.findall(r"\bthrough\s+(\d+(?:\.\d+)+)\b", descriptions))
    conflicts = set()
    for affected in osv_record.get("affected", []):
        for entry in affected.get("ranges", []):
            inferred = entry.get("database_specific", {}).get("extracted_events", [])
            for event in [*entry.get("events", []), *inferred]:
                if event.get("fixed") in ends:
                    conflicts.add(event["fixed"])
    return sorted(conflicts)


def validate_bundle(root, manifest, live=False, refresh=False):
    path = root / EVIDENCE / manifest.name
    config = json.loads(path.read_text(encoding="utf-8"))
    require(config["schema_version"] == 1, "unsupported evidence schema")
    advisory = config["advisory"]
    require(re.fullmatch(r"[a-z0-9-]+", advisory), "invalid advisory filename")
    checked = date.fromisoformat(config["checked_at"])
    require(checked <= datetime.now(timezone.utc).date(), "future evidence date")
    ids = config["cves"]
    require(ids and len(ids) == len(set(ids)), "empty or duplicate CVE list")
    prefix = config["finding_reference_prefix"]
    require(prefix.startswith("https://") and prefix.endswith("/"), "invalid reference prefix")
    records, changes = {}, []
    for cve in ids:
        require(CVE.fullmatch(cve), "invalid CVE in manifest")
        for kind in ENDPOINTS:
            snapshot = root / EVIDENCE / f"{cve}.{kind}.json"
            saved = json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.exists() else None
            if live or refresh:
                current = fetch(kind, cve)
                if saved is None or semantic_record(kind, current) != semantic_record(kind, saved):
                    changes.append(f"{cve}: {kind} changed; review mapping, impact, scores and versions")
                if refresh:
                    # Stage all responses in memory. No partial refresh on a later failure.
                    records[(cve, kind)] = current
            if not refresh:
                require(saved is not None, f"missing snapshot: {snapshot.name}")
                check_identity(kind, cve, saved)
                records[(cve, kind)] = saved
    if refresh:
        for (cve, kind), record in records.items():
            (root / EVIDENCE / f"{cve}.{kind}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        config["checked_at"] = datetime.now(timezone.utc).date().isoformat()
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    cve_records = {cve: records[(cve, "cve")] for cve in ids}
    text = (root / "advisories" / f"{advisory}.md").read_text(encoding="utf-8")
    rows = finding_rows(text)
    expected = {finding: set() for finding in rows}
    for cve, record in cve_records.items():
        finding = reference_finding(record, prefix)
        if finding not in rows:
            raise ValueError(f"{cve}: referenced {finding} has no advisory row")
        expected[finding].add(cve)
    errors = []
    declared_conflicts = config.get("version_conflicts", {})
    actual_conflicts = {cve: version_conflicts(record, records[(cve, "osv")])
                        for cve, record in cve_records.items()}
    actual_conflicts = {cve: ends for cve, ends in actual_conflicts.items() if ends}
    if declared_conflicts != actual_conflicts:
        errors.append(f"{advisory}: unreviewed/changed OSV fixed-version conflicts: {actual_conflicts}")
    if actual_conflicts and not config.get("version_conflict_note", "").strip():
        errors.append(f"{advisory}: version conflicts need a documented disposition")
    elif actual_conflicts and config["version_conflict_note"] not in text:
        errors.append(f"{advisory}: version conflict disposition missing from published advisory")
    if rows != expected:
        errors.append(f"{advisory}: CVE/finding rows disagree with CNA references: expected {expected}")
    block = score_block(cve_records, prefix, config["checked_at"])
    if text.count(START) != 1 or text.count(END) != 1 or block not in text:
        errors.append(f"{advisory}: missing/stale attributed scores; run --scores {advisory}")
    if live and changes:
        errors.extend(changes)
    return errors, block


def validate_all(root=ROOT, live=False, refresh=False):
    errors, covered = [], set()
    for manifest in sorted((root / EVIDENCE).glob("*.evidence.json")):
        try:
            config = json.loads(manifest.read_text(encoding="utf-8"))
            name = config["advisory"]
            if name in covered:
                raise ValueError(f"duplicate evidence manifest for {name}")
            covered.add(name)
            failures, _ = validate_bundle(root, manifest, live, refresh)
            errors.extend(failures)
        except (AssertionError, KeyError, ValueError, TypeError, OSError) as exc:
            errors.append(f"{manifest.name}: {exc}")
    for advisory in (root / "advisories").glob("*.md"):
        try:
            if finding_rows(advisory.read_text(encoding="utf-8")) and advisory.stem not in covered:
                errors.append(f"{advisory.name}: finding table needs an evidence manifest")
        except ValueError as exc:
            errors.append(f"{advisory.name}: {exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--refresh", action="store_true")
    mode.add_argument("--scores", metavar="ADVISORY_ID")
    args = parser.parse_args()
    if args.scores:
        if not re.fullmatch(r"[a-z0-9-]+", args.scores):
            parser.error("invalid advisory ID")
        _, block = validate_bundle(ROOT, ROOT / EVIDENCE / f"{args.scores}.evidence.json")
        print(block)
        return 0
    errors = validate_all(live=args.live, refresh=args.refresh)
    print("\n".join(errors) if errors else "CVE evidence checks passed.")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
