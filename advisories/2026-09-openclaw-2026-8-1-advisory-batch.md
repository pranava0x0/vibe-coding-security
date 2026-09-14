---
id: 2026-09-openclaw-2026-8-1-advisory-batch
title: "OpenClaw publishes 75 security advisories in one day (2026-09-11) for bugs fixed in 2026.7.1–2026.8.1 — 30 rated High: non-owner senders reaching owner-only tools, MCP config injection to RCE, exec approvals that outlive their directory, a gcloud argument injection"
date_disclosed: 2026-09-11
last_updated: 2026-09-14
severity: high
status: patched
ecosystems: [ai-agents, npm, mcp]
tools_affected: [openclaw, "@openclaw/whatsapp", "@openclaw/matrix", NemoClaw, ClawHub skills]
tags: [cve-batch, ghsa-batch, authorization-bypass, owner-only-tools, exec-approval, mcp, argument-injection, dns-rebinding, credential-exposure, ai-agent, openclaw]
---

## TL;DR
On **2026-09-11** the OpenClaw project published **75 GitHub Security Advisories in a single day** — 30 High, 40 Moderate, 5 Low — for bugs already fixed in releases between **2026.7.1** and **2026.8.1** (2026.8.1 shipped 2026-08-31). No CVE ids, no blog post, no press coverage; the only record is the project's own advisory index, which also carries a second, previously untracked batch of ~30 advisories dated **2026-06-30** (fixed 2026.6.8). The dominant theme is **authorization that stops at the channel boundary**: a non-owner sender on WhatsApp, Slack, Discord, Matrix, Signal, Teams or a voice call could reach owner-only tools, change MCP server configuration (a stdio command, so code execution on the host), install plugins, re-pair accounts, or reuse an operator's standing exec approval in a directory it was never reviewed for. If you run OpenClaw with any external channel connected, upgrade to **≥ 2026.8.1** and audit what non-owners could have done in the meantime.

## What happened

OpenClaw — the autonomous personal-agent framework this repo already tracks for [Claw Chain](2026-05-openclaw-claw-chain.md) and the [NemoClaw bulletin](2026-08-nvidia-nemoclaw-openshell-cve-batch.md) — discloses almost exclusively through its own GitHub Security Advisories tab. This sweep walked that index directly (eleven pages, per this repo's standing vendor-index practice) and found that **every one of the first 75 advisories carries the same publication date, 2026-09-11**, while their patched versions are 2026.7.1 or 2026.8.1 — so the fixes were live for two to ten weeks before the advisories existed. That is the "advisory-database date is not a disclosure date" pattern, inverted: here the *vendor* back-published, and a sweep sorting by date sees 75 "new" bugs that are all already fixed.

**Sampled advisories** (all fetched directly from the vendor's advisory pages; CVSS as stated by the project; no CVE assigned to any of them):

| Advisory | Title | CVSS | Affected | Fixed |
|---|---|---|---|---|
| [GHSA-wwx7-573h-pqwc](https://github.com/openclaw/openclaw/security/advisories/GHSA-wwx7-573h-pqwc) | MCP configuration changes could omit owner authorization | **8.8** | `openclaw` < 2026.7.1 | 2026.7.1 |
| [GHSA-7cp7-87pj-p32v](https://github.com/openclaw/openclaw/security/advisories/GHSA-7cp7-87pj-p32v) | Skill tool dispatch could skip owner-only policy | **8.3** | `openclaw` < 2026.8.1 | 2026.8.1 |
| [GHSA-9m4p-cqp4-jppq](https://github.com/openclaw/openclaw/security/advisories/GHSA-9m4p-cqp4-jppq) | WhatsApp login tool could reach non-owner turns | **8.1** | `@openclaw/whatsapp` < 2026.8.1 | 2026.8.1 |
| [GHSA-5mrc-77hj-xjxv](https://github.com/openclaw/openclaw/security/advisories/GHSA-5mrc-77hj-xjxv) | Workspace Cloud SDK arguments could execute code during Gmail setup | 7.8 | `openclaw` 2026.3.28 – 2026.8.0 | 2026.8.1 |
| [GHSA-crg9-c62w-j2p5](https://github.com/openclaw/openclaw/security/advisories/GHSA-crg9-c62w-j2p5) | OpenShell filesystem mutations could race path validation | 7.8 | `openclaw` < 2026.7.1 | 2026.7.1 |
| [GHSA-qgj5-6x35-9g6f](https://github.com/openclaw/openclaw/security/advisories/GHSA-qgj5-6x35-9g6f) | Config revision hashes could expose password verifiers | 7.5 | `openclaw` < 2026.8.1 | 2026.8.1 |
| [GHSA-62qm-6fjj-6g23](https://github.com/openclaw/openclaw/security/advisories/GHSA-62qm-6fjj-6g23) | Dreaming could widen restricted sender authority | 7.5 | `openclaw` ≥ 2026.4.5, < 2026.8.1 | 2026.8.1 |
| [GHSA-hgv5-f2r3-6v9r](https://github.com/openclaw/openclaw/security/advisories/GHSA-hgv5-f2r3-6v9r) | Matrix authorization could conflate case-distinct user IDs | 7.5 | `@openclaw/matrix` ≥ 2026.2.2, < 2026.8.1 | 2026.8.1 |
| [GHSA-3mq7-q27j-mq7q](https://github.com/openclaw/openclaw/security/advisories/GHSA-3mq7-q27j-mq7q) | Exec approvals could outlive their reviewed working directory | 7.3 | `openclaw` < 2026.8.1 | 2026.8.1 |

What the sampled ones actually let an attacker do:

- **MCP config injection → host code execution (8.8).** An *authorized non-owner* sender on an external channel could run `/mcp set` / `/mcp unset` and persist Gateway MCP server configuration. A stdio MCP server entry is a command line, so this is arbitrary command execution with the OpenClaw process's privileges (CWE-862 + CWE-78). The project's interim advice is to disable MCP chat commands in external channels and **audit existing MCP server entries for anything you did not add**.
- **Owner-only tools reachable by non-owners (8.3, 8.1, and roughly twenty Moderate/High siblings).** Skill-backed tool dispatch did not carry the sender's owner status, so non-owners could reach owner-restricted tools "depending on which owner-only tools were exposed by installed skills." The WhatsApp login tool was exposed through the generic channel-tool path: a non-owner could force a re-login, obtain the QR code, and disconnect or replace the account. The same shape recurs across the batch — `chat.send` exposing owner-only infrastructure tools, `message.action` trusting spoofed requester provenance, Claude permission replies and Codex bind/install omitting owner authorization, Slack group DMs skipping sender allowlists, inbound voice calls inheriting owner tool authority, Discord realtime transcripts inheriting another speaker's owner status.
- **Standing exec approvals that drift (7.3, plus three sibling Highs).** An `allow-always` approval matched a command's arguments but not its working directory, so a later run could execute the approved command somewhere with "materially different read or write effects." Sibling advisories: reusable approvals authorizing *changed* arguments, escaped newlines confusing allowlist parsing, and exec-wrapper allowlists trusting arbitrary inner commands.
- **Argument injection into `gcloud` (7.8).** An untrusted workspace configuration could set `CLOUDSDK_PYTHON_ARGS`, which Gmail setup inherited when launching `gcloud`, so the trusted Python interpreter executed attacker-supplied code as the host user. This is the same "config file you did not write becomes an environment variable that becomes code" class as [aider's `.aider.conf.yml`](2026-09-aider-conf-yml-command-execution.md) and [GitSpawn](2026-09-gitspawn-git-config-agent-rce-cluster.md).
- **Offline password cracking from a redacted config (7.5).** Redacted configuration responses kept deterministic hashes computed from the *unredacted* values; with a low-entropy Gateway password those hashes are an offline verifier that bypasses the Gateway's rate limiting. Use a high-entropy Gateway credential or secret references.
- **Memory "dreaming" as a privilege-escalation channel (7.5).** Session-derived memory captured from a restricted sender lost that sender's restrictions before a later background dreaming run processed it — so a low-privilege sender could plant instructions that a background agent later executed with broader tool access. This is stored prompt injection through the agent's own memory layer.
- **Case-folded identities (7.5).** `@openclaw/matrix` lowercased whole user IDs including the case-sensitive server-name portion, so two protocol-valid Matrix accounts could normalise to the same authorization identity and inherit each other's allowlist, owner-command, exec-approval and plugin-approval rights.
- **OpenShell sandbox TOCTOU (7.8).** `remove`/`mkdir`/`rename` could act on a different filesystem target after the sandbox path-safety check completed.

**Other High-rated titles in the batch** (listed from the index; not individually fetched): iOS Control UI not enforcing saved Gateway TLS pins; Codex native tools ignoring per-chat policy; Synology file delivery losing DNS pinning; Gateway upgrade-like requests retaining unauthenticated sockets; browser CDP connections discarding DNS pinning; the agent cron tool reaching operator command jobs; cron accepting mixed-case command payloads; browser proxy missing its admin scope; browser node targets bypassing sandbox host control; Signal reactions binding to the wrong approval; Google Meet node commands skipping exec approvals.

**The June batch nobody logged either.** Pages 8–11 of the same index carry roughly thirty more advisories dated **2026-06-30** (one sampled: [GHSA-jhfx-v2j8-x3m6](https://github.com/openclaw/openclaw/security/advisories/GHSA-jhfx-v2j8-x3m6), OpenAI-compatible HTTP model overrides missing admin authorization, CVSS 7.6, fixed **2026.6.8**) and three dated 2026-05-28, with titles including host-exec environment filtering missing interpreter and rustup startup variables, sandbox bind mounts bypassing parent-directory denylists, MCP loopback exposing owner-only tools to non-owner runs, plugin install commands allowing non-owner persistence, and MCP SSE redirects forwarding `Authorization` headers. None of these appear elsewhere in this repo. Treat **< 2026.8.1** as affected by both batches.

**What the release notes said.** The [2026.8.1 release](https://github.com/openclaw/openclaw/releases/tag/v2026.8.1) (2026-08-31) describes masked credential prompts, plugin-trust review, provenance warnings for arbitrary plugin sources, and protected-credential egress — hardening, not a list of fixed vulnerabilities. A reader following release notes alone had no way to know 75 advisories were coming.

## Am I affected?

```bash
# Core version — need >= 2026.8.1 (2026.7.1 closes only part of the batch)
openclaw --version 2>/dev/null || npm ls -g openclaw 2>/dev/null

# Channel plugins carry their own advisories
npm ls -g @openclaw/whatsapp @openclaw/matrix 2>/dev/null

# Anything below the fix line, with an external channel connected, is in scope:
#   - review MCP server entries you did not add (GHSA-wwx7-573h-pqwc)
#   - review standing exec approvals and plugin installs made by non-owner senders
#   - check whether Gmail setup ran from an untrusted workspace (GHSA-5mrc-77hj-xjxv)
```

You are affected if you ran any release before **2026.8.1** with at least one external channel (WhatsApp, Slack, Discord, Matrix, Signal, Teams, Feishu, LINE, QQBot, Telegram, voice) that non-owners could message, or with skills that expose owner-only tools, or with session-memory capture plus dreaming enabled for restricted senders. A single-user OpenClaw on loopback with no external channels is exposed mainly to the workspace-config and sandbox items.

## If you are affected

1. Upgrade `openclaw` and every `@openclaw/*` channel package to **≥ 2026.8.1** (current is 2026.9.4).
2. Audit Gateway MCP server configuration, plugin list, cron jobs, and standing exec approvals; remove anything you cannot account for. An MCP stdio entry you did not add is a confirmed compromise signal.
3. Rotate the Gateway password (use a high-entropy value or a secret reference) and any provider keys the Gateway held — the config-hash and embedding-fallback advisories both leak credential material.
4. Re-pair WhatsApp/Matrix/Signal accounts if a non-owner could have triggered a login.
5. → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
6. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md) — the OpenShell race and bind-mount items show the sandbox itself needs the update, not just the agent.
- [MCP hygiene](../prevention/mcp-hygiene.md) — MCP configuration is a command line; nobody but the operator should be able to write it.
- [Credential hygiene](../prevention/credential-hygiene.md)
- Keep OpenClaw on the latest release and stop reading release notes as a security changelog: this project ships fixes first and advisories weeks later, in bulk. Check `github.com/openclaw/openclaw/security/advisories` directly.

## Sources
- [OpenClaw — Security Advisories index](https://github.com/openclaw/openclaw/security/advisories) — walked directly 2026-09-14, pages 1–11: 75 advisories dated 2026-09-11 (30 High / 40 Moderate / 5 Low by the index's own labels), ~30 dated 2026-06-30, three dated 2026-05-28; page 12 and beyond not walked.
- Individual vendor advisory pages, fetched 2026-09-14: [GHSA-wwx7-573h-pqwc](https://github.com/openclaw/openclaw/security/advisories/GHSA-wwx7-573h-pqwc), [GHSA-7cp7-87pj-p32v](https://github.com/openclaw/openclaw/security/advisories/GHSA-7cp7-87pj-p32v), [GHSA-9m4p-cqp4-jppq](https://github.com/openclaw/openclaw/security/advisories/GHSA-9m4p-cqp4-jppq), [GHSA-5mrc-77hj-xjxv](https://github.com/openclaw/openclaw/security/advisories/GHSA-5mrc-77hj-xjxv), [GHSA-crg9-c62w-j2p5](https://github.com/openclaw/openclaw/security/advisories/GHSA-crg9-c62w-j2p5), [GHSA-qgj5-6x35-9g6f](https://github.com/openclaw/openclaw/security/advisories/GHSA-qgj5-6x35-9g6f), [GHSA-62qm-6fjj-6g23](https://github.com/openclaw/openclaw/security/advisories/GHSA-62qm-6fjj-6g23), [GHSA-hgv5-f2r3-6v9r](https://github.com/openclaw/openclaw/security/advisories/GHSA-hgv5-f2r3-6v9r), [GHSA-3mq7-q27j-mq7q](https://github.com/openclaw/openclaw/security/advisories/GHSA-3mq7-q27j-mq7q), [GHSA-jhfx-v2j8-x3m6](https://github.com/openclaw/openclaw/security/advisories/GHSA-jhfx-v2j8-x3m6) — CVSS scores, affected/patched ranges, descriptions, interim mitigations.
- [OpenClaw — release 2026.8.1](https://github.com/openclaw/openclaw/releases/tag/v2026.8.1) — fetched 2026-09-14: released 2026-08-31; hardening notes, no vulnerability list.
- [npm registry — `openclaw` package metadata](https://registry.npmjs.org/openclaw) — queried 2026-09-14 (`npm view openclaw time`): 2026.8.1 published 2026-08-31, 2026.9.4 (latest) 2026-09-11.
- Single-source note: every fact above comes from the vendor's own advisory pages; no independent researcher write-up or press coverage was found for this batch as of 2026-09-14. Status is `patched` because the vendor states patched versions for every sampled advisory.
