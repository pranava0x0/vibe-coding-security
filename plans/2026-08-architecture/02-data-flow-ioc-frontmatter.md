# Spec 02 — Data flow: IOC frontmatter as the single source of truth

> **Theme:** data architecture · **Effort:** medium-high · **Blocks:** Spec 04
> **Status:** proposed

## Problem

The repo's most valuable data — which package version is malicious, which domain
is C2, which file hash to grep for — exists only as prose inside advisory bodies.

That has three consequences.

**Nothing downstream can use it.** The site publishes `advisories.json` and
`api/v1/advisories.json`, but those carry only document metadata: id, title,
severity, status, dates, ecosystems, tools, tags, URLs. A tool asking "is
`chalk@5.6.1` in your corpus?" cannot answer from the API. It has to fetch 107
markdown files and parse English.

**Prose scraping is actively wrong, not just inconvenient.** An advisory body
contains both `webhook.site` (attacker C2) and `socket.dev` (a cited source),
formatted identically. Any regex that harvests domains harvests both. Publishing
a feed built that way would put legitimate security vendors' domains into other
people's blocklists.

**The same fact gets restated inconsistently.** A package version appears in the
`## Am I affected?` grep command, again in the prose, and sometimes again in a
table — three chances to typo, no mechanism to catch a mismatch.

The repo already recognises this. BACKLOG.md carries three related items, all
marked _(high)_: structured IOC frontmatter, an OSV-format export, and a
consolidated `iocs.json`. It also carries a fourth, `integrity.txt`, under "make
the site itself verifiable." All four are the same architectural change: **make
frontmatter the validated source of truth, then fan out.**

## Proposal

```
advisories/*.md  ──►  validated frontmatter  ──┬──►  iocs.json / .ndjson / .csv
   (source)              (single truth)        ├──►  osv/<id>.json + osv/all.zip
                                               ├──►  advisories.json (enriched)
                                               └──►  search.json (Spec 04)

                        every dist/ file       ──►  integrity.txt (SHA-256 manifest)
```

Four deliverables. Deliverable 1 is the enabler; 2–4 are independent fan-outs and
can ship in any order once it lands.

---

## Deliverable 1 — Structured IOC frontmatter

### Schema

Three new optional top-level keys. All arrays; all omitted when empty rather than
present-and-empty, so the diff on an advisory with no IOCs is zero.

```yaml
affected_packages:
  - ecosystem: npm            # npm | pypi | crates | vscode | golang | rubygems | maven | nuget
    name: "@scope/pkg"
    purl: "pkg:npm/%40scope/pkg"
    bad_versions: ["5.6.1", "5.6.2"]
    fixed: "5.6.3"            # optional — omit if no fixed version exists

iocs:
  - type: domain              # domain | ipv4 | ipv6 | sha256 | url | npm-account | github-account | email | wallet
    value: "example-c2.invalid"
    note: "exfil endpoint, live 2025-09-08 to 2025-09-11"   # optional

cves: ["CVE-2026-30615"]
cwes: ["CWE-506"]
cvss: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"        # vector string, not a bare score
```

**Why `cvss` is a vector string, not a number.** A bare `9.8` loses the
attack-vector detail that lets a reader decide whether it matters to them, and
different scorers disagree on the number while agreeing on the vector. Store the
vector; derive the score for display if wanted.

**Why `note` on IOCs.** An indicator without a time window is a landmine — the
domain that was C2 in September may be a parked domain or a legitimate service by
March. The note field is where the temporal caveat lives, and the export carries
it through.

### purl gotchas

These are the two that will bite, and both should be enforced by test rather than
by review:

- **npm scopes.** The `@` in a scoped name percent-encodes to `%40`:
  `@tanstack/react-router` → `pkg:npm/%40tanstack/react-router`. A raw `@` in the
  purl is the single most common error.
- **PyPI normalisation.** Names lowercase, and `_` and `.` normalise to `-`:
  `Django_Rest` → `pkg:pypi/django-rest`.

Rather than have authors hand-write purls and hope, generate the purl from
`ecosystem` + `name` in the build and *validate* any hand-written one against the
generated form. That turns a class of silent data errors into a test failure.

### Schema and validation

Add all five keys to `build_advisory_schema()`
([site/build.py:1043](../../site/build.py)) as optional properties with `"type":
"array"` and per-item `properties`. Keep `additionalProperties: true` — external
consumers depend on being able to ignore what they don't know.

### Tests

New file `tests/test_iocs.py`:

```python
def test_purl_matches_ecosystem_and_name(parsed_advisories):
    """A hand-written purl must agree with the canonical form for its ecosystem."""
    for path, fm, _ in parsed_advisories:
        for pkg in fm.get("affected_packages", []):
            if "purl" not in pkg:
                continue
            expected = canonical_purl(pkg["ecosystem"], pkg["name"])
            assert pkg["purl"] == expected, (
                f"{path.name}: purl {pkg['purl']!r} != canonical {expected!r}"
            )


def test_npm_scoped_purls_are_encoded(parsed_advisories):
    """The @ in a scoped npm name must be %40 in the purl."""
    for path, fm, _ in parsed_advisories:
        for pkg in fm.get("affected_packages", []):
            purl = pkg.get("purl", "")
            assert "@" not in purl.split("?")[0].removeprefix("pkg:"), (
                f"{path.name}: unencoded '@' in purl {purl!r} — scopes use %40"
            )


def test_ioc_values_are_defanged_consistently(parsed_advisories):
    """Either all C2 indicators are defanged or none are — pick one and hold it."""
    ...


def test_bad_versions_are_strings(parsed_advisories):
    """YAML will happily parse 5.60 as a float and silently lose the trailing zero."""
    for path, fm, _ in parsed_advisories:
        for pkg in fm.get("affected_packages", []):
            for v in pkg.get("bad_versions", []):
                assert isinstance(v, str), (
                    f"{path.name}: version {v!r} parsed as {type(v).__name__} — quote it"
                )
```

That last test is not hypothetical. Unquoted `5.60` in YAML becomes the float
`5.6`, and the advisory then names a version that doesn't exist.

### A decision this spec does not make

**Defanging.** Whether `evil.example.com` is stored as-is or as
`evil[.]example[.]com` is a real fork:

- *Stored raw* — directly usable in a grep or a blocklist import, no
  post-processing. But the published `iocs.json` then contains live-ish malicious
  domains in clickable form, and some corporate proxies will flag the file itself.
- *Stored defanged* — safe to publish and display, but every consumer must
  refang, and inconsistent refanging is its own bug source.

**Recommendation: store raw, defang at render time.** The machine-readable
exports are the product here, and their whole value is being usable without
post-processing; the HTML page can defang for display. But this is a judgment
call the maintainer should make explicitly, because reversing it later means
rewriting every advisory. The test above enforces whichever choice is made.

### Rollout

Same pattern as Spec 01: optional, front-load new advisories, back-fill by batch.
Prioritise back-filling advisories that name a concrete `package@version` — those
are the ones the OSV export needs, and they are roughly a third of the corpus.
Agent/MCP incidents and CVE-only entries can stay minimal.

---

## Deliverable 2 — `iocs.json` (+ `.ndjson`, `.csv`)

One record per indicator, not per advisory. This is the join-friendly shape: a
consumer greps a lockfile and wants a row back, not a document.

```json
{
  "generated": "2026-08-03",
  "indicators": [
    {
      "type": "purl",
      "value": "pkg:npm/chalk@5.6.1",
      "advisory_id": "2025-09-qix-compromise",
      "url": "https://pranava0x0.github.io/vibe-coding-security/advisories/2025-09-qix-compromise.html",
      "first_seen": "2025-09-08",
      "severity": "critical",
      "attack_class": "package-supply-chain",
      "tags": ["supply-chain", "npm"],
      "note": null
    }
  ]
}
```

Emit three encodings from one in-memory list:

- `iocs.json` — the full document, for anything that wants to load it whole.
- `iocs.ndjson` — one indicator per line, for `jq`/stream processing and for
  consumers who don't want to hold 107 advisories' worth of indicators in memory.
- `iocs.csv` — for spreadsheet and SIEM import, which is a real workflow and
  badly served by JSON.

`first_seen` derives from the advisory's `date_disclosed`. `attack_class` comes
from Spec 01 — if Spec 01 hasn't landed, omit the key rather than blocking.

**Sort deterministically** — by `(type, value, advisory_id)`. Two builds of
unchanged source must produce identical bytes; see the determinism note in the
overview.

Add to `validate.py`: assert `iocs.json` exists, parses, and that every
`advisory_id` in it resolves to a real advisory.

---

## Deliverable 3 — OSV export

Emit `dist/osv/<id>.json` per advisory plus `dist/osv/all.zip`, in
[OSV schema](https://ossf.github.io/osv-schema/) format. This is what makes the
corpus visible to OSV-Scanner and to everything downstream of osv.dev, without
anyone installing anything of ours.

### Scope

**Only advisories with at least one `affected_packages` entry that has
`bad_versions`.** An OSV record with no affected package is not useful to a
scanner and clutters the feed. Agent-runtime and prompt-injection advisories with
no package artifact stay out — they are real and important, but OSV is not their
distribution channel.

Expect this to cover roughly a third of the corpus initially and to grow as
back-fill proceeds.

### Mapping

| OSV field | Source |
|---|---|
| `id` | `VCS-<advisory-id>` — prefixed so it never collides with GHSA/CVE/PYSEC namespaces |
| `aliases` | `cves` frontmatter |
| `summary` | advisory `title` |
| `details` | the `## TL;DR` section, extracted via the existing `_extract_section()` helper ([site/build.py:904](../../site/build.py)) |
| `published` | `date_disclosed` |
| `modified` | `last_updated` |
| `affected[].package` | `{ecosystem, name, purl}` from `affected_packages` |
| `affected[].versions` | `bad_versions` |
| `affected[].ranges` | derived from `fixed` when present |
| `severity` | `cvss` vector, as `[{"type": "CVSS_V3", "score": "<vector>"}]` |
| `references` | advisory HTML URL (`WEB`) + the `## Sources` links (`ARTICLE`) |
| `database_specific` | `attack_class`, `tags`, `status` — the fields OSV has no home for |

**`date_disclosed` may be partial.** The schema permits `YYYY` and `YYYY-MM`
([site/build.py:1043](../../site/build.py)), but OSV requires an RFC3339
timestamp. Normalise partials to the first of the period (`2025` → `2025-01-01T00:00:00Z`)
and note in `database_specific` that the date was imprecise — silently inventing
a precise date is worse than saying so.

### Registration

Registering as an [OSV.dev data source](https://google.github.io/osv.dev/data/)
is a separate, outward-facing step: it publishes this data into an ecosystem-wide
index that many tools consume automatically, and it is not easily undone.

**Do not submit as part of this spec's implementation.** Ship the export, let it
run for a few sweeps, confirm the records are clean and stable, then raise
registration with the maintainer as an explicit decision. The technical work and
the publishing decision are separable and should stay separate.

### Tests

New `tests/test_osv.py`: every emitted record validates against the OSV schema;
every `id` is unique and `VCS-`-prefixed; `all.zip` contains exactly the emitted
records; every advisory with `bad_versions` has a record and every advisory
without one does not.

---

## Deliverable 4 — `integrity.txt`

The smallest item here and the most on-theme: a site that tells people to verify
what they download should let people verify what they download from it.

```
# SHA-256 of every file published at this build.
# Verify:  sha256sum -c integrity.txt
<hash>  advisories/2025-09-qix-compromise.html
<hash>  advisories.json
...
```

Written **last** in `main()` ([site/build.py:1101](../../site/build.py)), after
every other output exists, covering every file under `dist/` except itself.
Sorted by path for determinism.

Add to `validate.py`: every file in `dist/` except `integrity.txt` appears in the
manifest, and every hash matches. That check catches an emitter that writes a
file after the manifest — the one failure mode this feature has.

Link it from the site footer or `security.html` so it's discoverable, and
document the one-line verification command.

**Honest framing.** This proves integrity against accidental corruption and
transport-layer tampering. It is not build provenance — anyone who can change the
site can change the manifest. Say so on the page rather than implying more than
it delivers.

---

## Done when

- [ ] `affected_packages`, `iocs`, `cves`, `cwes`, `cvss` in the schema, optional.
- [ ] `tests/test_iocs.py` with purl-canonicalisation, npm-scope-encoding,
      string-version, and defang-consistency tests.
- [ ] Defanging decision made and written down in this spec.
- [ ] `iocs.json` + `.ndjson` + `.csv` emitted, deterministically sorted,
      validated.
- [ ] `dist/osv/<id>.json` + `all.zip` for every advisory with `bad_versions`;
      `tests/test_osv.py` green.
- [ ] `integrity.txt` written last, complete, verified by `validate.py`.
- [ ] Back-fill started on package-bearing advisories.
- [ ] `build.py` → `validate.py` → `pytest` all green.

## Explicitly out of scope

- **Submitting to osv.dev.** Deliberately deferred — see Deliverable 3.
- Full corpus back-fill. Incremental, tracked by ratchet as in Spec 01.
- Signing the manifest. `integrity.txt` is hashes only; signatures are a separate
  question with real key-management consequences.
- The client-side lockfile checker from BACKLOG.md. It consumes `iocs.json` and
  becomes easy once this lands, but it is Spec 04-adjacent frontend work.
