---
id: 2026-03-openhands-git-diff-rce
title: "OpenHands git-diff command injection — CVE-2026-33718 (March 2026)"
date_disclosed: 2026-03-27
last_updated: 2026-05-20
severity: high
status: patched
ecosystems: [pypi, ai-agents]
tools_affected: [openhands]
tags: [cve, command-injection, ai-agent-framework, agent-sandbox, authenticated]
---

## TL;DR
**CVE-2026-33718** — a command-injection flaw in **OpenHands** (the open-source coding agent, formerly OpenDevin). The `get_git_diff()` handler (`openhands/runtime/utils/git_handler.py:134`) interpolates the `path`/`file_path` parameter from `GET /api/conversations/{id}/git/diff` straight into a shell command string via Python `.format()` with `shell=True`, so an attacker who can reach that authenticated endpoint can inject shell metacharacters (`;`, `|`, `$()`, backticks) and **run arbitrary commands inside the agent sandbox**. CVSS v3.1 `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L` (HIGH). Authenticated-only, but matters because exposed/no-auth OpenHands instances are common. Fixed in **1.5.0** ([PR #13051](https://github.com/OpenHands/OpenHands/pull/13051)).

## What happened
GitHub advisory **GHSA-7h8w-hj9j-8rjw** (published **2026-03-27**) describes the bug: the `file_path` argument supplied to the git-diff API endpoint is directly interpolated into a shell command string and executed with `shell=True`. No sanitization is applied, so characters like `"`, `;`, and `#` are interpreted by the shell, enabling command chaining. An authenticated user can craft a request whose `path` carries an injected command, which then executes in the context of the agent's sandbox runtime.

The fix ([PR #13051](https://github.com/OpenHands/OpenHands/pull/13051)) replaces direct shell-string formatting with proper argument handling / path sanitization. All versions **before 1.5.0** are vulnerable.

The attack requires authentication (`PR:L`), so it's lower-urgency than the unauthenticated [Langflow RCE](2026-03-langflow-rce.md) or [PraisonAI auth bypass](2026-05-praisonai-auth-bypass.md) — *unless* the instance is exposed with weak or no auth, which recent scans show is endemic across AI agent platforms. It belongs to the same recurring class: **AI-agent frameworks shelling out with unsanitized, attacker-influenceable input.**

## Am I affected?

```bash
# Check installed OpenHands version (need >= 1.5.0)
pip show openhands 2>/dev/null | grep -E '^(Name|Version):'

# Is the API exposed beyond localhost?
ss -tlnp 2>/dev/null | grep -E ':3000|:3306|:8000'
ps eww | grep -i '[o]penhands'
```

You are affected if you run OpenHands **< 1.5.0** and the API is reachable by anyone you don't fully trust (multi-user, shared, or internet-exposed deployments especially).

### IOCs / fix

| Type | Value |
|---|---|
| CVE | `CVE-2026-33718` |
| GHSA | `GHSA-7h8w-hj9j-8rjw` |
| Weakness | CWE-78 (OS command injection) |
| Vulnerable code | `get_git_diff()` — `openhands/runtime/utils/git_handler.py:134` |
| Vulnerable endpoint | `GET /api/conversations/{conversation_id}/git/diff` (`path` param) |
| CVSS | v3.1 `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L` (HIGH) |
| Affected versions | all before 1.5.0 |
| Fixed version | 1.5.0 ([PR #13051](https://github.com/OpenHands/OpenHands/pull/13051)) |

## If you are affected
1. Upgrade OpenHands to **1.5.0+**.
2. If the API was exposed, treat the sandbox host as compromised: rotate any credentials the agent's tools could reach (cloud, GitHub, DB) and review for unexpected processes/outbound connections.
3. Put authentication in front of the API and bind it to `127.0.0.1` / a tunnel, not `0.0.0.0`.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Never expose an AI-agent dev server to the public internet without auth. Default-bind to localhost and front with an authenticated reverse proxy or tunnel.

## Sources
- [GitHub Advisory — GHSA-7h8w-hj9j-8rjw: Command Injection in Git Diff Handler (OpenHands)](https://github.com/OpenHands/OpenHands/security/advisories/GHSA-7h8w-hj9j-8rjw)
- [GitLab Advisory Database — CVE-2026-33718: OpenHands is Vulnerable to Command Injection through its Git Diff Handler](https://advisories.gitlab.com/pkg/pypi/openhands/CVE-2026-33718/)
- [SentinelOne — CVE-2026-33718: OpenHands Command Injection Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-33718/)
- [OpenHands — PR #13051: sanitize file_path in git diff shell commands to prevent command injection](https://github.com/OpenHands/OpenHands/pull/13051)
- [NVD — CVE-2026-33718](https://nvd.nist.gov/vuln/detail/CVE-2026-33718)
