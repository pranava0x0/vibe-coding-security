---
id: 2026-10-pwn2own-ireland-2026-ai-targets-codex-litellm-chroma-dynamo-zero-days
title: "Pwn2Own Ireland 2026: OpenAI Codex fell to an argument-injection bug, LiteLLM twice, NVIDIA Dynamo once and Chroma to two partial chains, all zero-days handed to the vendors with details withheld until fixes ship (2026-10-06 to 10-08)"
date_disclosed: 2026-10-06
last_updated: 2026-10-10
severity: high
status: ongoing
ecosystems: [codex, litellm, chroma, nvidia-dynamo, oracle, ai-infrastructure, coding-agents, vector-databases]
tools_affected: ["OpenAI Codex (coding agent; version not stated in the results posts)", "LiteLLM (AI gateway)", "Chroma (vector database)", "NVIDIA Dynamo (inference framework)", "Oracle Autonomous AI Database"]
tags: [zero-day, pwn2own, zdi, coding-agent, argument-injection, code-injection, ai-gateway, vector-database, inference, coordinated-disclosure, no-cve]
---

## TL;DR
At Pwn2Own Ireland 2026 (Cork, 2026-10-06 to 10-08) the Zero Day Initiative ran an AI Coding Agents category for the first time alongside its AI Infrastructure targets, and the agents and infrastructure vibe coders actually run were broken on the first day. Ikotas Labs took OpenAI Codex with what ZDI's results post calls an argument injection, for $40,000. Xint's Taisic Yun took LiteLLM with improper input validation plus code injection for $40,000, and Out of Bounds took LiteLLM again with a four-bug chain of which two were already known. Out of Bounds also took NVIDIA Dynamo on day two for $40,000. Chroma was attempted four times: VinSOC ran out of time, Team MAMMOTH landed one new bug plus two collisions, Alessandro Fanio Gonzalez landed two already-known bugs plus one collision, and one further attempt failed. Oracle Autonomous AI Database fell five times. Every winning entry is a working exploit chain against a current build that ZDI has handed to the vendor; the bug classes beyond the one-line labels, the affected versions and the fixes are not public yet, so this advisory records what was demonstrated, who holds the details, and what to do while the fixes are pending. Status `ongoing` until the ZDI advisories and vendor patches land.

## What happened
ZDI announced the AI Coding Agents category on 2026-07-21. Its rules fix the threat model this corpus already uses: a winning entry must get the agent to exploit a vulnerability by interacting with a contestant-controlled resource such as a web page, a repository or a media file, the vector must be a common coding-agent use case, and UI spoofing unrelated to permission prompts, model jailbreaks that do not cross a security boundary, and anything that needs an unsafe or permission-less mode are out of scope. In other words, the contest only pays for the shape of bug this corpus files under [Codex Heapjack/Overpatch](2026-09-codex-heapjack-overpatch-sandbox-escapes.md), [GitSpawn](2026-09-gitspawn-git-config-agent-rce-cluster.md) and [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md): untrusted content reaching code execution past the agent's own approval and sandbox controls. AI Infrastructure entries must be launched from the contestant's laptop.

The AI results, from ZDI's three daily posts (fetched 2026-10-10):

| Day | Team | Target | What ZDI printed | Payout | Points | Outcome |
|---|---|---|---|---|---|---|
| 10-06 | Ikotas Labs, Inc. | OpenAI Codex | "argument injection" | $40,000 | 4 | success |
| 10-06 | Taisic Yun, Xint | LiteLLM | "Improper Input Validation" plus code injection | $40,000 | 4 | success |
| 10-06 | HaeJung Yang and ByungYoung Yi, Out of Bounds | LiteLLM | 4 bugs, 2 previously known | $15,000 | 3 | success with collision |
| 10-06 | Nam Nguyen, Thanh Vu, Tin Huynh, VinSOC | Oracle Autonomous AI Database | 5 bugs combined | $40,000 | 4 | success |
| 10-06 | Nam Nguyen, Thai Son Dinh, Hoang Tien Minh, VinSOC | Chroma | not stated | $0 | 0 | failed (time limit) |
| 10-07 | HaeJung Yang, Out of Bounds | NVIDIA Dynamo | not stated | $40,000 | 4 | success |
| 10-07 | Taisic Yun, Xint | Oracle Autonomous AI Database | 2 zero-days plus 3 collisions | $14,000 | 3 | success with collision |
| 10-07 | Ikotas Labs, Inc. | Oracle Autonomous AI Database | 7-bug chain ending in a use-after-free and a type confusion | $10,000 | 4 | success |
| 10-07 | Team MAMMOTH | Chroma | 1 zero-day plus 2 collisions | $12,000 | 1.25 | success with collision |
| 10-07 | Alessandro Fanio Gonzalez | Chroma | 2 N-days plus 1 collision | $4,500 | 1 | success with collision |
| 10-07 | Eugene (@k3vg3n) | Chroma | not stated | none | none | failed |
| 10-08 | OtterSec (Nikolaos Mourousias, Bruno Halltari) | Oracle Autonomous AI Database | 3 collisions plus 1 zero-day | $6,250 | 2.5 | success with collision |
| 10-08 | Platform Security (Connor Laidlaw, Matthew Keeley) | Oracle Autonomous AI Database | 4 collisions plus 1 unique chain | $6,000 | 2.5 | success with collision |

A further Chroma run was on the day-three schedule; the results post records no outcome for it. ZDI named Ikotas Labs Master of Pwn after its Google Pixel 10 entry on day three. SecurityWeek's report of 2026-10-09 puts the contest total above $1.2 million across phones, printers, smart-home devices and the AI targets, and states that "affected vendors will be provided with the full details of all exploits"; neither it nor the ZDI posts state a disclosure window, so this advisory does not either.

What the labels tell a defender, and what they do not. "Argument injection" against Codex means contestant-controlled content got a string into a command the agent runs, in a configuration the rules require to be a default, approval-gated mode. That is the exact class of CVE-2026-19591 and CVE-2026-19592 (September, `apply_patch` and the trust-token leak) and of the git-config sinks in GitSpawn, and it means a fourth independent team has found a fresh one since those were fixed. "Improper input validation plus code injection" against LiteLLM is a code-execution path on the gateway that holds every provider key, in a product the [PoeLLM botnet](2026-10-poellm-canto-incognito-litellm-ollama-cryptomining-botnet.md) is already mass-exploiting through its last public RCE, and the second LiteLLM entry's "2 previously known" bugs show that chains built from already-published LiteLLM advisories still work against the contest build. Chroma, the vector store under most generated RAG apps, yielded one genuinely new bug and several collisions, which means multiple teams arrived with the same unpatched issue. Nothing beyond these labels is public, and this advisory does not guess at mechanisms.

Two-source note: ZDI's three results posts are the primary record; SecurityWeek independently carries the targets, the payout tiers and the vendor-disclosure statement. No CVE has been assigned to any AI entry as of 2026-10-10. When ZDI publishes the advisories (its published index is in `queries.md`; the most recent Codex entries there, ZDI-26-648 to ZDI-26-651, pre-date this contest), this file will carry the ids and fixed versions.

## Am I affected?
You are in scope if you run any of the five targets. Until the vendors ship fixes there is no version to check, so the question is exposure, not patch level.

```bash
# Codex: keep on the latest release; the contest build was current
codex --version; npm view @openai/codex version

# LiteLLM: a gateway on a routable address is the PoeLLM target and now has two more unpublished chains
pip index versions litellm 2>/dev/null | head -1; ss -ltnp | grep -E ':4000|:8000'

# Chroma: is the HTTP server reachable beyond localhost, and is auth configured?
ss -ltnp | grep ':8000'; env | grep -i CHROMA_SERVER_AUTH
```

## If you are affected
1. Codex: do not open untrusted repositories, pull requests or pages in an agent session with auto-approval on until OpenAI publishes the fix; the contest rules required a default, approval-gated configuration, so "I have approvals on" is not a mitigation here. Follow [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) if a session did something you did not ask for.
2. LiteLLM: take the proxy off routable interfaces, require a master key, and treat the provider keys it holds as the asset at risk ([rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) if it has been exposed).
3. Chroma and Dynamo: bind to localhost or a private network, put authentication in front, and watch the vendor release notes rather than the CVE feed, since Pwn2Own fixes often ship as a release line before any advisory.
4. Subscribe to ZDI's published-advisory index and the vendors' advisory tabs; the details arrive there first.

## Prevention
Run coding agents inside a sandbox whose boundary does not depend on the agent's own argument handling ([agent-sandboxing.md](../prevention/agent-sandboxing.md)), and keep the inference and retrieval tier off the internet with the same discipline as a database ([credential-hygiene.md](../prevention/credential-hygiene.md), [supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)).

## Sources
- [Zero Day Initiative — Pwn2Own Ireland 2026, Day One Results](https://www.zerodayinitiative.com/blog/2026/10/6/pwn2own-ireland-2026-day-one-results) (fetched 2026-10-10; the Codex argument-injection entry, both LiteLLM entries, the first Oracle entry and the failed VinSOC Chroma attempt, with payouts and points)
- [Zero Day Initiative — Pwn2Own Ireland 2026, Day Two Results](https://www.zerodayinitiative.com/blog/2026/10/7/pwn2own-ireland-2026-day-two-results) (fetched 2026-10-10; the Dynamo entry, two Oracle entries, the three Chroma attempts)
- [Zero Day Initiative — Pwn2Own Ireland 2026, Day Three Results and Master of Pwn](https://www.zerodayinitiative.com/blog/2026/10/8/pwn2own-ireland-2026-day-three-results-amp-master-of-pwn) (fetched 2026-10-10; two more Oracle entries, the unrecorded Chroma run, Ikotas Labs named Master of Pwn)
- [Zero Day Initiative — Pwn2Own Ireland 2026: New Targets and Categories](https://www.zerodayinitiative.com/blog/2026/7/21/pwn2own-ireland-2026-new-targets-and-categories) (fetched 2026-10-10; 2026-07-21; the AI Coding Agents rules: contestant-controlled resource, common use case, out-of-scope list; AI Infrastructure launched from the contestant's laptop; target names and payouts are in images the fetch could not read)
- [SecurityWeek — Google Pixel 10 Exploits Earned Hackers $560,000 at Pwn2Own](https://www.securityweek.com/google-pixel-10-exploits-earned-hackers-560000-at-pwn2own/) (fetched 2026-10-10; 2026-10-09; the five AI targets, the $40,000 tier, Chroma's $4,250 to $17,500 range, the "more than $1.2 million" total, "affected vendors will be provided with the full details of all exploits")
