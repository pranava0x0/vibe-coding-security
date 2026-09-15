# Sweep query list

> The literal search strings a sweep runs, and nothing else. This is the only
> file in this skill that may be handed to a delegated agent.

**Purpose of this file.** This project maintains a public index of
already-disclosed security advisories relevant to people building with AI
coding tools. The work is reading published disclosures and summarising them
for defenders. Running these searches means finding *coverage* of incidents —
vendor advisories, CVE records, researcher write-ups — not finding, testing, or
interacting with vulnerable systems.

**Why the annotations live elsewhere.** Every "why we run this query and what
to look for" note was moved to [`triage-patterns.md`](triage-patterns.md). Two
reasons, and they point the same way:

1. Those notes are ~25KB of attack-technique detail (C2 mechanics, install-time
   execution primitives, control-bypass specifics). Delivered to a fresh agent
   as one numbered task list with no surrounding context, that reads like
   offensive tasking, and Sonnet 5's cyber-safeguards classifier flagged it
   eight times across five consecutive days (2026-08-13 → 08-17). See
   [`../LEARNINGS.md`](../LEARNINGS.md).
2. They are triage/write-up material anyway. The agent *running a search* has
   no use for them; the session *writing the advisory* does.

`{year}` = the current year. Substitute before searching.

---

## Tier A — deep (24-hour window)

Aim for ~12 parallel `WebSearch` calls.

1. `npm supply chain attack {year}`
2. `malicious npm package compromise {year}`
3. `malicious mcp server {year}`
4. `Cursor vulnerability CVE {year}`
5. `Claude Code vulnerability prompt injection {year}`
6. `Lovable Bolt v0 Replit security {year}`
7. `AI coding assistant security incident {year}`
8. `PyPI malicious package supply chain {year}`
9. `malicious crate crates.io supply chain {year}`
10. `supply chain attack .cursorrules CLAUDE.md AI agent config {year}`
11. `AI agent framework CVE {year}` — rotate one framework per sweep from the
    Agent SDK list below
12. `AI tool OAuth supply chain breach {year}`
13. `AI agent infrastructure platform breach {year}`
14. `React Server Components RSC RCE vulnerability CVE {year}`
15. `binding.gyp node-gyp supply chain npm malicious {year}`
16. `Telegram bot developer PyPI backdoor supply chain {year}`

Prepend the top sources from `source-priorities.top.json` via `allowed_domains`
on rotating subsets, so high-signal pages aren't buried under news aggregators.

## Tier B — medium (3-day window)

~4–8 parallel calls, weighted to top sources.

1. `{top-3-source-domains} supply chain`
2. `GitHub Advisory Database npm critical`
3. `Shai-Hulud OR mini-shai-hulud cross-ecosystem npm pypi {year}`
4. `{vendor} security advisory {year}` — rotate from the vendor lists below
5. `{vendor} coordinated security release {year}`
6. `Claude.ai prompt injection vulnerability {year}`
7. `npm dependency confusion internal scope {year}`
8. `Supabase RLS misconfiguration exposed data {year}`
9. `{ecosystem} security response team supply chain {year}`
10. `{framework} CVE {year}` — direct per-framework CVE queries; these surface
    advisory-database-only CVEs that never get blog coverage
11. `{agent} auto mode OR autonomous mode prompt injection {year}` — agent
    "auto"/"yolo"/"full-access" modes are where classifier-bypass chains land;
    the researcher blogs below publish these before any outlet picks them up
12. `{vendor threat-intel blog} AI agent OR agentic {year}` — rotate GTIG,
    Microsoft Threat Intelligence, Unit 42, Mandiant, Anthropic threat reports.
    Telemetry reports name packages, paths, and tools with no CVE attached.

**Fetch directly, don't search for:** CISA's KEV catalog is a JSON feed at
`https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`.
Filter by `dateAdded >= t_7d`. One request, authoritative, no aggregator
paraphrase. Run it every sweep.

## Tier C — shallow (7-day window)

~5 parallel calls for slower-moving stories.

1. `vibe coding security incident week {year}`
2. `AI agent CVE OR security disclosed {year}`
3. `vibe coding security site:substack.com OR site:x.com OR site:bsky.app {year}`
4. `AI agent security arxiv {year}`
5. `supply chain attack AI arxiv preprint {year}`
6. `malicious VS Code extension {year}` / `Open VSX malicious extension`
7. `{agent} skills marketplace malicious {year}`
8. `{corporate parent} security bulletin {AI product} {year}` — rotate IBM
   (Langflow, ContextForge), NVIDIA (NemoClaw, OpenShell, NIM), Microsoft,
   Google, Salesforce; the parent's PSIRT page is where the batch lands

---

## Rotation lists

Rotate a different subset each sweep; the lists are a floor, not a ceiling.

- **IDEs / agents:** Cursor, Anthropic (Claude Code), Windsurf, Google
  (Antigravity), Cline, aider, OpenHands, OpenClaw
- **Vibe-coding platforms:** Lovable, Bolt, v0, Replit, Base44
- **Web frameworks:** Vercel (Next.js), React/Meta, Svelte, Tailwind, Vite,
  Shadcn UI, Nuxt/Vue, Astro (shares `sharp`/`libheif` with Next.js)
- **Self-hosted AI gateways / routers:** OmniRoute, LiteLLM, Bifrost, Portkey,
  OpenRouter-class proxies — a gateway holds every provider key
- **Backend / auth / DB:** Supabase, Prisma, NextAuth.js / Auth.js, FastAPI,
  Streamlit, Google AI Studio SDK, Google Agent Studio, better-auth, Lucia,
  Clerk, Casdoor
- **RAG ingestion layers:** unstructured, langchain-community loaders,
  LlamaIndex readers — a URL the model chooses becomes a server-side fetch
- **Agent SDKs:** Microsoft (Semantic Kernel), LangChain / LangGraph, PraisonAI,
  Langflow, aider, OpenHands, SWE-agent, Cline
- **Workflow automation / iPaaS:** n8n, Zapier, Make, Pipedream, Temporal
- **Agent-platform / connector brokers:** Composio, LangSmith, Smithery,
  AgentOps, Portkey, Helicone, OpenRouter
- **Cloud dev environments:** Coder, GitHub Codespaces, Gitpod, DevPod
- **AI-adjacent third parties (OAuth pivot):** Context.ai, Granola, Otter
- **Extension marketplaces:** VS Code Marketplace, Open VSX, Cursor / Windsurf
  extension stores
- **Agent skill / plugin marketplaces:** ClawHub, Claude Code skills, MCP
  registries

## Primary-source domains worth querying directly

- **Ecosystem security teams:** `blog.rust-lang.org`, `blog.pypi.org`,
  `github.blog/changelog`, `blog.golang.org`, RubyGems, Packagist
- **Advisory databases:** `github.com/advisories`, GitLab Advisory DB, NVD,
  CISA KEV, `advisory.splunk.com`, `spring.io`
- **Industry security blogs:** Anthropic, OpenAI, Google (Project Zero /
  Security Blog), Microsoft MSRC, AWS, Cloudflare, Red Hat, Databricks,
  Salesforce, Oracle
- **Vendor threat-intelligence reports (distinct from advisory pages):**
  `cloud.google.com/blog/topics/threat-intelligence` (GTIG — the 2026-09-08
  adversarial-AI report named trojanized MCP packages and `.claude/`/`.cursor/`
  persistence paths), Microsoft Threat Intelligence, `unit42.paloaltonetworks.com`,
  Mandiant, `gambit.security` (ransomware-affiliate AI-tool abuse from recovered
  operator infrastructure)
- **CNAs that are research firms:** `vulncheck.com/advisories`,
  `zerodayinitiative.com/advisories`, `research.jfrog.com/vulnerabilities` —
  for small AI-tool vendors with no GHSA channel, the CNA's own advisory is the
  independent second source (DeepSeek Harness CVE-2026-82533; Langflow
  CVE-2026-0768 was a ZDI 0-day advisory; Bifrost CVE-2026-90898 a JFrog one)
- **Auth-SDK advisory tabs (walk every cycle):** `clerk/javascript`,
  `better-auth/better-auth`, `nextauthjs/next-auth`, `supabase/auth` under
  `github.com/<org>/<repo>/security/advisories` — Clerk's CVSS 9.1 middleware
  bypass (CVE-2026-41248) sat five months unseen by `{framework} CVE` queries.
- **Advisory-database listings (fetch every sweep):**
  `github.com/advisories?query=mcp+sort%3Apublished-desc` and
  `github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical`
  (and `ecosystem%3Apip`). The reviewed lists omit CVE-only entries (Casdoor,
  Bifrost), so run the `mcp` recency list too.
- **Google Cloud release-notes feeds:**
  `docs.cloud.google.com/feeds/<product>-release-notes.xml` — customer-action
  security fixes (Agent Studio `/api-proxy` SSRF, 2026-07-20) appear only there.
- **Ecosystem security-team blogs (authoritative, may non-attribute):**
  `blog.rubygems.org` (Ruby Central), `blog.pypi.org`, `github.blog/changelog`
  — for a registry-abuse / mass-spam-publishing campaign these are the
  registry's own post-incident record and count as the independent second
  source even when they decline to attribute the activity to AI (RubyGems'
  2026-09-11 GemStuffer post named counts and fixes but would not confirm AI
  authorship the researchers asserted).
- **Rapid-reaction exploit research (KEV-adjacent, same-day):** `watchtowr.com`,
  `horizon3.ai`, `greynoise.io` (in-the-wild probing telemetry), `wiz.io` — for
  a CVSS-9/10 disclosure these publish the vulnerable endpoint, exploitation
  timing, and detection guidance within a day; pair with the NVD/vendor record.
- **Agentic-campaign primary research:** `greynoise.io` + `blackpointcyber.com`
  (the PaperCut AI-agent-swarm pair), `unit42.paloaltonetworks.com`,
  `gambit.security` — two firms on the same autonomous-agent campaign is a real
  two-source pair, not aggregator republication.
- **Corporate-parent PSIRT bulletins (the batch is the advisory):**
  `ibm.com/support/pages/node/<id>` — IBM is Langflow's CNA since the
  acquisition; its 2026-09-08 bulletin carried 11 Langflow CVEs the project's
  own advisory tab never listed. `github.com/NVIDIA/product-security` — NVIDIA's
  Markdown + CSAF mirror of every bulletin (fetch the raw `<id>.md`; the
  `nvidia.custhelp.com` HTML page returns 403). Query
  `"{parent} security bulletin {product}"` for any AI tool owned by IBM, NVIDIA,
  Microsoft, Google, Cisco or Salesforce, and grep *every* CVE the bulletin lists.
- **Vendor community-forum security posts (batch index for GHSA-only vendors):**
  `community.n8n.io` "Security update — <date>" posts enumerate each n8n batch
  (18 advisories on 2026-09-02) with severities and fixed versions; the GHSA
  index shows the same advisories one at a time with no batch grouping.
- **Hacker News via the Algolia API (works where the HN site is noisy):**
  `https://hn.algolia.com/api/v1/search_by_date?query=<one term>&tags=story&numericFilters=created_at_i>{epoch}`
  — one term per call (Boolean `OR` is not supported), filter by epoch for the
  sweep window; returns title, URL, points and comment count.
- **Vendor advisory indexes that must be paginated (bulk back-publication):**
  `github.com/openclaw/openclaw/security/advisories?page=N` — 75 advisories
  dated 2026-09-11 for fixes shipped weeks earlier, ~30 more dated 2026-06-30,
  11+ pages; `github.com/sveltejs/kit/security/advisories` — nine advisories
  Feb–Jul 2026 with no blog post, CVEs assigned by VulnCheck 2026-08-28. Walk
  every agent framework and web framework the corpus tracks, not just the
  IDE vendors, and read the *vendor's* published date, not the CVE's.
- **Cloud-vendor security bulletins for their own MCP servers:**
  `aws.amazon.com/security/security-bulletins/<year>-<nnn>-aws/` — AWS is the
  CNA for `awslabs.*-mcp-server` packages (2026-097/101/103 in one week);
  `ibm.com/support/pages/node/<id>` for ContextForge (four CVEs 2026-09-02).
- **Exploitation telemetry (post-patch mass scanning):** `f5.com/labs` — the
  2026-09-11 Vite CVE-2026-39364 report quantified a ~20× August scanning jump
  five months after the fix; pair with `greynoise.io`. A telemetry report is a
  status change (`patched` → `active`) even with no KEV entry.
- **Registry release dates as a primary source:** `npm view <pkg> time`,
  `pip index versions <pkg>` / PyPI JSON — settles whether a "fixed in X"
  claim is physically possible (OmniRoute's fix PR merged three weeks after
  the version the vendor page names as fixed).
- **Vendor patch-release trackers (fetch directly on a critical release):**
  `docs.gitlab.com/releases/patches/`, GitLab/Atlassian/JFrog release notes —
  the full CVE list in a "critical patch release" is often broader than the one
  CVE the press covers (GitLab 2026-09-10 shipped 19 CVEs behind the CVSS-10
  headline).
- **AI-credential threat intel:** `okta.com` (Jeremy Kirk) — infostealer-dump
  analysis quantifying replayable AI session tokens (Anthropic, Cursor, OpenAI)
  and the black market selling them.
- **Roundups that surface primaries (aggregators, not sources):**
  `adversa.ai/blog` monthly "top … security resources" posts,
  `labs.cloudsecurityalliance.org` CISO daily briefings — read them for the
  links, then fetch and cite the primary
- **Researcher blogs (upstream of aggregators):** 0day.click, cyata.ai,
  layerxsecurity.com, pillar.security, oasis.security, tenetsecurity.ai,
  labs.zenity.io, novee.security, danusminimus.github.io, oddguan.com,
  manifold.security (cross-vendor AI-coding-CLI pre-trust-execution findings —
  Cursor CLI worktree Aug 2026, GitSpawn Sept 2026), paddo.dev (independent
  technical follow-up/retest blog, not just restatement), embracethered.com
  (Johann Rehberger — agent prompt-injection chains; Claude Code Auto Mode
  module-shadowing, Aug 2026), itmeetsot.eu (independent replication of the
  same class via steganographic payloads)
- **AI-safety research nonprofits publishing standalone incident sites (not a
  blog post on their main domain):** `collusion.wiki` — the Nightingale
  Collective's primary report on the DSEWiki agent-collusion incident (Sept
  2026). A dedicated-domain report like this won't appear under the
  organization's own name in search results; check the article text for a
  bespoke report-site URL rather than assuming the org's main site is the
  primary source.

## Known source-access gaps

Report these as **"not covered"**, never folded into "nothing found" — a future
sweep reading the log needs to know whether a quiet category was quiet or just
unreachable.

- **X / Bluesky** — no native browsing; only search-indexed snippets.
- **`reddit.com`** — blocked for `WebFetch` in this environment.
- **`bleepingcomputer.com`, `cisa.gov` HTML pages** — return 403 (use the KEV
  JSON feed for CISA).
- **`checkmarx.com/zero-post/`** — 404.
- **`socket.dev/blog`** — index renders without dates, RSS 404s; date individual
  post pages instead.
- **arXiv API** — rate-limits (429); the HTML listing pages work.
- **`nvidia.custhelp.com`** — 403; use the `NVIDIA/product-security` GitHub mirror.
- **`securityonline.info`** — 503 on 2026-09-13; retry or cite a different secondary.
- **`msrc.microsoft.com/update-guide/vulnerability/<CVE>`** — renders as a bare
  title to `WebFetch` (client-side app); use the NVD API record for the
  description and score.
- **`techtimes.com`** — 403 on 2026-09-14.
- **`hn.algolia.com`** — an occasional non-JSON first response; retry once
  before logging it as a blocker.
- **`docs.cloud.google.com/<product>/release-notes`** — HTML is navigation
  only; use the `/feeds/<product>-release-notes.xml` feed.
- **Vendor-repo advisory URLs** sometimes 404 while `github.com/advisories/GHSA-…`
  resolves (knowns, 2026-09-15); try the database copy second.
- **`pypi.org/pypi/<pkg>/json`** — truncated by `WebFetch`; use `pip index versions`.
- **`spectrosec.com`** — 404 on 2026-09-15.

## Out of scope for this project

Stated here so it is unambiguous in the one file a delegated agent may receive:

- Do **not** connect to, scan, probe, enumerate, or test any third-party system.
- Do **not** check whether a specific named organisation is affected by anything.
- Do **not** search for, collect, or reconstruct working exploit code.

The sweep reads published disclosures. That is the whole job.
