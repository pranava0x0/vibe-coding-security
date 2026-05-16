---
id: 2025-08-nx-s1ngularity
title: "Nx 's1ngularity' — first AI-CLI-assisted malware (August 2025)"
date_disclosed: 2025-08-26
last_updated: 2026-05-16
severity: critical
status: contained
ecosystems: [npm]
tools_affected: [any-nx-project, claude-code, gemini-cli]
tags: [supply-chain, credential-theft, npm, ai-assisted-malware, postinstall, github-actions]
---

## TL;DR
On 2025-08-26, malicious versions of Nx and several plugins were published to npm after attackers exploited a GitHub Actions injection bug to steal the publish token. The postinstall script **invoked locally-installed Claude Code and Gemini CLI as recon tools** to find sensitive files — the first documented case of malware weaponizing AI coding assistants. 2,349 distinct credentials leaked to public GitHub repos in ~4 hours.

## What happened
Affected versions: `nx` 21.5.0, 20.9.0, 20.10.0, 21.6.0, 20.11.0, 21.7.0, 21.8.0, 20.12.0 and several supporting plugins.

The payload, executed via `postinstall`:

1. **Recon with AI CLIs.** If `claude` or `gemini` CLIs were present on the host, the malware **invoked them as subprocesses** to enumerate sensitive paths and credential locations more intelligently than a static script could.
2. **Harvest creds.** Targets: GitHub tokens, npm tokens (`~/.npmrc`), SSH keys, environment variables, browser-based cryptocurrency wallet artifacts.
3. **Exfiltrate via GitHub CLI.** Used the host's authenticated `gh` to create a public repo and upload the stolen data.

Among 2,349 leaked secrets: GitHub OAuth keys/PATs, Google AI keys, OpenAI keys, AWS keys, OpenRouter keys, Anthropic Claude keys, PostgreSQL creds, Datadog keys.

Active for ~4 hours before takedown. Root cause on the Nx side: a GitHub Actions workflow allowed PR-controlled input into a command run with publish privileges — classic Actions injection.

## Am I affected?

```bash
# Check Nx version anywhere in your tree
npm ls nx --all

# Specifically check for the bad versions
npm ls nx --all | grep -E '21\.(5|6|7|8)\.0|20\.(9|10|11|12)\.0'
```

If you installed any of those versions in the August 26 window, treat the host as fully compromised — all dev-machine creds, all cloud creds, every AI API key on disk.

```bash
# Did the malware plant a public repo with your creds?
gh api /user/repos --paginate --jq '.[] | select(.created_at > "2025-08-26T00:00:00Z" and .created_at < "2025-08-27T00:00:00Z") | {name, private}'
```

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

Pay special attention to: rotating Anthropic, OpenAI, and Google AI API keys; these are not always treated with the same rigor as cloud creds but cost the same when stolen.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `--ignore-scripts` would have completely neutered this attack
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources
- [Nx Blog — S1ngularity Postmortem](https://nx.dev/blog/s1ngularity-postmortem)
- [Snyk — Weaponizing AI Coding Agents for Malware in the Nx Malicious Package Security Incident](https://snyk.io/blog/weaponizing-ai-coding-agents-for-malware-in-the-nx-malicious-package/)
- [Semgrep — NX Compromised to Steal Wallets and Credentials](https://semgrep.dev/blog/2025/security-alert-nx-compromised-to-steal-wallets-and-credentials/)
- [The Hacker News — Malicious Nx Packages in 's1ngularity' Attack Leaked 2,349 Credentials](https://thehackernews.com/2025/08/malicious-nx-packages-in-s1ngularity.html)
- [GitHub Advisory — GHSA-cxm3-wv7p-598c](https://github.com/nrwl/nx/security/advisories/GHSA-cxm3-wv7p-598c)
