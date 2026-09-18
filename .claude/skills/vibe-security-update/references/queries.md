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

Bare pointers. The *why* for each lives in `triage-patterns.md` and `LEARNINGS.md`.

- **Ecosystem security teams:** `blog.rust-lang.org`, `blog.pypi.org`, `github.blog/changelog`,
  `blog.golang.org`, `blog.rubygems.org`, Packagist — the registry's own post-incident post is the
  authoritative second source for a registry-abuse campaign, even when it declines to attribute.
- **Advisory databases:** `github.com/advisories`, GitLab Advisory DB, NVD (use the API,
  `services.nvd.nist.gov/rest/json/cves/2.0?cveId=`), CISA KEV JSON, `advisory.splunk.com`, `spring.io`.
- **Advisory-database listings (fetch every sweep):**
  `github.com/advisories?query=mcp+sort%3Apublished-desc`,
  `…?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical`, `…ecosystem%3Apip…` — the reviewed
  lists omit CVE-only entries, so run the `mcp` recency list too.
- **Advisory-database package queries (for products whose own tab is empty):**
  `github.com/advisories?query=crewai`, `…?query=kiro`, `…?query=rmcp`, `…?query=vm2` — CVE-only
  entries from research CNAs (ZDI, VulnCheck) and corporate CNAs (AWS, IBM) never reach the vendor tab.
- **Per-product advisory tabs (`github.com/<org>/<repo>/security/advisories`, paginate):** Claude Code,
  Cursor, Cline, goose, OpenHands, SWE-agent, aider, Codex, gemini-cli, OpenClaw (11+ pages),
  n8n, Langflow, Flowise, PraisonAI, LiteLLM, LangChain, LangGraph, Semantic Kernel, Coder, MCP
  TS/Python SDKs, vm2; web: Next.js, React, Svelte, SvelteKit, Vite, Astro; **auth SDKs:**
  `clerk/javascript`, `better-auth/better-auth`, `nextauthjs/next-auth`, `supabase/auth`;
  backend: FastAPI, Prisma, Streamlit, `googleapis/python-genai`. Read the vendor's date, not the CVE's.
- **CNAs that are research firms:** `vulncheck.com/advisories`,
  `zerodayinitiative.com/advisories/published/` (AI-tool 0-days publish here first; the index's ZDI
  numbers can be off by one from the URLs — open the page and read the id),
  `research.jfrog.com/vulnerabilities`.
- **Corporate-parent / cloud-vendor bulletins (the batch is the advisory):**
  `ibm.com/support/pages/node/<id>` (Langflow, ContextForge); `github.com/NVIDIA/product-security`
  (raw `<id>.md`; `nvidia.custhelp.com` 403s); `aws.amazon.com/security/security-bulletins/` (Kiro,
  Amazon Q, `awslabs.*` MCP servers, Security Agent); `community.n8n.io` "Security update — <date>".
- **Industry security blogs:** Anthropic, OpenAI, Google Security/Project Zero, MSRC, AWS, Cloudflare,
  Red Hat, Databricks, Salesforce, Oracle.
- **Vendor threat-intel and incident reports:** `cloud.google.com/blog/topics/threat-intelligence`
  (GTIG), Mandiant reports (landing pages truncate — read via several outlets), Microsoft Threat
  Intelligence, `unit42.paloaltonetworks.com`, `gambit.security`, Anthropic threat reports,
  `alignment.openai.com/misalignment-reports/` (OpenAI internal-model incidents).
- **Google Cloud release-note feeds:** `docs.cloud.google.com/feeds/<product>-release-notes.xml`.
- **Rapid-reaction / telemetry:** `watchtowr.com`, `horizon3.ai`, `greynoise.io`, `wiz.io`,
  `f5.com/labs`, `blackpointcyber.com`, `okta.com` (AI-token infostealer analysis).
- **Vendor patch trackers:** `docs.gitlab.com/releases/patches/`, Atlassian, JFrog release notes.
- **Registry records:** `npm view <pkg> time`, `registry.npmjs.org/<pkg>` (`0.0.1-security` =
  takedown marker), `pip index versions <pkg>`, PyPI JSON via curl.
- **Hacker News (Algolia):**
  `hn.algolia.com/api/v1/search_by_date?query=<one term>&tags=story&numericFilters=created_at_i%3E{epoch}`
  — one term per call, `>` URL-encoded.
- **Roundups that surface primaries:** `adversa.ai/blog`, `labs.cloudsecurityalliance.org`.
- **Researcher blogs:** 0day.click, cyata.ai, layerxsecurity.com, pillar.security, oasis.security,
  tenetsecurity.ai, labs.zenity.io, novee.security, danusminimus.github.io, oddguan.com,
  manifold.security, paddo.dev, embracethered.com, itmeetsot.eu, forever.security, socket.dev,
  stepsecurity.io, aikido.dev, safedep.io.
- **Standalone incident sites from research nonprofits:** `collusion.wiki`, `rubyhack.ai`.
- **Regulators:** `aepd.es` (first GDPR notification for an attack executed by an AI agent).

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
  before logging it as a blocker. Also URL-encode `>` in `numericFilters` as
  `%3E` or every term returns non-JSON.
- **`docs.cloud.google.com/<product>/release-notes`** — HTML is navigation
  only; use the `/feeds/<product>-release-notes.xml` feed.
- **Vendor-repo advisory URLs** sometimes 404 while `github.com/advisories/GHSA-…`
  resolves (knowns, 2026-09-15); try the database copy second.
- **`pypi.org/pypi/<pkg>/json`** — truncated by `WebFetch`; use `pip index versions`.
- **`spectrosec.com`** — 404 on 2026-09-15.
- **`github.blog/changelog/label/security/`** — 404 on 2026-09-17; use the main changelog.
- **`cloud.google.com/security/resources/<report>`** — Mandiant report pages are
  landing pages whose body truncates; read the report through several outlets
  and label which case study each describes.
- **`openai.com/index/model-misalignment-reporting-framework`** — 403; the
  reports themselves at `alignment.openai.com` fetch fine.
- **`bbc.co.uk` / `bbc.com`** — blocked for `WebFetch`.
- **`cybernews.com`, `scworld.com`** — 403 on 2026-09-17.
- **`vulncheck.com/advisories/<slug>`** — some per-CVE pages 404 while the index
  lists them (three of six vm2 CVEs on 2026-09-17); cite the index and say so.

## Out of scope for this project

Stated here so it is unambiguous in the one file a delegated agent may receive:

- Do **not** connect to, scan, probe, enumerate, or test any third-party system.
- Do **not** check whether a specific named organisation is affected by anything.
- Do **not** search for, collect, or reconstruct working exploit code.

The sweep reads published disclosures. That is the whole job.
