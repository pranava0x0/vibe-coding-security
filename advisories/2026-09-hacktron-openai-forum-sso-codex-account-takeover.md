---
id: 2026-09-hacktron-openai-forum-sso-codex-account-takeover
title: "Hacktron reached OpenAI's internal monorepo through the community forum: a Claude-built exploit for an un-CVE'd libheif bug in Discourse's HEIC upload path, then an over-permissioned \"Sign in with OpenAI\" token that turned a forum session into full ChatGPT and Codex API access — a PR was opened in the internal repo via an employee's GitHub-connected Codex"
date_disclosed: 2026-09-18
last_updated: 2026-09-20
severity: high
status: patched
ecosystems: [openai, codex, discourse, libheif, imagemagick, sso, github]
tools_affected: ["OpenAI Codex (cloud, GitHub-connected) and ChatGPT accounts reachable via OpenAI SSO", "community.openai.com (Discourse)", "Discourse < 2026.7.0 / 2026.6.1 / 2026.5.2 / 2026.1.6 (CVE-2026-32882)", "any service that trusts OpenAI SSO session tokens", "Debian 12 libheif 1.19.7"]
tags: [account-takeover, sso, oauth-scope, coding-agent, ai-built-exploit, libheif, image-parsing, discourse, bug-bounty, memory-corruption]
---

## TL;DR
Hacktron (Harsh Jaiswal, Mohan Pedhapati, Rahul Maini) published on 2026-09-18 how, in under 72 hours in late July, they went from `community.openai.com` to a pull request in OpenAI's internal monorepo. Step one: Discourse validated images with FastImage, which does not understand **HEIC/HEIF**, so those uploads fell through to ImageMagick and **libheif 1.19.7** as shipped by Debian 12 — a build missing an upstream heap-overflow fix that "received no CVE" and was never backported. They had **Claude Opus 4.8 and then Opus 5** (hours after its 2026-07-24 release) write the exploit; RCE on OpenAI's production forum landed on 2026-07-25. Step two: OpenAI's **"Sign in with OpenAI"** forum tokens "carried excessive permissions, granting full API access to associated ChatGPT and Codex accounts," so a compromised forum session became a **no-interaction takeover of any active member's ChatGPT and Codex** — and an employee's GitHub-connected Codex was prompted to open PR #1186742 in the internal monorepo before testing stopped. OpenAI "narrowed the permissions on Community sign-in tokens," revoked affected tokens, confirmed the fix ~14 hours after the report and paid **$6,500**; Discourse shipped **CVE-2026-32882** (GHSA-vhm9-85gw-x335, CVSS 8.8, 2026-07-28) with image-processing sandboxing. The lesson for anyone wiring a coding agent to their repos through SSO: the agent's account is only as strong as the weakest app that can mint a session for it.

## What happened

**The chain (Hacktron's nine boxes):** libheif → Debian (missing backport) → ImageMagick → Discourse upload → community.openai.com → OpenAI SSO → ChatGPT/Codex → GitHub connector → internal repos.

**1. An un-CVE'd bug in a forum's image path.** Discourse's upload pipeline normally checks images with FastImage; because FastImage did not support HEIF, HEIC/HEIF files went straight to ImageMagick's `magick`, exposing libheif's parser to attacker-controlled bytes. The installed Debian package (libheif 1.19.7) lacked an upstream fix for a heap-buffer overflow that gave out-of-bounds read and write during HEIC decoding — fixed upstream a year earlier without ever being labelled a security fix, hence no CVE and no distro backport. This is the same library family behind [Next.js's August critical](2026-07-nextjs-july-security-release.md) (AVIF via `sharp`), and the same "fixed upstream, never flagged" shape.

**2. The exploit was model-written.** Per Hacktron: Opus 4.8 "identified libheif security issues" on 2026-07-24 but struggled to produce a reliable exploit under ASLR; when Opus 5 shipped that evening, it produced a working ARM64 exploit for local testing within hours, then a port to x86-64 with jemalloc matching Discourse's build. Local RCE through an image upload was confirmed by 06:00 UTC on 2026-07-25; the team then ran Claude "in an autonomous goal-loop" against their own Discourse instance (RCE by 10:00) and replicated it on OpenAI's production forum. This repo does not reproduce exploit detail; the point is that a year-old, un-CVE'd memory bug in a common image library was weaponised by a frontier model in a working day — see the [Anthropic cyber-eval](2026-07-anthropic-claude-cyber-eval-breaches.md) and [OpenAI Astra](2026-08-openai-astra-critical-cyber-threshold.md) entries for the capability context.

**3. The SSO token did too much.** With code execution on the forum, Hacktron found that forum accounts signed in "with OpenAI" via `auth.openai.com` held tokens whose scope reached the user's **ChatGPT and Codex API** — "a compromised forum session became a no-interaction takeover" of those accounts, "which could then access internal OpenAI repositories, and potentially many other connectors" (GitHub, Slack, email). They took over an employee account whose Codex was connected to OpenAI's GitHub organisation and sent that Codex instance a prompt to open a PR in the internal monorepo; the redacted screenshot shows PR **#1186742** created. Testing stopped there, "without accessing sensitive code." Hacktron's framing: the forum was one path, but "any first-party or third-party OpenAI service using the OpenAI SSO" would have created the same risk.

**Timeline (Hacktron):** 2026-07-23 pipeline review → 07-24 exploit development → 07-25 local RCE 05:00–06:00 UTC, remote RCE 08:00–10:00, production RCE ~10:00, account takeover and PoC PR 13:30–15:30, **OpenAI fix confirmed 22:49:45 UTC** (~14 h after report) → 07-25 Discourse report via HackerOne → 07-27 Discourse fix with image-processing sandboxing → **07-28 GHSA-vhm9-85gw-x335** → 09-01 OpenAI bounty ($6,500, "recognizes the OpenAI-side finding, not the actions against Discourse," which its programme excludes) → 09-18 public write-up.

**Discourse's fix.** CVE-2026-32882, "RCE via malformed HEIF file," High / CVSS 8.8, exploitable by a low-privilege user with no further interaction; patched **2026.7.0, 2026.6.1, 2026.5.2, 2026.1.6**; self-hosters must `./launcher rebuild app` so the container picks up patched libheif, and recent cores sandbox image processing. Credit: hacktronai-research.

**OpenAI's fix.** "We narrowed the permissions on Community sign-in tokens"; affected tokens and sessions revoked. No OpenAI blog post; the statement is quoted by SecurityWeek. Status here is **`patched`** on both sides on the vendors' word, with the caveat that the scope bug was in an identity layer and OpenAI has not described the other SSO relying parties.

## Am I affected?

- **Self-hosted Discourse:** version below the patched lines above, or a container not rebuilt since 2026-07-28 → rebuild now; check `magick -version` for `heic` in the delegate list and the libheif version it links.
- **You run a coding agent connected to your source control through an SSO/OAuth identity:** ask what other applications can mint or reuse that identity's session, and whether the token issued to a low-value app (a forum, a docs site, a support portal) carries the agent's scopes. That is the bug that mattered here.

```bash
# Discourse self-hosters
cd /var/discourse && ./launcher enter app -- dpkg -l | grep -i libheif
# Codex / ChatGPT users on the OpenAI forum: review active sessions and connected apps at platform.openai.com and chatgpt.com settings; revoke anything unfamiliar.
```

## If you are affected

- Discourse admins: patch and rebuild; treat the container as compromised if HEIC uploads were accepted from untrusted users on a vulnerable build — [`playbooks/if-your-webapp-was-compromised.md`](../playbooks/if-your-webapp-was-compromised.md).
- Codex users whose accounts were reachable through the forum SSO in July: OpenAI says it revoked affected tokens; review your GitHub connector's audit log for agent-authored PRs you did not request, and rotate the GitHub credentials the connector holds — [`playbooks/if-your-github-pat-leaked.md`](../playbooks/if-your-github-pat-leaked.md).

## Prevention

- Scope SSO tokens per relying party; a forum login must not be exchangeable for a coding agent's API access. [`prevention/credential-hygiene.md`](../prevention/credential-hygiene.md).
- Sandbox image decoding (ImageMagick delegates, `sharp`/libvips, libheif) and pin distro packages to a release that actually carries upstream security fixes — the AVIF/HEIF family has now produced Next.js, Astro and Discourse criticals in two months. [`prevention/supply-chain-attack-surface.md`](../prevention/supply-chain-attack-surface.md).
- Agent-connected repositories need branch protection and required review even for "your own" agent's PRs. [`prevention/ci-cd-hardening.md`](../prevention/ci-cd-hardening.md).

## Update 2026-09-19 — three more outlets, one new OpenAI statement, no comment from Anthropic

The Register (09-18), SecurityWeek (09-18) and The Hacker News (09-19) each wrote up Hacktron's post. The one materially new fact is OpenAI's framing of the bounty to The Register: "testing against the Discourse-hosted community.openai.com was explicitly excluded from our bug bounty program. The award recognizes the OpenAI-side finding" — i.e. the $6,500 (paid 2026-09-01, per THN) is for the over-scoped SSO token, not the forum RCE, which OpenAI treats as Discourse's issue. SecurityWeek adds that OpenAI's own review "found limited metadata reads and the researcher-submitted pull request," and that Discourse's patch was ready within two days. THN quotes Hacktron's caveat that "skilled human direction still mattered, and this was not automated hacking with no one at the controls." Neither OpenAI nor Anthropic answered The Register's further questions. No change to status or affected products; the SSO fix and the Discourse release line above stand.

## Sources
- [Hacktron — Hacking OpenAI](https://www.hacktron.ai/blog/hacking-openai) — primary; the nine-step chain, libheif 1.19.7 / Debian 12, Opus 4.8 → Opus 5 exploit development, the SSO scope finding, PR #1186742, the full timeline and bounty note. Fetched 2026-09-18.
- [The Register — Researchers used Claude to hack OpenAI employees' ChatGPT accounts](https://www.theregister.com/security/2026/09/18/researchers-used-claude-to-hack-openai-employees-chatgpt-accounts/5297517) — 2026-09-18; OpenAI's "explicitly excluded from our bug bounty program… recognizes the OpenAI-side finding" statement; the 72-hour / ~14-hour timeline; no further comment from OpenAI or Anthropic. Fetched 2026-09-20.
- [The Hacker News — Claude Opus 5 Helped Researchers Take Over OpenAI Staff Accounts via Chained Flaws](https://thehackernews.com/2026/09/claude-opus-5-helped-researchers-take.html) — 2026-09-19; CVE-2026-32882 / libheif 1.22.0 context, the 2026-09-01 bounty payment date, Hacktron's "skilled human direction still mattered" quote. Fetched 2026-09-20.
- [SecurityWeek — AI-Built Exploit and Sign-In Flaw Opened Path to Internal OpenAI Code](https://www.securityweek.com/ai-built-exploit-and-sign-in-flaw-opened-path-to-internal-openai-code/) — 2026-09-18; OpenAI's "narrowed the permissions on Community sign-in tokens" statement, the ~14-hour fix, the $6,500 bounty. Fetched 2026-09-18.
- [Discourse — GHSA-vhm9-85gw-x335: RCE via malformed HEIF file (CVE-2026-32882)](https://github.com/discourse/discourse/security/advisories/GHSA-vhm9-85gw-x335) — 2026-07-28, CVSS 8.8, patched versions, rebuild guidance, credit. Fetched 2026-09-18 (the `github.com/advisories/` mirror URL returned 404; the vendor-repo URL resolves).
