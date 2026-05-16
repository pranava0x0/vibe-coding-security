# Contributing

Spot a new incident? Find a fact wrong? Have a playbook to add? All welcome.

## Fastest path: open an issue

If you saw something live and don't have time to write it up properly, just open an issue with:
- Link(s) to the source(s).
- Affected package / tool / MCP.
- Approximate dates.
- Severity guess.

Use the **[New advisory](.github/ISSUE_TEMPLATE/new-advisory.yml)** or **[Update advisory](.github/ISSUE_TEMPLATE/update-advisory.yml)** template — they show up in the issue list when you click "New issue."

## To submit a full advisory PR

1. Fork + clone.
2. Copy the template below into `advisories/YYYY-MM-<short-id>.md`.
3. Add an entry to `advisories/README.md` and `ALERTS.md` (latest on top).
4. Open a PR. Include the sources you used in the PR body.

## Advisory template

```markdown
---
id: YYYY-MM-short-id
title: "Short human title (Month Year)"
date_disclosed: YYYY-MM-DD
last_updated: YYYY-MM-DD
severity: critical | high | medium
status: active | contained | patched | mitigated | ongoing | historical
ecosystems: [npm | pypi | mcp | cursor | claude-code | ...]
tools_affected: [list of tools/projects that should care]
tags: [supply-chain, credential-theft, prompt-injection, ...]
---

## TL;DR
Two sentences. A vibe coder should grok it in 5 seconds.

## What happened
Plain-language description. Cite sources inline as you go.

## Am I affected?
Concrete checks. Bash commands. Lockfile greps. Hashes. Whatever lets a reader answer "yes/no" in under 60 seconds.

## If you are affected
Link to relevant playbook(s).

## Prevention
Link to relevant prevention doc(s).

## Sources
- [Title](https://url) — what this source contributed.
```

## Playbook template

Use this for new entries in `playbooks/`. Pattern:

```markdown
# If [scenario]

> Scope: one-line scope statement.

## Do this first (60 seconds)
Most-urgent action(s), as commands.

## Triage
What could the attacker have done? How to confirm the blast radius?

## Rotate
Step-by-step credential rotation, in priority order.

## Verify
Confirm the rotation took effect and look for residual compromise.

## Prevention going forward
Link to prevention doc.
```

## Prevention doc template

```markdown
# [Topic]

> One-line statement of the goal.

## Why this matters
The threat model. Concrete incidents that this would have prevented.

## What to do
Numbered list of concrete actions. Commands where possible.

## What this stops / doesn't stop
Honest list of the trade-offs.
```

## Style notes

- **Date everything.** Format: `YYYY-MM-DD`. Update `last_updated` in frontmatter when you touch an advisory.
- **Cite multiple sources** when possible. At least two independent reporters before promoting to a full advisory.
- **Concrete > abstract.** Always include a command, a path, or a config snippet when relevant.
- **No FUD.** Severity claims need to be defensible. If only 1,000 people downloaded the package before takedown, say so.
- **Short.** Vibe coders are panicking. Hit the bullet points and link out for depth.

## Out-of-scope contributions

We're not the right home for:
- General npm/PyPI CVE listings unrelated to AI coding tools.
- Generic "how to do AppSec" content — there are 100 better resources.
- Vendor marketing (please).
- Speculation without sources.

When in doubt, open an issue and ask before doing the work.

## License

By contributing, you agree your work is released under [CC0](https://creativecommons.org/publicdomain/zero/1.0/) (effectively public domain). No attribution required.
