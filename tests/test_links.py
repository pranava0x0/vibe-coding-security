"""Link integrity: no broken internal hrefs, no leftover .md links."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.imgs_alts: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag, attrs):
        d = {k: v or "" for k, v in attrs}
        if tag == "a" and "href" in d:
            self.hrefs.append(d["href"])
        if tag == "img":
            self.srcs.append(d.get("src", ""))
            self.imgs_alts.append((d.get("src", ""), attrs and d.get("alt")))
        if tag == "link" and "href" in d:
            self.hrefs.append(d["href"])
        if tag == "script" and "src" in d:
            self.srcs.append(d["src"])


def test_no_relative_md_links_leaked(all_html_files, dist_dir):
    """Any .md href must point to an actual .md mirror file in dist/
    (these are the intentional 'View raw markdown' actions). Unrewritten
    .md links from source markdown would fail to resolve."""
    failures = []
    for html in all_html_files:
        text = html.read_text(encoding="utf-8")
        for m in re.finditer(r'href="([^"]+)"', text):
            href = m.group(1)
            if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            path = href.split("#", 1)[0]
            if not path.endswith(".md"):
                continue
            # The .md must resolve to an existing file
            target = (html.parent / path).resolve()
            if not target.exists():
                failures.append(f"{html.name}: unresolved .md link: {href}")
    assert not failures, "\n".join(failures[:10])


def test_all_internal_hrefs_resolve(dist_dir, all_html_files):
    failures = []
    for html in all_html_files:
        x = LinkExtractor()
        x.feed(html.read_text(encoding="utf-8"))
        for href in x.hrefs:
            if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            parsed = urlparse(href)
            path_part = parsed.path
            if not path_part:
                continue
            target = (html.parent / path_part).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                failures.append(
                    f"{html.relative_to(dist_dir)}: broken link: {href}"
                )
    assert not failures, "\n".join(failures[:20])


def test_canonical_link_present(all_html_files):
    for html in all_html_files:
        text = html.read_text(encoding="utf-8")
        assert 'rel="canonical"' in text, f"{html.name}: missing canonical link"


def test_md_alternate_link_present(all_html_files):
    for html in all_html_files:
        text = html.read_text(encoding="utf-8")
        assert 'rel="alternate" type="text/markdown"' in text, (
            f"{html.name}: missing markdown alternate link"
        )


def test_atom_feed_alternate_link_present(all_html_files):
    for html in all_html_files:
        text = html.read_text(encoding="utf-8")
        assert 'type="application/atom+xml"' in text, (
            f"{html.name}: missing atom feed alternate"
        )


def test_external_links_use_rel_noopener(all_html_files):
    """External links from `gh blob` rewrites should have rel='noopener'."""
    failures = []
    for html in all_html_files:
        for m in re.finditer(
            r'href="(https://github\.com/pranava0x0/vibe-coding-security/blob[^"]*)"([^>]*)>',
            html.read_text(encoding="utf-8"),
        ):
            tail = m.group(2)
            if "noopener" not in tail:
                failures.append(f"{html.name}: gh-blob link missing rel=noopener")
                break
    assert not failures, "\n".join(failures[:10])


def test_images_have_alt(all_html_files):
    """Every <img> needs alt (empty string allowed for decorative)."""
    failures = []
    for html in all_html_files:
        x = LinkExtractor()
        x.feed(html.read_text(encoding="utf-8"))
        for src, alt in x.imgs_alts:
            if alt is None:
                failures.append(f"{html.name}: <img src='{src}'> missing alt")
    assert not failures, "\n".join(failures[:10])
