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


# --- Active HTML in built pages -------------------------------------------
#
# `site/build.py` renders Markdown with raw HTML passed through, and the daily
# sweep writes that Markdown after reading web pages it does not control. A tag
# pasted outside a code span would be published as live HTML on a site with no
# Content-Security-Policy. The renderer escapes raw HTML; this is the second
# gate: the only script a page may carry is JSON-LD, and the only inline event
# handlers are the ones in `site/template.html` itself.

_EMBEDDING_TAGS = {"iframe", "frame", "frameset", "object", "embed", "applet", "base", "form"}
_URL_ATTRS = {"href", "src", "action", "formaction", "xlink:href", "data", "poster"}
_SCRIPT_SCHEMES = ("javascript:", "vbscript:", "data:text/html")
# Malformed tags the parser reads differently from a browser, such as
# `<svg/onload=...>` or a handler glued to a closing quote.
_HANDLER_TAG = re.compile(r"""<[a-zA-Z][^<>]*[\s/"']on[a-z]+\s*=[^<>]*>""", re.IGNORECASE)
_URL_NOISE = re.compile(r"[\x00-\x20]+")


class _ActiveHTMLFinder(HTMLParser):
    """Collect tags and attributes that make a page run code or load one.

    HTMLParser lower-cases names and decodes character references in attribute
    values, so `HREF="jav&#x61;script:..."` is seen as a browser sees it."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: list[str] = []
        self.handlers: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag, attrs):
        # A browser keeps the first of two attributes with the same name. Tag-level
        # checks read that one. Every occurrence is still checked on its own below.
        d: dict[str, str] = {}
        for name, value in attrs:
            d.setdefault(name, value or "")
        if tag == "script":
            if d.get("type", "").strip().lower() != "application/ld+json" or "src" in d:
                self.found.append(f"<script {sorted(d)}>")
        elif tag in _EMBEDDING_TAGS:
            self.found.append(f"<{tag}>")
        elif tag == "meta" and d.get("http-equiv", "").strip().lower() == "refresh":
            self.found.append("<meta http-equiv=refresh>")
        for name, value in attrs:
            value = value or ""
            if name.startswith("on"):
                self.handlers.append((tag, name, value))
            elif name == "srcdoc":
                self.found.append(f"<{tag} srcdoc>")
            elif name in _URL_ATTRS:
                url = _URL_NOISE.sub("", value).lower()
                if url.startswith(_SCRIPT_SCHEMES):
                    self.found.append(f"<{tag} {name}={url[:24]}>")

    handle_startendtag = handle_starttag


def _scan(page_html: str) -> _ActiveHTMLFinder:
    finder = _ActiveHTMLFinder()
    finder.feed(page_html)
    finder.close()
    return finder


def _active_html(page_html: str, template_html: str = "") -> list[str]:
    allowed_handlers = set(_scan(template_html).handlers)
    allowed_tags = set(_HANDLER_TAG.findall(template_html))
    finder = _scan(page_html)
    found = list(finder.found)
    found += [f"<{tag} {name}>" for tag, name, value in finder.handlers
              if (tag, name, value) not in allowed_handlers]
    found += [tag for tag in _HANDLER_TAG.findall(page_html) if tag not in allowed_tags]
    return found


def test_built_pages_carry_no_active_html(all_html_files, dist_dir, repo_root):
    template = (repo_root / "site" / "template.html").read_text(encoding="utf-8")
    assert all_html_files, "no built pages to check"
    offenders = {}
    for page in all_html_files:
        found = _active_html(page.read_text(encoding="utf-8"), template)
        if found:
            offenders[str(page.relative_to(dist_dir))] = found[:3]
    assert not offenders, (
        "Built pages contain active HTML that did not come from the template. "
        "Put the tag in a code span or fenced block in the Markdown source, or remove "
        "it if it came from copied web content:\n"
        + "\n".join(f"  {name}: {tags}" for name, tags in sorted(offenders.items())[:10])
    )


def test_active_html_detector_catches_each_shape():
    for sample in (
        "<p>ok</p><script>x()</script>",
        '<script src="//example.com/x.js" data-x="application/ld+json"></script>',
        '<script type="application/ld+json" src="//example.com/x.js"></script>',
        '<iframe src="https://example.com"></iframe>',
        '<base href="https://example.com/">',
        '<meta http-equiv="refresh" content="0;url=https://example.com/">',
        '<img src="a.png" onerror="x()">',
        "<img src=x ONERROR=x()>",
        "<svg/onload=x()>",
        '<img src="a"onerror=x()>',
        '<img alt=">" onerror=x()>',
        '<a href="javascript:x()">y</a>',
        '<a href="jav&#x61;script:x()">y</a>',
        '<a href=" java&#9;script:x()">y</a>',
        '<a HREF="JavaScript:x()">y</a>',
        '<button formaction="javascript:x()">y</button>',
        '<a href="javascript:x()" href="https://example.com/">y</a>',
        '<a href="https://example.com/" href="javascript:x()">y</a>',
        '<script type="text/javascript" type="application/ld+json">x()</script>',
        '<img src=x title=">" onerror="x()">',
    ):
        assert _active_html(sample), sample
    for sample in (
        '<script type="application/ld+json">{}</script><p>on = 1</p>',
        "<pre>&lt;script&gt;x()&lt;/script&gt;</pre>",
        '<h2 id="one">One</h2><a href="https://example.com/javascript:">x</a>',
        '<meta name="description" content="turn it on=now">',
    ):
        assert not _active_html(sample), sample
    handler = '<button onclick="t()">menu</button>'
    assert not _active_html(f"<body>{handler}</body>", handler)
    assert _active_html('<button onclick="other()">menu</button>', handler)


# --- Renderer output control ----------------------------------------------

def _render(markdown_text: str) -> str:
    import sys

    site_dir = str(Path(__file__).resolve().parent.parent / "site")
    if site_dir not in sys.path:
        sys.path.insert(0, site_dir)
    import build  # type: ignore

    return build.render_markdown(markdown_text)[0]


def test_renderer_escapes_raw_html():
    for source in (
        "Text <script>x()</script> more",
        "<script>x()</script>",
        '<img src="a.png" onerror="x()">',
        '<iframe src="https://example.com"></iframe>',
        "<div>\n\n<script>x()</script>\n\n</div>",
        'Path scripts/<subdir>/file and <a href="javascript:x()">link</a>',
    ):
        rendered = _render(source)
        assert not _active_html(rendered), (source, rendered)
    assert "&lt;subdir&gt;" in _render("Path scripts/<subdir>/file")


def test_renderer_neutralizes_markdown_made_active_content():
    for source in (
        "[link](javascript:x())",
        "[link](JaVaScRiPt:x())",
        "[link](data:text/html,x)",
        "![image](javascript:x())",
        '[link](https://example.com){: onclick="x()" }',
        "<javascript:x()>",
    ):
        rendered = _render(source)
        assert not _active_html(rendered), (source, rendered)
        assert "onclick" not in rendered.lower()
        assert "x()" not in rendered or "&lt;" in rendered, (source, rendered)
    for source in (
        "[link](javascript:x())",
        "[link](data:text/html,x)",
        "[link][ref]\n\n[ref]: javascript:x()",
        "[link](jav&#x61;script:x())",
    ):
        assert 'href="#"' in _render(source), source
    assert "&lt;javascript:" in _render("<javascript:x()>")
    styled = _render('[a](x){: style="position:fixed" ping="https://example.com" ONCLICK="x()" }')
    for attribute in ("style", "ping", "onclick"):
        assert attribute not in styled.lower(), styled
    kept = _render("[a](https://example.com/x) [b](../playbooks/x.md) [c](#top) [d](mailto:a@example.com)")
    for target in ('href="https://example.com/x"', 'href="../playbooks/x.md"', 'href="#top"', "mailto:"):
        assert target in kept, kept


def test_renderer_keeps_code_and_drops_marker_comments():
    rendered = _render("<!-- cve-metrics:start -->\n\nBody text.\n\n```html\n<!-- kept -->\n<script>x()</script>\n```\n")
    assert "cve-metrics" not in rendered
    assert "kept" in rendered and "Body text." in rendered
    assert "<script>" not in rendered
    indented = _render("Text.\n\n    <!-- indented -->\n    code\n")
    assert "indented" in indented and "code" in indented


def test_jsonld_cannot_close_its_script_element(all_html_files):
    pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
    checked = 0
    for page in all_html_files:
        for payload in pattern.findall(page.read_text(encoding="utf-8")):
            checked += 1
            assert "<" not in payload and ">" not in payload, page.name
            json.loads(payload)
    assert checked, "no JSON-LD found in built pages"
