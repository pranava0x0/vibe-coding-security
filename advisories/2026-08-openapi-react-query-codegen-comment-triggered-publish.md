---
id: 2026-08-openapi-react-query-codegen-comment-triggered-publish
title: "@7nohe/openapi-react-query-codegen compromised via comment-triggered npm publish workflow (Aug 2026)"
date_disclosed: 2026-08-28
last_updated: 2026-08-28
severity: critical
status: contained
ecosystems: [npm]
tools_affected: ["@7nohe/openapi-react-query-codegen", claude-code, cursor, github-copilot]
tags: [supply-chain, credential-theft, ci-cd-hardening, github-actions, oidc-token-abuse, mini-shai-hulud-lineage, ai-agent-config-poisoning]
---

## TL;DR
An attacker didn't need a stolen npm token or a hijacked maintainer account — they just commented `npm publish` on a pull request. `@7nohe/openapi-react-query-codegen` (~150,000 weekly downloads, generates React Query hooks from OpenAPI schemas) had a GitHub Actions release workflow that triggered on `issue_comment` events without checking the commenter's repo permissions, then ran `pnpm install` against the PR author's own fork code before publishing with `id-token: write` OIDC credentials. On 2026-08-28 the attacker used exactly that gap to publish 10 malicious versions carrying a credential-stealing payload with valid npm provenance.

## What happened
On 2026-08-28, GitHub user `p00paboot` opened pull requests (#215, #216) against the `@7nohe/openapi-react-query-codegen` repository, then posted a comment reading `npm publish` on the PR thread. The release workflow listened for `issue_comment` events and executed on that trigger without verifying the commenter's author association or repository role — it checked out the attacker's fork content, ran `pnpm install` (executing the attacker's `preinstall`/`binding.gyp` hooks in the process), and then published to npm using the workflow's own GitHub Actions OIDC identity, which held `id-token: write` permission ([StepSecurity](https://www.stepsecurity.io/blog/7nohe-openapi-react-query-codegen-compromised-npm-publishing-workflow); [Socket](https://socket.dev/blog/openapi-react-query-codegen-npm-compromise)).

Ten versions were published between **20:00:43 and 20:20:53 UTC** across two waves roughly 20 minutes apart: `0.5.4`, `0.5.5`, `1.6.3`, `1.6.4`, `2.2.1`, `2.2.2`, `3.0.3`, `3.0.4`, plus two prerelease-tagged commits (`0.0.0-365d4eb7...`, `0.0.0-ec7876d6...`). Package size for `0.5.4` jumped from a normal 41 KB to 5.6 MB, carrying a ~6.38 MB obfuscated JavaScript payload. Because the workflow's OIDC identity was legitimate, the malicious releases carried **valid npm provenance attestations** despite shipping attacker code — as Socket put it, "provenance proves which workflow built an artifact; it does not prove that the workflow only builds trusted source."

**Payload behavior.** Execution happened either via a `preinstall` script (wave 2) invoking `node 3FWCvzduYZg.js`, or via a poisoned `binding.gyp` using a Python object-traversal trick to reach `os.system()`. Once running, the payload:
- Downloaded the Bun runtime from GitHub release infrastructure to execute the main harvester.
- Attempted credential theft from the filesystem, process memory, environment variables, and cloud metadata endpoints (Google Cloud metadata probing confirmed; targets GitHub, npm, PyPI, RubyGems, JFrog, AWS, Azure, and Vault credentials per Socket's analysis).
- Ran `gh auth token` and `git credential-manager github list --no-ui` to harvest GitHub credentials, and enumerated SSH/SCP tooling for lateral movement to reachable hosts.
- Exfiltrated encrypted findings to attacker-created public GitHub repositories, and injected malicious workflows into any accessible repos to further expose secrets.
- Installed persistence via a macOS LaunchAgent and a Linux systemd user service (`sysvinit-detect-fash.sh`/`.plist`/`.service`), and planted a developer-tool backdoor (`.config/index.js`) that Socket describes as injecting persistence into "developer tool configurations (Claude, Copilot, Cursor, etc.)" — consistent with the AI-agent-config-poisoning pattern this repo tracks across multiple 2026 npm-worm campaigns.
- Monitored stored GitHub tokens and executed a stored handler on a 4xx auth response, and retrieved signed follow-on commands from GitHub commit messages.

**IOCs:** threat-actor GitHub account `github.com/p00paboot` (fork: `p00paboot/openapi-react-query-codegen`); payload file `3FWCvzduYZg.js` (SHA256 `b49afb7dba04cd99b357ce7c652c823a3707f28e130bd5c6645851a7adc030d6`); poisoned `binding.gyp` (SHA256 `d3246926b20a8d021ed7de0ac8e9eee1dda986088f84ba18f31cb2042a121f5d`); additional dropped files `ai_init.js`, `ai_setup.sh`, `is_it_this_simple.js`; persistence paths `~/.local/bin/sysvinit-detect-fash.sh`, `~/Library/LaunchAgents/com.user.sysvinit-detect-fash.plist`, `~/.config/systemd/user/sysvinit-detect-fash.service`, `/var/tmp/.shit` (command history) ([Socket](https://socket.dev/blog/openapi-react-query-codegen-npm-compromise)).

**Attribution.** Both sources describe the payload as sharing characteristics — npm delivery, Bun-based staging, credential-harvesting-then-propagate structure — with the broader Shai-Hulud/Mini-Shai-Hulud campaign lineage this repo already tracks, but neither source confirms attribution to a specific known actor; treat the lineage claim as circumstantial, not confirmed.

**Fix.** The maintainer removed the malicious versions; last known-good releases are `0.5.3`, `1.6.2`, `2.2.0`, and `3.0.2`. StepSecurity's writeup frames the durable fix as workflow-level: gate `issue_comment`-triggered jobs on commenter repository association (e.g. `github.event.comment.author_association == 'OWNER' || ... == 'MEMBER'`) before granting `id-token: write` or running untrusted PR content.

## Am I affected?
```bash
# Check installed versions
npm ls @7nohe/openapi-react-query-codegen 2>/dev/null

# Malicious versions: 0.5.4, 0.5.5, 1.6.3, 1.6.4, 2.2.1, 2.2.2, 3.0.3, 3.0.4
# Known-good: 0.5.3, 1.6.2, 2.2.0, 3.0.2

# Look for the dropped payload/persistence artifacts
find . -path '*/node_modules/*' -name '3FWCvzduYZg.js' 2>/dev/null
ls ~/Library/LaunchAgents/com.user.sysvinit-detect-fash.plist 2>/dev/null
ls ~/.config/systemd/user/sysvinit-detect-fash.service 2>/dev/null
cat ~/.local/bin/sysvinit-detect-fash.sh 2>/dev/null
```
If any match, treat the machine or CI runner as compromised — do not just downgrade the package.

## If you are affected
1. Isolate the affected machine/runner from the network before touching credentials — the persistence handler reportedly triggers on stored-token 4xx responses, so disable the LaunchAgent/systemd service first.
2. Rotate npm, GitHub, cloud (AWS/GCP/Azure), and SSH credentials from a clean, uncompromised system.
3. Rebuild the environment from a clean image rather than remediating in place; review lockfiles/SBOMs for transitive pulls of the malicious versions.
4. Audit your GitHub account for repos, workflow changes, or commits you don't recognize (the payload creates public repos to stage exfiltrated data).

→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)

## Prevention
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — never grant `id-token: write` or publish credentials to a workflow triggerable by an unvetted commenter; gate `issue_comment`/`pull_request_target` jobs on `author_association`.
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — pin exact versions; a valid provenance badge proves which pipeline built a release, not that the pipeline only builds trusted source.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Sources
- [Socket — OpenAPI React Query Codegen Compromised in Mini Shai-Hulud npm Supply Chain Attack](https://socket.dev/blog/openapi-react-query-codegen-npm-compromise) — primary technical analysis: payload behavior, IOCs, timeline.
- [StepSecurity — @7nohe/openapi-react-query-codegen Compromised Through an Exposed npm Publishing Workflow](https://www.stepsecurity.io/blog/7nohe-openapi-react-query-codegen-compromised-npm-publishing-workflow) — workflow vulnerability mechanics, PR numbers, remediation guidance.
- [CyberSecurityNews — Popular npm Package With 150K Weekly Downloads Compromised in Mini Shai-Hulud Supply-Chain Attack](https://cybersecuritynews.com/popular-npm-package-2/) — corroborating summary.
