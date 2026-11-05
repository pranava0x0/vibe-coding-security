---
id: 2026-11-haiou-codex-jailbreak-bundle-prompt-adware-remove-and-audit-agents-md
title: "Haiou Codex jailbreak bundle (GitHub haiou-666/haiou-codex, bundled in Codex-X): remove it and audit Codex global instruction files"
kind: malicious-artifact
date_disclosed: 2026-11-03
last_updated: 2026-11-05
severity: medium
status: unconfirmed
ecosystems: [github, codex, agent-config, agents-md, skills]
tools_affected: ["OpenAI Codex CLI and Codex desktop installations that applied the Haiou (海鸥) configuration pack", "Codex-X, the Chinese-language Codex GUI configuration tool that bundles the Haiou template offline", "the pack's Claude Code variant, which Check Point says carries no ad injection on GitHub"]
tags: [malicious-config, prompt-adware, agents-md, codex, jailbreak-bundle, third-party-skills, llm-gateway, check-point, single-firm, unconfirmed]
---

## TL;DR
Remove the Haiou (海鸥) "local enhancement configuration pack" for Codex, the six skills it installs, and the Codex-X bundled template, then restore Codex's global instruction files from a copy you wrote. If Codex traffic was ever routed to the LLM gateway the pack advertises, rotate the provider API key you gave it.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| GitHub | `haiou-666/haiou-codex` (archive `海鸥codeX版-开源一键包.tar.lzma`) | the pack Check Point analysed (it names version 4.5.0); no version is known clean | remove; Check Point says the pack's own uninstaller reverts its changes | repository live, 404 stars, 79 forks, 4 commits, first published 2026-07-10 per The Hacker News (2026-11-05) | none: not a registry package, no GHSA, no OSV record |
| GitHub | `yynxxxxx/Codex-X` | releases whose template table bundles "海鸥3.0破甲" offline (README, read 2026-11-05) | remove the template, or the tool | repository live, 4.4k stars, 560 forks (2026-11-05) | none |
| GitHub | the pack's Claude Code variant | Check Point found no ad injection in the GitHub copy; a `CLAUDE.md` inside the Codex pack carries the ad text | remove with the pack | not opened this run | none |

The status is `unconfirmed` because Check Point Research is the only firm to have analysed the pack; The Hacker News reports the same analysis. The pack is a configuration bundle, so no malware record will exist for it.

## Am I affected?

1. Did you, or a setup script, apply the Haiou pack or install Codex-X and select its 海鸥 template? Codex-X's README lists the template as bundled for offline use and refreshed from GitHub.
2. Read Codex's global instruction files in full. Codex reads `~/.codex/AGENTS.md` for user-level instructions and `~/.codex/config.toml` for providers and base URLs; the pack also writes project-level `AGENTS.md` files and skills. Anything that tells the agent to respond to greetings or trigger words with a recommendation, a URL or a product name is the shape Check Point describes.
   ```bash
   ls -la ~/.codex/ ~/.codex/skills/ 2>/dev/null
   grep -n -i "gateway\|base_url\|api.example\|推荐\|网关" ~/.codex/AGENTS.md ~/.codex/config.toml 2>/dev/null
   ```
3. Check `config.toml` for a model provider or base URL you did not configure. Check Point's concern is the unknown operator of the advertised OpenAI-compatible gateway, not only the ads.
4. Check Point describes the prompt content as packaged in encrypted blobs with signature checks, so a scanner that reads the archive will not show you the text; read the files the pack wrote on disk instead.

## If you are affected

- Remove the pack and its six skills; if you use the pack's uninstaller, verify afterwards that `~/.codex/AGENTS.md`, `~/.codex/config.toml` and any project `AGENTS.md` match copies you wrote.
- If `config.toml` pointed at the advertised gateway or you created an account there, rotate the provider API key you supplied and review that provider's usage since the change. Follow [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md) for the key rotation steps.
- Treat the pack's "security research" skills as untrusted code: delete them rather than keep them disabled.

## Prevention

- An agent's instruction file is executable configuration. Vet third-party `AGENTS.md`, `CLAUDE.md`, skills and "enhancement packs" the way you vet a dependency: [package vetting checklist](../prevention/package-vetting-checklist.md).
- Keep provider base URLs in your own hands; a configuration pack that changes them is the same class as the [unauthorized Codex and Claude Code relays](2026-10-unauthorized-codex-claude-code-relays-rewrite-cli-config-disable-sandbox-symantec.md).
- Instruction files that arrive encrypted or signed against your inspection are a reason to refuse them, not a reassurance. See [supply-chain attack surface](../prevention/supply-chain-attack-surface.md).

## Sources
- [Check Point Research — Free the Model, Sell the Gateway: Prompt Adware Hidden in Jailbreak Bundles](https://research.checkpoint.com/2026/free-the-model-sell-the-gateway-prompt-adware-hidden-in-jailbreak-bundles/) — fetched 2026-11-05 (2026-11-03): the pack (version 4.5.0), the six skills, the global-instruction-file writes, the encrypted packaging, the uninstaller, the Claude Code variant finding, the Codex-X bundling, the gateway-risk warning, the Bilibili and QQ promotion, the 250-plus stars at analysis time. Single firm.
- [The Hacker News — Researchers Uncover Prompt Adware Hidden in OpenAI Codex Jailbreak Toolkit](https://thehackernews.com/2026/11/researchers-uncover-prompt-adware.html) — fetched 2026-11-05 (2026-11-04, Ravie Lakshmanan): the repository's 2026-07-10 first availability, 403 stars and 77 forks at writing, the Check Point quotes. Outlet pickup of the same analysis.
- [GitHub — haiou-666/haiou-codex](https://github.com/haiou-666/haiou-codex) — fetched 2026-11-05: the description ("a local enhancement configuration pack for Codex"), 404 stars, 79 forks, 4 commits, the archive as the only file beside the README.
- [GitHub — yynxxxxx/Codex-X](https://github.com/yynxxxxx/Codex-X) — fetched 2026-11-05: the description, 4.4k stars, 560 forks, the template table row naming 海鸥3.0破甲 as bundled offline.
- Not opened: the HiddenLayer technique reference The Hacker News links, the pack's Bilibili video and QQ group, the Claude Code variant's repository.
- Related in this corpus: [unauthorized Codex and Claude Code relays](2026-10-unauthorized-codex-claude-code-relays-rewrite-cli-config-disable-sandbox-symantec.md), [AGENTS.md in the Downloads folder](2026-10-agents-md-in-downloads-folder-hijacks-coding-agents-started-there-function-color-npm.md), [ClawHavoc ClawHub skills](2026-02-clawhavoc-clawhub-skills.md).
