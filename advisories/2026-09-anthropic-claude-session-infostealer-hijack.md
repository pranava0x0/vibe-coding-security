---
id: 2026-09-anthropic-claude-session-infostealer-hijack
title: "Generic infostealer malware hijacks Claude.ai browser sessions to drain paid usage and expose account data"
date_disclosed: 2026-08-30
last_updated: 2026-09-12
severity: high
status: active
ecosystems: [anthropic, claude]
tools_affected: ["Claude.ai (web)", "Claude Pro/Max/Team accounts"]
tags: [infostealer, session-hijacking, credential-theft, account-takeover, malvertising-adjacent]
---

## TL;DR
Anthropic began emailing affected users on **2026-08-30** warning that ordinary desktop infostealer malware (Vidar, LummaC2, StealC, RedLine, Acreed on Windows; Atomic Stealer on a small number of Macs) has been stealing **already-authenticated Claude.ai browser session cookies** from infected machines and using them to log in as the victim — bypassing passwords and MFA entirely — to consume the victim's paid usage quota. The malware has no connection to Claude itself; it's generic credential-stealing malware that happens to also scoop up Claude's session cookie along with everything else in the browser.

## What happened
Anthropic's warning email, quoted directly by multiple outlets: *"We recently became aware of a bad actor that is using common infostealer malware to steal Claude login sessions from people's computers, then using those login sessions to access Claude accounts and consume their usage."* ([Malwarebytes](https://www.malwarebytes.com/blog/news/2026/09/infostealers-are-hijacking-claude-accounts-at-users-expense), 2026-09-01).

The mechanism is standard session-cookie theft, not a Claude-specific bug: infostealers already resident on a victim's machine (delivered the usual way — malicious downloads, cracked software, fake installers) harvest browser-stored passwords, cookies, and local app credentials wholesale. Because a session cookie represents an already-authenticated state, an attacker who replays it skips login and MFA entirely — the classic "pass-the-cookie" pattern. Victims noticed because their **usage limits appeared to refill and then drain while they weren't using Claude** ([BleepingComputer](https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-warns-infostealer-malware-is-hijacking-claude-sessions-to-drain-usage/), 2026-08-31).

A hijacked session exposes whatever the account holds: prior conversation history, uploaded files, project contents, connected organizational resources, and anything entered during coding or research tasks — not just the consumed API quota ([BleepingComputer](https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-warns-infostealer-malware-is-hijacking-claude-sessions-to-drain-usage/)).

**Anthropic's response:** signed affected users out (revoking the stolen sessions), removed saved payment methods from compromised accounts, and identified and refunded unauthorized charges. Anthropic explicitly cautioned that platform-side lockout only treats the symptom: *"Signing you out of Claude stops the stolen sessions, but it doesn't remove the malware"* ([BleepingComputer](https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-warns-infostealer-malware-is-hijacking-claude-sessions-to-drain-usage/)) — the underlying infection on the victim's machine, and every other credential it touched, remains compromised until the user cleans the machine separately.

No CVE applies — this is a malware-campaign/account-security incident, not a product vulnerability with a patch.

## Am I affected?
Anthropic notified affected users directly by email. Warning signs even without an email: Claude usage/quota that drops unexpectedly between your own sessions, unrecognized entries in Claude's "active sessions" list (Settings → Security), or a saved payment method you don't recognize interacting with your account. If any of those apply, assume infostealer malware is present on a machine where you've logged into Claude.

## If you are affected
1. Scan and clean the infected machine **before** logging back into Claude or any other account — signing back in on a still-infected machine hands the attacker a fresh session immediately.
2. Treat every credential used on that machine as compromised, not just Claude: change your email password, enable 2FA, and sign out other devices; change passwords for banking, work, and cloud accounts; check card statements for unauthorized charges.
3. Contact `usersafety@anthropic.com` if you see further suspicious activity after Anthropic's initial lockout.
4. → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — written for local-agent exploitation specifically, but its "assume full credential exposure, rotate everything the machine touched" guidance applies directly to a generic infostealer infection as well.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — a browser session cookie is a credential; the same hygiene that protects API keys and cloud IAM tokens (short-lived sessions, avoiding credential-stealing malware vectors) applies here.
- Don't download cracked software, pirated installers, or "free" tool cracks — the single largest infostealer delivery vector across this repo's tracked incidents.
- Review Claude's active-sessions list periodically (Settings → Security) and revoke anything unrecognized.

## Update 2026-09-12 — Okta quantifies the market: replayable AI tokens for Anthropic, Cursor, OpenAI and others in a 7 GB stealer dump, sold with "24x7 support"

Okta's threat-intelligence team analysed a **7 GB infostealer log** posted to Telegram on **2026-08-02** covering **5,871 infected machines in 162 countries**. It contained **44,791 unique JWTs**, of which **555** were likely AI-service authentication tokens — for Google, Microsoft, **Anthropic**, Amazon, Character.ai, **Cursor**, Poe.com and Pika AI — plus **2,937 encrypted JWT structures from OpenAI** (ChatGPT uses NextAuth.js sessions). Okta's Jeremy Kirk: *"Session tokens and API keys are sought specifically by threat actors because it is often possible to replay those secrets and bypass credential-based authentication."* Underground vendors now sell the bundles: one offered discounted access to Claude, Cursor, ChatGPT and Gemini with "24x7 support and money-back guarantees"; anti-detect browsers such as Camoufox are used to replay the sessions without tripping device checks (The Hacker News, 2026-09-09). This is the supply side of the account-hijacking Anthropic warned about above, and it extends the exposure from Claude.ai to **Cursor sessions** and OpenAI accounts. Okta's recommendations: IP allow-listing where available, Chrome's Device Bound Session Credentials, short-lived OAuth tokens, passkeys, and monitoring API-key usage patterns. Status stays `active`.

## Sources
- [The Hacker News — Infostealer Logs Expose Replayable AI Tokens That Can Bypass MFA](https://thehackernews.com/2026/09/infostealer-logs-expose-replayable-ai.html) — fetched 2026-09-12; 2026-09-09: Okta's dataset figures (5,871 machines, 162 countries, 44,791 JWTs, 555 AI-linked, 2,937 OpenAI), service list, vendor offerings, Kirk quote, remediation list.
- [Malwarebytes — Infostealers are hijacking Claude accounts at users' expense](https://www.malwarebytes.com/blog/news/2026/09/infostealers-are-hijacking-claude-accounts-at-users-expense) — 2026-09-01: direct quote from Anthropic's warning email, remediation steps, recommended user actions.
- [BleepingComputer — Anthropic warns infostealer malware is hijacking Claude sessions to drain usage](https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-warns-infostealer-malware-is-hijacking-claude-sessions-to-drain-usage/) — 2026-08-31: malware family list (Vidar, LummaC2, StealC, RedLine, Acreed, Atomic Stealer), Anthropic's remediation actions, "signing out doesn't remove the malware" quote.
- [SecurityWeek — Anthropic Warns Claude Users of Infostealer Malware Infections](https://www.securityweek.com/anthropic-warns-claude-users-of-infostealer-malware-infections/) — 2026-08-31: independent corroboration of the malware families and timeline.
