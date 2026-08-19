---
id: 2026-08-cosnitch-microsoft-copilot-oneclick-exfil
title: "CoSnitch: one-click data exfiltration from Microsoft Copilot Personal via an undocumented autorun parameter (CVE-2026-24301, patched)"
date_disclosed: 2026-08-18
last_updated: 2026-08-18
severity: critical
status: patched
ecosystems: [microsoft, copilot, oauth]
tools_affected: ["Microsoft Copilot Personal"]
tags: [prompt-injection, data-exfiltration, oauth, connector-chaining, one-click, memory-poisoning]
---

## TL;DR

Varonis Threat Labs found **three chainable weaknesses** in Microsoft Copilot Personal that let a single malicious link silently exfiltrate data from a victim's connected accounts (Gmail, Google Drive, Google Calendar, plus Copilot's own chat history and persistent memory) — no meaningful user interaction beyond the click, and no separate approval step. The core bug: an **undocumented `?autorun=1` URL parameter**, which — combined with the documented `?q=` prompt-prefill parameter — makes Copilot execute an attacker-supplied prompt instantly on page load instead of just pre-filling the input box for the user to confirm. Reported to Microsoft in **December 2025**; patched **2026-08-18**, roughly eight months later, with no evidence of pre-patch in-the-wild exploitation. Researchers found the undocumented parameter using a "meta-hacking" technique — repeatedly reframing Copilot's own refusals as follow-up questions until the model explained the mechanism it was refusing to use. Third Copilot flaw Varonis has disclosed in 2026, after Reprompt and SearchLeak.

## What happened

Varonis researcher Lior Adar disclosed **CVE-2026-24301** ("CoSnitch") on **2026-08-18**, the same day Microsoft shipped the fix ([Varonis](https://www.varonis.com/blog/cosnitch)). The attack chains three separate weaknesses in Microsoft Copilot Personal (the consumer-facing Copilot at `copilot.microsoft.com`, distinct from Microsoft 365 Copilot's enterprise product):

1. **Automatic prompt execution.** Copilot already supported a documented `?q=<text>` URL parameter that pre-fills the chat input with attacker-chosen text — by itself, this still requires the victim to manually hit send, so it isn't a one-click bug on its own. Varonis found an **undocumented second parameter, `?autorun=1`**, which — only when both parameters are present — causes Copilot to execute the pre-filled prompt automatically on page load, with no confirmation click. The full attack URL takes the shape `https://copilot.microsoft.com/?q=<malicious_prompt>&autorun=1`.
2. **Silent exfiltration via OAuth connectors.** Once the injected prompt runs, it executes with the full privileges of whatever the victim has already connected to Copilot — Gmail, Google Drive, Google Calendar, and Copilot's own chat history — using Copilot's built-in URL-fetch capability to encode stolen data into an outbound request to an attacker-controlled endpoint.
3. **Persistent memory poisoning.** A crafted webpage processed through Copilot's summarization feature can inject attacker instructions directly into the victim's **permanent Copilot memory store**, so the compromise can survive a password change or session revocation and keep re-triggering on future, unrelated sessions.

This is the same "reader connector piped into an executor with no trust boundary" shape already tracked in this repo for Claude Desktop Extensions, Claude Desktop's personalization-sync RCE, and Atlassian Rovo's exfiltration bug — here on a first-party Microsoft product, with a formally assigned CVE and a coordinated patch rather than a "won't fix."

**Discovery method — "meta-hacking."** Rather than directly probing for the bypass, Varonis interrogated Copilot about *why* automatic prompt execution was supposedly impossible, treating each refusal ("that won't work because…") as an invitation to ask about the "because." Copilot's own explanations of its guardrails eventually surfaced the undocumented `autorun` parameter it was describing as blocked ([The Register](https://www.theregister.com/research/2026/08/18/copilot-tricked-into-telling-reseachers-how-to-hack-itself/5288857)).

Microsoft patched CoSnitch on **2026-08-18**, about eight months after the December 2025 report — multiple outlets independently confirmed both the CVE assignment and this timeline ([Computerworld](https://www.computerworld.com/article/4211325/microsoft-finally-patches-critical-one-click-copilot-vulnerability-more-than-eight-months-after-learning-of-it.html), [CSO Online](https://www.csoonline.com/article/4211342/microsoft-finally-patches-critical-one-click-copilot-vulnerability-more-than-eight-months-after-learning-of-it-2.html)).

## Am I affected?

You were exposed if you use Microsoft Copilot Personal (`copilot.microsoft.com`) with any third-party account connected — Gmail, Google Drive, Google Calendar, or similar — and clicked a link you didn't fully trust before the **2026-08-18** patch. The fix is server-side; there is no client update to install, but confirm you haven't interacted with any suspicious `copilot.microsoft.com/?q=...&autorun=1`-shaped links before that date.

## If you are affected

1. Review Copilot's connected-services list (Settings → Connected apps) and disconnect anything you don't actively use.
2. Check Gmail/Google Drive/Google Calendar activity logs for unusual access patterns around any date you clicked an unfamiliar Copilot link.
3. Review Copilot's persistent memory/personalization settings for any instructions you don't recognize — memory poisoning here survives a password change, so inspect it explicitly rather than assuming a credential rotation clears it.
4. See [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) if you find evidence of unexpected connector activity.

## Prevention

- Treat any AI assistant with OAuth access to your inbox/drive/calendar as a privileged insider, not a passive tool — review its connector list the same way you'd review an OAuth app's permission grants.
- Be suspicious of links that open an AI assistant with pre-filled or auto-running prompts, especially from an untrusted source; a `?q=` or similarly-shaped parameter in a chat-assistant URL is a prompt-injection delivery vector, not just a convenience feature.
- → [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Sources

- [Varonis — CoSnitch: When Your AI Assistant Becomes Its Own Whistleblower](https://www.varonis.com/blog/cosnitch) — primary technical disclosure: CVE, timeline, three-weakness chain, autorun parameter, meta-hacking methodology.
- [The Register — Copilot tricked into telling researchers how to hack itself](https://www.theregister.com/research/2026/08/18/copilot-tricked-into-telling-reseachers-how-to-hack-itself/5288857) — independent corroboration of the meta-hacking discovery method and patch date.
- [Computerworld — Microsoft finally patches critical one-click Copilot vulnerability](https://www.computerworld.com/article/4211325/microsoft-finally-patches-critical-one-click-copilot-vulnerability-more-than-eight-months-after-learning-of-it.html) — independent corroboration of the December 2025 report date and ~8-month patch timeline.
