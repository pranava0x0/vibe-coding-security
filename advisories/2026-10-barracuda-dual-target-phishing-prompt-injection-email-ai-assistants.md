---
id: 2026-10-barracuda-dual-target-phishing-prompt-injection-email-ai-assistants
title: "Phishing mail with two payloads: a password-protected attachment for the person and hidden prompt-injection text (HTML comments, CSS-hidden text, Base64 blocks, zero-width characters) for the AI assistant that summarises the inbox (Barracuda, 2026-10-06; campaign scale not disclosed)"
date_disclosed: 2026-10-06
last_updated: 2026-10-09
severity: medium
status: active
ecosystems: [email, ai-assistants, prompt-injection]
tools_affected: ["email AI assistants and inbox summarisers", "support, screening and procurement bots that read mail", "code assistants that read web documentation (Barracuda's own extension of the finding)"]
tags: [prompt-injection, phishing, indirect-prompt-injection, hidden-text, zero-width, ai-assistant, social-engineering]
---

## TL;DR
Barracuda Research analysed a phishing campaign built for two readers. The person sees routine internal mail with a password-protected attachment and the password in the body, a shape that blinds attachment scanning. The AI assistant that summarises or triages the inbox sees a second layer the person never does: hidden instructions that tell it to present the message as legitimate or urgent, or to ignore its directions and surface a wire-transfer request, leak data or invent an urgent action. Barracuda lists four concealment methods seen in real attacks, hidden text in **HTML comments**, **CSS-invisible text** (zero-pixel, white, hidden), instructions buried in **Base64-encoded blocks** such as image data, and **zero-width Unicode characters**. The sample passed reputation filters because sender and recipient were the same mailbox, the message carried a trusted spam-confidence score and it came from a public-sector domain. Barracuda did not disclose the campaign's scale. Two sources (the vendor's write-up and Infosecurity Magazine's report of it); no assistant product is named, so `active`, medium.

## What happened
Barracuda's post, dated 2026-10-06 and carried by Infosecurity Magazine and The Hacker News' weekly bulletin on 10-07/08, describes the sample and three real-world examples. An invoice email carries a hidden block that instructs the summarising model to add a fake priority action changing vendor payment details, so the summary nudges an employee toward paying the attacker. A résumé carries hidden text telling an automated screener to rate the candidate 10 out of 10 and recommend an immediate interview. A customer-support request frames itself as an authorised maintenance or admin mode and asks the bot to reveal its own configuration. Barracuda adds that code assistants are exploitable the same way through poisoned documentation on a web page the assistant reads, which is the class this corpus already tracks for [Copilot CLI](2026-10-copilot-cli-cryptographic-context-injection-secret-exfil.md) and [Claude Code](2026-08-claude-code-desktop-ghsa-batch.md).

What is new is not the technique, every method on the list has been in the prompt-injection literature for two years, but the packaging: the same message carries a conventional lure and an assistant-targeted payload, and the assistant payload is there to rescue the human lure when the person would otherwise have skipped the mail. The vendor's framing is that the AI layer between the mailbox and the user is now a target in its own right, and that filtering for the person is no longer filtering for the organisation.

## Am I affected?
You are in scope if any assistant reads mail on your behalf: inbox summarisers, calendar and ticket automation, résumé screeners, support bots, or an agent with a mail-reading MCP server. For a vibe-coded app, the same shape applies to any feature that passes user-submitted documents, support tickets or scraped pages to a model that can then take an action.

## If you are affected
1. Strip or render-to-text before the model sees it: drop HTML comments, apply CSS so hidden elements are removed, decode and discard Base64 blobs that are not real attachments, and normalise zero-width characters out of the text an assistant summarises.
2. Keep the assistant's summary and the assistant's actions apart. A model that reads mail should not also be able to approve a payment, change vendor details or send a wire request without a person seeing the original message.
3. Review recent assistant-recommended actions that originated in email, especially payment-detail changes and "urgent" items, against the raw source of the message.
4. If an assistant already acted on an injected instruction, treat it as an account compromise of the assistant's permissions and follow [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention
Anything the model reads from outside the organisation is untrusted input, whatever channel it arrived on; design the assistant so that input can inform but never instruct ([agent-sandboxing.md](../prevention/agent-sandboxing.md), [mcp-hygiene.md](../prevention/mcp-hygiene.md)). Log the raw content alongside the summary so a hidden instruction can be found after the fact.

## Sources
- [Barracuda — Threat Spotlight: Email attacks target both humans and AI in the same message](https://blog.barracuda.com/2026/10/07/email-attacks-target-both-humans-ai-assistants) (fetched 2026-10-09; page dated "Updated: Oct. 6, 2026"; the dual-target sample, the four concealment techniques, the invoice, résumé and support-bot examples, the code-assistant extension)
- [Infosecurity Magazine — Attackers Hide AI Prompt Injections Inside Phishing Emails](https://infosecurity-magazine.com/news/attackers-hide-ai-prompt) (fetched 2026-10-09; confirms the campaign description and that Barracuda "did not say how widespread the campaign was")
- [The Hacker News — ThreatsDay bulletin, week of 2026-10-09](https://thehackernews.com/2026/10/threatsday-ransomware-affiliate.html) (the "Phishing Campaign Targets Both Humans and AI Agents" item quoting Barracuda)
