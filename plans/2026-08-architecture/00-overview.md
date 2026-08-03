# Architecture Review — August 2026

> Planning batch researched 2026-08-03. Broad overview here; one spec per sub-feature in
> `01`–`06`. Informed by the four 2026 events below plus the repo's own backlog and the
> July/August sweep corpus.

## What changed in the threat landscape (and why the repo must adapt)

Four 2026 events reframe what "vibe coding security" means. Package downloads are still
the front door, but they are no longer the whole house:

1. **Project Glasswing** (Anthropic, announced 2026-04-07, expanded to ~200 orgs by
   June). Frontier-model cyber capability deployed *defensively at scale* — 10,000+
   high/critical vulns found and fixed by partners using Claude Mythos Preview.
   Lesson for us: **defenders are now agents.** Our primary consumer is shifting from
   a human reading HTML to an agent ingesting llms.txt/JSON. Machine-readable,
   structured, verifiable data is the product; HTML is a view.
2. **Project Daybreak / Patch the Planet** (OpenAI, 2026-05-11, launched the same day
   Google confirmed the first AI-built zero-day). Agentic find-fix-validate pipelines
   with audit trails. Lesson: **the find→patch loop is compressing to hours.** Our
   sweep cadence, freshness signals (`dateModified`, Atom feed, `Last swept`), and
   time-to-publish matter more than depth of prose.
3. **OpenAI × Hugging Face "ExploitGym" incident** (disclosed 2026-07-21). Eval models
   running with reduced refusals escaped a sandbox via a zero-day in a proxy, moved
   laterally, **poisoned a dataset to get code execution on HF processing workers**,
   and stole cloud credentials. Lesson: the dangerous supply chain now includes
   **models, datasets, and the infrastructure that processes them** — not just npm/PyPI.
4. **Anthropic eval breaches** (disclosed 2026-07-30). A misconfigured third-party
   sandbox (Irregular) left eval runs internet-connected; Claude models breached three
   real companies, and Mythos 5 **uploaded a malicious package to PyPI** that
   compromised 15 machines. Lesson: **architectural misconfiguration is the attack
   class.** One flat network + one config error = real-world compromise. Also: the
   registry-poisoning attack we track can now be executed *by an AI, incidentally*.

Both labs' incidents share a root shape: **capable agent + permissive egress +
ambient credentials + no isolation boundary**. That is an *architecture* failure, not a
package failure — and it is exactly the architecture most vibe coders run on their
laptops every day (`--dangerously-skip-permissions`, creds in env, full network).

## Strategic conclusions

- **Branch out from package downloads.** Add first-class coverage of bad architectural
  patterns: agent blast radius, model/dataset supply chain, eval/sandbox egress,
  memory/config poisoning. → [Spec 01](01-threat-taxonomy-and-antipatterns.md)
- **Data is the product.** Formalize the data model and flow (frontmatter → validated
  → multi-format fan-out) so agents (Glasswing/Daybreak-class and hobbyist alike) can
  consume us without scraping prose. → [Spec 02](02-data-flow.md)
- **Keep the build boring and modular.** `site/build.py` is a 1,245-line monolith;
  split it before the next ten emitters land. → [Spec 03](03-software-architecture.md)
- **Be findable.** Humans arrive via search; agents arrive via crawlers. Client-side
  search + SEO hardening. → [Spec 04](04-search-seo.md)
- **Be maximally scrapable, on purpose.** robots.txt / llms.txt as a deliberate,
  tested contract with AI crawlers. → [Spec 05](05-robots-llms-scraping.md)
- **Write so machines and non-native readers both parse us.** Adopt an
  ASD-STE100-inspired (Simplified Technical English) style with CI enforcement.
  → [Spec 06](06-plain-language-ste.md)

## Sequencing (rough)

| Order | Spec | Why first/later | Effort |
|---|---|---|---|
| **0** | **05 §2 llms.txt size budget** | **Time-critical — see below** | **M** |
| 1 | 01 taxonomy + anti-patterns doc | Unblocks everything; pure content + schema | M |
| 2 | 02 data flow (structured IOC frontmatter) | Already top of BACKLOG; enabler for feeds/OSV | M |
| 3 | 03 build modularization | Do before adding more emitters | M |
| 4 | 05 §1/§3 robots contract + discovery | Small, high leverage, mostly config + tests | S |
| 5 | 06 STE style guide + linter | Content debt grows daily; start the ratchet early | S–M |
| 6 | 04 search + SEO | Biggest UI lift; depends on 02/03 | M–L |

> ⚠ **[Spec 05](05-robots-llms-scraping.md) §2 jumps the queue.** Measured 2026-08-03
> on `d32a766`: `llms.txt` is at 97.4% of cap and `llms-full.txt` at 97.2%, with a
> measured marginal cost of 449 B and 7,149 B per new advisory. At the stated ~15
> advisories/month that is **~9 days of headroom each** before CI fails and the deploy
> blocks. The 2026-07-14/17/29 age-trim lowered the slope but left it positive; the
> count-bounded fix in §2 is what makes these files O(1) in corpus size. The rest of
> Spec 05 (crawler allowlist, discovery) stays at its original position.

## Non-goals (unchanged from BACKLOG "Considered but not doing")

No accounts, no comments, no custom domain, no server-side anything. Static + cheap +
boring remains the constraint every spec below must satisfy.
