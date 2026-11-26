---
id: 2026-11-1password-backend-breach-github-account-malicious-code-account-records-ci-secrets
title: "1Password: attacker used an employee GitHub account to push code to backend services and copy account records; vaults not affected"
date_disclosed: 2026-11-25
last_updated: 2026-11-26
severity: high
status: contained
ecosystems: [saas, 1password, github, ci-cd]
tools_affected: ["1Password accounts", "1Password SCIM Bridge and Hosted Provisioning invitations", "1Password account recovery emails"]
tags: [incident, vendor-incident, saas-breach, github-account-compromise, ci-cd, source-code-theft, phishing-risk, contained]
---

## TL;DR

[1Password says](https://1password.com/blog/update-on-nov-2026-security-incident) an attacker used an employee's corporate GitHub account to push malicious code to backend services and copy account records for a subset of customers. The records hold names, sign-in email addresses and tokens from invitation and recovery emails. 1Password says vault contents and the keys that protect them were not accessed. It asks for no account changes. Expect phishing that mentions 1Password.

## What happened

1Password published the post on 2026-11-25. It says the investigation began on 2026-11-19, when it saw signs that an attacker had access to an employee's corporate GitHub account. The post gives no earlier date and does not say how the account was taken. It says 1Password revoked "the stolen token" and removed "the access the attacker created", and explains neither.

Per the post, the attacker "used the account to access source code and push malicious code to backend services, which downloaded administrative data pertaining to our customers". The attacker also copied source code from private repositories and "gained access to our CI/CD system". 1Password says the CI/CD system holds infrastructure secrets and that it "triggered a rotation of all credentials which may have been exposed".

Data in the downloaded account records, per the post:

- Names and email addresses
- Account and user identifiers, and account creation and last sign-in times
- Public keys
- Secure Remote Password protocol parameters
- Tokens present in certain emailed links for invitations, provisioning and account recovery
- Other non-secret account metadata

The post says an emailed-link token completes an invitation or recovery only with an SSO sign-in or a code sent to the user's registered email address. 1Password changed that code from six numeric digits to ten alphanumeric characters. It says "a small number of users" had a pending invitation or recovery and were notified.

The post lists as not affected: vaults and their items, the keys that protect vaults, account recovery keys, and the 1Password apps and browser extensions. It says 1Password does not store account passwords or Secret Keys. It reports "no internal evidence of user account takeovers or compromise using any exposed account provisioning tokens".

The post gives no count of affected customers. It does not say how long the malicious code ran or which backend services ran it.

[SecurityWeek](https://www.securityweek.com/1password-breach-exposes-customer-data-internal-source-code/) reports that a 1Password representative said on the company's community forum that the stolen data included Secure Remote Password verifiers derived from account passwords and Secret Keys. SecurityWeek also quotes a community manager: "We have no evidence that encrypted vaults were downloaded or accessed". The forum thread was not opened for this file. [The Register](https://www.theregister.com/security/2026/11/26/hackers-help-themselves-to-1passwords-source-code-and-customer-data/5312317) says 1Password did not answer its questions about how a GitHub account led to code running on backend services.

## Am I affected?

- 1Password says the records belong to "a subset of our users" and that users with a pending invitation or recovery "have been specifically notified". The post does not say whether everyone in the subset gets an email.
- The exposed-data list in the post has no API or service token other than the emailed-link tokens.
- The post says a provisioning invite is used for SCIM Bridge or Hosted Provisioning, so teams that provision that way should check for pending invites.

## If you are affected

1. Be cautious of unexpected email, texts and calls that mention 1Password, invitations or account recovery. 1Password says it "will never contact you to ask for your account password or Secret Key".
2. Enter the account password and Secret Key only in the app, or on the site after typing the address yourself.
3. As a caution beyond the post: if 1Password notified you about a pending invitation or recovery, cancel it and start a new one.
4. Report anything suspicious to the address in 1Password's post.

1Password says: "You do not need to update anything in your 1Password account."

## Prevention

- The attacker used one employee's GitHub account to push code that backend services ran. Require review and protected environments for deploys. See [CI/CD hardening](../prevention/ci-cd-hardening.md).
- Keep long-lived infrastructure secrets out of CI where short-lived credentials work. See [credential hygiene](../prevention/credential-hygiene.md).
- If a personal access token of yours may be exposed, follow [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).

## Sources

- [1Password: Update on a security incident involving 1Password's backend systems](https://1password.com/blog/update-on-nov-2026-security-incident), dated 2026-11-25, read 2026-11-26 with `curl`. Dates, data list, quotations and user steps.
- [SecurityWeek, 2026-11-26](https://www.securityweek.com/1password-breach-exposes-customer-data-internal-source-code/): the community forum statements on verifiers and on vault downloads.
- [The Register, 2026-11-26](https://www.theregister.com/security/2026/11/26/hackers-help-themselves-to-1passwords-source-code-and-customer-data/5312317): the unanswered questions.
- [The Hacker News, 2026-11-26](https://thehackernews.com/2026/11/1password-hacked-customer-data-and.html): restates the post.
- [Hacker News item 50644817](https://news.ycombinator.com/item?id=50644817): 1,549 points when read on 2026-11-26.
- Not opened: the 1Password community forum thread SecurityWeek cites.
