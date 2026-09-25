---
id: 2026-09-opencode-global-upgrade-cross-site-npm-install-rce
title: "OpenCode 1.14.30–1.18.21 (npm / pnpm / Bun installs): any web page could tell a running `opencode serve` or `opencode web` to 'upgrade' itself from an attacker's tarball — a `text/plain` form post reaches `/global/upgrade`, the `target` goes straight into `npm install -g opencode-ai@…`, and the package's lifecycle scripts run as you; fixed 1.18.22 on 2026-08-24, disclosed by Datadog 2026-09-24, no CVE by vendor choice"
date_disclosed: 2026-09-24
last_updated: 2026-09-25
severity: high
status: patched
ecosystems: [ai-agents, ai-ide, npm]
tools_affected: [opencode, anomalyco-opencode, "opencode-ai (npm)", "pnpm / Bun installs of OpenCode"]
tags: [cve-declined, rce, csrf, localhost, browser-attacker-model, content-type-confusion, npm-lifecycle-scripts, ai-ide, silent-patch, no-cve]
---

## TL;DR
On **2026-09-24** Datadog Security Labs published [GHSA-632h-h47v-g4x4](https://github.com/anomalyco/opencode/security/advisories/GHSA-632h-h47v-g4x4): while **OpenCode** (the open-source coding agent from Anomaly, formerly SST; **~1.67M npm downloads/week** as `opencode-ai`) is serving its local HTTP API via `opencode serve` or `opencode web`, **a web page in the developer's browser can post to `/global/upgrade`** and name the version to install. The handler parsed the body as JSON without checking `Content-Type`, so a plain HTML form (`text/plain`, no CORS preflight) reached it, and the `target` string went unvalidated into **`npm install -g opencode-ai@${target}`** — which npm accepts as a package spec, including a remote tarball URL, whose lifecycle scripts run on the developer's machine. Affects **1.14.30 through 1.18.21 when installed through npm, pnpm or Bun**; curl/Homebrew/Chocolatey/Scoop installs are not affected. **Fixed in 1.18.22 (2026-08-24)** — a month before disclosure, with no changelog security note. Datadog counts **647,000+ downloads of the 82 vulnerable versions between 2026-09-17 and 09-23**, i.e. after the fix shipped. The vendor **chose not to request a CVE**, so `npm audit` and CVE-driven scanners will never flag it. Same "localhost is not a boundary in the browser-attacker model" class as OpenCode's January pair — a different endpoint, a different fix, a different disclosure.

## What happened

**The endpoint.** OpenCode's local server exposes `POST /global/upgrade` so the UI can update the agent in place. Per the vendor advisory, "When OpenCode is installed via npm, pnpm, or Bun, a malicious webpage can submit a cross-site request that specifies an arbitrary package URL as the upgrade target. The endpoint fails to validate the request origin and accepts package specifications that point to attacker-controlled tarballs, enabling remote code execution through npm lifecycle scripts." The affected code "passes the untrusted `target` parameter directly to package manager commands: `npm install -g opencode-ai@${target}`."

**Why the browser could reach it.** Two things had to be true, and Datadog's write-up shows both. First, the server's origin check did not cover this route in the way the browser-side protections assume: a cross-site request with `Content-Type: text/plain` is a "simple" request under CORS, so the browser sends it without a preflight. Second, "the `upgradeRaw` handler parses the body as JSON without verifying that the `Content-Type` is `application/json`" — so the plain-text body was decoded as the JSON the handler expected. Datadog's framing: a content-type confusion made an underlying code-injection flaw reachable from a web page.

**Who was exposed.** Datadog's conditions, verbatim: the bug "is exploitable only if all of the following conditions apply: You use OpenCode 1.14.30 through 1.18.21, inclusive. You run `opencode serve` or `opencode web` without password authentication, or your browser has cached credentials from a recent authentication." Plus the npm/pnpm/Bun install path — the other installers do not run `npm install -g` to upgrade. The vendor advisory adds: "Password protection provides insufficient defense when the browser has cached HTTP Basic credentials."

**The fix.** Version **1.18.22** "enforced semantic version validation and switched from `handleRaw` to `handle`," which "inspects the `Content-Type` header and decodes the request body accordingly." The advisory lists the fix as requiring "proper JSON content-type, include explicit target parameters, and specify only valid semantic versions rather than general package specifiers." Registry dates: `1.18.21` published 2026-08-21, `1.18.22` 2026-08-24, `1.18.23` 2026-08-25.

**The disclosure choice.** Timeline from Datadog: reported through GitHub Security Advisories **2026-08-11**; fix merged and 1.18.22 released **2026-08-24**; public disclosure **2026-09-24** at the vendor's request. And: "Anomaly chose not to request a CVE for this vulnerability. Anomaly believes that assigning CVEs to vulnerabilities reported through GitHub Security Advisories incentivizes researchers to submit a high volume of low-quality reports." The vendor advisory carries CVSS 3.1 **7.5** (`AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H`), severity High. The vendor page lists affected as `>= 1.14.30` with patched `1.18.22`; Datadog's "through 1.18.21" is the same range read from the other end.

**A version-range note.** One of this sweep's reads of the vendor page reported "1.14.30 through 1.18.16"; the page's package table says `>= 1.14.30` / patched `1.18.22`, and Datadog's article says 1.18.21 inclusive. Use **< 1.18.22** as the affected test.

**Why it matters for vibe coders.** OpenCode is one of the most-installed open-source coding agents, and `opencode serve`/`opencode web` is how people run it as a long-lived local service for the browser UI, for remote clients, and for "keep the agent running 24/7" setups. Every one of those is a browser tab away from any site the developer visits. The payload path is not the agent's shell tool at all — it is **npm's own install-time script execution**, the same primitive as every install-hook supply-chain wave in this corpus, triggered by the tool's self-updater. And because the fix shipped silently and the vendor declined a CVE, **nothing in `npm audit`, Dependabot, or a CVE feed will tell you** — only the version number does. This is the third OpenCode disclosure in this repo's window; the [January pair](2026-01-opencode-localhost-rce.md) (CVE-2026-22812 / CVE-2026-22813) was the unauthenticated shell endpoint and the markdown XSS, fixed in 1.0.216 by adding a per-session token; this one is a route that token did not protect against a same-browser cross-site post.

## Am I affected?

- **Affected if:** OpenCode was installed with `npm i -g opencode-ai`, `pnpm add -g opencode-ai` or `bun add -g opencode-ai`, the version is **≥ 1.14.30 and < 1.18.22**, and you ever ran `opencode serve` or `opencode web` (with no password, or with a password your browser then cached) while browsing.
- **Not affected:** curl-script, Homebrew, Chocolatey or Scoop installs (they do not upgrade through `npm install -g`); versions ≥ 1.18.22.

```bash
opencode --version 2>/dev/null
npm ls -g opencode-ai 2>/dev/null | grep opencode-ai        # npm install path?
pnpm ls -g 2>/dev/null | grep opencode-ai
bun pm ls -g 2>/dev/null | grep opencode-ai
# Was the server ever exposed? Look for serve/web invocations in shell history
grep -hE 'opencode (serve|web)' ~/.bash_history ~/.zsh_history 2>/dev/null | head
# Did an "upgrade" install something that is not opencode-ai@<semver>?
npm ls -g --depth=0 2>/dev/null | grep -i opencode
```

If a global install shows a version that does not exist on the registry, or `opencode-ai` resolving to a tarball/URL rather than a semver, treat the machine as compromised.

## If you are affected

1. **Upgrade to ≥ 1.18.22** through the same installer you used, then verify with `opencode --version`.
2. If you ran `opencode serve`/`web` on a vulnerable version while browsing, assume an attacker-controlled package could have run install scripts as your user: → [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md), → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md). Rotate what the agent's environment could see (provider API keys in OpenCode's config, `~/.ssh`, cloud CLI credentials, npm/GitHub tokens): → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. Check the global `node_modules` for packages you did not install and the OpenCode config directory for changed provider/MCP settings.

## Prevention

- **Do not leave a coding agent's local server running unauthenticated while you browse**, and do not rely on "localhost only" — a browser tab is on localhost. Run `opencode serve` only when needed, behind a password you do not let the browser cache, or inside a container/VM: [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- **Keep AI tools on `latest`, not a pin** — this fix, like Claude Code's SOCKS bypass and Codex's `apply_patch` widening, shipped without a CVE or a security note; the version number is the only signal ([prevention/npm-hardening.md](../prevention/npm-hardening.md) on install-script exposure: `ignore-scripts` would have blocked this payload path).
- **Treat a self-updater as a package-install surface.** Anything that runs `npm install -g <input>` must validate the input as a semver, not a package spec.

## Sources
- [Datadog Security Labs — Discovering and exploiting a remote code execution vulnerability in OpenCode (GHSA-632h-h47v-g4x4)](https://securitylabs.datadoghq.com/articles/opencode-upgrade-remote-code-execution/) — primary, 2026-09-24 (Christophe Tafani-Dereeper): the `/global/upgrade` mechanism, the `text/plain` content-type confusion, the exploitation conditions verbatim, the 1.14.30–1.18.21 range, the 647,000 downloads (09-17 → 09-23) of 82 vulnerable versions, the 08-11 / 08-24 / 09-24 timeline, and the vendor's no-CVE rationale. Fetched 2026-09-25.
- [anomalyco/opencode — GHSA-632h-h47v-g4x4: Cross-site OpenCode server upgrade request can install arbitrary packages for npm-based installations](https://github.com/anomalyco/opencode/security/advisories/GHSA-632h-h47v-g4x4) — vendor advisory, published 2026-09-24: severity High, CVSS 3.1 7.5 and vector, affected `>= 1.14.30`, patched 1.18.22, the `npm install -g opencode-ai@${target}` line, the cached-Basic-credentials caveat, the not-affected installers, credit to christophetd. Fetched 2026-09-25. (The `github.com/advisories/` mirror returned 404 on 2026-09-25 — use the vendor-repo URL.)
- [anomalyco/opencode — security advisories tab](https://github.com/anomalyco/opencode/security/advisories) — fetched 2026-09-25: three advisories, this one newest (09-24), the January pair (GHSA-c83v-7274-4vgp, GHSA-vxw4-wv6m-9hhh) before it.
- npm registry — `npm view opencode-ai time` (fetched 2026-09-25): 1.14.30 = 2026-04-29, 1.18.21 = 2026-08-21, 1.18.22 = 2026-08-24, 1.18.23 = 2026-08-25; `api.npmjs.org/downloads/point/last-week/opencode-ai` = 1,665,504 (2026-09-15 → 09-21).
- Surfaced by the Hacker News Algolia feed (2026-09-24, 4 points); no outlet coverage found at sweep time.
- Related in this corpus: [OpenCode twin localhost RCEs, January 2026](2026-01-opencode-localhost-rce.md) (CVE-2026-22812 / CVE-2026-22813, fixed 1.0.216); [Codex Heapjack/Overpatch](2026-09-codex-heapjack-overpatch-sandbox-escapes.md) and [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md) for the other 2026 coding-agent fixes that never reached a CVE feed.
