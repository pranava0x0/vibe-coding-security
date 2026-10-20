---
id: 2026-10-deepagents-filesystem-rule-alternate-path-bypass-acp-always-allow-shell-bypass-ghsa-pair
title: "LangChain Deep Agents: filesystem deny and approval rules bypassed by alternate paths, ACP shell approval bypass; fixed deepagents 0.7.25 and deepagents-acp 0.0.13"
date_disclosed: 2026-10-13
last_updated: 2026-10-20
severity: medium
status: patched
ecosystems: [python, pypi, agent-frameworks, deepagents, langchain]
tools_affected: ["deepagents 0.5.2 through 0.7.24 (PyPI) with path-based deny or interrupt rules on a host FilesystemBackend", "deepagents-acp 0.0.3 through 0.0.12 exposing execute through a host backend such as LocalShellBackend", "every agent built on Deep Agents, including the twelve products in the Lasso/VulnCheck wave"]
tags: [ghsa, agent-framework, deepagents, langchain, approval-bypass, link-following, command-injection, policy-bypass, vendor-advisory, zero-file-product]
---

## TL;DR
LangChain's Deep Agents framework published two advisories in October with no CVE: before `deepagents` 0.7.25 the path-based `deny` and `interrupt` rules were checked against a path form that could differ from the file the `FilesystemBackend` actually touched, so an agent could read or modify a blocked file or skip an approval (GHSA-47w2-rfrr-wvq8, CVSS 4.0 6.0, 2026-10-15), and before `deepagents-acp` 0.0.13 a shell command that failed to parse ran without a prompt once the user had chosen "Always allow" for a different command in the same session (GHSA-459r-276m-w72x, CVSS 4.0 6.0, 2026-10-13). Both are fixed on PyPI (0.7.25 on 2026-10-14, 0.0.13 on 2026-10-12). The framework named by four of the seventeen records in [this week's Lasso/VulnCheck wave](2026-10-lasso-vulncheck-seventeen-cve-agent-platform-wave-deep-agents-ungated-shell-tools.md) had no file here before today.

## What happened

Deep Agents is LangChain's framework for agents that plan, spawn sub-agents and work a filesystem, with an `execute` tool that can be wired to a local shell. It is the layer the Cognition, piflow, Aix-DB and EvoScientist records in the Lasso/VulnCheck wave name. Its repository's security tab carries two advisories, both published by the maintainers.

**GHSA-47w2-rfrr-wvq8 (2026-10-15, CWE-59).** Affected `deepagents` >= 0.5.2, < 0.7.25; patched 0.7.25. The advisory says path-based `deny` and `interrupt` rules were evaluated against a path form that could differ from the target the `FilesystemBackend` used, so an agent that chose filesystem tool arguments could read or modify a file a rule was meant to block, or perform an operation without triggering the approval interruption. Impact is bounded by what the application process can access, and applications that configure no filesystem permission rules are not affected. The fix evaluates both the requested path and the resolved target. Reporter DavidCarliez; published by vladislav-nechakhin. CVSS 4.0 6.0 (`AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N`).

**GHSA-459r-276m-w72x (2026-10-13, CWE-78).** Affected `deepagents-acp` >= 0.0.3, < 0.0.13; patched 0.0.13. When `execute` is exposed through the ACP integration with a host-running backend such as `LocalShellBackend`, a shell command that failed to parse ran without the approval prompt after the user had chosen "Always allow" for a different command in the same session. The advisory calls it an integrity issue: files could be modified or deleted with the agent user's privileges without the user seeing it, and it adds no read access beyond what the agent already had. The fix stores "Always allow" grants as the exact command and arguments, scoped to the session, so a changed or appended command prompts again. Reporter p80n-sec; remediation by hntrl. CVSS 4.0 6.0 (`AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N`).

PyPI, read 2026-10-20: `deepagents` 0.7.25 uploaded 2026-10-14, newest 0.7.28 (2026-10-16); `deepagents-acp` 0.0.13 uploaded 2026-10-12 and is the newest. Neither advisory names a CVE and neither was on the advisory database's `agent` or `llm` listing this run; they were found by walking the repository's security tab after the wave records named the framework.

Both are the same class as [Claude Code's write-time symlink following](2026-08-claude-code-desktop-ghsa-batch.md), [Continue CLI's rule chaining](2026-10-continue-cli-bash-rule-chaining-bypass-vulncheck-agent-sandbox-batch.md) and [IntentKit's executor](2026-10-intentkit-executor-owner-only-tool-authorization-bypass-cve-2026-76066.md): the rule is checked against one representation of the action and the executing layer acts on another. The wave records describe the next step down, apps that wire no rule at all.

## Am I affected?

- `pip show deepagents deepagents-acp` on the host that runs the agent. Affected: `deepagents` 0.5.2 through 0.7.24 with `deny` or `interrupt` rules keyed on paths; `deepagents-acp` 0.0.3 through 0.0.12 with `execute` on a host backend.
- Not affected per the vendor: Deep Agents apps that configure no filesystem permission rules (the first advisory), and ACP deployments that use a sandboxed backend instead of the local shell (the second).
- If your app's protection is "the model never calls that path" rather than a configured rule, neither advisory applies and nothing protects the file; read [the wave file](2026-10-lasso-vulncheck-seventeen-cve-agent-platform-wave-deep-agents-ungated-shell-tools.md).

## If you are affected

1. `pip install -U "deepagents>=0.7.25" "deepagents-acp>=0.0.13"` and redeploy.
2. Until then, per the vendor: do not rely on path rules alone for sensitive host files, do not expose filesystem aliases that cross rule boundaries, and do not use "Always allow" for shell commands; prefer a sandboxed backend over `LocalShellBackend`.
3. Review the agent's session logs for file operations outside the configured allow set and for shell commands that ran without a prompt; if the agent read untrusted content in that window, treat the host's credentials per [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md): an OS boundary, not a path rule, is the control that holds when the rule is checked against the wrong string.
- [Credential hygiene](../prevention/credential-hygiene.md): keep nothing in the agent's environment that a bypassed rule could reach.

## Sources
- [langchain-ai/deepagents — GHSA-47w2-rfrr-wvq8: Filesystem permission and approval rules may be bypassed through alternate paths](https://github.com/langchain-ai/deepagents/security/advisories/GHSA-47w2-rfrr-wvq8) — fetched 2026-10-20: range, patched version, CVSS, CWE-59, the impact and "not affected" sentences, reporter, remediation and workarounds. Published 2026-10-15; no CVE.
- [langchain-ai/deepagents — GHSA-459r-276m-w72x: Shell approval bypass in deepagents-acp via commands that fail to parse](https://github.com/langchain-ai/deepagents/security/advisories/GHSA-459r-276m-w72x) — fetched 2026-10-20: range, patched version, CVSS, CWE-78, the "Always allow" mechanism and the session-scoped fix, reporter and remediation developer. Published 2026-10-13; no CVE.
- [langchain-ai/deepagents — security advisories tab](https://github.com/langchain-ai/deepagents/security/advisories) — fetched 2026-10-20: the two advisories above and no others.
- PyPI JSON for `deepagents` (0.7.25 on 2026-10-14; 0.7.28 newest) and `deepagents-acp` (0.0.13 on 2026-10-12, newest) — read 2026-10-20.
- Related in this corpus: [the Lasso/VulnCheck wave](2026-10-lasso-vulncheck-seventeen-cve-agent-platform-wave-deep-agents-ungated-shell-tools.md) (the apps built on this framework), [the Continue CLI batch](2026-10-continue-cli-bash-rule-chaining-bypass-vulncheck-agent-sandbox-batch.md) (rule chaining), [IntentKit](2026-10-intentkit-executor-owner-only-tool-authorization-bypass-cve-2026-76066.md) (executor versus prompt-layer checks).
