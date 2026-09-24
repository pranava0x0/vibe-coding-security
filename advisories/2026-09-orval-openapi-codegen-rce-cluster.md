---
id: 2026-09-orval-openapi-codegen-rce-cluster
title: "orval — eleven critical code-injection CVEs (fixed 8.21.0) and then a second wave of twenty vendor advisories and five more CVEs across 8.28.1 → 8.37.0 in the OpenAPI → TypeScript client/zod/MSW generator: a hostile spec executes at codegen, at test time, or the moment the generated module is imported"
date_disclosed: 2026-07-12
last_updated: 2026-09-24
severity: high
status: patched
ecosystems: [npm, typescript, openapi, react-query, zod]
tools_affected: ["orval < 8.21.0 (July batch)", "orval < 8.37.0 (September wave)", "generated axios/fetch/react-query/swr clients", "generated zod schemas", "generated MSW mocks"]
tags: [cve, code-injection, codegen, openapi, template-literal, import-time-rce, supply-chain, agent-workflow]
---

## TL;DR

**orval** — the OpenAPI-to-TypeScript generator that emits axios/fetch clients, TanStack Query and SWR hooks, zod schemas and MSW mocks, at **~1.6 million weekly npm downloads** (registry API, week ending 2026-09-11) — carried **eleven critical (CVSS 9.3) code-injection CVEs**, all reported by the same researchers (Gal3m, mrostamipoor), all fixed in **8.21.0** (published to npm 2026-07-12), and all entering the GitHub Advisory Database on **2026-09-02/03** — which is why they surfaced in a recency-sorted sweep two months after the fix. The shape is uniform: orval interpolated spec-controlled strings (paths, `servers[].url`, property names, parameter names, `default` values) into generated code **without escaping**, so a backtick or `${…}` in a hostile OpenAPI document becomes live JavaScript. Three of the eleven fire when the generated request function is called; **eight fire at *import time*** of the generated zod or mock module — no request, no user action. If an agent or a developer ran `orval` against a spec they did not author, treat the generated output as attacker-supplied code.

## What happened

orval reads an OpenAPI document and writes TypeScript. Several emitters used template literals or single-quoted object keys and pasted spec strings straight in. The eleven advisories, all published on GitHub 2026-07-12 (advisory date) with database entries 2026-09-02/03:

| CVE | GHSA | Sink | When it executes |
|---|---|---|---|
| CVE-2026-62681 | GHSA-fg9p-mrxr-hvq7 | OpenAPI **path** → request-URL template literal | when the generated URL/request/query-key function runs |
| CVE-2026-62682 | GHSA-88f2-fpv8-89q2 | `servers[].url` → request-URL template literal | same |
| CVE-2026-71867 | GHSA-2w86-xfrc-g85r | schema **property name** → computed-property key (MSW mock) | when the mock factory is called |
| CVE-2026-71866 | GHSA-6mr6-jvcr-2f25 | schema property name → computed property (second sink) | import/call of the generated module |
| CVE-2026-71865 | GHSA-653q-5476-x79g | **query parameter name** → computed property | import time |
| CVE-2026-71864 | GHSA-6437-gxhq-pqv8 | **header parameter name** → computed property | import time |
| CVE-2026-72717 | GHSA-w727-8j6c-2rj4 | schema **`default`** → zod module-level template | **import time** |
| CVE-2026-71869 | GHSA-2h9g-j24r-h63g | array-items `default` → zod module-level | import time |
| CVE-2026-71871 | GHSA-8j6p-r8jg-mxqh | header-parameter `default` → zod module-level | import time |
| CVE-2026-71868 | GHSA-3575-w9fc-c2j6 | enum-typed `default` → zod module-level | import time |
| CVE-2026-72716 | GHSA-p4cg-3328-rvfg | query-parameter `default` → zod module-level | import time |

Three of these (62681, 72717, 71867) were fetched directly for this advisory and each states **affected < 8.21.0, patched 8.21.0**, CVSS 9.3, the same reporters, and the same remediation author; the other eight were read from the GitHub Advisory Database listing (titles, CVE ids, dates) and carry the same publication date — confirm the individual page before relying on a specific one. GHSA-w727-8j6c-2rj4 also records the NVD publication as 2026-08-19, i.e. these are **not** September bugs; the September date is when GitHub's curated database picked them up.

**Why import-time matters.** A generated zod schema with a poisoned `default` of the form `` v${<code>}w `` becomes a module-level template literal, evaluated the moment anything imports the schema file — a test runner, a Next.js route handler, a Storybook story, an agent "just checking types." The URL-template variants need a call; the zod and mock variants need only `import`.

**Who is exposed in practice.** The attacker must influence the OpenAPI document. That is a realistic path in exactly the workflows this repo covers: an AI coding agent told to "generate a typed client for this API" fetches a third-party spec and runs `orval` on it; a monorepo consumes a partner's published spec; a CI job regenerates clients from a URL on every build. It is not a remote-network bug against a running app.

## Am I affected?

```bash
# Which orval is installed / pinned?
npm ls orval 2>/dev/null | grep orval
grep -rn '"orval"' package.json */package.json 2>/dev/null
# July wave: vulnerable if < 8.21.0. September wave (see Update 2026-09-24): vulnerable if < 8.37.0. Current latest at time of writing: 8.37.0.

# Did any generated file get a template-literal or computed-key payload? (quick, imperfect heuristics on generated output)
grep -rnE '\$\{[^}]*(require|process|child_process|fetch|import)\b' src/api/ src/generated/ 2>/dev/null
grep -rnE "\['?\`|\`[^\`]*\$\{" --include='*.zod.ts' --include='*.msw.ts' -r . 2>/dev/null | grep -v node_modules | head

# Where do your specs come from? Anything fetched over the network at generate time is untrusted input.
grep -rnE 'input:\s*["'\'']https?://' orval.config.* 2>/dev/null
```

## If you are affected

1. Upgrade to **orval ≥ 8.37.0** (8.21.0 closed the July batch; the September wave runs to 8.37.0 — see the 2026-09-24 update) and regenerate every client, schema and mock from a spec you have reviewed.
2. If a pre-8.21.0 generation ran against a spec you did not control, diff the generated output for interpolated code and treat the environment that imported it (dev machine, CI runner, test container) as having executed untrusted code: → [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md) — the triage is the same as a malicious install hook.
3. → [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md) for repos where an agent produced the client code.

## Prevention

- → [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — an OpenAPI spec is an input to a code generator, so it is code; review it like a dependency before generating from it.
- → [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run codegen (and the tests that import its output) in the same sandbox you would give an unknown npm package; "generate a client for this URL" is a fetch-and-execute instruction.
- Commit generated code and review the diff on regeneration; a template literal appearing in a zod `default` is visible in review and invisible at runtime.
- The same bug class — spec/schema strings pasted into generated source — is worth checking in any other generator you use (openapi-typescript, openapi-generator, Prisma-adjacent schema tooling); the fix pattern is `JSON.stringify` on every interpolated string.

## Update 2026-09-24 — a second wave: twenty more vendor advisories (2026-09-06 → 09-23) across 8.28.1 → 8.37.0, five new VulnCheck CVEs on 09-23, and the same root cause every time — a spec string pasted into generated source

The July batch above (fixed 8.21.0) was not the end. Since **2026-09-06** orval's own advisory tab has published **twenty more** advisories, nearly all critical or high, nearly all "import-time" code execution from an unescaped OpenAPI value, and the fixes have shipped as a rolling series of releases — `8.28.0`/`8.28.1` (2026-09-03), `8.29.0` (09-06), `8.30.0` (09-07), `8.31.0` (09-10), `8.32.0` (09-12), `8.33.0` (09-13), then `8.34.0`–`8.37.0`, with **8.37.0 current** on 2026-09-24 (registry `time` field; the GitHub releases page's summaries mis-state the year as 2024). VulnCheck, as CNA, assigned **five CVEs on 2026-09-23** to the earliest of this wave, all CVSS 4.0 9.3:

| CVE | Component | Affected → fixed (VulnCheck index) |
|---|---|---|
| CVE-2026-96754 | `@orval/hono` — OpenAPI **path** in a single-quoted route literal (apostrophe injection, executes on import of the generated module) | `< 8.29.0` → 8.29.0 (vendor GHSA-g4mf-q5hw-f9j9) |
| CVE-2026-96755 | `@orval/effect` — code injection | `8.14.0 – 8.28.1` → 8.29.0 |
| CVE-2026-96756 | factory generation | `< 8.30.0` → 8.30.0 |
| CVE-2026-96757 | unescaped OpenAPI **media-type** key | `6.7.1 – 8.28.x` → 8.29.0 (vendor GHSA-4q3x-rqfw-3x8p) |
| CVE-2026-96758 | `@orval/core` form-data serializer — multipart **property names** (vendor GHSA-jwhm-6748-j6pq) | `< 8.28.0` → 8.28.0 |

NVD carries CVE-2026-96754 and CVE-2026-96758 at 9.3 Critical (published 2026-09-23). Two later vendor advisories, fetched directly, show the wave did not stop at 8.29/8.30: **GHSA-v263-cp2v-vrrx** (published 09-13, CVSS 9.8, `@orval/zod ≤ 8.32.0` → **8.33.0**, reporter zx / `@manus-pi`) — `resolveZodType` allow-listed array item types but "returns raw, unvalidated strings for scalar types," which are then "emitted directly into generated source code as method names," so a JavaScript payload in a schema's `type` field runs the moment the generated module is imported or bundled, "requiring no authentication or special configuration"; and **GHSA-w4x4-mpp4-4854** (published 09-23, CVSS 9.8, `@orval/core ≤ 8.36.0` → **8.37.0**, reporter zx / `@manus-use`) — `buildPrimitivePayload` used bare `String(enumValues[0])` instead of `JSON.stringify` for numeric/boolean enum members in the factory generator, import-time again, but gated on the opt-in `output.factoryMethods`. The other advisories in the vendor listing (titles as published): the `mutationInvalidates` path-key predicate and the combine generator's schema names (09-10, both critical); `@orval/mock` enum generation and array-items `const` (09-12, critical); `@orval/fetch` and `@orval/axios` response-status keys (09-13, high); `@orval/mock` (MSW) status keys and the zod/effect/faker numeric-length constraints (09-07, critical); date defaults and numeric `const` values (09-07, high); faker enum type-confusion, `@orval/fetch` content-type keys, `@orval/hono` single quotes, a three-generator import-time RCE (09-06, high); an `externalRefs.allow` bypass through HTTP redirects (09-07, moderate); and a build-time DoS in `@orval/mock` (09-18).

**What changed in the guidance.** "Upgrade to ≥ 8.21.0" is no longer sufficient — **upgrade to 8.37.0 or later**, and expect more: two different researchers have now fuzzed the same sink class across the generator and the maintainers have been fixing them one emitter at a time for three weeks (the reporter handle pattern suggests AI-assisted discovery, which is consistent with the pace). The practical rule stands and is now stronger: **an OpenAPI document you did not write is untrusted code**; regenerate only from reviewed specs, in a sandbox, and diff the generated output. orval pulled **1,635,805 downloads** in the week to 2026-09-21 — the population that runs `orval` in CI against a partner's spec URL on every build is the exposure.

## Sources

- [GitHub Advisory Database — GHSA-fg9p-mrxr-hvq7 (CVE-2026-62681)](https://github.com/advisories/GHSA-fg9p-mrxr-hvq7) — fetched 2026-09-12; path → template-literal injection, CVSS 9.3, < 8.21.0 → 8.21.0, published 2026-07-12, reporters Gal3m and mrostamipoor.
- [GitHub Advisory Database — GHSA-w727-8j6c-2rj4 (CVE-2026-72717)](https://github.com/advisories/GHSA-w727-8j6c-2rj4) — fetched 2026-09-12; schema-default → zod module-level template, import-time execution, NVD 2026-08-19, database entry 2026-09-03.
- [GitHub Advisory Database — GHSA-2w86-xfrc-g85r (CVE-2026-71867)](https://github.com/advisories/GHSA-2w86-xfrc-g85r) — fetched 2026-09-12; property-name → computed-property key in MSW mocks, fix via `JSON.stringify` escaping.
- [GitHub Advisory Database — reviewed npm critical advisories listing](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical) — fetched 2026-09-12; source for the remaining eight orval CVE/GHSA ids, titles and 2026-09-02/03 database dates.
- [npm registry — orval](https://registry.npmjs.org/orval) and [npm downloads API](https://api.npmjs.org/downloads/point/last-week/orval) — queried 2026-09-12; 8.21.0 published 2026-07-12, latest 8.32.0, 1,610,137 downloads for 2026-09-05 → 09-11.
- **2026-09-24 update sources** — [orval-labs/orval — Security Advisories index](https://github.com/orval-labs/orval/security/advisories) (pages 1–2, fetched 2026-09-24: the twenty advisories of 2026-09-06 → 09-23 with titles, severities and dates); [GHSA-v263-cp2v-vrrx](https://github.com/orval-labs/orval/security/advisories/GHSA-v263-cp2v-vrrx) and [GHSA-w4x4-mpp4-4854](https://github.com/orval-labs/orval/security/advisories/GHSA-w4x4-mpp4-4854) (vendor pages, fetched 2026-09-24: CVSS 9.8, affected/patched ranges, mechanisms, reporters); [GitHub Advisory Database — GHSA-4p56-cvjx-38fv (CVE-2026-96754)](https://github.com/advisories/GHSA-4p56-cvjx-38fv) and [GHSA-f2xw-gqvf-336w (CVE-2026-96758)](https://github.com/advisories/GHSA-f2xw-gqvf-336w) (fetched 2026-09-24; VulnCheck CNA, 9.3, descriptions quoted); [VulnCheck — advisories index](https://www.vulncheck.com/advisories) (fetched 2026-09-24: the five orval entries' titles and affected/fixed ranges); [NVD API — CVE-2026-96754](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-96754) and [CVE-2026-96758](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-96758) (queried 2026-09-24: published 2026-09-23, CVSS 4.0 9.3); [orval-labs/orval — releases](https://github.com/orval-labs/orval/releases) (fetched 2026-09-24; per-release advisory references — the page's year labels are wrong, the registry is authoritative); `npm view orval time` and [npm downloads API](https://api.npmjs.org/downloads/point/last-week/orval) (queried 2026-09-24: 8.28.0/8.28.1 2026-09-03, 8.29.0 09-06, 8.30.0 09-07, 8.31.0 09-10, latest 8.37.0; 1,635,805 downloads 2026-09-15 → 09-21).
