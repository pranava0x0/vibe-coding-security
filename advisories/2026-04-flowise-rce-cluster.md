---
id: 2026-04-flowise-rce-cluster
title: "Flowise RCE cluster — CVE-2025-59528 actively exploited + April 2026 Agent-node cluster (CVE-2026-41265 et al.)"
date_disclosed: 2026-04-07
last_updated: 2026-09-16
severity: critical
status: patched
ecosystems: [npm, ai-agents, llm-workflow]
tools_affected: [flowise, flowiseai]
tags: [cve, rce, prompt-injection, ai-agent-framework, active-exploitation, decorator-as-documentation]
---

## TL;DR
**Flowise** — the drag-and-drop LLM workflow builder (~38K GitHub stars, **12,000–15,000 internet-exposed instances**) — has two overlapping RCE problems shipping concurrently. **(1) [CVE-2025-59528](https://www.sentinelone.com/vulnerability-database/cve-2025-59528/) (CVSS 10.0)** — unauthenticated code injection in the **CustomMCP node** where `mcpServerConfig` is `eval`'d as JavaScript; under **active in-the-wild exploitation since April 2026** ([VulnCheck via THN](https://thehackernews.com/2026/04/flowise-ai-agent-builder-under-active.html)). **(2) April 2026 Agent-node cluster** — **CVE-2026-41265, CVE-2026-41264, CVE-2026-41268, CVE-2026-41138, CVE-2026-40933** (CVSS 9.2 each) — prompt-injection-to-RCE in the **Airtable / CSV / generic Agent nodes** that run **LLM-generated Python** with no sandbox. All fixed in **Flowise 3.1.0** (CVE-2025-59528 fix line is **3.0.6 → 3.1.1**). If you exposed Flowise to the public internet on any vulnerable version, treat the host as compromised and rotate every upstream LLM/cloud key the platform held.

## What happened
Flowise stores upstream-provider API keys for OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, Cohere, Mistral, and similar — the same "central credentials cache" problem as [LiteLLM](2026-04-litellm-sql-injection.md), but for LLM-workflow-building rather than proxying. Two distinct vulnerability tracks landed against Flowise in the April → May 2026 window:

**Track 1 — CVE-2025-59528 (CVSS 10.0).** Disclosed originally in September 2025 ([SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-59528/)), the `CustomMCP` node accepts a user-supplied `mcpServerConfig` string and parses it without security validation, executing arbitrary JavaScript with full Node runtime privileges (including `child_process`, `fs`). Fix shipped in **3.0.6**. VulnCheck observed the **first confirmed in-the-wild exploitation from a Starlink IP in early April 2026** ([The Hacker News, 2026-04-08](https://thehackernews.com/2026/04/flowise-ai-agent-builder-under-active.html); [Cybersecurity News](https://cybersecuritynews.com/flowise-ai-agent-builder-vulnerability-exploited/); [Lab Space CSA Research Note](https://labs.cloudsecurityalliance.org/research/csa-research-note-flowise-mcp-rce-exploitation-20260409-csa/)); internet scans count **12,000–15,000 exposed instances**, of which many remain unpatched. [BleepingComputer](https://www.bleepingcomputer.com/news/security/max-severity-flowise-rce-vulnerability-now-exploited-in-attacks/) and [SC Media](https://www.scworld.com/brief/active-exploitation-of-max-severity-flowise-bug-threatens-broad-compromise) covered active exploitation; [CSO Online](https://www.csoonline.com/article/4155680/hackers-exploit-a-critical-flowise-flaw-affecting-thousands-of-ai-workflows.html) framed downstream impact.

**Track 2 — April 2026 Agent-node cluster.** GitHub Security Advisories disclosed five chainable RCEs in Flowise's various **Agent nodes** (all fixed in **3.1.0**):

- **[CVE-2026-41265](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-3gcm-f6qx-ff7p) (CVSS 9.2)** — Airtable Agent: `Airtable_Agents.run()` evaluates an LLM-generated Python script with no sandbox. An unauthenticated attacker who can send prompts to a chatflow using this node can prompt-inject the LLM into emitting Python that executes attacker commands on the host.
- **[CVE-2026-41138](https://github.com/advisories/GHSA-f228-chmx-v6j6)** — Airtable Agent RCE via lack of input verification using `Pandas`.
- **CVE-2026-41264, CVE-2026-41268** — sibling Agent-node RCEs.
- **[CVE-2026-40933](https://www.sentinelone.com/vulnerability-database/cve-2026-40933/)** — Flowise generic RCE.
- **CVE-2026-41137** — CSV Agent RCE.
- **CVE-2026-41269** — File Upload RCE.

The Airtable Agent class is the cleanest worked example of the **decorator-as-documentation** pattern already seen in [Microsoft Semantic Kernel](2026-05-semantic-kernel-rce.md): the SDK annotation marks a function as "agent tool" and the developer's intuition is that the framework provides isolation. The framework does not — `eval`-ing LLM output as Python on the server gives any chatflow caller a one-prompt path to RCE.

This adds Flowise to the running cluster of **"AI/data tools shipping unauthenticated RCE primitives"** — siblings: [Langflow CVE-2026-33017](2026-03-langflow-rce.md), [PraisonAI CVE-2026-44338](2026-05-praisonai-auth-bypass.md), [Marimo CVE-2026-39987](2026-04-marimo-notebook-rce.md), [LiteLLM CVE-2026-42208](2026-04-litellm-sql-injection.md).

## Am I affected?

```bash
# Check Flowise version (Docker or npm install)
docker ps --format '{{.Image}}\t{{.Names}}' | grep -i flowise
docker exec <container> npm list -g flowise 2>/dev/null | grep flowise

# Or self-hosted via npm
npx flowise --version 2>/dev/null

# Internet-exposed?
ss -tlnp 2>/dev/null | grep -E ':3000|:3001'  # default Flowise ports
```

If `Version < 3.0.6` → vulnerable to **CVE-2025-59528** (CustomMCP code injection).
If `Version < 3.1.0` → vulnerable to **CVE-2026-41264 / CVE-2026-41265 / CVE-2026-41268 / CVE-2026-41138 / CVE-2026-40933 / CVE-2026-41137 / CVE-2026-41269** (Agent-node prompt-injection RCEs).
**Recommended minimum: `3.1.1`** (CVE-2025-59528 follow-up hardening).

If any of those versions was reachable from the public internet (or from any network you don't fully trust), treat the host as compromised. **Flowise stores upstream LLM provider keys** — assume those keys, and any cloud-IAM credential wired into a chatflow, are exfiltrated.

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2025-59528` (CVSS 10.0, CustomMCP), `CVE-2026-41265` (CVSS 9.2, Airtable), `CVE-2026-41264`, `CVE-2026-41268`, `CVE-2026-41138`, `CVE-2026-40933`, `CVE-2026-41137`, `CVE-2026-41269` |
| Affected versions | `< 3.0.6` (CVE-2025-59528); `< 3.1.0` (Agent-node cluster) |
| Fixed version | `3.0.6` (CVE-2025-59528 baseline) → upgrade to **`3.1.1`** |
| GHSA (Airtable) | `GHSA-3gcm-f6qx-ff7p`, `GHSA-f228-chmx-v6j6` |
| Active exploitation | yes (April 2026, first VulnCheck telemetry from a Starlink IP) |
| Exposed instances | ~12,000–15,000 on the public internet |
| Vulnerable nodes | `CustomMCP`, `Airtable_Agents`, `CSV_Agent`, generic Agent nodes, File Upload |
| Vulnerable primitive | `eval`/`pickle`/`exec`-style execution of LLM-generated code with no sandbox |

## If you are affected
1. **Upgrade immediately** to **Flowise 3.1.1** or later.
2. **Treat the host as compromised** if it was internet-facing in any vulnerable version. Specifically:
   - **Rotate every upstream LLM provider key** stored in Flowise — OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, Cohere, Mistral, Google.
   - **Rotate every cloud IAM credential** wired into a chatflow (Airtable PATs, GitHub PATs, AWS access keys, etc.).
   - **Audit each provider's usage logs** during the exposure window for unexpected request volume, model-arbitrage spend, or geographic shifts in caller IP.
3. **Bind Flowise off the public internet** going forward (127.0.0.1 + auth-required reverse proxy, Tailscale, Cloudflare Tunnel, or VPC-only).
4. **Disable any unused Agent node** in the deployment — every additional Agent-node class is a fresh prompt-injection-to-RCE primitive until further notice.
5. Audit any chatflow definitions for attacker-injected nodes — an RCE that ran on your Flowise host could have rewritten the chatflow registry to plant a persistent backdoor.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Never expose an LLM-workflow-builder admin UI to the public internet — same rule as [LiteLLM](2026-04-litellm-sql-injection.md), [Langflow](2026-03-langflow-rce.md), [PraisonAI](2026-05-praisonai-auth-bypass.md), [Marimo](2026-04-marimo-notebook-rce.md). The default-bind for these tools should be `127.0.0.1`.
→ Treat any "Agent node that runs LLM-generated code" as a **prompt-injection-to-RCE primitive** until the vendor provides a hard, audited sandbox boundary. The decorator/SDK annotation is documentation, not a security control. (Same pattern as [Microsoft Semantic Kernel `[KernelFunction]`](2026-05-semantic-kernel-rce.md).)
→ Treat **disclosure-to-exploit as < 36 hours** for any AI-workflow CVE; CVE-2025-59528 went exploited ~6 months after disclosure because attackers needed time to weaponize, but newer Agent-node CVEs will move faster now that the recipe is public.

## Update — 2026-09: a ~17-CVE second wave (two more Custom-MCP-node RCEs), fixed in 3.1.4 — and the repo is now archived, so 3.1.4 is likely the last release

Between **2026-09-10 and 2026-09-15** a large second batch of Flowise CVEs was published — one from MITRE, most from **VulnCheck** as CNA — all against versions **≤ 3.1.3** and all marked **fixed in 3.1.4** (npm `flowise@3.1.4`, released **2026-07-29**; confirmed via the registry). Two land in the same **Custom MCP node** that caused the original CVE-2025-59528, and both are authenticated RCE:

- **[CVE-2026-91931](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-vcwp-f9rq-3887) (CVSS 9.0, GHSA-vcwp-f9rq-3887)** — the Custom MCP node's allowlist permits **`npx`** while blocking only specific flags, so an authenticated attacker sets `mcpServerConfig` to an attacker-named npm package (`npx shx touch …` is the vendor's PoC) and `npx` installs and runs it on the server (CWE-78). Fixed **3.1.4**. Credit DavidCarliez.
- **[CVE-2026-91932](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x7x8-95gh-42xm) (CVSS 9.0, GHSA-x7x8-95gh-42xm)** — `validateMCPServerConfig()` validates command, args and env but **ignores the `cwd` parameter**, so a clean filename in `args` passes while a poisoned working directory supplies the payload. Fixed **3.1.4**. Credit biecho / Diego Meyer.

The rest of the wave (VulnCheck, published 2026-09-12/15, all fixed 3.1.4) is a cross-tenant-authorization and SSRF cluster: **CVE-2026-91929 / -91930 / -91933** (cross-tenant workspace/org takeover — delete workspaces, self-invite as org owner, reach other workspaces' tools), **CVE-2026-90533** (any org member reads the owner's **bcrypt hash and temp tokens** via `GET /api/v1/organizationuser`), **CVE-2026-90534** (cross-workspace credential IDOR via `node-load-method`), **CVE-2026-91935 / -91938** (SSRF and LLM-provider-**API-key exfiltration** via chat-model `baseURL` and Cheerio/Playwright/Puppeteer document loaders, reaching cloud metadata), **CVE-2026-91937** (unauthenticated NoSQL injection in the MongoDB memory node reads other users' chat history), **CVE-2026-91934** (arbitrary file write via the SQL Database Chain SQLite path), **CVE-2026-91936** (CI workflow script injection stealing AWS/Docker Hub tokens), and **CVE-2026-90535** (unauth DoS). Separately, **CVE-2026-52098** (MITRE, CVSS 9.8) reports RCE via `POST /api/v1/prediction/<flowId>` against **3.1.2**, and **CVE-2026-90580** (VulDB, low) an Evaluations-endpoint SSRF in ≤ 3.0.2 (fixed 3.1.3, exploit public).

**The load-bearing caveat: the FlowiseAI/Flowise repository shows as archived on 2026-08-13** (noted in advisory GHSA-9gvv-qjj3-2p6g), and npm carries no release past **3.1.4** (2026-07-29). So while VulnCheck marks this whole batch "fixed in 3.1.4," Flowise is effectively **unmaintained** — CVE-2026-52098's fix version is not stated, and no future CVE here will get a patch. Treat exposure as the only control you still own: **get Flowise off the public internet, require auth in front of it, and disable the Custom MCP node** if you cannot migrate off the platform. This is the same advice as the original entry, now with no vendor backstop behind it.

## Sources
- [GitHub Security Advisory GHSA-vcwp-f9rq-3887 — CVE-2026-91931 Flowise Custom MCP npx RCE](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-vcwp-f9rq-3887) — fetched 2026-09-16; CVSS 9.0, fixed 3.1.4, `npx`-package execution PoC.
- [GitHub Security Advisory GHSA-x7x8-95gh-42xm — CVE-2026-91932 Flowise Custom MCP `cwd` bypass RCE](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x7x8-95gh-42xm) — fetched 2026-09-16; CVSS 9.0, fixed 3.1.4, unvalidated `cwd` parameter.
- [NVD — CVE-2026-52098](https://nvd.nist.gov/vuln/detail/CVE-2026-52098) — fetched 2026-09-16 via the NVD API; MITRE CNA, CVSS 9.8, RCE via `/api/v1/prediction/<flowId>` in 3.1.2.
- [VulnCheck — Flowise before 3.1.4 remote code execution via Custom MCP npx](https://www.vulncheck.com/advisories/flowise-before-3.1.4-remote-code-execution-via-custom-mcp-npx) — fetched 2026-09-16; CNA record for CVE-2026-91931 and the wider 3.1.4 batch.
- Registry check (2026-09-16): `npm view flowise time` — latest release `3.1.4` (2026-07-29), no `3.1.5`; repository archived 2026-08-13 per GHSA-9gvv-qjj3-2p6g.

## Sources — original April 2026 cluster
- [GitHub Security Advisory GHSA-3gcm-f6qx-ff7p — CVE-2026-41265 Flowise Airtable Agent RCE](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-3gcm-f6qx-ff7p) — vendor advisory.
- [GitHub Advisory Database — CVE-2026-41138 Flowise Airtable Agent RCE via Pandas](https://github.com/advisories/GHSA-f228-chmx-v6j6) — sibling CVE.
- [SentinelOne — CVE-2025-59528 Flowise RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2025-59528/) — CVSS 10.0 CustomMCP RCE catalog entry.
- [SentinelOne — CVE-2026-40933 Flowise RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-40933/) — sibling CVE catalog entry.
- [The Hacker News — Flowise AI Agent Builder Under Active CVSS 10.0 RCE Exploitation; 12,000+ Instances Exposed (2026-04-08)](https://thehackernews.com/2026/04/flowise-ai-agent-builder-under-active.html) — active exploitation reporting.
- [BleepingComputer — Max severity Flowise RCE vulnerability now exploited in attacks](https://www.bleepingcomputer.com/news/security/max-severity-flowise-rce-vulnerability-now-exploited-in-attacks/) — exploitation confirmation.
- [SC Media — Active exploitation of max severity Flowise bug threatens broad compromise](https://www.scworld.com/brief/active-exploitation-of-max-severity-flowise-bug-threatens-broad-compromise) — aggregator framing.
- [Cybersecurity News — Flowise AI Agent Builder Injection Vulnerability Exploited in Attacks, 15,000+ Instances Exposed](https://cybersecuritynews.com/flowise-ai-agent-builder-vulnerability-exploited/) — exposure scale.
- [CSO Online — Hackers exploit a critical Flowise flaw affecting thousands of AI workflows](https://www.csoonline.com/article/4155680/hackers-exploit-a-critical-flowise-flaw-affecting-thousands-of-ai-workflows.html) — downstream-impact framing.
- [Cloud Security Alliance Lab Space — Flowise CVSS 10.0 RCE: AI Agent Builders Under Attack (Research Note 2026-04-09)](https://labs.cloudsecurityalliance.org/research/csa-research-note-flowise-mcp-rce-exploitation-20260409-csa/) — research-note framing of the AI-agent-builder attack class.
- [Safe Security — No Credentials Required: How the Most Dangerous New CVEs Invite Themselves into Your Systems (2026-04-15)](https://safe.security/resources/blog/threat-research/most-dangerous-new-cves-april-15-2026/) — pre-auth RCE framing.
- [Tech Jack Solutions — Flowise (FlowiseAI) Vulnerability Rollup (2026-04-07)](https://techjacksolutions.com/scc-vendor-rollup/flowise-flowiseai-vulnerability-rollup-2026-04-07/) — vendor-rollup index.
- [Feedly — Latest Flowiseai Vulnerabilities](https://feedly.com/cve/vendors/flowiseai) — CVE tracker.
- [Threat Intelligence Network — CVE-2026-41265](https://cve.threatint.eu/CVE/CVE-2026-41265) — CVE detail.
