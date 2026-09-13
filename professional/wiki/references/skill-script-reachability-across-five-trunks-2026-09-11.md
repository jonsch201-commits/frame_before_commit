---
title: "Skill-to-script reachability across five trunks, 2026-09-11 19:18: 42 references, 33 single-trunk, 5 reachable nowhere; 9 of 15 skills depend on a script that lives in exactly one trunk"
kind: reference
date: 2026-09-11
written: "2026-09-11 19:2x CDT; measured 19:16–19:19 by Professional seat 9a25655d (non-author), landed verbatim by 682d274b under its id"
author: "professional backup seat 9a25655d"
status: LIVE
sensitivity: T1
instrument: "~/.claude/jobs/9a25655d/tmp/bucket_refs2.py; five enumerated roots N:\\claude-professional, N:\\claude-cfl\\clone, N:\\claude-personal, N:\\claude-secretary, N:\\antigravity-hub; skill roots ~/.claude/skills and N:\\claude-professional\\.claude\\skills; same regex as scripts/skill_reach.py"
bound: "repo-relative scripts/ paths only; skill-local scripts/ subdirectories and G: trees not tried; 'nowhere' means the five N: roots"
links: "query-before-build (wanted, not yet written), membership-is-not-retrievability (wanted, not yet written) -- see disposition footer"
---

# The defect, counted
A machine-global skill that names a repo-relative script is broken by construction in every trunk except the one holding the script, because `sync-universal.sh` promotes `skills/` machine-wide and never `scripts/`. This page is the count. It replaces this trunk's C11 label "42 DEAD" with what the population supports: 42 unreachable from this trunk, 5 reachable nowhere. Herald predicted the third bucket would be much smaller than 42 before the run; it was 5.

# Verbatim stdout of bucket_refs2.py, 19:18 CDT

```
roots: professional=OK, cfl=OK, personal=OK, secretary=OK, antigravity=OK
skills naming scripts = 15; distinct refs = 42
refs by number of trunks holding them: {0: 5, 1: 33, 2: 4}

PER REFERENCE (holders):
  scripts/ancestor.py                                  1  professional
  scripts/audit/ask_elder.py                           1  cfl
  scripts/audit/check_before_dispatch.py               1  cfl
  scripts/audit/check_compact_loss.py                  1  cfl
  scripts/audit/check_exchange_organization.py         1  cfl
  scripts/audit/exchange_write_check.py                1  cfl
  scripts/audit/for_jon_routed.py                      1  cfl
  scripts/audit/frontmatter_census.py                  1  cfl
  scripts/audit/lint_silence_clause.py                 1  cfl
  scripts/audit/on_silence_report.py                   1  cfl
  scripts/audit/reader_cost.py                         1  cfl
  scripts/audit/scan_midturn_messages.py               2  cfl,personal
  scripts/audit/su_gate.sh                             1  cfl
  scripts/audit/ticket_id_unique.py                    1  cfl
  scripts/audit/verdict_provenance_lint.py             1  cfl
  scripts/barrier_session_identity.py                  1  antigravity
  scripts/check_tree_occupancy.py                      2  personal,antigravity
  scripts/check_updates.py                             1  cfl
  scripts/close-check.sh                               1  personal
  scripts/consolidate_memory.py                        0  NONE
  scripts/convert-export.py                            0  NONE
  scripts/extract_claude_code_sessions.py              1  cfl
  scripts/graphrag.sh                                  1  professional
  scripts/graphrag/build_index.py                      1  cfl
  scripts/graphrag/retrieve.py                         2  cfl,personal
  scripts/hub_check.py                                 1  cfl
  scripts/inbound_dispatcher.py                        1  antigravity
  scripts/index_gen.py                                 1  professional
  scripts/lanes/nightly_corpus_delta.py                1  cfl
  scripts/lanes/regenerate_canonical.sh                1  cfl
  scripts/lanes/transcript_corpus_diff.py              1  cfl
  scripts/lint.sh                                      2  professional,personal
  scripts/ollama_wiki/wiki_agent.py                    1  cfl
  scripts/orphan_census.py                             1  personal
  scripts/pairing_check.py                             0  NONE
  scripts/pipeline.py                                  0  NONE
  scripts/readiness.sh                                 1  secretary
  scripts/rebuild-index.sh                             1  secretary
  scripts/refresh_beacon.py                            1  antigravity
  scripts/selftest-all.sh                              1  secretary
  scripts/session_identity.py                          1  professional
  scripts/write_barrier_memory.py                      0  NONE

PER SKILL:
  chat-exporter            machine-global refs= 1 single-trunk= 0 nowhere= 1 here= 0 trunks=NONE
  dream                    tree-local     refs= 4 single-trunk= 3 nowhere= 0 here= 2 trunks=personal,professional
  exchange-letters         machine-global refs= 3 single-trunk= 3 nowhere= 0 here= 0 trunks=cfl
  ground-before-stating    machine-global refs= 2 single-trunk= 2 nowhere= 0 here= 0 trunks=cfl
  loom                     machine-global refs= 1 single-trunk= 1 nowhere= 0 here= 0 trunks=cfl
  memory-core              machine-global refs= 2 single-trunk= 0 nowhere= 2 here= 0 trunks=NONE
  oath-checks              tree-local     refs= 1 single-trunk= 0 nowhere= 0 here= 1 trunks=personal,professional
  oath-pairing-check       machine-global refs= 1 single-trunk= 0 nowhere= 1 here= 0 trunks=NONE
  present-to-jon           machine-global refs= 1 single-trunk= 1 nowhere= 0 here= 0 trunks=cfl
  probe-registry           machine-global refs= 1 single-trunk= 0 nowhere= 0 here= 0 trunks=cfl,personal
  transcript-parser        machine-global refs= 3 single-trunk= 2 nowhere= 1 here= 0 trunks=cfl
  tree-occupancy-guard     machine-global refs= 1 single-trunk= 0 nowhere= 0 here= 0 trunks=antigravity,personal
  wiki-master              machine-global refs= 9 single-trunk= 7 nowhere= 1 here= 0 trunks=cfl,personal
  wiki-query               machine-global refs= 5 single-trunk= 4 nowhere= 0 here= 0 trunks=cfl,personal
  wikiskills-improve       machine-global refs=13 single-trunk=12 nowhere= 0 here= 3 trunks=antigravity,cfl,personal,professional,secretary

SKILLS WITH >=1 SCRIPT LIVING IN EXACTLY ONE TRUNK: 9 of 15
SKILLS WHOSE EVERY SCRIPT LIVES IN EXACTLY ONE TRUNK: 4 of 15
machine-global skills among the >=1 set: 8
```

# What the fleet does with it
- Public-tree rule for PR 4 criterion 2: every `scripts/` path a shipped skill names resolves inside the shipped tree.
- Fix shapes for machine-global skills, both already in `/wake`: a per-trunk table (Step 0), or degrade loudly ("ANCESTOR: UNKNOWN, go on").
- The worst case is the fleet's own improvement skill: `wikiskills-improve` names 13 scripts, 12 of them single-trunk, across all five trunks. No machine resolves it whole except one with all five roots mounted.
- Related, same evening: the lint check C23 that reports files absent from the query corpus reads `N:\claude-corpus\professional`, a mirror whose newest write was 18:13:13 and whose sync step timed out at 15:11; the index rebuilt at 19:11 was built over a mirror that had not received today's files. Mirror lag, not index lag.

**Disposition (2026-09-12 wiki-master, C22):** the frontmatter `links:` field carried two dangling body wikilinks — `query-before-build` and `membership-is-not-retrievability` — with no page under either name anywhere in `wiki/`. Both read as wanted companion-concept pages (the M-14 look-before-build gate, and the reachable-vs-retrieved distinction this page's own body draws on) that were never written; left OPEN rather than stubbed. De-linked from `[[...]]` syntax so C22 no longer counts them as unresolved.
