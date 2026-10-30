---
id: 2026-10-langflow-1-13-0-ibm-bulletin-seven-cves-auth-bypass-code-generation-rce
title: "Langflow 1.0.0 to 1.12.8: IBM bulletin of seven CVEs, two unauthenticated 9.8s (auth bypass, code generation RCE); fixed 1.13.0"
date_disclosed: 2026-10-28
last_updated: 2026-10-30
severity: critical
status: patched
ecosystems: [pypi, python, docker, agent-framework]
tools_affected: ["langflow (PyPI) 1.0.0 through 1.12.8 and the langflowai/langflow Docker image on the same lines", "any Langflow instance reachable by users who are not fully trusted, and any instance that still has automatic login on"]
tags: [cve, langflow, ibm-psirt, authentication-bypass, auto-login, code-injection, agentic-assistant, rce, credential-exposure, hono, vendor-bulletin, patched]
---

## TL;DR
IBM's PSIRT bulletin for Langflow OSS (published 2026-10-28, modified 10-29) lists seven CVEs for 1.0.0 through 1.12.8 and one fix, 1.13.0 (PyPI 2026-10-22): CVE-2026-93680 (IBM 9.8) lets a remote attacker bypass authentication, which the bulletin ties to an incomplete fix for the automatic-login control; CVE-2026-110186 (9.8) is unauthenticated code execution through improper control of code generation; CVE-2026-110193 (8.8) lets a low-privileged user steer the Agentic Assistant into generating or submitting component code with patterns the blocklist missed, for OS command execution; CVE-2026-110192 (6.5) exposes credentials to an authenticated user; and three Hono CVEs (CVE-2026-84363, 84364, 84365) come in through the bundled framework. Upgrade to 1.13.0, back up first, and if the instance ran with automatic login, follow the recovery steps the release notes added, because the default superuser now needs a password.

## What happened

IBM has owned Langflow's disclosure since the DataStax acquisition, and its bulletin precedes the vendor tab by weeks ([the September file](2026-09-langflow-ibm-psirt-eleven-cve-batch.md) records the same pattern). Bulletin `ibm17294467` carries the seven ids; the four IBM-assigned CVE records were published at CVE Services on 2026-10-29 and each describes the whole range, "IBM Langflow OSS 1.0.0 through 1.12.8", with the bulletin as its only reference.

| CVE | CNA | CVSS 3.1 (provider, read 2026-10-30) | What the record says |
|---|---|---|---|
| CVE-2026-93680 | IBM | 9.8 (IBM) `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | "could allow a remote attacker to bypass security restrictions due to improper authentication." The bulletin's summary ties it to an incomplete fix for the auto-login control. |
| CVE-2026-110186 | IBM | 9.8 (IBM) | "could allow a remote attacker to execute arbitrary code due to improper control of code generation." |
| CVE-2026-110193 | IBM | 8.8 (IBM) `PR:L` | "could allow a remote attacker with a low-privileged authenticated account to cause the Agentic Assistant to generate or submit component code using these unblocked patterns, resulting in arbitrary operating system command execution on the server." |
| CVE-2026-110192 | IBM | 6.5 (IBM) `PR:L`, `C:H` | "could allow a remote authenticated attacker to obtain sensitive information due to insufficiently protected credentials." |
| CVE-2026-84363, CVE-2026-84364, CVE-2026-84365 | GitHub | 5.9, 5.3, 6.5 (GitHub) | Hono: query parsing after a literal hash fragment (cache poisoning, filter bypass), `parseBody()` dot-notation memory exhaustion, and `toSSG()` path traversal at build time; all fixed in Hono 4.13.5 per the bulletin. |

The bulletin says "several other open-source dependencies in the product have known vulnerabilities" without listing them, and offers no workaround.

**The release.** `langflow` 1.13.0 reached PyPI on 2026-10-22 at 21:20 UTC, six days before the bulletin. Its release notes do not name a CVE. They do carry the lines the bulletin's summary points at: "fix: disable automatic login by default" (#14993), "fix(auth): keep the default superuser's data when AUTO_LOGIN is turned off" (#15326), "fix: guide recovery after upgrading from an auto-login installation" (#15789), "fix(auth): isolate sessions for runtime URL prefixes" (#15875), "fix: block unsafe module reexports in assistant code scanning" (#15586), "fix: enforce credential egress policy across provider components" (#15587) and "fix(security): bound URL component response size to prevent memory exhaustion" (#15436). This file does not pair release-note lines with CVE ids beyond what the bulletin states, because the records do not.

**What this adds to the Langflow record here.** The auto-login path is the one behind CVE-2026-9198 and the KEV-listed CVE-2026-105740 chain ([the fernet-key and REPL file](2026-10-langflow-fernet-key-webhook-bypass-python-repl-cve-wave.md), [the September file](2026-09-langflow-ibm-psirt-eleven-cve-batch.md)); CVE-2026-93680 is IBM saying the earlier fix was incomplete, and 1.13.0 is the release that turns automatic login off by default rather than patching around it. The Agentic Assistant finding is the third code-generation sink in the product this year after `/api/v1/validate/code` and the Smart Transform lambda.

**Severity.** `critical` on two unauthenticated 9.8s from the vendor's CNA; the bulletin, the records and the release are all IBM or Langflow primaries, so `status: patched` rests on the vendor alone.

## Am I affected?

```bash
pip show langflow 2>/dev/null | grep -i ^version        # 1.0.0 through 1.12.8 is affected; 1.13.0 is the fix
docker image ls | grep langflowai/langflow               # same lines for the image
grep -rn 'LANGFLOW_AUTO_LOGIN' .env docker-compose*.yml 2>/dev/null   # unset or true on an older release is the 9.8 path
```

- Any instance below 1.13.0 that an untrusted network can reach is affected by the two unauthenticated records.
- Any instance below 1.13.0 with accounts you do not fully trust is affected by the Agentic Assistant and credential records.

## If you are affected

1. Back up the database, the secret key and uploaded files, then upgrade: `pip install --upgrade "langflow==1.13.0"` or the `langflowai/langflow:1.13.0` image.
2. If the instance ran with automatic login, follow the release's recovery guidance so the default superuser has a password before anyone else reaches the login page.
3. Treat every credential stored in an exposed instance as readable and rotate it: [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md).

## Prevention

- Keep Langflow off the public internet and behind your own authentication: [agent sandboxing](../prevention/agent-sandboxing.md).
- Fewer long-lived provider keys inside the flow builder: [credential hygiene](../prevention/credential-hygiene.md).

## Sources
- [IBM Security Bulletin — Langflow OSS is affected by multiple vulnerabilities (ibm17294467)](https://www.ibm.com/support/pages/node/7294467) — fetched 2026-10-30: published 2026-10-28, modified 10-29, the seven CVEs with IBM and GitHub scores and vectors, the 1.0.0 through 1.12.8 range, the 1.13.0 remediation, the backup and auto-login notes, no workaround.
- [CVE Services — CVE-2026-93680](https://cveawg.mitre.org/api/cve/CVE-2026-93680), [CVE-2026-110186](https://cveawg.mitre.org/api/cve/CVE-2026-110186), [CVE-2026-110193](https://cveawg.mitre.org/api/cve/CVE-2026-110193), [CVE-2026-110192](https://cveawg.mitre.org/api/cve/CVE-2026-110192) — fetched 2026-10-30: CNA ibm, all published 2026-10-29, the descriptions quoted above, the bulletin as the single reference.
- [GitHub Advisory Database — `agent` listing](https://github.com/advisories?query=agent+sort%3Apublished-desc) — fetched 2026-10-30: the CVE-2026-110193 row (High, unreviewed, 2026-10-29), which is how the bulletin surfaced.
- [langflow-ai/langflow — release v1.13.0](https://github.com/langflow-ai/langflow/releases/tag/v1.13.0) — fetched 2026-10-30: dated 22 Oct, the auto-login, auth, assistant code-scanning and credential lines quoted above; no CVE named.
- PyPI `langflow` 1.13.0 release metadata, queried 2026-10-30: upload time 2026-10-22 21:20 UTC; `pip index versions langflow` lists 1.13.0 as newest.
- [langflow-ai/langflow — security advisories](https://github.com/langflow-ai/langflow/security/advisories) — fetched 2026-10-30: newest row 2026-09-28; none of the seven ids has a vendor-tab entry.
- Related in this corpus: [Langflow IBM PSIRT eleven-CVE batch (fixed 1.11.6)](2026-09-langflow-ibm-psirt-eleven-cve-batch.md), [Langflow fernet key, webhook bypass and Python REPL wave](2026-10-langflow-fernet-key-webhook-bypass-python-repl-cve-wave.md).
