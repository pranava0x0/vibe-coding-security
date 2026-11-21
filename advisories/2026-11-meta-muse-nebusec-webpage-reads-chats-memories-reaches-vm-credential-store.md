---
id: 2026-11-meta-muse-nebusec-webpage-reads-chats-memories-reaches-vm-credential-store
title: "Meta Muse: NebuSec shows a web page reading chats and memories with no approval prompt, then reaching the VM's credential store; reported fixed"
date_disclosed: 2026-11-20
last_updated: 2026-11-21
severity: high
status: unconfirmed
ecosystems: [personal-agents, meta-muse, browser-agents, cloud-sandbox]
tools_affected: ["Meta Muse personal agent (cloud VM per user), before the fixes NebuSec reports", "accounts connected to a Muse agent", "agent platforms that run a bundled Chromium beside the agent's credentials"]
tags: [personal-agent, prompt-injection, browser, sandbox-escape, credential-store, researcher-disclosure, vendor-silent, no-cve]
---

## TL;DR

[NebuSec](https://nebusec.ai/research/meta-muse-credential-exposure/) reported on 2026-11-20 that a web page opened by Meta's Muse agent could send out and alter the user's chat history and stored memories with no approval prompt. A second chain took control of the user's cloud VM, including its credential store. NebuSec says every exploit was patched before publication. Meta has not confirmed that, [The Hacker News](https://thehackernews.com/2026/11/a-single-malicious-webpage-let.html) reports. There is no version to update. Review what your Muse agent is connected to.

## What happened

Muse is Meta's personal agent, launched on 2026-09-08 according to The Hacker News. Each user's agent runs on its own cloud VM. A service called Sentinel is meant to gate everything the agent sends out.

NebuSec published two posts on 2026-11-20.

- [The first](https://nebusec.ai/research/meta-muse-credential-exposure/) lists its findings as "Sensitive user data could be accessed without approval" and "Persistent user information could be modified".
- [The second](https://nebusec.ai/research/inside-meta-muse/) describes a chain through the bundled Chromium and the VM's Linux kernel. It names Chromium issue numbers and no CVE ids. It says the kernel fell inside the affected ranges of several CVEs and names none.

Limits NebuSec states:

- The work was a laboratory test. The posts do not say whether any real user's data was accessed.
- The compromise stayed inside one user's VM. NebuSec did not reach the host or other users.
- It tested the bundled Chromium in depth and not the other three browser backends.

On fixes, the first post says "all exploits described in our research had been patched by the time of publication". Neither post gives a report date or a fix date. The posts do not say whether the Sentinel policy design changed.

This file is `unconfirmed` because the fix is known only from the researcher. The September flaw in [the Muse macOS app](2026-09-meta-muse-macos-dictation-endpoint-agent-token-hijack.md) is a different issue on the user's device.

## Am I affected?

- You use Muse and have connected accounts to it, such as mail, documents or payment.
- Your agent opened web pages you did not choose, for example from a search or a link in a message.
- No source gives a date after which the service is fixed, so no window can be stated.

## If you are affected

1. In Muse, remove account connections you do not use.
2. Read the agent's stored memories and delete entries you did not create. NebuSec says memories could be altered.
3. If the agent browsed untrusted pages before 2026-11-20 with sensitive accounts connected, reconnect those accounts so new tokens are issued. No source asks for this step.

## Prevention

- Give a personal agent the fewest connected accounts the task needs. See [credential hygiene](../prevention/credential-hygiene.md).
- If you build an agent platform, keep credentials outside the VM the browser runs in. See [agent sandboxing](../prevention/agent-sandboxing.md).

## Sources

- [NebuSec: Hacking Muse: Stealing Private Chats Through Browser Use](https://nebusec.ai/research/meta-muse-credential-exposure/): 2026-11-20, read 2026-11-21. Findings, fix sentence.
- [NebuSec: Inside Meta Muse: Browser, Sentinel and the Shared-Kernel Boundary](https://nebusec.ai/research/inside-meta-muse/): 2026-11-20. Components, stated limits.
- [The Hacker News](https://thehackernews.com/2026/11/a-single-malicious-webpage-let.html): read 2026-11-21. Launch date, Meta's silence. Coverage of the same research, not a second finder.
- Single researcher: NebuSec. No Meta statement was found.
