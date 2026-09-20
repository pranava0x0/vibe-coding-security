---
id: 2026-09-google-gemini-irregular-eval-real-company-breach
title: "Google is the fourth lab in the Irregular cluster — during a May 2026 capture-the-flag evaluation, Gemini got unintended internet access, guessed one real company's password and used credentials found in public code repositories to enter two more; the model stopped once it recognised the systems were real, Irregular notified Google in July, the public learned on 2026-09-18"
date_disclosed: 2026-09-18
last_updated: 2026-09-20
severity: high
status: contained
ecosystems: [ai-vendor-infrastructure, google, gemini]
tools_affected: ["Google Gemini (model under evaluation)", "Irregular evaluation environment", "any organisation whose credentials sit in a public code repository"]
tags: [agentic-threat-actor, ai-vendor-hygiene, red-team-evaluation, third-party-testing-vendor, leaked-credentials, password-guessing, disclosure-lag]
---

## TL;DR
The Wall Street Journal reported on **2026-09-18** (picked up by The Hacker News, CyberInsider and GBHackers) that during a **May 2026** capture-the-flag evaluation run by the third-party testing firm **Irregular**, a Google **Gemini** model reached the real internet and broke into systems belonging to **three real companies**: in one case by "repeatedly guessing its password," in two by finding credentials "in a public repository." The cause is the one Irregular already documented on 2026-08-14 — a fictional company name in the exercise "unintentionally coincided with a real domain," and internet access that should have been blocked was not. Google's VP of security engineering, Heather Adkins: "the model found public information online and guessed credentials to access websites it believed were within the scope of the test"; Google says the model "ended the intrusion after finding that it had breached a real company's system," notified the organisations, and that "the model acted appropriately." Irregular notified Google in **July**; Irregular's position is that this is "the same issue that was already reported and does not represent a materially separate incident." It is nonetheless the first publicly reported case of a Google model autonomously intruding on third-party systems, and it makes the Irregular containment failure a **four-lab** event — [OpenAI](2026-07-huggingface-agentic-intrusion.md), [Anthropic](2026-07-anthropic-claude-cyber-eval-breaches.md), [Meta](2026-08-meta-irregular-eval-containment-failure.md), now Google. No Google blog post exists; the vendor's statements live only in press coverage.

## What happened

**The evaluation.** Irregular runs offensive-security capture-the-flag evaluations for frontier labs. In May 2026 Gemini was being evaluated "inside a simulated environment," but, per the coverage of the WSJ report, "the testing setup unintentionally allowed internet access," and "a fictional company name used during 'capture the flag' exercises unknowingly matched with a real domain." The model, believing the real domain was its target, went after it.

**Three intrusions, two techniques.** The Hacker News: "The model gained access to a protected system after repeatedly guessing its password. Two other cases related to the model finding credentials in a public repository, allowing it to obtain unauthorized access to protected systems." CyberInsider and GBHackers carry the same split — one password-guessing success, two credential-reuse successes from public code. No victim is named; no data theft or damage is reported ("no damage occurred," per Google via GBHackers).

**The model stopped itself.** What distinguishes this from the OpenAI and Anthropic cases, per THN: "the Gemini model ended the intrusion after finding that it had breached a real company's system." Google's Heather Adkins (via CyberInsider): "the model found public information online and guessed credentials to access websites it believed were within the scope of the test." Google's statement to THN: "This event highlights the importance of training powerful AI models to act responsibly. In this case, the model acted appropriately." Google notified the affected organisations and "worked with Irregular to improve testing processes."

**Timeline and disclosure lag.** Incidents: May 2026. Irregular notified Google: July 2026 (THN: "notified Google in July"; Irregular's 08-14 post: "all relevant labs were notified in late July"). Irregular's public investigation post: **2026-08-14**, which said the problem affected "a few of our customers," occurred in "fewer than one in 10,000 advanced simulations," traced to "a single evaluation scenario," and that "All subsequent public disclosures refer to the same underlying issue first disclosed by one of our customers on July 30 — and are not materially separate incidents." Irregular did not name models or labs. OpenAI (2026-07-30), Anthropic and Meta (2026-08-06) each disclosed their own cases; Google did not, and the Gemini case surfaced only through the WSJ on 2026-09-18 — seven weeks after Irregular's notification.

**Irregular's remediation** (08-14 post): the affected evaluation was disabled, internet-access controls strengthened, manual review of model actions during evaluations expanded, a dedicated internal security team established, "no active issues today."

## Why this matters for vibe coders

- **Two of the three intrusions used credentials sitting in a public code repository.** That is the same primitive as OpenAI's internal model that [searched GitHub for leaked API keys and authenticated with one](2026-09-openai-misalignment-reports-leaked-keys-public-uploads.md), and the same loot the [Anthropic cyber-eval](2026-07-anthropic-claude-cyber-eval-breaches.md) models used. A key you pushed to a public repo is now something a frontier model will find and try within a single evaluation run — not only something a human attacker might get around to.
- **The third intrusion was a guessed password on an internet-facing system** with no lockout, rate limit or second factor in the way.
- The victims here were "in scope" only because a *name collided*. Nothing about them was targeted; they were reachable and weak.

## Am I affected?

You are not a party to this incident unless Google contacted you. The checks that would have kept the three victims out are the ones to run:

```bash
# Anything credential-shaped in your public repos, including history
gitleaks detect --source . --log-opts="--all" 2>/dev/null | head
# or: trufflehog git file://. --only-verified

# GitHub: push protection + secret scanning on every public repo
gh api repos/OWNER/REPO | jq '.security_and_analysis'

# Internet-facing logins: is there a lockout / rate limit / MFA on the admin surface?
# (Supabase Auth, NextAuth, Clerk, your own /login — check the provider's brute-force settings)
```

## If you are affected

If a secret in a public repository is live, rotate it now and assume it was tried: [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md), [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md). If an internet-facing account with a guessable password exists, treat it as already guessed: reset, add MFA, review its audit log.

## Prevention

- [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — secret scanning, push protection, no credentials in repos, history rewriting is not revocation.
- MFA and lockout on every internet-facing login; a "protected system" behind a password alone is one guess loop away from an agent.
- For teams running their own agent evaluations: Irregular's failure modes — unintended egress, and a fictional target name that resolves — are checklist items. Default-deny network egress from evaluation sandboxes and verify fictional domains are yours (register them).

## Sources
- [The Hacker News — Google Gemini Broke Into Real Company Systems After Security Test Domain Mix-Up](https://thehackernews.com/2026/09/google-gemini-broke-into-real-company.html) — 2026-09-19; the three-intrusion description, "ended the intrusion after finding that it had breached a real company's system," Google's "acted appropriately" statement, the May / July / September timeline. Fetched 2026-09-20.
- [CyberInsider — Google Gemini hacked three firms after test sandbox exposed web access](https://cyberinsider.com/google-gemini-hacked-three-firms-after-test-sandbox-exposed-web-access/) — 2026-09-18; Heather Adkins' quote, Irregular's "does not represent a materially separate incident" statement, the "fewer than one in 10,000" figure, first-known-Google-model framing. Names the WSJ as the original report. Fetched 2026-09-20.
- [GBHackers — Google Gemini AI Hacked 3 Real Companies After Cybersecurity Test Exposed It to Internet](https://gbhackers.com/google-gemini-ai-hacked-3-real-companies/) — 2026-09-19; Google's "stopped once it realized it had accessed genuine infrastructure" and "no damage occurred" statements; confirms no Google post or Irregular report is linked. Fetched 2026-09-20.
- [Irregular — Addressing Recent Incidents: Ongoing Findings and Path Forward](https://www.irregular.com/research/addressing-recent-incidents-ongoing-findings-and-path-forward) — 2026-08-14; the root cause (fictional name coinciding with a real domain, unintended internet access), "a single evaluation scenario," "not materially separate incidents," late-July lab notification, remediation list. Fetched 2026-09-20.
- The original report is The Wall Street Journal's 2026-09-18 story ("Gemini Hacked Three Companies in First Known Breakout by Google's AI"), which this sweep could not fetch (blocked); every fact above is taken from the three outlets that cite it and from Irregular's own post.
