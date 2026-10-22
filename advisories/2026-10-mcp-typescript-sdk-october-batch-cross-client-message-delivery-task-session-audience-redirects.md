---
id: 2026-10-mcp-typescript-sdk-october-batch-cross-client-message-delivery-task-session-audience-redirects
title: "MCP TypeScript SDK: six advisories (2026-10-02 to 10-15) for cross-client message delivery, task hijack, audience, redirects and DoS; fixed 1.32.0 and 2.3.0, two opt-in"
date_disclosed: 2026-10-15
last_updated: 2026-10-22
severity: high
status: mitigated
ecosystems: [npm, typescript, mcp, ai-agents]
tools_affected: ["@modelcontextprotocol/sdk 1.x before 1.32.0 (ranges differ per advisory; see table)", "@modelcontextprotocol/server 2.0.0 before 2.3.0, @modelcontextprotocol/client 2.0.0 before 2.3.0, @modelcontextprotocol/express before 2.0.2, @modelcontextprotocol/server-legacy before 2.3.1, @modelcontextprotocol/node and @modelcontextprotocol/hono before 2.1.0 / 2.0.1", "every MCP server or client built on the official TypeScript SDK and reachable over HTTP; stdio-only servers are not affected by the server-side items"]
tags: [cve, ghsa, mcp, typescript-sdk, cross-client-leak, race-condition, authorization-bypass, audience-validation, open-redirect, header-leak, refresh-token, dos, memory-exhaustion, opt-in-fix, db-date-lag]
---

## TL;DR
The official MCP TypeScript SDK published six advisories between 2026-10-02 and 2026-10-15 that the GitHub Advisory Database listed together on 2026-10-20 with five CVE ids, CVE-2026-111767 through CVE-2026-111771. Two matter most for anyone hosting an MCP server over HTTP: a shared transport or server instance could deliver one client's responses and notifications to another, because messages were matched by JSON-RPC `id` alone and SDK clients all count from 0 (CVE-2026-111770, 7.7, `@modelcontextprotocol/server` 2.x only); and experimental tasks were not tied to the session that created them, so clients could list, read and cancel each other's (CVE-2026-111767, 8.6). The client side followed cross-origin redirects and re-sent custom headers, the session id and, on 307/308, OAuth token bodies with refresh tokens and client secrets (CVE-2026-111769, 6.5). Two availability bugs: unbounded request bodies and batch lengths (GHSA-f897-62hf-6gxq, 7.5, fixed 1.30.1 and 2.1.0) and a single in-limit request that exhausts memory during validation (CVE-2026-111768, 7.5). Upgrade to 1.32.0 or 2.3.0 fixes four by default. Two are opt-in after upgrade: bearer-token audience checking needs `expectedResource` and an `aud` return from `verifyAccessToken()` (CVE-2026-111771, 6.8), and the validation-memory fix needs `maxToolInputElements` plus a lower `maxRequestBodySize`. Hence `mitigated`, not `patched`.

## What happened

| Vendor advisory (published) | CVE (DB 2026-10-20) | Packages and ranges | Fix | Default after upgrade? |
|---|---|---|---|---|
| GHSA-22jm-h49p-29qw (2026-10-02): experimental tasks not tied to the creating session | CVE-2026-111767, High 8.6 (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L`), CWE-639, CWE-862 | `sdk` 1.24.0 through 1.31.0 | 1.32.0 | yes; the feature is deprecated by the 2026-07-28 spec and the advisory says to stop using `taskStore` |
| GHSA-6prh-2h8m-c8cw (2026-10-02): HTTP client transports and OAuth requests followed cross-origin redirects and re-sent custom headers and bodies | CVE-2026-111769, Moderate 6.5, CWE-200 | `client` 2.0.0 through 2.2.0; `sdk` before 1.32.0 | 2.3.0, 1.32.0 | yes: redirects now same-origin only, none in browsers; `redirectPolicy: 'follow'` restores the exposure |
| GHSA-rvq5-wwqv-78pq (2026-10-05): server bearer authentication accepted tokens issued for another service | CVE-2026-111771, Moderate 6.8, CWE-863 | `sdk` 1.6.0 through 1.31.0; `server` 2.0.0 through 2.2.0; `express` before 2.0.2; `server-legacy` before 2.3.1 | 1.32.0, 2.3.0, 2.0.2, 2.3.1 | no: pass `expectedResource` to `requireBearerAuth()` and return `AuthInfo.resource` from `verifyAccessToken()` |
| GHSA-jm63-cq47-j5jp (2026-10-15): shared transport or server instances delivered one HTTP client's messages to another | CVE-2026-111770, High 7.7 (`AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:H`), CWE-362 | `server` 2.0.0 through 2.2.0; `sdk` 1.26.0 and later not affected | 2.3.0 | yes, and the fixed SDK rejects a second `connect()` (`ALREADY_CONNECTED`) and a stateless transport's second request, so shared-instance code must change to a per-request factory or per-session instances |
| GHSA-46jr-4wx8-v453 (2026-10-15): one in-limit HTTP request could exhaust server memory during validation | CVE-2026-111768, High 7.5, CWE-770 | `sdk` 1.3.0 through 1.31.0; `server` 2.0.0 through 2.2.0 | 1.32.0, 2.3.0 | no: set `maxToolInputElements` on `McpServer` (off by default) and lower `maxRequestBodySize` |
| GHSA-f897-62hf-6gxq (2026-10-15): HTTP server transports did not limit request body size or JSON-RPC batch length | no CVE, High 7.5, CWE-770 | `sdk` 1.10.0 before 1.30.1; `server` and `node` before 2.1.0; `hono` before 2.0.1 | 1.30.1, 2.1.0, 2.0.1 | yes: 4 MiB bodies get HTTP 413, batches over 100 messages HTTP 400; `express.json()` alone does not limit batch length |

**The cross-client leak.** The advisory's README examples for `@modelcontextprotocol/hono`, `express`, `fastify` and `node` showed the shared-instance pattern until this release, so a server copied from the docs was the affected shape. Not affected: `createMcpHandler()` with a factory that builds a new server per call, stdio servers, and `@modelcontextprotocol/sdk` 1.26.0 and later. Reporters DavidCarliez and legitu1337; PR #2918.

**The redirect leak.** `StreamableHTTPClientTransport`, `SSEClientTransport` and `auth()` followed redirects to any origin, sending `requestInit.headers` (an API-key header, for example) and `mcp-session-id`, and on 307 or 308 the request body, including OAuth token requests with refresh tokens and client secrets; runtimes already strip `Authorization` across origins. If a redirect may have reached a host you do not control, rotate the keys and secrets the client held and revoke its tokens. Reporter nickelsec; PRs #2901 and #2902.

**Dates.** Vendor pages 2026-10-02 to 10-15; all five CVE records and database rows 2026-10-20 (GitHub CNA; CVE Services returned "record does not exist" for CVE-2026-111768 through 111771 on 2026-10-22 while the database pages print them, so those four ids are cited from the database pages only). npm `time`, read 2026-10-22: `@modelcontextprotocol/sdk` 1.30.1 on 2026-09-23, 1.31.0 on 09-28, 1.32.0 on 10-02, 1.32.1 on 10-05; `server` and `client` 2.3.0 on 10-02, 2.3.1 on 10-05. The 09-30 OAuth advisory (GHSA-6qxp-vccf-f47h, CVE-2026-104850, client credentials sent to a server-chosen authorization server) is already in [the Python SDK issuer-validation file](2026-09-mcp-python-sdk-oauth-issuer-validation-credential-redirect.md), which also carries the Python SDK's twins of the audience, redirect, body-size and session advisories.

Why it is here: this SDK is under most TypeScript MCP servers the audience writes and most clients that call them, and the README pattern itself was the vulnerable one.

## Am I affected?

- `npm ls @modelcontextprotocol/sdk @modelcontextprotocol/server @modelcontextprotocol/client @modelcontextprotocol/express @modelcontextprotocol/server-legacy @modelcontextprotocol/node @modelcontextprotocol/hono` in every MCP project; compare with the table.
- Server side: HTTP-reachable servers only. `grep -ri taskstore` for the tasks bug; a transport or `McpServer` created once at startup and shared across requests for the cross-client bug; `requireBearerAuth()` or `verifyBearerToken()` with an authorization server that issues tokens for several services for the audience bug.
- Client side: any client using the HTTP transports or `auth()` against a server you do not fully trust, for the redirect bug.

## If you are affected

1. Upgrade to `@modelcontextprotocol/sdk` 1.32.1 or the 2.x packages at 2.3.1 (`express` 2.0.2, `server-legacy` 2.3.1).
2. Then make the three code changes the fixes require: build a new `McpServer` and transport per request or per session (the fixed SDK refuses the shared pattern); set `maxToolInputElements` and a lower `maxRequestBodySize`; set `expectedResource` and return `AuthInfo.resource`. Remove `taskStore` or use one `InMemoryTaskStore` per session.
3. Client side: leave `redirectPolicy` at its new default. If an affected client may have been redirected off-origin, rotate its API keys and client secrets and revoke its tokens.
4. If you cannot upgrade: cap bodies at a reverse proxy, pass a custom `fetch` with `redirect: 'error'`, and reject tokens whose `aud` does not include your server in `verifyAccessToken()`.
5. [If an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md) covers the client-side rotation set.

## Prevention

- [MCP hygiene](../prevention/mcp-hygiene.md): one server instance per session, body limits at the edge, audience-bound tokens, and no custom headers to servers you do not control.

## Sources
- [modelcontextprotocol/typescript-sdk — security advisories tab](https://github.com/modelcontextprotocol/typescript-sdk/security/advisories) — fetched 2026-10-22: ten advisories, the six above dated 2026-10-02 to 10-15.
- [GHSA-22jm-h49p-29qw — Experimental tasks were not tied to the session that created them](https://github.com/advisories/GHSA-22jm-h49p-29qw) — fetched 2026-10-22: CVE-2026-111767, 8.6 and vector, range, the deprecation note, remediation, PR #2925, reporter cipher-creator.
- [GHSA-6prh-2h8m-c8cw — HTTP client transports and OAuth requests followed cross-origin redirects](https://github.com/advisories/GHSA-6prh-2h8m-c8cw) — fetched 2026-10-22: CVE-2026-111769, 6.5, ranges, what a redirect target received, the new default, `redirectPolicy`, rotation advice, PRs #2901 and #2902, reporter nickelsec.
- [GHSA-rvq5-wwqv-78pq — Server bearer authentication accepted tokens issued for another service](https://github.com/advisories/GHSA-rvq5-wwqv-78pq) — fetched 2026-10-22: CVE-2026-111771, 6.8, the four package ranges, "upgrading alone does not enable the fix," `expectedResource`, reporter gdegrange.
- [GHSA-jm63-cq47-j5jp — Shared transport or server instances delivered one HTTP client's messages to another](https://github.com/advisories/GHSA-jm63-cq47-j5jp) — fetched 2026-10-22: CVE-2026-111770, 7.7 and vector, CWE-362, the `id`-only matching, the README examples, the not-affected list, `ALREADY_CONNECTED`, PR #2918, reporters.
- [GHSA-46jr-4wx8-v453 — One HTTP request within the default size limit could exhaust server memory during validation](https://github.com/advisories/GHSA-46jr-4wx8-v453) — fetched 2026-10-22: CVE-2026-111768, 7.5, ranges, `maxToolInputElements` off by default, the two-step mitigation, PRs #2926 and #2927, reporter root-Brainoverflow.
- [GHSA-f897-62hf-6gxq — HTTP server transports and handlers did not limit request body size or JSON-RPC batch length](https://github.com/modelcontextprotocol/typescript-sdk/security/advisories/GHSA-f897-62hf-6gxq) — fetched 2026-10-22: no CVE, 7.5, the four package ranges, the 4 MiB and 100-message limits, `maxRequestBodySize`, seven reporters.
- [CVE Services — CVE-2026-111767](https://cveawg.mitre.org/api/cve/CVE-2026-111767) — fetched 2026-10-22: GitHub CNA, published 2026-10-20, 8.6; CVE-2026-111768 through 111771 returned `CVE_RECORD_DNE` the same day.
- [GitHub Advisory Database — `mcp` listing sorted by published date](https://github.com/advisories?query=mcp+sort%3Apublished-desc) — fetched 2026-10-22: five rows dated 2026-10-20 with the CVE ids above.
- npm registry `time` for the three packages — read 2026-10-22: the publish dates above.
