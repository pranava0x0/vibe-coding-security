---
id: 2026-07-claude-cowork-sandbox-escape
title: "Claude Cowork for Windows — chained flaws reach root inside the Hyper-V sandbox; Anthropic disputes it's a vulnerability"
date_disclosed: 2026-07-01
last_updated: 2026-07-01
severity: high
status: active
ecosystems: [claude-cowork, anthropic]
tools_affected: ["Claude Cowork for Windows (Claude Desktop 1.9255.2.0 and related builds)"]
tags: [sandbox-escape, privilege-escalation, dll-sideloading, windows, hyper-v, wont-fix, claude-desktop]
---

## TL;DR

Armadin Inc. disclosed a chained sandbox-escape in **Claude Cowork for Windows** — Anthropic's Hyper-V-isolated Ubuntu VM environment for letting Claude execute code "safely." Reported to Anthropic on **2026-03-20**; Anthropic responded four days later disputing it as a security issue on the grounds that it requires an attacker to already have local code execution on the host. Armadin published full technical details on **2026-07-01/02**. The chain reaches **root inside the VM** and strips the domain-allowlisted network egress filter, and Anthropic has **not shipped a fix** as of this writing.

## What happened

Claude Cowork for Windows runs agent-executed code inside a Hyper-V-isolated Ubuntu virtual machine, mediated by a Windows service (**CoworkVMService**) that communicates over an Authenticode-gated named-pipe RPC interface. Inside the VM, the design relies on a stack of isolation primitives — bubblewrap namespaces, seccomp filters, and a per-session unprivileged user created fresh for each command — plus a domain-restricted egress proxy that's supposed to limit what the sandboxed code can reach on the network.

Armadin's research (credited to the firm, tested against **Claude Desktop for Windows 1.9255.2.0**) chains two design weaknesses:

1. **DLL sideloading into a signed binary.** `Claude.exe` resolves `USERENV.dll` from its own application directory before falling back to the system copy. An attacker with local code execution can drop a malicious `USERENV.dll` alongside the executable, achieving code execution inside a legitimately Authenticode-signed Anthropic process — which matters because the RPC interface to `CoworkVMService` is gated on the caller having a valid Anthropic signature.
2. **RPC parameter abuse.** Once able to speak to `CoworkVMService` as a "trusted" signed caller, two parameters in the process-spawn RPC call can be manipulated: a **resume flag** that, when set, bypasses the creation of a fresh unprivileged user for the command — yielding command execution **as root** inside the VM — and a **domain-allowlist override** that accepts a wildcard, disabling the egress proxy's network restrictions entirely.
3. **Escape from VM to host visibility.** With root inside the VM, the researchers used `nsenter` against the first (already-root) process to step outside the sandboxed namespace into the wider virtual machine, and from there exfiltrate data over the now-unrestricted network path.

### Vendor response

Armadin reported the finding to Anthropic on **2026-03-20**; Anthropic responded on **2026-03-24** disputing that it qualifies as a security vulnerability, on the basis that exploitation requires the attacker to already have local code execution on the host machine. Two independently fetched outlets (SiliconANGLE, SC Media) confirm this characterization in Anthropic's own words: the escape "requires an attacker to already have local code execution on the host," and Anthropic "does not consider this a security issue warranting a patch." A third source (Threat-Modeling.com) states a patch was released hardening namespace boundaries and seccomp profiles — this is a **reporting discrepancy** we have not independently resolved; two of three sources agree Anthropic declined to treat it as fixable, so we're recording this as `active`, not `patched`, pending clearer vendor confirmation. No CVE has been assigned as of this writing.

### Why "requires local code execution" undersells the risk

This is the same reasoning pattern flagged in this repo's [localhost-is-not-a-security-boundary](../ALERTS.md) class of findings and in prior "won't-fix" vendor responses (cf. [Claude Desktop's connector-chaining lethal trifecta](2026-07-claude-desktop-personalization-sync-rce.md)): a sandbox's entire value proposition is containing code that's already running with *some* level of access — a browser exploit, a malicious dependency, a supply-chain-planted script, or a prompt-injected agent action can all deliver "local code execution" without a human ever knowingly running untrusted code. Dismissing a full sandbox-to-root escape because it "requires prior code execution" is dismissing the sandbox's actual threat model.

## Am I affected?

If you use **Claude Cowork for Windows**, any process capable of writing a file into Claude's application directory (a malicious installer, a compromised update mechanism, or another already-running piece of malware) can plant the sideloaded DLL and pivot into root access inside the sandbox VM, then exfiltrate data past what should be a domain-restricted network boundary. There is currently no version-based fix to check for.

## If you are affected

1. Until Anthropic ships a structural fix, do not treat Claude Cowork's Hyper-V sandbox as a hard security boundary against a host that has *any* other foothold — treat it as defense-in-depth alongside standard host hardening (application allowlisting, restricting write access to Claude's install directory, host-based EDR).
2. Monitor for unexpected `USERENV.dll` files appearing in the Claude Desktop application directory.
3. If you operate Claude Cowork in an environment where sandboxed code processes untrusted input (fetched web content, third-party repos, MCP tool output), assume the sandbox's network egress restrictions can be bypassed by a sufficiently capable attacker and apply network-level controls (firewall/proxy) independent of Claude Cowork's own allowlist.

## Prevention

- See [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) for general guidance on not treating vendor-provided AI-agent sandboxes as a sole security boundary.
- Restrict write access to AI-tool installation directories via host-level permissions where your OS/EDR tooling supports it, to reduce DLL-sideloading opportunities.

## Sources

- [SiliconANGLE — Armadin details full sandbox escape in Claude Cowork but Anthropic disputes risk](https://siliconangle.com/2026/07/01/armadin-details-full-sandbox-escape-claude-cowork-anthropic-disputes-risk/) — primary technical writeup, disclosure timeline, Anthropic's dispute in its own words.
- [SC Media — Researchers detail attack chain escaping Anthropic's Claude Cowork sandbox](https://www.scworld.com/brief/researchers-detail-attack-chain-escaping-anthropics-claude-cowork-sandbox) — independent corroboration of the technical chain and Anthropic's response.
- [gbhackers — Claude Cowork Sandbox Flaw Lets Attackers Execute Commands as Root in Hyper-V VM](https://gbhackers.com/claude-cowork-sandbox-flaw/) — further corroboration of scope and impact.
