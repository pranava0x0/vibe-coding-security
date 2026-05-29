---
name: vibe-security-update
description: Sweep current security threats relevant to vibe coding (supply-chain attacks, malicious MCPs, prompt injection campaigns, AI-tool CVEs) and refresh ALERTS.md + advisories/. Trigger when the user says "update the security data", "refresh the sweep", "/vibe-security-update", or any phrase about updating the vibe-coding-security feed. Uses tiered search depth (deep 24h / medium 3d / shallow 7d) and a self-learning source-priority list to focus future runs on sources that produce hits.
---

# vibe-security-update

You are running a fresh sweep of vibe-coding-relevant security incidents and integrating findings into this repo. The repo is `vibe-coding-security/` and you are at its root.

## Output for the user (always include at end)

A 5-line summary:
1. Date of this sweep
2. # of new advisories added
3. # of existing advisories updated (status, IOCs, sources)
4. # of new sources discovered + added to priority list
5. Link to commit (if pushed)

---

## Process

### Step 0 — Load state

Read these files (all required):

- `ALERTS.md` — current active/recent/historical feed
- `advisories/README.md` — index
- `.claude/skills/vibe-security-update/source-priorities.json` — ranked sources
- `.claude/skills/vibe-security-update/runs.log.md` — prior runs

Set:
- `today` = current absolute date (YYYY-MM-DD)
- `t_24h` = today − 1 day
- `t_3d` = today − 3 days
- `t_7d` = today − 7 days

### Step 1 — Tiered web research (in parallel)

Run these in **a single message with parallel WebSearch calls**. Three depth tiers:

**Tier A — DEEP (24h window).** Comprehensive. Aim for ~8 parallel queries. Cover:
- "npm supply chain attack {today.year}" + last 24h
- "malicious npm package compromise {today.year}"
- "malicious mcp server {today.year}"
- "Cursor vulnerability CVE {today.year}"
- "Claude Code vulnerability prompt injection {today.year}"
- "Lovable / Bolt / v0 / Replit security {today.year}"
- "AI coding assistant security incident {today.year}"
- "PyPI malicious package supply chain {today.year}"
- "malicious crate Crates.io supply chain {today.year}" — Rust is now in the cross-ecosystem rotation. Crates run attacker code at *build* time via **`build.rs`** (the Rust analogue of an npm `postinstall` / a PyPI import-time exec). The TrapDoor campaign (May 2026) hit npm+PyPI+**Crates.io** in one wave; watch for `build.rs` that searches for keystores/SSH keys and exfiltrates (e.g., XOR-encrypted blobs to GitHub Gists).
- "supply chain attack poisons .cursorrules CLAUDE.md AI agent config {today.year}" — see the AI-agent-config-poisoning caution below; this is now its own query because the persistence surface is vibe-coding-specific.
- "AI agent framework CVE {today.year}" — rotate framework names: Semantic Kernel / LangChain / OpenClaw / PraisonAI / Langflow / aider / OpenHands / SWE-agent / Cline. As of 2026-Q2 this is a top attack-surface category (decorator-as-documentation pattern → RCE). LangChain in particular sits on ~98M downloads/month — assume any LangGrinch-class finding is high-impact.
- "AI tool OAuth supply chain breach {today.year}" — third-party AI productivity tools (Context.ai, Cline, meeting-notes assistants) granted Workspace/Drive/GitHub OAuth are an upstream-access path into the platforms they connect to. Watch for "[AI tool] employee compromised → [cloud platform] breach" chains; the Vercel/Context.ai April 2026 case is the template.
- "AI agent infrastructure platform breach {today.year}" — **agent-platform-as-MCP-broker is a high-trust hub.** Composio-class platforms sit *above* MCP, brokering ~100 toolkits (GitHub/Gmail/Slack/Notion/Jira/HubSpot/Drive/Calendar/Vercel/Sentry/etc.) on customers' behalf via OAuth grants and API keys. A foothold inside one of these platforms is upstream of every downstream service it brokers — much higher fan-out than a single AI productivity tool. Rotate named instances: **Composio, LangSmith, Pinecone Hub / Smithery, AgentOps, NexusGenAI, Portkey, Helicone, OpenRouter,** and similar agent-orchestration / connector-broker products. The Composio May 2026 breach is the template (LLM-augmented attacker → internal monitoring-agent foothold → automated-remediation pivot → **malicious tool definitions registered inside the sandboxed execution environment** → arbitrary code execution → 5,001 GitHub OAuth tokens + 5,241 API keys exposed).

For each query, prepend top sources from `source-priorities.json` (top 10 by weight) via the `allowed_domains` filter on rotating subsets so we don't miss high-signal pages buried under news aggregators.

**Tier B — MEDIUM (3-day window).** ~4 parallel queries on top-weight sources:
- "{top-3-source-domains} supply chain"
- "GitHub Advisory Database npm critical"
- "Shai-Hulud OR mini-shai-hulud cross-ecosystem npm pypi {today.year}" — also probe for **copycats** now that the worm source is public: "Shai-Hulud copycat / clone npm {today.year}", "leaked worm source supply chain attack competition BreachForums". Once a working supply-chain worm is open-sourced + a paid attack contest is announced (TeamPCP, May 2026), expect a long tail of low-skill clones (chalk-tempalte etc.) with their own C2 and **diversified payloads** (DDoS botnets, persistence) beyond credential theft. Watch for disposable-tunnel C2 (`*.lhr.life` / localhost.run / ngrok) as an IOC.
- "{tool-vendor} security advisory" — rotate vendor across:
  - **IDEs/agents:** Cursor, Anthropic (Claude Code), Windsurf, Google (Antigravity), Cline, aider, OpenHands, OpenClaw
  - **Vibe-coding platforms:** Lovable, Bolt, v0, Replit, Base44
  - **Web frameworks:** Vercel (Next.js), React/Meta, Svelte, Tailwind, Vite, Shadcn UI
  - **Backend/Auth/DB:** Supabase, Prisma, NextAuth.js / Auth.js, FastAPI, Streamlit, Google AI Studio SDK
  - **Agent SDKs:** Microsoft (Semantic Kernel), LangChain / LangGraph, PraisonAI
  - **AI-adjacent third parties** (OAuth-pivot surface — Vercel/Context.ai April 2026 template): meeting-notes / inbox / calendar AI tools that hold Workspace OAuth grants — Context.ai, Granola, Otter, etc. A breach at any of them now is upstream of every platform they're connected to.
  - **IDE / editor extension marketplaces** (VS Code Marketplace, Open VSX, Cursor/Windsurf extension stores): a poisoned extension on one developer's machine is a foothold into everything that editor can reach. The TeamPCP → GitHub internal-repo breach (May 2026, via a poisoned VS Code extension) is the template; see also the Amazon Q wiper and MaliciousCorgi campaign. Query "malicious VS Code extension {today.year}" / "Open VSX malicious extension".
  - **AI-agent skill / plugin marketplaces** (ClawHub for OpenClaw, Claude Code skills, MCP registries/servers): the agent-world analogue of npm/Open VSX, usually open-by-default. ClawHavoc (Koi, Feb 2026) flooded ClawHub with 335+ malicious skills dropping Atomic Stealer via fake prerequisites. Query "{agent} skills marketplace malicious {today.year}" / "ClawHub OR ClawHavoc OR mcp registry malicious skill". Also rotate widely-used **MCP servers** (mcp-atlassian, Azure MCP Server, **`aws-mcp-server` (community) vs AWS's official "AWS API MCP" — distinct projects, distinct CVE streams**, nginx-ui, n8n-mcp, GitHub/Slack/Supabase MCP) for "unauthenticated by default" RCE/SSRF CVEs. Note that **"cloud-provider MCP" is now a recurring named-instance pattern** — AWS, Azure, GCP each have multiple MCP surfaces (cloud-provider's own + popular community wrappers), and CVE streams cluster around the same root: HTTP transport bound to 0.0.0.0, allowed-commands lists treated as documentation, IMDS reachable from the server process.
- "{vendor} coordinated security release {today.year}" — catches multi-CVE rollups (Vercel May 2026 shipped 13 in one batch; Anthropic similar cadence post-source-leak).
- **Industry security blogs (user-requested coverage).** Sweep the big-vendor security feeds directly, not just via aggregators: Anthropic, OpenAI, Google (Project Zero / Security Blog), Microsoft (MSRC), AWS, Cloudflare, Red Hat, Databricks, Salesforce, Oracle. And treat **open-source advisory databases + registries as primary sources**: GitHub Advisory Database (GHSA), GitLab Advisory DB, NVD, CISA KEV, PyPI/npm security feeds. These often carry the canonical CVE/version data before any blog.

**Tier C — SHALLOW (7-day window).** ~3 parallel queries to catch slower-moving stories and social-media disclosure:
- "vibe coding security incident week {today.year}"
- "AI agent CVE OR security disclosed {today.year}"
- "vibe coding security site:substack.com OR site:x.com OR site:bsky.app {today.year}" — Substack newsletters (vibecodingweekly, mvidmar, ipenewsletter) and security-research X/Bluesky posts (StepSecurity, Snyk, Aikido, Socket) regularly break new IOCs hours before traditional aggregators pick them up. Also probe `news.ycombinator.com` and `reddit.com/r/{programming,netsec,cybersecurity}` discussions for first-hand reports.
- **Researcher blogs are upstream of aggregators.** Many primary disclosures land on the researcher's own domain (e.g., 0day.click, cyata.ai, layerxsecurity.com, pillar.security, oasis.security, danusminimus.github.io, oddguan.com — Aonan Guan's Claude Code sandbox/argv findings) hours-to-days before The Hacker News / Cybersecurity News mirror them. Also sweep **first-party vendor incident-response posts** (e.g., openai.com's "Our response to the TanStack npm supply chain attack") — when a major AI vendor is downstream of a supply-chain wave, its own writeup names the affected internal systems and timeline. If a Tier-A aggregator query surfaces a story citing "researcher X at firm Y," go fetch firm Y's own writeup directly — that's the canonical IOC source. Add the researcher domain to `source-priorities.json` at weight 10–11 on first hit even if it's single-source, because subsequent runs will benefit.

Don't repeat queries already run within the last 24h (check `runs.log.md`).

### Step 2 — Triage findings

For each unique candidate incident pulled from results, decide:

**A. NEW ADVISORY** — write a new file in `advisories/` if:
- Package > 100k weekly downloads compromised, OR
- CVE in major AI coding tool, OR
- CVE in major AI-agent framework SDK (LangChain, Semantic Kernel, PraisonAI, OpenClaw, etc.), OR
- CVE in core vibe-coding web stack (Next.js, React, Svelte, Vite, Tailwind, FastAPI, Streamlit, Prisma, NextAuth.js, Supabase) with practical exploitation path, OR
- Malicious MCP server, OR
- Prompt-injection PoC against vibe-coding tool, OR
- Vibe platform data exposure with PII impact, OR
- Cross-ecosystem worm (npm ↔ PyPI ↔ RubyGems with identical payload), OR
- Significant supply-chain hygiene incident at a major AI vendor (e.g., source-map leak, accidental token exposure)

Use the template in `CONTRIBUTING.md`. Filename: `YYYY-MM-short-id.md`.

**B. UPDATE EXISTING** — append to an existing advisory if:
- Status changed (active → contained, etc.)
- New IOCs published
- New sources strengthen / correct the writeup
- Patched version released

Always bump `last_updated` in frontmatter when touched.

**C. SKIP** — log but don't write up if:
- Already covered in an existing advisory with no new info
- Not relevant to vibe coding audience (e.g., kernel CVE, generic enterprise vuln)
- Single unconfirmed source (need ≥2 independent for a full advisory)

### Step 3 — Update ALERTS.md

For every NEW or UPDATED advisory:

- Insert/move into the right tier (🔴 active / 🟠 recent / 🟡 historical) by date:
  - 🔴 active = last 14 days OR malware still propagating
  - 🟠 recent = last 12 months
  - 🟡 historical = older OR pattern-class
- Update the `Last refreshed:` date at the top of ALERTS.md.
- Maintain latest-on-top within each tier.

### Step 4 — Update source priorities (the learning step)

For each source domain that contributed to a NEW or UPDATED advisory this run:

```python
# Pseudocode
src = source_priorities["sources"][domain]
src["hits"] += 1
src["last_hit"] = today
src["weight"] = min(20, src["weight"] + 1)   # cap at 20
src["ecosystems"] = unique(src.get("ecosystems", []) + new_ecosystems)
```

For sources NOT seen in any run for >60 days, decay weight by 1 (min 1). This keeps the list responsive to changing landscape.

For NEW sources discovered this run (not yet in the list), add with `weight: 5, hits: 1, last_hit: today, ecosystems: [...]`.

Write the updated JSON back. Sort by weight desc for readability.

### Step 5 — Append to runs.log.md

Add an entry:

```markdown
## YYYY-MM-DD

- **Queries run:** N (deep: a, medium: b, shallow: c)
- **New advisories:** [list of IDs] or "none"
- **Updated advisories:** [list of IDs] or "none"
- **Sources gained weight:** [list of domains]
- **New sources added:** [list of domains]
- **Notes:** [anything noteworthy — false-alarms, blocked domains, sweep duration]
```

### Step 6 — Sanity checks before committing

- All new advisory files have valid frontmatter (id, title, date_disclosed, last_updated, severity, status, ecosystems, sources).
- All internal links resolve (e.g., references to `playbooks/foo.md` exist).
- ALERTS.md still parses as markdown.
- `advisories/README.md` table has rows for all advisories.
- No secret or PII accidentally pasted into an advisory.

### Step 7 — Commit + push

```bash
git add -A
git status --short
# If anything changed:
git commit -m "sweep YYYY-MM-DD: N new, M updated"
git push
```

If nothing changed (zero new, zero updated), still commit the `runs.log.md` + `source-priorities.json` updates with message: `sweep YYYY-MM-DD: no new incidents`.

---

## Source-priority semantics

The `source-priorities.json` schema:

```json
{
  "version": 1,
  "last_updated": "YYYY-MM-DD",
  "notes": "Higher weight = query first / trust faster. Cap 20. Min 1.",
  "sources": {
    "<domain>": {
      "weight": <int 1-20>,
      "hits": <int>,
      "last_hit": "YYYY-MM-DD" | null,
      "ecosystems": [<str>...],
      "tier": "vendor" | "research" | "aggregator" | "independent" | "official"
    }
  }
}
```

Use `weight` to:
- Pick top 10 sources for the `allowed_domains` filter in deep-tier queries
- Decide whether a single-source claim is trustworthy (weight ≥ 12 = OK to start a draft; lower = wait for second source)

## Constraints & cautions

- **Don't fabricate.** If a candidate incident doesn't have ≥2 independent sources, mark it `status: unconfirmed` in a new advisory and link only the sources you have. Do not invent IOCs, package names, or version numbers.
- **Verify dates against `today`.** Use `Today's date is YYYY-MM-DD` from the system context as ground truth, not the model's intuition.
- **Cap output.** If a sweep finds more than 10 candidate incidents, prioritize by severity × audience overlap with vibe coders. Log skipped ones in `runs.log.md` under "Notes: deferred".
- **Don't touch playbooks/prevention** in a routine sweep — those are evergreen. If you find a new attack pattern that warrants a new playbook, flag in `runs.log.md` under "Notes: playbook backlog" and let a human decide.
- **Don't auto-resolve status to `patched`** unless a vendor explicitly says so in a primary source.
- **Treat AI-agent framework CVEs as time-critical.** As of 2026-Q2, baseline disclosure-to-exploit is < 4 hours (per Sysdig honeypot data on PraisonAI). Prioritize these in triage and write them up same-day even if only 2 sources are available.
- **Cross-link cross-ecosystem worms — and Rust/Crates.io is now in scope.** When the same threat actor or payload appears in multiple ecosystems, cross-link the advisories explicitly (see Mini Shai-Hulud: TanStack ↔ PyTorch Lightning). Don't let the npm advisory and the PyPI advisory live in isolation. The campaign list now routinely spans **npm (`postinstall`) ↔ PyPI (import-time exec) ↔ Crates.io (`build.rs` build script)** — TrapDoor (May 2026) shipped all three from one actor in timed waves. When you see a cross-ecosystem stealer, check whether there's a Rust crate arm using `build.rs`, and whether the same campaign marker / GitHub account / Gist exfil endpoint appears across registries.
- **AI-agent config + skill files (`.cursorrules` / `CLAUDE.md` / `AGENTS.md` / `SKILL.md`) are a write-target, not just a read-target.** Earlier incidents *read* AI-tool config to steal creds (Bitwarden CLI AI-tool collector; Nx Console `~/.claude/settings.json` theft). TrapDoor (May 2026) inverts it: a malicious package **writes a hidden prompt-injection instruction into the repo's `.cursorrules` / `CLAUDE.md`**, hidden with **zero-width Unicode**, so the developer's *own* agent re-runs the attack on its next invocation (exfiltration disguised as an "automated security scan"). This fuses the GlassWorm steganographic-Unicode technique with AI-config-as-persistence/re-infection. The class has been formalized by the **Cloud Security Alliance "Agent Context Poisoning: SKILL.md and the New AI Supply Chain Attack Surface"** research note (2026-05-06) — payloads are natural-language behavioral instructions interpreted by models at runtime, not machine code, so static analysis and sandboxing don't catch them. Triage cues: on any supply-chain or repo-compromise finding, ask **"did it touch an agent-instruction file?"**; offer the grep-for-invisible-Unicode heuristic over `.cursorrules`/`CLAUDE.md`/`AGENTS.md`/`SKILL.md`/`.github/copilot-instructions.md`/`.windsurfrules`; and advise readers to keep those files in version control and diff them on every dependency change. This is a vibe-coding-specific surface — write such incidents up even when the headline is "another crypto stealer," because the AI-config persistence is the part our audience won't see coming.
- **Decorator-as-documentation pattern.** Watch specifically for vulnerabilities where an SDK annotation (`[KernelFunction]`, `@tool`, `@function_tool`, FastAPI's `@app.get`) is treated as documentation rather than a security boundary. This is now a known recurring class. When you see one, look for sibling vulnerabilities in the same SDK.
- **"Two parsers, one string" class (argv-smuggling + resolver disagreement + reconstructed-URL disagreement + check-vs-effect scope disagreement).** A recurring root cause: two components disagree on how to interpret the same value, and the security check runs on the *wrong* interpretation. Four known shapes now: (1) **Argv-smuggling / pre-parser** — an "eager" pre-parser walks `process.argv` for a flag (Claude Code's `eagerParseCliFlag`, Cursor's auto-run built-in handling) without tracking whether the matched string is itself the *value* of another flag, so an attacker controlling any argv element (deeplink, URL handler, MCP tool reply) smuggles arbitrary flag values. (2) **Matcher-vs-resolver disagreement** — an allowlist matcher and the OS/network resolver disagree on where a hostname ends, e.g. Claude Code's **SOCKS5 null-byte bypass** (`attacker.com\x00.google.com` passes the `.google.com` suffix check, the OS truncates at `\x00` and dials `attacker.com`, May 2026). (3) **Reconstructed-URL vs canonical-scope disagreement (host-header bypass)** — auth middleware reads a *rebuilt* URL (`request.url.path`, built from the `Host` header), the router reads the *canonical* ASGI scope path (`scope["path"]`), and a malformed `Host: foo?` re-splits the URL so they diverge — auth check runs on the wrong path while the protected endpoint still gets dispatched. **Starlette BadHost CVE-2026-48710 (May 2026)** is the framework-level case; downstream FastAPI/vLLM/LiteLLM/Python-MCP-SDK/TGI/OpenAI-proxy apps that authorize on `request.url.path` are vulnerable until they upgrade to Starlette ≥ 1.0.1 *or* refactor middleware to use `request.scope["path"]`. (4) **Check-vs-effect scope disagreement** — a deny-list / permission check binds to *current* (mutable) workspace/scope state, but agent input can rewrite that state before the operation runs, so the permission check evaluates against a *different* scope than the operation actually uses. **Windsurf CVE-2025-62353 (Oct 2025)** is the cleanest case: README.md prompt-injection rewrites Cascade's workspace path to `/`, then `write_to_file` targets arbitrary paths — **even with Auto-Execution OFF and `write_to_file` on the explicit deny list** (the deny check evaluated the rewritten scope). Same shape in any agent that lets agent-readable content mutate the scope of subsequent security checks. Note the discovery vector for BadHost — X41 D-Sec found it during an OSTIF-sponsored vLLM source-code audit, then realized it was a framework-level bug below vLLM — so an audit of any single downstream consumer of Starlette is implicitly an audit of the framework; flag this when sweep results name an Alpha-Omega / OSTIF audit. Same family as the InversePrompt cluster. **General triage cue: whenever the framework hands you both a canonical and a derived/reconstructed value of the same thing, the canonical one is the security boundary** — argv structure, post-canonicalization path, `scope["path"]`, the bytes that will actually hit `connect()`, the user-confirmed-at-session-start workspace path. **And: when a security check evaluates state that the operation it's gating can also mutate, the check is a permission honeypot, not a permission boundary** — bind security decisions to immutable scope, or re-check after any scope-changing input. Look for this whenever a value crosses a boundary between an in-app validator and a lower-level executor/resolver/dispatcher (argv parser, DNS, SOCKS, shell, path canonicalizer, ASGI router, workspace-scope manager).
- **AI-tool OAuth pivot pattern.** A breach at a third-party AI productivity tool that holds Workspace/Drive/GitHub OAuth grants is upstream of every cloud account that authorized it. The Vercel/Context.ai April 2026 incident is the first widely documented case; expect more. When triaging an AI-vendor breach disclosure, check what *other* platforms the breached tool had OAuth into — those are downstream victims.
- **Vendor patched ≠ patched.** If a vendor ships a fix that adds approval prompts or alerts but leaves the underlying trust-boundary intact (cf. ClaudeBleed v1.0.70), the correct status is `mitigated`, not `patched`. Don't auto-promote based on "vendor released a version." Read the researcher's follow-up and confirm the structural fix.
- **Silent patch (no CVE/advisory) ≠ no incident.** Some vendors fix security bugs quietly — no CVE, no advisory, no changelog note. Claude Code's network-sandbox **SOCKS5 null-byte bypass** was fixed in v2.1.90 (2026-04-01) with zero disclosure; it was the *second* silently-patched Claude Code sandbox bypass in ~5 months (prior: CVE-2025-66479). Implications for the sweep: (1) a "silent fix" disclosure (usually from the finding researcher's own blog weeks later) IS a writeable incident — set `status: patched` but call out the silent handling and the unprotected window; (2) advise readers to keep AI tools on `latest` and not pin old versions, because **"latest" carries undisclosed security fixes you can't see in release notes**. When a researcher blog says "they fixed it quietly," diff the fixed vs. prior version to confirm and record the vulnerable version range.
- **Connector-chaining lethal trifecta in desktop AI apps.** When an AI desktop app (Claude Desktop, Cursor, etc.) lets the model autonomously compose connectors, a low-trust *reader* connector (calendar, email, Drive, web) piped into a high-trust *executor* connector (a local MCP server that runs shell/code) collapses the lethal trifecta into one app — a malicious calendar event + a vague prompt ("take care of it") = zero-click RCE (Claude Desktop Extensions / DXT, CVSS 10.0, LayerX; Anthropic declined to fix as "outside our threat model"). Triage cue: on any AI-desktop/IDE finding, ask whether reader and executor connectors share one trust domain, and whether the vendor's response is "won't-fix / out of threat model" (→ `status: active`, not `mitigated`). Siblings: Supabase MCP lethal trifecta, Windsurf zero-click MCP.
- **AI-agent → AI-agent supply chain.** Recurring: one compromised AI tool installs a second AI agent on victims (Clinejection → OpenClaw via npm postinstall; Comment and Control → exfil via Claude Code Sec Review). When you find a compromised AI dev tool, check whether the payload installs *another* known AI agent — cross-link both advisories.
- **Provenance is identity, not integrity.** Supply-chain worms now defeat provenance attestation in two ways: (1) hijacking a real release pipeline mid-build so the *legitimate* pipeline signs a malicious artifact (TanStack/Mini Shai-Hulud, May 11 2026 — first valid SLSA provenance on malicious npm), and (2) **self-minting cryptographically valid Sigstore attestations** with an ephemeral EC keypair + OIDC identity token, so every republished package shows a green "verified provenance" badge and passes standard verification (@antv/durabletask wave, May 19 2026). A green provenance/SLSA badge proves *who* built an artifact, **not that it is safe** — never treat it as a clean signal. Look for this whenever a worm "republishes under legitimate maintainer identity."
- **Poisoned IDE/editor extension as a platform-breach vector.** A malicious version of an editor extension (VS Code / Cursor / Windsurf / Open VSX) on a single developer's machine is a foothold into every repo and credential that editor touches. TeamPCP used exactly this — the trojanized **Nx Console** extension (`nrwl.angular-console@18.95.0`, May 2026) — to exfiltrate ~3,800 of GitHub's *own* internal repos. Same trust-transfer shape as the Amazon Q wiper and postmark-mcp (build trust over clean versions, then push one poisoned release) and a sibling of the AI-tool OAuth-pivot class. When triaging an "AI/dev tool was compromised" story, check whether the delivery vector was an extension marketplace, and whether silent auto-update carried the payload. Note also: extension payloads now specifically target **AI-tool config** (`~/.claude/settings.json` and similar) alongside cloud creds — flag that as its own IOC.
- **Cross-incident credential chaining (trace the leaked token forward).** Stolen credentials don't stay in their original incident. The Nx Console compromise happened because an Nx contributor's GitHub token leaked in the *prior* TanStack/Mini Shai-Hulud wave, then got reused a week later to publish the poisoned extension, which became the foothold for the *downstream* GitHub internal-repo breach — three "separate" incidents that are one chain. Sweep discipline: when a wave dumps credentials, ask **"whose token was stolen, and what can it publish next?"** and proactively check the maintainers/orgs named in a credential-theft wave for follow-on registry/extension compromises. Cross-link the chain explicitly (token-leak advisory ↔ extension advisory ↔ breach advisory).
- **Steganographic extension payloads + un-takedownable C2.** GlassWorm (Oct 2025 → 2026, recurring) hides its logic in **printable-but-non-rendering Unicode** (invisible to a human reviewer and to many diff tools) and pins C2 to a **Solana blockchain memo** (a censorship-resistant dead-drop) backed by direct-IP + Google Calendar fallbacks — so takedowns can't reach the control channel and the worm self-reseeds with every set of stolen publish creds. When triaging an extension/worm story, look for "invisible Unicode," "blockchain C2," "Open VSX," and "self-propagating," and offer a detection heuristic (grep for zero-width / variation-selector / bidi code points in extension source).
- **Incomplete fix ≠ patched.** A vendor shipping a version labeled "fixed" doesn't mean the hole is closed — confirm against a researcher's follow-up. Langflow 1.8.2 was widely reported as the CVE-2026-33017 patch but remained exploitable (JFrog); only 1.9.0 actually fixed it. When a "patched" version exists, search "{tool} {CVE} still exploitable / patch bypass / incomplete fix" before setting `status: patched`.
- **AI-agent skill/plugin marketplace poisoning.** AI agents now ship their own community "skill"/plugin marketplaces — **ClawHub** for OpenClaw (formerly Clawdbot/Moltbot), plus Claude Code skills, MCP registries, and the like. These are the npm/Open-VSX of the agent world and are usually **open-by-default**: ClawHub's only publish gate was a GitHub account one week old. ClawHavoc (Koi, Feb 2026) flooded it with **335+ malicious skills** (of 341/824+ found) that use **fake prerequisites** to drop Atomic Stealer (AMOS). Installing a skill is functionally `curl | bash` with the user's privileges. Triage cue: treat any "agent skill / plugin / extension marketplace" the same as a package registry — query "{agent} skills marketplace malicious / {marketplace} stealer," count it as supply-chain (not a product CVE), and write it up separately from any product-vuln advisory for the same agent (cf. ClawHavoc vs. OpenClaw "Claw Chain" CVEs). Watch for **fake-prerequisite** social engineering and **macOS password-prompt (osascript) → AMOS** as recurring IOCs. **It's a class, not one campaign / one site:** Snyk's "ToxicSkills" audit (May 2026) spanned **ClawHub *and* skills.sh** (3,984 skills) and found prompt injection in 36% + 1,467 malicious payloads — so rotate *multiple* skill registries, not just ClawHub. Two extra IOC/heuristic cues this surface taught us: (a) **runtime-fetch evasion** — ~3% of skills (21% of malicious ones) fetch-and-execute remote content at install/run time, so the published skill passes review and flips malicious later; "scan-on-publish clean" is **not** safety. (b) **"skill scanner" tools are themselves a target** — distrust a scanner badge and the scanner binary alike. A **"ToxicSkill"** = looks benign in static review but the *agent executing it* is the gadget that turns it malicious.
- **Open-sourced/leaked worm → commoditized copycat wave.** When a threat actor *publishes the working source* of a supply-chain worm and/or runs a paid "biggest attack" contest (TeamPCP open-sourced Mini Shai-Hulud on 2026-05-12 + a $1,000 BreachForums competition), the barrier to a Shai-Hulud-class attack collapses to "clone the repo, swap the C2 key." Expect a long tail of **low-skill clones** within days (chalk-tempalte, axois-utils, etc.), often **typosquats** of popular packages, with **diversified payloads beyond credential theft** — Golang DDoS botnets (Phantom Bot), persistence (Windows Startup / Linux scheduled task). Triage cues: low download counts but novel actors; **disposable-tunnel C2** (`*.lhr.life` / localhost.run / ngrok / trycloudflare) as an IOC; the planted GitHub-repo marker ("A Mini Sha1-Hulud has Appeared"). Write the copycat wave up *separately* from the original campaign and cross-link — the actor and trigger differ (deliberate release, not maintainer compromise).
- **MCP servers are unauthenticated network services by default.** A growing class: a widely-used MCP server binds `0.0.0.0` with no auth in its HTTP transport, so any network-reachable attacker invokes its tools (nginx-ui MCPwn CVE-2026-33032; Atlassian `mcp-atlassian` MCPwnfluence CVE-2026-27825/-27826, 4M+ downloads, SSRF+arbitrary-write→root RCE; Azure MCP Server CVE-2026-32211 missing-auth info-disclosure + CVE-2026-26118 SSRF). Triage cue: on any MCP-server finding, check the default bind address and whether auth is opt-in; fold concrete named instances into the systemic MCP advisory rather than spawning one advisory per server.
- **Agent-platform-as-MCP-broker — a high-trust hub with massive fan-out.** Above MCP sits a class of platforms that *brokers* tool calls — Composio, LangSmith, Smithery / Pinecone Hub, AgentOps, NexusGenAI, Portkey, Helicone, OpenRouter — holding customers' OAuth grants and API keys for ~100 downstream services on their behalf. A breach inside one of these is upstream of *every* service it brokers (GitHub/Gmail/Slack/Notion/Jira/HubSpot/Drive/Vercel/Sentry/…). Much higher fan-out than the [Vercel/Context.ai](advisories/2026-04-vercel-context-ai-breach.md) AI-tool OAuth-pivot (single tool, single tenant) or the [Bitwarden CLI AI-collector](advisories/2026-04-bitwarden-cli-shai-hulud-third-coming.md) (cred-scraper module). The [Composio May 2026 breach](advisories/2026-05-composio-ai-agent-platform-breach.md) is the template: 5,001 GitHub OAuth tokens + 5,241 API keys touched in one foothold. Triage cue: when an AI-agent platform that holds OAuth grants discloses a breach, **enumerate every downstream toolkit it brokers** — each is a separate rotation surface. Treat as a sibling of "AI-tool OAuth pivot" but distinct because the fan-out is the platform's *whole product*, not an incidental integration.
- **LLM-augmented attacker as an explicit category.** Earlier sweeps *inferred* AI augmentation from speed; [Composio's May 2026 disclosure](advisories/2026-05-composio-ai-agent-platform-breach.md) explicitly attributes attack pattern generation to LLMs ("brute-forcing many combinations of exploits using LLM-generated attack patterns"). Implications for the sweep: (1) defenders' rate limits and WAF signatures were calibrated against humans and are now under-scaled — an attacker with an LLM can produce 10,000 well-formed candidate exploits per minute; (2) "exceptional speed / deep knowledge of internal architecture" in a vendor IR post often correlates with LLM-augmented reconnaissance — if the vendor names it, record it; (3) AI-platform employees with broad-scope OAuth grants (Gmail / Workspace) are an outsized target because magic-link sign-in chains turn one stolen email account into platform admin. Watch for this language in vendor IR posts and quote it directly.
- **"Tool definitions are documentation" inside agent platforms is the new "decorator-as-documentation."** Where SDK annotations (`[KernelFunction]`, `@tool`, `@function_tool`) were treated as docs by Semantic Kernel and friends, agent *platforms* (Composio) treat **runtime tool-definition registration** the same way — `register_tool(name, handler)` is taken as an extensibility / docs primitive rather than a privileged write. The May 2026 Composio breach was the first widely-disclosed case where an attacker, having reached a sandboxed execution environment, **registered new malicious tool definitions** to chain privileges to arbitrary code execution. Triage cue: on any agent-platform / orchestration-framework finding, ask whether the platform exposes a tool-registration API to its own internal agents and whether that API is gated by code review / signed registration / rate limits — if not, that's the *write*-target analogue of `.cursorrules`/`CLAUDE.md`/`SKILL.md` on the developer side.
- **"Localhost is not a security boundary in the browser-attacker model."** A growing class of dev-tool / local-agent CVEs hinge on the assumption that "binds to 127.0.0.1, therefore safe." It isn't — the victim's *browser* trivially reaches `localhost`, and a single click on a malicious link delivered by any out-of-band channel (Slack, email, AI-tool chat, social) is an attack. **OpenClaw CVE-2026-25253 (Jan 2026)** is the cleanest worked example: the Control UI parsed a `gatewayUrl=` query parameter from the URL it was loaded with, repointed the WebSocket at an attacker-controlled gateway, leaked the auth token, and ran arbitrary shell commands — all from one bookmark, including against NAT'd / firewalled / IP-allowlisted instances. Sibling cluster: Open WebUI / Jupyter / Marimo / Langflow when bound to localhost without CSRF tokens or origin checks; many MCP servers when bound to localhost via HTTP transport. Triage cue on any local-agent UI / control-panel CVE: ask **(a) does the UI parse URL parameters or accept POSTs without CSRF tokens?**, **(b) does it apply those parameters as runtime config (gateway URL, MCP server, workspace path, settings file)?**, **(c) is there an Origin / Referer / SameSite check on state-changing requests?** If any of (a)/(b) and not (c), that's a 1-click attack surface regardless of network topology. Cross-link with the agent-config-write-target caution (TrapDoor / Nx Console / Bitwarden CLI) and the connector-chaining-lethal-trifecta caution (Claude Desktop DXT) — all three classes share the same defensive pattern: never let agent-readable input (URL params, file contents, fetched pages) cross into the privileged-write / privileged-execute path without an explicit, immutable user confirmation.
- **Registry-side hygiene matters as much as client-side (build-system primitives are supply-chain primitives).** [Cargo CVE-2026-5223](advisories/2026-05-cargo-symlink-sparse-url-cves.md) — symlink-override that lets a malicious crate overwrite the cached source of another crate in the same registry — affects every Cargo before Rust 1.96.0, but **crates.io users are NOT affected** because crates.io rejects symlinks at upload time. Generalizes a recurring lesson: registry-level enforcement closes the same primitive that client-level extraction misses. Use this as a triage / framing cue when writing up archive-extraction CVEs (symlinks, ZIP-slip, path traversal): always note whether the public registry server-side blocks the primitive, and whether self-hosted / corporate registries do the same. The general statement: **every archive-extraction primitive a client doesn't guard is one a registry can guard server-side, and vice-versa — defense in depth across both layers.** Examples: npm registries can reject `postinstall` from anonymous publishers / first-week accounts; PyPI mirrors can reject `*.pth` top-level files in uploaded wheels (the [elementary-data](advisories/2026-04-elementary-data-pypi-ghcr-compromise.md) primitive); private Cargo mirrors can reject symlinks; container registries can reject layers that contain setuid binaries.
