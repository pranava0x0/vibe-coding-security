---
id: 2026-11-t3-code-analytics-read-codex-claude-sign-in-files-hashed-account-ids
title: "T3 Code through 0.1.11 read Codex and Claude sign-in files and sent unsalted hashes of the account ids; fix merged 2026-11-24"
date_disclosed: 2026-11-24
last_updated: 2026-11-25
severity: medium
status: mitigated
ecosystems: [t3-code, coding-agents, telemetry, codex, claude-code]
tools_affected: ["T3 Code desktop app and server through 0.1.11", "machines with `~/.codex/auth.json` or `~/.claude.json` present"]
tags: [telemetry, privacy, account-identifiers, coding-agent, credential-file-read, unsalted-hash, vendor-fix, mitigated]
---

## TL;DR

T3 Code's analytics read `~/.codex/auth.json` and `~/.claude.json` at server start and sent unsalted SHA-256 hashes of the OpenAI and Claude account ids, according to [the vendor's own fix](https://github.com/pingdotgg/t3code/pull/42299). The fix merged on 2026-11-24 and is listed in the nightly notes. The 0.1.12 release notes read on 2026-11-25 do not list it. Set `T3CODE_TELEMETRY_ENABLED=false` until a release you run names the change.

## What happened

A post on X on 2026-11-24 accused T3 Code of collecting user data. [EveryDev.ai](https://www.everydev.ai/p/tool-t3-code-v0111-sends-hashed-openai-and-claude-account-ids-at-first-launch) tested version 0.1.11 on macOS the same day and reported:

- About ten seconds after launch and before sign-in, the app sent a request to `ingest.t3.codes` whose `distinct_id` was an unsalted SHA-256 hash of the Codex account id.
- It sent `install.owner_observed` events with SHA-256 hashes of the OpenAI user id and the Claude account UUID, once per server start.
- Usage reports carried the model, token count and run duration under the OpenAI account hash.
- EveryDev found no tokens, names, email addresses, prompts, code or file paths in the uploads.
- After a reinstall the install id changed and the three account hashes did not.

The vendor's pull request #42299, "fix(server): analytics no longer reads or sends Codex and Claude account IDs", merged on 2026-11-24. Its description says: "T3 Code's analytics read `~/.codex/auth.json` and `~/.claude.json` at server boot." It says the hashes "were unsalted" and that "Users did not sign in to those providers to be identified by T3 Code." After the change, "analytics never opens a provider's sign-in files" and the install id is the analytics identity.

The 0.1.11 [telemetry document](https://github.com/pingdotgg/t3code/blob/v0.1.11/docs/user/telemetry.md) said the server "sends hashed account identifiers: your T3 Connect account, your OpenAI and Claude accounts". EveryDev reports that the welcome screen says the app "collects anonymous usage data" and that neither it nor the privacy policy mentions account identifiers.

The maintainer replied on X:

> Okay, let's have an honest conversation about the telemetry data in T3 Code.
>
> [@theo on X, 2026-11-24](https://x.com/theo/status/2125332390239494211)

EveryDev summarises the rest of that post. The team removed the sign-in file reads, which existed so one person on several computers counts as one user. The app never uploaded files, prompts or file paths.

Which release carries the fix:

| Release | Date | Notes read 2026-11-25 |
|---|---|---|
| v0.1.12-nightly.20261124.5209 | 2026-11-24 | Lists "fix(server): analytics no longer reads or sends Codex and Claude account IDs". |
| v0.1.12, marked Latest | 2026-11-25 | The first 200,000 of 213,172 characters of the notes do not list the line or the pull request number. |

No source says whether 0.1.12 contains the change.

EveryDev dates the Codex account hash to a commit in March 2026 and the OpenAI and Claude hashes to pull request #21506 in October 2026. Those two pages were not opened for this file.

## Am I affected?

- You ran T3 Code 0.1.11 or an earlier release that included the hashes, with Codex or Claude Code signed in on the same machine.
- EveryDev did not test Windows or Linux.

```bash
ls -l ~/.codex/auth.json ~/.claude.json 2>/dev/null
env | grep T3CODE_TELEMETRY_ENABLED
```

## If you are affected

1. Set `T3CODE_TELEMETRY_ENABLED=false` in the server's environment and restart the app. The vendor document says the desktop app reads it from your shell profile on macOS and Linux.
2. The opt-out is partial. The vendor document says the browser web app ignores the variable and mobile tracing has no toggle. EveryDev reports that a startup diagnostic still went to Axiom.
3. Update when a release's notes name pull request #42299.
4. No token was sent, per EveryDev and the pull request, so no credential rotation follows from this. The hashes already sent stay with the vendor's analytics.

## Prevention

- An agent harness runs as you and can read every other tool's sign-in files. Read a tool's telemetry document before installing it, and check it again after updates. See [agent sandboxing](../prevention/agent-sandboxing.md) and [credential hygiene](../prevention/credential-hygiene.md).

## Sources

- [T3 Code pull request #42299](https://github.com/pingdotgg/t3code/pull/42299), merged 2026-11-24, read 2026-11-25 through a summarizing fetch. The vendor's description of the old and new behaviour.
- [EveryDev.ai: T3 Code v0.1.11 sends hashed OpenAI and Claude account IDs at first launch](https://www.everydev.ai/p/tool-t3-code-v0111-sends-hashed-openai-and-claude-account-ids-at-first-launch), Joe Seifi, 2026-11-24. Independent test of 0.1.11 on macOS.
- [T3 Code telemetry document at v0.1.11](https://github.com/pingdotgg/t3code/blob/v0.1.11/docs/user/telemetry.md). Collected fields, destinations, the opt-out variable and its limits.
- [T3 Code releases](https://github.com/pingdotgg/t3code/releases) and [v0.1.12](https://github.com/pingdotgg/t3code/releases/tag/v0.1.12), read 2026-11-25. Release dates and notes.
- [@theo on X](https://x.com/theo/status/2125332390239494211), 2026-11-24. The first sentence was read through the `api.fxtwitter.com` mirror, which returned a truncated post.
- [Original post on X](https://x.com/realchendahuang/status/2125153472450527440), 2026-11-24, in Chinese, read through the same mirror. The accusation that started the thread. Its other claims were not checked.
- [Hacker News item 50636552](https://news.ycombinator.com/item?id=50636552): where the EveryDev article surfaced.
