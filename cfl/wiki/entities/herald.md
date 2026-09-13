---
format: cfl-page/v1
kind: entity
slug: herald
title: Herald
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: seat
retrieval_key: herald personal project manager seat
aliases: [Herald, Herald of Home and Life, herald-of-home-and-life]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: active seat as of this writing; see wiki/concepts/herald-of-home-and-life.md for behavioral detail
probe_sealed: "What role does Herald play among Jon's personal-domain seats? => A personal project manager that routes incoming personal questions among Soul, Guide-of-Home-and-Family, and Exchequer, and holds open threads across Jon's personal life. TRUSTED"
---

## What it is

Herald is one of Jon's four personal-domain (Trunk 1) role seats — a Claude Code / claude.ai
identity that functions as a personal project manager, routing incoming personal questions among
Soul, Guide-of-Home-and-Family, and Exchequer, and holding open threads across Jon's personal
life. Herald is also documented as a background-agent-style skill/role in Claude Code, distinct
from the other three roles by a session-open protocol that loads all four wiki sub-indexes.
Herald also participates as a peer seat in CFL's cross-trunk correspondence (letters "to Herald",
"from Herald" appear across the corpus).

## Where it appears

Re-measured by this lane against the federated index (`docs_fts`), `WHERE trunk != 'XC-Exchequer'`:

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Herald' AND trunk != 'XC-Exchequer';
```
Result: **7564** matching rows (docs_fts rows are per-file/per-window chunks, not deduplicated
files).

The dream-sweep candidate list (`DREAM-2026-09-01-...`) reported **972 files**. That count and
this lane's 7564 differ by far more than 20% — flagged. The two numbers are not measuring the
same unit: the dream sweep counted distinct files in a narrower scope (this trunk's own working
tree at the time), while the federated index spans five trunks' raw + wiki corpora with many
windowed chunks per source file. Treat 972 as the file-level estimate and 7564 as the
chunk-level federated count; neither supersedes the other without re-deriving on the same corpus.

## Links

- [[herald-of-home-and-life]] — existing concept page with session-open protocol detail
- [[agent-guide]] — role → artifact ownership table lists `herald` under Personal-domain routing

## Not recorded here

No characterization of Herald's judgment, performance, or relationship to Jon beyond the
descriptive routing facts above. No family-member names, no financial figures, no predictions
about Herald's future scope.
