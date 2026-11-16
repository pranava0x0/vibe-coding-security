---
id: 2026-06-blender-mcp-execute-code-file-read-ssrf-path-traversal-four-cves-safe-mode-opt-in
title: "blender-mcp runs model-written Python in Blender unchecked unless BLENDER_MCP_SAFE_MODE=1, and has four CVEs"
date_disclosed: 2026-06-02
last_updated: 2026-11-16
severity: medium
status: mitigated
ecosystems: [pypi, python, mcp, blender, 3d-modeling, ai-coding-agents]
tools_affected: ["blender-mcp on PyPI before 1.6.5 (CVE-2026-66004)", "blender-mcp at or before commit 7636d13 (CVE-2026-10661, CVE-2026-10662, CVE-2026-10688)", "mcp-for-blender, the project's current PyPI name, with safe mode off (the default)", "Claude Desktop, Claude Code, Cursor and other MCP clients configured with the server"]
tags: [cve, mcp, blender, blender-mcp, mcp-for-blender, code-execution-by-design, opt-in-fix, ssrf, path-traversal, prompt-injection, vuldb, vulncheck, 3d-modeling, backfill]
---

## TL;DR
blender-mcp, now published as `mcp-for-blender`, is the MCP server that lets Claude, Cursor and other clients drive Blender. Its `execute_blender_code` tool runs Python written by the model inside your Blender process. The project's README says that by default the AI can run any Python code in Blender. A validator added on 2026-09-02 checks scripts first, and it is off unless you set `BLENDER_MCP_SAFE_MODE=1`. Four CVEs cover this tool, a local file read, an SSRF and a path traversal on asset download. Only the path traversal (CVE-2026-66004) has a fixed release on record, `blender-mcp` 1.6.5. Move to the current `mcp-for-blender`, set `BLENDER_MCP_SAFE_MODE=1`, and treat asset names and descriptions from third-party libraries as untrusted text that reaches the model.

## What happened

| CVE | CNA, date | Finding | Scores (CNA) | Fix evidence read |
|---|---|---|---|---|
| CVE-2026-10688 | VulDB, 2026-06-02 | `execute_blender_code` in `server.py` passes the `code` argument to execution | 5.5 (3.1), 5.1 (4.0) | no fix commit in the record; safe mode is opt-in |
| CVE-2026-10661 | VulDB, 2026-06-02 | `input_image_url` in the Hunyuan3D generation path is opened as a local path | 4.3 (3.1), 5.3 (4.0) | record cites a commit in a fork and an unmerged pull request |
| CVE-2026-10662 | VulDB, 2026-06-02 | `zip_file_url` in the ZIP import path is fetched with no check (SSRF) | 6.3 (3.1), 5.3 (4.0) | same as above |
| CVE-2026-66004 | VulnCheck, 2026-07-24 | `download_polyhaven_asset` writes files to paths taken from API response keys | 5.3 (3.1), 6.0 (4.0) | pull request 258 merged 2026-07-20; `blender-mcp` 1.6.5 |

**The three VulDB records.** All three name the affected version as commit 7636d13 (dated 2026-01-23) and say the project uses rolling releases. They reference GitHub issues 201, 202 and 203, opened on 2026-03-10. The maintainer did not reply on issue 201 before it was closed on 2026-06-25; the two comments are the reporter asking for a response. A pull request linked from it (269) was closed without merging.

For CVE-2026-10661 and CVE-2026-10662 the records cite pull request 205, "Fix arbitrary file read and SSRF in Hunyuan3D integration", and a commit 5b37be25 under a fork's URL. Pull request 205 was closed on the upstream repository without merging. The commit was authored on 2026-03-11 and committed on 2026-04-18. It is not an ancestor of the upstream `main` branch. Issues 202 and 203 were closed on 2026-04-19. On 2026-11-16 the argument names `input_image_url` and `zip_file_url` did not appear in `server.py` on `main`. Not established: which commit or release removed them. No fixed version is given here for those two ids.

**CVE-2026-10688 and safe mode.** The README warns that `execute_blender_code` "allows running arbitrary Python code in Blender". Commit 41d98fc (2026-09-02) added `safe_mode.py`, an allowlist validator. Its own documentation says:

- it is opt-in, through `BLENDER_MCP_SAFE_MODE=1`, and by default nothing is validated;
- the threat it addresses is prompt injection, because asset names and descriptions from Poly Haven, Sketchfab and Hyper3D flow into the model's context;
- it covers the MCP path only. The Blender add-on's socket accepts a raw execute command from any local process, so the validator "is a guard on what the model can be talked into, not a sandbox around Blender".

That is why the status here is `mitigated` and not `patched`. An upgrade with no further action leaves the default unchanged.

**CVE-2026-66004.** VulnCheck's record says a man-in-the-middle or a prompt injection can supply traversal sequences in the asset API response and overwrite files. The GitHub Advisory Database row GHSA-4h8q-hh2j-755w gives pip `blender-mcp` affected `< 1.6.5`, patched 1.6.5. PyPI shows 1.6.5 uploaded on 2026-07-29.

**Two package names.** PyPI `blender-mcp` has 38 releases and stops at 2.0.0 (2026-09-16). PyPI `mcp-for-blender` starts at 1.9.0 (2026-09-01) and its newest is 2.3.0 (2026-11-15), which matches the version in the repository's `pyproject.toml`. The GitHub repository `ahujasid/blender-mcp` now resolves to `ahujasid/mcp-for-blender`. `blender-mcp` 2.0.0 is a shim: its only dependency is `mcp-for-blender>=2.0.0`, and the README says `uvx blender-mcp` still runs the server. So `pip show blender-mcp` prints 2.0.0 while the code that runs is whatever `mcp-for-blender` version was resolved. Check both names. A config pinned to `blender-mcp` 1.6.x or earlier predates the safe mode commit. Safe mode's commit is dated 2026-09-02. Not checked: which release of either name first contains it.

## Am I affected?

```bash
pip show blender-mcp mcp-for-blender 2>/dev/null | grep -E '^(Name|Version)'
```

- Search your MCP client configuration for `blender-mcp` and `mcp-for-blender`. A `uvx` entry runs whatever version it resolves at start.
- `blender-mcp` before 1.6.5: affected by CVE-2026-66004.
- Any version with `BLENDER_MCP_SAFE_MODE` unset: scripts from the model run in Blender with no check. That is the product's documented default.
- Higher exposure: sessions that also search or import third-party assets, read web pages, or open files from others, because that text can steer what the model writes.

## If you are affected

- Move to the current `mcp-for-blender` release and set `BLENDER_MCP_SAFE_MODE=1` in the server's environment in your MCP client config.
- Keep script approval prompts on in the client. Read a script before approving it when the session has pulled in outside content.
- If a session ran scripts you did not review while outside content was in context, follow [if an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md) and [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).
- None of the sources below reports exploitation in the wild. The VulDB records say exploit details are public.

## Prevention

- An MCP bridge into a desktop application gives the model that application's scripting interface. Run Blender for agent work under an account and directory with no credentials. See [agent sandboxing](../prevention/agent-sandboxing.md).
- Enable the server only in sessions that need it. See [MCP hygiene](../prevention/mcp-hygiene.md).
- Pin the server version in the client config and review releases before moving the pin. See the [package vetting checklist](../prevention/package-vetting-checklist.md).
- Not checked: whether the FreeCAD, Unity or Unreal bridges have a validator, or its default. Check each one before trusting it with outside content.

## Sources
- [CVE Services: CVE-2026-10688](https://cveawg.mitre.org/api/cve/CVE-2026-10688), fetched 2026-11-16: VulDB CNA, published 2026-06-02, `execute_blender_code`, commit 7636d13, the scores, issue 201.
- [CVE Services: CVE-2026-10661](https://cveawg.mitre.org/api/cve/CVE-2026-10661), fetched 2026-11-16: `input_image_url`, the scores, issue 202, pull request 205, the fork commit URL.
- [CVE Services: CVE-2026-10662](https://cveawg.mitre.org/api/cve/CVE-2026-10662), fetched 2026-11-16: `zip_file_url`, SSRF, the scores, issue 203.
- [CVE Services: CVE-2026-66004](https://cveawg.mitre.org/api/cve/CVE-2026-66004), fetched 2026-11-16: VulnCheck CNA, published 2026-07-24, `download_polyhaven_asset`, before commit 30a3308, 5.3 and 6.0, issue 257 and pull request 258.
- [ahujasid/blender-mcp issue 201](https://github.com/ahujasid/blender-mcp/issues/201), read through the GitHub API on 2026-11-16: opened 2026-03-10, closed 2026-06-25, two comments, both from the reporter. Issues 202 and 203, same call: opened 2026-03-10, closed 2026-04-19.
- [ahujasid/blender-mcp pull request 205](https://github.com/ahujasid/blender-mcp/pull/205), read through the GitHub API on 2026-11-16: opened 2026-03-11, closed, not merged. Pull request 258: merged 2026-07-20. Pull request 269: closed, not merged.
- Repository files on `main`, read through the GitHub API on 2026-11-16: `README.md` (the safe mode table and section, the arbitrary-code warning), `src/blender_mcp/safe_mode.py` (the module documentation quoted above), `src/blender_mcp/server.py` (the `safe_mode_enabled()` check, no `input_image_url` or `zip_file_url`), `pyproject.toml` (name `mcp-for-blender`, version 2.3.0); commit 41d98fc dated 2026-09-02; 34,614 stars.
- GitHub Advisory Database, queried 2026-11-16 through the API: GHSA-4h8q-hh2j-755w, CVE-2026-66004, Medium, published 2026-07-24, pip `blender-mcp` `< 1.6.5`, patched 1.6.5.
- PyPI `blender-mcp` and `mcp-for-blender`, queried 2026-11-16: the release counts and upload dates above; `blender-mcp` 2.0.0 lists `mcp-for-blender>=2.0.0` as its only requirement and the summary "Renamed to mcp-for-blender".
- Not opened: the VulDB entry pages and the VulnCheck advisory page the records reference. Not checked: which release first carries safe mode, and which commit removed the two Hunyuan3D arguments.
