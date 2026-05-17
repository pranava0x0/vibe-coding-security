#!/usr/bin/env python3
"""
Validate the built site. Run after build.py.

Checks:
  1. Every expected output exists (HTML pages, llms.txt, sitemap.xml, etc.).
  2. No leftover .md links in rendered HTML (they should all be rewritten to .html).
  3. Every internal href in every HTML file resolves to an existing file.
  4. Every HTML page has: <title>, <meta description>, canonical link, JSON-LD.
  5. Heading hierarchy: no skipped levels (h1 → h3 without h2, etc.).
  6. Every advisory has required frontmatter (id, title, severity, status, date_disclosed).
  7. llms.txt is valid llmstxt.org format (starts with # title and contains > tagline).
  8. sitemap.xml is well-formed.
  9. advisories.json is parseable + contains the expected count.

Exits non-zero on any failure.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"
ADV_DIR = REPO_ROOT / "advisories"


class HTMLAuditor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str | None = None
        self._in_title = False
        self.has_description = False
        self.has_canonical = False
        self.has_jsonld = False
        self._in_jsonld = False
        self.jsonld_text = ""
        self.headings: list[int] = []
        self.internal_hrefs: list[str] = []
        self._stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = {k: v or "" for k, v in attrs}
        self._stack.append(tag)
        if tag == "title":
            self._in_title = True
        if tag == "meta" and attrs_d.get("name") == "description":
            if attrs_d.get("content"):
                self.has_description = True
        if tag == "link" and attrs_d.get("rel") == "canonical":
            self.has_canonical = True
        if tag == "script" and attrs_d.get("type") == "application/ld+json":
            self._in_jsonld = True
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1:]))
        if tag == "a":
            href = attrs_d.get("href", "")
            if href and not href.startswith(("http://", "https://", "mailto:", "#", "data:", "javascript:")):
                self.internal_hrefs.append(href)

    def handle_endtag(self, tag: str) -> None:
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            if self.jsonld_text.strip():
                self.has_jsonld = True

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title = (self.title or "") + data
        if self._in_jsonld:
            self.jsonld_text += data


def check_outputs_exist() -> list[str]:
    required = [
        "index.html", "alerts.html", "contributing.html",
        "advisories/index.html",
        "playbooks/index.html",
        "prevention/index.html",
        "sources/index.html",
        "tools/index.html",
        "style.css",
        ".nojekyll",
        "llms.txt", "llms-full.txt",
        "sitemap.xml", "robots.txt",
        "advisories.json", "search.json",
    ]
    errors = []
    for rel in required:
        if not (DIST_DIR / rel).exists():
            errors.append(f"missing required file: dist/{rel}")
    return errors


def check_no_md_links() -> list[str]:
    """Find .md links that *should* have been rewritten (relative paths only).
    External links to .md files (e.g., GitHub blob URLs) are intentional."""
    errors = []
    for html_path in DIST_DIR.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        for m in re.finditer(r'href="([^"]+)"', text):
            href = m.group(1)
            if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            # Strip anchor
            path = href.split("#", 1)[0]
            if path.endswith(".md"):
                errors.append(f"{html_path.relative_to(DIST_DIR)}: unrewritten .md link: href=\"{href}\"")
    return errors


def check_internal_links() -> list[str]:
    errors = []
    for html_path in DIST_DIR.rglob("*.html"):
        auditor = HTMLAuditor()
        try:
            auditor.feed(html_path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{html_path.relative_to(DIST_DIR)}: parse error: {e}")
            continue
        for href in auditor.internal_hrefs:
            # Strip query / anchor
            parsed = urlparse(href)
            path_part = parsed.path
            if not path_part:
                continue
            target = (html_path.parent / path_part).resolve()
            # Allow target to be a directory (with index.html) or a file
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(
                    f"{html_path.relative_to(DIST_DIR)}: broken link: {href} → {target.relative_to(REPO_ROOT)}"
                )
    return errors


def check_html_metadata() -> list[str]:
    errors = []
    for html_path in DIST_DIR.rglob("*.html"):
        auditor = HTMLAuditor()
        try:
            auditor.feed(html_path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{html_path.relative_to(DIST_DIR)}: parse error: {e}")
            continue
        rel = html_path.relative_to(DIST_DIR)
        if not auditor.title:
            errors.append(f"{rel}: missing <title>")
        if not auditor.has_description:
            errors.append(f"{rel}: missing <meta name='description'>")
        if not auditor.has_canonical:
            errors.append(f"{rel}: missing canonical link")
        if not auditor.has_jsonld:
            errors.append(f"{rel}: missing JSON-LD")
    return errors


def check_heading_hierarchy() -> list[str]:
    errors = []
    for html_path in DIST_DIR.rglob("*.html"):
        auditor = HTMLAuditor()
        try:
            auditor.feed(html_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        levels = auditor.headings
        if not levels:
            continue
        # Allowed: any sequence where each level is at most prev+1
        for i in range(1, len(levels)):
            if levels[i] > levels[i - 1] + 1:
                rel = html_path.relative_to(DIST_DIR)
                errors.append(
                    f"{rel}: heading hierarchy skips from h{levels[i-1]} to h{levels[i]}"
                )
                break  # one per file is enough signal
    return errors


def check_advisory_frontmatter() -> list[str]:
    errors = []
    import yaml  # type: ignore
    required = {"id", "title", "severity", "status", "date_disclosed", "last_updated"}
    for md_path in ADV_DIR.glob("*.md"):
        if md_path.name == "README.md":
            continue
        text = md_path.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            errors.append(f"advisories/{md_path.name}: missing frontmatter")
            continue
        try:
            data = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            errors.append(f"advisories/{md_path.name}: yaml error: {e}")
            continue
        missing = required - set(data.keys())
        if missing:
            errors.append(f"advisories/{md_path.name}: missing frontmatter keys: {sorted(missing)}")
    return errors


def check_llms_txt() -> list[str]:
    errors = []
    p = DIST_DIR / "llms.txt"
    if not p.exists():
        return ["llms.txt missing"]
    text = p.read_text(encoding="utf-8")
    if not text.startswith("# "):
        errors.append("llms.txt does not start with '# Title'")
    if "\n> " not in text:
        errors.append("llms.txt missing '> tagline' line")
    if "## Advisories" not in text:
        errors.append("llms.txt missing '## Advisories' section")
    return errors


def check_sitemap() -> list[str]:
    errors = []
    p = DIST_DIR / "sitemap.xml"
    if not p.exists():
        return ["sitemap.xml missing"]
    try:
        tree = ET.parse(p)
        root = tree.getroot()
    except ET.ParseError as e:
        return [f"sitemap.xml parse error: {e}"]
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if not root.tag.endswith("urlset"):
        errors.append(f"sitemap.xml root is not urlset: {root.tag}")
    urls = root.findall(f"{ns}url")
    if len(urls) < 10:
        errors.append(f"sitemap.xml has only {len(urls)} URLs, expected more")
    for url in urls:
        loc = url.find(f"{ns}loc")
        if loc is None or not loc.text:
            errors.append("sitemap.xml: url missing <loc>")
    return errors


def check_advisories_json() -> list[str]:
    errors = []
    p = DIST_DIR / "advisories.json"
    if not p.exists():
        return ["advisories.json missing"]
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"advisories.json invalid JSON: {e}"]
    if "advisories" not in data:
        errors.append("advisories.json missing 'advisories' key")
    md_count = sum(1 for m in ADV_DIR.glob("*.md") if m.name != "README.md")
    json_count = len(data.get("advisories", []))
    if md_count != json_count:
        errors.append(f"advisories.json has {json_count} entries, but {md_count} advisory .md files exist")
    return errors


def main() -> int:
    checks = [
        ("Required outputs exist", check_outputs_exist),
        ("No leftover .md links in HTML", check_no_md_links),
        ("All internal links resolve", check_internal_links),
        ("HTML metadata present", check_html_metadata),
        ("Heading hierarchy OK", check_heading_hierarchy),
        ("Advisory frontmatter complete", check_advisory_frontmatter),
        ("llms.txt format", check_llms_txt),
        ("sitemap.xml well-formed", check_sitemap),
        ("advisories.json sane", check_advisories_json),
    ]
    total_errors = 0
    for label, fn in checks:
        errs = fn()
        if errs:
            print(f"✗ {label} ({len(errs)} issue{'s' if len(errs) != 1 else ''}):")
            for e in errs[:20]:
                print(f"    {e}")
            if len(errs) > 20:
                print(f"    ... +{len(errs) - 20} more")
            total_errors += len(errs)
        else:
            print(f"✓ {label}")
    if total_errors:
        print(f"\n{total_errors} validation issue(s) — fix before deploying.")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
