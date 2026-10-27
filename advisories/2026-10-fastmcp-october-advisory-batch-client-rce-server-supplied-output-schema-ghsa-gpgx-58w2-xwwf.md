---
id: 2026-10-fastmcp-october-advisory-batch-client-rce-server-supplied-output-schema-ghsa-gpgx-58w2-xwwf
title: "FastMCP October batch: malicious server output schema runs Python in the client (GHSA-gpgx-58w2-xwwf, Critical) plus nine authorization bugs; fixed 3.4.11 and 4.1.3"
date_disclosed: 2026-10-16
last_updated: 2026-10-26
severity: critical
status: patched
ecosystems: [pypi, mcp, fastmcp, agent-framework]
tools_affected: ["fastmcp (PyPI) 2.10.0 up to 3.4.8 and 4.0.0a1 up to 4.0.11 as an MCP client connecting to any server you do not control", "fastmcp servers before 3.4.10 / 4.1.2 using component authorization, OpenAPI-generated components, MultiAuth, the SSE transport, or M2M OAuth client wrappers", "2.x users: no 2.x fix exists"]
tags: [ghsa, fastmcp, mcp, mcp-client, eval-injection, forwardref, output-schema, rce, authorization-bypass, oauth, issuer-binding, sse, host-origin, openapi, path-traversal, incomplete-fix, skills, symlink, no-cve]
---

## TL;DR
FastMCP, the most common Python MCP server and client library, published ten advisories on its repository on 2026-10-16 and 10-20. The one that matters most is on the client side: **GHSA-gpgx-58w2-xwwf** (Critical, no CVE, reporter jlmitra-ampl) lets a malicious or compromised MCP server send a tool output schema whose self-referencing `$ref: "#"` branch passes an untrusted `title` to Python's `ForwardRef`, which evaluates it; the tool call looks successful and the code runs with the client's privileges. Affected `>= 2.10.0, < 3.4.8` and `>= 4.0.0a1, < 4.0.11`; fixed 3.4.8 and 4.0.11 (PRs #5414 and #5413); there is no 2.x fix. Nine further advisories cover servers: post-transform authorization skipped on direct calls (GHSA-7xgj-8392-5q4r, 10-20, fixed 3.4.10 / 4.1.2), M2M OAuth client wrappers built without issuer binding so the client secret can be redirected to an attacker-advertised authorization server (GHSA-vqqp-x5qm-5qp4, 10-20, fixed 4.1.2), OpenAPI components forwarding undeclared header, cookie and query arguments that override configured upstream credentials (GHSA-qvjc-pw7p-hvg5), hashed tool calls bypassing disable and allowlist rules (GHSA-c3q8-4mcq-p7vg), enable/disable routes skipping the auth provider when `required_scopes` is unset (GHSA-63pr-7fpf-v477), OpenAPI path parameters of `..` reaching other backend routes as an incomplete fix for CVE-2026-32871 (GHSA-99xm-8q53-5c8p), skill providers following a symlinked `SKILL.md` outside its folder (GHSA-pwp3-fpg3-p53c, Low), `host_origin_protection` silently ignored on SSE (GHSA-6868-q46w-rmjv), and MultiAuth merging security state across providers (GHSA-76mv-6cmh-q7fj). Releases: 3.4.9 (10-16), 4.1.1 (10-18), 3.4.10, 3.4.11, 4.1.2 and 4.1.3 (10-20, the last pair also moving to certifi 2026.10.19 for the eMudhra removal), 4.1.4 (10-26). Upgrade clients first.

## What happened

**Client RCE.** Per the vendor advisory (published 2026-10-16 by zzstoatzz, CWE-95): when a FastMCP client parses a successful structured result, the `$ref: "#"` branch of `json_schema_type.py` builds a type from the server-supplied schema and passes the schema's `title` to `ForwardRef` without the sanitisation the rest of the file applies. A server the client connects to, or a legitimate server whose package was replaced, therefore chooses code that runs in the client process, and the call returns as if nothing happened. The fix builds schema types with sanitised names. No CVE has been assigned as of 2026-10-26; the GitHub Advisory Database carries the GHSA.

**Server-side batch.** The eight 10-16 advisories and two 10-20 advisories are listed above with the vendor's titles; all but the skills one are Moderate on the vendor tab. The two 10-20 items surfaced on the GitHub Advisory Database `mcp` listing on 10-23, which is how this batch was found.

**Registry.** `pip index versions fastmcp` returned no output in this session on 2026-10-26; version facts here come from the repository releases page fetched the same day.

Why it is here: FastMCP is the library behind a large share of the MCP servers coding agents install, and the client bug inverts the usual threat: here the server attacks the agent host. Earlier FastMCP-adjacent entries: [Starlette bad-host bypass](2026-05-starlette-badhost-host-header-bypass.md), [mcp-atlassian mass assignment](2026-09-mcp-atlassian-cve-mass-assignment.md).

## Am I affected?

- `pip show fastmcp` in every environment that runs an MCP client (agents, gateways, test harnesses): below 3.4.8 on 3.x, below 4.0.11 on 4.x, or any 2.x, is exposed to the client RCE from any server you connect to.
- Servers: below 3.4.10 / 4.1.2 if you rely on component authorization, OpenAPI-generated tools, MultiAuth, SSE with origin protection, or M2M OAuth wrappers.
- Check which third-party MCP servers each affected client has connected to since the release; a server you did not audit is a code-execution path.

## If you are affected

1. Upgrade clients to 3.4.11 or 4.1.4; 2.x must move to 3.x.
2. Upgrade servers to the same and re-test authorization on direct calls and hashed names.
3. If a client on an affected version connected to an untrusted server, treat the host as having run that server's code: [if an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md).

## Prevention

- [MCP hygiene](../prevention/mcp-hygiene.md): pin and review every server; the client library is part of the trust boundary.
- [Agent sandboxing](../prevention/agent-sandboxing.md): run clients that talk to third-party servers in a container without your credentials.

## Sources
- [jlowin/fastmcp — GHSA-gpgx-58w2-xwwf: Remote code execution in FastMCP client when parsing a server-supplied tool output schema](https://github.com/jlowin/fastmcp/security/advisories/GHSA-gpgx-58w2-xwwf) — fetched 2026-10-26: published 2026-10-16, affected and patched ranges, the `ForwardRef` mechanism, CWE-95, PRs #5413 and #5414, reporter credit, "no 2.x fix".
- [jlowin/fastmcp — security advisories tab](https://github.com/jlowin/fastmcp/security/advisories) — fetched 2026-10-26: the ten October advisories with ids, titles, severities and dates.
- [jlowin/fastmcp — releases](https://github.com/jlowin/fastmcp/releases) — fetched 2026-10-26: 3.4.9, 4.1.1, 3.4.10, 3.4.11, 4.1.2, 4.1.3, 4.1.4 dates and the certifi note.
- [GitHub Advisory Database — `mcp` listing](https://github.com/advisories?query=mcp) — fetched 2026-10-26: GHSA-7xgj-8392-5q4r and GHSA-vqqp-x5qm-5qp4 dated 2026-10-23.
