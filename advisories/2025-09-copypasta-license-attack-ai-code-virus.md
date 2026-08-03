---
id: 2025-09-copypasta-license-attack-ai-code-virus
title: "CopyPasta License Attack — self-replicating prompt injection in LICENSE.txt/README.md across Cursor, Windsurf, Kiro, Aider (Sept 2025)"
date_disclosed: 2025-09-04
last_updated: 2026-08-03
severity: high
status: active
ecosystems: [cursor, windsurf, kiro, aider]
tools_affected: [cursor, windsurf, kiro, aider]
tags: [prompt-injection, self-propagating, license-file, readme, markdown-comment, ai-worm, indirect-prompt-injection]
---

## TL;DR
HiddenLayer researcher Kenneth Yeung disclosed **CopyPasta**, a proof-of-concept prompt-injection "virus" hidden in invisible markdown comments inside a repo's **`LICENSE.txt`**/**`README.md`**. Because AI coding assistants are tuned to treat license text as authoritative, the agent obeys the hidden instruction and **copies the payload into every new or edited file it generates** — so each file the assistant touches becomes a fresh carrier. Demonstrated against **Cursor** (Coinbase's primary coding tool at the time), **Windsurf**, **Kiro**, and **Aider**; no CVE, no vendor patch, and the class remains open.

## What happened
Yeung's research (published 2025-09-04) builds on the "self-replicating prompt injection" idea (an evolution of theoretical worms like Morris II) but targets **code-generation systems whose output is far more likely to actually execute** than a chatbot's chat log. The payload sits in an HTML/markdown comment inside `LICENSE.txt` or `README.md` — invisible when rendered, plain text to the model. When a developer asks the assistant to work on the repo (even something routine like "update the docs" or "add a feature"), the agent reads the license file as part of its context, treats the hidden instruction as a legitimate licensing requirement it must honor, and **re-inserts the same hidden comment plus an attacker-chosen payload into whatever file it writes next**. Demonstrated payloads included arbitrary code insertion and outbound HTTP calls; the researcher notes the same mechanism generalizes to backdoors, data exfiltration, or sabotage.

Because propagation piggybacks on the developer's own normal workflow (not a dependency install, not a build step), it evades the controls this repo already tracks for `.cursorrules`/`CLAUDE.md` write-target poisoning ([TrapDoor](2026-05-trapdoor-cross-ecosystem-stealer.md)) and for MCP/config auto-execution — there is no install hook or config file to diff, only ordinary generated source and doc files. HiddenLayer specifically flagged **Cursor** (reported as "every Coinbase engineer's" preferred tool at the time, per Coinbase's own engineering commentary) as the primary demonstration target, with **Windsurf, Kiro, and Aider** confirmed independently vulnerable to the same technique — indicating the root cause (treating license/README text as an authoritative, propagation-worthy instruction) is common across unrelated agent implementations rather than a single vendor's bug.

At disclosure this was lab-only proof-of-concept with no confirmed in-the-wild infection, and no vendor has published a patch or a CVE for it — Yeung's own recommended mitigations are process-level (runtime indirect-prompt-injection defenses, mandatory human review of every AI-generated file change) rather than a vendor fix, so the underlying weakness should be assumed to still be present in current tool versions unless a specific vendor states otherwise.

## Am I affected?
```bash
# Look for hidden/invisible-comment instructions in the files most agents treat as authoritative
for f in LICENSE LICENSE.txt LICENSE.md README.md; do
  [ -f "$f" ] && grep -nE '<!--.*(license|must|required|instruction|copy this).*-->' "$f" -i \
    && echo "  ^ suspicious hidden comment in $f — inspect manually"
done

# Same invisible-Unicode check this repo already recommends for .cursorrules/CLAUDE.md
for f in LICENSE LICENSE.txt LICENSE.md README.md; do
  [ -f "$f" ] && grep -nP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2060}-\x{206F}\x{FEFF}]' "$f" \
    && echo "  ^ invisible Unicode in $f — inspect manually"
done
```
If your project's LICENSE/README came from a template repo, a contributor's fork, or any source you didn't author from scratch, and you use Cursor, Windsurf, Kiro, or Aider against it, treat every file the assistant has since generated or edited as a possible carrier — check newly-added files for the same hidden-comment pattern, not just the original LICENSE/README.

## If you are affected
1. Diff `LICENSE`/`README.md` against a known-good upstream or the original template; remove any hidden comment content.
2. Grep every AI-generated file in the repo for the same comment signature/payload before treating them as clean.
3. Rotate any credentials or tokens the payload's HTTP calls could have reached, per the standard post-compromise playbook.

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — don't let an agent auto-run on unreviewed repos/templates.
- Treat `LICENSE`/`LICENSE.txt`/`README.md` the same as `.cursorrules`/`CLAUDE.md`/`AGENTS.md`: version-controlled, diffed on every change, and grepped for invisible Unicode or suspicious HTML comments before letting an agent process them.
- Require human review of every AI-generated file diff rather than auto-accepting — this is the one mitigation HiddenLayer itself recommends, since no vendor patch closes the underlying "agent treats license text as authoritative" behavior.

## Sources
- [HiddenLayer — CopyPasta: The First Practical Prompt Injection Virus for AI Code Assistants](https://www.hiddenlayer.com/research/prompts-gone-viral-practical-code-assistant-ai-viruses) — primary research, technique, affected-tools list (Cursor, Windsurf, Kiro, Aider), mitigation recommendations.
- [Decrypt — 'CopyPasta' Attack Shows How Prompt Injections Could Infect AI at Scale](https://decrypt.co/338143/copypasta-attack-shows-prompt-injections-infect-ai-scale) — independent corroboration, researcher quotes, lab-only-PoC status.
- [CoinDesk — Coinbase's Go-To AI Coding Tool Found Vulnerable to 'CopyPasta' Exploit](https://www.coindesk.com/tech/2025/09/06/coinbase-s-go-to-ai-coding-tool-found-vulnerable-to-copypasta-exploit) — Cursor/Coinbase angle, propagation mechanism.
