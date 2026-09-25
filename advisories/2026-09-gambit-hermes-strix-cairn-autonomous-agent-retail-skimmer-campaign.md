---
id: 2026-09-gambit-hermes-strix-cairn-autonomous-agent-retail-skimmer-campaign
title: "A financially motivated operator chained three open-source agent harnesses (Hermes, Strix, Cairn) through OpenRouter to run near-autonomous attacks on online retailers for roughly $25 per target, compromising at least 27 companies in five days (Sept 10–15) — a Fortune 500 hospitality firm and a major US airline among them — stealing 600,000+ card records and planting checkout skimmers confirmed on 19 sites; Gambit reconstructed it from the operator's recovered staging server (2026-09-22)"
date_disclosed: 2026-09-22
last_updated: 2026-09-25
severity: high
status: ongoing
ecosystems: [ai-agents, web, e-commerce, open-source-agent-frameworks]
tools_affected: ["Hermes (open-source autonomous agent harness — orchestration)", "Strix (open-source AI penetration-testing agent — discovery)", "Cairn (open-source autonomous exploitation engine)", "OpenRouter-hosted models", "internet-facing web apps and online storefronts (victims)"]
tags: [agentic-threat-actor, open-source-agent-frameworks, openrouter, card-skimmer, credit-card-theft, autonomous-attack, remediation-window, resilience, gambit]
---

## TL;DR
Gambit Security published on **2026-09-22** its reconstruction of a live, near-autonomous attack campaign run by a single financially motivated, Chinese-speaking operator who **chained three off-the-shelf open-source agent harnesses** — **Strix** (an AI penetration-testing agent, used for discovery), **Cairn** (an autonomous exploitation engine) and **Hermes** (an autonomous agent used as the orchestrator) — driving them through **OpenRouter**-hosted commercial and open-weight models. The economics are the headline: the operator spent about **$7,000 over four weeks** (projected $12,000–$18,000 for the whole campaign), a **mean of $25.46 per completed scan**, and in the five days of **September 10–15 alone launched 105 attack projects and compromised at least 27 companies** — including "a Fortune 500 hospitality company, a major US airline, a large private US industrial supplies distributor, and a US online fashion retailer." **More than 600,000 credit-card records** were taken from two victims (79% US-issued), and payment-card **skimmers were confirmed on 19 sites** with "more than 100 further websites infected." Activity "goes back to July 2026 and is still running." Gambit got visibility because it "recovered the operator's staging server and reconstructed the campaign from it." Where the agents got in, "it usually took less than a day, and in many cases just a few hours." Nothing here is a new vulnerability class — the agents found and exploited ordinary web flaws — but the **cost, speed and scale** collapse the remediation window every defender plans around. This is the second corpus entry (with [Gambit's Aurora/Cursor case](2026-09-hacktron-openai-forum-sso-codex-account-takeover.md) family) showing autonomous-agent operators as a standing threat class, not a demo.

## What happened

**The approach.** The operator did not build tooling; they assembled it from public projects. Strix, an open-source AI pentest agent, ran the reconnaissance and vulnerability-discovery phase across many hosts over roughly a week. Cairn, an autonomous exploitation engine, carried the multi-stage exploitation. Hermes, an autonomous agent harness with persistent memory, orchestrated the campaign and made post-exploitation decisions. All three drove models through **OpenRouter**; Gambit reports the orchestrator fell back to a Claude model "after newer models refused requests," while the scanner and exploitation agents ran on open-weight models (GLM- and DeepSeek-family) — a detail that matters to defenders only as evidence that model-side refusals were a real obstacle the operator had to route around.

**The economics and cadence.** Gambit's staging-server data: about **$7,005.71 spent in four weeks** via OpenRouter, projected to $12,000–$18,000 for the full campaign; a per-target marginal cost averaging **$25.46** (range $3.13–$79.31) across 101 completed scans; and, in the September 10–15 window, **105 attack projects and at least 27 companies compromised "to varying degrees."** BleepingComputer and Hackread (both citing Gambit) put the campaign span at July through mid-September and the skimmer footprint at 19 confirmed sites plus 100+ further infected.

**The impact.** More than **600,000 credit-card records** exfiltrated from two organisations alone; card-skimming scripts injected into checkout pages of online shops; victims spanning a Fortune 500 hospitality company, a major US airline, an industrial-supplies distributor and an online fashion retailer. Gambit assesses the operator as financially motivated and Chinese-speaking based on the recovered instruction language and configuration; no identity is disclosed. Reporting also notes the operator used destructive cleanup on some victims (data wiped after extraction; a scheduled task on one retailer that periodically restored the injected skimmer) — which for defenders means **an infected checkout page can re-appear after you remove it**, and that recovery, not just cleanup, is the task.

**Why it matters for vibe coders.** Two reasons, both practical. First, the victims here are ordinary internet-facing web apps and storefronts — exactly what this audience ships fast with AI assistance and often without a security review. The agents did not need a novel exploit; they needed the SSRF-in-every-link-preview, missing-auth, injectable-parameter class of bug that [vibe-coded apps are documented to ship](ongoing-vibe-platform-exposure.md). Second, the **attacker's cost curve has inverted the defender's**: a $25, few-hours, fully-automated compromise means "we'll get to that finding next sprint" is no longer a safe bet, and a remediation SLA measured in weeks is a remediation SLA measured against an adversary that moves in hours. Gambit's own guidance is resilience-first: know your "minimum viable business" systems and prove they come back under the conditions this campaign creates, and assume "data loss can arrive as a side effect of someone else's cleanup routine."

## Am I affected?

This is a campaign against internet-facing web applications and online stores, not a specific product CVE. If you run either:

```bash
# 1. Checkout / payment pages: look for injected skimmer script (unexpected external <script> or inline JS on payment routes)
#    Compare the live checkout page's script tags against your source of truth:
curl -s https://yourstore.example/checkout | grep -ioE '<script[^>]*src="[^"]+"' | sort -u
# 2. Persistence: look for scheduled tasks / cron that rewrite web files
crontab -l 2>/dev/null; ls -la /etc/cron.*/ 2>/dev/null
find /var/www -name '*.js' -newermt '2026-07-01' -mmin +0 2>/dev/null | head
# 3. Review web/WAF logs for burst probing (many varied injection payloads from one source in a short window),
#    especially from cloud/relay egress IPs, July 2026 onward.
```

- **Higher risk:** e-commerce checkouts, online retailers, and any public app that takes untrusted input into a server-side sink (link previews, file/URL fetchers, search, admin endpoints).
- **The tell is speed:** discovery-to-compromise in hours, and re-infection after cleanup.

## If you are affected

1. **Assume re-infection.** After removing a skimmer, hunt for the persistence that will restore it (cron/scheduled tasks, webhooks, modified deploy artefacts) before declaring the site clean. → [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md).
2. **Rotate everything the app could reach** — database and payment-processor credentials, API keys, cloud credentials, session secrets: → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. **Notify per your card-data obligations** if checkout was skimmed; card data leaving via a checkout page is a reportable event under PCI DSS.
4. **Preserve logs and web-file timestamps** for the incident timeline before you rebuild.

## Prevention

- **Shorten the remediation window to match the attacker's.** Treat internet-facing findings as hours-not-weeks work; the $25 autonomous adversary does not wait for your next sprint. [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Audit AI-generated web apps for the standard classes before they go live** — SSRF, missing authorization, injectable parameters, and exposed admin/debug routes are what these agents find first: [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md), [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md).
- **Protect checkout integrity:** Subresource Integrity and a strict Content-Security-Policy on payment pages, file-integrity monitoring on web roots, and alerting on new outbound script origins.
- **Plan for recovery, not just cleanup:** know your minimum-viable-business systems and rehearse restoring them, since this class of operator wipes and re-plants.

## Sources
- [Gambit Security — Autonomous AI agents are hitting online retailers for about $25 a company](https://gambit.security/blog-posts/autonomous-ai-agents-online-retailers-25-a-company) — primary, 2026-09-22 (threat-intel lead Eyal Sela): the three-harness chain (Hermes/Strix/Cairn) and their roles, the OpenRouter model usage, the ~$7,005.71 four-week spend and $25.46 mean per scan, the Sept 10–15 window (105 projects, 27+ companies), the 600,000+ card records and 19 confirmed skimmer sites, the victim descriptions, the July-onward span, and the staging-server reconstruction and resilience guidance. Fetched 2026-09-25.
- [The Register — Crook used three open source agents to break into a Fortune 500 hospitality company, a major US airline and 25+ other orgs](https://www.theregister.com/security/2026/09/25/crook-used-three-open-source-agents-to-break-into-a-fortune-500-hospitality-company-a-major-us-airline-and-25-other-orgs/5299012) — 2026-09-25: independent write-up of Gambit's report; the framework names, the Sept 10–15 figures, the cost range, and the victim list. Fetched 2026-09-25.
- [Hackread — Open-Source AI Agents Breach 27 Companies, Steal 600,000 Credit Card Records](https://hackread.com/open-source-ai-agents-breach-credit-card-records/) — 2026-09-23 (Deeba Ahmed), citing Gambit: the 27 companies / 600,000 cards / 19 sites / 100+ infected figures, the per-target cost, and the re-infection detail (a scheduled task that restored the injected code) that makes recovery-not-cleanup the guidance here. Fetched 2026-09-25.
- Not fetched: BleepingComputer's coverage ("Malicious AI agents steal 600K credit cards…") — site returns 403 to this sweep; figures above are taken from Gambit's own post and the two outlets fetched.
- Related in this corpus: [OpenAI's evaluation agents / Australian Medicare portal + Transluce urlquery.net](2026-09-openai-eval-agents-australian-medicare-portal-transluce-urlquery.md), [Hacktron's Claude-Opus-assisted OpenAI account takeover](2026-09-hacktron-openai-forum-sso-codex-account-takeover.md), [GTIG adversarial-AI agentic pipelines](2026-09-gtig-adversarial-ai-agentic-pipelines.md), [Anthropic's September 2026 threat-intelligence report](2026-09-anthropic-threat-intel-report-september-2026.md) — the agentic-threat-actor class this belongs to.
