---
id: 2026-11-gitbook-november-2-security-incident-ai-agents-rotate-api-tokens-git-sync-secrets-reauth-mcp-server
title: "GitBook security incident 2026-11-02: infrastructure credentials taken by an attacker using AI agents; rotate API tokens, Git Sync and integration secrets, re-authenticate the MCP server"
date_disclosed: 2026-11-03
last_updated: 2026-11-04
severity: high
status: ongoing
ecosystems: [gitbook, documentation, github, mcp, saas]
tools_affected: ["GitBook organizations: personal API tokens (all revoked by GitBook), Git Sync secrets for GitHub and GitLab repositories, third-party API tokens stored for integrations, secrets of published integrations", "the GitBook MCP server connections used from Claude Code, Cursor and other agents", "visitor questions submitted to GitBook Assistant on published sites"]
tags: [vendor-incident, credential-exposure, api-tokens, git-sync, mcp, documentation-platform, ai-agents, rotate-credentials, hacker-news, status-page, postmortem-pending]
---

## TL;DR
GitBook says an attacker "gained unauthorized access to some of our infrastructure credentials" at 19:00 CET on 2026-11-02 in "a sophisticated, highly targeted attack using AI agents", and may have accessed integration tokens, Git Sync secrets, API tokens and the questions site visitors asked GitBook Assistant. GitBook revoked every personal API token, replaced its own credentials, and tells every organization to rotate its GitBook API tokens, rotate the third-party tokens and secrets it stored in GitBook, rotate the secrets of its published integrations, and re-authenticate the GitBook MCP server. The incident was declared resolved at 11:36 CET on 2026-11-04 with a post-mortem promised within 24 hours. No root cause, customer count or record count has been published.

## What happened

**The vendor's timeline (incident page, all times CET).** 2026-11-03 13:15: GitBook reports that it detected a security incident on 2026-11-02 and contained it, took some services offline as a precaution, calls the issue platform-wide, and says no customer action is required yet. 2026-11-03 16:21: the app, API and published docs are back, some services degraded; the attacker "gained unauthorized access to some of our infrastructure credentials at 19:00 CET on November 2"; GitBook blocked the attacker, replaced credentials and secrets, invalidated customers' API tokens, took the app and authenticated docs offline while securing systems, and served published content from cache. 2026-11-04 11:36: the incident is resolved, functionality is restored, Git Sync is still affected by "a separate, ongoing GitHub outage", and "a full postmortem" covering timeline, details, response and prevention will follow within 24 hours. The page says the attacker "may have accessed" four categories: integrations tokens, Git Sync secrets, API tokens, and questions asked to GitBook Assistant by site visitors. It says there is "no evidence that any of your content in GitBook was modified". It does not say how the credentials were obtained, which AI agents were used, or how GitBook attributes the activity to agents.

**How it reached the public.** The first public account was a Hacker News post at 16:45 UTC on 2026-11-03 ("Gitbook Breached", 162 points) by a customer who had opened a support ticket about availability and received the incident text in the reply, before any customer notification. GitBook's CTO Samy Pessé replied in the thread at 18:05 UTC that the team had been responding since the previous day and was bringing services back gradually, and at 13:54 UTC on 2026-11-04 that the incident was resolved and the post-mortem would follow within 24 hours. Commenters noted that `gitbookstatus.com` showed no incident while the detailed page sat under `gitbook.com/status`; read on 2026-11-04 the status host still said "We're not aware of any issues affecting our systems" with no November incident marker. GitBook's X post of 2026-11-03 ("We're addressing a security incident affecting GitBook") was not opened; crypto.news quotes it.

**What the tokens unlock.** A GitBook API token reads and writes the organization's spaces and can publish content. A Git Sync secret is the credential GitBook holds for the customer's GitHub or GitLab repository, so a stolen one is a repository credential, not a docs credential. Third-party tokens stored for integrations are whatever the customer connected: analytics, support desks, Slack. The GitBook MCP server is how coding agents read and edit docs; its re-authentication is on GitBook's own list, which is the first time a vendor incident page in this corpus has named an MCP connection as a thing to re-authenticate. Visitor questions to GitBook Assistant are whatever a reader typed into a public docs site's chat box, which for product docs can include account identifiers and snippets of the reader's own code.

**What is separate.** Trade.xyz reported unauthorized activity on its GitBook-hosted documentation on the morning of 2026-11-02 (restored by 09:15 ET, readers told not to click links in the docs while it investigated); crypto.news reports it as a separate event that Trade.xyz did not attribute to GitBook's platform and that predates the 19:00 CET credential access by hours. GitBook's incident page does not mention it. PancakeSwap took its GitBook docs offline after the GitBook notice, per the same outlet. Neither is confirmed as connected to the GitBook credential access; both are recorded here because a reader whose docs link to wallets or downloads should assume a modified docs page is the attacker's easiest monetisation of a docs-platform breach, and GitBook's "no evidence of modification" statement is scoped to its investigation so far.

**The pattern.** This is the second documentation or developer-tooling SaaS in a week, after WorkOS (2026-10-30), to attribute an intrusion to AI agents without naming the framework, and the ninth hosted developer platform since 2026-10-09 to report theft of stored customer secrets (Fireworks AI, Lightning AI, OpenCode Console, Zeabur, Railway, Northflank, Trigger.dev, WorkOS, each tracked here). SecurityWeek's 2026-11-04 roundup counts "at least a dozen" platforms and quotes Wiz on a market for stolen inference credentials; GitBook is not in that article.

## Am I affected?

1. **Every GitBook organization is affected by the token revocation.** Any CI job, script, agent or integration that used a personal GitBook API token stopped working on 2026-11-03 and needs a new token.
2. **List what GitBook held for you.** In the organization settings: Git Sync configurations (which repositories, which GitHub App installation or GitLab token), integrations and their stored third-party credentials, published integrations and their secrets, and MCP server connections.
3. **Check the GitHub or GitLab side.** For each synced repository, review the installation or deploy token GitBook used and the repository's recent commits and pushes since 2026-11-02 18:00 UTC for anything not made by your team.
4. **Check your docs.** Diff published content against the repository for changed links, addresses or download URLs, especially on pages that point readers at wallets, installers or support channels.
5. **GitBook Assistant on a public site:** assume the questions readers asked since the site enabled the assistant may have been read. GitBook has not given a date range.

## If you are affected

- Rotate GitBook API tokens (the old ones are already revoked), the third-party tokens stored for integrations, and the secrets of published integrations, in that order, as GitBook's page instructs.
- Treat Git Sync as a repository credential: rotate or reinstall the GitHub App or GitLab token GitBook used, and audit the repository for pushes you did not make. See [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).
- Re-authenticate the GitBook MCP server in every agent that had it configured, and remove stale entries from `.mcp.json`, Cursor and Claude Code MCP settings. See [MCP hygiene](../prevention/mcp-hygiene.md).
- If a docs page was altered, publish a notice to readers before restoring it, because the altered page is what readers already acted on.
- Watch for the post-mortem and re-check this file; GitBook promised it by 2026-11-05.

## Prevention

- Give docs platforms least privilege on the repository: a GitHub App installation scoped to the docs repository, not an organization-wide token. See [credential hygiene](../prevention/credential-hygiene.md).
- Keep an inventory of which SaaS platforms hold which tokens. This month's platform breaches are being disclosed days apart and rotation has to start the same day.
- Treat an MCP server connection as a credential: it carries the user's authorization to a third-party service and belongs in the rotation list after a vendor incident.

## Sources
- [GitBook — Security incident, November 2026](https://www.gitbook.com/status/security-incident-2026-11-03) — fetched 2026-11-04: the three dated updates quoted above (2026-11-03 13:15 and 16:21 CET, 2026-11-04 11:36 CET), the four data categories, the customer actions, the AI-agents sentence, the post-mortem promise.
- Hacker News item 50354336 ("Gitbook Breached", 162 points), read through the Algolia items API 2026-11-04: the support-ticket reply reproduced by the poster at 16:45 UTC on 2026-11-03, the CTO's replies at 18:05 UTC and 13:54 UTC the next day, the status-page objections.
- [crypto.news — GitBook urges token resets after AI-powered cyberattack](https://crypto.news/gitbook-ai-cyberattack-api-tokens-secrets/) — fetched 2026-11-04 (2026-11-03 19:15 UTC): the incident-page link, the X post quote, the Trade.xyz and PancakeSwap mentions, the GTIG reference.
- [crypto.news — Trade.xyz GitBook docs unauthorized activity](https://crypto.news/trade-xyz-gitbook-docs-unauthorized-activity/) — fetched 2026-11-04 (2026-11-02 17:00 UTC): the morning-of-11-02 activity, the 09:15 ET restoration, the do-not-click notice, no attribution to GitBook's platform.
- [gitbookstatus.com](https://gitbookstatus.com/) — fetched 2026-11-04: "We're not aware of any issues affecting our systems", no November incident listed.
- [SecurityWeek — AI-Linked Breaches Mount as WorkOS, Northflank, Trigger.dev Disclose Hacks](https://www.securityweek.com/ai-linked-breaches-mount-as-workos-northflank-trigger-dev-disclose-hacks/) — fetched 2026-11-04 (2026-11-04, Ionut Arghire): the platform count and the credential-market framing; GitBook not mentioned.
- Not opened: GitBook's X post of 2026-11-03 and Trade.xyz's X post of 2026-11-02 (X is not reachable from this environment); both are quoted by crypto.news.
- Related in this corpus: [WorkOS incident](2026-11-workos-october-30-internal-sales-tool-incident-crm-support-slack-excerpts-phishing-risk.md), [Trigger.dev incident](2026-11-trigger-dev-security-incident-environment-variables-exposed-subset-of-organizations-rotate.md), [Northflank incident](2026-10-northflank-security-incident-assume-all-environment-variables-decrypted-ai-keys-abused.md), [Railway incident](2026-10-railway-environment-variable-store-breach-rotate-every-secret.md).
