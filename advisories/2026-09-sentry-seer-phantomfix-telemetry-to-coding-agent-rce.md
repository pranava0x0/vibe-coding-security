---
id: 2026-09-sentry-seer-phantomfix-telemetry-to-coding-agent-rce
title: "Sentry Seer \"PhantomFix\" (CVE-2026-90999, CVSS 9.8) — anyone who can post an error event to your public Sentry DSN can fabricate a bug, have Seer's root-cause analysis embed it into the prompt it hands your coding agent, and get the agent to install an attacker-chosen package; no vendor statement as of CERT/CC's 2026-09-16 note"
date_disclosed: 2026-09-16
last_updated: 2026-09-18
severity: critical
status: unconfirmed
ecosystems: [sentry, claude-code, cursor, github-copilot, ci-cd, ai-agents]
tools_affected: ["Sentry Seer (Issue Fix / Autofix) with coding-agent handoff enabled", "Claude Agent, Cursor Cloud Agent and GitHub Copilot Cloud Agent when driven by Seer", "any repository whose Sentry project exposes a browser DSN"]
tags: [cve, prompt-injection, observability, telemetry-injection, coding-agent, unauthenticated, rce, cert-cc, agentjacking-class]
---

## TL;DR
CERT/CC published **VU#212479 / CVE-2026-90999** on 2026-09-16 (CVSS 3.1 **9.8**, NVD; CWE-20/74/94/116/913): Sentry Seer, the AI debugging agent that finds a root cause and can **hand the issue to a coding agent for an automated fix**, is "vulnerable to a multi-stage trust-boundary violation that allows unauthenticated attacker-controlled telemetry to become code that is executed by an agent in a privileged automation environment." Browser apps ship a **public DSN** so that any visitor's errors reach Sentry; an attacker uses it to submit fabricated events, Seer analyses them, and the resulting "analysis" — with the attacker's narrative about which package is missing or broken — is embedded into the prompt sent to the integrated coding agent, which then installs or runs the attacker-controlled package with access to the connected source repositories. The reporters (Nikita Benkovich and Vitalii Valkov, agyn; the Hacker News submission calls it "PhantomFix") need no Sentry account, no repo access and no infrastructure. **Functional Software (Sentry) had not responded to CERT/CC** as of the note, and no fix, changelog entry or affected-version range exists. This is the Agentjacking/GhostJacking pattern — instructions planted in the data a developer's agent is asked to read — with one important difference: here the platform's own AI does the planting, and the handoff can be **fully automatic**.

## What happened

**The pipeline.** Sentry's docs describe Seer Issue Fix as root-cause analysis → solution → either Seer writes the patch or the user hands off to a coding agent: **Claude Agent** ("receives structured root cause and solution prompts"), **Cursor Cloud Agent** ("implements fixes asynchronously without requiring an open IDE") or **GitHub Copilot Cloud Agent** ("runs in GitHub Actions to generate fixes and open PRs"). Autofix runs **automatically** when an issue has 10+ events within 14 days and Seer's fixability score is high enough, up to whichever stop point the organisation configured (root cause / plan / PR drafted). None of those steps authenticates the *events*: Sentry's whole model is that a public DSN accepts telemetry from any browser.

**The injection.** CERT/CC: "Because Sentry front-end projects commonly expose a public DSN (Data Source Name) to allow browsers to submit this telemetry, an attacker can craft and submit malicious events through this public endpoint." Seer processes the attacker's events, and "the system embeds this fabricated analysis directly into prompts sent to integrated coding agents, which then interpret the malicious content as legitimate codebase information and execute attacker-controlled packages." The result is "arbitrary code execution within the coding-agent environment and access to connected source repositories." Ten crafted events clears the auto-trigger threshold; the fake stack trace does the rest.

**Why 9.8.** NVD's vector is AV:N/AC:L/PR:N/UI:N/C:H/I:H/A:H — network, no privileges, no user interaction — because in the automated configuration nobody reads the prompt before the agent acts on it. The weakness list (CWE-74 injection, CWE-94 code injection, CWE-913 improper control of dynamically-managed code resources) is NVD's, not this repo's.

**Vendor status.** CERT/CC lists Functional Software, Inc. with status *Unknown* and "no vendor statement received as of the notification date of August 13, 2026." The GitHub Advisory Database mirror (GHSA-vh55-q5m4-8wr6) carries "affected: unknown, patched: unknown." No Sentry changelog, blog or docs change referencing the CVE was found this sweep. Status here is **`unconfirmed`** in this repo's sense — one research team plus the CNA's own note, no vendor acknowledgement, no independent reproduction — but readers should act on the mitigation now, because the exposure is a configuration they control.

**Relationship to existing entries.** Sentry error data was already an injection channel in [Agentjacking (June 2026)](2026-06-agentjacking-sentry-mcp-injection.md) and [GhostJacking (August 2026)](2026-08-ghostjacking-firewall-log-injection.md), where the *developer's* agent read poisoned events through MCP. PhantomFix removes the developer from the loop: Seer reads the events, Seer writes the prompt, and Seer's handoff triggers the agent.

## Am I affected?

- You use Sentry Seer with **Issue Fix / Autofix automation** enabled past "Stop after Root Cause," **and** a coding-agent integration (Claude, Cursor Cloud Agent, GitHub Copilot Cloud Agent) is connected to the same repositories.
- Any of your Sentry projects has a DSN embedded in client-side code (every browser SDK does).

```bash
# DSNs shipped to browsers — each one is an unauthenticated write path into Seer's input
grep -rnoE '[0-9a-f]{32}@o[0-9]+\.ingest(\.[a-z]+)?\.sentry\.io/[0-9]+' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.html' . 2>/dev/null | head   # a DSN's public key + ingest host
# Sentry org settings to check by hand: Seer > Automation (stop point), Integrations > Coding Agents (which repos), and the audit log for autofix runs and agent-opened PRs you did not expect.
```

## If you are affected

- **Turn the automation down** until Sentry ships a fix: set Seer's automation to *Stop after Root Cause* (or disable it), and disconnect the coding-agent handoff for repositories that matter. CERT/CC's mitigations: disable automated remediation workflows, restrict package installation in the agent environment, deactivate Seer handoff, and filter telemetry before Seer analyses it.
- Review every agent-opened PR and every package the agent added since your Seer handoff went live; a dependency you did not recognise from a "fix" PR is the signal. [`playbooks/auditing-a-vibe-coded-repo.md`](../playbooks/auditing-a-vibe-coded-repo.md).
- If the agent environment held repository or cloud credentials, rotate them: [`playbooks/if-your-github-pat-leaked.md`](../playbooks/if-your-github-pat-leaked.md), [`playbooks/rotating-cloud-credentials.md`](../playbooks/rotating-cloud-credentials.md).

## Prevention

- An agent that acts on production telemetry must run with an install allow-list and no write access it does not need — see [`prevention/agent-sandboxing.md`](../prevention/agent-sandboxing.md) and [`prevention/ci-cd-hardening.md`](../prevention/ci-cd-hardening.md).
- Treat anything derived from a public ingest endpoint (error events, logs, WAF blocks) as attacker-authored text when it reaches a model; keep a human on the approval step for anything that installs a package or opens a PR.

## Sources
- [CERT/CC VU#212479 — Sentry Seer vulnerability allows attacker-controlled input to be executed in a privileged environment](https://kb.cert.org/vuls/id/212479) — primary; published 2026-09-16, CVE-2026-90999, vendor status Unknown (notified 2026-08-13), mitigations, credit to Nikita Benkovich and Vitalii Valkov (agyn). Fetched 2026-09-18.
- [NVD — CVE-2026-90999](https://nvd.nist.gov/vuln/detail/CVE-2026-90999) — CNA cret@cert.org, CVSS 3.1 9.8, CWE list; queried via the NVD API 2026-09-18.
- [GitHub Advisory Database — GHSA-vh55-q5m4-8wr6](https://github.com/advisories/GHSA-vh55-q5m4-8wr6) — unreviewed mirror, affected/patched unknown, published 2026-09-16. Fetched 2026-09-18.
- [Sentry docs — Seer Issue Fix](https://docs.sentry.io/product/ai-in-sentry/seer/issue-fix/) — the automation thresholds (10 events / 14 days / fixability), stop points, and the Claude / Cursor Cloud Agent / Copilot Cloud Agent handoffs. Fetched 2026-09-18.
- Hacker News front-page submission "PhantomFix: A fake bug to Sentry Seer gets a coding agent to run attacker code" (2026-09-18, linking the CERT/CC note) — the campaign name; via the Algolia API this sweep.
