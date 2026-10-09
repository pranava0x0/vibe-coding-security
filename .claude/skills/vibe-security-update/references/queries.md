# Sweep query list

> The literal search strings a sweep runs, and nothing else. This is the only
> file in this skill that may be handed to a delegated agent.

**Purpose.** This project indexes already-disclosed security advisories for people building with AI coding tools.
These searches find *coverage* — vendor advisories, CVE records, researcher write-ups — never vulnerable systems.

**Frozen size.** This file is at its 4,000-token cap. Do not add sources or notes here: sources go in
`source-priorities.json`, notes in `LEARNINGS.md`. The "why" per query is in `triage-patterns.md` (§1).

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

Rotate a different subset each sweep; floors, not ceilings.

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

Bare pointers; the *why* lives in `triage-patterns.md` and `LEARNINGS.md`.

- **Ecosystem security teams:** `blog.rust-lang.org`, `blog.pypi.org`, `github.blog/changelog`, `blog.golang.org`, `blog.rubygems.org`, Packagist (§17).
- **Advisory databases:** `github.com/advisories`, GitLab Advisory DB, NVD API (`services.nvd.nist.gov/rest/json/cves/2.0?cveId=`), CNA records `cveawg.mitre.org/api/cve/<id>` (title and description can disagree), CISA KEV JSON, `advisory.splunk.com`, `spring.io`.
- **Advisory-database listings (fetch every sweep):** `github.com/advisories?query=mcp+sort%3Apublished-desc`,
  `…?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical`, `…ecosystem%3Apip…` (reviewed lists omit CVE-only entries).
  **Backfill:** rows are vendor advisories 1–4 months old — grep each CVE id; date by the vendor page; a package with no file here may have a five-page tab (§39, §40).
- **Front pages, fetched before any search:** `thehackernews.com`, `securityweek.com`, `theregister.com/security/` — cite the article, not the page (§28).
- **THN weekly roundup** (`thehackernews.com/2026/MM/threatsday-….html`): grep every item (§33).
- **NVD API batch enumeration:** `services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=<product>&pubStartDate=…&pubEndDate=…&resultsPerPage=200` — a CVE wave in one call (§33).
- **CERT/CC:** `kb.cert.org/vuls/`.
- **Advisory-database package queries (products whose own tab is empty):** `github.com/advisories?query=crewai`, `…kiro`, `…rmcp`, `…vm2`, `…docker+sandboxes`, `…sentry`, `…copilot`, `…mcp-toolbox` (§25, §40).
- **Advisory-database agent-name queries, every sweep:** `github.com/advisories?query=claude+sort%3Apublished-desc`, `…codex…`, `…cursor…`, `…agent…` (page 2 too), `…llm…` (§29, §36).
- **Registry `time` fields** settle fix dates and whether a "deprecated" package still ships.
- **Per-product advisory tabs (`github.com/<org>/<repo>/security/advisories`, paginate):** Claude Code, Cursor, Cline, goose, OpenHands, SWE-agent, aider, Codex, gemini-cli, OpenClaw (11+ pages), n8n, Langflow, Flowise, PraisonAI (18 pages), LiteLLM, LangChain, LangGraph, Semantic Kernel, Coder, MCP TS/Python SDKs, vm2; web: Next.js, React, Svelte, SvelteKit, Vite, Astro; **auth SDKs:**
  `clerk/javascript`, `better-auth/better-auth`, `nextauthjs/next-auth`, `supabase/auth`; **identity servers:** `zitadel/zitadel` (2 pages), Keycloak, Authentik, Ory (§38); Supabase components: `supabase/realtime`, `supabase/storage-api`, `supabase/postgrest`; framework upstreams: `vercel/satori`, `lovell/sharp`;
  backend: FastAPI, Prisma, Streamlit, `googleapis/python-genai`, `triggerdotdev/trigger.dev`, **`payloadcms/payload` (5 pages, §40)**; agent platforms: `awslabs/loom`; companion repos: `openclaw/openclaw-windows-node`, `gitpython-developers/GitPython`, `unslothai/unsloth` (§36); **primitives under agents and generated apps:**
  `steveukx/git-js`, `jpadilla/pyjwt`, `tinylibs/tinypool`, `ljharb/shell-quote`, `jshttp/proxy-addr`, `lxsmnsyc/seroval` (§39), `mpdavis/python-jose` (watch PR #422), `agronholm/anyio` (§40).
  Vendor date, not CVE date; products with 3+ files here get the whole tab diffed.
- **CSIRT CNA case files:** `csirt.divd.nl/cases/` (§36).
- **CNAs that are research firms:** `vulncheck.com/advisories`, `zerodayinitiative.com/advisories/published/` (ZDI numbers can be off by one — read the page), `research.jfrog.com/vulnerabilities`.
- **Corporate-parent / cloud-vendor bulletins (the batch is the advisory):** `ibm.com/support/pages/node/<id>` (Langflow, ContextForge; leads the vendor tab by 1–3 months — carry both, §39); `github.com/NVIDIA/product-security` (raw `<id>.md`); `aws.amazon.com/security/security-bulletins/` (Kiro, Amazon Q, AgentCore, `awslabs.*`); `community.n8n.io` "Security update — <date>".
- **Industry security blogs:** Anthropic, OpenAI, Google Security/Project Zero, MSRC, AWS, Cloudflare,
  Red Hat, Databricks, Salesforce, Oracle.
- **Vendor threat-intel and incident reports:** GTIG (`cloud.google.com/blog/topics/threat-intelligence`), Mandiant (use outlets), Microsoft TI, `unit42.paloaltonetworks.com`, `gambit.security`, Anthropic threat reports, `alignment.openai.com/misalignment-reports/`.
- **Google Cloud release-note feeds:** `docs.cloud.google.com/feeds/<product>-release-notes.xml`.
- **Rapid-reaction / telemetry:** `watchtowr.com`, `horizon3.ai`, `greynoise.io`, `wiz.io`, `f5.com/labs`, `blackpointcyber.com`, `okta.com`.
- **Vendor patch trackers:** `docs.gitlab.com/releases/patch-releases.xml` (the feed, not the hub), Atlassian, JFrog release notes.
- **Registry records:** `osv.dev/vulnerability/MAL-<year>-<n>`, `npm view <pkg> time dist-tags` (report, don't interpret — §38), `registry.npmjs.org/<pkg>/<ver>` (`version not found` = removed; `0.0.1-security` = takedown), `pip index versions <pkg>`, `npm view <consumer>@<major> dependencies.<dep>` (§39).
- **Hacker News (Algolia):** `hn.algolia.com/api/v1/search_by_date?query=<one term>&tags=story&numericFilters=created_at_i%3E{epoch}`
- **Roundups that surface primaries:** `adversa.ai/blog` (§39), `labs.cloudsecurityalliance.org`, `xygeni.io/blog`, `noma.security/blog` (grep the incident token, not the product; §38).
- **Personal agents** (`<product> zero-day OR token`): Meta Muse, dots, Grok Bot, Instinct, Perplexity Computer; `objective-see.org`, `malwarebytes.com/blog`, `venturebeat.com`.
- **Researcher blogs:** remedio.io, upguard.com/blog, 0day.click, cyata.ai, layerxsecurity.com, pillar.security, oasis.security, tenetsecurity.ai, labs.zenity.io, novee.security, danusminimus.github.io, oddguan.com, manifold.security, paddo.dev, embracethered.com, itmeetsot.eu, forever.security, air.security, hacktron.ai, opensourcemalware.com, research.empiricalsecurity.com, crowdstrike.com/en-us/blog, accomplish.ai/blog, cycode.com, glow.io, threatdown.com.
- **Eval-vendor posts:** `irregular.com/research`. **Victim post-mortems:** `crowdsec.net/blog`. **Agent reports:** `transluce.org/investigations`, `asymmetricsecurity.com/newsroom`.
- **Coding-tool upload/telemetry (§30):** `"<tool>" upload OR telemetry OR privacy` — Grok Build, ZCode, Kimi Code, Qwen Code, Trae, Kiro; `blog.ferstar.org`, `blog.vonng.com`, `eu.36kr.com`, `panews.io`.
- **`api.npmjs.org/downloads/point/last-week/<pkg>`** — millions on a stub = inflation.
- **Sandbox vendor CNA:** `github.com/docker/sbx-releases/releases`.
- **Incident sites:** `collusion.wiki`, `rubyhack.ai`, `lasstorg.substack.com`. **Regulators:** `aepd.es`, `oag.ca.gov`.
- **Platform blog indexes (post-mortems with no CVE):** `blog.cloudflare.com`, `openclaw.ai/blog`, `docs.gitlab.com/releases/patches/`, `vercel.com/blog`, `payloadcms.com/posts/releases` ("hardening" = undisclosed fixes, §40).
- **Cross-vendor researcher reports:** outlets (`unite.ai`, `thenextweb.com`) name the organisations; build the table from `cveawg.mitre.org` + the credited fix PRs (§40).

## Known source-access gaps

Report these as **"not covered"**, never as "nothing found."

- **X / Bluesky** — search snippets only. **Blocked / 403:** `reddit.com`, `wired.com`, `wsj.com`, `bbc.com`, `apnews.com`,
  `theguardian.com` (AP copy: `wtop.com`, `edweek.org`, `usnews.com`), `bleepingcomputer.com`, `cisa.gov` HTML (use KEV JSON), `nvidia.custhelp.com`
  (`NVIDIA/product-security` mirror), `techtimes.com`, `cybernews.com`, `scworld.com`, `spectrosec.com`, `securityonline.info`, `arstechnica.com`,
  `anas-security-portfolio.vercel.app`, `openai.com/index/...` and `openai.com/hugging-face-incident-and-misalignment/` (use `alignment.openai.com` — itself 403 on 10-07, retry — and outlets).
- **Empty / truncated bodies:** `gbhackers.com`, `cybersecuritynews.com` (cite THN), `msrc.microsoft.com/update-guide` and
  `nvd.nist.gov/vuln/detail` (use the NVD API), `pypi.org/pypi/<pkg>/json` (`pip index versions`), `docs.cloud.google.com/<product>/release-notes`
  (the `/feeds/...xml`), `cloud.google.com/security/resources/<report>` (outlets), `socket.dev/blog` index (undated), `github.blog/changelog/label/security/`.
- **`kb.cert.org/vuls/id/<n>`** — `WebFetch` 404s; `curl -sSL --compressed` works. **`checkmarx.com/zero-post/`** — intermittent 404. **`koi.ai/blog`** — 301s; cite via THN.
- **GitHub `security/advisories` tabs** — occasional 504; retry. **Database GHSA URL 404s for vendor-repo-only advisories** — use `github.com/<org>/<repo>/security/advisories/GHSA-…`.
  **Release pages** mis-render years and `api.github.com/.../releases/tags/<t>` is empty via the proxy — fix dates come from the registry or NVD.
- **arXiv API** — 429; HTML listings work. **`hn.algolia.com`** — retry once; encode `>` as `%3E`. **`vulncheck.com/advisories/<slug>`** — some 404; cite the index.
- **`github.com` via `curl` (cloud session)** — proxy scope error; `WebFetch` reaches listings, tabs and GHSA pages; the read-only `web-fetch` agent with bare URLs is the fallback.
- **`security.salesforce.com/security-advisories`** → status page; **`msrc.microsoft.com/blog`** → undated page; **`openai.com/news`** 403;
  **`NVIDIA/product-security`** root shows year folders (open the year); **ZDI published index** truncates in `WebFetch`.
- **GHSA prints a CVE id CVE Services lacks** — cite the GHSA, note DNE, re-check (§38; Claude Code's resolved in two days).
- **`securityweek.com`** — intermittent 403 to `curl`; `WebFetch` works. **`pypistats.org`** — 429 after one or two calls.
- **`cyber.gc.ca`** — client-rendered. **`zammad.com/en/advisories`** — stale; GitHub tab only. **Paywall:** `washingtonpost.com`, `reuters.com` (`devdiscourse.com` mirrors).
- **`techcrunch.com`** — guessed slugs 404; search for the URL. **403:** `techrepublic.com`, `cnbc.com`, `cbc.ca`, `darkreading.com`, `marketscreener.com`.
  **`theregister.com/<date>/`** day indexes 404 — use `/security/`. **`technology.org`** — JS wall.
- **`aws.amazon.com/security/security-bulletins/<id>/`** — lower-case id only (`2026-127-aws`). **`supabase.com/changelog/<slug>`** — `WebFetch` 403; append `.md`, `curl`.
- **Cloud-session Python** — no `markdown`/`pytest`; `python -m pip install markdown==3.7 Pygments==2.18.0 pytest==8.3.3` (skip the Debian PyYAML; bare `pip` is another interpreter).

## Out of scope for this project

- Do **not** connect to, scan, probe, enumerate, or test any third-party system.
- Do **not** check whether a specific named organisation is affected by anything.
- Do **not** search for, collect, or reconstruct working exploit code.

The sweep reads published disclosures. That is the whole job.
