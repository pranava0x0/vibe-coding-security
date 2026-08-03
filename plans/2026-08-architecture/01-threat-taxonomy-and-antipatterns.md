# Spec 01 — Threat taxonomy expansion + architectural anti-patterns catalog

**Goal.** Branch coverage out from "bad package downloads" to the full 2026 attack
surface, and give the site a controlled taxonomy so every advisory is classifiable and
filterable.

**Motivated by.** ExploitGym (dataset poisoning → code exec on processing workers) and
the Anthropic/Irregular breaches (sandbox egress misconfig; AI-published malicious PyPI
package) are architecture-class incidents. The corpus already contains agent-runtime
advisories (MemGhost memory poisoning, Kiro MCP config self-rewrite, SharedRoot VM
escape, Rogue Agent shared-execution) but nothing groups or explains them as a class.

## 1. Controlled `attack_class` frontmatter field

Add an optional (then required-for-new) enum field to advisory frontmatter and
`advisory-schema.json`:

- `package-supply-chain` — npm/PyPI/crate compromise, typosquat, slopsquat
- `model-supply-chain` — malicious/cloned model repos, poisoned weights, loader.py droppers
- `dataset-poisoning` — data that executes or that steers agents (ExploitGym class)
- `agent-runtime` — memory poisoning, config self-rewrite, tool poisoning, MCP abuse
- `prompt-injection` — content-borne instruction attacks
- `sandbox-escape` — eval/VM/container isolation failures (SharedRoot, ExploitGym)
- `credential-theft` — infostealers, token exfil
- `platform-vuln` — CVEs in AI tools/frameworks (Langflow, n8n, Next.js class)
- `ai-discovered` — cross-cutting flag: the vuln/exploit was found or built by an AI

Rules: one primary class per advisory; optional `attack_classes_secondary` list.
Back-fill is mechanical (~1h with an agent pass over ~100 advisories); schema stays
`additionalProperties: true` so old files don't break mid-migration. `validate.py`
warns on missing class; after back-fill, tests enforce it on new files.

## 2. New prevention doc: `prevention/agent-blast-radius.md` (the anti-patterns catalog)

The flagship "branch out" deliverable. An anti-patterns catalog in the style of the
existing attack-surface map. Each anti-pattern: name, why it's dangerous, real incident
that proves it, and the cheapest fix. Initial list:

1. **Flat-network agent** — agent has unrestricted egress. (Irregular misconfig; fix:
   deny-by-default egress allowlist, document per-tool.)
2. **Ambient credentials** — long-lived cloud/registry creds in env vars the agent
   inherits. (ExploitGym credential theft; Nx s1ngularity. Fix: short-lived tokens,
   OIDC, keychain-backed helpers.)
3. **Shared execution surface** — eval/CI/data-processing workers that both touch
   untrusted content and hold secrets. (HF processing workers; Rogue Agent Dialogflow.
   Fix: split "parses untrusted stuff" from "holds creds" into separate runtimes.)
4. **Writable agent config** — agent can rewrite its own instruction/config files
   (`CLAUDE.md`, `.cursorrules`, MCP config). (Kiro self-rewrite, MemGhost. Fix:
   read-only mounts / diff-on-change.)
5. **Publish rights from a dev box** — the machine an agent codes on can also publish
   to npm/PyPI. (Mythos 5's PyPI upload shows an agent will do this *incidentally*.
   Fix: publish only from CI with 2FA-gated staged publishing.)
6. **Trusting model/dataset artifacts more than packages** — `loader.py` /
   `trust_remote_code=True` / pickled weights. (Open-OSS/privacy-filter clone. Fix:
   safetensors only, `trust_remote_code=False`, treat HF repos as unreviewed code.)
7. **The lethal trifecta as an architecture smell** — private data + untrusted content
   + egress in one context. Cross-link the planned
   `prevention/prompt-injection-defense.md` (BACKLOG high-priority item; still write it).

## 3. New prevention doc: `prevention/model-dataset-supply-chain.md`

npm-hardening's sibling for the HF ecosystem: verifying model provenance
(`gh attestation verify`, HF commit signatures), model-card-clone red flags, dataset
provenance and hash pinning, scanner coverage and limits (e.g. picklescan bypasses),
and a "60-second model vetting checklist" mirroring the package one.

## 4. Site surfacing

- Filter chips (Spec 04) get `attack_class` as a facet.
- `advisories/README.md` index gains a by-class section.
- ALERTS.md entries get a class tag chip.

## Acceptance criteria

- Schema + validator + tests updated; all new advisories carry `attack_class`.
- Both prevention docs published, cross-linked from attack-surface map and README.
- Back-fill PR lands within one week of schema change (avoid a long half-migrated state).

**Effort.** Medium. Schema ½ day; docs 1 day; back-fill 1 agent pass + review.
