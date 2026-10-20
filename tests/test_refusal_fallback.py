"""Guards on how the sweep routine handles being switched off Claude Fable.

Why this file exists
--------------------
The daily cloud routine runs this skill on Fable 5.1. A safety classifier
flagged the model's own advisory text about a worm, the run re-sent it, and
Claude Code's refusal fallback emitted `model_refusal_fallback` and finished
the session on Opus 4.8. The owner chose to keep that switch on, because a
refused turn would otherwise end an unattended run. The guard is now: the
switch is allowed but every model event is logged in fallback.log.md, and a
classifier-stop protocol in SKILL.md tells the run not to re-send flagged text.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

SKILL_PATH = ".claude/skills/vibe-security-update/SKILL.md"
FALLBACK_LOG = ".claude/skills/vibe-security-update/fallback.log.md"
LOG_HEADER = "| Date | Run | Event | From \u2192 to | Doing | Cause | Resolution |"
LOG_EVENTS = {"safeguard-stop", "model-switch", "overload-fallback", "permission-block", "rate-limit"}


def _settings(repo_root: Path) -> dict:
    return json.loads((repo_root / ".claude" / "settings.json").read_text(encoding="utf-8"))


def _skill(repo_root: Path) -> str:
    return (repo_root / SKILL_PATH).read_text(encoding="utf-8")


def _has_heading(text: str, needle: str) -> bool:
    # Skip fenced code blocks so example headings in templates do not count.
    # A fence closes only on the same character repeated at least as many times.
    fence = ""
    for line in text.splitlines():
        m = re.match(r"^(`{3,}|~{3,})", line)
        if m and not fence:
            fence = m.group(1)
        elif m and fence and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
            fence = ""
        elif not fence and re.match(r"^#{1,6} ", line) and needle in line:
            return True
    return False


def _section(text: str, start: str, end: str) -> str:
    m = re.search(rf"^{re.escape(start)}.*?(?=^{re.escape(end)})", text, re.DOTALL | re.MULTILINE)
    assert m, f"SKILL.md section between '{start}' and '{end}' not found."
    return m.group(0)


def test_project_settings_keep_switch_explicit_and_use_opus_alias(repo_root: Path):
    s = _settings(repo_root)
    assert s.get("switchModelsOnFlag") is True, (
        "switchModelsOnFlag must be exactly true. This is a recorded decision: a switch "
        "may happen but is logged in fallback.log.md, because a refused turn would end "
        "an unattended run. Removing the key hides the decision behind a default."
    )
    fb = s.get("fallbackModel")
    assert isinstance(fb, list) and fb and fb[0] == "opus", (
        f"fallbackModel must be a list starting with the alias 'opus', got {fb!r}. "
        "A pinned id such as claude-opus-4-8 goes stale when a newer Opus ships."
    )


def test_settings_json_sets_only_the_two_fallback_keys(repo_root: Path):
    keys = set(_settings(repo_root).keys())
    assert keys == {"switchModelsOnFlag", "fallbackModel"}, (
        f".claude/settings.json has keys {sorted(keys)}. Any other key (model, "
        "modelOverrides, availableModels, env, hooks) changes every cloud and local "
        "session in this repo and must be added deliberately with its own test."
    )


def test_fallback_log_is_well_formed(repo_root: Path):
    why = " The log is the owner's audit trail for model switches and must stay machine-readable."
    path = repo_root / FALLBACK_LOG
    assert path.exists(), f"{FALLBACK_LOG} is missing." + why
    lines = path.read_text(encoding="utf-8").splitlines()
    assert LOG_HEADER in lines, f"Table header must be exactly: {LOG_HEADER}" + why
    rows = [ln for ln in lines[lines.index(LOG_HEADER) + 2:] if ln.startswith("|")]
    prev = ""
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        assert len(cells) == 7, f"Row has {len(cells)} cells, expected 7: {row}" + why
        day, event = cells[0], cells[2]
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", day), f"Date {day!r} is not YYYY-MM-DD: {row}" + why
        bad = {t.strip() for t in event.split(",")} - LOG_EVENTS
        assert not bad, f"Unknown Event value(s) {sorted(bad)} in: {row}" + why
        assert day >= prev, f"Date {day} comes after {prev}; rows must be oldest first." + why
        prev = day


def test_skill_requires_fallback_log_rows(repo_root: Path):
    count = _skill(repo_root).count("fallback.log.md")
    assert count >= 2, (
        f"SKILL.md mentions fallback.log.md {count} time(s), expected at least 2 (the "
        "file table and the rule that every model event gets a row). Without both, "
        "switches stop being logged and the owner loses the audit trail."
    )


def test_skill_has_classifier_stop_protocol(repo_root: Path):
    text = _skill(repo_root)
    why = " Removing the classifier-stop protocol makes the switch to Opus 4.8 more likely."
    assert _has_heading(text, "Classifier stops"), "SKILL.md has no 'Classifier stops' heading." + why
    assert "do not re-send" in text, "SKILL.md no longer says 'do not re-send'." + why
    assert "deferred_after_classifier_stop" in text, (
        "SKILL.md no longer names the deferred_after_classifier_stop field." + why
    )


def test_skill_has_writing_rules(repo_root: Path):
    assert _has_heading(_skill(repo_root), "Writing rules"), (
        "SKILL.md has no 'Writing rules' heading. The routine's prose rules live there."
    )


def test_run_log_schema_records_classifier_events(repo_root: Path):
    step5 = _section(_skill(repo_root), "### Step 5", "### Step 6")
    assert "classifier_events:" in step5, (
        "The Step 5 run-log template must include 'classifier_events:' so each run "
        "records classifier stops and a recurring trigger is visible across runs."
    )
    assert "deferred_after_classifier_stop:" in step5, (
        "The Step 5 run-log template must include 'deferred_after_classifier_stop:' "
        "so items a run skipped after a classifier stop are written down for the next run."
    )


def test_step0_reads_deferred_items(repo_root: Path):
    step0 = _section(_skill(repo_root), "### Step 0", "### Step 1")
    assert "deferred_after_classifier_stop" in step0, (
        "Step 0 must read deferred_after_classifier_stop from the last run log. "
        "Otherwise items deferred after a classifier stop are never picked up again."
    )


def test_skill_checkpoints_before_malware_writes(repo_root: Path):
    assert "checkpoint commit" in _skill(repo_root), (
        "SKILL.md must tell the run to make a checkpoint commit of non-malware work "
        "before writing worm or campaign advisories, so a run ended by a refusal keeps it."
    )


def test_new_advisory_titles_are_short(parsed_advisories):
    # The 25-word limit starts on 2026-10-10. Older advisories are exempt because
    # the rule is new and they were written before it existed.
    cutoff = date(2026, 10, 10)
    for path, fm, _body in parsed_advisories:
        raw = fm.get("date_disclosed")
        if raw is None:
            continue
        if isinstance(raw, date):
            disclosed = raw
        else:
            # Some older advisories use a partial date such as 2025-07 or 2025.
            parts = [int(x) for x in str(raw)[:10].split("-")] + [1, 1]
            disclosed = date(parts[0], parts[1], parts[2])
        if disclosed < cutoff:
            continue
        words = len(str(fm["title"]).split())
        assert words <= 25, (
            f"{path.name}: title is {words} words. Titles on or after {cutoff} must be "
            "25 words or fewer; move detail into the body."
        )


# Every main-session safeguard stop from 2026-10-05 to 2026-10-19 was the
# sweep's own prose about malicious software (LEARNINGS.md §54). The corpus only
# needs the artifact's identity and the remediation, so these files use a
# table-first template with no narrative section.
ALLOWED_SECTIONS = (
    "## TL;DR",
    "## Packages and versions",
    "## Am I affected?",
    "## If you are affected",
    "## Prevention",
    "## Sources",
)


def _sections(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    current = None
    fence = ""
    for line in body.splitlines():
        m = re.match(r"^(`{3,}|~{3,})", line)
        if m:
            if not fence:
                fence = m.group(1)
            elif line.startswith(fence[0] * len(fence)):
                fence = ""
        elif not fence and line.startswith("## "):
            current = line.strip()
            out[current] = ""
            continue
        if current:
            out[current] += line + "\n"
    return out


TABLE_COLUMNS = ("ecosystem", "name", "version", "action")


def _cells(row: str) -> list[str]:
    return [c.strip().lower() for c in row.strip().strip("|").split("|")]


def _has_table(text: str) -> bool:
    # Header must name the ecosystem, name, versions and action columns, the
    # second row must be the separator, and every data row must fill each column.
    rows = [l for l in text.splitlines() if re.match(r"^\|.*\|\s*$", l)]
    if len(rows) < 3 or not re.match(r"^\|(\s*:?-{3,}:?\s*\|)+\s*$", rows[1]):
        return False
    header = _cells(rows[0])
    if not all(any(col in h for h in header) for col in TABLE_COLUMNS):
        return False
    required = [i for i, h in enumerate(header) if any(col in h for col in TABLE_COLUMNS)]
    return all(
        len(cells) == len(header) and all(cells[i] for i in required)
        for cells in (_cells(r) for r in rows[2:])
    )


def test_malicious_artifact_advisories_use_blocklist_template(parsed_advisories):
    for path, fm, body in parsed_advisories:
        if fm.get("kind") != "malicious-artifact":
            continue
        sections = _sections(body)
        assert _has_table(sections.get("## Packages and versions", "")), (
            f"{path.name}: a kind: malicious-artifact advisory needs a "
            "'## Packages and versions' section with a table of ecosystem, name and versions."
        )
        missing = [h for h in ALLOWED_SECTIONS if h not in sections]
        assert not missing, (
            f"{path.name}: a malicious-artifact advisory needs every template section; "
            f"missing {missing}."
        )
        for heading in sections:
            # Dated "## Update YYYY-MM-DD: ..." sections are how Step 2 records changes.
            if heading in ALLOWED_SECTIONS or heading.startswith("## Update "):
                continue
            raise AssertionError(
                f"{path.name}: drop '{heading}'. A malicious-artifact advisory names the "
                "artifact and the remediation and links the write-up for behaviour. "
                f"Allowed sections: {', '.join(ALLOWED_SECTIONS)}, and dated Update sections."
            )


def test_skill_writes_malicious_artifacts_last(repo_root: Path):
    text = _skill(repo_root)
    assert "Write malicious-artifact files last" in text, (
        "SKILL.md must keep malicious-artifact files at the end of the run, after the "
        "checkpoint commit and the review rounds, so a stop and the switch it can cause "
        "leave nothing else for the run to do."
    )


MALICIOUS_TAGS = {"worm", "self-propagating", "infostealer", "stealer", "rat", "backdoor",
                  "malicious-package", "typosquat", "malware"}


def _malicious_tags(fm: dict) -> set[str]:
    # malicious-package, malicious-extension, malicious-skill, malicious-mcp-server, ...
    tags = {str(t).lower() for t in fm.get("tags") or []}
    return {t for t in tags if t in MALICIOUS_TAGS or t.startswith("malicious-")}


def _legacy_malicious(repo_root: Path) -> set[str]:
    text = (repo_root / "tests" / "legacy_malicious_advisories.txt").read_text(encoding="utf-8")
    return {l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")}


def test_new_malicious_advisories_carry_kind(parsed_advisories, repo_root: Path):
    # Without the tag the template test above never runs, so a new worm or
    # stealer file could slip back to narrative prose. The exemption is keyed to
    # the files that existed when the template landed, not to date_disclosed,
    # because a deferred or late-found advisory can describe an older incident.
    legacy = _legacy_malicious(repo_root)
    for path, fm, _body in parsed_advisories:
        if path.name in legacy:
            continue
        hits = _malicious_tags(fm)
        if hits:
            assert fm.get("kind") == "malicious-artifact", (
                f"{path.name}: tagged {sorted(hits)} but has no 'kind: malicious-artifact'. "
                "Use the malicious-artifact template in CONTRIBUTING.md."
            )
