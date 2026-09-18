---
id: 2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins
title: "Plugin4Shell — Claude Code, OpenAI Codex, GitHub Copilot and Gemini CLI all checked out a pinned plugin commit without verifying they landed on it, so a repository owner can serve different code under a reviewed SHA and auto-update it into every installed agent; Claude Code and Codex are patched, Copilot and the retired Gemini CLI are not"
date_disclosed: 2026-09-17
last_updated: 2026-09-18
severity: high
status: mitigated
ecosystems: [claude-code, codex, github-copilot, gemini-cli, git, agent-plugins, skills]
tools_affected: ["Claude Code < 2.1.179", "OpenAI Codex CLI < 0.146.0", "GitHub Copilot CLI (no fix shipped as of 2026-09-18)", "Google Gemini CLI (all versions; product retired, no fix)", "any plugin marketplace served from Bitbucket or a self-hosted Git server"]
tags: [supply-chain, agent-plugins, skills, sha-pinning, git, zero-click, auto-update, rce, coordinated-disclosure, no-cve]
---

## TL;DR
Air Security (Or Nevo, Dor Granat, Niv Hoffman) found that the plugin systems of **Claude Code, OpenAI Codex, GitHub Copilot and Gemini CLI** all "pin" a marketplace plugin to a reviewed commit SHA and then run `git checkout <sha>` — but **never check that `HEAD` actually resolved to that SHA**. Git resolves a ref name before a raw object id, so on any host that permits a **branch named with the 40-hex SHA** (Bitbucket and self-hosted Git do; GitHub rejects the shape), the repository owner can point that branch at malicious code, and the agent installs it while reporting the pinned, reviewed version. Gemini CLI's three-step install (`clone` / `fetch origin <sha>` / `checkout FETCH_HEAD`) has a sibling flaw: a default branch literally named `FETCH_HEAD` wins the same way. Because the agents auto-update installed plugins in the background, the swap is **zero-click** for every developer who ever installed the plugin. Disclosed June 2026; **Claude Code fixed in 2.1.179** (npm: 2026-06-16), **Codex fixed in 0.146.0** (rust-v0.146.0, 2026-07-29, "Verify Git plugin SHA checkouts"), **GitHub Copilot has shipped no fix** (GitHub says its host-side branch-name block already prevents exploitation), and **Google will not fix Gemini CLI**, which it retired for consumer accounts on 2026-06-18 in favour of Antigravity CLI — while still publishing new versions for enterprise Code Assist customers. No CVE has been assigned as of 2026-09-18. Update Claude Code and Codex; on Copilot and Gemini CLI, only install plugins hosted on GitHub, and verify what actually got checked out.

## What happened

**The bug, in one line.** Every one of the four agents "checks out the pinned commit without verifying the checkout landed there" (Air). A marketplace records `<repo>@<sha>`; the agent clones the repo and runs `git checkout <sha>`; and Git, given a 40-hex string, **prefers a ref of that name over the object of that id**. If the repository has a branch whose name *is* the pinned SHA, `checkout` lands on the branch tip, `HEAD` reports the branch, and the agent — which only checks that the command succeeded — records the install as the reviewed commit. Air's recommended fix is the one-liner the agents were missing: after checkout, `test "$(git rev-parse HEAD)" = "<pinned-sha>" || abort`.

**Two variants.**
- **Branch-named-as-SHA** (Claude Code, Codex, GitHub Copilot): create a branch whose name is the exact 40-character pinned commit hash, set it as the default branch, put the payload on it. GitHub blocks branch names that look like commit hashes, so plugins hosted there are safe from this variant regardless of agent version; **Bitbucket and self-hosted Git servers allow them**, and Anthropic's own marketplace documentation lists both as supported plugin backends.
- **`FETCH_HEAD` override** (Gemini CLI): the install sequence is `git clone`, `git fetch origin <sha>`, `git checkout FETCH_HEAD`. A default branch named `FETCH_HEAD` is resolved in place of the fetched commit.

**Two attack paths (Air).**
1. *Benign-to-malicious pivot.* Publish a clean plugin; pass marketplace review and get pinned; ship a routine update so the marketplace re-pins to a fresh commit; then create a branch named after that commit pointing at the payload. The marketplace still shows the reviewed hash, the agents' background auto-update fetches the branch, and "trusted plugin is silently swapped for a malicious one and auto-installed past the agent's SHA pinning."
2. *Repository hijacking.* Take over a plugin author's repository (Air's July 2026 **SkillJacking** work found **925 skills serving ~134,000 agents** whose upstream GitHub account, package, domain or cloud-app slot could be claimed; they re-registered the deleted `hexiaochun` account behind `seedance2-api`, 11,483 installs on skills.sh, and gained "cloud credentials, their `.env`, their identity" without changing the listing) and use Plugin4Shell to push malicious code past the pin.

**What the plugin gets.** A coding-agent plugin runs with the agent's own permissions — the developer's files, shell, environment variables, MCP connections and whatever credentials the agent can reach. Air calls it "a first-of-its-kind AI supply-chain attack"; The Hacker News and Help Net Security both carry the zero-click framing. Air says it built working proofs of concept against all four agents in May 2026.

**Vendor responses (Air's disclosure timeline, cross-checked against registries):**

| Agent | Status | Detail |
|---|---|---|
| **Claude Code** | Fixed | Anthropic confirmed the fix 2026-06-17 in **2.1.179**. `npm view @anthropic-ai/claude-code time` shows 2.1.179 published 2026-06-16 (current release 2.1.276). No GitHub Security Advisory was published; the vendor advisory tab's newest entry is still 2026-06-25 and does not mention this. |
| **OpenAI Codex** | Fixed | **0.146.0** (npm 2026-07-29; GitHub tag `rust-v0.146.0` release notes list "Verify Git plugin SHA checkouts" #34644). OpenAI's public fix description: "Git can interpret a requested commit SHA as a branch name," so a plugin source could "materialize a different commit than the one it pinned." Air verified the fix 2026-08-12. |
| **GitHub Copilot** | **No fix** | Air: Microsoft "has not shipped a fix, so users have no patch"; The Register reports Microsoft cited disclosure volume for its non-response and that GitHub's position is that SHA-shaped branch names are blocked on GitHub, which prevents exploitation for GitHub-hosted plugins. The agent-side check is still absent, so a Copilot plugin sourced from Bitbucket or a self-hosted server remains exposed. |
| **Gemini CLI** | **Will not fix** | Google confirmed on 2026-08-04 that it would not patch and advised migrating to Antigravity CLI. Google's developer blog announced the transition on 2026-05-19 with a **2026-06-18** cutover for AI Pro/Ultra and free Code Assist users; enterprise Code Assist customers keep the legacy CLI, and Google says it "will continue to support Gemini CLI." The npm package is not marked deprecated and shipped **0.60.0 on 2026-09-15** plus nightlies through 2026-09-18 — so "retired" means the consumer entitlement ended, not that vulnerable builds stopped being published. |

**Why the "marketplace can't fix it" point matters.** The pin is resolved by the agent on the developer's machine, so only an agent-side check restores the guarantee. A marketplace can blunt the branch-name variant by accepting only hosts that reject SHA-shaped names, but that bans hosts the agents officially support and does nothing for the `FETCH_HEAD` variant.

**Two-source note.** Air's technical write-up (2026-09-17) is the primary; The Hacker News, The Register and Help Net Security (2026-09-17/18) each carry the vendor responses, and the Codex release notes independently confirm the fix commit. The version numbers above were checked against npm's `time` field this sweep.

## Am I affected?

```bash
# Agent versions — fixed lines are Claude Code >= 2.1.179, Codex >= 0.146.0
claude --version 2>/dev/null; codex --version 2>/dev/null
npm ls -g @anthropic-ai/claude-code @openai/codex @github/copilot @google/gemini-cli 2>/dev/null

# Where do your installed plugins come from? Anything not on github.com is exposed on Copilot / Gemini CLI.
grep -rhoE 'https?://[^"/]+/[^"]+' ~/.claude/plugins/ ~/.codex/plugins/ ~/.copilot/ ~/.gemini/ 2>/dev/null | sort -u

# For each plugin checkout, does HEAD equal the pinned SHA the marketplace recorded?
for d in ~/.claude/plugins/*/ ~/.codex/plugins/*/ ~/.gemini/extensions/*/; do
  [ -d "$d/.git" ] || continue
  echo "$d $(git -C "$d" rev-parse HEAD) $(git -C "$d" symbolic-ref -q HEAD || echo detached)"
done
# A checkout that is NOT detached (i.e. HEAD is a branch, not a bare commit) is the signal to investigate:
# a correctly pinned install is a detached HEAD at the recorded SHA.

# Branches named like commit hashes in a plugin repo you control or review:
git -C <plugin-repo> branch -r | grep -E '/[0-9a-f]{40}$|/FETCH_HEAD$'
```

## If you are affected

- **Update Claude Code (≥ 2.1.179) and Codex (≥ 0.146.0)** — both are months old; if you pin an older version, unpin.
- **On GitHub Copilot and Gemini CLI:** remove plugins sourced from Bitbucket or self-hosted Git until the agent verifies checkouts, or vendor the plugin at a commit you have read and disable auto-update. Gemini CLI consumer users should migrate to Antigravity CLI as Google directs; enterprise users should ask Google for a fix commitment, because the package is still being published.
- If a plugin checkout shows a branch instead of a detached commit, treat the machine as compromised by an unknown plugin payload: [`playbooks/if-your-local-ai-agent-was-exploited.md`](../playbooks/if-your-local-ai-agent-was-exploited.md), then rotate what the agent could reach — [`playbooks/rotating-cloud-credentials.md`](../playbooks/rotating-cloud-credentials.md), [`playbooks/if-your-github-pat-leaked.md`](../playbooks/if-your-github-pat-leaked.md).
- Plugin authors: audit whether your upstream dependencies (GitHub account, npm package, domain, Vercel/Railway app) are claimable — the SkillJacking classes — and protect the repository with 2FA and branch protection.

## Prevention

- Treat agent plugins and skills as dependencies with a lockfile: pin, and verify the resolved commit, not just the command's exit code. [`prevention/package-vetting-checklist.md`](../prevention/package-vetting-checklist.md), [`prevention/supply-chain-attack-surface.md`](../prevention/supply-chain-attack-surface.md).
- Disable background auto-update for agent plugins where the agent allows it; review updates the way you review a dependency bump.
- Run agents with the least reach a plugin could abuse: [`prevention/agent-sandboxing.md`](../prevention/agent-sandboxing.md), [`prevention/credential-hygiene.md`](../prevention/credential-hygiene.md).

## Sources
- [Air Security — Plugin4Shell: Zero Click RCE Vulnerability found in top 4 most popular coding agents](https://www.air.security/blog-posts/plugin4shell) — primary; the two variants, the `git rev-parse` fix, the per-vendor timeline (Anthropic 06-17, Google 08-04, Codex verified 08-12), the GitHub-vs-Bitbucket host behaviour, researcher names. Fetched 2026-09-18.
- [The Hacker News — Plugin4Shell Lets Repository Owners Swap Pinned Plugin Code Across Four AI Coding Agents](https://thehackernews.com/2026/09/plugin4shell-lets-repository-owners.html) — 2026-09-18; OpenAI's fix description quote, "no CVE as of September 18," GitHub's branch-name block. Fetched 2026-09-18.
- [The Register — AI coding agents' 0-click RCE flaw could hand attackers keys to the kingdom](https://www.theregister.com/security/2026/09/17/ai-coding-agents-0-click-rce-flaw-could-hand-attackers-keys-to-the-kingdom/5297335) — 2026-09-17; Microsoft's disclosure-volume non-response, GitHub's mitigation claim, the "never verifies it landed there" quote. Fetched 2026-09-18.
- [Help Net Security — Zero-click RCE vulnerability hit four major AI coding agents, two remain unpatched](https://www.helpnetsecurity.com/2026/09/18/plugin4shell-ai-coding-agents-vulnerability/) — 2026-09-18; the SkillJacking tie-in (925 skills / 134,000 agents). Fetched 2026-09-18.
- [Air Security — SkillJacking: 925 Skills Hijacked From Their Maintainers, Affecting 134K Agents](https://www.air.security/blog-posts/skilljacking) — 2026-07-02; the four hijackable-dependency classes and the `seedance2-api` demonstration. Fetched 2026-09-18.
- [openai/codex release rust-v0.146.0](https://github.com/openai/codex/releases/tag/rust-v0.146.0) — 2026-07-29; "Verify Git plugin SHA checkouts" (#34644). Fetched 2026-09-18.
- [Google Developers Blog — An important update: Transitioning Gemini CLI to Antigravity CLI](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) — 2026-05-19 announcement, 2026-06-18 cutover, enterprise carve-out. Fetched 2026-09-18.
- npm registry `time` fields for `@anthropic-ai/claude-code` (2.1.179 → 2026-06-16), `@openai/codex` (0.146.0 → 2026-07-29) and `@google/gemini-cli` (0.60.0 → 2026-09-15, not deprecated) — queried 2026-09-18.
