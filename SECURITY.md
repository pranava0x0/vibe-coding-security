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

**Last advisory sweep on these build deps:** 2026-05-17. (Refresh if >7 days old per the universal CLAUDE.md.)

## Site security headers

GitHub Pages provides HTTPS by default. We do not currently set custom security headers (CSP, HSTS, etc.) because GitHub Pages doesn't allow it. The static site has no JS that fetches user input, no forms, no third-party analytics, and no cookies — so the attack surface is minimal.

## Acknowledgements

Thanks to everyone who has reported issues responsibly.
