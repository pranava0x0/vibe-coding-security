---
id: 2026-08-vm2-isolated-vm-sandbox-escapes
title: "Both JavaScript sandboxes that AI workflow platforms run untrusted code in broke in the same fortnight — vm2 (host DNS hijack) and isolated-vm (type confusion → host RCE), August 2026"
date_disclosed: 2026-08-07
last_updated: 2026-09-20
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

### Update 2026-09-17 — vm2 shipped ten more advisories in three weeks (2026-08-24 → 09-08), six of them critical host RCE; VulnCheck assigned CVEs on 2026-09-17; the fix line is now **3.12.2**

The 3.11.6 fix above was the start, not the end. vm2's advisory tab now carries ten further entries between 2026-08-24 and 2026-09-08, and the npm `time` field shows the matching release cadence — **3.11.7 (08-24), 3.11.8 (08-27), 3.12.0 (09-01), 3.12.1 (09-03), 3.12.2 (09-08)**. On **2026-09-17** VulnCheck published CVEs for six of them; the vendor advisories themselves still read "No known CVE." Fetched from the vendor advisory pages and VulnCheck:

- **GHSA-8hr7-r645-pc6w / CVE-2026-92935** (VulnCheck CVSS **9.5**, published 08-24): the NodeVM `require` option guard checks `typeof === 'object' && !== null`, which **accepts arrays**; an array-shaped `require` with `nesting: true` lets sandboxed code require the host `vm2` module and build a nested NodeVM with `child_process` — host command execution. Affects **≥ 3.11.4, < 3.11.7**. Credit lexdotdev.
- **GHSA-x965-fc75-jpqh / CVE-2026-92934** (vendor CVSS 9.0, VulnCheck **9.5**, published 08-27): an **incomplete fix for `Error.cause` sanitisation** — a host-wrapped `AggregateError` revisited within one exception-handling walk (self-cycle, mutual cycle or duplicate reference) short-circuits `handleException`'s cycle check and returns **unsanitised host proxies in the `errors` array**: host RCE plus `process.env`. Affects **≤ 3.11.7**, fixed **3.11.8**. Credit zx (Jace) and maru1009.
- **GHSA-r273-hxvj-fxhp / CVE-2026-92933** (Moderate, 08-27): `util.getCallSites()` bypasses host-frame redaction and leaks the host call stack. Fixed 3.11.8.
- **GHSA-j89j-5m6r-cr2q** (vendor CVSS **10.0**, 09-03): calling a **non-strict (sloppy-mode) host function** the embedder exposed, with no receiver, makes V8 bind `this` to the host global object, which vm2 returned **unwrapped** — "a live proxy of the host global," hence `process` and RCE. Only strict-mode/ESM host functions were safe. Affects **≤ 3.12.0**, fixed **3.12.1**. Credit RajChowdhury240.
- **GHSA-pq68-rvw4-xp4r** (10.0, 09-03): the hardened builtin denylist that blocks `cluster`, `worker_threads` and `vm` **omitted `child_process`**, so `require:{builtin:['*']}` gave `require('child_process').execSync(...)`. Fixed 3.12.1. (The exact `builtin:['*']` configuration that the August `os`/`dns` finding above already showed to be unsafe.)
- **GHSA-6454-5x88-m6jw** (10.0, 09-03): host-realm Promises crossing the bridge — hijack `Symbol.species` on the host Promise and call `.then()` without an `onRejected`, and V8's internal Thrower re-throws the **raw host rejection** into the sandbox. Fixed 3.12.1.
- **GHSA-x3v6-43hc-82mc** (High, 09-03): the NodeVM `crypto` sanitiser exposed process-wide `crypto.setFips`. Fixed 3.12.1.
- **GHSA-5h3f-q97h-ccvc** (10.0, 09-08): NodeVM's **custom module resolver** stored allow-listed paths as raw string prefixes, so after requiring an allowed module a guest could `require` an absolute path to a **prefix-sharing sibling file** never allow-listed — code execution in the host process. Affects **≤ 3.12.1**, fixed **3.12.2**. Credit @rexpository.
- **GHSA-489w-w794-jq94** (Critical, 09-08): NodeVM `zlib` Buffers exposed **pooled host memory** across the VM boundary. **GHSA-2v2p-6j97-cjg9** (High, 09-08): a host Promise rejection from an exposed constructor terminates the host. Both fixed 3.12.2.
- VulnCheck's 09-17 batch also lists **CVE-2026-92937** ("3.11.6 remote code execution via Promise call/apply"), **CVE-2026-92938** ("3.11.3 through 3.11.6 remote code execution via node:sqlite") and **CVE-2026-92936** ("3.11.0 before 3.11.7 information disclosure via error stack") — VulnCheck's advisory pages for these three returned 404 to this sweep; the ids and version ranges are as printed on VulnCheck's advisory index, not verified against a per-CVE page.

**What changed in the reading.** In August the finding was "two sandboxes broke in a fortnight." By mid-September it is that **vm2's bridge is being taken apart primitive by primitive** — error objects, Promises, `this` binding, the module resolver, `Buffer` pools — by at least six independent reporters, with a critical escape landing roughly weekly and each fix revealing the next incomplete sanitiser. The maintainer's own advisory text for CVE-2026-92934 says "incomplete fix." For any product whose untrusted-code story is "vm2" — including everything in `tools_affected` above — the practical position is: the current version is the *minimum*, an OS-level boundary beneath it is the *control*, and the 2026-09-17 CVE assignments mean CVE-driven scanners will finally flag versions below **3.11.8** (and nothing yet for the 3.12.x fixes, which still carry no CVE).

```bash
# What vm2 do you actually run (transitively)?
npm ls vm2 2>/dev/null | grep vm2
# Below 3.12.2 = at least one unfixed vendor advisory; below 3.11.8 = a CVE
```

### Update 2026-09-20 — an eleventh advisory from the same window: the host's `https.globalAgent` is exposed to the sandbox, leaking Authorization headers and plaintext TLS socket data (GHSA-h85j-hv3c-qfgq / CVE-2026-92940, CVSS 10.0; 3.11.3–3.11.6, fixed 3.11.7)

The 09-17 list above missed one vendor advisory dated **2026-08-24** (reporter Forrof), which VulnCheck CVE'd on **2026-09-17** as **CVE-2026-92940** (database copy GHSA-5843-9mh5-hhgw; CVSS 3.1 vector `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L`). When a NodeVM is configured to allow `https`, vm2 exposed the **process-wide `https.globalAgent` singleton**. It was wrapped read-only, but the agent is an EventEmitter whose *methods* mutate state, and the read-only proxy forwards method calls — so sandboxed code could call `Agent.prototype.on()` and register a listener on the agent's `free` event. From there it captured the host's **Authorization headers and other sensitive request headers, private destination hostnames and ports, and plaintext data on reused TLS sockets**, and could make authenticated requests with the stolen credentials. Affects **≥ 3.11.3, ≤ 3.11.6**; fixed **3.11.7** (npm 2026-08-24). The root cause is the same one as the August `os`/`dns` finding: a process-global object handed to the guest instead of a sandbox-local instance. For a multi-tenant workflow platform this is cross-tenant credential theft without any host RCE at all — which is why it scores 10.0 while "only" reading. `vm2` still pulled ~824K downloads in the week to 2026-09-19.

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
- [patriksimek/vm2 — security advisories index](https://github.com/patriksimek/vm2/security/advisories) — fetched 2026-09-17; the ten advisories 2026-08-24 → 09-08 with severities and titles (no CVEs shown on the vendor page).
- [vm2 — GHSA-x965-fc75-jpqh (AggregateError sanitisation bypass)](https://github.com/patriksimek/vm2/security/advisories/GHSA-x965-fc75-jpqh), [GHSA-j89j-5m6r-cr2q (nullish receiver on non-strict host function)](https://github.com/patriksimek/vm2/security/advisories/GHSA-j89j-5m6r-cr2q), [GHSA-pq68-rvw4-xp4r (child_process omitted from denylist)](https://github.com/patriksimek/vm2/security/advisories/GHSA-pq68-rvw4-xp4r), [GHSA-6454-5x88-m6jw (Symbol.species / onRejected)](https://github.com/patriksimek/vm2/security/advisories/GHSA-6454-5x88-m6jw), [GHSA-5h3f-q97h-ccvc (custom resolver prefix bypass)](https://github.com/patriksimek/vm2/security/advisories/GHSA-5h3f-q97h-ccvc) — all fetched 2026-09-17; affected/patched versions, CVSS and credits as quoted in the 2026-09-17 update.
- [VulnCheck — vm2 before 3.11.8 Sandbox Escape RCE via AggregateError (CVE-2026-92934)](https://www.vulncheck.com/advisories/vm2-before-3.11.8-sandbox-escape-rce-via-aggregateerror) and [vm2 NodeVM Remote Code Execution via Array-Shaped Require (CVE-2026-92935)](https://www.vulncheck.com/advisories/vm2-nodevm-remote-code-execution-via-array-shaped-require) — fetched 2026-09-17; published 2026-09-17, CVSS 9.5 each, version ranges; the [VulnCheck advisory index](https://www.vulncheck.com/advisories) (fetched 2026-09-17) lists the sibling CVE-2026-92933, CVE-2026-92936, CVE-2026-92937 and CVE-2026-92938 entries.
- [vm2 — GHSA-h85j-hv3c-qfgq: vm2 3.11.6 exposes host HTTPS credentials and TLS traffic through globalAgent](https://github.com/patriksimek/vm2/security/advisories/GHSA-h85j-hv3c-qfgq) — vendor advisory, published 2026-08-24: CVSS 10.0 vector, ≥ 3.11.3 ≤ 3.11.6 → 3.11.7, the `free`-event listener mechanism, reporter Forrof. Fetched 2026-09-20.
- [GitHub Advisory Database — GHSA-5843-9mh5-hhgw (CVE-2026-92940)](https://github.com/advisories/GHSA-5843-9mh5-hhgw) — VulnCheck-sourced copy published 2026-09-17; `Agent.prototype.on()` detail, CVSS 4.0 10.0. Fetched 2026-09-20.
- npm registry `time` field for `vm2` (via `npm view vm2 time`, 2026-09-17): 3.11.6 2026-08-14, 3.11.7 08-24, 3.11.8 08-27, 3.12.0 09-01, 3.12.1 09-03, 3.12.2 09-08.
