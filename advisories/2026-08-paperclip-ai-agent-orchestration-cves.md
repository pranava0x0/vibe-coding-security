---
id: 2026-08-paperclip-ai-agent-orchestration-cves
title: "Paperclip AI agent orchestration platform — self-registration to unauthenticated RCE via malicious agent import (CVE-2026-41679, CVSS 10.0, plus 2 more)"
date_disclosed: 2026-08-05
last_updated: 2026-10-31
severity: critical
status: patched
ecosystems: [ai-agents, paperclip]
tools_affected: [paperclip]
tags: [rce, privilege-escalation, agent-orchestration, decorator-as-documentation, dns-rebinding]
---

## TL;DR
**Paperclip**, an open-source platform for managing autonomous AI agents at scale (operators "import companies" from portable YAML bundles that define agents and the commands they run), shipped three vulnerabilities that chain from an **unauthenticated self-registered account** to **arbitrary command execution as the Paperclip server process**. The worst, **CVE-2026-41679 (CVSS 10.0)**, required no pre-existing account and no victim interaction against default-configuration deployments running in authenticated mode. Root cause: Paperclip treats an imported agent's YAML configuration as trusted — the same "configuration file is documentation, not a security boundary" mistake this repo has tracked across SDK decorators (`@tool`, `[KernelFunction]`) and agent-platform tool-registration APIs (Composio), here applied to an agent-import bundle instead. Fixed in **Paperclip 2026.416.0**, published **2026-08-05**.

## What happened
Paperclip lets operators "import companies" — portable bundles (YAML files) that define one or more AI agents and specify which commands each agent is authorized to execute, functionally equivalent to a Dockerfile or Kubernetes manifest in that the bundle determines what code runs and in what context. Three chained flaws let an anonymous attacker turn that import feature into unauthenticated remote code execution:

1. **CVE-2026-41679 (CVSS 10.0) — self-registration to self-approved admin access.** An unauthenticated attacker could self-register a new account with no email verification, then self-approve their own CLI authorization request — obtaining persistent, board-level API access without any separate administrative approval step. Against default-configuration deployments running in authenticated mode with self-registration enabled, this required no pre-existing account and no victim interaction at all.
2. **GHSA-xfqj-r5qw-8g4j (CVSS 8.3) — missing authorization checks on import API routes.** The import route intended for higher-privileged operators allowed a user with only lower board-level access to import a *new* company — including one containing a maliciously configured agent — bypassing the intended access-level distinction between importing into an existing company versus creating a new one.
3. **GHSA-x8hx-rhr2-9rf7 (CVSS 9.6) — DNS rebinding bypass of loopback isolation.** A network-isolation control meant to keep certain operations bound to loopback could be defeated via DNS rebinding, widening the blast radius of the other two bugs.

**Chained attack:** self-register (bug 1) → import a company containing an agent configured with a **process adapter** (Paperclip's built-in command executor) and a malicious command (bug 2) → "wake" the agent, and the configured command executes directly as the Paperclip server process. No sandbox, no isolation, no second approval step stood between "imported YAML" and host command execution.

Fixed in **Paperclip 2026.416.0**, which requires instance-administrator access for imports targeting a new company and requires company-level access for imports targeting an existing one. Disclosure followed Paperclip's own responsible-disclosure process; published **2026-08-05**.

## Am I affected?
```bash
# Check your Paperclip version
paperclip --version   # or check your deployment's package/container tag
```
You're exposed if you self-host Paperclip **< 2026.416.0**, especially if:
- Self-registration is enabled (default configuration), or
- Your deployment relies on network-level loopback isolation as a security boundary for any Paperclip component.

## If you are affected
1. Upgrade to Paperclip **≥ 2026.416.0** immediately.
2. Audit existing companies/agents for any process-adapter agent you didn't configure yourself — treat any unrecognized imported agent as a potential backdoor.
3. Disable self-registration if you don't need it, and review board-level user lists for accounts you don't recognize.
4. Rotate any credentials the Paperclip server process had access to (API keys, cloud credentials, downstream service tokens).

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — an agent-configuration import (YAML, JSON, or otherwise) that specifies executable commands is equivalent to a build manifest and deserves the same code-review and access-control treatment as a Dockerfile, not the lighter treatment typically given to "config."
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
- Don't rely on network-level loopback binding as your only isolation boundary — DNS rebinding defeats it. Pair with application-level authentication on every endpoint.
- This is the same "decorator/config-is-documentation, not a security boundary" root cause this repo tracks for Semantic Kernel, Flowise's Agent-node `eval`, and Composio's tool-registration API — any platform that lets imported configuration define executable commands needs an explicit privilege check at the point commands are *defined*, not just when they're *run*.

## Update 2026-10-31 — a fourth Paperclip bug gets a CVE six months after the vendor fixed it: cleanup commands set through PATCH ran in a shell (CVE-2026-119713, 8.7; vendor 9.8); same fix release, 2026.416.0

VulnCheck published CVE-2026-119713 on 2026-10-30 for a vendor advisory Paperclip had carried since 2026-04-16: GHSA-vr7g-88fq-vhq3, "OS Command Injection via Execution Workspace cleanupCommand", reported 2026-04-13 by Yuval Elbar. A holder of an agent API key could set `cleanupCommand` and `teardownCommand` through `PATCH /api/execution-workspaces/:id`; when the workspace was archived, `cleanupExecutionWorkspaceArtifacts` ran them through a shell as the Paperclip server process. The CNA record names `@paperclipai/server` 2026.403.0 before 2026.416.0 and scores it CVSS 4.0 8.7 / 3.1 8.8 with `PR:L` (an agent key); the vendor page rates it Critical 9.8 with `PR:N`, because in `local_trusted` mode the request needs no authentication. Both are printed here; the file's `severity` was already `critical` for CVE-2026-41679. The fix is the same release as the three bugs above, 2026.416.0, which npm shows published on 2026-04-16 (2026.403.0 on 2026-04-04); the "published 2026-08-05" in this file's TL;DR is the date Oasis disclosed the first three, not the release date. Current `latest` on 2026-10-31 is 2026.1023.0. The GitHub Advisory Database row is GHSA-832j-x75x-r6jc (unreviewed, High, 2026-10-30). The record is six months old news for anyone on a current release and a fourth reason not to be on an April build; the triage lesson is that a research CNA can issue an id for an old vendor advisory at any time, and the id lands in scanners the day it is issued.

## Sources
- [Oasis Security — Paperclip Vulnerabilities: CVE-2026-41679 RCE + 2 More Flaws](https://www.oasis.security/blog/paperclip-agent-vulnerabilities) — primary technical writeup: all three CVEs, attack chain, patched version.
- [The Hacker News — Paperclip AI Flaws Let Attackers Run Host Commands via Malicious Agent Imports](https://thehackernews.com/2026/08/paperclip-ai-flaws-let-attackers-run.html) — independent confirmation.
- [CSO Online — Critical Paperclip bugs expose AI agent trust failures](https://www.csoonline.com/article/4205630/critical-paperclip-bugs-expose-ai-agent-trust-failures.html) — independent confirmation, framing on agent-config-as-trust-boundary.
- **2026-10-31 update sources** — [CVE Services — CVE-2026-119713](https://cveawg.mitre.org/api/cve/CVE-2026-119713) — fetched 2026-10-31: CNA VulnCheck, published 2026-10-30 15:16 UTC, `@paperclipai/server` 2026.403.0 before 2026.416.0, CVSS 4.0 8.7 and 3.1 8.8, the description, credit Yuval Elbar, references; [paperclipai/paperclip — GHSA-vr7g-88fq-vhq3](https://github.com/paperclipai/paperclip/security/advisories/GHSA-vr7g-88fq-vhq3) — fetched 2026-10-31: published 2026-04-16, reported 2026-04-13, Critical 9.8 `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`, "No known CVE" on the page, the `local_trusted` statement, reporter YuvalElbar6; [GitHub Advisory Database — GHSA-832j-x75x-r6jc](https://github.com/advisories/GHSA-832j-x75x-r6jc) — fetched 2026-10-31: unreviewed, High, 2026-10-30; npm registry `@paperclipai/server` `time`, queried 2026-10-31: 2026.403.0 at 2026-04-04, 2026.416.0 at 2026-04-16, `latest` 2026.1023.0.
