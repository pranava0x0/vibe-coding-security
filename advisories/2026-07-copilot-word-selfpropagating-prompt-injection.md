---
id: 2026-07-copilot-word-selfpropagating-prompt-injection
title: "Microsoft Copilot for Word: self-propagating 'AI worm' via document-borne prompt injection (no CVE, unresolved as of disclosure)"
date_disclosed: 2026-07-28
last_updated: 2026-07-29
severity: high
status: active
ecosystems: [microsoft-copilot, ai-vendor-infrastructure]
tools_affected: ["Microsoft Copilot for Word", "Microsoft 365 Copilot"]
tags: [prompt-injection, self-propagating, xpia, document-borne, unresolved, ai-worm]
---

## TL;DR

Researcher Håkon Måløy disclosed a **cross-domain prompt-injection attack against Microsoft Copilot for Word** that behaves like a self-replicating worm: hidden white-text instructions in a Word document get executed by Copilot, silently tamper with content, and get copied into every new document Copilot subsequently generates from that content — turning each output into a fresh carrier. After **144 days of coordinated disclosure** and two Microsoft mitigation attempts (including a model upgrade to GPT-5.6), the researcher could still reproduce the full worm chain as of the public disclosure on **2026-07-28**. No CVE has been assigned, and Microsoft has not stated the underlying vulnerability class is fixed.

## What happened

This is the third installment ("Context Collapse, Part 3") in Måløy's research into cross-domain prompt injection (XPIA — cross-prompt injection attack) against Microsoft's Copilot products. The technique:

1. **Stage 1 — planting:** An attacker embeds a JSON-formatted malicious instruction as **white text on a white background** (invisible on screen, present in the document's text layer) inside an otherwise-normal Word document.
2. **Stage 2 — execution:** A victim asks Copilot for Word to draft or edit content using that document as a source. Copilot strips formatting when it reads the document, exposing the hidden instruction as plain text, and treats it as part of the user's own request — for example, silently halving financial figures in a generated report.
3. **Stage 3 — propagation:** The same hidden instruction directs Copilot to **copy the payload into the newly generated document**. That new, clean-looking file is now itself an infected carrier: anyone who later uses it as source material for another Copilot session triggers the same chain, with no further attacker involvement.

**Disclosure timeline** (per the researcher's own writeup and The Register's reporting): initial MSRC report **2026-03-06**; Microsoft confirmed the reported behavior **2026-03-31**; a first mitigation shipped **2026-04-03**, but the researcher reproduced a new variant by **2026-04-09**; Microsoft deployed a model upgrade (to GPT-5.5, then GPT-5.6) as a second mitigation attempt around **2026-07-14/15**, and the researcher reproduced the full worm chain again days later; public disclosure followed on **2026-07-28/29** after 144 days of coordination. Måløy states plainly that "no robust mitigation for the broader vulnerability class is currently available" and deliberately withheld exact payload details given the absence of a real fix. Microsoft's public response points to a "defense-in-depth" posture of layered safeguards rather than claiming the class is closed, and recommends users apply updates, layer additional controls, treat documents from unknown sources cautiously, and review AI-generated output before sharing or forwarding it.

No CVE or GHSA identifier has been assigned to this issue as of this sweep.

## Am I affected?

Any organization or individual using Microsoft Copilot for Word (or, by the same architectural pattern, other Microsoft 365 Copilot surfaces that ingest documents as context) is potentially exposed. There is no local package/version check — this is a hosted-service behavior, not client software you patch yourself. Practical exposure signals:

- You regularly ask Copilot to summarize, draft from, or edit content sourced from documents you didn't author yourself (attachments, shared drives, OneDrive auto-discovery).
- Your organization shares Word documents across teams or with external parties and then reuses those documents as Copilot source material.
- You have no process for visually inspecting documents for hidden/invisible text (white-on-white, near-zero font size) before treating them as trusted Copilot input.

## If you are affected

There is no patch to apply. Mitigation is procedural, not technical, until Microsoft closes the underlying class:

- Treat any document from an untrusted or unverified source as untrusted **Copilot input**, not just untrusted content to read manually — the same discipline this repo already recommends for MCP tool output and fetched web pages.
- Review AI-generated document output (especially altered figures, numbers, or instructions) before forwarding or acting on it, particularly for documents that passed through multiple rounds of AI-assisted editing.
- See [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) for general incident-response steps if you suspect a document-borne injection already altered your organization's content.

## Prevention

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — trust-boundary discipline for any AI tool that treats external content as executable instruction
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Why this matters for vibe coders

This repo mostly tracks prompt injection reaching agents through code, MCP tool output, and repository files (`README.md`, `.cursorrules`, `CLAUDE.md`). This incident shows the identical trust-boundary failure — content an AI tool reads is implicitly treated as instruction — generalizes to **office documents as a self-propagating carrier**, with no code or install step involved at all. Many vibe-coding teams use Copilot alongside their coding tools for specs, requirements docs, and reports; a document that silently tampers with numbers and re-infects every document generated from it is a business-logic integrity risk, not just a data-exfiltration one. It is also a useful data point on vendor response times: 144 days and two mitigation attempts (including a full model upgrade) were not enough to close a document-borne prompt-injection class — a caution against assuming any single AI vendor's guardrails are a complete defense.

## Sources

- [enklypesalt.com — Context Collapse, Part 3: AI Worming through Word](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/) — primary researcher disclosure: full timeline, technique, exploitability caveats, and explicit statement that no robust mitigation exists.
- [The Register — Word worm crawls into Copilot, spreads chaos](https://www.theregister.com/security/2026/07/29/word_worm_crawls_into_copilot_spreads_chaos/5280588) — independent reporting confirming researcher identity, timeline, and Microsoft's official response.
- [Malwarebytes — Hidden prompt turns Microsoft Copilot into an AI worm](https://www.malwarebytes.com/blog/ai/2026/07/hidden-microsoft-copilot-ai-worm) — independent corroboration of the technical mechanism and reproduction after Microsoft's mitigations.
