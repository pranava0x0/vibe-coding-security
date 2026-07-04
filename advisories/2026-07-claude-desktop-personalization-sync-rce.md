---
id: 2026-07-claude-desktop-personalization-sync-rce
title: "Claude Desktop personalization-sync prompt injection → reverse shell — Anthropic calls it expected functionality (July 2026)"
date_disclosed: 2026-07-01
last_updated: 2026-07-04
severity: high
status: active
ecosystems: [claude-code, anthropic, mcp]
tools_affected: [claude-desktop]
tags: [prompt-injection, rce, mcp, lethal-trifecta, wont-fix, account-takeover]
---

## TL;DR

Pentera Labs red teamers showed that Claude Desktop's account-wide **personalization/preferences** feature — which syncs across every device signed into a Claude account — is an unsandboxed instruction channel: a base64-encoded prompt planted in personal preferences silently loads on every future chat and, if a command-capable MCP connector (e.g., Desktop Commander) is installed, executes a stealthy reverse shell with no user interaction beyond opening the app. Anthropic classified this as **expected functionality**, not a vulnerability — "personal preferences, skills, and MCP connectors [are] features that can execute code through Claude Desktop by design." No CVE, no patch.

## What happened

Pentera Labs (researchers Dvir Avraham and Reef Spektor) disclosed findings reported **2026-07-01** ([The Register](https://www.theregister.com/security/2026/07/01/red-teamers-turned-claude-desktop-into-a-double-agent-to-do-their-evil-bidding/5264692)): after compromising a victim's email inbox via an unrelated third-party breach, the red team used that access to log into the victim's Claude account and inject a **base64-encoded malicious prompt into the account's personal preferences**. Because preferences sync account-wide across every device, the payload propagated silently to the victim's Claude Desktop app the next time they opened it and started a chat — no attachment, no link click, no separate exploit delivery needed ([TechNadu](https://www.technadu.com/claude-desktop-hijacked-for-remote-code-execution-deepseek-generates-in-browser-ransomware/630204/)).

The injected instruction told Claude to check whether a command-capable tool (an MCP connector such as Desktop Commander, or similar) was available. If one was present, Claude used it to execute a **stealthy reverse shell**; if not, Claude instead rendered a convincing fake error message with a "fix" link, pivoting the attack into phishing. Both branches ran silently, behind the scenes, as soon as the victim opened a normal chat.

Anthropic's response, per the researchers: the company does not consider this a vulnerability in its infrastructure, since it requires a **compromised Claude account** as a precondition, and stated that "our current threat model treats personal preferences, skills, and MCP connectors as features that can execute code through Claude Desktop by design." No CVE has been assigned and there is no patch.

This is a sibling of the previously tracked **Claude Desktop Extensions (DXT) zero-click RCE** ([advisories/2026-02-claude-desktop-extensions-rce.md](2026-02-claude-desktop-extensions-rce.md)), where Anthropic similarly declined to fix a connector-chaining lethal-trifecta issue as "outside our threat model." Both share the same root cause — Claude autonomously composing a low-trust content source (a calendar event in the DXT case; account-synced personal preferences here) with a high-trust executor connector, with no confirmation gate in between — but this one adds **account-compromise-driven cross-device persistence** as a new distribution mechanism distinct from the DXT case's single-session calendar poisoning.

## Am I affected?

You are exposed if you use Claude Desktop with any command-capable MCP connector or extension installed (Desktop Commander or similar), **and** an attacker gains access to your Claude account (directly, or via a compromised linked email/SSO identity).

```text
Review your Claude account's personal preferences / custom instructions manually for
any text you did not write yourself, especially base64-looking blobs or instructions
referencing "check for tools," "run a command," or "display an error."
```

## If you are affected

1. Treat any unexplained content in your Claude account's personal preferences or custom instructions as a compromise indicator; remove it immediately.
2. If you find injected preferences, assume any command-capable MCP connector on any device signed into that account may have executed attacker instructions — treat those machines as potentially compromised and follow [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).
3. Rotate the credentials for the account/identity used to sign into Claude (especially the linked email), and enable MFA if not already active, per [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Review which MCP connectors/extensions you have installed in Claude Desktop and remove any command-capable ones you don't actively need.

## Prevention

- Treat "personalization" / account-wide preference sync in any AI desktop tool as a code-adjacent trust boundary, not just cosmetic settings — protect the account behind strong auth (MFA, unique password) as if it were a privileged system, since Anthropic has stated it will not add sandboxing here.
- Avoid installing command-capable MCP connectors (shell/file-execution tools) into AI desktop apps unless you specifically need them, and remove them when done — see [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).
- See [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) for the general connector-chaining "lethal trifecta" mitigation pattern (never let agent-readable, attacker-influenceable content reach a privileged executor without an explicit, immutable confirmation step).

## Sources

- [The Register — "Red teamers turned Claude Desktop into a double agent to do their evil bidding"](https://www.theregister.com/security/2026/07/01/red-teamers-turned-claude-desktop-into-a-double-agent-to-do-their-evil-bidding/5264692) — primary reporting: attack chain, Pentera Labs attribution, Anthropic's stated response.
- [TechNadu — "Claude Desktop Hijacked for Remote Code Execution, DeepSeek Generates In-Browser Ransomware"](https://www.technadu.com/claude-desktop-hijacked-for-remote-code-execution-deepseek-generates-in-browser-ransomware/630204/) — independent confirmation of the exploitation mechanism.
