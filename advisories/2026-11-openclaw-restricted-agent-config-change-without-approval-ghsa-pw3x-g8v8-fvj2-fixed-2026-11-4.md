---
id: 2026-11-openclaw-restricted-agent-config-change-without-approval-ghsa-pw3x-g8v8-fvj2-fixed-2026-11-4
title: "OpenClaw: a restricted agent could change configuration without approval and enable host command execution (GHSA-pw3x-g8v8-fvj2); fixed 2026.11.4 and 2026.10.33"
date_disclosed: 2026-11-19
last_updated: 2026-11-23
severity: high
status: patched
ecosystems: [npm, openclaw, ai-agent]
tools_affected: ["`openclaw` (npm) 2026.9.2 to below 2026.10.33", "`openclaw` (npm) 2026.11.1 to below 2026.11.4", "OpenClaw gateways that run agents under a tool policy denying execution and file writes"]
tags: [openclaw, ai-agent, approval-bypass, authorization-bypass, tool-policy, host-execution, no-cve, patched]
---

## TL;DR
[GHSA-pw3x-g8v8-fvj2](https://github.com/openclaw/openclaw/security/advisories/GHSA-pw3x-g8v8-fvj2) says the `openclaw` tool could make persistent configuration changes without approval, even when tool policy denied execution and file writes. A restricted agent could use that to enable host command execution. Affected 2026.9.2 to below 2026.10.33 and 2026.11.1 to below 2026.11.4. Upgrade to 2026.11.4, or 2026.10.33 on extended-stable. No CVE.

## What happened

The vendor published the advisory on 2026-11-19 and rates it High, CVSS 3.1 8.8, `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`, CWE-863. It says the practical risk depends on the operator's configuration and on whether lower-trust input can reach the delegation path. It also says the advisory does not change OpenClaw's trusted-operator model.

Registry dates, read 2026-11-23 with `npm view openclaw time dist-tags`:

| Version | Published | Channel |
|---|---|---|
| 2026.11.4 | 2026-11-16 | first fixed stable release |
| 2026.10.33 | 2026-11-18 | `extended-stable` |
| 2026.11.7 | 2026-11-23 | `latest` |

Both dist-tags are at or past a fixed version. The page printed "No known CVE" and OSV had no record on 2026-11-23, so scanners do not flag it.

## Am I affected?

```bash
npm ls -g openclaw 2>/dev/null; openclaw --version 2>/dev/null
```

- The version is in one of the two ranges.
- You run an agent that a tool policy restricts, and input you do not fully trust can reach it, such as channel messages or fetched content.

## If you are affected

1. Upgrade to 2026.11.4 or later, or 2026.10.33 on extended-stable.
2. Until then, the vendor's mitigation is to set `tools.exec.mode` to `ask` and deny untrusted delegated changes.
3. Compare the gateway configuration with your last known-good copy and look for an exec setting you did not make. This step is this file's advice. See [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- Keep channel and tool allowlists narrow and do not share one gateway between users who do not trust each other. Both are the vendor's hardening notes.
- See [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).

## Sources

Single source: the vendor.

- [GHSA-pw3x-g8v8-fvj2](https://github.com/openclaw/openclaw/security/advisories/GHSA-pw3x-g8v8-fvj2), fetched 2026-11-23 through a summarizing fetch: date, score, vector, ranges, patched versions, impact, mitigation, "No known CVE". Paraphrased, not quoted.
- [openclaw/openclaw security advisories](https://github.com/openclaw/openclaw/security/advisories), fetched 2026-11-23: the row, first on page 1.
- `npm view openclaw time dist-tags`, run 2026-11-23.
- OSV returned no record for the id on 2026-11-23.
- Not covered: the fix commit and the release notes.
