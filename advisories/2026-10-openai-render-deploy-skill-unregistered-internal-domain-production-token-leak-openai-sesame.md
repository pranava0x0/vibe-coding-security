---
id: 2026-10-openai-render-deploy-skill-unregistered-internal-domain-production-token-leak-openai-sesame
title: "OpenAI's render-deploy skill told generated apps to call an unregistered render-internal domain with tokens; Render fixed its copy, OpenAI's still carries it (AIR Security, 2026-10-14)"
date_disclosed: 2026-10-14
last_updated: 2026-10-19
severity: high
status: mitigated
ecosystems: [agent-skills, codex, openai-skills, render, generated-code]
tools_affected: ["openai/skills curated render-deploy skill, references/service-types.md and configuration-guide.md, unchanged as of 2026-10-19", "openai/plugins Render plugin between 2026-03-13 and 2026-08-26", "render-oss/skills render-deploy before commit 5152e543", "any application whose deploy or service-communication code was generated with the skill loaded"]
tags: [agent-skills, skill-supply-chain, hallucinated-domain, unregistered-domain, token-leak, codex, openai, render, generated-code, sinkhole, fork-fixed-upstream-not, mitigated]
---

## TL;DR
The `render-deploy` skill that OpenAI curates in `openai/skills`, and bundled in `openai/plugins` from 2026-03-13 to 08-26, taught agents that Render's private service DNS lived under `render-internal.com`, with example code and a database URL on that domain. Nobody owned the domain. When AIR Security asked Codex to deploy two services that talk to each other, the domain came out of the skill's reference files into the generated code as the default internal API URL and the `INTERNAL_API_URL` environment variable, so an app deployed without overriding it sent its internal requests, bearer tokens included, to a name anyone could register. AIR registered it and ran a listen-only sinkhole, which received "live, token-bearing calls" from real production applications. Render removed every reference from its own copy of the skill in `render-oss/skills` on commit 5152e543 ("Update Guidence on Internal Addresses"), OpenAI removed the Render plugin from `openai/plugins` on 2026-08-26, and AIR says the domain is now held by Render. The OpenAI-curated copy, `skills/.curated/render-deploy/references/service-types.md` on `openai/skills` main, still printed `[service-name].render-internal.com` and the example URL when read on 2026-10-19. The leak path is closed by who owns the domain, not by the skill text an agent reads today: grep deployed code and environment for the domain and rotate any token that travelled in those requests.

## What happened

**The skill.** `render-deploy` is one of the curated skills in `github.com/openai/skills`, written to walk a coding agent through deploying an application to Render by generating a `render.yaml` Blueprint or creating a service through Render's MCP tools; it includes MCP setup steps for Cursor, Claude Code and Codex and references a `RENDER_API_KEY`. The path's history on `openai/skills` begins with "add-partner deploy skills (#68)" on 2026-01-31 and ends with two commits on 2026-02-02; Render maintains its own copy in `render-oss/skills` ("Render Agent Skills", 87 stars), synced by a copybara bot. The skill's `references/service-types.md` presented `[service-name].render-internal.com` as Render's private DNS and used `internal-api.render-internal.com` on port 10000 in a JavaScript example, with a best practice telling the agent to always use `.render-internal.com` domains; `references/configuration-guide.md` claimed `fromDatabase` provides `.render-internal.com` URLs and showed a `postgresql://` connection string on that domain. Render's private networking does not use that domain, and it was unregistered.

**What the agent did with it.** AIR Security's researchers, Eliad Mualem and Dor Granat, had Codex deploy two internally communicating services with the skill loaded. The domain appeared in the generated code as `defaultInternalAPIURL` and in configuration as `INTERNAL_API_URL`; when no value is supplied at runtime the default is used, so the app calls the unregistered name with its service-to-service credentials. That is the mechanism: a reference document inside a skill became a hard-coded default in production code, with the agent's confidence attached.

**The sinkhole.** AIR registered `render-internal.com` and pointed it at a passive, listening-only server. It received token-bearing requests and API calls from real applications that believed the name was their internal service. AIR's post gives no counts, token types or observation window; this file does not supply any.

**The timeline AIR states, and what the repositories show.** AIR: 2026-01-27 guidance added (commit d6231b6c); 2026-03-13 bundled into `openai/plugins` (commit 6a8ab473); 2026-08-14 Render removed all references (commit 5152e543); 2026-08-26 OpenAI removed the Render plugin (commit 33bd9529); 2026-10-14 the post; no report date, no CVE, no quoted statement from either vendor, Render described as having "quickly acknowledged the risk." Checked 2026-10-19: commit 5152e543 is in `render-oss/skills`, not `openai/skills`; its message is "[GROW-3228] Update Guidence on Internal Addresses (#37)" and its diff replaces the private-DNS bullet, the JavaScript example, the best-practice line and the `fromDatabase` claim with "internal address" wording in the two reference files (+18, −21); the page shows no date, so 2026-08-14 is AIR's. Commit 6a8ab47, "Add Netlify and Render deployment skills (#17)", is on `openai/plugins` dated 2026-03-13, and commit 33bd952, "Sync curated plugins and remove app-only integrations (#388)", is dated 2026-08-26; the `plugins/render` tree returns 404 on main, consistent with removal. Commit d6231b6c could not be opened and no 2026-01-27 commit appears in the path's history on `openai/skills`, whose first commit for the path is 2026-01-31. And the OpenAI-curated `references/service-types.md` on `openai/skills` main still contains the "Private DNS: `[service-name].render-internal.com`" line and the `internal-api.render-internal.com:10000` example. AIR's "update to the patched skill" therefore means Render's repository, not the OpenAI catalog an agent loads by name.

**Why this is the skill class, not a Render bug.** Nothing on Render's side was wrong and no server was exploited. The skill is text an agent trusts the way a developer trusts documentation, and the agent copied its example into a default. Every skill, plugin and rules file in the agent's context is a dependency with that property; the [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md) and [skills.sh malicious-skill](2026-08-zenity-skillssh-malicious-agent-skills.md) findings are the malicious version of the same supply chain, the [placeholder-domain skills](2026-09-third-party-com-placeholder-domain-clickfix-agent-skills.md) file is the nearest prior shape, and this one is the unintentional version: a hallucinated domain, published under a vendor's name, into code that ran in production.

**Status.** `mitigated`, not `patched`: the leak path depends on who controls the domain, and AIR says Render holds it; the fix that removes the instruction exists in Render's fork while the upstream OpenAI copy still carries it, so an agent loading the curated skill today still learns the domain. If OpenAI's copy changes, or the domain's holder changes, the status moves.

**Two-source note.** AIR Security is the single researcher and the sinkhole observation is theirs alone; the `render-oss/skills` diff, the `openai/plugins` history and the current `openai/skills` reference file are the repository-side record read this sweep; CSO Online is outlet pickup of AIR.

## Am I affected?

You are in scope if an agent with the `render-deploy` skill, from `openai/skills`, `openai/plugins` or `render-oss/skills` before its fix, generated or edited deployment or service-communication code; the OpenAI-curated copy still carries the domain, so the window has no end date.

```bash
# In every repository the agent touched, and in deployed environment variables
grep -rn 'render-internal' . 2>/dev/null
grep -rn 'INTERNAL_API_URL\|defaultInternalAPIURL' . 2>/dev/null
# The skill copy your agent loads
grep -rn 'render-internal' ~/.codex ~/.claude ~/.cursor .agents .claude 2>/dev/null
# Render dashboard: environment groups and per-service env vars for the same string
```

- A hit in code or configuration means the app has been sending internal requests to a domain it did not own; the tokens in those requests are exposed.
- A hit in a local skill copy means the next generated service will do the same.

## If you are affected

1. Replace the domain with the service's internal address from the Render Dashboard or a Blueprint service reference, as Render's fixed skill now says, and redeploy; a local edit patches nothing deployed.
2. Rotate every credential that travelled in internal requests: service-to-service tokens, API keys passed in headers, and the database password from any URL that copied the example. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) has the order.
3. Read the service's outbound logs for requests to the domain to size the window.
4. Delete old deploy previews and environment snapshots that still carry the value.
5. Replace the skill copy with `render-oss/skills` at or after commit 5152e543, or edit the two reference files by hand until the OpenAI catalog changes.

## Prevention

- Treat skills, plugins and rules files as dependencies: pin them, review their reference documents for domains, URLs and credentials, and re-review on update. [Package vetting checklist](../prevention/package-vetting-checklist.md) applies to skill files as it does to packages.
- Lint generated code for hard-coded hostnames and default URLs before deploy; a default that only matters when an environment variable is unset is the one that reaches production.
- Register, or block at egress, any internal-looking domain your generated code references that you do not own.

## Sources
- [AIR Security, OpenAI Sesame: Skill Vulnerability in OpenAI's Official Skill Made Production Apps Leak Tokens, Real Victims Found in the Wild](https://www.air.security/blog-posts/render-openai) — 2026-10-14, Eliad Mualem and Dor Granat; the reference-file lines, the Codex test and the `INTERNAL_API_URL` default, the sinkhole result, the four commits with dates, the domain transfer, the remediation advice.
- [CSO Online, Hallucinated domain in official OpenAI skill underscores AI supply chain risks](https://www.csoonline.com/article/4236659/hallucinated-domain-in-official-openai-skill-underscores-ai-supply-chain-risks.html) — 2026-10-16, John Leyden; outlet pickup of AIR, the Hoffman quotation.
- [render-oss/skills commit 5152e543, "[GROW-3228] Update Guidence on Internal Addresses (#37)"](https://github.com/render-oss/skills/commit/5152e543) — read 2026-10-19; two reference files, +18 −21, the private-DNS bullet, the example URL, the best-practice line and the `fromDatabase` claim removed; no date shown on the page.
- [render-oss/skills, skills/render-deploy/references/service-types.md](https://github.com/render-oss/skills/blob/main/skills/render-deploy/references/service-types.md) — read 2026-10-19; no `render-internal` reference, "internal hostname" without a pattern.
- [openai/skills, skills/.curated/render-deploy/references/service-types.md](https://github.com/openai/skills/blob/main/skills/.curated/render-deploy/references/service-types.md) — read 2026-10-19; still "Private DNS: `[service-name].render-internal.com`" and the `internal-api.render-internal.com:10000` example.
- [openai/skills, history of skills/.curated/render-deploy](https://github.com/openai/skills/commits/main/skills/.curated/render-deploy) — read 2026-10-19; five commits, 2026-01-31 ("add-partner deploy skills (#68)") to 2026-02-02, none in August.
- [openai/plugins, history of plugins/render](https://github.com/openai/plugins/commits/main/plugins/render) — read 2026-10-19; 6a8ab47 2026-03-13 "Add Netlify and Render deployment skills (#17)", 314574a 2026-04-16 "Render Skills-Only Plugin (#168)", 33bd952 2026-08-26 "Sync curated plugins and remove app-only integrations (#388)"; the `plugins/render` tree on main returns 404.
- [openai/skills, skills/.curated/render-deploy/SKILL.md](https://github.com/openai/skills/blob/main/skills/.curated/render-deploy/SKILL.md) — read 2026-10-19; the skill's own text names `dashboard.render.com`, `mcp.render.com` and `raw.githubusercontent.com` only; the domain is in the reference files, not here.
- [The Hacker News weekly recap, 2026-10-19](https://thehackernews.com/2026/10/weekly-recap-98-zero-days-rogue-ai.html) — one-line mention citing AIR Security.
- Related in this corpus: [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md), [placeholder domains in agent skills](2026-09-third-party-com-placeholder-domain-clickfix-agent-skills.md), [malicious skills on skills.sh](2026-08-zenity-skillssh-malicious-agent-skills.md).
