---
id: 2026-08-siteboon-claude-code-ui-rce-batch
title: "@siteboon/claude-code-ui — three command-injection CVEs, including unauthenticated RCE from a default JWT secret (backfill)"
date_disclosed: 2026-03-09
last_updated: 2026-08-20
severity: critical
status: patched
ecosystems: [npm, claude-code, cursor, codex, gemini-cli]
tools_affected: ["@siteboon/claude-code-ui", "claudecodeui"]
tags: [command-injection, rce, npm, authentication-bypass, ai-coding-tool, wrapper-ui, default-credentials]
---

## TL;DR

**`@siteboon/claude-code-ui`** — a popular self-hosted web UI that wraps Claude Code, Cursor CLI, Codex, and Gemini CLI — shipped three command-injection CVEs disclosed in March 2026. The worst, **CVE-2026-31975**, chains a **well-known default JWT secret** with a WebSocket auth handler that never checks whether the user actually exists, into **OS command injection in the shell handler** — giving *unauthenticated* remote code execution against any instance left in its default configuration. Fixed in **1.24.0** (two CVEs) and **1.25.0** (the unauthenticated chain).

## What happened

Three separate advisories were published against the same package on **2026-03-09/10** (NVD 2026-03-11). This is a **backfill** — the CVEs are five months old and already patched, but the package had never been tracked here despite sitting directly in this repo's audience: it is a browser front-end that people run so they can drive Claude Code and other coding agents from a phone or a remote machine, which by design means exposing an agent-with-shell-access over HTTP.

**CVE-2026-31861 — shell command injection in Git routes** ([GHSA-7fv4-fmmc-86g2](https://github.com/advisories/GHSA-7fv4-fmmc-86g2)). The `/api/user/git-config` endpoint interpolates user-supplied `gitName` and `gitEmail` values straight into a command string passed to `child_process.exec()` (`server/routes/user.js`). Because interpolation happens inside double quotes, `$(...)` **command substitution survives** naive filtering of `;`, `&&`, `|`, and backticks. CWE-78. Affected `< 1.24.0`, fixed in **1.24.0**. CVSS v4.0 **8.7 High**.

**CVE-2026-31862 — command injection via multiple parameters** ([GHSA-f2fc-vc88-6w7q](https://github.com/advisories/GHSA-f2fc-vc88-6w7q)). Multiple Git API endpoints pass user-controlled parameters — file paths, branch names, commit messages — into `execAsync()` by string interpolation. The advisory explicitly notes the quote-escaping protection is bypassable with command substitution (`$(command)`, backticks), chaining (`;`, `&&`, `||`), and newlines/control characters. Authenticated attackers get arbitrary OS commands as the Node process user. Affected `<= 1.23.0`, fixed in **1.24.0**. CVSS v3 **9.1 Critical**.

**CVE-2026-31975 — unauthenticated RCE via WebSocket shell injection** ([GHSA-gv8f-wpm2-m5wr](https://github.com/advisories/GHSA-gv8f-wpm2-m5wr)). Three weaknesses compose into a full pre-auth chain:

1. The app uses **a well-known default value** for the JWT signing secret when the environment variable is left unset (CWE-1188) — so an attacker can forge a valid token.
2. WebSocket authentication validates only the **token signature**, never confirming the user exists in the database (CWE-287).
3. The shell handler interpolates unsanitized input directly into bash commands (CWE-78).

Net effect: **arbitrary command execution as the server process user, with no credentials, against any instance running the default configuration.** Affected `<= 1.24.0`, fixed in **1.25.0**. CVSS v4.0 **8.7 High**.

**Why this belongs here.** This is the "wrapper UI around a coding agent" surface, and it's a recurring shape: the agent itself already has shell access by design, so a thin web layer in front of it converts a *local* trust model into a *network* one. The default-JWT-secret failure is the same class as the [Langflow auto-login bypass](2026-08-langflow-cve-2026-9198-autologin-bypass-rce.md) and the [PraisonAI auth-disabled-by-default finding](2026-05-praisonai-auth-bypass.md): an AI/dev tool ships a convenience default that becomes an unauthenticated RCE the moment the instance is reachable. It is also a sibling of this repo's ["localhost is not a security boundary"](2026-06-cline-cve-2026-44211-websocket-rce.md) cluster — except here the tool is *meant* to be exposed, so the exposure isn't the mistake; the missing auth is.

## Am I affected?

```bash
npm ls @siteboon/claude-code-ui 2>/dev/null
# or, if installed globally / run from a clone:
grep -rn '"@siteboon/claude-code-ui"' --include=package.json . 2>/dev/null
```

You are affected if you run **any version at or below 1.24.0** (below 1.25.0 for the unauthenticated chain). Treat it as **actively exploitable** if all of the following are true:

- The instance is reachable from anything other than loopback (a tunnel, reverse proxy, LAN bind, or cloud VM all count), **and**
- You never explicitly set a strong JWT secret via the environment variable — check your `.env` / process environment for an unset or default-looking JWT secret value.

```bash
# Is it listening beyond loopback?
ss -tlnp 2>/dev/null | grep -i node
```

## If you are affected

1. **Upgrade to ≥ 1.25.0 immediately** — 1.24.0 fixes only the two authenticated injections, not the pre-auth chain.
2. **Set a strong, random JWT secret** explicitly. Do not rely on the default under any version.
3. Take the instance off the public internet until both of the above are done — put it behind a VPN or an authenticating reverse proxy rather than exposing it directly.
4. If the instance was internet-reachable on a vulnerable version, **assume compromise**: the shell handler runs as the server process user, which on a typical deployment is the same user whose credentials the coding agent uses. Rotate everything that user could reach — cloud keys, `~/.npmrc` tokens, SSH keys, `GITHUB_TOKEN`, and the AI-provider API keys the wrapped agents authenticate with.
5. See [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) and [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- **Never expose an agent wrapper UI directly.** The thing behind it has a shell. Front it with a VPN or an authenticating proxy, and bind to loopback otherwise.
- **Treat a default secret as no secret.** Any tool that "works out of the box" with authentication enabled is shipping a shared credential to every one of its users; grep your deployments for unset auth-related environment variables.
- See [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) and [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

- [GHSA-gv8f-wpm2-m5wr (CVE-2026-31975) — GitHub Advisory Database](https://github.com/advisories/GHSA-gv8f-wpm2-m5wr) — the unauthenticated RCE chain: default JWT secret, WebSocket auth not validating user existence, shell-handler command injection; affected `<= 1.24.0`, fixed 1.25.0, CVSS v4 8.7.
- [GHSA-f2fc-vc88-6w7q (CVE-2026-31862) — GitHub Advisory Database](https://github.com/advisories/GHSA-f2fc-vc88-6w7q) — multi-parameter command injection via `execAsync()` across Git endpoints; affected `<= 1.23.0`, fixed 1.24.0, CVSS v3 9.1.
- [GHSA-7fv4-fmmc-86g2 (CVE-2026-31861) — GitHub Advisory Database](https://github.com/advisories/GHSA-7fv4-fmmc-86g2) — `/api/user/git-config` shell injection via `gitName`/`gitEmail` into `exec()`.
- [CVE-2026-31861 — GitLab Advisory Database](https://advisories.gitlab.com/pkg/npm/@siteboon/claude-code-ui/CVE-2026-31861/) — independent advisory-database record corroborating affected/patched version ranges.
