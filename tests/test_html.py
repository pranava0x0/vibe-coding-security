"""Per-page HTML semantic + metadata + structural checks."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path


class MetaAuditor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str = ""
        self._in_title = False
        self.description: str = ""
        self.canonical: str = ""
        self.og: dict[str, str] = {}
        self.jsonld_blobs: list[str] = []
        self._in_jsonld = False
        self.headings: list[int] = []
        self.landmarks: set[str] = set()
        self._jsonld_buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = {k: v or "" for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            if d.get("name") == "description":
                self.description = d.get("content", "")
            if d.get("property", "").startswith("og:"):
                self.og[d["property"][3:]] = d.get("content", "")
        if tag == "link" and d.get("rel") == "canonical":
            self.canonical = d.get("href", "")
        if tag == "script" and d.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = []
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1:]))
        if tag in {"main", "nav", "aside", "header", "footer", "article"}:
            self.landmarks.add(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self.jsonld_blobs.append("".join(self._jsonld_buf))
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_jsonld:
            self._jsonld_buf.append(data)


def _audit(html_path: Path) -> MetaAuditor:
    a = MetaAuditor()
    a.feed(html_path.read_text(encoding="utf-8"))
    return a


def test_every_page_has_title(all_html_files, dist_dir):
    for html in all_html_files:
        a = _audit(html)
        assert a.title.strip(), f"{html.relative_to(dist_dir)}: empty <title>"


def test_every_page_has_meta_description(all_html_files, dist_dir):
    for html in all_html_files:
        a = _audit(html)
        assert a.description.strip(), f"{html.relative_to(dist_dir)}: missing meta description"


def test_every_page_has_canonical(all_html_files, dist_dir):
    for html in all_html_files:
        a = _audit(html)
        assert a.canonical.startswith("https://"), (
            f"{html.relative_to(dist_dir)}: missing canonical link"
        )


def test_every_page_has_og_tags(all_html_files, dist_dir):
    for html in all_html_files:
        a = _audit(html)
        for key in ("type", "title", "description", "url", "site_name"):
            assert a.og.get(key), f"{html.relative_to(dist_dir)}: missing og:{key}"


def test_every_page_has_valid_jsonld(all_html_files, dist_dir):
    for html in all_html_files:
        a = _audit(html)
        assert a.jsonld_blobs, f"{html.relative_to(dist_dir)}: missing JSON-LD"
        for blob in a.jsonld_blobs:
            data = json.loads(blob)
            assert data.get("@context") == "https://schema.org", (
                f"{html.relative_to(dist_dir)}: JSON-LD missing schema.org context"
            )
            assert "@type" in data, f"{html.relative_to(dist_dir)}: JSON-LD missing @type"


def test_heading_hierarchy_unbroken(all_html_files, dist_dir):
    """No skipping levels (h1 → h3 without an h2)."""
    for html in all_html_files:
        a = _audit(html)
        for i in range(1, len(a.headings)):
            assert a.headings[i] <= a.headings[i - 1] + 1, (
                f"{html.relative_to(dist_dir)}: heading hierarchy skips "
                f"h{a.headings[i-1]} → h{a.headings[i]}"
            )


def test_exactly_one_h1_per_page(all_html_files, dist_dir):
    for html in all_html_files:
        a = _audit(html)
        h1_count = sum(1 for h in a.headings if h == 1)
        assert h1_count == 1, (
            f"{html.relative_to(dist_dir)}: expected exactly 1 h1, got {h1_count}"
        )


def test_semantic_landmarks_present(all_html_files, dist_dir):
    """Each page should use the major HTML5 landmarks."""
    required = {"main", "nav", "header", "footer", "article"}
    for html in all_html_files:
        a = _audit(html)
        missing = required - a.landmarks
        assert not missing, (
            f"{html.relative_to(dist_dir)}: missing landmarks {sorted(missing)}"
        )


def test_html_has_lang_attribute(all_html_files, dist_dir):
    for html in all_html_files:
        text = html.read_text(encoding="utf-8")
        assert re.search(r'<html\s+[^>]*lang="', text), (
            f"{html.relative_to(dist_dir)}: <html> missing lang attribute"
        )


def test_skip_link_present(all_html_files, dist_dir):
    for html in all_html_files:
        text = html.read_text(encoding="utf-8")
        assert 'class="skip"' in text and 'href="#main"' in text, (
            f"{html.relative_to(dist_dir)}: missing skip-to-content link"
        )


def test_advisory_pages_have_techarticle_jsonld(dist_dir, parsed_advisories):
    for path, fm, _ in parsed_advisories:
        slug = path.stem
        html = dist_dir / "advisories" / f"{slug}.html"
        a = _audit(html)
        assert a.jsonld_blobs, f"{slug}: missing JSON-LD"
        types = {json.loads(b).get("@type") for b in a.jsonld_blobs}
        assert "TechArticle" in types, f"{slug}: advisory JSON-LD should be TechArticle"


def test_advisories_index_has_itemlist_jsonld(dist_dir):
    a = _audit(dist_dir / "advisories" / "index.html")
    types = {json.loads(b).get("@type") for b in a.jsonld_blobs}
    assert "ItemList" in types, "advisories index should have ItemList JSON-LD"
