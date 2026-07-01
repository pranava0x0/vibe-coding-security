---
id: 2026-03-claudy-day-claude-ai-exfiltration
title: "Claudy Day — three chained Claude.ai flaws exfiltrate conversation history via hidden URL-parameter prompt injection (March 2026)"
date_disclosed: 2026-03-18
last_updated: 2026-07-01
severity: high
status: mitigated
ecosystems: [claude-ai]
tools_affected: ["Claude.ai / claude.com web app"]
tags: [prompt-injection, data-exfiltration, claude-ai, open-redirect, anthropic]
---

## TL;DR

Oasis Security disclosed **"Claudy Day"**: three chainable flaws in **Claude.ai / claude.com** that together let an attacker deliver a single crafted link and silently exfiltrate a victim's Claude conversation history — no visible malicious text, no confirmation dialog. Anthropic fixed the prompt-injection vector; the open-redirect and Files-API exfiltration channel were still being addressed as of the report's publication.

## What happened

Claude.ai supports pre-filling the chat box via a `claude.ai/new?q=...` URL parameter — intended for "share a prompt" links. Oasis Security found three flaws that chain into a full exploit:

1. **Invisible prompt injection via the `q=` parameter.** An attacker embeds HTML tags in the `q=` value that render invisibly in the pre-filled chat box. The victim sees what looks like an innocuous prompt; when they press Enter, Claude also processes the hidden instructions as part of the submitted prompt.
2. **Data exfiltration via the Anthropic Files API.** The hidden instructions direct Claude to search the victim's own conversation history/memory for sensitive content, write it to a file, and upload that file via the **Files API** using an attacker-controlled API key embedded in the injected prompt — sending the victim's data straight to the attacker's own Anthropic account. No third-party MCP integration is required for this step.
3. **Open redirect on `claude.com`.** URLs of the form `claude.com/redirect/<target>` redirect without validating the destination. Paired with a Google Ads campaign (which only validates the display hostname, `claude.com`), an attacker can run a legitimate-looking search ad that silently redirects clicks to the crafted injection URL — giving the whole chain a trusted-looking delivery vector.

In a default Claude.ai session, a successful chain can expose conversation history and memory — which may include business strategy, financial details, health information, or anything else a user has discussed with Claude — and, where MCP servers or other integrations are connected, potentially files, messages, or connected-service data reachable from that session.

Anthropic was notified through its Responsible Disclosure Program before publication. Per the researchers, **the prompt-injection vector has been fixed**; the open-redirect and Files-API exfiltration issues were still being addressed as of publication (2026-03-18, updated 2026-05-27) — treat this as **mitigated, not fully patched**, until Anthropic confirms both remaining issues are closed.

## Am I affected?

This is a web-app vulnerability, not something you can grep for locally. You were at risk if you ever clicked a `claude.ai/new?q=...` or `claude.com/redirect/...` link from an untrusted source (email, ad, chat, social media) before the fix.

- Review your Claude.ai conversation history for any sessions you don't recognize starting, or any session where a prompt appeared with unexpected/garbled leading content.
- If you clicked a suspicious Claude-branded link and then noticed Claude referencing conversations or context you didn't provide in that session, treat your account as potentially exposed.

## If you are affected

1. Review your Claude.ai account's connected integrations (MCP servers, third-party connections) and revoke anything unfamiliar.
2. Treat any sensitive information ever discussed in Claude.ai as potentially exposed if you clicked a suspicious `claude.ai`/`claude.com` link around or before March 2026.
3. Report suspicious Claude-branded links to Anthropic rather than clicking them.

## Prevention

- Treat AI-chat "shareable prompt" links (`?q=`, `?prompt=`, etc.) from unsolicited sources the same as any other phishing link — don't click, and if you must, inspect the full URL for hidden/invisible content first.
- Prefer typing prompts directly rather than following pre-fill links from email or ads.
- See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) for general guidance on treating AI-tool sessions as a data-exposure surface, not just a productivity tool.

## Sources

- [Oasis Security — "Claude.ai Prompt Injection Vulnerability"](https://www.oasis.security/blog/claude-ai-prompt-injection-data-exfiltration-vulnerability) — primary disclosure: technical breakdown of all three chained flaws, disclosure/update dates, patch status.
- [SecurityBuzz — "Researchers Say Claude Flaws Could Be Chained to Silently Exfiltrate User Data"](https://securitybuzz.com/cybersecurity-news/researchers-say-claude-flaws-could-be-chained-to-silently-exfiltrate-user-data/) — independent confirmation, patch-status summary, researcher attribution.
