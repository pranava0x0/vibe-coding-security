---
id: 2026-07-promptfiction-claude-desktop
title: "PromptFiction — Claude Desktop's claude:// URI auto-submitted hidden prompts with zero clicks, chainable with Claudy Day for exfiltration (patched 1.1.2321)"
date_disclosed: 2026-07-15
last_updated: 2026-07-16
severity: high
status: patched
ecosystems: [claude-desktop, anthropic, mcp]
tools_affected: [claude-desktop]
tags: [prompt-injection, deeplink, uri-scheme, zero-click, exfiltration, claude-desktop, lethal-trifecta]
---

## TL;DR
Oasis Security disclosed **PromptFiction**: Claude Desktop's `claude://` custom URI scheme auto-opened the app and **auto-submitted** an attacker-crafted prompt with a single click — no Send/Enter action, no review screen, unlike Claude's web app which places the same content in the chat box but waits for the user to hit Enter. Chained with Oasis's earlier ["Claudy Day"](2026-03-claudy-day-claude-ai-exfiltration.md) findings (conversation-history extraction + Files-API exfil), this removed the one remaining human-in-the-loop step separating "victim clicks a link" from "conversation history silently leaves the machine." Fixed in **Claude Desktop 1.1.2321**.

## What happened
Claude Desktop registers a handler for the custom `claude://` URI scheme. Oasis Security found that a link of the form `claude://claude.ai/new?q=<prompt>` opened a new conversation and **immediately submitted the `q` parameter as a prompt** — no confirmation dialog, no Send button, nothing for the user to review before Claude began acting on it ([Oasis Security](https://www.oasis.security/blog/claude-desktop-vulnerability)). This is a materially different behavior from Claude's own web app (`claude.ai`), which places the same `q=` content into the chat input box but requires the user to actually press Enter before it's sent — a distinction this repo's [Claudy Day](2026-03-claudy-day-claude-ai-exfiltration.md) advisory already flagged as the web app's one remaining safeguard against this exact parameter-to-prompt injection class.

**Concealment**: Claude Desktop's interface collapses long messages behind a "show more" control, letting an attacker pad a `claude://` link's prompt with enough content that the malicious instruction scrolls out of the visible area — the same fold-based concealment shape already tracked in this repo's [Lies in the Loop](2025-09-litl-ai-approval-dialog-bypass.md) caution, applied here to injected prompt content rather than a command-approval dialog.

**Delivery and escalation**: A `claude://` link can be delivered via any channel — a webpage, a document, a chat message, an email, or a poisoned search result — and Oasis notes an attacker could further disguise it behind a `claude.com` open redirect, the same delivery trick documented in Claudy Day. Once the hidden prompt executes, Oasis documents three escalation paths: (1) instructing Claude to retrieve prior conversation history and upload it via Anthropic's Files API using attacker-supplied credentials — chaining directly into Claudy Day's exfiltration channel; (2) on a machine with Anthropic's official Filesystem MCP server installed, injecting remote-debugging code into a user's own scripts for local code execution; (3) general read/write access to whatever the configured MCP connectors expose — the same reader-into-executor "lethal trifecta" shape this repo has tracked repeatedly (Claude Desktop Extensions, Windsurf, Supabase MCP).

**Disclosure and fix**: Reported through Anthropic's Responsible Disclosure Program; fixed in **Claude Desktop 1.1.2321**, which now requires the user to manually review and send prompts delivered via a `claude://` link rather than auto-submitting them. No CVE has been assigned in either source. [Hackread's](https://hackread.com/promptfiction-flaw-auto-prompts-claude-desktop/) independent writeup corroborates the mechanism, the patched version, and the Claudy Day chaining.

**Distinct from other tracked Claude deeplink issues**: this is specifically the `claude://` scheme in **Claude Desktop**, not the `claude-cli://` scheme RCE already tracked in [Claude Code `claude-cli://` deeplink RCE](2026-05-claude-code-deeplink-rce.md) — different product, different URI scheme, different underlying bug, both now patched.

## Am I affected?
Check your Claude Desktop version — anything before **1.1.2321** was vulnerable:
- **macOS/Windows**: Claude Desktop → Help/About → version number.
- If you're on an older build, update immediately; there is no workaround short of updating, since the flaw required no user error beyond clicking an ordinary-looking link.

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — if you clicked an unfamiliar `claude://` link before updating and have MCP connectors configured, review recent conversation/file activity for anything you didn't initiate.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — limit which MCP connectors (especially filesystem/shell-capable ones) are active by default in Claude Desktop.

## Why this matters for vibe coders
PromptFiction is the logical next step after Claudy Day: it closes the one gap that let a defender say "at least the user has to hit Enter." Custom URI-scheme handlers registered by AI desktop apps are an under-scrutinized delivery surface — this repo has tracked the analogous `claude-cli://` RCE in Claude Code already; expect the same "does clicking a link require review before the agent acts on it?" question to keep surfacing across every AI desktop tool that registers its own protocol handler.

## Sources
- [Oasis Security — PromptFiction: a one-click flaw that made Claude Desktop act without consent](https://www.oasis.security/blog/claude-desktop-vulnerability) — primary disclosure, attack chain, patched version.
- [Hackread — PromptFiction Flaw Auto-Submitted Hidden Prompts in Claude Desktop](https://hackread.com/promptfiction-flaw-auto-prompts-claude-desktop/) — independent corroboration.
