---
id: 2026-11-nodejs-november-11-security-release-sixteen-cves-http2-crash-memory-disclosure-https-heap-read-tls-client-cert-bypass
title: "Node.js 22.23.5, 24.22.3, 26.13.1 fix 16 CVEs: HTTP/2 crash and memory disclosure, HTTPS heap read (CVE-2026-123864), TLS client-certificate bypasses"
date_disclosed: 2026-11-11
last_updated: 2026-11-12
severity: high
status: patched
ecosystems: [nodejs, npm, javascript, nextjs, serverless, ci-cd]
tools_affected: ["Node.js 22.x before 22.23.5, 24.x before 24.22.3, 26.x before 26.13.1", "Node.js 20.x, 25.x and other end-of-life lines (no fix)", "any Node.js server that terminates HTTP/2 or HTTPS itself: self-hosted Next.js, Express, Fastify, gRPC services, MCP servers over HTTP", "servers that use per-hostname client-certificate policies (mTLS) through SNI contexts", "code that relies on the Node.js Permission Model with wildcard file grants"]
tags: [cve, nodejs, http2, https, tls, mtls, memory-disclosure, denial-of-service, use-after-free, permission-model, proxy-credentials, security-release, ai-found]
---

## TL;DR
Node.js released 22.23.5, 24.22.3 and 26.13.1 with fixes for 16 CVEs: seven High, six Medium and three Low by the project's own ratings. An unauthenticated client can crash a default HTTP/2 server on 24.x and 26.x (CVE-2026-123863). Two flaws can send a client memory that belongs to other connections: CVE-2026-123864 on HTTPS servers, which the project says can include TLS private keys and other users' requests, and CVE-2026-123866 on HTTP/2. Two more let a client reach a hostname whose client-certificate policy it does not satisfy. Upgrade and restart. The advisory lists no workaround and reports no attacks. End-of-life lines get no fix.

## What happened

The Node.js project published "Wednesday, November 11, 2026 Security Releases". It had pre-announced the release on 2026-11-04 with no CVE ids. The release also updates bundled llhttp (22.x, 24.x, 26.x), undici (24.x, 26.x) and sqlite (22.x, 24.x) "to address public vulnerabilities".

The counts below were made in code against the advisory page: 16 distinct new CVE ids, seven High, six Medium, three Low.

| CVE | Project rating | Lines | What the advisory says |
|---|---|---|---|
| CVE-2026-123863 | High | 24.x, 26.x | Any unauthenticated client can abort a default HTTP/2 server whose handler responds before the request body has ended, over TLS and cleartext. A variant of CVE-2024-27983 that the earlier fix did not cover. |
| CVE-2026-123864 | High | 22.x, 24.x, 26.x | An unauthenticated client can read memory belonging to other connections on an HTTPS server, "including TLS private keys and other users' requests". Needs a handler that calls `res.flushHeaders()` before the request body ends and later calls `res.end()` with a non-empty chunk, plus a route that echoes or stores a request body. Cleartext `node:http` is not affected. |
| CVE-2026-123865 | High | 22.x, 24.x, 26.x | An unauthenticated HTTP/2 client can leak server memory and file descriptors permanently. An incomplete fix of CVE-2026-48937. |
| CVE-2026-123866 | High | 22.x, 24.x, 26.x | HTTP/2 stream teardown can write freed response memory, including other connections' response buffers, to a peer. A remote peer alone can drive it on 24.22.0 and later and 26.9.0 and later. On all lines an application-initiated teardown such as a per-stream idle timeout reaches it. |
| CVE-2026-126051 | High | 24.x, 26.x | A remote, unauthenticated client can terminate a TLS server that uses `SNICallback`, `OCSPRequest`, `newSession` or `resumeSession` hooks, or `server.addContext()`. |
| CVE-2026-123872 | High | 22.x, 24.x, 26.x | A client can change the servername during TLS 1.2 renegotiation and carry its client-certificate authentication to a hostname with a stricter policy. |
| CVE-2026-123874 | High | 24.x, 26.x | An unauthenticated client can corrupt server memory when the application serves files with `respondWithFile()` or `respondWithFD()`. |
| CVE-2026-123828 | Medium | 24.x, 26.x | One-byte heap overflow when an application passes an attacker-controlled value to `Http2Session.altsvc()`. |
| CVE-2026-123867 | Medium | 22.x, 24.x, 26.x | An SNI context added with a client CA and no server certificate falls back to the default client CA, so per-host mTLS authorization is bypassed. |
| CVE-2026-123868 | Medium | 24.x, 26.x | An unauthenticated HTTP/2 client can exhaust server memory. `maxSessionMemory` does not bound it. |
| CVE-2026-123871 | Medium | 22.x, 24.x, 26.x | Proxy credentials appear in `ERR_PROXY_INVALID_CONFIG` error messages, and so in stderr, container logs and crash reports. Four error paths the fix for CVE-2026-48615 missed. |
| CVE-2026-123877 | Medium | 22.x, 24.x, 26.x | `https.Agent` reuses a TLS session authenticated under the default trust store for a later request that sets `ca: []`. |
| CVE-2026-123875 | Medium | 22.x, 24.x, 26.x | A client that cancels a `respondWithFile()` or `respondWithFD()` download can crash an HTTP/2 server. |
| CVE-2026-123829 | Low | 22.x, 24.x, 26.x | Permission Model: recursive `fs.watch` on macOS and Windows reports names of files the process may not read. |
| CVE-2026-123862 | Low | 22.x, 24.x, 26.x | A peer that disconnects while a stream calls `zlib.params()` can crash the process. |
| CVE-2026-106071 | Low | 22.x, 24.x, 26.x | Permission Model: a wildcard `--allow-fs-read` or `--allow-fs-write` grant can match a shorter path. |

Scores. The OpenJS Foundation is the CNA. Its records, published 2026-11-11 and read 2026-11-12, give CVSS 3.0 base scores of 8.2 for CVE-2026-123863, 8.1 for CVE-2026-123864 and 7.5 for CVE-2026-123866. This sweep queried those three records and no others. This file's `severity` is `high`, which matches the project's highest rating.

Dates. The advisory is titled 2026-11-11. The `nodejs.org/dist/index.json` release index dates v26.13.1 and v24.22.3 2026-11-10 and v22.23.5 2026-11-11, and marks all three as security releases.

Credits. Five of the sixteen (CVE-2026-123863, CVE-2026-123864, CVE-2026-123874, CVE-2026-123875, CVE-2026-123862) are credited to "Chris Rohlf in collaboration with Claude and Anthropic Research". CVE-2026-123829 is credited to "Trail of Bits (OpenAI)". The others name individual reporters.

What the advisory does not say. The Hacker News (2026-11-12) notes that it lists no workaround, reports no attacks, and does not say whether operators of HTTPS servers exposed to CVE-2026-123864 should rotate TLS keys after updating. This file does not answer that either. The conservative reading of "including TLS private keys" is in the steps below and is this file's advice, not the project's.

## Am I affected?

- `node --version`. Affected below 22.23.5 on 22.x, 24.22.3 on 24.x, 26.13.1 on 26.x. The project says end-of-life versions "are always affected when a security release occurs", which covers 20.x and 25.x.
- Check container base image tags and CI runner images, not only the host.
- You are exposed to the HTTP/2 flaws only where Node itself speaks HTTP/2 to untrusted clients: `node:http2` servers, gRPC services, frameworks configured for HTTP/2. A reverse proxy or CDN that terminates HTTP/2 and speaks HTTP/1.1 to Node removes that path. It does not remove CVE-2026-123864 when the proxy connects to Node over HTTPS.
- For CVE-2026-123864, search handlers for `flushHeaders()` followed by a later `res.end(` with data, on a server created with `node:https`.
- For the mTLS flaws (CVE-2026-123872, CVE-2026-123867), check for `server.addContext(` with a `ca` option, and for per-hostname client-certificate rules on a server that still accepts TLS 1.2 renegotiation.
- For CVE-2026-123871, search logs and crash reports for `ERR_PROXY_INVALID_CONFIG`. A hit may contain the proxy username and password.
- Managed platforms patch their own runtimes on their own schedule. This sweep opened no platform bulletin for this release, so check your provider's.

## If you are affected

1. Upgrade to 22.23.5, 24.22.3 or 26.13.1 and restart every process. Rebuild container images on a patched base and redeploy.
2. On 20.x, 25.x or older, move to a supported line. There is no fix.
3. If a public `node:https` server matched the CVE-2026-123864 handler pattern, treat its TLS private key and any secrets that passed through request bodies as possibly disclosed. Reissue the certificate with a new key after upgrading. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) for the order of work.
4. If `ERR_PROXY_INVALID_CONFIG` appears in shared logs, rotate the proxy credential.
5. Until you can upgrade, put a proxy that terminates HTTP/2 and TLS in front of Node. This is not a project-stated workaround.

## Prevention

- [CI/CD hardening](../prevention/ci-cd-hardening.md): pin runtime images to a supported line and rebuild on every security release.
- [Credential hygiene](../prevention/credential-hygiene.md): keep proxy credentials out of URLs that can reach error messages, and scrub logs before they leave the host.
- The Node.js Permission Model fixes here are two more boundary corrections. Do not use it as the only sandbox for an agent or for untrusted code. See [agent sandboxing](../prevention/agent-sandboxing.md).

## Sources

- [Node.js: Wednesday, November 11, 2026 Security Releases](https://nodejs.org/en/blog/vulnerability/november-2026-security-releases), fetched 2026-11-12: the sixteen CVEs with ratings, affected lines, descriptions and credits, the dependency updates, the fixed versions and the end-of-life note.
- [CVE Services: CVE-2026-123863](https://cveawg.mitre.org/api/cve/CVE-2026-123863), [CVE-2026-123864](https://cveawg.mitre.org/api/cve/CVE-2026-123864) and [CVE-2026-123866](https://cveawg.mitre.org/api/cve/CVE-2026-123866), fetched 2026-11-12: OpenJS CNA, published 2026-11-11, CVSS 3.0 8.2, 8.1 and 7.5, affected ranges ending at the fixed versions.
- [Node.js release index](https://nodejs.org/dist/index.json), fetched 2026-11-12: v26.13.1 and v24.22.3 dated 2026-11-10, v22.23.5 dated 2026-11-11, all flagged `security`.
- [The Hacker News: Node.js Fixes 16 Flaws, Including HTTP/2 Bugs That Crash Servers and Leak Other Connections' Data](https://thehackernews.com/2026/11/nodejs-fixes-16-flaws-including-http2.html), fetched 2026-11-12 (2026-11-12): no workaround, no reported attacks, the open question on rotating TLS keys, and the note that 20.x and 25.x get no fix.
- Related in this corpus: [the 2026-10-21 Node.js release](2026-10-nodejs-october-21-security-release-brotli-decoder-rce-cve-2026-111497-tls-hostname-bypasses.md), whose 2026-11-04 Update recorded the pre-announcement of this one.
