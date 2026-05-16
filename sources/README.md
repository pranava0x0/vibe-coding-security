# Sources

Where the advisories in this repo come from, and where you should look yourself between updates.

| Source type | Where |
|---|---|
| Live commentary, fastest signal | [twitter-accounts.md](twitter-accounts.md) |
| Long-form research and detailed writeups | [security-blogs.md](security-blogs.md) |
| Machine-readable feeds (RSS, JSON) for automation | [advisory-feeds.md](advisory-feeds.md) |

## Recommended monitoring stack

For a solo dev who wants to stay ahead without checking 30 sites a day:

1. **Follow ~10 X (Twitter) accounts** on a dedicated list. → [twitter-accounts.md](twitter-accounts.md). Scan once a day.
2. **Subscribe to 3 RSS feeds:** Socket blog, GitHub Advisory Database (npm + pip), CISA alerts. → [advisory-feeds.md](advisory-feeds.md). Use Feedly / NetNewsWire / Inoreader.
3. **Run Socket on your repos.** Auto-PRs when a dep has a problem.
4. **Subscribe to Anthropic, Cursor, and your other AI tools' release notes** so you upgrade past CVEs quickly.

That's ~10 minutes a day, and you'll be in the top 1% of vibe coders for awareness.

## How we triage what makes it into this repo

A new entry lands in [ALERTS.md](../ALERTS.md) when:

- A package with > 100k weekly downloads is compromised, OR
- A CVE in a major AI tool (Cursor, Claude Code, Copilot, Cody, Windsurf, etc.) is published, OR
- A malicious MCP server is publicly documented, OR
- A prompt-injection attack against a vibe-coding tool is demonstrated with PoC, OR
- A vibe-coding platform (Lovable, Bolt, v0, Replit) has a security incident with user-data exposure.

It gets promoted to a full advisory file when:

- Sources can be triangulated across at least two independent reporters.
- Concrete IOCs (package names, versions, hashes, domains) exist.
- A reader can answer "am I affected?" in under a minute using a command in the advisory.
