---
id: 2026-09-deepseek-harness-host-header-sandbox-escape
title: "DeepSeek Harness — Host-header-only trust on the local API let a sandboxed agent disable its own sandbox (CVE-2026-82533, CVSS 9.4)"
date_disclosed: 2026-09-08
last_updated: 2026-09-10
severity: critical
status: patched
ecosystems: [deepseek-harness, npm, ai-coding-agent, localhost-api]
tools_affected: [deepseek-harness, dsh, any-agent-harness-with-a-loopback-control-api]
tags: [cve, sandbox-escape, auth-bypass, host-header, localhost-not-a-boundary, prompt-injection, agent-harness, cwe-807]
---

## TL;DR

**DeepSeek Harness** (`dsh`) — DeepSeek's open-source, local-first harness for running AI coding agents, which passed 216,000 GitHub stars within weeks of its August 2026 release — shipped a local HTTP control-plane API whose only "is this request trusted?" check was the value of the HTTP `Host` header. Because the OS sandbox allowed loopback networking while restricting file writes, a sandboxed agent (or any content that could steer it) needed **one shell command** against that API to flip its own session to `danger-full-access` mode, disabling its file-system confinement and approval prompts. **CVE-2026-82533**, CVSS 4.0 **9.4** / CVSS 3.1 **9.6**, CWE-807. Affects **< 0.1.2-alpha.1**; fixed on GitHub 2026-08-27 and on npm from **0.1.2-alpha.2** (2026-08-30). If you installed `dsh` in its first two weeks, upgrade.

## What happened

OX Security researchers Nir Zadok and Moshe Siman Tov Bustan found that the harness's browser UI is backed by a local HTTP API, and that the function deciding whether an API request is trusted (`isTrustedApiRequest`) compared only the client-supplied `Host` header against expected values — it never looked at where the TCP connection actually came from. Any process that could reach the loopback interface and set a header could therefore call privileged endpoints: change the execution policy, run commands, and read stored conversations, with no API key, no model call, and no user approval.

That matters because of how the sandbox was scoped. DeepSeek's own safety documentation said file *reads* and *network* access were not confined — only writes were — so loopback traffic from inside the sandbox was permitted by design. The confined agent could reach the control plane that governs its own confinement. OX's proof of concept was a single shell command issued from the sandboxed session that elevated it to `danger-full-access`; the trigger could equally be an attacker-controlled text prompt (a README, an issue, a web page) that induces the agent to run that command, which is the same prompt-injection-to-sandbox-escape shape this repo tracks for [Cursor DuneSlide](2026-06-cursor-duneslide-zeroclick-rce.md) and the ["localhost is not a security boundary" cluster](2026-06-autojack-autogen-studio-mcp-rce.md).

VulnCheck, acting as CNA, additionally notes the remote angle: **when the harness is exposed beyond the local machine**, an unauthenticated remote attacker gets the same control — command execution plus download of stored conversation logs — because the check was header-based rather than connection-based. The Hacker News reports two developers had independently raised the same issue on the project's discussion board on 2026-08-13 and 2026-08-14, before OX's formal report, and that the project published no security advisory of its own; the CVE record is VulnCheck's.

**Timeline** (per OX and VulnCheck): reported to VulnCheck as CNA **2026-08-24** → fix released **2026-08-27** (`dsh-v0.1.2-alpha.1`, GitHub only) → remediation verified **2026-08-30** (the same day 0.1.2-alpha.2 became the first npm release) → CVE published **2026-09-08**. The current npm release at time of writing is 0.1.2-rc.1 (2026-09-03). The fix replaces the header check with one-time token authentication: the browser exchanges a token for signed cookies, and every interface request must carry them.

## Am I affected?

You are affected if you ran any DeepSeek Harness build **before 0.1.2-alpha.1** (GitHub) / **0.1.2-alpha.2** (npm) — i.e. anything installed between the August 2026 launch and 2026-08-30 that hasn't been upgraded since.

```bash
# Which version is installed? (check both global npm and any git checkout)
npm ls -g 2>/dev/null | grep -i deepseek
dsh --version 2>/dev/null
git -C ~/deepseek-harness describe --tags 2>/dev/null   # if you run from source

# Was the local API ever reachable off-box? Anything bound to 0.0.0.0 or a LAN IP is the remote case.
ss -tlnp 2>/dev/null | grep -v '127.0.0.1\|::1'
```

The affected version range is stated by NVD/VulnCheck as **< 0.1.2-alpha.1**; OX describes it as "0.1.1-rc.2 and earlier." Those are the same range. If a previously-sandboxed session in that window ran anything you didn't author — a repo's setup instructions, a fetched page, a third-party skill — treat the sandbox as having been optional during that session and review what it touched.

## If you are affected

1. Upgrade to **0.1.2-rc.1** or later (`npm install -g` the current release, or pull the tagged fix).
2. If the harness was reachable from another host, or ran untrusted content while vulnerable, follow [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — the conversation-download endpoint means stored sessions (and any secrets pasted into them) should be treated as exposed.
3. Rotate anything the agent's working directory or environment held: [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — the sandbox has to confine the *control plane* too. A harness whose "unconfined mode" switch lives on a loopback API the confined process can reach has no sandbox, regardless of how tight the file-system rules are.
- Treat `Host` as attacker-controlled input everywhere. This is the third Host-header trust failure this repo has tracked in a few months, after [Starlette BadHost](2026-05-starlette-badhost-host-header-bypass.md) and the Ray `User-Agent`-prefix check ([CVE-2025-62593](2026-08-ray-cve-2025-62593-kev.md)): a request header is a string the client chose, never evidence of who sent it.
- "Loopback only" is a *reachability* statement, not an *authentication* one. Anything that runs on the machine — the sandboxed agent, a browser tab via DNS rebinding, another local process — can talk to 127.0.0.1.
- Keep fast-moving agent harnesses on `latest`. This project went from launch to 216K stars to a CVSS 9.4 fix in under a month, and the first two reports of the bug sat on a discussion board with no advisory; release notes are not where you'll learn about the next one.

## Sources

- [OX Security — CVE-2026-82533: DeepSeek Harness Vulnerability Lets AI Agents Escape Their Own Sandbox](https://www.ox.security/blog/cve-2026-82533-deepseek-harness-ai-agent-sandbox-escape/) — fetched 2026-09-10; primary researcher write-up: `isTrustedApiRequest` mechanism, sandbox scope, single-command PoC description, disclosure timeline, researcher credits.
- [VulnCheck — DeepSeek Harness < 0.1.2-alpha.1 Authentication Bypass via Host Header Spoofing](https://www.vulncheck.com/advisories/deepseek-harness-alpha-1-authentication-bypass-via-host-header-spoofing) — fetched 2026-09-10; CNA advisory: CVSS 4.0 9.4 vector, CWE-807, affected/fixed versions, the remote-exposure case, links to the patch commit and release tag.
- [NVD — CVE-2026-82533](https://nvd.nist.gov/vuln/detail/CVE-2026-82533) — fetched via the NVD API 2026-09-10; confirms publication 2026-09-08, CVSS 3.1 9.6 alongside the 4.0 score, and the VulnCheck/GitHub references.
- [The Hacker News — DeepSeek Harness Flaw Let AI Agents Disable Their Own File Sandbox Without Approval](https://thehackernews.com/2026/09/deepseek-harness-flaw-let-ai-agents.html) — fetched 2026-09-10; adds the star count, the npm release sequence (0.1.2-alpha.2 on 2026-08-30, 0.1.2-rc.1 on 2026-09-03), the earlier discussion-board reports, and the token/signed-cookie fix design.
