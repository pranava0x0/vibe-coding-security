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



## 2026-09-08

```yaml
queries: {deep: 16, medium: 10, shallow: 8}
new: [2026-03-openai-codex-branch-name-command-injection, 2026-04-llm-router-malicious-intermediary-attacks]
updated: [2026-02-clawhavoc-clawhub-skills]
sources_added: [beyondtrust.com, blog.barrack.ai, cointelegraph.com, straiker.ai]
sources_weighted: [securityweek.com, arxiv.org, coindesk.com]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only]
```

**Notes (≤300 words).** Full-coverage sweep per this run's explicit ask (social/web/industry/open-source,
all cited; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend incl. Shadcn/Svelte/
Tailwind/Vite; backend/auth/DB incl. FastAPI/Google AI Studio SDK/NextAuth.js/Prisma/Streamlit/Supabase).
All research via direct `WebSearch`/`WebFetch` in this session, no delegated subagents. Two genuinely new,
both backfilled (older than this sweep's window but never previously tracked): **OpenAI Codex** branch-name
`${IFS}`-based shell-injection stealing GitHub OAuth/Installation tokens (BeyondTrust Phantom Labs; disclosed
2026-03-30, but OpenAI silently remediated server-side by 2026-02-05 — no CVE assigned, consistent with
SaaS-fix practice) and a UC research paper on malicious third-party LLM routers injecting tool calls / stealing
credentials (arXiv:2604.08407, Apr 2026) — marked `status: unconfirmed` since it's one research group with no
independent replication. **Accuracy-bar catch on the router paper:** several crypto-press outlets (Cointelegraph,
CCN, ChainCatcher) headlined the wallet-drain finding as "$500,000," but CoinDesk — which read the paper directly
— described the seeded canary wallet as carrying only a nominal balance with losses under $50, and the arXiv
abstract itself gives no dollar figure at all. Rather than pick one, the advisory states both, names which
source is better-grounded, and flags the "$500,000" figure as unverified — same "verify the outlet, don't trust
the aggregator's number" lesson as the Ray-KEV and Wiz/Red-Agent cautions in `LEARNINGS.md` §6, now observed for
a raw dollar figure rather than a quote or attribution claim. One update: Straiker's separate Feb 2026 ClawHub
campaign (`bob-p2p-beta`, threat actor `26medias`/`BobVonNeumann`, agent-to-agent distribution via Moltbook,
71 malicious + 73 high-risk of 3,505 skills scanned) folded into the existing ClawHavoc advisory as a new dated
update — distinct researcher, distinct payload (direct Solana wallet drain vs. the original campaign's AMOS
infostealer), and a distinct distribution mechanism (agent-to-agent social engineering via a dedicated
agent-social-network persona) from every update already tracked there (Koi Security's original find, Snyk
ToxicSkills, Trail of Bits scanner bypasses, SkillCloak/SkillDetonate, Zenity's skills.sh campaign) — explicitly
flagged as single-sourced to Straiker, since SecurityWeek's pickup restates rather than independently verifies.
Investigated and declined: a SentinelOne/Prompt Security "dependency hijack" piece reads as generic risk
commentary with no specific incident, victim, or CVE — doesn't meet the bar. A "GitHub Actions defaults for
Anthropic/Google/OpenAI fall to unauthenticated RCE" claim (from a search-result synthesis, not a primary
article) resolved on investigation to already-tracked findings (gitlost, gemini-cli-trustissues,
claude-code-github-actions-bot-bypass) with no distinct new OpenAI-specific finding — not written up separately.
CISA KEV feed fetched directly (dateAdded >= 2026-08-31): 8 entries, all already tracked (LiteLLM, Starlette,
Kestra, JFrog) or out of scope (Chromium V8, Sangoma, SonicWall x2). Extensively cross-checked via
advisory-index.jsonl + corpus grep before writing anything: npm/PyPI/crates supply-chain waves (arrayref,
binding.gyp/Phantom Gyp, ChainDrop, TeamPCP/Mini Shai-Hulud, Operation Navy Ghost), Cursor CVE batch, OpenClaw
Claw Chain, Vercel/Context.ai OAuth breach, Hugging Face agentic intrusion, React2Shell/Next.js/Svelte CVE
batches, FastAPI/Starlette BadHost, Streamlit SSRF, Supabase RLS misconfiguration pattern, Google AI Studio
API-key leak, Semantic Kernel RCE (CVE-2026-25592/26030), Open VSX GlassWorm + evil-twin campaigns, GhostSplice
MCP instruction-splitting, GitSpawn, CoreBreak — all confirmed already tracked, no duplicates written. No source-
priority decay beyond the routine 2 sources this run (blog.trailofbits.com, securityaffairs.com, 60-day
threshold). **Branch cleanup:** stale `claude/eloquent-lovelace-*` branches present at session start
(`0c4quz`, `biz8jx`, `dq6yjk`, `ilp5b9`, `o3cag1`, `r7xawf`, `r7xawf-followup`, `v8dj3u`) — same recurring
403/no-delete-tool situation documented since 2026-08-18; not re-attempted without a working deletion path.

## 2026-09-09

```yaml
queries: {deep: 16, medium: 11, shallow: 6}
new: [2026-09-deadbugz-mcp-supply-chain-campaign]
updated: [2026-08-agent-framework-mcp-cve-batch, 2025-11-n8n-ni8mare-rce]
sources_added: []
sources_weighted: [pillar.security, adversa.ai, nhimg.org, vulncheck.com, advisories.gitlab.com, nvd.nist.gov, github.com, cisa.gov]
blockers: [reddit-webfetch-403, x-bsky-search-snippets-only]
```

**Notes (≤300 words).** Full-coverage sweep per this run's explicit ask (social/web/industry/open-source, all
cited; agent-orchestration incl. aider/OpenHands/SWE-agent/OpenClaw; frontend incl. Shadcn/Svelte/Tailwind/Vite;
backend/auth/DB incl. FastAPI/Google AI Studio SDK/NextAuth.js/Prisma/Streamlit/Supabase). All research via direct
`WebSearch`/`WebFetch` in this session, no delegated subagents. CISA KEV feed fetched directly (dateAdded >=
2026-09-02): 12 entries, all already tracked (LiteLLM, Starlette, Kestra, JFrog) or out of scope (Adobe
Commerce/Magento, Windows x2, N-able N-central, Chromium V8, Sangoma, SonicWall x2). One new advisory: **Deadbugz**
(Pillar Security, 2026-08-12) — a malicious MCP server (`productivity-suite`) that behaves benignly for its first
three tool calls then rewrites its own metadata into credential-theft instructions; distributed via 23 GitHub PRs
in a 74-minute window. Single-primary-source (Adversa and nhimg.org both summarize Pillar's own research rather
than independently verifying it) — marked `unconfirmed` per the two-independent-source bar, same as the related
GhostSplice entry. Two updates, both confirmed CVE-by-CVE against primary sources rather than an aggregator
roundup: `2026-08-agent-framework-mcp-cve-batch.md` gained three unrelated single-server MCP CVEs surfaced by an
Adversa roundup — `mcp-atlassian` CVE-2026-73498 (path traversal, confirmed on the GHSA page directly), ArcadeDB
CVE-2026-67357 (MCP `get_server_settings` cluster-token leak, confirmed via VulnCheck; explicitly disambiguated
from the distinct sibling CVE-2026-67343, a non-MCP REST-endpoint leak of the same token fixed one version
earlier), and `facebook-ads-mcp-server` CVE-2026-19956 (SSRF, confirmed via the NVD API — VulDB-sourced, no GHSA
filed). `2025-11-n8n-ni8mare-rce.md` gained two medium-severity authorization-bypass CVEs, both confirmed via
GitLab's advisory-database mirror: CVE-2026-86996 (an Agent-tool workflow invocation path skipped the
sub-workflow caller-policy check that the conventional Execute-Workflow path enforces) and GHSA-h3jj-5f3v-3685
(the Public API's execution-retry endpoint checked `workflow:read` instead of `workflow:execute`). Vendor
GHSA-index page-walk repeated for Claude Code and Cursor per the standing practice — no advisories newer than the
already-tracked June/July 2026 batches on either, confirming no gap rather than a quiet one. Extensively
cross-checked against `advisory-index.jsonl` + corpus grep before writing anything: npm/PyPI/crates-io supply-
chain waves (arrayref, binding.gyp/Phantom Gyp/Miasma lineage, Hades/ensmallen, Operation Navy Ghost, npm
bin-entry-harvesting), Cursor CVE batch, OpenClaw Claw Chain, GitSpawn, Mexico-government breach, Hugging Face
agentic intrusion (incl. the OpenAI-agent message-board story, already folded in), Google API-key/Gemini-scope
leak, Supabase Auth OIDC bypass, React2Shell/Next.js CVE batch, Streamlit CVE-2026-33682, Open VSX evil-twin —
all confirmed already tracked, no duplicates written. Declined: Nodemailer's IDN/Punycode allow-list bypass
(GHSA-wmmp-3585-3rmp, moderate) — a real, confirmed CVE but a generic email library with no vibe-coding-specific
angle, thin enough to skip per the routine out-of-audience-scope rule. All external citations in the new/updated
advisories passed `tools/check-external-links.py` (0 flagged of 74 checked across the three files). No
source-priority decay beyond the routine single source this run (60-day threshold).

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
