---
id: 2026-07-vitest-browser-mode-cdp-rce
title: "Vitest Browser Mode — unauthenticated Chrome DevTools Protocol proxy leads to RCE (CVE-2026-53633, CVSS 9.8, public PoC)"
date_disclosed: 2026-06-01
last_updated: 2026-07-29
severity: critical
status: patched
ecosystems: [npm, vite, vitest]
tools_affected: [vitest, "@vitest/browser", vite-plus]
tags: [cve, rce, vite, vitest, chrome-devtools-protocol, unauthenticated, public-poc, testing-framework]
---

## TL;DR
Vitest's **Browser Mode** — the feature that runs your test suite in a real browser instead of a simulated DOM — exposed a `cdp()` API that forwards raw **Chrome DevTools Protocol (CDP)** commands over its WebSocket RPC channel with **no `allowWrite`/`allowExec` gating at all**. Any client that can reach the exposed browser API can use CDP's `Page.setDownloadBehavior` to redirect Chrome's download directory to your project root, then use `Runtime.evaluate` to download a malicious `vite.config.ts` — which Vitest automatically reloads and executes as Node.js code. **CVE-2026-53633**, CVSS **9.8 (critical)**, with a **public proof-of-concept exploit already circulating**. Fixed in `@vitest/browser` 3.2.5, 4.1.8, and 5.0.0-beta.4 (and `vite-plus` 0.1.24).

## What happened
Vitest is the default test runner for most Vite-based projects (React, Vue, Svelte, SvelteKit) and is itself part of the Vite tooling family this repo tracks directly. Its **Browser Mode** feature spins up a real browser instance to run tests and exposes a client API for controlling that browser — including a low-level `cdp()` method that forwards arbitrary Chrome DevTools Protocol commands.

The flaw ([GHSA-g8mr-85jm-7xhm](https://github.com/advisories/GHSA-g8mr-85jm-7xhm)): Vitest's own configuration options for restricting what the Browser Mode API can do — `allowWrite: false` and `allowExec: false` — only gate Vitest's *own* high-level file-write/exec methods. They do **not** gate the raw `cdp()` passthrough, so an attacker who can reach the exposed WebSocket API (network-accessible whenever Browser Mode's server isn't restricted to localhost, or reachable via CSRF/cross-origin WebSocket the same way this repo's tracked "localhost is not a security boundary" cluster describes) can call CDP methods directly:

1. `Page.setDownloadBehavior` — redirect the browser's download directory to the project root.
2. Trigger a download of an attacker-controlled `vite.config.ts`, overwriting the real one.
3. Vitest's file watcher picks up the change and reloads the config — executing the attacker's Node.js code with the privileges of whoever is running the test suite (a developer's machine or, worse, a CI runner).

**CVSS 9.8** (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H) — no privileges, no user interaction, network-reachable, full compromise of confidentiality/integrity/availability. Sources disagree slightly on the exact publish date: the GitHub Advisory Database lists **2026-06-01**, while NVD's own record lists **2026-07-14** — both dates are stated here rather than picking one, per this repo's accuracy bar. Multiple outlets (SecurityOnline, DailyCVE) report a **public proof-of-concept exploit is already available**, and cite Vitest's download count as either "57 million" or "53 million" weekly npm downloads depending on the source — both figures are repeated here as reported rather than resolved to a single number, since neither outlet's own primary data was directly verifiable this sweep.

**Affected versions:** `@vitest/browser` 3.0.0–3.2.4, 4.0.0–4.1.7, 5.0.0-beta.0–5.0.0-beta.3; `vite-plus` ≤0.1.23.
**Patched versions:** `@vitest/browser` 3.2.5, 4.1.8, 5.0.0-beta.4; `vite-plus` 0.1.24.

## Am I affected?
```bash
# Check your installed Vitest browser-mode version
npm ls @vitest/browser 2>/dev/null
cat node_modules/@vitest/browser/package.json | grep '"version"'
```
If you're on an affected version and use Browser Mode (`test.browser.enabled: true` in your Vite/Vitest config) — especially in CI, in a devcontainer, or on any host reachable from an untrusted network — treat this as exploitable until you upgrade. Browser Mode servers bound to `0.0.0.0` (rather than `127.0.0.1`) are the highest-risk case, consistent with this repo's standing "localhost is not a security boundary" caution — a malicious webpage open in another tab can reach a Vitest Browser Mode server the same way it can reach any other unauthenticated local WebSocket service.

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — if a CI runner or dev host was exploited via this path, treat any credentials that host had access to as compromised.
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — never run Browser Mode's server bound to all interfaces on a shared or CI network.
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)

## Why this matters for vibe coders
Vitest ships as the default test runner in most Vite scaffolds (`npm create vite@latest`, SvelteKit, and most React/Vue Vite templates), so a large share of vibe-coded frontend projects have it installed even if the developer never directly thinks about "Vitest security." A CVSS 9.8 RCE with a public PoC in a testing tool this widely deployed — especially one that regularly runs inside CI pipelines holding real secrets — is exactly the kind of dependency-you-didn't-choose-directly risk this repo tracks for Vite itself.

## Sources
- [GitHub Advisory Database — GHSA-g8mr-85jm-7xhm](https://github.com/advisories/GHSA-g8mr-85jm-7xhm) — canonical advisory: affected/patched versions, CVSS, root cause, publish date 2026-06-01.
- [NVD — CVE-2026-53633](https://nvd.nist.gov/vuln/detail/CVE-2026-53633) — canonical CVE record: CVSS 9.8, CWE-749/CWE-862, publish date 2026-07-14 (differs from GHSA's date, both stated per accuracy bar).
- [SentinelOne — CVE-2026-53633: Vitest Browser Mode RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-53633/) — independent corroboration of technical root cause and PoC mechanics.
- [Security Online — Vitest RCE Vulnerability (CVSS 9.8): Public PoC Disclosed for Testing Tool With 57M Weekly Downloads](https://securityonline.info/vitest-rce-vulnerability-cve-2026-53633/) — independent corroboration; source of the "public PoC circulating" and download-count claims.
