---
id: 2025-09-postmark-mcp-backdoor
title: "postmark-mcp backdoor — first malicious MCP server (September 2025)"
date_disclosed: 2025-09-25
last_updated: 2026-05-16
severity: high
status: contained
ecosystems: [npm, mcp]
tools_affected: [claude-code, cursor, any-mcp-host]
tags: [mcp, supply-chain, email-exfiltration, trust-erosion, npm]
---

## TL;DR
The npm package `postmark-mcp` — an unofficial MCP server for the Postmark email service — was modified in v1.0.16 (published 2025-09-17) to silently BCC every outgoing email to `phan@giftshop[.]club`. Versions 1.0.0–1.0.15 were clean: the attacker built trust for months before injecting the backdoor. This is the first publicly-known malicious MCP server. ~1,643 downloads before removal.

## What happened
The author published 15 clean, functional versions of `postmark-mcp` impersonating the official Postmark Labs MCP library. AI assistants installed it, sent emails through it for months, and saw correct behavior. Adoption grew.

In v1.0.16, the attacker added **one line of code**: a hidden BCC field on every outgoing email pointing to an attacker-controlled inbox.

Because MCP servers typically operate with broad permissions and act on behalf of an AI assistant, the exfiltrated emails included password resets, invoices, internal memos, and other high-value content.

## Am I affected?

```bash
# Did you install postmark-mcp from npm?
npm ls -g postmark-mcp
npm ls postmark-mcp --all

# Check your MCP config files for it
grep -r "postmark-mcp" ~/.config/claude/ ~/.cursor/ ~/.codeium/ 2>/dev/null
grep -r "postmark-mcp" ~/Library/Application\ Support/Claude/ 2>/dev/null
```

If `postmark-mcp` appears in any MCP config, check whether you sent emails through it after 2025-09-17.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)
1. Uninstall `postmark-mcp` from every machine and MCP config.
2. Rotate **every credential that has ever been sent via email through this MCP** (password reset links, API key delivery emails, etc.).
3. Audit your Postmark "sent" logs for BCC traffic to `phan@giftshop[.]club` or anything else suspicious.
4. Use only the **official** Postmark MCP from `postmarkapp.com` going forward.

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — vet every MCP before installing

The general lesson: **an MCP server is arbitrary code running with the AI's privileges**. Treat MCP installs with at least as much scrutiny as `npm install -g`. Prefer official MCPs from the vendor; for community MCPs, read the source, check author reputation, and pin a specific commit.

## Sources
- [Postmark — Security Alert: Malicious 'postmark-mcp' npm Package Impersonating Postmark](https://postmarkapp.com/blog/information-regarding-malicious-postmark-mcp-package)
- [The Hacker News — First Malicious MCP Server Found Stealing Emails](https://thehackernews.com/2025/09/first-malicious-mcp-server-found.html)
- [Snyk — Malicious MCP Server on npm postmark-mcp Harvests Emails](https://snyk.io/blog/malicious-mcp-server-on-npm-postmark-mcp-harvests-emails/)
- [Dark Reading — Sneaky, Malicious MCP Server Exfiltrates Secrets via BCC](https://www.darkreading.com/application-security/malicious-mcp-server-exfiltrates-secrets-bcc)
- [The Register — Fake Postmark MCP npm package stole emails with one-liner](https://www.theregister.com/2025/09/29/postmark_mcp_server_code_hijacked/)
- [Koi — First Malicious MCP in the Wild](https://www.koi.ai/blog/postmark-mcp-npm-malicious-backdoor-email-theft)
