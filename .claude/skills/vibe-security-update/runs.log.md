# Runs log — vibe-security-update

> The **7 most recent** sweep entries. Older entries rotate into
> [`runs.archive.md`](runs.archive.md), which is never read into context — only
> grepped. Durable rules distilled from all runs live in
> [`LEARNINGS.md`](LEARNINGS.md), which every sweep reads at Step 0.
>
> Why the split: this file had reached 769KB (~192K tokens) across 93 entries,
> and Step 0 required reading all of it. Because run *n* re-read every prior
> entry, the project had spent roughly 10.7M tokens re-reading its own run
> history — while the workaround for a recurring blocker sat unread near the
> middle of the file. Entries average ~9.8KB; keep new ones to the structured
> format in SKILL.md Step 5.

---



## 2026-09-10

```yaml
queries: {deep: 16, medium: 12, shallow: 8}
new: [2026-09-deepseek-harness-host-header-sandbox-escape, 2026-08-claude-code-auto-mode-module-shadowing-bypass, 2026-09-gtig-adversarial-ai-agentic-pipelines, 2026-09-langflow-cve-2026-0768-validate-code-rce-exploited, 2026-08-aurora-ransomware-cursor-agent-abuse]
updated: [2026-07-nextjs-july-security-release, 2026-07-huggingface-agentic-intrusion]
sources_added: [embracethered.com, itmeetsot.eu, cloud.google.com, techxplore.com]
sources_weighted: [ox.security, vulncheck.com, nvd.nist.gov, thehackernews.com, theregister.com, thenextweb.com, adversa.ai, zerodayinitiative.com, securityaffairs.com, labs.cloudsecurityalliance.org, gambit.security, nextjs.org, github.com, securityweek.com]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only, bleepingcomputer.com-403]
```

**Notes (≤300 words).** Full-coverage sweep per the scheduled ask (social/web/industry/open-source, all cited;
agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend incl. Shadcn/Svelte/Tailwind/Vite;
backend/auth/DB incl. FastAPI/Google AI Studio SDK/NextAuth.js/Prisma/Streamlit/Supabase). All research via direct
`WebSearch`/`WebFetch` in this session, no delegated subagents. CISA KEV fetched directly (dateAdded ≥ 2026-09-03):
Citrix, Fortinet, Chromium ×2, Cisco FMC, Adobe Commerce, Windows ×2, N-able — none in scope. Five new advisories,
two of them the kind of miss worth logging. **(1) Langflow CVE-2026-0768** was untracked despite five existing
Langflow files — prior sweeps grepped the *product*, saw hits, and moved on; the CVE id itself never got a corpus
grep until a mass-exploitation report named it. Now in `LEARNINGS.md` §15. **(2) DeepSeek Harness CVE-2026-82533**
had no vendor advisory; the VulnCheck CNA record served as the independent second source (`LEARNINGS.md` §14).
**Accuracy-bar catch:** search-result summaries of the Aurora/Cursor story attributed a "told the agent it was an
authorized test" jailbreak to Aurora; The Hacker News' own text attributes that quote to ReliaQuest describing a
*different* actor's toolkit (Gryxa), and neither Gambit's primary nor the CSA note mentions any jailbreak. Written
up as a declined claim inside the advisory. **Next.js:** the pre-announced "one critical" release shipped two
(second one found in `libheif` via `sharp`); severity bumped high → critical, README row and ALERTS tier text
updated. **Investigated and declined:** OpenClaw CVE-2026-35665 / CVE-2026-41301 (March/April, moderate, DoS +
webhook signature-order bugs — fold into the OpenClaw file if a future sweep has room); two open-webui moderate
advisories (2026-09-09, out of audience); arXiv 2608.05223 malicious-skill-file benchmark (Gemini CLI 95.5%, Qwen
Code 71.6% — research, no incident; a candidate update for the ClawHavoc/skills file); CrowdStrike/AIR Security
"17,800 add-ons" figure (vendor launch PR, no primary report located). Pillar's Google ADK finding, GhostJacking,
Novee's GitHub Actions defaults, keyv, Mastra, RHSB-2026-006, and the CSA Sept 4 briefing items all resolved to
already-tracked advisories via index + corpus grep. Link checker: 19 URLs across the 5 new files, 1 flagged
(thenextweb.com returns 404 to the checker but fetched fine this session and has a 2026-09-05 Wayback snapshot —
kept). **Branch cleanup:** stale `claude/eloquent-lovelace-v8dj3u` present at session start; attempted after merge.

## 2026-09-12

```yaml
queries: {deep: 16, medium: 12, shallow: 7}
new: [2026-09-openai-agents-rubygems-gemstuffer-campaign, 2026-09-anthropic-threat-intel-report-september-2026, 2026-09-gitlab-cve-2026-85706-unauth-file-read-kev, 2026-09-jfrog-artifactory-auth-bypass-chain-kev, 2026-09-orval-openapi-codegen-rce-cluster]
updated: [2026-08-knaithe-hermes-autonomous-ai-scanning, 2026-09-anthropic-claude-session-infostealer-hijack, 2026-07-anthropic-claude-cyber-eval-breaches, 2026-04-litellm-sql-injection, 2026-09-gitspawn-git-config-agent-rce-cluster, 2026-08-agent-framework-mcp-cve-batch]
sources_added: [rubyhack.ai, blog.rubygems.org, watchtowr.com, docs.gitlab.com, greynoise.io, blackpointcyber.com, okta.com]
sources_weighted: [wiz.io, thehackernews.com, securityweek.com, theregister.com, nvd.nist.gov, cisa.gov, github.com, socket.dev, anthropic.com, labs.cloudsecurityalliance.org, siliconangle.com]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only, reuters-webfetch-blocked]
```

**Notes (≤300 words).** Full-coverage scheduled sweep (social/web/industry/open-source, all cited; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend incl. Shadcn/Svelte/Tailwind/Vite; backend/auth/DB incl. FastAPI/Google AI Studio SDK/NextAuth.js/Prisma/Streamlit/Supabase). All research via direct WebSearch/WebFetch, no delegated subagents. **Mid-run model switch (Fable 5.1 → context-compacted → Opus 4.8) and a context compaction dropped two already-applied edits (cyber-eval fourth-incident update, infostealer Okta update) out of the visible transcript — verified they were on disk and correct via git diff rather than re-adding; only one Claude process was running (ruled out a concurrent writer, LEARNINGS §2).** Five new: OpenAI-agents/RubyGems "GemStuffer" (Nightingale rubyhack.ai + Socket's May GemStuffer + RubyGems' own non-attributing post — three independent sources, `contained`); Anthropic Sept threat report (`ongoing`, single-source vendor telemetry per §16); GitLab CVE-2026-85706 CVSS-10 unauth file read (KEV 09-11, NVD score confirmed via API); JFrog CVE-2026-42018+42016 chain (KEV 09-11; folded the pre-existing CVE-2026-82329 tracking in the HF advisory by cross-link rather than duplicating); orval 11-CVE codegen cluster (fix 8.21.0 in July, GHSA-DB-published Sept per §"GHSA date ≠ disclosure date" — dated by original disclosure). Six updates incl. PaperCut AI-agent swarm folded into knaithe ATA file (GreyNoise+Blackpoint), Okta AI-token-market into the infostealer file, GitPython CVE-2026-78676 into GitSpawn (aider pins vulnerable gitpython 3.1.46 — verified via PyPI), LiteLLM SSTI+Wiz-default-key, MCP batch (chainlit/contextforge/mysql-mcp/praisonai). KEV feed fetched directly (14 entries since 09-05: only GitLab and JFrog×2 in scope). **Declined:** CoreBreak/Astra/GTIG/Langflow-0768/Deadbugz/DeepSeek-harness all already tracked (index+corpus grep per §15, per-identifier). Reuters blocked for WebFetch (new blocker). New source pattern: `rubyhack.ai` is a second bespoke standalone incident-site (cf. collusion.wiki, §12), and ecosystem-security-team blogs (blog.rubygems.org) are the authoritative non-attributing second source for registry-abuse — added to queries.md and LEARNINGS §17.

## 2026-09-13

```yaml
queries: {deep: 16, medium: 14, shallow: 9}
new: [2026-09-langflow-ibm-psirt-eleven-cve-batch, 2026-08-nvidia-nemoclaw-openshell-cve-batch, 2026-08-swe-agent-inspector-path-traversal]
updated: [2025-11-n8n-ni8mare-rce, 2026-08-agent-framework-mcp-cve-batch, 2026-09-aider-conf-yml-command-execution]
sources_added: [forkast.news, community.n8n.io, grafana.com, hn.algolia.com]
sources_weighted: [ibm.com, nvd.nist.gov, github.com, vulncheck.com, cyera.com, pillar.security, labs.cloudsecurityalliance.org, socket.dev]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only, nvidia.custhelp.com-403, securityonline.info-503, langflow-releases-tag-without-v-404]
```

**Notes (≤300 words).** Full-coverage scheduled sweep (social/web/industry/open-source; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend; backend/auth/DB). All research via direct WebSearch/WebFetch, no subagents. KEV fetched directly (dateAdded ≥ 09-06): ScreenConnect, MikroTik ×2 new since last run — none in scope. Vendor advisory-index walks: Claude Code (newest 06-25), Cursor (07-14), OpenHands (03-23), SWE-agent (none), Langflow (a 09-10 advisory, see below) — no gaps. **Three new, all found by grepping the *identifier*, not the product (LEARNINGS §15):** the Forkast roundup named one Langflow CVE; fetching IBM's bulletin behind it revealed **eleven** (LEARNINGS §18). NemoClaw came from a Forkast mention → NVIDIA's `product-security` GitHub mirror (the `custhelp.com` bulletin page 403s; the raw `5872.md` does not). SWE-agent CVE-2026-75482 surfaced only because the framework-rotation query put "SWE-agent" next to "CVE". **Two source discrepancies logged rather than resolved:** Langflow's own GHSA-7w94-79vh-5mr2 says the MCP-stdio RCE is "1.8.3 → 1.9.0" while IBM's CVE-2026-78575 says "1.0.0–1.11.5 → 1.11.6" — advisory states both and prefers the CNA. The Langflow releases page summary came back with the wrong year on dates; cited the tag without a date. **n8n:** the 09-02 community post is the batch index for 18 GHSAs; corrected the 09-09 entry's claim that GHSA-7hgx-277f-7vmg "entered independently." **Declined:** SGLang CVE-2026-86793 (single-source, inference-only), Meta Muse, Trezor/Brevo, browser-extension stealers, Cursor CVE-2026-63093 (tracked), Lovable April regression (tracked), Anthropic PyPI/Russian-actor items (both already in the 09-12 updates). HN via the Algolia API works (`hn.algolia.com/api/v1/search_by_date`) — 6 hits for "prompt injection", none new; Boolean OR is not supported there, use one term per call. Link checker: see Step 6 output in the commit.

## 2026-09-14

```yaml
queries: {deep: 16, medium: 20, shallow: 14}
new: [2026-09-openclaw-2026-8-1-advisory-batch, 2026-02-sveltekit-remote-functions-cve-batch, 2026-09-omniroute-acp-agent-unauth-rce]
updated: [2026-08-agent-framework-mcp-cve-batch, 2026-07-nextjs-july-security-release, 2026-04-vite-dev-server-file-read, 2026-09-gitspawn-git-config-agent-rce-cluster, 2026-08-knaithe-hermes-autonomous-ai-scanning]
sources_added: [f5.com, registry.npmjs.org]
sources_weighted: [github.com, nvd.nist.gov, aws.amazon.com, ibm.com, unit42.paloaltonetworks.com, theregister.com, advisories.gitlab.com, cisa.gov, svelte.dev]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only, msrc.microsoft.com-update-guide-renders-empty, techtimes.com-403]
```

**Notes (≤300 words).** Full-coverage scheduled sweep (social/web/industry/open-source; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend incl. Svelte/Vite/Astro; backend/auth/DB). All research direct WebSearch/WebFetch, no subagents. KEV fetched directly (dateAdded ≥ 09-07): nothing new in scope beyond the already-tracked GitLab/JFrog entries. **All three new advisories came from vendor advisory-index walks, not search.** (1) OpenClaw's index carries **75 advisories all dated 2026-09-11** for fixes shipped 2026.7.1–2026.8.1, plus ~30 dated 06-30 that no sweep had logged — walked 11 pages, sampled 10 (LEARNINGS §19). (2) SvelteKit: six CVEs published by VulnCheck on 08-28 map to vendor advisories from **Feb–Jul**; the DB carries a second GHSA id per CVE alongside the vendor-repo id. Dated by vendor publication. (3) OmniRoute CVE-2026-88062: vendor page says fixed 3.8.49, NVD says 3.8.49 affected, DB copy says ≤3.8.50 no fix, PR merged into 3.8.50 branch after 3.8.49 shipped — all four stated, status `patched` on the vendor's word with the caveat prominent. **Corrections to my own triage:** the EU/DSEWiki probe looked new but the 09-10 sweep had already folded it into the Hugging Face file — checked the file before writing. Copilot CLI CVE-2026-45033 (May) is a GitSpawn precedent no GitSpawn source cited; folded in with the generic `safe.bareRepository=explicit` mitigation. **Declined:** MSRC CVE-2026-81381/81380 (Copilot+VS Code token disclosure, Sept Patch Tuesday, medium) — MSRC page renders empty to WebFetch and NVD has one line; nltk pickle RCEs, prowler SAML, yayson, maplibre (out of audience); OpenClaw CVE-2026-33575/35665/41301 (older, medium; noted in the new OpenClaw file's context only via NVD, not written up); arXiv 2609.07754 "coding assistants never check supply-chain trust signals" (research); Microsoft ASCII-smuggling blog (phishing, not agents). HN Algolia: first call returned non-JSON, retry was clean — transient, not a blocker. Link checker output in Step 6.

## 2026-09-15

```yaml
queries: {deep: 16, medium: 20, shallow: 8}
new: [2026-04-clerk-sdk-middleware-bypass-cve-batch, 2026-09-bifrost-mcp-client-registration-unauth-rce, 2026-07-google-agent-studio-api-proxy-ssrf, 2026-07-unstructured-partition-url-ssrf]
updated: [2026-08-agent-framework-mcp-cve-batch, 2026-06-langgraph-rce-chain, 2026-04-litellm-sql-injection, 2026-08-jsonata-sandbox-escape-rce, 2026-09-openai-agents-rubygems-gemstuffer-campaign, 2026-09-langflow-ibm-psirt-eleven-cve-batch, 2025-11-n8n-ni8mare-rce, 2026-04-vite-dev-server-file-read, 2026-08-npm-bin-entry-harvesting-google-scoped]
sources_added: [zeropath.com, blog.centriole.io, docs.cloud.google.com]
sources_weighted: [github.com, nvd.nist.gov, vulncheck.com, research.jfrog.com, theregister.com, ibm.com, sentinelone.com, registry.npmjs.org]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only, spectrosec.com-404, docs.cloud.google.com-html-renders-nav-only-use-feed, vendor-repo-ghsa-url-404-for-knowns, pypi-json-truncated-by-webfetch]
```

**Notes (≤300 words).** Full-coverage scheduled sweep (social/web/industry/open-source; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend incl. Vite/Svelte/Next.js; backend/auth/DB incl. FastAPI/Streamlit/Prisma/Supabase/NextAuth/Clerk/Google). All research direct WebSearch/WebFetch, no subagents. KEV fetched directly (dateAdded ≥ 09-08): only Cisco Secure Email Gateway new since 09-14 — nothing in scope. **All four new advisories came from a vendor advisory tab or an advisory-database listing; none from search.** (1) Clerk: three 2026 advisories including a CVSS 9.1 — `{framework} CVE` covers Next.js, not the auth SDK above it, and the Clerk tab had never been walked (LEARNINGS §20). (2) Bifrost 9.8 via the `mcp` recency listing; JFrog is CNA and researcher (§14). (3) Agent Studio SSRF exists only in the Google Cloud release-notes *feed* — the HTML page renders as navigation (§22). (4) unstructured 9.3 via the reviewed-critical pip list (July vendor advisory, NVD 08-20). Casdoor (9.9, unpatched, maintainers deleted the researcher's issues) folded into the MCP batch rather than a new file. **Declined:** esphome, prowler, NLTK, yayson, maplibre, omnigent, Serena (out of audience); Streamlit GHSA-7p48-42j8-8846 = tracked CVE-2026-33682; Cline Hub/Kanban, goose fsmonitor, better-auth SSO, Starlette, elementary-data, OpenClaw CVE-2026-32922, Windsurf CVE-2026-30615 all confirmed tracked by identifier; techtimes agent-pipeline study (403, research); arXiv 2604.08407 (research). HN Algolia: 4 terms, nothing new. Vendor-tab newest dates: Claude Code 06-25, Cursor 07-14, Cline 06-23, aider none, goose 07-24, OpenHands 03-23 (page error), LangChain 06-12, LangGraph 08-28, Semantic Kernel 02-19, better-auth 08-11, supabase/auth 03-11, Prisma 2021, FastAPI 2021, Streamlit 03-24, Vite 06-01, SvelteKit 07-29, Next.js 08-25, OpenClaw 09-11, gemini-cli none, LiteLLM 08-26, NextAuth 07-20, Langflow 09-10, Codex 2025-09 (page error), MCP TS SDK 02-04, Clerk 04-22. Five sources decayed (60-day rule). Link checker: 0/190 flagged across the nine edited files; 1/21 in the new files (`clerk.com/changelog` URLError to the checker, fetched fine in-session, Wayback snapshot exists — kept). **Budget warning:** `dist/llms.txt` built at 69,582 B against a 69,632 B budget after shortening four new titles — the next new advisory breaches it at the Tier-2 floor (LEARNINGS §9); the BACKLOG "llms.txt Tier-2 floor" item is now due, not optional.

## 2026-09-16

```yaml
queries: {deep: 16, medium: 18, shallow: 10}
new: [2026-09-coder-registry-cloudflare-terraform-supply-chain, 2026-07-gitlab-mcp-account-takeover-cve-cluster, 2026-08-revstealer-fake-claude-opus5-desktop]
updated: [2026-04-flowise-rce-cluster, 2026-05-praisonai-auth-bypass, 2025-11-n8n-ni8mare-rce, 2026-08-agent-framework-mcp-cve-batch]
sources_added: [coder.com, morphisec.com]
sources_weighted: [pluto.security, vulncheck.com, nvd.nist.gov, github.com, community.n8n.io, bleepingcomputer.com, esecurityplanet.com, labs.cloudsecurityalliance.org, helpnetsecurity.com, scworld.com, cloud.google.com, ibm.com, registry.npmjs.org]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only, hn-algolia-numericfilters-need-url-encoded-gt, nvd-web-page-renders-home-use-api, coder-github-advisory-403-use-blog]
```

**Notes (≤300 words).** Full-coverage scheduled sweep (social/web/industry/open-source, all cited; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend incl. Svelte/Vite/Next.js/Tailwind/Shadcn; backend/auth/DB incl. FastAPI/Streamlit/Prisma/Supabase/NextAuth/Clerk/Google). All research direct WebSearch/WebFetch, no subagents. KEV fetched directly (dateAdded >= 09-09): ScreenConnect, JFrog x2, GitLab, MikroTik x2, Citrix, Fortinet, Chromium, Cisco FMC/Email, Pixel — only the already-tracked GitLab/JFrog in scope. **Three new.** (1) **Coder registry compromise** — a stolen Cloudflare API key rerouted `registry.coder.com` for 14h on 08-31 serving credential-stealing Terraform modules; Coder blog + GHSA + BleepingComputer + eSecurityPlanet + CSA (the GHSA page 403s to WebFetch, the Coder blog carries the same IOCs). (2) **@zereight/mcp-gitlab** cluster — Pluto Security (July) + five GHSAs + NVD; downloads 82K/wk via the npm API; dated by the July research per the GHSA-date-is-not-disclosure-date rule though CVEs landed 09-15/16. (3) **RevStealer** fake "Claude Opus 5 Free Desktop" GitHub repo (Morphisec + Help Net + SC Media); generic stealer but the fake-Claude GitHub delivery is squarely on-audience. **Four updates**, all confirmed by identifier grep first: Flowise (~17 new Sept CVEs incl. two Custom-MCP-node RCEs, all fixed 3.1.4 — and the repo is **archived 2026-08-13**, no release past 3.1.4, so effectively EOL: flagged prominently); PraisonAI (~30-CVE mass audit, five+ unauth 9.8 RCE, fixed 4.6.62, confirmed via NVD API); n8n (16-advisory 09-16 batch via community forum + GHSAs); MCP batch (LightLLM pickle RCE 9.3 unpatched + atomic-agents-stack MITM 9.2). **Declined/logged:** Mandiant "AI Risk and Resilience" special report (Sept 16 Help Net coverage — the $50K runaway agent and repo-cloning items are real but the report repackages already-tracked GTIG "From Prompting to Autonomy" + ClawHavoc/VirusTotal; single-source vendor telemetry, no distinct new incident); Claude Chrome ShadowPrompt/ClaudeBleed (already tracked); dependency-confusion google-cloud-internal 129-day (Centriole, already in the bin-entry-harvesting file's theme — grepped, not re-filed); Supabase RLS "advisor" scans (vendor tooling, not an incident). **HN Algolia fix:** the `numericFilters=created_at_i>EPOCH` needs the `>` URL-encoded as `%3E` or the API returns non-JSON — first attempt with a bare `>` failed on every term, `%3E` worked (added to blockers/queries note). Vendor-tab walks: Claude Code newest 06-25, Cursor 07-14, OpenHands 03-23, SWE-agent none, aider none, goose 07-24, Cline 06-23, LangChain 06-12, Semantic Kernel 02-19, Next.js 08-25, React 07-21, Svelte 05-14, SvelteKit 07-29, Vite 06-01, Tailwind/shadcn/Supabase/python-genai none, FastAPI 2021, Prisma 2021, Streamlit 03-24, NextAuth 07-20, Clerk 04-22, better-auth 08-11, Codex 2025-09, Flowise 09-10, PraisonAI 09-15 (18 pages), n8n 09-16, Langflow 09-10, LiteLLM 08-26, Coder 09-01, MCP TS SDK 02-04 — all gaps covered. **Branch cleanup:** stale `jam/youthful-wozniak-y9zt6j` and prior `claude/eloquent-lovelace-*` branches present; deletion attempted per the recurring 403/no-delete situation documented since 08-18.

## 2026-09-17

```yaml
queries: {deep: 16, medium: 22, shallow: 12}
new: [2026-09-crewai-zdi-zero-day-agent-loading-cve-batch, 2026-09-kiro-ide-cli-aws-bulletin-cve-batch, 2026-09-aws-security-agent-mcp-s3-bucket-squat, 2026-09-bragjack-browser-extension-builtin-ai-assistant-hijack, 2026-09-mandiant-hijacked-coding-assistant-session-shai-hulud-saas, 2026-09-shai-hulud-111-day-dormant-payload-mcp-package, 2026-09-openai-misalignment-reports-leaked-keys-public-uploads]
updated: [2026-08-vm2-isolated-vm-sandbox-escapes, 2026-08-mindsdb-minds-platform-unauthenticated-rce, 2026-08-agent-framework-mcp-cve-batch, 2026-08-knaithe-hermes-autonomous-ai-scanning, 2026-07-kiro-mcp-config-self-rewrite-rce]
sources_added: [forever.security, alignment.openai.com, aepd.es, securitybrief.news, kiro.dev, pypi.org]
sources_weighted: [zerodayinitiative.com, github.com/advisories, github.com, aws.amazon.com, nvd.nist.gov, vulncheck.com, thehackernews.com, helpnetsecurity.com, securityweek.com, theregister.com, aikido.dev, registry.npmjs.org, cloud.google.com]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only, github-blog-changelog-security-label-404, openai-misalignment-framework-page-403, cloud-google-mandiant-report-landing-truncated, bbc-webfetch-blocked, cybernews-403, scworld-403, vulncheck-per-cve-pages-404-for-3-of-6-vm2, ghsa-3jxw-vj8m-8x77-404]
```

**Notes (≤300 words).** Full-coverage scheduled sweep (social/web/industry/open-source, all cited; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw/CrewAI; frontend incl. Next.js/React/Svelte/Vite; backend/auth/DB incl. FastAPI/Streamlit/Prisma/Supabase/NextAuth/Clerk/better-auth/python-genai). All research direct WebSearch/WebFetch, no subagents. KEV fetched directly (dateAdded ≥ 09-10): Pixel, Cisco ISE/Email, Acronis, ScreenConnect, JFrog ×2, GitLab, MikroTik ×2 — only the tracked GitLab/JFrog in scope. **Seven new; again most came from direct listings, not search:** `github.com/advisories?query=kiro` (nine unreviewed AWS-CNA CVEs; only one tracked), the AWS bulletin index (2026-105/111), the ZDI published-advisories index (CrewAI + MindsDB 0-days — note the index page's ZDI numbers were off by one from the advisory URLs: "707 CrewAI" on the list resolved to `/ZDI-26-706/`; fetch the URL and read the id printed on the page), the `rmcp` recency hits, and the vm2 vendor tab (ten advisories after the one we had). BragJack and the Mandiant case came from THN's front page; OpenAI's reports from HN Algolia. **Accuracy calls:** THN and Help Net described *different* case studies from the same Mandiant report (a real SaaS intrusion vs a red-team exercise) — fetched three outlets and wrote both, labelled; the report landing page itself would not render. CrewAI's advisory tab is empty while the CVE record has nine — LEARNINGS §25. Kiro CVE-2026-89332's fix (0.8.135) is dated 2026-01-14 on the vendor changelog; CVE 2026-09-11 — dated by disclosure, fix date stated. vm2 vendor pages say "No known CVE" for all ten; VulnCheck CVE'd six on 09-17 (three per-CVE pages 404 — cited from the index, flagged as such). **Declined:** Irregular self-retraining (research); Flutter `universal_file_viewer` XCSSET (pub.dev, ~500 downloads, `example/` only); lmdeploy/SGLang/djust/@cyclonedx/@vendure/tinacms (out of audience); Mozilla 0DIN (June, tracked); Grafana MCP, 7nohe, n8n 09-16, OpenClaw 09-11, GemStuffer/tenderlove (all tracked by identifier). **Budget:** watch `dist/llms.txt` after seven new Tier-2 lines. Two sources decayed.
