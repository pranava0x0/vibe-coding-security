"""Regression cases for issue #114 and registry disagreements found in review."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cve_evidence", ROOT / "tools/validate_cve_evidence.py")
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
ADVISORY = "2026-09-mcp-remote-oauth-discovery-ssrf-cve-batch"
CVE = "CVE-2026-51995"


@pytest.fixture
def corpus(tmp_path):
    shutil.copytree(ROOT / evidence.EVIDENCE, tmp_path / evidence.EVIDENCE)
    (tmp_path / "advisories").mkdir()
    shutil.copy(ROOT / "advisories" / f"{ADVISORY}.md", tmp_path / "advisories")
    return tmp_path


def change_json(root, name, mutate):
    path = root / evidence.EVIDENCE / name
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data))


def test_repository_evidence():
    assert evidence.validate_all() == []


def test_original_swap_fails(corpus):
    path = corpus / "advisories" / f"{ADVISORY}.md"
    text = path.read_text()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("| F-02 |"):
            lines[i] = line[:line.rfind("|", 0, len(line) - 1) + 1] + " (none listed) |"
        elif line.startswith("| F-10 |"):
            lines[i] = line.replace("(none listed)", CVE)
    path.write_text("\n".join(lines))
    assert any("CVE/finding rows disagree" in e for e in evidence.validate_all(corpus))


@pytest.mark.parametrize("mode", ["remove-cve", "remove-row", "duplicate-row", "extra-cve"])
def test_table_omissions_and_duplicates(corpus, mode):
    path = corpus / "advisories" / f"{ADVISORY}.md"
    text = path.read_text()
    row = next(l for l in text.splitlines() if l.startswith("| F-02 |"))
    replacement = {
        "remove-cve": row.replace(CVE, "none"),
        "remove-row": "",
        "duplicate-row": row + "\n" + row,
        "extra-cve": row.replace(CVE, CVE + ", CVE-2026-51994"),
    }[mode]
    path.write_text(text.replace(row, replacement))
    assert evidence.validate_all(corpus)


@pytest.mark.parametrize("case", ["missing", "ambiguous", "adp-only", "wrong-id", "rejected"])
def test_invalid_cna_evidence(corpus, case):
    def mutate(record):
        cna = record["containers"]["cna"]
        if case in {"missing", "adp-only"}:
            if case == "adp-only":
                record["containers"]["adp"][0]["references"] = deepcopy(cna["references"])
            cna["references"] = []
        elif case == "ambiguous":
            cna["references"].append({"url": cna["references"][-1]["url"].replace("F-02", "F-10")})
        elif case == "wrong-id":
            record["cveMetadata"]["cveId"] = "CVE-2026-51994"
        else:
            record["cveMetadata"]["state"] = "REJECTED"
    change_json(corpus, CVE + ".cve.json", mutate)
    assert evidence.validate_all(corpus)


@pytest.mark.parametrize("field,value", [
    ("baseScore", 8.0),
    ("baseSeverity", "CRITICAL"),
    ("vectorString", "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N"),
])
def test_changed_scores_require_prose_update(corpus, field, value):
    def mutate(record):
        record["containers"]["adp"][0]["metrics"][0]["cvssV3_1"][field] = value
    change_json(corpus, CVE + ".cve.json", mutate)
    assert any("stale attributed scores" in e for e in evidence.validate_all(corpus))


def test_score_provider_not_assumed(corpus):
    def mutate(record):
        record["containers"]["adp"][0]["providerMetadata"]["shortName"] = "Another-ADP"
    change_json(corpus, CVE + ".cve.json", mutate)
    assert any("stale attributed scores" in e for e in evidence.validate_all(corpus))


def test_new_score_on_previously_unscored_record(corpus):
    base = json.loads((corpus / evidence.EVIDENCE / (CVE + ".cve.json")).read_text())
    def mutate(record):
        record["containers"]["adp"] = base["containers"]["adp"]
    change_json(corpus, "CVE-2026-52001.cve.json", mutate)
    assert evidence.validate_all(corpus)


def test_new_table_cannot_skip_evidence(corpus):
    (corpus / "advisories/new.md").write_text("| **F-01** | finding | 1–2 | CVE-2026-12345 |")
    assert any("needs an evidence manifest" in e for e in evidence.validate_all(corpus))


def test_deleted_manifest_cannot_skip_checks(corpus):
    next((corpus / evidence.EVIDENCE).glob("*.evidence.json")).unlink()
    assert evidence.validate_all(corpus)


def test_missing_snapshot(corpus):
    (corpus / evidence.EVIDENCE / (CVE + ".cve.json")).unlink()
    assert evidence.validate_all(corpus)


def test_version_conflict_requires_public_disposition(corpus):
    change_json(corpus, ADVISORY + ".evidence.json", lambda d: d.update(version_conflicts={}))
    assert any("OSV fixed-version conflicts" in e for e in evidence.validate_all(corpus))


def test_resolved_osv_conflict_requires_review(corpus):
    change_json(corpus, CVE + ".osv.json", lambda d: d.update(affected=[]))
    assert any("OSV fixed-version conflicts" in e for e in evidence.validate_all(corpus))


def test_removed_public_conflict_note(corpus):
    path = corpus / "advisories" / f"{ADVISORY}.md"
    path.write_text(path.read_text().replace("Do not use that OSV boundary as proof of a fix.", ""))
    assert any("disposition missing" in e for e in evidence.validate_all(corpus))


def test_offline_does_not_fetch(corpus, monkeypatch):
    def unexpected(*args):
        pytest.fail("offline gate made a network request")
    monkeypatch.setattr(evidence, "fetch", unexpected)
    assert evidence.validate_all(corpus) == []


def test_live_failure_is_not_success(corpus, monkeypatch):
    def unavailable(*args):
        raise OSError("registry unavailable")
    monkeypatch.setattr(evidence, "fetch", unavailable)
    assert any("registry unavailable" in e for e in evidence.validate_all(corpus, live=True))


def test_live_drift_does_not_write(corpus, monkeypatch):
    before = {p: p.read_bytes() for p in (corpus / evidence.EVIDENCE).glob("*.json")}
    def drift(kind, cve):
        record = json.loads((corpus / evidence.EVIDENCE / f"{cve}.{kind}.json").read_text())
        if kind == "cve":
            record["cveMetadata"]["dateUpdated"] = "2026-10-02T18:00:00Z"
        return record
    monkeypatch.setattr(evidence, "fetch", drift)
    assert any("changed; review" in e for e in evidence.validate_all(corpus, live=True))
    assert all(p.read_bytes() == data for p, data in before.items())


def test_failed_refresh_does_not_partially_write(corpus, monkeypatch):
    before = {p: p.read_bytes() for p in (corpus / evidence.EVIDENCE).glob("*.json")}
    def partial(kind, cve):
        if kind == "osv":
            raise OSError("OSV unavailable")
        record = json.loads((corpus / evidence.EVIDENCE / f"{cve}.{kind}.json").read_text())
        record["extra"] = "new data"
        return record
    monkeypatch.setattr(evidence, "fetch", partial)
    assert evidence.validate_all(corpus, refresh=True)
    assert all(p.read_bytes() == data for p, data in before.items())


def test_nvd_transport_timestamp_is_not_drift(corpus, monkeypatch):
    def same(kind, cve):
        record = json.loads((corpus / evidence.EVIDENCE / f"{cve}.{kind}.json").read_text())
        if kind == "nvd":
            record["timestamp"] = "later"
        return record
    monkeypatch.setattr(evidence, "fetch", same)
    assert evidence.validate_all(corpus, live=True) == []


def test_no_registry_redirects():
    with pytest.raises(ValueError, match="redirect refused"):
        evidence.NoRedirect().redirect_request(None, None, 302, "", {}, "http://127.0.0.1/")


@pytest.mark.parametrize("cve", ["../../secrets", "CVE-2026-1234?url=http://localhost", "CVE-1234"])
def test_fetch_validates_id_before_network(cve):
    with pytest.raises(ValueError, match="invalid CVE"):
        evidence.fetch("cve", cve)


def test_score_rows_record_vectors():
    """A score without its vector hides conditions such as required user interaction."""
    _, block = evidence.validate_bundle(ROOT, ROOT / evidence.EVIDENCE / f"{ADVISORY}.evidence.json")
    rows = {line.split("|")[1].strip(): line for line in block.splitlines() if line.startswith("| CVE-")}
    assert "`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H`" in rows["CVE-2026-51997"]
    # CISA ADP scored CVE-2026-52001 on 2026-10-06 (previously unscored); the row must carry
    # the vector and the provider date, attributed to CISA-ADP, not to the CNA.
    assert "CISA-ADP / 3.1: 7.5 High" in rows["CVE-2026-52001"]
    assert "`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`" in rows["CVE-2026-52001"]
    assert "2026-10-06" in rows["CVE-2026-52001"]


def test_checks_survive_python_optimize_flag(corpus):
    """`python -O` strips assert statements; the gate must not depend on them."""
    change_json(corpus, CVE + ".cve.json", lambda record: record["cveMetadata"].update(state="REJECTED"))
    code = ("import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
            "import validate_cve_evidence as v; print(len(v.validate_all(Path(sys.argv[2]))))")
    result = subprocess.run([sys.executable, "-O", "-c", code, str(ROOT / "tools"), str(corpus)],
                            capture_output=True, text=True, check=True)
    assert int(result.stdout.strip()) > 0


def test_live_requests_are_spaced(monkeypatch):
    """NVD allows five unauthenticated requests per rolling 30 seconds."""
    slept = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self, limit):
            return json.dumps({"cveMetadata": {"cveId": CVE, "state": "PUBLISHED"}}).encode()

    class Opener:
        def open(self, request, timeout):
            return Response()

    monkeypatch.setattr(evidence.urllib.request, "build_opener", lambda *handlers: Opener())
    monkeypatch.setattr(evidence.time, "sleep", slept.append)
    monkeypatch.setattr(evidence, "_last_request", float("-inf"))
    evidence.fetch("cve", CVE)
    evidence.fetch("cve", CVE)
    assert len(slept) == 1 and 0 < slept[0] <= evidence.REQUEST_DELAY


def test_evidence_published_without_local_research(dist_dir):
    for source in (ROOT / evidence.EVIDENCE).glob("*.json"):
        assert (dist_dir / evidence.EVIDENCE / source.name).read_bytes() == source.read_bytes()
    assert (dist_dir / evidence.EVIDENCE / "NOTICE.txt").read_bytes() == (ROOT / evidence.EVIDENCE / "NOTICE.txt").read_bytes()
    assert (dist_dir / "sources/mcp-remote-evidence.html").exists()
    assert not list(dist_dir.rglob("*.local.md"))
