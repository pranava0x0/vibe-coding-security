---
id: 2026-10-agno-function-call-field-type-eval-rce-fixed-2-3-24
title: "Agno before 2.3.24 ran Python from a FunctionCall field_type through eval() (CVE-2026-35002, 9.3); fixed 2.3.24, reviewed 2026-10-27"
date_disclosed: 2026-04-02
last_updated: 2026-10-27
severity: critical
status: patched
ecosystems: [pypi, ai-agents, agent-frameworks]
tools_affected: ["agno (PyPI) < 2.3.24; any Agno deployment where an API, web UI, tool output or model output can set a FunctionCall input field's field_type"]
tags: [cve, eval-injection, remote-code-execution, agent-framework, vulncheck-cna, db-reviewed-months-later]
---

## TL;DR
Agno versions before 2.3.24 passed the `field_type` parameter of a `FunctionCall` input field to Python's `eval()`, so anything that could set that value ran Python in the Agno process (CVE-2026-35002; VulnCheck CVSS 4.0 9.3, credit Eran Shimony of Palo Alto Networks). The fix, a fixed `type_mapping` lookup, reached PyPI as 2.3.24 on 2026-01-08; the CNA record is from 2026-04-02, the vendor advisory from 2026-06-30, and the GitHub Advisory Database reviewed it on 2026-10-27, which is why it appears on today's reviewed-critical pip listing as a new row. Anything at or above 2.3.24 is past it.

## What happened

- **2026-01-08.** Agno 2.3.24 reached PyPI with commit cbf67552 (PR #5912), which replaced `eval()` on `field_type` with a dictionary lookup and validates the value as a known string key or an already-resolved `type` object.
- **2026-04-02.** VulnCheck published CVE-2026-35002: "Agno versions prior to 2.3.24 contain an arbitrary code execution vulnerability in the model execution component that allows attackers to execute arbitrary Python code by manipulating the field_type parameter passed to eval()". CVSS 4.0 9.3 (`AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H`), CWE-95. Updated 2026-10-08.
- **2026-06-30.** The vendor advisory GHSA-m4w4-3r8h-jw98 was published on `agno-agi/agno`: any deployment that exposes Agno to user-influenced `FunctionCall` inputs, through an API, a web UI, or untrusted tool or model output, is affected; no safe workaround; upgrade.
- **2026-10-27.** The database reviewed the advisory. Its page prints CVSS 3.1 9.8 in the header and cites 9.3 in the text; the CNA's figure is 9.3 on CVSS 4.0. This file uses the CNA's.

**Why it matters.** `field_type` is a schema field an agent framework builds from tool definitions and model output. A tool definition pulled from a registry, or a model-written structured call, is the kind of input the vendor advisory names. The two VulDB records in the [Agno confirmation-gate file](2026-10-agno-tool-call-confirmation-gate-team-delegation-vuldb-cves.md) are a different, unresolved matter.

## Am I affected?

```bash
pip show agno 2>/dev/null | grep -i ^version     # below 2.3.24 is affected; PyPI latest is 3.1.10 (2026-10-27)
```

## If you are affected

1. Upgrade to 2.3.24 or later and redeploy.
2. If untrusted input could reach a `FunctionCall` on an affected version, treat the host as having run untrusted code. [If your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- Keep agent frameworks on current releases; this fix carried a CVE three months after it shipped and a database review nine months after. [Agent sandboxing](../prevention/agent-sandboxing.md).

## Sources
- [CVE Services — CVE-2026-35002](https://cveawg.mitre.org/api/cve/CVE-2026-35002) — queried 2026-10-27: CNA VulnCheck, published 2026-04-02, updated 2026-10-08, Agno before 2.3.24 and commit cbf67552, CVSS 4.0 9.3, credit.
- [GitHub Advisory Database — GHSA-m4w4-3r8h-jw98](https://github.com/advisories/GHSA-m4w4-3r8h-jw98) — fetched 2026-10-27: vendor-dated 2026-06-30, reviewed 2026-10-27, Critical, header 9.8 beside text 9.3, affected < 2.3.24, patched 2.3.24, the `type_mapping` fix, no safe workaround, PYSEC-2026-256.
- [VulnCheck — Agno < 2.3.24 field_type Eval Injection Arbitrary Code Execution](https://www.vulncheck.com/advisories/agno-field-type-eval-injection-arbitrary-code-execution) — fetched 2026-10-27: published 4/2/2026, fixed 2.3.24, the release and commit references.
- [agno-agi/agno — Security Advisories](https://github.com/agno-agi/agno/security/advisories) — fetched 2026-10-27: three rows, GHSA-m4w4-3r8h-jw98 dated Jun 30, 2026.
- PyPI `agno` metadata queried 2026-10-27: 2.3.24 on 2026-01-08, latest 3.1.10.
