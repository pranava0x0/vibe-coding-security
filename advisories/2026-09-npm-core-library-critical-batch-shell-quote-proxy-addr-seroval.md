---
id: 2026-09-npm-core-library-critical-batch-shell-quote-proxy-addr-seroval
title: "Three critical advisories in npm libraries almost every generated Node app ships without knowing — shell-quote's quote() emits a `#` comment token that a later string's newline terminates, re-opening the line to injection (CVE-2026-102422, 9.2; 96.9M weekly downloads); proxy-addr, which backs Express's req.ip, treats an IPv4-mapped IPv6 trust subnet like `::ffff:10.0.0.0/8` as matching every IPv4 address, so any client is a trusted proxy and can spoof X-Forwarded-For past rate limits and IP allow-lists (CVE-2026-90711, 9.1; 137M weekly); seroval's fromJSON() lets a fulfilled Promise node invoke plugin-produced callables through native thenable assimilation, bypassing a prior fix (CVE-2026-104846, 9.8; 37.5M weekly) — all three fixed, all three surfaced in the advisory database only on 2026-10-05/06"
date_disclosed: 2026-09-15
last_updated: 2026-10-06
severity: high
status: patched
ecosystems: [npm, javascript, express, node]
tools_affected: ["shell-quote ≥ 1.8.4, < 1.11.0", "proxy-addr ≥ 1.1.0, < 2.0.8 (Express 4 and 5 depend on ^2.0.7, so a floating install resolves to the fix)", "seroval ≥ 0.12.0, ≤ 1.6.0 (SolidStart depends on ^1.6.0)", "any Express/Connect app with a `trust proxy` subnet written in ::ffff: notation", "any tool that builds shell commands from shell-quote parse() output plus untrusted strings"]
tags: [cve-batch, command-injection, ip-spoofing, rate-limit-bypass, deserialization, express, trust-proxy, npm, core-dependency, vendor-ghsa, database-backfill]
---

## TL;DR

Three unrelated maintainers fixed three unrelated criticals in September; the GitHub Advisory Database's reviewed `npm` critical listing put all three in front of this sweep on **2026-10-05 and 10-06**. They are grouped here because they share an audience — the generated Express/Node backend — rather than a root cause.

| Package (weekly downloads, week ending 10-04) | Bug | Id | Score | Affected → fixed | Vendor date → CVE → database |
|---|---|---|---|---|---|
| **shell-quote** (96,903,350) | `quote()` renders a `{ comment }` token as `#` plus text, which comments out the rest of the shell line — including the opening quote of the next string token. A line terminator (`\n`, `\r`, U+2028, U+2029) inside that later string ends the comment early and the remainder runs as shell. `parse()` emits comment tokens for `#` inside words, so a URL fragment is enough to set it up. | [GHSA-pqg4-j6r4-53mv](https://github.com/advisories/GHSA-pqg4-j6r4-53mv) / **CVE-2026-102422** | **9.2** (4.0) / 8.1 (3.1) | `≥ 1.8.4, < 1.11.0` → **1.11.0** | 2026-09-29 → 09-29 → 10-06 |
| **proxy-addr** (137,090,651) — the module behind Express's `req.ip` / `req.ips` and the `trust proxy` setting | A trust subnet "written in IPv4-mapped IPv6 notation with an IPv4-sized prefix" — `::ffff:10.0.0.0/8` — matches **all IPv4 addresses**, so "every unauthenticated client is then trusted as a proxy at hop 0" and can set `X-Forwarded-For` to any address, defeating IP allow-lists, per-IP rate limiting and audit logs. | [GHSA-jqcg-44mw-7w3h](https://github.com/advisories/GHSA-jqcg-44mw-7w3h) / **CVE-2026-90711** | **9.1** (3.1) | `≥ 1.1.0, < 2.0.8` → **2.0.8** | 2026-09-15 → 09-15 (OpenJS CNA) → 10-05 |
| **seroval** (37,545,257) — the serialiser SolidStart uses for server/client data | `fromJSON()` deserialising a fulfilled Promise control node "can trigger unintended invocation of a plugin-produced callable through native ECMAScript thenable assimilation" — a bypass of GHSA-mv8w-475r-vwqw (fixed 1.5.3); every plugin-capable release is in range. | [GHSA-p6vx-979v-rg4c](https://github.com/advisories/GHSA-p6vx-979v-rg4c) / **CVE-2026-104846** | **9.8** (3.1) | `≥ 0.12.0, ≤ 1.6.0` → **1.6.2** | 2026-09-19 → 10-02 → 10-05 |

**Severity `high` for the file** because each has a precondition the vendor spells out: shell-quote needs an application that concatenates `parse()` output with untrusted strings before `quote()`; proxy-addr needs the specific misconfiguration (a correct `10.0.0.0/8` is unaffected); seroval needs an application that deserialises untrusted `fromJSON()` input with plugins registered. Where the precondition holds, each is as bad as its number.

## What happened

**shell-quote.** The library exists to make shell commands safe to assemble, and it is what several agent command-guards use to tokenise what the model wants to run (this repo's [GuardFall](2026-06-guardfall-shell-injection-agents.md) entry credits Continue's guard with "shell-quote semantics" as the one that held up). The bug is in the round trip: `parse()` of a command whose URL argument ends in `#frag` yields a comment token for `#frag`; `quote([...parsed, untrusted])` prints `#frag` followed by the untrusted string, and if that string contains a newline, the shell stops treating the line as a comment at the newline and executes what follows. Finder euriconicacio; fix by ljharb in 1.11.0 (commit 6002b2ed). Affected from **1.8.4**, i.e. the versions that added comment tokens.

**proxy-addr.** Express's `app.set('trust proxy', …)` accepts CIDRs, and people behind a dual-stack load balancer write the IPv4-mapped form because that is what `req.socket.remoteAddress` shows them. proxy-addr parsed `::ffff:10.0.0.0/8` as an IPv6 /8 — which covers every `::ffff:*` address, i.e. every IPv4 client — rather than as an IPv4 /8. Reporters kagebunsher and kustundag; fix by UlisesGascon (commit 780911d). **Express 4 and 5 both depend on `proxy-addr ^2.0.7`** (checked 2026-10-06, express 5.2.1), so a fresh `npm install` or `npm update` picks up 2.0.8; a committed lockfile from before 09-15 does not.

**seroval.** A serialisation format that can carry Promises and plugin-defined types has to decide when deserialised values are allowed to run code; 1.5.3 closed one such path and 1.6.2 closes the thenable path that bypassed it (reporter Sicks3c, commit f1ffcc9). `@solidjs/start` depends on `seroval ^1.6.0` (checked 2026-10-06), so SolidStart projects float to the fix on reinstall; applications that call `fromJSON()` on data from a client or a cache are the exposed case, and a server framework's own use of the format is exactly that.

**The dating problem, again.** Vendor dates 09-15, 09-19 and 09-29; CVE records 09-15, 10-02, 09-29; database reviewed listings 10-05 and 10-06. The dates in this file's frontmatter and table are the vendors'.

## Am I affected?

```bash
npm ls shell-quote proxy-addr seroval --all 2>/dev/null | head -30
grep -n '"shell-quote"\|"proxy-addr"\|"seroval"' package-lock.json 2>/dev/null | head
# proxy-addr: the misconfiguration is the trigger
grep -rn "trust proxy\|trustProxy\|trust_proxy" --include='*.js' --include='*.ts' --include='*.json' . 2>/dev/null | grep -i '::ffff'
# shell-quote: parse() output recombined with other input
grep -rn "shell-quote\|shellQuote\|quote(" --include='*.js' --include='*.ts' src/ 2>/dev/null | head
# seroval: untrusted fromJSON
grep -rn "fromJSON(" --include='*.js' --include='*.ts' src/ 2>/dev/null | head
```

- **proxy-addr < 2.0.8 with a `::ffff:` subnet in `trust proxy`** → every client can spoof its IP to your rate limiter, allow-list and logs. Same version with a plain IPv4 CIDR, `true`, `loopback` or a hop count → not this bug.
- **shell-quote 1.8.4–1.10.x** in anything that assembles commands from mixed trusted/untrusted tokens — CLI wrappers, task runners, agent command guards that re-serialise what they parsed.
- **seroval ≤ 1.6.0** where `fromJSON()` receives data an attacker could have produced.

## If you are affected

1. **Update the three packages** (`npm update shell-quote proxy-addr seroval`, then check `npm ls` shows ≥ 1.11.0 / ≥ 2.0.8 / ≥ 1.6.2); regenerate the lockfile with the repo's package manager, not by hand.
2. **Rewrite the `trust proxy` setting** as an IPv4 CIDR or a hop count regardless of version — the IPv4-mapped form was never what you meant — and then **re-check anything that relied on `req.ip`** during the exposed window: rate-limit counters that never tripped, admin allow-lists that admitted the wrong network, audit logs whose client IPs are attacker-chosen. [if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md).
3. For shell-quote consumers, **stop combining `parse()` output with raw strings**; quote each untrusted value on its own and never pass a value containing a line terminator to a shell — the fix stops this one encoding, not the design.
4. For seroval, treat `fromJSON()` of client-supplied data as deserialisation of untrusted input: validate the shape first, and keep plugins out of that path.

## Prevention

- The lockfile is the attack surface here: all three fixes were out for two to seven weeks before the database listed them, and a project whose `package-lock.json` has not been regenerated since September still ships every one — [prevention/npm-hardening.md](../prevention/npm-hardening.md), [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- Rate limiting and IP allow-listing that trust `X-Forwarded-For` are only as strong as the proxy configuration; test them from outside the trusted network with a forged header once, and again after every proxy change — [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- A library that "makes shell commands safe" is a reason to still not build shell commands from strings; `execFile` with an argument vector has no quoting layer to bypass.

## Why this matters for vibe coders

The generated Express app gets `app.set('trust proxy', …)` from whatever the deployment docs said, a rate limiter keyed on `req.ip` in front of the login route, and a lockfile committed on day one. Nobody in that story knows the words proxy-addr, and the first sign of the bug is a credential-stuffing run that the rate limiter counted as a million different clients. The other two are the same shape one layer down: a quoting helper in a build script and a serialiser in the framework, each a transitive dependency with a critical nobody saw because the listing was six weeks late.

## Sources

- [GHSA-pqg4-j6r4-53mv — shell-quote: `quote()` command injection via a line terminator in a token after a `{ comment }` token (CVE-2026-102422)](https://github.com/advisories/GHSA-pqg4-j6r4-53mv) — fetched 2026-10-06: 9.2 `CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H`, `≥ 1.8.4, < 1.11.0` → 1.11.0, the comment-token mechanism and the `parse()`-emits-comments-for-URL-fragments note, finder euriconicacio, remediation ljharb, published 2026-09-29.
- [GHSA-jqcg-44mw-7w3h — proxy-addr vulnerable to IP spoofing via IPv4-mapped IPv6 trust subnet (CVE-2026-90711)](https://github.com/advisories/GHSA-jqcg-44mw-7w3h) — fetched 2026-10-06: 9.1 `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`, `≥ 1.1.0, < 2.0.8` → 2.0.8, the `::ffff:10.0.0.0/8` example, "every unauthenticated client is then trusted as a proxy at hop 0," reporters kagebunsher and kustundag, remediation UlisesGascon, commit 780911d, published 2026-09-15.
- [GHSA-p6vx-979v-rg4c — Seroval: `fromJSON()` Promise thenable assimilation invokes plugin-produced callables (CVE-2026-104846)](https://github.com/advisories/GHSA-p6vx-979v-rg4c) — fetched 2026-10-06: 9.8 `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`, `≥ 0.12.0, ≤ 1.6.0` → 1.6.2, bypass of GHSA-mv8w-475r-vwqw (1.5.3), reporter Sicks3c, commit f1ffcc9, published 2026-09-19.
- [NVD API — CVE-2026-102422, CVE-2026-90711, CVE-2026-104846](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-90711) — fetched 2026-10-06: shell-quote CNA 9.2 (4.0) / 8.1 (3.1), published 2026-09-29; proxy-addr CNA OpenJS Foundation 9.1, published 2026-09-15, references `cna.openjsf.org/security-advisories.html`; seroval CNA GitHub 9.8, published 2026-10-02.
- [npm registry — dependency pins](https://registry.npmjs.org/express) — queried 2026-10-06 via `npm view`: `express@5.2.1` → `proxy-addr ^2.0.7`; `@solidjs/start` → `seroval ^1.6.0`; `latest`: proxy-addr 2.0.8, shell-quote 1.11.0 or later, seroval 1.6.8.
- [npm downloads API — week ending 2026-10-04](https://api.npmjs.org/downloads/point/last-week/proxy-addr) — shell-quote 96,903,350; proxy-addr 137,090,651; seroval 37,545,257.
- [GitHub Advisory Database — reviewed `npm` critical listing](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical) — fetched 2026-10-06: shell-quote listed Oct 6; proxy-addr and seroval Oct 5 (database dates).
- Related in this repo: [GuardFall — shell-quote semantics in agent command guards](2026-06-guardfall-shell-injection-agents.md), [DirtyBlanket Express typosquat worm](2026-09-dirtyblanket-npm-express-typosquat-linux-ssh-worm.md), [simple-git denylist bypasses](2026-09-simple-git-unsafe-operations-guard-bypass-cve-batch.md).
