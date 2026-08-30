---
id: 2026-08-context7-contextcrush-prompt-injection
title: "Context7 MCP documentation server — attacker-registered library docs inject instructions into every connected coding agent ('ContextCrush', CVE-2026-75130); fixed since February 2026, CVE only assigned in August"
date_disclosed: 2026-02-18
last_updated: 2026-08-30
severity: high
status: patched
ecosystems: [mcp, npm]
tools_affected: ["Context7", "Upstash Context7 MCP server"]
tags: [prompt-injection, mcp, supply-chain, credential-theft, documentation-poisoning]
---

## TL;DR

**Context7** — Upstash's MCP documentation server that feeds version-specific library docs to Cursor, Claude Code, Windsurf, and other coding agents (~50–61K GitHub stars, several million monthly npm downloads) — let anyone who registers a library on its public index attach "Custom AI Instructions" that were served **verbatim, unsanitized, and indistinguishable from real documentation** to every agent that queried that library. Researchers at Noma Security ("ContextCrush") demonstrated a poisoned library entry that made a connected agent read local `.env` files, exfiltrate the contents to an attacker-controlled endpoint, and delete files — triggered by an ordinary "look up docs for this library" request, no unusual user action required. Upstash fixed it with sanitization/guardrails within days of the February 2026 report. A CVE (**CVE-2026-75130**, CVSS 3.1 9.0 critical / CVSS 4.0 6.4 medium) was assigned in August 2026, months after the fix shipped — treat the CVE's publication date as a paperwork date, not a "this is currently unpatched" signal.

## What happened

Context7 is an MCP server: any coding agent that adds it as a tool source can call `resolve-library-id` and `query-docs` to pull up-to-date documentation for a library instead of relying on the model's (often stale or hallucinated) training knowledge. Library maintainers — or, critically, **anyone who registers an entry, not just the actual maintainer** — could attach a "Custom Rules" / "Custom AI Instructions" field intended to help agents use the library correctly (e.g., "always import from the `/v2` path").

Noma Security's research, reported to Upstash on **2026-02-18**, showed those custom instructions were **served through the MCP server with no sanitization, content filtering, or signal distinguishing them from legitimate documentation text**. Because Context7's own trust model treats everything it returns as "documentation," any agent architecture that treats tool output as lower-trust than user input still had no way to tell a poisoned instruction field apart from a real one. Researchers registered a poisoned library and demonstrated the connected agent, acting on the injected instructions during a routine `query-docs` call: reading local `.env` files, sending the contents to an attacker-controlled GitHub repository, and performing destructive local file deletion — entirely through an agent's own already-granted filesystem and network permissions, since Context7 itself has no code-execution, file-write, or network capability of its own. It is a courier; the agent it's talking to is the payload's actual engine.

**Upstash's response, per Noma's own timeline:** accepted the finding 2026-02-19, deployed a fix ("rule sanitization and guardrails") **2026-02-23** — five days after report — and Noma published its writeup 2026-03-05 after verifying the fix. No evidence of exploitation prior to the fix.

**Why this is only now getting a CVE.** VulnCheck (`disclosure@vulncheck.com`) filed **CVE-2026-75130** on **2026-08-18**, citing Noma's original ContextCrush post as its primary reference, listing "Context7 through 2.1.2" as the affected range. Version 2.1.2 is the version Upstash's February fix shipped in — under the standard CVE convention, "through X" names the last vulnerable version, and the fix landed in that same release. Secondary coverage that treated the August CVE as describing a **current, unpatched** critical flaw (because no GHSA cross-reference or vendor release note explicitly ties CVE-2026-75130 to a fix) is reading the CVE's metadata gap, not a real gap in remediation — this repo's own past experience with GHSA publication dates lagging real disclosure dates ([see the June-disclosed MCP batch above](2026-08-agent-framework-mcp-cve-batch.md)) is the same pattern here, just for a CVE assignment instead of a GHSA database entry. This is stated explicitly because the underlying facts (fixed February, CVE filed August) come from two sources that don't cross-reference each other, and a reader who only saw the CVE record without Noma's timeline would reasonably conclude the opposite.

## Why this matters for vibe coders

Any MCP server that streams text into an agent's context is an instruction channel, not just a data channel — and a **documentation index anyone can register a library on** is one of the least-suspicious-looking places for that channel to be poisoned, because the entire point of the tool is "give the agent instructions about how to use this library correctly." This is the same "the file you load is treated as code" root cause tracked elsewhere in this repo (Hugging Face dataset loaders, PyPI import-time execution), applied to an MCP documentation feed instead of a package or dataset. If your agent config auto-approves Context7 (or any similarly-scoped documentation/registry MCP server) for filesystem and network access without per-call review, that trust extends to whatever any registrant of that index chooses to publish.

## Am I affected?

```bash
# Check whether Context7 is configured as an MCP server for your agent
grep -rl "context7" ~/.cursor/mcp.json ~/.claude.json ~/.codeium/windsurf/mcp_config.json 2>/dev/null
grep -rl "context7" .cursor/ .claude/ 2>/dev/null

# Check the installed version if you self-host rather than use the hosted service
npm ls @upstash/context7-mcp 2>/dev/null
```

Upstash's fix shipped in the release containing version **2.1.2** (Feb 2026); the hosted service has been patched since then, and later npm releases (4.0.3 and beyond, as of this writing) postdate the fix. There is no current action needed solely on the basis of this CVE if you are using an up-to-date Context7 — the exposure window closed in February 2026.

## If you are affected

If you registered or relied on a third-party library's Context7 entry before February 2026 and your agent had unattended filesystem/network access at the time, review shell history and outbound-connection logs from that period for unexpected `.env` reads or unfamiliar destinations.
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — treat any MCP server that can inject arbitrary text into your agent's context as a prompt-injection surface, documentation servers included.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — an agent that can read `.env` and make outbound network calls without per-action approval turns any injected instruction into an actual credential-theft primitive, regardless of which tool delivered it.

## Sources

- [NVD — CVE-2026-75130](https://nvd.nist.gov/vuln/detail/CVE-2026-75130) — fetched directly via the NVD API; CVSS 3.1 9.0 critical / CVSS 4.0 6.4 medium, affected range "through 2.1.2," published 2026-08-18.
- [Noma Security — "ContextCrush: The Context7 MCP Server Vulnerability"](https://noma.security/blog/contextcrush-context7-the-mcp-server-vulnerability/) — primary researcher writeup, fetched directly: attack mechanism, proof-of-concept detail (credential theft, exfiltration to attacker-controlled GitHub, destructive deletion), full disclosure timeline (reported 2026-02-18, accepted 2026-02-19, fixed 2026-02-23, published 2026-03-05).
- [VulnCheck — Context7 prompt injection via Custom AI Instructions](https://www.vulncheck.com/advisories/context7-prompt-injection-via-custom-ai-instructions) — the CVE-assigning advisory; confirms affected range and CVSS, does not itself state a patched version number or explicitly cross-reference the February fix.
- [Digital Applied — "An MCP Server Bug Scores 9.0. No Fix Is Documented"](https://www.digitalapplied.com/blog/context7-mcp-prompt-injection-cve-2026-75130) — secondary analysis, fetched directly; independently identified the version-number overlap between the CVE's affected range and Noma's February fix, and Context7's install-base figures (GitHub stars, npm download volume) used above.
