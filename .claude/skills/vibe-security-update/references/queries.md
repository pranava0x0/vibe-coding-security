# Sweep query list

> The literal search strings a sweep runs, and nothing else. This is the only
> file in this skill that may be handed to a delegated agent.

**Purpose of this file.** This project maintains a public index of
already-disclosed security advisories relevant to people building with AI
coding tools. The work is reading published disclosures and summarising them
for defenders. Running these searches means finding *coverage* of incidents —
vendor advisories, CVE records, researcher write-ups — not finding, testing, or
interacting with vulnerable systems.

**Why the annotations live elsewhere.** The "why we run this query" notes are in
[`triage-patterns.md`](triage-patterns.md): handed to a fresh agent they read like
offensive tasking (classifier trips 2026-08-13 → 08-17; [`../LEARNINGS.md`](../LEARNINGS.md) §1),
and they are write-up material anyway.

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

Prepend top sources from `source-priorities.top.json` via `allowed_domains` on rotating subsets.

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
10. `{framework} CVE {year}` — surfaces advisory-database-only CVEs
11. `{agent} auto mode OR autonomous mode prompt injection {year}` — researcher blogs publish these first
12. `{vendor threat-intel blog} AI agent OR agentic {year}` — rotate GTIG, Microsoft TI, Unit 42, Mandiant, Anthropic
13. `{agent} plugin OR skill marketplace vulnerability {year}` — rotate Claude Code, Codex, Copilot, Gemini CLI/Antigravity, OpenClaw
14. `{platform} AI autofix OR coding agent handoff vulnerability {year}` — rotate Sentry, Datadog, Copilot Autofix, Linear, PagerDuty

**Fetch directly, every sweep:** CISA KEV JSON at
`https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`, filtered by `dateAdded >= t_7d`.

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
  `blog.golang.org`, `blog.rubygems.org`, Packagist (LEARNINGS §17).
- **Advisory databases:** `github.com/advisories`, GitLab Advisory DB, NVD (use the API,
  `services.nvd.nist.gov/rest/json/cves/2.0?cveId=`), CNA records `cveawg.mitre.org/api/cve/<id>` (title and description can disagree), CISA KEV JSON, `advisory.splunk.com`, `spring.io`.
- **Advisory-database listings (fetch every sweep):**
  `github.com/advisories?query=mcp+sort%3Apublished-desc`,
  `…?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical`, `…ecosystem%3Apip…` — the reviewed
  lists omit CVE-only entries, so run the `mcp` recency list too.
- **Front pages, fetched before any search:** `thehackernews.com`, `securityweek.com`,
  `theregister.com/security/` — dated headlines; fetch and cite the article (LEARNINGS §28).
- **THN weekly roundup** (`thehackernews.com/2026/MM/threatsday-….html`): grep every item against the corpus (§33).
- **NVD API batch enumeration:** `services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=<product>&pubStartDate=…&pubEndDate=…&resultsPerPage=200` — a CVE wave in one call (§33).
- **CERT/CC notes:** `kb.cert.org/vuls/`.
- **Advisory-database package queries (products whose own tab is empty):**
  `github.com/advisories?query=crewai`, `…?query=kiro`, `…?query=rmcp`, `…?query=vm2`,
  `…?query=docker+sandboxes`, `…?query=sentry`, `…?query=copilot` (LEARNINGS §25).
- **Advisory-database agent-name queries, every sweep:** `github.com/advisories?query=claude+sort%3Apublished-desc`,
  `…?query=codex…`, `…?query=cursor…`, `…?query=agent…` (page 2 too), `…?query=llm…` (LEARNINGS §29, §36).
- **Victim post-mortems, monthly:** `"<campaign>" post-mortem` (§29).
- **Registry `time` fields** settle fix dates and whether a "deprecated" package still ships.
- **Per-product advisory tabs (`github.com/<org>/<repo>/security/advisories`, paginate):** Claude Code,
  Cursor, Cline, goose, OpenHands, SWE-agent, aider, Codex, gemini-cli, OpenClaw (11+ pages),
  n8n, Langflow, Flowise, PraisonAI, LiteLLM, LangChain, LangGraph, Semantic Kernel, Coder, MCP
  TS/Python SDKs, vm2; web: Next.js, React, Svelte, SvelteKit, Vite, Astro; **auth SDKs:**
  `clerk/javascript`, `better-auth/better-auth`, `nextauthjs/next-auth`, `supabase/auth`; **identity servers:** `zitadel/zitadel` (2 pages), Keycloak, Authentik, Ory (§38);
  Supabase components (`supabase/supabase`'s tab is empty): `supabase/realtime`, `supabase/storage-api`,
  `supabase/postgrest`; framework upstreams: `vercel/satori`, `lovell/sharp`;
  backend: FastAPI, Prisma, Streamlit, `googleapis/python-genai`, `triggerdotdev/trigger.dev`; agent platforms: `awslabs/loom`; companion repos: `openclaw/openclaw-windows-node`,
  `gitpython-developers/GitPython`, `unslothai/unsloth` (§36). Read the vendor's date, not the CVE's.
- **CSIRT CNA case files:** `csirt.divd.nl/cases/` (§36).
- **CNAs that are research firms:** `vulncheck.com/advisories`,
  `zerodayinitiative.com/advisories/published/` (AI-tool 0-days publish here first; the index's ZDI
  numbers can be off by one from the URLs — open the page and read the id),
  `research.jfrog.com/vulnerabilities`.
- **Corporate-parent / cloud-vendor bulletins (the batch is the advisory):**
  `ibm.com/support/pages/node/<id>` (Langflow, ContextForge); `github.com/NVIDIA/product-security`
  (raw `<id>.md`; `nvidia.custhelp.com` 403s); `aws.amazon.com/security/security-bulletins/` (Kiro,
  Amazon Q, `awslabs.*` MCP); `community.n8n.io` "Security update — <date>".
- **Industry security blogs:** Anthropic, OpenAI, Google Security/Project Zero, MSRC, AWS, Cloudflare,
  Red Hat, Databricks, Salesforce, Oracle.
- **Vendor threat-intel and incident reports:** `cloud.google.com/blog/topics/threat-intelligence`
  (GTIG), Mandiant reports (truncates; use outlets), Microsoft Threat
  Intelligence, `unit42.paloaltonetworks.com`, `gambit.security`, Anthropic threat reports,
  `alignment.openai.com/misalignment-reports/` (OpenAI internal-model incidents).
- **Google Cloud release-note feeds:** `docs.cloud.google.com/feeds/<product>-release-notes.xml`.
- **Rapid-reaction / telemetry:** `watchtowr.com`, `horizon3.ai`, `greynoise.io`, `wiz.io`,
  `f5.com/labs`, `blackpointcyber.com`, `okta.com` (AI-token infostealer analysis).
- **Vendor patch trackers:** `docs.gitlab.com/releases/patch-releases.xml` (the feed; the HTML hub hides AI Gateway "other patches"), Atlassian, JFrog release notes.
- **Registry records:** `osv.dev/vulnerability/MAL-<year>-<n>`, `npm view <pkg> time dist-tags` (the publish timeline; report, don't interpret — §38), `registry.npmjs.org/<pkg>/<ver>` (`version not found` = removed; `0.0.1-security` = takedown), `pip index versions <pkg>`.
- **Hacker News (Algolia):**
  `hn.algolia.com/api/v1/search_by_date?query=<one term>&tags=story&numericFilters=created_at_i%3E{epoch}`

- **Roundups that surface primaries:** `adversa.ai/blog`, `labs.cloudsecurityalliance.org`, `xygeni.io/blog`, `noma.security/blog` (grep the incident token, not the product; §38).
- **Personal agents** (`<product> zero-day OR token`): Meta Muse, OpenAI dots, Grok Bot, Instinct, Perplexity Computer; `objective-see.org`, `malwarebytes.com/blog`, `venturebeat.com/security`.
- **Researcher blogs:** remedio.io, upguard.com/blog, 0day.click, cyata.ai, layerxsecurity.com, pillar.security, oasis.security,
  tenetsecurity.ai, labs.zenity.io, novee.security, danusminimus.github.io, oddguan.com,
  manifold.security, paddo.dev, embracethered.com, itmeetsot.eu, forever.security, socket.dev,
  stepsecurity.io, aikido.dev, safedep.io, air.security,
  hacktron.ai, opensourcemalware.com, research.empiricalsecurity.com, crowdstrike.com/en-us/blog,
  accomplish.ai/blog,
  cycode.com, glow.io, threatdown.com.
- **Eval-vendor posts:** `irregular.com/research`. **Victim post-mortems:** `crowdsec.net/blog`.
- **Exploitation telemetry:** `research.empiricalsecurity.com/research`. **Agent reports:** `transluce.org/investigations`, `asymmetricsecurity.com/newsroom`.
- **Coding-tool upload/telemetry (LEARNINGS §30):** `"<tool>" upload OR telemetry OR privacy`, rotating desktop/CLI
  agents (Grok Build, ZCode, Kimi Code, Qwen Code, Trae, Kiro); `blog.ferstar.org`, `blog.vonng.com`, `eu.36kr.com`, `panews.io`.
- **Registry-team blog index pages, fetched each sweep.**
- **`api.npmjs.org/downloads/point/last-week/<pkg>`** after a takedown — millions on a stub = inflation.
- **Endpoint telemetry:** `gendigital.com/blog/insights/research`.
- **Sandbox vendors as their own CNA:** `github.com/docker/sbx-releases/releases`.
- **Standalone incident sites:** `collusion.wiki`, `rubyhack.ai`, `lasstorg.substack.com`.
- **National broadcasters:** `abc.net.au`, `sbs.com.au`.
- **Platform blog indexes (post-mortems with no CVE):** `blog.cloudflare.com`, `openclaw.ai/blog`, `docs.gitlab.com/releases/patches/`.
- **Regulators:** `aepd.es` (GDPR notifications for AI-agent attacks), `oag.ca.gov`.

## Known source-access gaps

Report these as **"not covered"**, never as "nothing found."

- **X / Bluesky** — search snippets only. **Blocked / 403:** `reddit.com`, `wired.com`, `wsj.com`, `bbc.com`, `apnews.com`,
  `theguardian.com` (AP copy: `wtop.com`, `edweek.org`, `usnews.com`), `bleepingcomputer.com`, `cisa.gov` HTML (KEV JSON), `nvidia.custhelp.com`
  (`NVIDIA/product-security` mirror), `techtimes.com`, `cybernews.com`, `scworld.com`, `spectrosec.com`, `securityonline.info`,
  `openai.com/index/...` and `openai.com/hugging-face-incident-and-misalignment/` (use `alignment.openai.com` and outlets).
- **Empty / truncated bodies:** `gbhackers.com`, `cybersecuritynews.com` (cite THN), `msrc.microsoft.com/update-guide` and
  `nvd.nist.gov/vuln/detail` (use the NVD API), `pypi.org/pypi/<pkg>/json` (`pip index versions`), `docs.cloud.google.com/<product>/release-notes`
  (the `/feeds/...xml`), `cloud.google.com/security/resources/<report>` (outlets), `socket.dev/blog` index (undated), `github.blog/changelog/label/security/`.
- **`kb.cert.org/vuls/id/<n>`** — 301 → `sei.cmu.edu` 404 for `WebFetch`; `curl -sSL --compressed` works.
- **`checkmarx.com/zero-post/`** — intermittent 404. **`koi.ai/blog`** — 301s; cite via THN.
- **GitHub `security/advisories` tabs** — occasional 504; retry. **Vendor-repo vs `github.com/advisories/GHSA-…`** — either can 404; try both.
  **Release pages** mis-render years and `api.github.com/.../releases/tags/<t>` is empty via the proxy — fix dates come from the registry or NVD.
- **arXiv API** — 429; HTML listings work. **`hn.algolia.com`** — retry once; encode `>` as `%3E`.
- **`vulncheck.com/advisories/<slug>`** — some per-CVE pages 404; cite the index.
- **`github.com` via `curl` (cloud session)** — proxy scope error; `WebFetch` reaches listings, tabs and GHSA pages (2026-10-05); the read-only `web-fetch` agent with bare URLs is the fallback.
- **`security.salesforce.com/security-advisories`** → status page; **`msrc.microsoft.com/blog`** → undated page; **`openai.com/news`** 403;
  **`NVIDIA/product-security`** root shows year folders (open the year); **ZDI published index** truncates in `WebFetch`.
- **GHSA prints a CVE id CVE Services lacks** — cite the GHSA, note DNE, re-check (§38).
- **`securityweek.com`** — intermittent 403 to `curl`; `WebFetch` works.
- **`cyber.gc.ca`** news — client-rendered, empty. **`zammad.com/en/advisories`** — stale; GitHub tab only. **`washingtonpost.com`** — paywall.
- **`techcrunch.com`** — guessed slugs 404 silently; search for the URL. **403:** `techrepublic.com`, `cnbc.com`, `cbc.ca`, `darkreading.com`, `marketscreener.com`.
  **`theregister.com/<date>/`** day indexes 404 — use `/security/`. **`reuters.com`** — paywall (`devdiscourse.com` mirrors the wire). **`technology.org`** — JS wall.

## Out of scope for this project

- Do **not** connect to, scan, probe, enumerate, or test any third-party system.
- Do **not** check whether a specific named organisation is affected by anything.
- Do **not** search for, collect, or reconstruct working exploit code.

The sweep reads published disclosures. That is the whole job.
