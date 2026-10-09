"""Guards against the sweep routine being silently switched off Claude Fable.

Why this file exists
--------------------
The daily cloud routine runs this skill on Fable 5.1. A safety classifier would
flag the model's own advisory text about a worm, the run would re-send it, and
Claude Code's refusal fallback would emit `model_refusal_fallback` and finish
the session on Opus 4.8. Two guards stop that: a committed .claude/settings.json
that disables the switch, and a classifier-stop protocol in SKILL.md that tells
the run not to re-send flagged text. Deleting either one re-opens the path.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SKILL_PATH = ".claude/skills/vibe-security-update/SKILL.md"


def _settings(repo_root: Path) -> dict:
    return json.loads((repo_root / ".claude" / "settings.json").read_text(encoding="utf-8"))


def _skill(repo_root: Path) -> str:
    return (repo_root / SKILL_PATH).read_text(encoding="utf-8")


def _has_heading(text: str, needle: str) -> bool:
    return any(needle in line for line in text.splitlines() if re.match(r"^#{1,6} ", line))


def test_project_settings_disable_refusal_fallback(repo_root: Path):
    s = _settings(repo_root)
    assert s.get("switchModelsOnFlag") is False, (
        "switchModelsOnFlag must be exactly false. When true, a classifier flag "
        "silently degrades the Fable routine to Opus 4.8 for the rest of the run."
    )
    fb = s.get("fallbackModel")
    assert isinstance(fb, list) and fb and fb[0] == "opus", (
        f"fallbackModel must be a list starting with the alias 'opus', got {fb!r}. "
        "A pinned id such as claude-opus-4-8 goes stale when a newer Opus ships."
    )


def test_settings_json_has_no_other_model_keys(repo_root: Path):
    s = _settings(repo_root)
    assert "model" not in s, (
        "Do not set 'model' here. The routine's model is pinned in the routine "
        "definition, and a repo-level model would override it for every session."
    )
    env = s.get("env", {})
    val = env.get("CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK", "1")
    assert val == "1", (
        f"env.CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK is {val!r}. Any value other "
        "than '1' re-enables the switch to Opus 4.8 that switchModelsOnFlag turns off."
    )


def test_skill_has_classifier_stop_protocol(repo_root: Path):
    text = _skill(repo_root)
    why = " Removing the classifier-stop protocol re-opens the Opus 4.8 switch path."
    assert _has_heading(text, "Classifier stops"), "SKILL.md has no 'Classifier stops' heading." + why
    assert "do not re-send" in text, "SKILL.md no longer says 'do not re-send'." + why
    assert "deferred_after_classifier_stop" in text, (
        "SKILL.md no longer names the deferred_after_classifier_stop status." + why
    )


def test_skill_has_writing_rules(repo_root: Path):
    assert _has_heading(_skill(repo_root), "Writing rules"), (
        "SKILL.md has no 'Writing rules' heading. Those rules keep advisory prose "
        "from tripping the classifier in the first place."
    )


def test_run_log_schema_records_classifier_events(repo_root: Path):
    text = _skill(repo_root)
    m = re.search(r"^### Step 5.*?(?=^### Step 6)", text, re.DOTALL | re.MULTILINE)
    assert m, "SKILL.md Step 5 (run-log template) section not found."
    assert "classifier_events:" in m.group(0), (
        "The Step 5 run-log template must include 'classifier_events:' so each run "
        "records classifier stops and a recurring trigger is visible across runs."
    )
