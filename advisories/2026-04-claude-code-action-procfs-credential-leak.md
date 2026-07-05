---
id: 2026-04-claude-code-action-procfs-credential-leak
title: "Claude Code GitHub Action's unsandboxed Read tool leaks CI/CD secrets via /proc/self/environ (patched in Claude Code 2.1.128)"
date_disclosed: 2026-04-29
last_updated: 2026-04-29
severity: high
status: patched
ecosystems: [github-actions, claude-code, anthropic]
tools_affected: [Claude Code GitHub Actions (anthropics/claude-code-action), any CI/CD pipeline running Claude Code on untrusted GitHub content]
tags: [claude-code, github-actions, prompt-injection, credential-theft, ci-cd, sandbox-bypass]
---

## TL;DR

Microsoft Threat Intelligence found that Claude Code's **Read tool did not get the same sandboxing as the Bash tool**, so a prompt-injected instruction hidden in a GitHub issue, PR, or comment could make the agent read `/proc/self/environ` inside the CI runner and exfiltrate the `ANTHROPIC_API_KEY` (and any other secret in the workflow's environment) — via a workflow log, a comment, or an outbound web request. Disclosed to Anthropic via HackerOne on **2026-04-29**; patched in **Claude Code 2.1.128** (**2026-05-05**) by blocking Read-tool access to sensitive `/proc` files. No CVE assigned.

## What happened

Anthropic's official `claude-code-action` GitHub Action lets Claude Code run autonomously inside CI/CD pipelines — reviewing issues, triaging PRs, responding to comments — with access to whatever secrets the workflow has (API keys, cloud OIDC tokens, deploy credentials). Claude Code's **Bash tool** already scrubbed the process environment before executing shell commands, but the **Read tool** was not held to the same standard: it could open and read arbitrary files the runner process had permission to access, including `/proc/self/environ`, which contains every environment variable of the running process in raw, unredacted form.

Microsoft's attack chain:
1. Plant a hidden instruction inside a GitHub issue body, PR description, or comment — invisible to a human skimming the rendered page (e.g. wrapped in an HTML comment), but plain text to the model reading the raw content.
2. Frame the injected instruction as an innocuous task, e.g. a "compliance review," that directs Claude to read `/proc/self/environ`.
3. Launder the extracted secret past output filters — Microsoft's PoC had the injected prompt instruct Claude to mangle the string (e.g. "cut the first 7 characters") before repeating it back, defeating simple secret-pattern redaction.
4. Exfiltrate the reconstructed credential through any channel the agent had access to: a posted issue/PR comment, a workflow log line, or an outbound web request.

Because the Read tool ran with the CI runner's full process environment and no equivalent of the Bash tool's environment-scrubbing, this gave an unauthenticated external attacker — anyone who can open an issue or comment on a public repo — a path to steal the `ANTHROPIC_API_KEY` and any other secret exposed to the workflow (cloud OIDC tokens, deploy keys, etc.), without needing write access to the repository.

This is a **different vulnerability** from the previously-tracked [Claude Code GitHub Actions `[bot]`-suffix trust bypass](2026-06-claude-code-github-actions-bot-bypass.md) (RyotaK, disclosed 2026-06-04, patched in the Action's own v1.0.94) — different root cause (unsandboxed file-read tool vs. a string-suffix trust check), different fix (Claude Code core 2.1.128 vs. the Action wrapper 1.0.94), different researcher. Both share the same entry point (prompt injection via untrusted GitHub content processed by an agentic CI workflow) and the same underlying lesson: any AI agent with both secrets access and untrusted-content exposure in CI is a credential-exfiltration path until every tool it can invoke is sandboxed as tightly as the most dangerous one.

## Am I affected?

```bash
# Check whether your workflows use claude-code-action and which version
grep -rn "anthropics/claude-code-action" .github/workflows/

# Check your installed Claude Code CLI version (the Action shells out to this)
claude --version   # fixed in 2.1.128 and later
```

If any workflow ran `claude-code-action` (or a self-hosted Claude Code CLI invocation) against untrusted GitHub content — public-repo issues, PRs, or comments from non-collaborators — on a Claude Code version **older than 2.1.128**, treat any secret exposed to that workflow's environment as potentially exposed.

## If you are affected

1. **Update Claude Code to 2.1.128 or later** everywhere it runs in CI, including any pinned version inside `claude-code-action` workflows.
2. **Rotate `ANTHROPIC_API_KEY`** and any other secret that was present in the environment of a workflow that processed untrusted GitHub content before the patch.
3. **Audit workflow logs and posted comments** for unexpected reconstructed strings (partial keys, base64/reversed/sliced fragments) that could indicate a successful exfiltration attempt.
4. **Review which secrets are actually needed** by agent-driven CI workflows — scope tokens as narrowly as possible so a single leaked credential has limited blast radius.

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)

## Prevention

- **Treat every tool an agent can invoke as equally dangerous.** A sandbox that scrubs the environment for `Bash` but not `Read` (or any other tool) is not a sandbox — it's a suggestion. Audit agentic CI tools for tool-by-tool parity in sandboxing, not just the obviously "risky" ones.
- **Never run an AI agent with both secrets access and untrusted-content exposure in the same execution context** without least-privilege scoping — treat GitHub issue/PR/comment content from non-collaborators as attacker-controlled input.
- **Least-privilege CI tokens.** Scope `GITHUB_TOKEN` and any injected API keys to the minimum required for the workflow; use short-lived OIDC tokens over long-lived static secrets where possible.
- Keep CI-embedded AI tools on auto-update — this is another entry in the growing list of Claude Code security fixes shipped without a CVE or changelog callout.

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

## Sources

- [Microsoft Security Blog — Securing CI/CD in an agentic world: Claude Code GitHub Action case](https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/) — primary disclosure; attack chain, `/proc/self/environ` detail, disclosure/patch dates and version, output-laundering PoC.
- [Decrypt — Claude Code Vulnerability Could Let Attackers Steal Credentials From GitHub, Says Microsoft](https://decrypt.co/370238/claude-code-vulnerability-attackers-steal-credentials-github-microsoft) — independent confirmation of timeline (2026-04-29 disclosure via HackerOne, 2026-05-05 patch in Claude Code 2.1.128) and attack framing.
- [The420.in — Microsoft Threat Intelligence Exposes Prompt Injection Flaw In Anthropic Claude Code Action](https://the420.in/microsoft-claudecode-vulnerability-github-secrets/) — corroborates the unsandboxed Read tool / `/proc/self/environ` mechanism and the procfs-blocking mitigation.
- Cross-reference: [2026-06-claude-code-github-actions-bot-bypass.md](2026-06-claude-code-github-actions-bot-bypass.md) — sibling vulnerability in the same GitHub Action ecosystem, different root cause.
