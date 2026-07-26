---
id: 2026-07-sharedroot-claude-cowork-macos-vm-escape
title: "SharedRoot — Claude Cowork's local macOS VM shares the host filesystem read-write with guest-root (CVE-2026-46331, Jul 2026)"
date_disclosed: 2026-07-23
last_updated: 2026-07-26
severity: high
status: active
ecosystems: [claude-cowork, ai-desktop-app, macos]
tools_affected: [Claude Cowork (local execution mode, macOS)]
tags: [sandbox-escape, vm-escape, macos, kernel-cve, wont-fix, connector-chaining]
---

## TL;DR

Security researcher Oren Yomtov (Accomplish AI) disclosed **SharedRoot**: a chain that lets code running inside Claude Cowork's local Linux VM sandbox on macOS escape to **read-write access on the host Mac's entire filesystem** — SSH keys, cloud credentials, and user files included — via a real Linux kernel privilege-escalation bug (**CVE-2026-46331**). Anthropic closed the report as "Informative" without a fix; the practical mitigation is that current Cowork defaults to cloud execution, which sidesteps the local escape path entirely. Anyone still running local Cowork sessions on macOS is exposed.

## What happened

Claude Cowork's local execution mode runs the agent inside a Linux VM (via Apple's Virtualization framework) for isolation. To let the agent read and write files in the connected folder, Cowork mounts the **entire host root filesystem (`/`)** into the VM via `virtiofs` at `/mnt/.virtiofs-root` — intended to be visible only to guest-root inside the VM, not to the unprivileged session user the agent's own code runs as.

Yomtov's exploit chain gets from unprivileged code inside the VM to guest-root, then to the host filesystem, in four steps:

1. **Namespace escalation** — the unprivileged session user calls `unshare` to create a new user namespace, becoming "root" inside it with a full capability set, including `CAP_NET_ADMIN`.
2. **Kernel module trigger** — with `CAP_NET_ADMIN`, the attacker configures a traffic-control action using the `act_pedit` kernel module over a netlink socket, forcing it to autoload.
3. **Memory corruption via CVE-2026-46331 ("pedit COW")** — a partial copy-on-write flaw in `act_pedit`: `tcf_pedit_act()` computes the COW range for `skb_ensure_writable()` once, before its key loop, without accounting for runtime header offsets, leaving part of the write region unprotected. This lets the attacker poison the page cache of a file they should only be able to read — targeting a root-owned helper binary. CVE-2026-46331 is a real Linux kernel CVE (CVSS 7.8 per the kernel.org CNA), affecting kernel branches from 4.19.244 through 7.0.x, published 2026-06-16.
4. **Privilege escalation to guest-root** — Cowork's root-owned `coworkd` daemon re-execs the now-corrupted helper binary. Because `coworkd` is already root and `NoNewPrivs` does not block privilege gain across an exec of a setuid/root-owned binary, the session user's code ends up running as guest-root inside the VM — with full read-write access to `/mnt/.virtiofs-root`, i.e., the entire host Mac filesystem.

Yomtov described the practical trigger as trivial: connecting a folder to a fresh Cowork session and sending "one short message" was enough to demonstrate the escape. Accomplish AI estimates roughly **500,000 macOS users** were running local Cowork sessions exposed to this chain before mitigation.

Anthropic's response, per the researcher's writeup, was to close the report as **"Informative"** rather than issue a dedicated fix, framing further hardening as "defense-in-depth" rather than a required patch. The de facto mitigation is that the current version of Cowork **defaults to cloud execution**, which does not use this local VM/virtiofs architecture — but any user still on local execution mode remains exposed, since Anthropic did not patch the underlying mount design or the exploit path itself.

## Am I affected?

You're potentially affected if you run **Claude Cowork on macOS in local execution mode** (as opposed to the newer cloud-execution default):

```bash
# Check whether Cowork is configured for local vs. cloud execution
# (consult Cowork's own settings/preferences UI — no single file check applies across versions)

# Look for the virtiofs mount characteristic of local-mode sessions
mount | grep -i virtiofs
ls -la /mnt/.virtiofs-root 2>/dev/null
```

If you cannot confirm you're on cloud execution mode, treat local Cowork sessions as exposed until you verify your version and settings directly with Anthropic's current documentation.

## If you are affected

1. Switch Claude Cowork to **cloud execution mode** if a local-mode option is still presented — this is the only mitigation Anthropic has shipped for this class of issue.
2. Avoid connecting folders containing SSH keys, cloud credential files, or other sensitive material to a local-mode Cowork session until you've confirmed you're on cloud execution.
3. If you ran local-mode sessions on untrusted or agent-directed content (e.g., a prompt injection could trigger the same VM/shell access an unprivileged escape would rely on), treat the host as potentially exposed and review for unexpected file modifications outside the connected folder.

→ [Playbook: if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention

- Prefer cloud execution mode for Claude Cowork where available — it does not share the host filesystem into a VM the agent's own code can escalate within.
- Treat "runs in a local VM sandbox" as a mitigation for *accidental* mistakes, not a security boundary against a determined escape chain — the VM's value depends entirely on what it shares back to the host and how.
- Don't grant a local sandboxed agent access to folders containing credentials, SSH keys, or other high-value secrets, regardless of vendor sandboxing claims.

→ [Prevention: agent sandboxing](../prevention/agent-sandboxing.md)

## IOCs

This is a design/architecture flaw exploited locally, not a remote campaign — there are no network IOCs. Relevant artifacts for detection/audit:

| Type | Value |
|---|---|
| CVE (underlying kernel bug) | CVE-2026-46331 ("pedit COW", Linux `act_pedit` traffic-control subsystem) |
| Affected kernel branches | 4.19.244 through 7.0.x (multiple stable branches, incl. 5.4, 5.10, 5.15, 5.17, 6.13+) |
| Host mount point (local Cowork VM) | `/mnt/.virtiofs-root` |
| Vulnerable daemon | `coworkd` (runs as root inside the Cowork Linux VM) |
| Vendor status | Anthropic closed the report as "Informative"; no dedicated patch for the escape chain — mitigation is the shift to cloud-execution-by-default |

## Technique note

This is a sibling of the "localhost is not a security boundary" and connector-chaining lethal-trifecta classes this repo already tracks (OpenClaw CVE-2026-25253, OpenCode CVE-2026-22812 and CVE-2026-22813, and Claude Cowork's own earlier Windows/Hyper-V escape, [tracked separately](2026-07-claude-cowork-sandbox-escape.md)) — except here the trust boundary is a VM/virtiofs mount rather than a network port, and the vendor's response ("Informative," no fix) is another documented case of a major AI vendor declining to treat a local-sandbox escape as in-scope, consistent with the pattern already noted for Claude Desktop Extensions and the account-wide personalization-sync RCE.

## Sources

- [Accomplish AI — SharedRoot: Escaping the Claude Cowork sandbox](https://www.accomplish.ai/blog/sharedroot-escaping-claude-cowork-sandbox/) — primary disclosure; full exploit chain, root cause, researcher quote, Anthropic's "Informative" response, mitigation status.
- [The Hacker News — Claude Cowork Flaw Could Let AI Agent Escape Its VM and Access Mac Files](https://thehackernews.com/2026/07/claude-cowork-flaw-could-let-ai-agent.html) — independent corroboration; ~500,000 affected macOS users, CVE-2026-46331 details, disclosure date.
- [NVD — CVE-2026-46331](https://nvd.nist.gov/vuln/detail/CVE-2026-46331) — canonical kernel CVE record: CVSS score, affected version ranges, publish date (2026-06-16).
