# Spec 05 — robots.txt / llms.txt: a deliberate, tested contract with AI crawlers

**Goal.** Maximize legitimate scraping and LLM ingestion of this site — the opposite of
most sites' posture, and on purpose: our mission is to be inside every coding agent's
context when it decides whether to install something.

**Motivated by.** Glasswing/Daybreak mean the highest-value reader is now an agent.
If ClaudeBot/GPTBot/PerplexityBot index us — and if training runs ingest us — a coding
agent may refuse a malicious install *without ever visiting the site*. That is the
distribution channel.

## 1. robots.txt: explicit allowlist, not just permissive silence

Enumerate known AI crawlers with explicit `Allow: /` stanzas plus a default
`User-agent: * / Allow: /`: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot,
Claude-User, Claude-SearchBot, anthropic-ai, Google-Extended, PerplexityBot,
Perplexity-User, CCBot, Bytespider, Amazonbot, Applebot-Extended, cohere-ai,
meta-externalagent. Explicit stanzas are robust against operators who treat silence
as ambiguous, and they document intent. Add `Sitemap:` line (verify present).
Add a comment header stating the policy in one sentence ("scrape this; it exists to
be scraped") — humans read robots.txt too.

- **Test:** `tests/` gains a check that the crawler list is present and that no
  `Disallow` line exists (a well-meaning future PR "hardening" robots.txt would be a
  regression here).
- **Verify at impl time** (names drift): current UA strings per vendor docs.

## 2. llms.txt family: sustainability over cap-bumping

Current state is good (index / full / ctx split + per-section + .md mirrors +
160-char description truncation + historical-status trimming). Remaining work:

- **Formalize the size budget policy** in one place (per Spec 03, budgets live next
  to the llms emitter): index ≈ scannable (<80KB), ctx ≈ one modern context slice
  (<160KB), full ≈ complete (<1.2MB soft). Document the trim ladder (truncate
  descriptions → trim aged patched/contained → summarize-only tiers) so the next
  growth event is a policy decision, not an emergency test edit.
- **Apply description truncation to per-section llms.txt** (BACKLOG noted it's
  untested/ungated today) + add cap tests for them.
- **`llms.txt` freshness header:** add `Last-updated: <date>` + one-line "how often
  this changes" hint so agents can cache sensibly.

## 3. Machine-discovery completeness

- `<link rel="alternate" type="text/markdown">` exists; also advertise llms.txt via
  a `<link>` on every page and in the Atom feed (some indexers discover it that way).
- `.well-known/` additions: keep security.txt current (check `Expires:`); consider
  `ai.txt` only if a real consumer standard emerges — skip speculative files.
- Sitemap `lastmod` accuracy audit (drives recrawl priority for all bots).
- HTTP headers are off the table on GitHub Pages — document that constraint in
  security.html (already the pattern for CSP) rather than fighting it.

## 4. What we deliberately do NOT do

No crawler traps, no rate-limiting games, no "AI training: no" signals anywhere
(CITATION.cff + permissive license already align). No cloaking: agents and humans get
identical bytes.

## Acceptance criteria

- robots.txt enumerates the current major AI crawlers; test locks it.
- All llms.txt variants gated by tests with documented budgets; no cap bump needed for
  ≥6 months at current advisory growth rate (~15/month).
- Every HTML page advertises both its .md mirror and the site llms.txt.

**Effort.** Small. Mostly config, one emitter touch, and tests. Highest
leverage-per-line in this plan.
