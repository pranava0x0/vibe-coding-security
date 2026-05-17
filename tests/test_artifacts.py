"""Site-level artifacts: sitemap, atom feed, JSON schema, API endpoints."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET


SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def test_sitemap_well_formed(sitemap_root):
    assert sitemap_root.tag.endswith("urlset"), f"sitemap root is {sitemap_root.tag}, not urlset"


def test_sitemap_has_enough_urls(sitemap_root):
    urls = sitemap_root.findall(f"{SITEMAP_NS}url")
    assert len(urls) >= 30, f"sitemap has only {len(urls)} URLs"


def test_every_sitemap_entry_has_loc_and_lastmod(sitemap_root):
    for url in sitemap_root.findall(f"{SITEMAP_NS}url"):
        loc = url.find(f"{SITEMAP_NS}loc")
        lastmod = url.find(f"{SITEMAP_NS}lastmod")
        assert loc is not None and loc.text, "url missing <loc>"
        assert lastmod is not None and lastmod.text, f"{loc.text}: missing lastmod"


def test_sitemap_has_changefreq_and_priority(sitemap_root):
    for url in sitemap_root.findall(f"{SITEMAP_NS}url"):
        cf = url.find(f"{SITEMAP_NS}changefreq")
        pri = url.find(f"{SITEMAP_NS}priority")
        assert cf is not None and cf.text, "missing changefreq"
        assert pri is not None and pri.text, "missing priority"
        assert 0.0 <= float(pri.text) <= 1.0, f"priority out of range: {pri.text}"


def test_atom_feed_well_formed(atom_feed_root):
    assert atom_feed_root.tag.endswith("feed"), f"atom root is {atom_feed_root.tag}"


def test_atom_feed_has_required_elements(atom_feed_root):
    for tag in ("title", "id", "updated", "link"):
        elem = atom_feed_root.find(f"{ATOM_NS}{tag}")
        assert elem is not None, f"atom feed missing <{tag}>"


def test_atom_entries_are_valid(atom_feed_root):
    entries = atom_feed_root.findall(f"{ATOM_NS}entry")
    assert len(entries) > 0, "atom feed has no entries"
    for entry in entries:
        for tag in ("title", "id", "updated", "link", "summary"):
            elem = entry.find(f"{ATOM_NS}{tag}")
            assert elem is not None, f"atom entry missing <{tag}>"
        updated = entry.find(f"{ATOM_NS}updated").text
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", updated), (
            f"atom updated must be RFC3339: {updated}"
        )


def test_atom_feed_entries_recent_first(atom_feed_root):
    """The latest entry should be on top."""
    entries = atom_feed_root.findall(f"{ATOM_NS}entry")
    if len(entries) < 2:
        return
    updates = [e.find(f"{ATOM_NS}updated").text for e in entries]
    assert updates == sorted(updates, reverse=True), "atom feed entries not in descending date order"


def test_advisories_json_well_formed(advisories_json, parsed_advisories):
    assert "advisories" in advisories_json
    assert "generated" in advisories_json
    assert len(advisories_json["advisories"]) == len(parsed_advisories), (
        f"advisories.json has {len(advisories_json['advisories'])} entries, "
        f"but {len(parsed_advisories)} .md files exist"
    )


def test_advisories_json_entries_have_all_fields(advisories_json):
    required = {"id", "title", "description", "severity", "status",
                "date_disclosed", "last_updated", "ecosystems",
                "tools_affected", "tags", "url", "markdown_url"}
    for entry in advisories_json["advisories"]:
        missing = required - set(entry.keys())
        assert not missing, f"advisory {entry.get('id')}: missing JSON fields: {missing}"


def test_advisory_schema_is_valid_json_schema(advisory_schema):
    assert advisory_schema["$schema"].startswith("https://json-schema.org/")
    assert advisory_schema["type"] == "object"
    assert "required" in advisory_schema
    assert "properties" in advisory_schema
    # Enums sanity
    assert set(advisory_schema["properties"]["severity"]["enum"]) >= {"critical", "high", "medium"}


def test_search_json_indexes_every_page(search_json, all_html_files, dist_dir):
    indexed_urls = {item["url"] for item in search_json["items"]}
    page_urls = {f"/{html.relative_to(dist_dir).as_posix()}" for html in all_html_files}
    missing = page_urls - indexed_urls
    assert not missing, f"search.json missing entries for: {sorted(missing)}"


def test_api_v1_endpoints_exist(dist_dir: Path):
    assert (dist_dir / "api" / "v1" / "advisories.json").exists()
    assert (dist_dir / "api" / "v1" / "index.json").exists()
    api_idx = json.loads((dist_dir / "api" / "v1" / "index.json").read_text())
    assert api_idx["version"] == "v1"
    assert "endpoints" in api_idx


def test_robots_txt_allows_all_and_points_to_sitemap(dist_dir: Path):
    text = (dist_dir / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in text
    assert "Allow: /" in text
    assert "Sitemap: https://" in text
