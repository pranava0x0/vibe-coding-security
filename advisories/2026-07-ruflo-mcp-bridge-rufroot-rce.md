---
id: 2026-07-ruflo-mcp-bridge-rufroot-rce
title: "RufRoot: Ruflo's unauthenticated MCP bridge lets one HTTP request run shell commands and poison agent memory (CVE-2026-59726, CVSS 10.0, patched 3.16.3)"
date_disclosed: 2026-07-29
last_updated: 2026-07-29
severity: critical
status: patched
ecosystems: [mcp, npm, docker]
tools_affected: [ruflo (formerly claude-flow), claude code, openai codex]
tags: [cve, mcp, unauthenticated-rce, agent-orchestration, memory-poisoning, credential-theft]
---

## TL;DR
Noma Security disclosed **RufRoot**: Ruflo (formerly Claude Flow), an open-source multi-agent orchestration harness for Claude Code and OpenAI Codex with ~67,000 GitHub stars and roughly 10M downloads, shipped a default Docker configuration that bound its Model Context Protocol "bridge" to `0.0.0.0:3001` with **zero authentication**. A single unauthenticated HTTP POST to `/mcp` could invoke any of 233 exposed tools — including a raw shell-execute tool — for full remote code execution, LLM API key theft, conversation harvesting, and persistent AI-memory poisoning. **CVE-2026-59726**, CVSS **10.0**. Reported 2026-06-30, patched within 24 hours in **v3.16.3**, publicly disclosed 2026-07-29.

## What happened
Ruflo is an AI agent-orchestration platform: it lets developers spin up "swarms" of Claude Code / Codex agents that coordinate over persistent memory and call tools via MCP. To wire that together, Ruflo runs an Express.js **MCP bridge** — a server that turns HTTP requests into MCP tool calls against the running agent swarm.

Noma Labs researcher **Eli Ainhorn** found that Ruflo's default `docker-compose` setup:
- Bound the bridge's port **3001 to all network interfaces** (`0.0.0.0`), not just localhost.
- Accepted `POST /mcp` and `POST /mcp/:group` requests and routed them straight into `executeTool()` with **no authentication check at all**.
- Exposed **233 tools** through that unauthenticated endpoint, including `ruflo__terminal_execute` — arbitrary shell command execution inside the container.

A single crafted request was sufficient for code execution ([Noma Security](https://noma.security/blog/rufroot-the-mcp-bridge-vulnerability-that-turns-agents-into-rogue-admins-cve-2026-59726/), [The Hacker News](https://thehackernews.com/2026/07/ruflo-mcp-flaw-lets-unauthenticated.html)):
```bash
curl -s -X POST https://<target>:3001/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"ruflo__terminal_execute","arguments":{"command":"id && hostname"}}}'
```
Commands run as the container's `node` user (UID 1000) — enough to steal the LLM API keys sitting in the container's environment variables, read every stored conversation, and — because Ruflo's persistent agent memory is itself one of the 233 exposed tools — **write false "memories" into the agent's own long-term store**, biasing every future session's behavior without touching a config file a developer would think to review.

**Disclosure timeline:**
- **2026-06-30** — Noma Labs reports the finding to Ruflo maintainer Reuven Cohen.
- **Within ~24 hours** — fix merged (PR #2521), shipped as **v3.16.3**.
- **2026-07-29** — GitHub Security Advisory **GHSA-c4hm-4h84-2cf3** and **CVE-2026-59726** published; Noma and The Hacker News publish technical writeups.

NVD confirms the CVE↔GHSA pairing directly: CVE-2026-59726, CVSS 3.1 **10.0** (`AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`), CWE-78 (OS command injection) + CWE-306 (missing authentication for a critical function) + CWE-942 (permissive cross-domain policy), affecting Ruflo before 3.16.3, cross-referencing GHSA-c4hm-4h84-2cf3 ([NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59726)).

Because the vulnerable tool set includes both credential-exposure and memory-write primitives, The Hacker News reports that patching alone does not confirm a previously-exposed instance is clean — Noma's own remediation guidance tells operators to also **rotate every LLM API credential** the container held and **audit the AgentDB/MongoDB memory store for injected "memories"** left behind before the patch, since an attacker who reached the bridge pre-patch could have planted a persistent backdoor or poisoned instruction that a version bump alone won't remove.

## Am I affected?
Check your Ruflo version:
```bash
docker exec <ruflo-container> cat package.json | grep '"version"'
```
Anything before **3.16.3** shipped the unauthenticated bridge by default. Check whether your deployment is/was network-exposed:
```bash
docker port <ruflo-container> | grep 3001
# or, from outside the host:
curl -s -X POST http://<host>:3001/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```
If that returns a tool list without any credential, your (pre-3.16.3) instance was — or still is — exploitable. Also check that MongoDB (port 27017, used for Ruflo's memory store) isn't separately exposed to the network.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — rotate every LLM API key the container had in its environment.

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — never bind an MCP transport to `0.0.0.0`; treat "unauthenticated by default" as the norm to check for, not the exception.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — persistent agent memory is a write-target: audit it for injected content the same way you'd audit a config file after any suspected exposure window.

## Why this matters for vibe coders
RufRoot is a clean instance of this repo's standing "MCP servers are unauthenticated network services by default" pattern (siblings: nginx-ui MCPwn, Atlassian `mcp-atlassian` MCPwnfluence, Azure MCP Server) — except the blast radius here is unusually broad, because Ruflo's bridge deliberately exposes hundreds of tools (shell, database, agent management, memory) as a *feature*, not an oversight in one tool's scope. It also extends the "AI-agent config files are a write-target" caution one step further: past incidents (TrapDoor, Miasma Wave 5) poisoned `.cursorrules`/`CLAUDE.md` files a developer could `git diff`; here the poisoned state lives in the agent's own persistent memory store, which most teams have no habit of auditing at all. If you run any self-hosted multi-agent orchestration platform, don't assume its default Docker Compose file is safe to expose — check the bind address on every port it publishes.

## Sources
- [Noma Security — RufRoot: The MCP Bridge Vulnerability That Turns Agents Into Rogue Admins (CVE-2026-59726)](https://noma.security/blog/rufroot-the-mcp-bridge-vulnerability-that-turns-agents-into-rogue-admins-cve-2026-59726/) — primary technical disclosure, PoC, researcher attribution, remediation detail.
- [The Hacker News — Ruflo MCP Flaw Lets Unauthenticated Attackers Run Commands and Poison AI Memory](https://thehackernews.com/2026/07/ruflo-mcp-flaw-lets-unauthenticated.html) — independent corroboration, disclosure timeline, post-breach remediation guidance.
- [NVD — CVE-2026-59726](https://nvd.nist.gov/vuln/detail/CVE-2026-59726) — canonical CVE record, CVSS vector, CWE classification, GHSA-c4hm-4h84-2cf3 cross-reference.
