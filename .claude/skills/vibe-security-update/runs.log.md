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
