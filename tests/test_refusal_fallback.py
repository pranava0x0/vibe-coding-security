"""Guards against the sweep routine being silently switched off Claude Fable.

Why this file exists
--------------------
The daily cloud routine runs this skill on Fable 5.1. A safety classifier
flagged the model's own advisory text about a worm, the run re-sent it, and
Claude Code's refusal fallback emitted `model_refusal_fallback` and finished
the session on Opus 4.8. Two guards stop that: a committed .claude/settings.json
that disables the switch, and a classifier-stop protocol in SKILL.md that tells
the run not to re-send flagged text. Deleting either one re-opens the path.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

SKILL_PATH = ".claude/skills/vibe-security-update/SKILL.md"


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


def test_project_settings_disable_refusal_fallback(repo_root: Path):
    s = _settings(repo_root)
    assert s.get("switchModelsOnFlag") is False, (
        "switchModelsOnFlag must be exactly false. When true, a classifier flag "
        "silently switches the Fable routine to Opus 4.8 for the rest of the run."
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


def test_skill_has_classifier_stop_protocol(repo_root: Path):
    text = _skill(repo_root)
    why = " Removing the classifier-stop protocol re-opens the Opus 4.8 switch path."
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
