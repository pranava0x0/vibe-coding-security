---
id: 2026-11-ibm-contextforge-mcp-gateway-eight-cves-upstream-credential-override-identity-replay-fixed-1-1-1
title: "IBM ContextForge MCP Gateway: eight CVEs on 2026-11-13; a request header overrides the gateway's upstream credential (CVE-2026-110279, 8.1); upgrade to 1.1.1"
date_disclosed: 2026-11-12
last_updated: 2026-11-14
severity: high
status: patched
ecosystems: [mcp, pypi, python, ibm, mcp-gateway]
tools_affected: ["mcp-contextforge-gateway (PyPI) 1.0.0 through 1.1.0", "IBM ContextForge MCP Gateway deployments that store upstream OAuth, bearer or basic credentials", "ContextForge deployments with identity propagation enabled", "multi-tenant ContextForge deployments that grant `admin.import` to team roles"]
tags: [cve, mcp, mcp-gateway, contextforge, ibm, credential-handling, identity-propagation, authorization-bypass, ssrf, xss, denial-of-service, multi-tenant, patched]
---

## TL;DR
IBM published eight CVEs for ContextForge MCP Gateway on 2026-11-12 and 2026-11-13. Two are High. CVE-2026-110279 (8.1) lets an authenticated user replace the credential the gateway holds for an upstream MCP server by sending an `X-Upstream-Authorization` header. CVE-2026-110278 (7.4) sends user identity to upstream servers configured not to receive it. Five ids are fixed in 1.1.0 and three need 1.1.1. Upgrade `mcp-contextforge-gateway` to 1.1.1, which is on PyPI.

## What happened

The CVE Services records, all from the IBM CNA and all published 2026-11-13, were read on 2026-11-14. The count of eight was made from those records. Each record references one IBM bulletin.

| Id | IBM score | Affected | Fixed | What IBM says |
|---|---|---|---|---|
| CVE-2026-110279 | 8.1 | 1.0.0 through 1.1.0 | 1.1.1 | the `X-Upstream-Authorization` request header overrides the gateway-managed upstream credential for OAuth, bearer and basic gateways, bypassing per-user permission and audit attribution |
| CVE-2026-110278 | 7.4 | 1.0.0 through 1.1.0 | 1.1.1 | identity propagation signatures can be replayed, and the per-server setting is ignored on tool calls, so identity reaches third-party MCP servers |
| CVE-2026-110189 | 6.5 | 1.0.8 through 1.0.11, and 1.1.0 | 1.1.1 | incomplete denylist in the jq filter guard lets an authenticated user stop a worker |
| CVE-2026-94407 | 6.5 | 1.0.0 through 1.0.11 | 1.1.0 | a tool's JSON Schema `pattern` can carry a backtracking regex |
| CVE-2026-110194 | 5.4 | 1.0.0 through 1.0.11 | 1.1.0 | server-side request forgery by an authenticated user |
| CVE-2026-110195 | 5.4 | 1.0.0 through 1.0.11 | 1.1.0 | the token-exchange cache key is too coarse, so cached upstream tokens are reused across a user's credentials |
| CVE-2026-110199 | 4.8 | 1.0.0 through 1.0.11 | 1.1.0 | DOM-based cross-site scripting in the Web UI |
| CVE-2026-110178 | 4.1 | 1.0.0 through 1.0.11 | 1.1.0 | a holder of team-scoped `admin.import` can overwrite the URL, headers and credentials of other tenants' public tools through `/v1/import` |

The two High bulletins are dated 2026-11-12. The other six are dated 2026-11-13. The GitHub Advisory Database listed all eight on 2026-11-14.

The bulletin for CVE-2026-110279 names v1.1.1 as the fix and links pull request 7341. Its remediation table also prints a version "2.0". No 2.0 exists on PyPI or on the releases page. This file uses 1.1.1.

Registry and release facts, read 2026-11-14: PyPI lists 1.1.0 and 1.1.1 as the two newest versions. The repository's releases page dates v1.1.1 to 2026-11-10 and v1.1.0 to 2026-10-20. The v1.1.1 notes say the release "hardens ownership, OAuth discovery, credential masking, and token scoping". The v1.1.0 notes list "configuration import ownership enforcement". Neither set of notes names a CVE.

ContextForge's earlier ids are in [2026-08-agent-framework-mcp-cve-batch.md](2026-08-agent-framework-mcp-cve-batch.md).

## Am I affected?

```bash
pip show mcp-contextforge-gateway | grep -i '^version'
```

- Any version from 1.0.0 through 1.1.0 is affected by at least two ids.
- CVE-2026-110279 matters most where the gateway stores the upstream credential and users are meant to act only through it.
- CVE-2026-110278 applies where identity propagation is on.

## If you are affected

1. Upgrade to 1.1.1.
2. If you cannot upgrade, apply IBM's workarounds. Strip `X-Upstream-Authorization` at the reverse proxy in front of the gateway for all MCP endpoints. Set `IDENTITY_PROPAGATION_ENABLED=false`. Set `DCR_ALLOWED_ISSUERS` or `DCR_ENABLED=false`. Keep `admin.import` for platform administrators.
3. Review upstream MCP server logs for calls made with a credential other than the gateway's. This step is this file's advice.

## Prevention

- Treat an MCP gateway as a credential store. Put it behind a proxy that drops headers users should not set.
- See [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).

## Sources

Single source: the vendor, through its bulletins and its CNA records.

- CVE Services records for [CVE-2026-110279](https://cveawg.mitre.org/api/cve/CVE-2026-110279), [CVE-2026-110278](https://cveawg.mitre.org/api/cve/CVE-2026-110278), [CVE-2026-110189](https://cveawg.mitre.org/api/cve/CVE-2026-110189), [CVE-2026-94407](https://cveawg.mitre.org/api/cve/CVE-2026-94407), [CVE-2026-110194](https://cveawg.mitre.org/api/cve/CVE-2026-110194), [CVE-2026-110195](https://cveawg.mitre.org/api/cve/CVE-2026-110195), [CVE-2026-110199](https://cveawg.mitre.org/api/cve/CVE-2026-110199) and [CVE-2026-110178](https://cveawg.mitre.org/api/cve/CVE-2026-110178), fetched 2026-11-14: CNA IBM, published 2026-11-13, descriptions, ranges, scores, bulletin references.
- IBM bulletins [7296490](https://www.ibm.com/support/pages/node/7296490), [7296489](https://www.ibm.com/support/pages/node/7296489), [7296697](https://www.ibm.com/support/pages/node/7296697), [7296667](https://www.ibm.com/support/pages/node/7296667), [7296696](https://www.ibm.com/support/pages/node/7296696), [7296695](https://www.ibm.com/support/pages/node/7296695), [7296694](https://www.ibm.com/support/pages/node/7296694) and [7296701](https://www.ibm.com/support/pages/node/7296701), fetched 2026-11-14: dates, fixed versions, workarounds, the "2.0" entry.
- [IBM/mcp-context-forge releases](https://github.com/IBM/mcp-context-forge/releases), fetched 2026-11-14: release dates and the quoted note lines.
- [GitHub Advisory Database: contextforge](https://github.com/advisories?query=contextforge+sort%3Apublished-desc), fetched 2026-11-14: twenty rows, eight dated 2026-11-14.
- `pip index versions mcp-contextforge-gateway`, run 2026-11-14.
- Not covered: the two linked pull requests and the per-CVE NVD pages.
