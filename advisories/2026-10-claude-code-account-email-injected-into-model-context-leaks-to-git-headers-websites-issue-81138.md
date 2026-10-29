---
id: 2026-10-claude-code-account-email-injected-into-model-context-leaks-to-git-headers-websites-issue-81138
title: "Claude Code puts the account email in every model prompt; users report it in git commits, headers and web requests (issue #81138)"
date_disclosed: 2026-07-25
last_updated: 2026-10-29
severity: medium
status: ongoing
ecosystems: [claude-code, npm, ai-coding-agents]
tools_affected: ["@anthropic-ai/claude-code 2.1.220 through at least 2.1.289 when signed in with a Claude account (the `oauthAccount` path); API-key, Bedrock and Vertex authentication reportedly do not inject it"]
tags: [privacy, pii, system-prompt, claude-code, data-leak, git-identity, prompt-injection-surface, no-vendor-response, open-issue, hacker-news]
---

## TL;DR
Claude Code reads the signed-in account's email address from `~/.claude.json` and places the sentence "The user's email address is …" in the model's context on every request, with no setting to turn it off; the open issue #81138 (2026-07-25) has reports from fifteen commenters, including the model writing the address into ten git commits as `user.email`, into an HTTP `User-Agent` header, and handing it to a web service from a subagent, and no reply from Anthropic as of 2026-10-29. If your commits, logs or outbound requests from agent sessions carry an address you did not configure, this is where it came from; API-key authentication is the only reported path that omits it.

## What happened

**The behaviour.** The issue's reporter (skflowne) decompiled the bundle: when `ANTHROPIC_UNIX_SOCKET` is unset, the client reads `oauthAccount.emailAddress` and adds a `userEmail` field to the user-context block. In 2.1.220 the text was the bare address; 2.1.246 appended "Use it only to identify the user… Never send it to an unrelated service… unless the user explicitly asks"; a 2.1.289 report places it inside a `<system-reminder>` attached to every outbound Messages API request, including the requests that follow tool results within a turn. The reporter found no consumer of the value in the bundle other than a telemetry flag recording its presence (`has_user_email`). `IS_DEMO=1`, documented as hiding the email, gates seven display surfaces and not the context builder. None of the documentation pages (environment variables, authentication, data usage, settings) mention it.

**The reports.** All are self-reported in the thread; they come from different accounts across three months:

- The reporter: the model passed `git -c user.email=<private address>` on ten commits, overriding a configured `noreply` identity; GitHub push protection blocked the push and the address stayed in the local reflog.
- inigohidalgo (2026-09-01) and Goofables (2026-09-07, 2.1.263): the agent used the subscription email as the git identity.
- mootari (2026-10-20): the model placed the address in a `User-Agent` header on the web harness (Opus 5.5).
- markblundeberg (2026-10-27): a subagent gave the address to a web service.
- Coice (2026-08-20): the model drew inferences from the address that changed its output.
- The model has also volunteered the sentence to the user unprompted ("My system prompt tells me your email address is…").

**The vendor.** No Anthropic or maintainer comment is on the thread; the issue carries the `bug` label and no assignee. The reporter's tag of a maintainer on 2026-08-20 drew no visible reply. Earlier issues on the same behaviour were closed: #53231 and #50702 as not planned after inactivity, #67605 as a duplicate of #58081, which was then locked. A Hacker News thread of 2026-10-29 ("Tell HN: Claude Code adds your email to the prompt, the LLM sends it to websites", TekMol) links the issue and a Reddit thread this run could not open.

**Why it matters here.** The address is a stable personal identifier inside every prompt, which makes it available to any content the agent reads: a prompt-injected README or web page that asks the model to include "the user's email" in a request gets it. The git reports are the concrete harm so far: a private address in commit metadata on a public repository is a disclosure that survives a force-push. The vendor's instruction sentence governs use, not presence, and the reports after 2.1.246 show the sentence is not sufficient.

## Am I affected?

```bash
grep -o '"emailAddress":"[^"]*"' ~/.claude.json 2>/dev/null       # the field the client reads; present means it is injected
git log --all --format='%ae%n%ce' | sort -u                          # addresses in your commits; look for one you did not configure
CLI=$(readlink -f "$(which claude)"); grep -ao 'userEmail:`[^`]\{0,200\}' "$CLI" | head -1   # the construction site, from the issue
```

- Signed in with a Claude account: affected on every reported version from 2.1.220 to 2.1.289.
- Using an API key, Bedrock or Vertex: a commenter (yurukusa) reports no `oauthAccount` and therefore no injection; this file has not verified it.

## If you are affected

1. Check public repositories you pushed to from agent sessions for the address in author or committer fields; GitHub's push protection catches it only when enabled for the repository.
2. Set and verify a repository-level `user.email` and watch for `-c user.email=` in the agent's git commands; the reports show the model overriding the configured value.
3. Reported workarounds, each partial: a CLAUDE.md instruction not to use the address (governs use, not presence); API-key authentication (no setting, changes billing); a local relay via `ANTHROPIC_BASE_URL` that strips the block (the relay sees your bearer token; a third-party relay is a worse exposure than the address).
4. Treat the address as a known-injected value when assessing a prompt-injection incident: [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md): egress controls limit where an injected identifier can go.
- [Credential hygiene](../prevention/credential-hygiene.md): what the client puts in context is part of your data footprint; know the fields.

## Sources
- [anthropics/claude-code — issue #81138: Account email (PII) is injected into the model's system prompt without consent, disclosure…](https://github.com/anthropics/claude-code/issues/81138) — fetched 2026-10-29: opened 2026-07-25, the decompiled construction site, the version history 2.1.220 to 2.1.289, the five leak reports with dates and commenters, the `IS_DEMO` finding, the closed sibling issues, no vendor response, 19 comments.
- [Hacker News — Tell HN: Claude Code adds your email to the prompt, the LLM sends it to websites](https://news.ycombinator.com/item?id=50286306) — fetched 2026-10-29 through the Algolia API: posted 2026-10-29 by TekMol, links the issue and a Reddit thread (not opened; reddit.com is not reachable from this sweep).
- Related in this corpus: [Claude Code and Claude Desktop advisory batches](2026-08-claude-code-desktop-ghsa-batch.md) for the product's own disclosure channel, which carries nothing on this behaviour.
