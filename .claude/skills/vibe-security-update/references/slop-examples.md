# Slop examples: before and after

Read this before writing any advisory or `ALERTS.md` entry. Append a pair each
time review or the owner finds slop, and add a matching line to
`tools/slop_patterns.tsv` when the shape can be matched by a regex. Newest on top.

## 2026-11-23 (sweep self-review)

**Relative duration where two dates do the job** (LiteLLM advisory)
- Before: "The fixed version is eight weeks older than the advisory."
- After: "The fixed release predates the advisory. PyPI shows 1.103.0 uploaded 2026-09-27."
- Why: the reader needs the two dates, and the subtraction was done by hand. No regex matches this shape.

## 2026-11-22 (sweep self-review)

**Generalisation no source states** (Ghostscript advisory, Am I affected?)
- Before: "Many images install Ghostscript as a dependency of ImageMagick or a PDF tool."
- After: "List the packages in each image before assuming Ghostscript is absent. pwn.ai notes that the official Paperless-ngx image includes it."
- Why: "many" was not counted and no fetched page says it. No regex matches this shape, so check every quantifier against the fetched text.

## 2026-11-21 (sweep self-review)

**Instruction about paperwork** (MONAI Label advisory, If you are affected)
- Before: "Do not write "upgraded" in a ticket. There is no fixed release to upgrade to."
- After: "There is no fixed release to upgrade to."
- Why: the reader acts on the server, not on a ticket. Pattern `paperwork-aside-2026-11-21-monai`.

**Explanation the source does not give** (NLTK advisory)
- Before: "The 9.8 assumes the attacker supplies the argument, and most of the other 30 are denial of service or need local access."
- After: "Both paths in the critical advisory need a caller-supplied argument, and the database rates the other 30 high or moderate."
- Why: "assumes" and "most" were not counted or stated anywhere. No regex matches this shape.

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
