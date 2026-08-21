---
id: 2026-08-vm2-isolated-vm-sandbox-escapes
title: "Both JavaScript sandboxes that AI workflow platforms run untrusted code in broke in the same fortnight — vm2 (host DNS hijack) and isolated-vm (type confusion → host RCE), August 2026"
date_disclosed: 2026-08-07
last_updated: 2026-08-21
severity: critical
status: patched
ecosystems: [npm, javascript, self-hosted]
tools_affected: [vm2, isolated-vm, n8n, Mastra, Activepieces, Budibase, Sim.ai, Directus, any low-code or agent platform running untrusted JS]
tags: [sandbox-escape, type-confusion, dns-hijack, rce, agent-sandboxing, ai-workflow-platforms]
---

## TL;DR

Two npm JavaScript sandboxes — the ones AI workflow platforms, low-code tools, and agent harnesses use to run user- and model-supplied code — shipped escape advisories within two weeks of each other:

- **`isolated-vm` ≤ 7.0.0** — **GHSA-864f-rcv7-6rh4**, **Critical**, published **2026-08-07**, fixed in **7.0.1** and **6.2.0**. A **TOCTOU type confusion** in `ExternalCopy(value, { transferList })`: the constructor walks the transfer list twice, validating on the first pass and doing an unchecked `As<ArrayBuffer>()` cast on the second. A stateful index getter answers differently each time — a real `ArrayBuffer` when checked, an integer when cast — yielding a controlled-address read/write that lifts to **control-flow hijack in the host process**. **No CVE assigned.**
- **`vm2` ≤ 3.11.5** — **GHSA-m5w8-4gq2-6f8x**, **Critical, CVSS 9.3**, published **2026-08-14**, fixed in **3.11.6**. Under the documented `builtin: ['*']` wildcard, `os` and `dns` were missing from the dangerous-builtins denylist. vm2's readonly proxy blocks property *assignment* but forwards *method calls* into the host realm — so **one line of sandboxed code calling `dns.setServers()` hijacks DNS resolution for the entire host Node process**, persisting after the sandbox is torn down, with no notification to the embedder. **No CVE assigned.**

Endor Labs names six downstream consumers that run untrusted code in `isolated-vm`: **n8n, Activepieces, Mastra, Budibase, Sim.ai, Directus**. **Patch both. Neither carries a CVE, so CVE-based scanners will not flag either one.**

## What happened

Both of these sit at the same structural position: they are the thing a platform reaches for when it needs to run code it does not trust — a user's workflow expression, a model's generated snippet, a tenant's plugin. When that boundary fails, the platform's entire security model fails with it, because everything above assumed the sandbox held.

### isolated-vm — TOCTOU type confusion (GHSA-864f-rcv7-6rh4)

The bug is a **double-walk pattern** in the `ExternalCopySerialized` constructor. It iterates `transfer_list` twice: once to validate that each element is an `ArrayBuffer`, then again to cast and dereference. Nothing re-validates on the second pass.

Because array index access can invoke a JavaScript getter, and **that getter fires once per walk**, an attacker's getter can answer differently each time — returning a genuine `ArrayBuffer` during validation, then an integer during the cast, where it hits an unchecked `As<ArrayBuffer>()` reinterpret-cast. The advisory describes the result as *"a controlled-address read/write [that] can be lifted to control-flow hijacking in the host process."*

Endor Labs' writeup escalates it from a single `ivm.Reference` to a **fake-vtable control-flow hijack of the host process**. The fix wraps the copy in a `v8::Isolate::DisallowJavascriptExecutionScope` — i.e. it removes the attacker's ability to run a getter mid-operation at all, rather than trying to re-validate. Credited to **Cristian-Alexandru Staicu**.

### vm2 — `os` and `dns` reachable, and they have *write* operations (GHSA-m5w8-4gq2-6f8x)

vm2's advisory describes this as an **incomplete implementation of a prior vm2 advisory's fix**, which blocked process-wide observability builtins but overlooked two: `os` and `dns`. (That earlier advisory's id appeared only in truncated form on the page fetched this sweep, so it is deliberately not cited here rather than guessed at.)

The subtlety is why the readonly proxy wasn't enough. `vm.readonly()` prevents a sandboxed script from *assigning* to properties — but it **forwards method calls into the host realm**, and both modules expose methods that mutate host state:

| Module | Read | **Write** |
|---|---|---|
| `os` | `os.userInfo()`, `os.networkInterfaces()`, `os.hostname()` | `os.setPriority()` |
| `dns` | `dns.lookup()`, `dns.getServers()` | **`dns.setServers()`**, `dns.setDefaultResultOrder()` |

`dns.setServers()` is the severe one. Per the advisory, *"every subsequent DNS lookup the host process performs … goes through the attacker's resolver"* — enabling credential exfiltration and supply-chain attacks against everything the host process subsequently talks to. It is **process-wide**, it **persists after sandbox teardown**, and the embedder is never told. A platform that spins up a fresh sandbox per job stays poisoned across every later job in the same process.

The fix adds `'os'` and `'dns'` to `DANGEROUS_BUILTINS` in `lib/builtin.js`, using the existing family-prefix matcher so `node:dns` and `dns/promises` are caught too.

### Why these two together are the story

Neither is exotic. Both are the *second* time the same sandbox has had its containment questioned, and both were found in the same window by different researchers. For this repo's audience the practical reading is:

**A JS sandbox is a mitigation, not a boundary.** If your architecture's answer to "what if the model generates something malicious?" or "what if a tenant writes a hostile expression?" is "it runs in a sandbox," that answer just failed twice in a fortnight. This is the same lesson the [n8n expression-sandbox escapes](2025-11-n8n-ni8mare-rce.md), the [Flowise `eval`-on-LLM-output cluster](2026-04-flowise-rce-cluster.md), and the DEF CON Pyodide escapes point at from different directions.

**The dependency is invisible from above.** Most teams running n8n, Directus, or Budibase do not know they depend on `isolated-vm`, and it will not appear in the platform's own release notes as a security fix. **Neither advisory has a CVE**, so CVE-feed-driven scanning misses both entirely — you have to be watching GHSA directly, or watching your platform's patch releases closely enough to notice a transitive bump.

**n8n patched both in the same window**, alongside its own [nine-advisory batch on 2026-08-19](2025-11-n8n-ni8mare-rce.md) — which included two more first-party sandbox escapes to host RCE. If you run n8n, treat this as one upgrade event, not three.

## Am I affected?

```bash
# Direct or transitive dependency on either sandbox, and at what version?
npm ls isolated-vm vm2 --all 2>/dev/null
# Or, if you only have a lockfile:
grep -n -A2 '"\(isolated-vm\|vm2\)"' package-lock.json 2>/dev/null | head -40
```

Fixed versions:

- **`isolated-vm` → 7.0.1** (or **6.2.0** on the 6.x line). Anything **≤ 7.0.0** is affected.
- **`vm2` → 3.11.6**. Anything **≤ 3.11.5** is affected.

For `vm2` specifically, check whether you pass the wildcard, since that is the configuration the advisory describes:

```bash
grep -rn "builtin.*\[.*'\*'\|builtin.*\[.*\"\*\"" --include='*.js' --include='*.ts' . 2>/dev/null
```

If you run one of the named `isolated-vm` consumers — **n8n, Activepieces, Mastra, Budibase, Sim.ai, Directus** — upgrade the platform to a release that bumps the transitive dependency rather than trying to patch it underneath.

**Assessing whether you were hit is hard, and worth being honest about.** A successful escape leaves little in application logs by design. The vm2 DNS hijack is the more detectable of the two: look for **unexpected resolver configuration** on hosts running vm2, and for DNS queries from that process going somewhere other than your configured resolvers. Because `dns.setServers()` persists process-wide, **restart the affected Node process after patching** — patching the library does not undo a resolver change already made in a running process. If you cannot rule out exploitation on a host that ran untrusted code, treat every credential that host held as in scope.

## If you are affected

- [If your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md)
- [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) — a host-process escape reaches every credential in that process's environment, not just the sandboxed job's inputs.
- [If your web app was compromised](../playbooks/if-your-webapp-was-compromised.md)

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md)
- [Package vetting checklist](../prevention/package-vetting-checklist.md)
- [Supply-chain attack surface](../prevention/supply-chain-attack-surface.md)

Practical guidance: put an **OS-level boundary** (container, VM, seccomp, separate process with dropped privileges) beneath any in-process JS sandbox running untrusted or model-generated code, so a single library bug is not the only thing between a hostile expression and your host. And **watch GHSA, not just CVE feeds** — both of these would have been invisible to CVE-driven tooling.

## Sources

- [GitHub Security Advisory — GHSA-864f-rcv7-6rh4 (isolated-vm)](https://github.com/laverdet/isolated-vm/security/advisories/GHSA-864f-rcv7-6rh4) — fetched directly: Critical severity, published 2026-08-07, affected ≤ 7.0.0, patched 7.0.1 / 6.2.0, no CVE assigned, and the double-walk / *"An index getter therefore fires once per walk and can answer differently each time"* root cause plus the unchecked `As<ArrayBuffer>()` cast.
- [GitHub Advisory Database — GHSA-m5w8-4gq2-6f8x (vm2)](https://github.com/advisories/GHSA-m5w8-4gq2-6f8x) — fetched directly: Critical, CVSS 9.3, published 2026-08-14, affected ≤ 3.11.5, patched 3.11.6, no CVE assigned; the incomplete-prior-fix framing, the `os`/`dns` read and write method inventory, the readonly-proxy-forwards-method-calls mechanism, the *"every subsequent DNS lookup the host process performs … goes through the attacker's resolver"* impact, and the `DANGEROUS_BUILTINS` fix.
- [Endor Labs — GHSA-864f-rcv7-6rh4: Critical Type Confusion Vulnerability in isolated-vm](https://www.endorlabs.com/learn/ghsa-864f-rcv7-6rh4-critical-type-confusion-vulnerability-in-isolated-vm) — independent research writeup: escalation to fake-vtable host control-flow hijack, the `DisallowJavascriptExecutionScope` fix, discovery credit to Cristian-Alexandru Staicu, and the named downstream consumers (n8n, Activepieces, Mastra, Budibase, Sim.ai, Directus).
- [OX Security — Critical vm2 Vulnerability Allows Host DNS Hijacking and Information Disclosure](https://www.ox.security/blog/critical-vm2-vulnerability-allows-host-dns-hijacking-and-information-disclosure/) — independent corroboration of the vm2 finding and its relevance to low-code platforms, webhook/rules executors, plugin systems, and CI job runners.
- [The Hacker News — isolated-vm Flaw Lets Sandboxed Code Escape](https://thehackernews.com/2026/08/isolated-vm-flaw-lets-sandboxed.html) — independent press confirmation of the isolated-vm finding.
