---
id: 2026-09-docker-sandboxes-virtiofs-symlink-host-escape
title: "Docker Sandboxes — the microVM that runs your coding agent could read and modify arbitrary macOS host files through a virtio-fs symlink race (CVE-2026-77179, CVSS 9.4) and reach any host Unix socket (CVE-2026-79994, 8.7); fixed in 0.42.0 alongside a D-Bus host-command bug and a cross-sandbox OAuth hijack"
date_disclosed: 2026-09-15
last_updated: 2026-09-18
severity: critical
status: patched
ecosystems: [docker, macos, claude-code, codex, cursor, github-copilot, gemini-cli, agent-sandboxing]
tools_affected: ["Docker Sandboxes 0.28.0 – 0.41.9 on macOS (CVE-2026-77179)", "Docker Sandboxes 0.37.0 – 0.41.9 (CVE-2026-79994)", "every agent it hosts: Claude Code, Codex, Copilot, Cursor, Devin, Docker Agent, Droid, Gemini, Kiro, OpenCode"]
tags: [cve, sandbox-escape, symlink, toctou, virtio-fs, microvm, agent-sandboxing, macos, vendor-cna]
---

## TL;DR
**Docker Sandboxes** is Docker's product for running AI coding agents (Claude Code, Codex, Copilot, Cursor, Devin, Gemini, Kiro, OpenCode and others) in per-agent microVMs with the project directory shared in — the isolation layer a lot of readers adopted after the run-of-agent escape bugs tracked here. Docker's docs promised "Symlinks pointing outside the workspace scope are not followed." Two advisories published 2026-09-15 show they were. **CVE-2026-77179** (CVSS 4.0 **9.4**, Critical, CWE-59; Oren Yomtov, accomplish.ai): on macOS the **virtio-fs host server** followed symlinks when reopening an unlinked file from a stored path, so a malicious guest process could replace a parent directory with a symlink and "read or modify arbitrary host files as the VMM user, potentially achieving host code execution." **CVE-2026-79994** (**8.7**, High, CWE-367; Jurre van Bergen, ThreatNotify): the guest-to-host Unix-socket relay validated a socket path and later reconnected by pathname, so a symlink swap between check and use made "the host connect to an arbitrary AF_UNIX socket outside the shared workspace." Both fixed in **0.42.0 (2026-09-07)**, whose release notes also close a bug where "a sandboxed process could get the daemon to open a host D-Bus transport and execute an arbitrary command on the host" and one where "a malicious sandbox could hijack another sandbox's OAuth login." The "malicious guest" is whatever your agent runs — a poisoned dependency, a prompt-injected agent, a test suite from an untrusted repo. Upgrade; until then prefer clone mode over read-write mounts.

## What happened

**What the product is.** Docker's docs: "Docker Sandboxes run AI coding agents in isolated microVM sandboxes. Each sandbox gets its own Docker daemon, filesystem, and network." Workspaces are mounted three ways — mountless, **direct read-write mount**, or **clone mode** (host repo mounted read-only at `/run/sandbox/source`, agent works on a private clone). API credentials stay on the host and are injected by a proxy. The product's supported-agents page lists **Claude Code, Codex, Copilot, Cursor, Devin, Docker Agent, Droid, Gemini, Kiro, OpenCode** and a bare shell. It is, in other words, the sandbox this repo's [agent-sandboxing guidance](../prevention/agent-sandboxing.md) tells people to put beneath their agent.

**CVE-2026-77179 — virtio-fs symlink follow (macOS).** NVD (CNA Docker): "On macOS, the virtio-fs host server used by Docker Sandboxes improperly follows symlinks when reopening an unlinked file from a stored path. A malicious guest can replace a parent directory with a symlink, escape the shared workspace, and read or modify arbitrary host files as the VMM user, potentially achieving host code execution." The VMM runs as the developer, so "arbitrary host files as the VMM user" is the developer's home directory: `~/.ssh`, `~/.aws`, `~/.claude.json`, shell profiles — write access to any of which is host code execution on next login. CVSS 4.0 vector AV:L/AC:L/AT:N/PR:N/UI:N with high impact on the *subsequent* system (SC:H/SI:H/SA:H) — the "local" is the guest, which is exactly where untrusted code runs. Affected **0.28.0 ≤ v < 0.42.0** on macOS; Docker's own docs had said since March that outside-workspace symlinks are not followed.

**CVE-2026-79994 — socket-relay TOCTOU.** "The guest-to-host Unix-domain socket relay in Docker Sandboxes validates that a socket path is inside an authorized workspace, but later reconnects using the pathname. A malicious guest can replace an intermediate directory with a symlink between validation and connection, causing the host to connect to an arbitrary AF_UNIX socket outside the shared workspace. This can expose data or host-side capabilities provided by the targeted socket." On a developer Mac the interesting sockets are the Docker daemon's, the SSH agent's, and the ones IDEs and password managers listen on. Affected **0.37.0 ≤ v < 0.42.0**, all platforms. Fix references: `docker/sailor` PR 2021 and `docker/sandboxes` PR 5342.

**The two extra fixes in 0.42.0.** The release notes name two more issues without CVEs: a sandboxed process "could get the daemon to open a host D-Bus transport and execute an arbitrary command on the host," and "a malicious sandbox could hijack another sandbox's OAuth login." The second matters for teams running several agents side by side: one poisoned sandbox could take the OAuth session another agent was completing. The same release also adds Devin as a built-in agent and defaults ports to `tcp4`.

**Exploitation.** None reported; Docker's advisories and The Hacker News (2026-09-17) both say no known exploitation. The precondition — attacker code running inside the sandbox — is the normal condition for anyone using the product for what it is for.

**Sources and dating.** The vendor is the CNA; NVD published both CVEs 2026-09-15 and the GitHub Advisory Database mirrors them (GHSA-4x2g-7mfh-8rx6, GHSA-wq46-97v9-q386). The fix shipped 2026-09-07 in `docker/sbx-releases` v0.42.0 (release notes carry the CVE text); public write-ups followed on 2026-09-17 (The Hacker News). Dated here by the advisory publication.

## Am I affected?

```bash
sbx version 2>/dev/null || docker sandbox version 2>/dev/null   # need >= 0.42.0
# macOS: is the host-side VMM process older than the fix? Check the release you installed:
ls -la ~/.docker/sandboxes 2>/dev/null; docker desktop version 2>/dev/null
# Which workspaces were shared read-write (direct mount) rather than clone/mountless?
sbx ls 2>/dev/null
```

If a sandbox ran untrusted code (an unreviewed repo's tests, a dependency install, an agent that read attacker-controlled content) on a vulnerable version, assume the host user's files were readable and possibly modified.

## If you are affected

- Upgrade to **0.42.0 or later** and restart existing sandboxes.
- Audit the host user's dotfiles and startup hooks for changes made during the exposure window (`~/.zshrc`, `~/.bash_profile`, `~/.ssh/authorized_keys`, `~/.claude/settings.json`, `~/.vscode/tasks.json`, LaunchAgents) — [`playbooks/if-your-local-ai-agent-was-exploited.md`](../playbooks/if-your-local-ai-agent-was-exploited.md).
- Rotate credentials that lived on the host as files: [`playbooks/rotating-cloud-credentials.md`](../playbooks/rotating-cloud-credentials.md), [`playbooks/if-your-github-pat-leaked.md`](../playbooks/if-your-github-pat-leaked.md).

## Prevention

- Prefer **clone mode** or mountless workspaces; Docker's own guidance for direct mounts is to "treat sandbox-modified workspace files the same way you would treat a pull request from an untrusted contributor."
- A sandbox is a mitigation, not a boundary; keep secrets off the host user's disk where the VMM runs and lean on the credential proxy. [`prevention/agent-sandboxing.md`](../prevention/agent-sandboxing.md), [`prevention/credential-hygiene.md`](../prevention/credential-hygiene.md).

## Sources
- [NVD — CVE-2026-77179](https://nvd.nist.gov/vuln/detail/CVE-2026-77179) and [NVD — CVE-2026-79994](https://nvd.nist.gov/vuln/detail/CVE-2026-79994) — CNA security@docker.com, published 2026-09-15, CVSS 4.0 9.4 / 8.7, CWE-59 / CWE-367, descriptions quoted above; queried via the NVD API 2026-09-18.
- [docker/sbx-releases — v0.42.0 release notes](https://github.com/docker/sbx-releases/releases/tag/v0.42.0) — the two CVE fixes plus the D-Bus and OAuth-hijack fixes, Devin support, `tcp4` default. Fetched 2026-09-18.
- [GitHub Advisory Database — "docker sandboxes" listing](https://github.com/advisories?query=docker+sandboxes) — GHSA-4x2g-7mfh-8rx6 (Critical) and GHSA-wq46-97v9-q386 (High), both 2026-09-15; also the earlier CVE-2026-18171 / 12539 / 12039 entries. Fetched 2026-09-18.
- [Docker docs — Sandboxes isolation](https://docs.docker.com/ai/sandboxes/security/isolation/) and [supported agents](https://docs.docker.com/ai/sandboxes/agents/) — the symlink promise, the three workspace modes, the credential proxy, the agent list. Fetched 2026-09-18.
- [The Hacker News — Critical Docker Sandboxes Flaw Lets Malicious Guest Code Read and Modify macOS Host Files](https://thehackernews.com/2026/09/critical-docker-sandboxes-flaw-lets.html) — 2026-09-17; the discoverers (Oren Yomtov, accomplish.ai; Jurre van Bergen, ThreatNotify), the 2026-09-07 fix date, no known exploitation. Fetched 2026-09-18.
