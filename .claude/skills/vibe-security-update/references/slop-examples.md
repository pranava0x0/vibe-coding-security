# Slop examples: before and after

Read this before writing any advisory or `ALERTS.md` entry. Append a pair each
time review or the owner finds slop, and add a matching line to
`tools/slop_patterns.tsv` when the shape can be matched by a regex. Newest on top.

## 2026-11-20 (sweep self-review)

**Sentence about the file's own history** (PHP advisory, Update)
- Before: "The first version of this file counted eight records and missed it."
- After: "This file listed eight records on 2026-11-19."
- Why: the reader needs the dated fact, not an account of the mistake. Pattern `file-version-meta`.

**Explanation the source does not give** (MCP batch, Jupyter rows)
- Before: "The two ratings differ because CVE-2026-77318 needs network reach to the server and CVE-2026-77359 needs only a web page."
- After: cut. The table prints each rating.
- Why: the vectors do not support the stated reason. No regex matches this shape, so check every "because" against the fetched text.

## 2026-11-17 (owner review)

**Aside about a source's business and independence** (Optimizely advisory, Sources)
- Before: "The reports draw on each other and on the same urlscan captures, and Report URI sells script monitoring, which its post promotes."
- After: cut. "Three researcher reports, read 2026-11-16. No vendor statement exists."
- Why: it tells the reader nothing to check or do, insinuates bias without evidence, and packs three ideas into one sentence.

**Note about this file's own reasoning** (Optimizely advisory, Prevention)
- Before: "Subresource Integrity cannot pin a snippet that the vendor rebuilds on every project change. This is this file's note, not the sources'."
- After: "Subresource Integrity cannot pin a snippet that the vendor rebuilds on every project change."

**Inference written as meta** (Fireworks advisory)
- Before: "This file reads it as the incident tracked here because the vendor, the data type and the 2026-11-03 disconnection fit, and that link is this file's inference."
- After: "No source ties the notice to this incident. The vendor, the data type and the 2026-11-03 disconnection match."

**Opener and moral** (Ray, Strapi, Next.js advisories)
- Before: "It is worth noting explicitly because ..." / "... and the lesson is the same: the CMS ..."
- After: state the fact. "Binding to localhost and checking the User-Agent do not stop an attacker who works through the victim's browser."

**Long alert with no citation** (`ALERTS.md`, median entry 96 words, 7 of 440 cited)
- Before: five or six sentences restating the advisory, no source link, the only link the `→` line.
- After: three sentences, at most 50 words, the primary source linked inline: "[Report URI](https://blog.report-uri.com/...) found attacker code in 188 Optimizely Web snippets from 178 organisations on 2026-11-16. ... Audit every project's Project JavaScript and rotate Optimizely credentials."

**Relative dates**
- Before: "last week", "today's three releases", "a month ago".
- After: the YYYY-MM-DD date or the month.
