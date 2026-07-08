---
id: 2026-07-claude-code-china-proxy-fingerprint
title: "Claude Code shipped a covert China-proxy fingerprinting channel steganographically encoded in the system prompt (versions 2.1.91–2.1.196; removed in 2.1.197)"
date_disclosed: 2026-06-30
last_updated: 2026-07-08
severity: medium
status: patched
ecosystems: [claude-code, anthropic]
tools_affected: [claude-code]
tags: [covert-channel, steganography, telemetry, vendor-hygiene, unicode, privacy]
---

## TL;DR

Independent researcher **Adnane Khan** published a GitHub-hosted technical analysis showing that Claude Code, when configured to route through a custom API endpoint (`ANTHROPIC_BASE_URL` set to anything other than `api.anthropic.com`), silently checked the proxy's hostname against a decoded list of **147 Chinese corporate/cloud/AI-lab domains** and the user's system timezone, then encoded the result as an **undisclosed covert channel using visually-identical Unicode character substitutions** inside the "Today's date is..." line of its own system prompt — sent back to Anthropic on every request, with no user notification. Anthropic acknowledged the code was present and shipped **Claude Code 2.1.197** removing it, though without a changelog entry documenting the removal.

## What happened

The finding first surfaced via a Reddit post and was substantiated by a GitHub-hosted technical writeup from security researcher **Adnane Khan**, who confirmed the mechanism was present in Claude Code **2.1.193, 2.1.195, and 2.1.196** (and reported as introduced in **2.1.91**, released 2026-04-02). Multiple outlets independently reported on and corroborated the same underlying GitHub analysis.

**How the covert channel worked:**

1. **Trigger condition.** When Claude Code is pointed at a custom API endpoint via `ANTHROPIC_BASE_URL` (rather than Anthropic's own `api.anthropic.com` — a configuration commonly used by proxy/gateway tools, self-hosted routers, and third-party billing wrappers), the client-side code extracted the configured hostname.
2. **Fingerprint check.** That hostname was compared against a **decoded list of 147 Chinese corporate, cloud, and AI-lab domains** (e.g., Baidu, Alibaba, ByteDance), and separately checked for AI-lab keywords ("deepseek," "moonshot," "minimax") in the route. The user's system timezone was also read and checked against `Asia/Shanghai` / `Asia/Urumqi`.
3. **Steganographic encoding.** Rather than sending an explicit telemetry field, the result was encoded invisibly into the system prompt's "Today's date is ..." line:
   - The date separator flipped from a dash (`2026-06-30`) to a slash (`2026/06/30`) if the system timezone matched a China-linked zone.
   - The apostrophe in "Today's" was swapped between four visually-identical Unicode code points — standard ASCII apostrophe, U+2019 (right single quotation mark), U+02BC (modifier letter apostrophe), and U+02B9 (modifier letter prime) — to encode whether the proxy hostname matched the domain list, the AI-lab keyword list, both, or neither.
   - Strings used in the detection logic were reportedly obfuscated in the compiled binary with a simple XOR (key 91).
4. **Purpose (as reported).** Security researchers characterized the likely motivation as detecting unauthorized proxy/route usage tied to "distillation attack" campaigns that Anthropic had previously and separately disclosed — i.e., using this signal to identify traffic patterns associated with third parties routing large volumes of requests through unofficial channels to train competing models on Claude's outputs.

**Anthropic's response:** Anthropic acknowledged the code was present in the shipped client and stated it would be removed in the next release. **Claude Code 2.1.197** was published shortly after, though its changelog did not explicitly document the removal of this mechanism.

**Why this belongs in this repo even without a CVE:** this is the same **invisible-Unicode steganographic encoding technique** this repo has repeatedly flagged as an attacker IOC (GlassWorm, TrapDoor, Miasma Wave 5) — here used by the **vendor itself**, inside a widely-deployed developer tool, to exfiltrate a covert signal about the user's network configuration and geography without disclosure. It fits this repo's "significant supply-chain hygiene incident at a major AI vendor" criterion: a widely-run developer tool shipped an undisclosed, deliberately-obfuscated data channel for roughly three months before independent researchers found it.

## Update 2026-07-08 — China's NVDB issues a public "security backdoor" alert; Alibaba bans internal use; Anthropic engineer responds on the record

On **2026-07-08**, China's **National Vulnerability Database (NVDB)**, a body affiliated with the Ministry of Industry and Information Technology, published a public alert calling the mechanism described above a **"security backdoor"** — asserting it could transmit users' location and identity-related signals to Anthropic without consent, and advising "relevant institutions and users" to "conduct a comprehensive check immediately" and uninstall or upgrade to a version with the code removed. The alert was widely reported same-day by CNBC, CBS News/AFP, The Register, Tom's Hardware, Security Boulevard, China Daily, Global Times, and Cybernews.

**Anthropic's on-the-record response:** Claude Code engineer **Thariq Shihipar** stated publicly (as quoted by CBS News/AFP) that the mechanism was "an experiment we launched in March that was meant to prevent account abuse" (i.e., anti-distillation abuse detection, consistent with this advisory's original reporting), that "the team has landed stronger mitigations since then," and that Anthropic had "actually been meaning to take this down for a while." Anthropic maintains the mechanism does not constitute a security backdoor and notes China access to Claude was never a permitted use case in the first place.

**Patched version — note a reporting discrepancy:** this advisory's original sources (2026-06-30/07-01) reported the mechanism was removed in **Claude Code 2.1.197**. CNBC's 2026-07-08 coverage of the NVDB alert instead states it was "removed in version 2.1.198, released July 1." Both dates point to the same ~July 1 timeframe; we have not independently confirmed which exact version number fully removed the mechanism (it's plausible 2.1.197 shipped a partial removal and 2.1.198 completed it, or one outlet has the version number slightly wrong). **If you need certainty, update to the latest available Claude Code release rather than pinning to either 2.1.197 or 2.1.198 specifically.**

**Business fallout:** Alibaba notified employees it will **ban internal use of Claude Code starting 2026-07-10**, directing staff to switch to its own Qoder tool — the first documented case of a major tech company restricting Claude Code over a security disclosure this repo tracks.

**Status:** kept as `patched` (Anthropic confirms the mechanism has been removed), but this is now also a **vendor-trust/geopolitical-fallout incident**, not purely a technical one — the underlying facts are unchanged from the original disclosure, but an official state body's public alert and a major enterprise's usage ban are new, independently newsworthy developments worth tracking here.

## Am I affected?

You may have been running an affected build if you used Claude Code with a custom `ANTHROPIC_BASE_URL` (any third-party proxy, self-hosted gateway, or billing wrapper) between **2026-04-02 (2.1.91)** and the release of **2.1.197**.

```bash
# Check your installed Claude Code version
claude --version

# Check whether you route through a custom endpoint
echo "$ANTHROPIC_BASE_URL"
```

If you were on an affected version and used a custom base URL, your proxy hostname and system timezone were compared against the domain/keyword lists described above and the result was transmitted back to Anthropic on every request via the system-prompt encoding, regardless of whether you are actually based in or affiliated with the flagged region.

## If you are affected

- No credential or code-execution impact is reported — this is an **information/telemetry disclosure**, not an RCE or credential-theft vector. There is no remediation action beyond updating to a patched version.
- Update to **Claude Code ≥ 2.1.197**.
- If you operate a proxy/gateway product that sits between developers and `api.anthropic.com`, be aware that client requests may carry covert signals like this one; treat vendor-supplied CLI/agent binaries as untrusted with respect to what telemetry they may embed, not just what they document.

## Prevention

- Treat any AI-vendor CLI or agent binary as capable of embedding **undisclosed telemetry**, and don't assume a clean, documented changelog means a release has no undocumented behavioral changes — this is the same "silent patch ≠ no incident" principle this repo already tracks for security fixes, extended here to silently *added* (and silently *removed*) behavior.
- If you build or operate a proxy in front of an AI vendor's API, consider diffing system-prompt content across the same tool version and inputs to spot covert encoding channels — invisible Unicode substitutions are detectable with a straightforward character-frequency or codepoint diff.
- See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) for general guidance on treating AI developer tools as an active part of your trust boundary, not a passive dependency.

## Sources

- [Tech Startups — Anthropic's Claude Code accused of hiding proxy fingerprints inside system prompts to identify China-linked users](https://techstartups.com/2026/06/30/anthropics-claude-code-accused-of-hiding-proxy-fingerprints-inside-system-prompts-to-identify-china-linked-users/) — primary reporting; attributes the finding to researcher Adnane Khan's GitHub-hosted analysis; full Unicode-encoding mechanism; affected version range.
- [KuCoin News — Claude Code Accused of Hiding China Proxy Fingerprints in System Prompts](https://www.kucoin.com/news/flash/claude-code-accused-of-hiding-china-proxy-fingerprints-in-system-prompts) — independent corroboration of the mechanism, version range, and Anthropic's acknowledgment plus the 2.1.197 release.
- [Tech Times — Claude Code Hid Proxy Fingerprints in System Prompts: Anthropic Promises Fix](https://www.techtimes.com/articles/319415/20260701/claude-code-hid-proxy-fingerprints-system-prompts-anthropic-promises-fix.htm) — independent corroboration; timeline and Anthropic's promised fix.
- [CNBC — China warns about AI risks with Anthropic's Claude Code](https://www.cnbc.com/2026/07/08/china-anthropic-ai-claude-code-backdoor-security-threat.html) — NVDB public alert text, affected version range, "removed in 2.1.198" claim, Alibaba ban.
- [The Register — China tells devs to ditch Claude Code over 'backdoor code' fears](https://www.theregister.com/security/2026/07/08/china-ditch-older-claude-versions-with-backdoor-code/5268371) — independent corroboration of the NVDB alert and Alibaba's ban.
- [Tom's Hardware — Alibaba bans Anthropic's Claude Code after an alleged hidden China-detection backdoor is uncovered; employees told to switch to Qoder](https://www.tomshardware.com/tech-industry/artificial-intelligence/alibaba-bans-anthropics-claude-code-after-an-alleged-hidden-china-detection-backdoor-is-uncovered-employees-told-to-switch-to-qoder-as-the-rift-between-the-firms-widens) — Alibaba ban details, effective date 2026-07-10.
