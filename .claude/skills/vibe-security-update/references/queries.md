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

---

## Rotation lists

Rotate a different subset each sweep; the lists are a floor, not a ceiling.

- **IDEs / agents:** Cursor, Anthropic (Claude Code), Windsurf, Google
  (Antigravity), Cline, aider, OpenHands, OpenClaw
- **Vibe-coding platforms:** Lovable, Bolt, v0, Replit, Base44
- **Web frameworks:** Vercel (Next.js), React/Meta, Svelte, Tailwind, Vite,
  Shadcn UI, Nuxt/Vue
- **Backend / auth / DB:** Supabase, Prisma, NextAuth.js / Auth.js, FastAPI,
  Streamlit, Google AI Studio SDK, better-auth, Lucia, Clerk
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
- **Researcher blogs (upstream of aggregators):** 0day.click, cyata.ai,
  layerxsecurity.com, pillar.security, oasis.security, tenetsecurity.ai,
  labs.zenity.io, novee.security, danusminimus.github.io, oddguan.com

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

## Out of scope for this project

Stated here so it is unambiguous in the one file a delegated agent may receive:

- Do **not** connect to, scan, probe, enumerate, or test any third-party system.
- Do **not** check whether a specific named organisation is affected by anything.
- Do **not** search for, collect, or reconstruct working exploit code.

The sweep reads published disclosures. That is the whole job.
