---
id: 2026-08-jsonata-sandbox-escape-rce
title: "JSONata — the expression engine n8n and other workflow platforms embed as a 'safe' query language ships two CVSS 9.3 sandbox-escape RCEs (CVE-2026-77414, CVE-2026-77415)"
date_disclosed: 2026-07-13
last_updated: 2026-08-23
severity: critical
status: patched
ecosystems: [npm, javascript, self-hosted]
tools_affected: [jsonata, n8n, any low-code or workflow platform embedding jsonata for expression evaluation]
tags: [sandbox-escape, rce, code-injection, prototype-pollution, agent-sandboxing, ai-workflow-platforms]
---

## TL;DR

**JSONata** — a 1.3M-weekly-download npm package that workflow-automation platforms (most notably **n8n**, which ships it as a first-class expression language) and other AI-agent/low-code tools embed specifically because it's marketed as a *safe*, sandboxed way to let users write data-transformation expressions — shipped two critical arbitrary-code-execution advisories on the same day: **CVE-2026-77414** (GHSA-2943-5xfg-gq5f) and **CVE-2026-77415** (GHSA-66mm-25pp-rfff), both **CVSS 9.3 (v4.0) / 9.8 (v3.1)**. A crafted JSONata expression — the exact kind of untrusted input the library exists to evaluate — escapes the evaluation sandbox and runs arbitrary Node.js code. Fixed in **1.8.8** and **2.2.1**.

## What happened

JSONata is a JSON query-and-transformation language, and its whole value proposition to embedders is that user-supplied expressions can be evaluated without giving the expression author access to the host JavaScript environment — the same "safe sandbox for untrusted expressions" pitch that `vm2` and `isolated-vm` make (see [the vm2/isolated-vm sandbox-escape advisory](2026-08-vm2-isolated-vm-sandbox-escapes.md)), just implemented as a language interpreter rather than a V8 isolate. Both new CVEs break that promise, discovered and reported by researcher **c0rydoras**, published to GHSA/NVD **2026-08-21** (originally filed 2026-07-13):

- **CVE-2026-77414 (GHSA-2943-5xfg-gq5f)** — a **bypassable `hasOwnProperty` check in `environment.lookup`**. The environment-lookup function is supposed to confine name resolution to the sandbox's own scope, but the check can be defeated by shadowing local lookup methods and walking the prototype chain, letting a crafted expression reach host-realm objects and functions it was never meant to see.
- **CVE-2026-77415 (GHSA-66mm-25pp-rfff)** — three chainable weaknesses in the same evaluator: overwriting the built-in **`$clone`** function lets an expression mutate objects during a transform instead of only copying them; JSONata functions/lambdas can be **destructured** (e.g. via `$merge.*`) to expose their internals; and `applyProcedure`'s custom `forEach`-style argument handling (rather than `Array.prototype.forEach`) gives a crafted expression a way to manipulate `proc.arguments`. Chained together, these let an attacker escape the evaluation environment and execute arbitrary system commands through the Node.js runtime.

Both bugs share the same root shape as the vm2/isolated-vm cluster tracked in this repo three weeks earlier: **a component that markets itself as a safe way to run untrusted, model- or user-supplied input turns out not to be one**, and because neither is a lifecycle-script or install-time issue, standard `--ignore-scripts` / supply-chain hygiene does nothing to stop it — the vulnerable code only runs when the *application* evaluates an expression, which is JSONata's entire purpose.

## Am I affected?

```bash
# Direct or transitive dependency on jsonata, and at what version?
npm ls jsonata --all 2>/dev/null
# Or from a lockfile:
grep -n -A2 '"jsonata"' package-lock.json 2>/dev/null | head -40
```

Fixed versions: **1.8.8** and **2.2.1**. Anything **`< 1.8.8`** or **`>= 2.0.0, < 2.2.1`** is affected.

If you run **n8n**, check whether your build has already picked up the patched jsonata via its own dependency updates — n8n embeds JSONata as a built-in expression mode, so any workflow that accepts a JSONata expression from an untrusted source (a webhook payload, a form submission, another tenant) is a direct attack surface until the transitive dependency is bumped. The same applies to any other platform that lets users author JSONata expressions — treat "we sandbox user expressions with JSONata" the same way you'd treat "we sandbox user code with vm2": as a mitigation that just failed, not a boundary.

## If you are affected

- [If your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md)
- [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) — a host-process RCE reaches every credential in that process's environment, not just the expression's inputs.
- [If your web app was compromised](../playbooks/if-your-webapp-was-compromised.md)

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md)
- [Supply-chain attack surface](../prevention/supply-chain-attack-surface.md)
- [Package vetting checklist](../prevention/package-vetting-checklist.md)

Practical guidance: put an **OS-level boundary** (container, VM, seccomp, separate process with dropped privileges) beneath any embedded expression/query-language evaluator that processes untrusted input, exactly as recommended for `vm2`/`isolated-vm` — an in-language "safe expression" sandbox is not a substitute for process isolation. Watch GHSA and your platform's dependency-bump changelogs directly; a transitive jsonata upgrade will rarely be called out as a security fix in the embedding platform's own release notes.

## Sources

- [GitHub Advisory Database — GHSA-2943-5xfg-gq5f (CVE-2026-77414)](https://github.com/advisories/GHSA-2943-5xfg-gq5f) — fetched directly: CVSS 9.3 (v4.0), affected `< 1.8.8` and `>= 2.0.0, < 2.2.1`, patched 1.8.8 / 2.2.1, the bypassable `hasOwnProperty` root cause, reporter c0rydoras, fix PR #799 and commits 59e2514/c41ef18/f09df84.
- [NVD — CVE-2026-77414](https://nvd.nist.gov/vuln/detail/CVE-2026-77414) — independently fetched: confirms CVSS 9.3 (v4.0) vector, affected/patched version ranges, and the fix commit reference, corroborating the GHSA record.
- [GitHub Advisory Database — GHSA-66mm-25pp-rfff (CVE-2026-77415)](https://github.com/advisories/GHSA-66mm-25pp-rfff) — fetched directly: CVSS 9.3, the `$clone` overwrite / lambda destructuring / `applyProcedure` chain, reporter c0rydoras, fix PRs #799/#800/#802 backported to 1.8.8.
- [GitLab Advisory Database — CVE-2026-77414](https://advisories.gitlab.com/npm/jsonata/CVE-2026-77414/) — independent corroboration of CVSS 9.8 (v3.1 scoring), affected/patched versions.
- [GitLab Advisory Database — CVE-2026-77415](https://advisories.gitlab.com/npm/jsonata/CVE-2026-77415/) — independent corroboration of CVSS 9.8 (v3.1 scoring), affected/patched versions.
