---
id: 2026-08-tinypool-prototype-pollution-worker-rce
title: "Tinypool (the worker-thread pool under Vitest 1–3; 59.6M weekly downloads): two prototype-pollution-to-code-execution gadgets — worker options spread from a polluted Object.prototype into `new Worker()` so an inherited `execArgv: ['--require', …]` or `env.NODE_OPTIONS` runs in every worker (CVE-2026-104848), and `pool.run(task, options)` reads `filename` through the prototype chain so a polluted `Object.prototype.filename` swaps the worker module (CVE-2026-104849); both scored 9.5, both fixed 2026-08-23 (2.1.1 / 2.1.2), both reached the GitHub Advisory Database on 2026-10-05 — and Vitest 2.x and 3.x pin tinypool ^1.x, which has no patched release"
date_disclosed: 2026-08-30
last_updated: 2026-10-06
severity: high
status: patched
ecosystems: [npm, javascript, testing, ci-cd]
tools_affected: ["tinypool ≤ 2.1.0 (CVE-2026-104848), < 2.1.2 (CVE-2026-104849) — including every 1.x and 0.x release", "Vitest 3.x (pins tinypool ^1.1.1), 2.x (^1.0.1), 1.x (^0.8.3)", "any Node.js service that uses tinypool to run work on behalf of requests and has a prototype-pollution bug anywhere in its dependency graph"]
tags: [cve, prototype-pollution, gadget, rce, worker-threads, vitest, testing, ci-cd, npm, vendor-ghsa, database-backfill, no-fix-for-major]
---

## TL;DR

**tinypool** is the minimal `worker_threads` pool that Vitest spun out of piscina; it moved **59,633,803 copies in the week ending 2026-10-04**, and Vitest itself **142,142,023**. On **2026-08-30** its maintainers published two advisories, each a **prototype-pollution gadget**: tinypool does not pollute anything itself, but if any other code in the process has already written to `Object.prototype`, tinypool turns that into **code execution inside every worker it spawns**, "with the privileges of the host process."

- **[GHSA-5gmw-xhrv-c9v3](https://github.com/advisories/GHSA-5gmw-xhrv-c9v3) / CVE-2026-104848** — `ThreadPool.options` is built with object spread from a normal options object, which **materialises inherited properties as own properties**, and `execArgv` and `env` are then handed to `new Worker()`. Node's own protection against inherited worker options is defeated. A polluted `Object.prototype.execArgv = ['--require', '/path/attacker.js']` or `Object.prototype.env = { NODE_OPTIONS: … }` executes in each worker. **≤ 2.1.0 → 2.1.1.** CVSS 4.0 **9.5**. Reporter ambushneupane; PR #134.
- **[GHSA-85c8-ppgw-ccpr](https://github.com/advisories/GHSA-85c8-ppgw-ccpr) / CVE-2026-104849** — `pool.run(task, options)` reads `options.filename` without requiring an own property, so a polluted `Object.prototype.filename` "can replace the intended worker module." Only triggers when the caller passes its own options object to `run()`; inherited from piscina. **< 2.1.2 → 2.1.2.** CVSS 4.0 **9.5**. Reporter Fcmam5; PR #135.

The registry shows **2.1.1 at 2026-08-23 14:26 UTC and 2.1.2 at 15:03 UTC**; the advisories followed a week later, the CVE records on **2026-10-02**, and the database's reviewed `npm` critical listing on **10-05** — which is how a six-week-old fix looked like a fresh wave. **The problem for Vitest users:** the affected range is everything below 2.1.1, there is **no 1.x or 0.x patch** (the version list goes 1.1.1 → 2.0.0), and `npm view` on 2026-10-06 shows **Vitest 3.2.x pinning `tinypool: ^1.1.1`, 2.1.x `^1.0.1`, 1.6.x `^0.8.3`**; Vitest 4.x and 5.x do not list tinypool as a dependency at all. So `npm update` fixes a direct tinypool dependency and fixes nothing for a Vitest 1–3 project; the fix there is Vitest 4+.

## What happened

**Why "gadget" and why `high` rather than the vendor's critical.** Both advisories require a *prior* prototype pollution — an unrelated bug in a merge, deep-clone, query-string or config library — before tinypool does anything wrong. The vendor scores them 9.5 with `AT:P` (attack requirements present) to encode exactly that; this repo's severity reflects that an attacker needs two bugs, not one, while the consequence (arbitrary code in a process that may hold CI secrets or a service's credentials) is the full one. If your dependency graph has a known prototype-pollution CVE, treat this as critical; the gadget is what makes a "low-impact" pollution finding exploitable.

**The mechanism, in the vendor's words.** For CVE-2026-104848: "Tinypool constructs ThreadPool.options from a normal options object and reads the execArgv and env worker options … allowing values inherited from a polluted Object.prototype to reach `new Worker()`." The root cause is the spread (`{...options}`), which copies inherited keys onto a fresh object — after which Node's check that worker options are own properties sees own properties. For CVE-2026-104849: "If that object does not have an own `filename` property, the lookup falls through to `Object.prototype`." The limitation is real: calls to `run()` without a second argument use tinypool's trusted default and are not affected.

**Where it sits.** Vitest's default `pool: 'threads'` and `'forks'` runners used tinypool through 3.x; Vitest's own advisory tab (fetched 2026-10-06) does not carry an entry for either CVE, and the GHSA for CVE-2026-104848 is the source for "tinypool's role in Vitest (~42M weekly downloads)" — the registry figure is now 142M. Tinypool is also used directly by servers that offload CPU-bound work per request, which is the deployment where an attacker-reachable prototype pollution is most likely to exist in the same process.

## Am I affected?

```bash
npm ls tinypool vitest --all 2>/dev/null | head -20
grep -n '"tinypool"' package-lock.json 2>/dev/null | head
# Which Vitest line pins which tinypool range (2026-10-06 values: 3.x ^1.1.1, 2.x ^1.0.1, 1.x ^0.8.3; 4.x/5.x none)
npm view vitest@3 dependencies.tinypool
# Known prototype-pollution findings elsewhere in the tree — the first half of the chain:
npm audit --json 2>/dev/null | grep -i -c 'prototype pollution'
```

- Direct dependency on tinypool **< 2.1.2** → affected by both; **2.1.1** → still CVE-2026-104849.
- **Vitest 1.x–3.x** → tinypool 0.x/1.x in the tree, no in-range fix. The practical exposure in a test runner is a polluted prototype inside the Vitest main process — a malicious dependency, a test that imports untrusted fixtures, or a vulnerable transitive library — which then runs code in every test worker with the CI job's credentials.
- **Vitest 4.x / 5.x** → tinypool is not a listed dependency (checked `vitest@4.1.11`, `vitest@5.0.3`, and `@vitest/runner` for both).

## If you are affected

1. **Direct users: upgrade to `tinypool@2.2.0`** (latest; 2.1.2 is the minimum). **Vitest 1–3 users: upgrade Vitest to 4.x or later**; there is no tinypool release that satisfies `^1.1.1` and carries the fix, and overriding the transitive version to 2.x is a major bump tinypool's API may not honour — test it rather than assume.
2. Until then, **fix the first half of the chain**: run `npm audit`, remove or upgrade anything with a prototype-pollution finding, and freeze `Object.prototype` at process start in services where that is viable (`Object.freeze(Object.prototype)` breaks some libraries; measure).
3. In CI, this is a reason to keep test jobs on **short-lived, minimally scoped tokens** — code running in a Vitest worker has whatever the job has — [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
4. If a service that used tinypool per request also had an exploitable pollution, treat it as a code-execution incident: [if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md), then [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Treat prototype-pollution findings as code execution until proven otherwise; gadgets like this one, in libraries nobody audits, are why — [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- When a security fix lands only in a new major of a transitive dependency, the fix has not reached you until the package that pins it moves; check `npm ls` for the installed version, not the advisory's "patched" line — [prevention/npm-hardening.md](../prevention/npm-hardening.md).
- Vendor advisories, CVE records and database listings for the same bug were six weeks apart here; the registry `time` field is the one date that does not move.

## Why this matters for vibe coders

Vitest is the test runner agents reach for in generated TypeScript projects, and the CI job that runs it usually holds a deploy token. The chain is: a dependency the agent added has a prototype-pollution bug, a test imports a fixture that triggers it, tinypool spawns the next worker with an inherited `--require`, and the deploy token leaves the runner. None of the three pieces is exotic, and the fix for two of them is a major-version upgrade nobody asked the agent to do.

## Sources

- [GHSA-5gmw-xhrv-c9v3 — Tinypool: Prototype Pollution gadget in worker options leads to Remote Code Execution (CVE-2026-104848)](https://github.com/advisories/GHSA-5gmw-xhrv-c9v3) — fetched 2026-10-06: 9.5 `CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H`, `≤ 2.1.0` → 2.1.1, the spread-materialises-inherited-properties root cause, the `execArgv` `--require` and `env.NODE_OPTIONS` vectors, "arbitrary code execution inside every worker the pool spawns, with the privileges of the host process," the "~42M weekly downloads" Vitest reference, reporter ambushneupane, PR tinylibs/tinypool#134, published 2026-08-30.
- [GHSA-85c8-ppgw-ccpr — Tinypool: Prototype Pollution Gadget to RCE in run() options (CVE-2026-104849)](https://github.com/advisories/GHSA-85c8-ppgw-ccpr) — fetched 2026-10-06: 9.5, `< 2.1.2` → 2.1.2, "falls through to `Object.prototype`," the own-options-object precondition, piscina lineage, reporter Fcmam5, PR #135, commit f41411a3, published 2026-08-30.
- [NVD API — CVE-2026-104848, CVE-2026-104849](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-104848) — fetched 2026-10-06: both published 2026-10-02 by `security-advisories@github.com`, 9.5 (4.0), status Deferred, references to commits 24df4e73 / f41411a3, PRs #134 / #135 and release tags v2.1.1 / v2.1.2.
- [tinylibs/tinypool — release v2.1.1](https://github.com/tinylibs/tinypool/releases/tag/v2.1.1) — fetched 2026-10-06: "guard worker options from proto pollution" (#134) referencing GHSA-5gmw-xhrv-c9v3. The page's rendered year is unreliable; the date below is the registry's.
- [npm registry — `tinypool` `time` and `versions`](https://registry.npmjs.org/tinypool) — queried 2026-10-06: 2.1.0 2026-01-03, **2.1.1 2026-08-23 14:26 UTC, 2.1.2 2026-08-23 15:03 UTC**, 2.2.0 2026-09-13; version list ends `1.0.2, 1.1.0, 1.1.1, 2.0.0, 2.1.0, 2.1.1, 2.1.2, 2.2.0` — no 1.x release after 1.1.1.
- [npm registry — `vitest` dependency pins](https://registry.npmjs.org/vitest) — queried 2026-10-06 via `npm view`: `vitest@3.2.4` → `tinypool ^1.1.1`; `vitest@2.1.9` → `^1.0.1`; `vitest@1.6.1` → `^0.8.3`; `vitest@4.1.11` and `vitest@5.0.3` list no tinypool dependency (nor does `@vitest/runner` at either version).
- [npm downloads API — `tinypool`, `vitest` (week ending 2026-10-04)](https://api.npmjs.org/downloads/point/last-week/tinypool) — 59,633,803 and 142,142,023.
- [vitest-dev/vitest — security advisories tab](https://github.com/vitest-dev/vitest/security/advisories) — fetched 2026-10-06: seven advisories, none for the tinypool CVEs.
- [GitHub Advisory Database — reviewed `npm` critical listing](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical) — fetched 2026-10-06: both tinypool entries listed Oct 5 (database date).
- Related in this repo: [Vitest browser-mode CDP RCE](2026-07-vitest-browser-mode-cdp-rce.md), [vm2 / isolated-vm sandbox escapes](2026-08-vm2-isolated-vm-sandbox-escapes.md).
