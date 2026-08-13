---
id: 2026-08-reasoning-trace-replay-credential-leak
title: "Encrypted reasoning-trace replay across OpenAI, Anthropic, Google APIs leaks credentials from public agent transcripts (research, unconfirmed)"
date_disclosed: 2026-08-10
last_updated: 2026-08-13
severity: medium
status: unconfirmed
ecosystems: [openai-api, anthropic-api, google-ai-studio, agent-transcripts]
tools_affected: [openai-api, anthropic-api, google-gemini-api, claude-code, codex, any-agent-that-posts-transcripts-publicly]
tags: [prompt-injection, credential-theft, research, reasoning-traces, chain-of-thought, api-security]
---

## TL;DR
Researchers found that the encrypted "reasoning"/chain-of-thought blocks returned by OpenAI, Anthropic, and Google's APIs are interchangeable across sessions, users, and (for OpenAI) models — so anyone with an API account on the same provider can get a model to decrypt and echo back a reasoning block captured from someone else's session. Scanning 315,320 reasoning blocks pulled from public repositories, the researchers recovered 182 credentials and 367 PII artifacts believed hidden inside blocks that developers assumed were opaque. No CVE has been assigned and no vendor has publicly confirmed the finding; treat as `unconfirmed` pending vendor acknowledgment or independent replication.

## What happened
On 2026-08-10, a research team (Alexander Panfilov, David Schmotz, Ilia Shumailov, Luca Beurer-Kellner, Joachim Schaeffer, Ameya Prabhu, Jonas Geiping, Maksym Andriushchenko — affiliated with the ELLIS Institute Tübingen and MPI-IS) posted "Stealing Reasoning Traces from Proprietary LLM APIs" to arXiv ([arXiv:2608.09867](https://arxiv.org/abs/2608.09867)). The paper describes replaying encrypted chain-of-thought/reasoning blocks — the opaque tokens OpenAI, Anthropic, and Google APIs return alongside a model's visible output, meant to let a client display "thinking" without exposing the provider's raw reasoning — across sessions, accounts, and (for OpenAI specifically) between different models from the same provider. Feeding a stronger model's captured reasoning block to a weaker, less-safeguarded model from the same vendor forced the weaker model to decode and output the plaintext reasoning it was never supposed to be able to read.

The practical risk for vibe coders: developers regularly paste full AI-agent session transcripts — including these "opaque" reasoning blocks — into GitHub issues, gists, forum posts, and bug reports when asking for debugging help, without realizing the block itself might still carry recoverable content. The researchers scanned **315,320 reasoning blocks harvested from public repositories** and recovered **182 credentials** (62 API keys, 33 passwords, 24 access tokens, 7 private keys, per the paper) and **367 PII items**. A developer who scrubbed their visible transcript of secrets before posting could still be exposing them via the reasoning block, because the block itself — not just the model's visible answer — can carry forward context the model reasoned over, including secrets that appeared earlier in its own context window.

This generalizes a related, earlier warning: cryptographer Matthew Green reported similar replay behavior in encrypted reasoning blocks to OpenAI and Anthropic via bug bounty on 2026-05-29, and that report was reportedly initially disputed by at least one vendor. The new arXiv paper is the first to demonstrate concrete credential/PII recovery at scale from real, already-public data rather than a lab-only proof of concept.

**Vendor response:** as of publication (and as of this repo's last check on 2026-08-13), none of OpenAI, Anthropic, or Google has publicly acknowledged this specific research or tied it to documentation changes. The researchers state the specific attacks they demonstrated stopped working as of August 2026, which they interpret as a silent mitigation — but this is the researchers' own reproducibility observation, not a vendor confirmation, and it does not address whether reasoning blocks already posted publicly (before any mitigation) remain replayable.

**Why `status: unconfirmed`:** this advisory rests on a single primary source — the arXiv preprint itself. The Hacker News' 2026-08-12 coverage summarizes the same paper without independent verification or new reporting (no second research group, no vendor statement), so it does not count as an independent second source under this repo's accuracy bar. No CVE/GHSA has been assigned by any vendor.

## Am I affected?
This is hard to self-check directly — you cannot inspect the contents of an encrypted reasoning block. Instead, assess exposure:

- Have you (or your team) ever pasted a full AI-agent session transcript — including any "thinking" / "reasoning" panel content shown by Claude Code, Codex, Cursor, or a similar tool — into a public GitHub issue, gist, forum post, Stack Overflow question, or bug report?
- Did that session touch any secrets (API keys, passwords, tokens, private keys) at any point, even if you redacted them from the *visible* transcript before posting?
- If yes to both, treat any secret that was live in that session's context as potentially exposed, regardless of whether it appeared in the visible/human-readable part of what you posted.

```bash
# Find transcripts you may have posted publicly that could carry an exposed reasoning block
grep -ril "reasoning" ~/Downloads ~/Desktop 2>/dev/null | xargs grep -l "sk-\|ghp_\|AKIA" 2>/dev/null
```

## If you are affected
1. Treat this the same as any other suspected credential exposure: rotate every secret that was live in context during a session whose transcript you posted publicly.
2. Delete or edit the public post to remove the full transcript (including any reasoning/thinking block), not just the visible text — most platforms don't purge history/cached copies, so also assume search-engine caches and any archive.org snapshot may retain it.
3. Going forward, do not paste full agent session transcripts (including "show thinking" panels) into public issues/gists when asking for help — summarize the problem and redact or omit the transcript, or share it privately with a maintainer instead.

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — never let a secret enter an AI agent's context in the first place (use env vars/secret managers the agent doesn't echo, not hardcoded values it might reason over and later leak).
→ Avoid posting full "show reasoning" / "show thinking" transcripts publicly. If a debugging transcript needs to be public, share only the final visible exchange, not the full session export.

## Sources
- [arXiv — Stealing Reasoning Traces from Proprietary LLM APIs (arXiv:2608.09867)](https://arxiv.org/abs/2608.09867) — primary research source; submitted 2026-08-10.
- [The Hacker News — OpenAI, Anthropic, Google API Flaw Let Researchers Steal Reasoning Traces](https://thehackernews.com/2026/08/openai-anthropic-google-api-flaw-let.html) — 2026-08-12 summary coverage; no independent verification beyond the paper, cited for context and vendor-response framing only.
