---
id: 2026-10-gitlab-ai-gateway-duo-flow-prompt-template-sandbox-escape
title: "GitLab AI Gateway CVE-2026-90970 (CVSS 9.9): an authenticated user with Duo Agent Platform access escapes the custom-flow prompt-template sandbox through a crafted flow configuration and runs commands on the self-hosted AI Gateway — the second 9.9 template-engine escape in the same component this year (CVE-2026-1868, February); fixed 19.2.4 / 19.3.2 / 19.4.1, published 2026-10-02; GitLab.com and Dedicated already patched"
date_disclosed: 2026-10-02
last_updated: 2026-10-04
severity: critical
status: patched
ecosystems: [gitlab, ai-agents, self-hosted, python]
tools_affected: ["GitLab AI Gateway (self-hosted) 18.1.6 – 19.2.3, 19.3.0 – 19.3.1, 19.4.0", "GitLab Duo Agent Platform custom flows", "any self-managed GitLab with a self-hosted AI Gateway serving Duo"]
tags: [cve, gitlab, ai-gateway, duo-agent-platform, prompt-template, template-injection, sandbox-escape, rce, cwe-1336, self-hosted, hackerone]
---

## TL;DR

GitLab published a **critical AI Gateway patch release on 2026-10-02** for **CVE-2026-90970 (CVSS 3.1 9.9, `AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`, CWE-1336)**: "an authenticated user with Duo Agent Platform access could have escaped the prompt template sandbox via a specially crafted flow configuration, resulting in arbitrary command execution on the AI Gateway." Affected: **AI Gateway 18.1.6 through 19.2.3, 19.3.0–19.3.1 and 19.4.0**; fixed **19.2.4, 19.3.2, 19.4.1**. **GitLab.com and GitLab Dedicated are already patched**; self-managed instances that are *not* running their own AI Gateway are not affected; everyone running a **self-hosted AI Gateway** should upgrade now. Reporter: `invisiblemeerkat` via HackerOne. This is the **second 9.9 in the same component's template handling this year** — CVE-2026-1868 (2026-02-09, "insecure template expansion of user supplied data via crafted Duo Agent Platform Flow definitions," fixed 18.6.2 / 18.7.1 / 18.8.1) was the first, and the new affected range begins at 18.1.6, so the February fix did not close the class. The AI Gateway is the box that holds the model-provider credentials and the agent-execution plane for the whole instance.

## What happened

**The component.** GitLab Duo's agentic features — Duo Agent Platform *flows*, which are user-defined multi-step agent workflows — are served by the **AI Gateway**, a Python service GitLab runs for GitLab.com and that self-managed customers can host themselves to keep traffic in their own environment. Flow definitions carry prompt templates; the gateway renders them. The patch post names the bug "Improper Neutralization issue in custom flow prompt template impacts AI Gateway" and classes it CWE-1336 (improper neutralization of special elements used in a template engine).

**The bug.** A flow configuration crafted by someone who already has Duo Agent Platform access (PR:L) escapes the template sandbox and executes commands on the gateway host. No user interaction, network-reachable, scope-changed — the 9.9 is the gateway's trust position, not the difficulty. The Hacker News' 10-02 write-up adds nothing beyond the vendor text but confirms the self-hosted-only exposure and the HackerOne credit.

**The precedent.** [CVE-2026-1868](https://www.incibe.es/en/incibe-cert/early-warning/vulnerabilities/cve-2026-1868) (published 2026-02-09, 9.9, found internally by GitLab's Joern Schneeweisz) was "insecure template expansion of user supplied data via crafted Duo Agent Platform Flow definitions" in the Duo Workflow Service of the same gateway, affecting 18.1.6 → 18.8.0, "could be used to cause Denial of Service or gain code execution on the Gateway." Eight months later the same flow-definition surface yields a second code-execution escape with the same score and the same starting version. Two independent fixes for one trust boundary is the pattern this corpus names "vendor patched ≠ patched": the first patch closed a path, not the class.

**Why vibe coders should care.** Self-managed GitLab with a self-hosted AI Gateway is the "keep our code and our model traffic on-prem" deployment — exactly the configuration security-conscious teams choose. The gateway holds the API keys to the model providers, brokers every Duo chat, code suggestion and agent run, and in the Agent Platform executes flows against repositories. A developer account that can author a flow is the lowest tier of Duo access; from there this bug reaches the host. This is distinct from, and worse than, the two 9.9 *GitLab* (not gateway) RCEs in the [19.4.1 patch on 09-24](2026-09-gitlab-19-4-1-regex-rce-duo-mcp-batch.md); it is the same release train (19.4.1) with a separate component version.

## Am I affected?

```bash
# Only self-hosted AI Gateway deployments are affected. Check the running gateway image/version:
docker ps --format '{{.Image}}' | grep -i 'ai-gateway'            # tag < 19.2.4 / 19.3.2 / 19.4.1 → affected
kubectl get deploy -A -o jsonpath='{..image}' | tr ' ' '\n' | grep -i 'ai-gateway'
# GitLab-side: Admin → Settings → General → AI-powered features → "Self-hosted AI Gateway URL" set? If not, you are on GitLab.com's gateway and already patched.
```

Affected if the gateway version is **18.1.6 ≤ v < 19.2.4**, **19.3.0–19.3.1**, or **19.4.0**.

## If you are affected

1. Upgrade the AI Gateway to **19.2.4, 19.3.2 or 19.4.1** (match your GitLab minor) using the self-hosted AI Gateway install docs.
2. Treat the gateway host as potentially compromised if any user with Duo Agent Platform access was untrusted: review flow definitions created since 2026-06 (18.1.6 era), gateway process logs, and outbound connections.
3. **Rotate the model-provider credentials** the gateway holds (Anthropic, Vertex, Bedrock, self-hosted model keys) and any GitLab tokens the gateway uses; see [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Restrict who can author Agent Platform flows until the fleet is patched.

## Prevention

- A template engine that renders user-authored agent definitions is a code-execution surface; sandbox it as code, not as text. Second escape in eight months says the boundary needs an architectural fix (separate process, no shell, no filesystem), not another filter.
- Run the AI Gateway with the least network reach it needs — it should talk to model providers and GitLab, nothing else — so an escape cannot pivot. [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- Subscribe to GitLab's **patch-releases feed** (`docs.gitlab.com/releases/patch-releases.xml`): AI Gateway patches are published as "other patches" outside the GitLab version train and are easy to miss.

## Sources

- [GitLab — AI Gateway Critical Patch Release: 19.2.4, 19.3.2, and 19.4.1](https://docs.gitlab.com/releases/patches/other-patches/patch-release-gitlab-ai-gateway-19-4-1-released/) — vendor post: CVE-2026-90970, Critical 9.9 with vector, "Improper Neutralization issue in custom flow prompt template impacts AI Gateway," affected and fixed ranges, HackerOne credit `invisiblemeerkat`, GitLab.com/Dedicated already patched, self-hosted gateway must upgrade. Fetched 2026-10-04. [GitLab patch-releases feed](https://docs.gitlab.com/releases/patch-releases.xml) — the entry dated 2026-10-02.
- [NVD API — CVE-2026-90970](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-90970) — CNA `cve@gitlab.com`, published 2026-10-02, CVSS 3.1 9.9, description quoted above. Queried 2026-10-04. [GitHub Advisory Database — GHSA-5295-vp56-jghq](https://github.com/advisories/GHSA-5295-vp56-jghq) — unreviewed mirror, CWE-1336, references the GitLab work item 628842 (not publicly readable at sweep time). Fetched 2026-10-04.
- [The Hacker News — GitLab Patches Critical Self-Hosted AI Gateway Flaw](https://thehackernews.com/2026/10/gitlab-patches-critical-self-hosted-ai.html) — 2026-10-02: independent report; names CVE-2026-1868 (February, 9.9) as the related earlier template-engine weakness. Fetched 2026-10-04.
- [INCIBE-CERT — CVE-2026-1868](https://www.incibe.es/en/incibe-cert/early-warning/vulnerabilities/cve-2026-1868) — the February record: "insecure template expansion of user supplied data via crafted Duo Agent Platform Flow definitions," 18.1.6 → 18.8.0, fixed 18.6.2 / 18.7.1 / 18.8.1, 9.9, internal finder. Surfaced by search; opened 2026-10-04.
- Related in this corpus: [GitLab 19.4.1 regex RCE + Duo/MCP batch (09-24)](2026-09-gitlab-19-4-1-regex-rce-duo-mcp-batch.md), [GitLab incoming-email token push (09-24)](2026-09-gitlab-incoming-email-token-push-to-main.md).
