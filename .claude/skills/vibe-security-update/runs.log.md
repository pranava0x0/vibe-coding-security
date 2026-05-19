# Runs log — vibe-security-update

> Appended each time the skill runs. Latest at the bottom (chronological).

---

## 2026-05-16 (initial seed)

- **Queries run:** 12 (deep: 8, medium: 4, shallow: 0)
- **New advisories:** 13 (full initial backfill — Shai-Hulud, Shai-Hulud 2.0, qix, Nx s1ngularity, postmark-mcp, Axios, TanStack mini Shai-Hulud, node-ipc, Cursor CurXecute/MCPoison, Claude Code InversePrompt, Amazon Q wiper, Supabase MCP lethal trifecta, slopsquatting, vibe-platform exposure)
- **Updated advisories:** none (first run)
- **Sources gained weight:** all 78 initial entries seeded
- **New sources added:** 78 (initial seed)
- **Notes:** Repo creation sweep. Established baseline. Source weights derived from how many initial advisories cited each source.

---

## 2026-05-17

- **Queries run:** 8 (deep: 8, medium: 0, shallow: 0)
- **New advisories:** 3
  - `2026-05-windsurf-zero-click-mcp-rce` (CVE-2026-30615, CVSS 8.0, zero-click)
  - `2026-04-comment-and-control-pr-injection` (CVSS 9.4 Critical; Claude Code Sec Review, Gemini CLI, Copilot Agent)
  - `2026-05-mcp-stdio-systemic-rce` (OX Security; ~200k MCP servers exposed; 3 DB MCPs disclosed 2026-05-13; Alibaba RDS unpatched)
- **Updated advisories:** 2
  - `2026-05-node-ipc-compromise` — corrected weekly downloads (822K, not 10M), added specific versions (9.1.6, 9.2.3, 12.0.1), DNS C2 IOCs (sh.azurestaticprovider.net, 37.16.75.69), shasum, forensic timestamp marker, env flag, temp dir pattern.
  - `2026-05-tanstack-mini-shai-hulud` — broadened to full Mini Shai-Hulud wave (172 packages, 403 versions, npm+PyPI); attributed to TeamPCP; added @mistralai/@uipath/@opensearch-project scopes; noted first valid SLSA-provenance abuse; added 8 new sources.
  - `2025-08-claude-code-inverseprompt` — added 4 new CVEs (CVE-2025-52882, CVE-2025-59536, CVE-2026-21852, CVE-2026-33068) + TrustFall reference; cross-linked to Comment and Control.
- **Sources gained weight:** snyk.io +1 (16→17), socket.dev +1, stepsecurity.io +1, aikido.dev +1, wiz.io +1, microsoft.com +1, unit42.paloaltonetworks.com +1, thehackernews.com +1, theregister.com +1, github.com/advisories +1, vibe-eval.com +1, darkreading.com +1, picussecurity.com +1, cybersecuritynews.com +1
- **New sources added:** 14 — ox.security, venturebeat.com, policylayer.com, securityweek.com, expel.com, mend.io, safedep.io, cybersecuritynews.com, upwind.io, tomshardware.com, bitsight.com, pointguardai.com, adversa.ai, witness.ai, sentinelone.com, techrepublic.com, waxell.ai, qualysec.com, thecybersecguru.com
- **Notes:**
  - Tier-A deep sweep produced 5 high-confidence incidents in one pass.
  - OX Security and VentureBeat were the breakout new sources this run — added at weight 13/11 respectively.
  - Class issues (Windsurf RCE + MCP stdio + Comment-and-Control) are converging — flagging for a possible **playbook backlog** entry: "MCP write-path hardening" + "CI/AI-agent secret isolation."
  - No PyPI-specific new advisory written — Mistral / PyTorch Lightning rolled into the Mini Shai-Hulud entry rather than splitting.
  - **Deferred:** Google Antigravity sandbox-escape RCE (CyberScoop) and detailed PyTorch Lightning writeup. Both have <2 independent sources at time of sweep.

---

## 2026-05-18

- **Queries run:** 22 (deep: 8, medium: 8, shallow: 6)
- **New advisories:** 8
  - `2026-04-pytorch-lightning-compromise` — Mini Shai-Hulud cross-ecosystem (PyPI + npm); SHA-256 IOC + `.claude/setup.mjs` postinstall artifacts; downgrade to 2.6.1
  - `2026-05-praisonai-auth-bypass` — CVE-2026-44338; Sysdig honeypot saw first exploit attempt in 3h44m; new "disclosure-to-exploit" record for AI-agent frameworks
  - `2026-05-semantic-kernel-rce` — CVE-2026-25592 (CVSS 10.0, .NET) + CVE-2026-26030 (CVSS 9.9, Python); `[KernelFunction]`-as-documentation pattern
  - `2026-05-openclaw-claw-chain` — 4 chainable CVEs (-44112/-44113/-44115/-44118); 245K exposed instances; "Claw Chain" name; patched in OpenClaw 2026.4.22
  - `2026-05-nextjs-react-security-release` — 13 CVEs rollup; headline SSRF CVE-2026-44578 (CVSS 8.6) on self-hosted Next.js + React Server Components DoS CVE-2026-23870; Vercel-hosted not affected
  - `2026-02-google-antigravity-sandbox-escape` — Previously deferred; now has ≥7 independent sources; Pillar Security; `fd -X` flag injection bypasses Secure Mode
  - `2026-05-cursor-open-folder-autorun` — Cluster of 3 CVEs (-26268, -22708, -32202); Git-hook RCE in nested bare repos, Auto-Run built-in bypass, Workspace Trust off-by-default; fixed in Cursor 2.5
  - `2026-03-claude-code-source-map-leak` — Anthropic shipped 59.8 MB `.map` exposing 512K lines of internal TS; supply-chain hygiene incident; precursor to subsequent CVE cluster
- **Updated advisories:** 4
  - `2026-05-tanstack-mini-shai-hulud` — Added CVE-2026-45321 (CVSS 9.6); C2 IOCs (git-tanstack[.]com, *.getsession.org, 83.142.209[.]194, filev2.getsession.org, api.masscan.cloud); 518M+ cumulative downloads; cross-linked to PyTorch Lightning
  - `2026-05-node-ipc-compromise` — Added publisher account (atiertant), Datadog Security Labs analysis, StepSecurity X post
  - `2025-08-claude-code-inverseprompt` — Added May 2026 cluster (CVE-2026-24887, -35021, -39861, -35603); cross-linked source-map-leak as precursor
  - `ongoing-vibe-platform-exposure` — Added RedAccess May 2026 scan (380K apps, 5K leaking sensitive data)
- **Sources gained weight:** socket.dev +1 (17→18), snyk.io +1, stepsecurity.io +1, aikido.dev +1, wiz.io +1, microsoft.com +2 (15→17), thehackernews.com +2 (12→14), venturebeat.com +1, sysdig.com +2 (12→14), sentinelone.com +2 (8→10), darkreading.com +1, bleepingcomputer.com +1, github.com/advisories +1, securityweek.com +2 (10→12), cybersecuritynews.com +2 (8→10), safedep.io +1, hackread.com +1, semgrep.dev +1, orca.security +1, infosecurity-magazine.com +1, socradar.io +1, adversa.ai +1, securityboulevard.com +2, kodemsecurity.com +2, oasis.security (new at 10), phoenix.security +1
- **New sources added:** 24 — akamai.com, particula.tech, nuka-ai.github.io, miggo.io, advisories.gitlab.com, pillar.security, cyberscoop.com, oecd.ai, labs.cloudsecurityalliance.org, danusminimus.github.io, cyera.com, reco.ai, oasis.security, sangfor.com, kaspersky.com, novee.security, tanstack.com, vercel.com, netlify.com, developers.cloudflare.com, hadrian.io, endorlabs.com, lightning.ai, aviatrix.ai, datadoghq.com, axios.com, iansresearch.com, futurism.com, csoonline.com, gbhackers.com, infoq.com, layer5.io, blog.kilo.ai, claudefa.st, dev.to, devops.com, x.com, vibecodingweekly.substack.com, mvidmar.substack.com, ipenewsletter.substack.com
- **Notes:**
  - Single biggest sweep so far: 8 new + 4 updated. Reflects an unusually busy 7-day window covering Anthropic Code with Claude conf (May 6), Microsoft "When prompts become shells" disclosure (May 7), Next.js coordinated release (May 6–7), Mini Shai-Hulud TanStack wave (May 11–12), and OpenClaw Claw Chain (May 13).
  - **Pattern shift detected:** Vendor framework SDKs (Microsoft Semantic Kernel, PraisonAI, OpenClaw) are now a top attack-surface category. Until this sweep the repo skewed toward npm/PyPI registry attacks and IDE prompt-injection; now we have multiple "agent framework with annotation-as-documentation" RCEs. **Playbook backlog candidate:** "AI-agent framework hardening: decorator audit + sandbox-as-policy."
  - **Pattern shift detected:** Disclosure-to-exploit window for AI-agent framework CVEs is < 4 hours (PraisonAI). Treat as new baseline. **Playbook backlog candidate:** "Pinning + auto-update strategy for AI-agent framework dependencies."
  - **Cross-ecosystem worms:** Mini Shai-Hulud now confirmed crossing npm ↔ PyPI with identical payload (PyTorch Lightning + intercom-client on 2026-04-30, then TanStack ecosystem on 2026-05-11). The `.claude/`-postinstall-artifact TTP is consistent across both ecosystems.
  - **Skill update:** Added Tier-D-equivalent sources to the priority list this sweep — Substack newsletters (vibecodingweekly, mvidmar, ipenewsletter) and X.com posts (StepSecurity breaking-news threads). The skill now recognizes social-media security disclosure as a class. No skill behavior change needed beyond the broader source set.
  - **Skill update:** Added `axios.com` (news, not the npm package), `oasis.security`, `cyera.com`, `pillar.security` as new high-signal research sources surfacing this cycle. All weighted 9–11 based on multi-incident contribution.
  - **Deferred:** MaliciousCorgi VS Code marketplace campaign (Koi, 1.5M installs) is from January 2026; covered already in passing in [vibe platform exposure] context, not promoted to its own advisory. Microsoft Exchange CVE-2026-42897, Azure AI Foundry CVE-2026-35435, and the Aliyun-AI-Labs PyPI 2025 incident: out of scope (former two are non-vibe, latter is older). Replit Workspace Security Center 2.0 release (May 8): defender update, not an incident, no advisory needed.

---

## 2026-05-19

- **Queries run:** 20 (deep: 8, medium: 8, shallow: 4)
- **New advisories:** 5
  - `2026-05-claude-code-deeplink-rce` — `eagerParseCliFlag()` argv-smuggle via `claude-cli://` deeplink `q=` parameter; one-click RCE; patched in **Claude Code 2.1.118**. Researcher: Joernchen / 0day.click.
  - `2026-05-claudebleed-chrome-extension` — LayerX disclosure; `externally_connectable` trust-boundary failure lets *any* Chrome extension drive Claude in Chrome; v1.0.70 ships approval prompts but does **not** remove the handler — side-panel/privileged-mode bypass remains. Status: **mitigated, not patched**.
  - `2026-04-vercel-context-ai-breach` — Lumma Stealer → Context.ai → Workspace OAuth → Vercel employee → internal env-var read. Non-sensitive env vars enumerated; Next.js/Turbopack/npm untouched. First widely documented "AI tool → cloud platform" OAuth pivot.
  - `2025-12-langchain-langgrinch` — CVE-2025-68664 (CVSS 9.3, Dec 23 2025) + CVE-2026-34070 (CVSS 7.5, May 2026 path traversal). `dumps()`/`dumpd()` did not escape user dicts with `"lc"` key → deserialize → instantiate framework classes → Jinja2 → env var exfil → RCE. Patched in 0.3.81 / 1.2.5 (LangGrinch) and 1.2.22 (path traversal).
  - `2026-02-cline-clinejection` — Backfilled missing major incident. GitHub-issue-title prompt injection → Cline's own AI triage bot ran attacker `npm install` → Cacheract poisoned Actions cache → publish workflow leaked `NPM_RELEASE_TOKEN` → 8 days later, `cline@2.3.0` published with `postinstall` that installs **OpenClaw** as system daemon on ~4,000 dev machines. Cline rotated the wrong token. Researcher: Adnan Khan.
- **Updated advisories:** 1
  - `ongoing-vibe-platform-exposure` — added **Moltbook** (1.5M auth tokens + 35K email addresses leaked via misconfigured DB), and Georgia Tech Vibe Security Radar Q1 2026 CVE attribution (35 March CVEs vs 6 January, ~6× quarterly growth).
- **Sources gained weight:** snyk.io (18→19), stepsecurity.io (17→18), thehackernews.com (14→15), ox.security (13→14), securityweek.com (12→13), safedep.io (9→10), cybersecuritynews.com (10→11), darkreading.com (10→11), hackread.com (6→7), vercel.com (13→14), github.com/advisories (16→17), trendmicro.com (12→13), miggo.io (7→8), socradar.io (9→10), rescana.com (7→8), cremit.io (5→6), reco.ai (7→8)
- **New sources added:** 14 — 0day.click (researcher, weight 11), layerxsecurity.com (research, 11), cyata.ai (research, 11), nvd.nist.gov (official, 13), techcrunch.com (aggregator, 9), cyberinsider.com (aggregator, 7), business-standard.com (aggregator, 6), safe.security (research, 6), cyberpress.org (aggregator, 5), infosecbulletin.com (aggregator, 5), cyberwebspider.com (aggregator, 4), vucense.com (research, 5), news.ycombinator.com (aggregator, 8), earezki.com (independent, 4)
- **Notes:**
  - **Pattern: AI tool → cloud OAuth pivot.** The Vercel/Context.ai breach is the first publicly documented case where the *AI tool itself* was the upstream supply-chain compromise into a cloud platform. Expect more. Treat every "Connect to my Workspace/Drive/Calendar" OAuth grant to an AI tool as a third-party-risk vector. **Playbook backlog candidate:** "Third-party AI OAuth grants as a privileged access path."
  - **Pattern: argv smuggling.** Claude Code's `eagerParseCliFlag` joins a small but recurring class — Cursor's Auto-Run built-in bypass (CVE-2026-22708) and the InversePrompt cluster — where a string was treated as a different kind of token than intended. Worth thinking about: any AI-tool CLI that "pre-parses" config flags before main argv handling is a candidate for the same bug. **Playbook backlog candidate:** "Auditing AI CLI argument parsers."
  - **Pattern: AI agent installs *another* AI agent.** Clinejection (Cline → OpenClaw via npm postinstall) and Comment and Control (AI-agent CI workers exfiltrating secrets) both involve one AI tool weaponized to install/exploit another. As the AI dev-tool dependency graph thickens, this becomes a generic supply-chain shape. Cross-link both advisories to the [systemic vibe-platform exposure] entry as conceptual neighbors.
  - **Source-discovery pattern:** Primary disclosures are increasingly arriving on **individual researcher blogs and Substack/Medium-style posts** (0day.click, Cyata.ai, LayerX), not on aggregator news sites. Two of this run's five new advisories (Claude Code deeplink RCE, LangGrinch) cite a researcher's own writeup as the canonical source. Skill update: keep researcher domains weighted ≥ 10 even when single-hit, because they are *upstream* of the aggregators.
  - **Skill update:** Pattern recognized — when a vendor releases a security patch *without* removing the underlying trust-boundary (ClaudeBleed v1.0.70), the correct status is `mitigated`, not `patched`. The advisory template handled this fine; no skill change needed, just a discipline note for future sweeps.
  - **Deferred:** OpenHands CVE-2026-33718 (command injection in `get_git_diff()`; CVSS 3.1, authenticated-only, low severity) — logged but not promoted to its own advisory because the auth-required attack profile and low CVSS don't meet the vibe-coding-relevant bar. Will revisit if exploitation is observed. Cloudflare's May 7 AI-first restructuring announcement is corporate news, not a security incident. GPT-5.5-Cyber / Anthropic Mythos / Claude Security beta are capability releases, not advisories. Schneier "How Dangerous Is Anthropic's Mythos AI?" is commentary, not an incident.
