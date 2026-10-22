---
id: 2026-10-opencode-mcp-oauth-authorization-endpoint-powershell-command-injection-windows-wsl-fixed-1-18-33-no-cve
title: "OpenCode 1.0.137 to 1.18.32 on Windows and WSL: a remote MCP server's OAuth authorization endpoint ran PowerShell at sign-in; fixed 1.18.33, no CVE"
date_disclosed: 2026-10-19
last_updated: 2026-10-22
severity: high
status: patched
ecosystems: [npm, ai-coding-agents, mcp, windows]
tools_affected: ["opencode-ai (npm) 1.0.137 through 1.18.32 on Windows and WSL; macOS and Linux not affected", "any developer who ran `opencode mcp auth` against a remote MCP server not under their control", "other MCP clients that pass a server-supplied URL to the `open` npm package below 11.0.0 on Windows"]
tags: [mcp, oauth, command-injection, powershell, open-package, windows, wsl, opencode, no-cve, silent-fix, out-of-threat-model, pillar-security, cwe-78, mcp-remote-class]
---

## TL;DR
Pillar Security reports that OpenCode on Windows and WSL passed the `authorization_endpoint` an MCP server supplies during OAuth discovery straight to the `open` package (pinned at 10.1.2), which built a PowerShell command around it without escaping the URL, so a well-formed https address containing a PowerShell subexpression ran attacker-chosen commands with the developer's privileges when the developer started sign-in. The server need not be malicious when configured; a later takeover, a hijacked registry entry or an expired domain reaches the same path. Anomaly fixed it in 1.18.33 (npm 2026-09-28) by bumping `open` to 11.0.4 and adding a scheme check, in a pull request described as a browser-launch refactor whose release note says "MCP browser launch failures are now reported"; it told Pillar that a malicious MCP server is outside its threat model and declined to request a CVE, so no scanner will flag affected installs. Pillar's proposed CVSS 3.1 is 9.8; this file rates it `high` because the vector needs the developer to run `opencode mcp auth` against a remote server the attacker controls, on Windows or WSL. Upgrade, and inventory OpenCode on Windows hosts by hand.

## What happened

**Mechanism (Pillar Security, 2026-10-19).** An MCP server that requires authorization answers with a 401 and a `WWW-Authenticate` challenge pointing to discovery documents; the `authorization_endpoint` field there is a free string the server chooses. It flowed through the MCP SDK, `oauth-provider.ts`, `mcp/index.ts` and `browser.ts` to `open()`, which on Windows escapes the application name but not the target URL and passes the command to `powershell -EncodedCommand`; PowerShell expands `$(...)` inside double-quoted strings. The browser launch then fails and OpenCode discards the error. CWE-78 with CWE-88. The report's central point is that scheme validation does not stop the payload, because it is a well-formed `https:` URL with no spaces: the MCP SDK's denylist (`javascript:`, `data:`, `vbscript:`) allows it, the stricter http/https allowlist the SDK rejected (PR #841, closed; PR #877 merged in 1.17.4) would allow it, and OpenCode's new `openUrl()` check allows it. The change that closed the hole was `open` 11.0.4, which wraps the target in single quotes.

**History of the sink.** `open` issue #202 (2020-10-22) reported URLs with `$` breaking on WSL; issue #323 (2023-10-18) described the command injection with a one-line proof, and the maintainer replied that sanitising untrusted input is the caller's job, which the README has said since 2021-09-17; `open` 11.0.0 (2025-11-15) fixed PowerShell argument escaping. OpenCode added `await open(authorizationUrl)` on 2025-12-07 (commit 509e43d6) with `open@10.1.2` already pinned. Pillar lists three earlier CVEs on the same sink: mcp-remote CVE-2025-6514, openmcp-client CVE-2025-58062, sequa-mcp CVE-2025-10619.

**Disclosure.** Reported privately through a GitHub Security Advisory on 2026-08-29; on 2026-09-25 Anomaly confirmed receipt, said malicious MCP servers are outside its threat model, and merged PR #51414 (commit 29f07e0c: `open` to 11.0.4, a new `openUrl()` rejecting non-http(s) schemes, a scheme check in `redirectToAuthorization`); Pillar asked for a CVE and said it would publish; 1.18.33 reached npm on 2026-09-28. Pillar's page is dated 2026-10-19 and The Hacker News reports the public disclosure as 10-19; the page's own timeline prints 2026-10-04 as the publication date, a discrepancy this file records rather than resolves. The Hacker News adds that Pillar later asked Anomaly to reconsider the CVE and that Pillar reports no known exploitation and published no indicators. OpenCode's security policy says user-configured MCP servers are "outside our trust boundary"; its advisories tab (read 2026-10-22) lists three unrelated advisories and nothing for this.

**Registry.** npm `opencode-ai`, read 2026-10-22: newest 1.19.4 (2026-10-22). Pillar contrasts gemini-cli (scheme-gated `execFile`), Claude Code (the OAuth path cannot pass a server value to the opener), github-mcp-server and Docker mcp-gateway (argv openers, operator-chosen authorization servers) as clients that avoid the sink.

Why it is here: it is the mcp-remote bug class a year on, in a coding agent with its own breach [five days earlier](2026-10-opencode-console-legacy-system-breach-provider-api-keys-exposed-distillation-attack.md), with the twist that the vendor's position and the missing CVE leave the affected range invisible to dependency tooling.

## Am I affected?

- Windows or WSL, `opencode --version` between 1.0.137 and 1.18.32, and at least one remote MCP server configured. `opencode mcp list` shows them.
- The code ran only when the developer started sign-in (`opencode mcp auth` or the matching request). Configuring the server or opening a session did not trigger it.
- No CVE, so `npm audit`, Dependabot and SCA tools will not report it; inventory by version.

## If you are affected

1. Upgrade to 1.18.33 or later (1.19.4 is current).
2. If you cannot upgrade, remove unvetted remote MCP servers from the configuration; Pillar says keeping them means accepting the exposure.
3. If a sign-in was run against a server you did not control while on an affected version on Windows or WSL, treat the machine as having run that server's command: [if an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md), then [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).
4. Maintainers of anything that calls `open`: pass nothing remote to it; 11.x escaping is a layer, not a fix; scheme checks are necessary and insufficient; use argv openers.

## Prevention

- [MCP hygiene](../prevention/mcp-hygiene.md): every server-controlled field is untrusted input, including OAuth discovery; bind discovery to the configured origin.
- [Agent sandboxing](../prevention/agent-sandboxing.md).

## Sources
- [Pillar Security — Open and Shut: Remote Code Execution in opencode via MCP OAuth](https://www.pillar.security/blog/open-and-shut-remote-code-execution-in-opencode-via-mcp-oauth) — fetched 2026-10-22 (page dated 2026-10-19, Eilon Cohen): affected and fixed versions, the mechanism and the chain of files, the `open` history with issue and release dates, the scheme-validation argument, the disclosure timeline, the fix contents, the peer comparison, the recommendations.
- [The Hacker News — OpenCode Flaw Lets Malicious MCP Servers Execute Code During Sign-In on Windows and WSL](https://thehackernews.com/2026/10/opencode-flaw-lets-malicious-mcp.html) — fetched 2026-10-22 (2026-10-22, Swati Khandelwal): no CVE requested, the 9.8 as Pillar's proposal, the vendor policy quotation, the 10-19 public disclosure date, no known exploitation.
- [anomalyco/opencode — release v1.18.33](https://github.com/anomalyco/opencode/releases/tag/v1.18.33) — fetched 2026-10-22: dated 28 Sep, the four bugfix lines quoted above, no security wording.
- [anomalyco/opencode — security advisories tab](https://github.com/anomalyco/opencode/security/advisories) — fetched 2026-10-22: three advisories (2026-01-12 ×2, 2026-09-24), none for this issue.
- npm registry `time` for `opencode-ai` — read 2026-10-22: 1.19.4 on 2026-10-22; `npm view open version` 11.0.4.
- Related in this corpus: [OpenCode localhost RCE (January)](2026-01-opencode-localhost-rce.md), [OpenCode global-upgrade cross-site install](2026-09-opencode-global-upgrade-cross-site-npm-install-rce.md), [OpenCode Console breach](2026-10-opencode-console-legacy-system-breach-provider-api-keys-exposed-distillation-attack.md).
