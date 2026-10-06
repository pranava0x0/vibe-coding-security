---
id: 2026-10-copilot-cli-cryptographic-context-injection-secret-exfil
title: "GitHub Copilot CLI in autopilot mode: a web page carrying AES-encrypted instructions plus the key makes the agent decrypt them in its own tool environment and send local secrets (.env.prod) to the attacker in about 28 seconds — Adversa AI's 'Cryptographic Context Injection' works roughly half the time on Microsoft's mai-code-1.1-flash, which Auto model routing can assign without the user knowing, and not at all on GPT-5.6; reported 2026-09-17, GitHub's bounty triage 'validated the finding but declined to treat it as a vulnerability' on 10-01; no patch, no CVE, disclosed 2026-10-06"
date_disclosed: 2026-10-06
last_updated: 2026-10-06
severity: high
status: active
ecosystems: [ai-agents, github, copilot, cli]
tools_affected: ["GitHub Copilot CLI (autopilot / full-permission mode) with Auto model routing or mai-code-1.1-flash selected", "any coding agent that will decrypt or decode content it fetched and act on the plaintext", "developer machines whose working directory holds .env files or other secrets the agent can read"]
tags: [prompt-injection, indirect-prompt-injection, encrypted-payload, guardrail-bypass, data-exfiltration, env-file, copilot-cli, autopilot, model-routing, vendor-declined, no-patch, no-cve]
---

## TL;DR

**Adversa AI** (researcher Rony Utevsky) published on **2026-10-06**, with The Register running the story the same day, a working chain against **GitHub Copilot CLI**: a user in **autopilot mode** asks the agent to fetch a URL; the page holds **AES-encrypted instructions, the key material, and a request to decrypt**; the agent writes and runs the Python to do so. The decryption recipe asks for two candidate keys — a real one, and a "template" key built from the contents of local files such as `.env.prod`. Building the template key is what reads the secrets. The fake key fails by design, the real key succeeds, and the plaintext tells the agent to fetch a second URL whose query string carries the already-harvested values. Adversa's headline figure: **"one encrypted page makes GitHub Copilot CLI send local secrets to an attacker in 28 seconds."**

The technique is Adversa's **Cryptographic Context Injection (CCI)**: "Static guardrails read text; they do not run it … CCI ships malicious instructions as strong ciphertext, along with the key material and an instruction to decrypt." A classifier scanning the fetched page sees random bytes; the instructions only exist inside the agent's sandbox after it has done the work.

**Model-dependent.** On paid accounts with **Auto model routing**, the chain executed end-to-end in **about 50% of runs when the router picked Microsoft's `mai-code-1.1-flash`**; **GPT-5.6 models refused the identical payload consistently**. The user does not choose, and is not told, which model Auto assigned.

**Vendor position.** Reported through GitHub's bug bounty on **2026-09-17**. On **2026-10-01** GitHub "validated the finding but declined to treat it as a vulnerability," on the grounds that the user "explicitly asked Copilot CLI to fetch attacker-controlled content while giving copilot full permissions"; GitHub told The Register the scenario "requires a user to intentionally direct Copilot CLI to fetch attacker-controlled or untrusted content," noted possible future functionality changes with nothing to announce, and ruled the report ineligible. **No patch, no CVE.** `status: active` because the chain still reproduced at disclosure and the vendor does not intend to change it.

## What happened

**Why this is different from the prompt-injection PoCs already in this repo.** The usual indirect-injection story is plaintext instructions hidden in a page, a README or an issue. CCI removes the plaintext entirely. The agent is not tricked into *reading* instructions; it is given a legitimate-looking task — "decrypt this" — whose *execution* produces the instructions, and whose *setup* (constructing a key from local files) is the exfiltration. Any content filter on the fetched page, any guardrail model on the context window, and any human skimming the transcript sees a Python decryption helper and some base64. The vendor's "the user asked for it" framing is accurate about the first step and silent about every step after it.

**The autopilot precondition is real, and it is the default people use.** Autopilot (full permissions, no per-tool confirmation) is what makes a web fetch flow into file reads and an outbound request without a prompt. In confirmation mode the user would see the outbound fetch to a new destination and could stop it — but would also see a plausible "fetching the decryption dependency" and likely approve it, which is the pattern the [TrustFall](2026-05-trustfall-mcp-auto-execute.md) and [GhostApproval-class](2026-09-gitspawn-git-config-agent-rce-cluster.md) entries here describe.

**The model-routing precondition is the new part.** Adversa frames the 50% as a property of one model that the platform can assign silently: "the vulnerable model could be auto-assigned without user awareness on accounts with Auto routing enabled." For a defender that means the security properties of a coding agent session change from run to run, and the thing that changed is not in the agent's version number or the user's configuration.

**Adversa's recommended controls** (from the post): capture a per-session trace of every tool call "with its arguments fully resolved"; alert on action sequences (read-secret → outbound-request) rather than payload content; gate "irreversible and outbound actions" behind confirmation for new network destinations; "quarantine untrusted content in a context with no tools and no credentials"; and make model routing and tool-output provenance "a procurement question."

## Am I affected?

- You use **Copilot CLI** with autopilot / `--allow-all`-style full permissions **and** ask it to fetch or summarise URLs, or run it on tasks where it chooses to fetch (documentation lookups, dependency READMEs, issue links).
- You are on **Auto model routing** or have selected `mai-code-1.1-flash`. GPT-5.6 refused in Adversa's tests; that is a measurement, not a guarantee, and routing can change.
- The working directory, home directory or environment holds secrets the agent can read — `.env*`, cloud credential files, tokens in shell history.

```bash
# Secrets the agent can reach from a typical project directory
ls -la .env* .env.prod .env.local 2>/dev/null; ls ~/.aws ~/.config/gh 2>/dev/null
# Copilot CLI session logs/transcripts, if retained, for outbound fetches that followed a file read
grep -rn "python\|decrypt\|AES\|GCM" ~/.copilot 2>/dev/null | head
```

## If you are affected

1. **Turn autopilot off for any session that will touch the network**, and treat "fetch this URL" as the moment the session becomes untrusted — the same rule this repo gives for MCP tools that return web content.
2. **Pin a model** rather than Auto where the CLI allows it, and prefer one that refused in the published test; re-test when either the CLI or the routing changes.
3. **Move secrets out of the agent's reach**: no `.env.prod` on a developer machine, cloud credentials via short-lived SSO sessions rather than files, and a per-project allow-list of what the agent may read — [prevention/credential-hygiene.md](../prevention/credential-hygiene.md), [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
4. If an autopilot session fetched an untrusted page and you cannot reconstruct what it did afterwards, **rotate what was in reach** — [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — and run [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).
5. **Egress-filter the agent's host.** The exfiltration is a plain HTTPS request to a new domain; a proxy allow-list or an alert on first-seen destinations from the agent process is the control that would have fired here.

## Prevention

- Content a model *computes* is as untrusted as content it *reads*; decrypting, decoding, decompressing or executing fetched material inside a tool-enabled context is a trust-boundary crossing, and the only durable defence is that the context doing it holds no secrets and no outbound tools — [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) applies to built-in fetch tools too.
- Ask vendors which model served a session and log it; a safety property that varies with silent routing is one you cannot reason about otherwise.
- "The user asked for it" is now the stated triage position of at least one major vendor for autopilot-mode injection; plan on the assumption that this class is not getting patched and must be contained operationally.

## Why this matters for vibe coders

Autopilot mode exists because people want to say "read these docs and implement it" and walk away. This chain is one page in those docs. The agent did nothing a reviewer would call an exploit — it wrote a decryption helper, it read a config file to fill in a template, it fetched a URL — and the `.env.prod` left the machine before the coffee was ready. The vendor says that is working as intended; the fix is therefore on your side: no secrets where the agent works, no full autonomy when it reads the web, and a log of what it actually ran.

## Sources

- [Adversa AI — GitHub Copilot CLI vulnerability: Cryptographic Context Injection steals developer secrets](https://adversa.ai/blog/cryptographic-context-injection-github-copilot/) — 2026-10-06, the primary: the two-key decryption recipe, `.env.prod` as the exfiltrated file, "28 seconds," the ~50% rate on `mai-code-1.1-flash` and the GPT-5.6 refusals, the Auto-routing observation, the timeline (reported 09-17, declined 10-01), GitHub's triage wording, the five recommended controls, no CVE. Fetched 2026-10-06.
- [The Register — Zombie instructions on carefully constructed web pages could trick GitHub Copilot CLI into sharing secrets](https://www.theregister.com/ai-and-ml/2026/10/06/zombie-instructions-on-carefully-constructed-web-pages-could-trick-github-copilot-cli-into-sharing-secrets/5301206) — 2026-10-06: independent write-up with GitHub's spokesperson statement ("requires a user to intentionally direct Copilot CLI to fetch attacker-controlled or untrusted content"), the researcher quote on static guardrails, the model split. Fetched 2026-10-06.
- [Adversa AI — blog index](https://adversa.ai/blog/) — fetched 2026-10-06 to locate the post; also lists the firm's 09-23 "Top 10 attacks on Claude Code" roundup (not opened this sweep).
- Related in this repo: [Claude Code InversePrompt](2025-08-claude-code-inverseprompt.md), [TrustFall MCP auto-execute](2026-05-trustfall-mcp-auto-execute.md), [Azure DevOps MCP PR injection (Copilot)](2026-07-azure-devops-mcp-pr-injection.md), [RoguePilot Codespaces token leak](2026-02-roguepilot-codespaces-copilot-token-leak.md), [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md).
