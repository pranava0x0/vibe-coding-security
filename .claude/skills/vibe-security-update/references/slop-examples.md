# Slop examples: before and after

Read this before writing any advisory or `ALERTS.md` entry. Append a pair each
time review or the owner finds slop, and add a matching line to
`tools/slop_patterns.tsv` when the shape can be matched by a regex. Newest on top.

## 2026-11-27 (sweep review)

**"The vendor has not said" from a partial read** (1984 Hosting advisory and alert)
- Before: "Whether your data was reached is not known. The vendor has not said."
- After: "Whether your data was reached is not known. No vendor text read for this file says."
- Why: the status entry kept only its newest update and the vendor site was not opened. No regex matches this shape, so scope every "has not said" to the texts read.

**Example list widened** (Airflow advisory, Am I affected?)
- Before: "A Dag that feeds tickets, emails, web pages or documents to `@task.llm` or `@task.agent` meets the record's second case."
- After: "A Dag that feeds tickets or downloaded documents ... meets the record's second case. Emails and web pages are the same kind of input."
- Why: the record gives two examples, and the draft printed four as the record's.

**Condition dropped from a table cell** (reference MCP servers advisory)
- Before: "`git_show` can read objects from a second repository outside `--repository`, through a race."
- After: the same, plus "Needs a file-write tool on the same repository and a known object id."
- Why: the advisory states both conditions, and the cell read as if `git_show` alone were enough.

## 2026-11-26 (sweep review)

**Step the vendor does not give, written as an instruction** (Kiro Web alert, MCP batch, Rackspace Spot)
- Before: "It is fixed service-side. Review sessions from that window that read untrusted content."
- After: "It is fixed service-side and AWS asks for no action. As a caution, review sessions from that window."
- Why: the vendor asks for nothing, and the alert dropped that. No regex matches this shape, so mark each step that goes beyond the source.

**Example list read as a limit** (Kiro Web advisory)
- Before: 'Per the bulletin, the content could be "a repository file or a web page".'
- After: 'Per the bulletin, the content is anything the session read, "such as a repository file or a web page".'
- Why: the quotation cut "such as", which turned two examples into the whole scope.

**Verb stronger than the source** (Rackspace Spot title)
- Before: "intruders read Kubernetes Secrets and API tokens"
- After: "intruders gained access to Kubernetes Secrets"
- Why: the notification says they "could have read" them.

## 2026-11-25 (sweep review)

**Advice wider than the vendor's scope** (Todoist advisory, Am I affected?)
- Before: "You are exposed beyond Todoist if you ever wrote an API key, access token or recovery phrase into a task or comment."
- After: "If the email says your content matched the searches, treat every credential in your tasks and comments as read. Todoist says the searches covered one database shard."
- Why: "ever" covered every user, and the notice limits the searches to one shard and the emailed accounts. No regex matches this shape, so check each "if you ever" against the vendor's stated scope.

**Quotation closed where the source goes on** (T3 Code advisory)
- Before: 'Its description says: "T3 Code's analytics read ... at server boot."'
- After: 'Its description says T3 Code's analytics "read ... at server boot" and sent hashes of the ids it found.'
- Why: the source sentence continues, so the full stop inside the quotation marks was not the source's.

## 2026-11-24 (sweep review)

**One page's wording applied to six** (mcp-server-git advisory)
- Before: "The pages share one precondition. A repository with an attacker-written `.git` directory has to reach the disk through an archive, a CI artifact, a shared folder, a vendored tree or a copied workspace."
- After: "Five of the six pages name a delivery path. GHSA-pm7p-vphh-2cg7 lists an archive, a CI artifact, a shared folder, a vendored tree or a copied workspace. GHSA-8wv7-r664-7594 names no delivery path."
- Why: "share" was not checked page by page. No regex matches this shape, so attribute each condition to an id.

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
