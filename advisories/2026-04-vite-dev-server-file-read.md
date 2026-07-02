---
id: 2026-04-vite-dev-server-file-read
title: "Vite dev-server WebSocket arbitrary file read + fs.deny bypasses (CVE-2026-39363, CVE-2026-39364, CVE-2026-39365)"
date_disclosed: 2026-04-06
last_updated: 2026-07-02
severity: high
status: patched
ecosystems: [vite, npm]
tools_affected: [vite]
tags: [file-read, dev-server, websocket, path-traversal, access-control-bypass]
---

## TL;DR
Three related flaws in **Vite**'s dev server let an attacker who can reach it over the network (e.g. it was started with `--host` or otherwise exposed) read **arbitrary files on the machine** — including `.env` secrets — by talking to the HMR WebSocket directly or by appending query parameters that dodge the `server.fs.deny`/`server.fs.allow` checks. Fixed in **Vite 6.4.2 / 7.3.2 / 8.0.5**.

## What happened
Vite's dev server exposes an HMR WebSocket alongside its HTTP interface, and the two don't enforce the same access controls:

- **CVE-2026-39363 (CVSS 8.2)** — the WebSocket's `vite:invoke` event can call the internal `fetchModule` method directly. `fetchModule` doesn't apply the `server.fs` restrictions that gate the HTTP request path. An attacker who can open a WebSocket connection to the dev server **without an `Origin` header** can request a `file://` path with a query suffix like `?raw` or `?inline` and get the raw file contents back as a JS module string — bypassing the HTTP-level file-access allowlist entirely.
- **CVE-2026-39364 (CVSS 8.2)** — `server.fs.deny` (Vite's denylist for sensitive files like `.env` or TLS keys) can be bypassed by appending query parameters — files that should 404 are instead returned with an HTTP 200 when the request carries a suffix like `?raw`, `?import&raw`, or `?import&url&inline`.
- **CVE-2026-39365 (CVSS 5.3 medium)** — the dev server's handling of `.map` (source map) requests for optimized dependencies resolves file paths and calls `readFile` **without stripping `../` segments** from the URL, letting a request walk outside the project root and outside the `server.fs.strict` allowlist to fetch arbitrary `.map` files. Also affects the `vite-plus` package (≤ 0.1.15).

All three require the dev server to be network-reachable (started with `--host`, or otherwise not bound to loopback-only) — the default `vite dev` on `localhost` without `--host` is not exposed to this from outside the machine, but any container, Codespace, VM, or shared dev environment where Vite listens on a non-loopback interface is in scope, as is any browser tab on the same host/network per the broader "localhost is not a security boundary" pattern this repo tracks for local dev servers.

## Am I affected?
```bash
npm ls vite
```
Vulnerable ranges: CVE-2026-39363 and CVE-2026-39365 affect **6.0.0 – 6.4.1**, **7.0.0 – 7.3.1**, and **8.0.0 – 8.0.4**; CVE-2026-39364 affects **7.1.0 – 7.3.1** and **8.0.0 – 8.0.4** (6.x branch not affected). Fixed in **6.4.2**, **7.3.2**, **8.0.5** (and later). If you (or a CI/preview environment) ever run `vite dev --host` or otherwise expose the dev server beyond localhost, treat any secrets in `.env` files in that project as potentially read during the exposure window.

## If you are affected
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — rotate anything in a `.env` the dev server could reach.
→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention
→ Upgrade to a patched Vite release; don't run `--host` / expose the dev server beyond `127.0.0.1` unless you also gate it behind auth or a VPN.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — keep secrets out of files a dev server could ever serve; prefer environment injection at the process level over `.env` files in the project root.

## Sources
- [GitHub Advisory Database — GHSA-p9ff-h696-f583 (CVE-2026-39363, Vite arbitrary file read via dev server WebSocket)](https://github.com/advisories/GHSA-p9ff-h696-f583)
- [GitHub Advisory Database — GHSA-v2wj-q39q-566r (CVE-2026-39364, Vite server.fs.deny bypassed with queries)](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [NVD — CVE-2026-39365 (Vite source-map path traversal)](https://nvd.nist.gov/vuln/detail/CVE-2026-39365)
- [SentinelOne Vulnerability Database — CVE-2026-39363](https://www.sentinelone.com/vulnerability-database/cve-2026-39363/)
