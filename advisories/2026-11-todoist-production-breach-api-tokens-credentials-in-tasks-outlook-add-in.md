---
id: 2026-11-todoist-production-breach-api-tokens-credentials-in-tasks-outlook-add-in
title: "Todoist: attacker reached production on 2026-11-23, took API tokens and searched tasks for credentials; rotate tokens and any secret stored in Todoist"
date_disclosed: 2026-11-24
last_updated: 2026-11-25
severity: high
status: contained
ecosystems: [saas, todoist, api-tokens, ci-cd, outlook]
tools_affected: ["Todoist accounts", "scripts, agents and MCP servers that hold a Todoist API token", "Todoist Slack integration", "Todoist for Outlook add-in", "accounts with API keys or tokens written in tasks or comments"]
tags: [incident, vendor-incident, saas-breach, api-tokens, credentials-in-notes, ci-workflow-modification, stolen-credential, password-hashes, contained]
---

## TL;DR

[Todoist says](https://www.todoist.com/help/todoist/get-started/security-incident-in-november-2026-cG0EIACNU) an attacker reached its production systems on 2026-11-23. The attacker downloaded email addresses and salted SHA1 password hashes for about 6% of users. For smaller groups the attacker took Todoist API and Slack integration tokens, searched tasks and comments for credentials, and read connected Outlook mail. Todoist emailed affected accounts. If you got that email, replace the API token in your scripts and revoke every secret you stored in Todoist.

## What happened

Todoist published the notice on 2026-11-24 at 16:11 UTC and added a FAQ on 2026-11-25 at 04:22 UTC. All times below are UTC and come from the notice.

| Time | Event, per Todoist |
|---|---|
| 2026-11-22 14:04 | Earliest use of "a stolen credential associated with our version control system". The attacker modified automated workflows in three repositories to obtain more credentials. |
| 2026-11-23 06:06 | The attacker obtained an administrative credential for the employee sign-in system "through an infrastructure automation workflow". |
| 2026-11-23 06:33 to 06:54 | The attacker changed an employee's authentication settings and signed in to the cloud infrastructure as that employee. |
| 2026-11-23 09:08 onward | The attacker accessed production databases and ran commands in production. |
| 2026-11-23 12:45 to 12:51 | Account records with email addresses and legacy password hashes were exported and downloaded. |
| 2026-11-23 13:05 to 17:12 | Queries for account tokens, access to connected Outlook mailboxes, and searches of Todoist content for credentials. |
| 2026-11-23 17:01 | Todoist began investigating an unexpected administrator account. |
| 2026-11-24 05:06 | Todoist disabled the Todoist for Outlook email add-in. |

Todoist says the attacker could read its source code and that the "investigation found no changes to application code".

What was taken, with Todoist's approximate shares of its users:

| Group | Share | Data |
|---|---|---|
| Legacy password hashes | 6% | Email address, salted SHA1 password hash, account creation date. These are accounts whose password had not changed since Todoist stopped using that method "over a decade ago". |
| Tokens | 0.003% | Todoist API tokens and Slack integration tokens. |
| Content resembling credentials | 0.001% | Matches from searches of tasks, comments and attachment names on one database shard, up to 320 characters of text per match. |
| Connected Outlook accounts | 0.001% | Email subjects, senders, the first 255 characters of messages, and attachment names and links. |

Todoist says the searches looked for "API keys, access tokens, and other sensitive information you may have stored in Todoist". It disabled affected passwords, revoked API tokens, disconnected OAuth applications and ended sessions for affected accounts.

The notice does not say how the version control credential was stolen. It gives no user counts, only percentages.

A separate flaw in the `@doist/todoist-mcp` server, CVE-2026-76807, is in [the 2026-11-19 MCP batch](2026-11-mcp-server-advisories-november-19-20-jupyter-todoist-k8s-sqlite-obsidian-codewhale-fixed-earlier.md). Todoist's notice does not mention it.

## Am I affected?

- Todoist says it emailed every affected account from `no-reply@notify.todoist.com`, and that accounts with no email need no action.
- You are in the token group if a script, agent or MCP server that used your Todoist API token stopped authenticating after 2026-11-23.
- You are exposed beyond Todoist if you ever wrote an API key, access token or recovery phrase into a task or comment.

## If you are affected

1. Reset your Todoist password. Change it on any other service where you reused it.
2. Copy the new API token from Settings → Integrations → Developer in the Todoist web app, and update every script, agent configuration and MCP server that held the old one.
3. Revoke and replace every credential you stored in tasks or comments, at the service that issued it. Todoist notes that deleting a comment does not invalidate a secret that was already copied.
4. Reconnect the Slack integration and the Outlook add-in if Todoist disconnected them. Todoist says the new Outlook app may show as unverified until Microsoft's verification completes.
5. Treat email about this incident from any other sender as phishing. Todoist says it will not ask for your password or ask you to install software.

See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) for the rotation order when a stored secret was a cloud key.

## Prevention

- Do not store credentials in task managers or notes. Use a secret manager. See [credential hygiene](../prevention/credential-hygiene.md).
- Give agents and MCP servers their own tokens so one revocation does not break everything.
- The entry point was a version control credential that could change workflows. Limit which changes can trigger workflows that hold infrastructure secrets. See [CI/CD hardening](../prevention/ci-cd-hardening.md).

## Sources

Single source: the vendor.

- [Todoist: Security incident in November 2026](https://www.todoist.com/help/todoist/get-started/security-incident-in-november-2026-cG0EIACNU), published 2026-11-24, updated 2026-11-25, read 2026-11-25 with `curl`. Timeline, shares, quotations and user steps.
- [Hacker News item 50633882](https://news.ycombinator.com/item?id=50633882): where the notice surfaced, 9 points when read.
- Not found: outlet coverage. One web search on 2026-11-25 returned only Todoist help pages.
