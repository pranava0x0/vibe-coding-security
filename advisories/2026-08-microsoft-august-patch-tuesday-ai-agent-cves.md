---
id: 2026-08-microsoft-august-patch-tuesday-ai-agent-cves
title: "Microsoft August 2026 Patch Tuesday — critical elevation-of-privilege CVEs in Azure SRE Agent and Copilot Cowork"
date_disclosed: 2026-08-11
last_updated: 2026-08-14
severity: critical
status: patched
ecosystems: [azure, microsoft-365, ai-agents]
tools_affected: [azure-sre-agent, copilot-cowork]
tags: [elevation-of-privilege, authorization-bypass, patch-tuesday, managed-identity]
---

## TL;DR
Microsoft's August 2026 Patch Tuesday included two critical elevation-of-privilege CVEs in first-party AI-agent products: **Azure SRE Agent** (CVSS 9.9) and **Microsoft Copilot Cowork** (CVSS 9.3). Both are missing/improper-authorization bugs (CWE-862/CWE-285) — the same "the SDK/platform trusted the caller's claimed scope" root cause this repo tracks across agent frameworks generally, here landing in two of Microsoft's own agent products on the same disclosure day.

## What happened
**CVE-2026-62830** (CVSS 9.9, CWE-862 Missing Authorization) — Azure SRE Agent's on-behalf-of (OBO) elevation flow lacked an authorization check, letting a low-privileged remote attacker escalate privileges across the network with no user interaction. Because Azure SRE Agent operates with a managed identity spanning runbooks, telemetry, incident-response tooling, and other Azure resources, the blast radius extends to everything that identity can touch, not just the agent itself. Confirmed directly on [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-62830), published 2026-08-06 as part of the 2026-08-11 Patch Tuesday batch. Microsoft applied a **service-side fix** — no customer patch action required, though auditing managed-identity RBAC assignments is still recommended.

**CVE-2026-59118** (CVSS 9.3, CWE-285 Improper Authorization) — Microsoft Copilot Cowork, an AI collaboration agent operating with access to Microsoft 365 organizational content and workflows, had an improper-authorization flaw letting an attacker elevate privileges over the network (requires some user interaction, per vendor scoring). Confirmed directly on [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59118), published 2026-08-06.

Both were reported via CrowdStrike's and Qualys's independent Patch Tuesday analyses ([CrowdStrike](https://www.crowdstrike.com/en-us/blog/patch-tuesday-analysis-august-2026/), [Qualys](https://blog.qualys.com/vulnerabilities-threat-research/patch-tuesday/2026/08/11/microsoft-patch-tuesday-august-2026-security-update-review)); Microsoft's own MSRC advisory pages were unreachable (HTTP 503) during this sweep's verification, so both CVE numbers, CVSS scores, and descriptions were confirmed directly against NVD rather than trusted from either aggregator's prose.

This is the same "agent identity/managed-identity scope isn't actually enforced the way the platform assumes" class this repo already tracks in Rogue Agent (Dialogflow CX shared execution) and the CoreBreak agent-harness tool-call-forgery cluster — here landing in two separate first-party Microsoft AI-agent products on the same Patch Tuesday.

## Am I affected?
- **Azure SRE Agent**: Microsoft applied the fix server-side — no action required to receive the patch. Review managed-identity RBAC assignments for Azure SRE Agent deployments in your tenant as a precaution.
- **Copilot Cowork**: check that your Microsoft 365 tenant has received the August 2026 security update; Copilot Cowork updates typically roll out automatically, but verify via your Microsoft 365 admin center's update history.

## If you are affected
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources
- [NVD — CVE-2026-62830](https://nvd.nist.gov/vuln/detail/CVE-2026-62830) — canonical CVE record, CVSS 9.9, CWE-862.
- [NVD — CVE-2026-59118](https://nvd.nist.gov/vuln/detail/CVE-2026-59118) — canonical CVE record, CVSS 9.3, CWE-285.
- [CrowdStrike — Patch Tuesday Analysis, August 2026](https://www.crowdstrike.com/en-us/blog/patch-tuesday-analysis-august-2026/) — batch context, managed-identity blast-radius framing.
- [Qualys — Microsoft Patch Tuesday, August 2026 Security Update Review](https://blog.qualys.com/vulnerabilities-threat-research/patch-tuesday/2026/08/11/microsoft-patch-tuesday-august-2026-security-update-review) — independent corroboration of both CVEs.
