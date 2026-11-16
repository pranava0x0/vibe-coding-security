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

## Agent source audits (Cloudflare `security-audit` skill)

Cloudflare's open-source [`security-audit` skill](https://github.com/cloudflare/security-audit-skill) runs a multi-agent source audit. A full run launches at least four reconnaissance agents, hunters, a critic and a verifier, so it is used here rarely and on a narrow scope. This repository's executable surface is 2,574 lines of Python in `site/` and `tools/` (counted 2026-11-16) plus two workflows. The rest is Markdown.

**When to run it**

- Never as part of the daily content sweep. Advisories, `ALERTS.md` and the skill's own notes are content, not code.
- Run it in full audit mode with the `quick` profile when a pull request changes how text becomes published HTML or how a workflow holds credentials: the render path in `site/build.py`, `site/template.html`, `.github/workflows/`, or a tool that fetches from the network.
- Otherwise twice a year, in January and July, as a scoped `quick` run on `site/ tools/ .github/workflows/`.
- For a single question or one diff, use the skill's guidance mode. It does not run the six phases or write report files.

**How to run it**

- Set an agent budget in the request. The skill's minimum is four reconnaissance calls, one critic and one verifier, and it reports an incomplete run when the budget cannot cover more.
- Install the skill outside this repository, pinned to a reviewed commit, and keep the output directory outside this repository. Do not copy the skill into the tree.
- It does not check dependencies for known CVEs. The dependency log above stays a separate step.
- Check every finding the skill marks `confirmed` against the file and line it cites before acting on it.

**Record**

| Date | Mode | Scope | Result |
|---|---|---|---|
| 2026-11-06 | full audit, `quick` profile | build pipeline | Not completed. No report was published. One lead was checked by hand on 2026-11-16 and is tracked in [ISSUES.md](ISSUES.md): `site/build.py` renders Markdown with raw HTML passed through, and no test rejects active HTML in content. |

## Site security headers

GitHub Pages provides HTTPS by default. We do not currently set custom security headers (CSP, HSTS, etc.) because GitHub Pages doesn't allow it. The static site has no JS that fetches user input, no forms, no third-party analytics, and no cookies — so the attack surface is minimal.

## Acknowledgements

Thanks to everyone who has reported issues responsibly.
