---
id: 2026-09-omniroute-acp-agent-unauth-rce
title: "OmniRoute (66K-star self-hosted AI gateway) — unauthenticated RCE through the custom ACP agent endpoint when requireLogin is off (CVE-2026-88062, CVSS 9.5–10.0); vendor, NVD and the advisory database disagree on which version is fixed"
date_disclosed: 2026-09-03
last_updated: 2026-09-14
severity: critical
status: patched
ecosystems: [npm, ai-gateways, llm-routers, self-hosted]
tools_affected: [omniroute, "AI coding agents configured to route model calls through a self-hosted OmniRoute", "ACP (Agent Client Protocol) agent integrations"]
tags: [cve, rce, missing-authentication, code-injection, llm-router, ai-gateway, acp, credential-theft, version-discrepancy]
---

## TL;DR
**OmniRoute** — an MIT-licensed, self-hosted AI gateway that fronts "352+ providers" behind one OpenAI-compatible endpoint (66,000+ GitHub stars) — let anyone who could reach it register a custom **ACP (Agent Client Protocol) agent** whose `binary` and `versionCommand` it then executed with `execFileSync()`. The only check was that the first token of `versionCommand` matched `binary`, and both were attacker-supplied, so `binary: "node", versionCommand: "node -e …"` is arbitrary code execution in the gateway container. With `requireLogin=false` (or a fresh install with no management password yet) it is **unauthenticated**: one HTTP request. A gateway holds every provider key you gave it. **CVE-2026-88062**, CVSS 4.0 **9.5** per the vendor advisory, **10.0** per the GitLab mirror. The vendor page says "update to 3.8.49"; NVD says 3.8.49 is affected; the advisory-database copy says ≤ 3.8.50 with no fix; the fix PR merged into the 3.8.50 branch. Run the latest release (3.8.51 per the repo) **and** turn `requireLogin` on.

## What happened

OmniRoute's `POST /api/acp/agents` registers a custom ACP agent. The request body carries the agent's `binary` and a `versionCommand` used to probe its version; the handler validated only that the command's first token equalled the binary name, then called `refreshAgentCache()` → `detectAgent()` → `execFileSync(probe.command, probe.args)`. Because the check compares two attacker-controlled strings, an interpreter name plus an eval flag passes it (`node -e`, and by the same logic any interpreter with an inline-code switch), and the code runs as the Node.js process inside the OmniRoute container.

Two authentication properties turned this from "authenticated RCE" into "one request from the internet":

- When `requireLogin=false`, `isAuthenticated()` treats anonymous requests as authenticated.
- `/api/acp/` is in neither `LOCAL_ONLY_API_PREFIXES` nor `SPAWN_CAPABLE_PREFIXES`, so the local-only policy that gates other spawn-capable routes never blocks it before the anonymous-allow branch.

A fresh bootstrap install with no management password configured is in the same state. With `requireLogin=true` and credentials set, exploitation needs a valid login.

**Impact.** Full compromise of the gateway container with the Node process's privileges. For this repo's readers the point is what the container holds: OmniRoute's job is to store your OpenAI/Anthropic/Google/… provider keys and route agent traffic through them, so a compromised gateway is a compromised key ring plus a man-in-the-middle position on every model call — the exact shape of the [malicious-LLM-router research](2026-04-llm-router-malicious-intermediary-attacks.md) already tracked here, now as a CVE in a self-hosted router rather than a hostile third-party one. The same fix PR also moved `/api/db-backups` (SQLite dumps containing API keys) behind authentication, closed an uppercase-path authentication bypass (`/V1/…`, `/CHAT`, `/MODELS`), and added a `chatgpt-web-codex-doctor` endpoint to the spawn-veto patterns.

**Which version is fixed — four sources, three answers.** Recorded here rather than resolved, per this repo's rule for version-number disagreements:

| Source | Affected | Fixed |
|---|---|---|
| Vendor advisory page ([GHSA-hf57-cqmx-p4gr](https://github.com/diegosouzapw/OmniRoute/security/advisories/GHSA-hf57-cqmx-p4gr), published 2026-09-03, reporter c111mb3r) | "before 3.8.49" | "Update to version 3.8.49 or later" |
| NVD record (CNA: GitHub; published 2026-09-10) | "3.8.49 and earlier" | — (references fix commit `6082924` and [PR #11028](https://github.com/diegosouzapw/OmniRoute/pull/11028)) |
| GitHub Advisory Database copy of the same GHSA | ≤ 3.8.50 | none listed |
| GitLab Advisory Database mirror | "all versions up to 3.8.50" | none |

The fix PR (#11028, "ACP version probe hardening") **merged 2026-08-21 into `release/v3.8.50`**; 3.8.49 was published to npm on **2026-07-30**, three weeks *before* the merge, so the vendor page's "3.8.49" cannot be the version carrying this PR. 3.8.50 reached npm on 2026-08-28 and its release notes do not mention the fix; the repository README shows v3.8.51 as current. **Reading:** treat 3.8.49 as vulnerable, 3.8.50 as the first release that plausibly contains the fix, and verify on your own instance — the advisory-database "no patched version" line means automated scanners will keep flagging every version until someone updates the record. Status here is `patched` because the vendor's own advisory states a fixed version and a merged fix exists; the caveat is which number.

## Am I affected?

```bash
npm ls -g omniroute 2>/dev/null; docker images | grep -i omniroute   # version <= 3.8.49 is vulnerable by every source
# Is login required?  (settings/env vary by install — look for requireLogin)
grep -rn 'requireLogin' ~/.omniroute* /etc/omniroute* 2>/dev/null
# Is the gateway reachable beyond loopback?
ss -tlnp 2>/dev/null | grep -i node
```

You are affected if you ran OmniRoute ≤ 3.8.49 (and possibly 3.8.50) reachable by anyone — a LAN, a Tailscale mesh, a cloud VM — with `requireLogin=false`, or if the instance was ever left in its bootstrap state before a management password was set. Because the endpoint was not gated by the local-only policy, "it's only bound to my home network" is not a boundary if any browser on that network can be pointed at it.

## If you are affected

1. Upgrade to the latest release (3.8.51 per the repo as of 2026-09-14) and set `requireLogin=true` with a real management password.
2. Treat **every provider API key the gateway held as exposed** and rotate it at the provider — OpenAI, Anthropic, Google, and every free-tier provider it was configured for. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
3. Check the container for added ACP agents (`/api/acp/agents` listing), unexpected processes, and modified SQLite state; the same PR closed an unauthenticated database-backup route, so assume the backup was readable too.
4. → [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md) — a router that holds keys for 352 providers is a single point of total loss; scope each upstream key to what the gateway needs and cap spend.
- [Supply-chain attack surface](../prevention/supply-chain-attack-surface.md)
- Never run an AI gateway with login disabled, even "just locally": the [DeepSeek Harness](2026-09-deepseek-harness-host-header-sandbox-escape.md), [NemoClaw/Ollama](2026-08-nvidia-nemoclaw-openshell-cve-batch.md) and [MCP bind-all-interfaces](2026-08-agent-framework-mcp-cve-batch.md) entries are the same lesson.

## Sources
- [OmniRoute — GHSA-hf57-cqmx-p4gr: OmniRoute ACP Custom-Agent Remote Code Execution (RCE)](https://github.com/diegosouzapw/OmniRoute/security/advisories/GHSA-hf57-cqmx-p4gr) — vendor advisory, fetched 2026-09-14: mechanism (`execFileSync` via `refreshAgentCache`/`detectAgent`), the `requireLogin=false`/bootstrap precondition, the `LOCAL_ONLY_API_PREFIXES` omission, "before 3.8.49 / update to 3.8.49," published 2026-09-03, reporter c111mb3r.
- [GitHub Advisory Database — GHSA-hf57-cqmx-p4gr (CVE-2026-88062)](https://github.com/advisories/GHSA-hf57-cqmx-p4gr) — fetched 2026-09-14: CVSS 4.0 9.5, "≤ 3.8.50, no patched version," CWE-306/CWE-94.
- [NVD — CVE-2026-88062](https://nvd.nist.gov/vuln/detail/CVE-2026-88062) — fetched via the NVD API 2026-09-14: published 2026-09-10, CNA GitHub, CVSS 4.0 9.5 CRITICAL, "3.8.49 and earlier," references to the fix commit and PR #11028.
- [GitLab Advisory Database — CVE-2026-88062 (omniroute)](https://advisories.gitlab.com/npm/omniroute/CVE-2026-88062/) — fetched 2026-09-14: mirror stating CVSS 10.0, "all versions up to 3.8.50," no fixed version.
- [OmniRoute PR #11028](https://github.com/diegosouzapw/OmniRoute/pull/11028) — fetched 2026-09-14: merged 2026-08-21 into `release/v3.8.50`; ACP version-probe hardening, `/api/db-backups` moved behind auth, case-insensitive path-auth fix, spawn-veto pattern alignment.
- [OmniRoute — Releases](https://github.com/diegosouzapw/OmniRoute/releases) — fetched 2026-09-14: v3.8.50 dated 2026-08-26, v3.8.49 2026-07-30; release notes do not mention the CVE.
- [OmniRoute — repository README](https://github.com/diegosouzapw/OmniRoute) — fetched 2026-09-14: product description, "352+ providers," 66,000+ stars, v3.8.51 shown as latest; README does not document a `requireLogin` default.
- [npm registry — `omniroute`](https://registry.npmjs.org/omniroute) — queried 2026-09-14 (`npm view omniroute time`): 3.8.49 published 2026-07-30, 3.8.50 published 2026-08-28 (latest on npm).
