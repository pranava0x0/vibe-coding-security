---
id: 2026-09-cloudflare-containers-sandboxes-cross-tenant-residual-storage
title: "Cloudflare Containers and Sandboxes: a customer could read other customers' residual disk blocks — directory trees, database pages and 'structurally complete SQLite databases' from previous tenants on the same host — through thin-provisioned storage with block zeroing disabled; reported by Accomplish on 2026-09-04, fixed 09-07, disclosed 09-24, no evidence of other exploitation"
date_disclosed: 2026-09-24
last_updated: 2026-09-24
severity: high
status: patched
ecosystems: [cloudflare, containers, serverless, ai-agents, sandboxes]
tools_affected: ["Cloudflare Containers (all customers with a Workers Paid plan could run the attack; any Container on a shared host could be the victim)", "Cloudflare Sandboxes (built on Containers; the agent-code-execution product)"]
tags: [cloud-platform, cross-tenant, data-exposure, storage, thin-provisioning, sandbox, agent-sandbox, vendor-disclosure, cloudflare]
---

## TL;DR
On **2026-09-24** Cloudflare disclosed a **cross-tenant data-exposure bug in Cloudflare Containers** — and therefore in **Cloudflare Sandboxes**, the product built on Containers for running AI-agent code. Container disks were carved from Linux device-mapper **thin-provisioned** pools with `skip_block_zeroing` enabled; when a storage block was freed by one container and reassigned to another, "a smaller write changed only the written portion. The remainder could retain data from the block's previous owner." A customer with a Workers Paid account could "write aligned blocks to trigger reallocation and then read unwritten portions containing residual information" — and what came back included "directory structures, database pages, and structurally complete SQLite databases" belonging to other customers' Containers on the same host. The attack "could not target a particular victim" and "depended on Cloudflare's workload placement," but it needed nothing beyond a paid account. Reported by **Oren Yomtov (Accomplish)** on 2026-09-04 at 15:26 UTC; fix deployed **2026-09-07 06:13 UTC**; cleanup of existing pools completed 2026-09-19; "no evidence that this specific attack vector was exploited by anyone else." No customer action is required. Single-source (Cloudflare's own post-mortem) — the researcher has not yet published.

## What happened

**The mechanism.** Cloudflare gives each Container a block device from a thin pool (`dm-thin`). Thin pools hand out blocks lazily and, by default, zero a block before a new volume first uses it; Cloudflare had that zeroing turned off (`skip_block_zeroing`) for performance. A block freed by container A and reallocated to container B is then presented to B as-is: if B writes only part of the block, the rest still contains A's bytes, and B can read them. Cloudflare's post-mortem describes the attacker's loop as writing aligned blocks to force reallocation, then reading the unwritten remainder. Because placement is Cloudflare's decision, the attacker gets whichever tenants happened to precede them on the host — no targeting, but also no way for a victim to opt out.

**What could be recovered.** Cloudflare's own characterisation: "residual data from storage blocks previously used by other customers' Containers on the same underlying host," including directory structures, database pages and structurally complete SQLite databases. For a Sandboxes customer that means whatever an agent wrote to its working disk — cloned repositories, `.env` files it was handed, the SQLite state file of whatever tool it ran — could survive the container's teardown and be read by the next tenant.

**Timeline (Cloudflare's).** 2026-09-04 15:26 UTC report received → 2026-09-07 06:13 UTC fix deployed (block zeroing on, and re-provisioning of pools) → 2026-09-19 15:03 UTC cleanup complete → 2026-09-24 disclosure. Cloudflare says it saw no evidence of exploitation by anyone other than the reporter and that no customer-side configuration change is needed.

**Why it matters for vibe coders.** Cloudflare Sandboxes is one of the "put the agent in a sandbox" products this corpus points people at; Containers is where a growing share of Workers-based apps keep their non-serverless pieces. A cross-tenant residual-storage bug turns the sandbox's disk into a shared surface in exactly the direction [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) warns about — the sandbox protected the host from the agent, but not one agent's data from another tenant. The pattern is not new (it is the classic "dirty blocks from the previous VM" cloud bug), but the tenant population is: agent sandboxes are provisioned and torn down per task, by the thousand, each one briefly holding a fresh set of secrets. And the fix was entirely on the platform side: version-pinning, dependency scanning and your own code review could not have found or prevented it — this is the platform's shared-responsibility half, which is why the corpus tracks vendor post-mortems as incidents. Same reporter as the [Docker Sandboxes](2026-09-docker-sandboxes-virtiofs-symlink-host-escape.md), [Codex](2026-09-codex-heapjack-overpatch-sandbox-escapes.md) and [Claude Cowork](2026-07-sharedroot-claude-cowork-macos-vm-escape.md) escapes; the same shape as Cloudflare's own Workers cross-tenant findings in August.

## Am I affected?

- **Potentially exposed if:** you ran Cloudflare Containers or Sandboxes workloads **before 2026-09-07** that wrote sensitive material to the container's disk (repository checkouts, credentials passed in as files, local databases). There is no per-customer indicator; exposure depends on host co-location and the attacker's timing, and Cloudflare reports no evidence of exploitation beyond the researcher.
- **Not affected:** workloads created after the 09-07 fix; Workers without Containers; data that never touched the container filesystem.

```bash
# Inventory what your Containers / Sandboxes workloads wrote to disk. Wrangler config names the container images;
# the question is what the running code persisted.
grep -rn "containers\|sandbox" wrangler.toml wrangler.json* 2>/dev/null
# Secrets handed to a sandbox as files (as opposed to env vars read at runtime) are the higher-risk class
grep -rnE "writeFile.*(\.env|credentials|token|\.pem)" --include=*.ts --include=*.js . | grep -v node_modules
```

## If you are affected

1. No platform action is needed; Cloudflare has fixed and cleaned up.
2. If a pre-09-07 Container or Sandbox held long-lived credentials on disk (a cloned repo with committed secrets, a service-account file, an API key written to a config), treat that as a low-probability exposure and rotate per → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md). The probability is low — untargeted, placement-dependent, no evidence of exploitation — but rotation is cheap.
3. → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) applies to a sandboxed agent's environment as much as a local one: inventory what the agent could read.

## Prevention

- **Give a sandboxed agent short-lived, scoped credentials, not files.** A residual-disk bug leaks what is written; an OIDC-minted token that expired an hour later is worthless to whoever reads the block. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- **The sandbox vendor is in your threat model.** Docker Sandboxes (virtiofs symlink escape), Codex (Heapjack/Overpatch), Claude Cowork (SharedRoot) and now Cloudflare Containers have all had an isolation failure in 2026; keep the sandbox layer *plus* a credential and egress policy that assumes the isolation fails. [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- **Read the platform's post-mortems, not only its CVE feed.** This bug has no CVE and no advisory-database entry; the disclosure is a blog post. Cloudflare's, AWS's and Google's incident posts are a source class of their own.

## Sources
- [Cloudflare — How Cloudflare addressed a cross-tenant data exposure vulnerability in Containers](https://blog.cloudflare.com/containers-cross-tenant-vulnerability/) — vendor post-mortem, 2026-09-24: the `skip_block_zeroing` thin-provisioning mechanism, the aligned-write/read attack description, "directory structures, database pages, and structurally complete SQLite databases," Workers Paid as the prerequisite, the placement dependency, the 09-04 / 09-07 / 09-19 timestamps, the reporter (Oren Yomtov, Accomplish), no evidence of other exploitation, no customer action. Fetched 2026-09-24.
- Single-source note: as of 2026-09-24 the only account is Cloudflare's own; Accomplish's blog carries no post on it yet and no outlet had covered it. The Hacker News (news.ycombinator.com) item for the post existed the same day. Status is `patched` on the vendor's statement that the fix and cleanup are complete.
- Related in this corpus: [Docker Sandboxes virtiofs symlink host escape](2026-09-docker-sandboxes-virtiofs-symlink-host-escape.md), [Codex Heapjack/Overpatch](2026-09-codex-heapjack-overpatch-sandbox-escapes.md), [SharedRoot (Claude Cowork)](2026-07-sharedroot-claude-cowork-macos-vm-escape.md).
