# Model fallback log

One row per event that changed which model was running, stopped a response, or blocked a tool call. Newest row last. Append a row during the run, the moment the transcript shows the notice; do not wait for Step 5.

Event values: `safeguard-stop` (Fable refused its own response), `model-switch` (session re-run on another model after a flag), `overload-fallback` (fallbackModel chain used), `permission-block` (auto mode refused a tool call), `rate-limit` (run refused or ended by a usage limit).

| Date | Run | Event | From → to | Doing | Cause | Resolution |
|---|---|---|---|---|---|---|
| 2026-09-23 | session_01RntooQWjn8TtUQkdTYf2To | safeguard-stop, model-switch | fable-5-1 → opus-4-8 | Bash heredoc writing the MemTensor sckit worm advisory | payload mechanics in the advisory text | rewritten remediation-first; rest of run on Opus 4.8 |
| 2026-09-25 | session_01WJrYUiPZv7jZbrvg7aA6Bi | safeguard-stop, model-switch | fable-5-1 → opus-4-8 | writing the Gambit retail-skimmer campaign advisory | operational tradecraft in the advisory text | rewritten defender-first; rest of run on Opus 4.8 |
| 2026-09-28 | session_01PvfvAE6viggB9aohySAiCd | rate-limit | fable-5-1 | run start | weekly usage limit reached | run did not start |
| 2026-09-29 | session_01GU35AFvJ1o9RJdx1gbKYmb | safeguard-stop, permission-block | fable-5-1 | Bash heredoc writing the DirtyBlanket worm advisory, re-sent | worm propagation narrated; retry flagged again | auto mode blocked every write; nothing committed |
| 2026-09-30 | session_0132j2kRHcRKuZsua2RiZobD | permission-block | fable-5-1 | WebFetch of a malware write-up | page carried live loader and onion URLs | writes blocked until context compaction; run finished |
| 2026-10-01 | session_01GYMHbfo4qL4eHkVybsCgcb | safeguard-stop | subagent only | fetch subagent returning its report | exploitation steps in the report | subagent re-reported metadata only |
| 2026-10-06 | session_01YaDodMtFhKcu1aAuuUdG2V | permission-block | fable-5-1 | Bash | permission classifier timed out | retried after a read-only step |
| 2026-10-08 | session_01Ns9tKe6qpBG5JToNm9nk4Y | safeguard-stop, model-switch | fable-5-1 → opus-4-8 | Bash heredoc writing the tensorlake worm advisory, re-sent | retry flagged again | six advisories and the PR written on Opus 4.8; not recorded in the run log |
