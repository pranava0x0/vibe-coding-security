# SECURITY.md

> Reporting a security issue with **this repo itself** (the website, build pipeline, or skill code). For incidents *tracked by* this repo, see [ALERTS.md](ALERTS.md) and [advisories/](advisories/).

## Supported versions

This is a living advisory tracker with no formal release cadence. The `main` branch is the only supported version. The deployed site at <https://pranava0x0.github.io/vibe-coding-security/> always reflects `main`.

## Reporting a vulnerability

Found a problem with this project? Two channels:

- **Private (preferred for security issues):** Open a private GitHub security advisory via the **Security tab** of the repo, or email the repo owner. We'll respond within 7 days.
- **Public (preferred for typos, bad links, factual corrections, false-positive advisories):** Open a regular GitHub issue.

What counts as a security issue *in this repo*:

- A malicious PR that snuck through (advisory bodies with smuggled scripts, fetch URLs pointing at attacker infrastructure, etc.).
- A false-positive advisory that could cause real-world harm (e.g., naming the wrong package as compromised).
- A vulnerability in the build pipeline that could let a contributor inject malicious content into the deployed site.
- A compromised maintainer account.

What doesn't count (just open a normal issue):

- Disagreements about severity ratings.
- Out-of-date advisories.
- Broken external links.
- Stylistic / typo fixes.

## Disclosure timeline

We follow a coordinated disclosure model:

1. Receive report.
2. Acknowledge within 7 days.
3. Investigate and reproduce within 14 days.
4. Patch + advise within 30 days where reasonable.
5. Public disclosure with credit to the reporter (if they want it).

## Dependency hygiene log

The `main` branch has no runtime dependencies. Build-time dependencies:

- `markdown==3.7`, `PyYAML==6.0.2`, `Pygments==2.18.0` ([requirements.txt](site/requirements.txt))
- All install scripts disabled where possible. See [prevention/npm-hardening.md](prevention/npm-hardening.md) for the discipline we apply.

**Last advisory sweep on these build deps:** 2026-11-06 (`pip index versions` for the four pins; see the self-audit section below for the hash-pinning note).

## Site security headers

GitHub Pages provides HTTPS by default. We do not currently set custom security headers (CSP, HSTS, etc.) because GitHub Pages doesn't allow it. The static site has no JS that fetches user input, no forms, no third-party analytics, and no cookies — so the attack surface is minimal.

## Self-audits with Cloudflare's security-audit skill

Since 2026-11-06 this repository audits its own build pipeline, tools, tests and workflows with a vendored copy of Cloudflare's open-source [`security-audit` skill](https://github.com/cloudflare/security-audit-skill) at [`.claude/skills/security-audit/`](.claude/skills/security-audit/UPSTREAM.md). The skill coordinates read-only reconnaissance and hunting agents, hands every candidate to an independent verifier, and writes `findings.json` checked by the skill's own validators; only a candidate with a complete source trace and a bounded observed result becomes `confirmed`. Target code runs only inside an OS-level sandbox (user, mount and network namespaces, read-only target, empty environment, resource limits).

- **Cadence:** a `quick` run on the build pipeline after any change to `site/`, `tools/`, `tests/` or `.github/workflows/`, and at least one run per quarter. The daily content sweep does not run it.
- **Where the results live:** every run's `REPORT.md`, `FINDINGS-DETAIL.md` and `NEEDS-VALIDATION.md` are published under [`security-audits/`](security-audits/), including rejected candidates, so the record shows what the tool found and what it did not.
- **How to run it here:** open Claude Code in this repository and ask for `/security-audit` on `site/ tools/ tests/ .github/` with the `quick` profile and an explicit agent budget; keep the output directory outside the tree, then copy the three reports into `security-audits/` with the date prefix. The audience-facing guide is [prevention/agent-security-audit.md](prevention/agent-security-audit.md).

## Acknowledgements

Thanks to everyone who has reported issues responsibly.
