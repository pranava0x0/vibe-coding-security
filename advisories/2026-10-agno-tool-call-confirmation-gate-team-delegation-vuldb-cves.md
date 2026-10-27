---
id: 2026-10-agno-tool-call-confirmation-gate-team-delegation-vuldb-cves
title: "Agno runs model-requested tool calls with no default confirmation gate and delegates with the leader's identity (CVE-2026-108819, CVE-2026-108820); fix PRs open, no release"
date_disclosed: 2026-10-12
last_updated: 2026-10-27
severity: high
status: unconfirmed
ecosystems: [pypi, ai-agents, agno]
tools_affected: ["agno 3.0.0 through 3.0.6 and 3.1.0 through 3.1.1 per the CNA record; the reporter's advisory says <= 3.0.6; PyPI latest is 3.1.3 and nothing on the record says it is fixed", "any Agno agent with PythonTools, ShellTools or another code-executing toolkit registered", "any Agno Team in route or broadcast mode whose members hold file, shell or code tools"]
tags: [cve, vuldb, agent-framework, prompt-injection, tool-execution, human-in-the-loop, confirmation-gate, delegation, privilege, single-reporter, no-fix, unconfirmed]
---

## TL;DR
Two VulDB-assigned CVEs published on 2026-10-12 describe Agno, the Python agent framework, running whatever tool call the model requests. CVE-2026-108819: the orchestration loop in `run_function_calls()` executes every model-requested tool immediately unless a per-tool confirmation flag is set, and the flags default to off, so an agent with `PythonTools` registered turns a prompt injection in a page or document into code running in the host process. CVE-2026-108820: a Team's `delegate_task_to_member` runs the member agent under the leader's user, session and state with the member's full toolset and no confirmation, so an injected leader hands an attacker every member's tools. Both come from one reporter's GitHub issues opened 2026-09-08, with no maintainer reply on either issue as of 2026-10-12. Two community pull requests that make confirmation the default (PR #10523, PR #10124) have been open since 2026-09-24 and 2026-09-11. No release fixes either; PyPI latest is 3.1.3. The CNA record lists 3.0.0 through 3.1.1 as affected. These are design defaults, not memory bugs: the framework behaves as documented, and whether that is a vulnerability is what the open issues are arguing about.

## What happened

The GitHub Advisory Database's `agent` listing showed two unreviewed Agno rows on 2026-10-12. The CVE records name VulDB as CNA, list the versions 3.0.0 through 3.0.6 and 3.1.0 through 3.1.1 individually, and reference the reporter's issues, the fix pull requests and an advisories repository the reporter maintains (`ybyu-ieu/agno-security-advisories`). The VulDB descriptions are generic ("manipulation of the argument code results in dynamically-managed code resources"; "execution with unnecessary privileges"); the mechanism below is from the issues and the reporter's advisory, which were opened this run.

| Finding | CVE | Component | Precondition | What the attacker gets | Scores | Fix |
|---|---|---|---|---|---|---|
| Tool calls run without a confirmation gate | CVE-2026-108819 | `libs/agno/agno/models/base.py`, `run_function_calls()` | An agent that processes untrusted content and has a code-executing toolkit (`PythonTools`: `run_python_code`, `save_to_file_and_run`, `run_python_file_return_variable`, `pip_install_package`, `uv_pip_install_package`) registered with the default `requires_confirmation_tools` | Arbitrary code in the host Python process with its privileges: read secrets, write or delete files, open network connections, no prompt shown | Reporter 9.8 CVSS 3.1 (CWE-913); VulDB 7.3 CVSS 3.1 / 6.9 CVSS 4.0 | PR #10523 (opened 2026-09-24, open) makes the five code-executing PythonTools require confirmation by default, with an explicit empty list to opt out; the author labels it a breaking default change and says it is not a sandbox. ShellTools and DaytonaTools are out of its scope. |
| Team delegation runs members as the leader | CVE-2026-108820 | `libs/agno/agno/team/_default_tools.py`, `delegate_task_to_member` / `delegate_task_to_members` | A Team in route or broadcast mode whose members have file, shell or code tools | The member runs under the leader's `user_id`, session, state and dependencies with the member's full toolset, no scoping, no confirmation and no audit record | Reporter 9.8 CVSS 3.1 (CWE-250, CWE-862); VulDB 6.3 CVSS 3.1 / 5.3 CVSS 4.0 | PR #10124 (opened 2026-09-11, open) sets `requires_confirmation=True` on the generated delegation functions; tasks mode is unaffected because it attaches no delegation tool. A bot labelled the PR `missing-issue-link`. |

The reporter's advisory for the first finding verified its proof of concept against agno 2.7.3 in September 2026 and lists `<= 3.0.6` as affected with no patched version; the CNA record extends the range to 3.1.1. Nothing on the record, the issues or the pull requests says 3.1.2 or 3.1.3 changed the default. The environment field on both issues says 2.7.3, which is below the stated range ceiling, so the lower bound is unknown and probably much older than 3.0.0.

### Why `unconfirmed`, and why it is still written up
One reporter, two issues with no maintainer comment, two community fixes nobody has merged, and a CNA (VulDB) that assigns on submission rather than on validation. That is the shape §10 of this corpus's process notes calls a GitHub issue as primary source, and it gets `status: unconfirmed` with the vendor silence stated. It is written anyway because the claim is checkable from the code the issues cite, the pull requests exist and describe the behaviour they change, and the class is the one this corpus keeps recording: a framework that executes model output by default, as in [the PraisonAI batch](2026-08-agent-framework-mcp-cve-batch.md), [the MITRE agent-framework wave](2026-09-ro1me-open-source-agent-framework-llm-output-execution-cve-wave.md) and [LangGrinch](2025-12-langchain-langgrinch.md). The scores disagree by design: the reporter scores the host application that embeds the library (9.8, or 10.0 with a scope change); VulDB scores the library on its own (7.3 and 6.3). Neither is this advisory's assessment. `high` because the precondition, a code-executing toolkit on an agent that reads untrusted content, is the default shape of an Agno coding or research agent, and because no release changes it.

## Am I affected?

```bash
pip show agno 2>/dev/null | grep -i ^version          # every released version is in or below the stated range
# Code-executing toolkits registered on an agent
grep -rn "PythonTools\|ShellTools\|DaytonaTools\|E2BTools" --include=*.py . 2>/dev/null
# Whether confirmation is set anywhere
grep -rn "requires_confirmation" --include=*.py . 2>/dev/null
# Teams in route or broadcast mode (delegation tool attached)
grep -rn "Team(" --include=*.py . 2>/dev/null | grep -v "mode=\"tasks\"\|mode='tasks'"
```

- Affected if an agent that reads web pages, documents, email, tickets or repository content also has a code, shell or file toolkit and `requires_confirmation_tools` is unset. The model decides, and the framework runs it.
- Affected if a Team routes or broadcasts to members holding such tools and processes untrusted content at the leader.
- Not affected by these two records if every tool the agent holds is read-only against trusted data, or if confirmation is already set on the dangerous tools and a human reviews the pause.

## If you are affected

1. **Set `requires_confirmation_tools` explicitly** on every toolkit that writes, executes or installs, today, without waiting for the pull requests. The mechanism exists in current releases; only the default is at issue.
2. **Give members their own identity** or move the Team to tasks mode until delegation can be gated. Audit what the leader's session and dependencies expose to members.
3. **Run code-executing agents in a sandbox with no long-lived secrets in the environment** and with network egress controlled: [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md). If an agent in the vulnerable shape has already processed untrusted content, rotate the keys its process could read: [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md), [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. **Watch issues #10053 and #10054 and the two pull requests** for a maintainer position. A merge would change the default and the status here; a "works as designed" reply would make this a hardening file.

## Prevention

- **The model's tool call is attacker input.** A confirmation gate, an allowlist and a sandbox each cover what the others miss; none is optional on an agent that reads the web: [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).
- **Delegation is privilege transfer.** A sub-agent should get a scoped identity and the minimum toolset, and its runs should be attributable to it, not to the leader.
- **Frameworks disclose through issues before advisories.** Agno's own security tab was not checked this sweep; the CVEs surfaced through the database listing and the records point at issues, not at a vendor page. Grep the issue tracker of any framework you embed for "CVSS", "CWE" and "security" each release.

## Sources
- CVE Services (CNA: VulDB), fetched 2026-10-12: [CVE-2026-108819](https://cveawg.mitre.org/api/cve/CVE-2026-108819) and [CVE-2026-108820](https://cveawg.mitre.org/api/cve/CVE-2026-108820) — published 2026-10-12, the per-version affected list (3.0.0 through 3.0.6, 3.1.0, 3.1.1), VulDB's CVSS 3.1 7.3 and 6.3 and CVSS 4.0 6.9 and 5.3, the "exploit has been released to the public" and "pull request to fix" statements, and the references to the issues, pull requests and the reporter's advisory repository.
- [agno-agi/agno issue #10053](https://github.com/Agno-agi/Agno/issues/10053) — fetched 2026-10-12: opened 2026-09-08 by ybyu-ieu, open, label `bug`, the `run_function_calls()` claim, the PythonTools precondition, the 9.8 vector, the offline proof of concept, no maintainer comment; two 2026-09-24 comments by contributor Kylinny announcing and linking PR #10523.
- [agno-agi/agno issue #10054](https://github.com/Agno-agi/Agno/issues/10054) — fetched 2026-10-12: opened 2026-09-08, open, the `delegate_task_to_member` claim, CWE-250 with CWE-862, "Patched: none yet," environment Agno 2.7.3, no maintainer comment, linked PR #10124.
- [agno-agi/agno pull request #10523 "fix: require confirmation by default for PythonTools code-executing tools"](https://github.com/agno-agi/agno/pull/10523) — fetched 2026-10-12: opened 2026-09-24, open, the five tools gated, the opt-out semantics, the breaking-default and not-a-sandbox statements, ShellTools and DaytonaTools out of scope. [Pull request #10124 "fix: require confirmation for team delegation"](https://github.com/agno-agi/agno/pull/10124) — fetched 2026-10-12: opened 2026-09-11, open, `requires_confirmation=True` on the delegation functions, tasks mode unaffected, the `missing-issue-link` label.
- [ybyu-ieu/agno-security-advisories — agno agent orchestration missing confirmation gate](https://github.com/ybyu-ieu/agno-security-advisories/blob/main/advisories/agno-agent-orchestration-missing-confirmation-gate-code-execution.md) — fetched 2026-10-12: `<= 3.0.6`, patched "None," 9.8 (10.0 with scope change), CWE-913, proof of concept verified against 2.7.3 in September 2026, no vendor timeline.
- [GitHub Advisory Database — `agent` listing sorted by published date](https://github.com/advisories?query=agent+sort%3Apublished-desc) — fetched 2026-10-12: GHSA-fxvj-hc6f-3f6v and GHSA-rh58-m2cv-88pv, both unreviewed, published 2026-10-12.
- Registry, checked 2026-10-12: `pip index versions agno` shows 3.1.3 latest, with 3.1.2, 3.1.1, 3.1.0 and 3.0.0 through 3.0.11 published; no release note was located that names either issue.
- Related in this corpus: [PraisonAI and the agent-framework MCP batch](2026-08-agent-framework-mcp-cve-batch.md), [one reporter's MITRE agent-framework wave](2026-09-ro1me-open-source-agent-framework-llm-output-execution-cve-wave.md), [LangGrinch](2025-12-langchain-langgrinch.md).
- Related (2026-10-27): an older, vendor-acknowledged and patched Agno RCE reviewed by the advisory database today is filed separately as [Agno eval on field_type](2026-10-agno-function-call-field-type-eval-rce-fixed-2-3-24.md); it is unrelated to the two VulDB records above.
