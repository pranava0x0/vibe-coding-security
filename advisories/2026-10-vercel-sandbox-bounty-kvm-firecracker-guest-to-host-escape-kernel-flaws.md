---
id: 2026-10-vercel-sandbox-bounty-kvm-firecracker-guest-to-host-escape-kernel-flaws
title: "The microVM under the agent sandbox: Vercel's $1M Sandbox challenge (1,285 reports in two weeks) surfaced two Linux-kernel networking defects — one leaks host kernel memory, one crashes the host — with CVEs pending, and on 2026-10-06 researcher Paulos Yibelo said he has a full KVM guest-to-host-root escape found through the same program, which Vercel's CEO publicly confirmed for a $50,000 award; no CVE, no details, disclosure ongoing"
date_disclosed: 2026-10-06
last_updated: 2026-10-07
severity: high
status: unconfirmed
ecosystems: [firecracker, kvm, linux-kernel, vercel, ai-agents]
tools_affected: ["Vercel Sandbox", "Firecracker microVM-based agent sandboxes", "KVM hosts (per the researcher's claim)", "any product that runs untrusted agent-generated code in a microVM on a shared host"]
tags: [sandbox-escape, hypervisor, kvm, firecracker, linux-kernel, bug-bounty, zero-day, agent-sandboxing, unconfirmed, pending-cve]
---

## TL;DR
Vercel ran a two-week, $1M-pool bounty (2026-08-18 → 09-01) inviting HackerOne researchers and Trail of Bits to escape **Vercel Sandbox**, the Firecracker-microVM service it sells for running untrusted AI-agent code. Its 2026-09-15 results, as reported by SecurityWeek: **1,285 reports**, 1 Critical / 7 High / 15 Medium / 49 Low validated, ~$325k committed, **no report reached another customer's data** — and the headline finding was **two independent defects in the Linux kernel's networking stack**, not Vercel's code: one leaks memory from the host kernel, the other crashes the host deterministically; fixes under private review, **CVEs pending**. Then on 2026-10-06 The Register reported researcher **Paulos Yibelo** posting that he has a "full VM escape zeroday (guest>host root in industry standard hypervisors)" in **KVM**, and Vercel CEO Guillermo Rauch confirming "a KVM 0day through our Vercel Sandbox bounty program," paid at the $50,000 cap; no CVE, no mailing-list traffic, no technical detail. This file exists because Firecracker-on-KVM is the isolation layer under most "run the agent's code safely" products, not only Vercel's. **Status `unconfirmed`:** the escape rests on two X posts relayed by one outlet; the kernel bugs are vendor-confirmed but unidentified.

## What happened

**The program.** Vercel's 2026-08-18 post describes the target: Sandbox runs on bare-metal EC2, "each sandbox gets its own Firecracker microVM with a dedicated guest kernel," a Linux container inside runs the operator's code, and "the microVM, not the container, is the security boundary." In scope: escaping the microVM to the host or to another tenant's sandbox, and defeating the host-enforced network firewall; container-namespace escapes that stay inside the guest were explicitly out of scope ("namespaces are a developer-experience feature, not the security boundary"). Up to $50,000 per report, $1M pool, live proof-of-concept required.

**The results (2026-09-15, vendor analysis as reported).** 1,285 filings; 1 Critical, 7 High, 15 Medium, 49 Low, 19 Informative validated; about $325,000 committed. "None of the reports showed anyone being able to access a real customer's data." The most important filing "found two independent defects in the Linux kernel's networking stack (not Vercel's own code). One leaks memory from the host's kernel, while the other crashes the host, deterministically." Vercel says it learned of them two weeks before the kernel maintainers, the fixes are under private review, and CVEs are pending; it notes the same kernel layer isolates workloads at other large cloud providers. Vercel also used an AI agent built on its Eve framework to triage the volume. (SecurityWeek's article does not link Vercel's results post and this sweep did not locate it on vercel.com; the numbers above are SecurityWeek's reporting of it.)

**The KVM claim (2026-10-06).** The Register: Yibelo posted that he had a "Full VM escape zeroday (guest>host root in industry standard hypervisors)!" affecting KVM, the Linux kernel hypervisor Firecracker runs on; Rauch replied "We've confirmed a KVM 0day through our Vercel Sandbox bounty program." The Register could find "no chat on relevant mailing lists," infers responsible disclosure is under way, lists AWS (Firecracker's author), Google Cloud, Nutanix, HPE and Proxmox as KVM users who would care, and relays commentary that $50,000 is cheap for a hypervisor escape. **No CVE, no advisory, no proof, no affected kernel versions** — only the researcher's and the vendor's statements.

**How this relates to the "two kernel defects."** Unknown. A host-memory leak plus a deterministic host crash in the networking stack is not the same thing as "guest to host root," and the dates differ (results 09-15; the escape confirmation 10-06). This advisory does not merge them; a future sweep should, once a CVE or a writeup names what the $50k paid for.

**Why it is here.** Every coding agent that "runs the code in a sandbox" — Vercel Sandbox, E2B-style services, Cursor's and Claude's cloud agents, self-hosted Firecracker setups — depends on exactly this boundary, and this repo already carries three advisories where the boundary inside the VM failed ([Claude Cowork VM escape](2026-07-claude-cowork-sandbox-escape.md), [OpenClaw Claw Chain](2026-05-openclaw-claw-chain.md), [Meta Muse](2026-09-meta-muse-macos-dictation-endpoint-agent-token-hijack.md)). A hypervisor bug is the one layer below those that no product can patch on its own.

## Am I affected?

You cannot test for an undisclosed bug, and this project does not probe hosts. What you can know:

- **Do you run untrusted agent output on a shared KVM/Firecracker host you operate?** (Self-hosted Firecracker, `firecracker-containerd`, Kata on KVM, Proxmox VMs for agents.) Then you are in the population the researcher describes, pending details. Keep the host kernel on the distribution's security channel and subscribe to the `linux-distros`/oss-security announcements for the pending CVEs.
- **Do you buy sandboxing as a service?** The vendor patches the host; your exposure is co-tenancy. Vercel's own statement is that no bounty report reached customer data.
- **Does your agent product's sandbox *claim* VM isolation but run a container?** Vercel's post is unusually clear that the container is not the boundary; check whether your vendor says the same.

## If you are affected
- [if-your-local-ai-agent-was-exploited](../playbooks/if-your-local-ai-agent-was-exploited.md) for the inside-the-VM triage; for a suspected host compromise on infrastructure you operate, [rotating-cloud-credentials](../playbooks/rotating-cloud-credentials.md) — an escaped guest has the host's instance credentials.

## Prevention
- [agent-sandboxing](../prevention/agent-sandboxing.md) — defence in depth below the microVM: minimal guest kernel, no unnecessary virtio devices, egress control at the host, and assume the hypervisor will have a bad month.

## Sources
- [The Register — Security researcher claims they found KVM guest-host escape flaw](https://www.theregister.com/offbeat/2026/10/06/security-researcher-claims-they-found-kvm-guest-host-escape-flaw/5301267) — 2026-10-06; Yibelo's and Rauch's quoted posts, the $50,000 award, "no chat on relevant mailing lists," the list of KVM-dependent vendors. The X posts themselves were not opened by this sweep (search snippets only).
- [SecurityWeek — $1 Million Sandbox Challenge Uncovers Linux Kernel Flaws](https://www.securityweek.com/1-million-sandbox-challenge-uncovers-linux-kernel-flaws/) — 2026-09-15; the 1,285 / 1-7-15-49-19 / ~$325k figures, "two independent defects in the Linux kernel's networking stack," memory leak and deterministic crash, CVEs pending, the no-customer-data statement, the Eve triage agent.
- [Vercel — $1 million hacker challenge for Vercel Sandbox](https://vercel.com/blog/one-million-dollar-hacker-challenge-for-vercel-sandbox) — 2026-08-18 (Andy Riancho): program dates, the architecture and scope statements quoted above, the "microVM, not the container" boundary, the $50,000 / $1M terms.
