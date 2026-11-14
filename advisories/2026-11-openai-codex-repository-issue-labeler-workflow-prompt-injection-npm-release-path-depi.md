---
id: 2026-11-openai-codex-repository-issue-labeler-workflow-prompt-injection-npm-release-path-depi
title: "OpenAI Codex repository: Depi reports an issue-labeler workflow prompt injection that could have reached the `@openai/codex` npm release; fixed, nothing published"
date_disclosed: 2026-11-11
last_updated: 2026-11-14
severity: medium
status: unconfirmed
ecosystems: [codex, openai, github-actions, npm, ci-cd]
tools_affected: ["openai/codex repository CI (not the Codex CLI on a user's machine)", "repositories that run openai/codex-action or another coding agent on issue or pull request text", "users of `@openai/codex` with automatic updates (no malicious release was published)"]
tags: [prompt-injection, github-actions, ci-cd, codex, openai, agent-in-ci, supply-chain-risk, npm, researcher-report, no-cve, unconfirmed]
---

## TL;DR
Depi researchers reported on 2026-11-11 that the issue-labeler workflow in the `openai/codex` repository ran a coding agent on text any GitHub user could submit, and that they chained this in a test environment to CI runner tokens and cache write access. They say that access could have been used to publish a malicious `@openai/codex` release to npm. They published none, and they say OpenAI fixed the core bug. Users of Codex have nothing to patch. If your own repository runs an agent on issue text, this is your configuration to check.

## What happened

Depi's post (Pierre Martin and Garance de la Brosse, 2026-11-11) names the Issue Labeler workflow, `issue-labeler.yml`, which used `openai/codex-action` on issue content. It names `rust-ci.yml` as the later step, because of its write permissions and its use of the CI cache. The post gives no disclosure dates. It says the report went through Bugcrowd, that OpenAI deployed a fix for the core bug soon after, and that an initial award of $1,000 was paid with the report still under review. It mentions no CVE.

Everything about OpenAI's response is the researchers' account. No OpenAI statement was found.

One fact from the repository, read 2026-11-14: the commit history of `.github/workflows/issue-labeler.yml` shows a commit on 2026-11-11 titled "Use the Responses API for issue label suggestions" (pull request 60897). The commit before it is dated 2026-10-02. This file does not say that commit is the fix. The post names no commit.

SecurityWeek's weekly roundup (2026-11-13) carries the item and links the post. It is coverage of the same post, not a second finding. That is why the status is `unconfirmed`.

## Am I affected?

- As a Codex user: no action. The researchers state that they published no package.
- As a repository owner: check whether any workflow triggered by issues, issue comments or pull requests from outside contributors starts a coding agent, and what that job's token and cache can write to.

```bash
grep -rl 'codex-action' .github/workflows/
```

## If you are affected

1. Give the agent job a read-only token and no secrets. Do the write step in a separate job that takes only the agent's structured output.
2. Do not share a cache between a job that reads untrusted text and a job that builds a release.
3. Limit who can trigger the agent.

## Prevention

- The post suggests a short cooldown before taking automatic updates of developer tools.
- See [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) and [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).

## Sources

One research source. The outlet item is coverage of it.

- [Depi: Backdooring Codex](https://depi.security/blog/20261111-backdooring-codex/), fetched 2026-11-14 (dated 2026-11-11) for affected workflows, outcome, vendor response as the researchers describe it, bounty and user guidance only.
- [openai/codex: history of `.github/workflows/issue-labeler.yml`](https://github.com/openai/codex/commits/main/.github/workflows/issue-labeler.yml), fetched 2026-11-14: 27 commits, the 2026-11-11 and 2026-10-02 entries.
- [SecurityWeek: In Other News, 2026-11-13](https://www.securityweek.com/in-other-news-new-cisa-director-nominee-connected-car-hacking-baker-tilly-data-breach/), fetched 2026-11-14: the item and its link.
- Not covered: pull request 60897 itself, `rust-ci.yml`, Bugcrowd, and any OpenAI page.
