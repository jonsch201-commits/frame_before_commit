# DERIVATION-LOG -- public-safe derived tree

Produced by `scripts/audit/derive_public_tree.py` (lane PUB-1).

Source: fs N:/claude-cfl/clone

**Two dispositions only: INCLUDE byte-identical, or EXCLUDE whole-file. No file's content was rewritten, and nothing in the source tree was modified.**

## Exclusion set

- Read from `scripts/audit/public_exclusions.txt` (sha256 `72e237bd67fdf79a51b57cfd3e4e35e3e0e352784a4ff8fafe5e4ddb5cfa316c`), never inferred from repo prose.
- DIR_NAME entries: XC-Exchequer | CONTENT_CLASS entries: 9 | PATH_PREFIX entries: 17

## Gazetteer arming

- ARMED: 4 gazetteer entries loaded (entries themselves are never printed).

## Counts

| quantity | n |
|---|---|
| paths at source | 18409 |
| not in the include spec (never considered) | 17299 |
| considered | 1110 |
| INCLUDED | 1046 |
| EXCLUDED (distinct files) | 94 |
| exclusion hits (a file may carry several) | 379 |

## Exclusions by class

| class | files |
|---|---|
| BINARY-OR-UNDECODABLE | 1 |
| CONTENT-ACCOUNT | 3 |
| CONTENT-ADDRESS | 3 |
| CONTENT-CARD | 14 |
| CONTENT-EMAIL | 5 |
| CONTENT-FINANCIAL | 7 |
| CONTENT-NAME | 45 |
| CONTENT-PHONE | 3 |
| CONTENT-SSN | 3 |
| CONTENT-XC-EXCHEQUER-PATH | 6 |
| ENTITY-NOT-SEAT-OR-SYSTEM | 3 |
| PATH-DENY-EXACT | 30 |

## Every exclusion (path, class, line, detail)

| path | class | line | detail |
|---|---|---|---|
| `.claude/hooks/__pycache__/global-staleness-probe.cpython-314.pyc` | BINARY-OR-UNDECODABLE | 0 | not valid utf-8 |
| `scripts/audit/assign_branch_frontmatter.py` | CONTENT-NAME | 196 |  |
| `scripts/audit/assign_branch_frontmatter.py` | CONTENT-NAME | 196 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 47 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 47 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 47 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 52 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 52 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 145 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 146 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 146 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 146 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 147 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 166 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 179 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 179 |  |
| `scripts/audit/check_tracked_content.py` | CONTENT-NAME | 179 |  |
| `scripts/audit/corpus_index.py` | CONTENT-NAME | 65 |  |
| `scripts/audit/depii_derive.py` | CONTENT-NAME | 166 |  |
| `scripts/audit/depii_derive.py` | CONTENT-NAME | 166 |  |
| `scripts/audit/depii_derive.py` | CONTENT-NAME | 167 |  |
| `scripts/audit/depii_derive.py` | CONTENT-NAME | 345 |  |
| `scripts/audit/depii_lexicon.py` | CONTENT-CARD | 216 | Luhn-valid, non-excluded context |
| `scripts/audit/depii_path_canary.py` | CONTENT-ACCOUNT | 47 |  |
| `scripts/audit/depii_path_canary.py` | CONTENT-ADDRESS | 41 |  |
| `scripts/audit/depii_path_canary.py` | CONTENT-CARD | 43 | Luhn-valid, non-excluded context |
| `scripts/audit/depii_path_canary.py` | CONTENT-EMAIL | 40 |  |
| `scripts/audit/depii_path_canary.py` | CONTENT-FINANCIAL | 0 | account-number pattern @L47 |
| `scripts/audit/depii_path_canary.py` | CONTENT-PHONE | 39 |  |
| `scripts/audit/depii_path_canary.py` | CONTENT-SSN | 42 |  |
| `scripts/audit/ingest_gate.py` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '.ofx' |
| `scripts/audit/ingest_gate.py` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '.qfx' |
| `scripts/audit/ingest_gate.py` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '<BANKTRANLIST>' |
| `scripts/audit/ingest_gate.py` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '<OFX>' |
| `scripts/audit/ingest_gate.py` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '<STMTTRN>' |
| `scripts/audit/ingest_gate.py` | CONTENT-FINANCIAL | 0 | OFX/QFX marker 'OFXHEADER' |
| `scripts/audit/ingest_gate.py` | CONTENT-XC-EXCHEQUER-PATH | 146 | XC-Exchequer/ledger.ofx |
| `scripts/audit/ingest_gate.py` | CONTENT-XC-EXCHEQUER-PATH | 146 | XC-Exchequer\file |
| `scripts/audit/ingest_gate.py` | CONTENT-XC-EXCHEQUER-PATH | 153 | XC-Exchequer\b |
| `scripts/audit/leak_control.py` | CONTENT-ACCOUNT | 98 |  |
| `scripts/audit/leak_control.py` | CONTENT-ADDRESS | 89 |  |
| `scripts/audit/leak_control.py` | CONTENT-CARD | 50 | Luhn-valid, non-excluded context |
| `scripts/audit/leak_control.py` | CONTENT-EMAIL | 54 |  |
| `scripts/audit/leak_control.py` | CONTENT-FINANCIAL | 0 | account-number pattern @L98 |
| `scripts/audit/leak_control.py` | CONTENT-FINANCIAL | 0 | balance-with-currency pattern |
| `scripts/audit/leak_control.py` | CONTENT-PHONE | 56 |  |
| `scripts/audit/leak_control.py` | CONTENT-SSN | 76 |  |
| `scripts/audit/leak_control.py` | CONTENT-XC-EXCHEQUER-PATH | 60 | XC-Exchequer/2026-ledger-summary.md |
| `scripts/audit/leak_control.py` | CONTENT-XC-EXCHEQUER-PATH | 66 | XC-Exchequer/leakctl-plant-path.md |
| `scripts/audit/leak_control.py` | CONTENT-XC-EXCHEQUER-PATH | 67 | XC-Exchequer\n\nThis |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 219 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 219 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 749 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 784 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 787 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 873 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 876 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 883 |  |
| `scripts/audit/publication_screen.py` | CONTENT-NAME | 885 |  |
| `scripts/audit/publish_content_gate.py` | CONTENT-NAME | 351 |  |
| `scripts/audit/publish_content_gate.py` | CONTENT-NAME | 361 |  |
| `scripts/audit/publish_lexicon.py` | CONTENT-NAME | 34 |  |
| `scripts/audit/publish_lexicon.py` | CONTENT-NAME | 34 |  |
| `scripts/audit/publish_lexicon.py` | CONTENT-NAME | 34 |  |
| `scripts/audit/publish_lexicon.py` | CONTENT-NAME | 34 |  |
| `scripts/audit/selftest_ingest_gate.py` | CONTENT-CARD | 245 | Luhn-valid, non-excluded context |
| `scripts/audit/selftest_ingest_gate.py` | CONTENT-FINANCIAL | 0 | balance-with-currency pattern |
| `scripts/audit/selftest_ingest_gate.py` | CONTENT-XC-EXCHEQUER-PATH | 271 | XC-Exchequer/, |
| `scripts/audit/selftest_ingest_gate.py` | CONTENT-XC-EXCHEQUER-PATH | 274 | XC-Exchequer/leak.md |
| `scripts/audit/verify_quotes.py` | PATH-DENY-EXACT | 0 | LOCATION (comments cite the home-repair page and a given name) |
| `scripts/audit/write_fence.py` | CONTENT-ACCOUNT | 675 |  |
| `scripts/audit/write_fence.py` | CONTENT-CARD | 631 | Luhn-valid, non-excluded context |
| `scripts/audit/write_fence.py` | CONTENT-CARD | 691 | Luhn-valid, non-excluded context |
| `scripts/audit/write_fence.py` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '.ofx' |
| `scripts/audit/write_fence.py` | CONTENT-FINANCIAL | 0 | account-number pattern @L675 |
| `scripts/audit/write_fence.py` | CONTENT-SSN | 630 |  |
| `scripts/audit/write_fence.py` | CONTENT-XC-EXCHEQUER-PATH | 724 | XC-Exchequer/ledger-2026-08.ofx |
| `scripts/graphrag/render_history_cc.py` | CONTENT-CARD | 252 | Luhn-valid, non-excluded context |
| `scripts/graphrag/render_history_cc.py` | CONTENT-CARD | 268 | Luhn-valid, non-excluded context |
| `scripts/graphrag/render_history_cc.py` | CONTENT-CARD | 280 | Luhn-valid, non-excluded context |
| `scripts/migrations/add_asana_items.py` | CONTENT-NAME | 3 |  |
| `scripts/migrations/add_asana_items.py` | CONTENT-NAME | 9 |  |
| `scripts/migrations/add_asana_items.py` | CONTENT-NAME | 17 |  |
| `scripts/migrations/add_asana_items.py` | CONTENT-NAME | 18 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 3 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 8 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 21 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 22 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 33 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 34 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 44 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 46 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 50 |  |
| `scripts/migrations/reclassify_categories.py` | CONTENT-NAME | 87 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 3 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 6 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 11 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 43 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 44 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 53 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 57 |  |
| `scripts/migrations/reprioritize_and_sort.py` | CONTENT-NAME | 60 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-ADDRESS | 175 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-CARD | 177 | Luhn-valid, non-excluded context |
| `scripts/pii/ollama_strip.py` | CONTENT-CARD | 183 | Luhn-valid, non-excluded context |
| `scripts/pii/ollama_strip.py` | CONTENT-EMAIL | 175 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-EMAIL | 183 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-NAME | 177 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-NAME | 177 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-NAME | 184 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-PHONE | 178 |  |
| `scripts/pii/ollama_strip.py` | CONTENT-PHONE | 184 |  |
| `skills/cross-venue-intake/SKILL.md` | PATH-DENY-EXACT | 0 | CREDENTIAL-SHAPED access locator (Drive folder id) |
| `skills/ground-before-stating/references/worked-examples.md` | CONTENT-NAME | 121 |  |
| `skills/guide-of-home-and-family/SKILL.md` | CONTENT-NAME | 47 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 153 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 155 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 200 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 257 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 257 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 267 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 269 |  |
| `skills/herald/SKILL.md` | CONTENT-NAME | 272 |  |
| `skills/security-master/SKILL.md` | PATH-DENY-EXACT | 0 | HOUSEHOLD-FINANCE (financial-account providers + personal security incident) |
| `skills/soul/SKILL.md` | PATH-DENY-EXACT | 0 | FAMILY+HEALTH+HOUSEHOLD-FINANCE (three sections) |
| `skills/wiki-orientation/SKILL.md` | CONTENT-NAME | 60 |  |
| `skills/wiki-orientation/SKILL.md` | CONTENT-NAME | 60 |  |
| `skills/wiki-orientation/SKILL.md` | CONTENT-NAME | 85 |  |
| `wiki/concepts/herald-of-home-and-life.md` | CONTENT-NAME | 35 |  |
| `wiki/concepts/personal-role-architecture.md` | CONTENT-NAME | 30 |  |
| `wiki/concepts/personal-role-architecture.md` | CONTENT-NAME | 61 |  |
| `wiki/concepts/personal-role-architecture.md` | CONTENT-NAME | 63 |  |
| `wiki/concepts/probe-registry.md` | CONTENT-NAME | 63 |  |
| `wiki/concepts/repo-hygiene.md` | PATH-DENY-EXACT | 0 | HOUSEHOLD-FINANCE (lock warranty claim) |
| `wiki/entities/ENTITY-masters-kitchen-bath.md` | ENTITY-NOT-SEAT-OR-SYSTEM | 0 | entity_type: (absent) |
| `wiki/entities/claude-code.md` | ENTITY-NOT-SEAT-OR-SYSTEM | 0 | entity_type: (absent) |
| `wiki/entities/index.md` | CONTENT-NAME | 57 |  |
| `wiki/entities/jon.md` | ENTITY-NOT-SEAT-OR-SYSTEM | 0 | entity_type: (absent) |
| `wiki/index.md` | CONTENT-NAME | 885 |  |
| `wiki/index.md` | CONTENT-NAME | 886 |  |
| `wiki/index.md` | CONTENT-NAME | 899 |  |
| `wiki/references/SCOPE-anthropic-zips-read-fence-2026-08-24.md` | PATH-DENY-EXACT | 0 | HEALTH (semantic read chunk 3) |
| `wiki/references/agent-memory/active-work-state.md` | PATH-DENY-EXACT | 0 | FAMILY (semantic read chunk 3) |
| `wiki/references/agent-memory/cc-jsonl-thinking-signature-only.md` | PATH-DENY-EXACT | 0 | THIRD-PARTY |
| `wiki/references/agent-memory/md-not-uncaptured-authoritative-disposition.md` | PATH-DENY-EXACT | 0 | FAMILY |
| `wiki/references/agent-memory/t44-apollo-artemis-complete.md` | CONTENT-NAME | 42 |  |
| `wiki/references/agent-memory/verify-conditional-claim-resolution.md` | PATH-DENY-EXACT | 0 | HOUSEHOLD-FINANCE (solar lease) |
| `wiki/references/audit-census-2026-07-13.md` | CONTENT-NAME | 44 |  |
| `wiki/references/audit-census-2026-07-13.md` | CONTENT-NAME | 68 |  |
| `wiki/references/audit-census-2026-07-13.md` | CONTENT-NAME | 145 |  |
| `wiki/references/audit-census-2026-07-13.md` | CONTENT-NAME | 152 |  |
| `wiki/references/audit-census-2026-07-13.md` | CONTENT-NAME | 156 |  |
| `wiki/references/audit-census-2026-07-13.md` | CONTENT-NAME | 168 |  |
| `wiki/references/audit-conformance-ledger.md` | CONTENT-NAME | 131 |  |
| `wiki/references/audit-conformance-ledger.md` | CONTENT-NAME | 170 |  |
| `wiki/references/audit-conformance-ledger.md` | CONTENT-NAME | 171 |  |
| `wiki/references/audit-conformance-ledger.md` | CONTENT-NAME | 172 |  |
| `wiki/references/audit-conformance-ledger.md` | CONTENT-NAME | 173 |  |
| `wiki/references/audit-conformance-ledger.md` | CONTENT-NAME | 183 |  |
| `wiki/references/audit-program-2026-07-13.md` | PATH-DENY-EXACT | 0 | LOCATION (home town via repair-page slug) + personal security incident |
| `wiki/references/calibration-results-2026-07-13.md` | PATH-DENY-EXACT | 0 | OTHER personal security incident + HOUSEHOLD-FINANCE rows |
| `wiki/references/cfl-branch-registry.md` | CONTENT-NAME | 311 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 95 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 151 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 152 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 153 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 154 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 164 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 493 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 497 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 525 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 526 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 527 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 528 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 529 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 530 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 531 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 532 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 533 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 534 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 535 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 536 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 537 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 538 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 539 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 540 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 541 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 546 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 547 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 548 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 549 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 550 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 551 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 552 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 553 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 554 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 555 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 556 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 557 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 558 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 559 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 562 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 563 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 564 |  |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | CONTENT-NAME | 565 |  |
| `wiki/references/claude-code/settings-reference.md` | CONTENT-EMAIL | 3668 |  |
| `wiki/references/claude-code/settings-reference.md` | CONTENT-EMAIL | 3747 |  |
| `wiki/references/claude-code/settings-reference.md` | CONTENT-EMAIL | 4239 |  |
| `wiki/references/claude-code/settings-reference.md` | CONTENT-EMAIL | 5179 |  |
| `wiki/references/claude-code/settings-reference.md` | CONTENT-EMAIL | 5187 |  |
| `wiki/references/corpus-operations-taxonomy.md` | PATH-DENY-EXACT | 0 | EMPLOYER/THIRD-PARTY |
| `wiki/references/growth-intent-worked-examples/example-a-material-agent-interaction-after.md` | CONTENT-NAME | 67 |  |
| `wiki/references/growth-intent-worked-examples/example-a-material-agent-interaction-after.md` | CONTENT-NAME | 67 |  |
| `wiki/references/ingest-queue.md` | PATH-DENY-EXACT | 0 | LOCATION+FAMILY+HOUSEHOLD-FINANCE+EMPLOYER |
| `wiki/references/partial-sessions-registry.md` | PATH-DENY-EXACT | 0 | GOOGLE-RESOURCE-ID line 38 + EMPLOYER/THIRD-PARTY (token sweep) |
| `wiki/references/pilot-backfill-findings-2026-07-13.md` | PATH-DENY-EXACT | 0 | HOUSEHOLD-FINANCE (secondary-market share purchase research, platforms, valuation figures) |
| `wiki/references/privacy-default-rule-2026-07-29.md` | PATH-DENY-EXACT | 0 | PATH_EXACT row (no comment) |
| `wiki/references/registries/trunks.md` | CONTENT-NAME | 90 |  |
| `wiki/references/registries/trunks.md` | CONTENT-NAME | 90 |  |
| `wiki/references/registries/trunks.md` | CONTENT-NAME | 104 |  |
| `wiki/references/registries/trunks.md` | CONTENT-NAME | 105 |  |
| `wiki/references/registries/trunks.md` | CONTENT-NAME | 106 |  |
| `wiki/references/registries/trunks.md` | CONTENT-NAME | 167 |  |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 1411 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 1413 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 1936 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 1938 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 2637 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 2639 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 4423 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 4425 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 5078 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 5080 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-CARD | 5082 | Luhn-valid, non-excluded context |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '.ofx' |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '.qfx' |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-NAME | 4933 |  |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-NAME | 4955 |  |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 104 | XC-Exchequer/exchange/inbound/ |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 104 | XC-Exchequer/exchange/inbound/, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 104 | XC-Exchequer\exchange |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 104 | XC-Exchequer\exchange\secretary-claudeai-to-XC-Q16-Q24-REOPENED-AND-RULED-2026-08-15.md |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 170 | XC-Exchequer/\\, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 170 | XC-Exchequer/exchange/, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 170 | XC-Exchequer/exchange/README-THIS-IS-A-DEAD-DROP.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 170 | XC-Exchequer/exchange/\ |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 170 | XC-Exchequer/exchange/\, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 170 | XC-Exchequer/exchange/inbound\ |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 509 | XC-Exchequer/tools/xc_ofx.py, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 584 | XC-Exchequer/CLAUDE.md |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 584 | XC-Exchequer/CLAUDE.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 584 | XC-Exchequer/\, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 584 | XC-Exchequer/exchange/inbound/\ |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 719 | XC-Exchequer/exchange, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 719 | XC-Exchequer/exchange/secretary-claudeai-to-XC-Q16-Q24-REOPENED-AND-RULED-2026-08-15.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 719 | XC-Exchequer/exchange/td-005-herald-coordinates-xc-work-and-jons-08-15-rulings-were-never-delivered.md |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 719 | XC-Exchequer/exchange/td-005-herald-coordinates-xc-work-and-jons-08-15-rulings-were-never-delivered.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 763 | XC-Exchequer/exchange/questions-for-triage.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1000 | XC-Exchequer/exchange/personal-to-xc-SUMMONS-second-town-hall-2026-08-15.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1000 | XC-Exchequer/exchange/td-004-inbound-channel-built-and-town-hall-absence.md |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1110 | XC-Exchequer\. |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1154 | XC-Exchequer/exchange/personal-to-xc-Q22-APPROVED-pdfplumber-parse-the-11-2026-08-15.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1154 | XC-Exchequer\\ |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1154 | XC-Exchequer\\exchange\, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1154 | XC-Exchequer\exchange\questions-for-triage.md |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1376 | XC-Exchequer\.claude\settings.json, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1376 | XC-Exchequer\\.claude\\settings.json\ |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1442 | XC-Exchequer/exchange/personal-to-xc-ROUTED-jon-continual-improvement-mandate-2026-08-15.md |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1729 | XC-Exchequer/exchange/td-004-inbound-channel-built-and-town-hall-absence.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1729 | XC-Exchequer/exchange/td-005-…md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1740 | XC-Exchequer/exchange/$b\, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1740 | XC-Exchequer/exchange/herald-to-xc-Q22-EXECUTED-11-of-11-reconciled-2026-08-17.md\ |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 1740 | XC-Exchequer/exchange/herald-to-xc-Q22-EXECUTED-11-of-11-reconciled-2026-08-17.md\; |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 2338 | XC-Exchequer\pointers\2026-08-05-jon-manual-fetch.md |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4900 | XC-Exchequer/exchange/inbound, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4900 | XC-Exchequer\n |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4900 | XC-Exchequer\n\nYour |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4911 | XC-Exchequer/exchange/herald-replies, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4911 | XC-Exchequer\\, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4922 | XC-Exchequer/$d, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4922 | XC-Exchequer/*.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4922 | XC-Exchequer/.claude/settings.json, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4922 | XC-Exchequer/.gitignore, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4933 | XC-Exchequer/exchange/td-013-...-2026-08-23.md, |
| `wiki/skills-gate/INGEST-LEDGER.md` | CONTENT-XC-EXCHEQUER-PATH | 4933 | XC-Exchequer/exchange/td-013-herald-supports-your-jon-and-jessica-status-file-name-it-and-i-pre-review-it-2026-08-23.md, |
| `wiki/skills-gate/validation/su-compact/blind-run1-mechanical.json` | CONTENT-CARD | 577 | Luhn-valid, non-excluded context |
| `wiki/sources/ai-governance/ai-oversight-quality-paper-2026-03-09-89c6d7.md` | PATH-DENY-EXACT | 0 | EMPLOYER (disclosure stance) |
| `wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md` | CONTENT-NAME | 173 |  |
| `wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md` | CONTENT-NAME | 173 |  |
| `wiki/sources/infrastructure/capacity-planning-autonomy-governance-2026-07-10-7f2815.md` | CONTENT-NAME | 64 |  |
| `wiki/sources/infrastructure/capacity-planning-autonomy-governance-2026-07-10-7f2815.md` | CONTENT-NAME | 76 |  |
| `wiki/sources/infrastructure/capacity-planning-autonomy-governance-2026-07-10-7f2815.md` | CONTENT-NAME | 76 |  |
| `wiki/sources/infrastructure/capacity-planning-autonomy-governance-2026-07-10-7f2815.md` | CONTENT-NAME | 76 |  |
| `wiki/sources/infrastructure/cfl-port-work-and-friend-fork-2026-07-09-a0113e.md` | PATH-DENY-EXACT | 0 | PATH_EXACT row (no comment) |
| `wiki/sources/infrastructure/cfl-project-transfer-tom-scoping-2026-08-12-f71d18.md` | CONTENT-NAME | 98 |  |
| `wiki/sources/infrastructure/cfl-project-transfer-tom-scoping-2026-08-12-f71d18.md` | CONTENT-NAME | 111 |  |
| `wiki/sources/infrastructure/citation-audit-2026-05-26.md` | CONTENT-NAME | 224 |  |
| `wiki/sources/infrastructure/citation-audit-2026-05-26.md` | CONTENT-NAME | 225 |  |
| `wiki/sources/infrastructure/citation-audit-2026-05-26.md` | CONTENT-NAME | 264 |  |
| `wiki/sources/infrastructure/computer-use-knowledge-base-organization-2026-09-03-8d00d7.md` | CONTENT-NAME | 80 |  |
| `wiki/sources/infrastructure/coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477.md` | PATH-DENY-EXACT | 0 | HOUSEHOLD-FINANCE |
| `wiki/sources/infrastructure/corpus-completeness-audit-2026-07-08.md` | PATH-DENY-EXACT | 0 | OTHER (vulnerable statement + expense session) |
| `wiki/sources/infrastructure/corpus-loss-audit-2026-07-19.md` | CONTENT-NAME | 187 |  |
| `wiki/sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` | CONTENT-EMAIL | 153 |  |
| `wiki/sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` | CONTENT-NAME | 191 |  |
| `wiki/sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` | CONTENT-NAME | 192 |  |
| `wiki/sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` | CONTENT-NAME | 205 |  |
| `wiki/sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` | CONTENT-NAME | 206 |  |
| `wiki/sources/infrastructure/fable-mirror-first-extended-deployment-2026-08-01-a4db57.md` | PATH-DENY-EXACT | 0 | PATH_EXACT row (no comment) |
| `wiki/sources/infrastructure/global-claude-md-is-cfls-constitution-2026-08-17-03827a.md` | PATH-DENY-EXACT | 0 | GOOGLE-RESOURCE-ID line 122 |
| `wiki/sources/infrastructure/graph-navigation-link-quality-audit-2026-06-04.md` | CONTENT-NAME | 20 |  |
| `wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md` | CONTENT-NAME | 71 |  |
| `wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md` | CONTENT-NAME | 71 |  |
| `wiki/sources/infrastructure/motherboard-request-becomes-memory-tree-and-oath-deposit-2026-08-14-5107dd.md` | CONTENT-XC-EXCHEQUER-PATH | 48 | XC-Exchequer\pointers\2026-08-05-jon-manual-fetch.md |
| `wiki/sources/infrastructure/pm-ds3-verification-backlog-plan-2026-07-10-da51cc.md` | PATH-DENY-EXACT | 0 | PATH_EXACT row (no comment) |
| `wiki/sources/infrastructure/pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont.md` | PATH-DENY-EXACT | 0 | OTHER career intent + HOUSEHOLD-FINANCE + FAMILY + LOCATION |
| `wiki/sources/infrastructure/security-master-docker-permission-priority-2026-06-27-8881d3.md` | PATH-DENY-EXACT | 0 | PATH_EXACT row (no comment) |
| `wiki/sources/infrastructure/self-improvement-framework-triage-roadmap-2026-07-17-44a95b.md` | PATH-DENY-EXACT | 0 | PATH_EXACT row (no comment) |
| `wiki/sources/infrastructure/triage-master-open-items-2026-04-28-090a56.md` | CONTENT-NAME | 77 |  |
| `wiki/sources/infrastructure/triage-project-model-direction-2026-07-11-a3e6cf.md` | PATH-DENY-EXACT | 0 | CREDENTIAL-SHAPED same Drive folder id, line 31 |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 23 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 23 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 24 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 25 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 25 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 28 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 41 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 46 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 53 |  |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | CONTENT-NAME | 53 |  |
| `wiki/sources/infrastructure/wiki-master-audit-skill-review-2026-06-09-707392.md` | CONTENT-NAME | 30 |  |
| `wiki/sources/infrastructure/wiki-master-audit-skill-review-2026-06-09-707392.md` | CONTENT-NAME | 30 |  |
| `wiki/sources/infrastructure/wiki-master-phase-cycle-2026-07-08-774a3a.md` | PATH-DENY-EXACT | 0 | OTHER + CREDENTIAL-SHAPED incident |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 11 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 12 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 13 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 17 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 21 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 32 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 36 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 38 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 56 |  |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | CONTENT-NAME | 58 |  |
| `wiki/sources/infrastructure/wiki-multi-master-audit-2026-06-02-dba2c0b.md` | CONTENT-NAME | 91 |  |
| `wiki/sources/infrastructure/wiki-multi-master-audit-2026-06-02-dba2c0b.md` | CONTENT-NAME | 91 |  |
| `wiki/sources/infrastructure/wiki-session-conflict-resolution-crosslinks-2026-06-04.md` | CONTENT-NAME | 22 |  |
| `wiki/sources/infrastructure/wiki-session-conflict-resolution-crosslinks-2026-06-04.md` | CONTENT-NAME | 22 |  |
| `wiki/sources/reference/cfl-goals-2026-07-08-verbatim.md` | PATH-DENY-EXACT | 0 | FAMILY (verbatim family/wife/kids goals) |
| `wiki/sources/security-master-audit-2026-06-27.md` | CONTENT-NAME | 47 |  |
| `wiki/sources/security-master-audit-2026-06-27.md` | CONTENT-NAME | 47 |  |
| `wiki/sources/security-master-audit-2026-06-27.md` | CONTENT-NAME | 89 |  |
| `wiki/sources/security-master-audit-2026-06-27.md` | CONTENT-NAME | 89 |  |
| `wiki/sources/session-stubs.md` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '.ofx' |
| `wiki/sources/session-stubs.md` | CONTENT-FINANCIAL | 0 | OFX/QFX marker '.qfx' |
| `wiki/sources/session-stubs.md` | CONTENT-NAME | 40 |  |
| `wiki/sources/session-stubs.md` | CONTENT-NAME | 40 |  |
| `wiki/sources/session-stubs.md` | CONTENT-NAME | 57 |  |
| `wiki/sources/session-stubs.md` | CONTENT-NAME | 57 |  |
| `wiki/sources/session-stubs.md` | CONTENT-NAME | 60 |  |
| `wiki/test-outputs/HOOK-HARNESS-run.jsonl` | CONTENT-CARD | 6 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-degrade.jsonl` | CONTENT-CARD | 18 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-degrade.jsonl` | CONTENT-CARD | 34 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-final-2026-09-02.jsonl` | CONTENT-CARD | 18 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-final-2026-09-02.jsonl` | CONTENT-CARD | 20 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-final-2026-09-02.jsonl` | CONTENT-CARD | 23 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-final-2026-09-02.jsonl` | CONTENT-CARD | 26 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-final-2026-09-02.jsonl` | CONTENT-CARD | 29 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-final-2026-09-02.jsonl` | CONTENT-CARD | 34 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 2 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 5 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 9 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 13 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 18 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 20 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 23 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 26 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 29 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | CONTENT-CARD | 34 | Luhn-valid, non-excluded context |
| `wiki/test-outputs/HOOK-HARNESS-v5-cfl-baseline.jsonl` | CONTENT-CARD | 19 | Luhn-valid, non-excluded context |

## REPORT-ONLY (nothing was withheld for these)

**0 row(s).** These classes are REPORTED and never cut. `FM-HELD-PROSE` exists because T5 (Professional, 2026-09-13) found `HELD_VAL_RX` matching `held` inside a value's PROSE and withholding a LIVE page for a sentence about being held to a standard. `FM_HELD_KEY` includes `visibility` and `FM_HELD_VALUE` includes `held`/`personal`/`private`, all ordinary English, so any narrative value under a common key tripped it. **A page is withheld for a DECLARATION, not for a sentence** -- and the match was not loosened, because failing open is the dangerous direction on a public surface.

| path | class | line | detail |
|---|---|---|---|
| *(none)* | | | |

## REFERENCE-SURVIVORS

**REFERENCE-SURVIVORS: 72 of 261 excluded files have >= 1 inbound reference by name in an INCLUDED file (1015 refs total); PATH_EXACT rows: 25 of 30 have survivors**

A whole-file EXCLUDE removes the body; the NAME survives wherever an INCLUDED file referred to it. Nothing below was rewritten -- a reference by name is disclosed here as a name only. Forms: FULL (repo-relative path), SUFFIX (parent-dir/basename), FILENAME, WIKILINK (`[[stem]]`), STEM (bare basename). FILENAME is armed only when no other file at source shares the basename; WIKILINK and STEM only when no other path shares the stem, and STEM additionally only for slug-shaped stems (a hyphen, underscore or digit) -- a shared name or a plain word is not a reference to THIS file, and the `forms dropped` column says so per file. One row per (referring file, line, excluded file), most specific form wins. `--fail-on-survivors` exits 4 when any PATH_EXACT row has >= 1 survivor.

| excluded file | exclusion | inbound refs | forms dropped |
|---|---|---|---|
| `scripts/audit/verify_quotes.py` | PATH_EXACT | 20 | none |
| `skills/cross-venue-intake/SKILL.md` | PATH_EXACT | 5 | FILENAME (45 files at source named SKILL.md); WIKILINK+STEM (45 paths at source share stem SKILL) |
| `skills/security-master/SKILL.md` | PATH_EXACT | 0 | FILENAME (45 files at source named SKILL.md); WIKILINK+STEM (45 paths at source share stem SKILL) |
| `skills/soul/SKILL.md` | PATH_EXACT | 0 | FILENAME (45 files at source named SKILL.md); WIKILINK+STEM (45 paths at source share stem SKILL) |
| `wiki/concepts/repo-hygiene.md` | PATH_EXACT | 12 | none |
| `wiki/references/SCOPE-anthropic-zips-read-fence-2026-08-24.md` | PATH_EXACT | 1 | none |
| `wiki/references/agent-memory/active-work-state.md` | PATH_EXACT | 8 | none |
| `wiki/references/agent-memory/cc-jsonl-thinking-signature-only.md` | PATH_EXACT | 13 | none |
| `wiki/references/agent-memory/md-not-uncaptured-authoritative-disposition.md` | PATH_EXACT | 13 | none |
| `wiki/references/agent-memory/verify-conditional-claim-resolution.md` | PATH_EXACT | 4 | none |
| `wiki/references/audit-program-2026-07-13.md` | PATH_EXACT | 1 | none |
| `wiki/references/calibration-results-2026-07-13.md` | PATH_EXACT | 2 | none |
| `wiki/references/corpus-operations-taxonomy.md` | PATH_EXACT | 2 | none |
| `wiki/references/ingest-queue.md` | PATH_EXACT | 13 | none |
| `wiki/references/partial-sessions-registry.md` | PATH_EXACT | 5 | none |
| `wiki/references/pilot-backfill-findings-2026-07-13.md` | PATH_EXACT | 2 | none |
| `wiki/references/privacy-default-rule-2026-07-29.md` | PATH_EXACT | 6 | none |
| `wiki/sources/ai-governance/ai-oversight-quality-paper-2026-03-09-89c6d7.md` | PATH_EXACT | 10 | none |
| `wiki/sources/infrastructure/cfl-port-work-and-friend-fork-2026-07-09-a0113e.md` | PATH_EXACT | 0 | none |
| `wiki/sources/infrastructure/coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477.md` | PATH_EXACT | 10 | none |
| `wiki/sources/infrastructure/corpus-completeness-audit-2026-07-08.md` | PATH_EXACT | 1 | none |
| `wiki/sources/infrastructure/fable-mirror-first-extended-deployment-2026-08-01-a4db57.md` | PATH_EXACT | 1 | none |
| `wiki/sources/infrastructure/global-claude-md-is-cfls-constitution-2026-08-17-03827a.md` | PATH_EXACT | 0 | none |
| `wiki/sources/infrastructure/pm-ds3-verification-backlog-plan-2026-07-10-da51cc.md` | PATH_EXACT | 1 | none |
| `wiki/sources/infrastructure/pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont.md` | PATH_EXACT | 9 | none |
| `wiki/sources/infrastructure/security-master-docker-permission-priority-2026-06-27-8881d3.md` | PATH_EXACT | 0 | none |
| `wiki/sources/infrastructure/self-improvement-framework-triage-roadmap-2026-07-17-44a95b.md` | PATH_EXACT | 4 | none |
| `wiki/sources/infrastructure/triage-project-model-direction-2026-07-11-a3e6cf.md` | PATH_EXACT | 2 | none |
| `wiki/sources/infrastructure/wiki-master-phase-cycle-2026-07-08-774a3a.md` | PATH_EXACT | 2 | none |
| `wiki/sources/reference/cfl-goals-2026-07-08-verbatim.md` | PATH_EXACT | 2 | none |
| `.claude/hooks/state/.gitignore` | PATH_PREFIX | 0 | FILENAME (2 files at source named .gitignore); WIKILINK+STEM (7 paths at source share stem ) |
| `.claude/hooks/state/MODE` | PATH_PREFIX | 40 | STEM ('MODE' is a plain word, not slug-shaped) |
| `.claude/hooks/state/post-skills-sync.log` | PATH_PREFIX | 1 | WIKILINK+STEM (2 paths at source share stem post-skills-sync) |
| `.claude/hooks/state/postcompact-graded-20260905T144121-71ce5a0e.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260905T151631-71ce5a0e.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260905T223400-46276084.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260906T215038-46276084.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260907T202211-a86404c0.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260912T012338-8634adc3.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260912T112654-8634adc3.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260912T163111-8634adc3.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/postcompact-graded-20260912T204558-8634adc3.stamp` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/pre-stop-consult.log` | PATH_PREFIX | 6 | WIKILINK+STEM (2 paths at source share stem pre-stop-consult) |
| `.claude/hooks/state/prestop-0242b512-3782-437e-97b9-562ee954b04b-6.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-0808192b-a200-45db-a535-2d21a1d0f4f4-7.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-1191b3e8-7f9a-45de-a3a3-fbe0e2759d74-5.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-10.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-1142.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-1248.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-1402.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-1625.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-2070.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-3522.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-3907.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-4432.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-4644.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-4678.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-4972.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-5045.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-5590.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-5934.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-5958.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-6006.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-6178.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-6274.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-6408.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-6789.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-6992.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-7022.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-7179.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-7226.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-7590.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-8502.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-861.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-8843.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-9117.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-9209.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-9273.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-9423.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-46276084-5985-4514-9ad1-0d77cf7a0ceb-9503.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-5201a340-c9d1-4c6e-8ae3-adc9bfbd2ad3-6.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-56676636-7691-4d0e-9ad2-1cc0cd3ace91-6.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-10336.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-11246.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-11512.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-11653.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-12221.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-12343.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-12985.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-1303.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-1386.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-14286.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-14847.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-15648.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-15953.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-17206.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-17406.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-17648.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-17758.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-17931.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-20.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-20304.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-20595.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-21018.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-21376.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-214.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-2352.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-2728.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-2883.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-2930.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-2964.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-3540.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-3602.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-4527.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-4961.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5119.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5174.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5183.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5300.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5339.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5391.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5421.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5435.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5456.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5503.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5519.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5539.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5553.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5722.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5857.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5901.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5954.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-5986.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6007.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6028.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6049.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6078.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6092.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6222.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6287.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-6451.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-737.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-751.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-8531.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-8559.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-8619.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-8643.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-9050.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-9337.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-9436.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-9744.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb-9945.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-78df46c6-2239-4a4e-ac3e-c24fca71a7ce-7.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-10367.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-10853.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-1114.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-11285.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-11483.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-11739.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-1292.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-1418.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-1474.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-21.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-3000.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-3210.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-3270.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-3668.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-403.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-4318.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-4612.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-4878.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-5265.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-5669.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-5923.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-6037.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-6217.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-6574.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-6718.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-709.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-7226.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-7467.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-7779.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-8531.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-8621.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-875.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-8813.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-9277.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-9498.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-8634adc3-9999-4303-8ca9-714cce57a921-9834.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-a86404c0-42c6-4581-a86f-a52e35bdfae7-18.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-a86404c0-42c6-4581-a86f-a52e35bdfae7-758.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-a9842e87-0a5a-4285-917f-29d38696d807-64.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-c5265c73-1758-4a20-aba2-cac6631eee5d-6.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-d8fa6bf3-4513-48d1-be0c-ed83c8dd116f-64.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/prestop-harness-0000-8.count` | PATH_PREFIX | 1 | none |
| `.claude/hooks/state/prestop-test-0000-0.count` | PATH_PREFIX | 0 | none |
| `.claude/hooks/state/skills-sync.stamp` | PATH_PREFIX | 1 | none |
| `.claude/hooks/__pycache__/global-staleness-probe.cpython-314.pyc` | SCAN | 0 | none |
| `scripts/audit/assign_branch_frontmatter.py` | SCAN | 6 | none |
| `scripts/audit/check_tracked_content.py` | SCAN | 0 | none |
| `scripts/audit/corpus_index.py` | SCAN | 97 | none |
| `scripts/audit/depii_derive.py` | SCAN | 2 | none |
| `scripts/audit/depii_lexicon.py` | SCAN | 18 | none |
| `scripts/audit/depii_path_canary.py` | SCAN | 1 | none |
| `scripts/audit/ingest_gate.py` | SCAN | 20 | none |
| `scripts/audit/leak_control.py` | SCAN | 6 | none |
| `scripts/audit/publication_screen.py` | SCAN | 4 | none |
| `scripts/audit/publish_content_gate.py` | SCAN | 4 | none |
| `scripts/audit/publish_lexicon.py` | SCAN | 2 | none |
| `scripts/audit/selftest_ingest_gate.py` | SCAN | 0 | none |
| `scripts/audit/write_fence.py` | SCAN | 11 | none |
| `scripts/graphrag/render_history_cc.py` | SCAN | 2 | none |
| `scripts/migrations/add_asana_items.py` | SCAN | 0 | none |
| `scripts/migrations/reclassify_categories.py` | SCAN | 0 | none |
| `scripts/migrations/reprioritize_and_sort.py` | SCAN | 0 | none |
| `scripts/pii/ollama_strip.py` | SCAN | 0 | none |
| `skills/ground-before-stating/references/worked-examples.md` | SCAN | 4 | FILENAME (2 files at source named worked-examples.md); WIKILINK+STEM (2 paths at source share stem worked-examples) |
| `skills/guide-of-home-and-family/SKILL.md` | SCAN | 0 | FILENAME (45 files at source named SKILL.md); WIKILINK+STEM (45 paths at source share stem SKILL) |
| `skills/herald/SKILL.md` | SCAN | 4 | FILENAME (45 files at source named SKILL.md); WIKILINK+STEM (45 paths at source share stem SKILL) |
| `skills/wiki-orientation/SKILL.md` | SCAN | 0 | FILENAME (45 files at source named SKILL.md); WIKILINK+STEM (45 paths at source share stem SKILL) |
| `wiki/concepts/herald-of-home-and-life.md` | SCAN | 15 | none |
| `wiki/concepts/personal-role-architecture.md` | SCAN | 9 | none |
| `wiki/concepts/probe-registry.md` | SCAN | 130 | none |
| `wiki/entities/ENTITY-masters-kitchen-bath.md` | SCAN | 0 | none |
| `wiki/entities/claude-code.md` | SCAN | 180 | none |
| `wiki/entities/index.md` | SCAN | 0 | FILENAME (7 files at source named index.md); WIKILINK+STEM (7 paths at source share stem index) |
| `wiki/entities/jon.md` | SCAN | 1 | FILENAME (3 files at source named jon.md); WIKILINK+STEM (3 paths at source share stem jon) |
| `wiki/index.md` | SCAN | 120 | FILENAME (7 files at source named index.md); WIKILINK+STEM (7 paths at source share stem index) |
| `wiki/references/agent-memory/t44-apollo-artemis-complete.md` | SCAN | 2 | none |
| `wiki/references/audit-census-2026-07-13.md` | SCAN | 3 | none |
| `wiki/references/audit-conformance-ledger.md` | SCAN | 7 | none |
| `wiki/references/cfl-branch-registry.md` | SCAN | 18 | none |
| `wiki/references/cfl-file-manifest-2026-07-16.md` | SCAN | 1 | none |
| `wiki/references/claude-code/settings-reference.md` | SCAN | 44 | none |
| `wiki/references/growth-intent-worked-examples/example-a-material-agent-interaction-after.md` | SCAN | 2 | none |
| `wiki/references/registries/trunks.md` | SCAN | 9 | STEM ('trunks' is a plain word, not slug-shaped) |
| `wiki/skills-gate/INGEST-LEDGER.md` | SCAN | 14 | none |
| `wiki/skills-gate/validation/su-compact/blind-run1-mechanical.json` | SCAN | 0 | FILENAME (5 files at source named blind-run1-mechanical.json); WIKILINK+STEM (5 paths at source share stem blind-run1-mechanical) |
| `wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md` | SCAN | 3 | FILENAME (2 files at source named agent-interaction-framework-2026-07-02-5990f2.md); WIKILINK+STEM (2 paths at source share stem agent-interaction-framework-2026-07-02-5990f2) |
| `wiki/sources/infrastructure/capacity-planning-autonomy-governance-2026-07-10-7f2815.md` | SCAN | 1 | none |
| `wiki/sources/infrastructure/cfl-project-transfer-tom-scoping-2026-08-12-f71d18.md` | SCAN | 0 | none |
| `wiki/sources/infrastructure/citation-audit-2026-05-26.md` | SCAN | 3 | FILENAME (3 files at source named citation-audit-2026-05-26.md); WIKILINK+STEM (3 paths at source share stem citation-audit-2026-05-26) |
| `wiki/sources/infrastructure/computer-use-knowledge-base-organization-2026-09-03-8d00d7.md` | SCAN | 0 | none |
| `wiki/sources/infrastructure/corpus-loss-audit-2026-07-19.md` | SCAN | 6 | none |
| `wiki/sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` | SCAN | 1 | none |
| `wiki/sources/infrastructure/graph-navigation-link-quality-audit-2026-06-04.md` | SCAN | 0 | none |
| `wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md` | SCAN | 5 | none |
| `wiki/sources/infrastructure/motherboard-request-becomes-memory-tree-and-oath-deposit-2026-08-14-5107dd.md` | SCAN | 0 | none |
| `wiki/sources/infrastructure/triage-master-open-items-2026-04-28-090a56.md` | SCAN | 4 | none |
| `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` | SCAN | 1 | none |
| `wiki/sources/infrastructure/wiki-master-audit-skill-review-2026-06-09-707392.md` | SCAN | 0 | none |
| `wiki/sources/infrastructure/wiki-master-session-2026-05-25-ee177e24.md` | SCAN | 0 | none |
| `wiki/sources/infrastructure/wiki-multi-master-audit-2026-06-02-dba2c0b.md` | SCAN | 12 | none |
| `wiki/sources/infrastructure/wiki-session-conflict-resolution-crosslinks-2026-06-04.md` | SCAN | 2 | none |
| `wiki/sources/security-master-audit-2026-06-27.md` | SCAN | 3 | none |
| `wiki/sources/session-stubs.md` | SCAN | 39 | none |
| `wiki/test-outputs/HOOK-HARNESS-run.jsonl` | SCAN | 1 | WIKILINK+STEM (2 paths at source share stem HOOK-HARNESS-run) |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-degrade.jsonl` | SCAN | 0 | WIKILINK+STEM (2 paths at source share stem HOOK-HARNESS-v4-cfl-degrade) |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-final-2026-09-02.jsonl` | SCAN | 0 | WIKILINK+STEM (2 paths at source share stem HOOK-HARNESS-v4-cfl-final-2026-09-02) |
| `wiki/test-outputs/HOOK-HARNESS-v4-cfl-postH3b.jsonl` | SCAN | 0 | WIKILINK+STEM (2 paths at source share stem HOOK-HARNESS-v4-cfl-postH3b) |
| `wiki/test-outputs/HOOK-HARNESS-v5-cfl-baseline.jsonl` | SCAN | 0 | WIKILINK+STEM (2 paths at source share stem HOOK-HARNESS-v5-cfl-baseline) |

### `scripts/audit/verify_quotes.py` (PATH_EXACT) -- 20 inbound ref(s)

- `scripts/audit/check_secondary_attribution.py:9` FILENAME `verify_quotes.py`
- `scripts/audit/check_secondary_attribution.py:40` FILENAME `verify_quotes.py`
- `scripts/audit/find_resurrection_candidates.py:51` FILENAME `verify_quotes.py`
- `scripts/audit/stranded_branches.py:10` FILENAME `verify_quotes.py`
- `scripts/audit/sync_parity.py:74` FILENAME `verify_quotes.py`
- `scripts/audit/sync_parity.py:83` FILENAME `verify_quotes.py`
- `wiki/concepts/four-things-the-fleet-is-missing.md:208` FILENAME `verify_quotes.py`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:318` FILENAME `verify_quotes.py`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:398` FILENAME `verify_quotes.py`
- `wiki/concepts/mirror-consult-economics.md:162` FILENAME `verify_quotes.py`
- `wiki/concepts/mirror-consult-economics.md:184` FILENAME `verify_quotes.py`
- `wiki/references/LAWS-what-a-green-means.md:848` FILENAME `verify_quotes.py`
- `wiki/references/agent-memory/migrations-blind-instruments.md:34` FILENAME `verify_quotes.py`
- `wiki/references/record-architecture-v1.md:117` FILENAME `verify_quotes.py`
- `wiki/references/skills/wiki-master.md:231` FILENAME `verify_quotes.py`
- `wiki/references/update-levels-2026-07-31.md:12` FILENAME `verify_quotes.py`
- `wiki/references/update-levels-2026-07-31.md:258` FULL `scripts/audit/verify_quotes.py`
- `wiki/sources/infrastructure/branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e.md:70` STEM `verify_quotes`
- `wiki/sources/infrastructure/merge-train-instrument-blindness-wayfinder-2026-07-29-627c1e.md:126` FILENAME `verify_quotes.py`
- `wiki/sources/infrastructure/merge-train-instrument-blindness-wayfinder-2026-07-29-627c1e.md:131` FILENAME `verify_quotes.py`

### `skills/cross-venue-intake/SKILL.md` (PATH_EXACT) -- 5 inbound ref(s)

- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:623` FULL `skills/cross-venue-intake/SKILL.md`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:630` FULL `skills/cross-venue-intake/SKILL.md`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:694` FULL `skills/cross-venue-intake/SKILL.md`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:703` FULL `skills/cross-venue-intake/SKILL.md`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:761` FULL `skills/cross-venue-intake/SKILL.md`

### `wiki/concepts/repo-hygiene.md` (PATH_EXACT) -- 12 inbound ref(s)

- `wiki/concepts/bgisolation-membrane.md:64` WIKILINK `[[repo-hygiene`
- `wiki/concepts/fable-mirror.md:102` WIKILINK `[[repo-hygiene`
- `wiki/concepts/transcript-corpus.md:42` WIKILINK `[[repo-hygiene`
- `wiki/concepts/transcript-corpus.md:89` WIKILINK `[[repo-hygiene`
- `wiki/references/agent-memory/derive-dont-record.md:62` FILENAME `repo-hygiene.md`
- `wiki/references/efficiency-rules.md:104` WIKILINK `[[repo-hygiene`
- `wiki/references/records-map.md:21` WIKILINK `[[repo-hygiene`
- `wiki/references/records-map.md:67` FULL `wiki/concepts/repo-hygiene.md`
- `wiki/sources/infrastructure/cfl-video-implementation-planning-2026-07-26-a42d10.md:77` WIKILINK `[[repo-hygiene`
- `wiki/sources/infrastructure/merge-train-instrument-blindness-wayfinder-2026-07-29-627c1e.md:164` WIKILINK `[[repo-hygiene`
- `wiki/sources/infrastructure/wiki-su-pr68-sync-to-g-and-elder-witness-on-canonical-whitelist-2026-07-21-47d61b.md:106` WIKILINK `[[repo-hygiene`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:75` STEM `repo-hygiene`

### `wiki/references/SCOPE-anthropic-zips-read-fence-2026-08-24.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:152` STEM `SCOPE-anthropic-zips-read-fence-2026-08-24`

### `wiki/references/agent-memory/active-work-state.md` (PATH_EXACT) -- 8 inbound ref(s)

- `wiki/references/agent-memory/README.md:155` WIKILINK `[[active-work-state`
- `wiki/references/agent-memory/README.md:210` STEM `active-work-state`
- `wiki/references/agent-memory/decision-grain-one-clause-per-pr.md:33` WIKILINK `[[active-work-state`
- `wiki/references/agent-memory/deploy-phase-operating-protocol.md:37` WIKILINK `[[active-work-state`
- `wiki/references/agent-memory/drive-lag-stale-read-hazard.md:29` WIKILINK `[[active-work-state`
- `wiki/references/agent-memory/planned-path-g1-g2-gate-order.md:35` WIKILINK `[[active-work-state`
- `wiki/references/agent-memory/session-close-2026-07-07-backlog-plan.md:36` WIKILINK `[[active-work-state`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:153` STEM `active-work-state`

### `wiki/references/agent-memory/cc-jsonl-thinking-signature-only.md` (PATH_EXACT) -- 13 inbound ref(s)

- `scripts/claude_api_capture.py:9` STEM `cc-jsonl-thinking-signature-only`
- `skills/session-order/SKILL.md:303` STEM `cc-jsonl-thinking-signature-only`
- `wiki/references/agent-memory/README.md:94` WIKILINK `[[cc-jsonl-thinking-signature-only`
- `wiki/references/agent-memory/live-session-liveness-and-untracked-state.md:30` WIKILINK `[[cc-jsonl-thinking-signature-only`
- `wiki/references/source-schemas.md:17` FULL `wiki/references/agent-memory/cc-jsonl-thinking-signature-only.md`
- `wiki/references/source-schemas.md:309` FULL `wiki/references/agent-memory/cc-jsonl-thinking-signature-only.md`
- `wiki/references/source-schemas.md:322` FILENAME `cc-jsonl-thinking-signature-only.md`
- `wiki/sources/consciousness/blind-self-sitting-memory-on-2026-07-18-48f858.md:68` WIKILINK `[[cc-jsonl-thinking-signature-only`
- `wiki/sources/fbc/fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3.md:52` FILENAME `cc-jsonl-thinking-signature-only.md`
- `wiki/sources/infrastructure/channel-design-and-jon-answers-2026-08-02.md:240` STEM `cc-jsonl-thinking-signature-only`
- `wiki/sources/infrastructure/thinking-tokens-cc-vs-api-legibility-2026-08-12-183fa5.md:83` WIKILINK `[[cc-jsonl-thinking-signature-only`
- `wiki/sources/infrastructure/thinking-tokens-cc-vs-api-legibility-2026-08-12-183fa5.md:101` WIKILINK `[[cc-jsonl-thinking-signature-only`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:161` STEM `cc-jsonl-thinking-signature-only`

### `wiki/references/agent-memory/md-not-uncaptured-authoritative-disposition.md` (PATH_EXACT) -- 13 inbound ref(s)

- `wiki/references/agent-memory/README.md:116` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/askuserquestion-answers-not-captured.md:59` STEM `md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/derive-dont-record.md:93` STEM `md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/fbc-format-gap.md:35` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/flagged-unknowns-are-work.md:59` STEM `md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/live-session-liveness-and-untracked-state.md:43` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/migrations-blind-instruments.md:58` STEM `md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/nightly-lane-leg2-truncated-prompt.md:25` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/references/agent-memory/unshipped-fix-updates-its-own-docs.md:41` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/sources/infrastructure/professional-21st-wake-marker-grep-not-a-detector-2026-08-17-adc56d.md:106` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/sources/infrastructure/professional-fifth-wake-declines-subprocess-read-path-2026-08-17-9ff05b-v2.md:110` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/sources/infrastructure/wiki-master-su-capture-only-2026-07-13-96e1c2.md:103` WIKILINK `[[md-not-uncaptured-authoritative-disposition`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:193` STEM `md-not-uncaptured-authoritative-disposition`

### `wiki/references/agent-memory/verify-conditional-claim-resolution.md` (PATH_EXACT) -- 4 inbound ref(s)

- `wiki/references/agent-memory/README.md:134` WIKILINK `[[verify-conditional-claim-resolution`
- `wiki/references/agent-memory/max-plan-fl-budget.md:29` WIKILINK `[[verify-conditional-claim-resolution`
- `wiki/references/agent-memory/no-public-clone-inside-private-tree.md:34` WIKILINK `[[verify-conditional-claim-resolution`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:223` STEM `verify-conditional-claim-resolution`

### `wiki/references/audit-program-2026-07-13.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:157` STEM `audit-program-2026-07-13`

### `wiki/references/calibration-results-2026-07-13.md` (PATH_EXACT) -- 2 inbound ref(s)

- `wiki/references/README-genre-split.md:39` FILENAME `calibration-results-2026-07-13.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:160` STEM `calibration-results-2026-07-13`

### `wiki/references/corpus-operations-taxonomy.md` (PATH_EXACT) -- 2 inbound ref(s)

- `wiki/references/README-genre-split.md:49` FILENAME `corpus-operations-taxonomy.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:169` STEM `corpus-operations-taxonomy`

### `wiki/references/ingest-queue.md` (PATH_EXACT) -- 13 inbound ref(s)

- `scripts/audit/coverage_gap.py:78` FULL `wiki/references/ingest-queue.md`
- `scripts/audit/coverage_gap.py:171` FULL `wiki/references/ingest-queue.md`
- `wiki/references/README-genre-split.md:48` FILENAME `ingest-queue.md`
- `wiki/references/record-architecture-v1.md:98` STEM `ingest-queue`
- `wiki/references/source-page-standard-v4.md:187` FULL `wiki/references/ingest-queue.md`
- `wiki/references/source-page-standard-v4.md:203` FILENAME `ingest-queue.md`
- `wiki/sources/infrastructure/packet-a-l1-l2-l3-execution-2026-07-18-49a1c0.md:207` FULL `wiki/references/ingest-queue.md`
- `wiki/sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md:23` STEM `ingest-queue`
- `wiki/sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md:94` FULL `wiki/references/ingest-queue.md`
- `wiki/sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md:224` FULL `wiki/references/ingest-queue.md`
- `wiki/sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md:230` FULL `wiki/references/ingest-queue.md`
- `wiki/sources/infrastructure/wiki-su-pr68-sync-to-g-and-elder-witness-on-canonical-whitelist-2026-07-21-47d61b.md:57` FILENAME `ingest-queue.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:187` STEM `ingest-queue`

### `wiki/references/partial-sessions-registry.md` (PATH_EXACT) -- 5 inbound ref(s)

- `skills/wiki-master/SKILL.md:119` FULL `wiki/references/partial-sessions-registry.md`
- `skills/wiki-master/SKILL.md:415` FULL `wiki/references/partial-sessions-registry.md`
- `wiki/references/README-genre-split.md:48` FILENAME `partial-sessions-registry.md`
- `wiki/references/agent-memory/session-close-2026-07-07-backlog-plan.md:34` FILENAME `partial-sessions-registry.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:199` STEM `partial-sessions-registry`

### `wiki/references/pilot-backfill-findings-2026-07-13.md` (PATH_EXACT) -- 2 inbound ref(s)

- `wiki/references/README-genre-split.md:40` FILENAME `pilot-backfill-findings-2026-07-13.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:200` STEM `pilot-backfill-findings-2026-07-13`

### `wiki/references/privacy-default-rule-2026-07-29.md` (PATH_EXACT) -- 6 inbound ref(s)

- `wiki/patterns/exclusion-verified-by-absence-not-by-list.md:31` FULL `wiki/references/privacy-default-rule-2026-07-29.md`
- `wiki/references/update-levels-2026-07-31.md:191` FULL `wiki/references/privacy-default-rule-2026-07-29.md`
- `wiki/references/update-levels-2026-07-31.md:241` FULL `wiki/references/privacy-default-rule-2026-07-29.md`
- `wiki/references/update-levels-2026-07-31.md:267` FULL `wiki/references/privacy-default-rule-2026-07-29.md`
- `wiki/sources/infrastructure/question-pricing-model-and-outcome-tracking-approval-2026-07-27-408368.md:137` FULL `wiki/references/privacy-default-rule-2026-07-29.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:203` STEM `privacy-default-rule-2026-07-29`

### `wiki/sources/ai-governance/ai-oversight-quality-paper-2026-03-09-89c6d7.md` (PATH_EXACT) -- 10 inbound ref(s)

- `wiki/concepts/actuarial-epistemology.md:42` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:8` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:18` WIKILINK `[[ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:33` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:34` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:43` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:45` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:56` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/concepts/ai-governance.md:70` STEM `ai-oversight-quality-paper-2026-03-09-89c6d7`
- `wiki/sources/infrastructure/wiki-master-phase3-subagent-log-2026-06-01-ad8e70.md:59` FULL `wiki/sources/ai-governance/ai-oversight-quality-paper-2026-03-09-89c6d7.md`

### `wiki/sources/infrastructure/coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477.md` (PATH_EXACT) -- 10 inbound ref(s)

- `wiki/concepts/bgisolation-membrane.md:8` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/concepts/coordinator.md:21` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/concepts/coordinator.md:29` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/concepts/coordinator.md:34` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/concepts/coordinator.md:39` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/concepts/coordinator.md:41` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/concepts/fable-mirror.md:8` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/concepts/transcript-corpus.md:8` STEM `coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/sources/infrastructure/deploy-phase-delegation-clause-2026-07-22-turn5.md:28` WIKILINK `[[coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`
- `wiki/sources/infrastructure/misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44.md:131` WIKILINK `[[coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477`

### `wiki/sources/infrastructure/corpus-completeness-audit-2026-07-08.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/sources/infrastructure/fork-test-never-run-and-wiki-md-gap-2026-08-19-910b80.md:126` WIKILINK `[[corpus-completeness-audit-2026-07-08`

### `wiki/sources/infrastructure/fable-mirror-first-extended-deployment-2026-08-01-a4db57.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/references/skills/wiki-master.md:142` SUFFIX `infrastructure/fable-mirror-first-extended-deployment-2026-08-01-a4db57.md`

### `wiki/sources/infrastructure/pm-ds3-verification-backlog-plan-2026-07-10-da51cc.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/sources/infrastructure/packet-a-l1-l2-l3-execution-2026-07-18-49a1c0.md:204` WIKILINK `[[pm-ds3-verification-backlog-plan-2026-07-10-da51cc`

### `wiki/sources/infrastructure/pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont.md` (PATH_EXACT) -- 9 inbound ref(s)

- `wiki/sources/ai-mechanics/tree-search-generation-j-layer-licensing-2026-07-17-5d2f71.md:331` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`
- `wiki/sources/consciousness/blind-self-sitting-incognito-2026-07-18-3ee22d.md:116` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`
- `wiki/sources/consciousness/blind-self-sitting-memory-on-2026-07-18-48f858.md:39` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`
- `wiki/sources/consciousness/blind-self-sitting-memory-on-2026-07-18-48f858.md:128` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`
- `wiki/sources/infrastructure/corpus-remediation-program-design-2026-07-13-ca3309.md:22` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`
- `wiki/sources/infrastructure/corpus-remediation-program-design-2026-07-13-ca3309.md:52` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`
- `wiki/sources/infrastructure/da51cc-continuation-fable-planner-no-go-and-the-0810-resume-2026-08-10-9689d3.md:99` FULL `wiki/sources/infrastructure/pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont.md`
- `wiki/sources/infrastructure/docker-isolation-planner-packet-a-work-order-2026-07-18-a8bbda.md:171` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`
- `wiki/sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md:219` WIKILINK `[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont`

### `wiki/sources/infrastructure/self-improvement-framework-triage-roadmap-2026-07-17-44a95b.md` (PATH_EXACT) -- 4 inbound ref(s)

- `wiki/concepts/heteronomy-horn-pearl-lens.md:33` FULL `wiki/sources/infrastructure/self-improvement-framework-triage-roadmap-2026-07-17-44a95b.md`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:167` FULL `wiki/sources/infrastructure/self-improvement-framework-triage-roadmap-2026-07-17-44a95b.md`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:191` FULL `wiki/sources/infrastructure/self-improvement-framework-triage-roadmap-2026-07-17-44a95b.md`
- `wiki/references/skills/wiki-master.md:169` STEM `self-improvement-framework-triage-roadmap-2026-07-17-44a95b`

### `wiki/sources/infrastructure/triage-project-model-direction-2026-07-11-a3e6cf.md` (PATH_EXACT) -- 2 inbound ref(s)

- `wiki/sources/infrastructure/fusion-multihop-routing-design-2026-08-12-f7b11b.md:51` FILENAME `triage-project-model-direction-2026-07-11-a3e6cf.md`
- `wiki/sources/infrastructure/fusion-multihop-routing-design-2026-08-12-f7b11b.md:139` FILENAME `triage-project-model-direction-2026-07-11-a3e6cf.md`

### `wiki/sources/infrastructure/wiki-master-phase-cycle-2026-07-08-774a3a.md` (PATH_EXACT) -- 2 inbound ref(s)

- `wiki/sources/infrastructure/docker-isolation-planner-packet-a-work-order-2026-07-18-a8bbda.md:80` WIKILINK `[[wiki-master-phase-cycle-2026-07-08-774a3a`
- `wiki/sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md:223` WIKILINK `[[wiki-master-phase-cycle-2026-07-08-774a3a`

### `wiki/sources/reference/cfl-goals-2026-07-08-verbatim.md` (PATH_EXACT) -- 2 inbound ref(s)

- `scripts/audit/find_answer.py:271` FILENAME `cfl-goals-2026-07-08-verbatim.md`
- `scripts/audit/find_answer.py:627` STEM `cfl-goals-2026-07-08-verbatim`

### `.claude/hooks/state/MODE` (PATH_PREFIX) -- 40 inbound ref(s)

- `.claude/hooks/turn-boundary-retrieval.sh:12` FULL `.claude/hooks/state/MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:18` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:20` FULL `.claude/hooks/state/MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:21` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:22` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:24` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:28` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:38` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:39` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:73` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:74` FILENAME `MODE`
- `.claude/hooks/turn-boundary-retrieval.sh:79` FILENAME `MODE`
- `scripts/audit/check_compact_loss.py:83` FILENAME `MODE`
- `scripts/audit/check_compact_loss.py:428` FILENAME `MODE`
- `scripts/audit/exchange_inbox.py:24` FILENAME `MODE`
- `scripts/audit/fbc_decision_log.py:235` FILENAME `MODE`
- `scripts/audit/fbc_decision_log.py:333` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:9` FULL `.claude/hooks/state/MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:29` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:31` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:32` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:33` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:36` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:136` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:138` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:141` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:145` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:149` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:151` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:152` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:154` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:156` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:157` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:159` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:165` FILENAME `MODE`
- `scripts/audit/turn_boundary_wrapper_selftest.py:172` FILENAME `MODE`
- `skills/wikiskills-improve/SKILL.md:204` FILENAME `MODE`
- `wiki/concepts/claude-code-function-hooks.md:98` FILENAME `MODE`
- `wiki/references/constitution/constitution-where-jons-words-live.md:103` FILENAME `MODE`
- `wiki/references/skills/frame-before-commit.md:251` FILENAME `MODE`

### `.claude/hooks/state/post-skills-sync.log` (PATH_PREFIX) -- 1 inbound ref(s)

- `.claude/hooks/post-skills-sync.sh:58` FILENAME `post-skills-sync.log`

### `.claude/hooks/state/pre-stop-consult.log` (PATH_PREFIX) -- 6 inbound ref(s)

- `.claude/hooks/pre-stop-consult.sh:73` FILENAME `pre-stop-consult.log`
- `wiki/patterns/a-logs-first-line-is-the-instruments-sensitivity.md:39` FULL `.claude/hooks/state/pre-stop-consult.log`
- `wiki/patterns/a-logs-first-line-is-the-instruments-sensitivity.md:118` FULL `.claude/hooks/state/pre-stop-consult.log`
- `wiki/patterns/a-shared-aggregate-read-as-a-per-actor-fact.md:100` FILENAME `pre-stop-consult.log`
- `wiki/patterns/a-shared-aggregate-read-as-a-per-actor-fact.md:103` FILENAME `pre-stop-consult.log`
- `wiki/patterns/a-shared-aggregate-read-as-a-per-actor-fact.md:106` FILENAME `pre-stop-consult.log`

### `.claude/hooks/state/prestop-harness-0000-8.count` (PATH_PREFIX) -- 1 inbound ref(s)

- `wiki/patterns/a-shared-aggregate-read-as-a-per-actor-fact.md:97` FILENAME `prestop-harness-0000-8.count`

### `.claude/hooks/state/skills-sync.stamp` (PATH_PREFIX) -- 1 inbound ref(s)

- `.claude/hooks/post-skills-sync.sh:59` FILENAME `skills-sync.stamp`

### `scripts/audit/assign_branch_frontmatter.py` (SCAN) -- 6 inbound ref(s)

- `scripts/audit/normalize_wiki_eol_to_head.py:6` FILENAME `assign_branch_frontmatter.py`
- `scripts/audit/normalize_wiki_eol_to_head.py:18` FILENAME `assign_branch_frontmatter.py`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:10` FILENAME `assign_branch_frontmatter.py`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:78` FULL `scripts/audit/assign_branch_frontmatter.py`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:384` FULL `scripts/audit/assign_branch_frontmatter.py`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:408` FULL `scripts/audit/assign_branch_frontmatter.py`

### `scripts/audit/corpus_index.py` (SCAN) -- 97 inbound ref(s)

- `scripts/audit/fbc_decision_log.py:55` STEM `corpus_index`
- `scripts/audit/fbc_decision_log.py:99` STEM `corpus_index`
- `scripts/audit/fbc_decision_log.py:499` STEM `corpus_index`
- `scripts/audit/fbc_decision_log.py:648` STEM `corpus_index`
- `scripts/audit/fbc_decision_log.py:876` FULL `scripts/audit/corpus_index.py`
- `scripts/audit/find_answer.py:84` FILENAME `corpus_index.py`
- `scripts/audit/find_answer.py:93` FILENAME `corpus_index.py`
- `scripts/audit/find_answer.py:94` FILENAME `corpus_index.py`
- `scripts/audit/find_answer.py:97` STEM `corpus_index`
- `scripts/audit/find_answer.py:99` FILENAME `corpus_index.py`
- `scripts/audit/find_answer.py:110` FILENAME `corpus_index.py`
- `scripts/audit/find_answer.py:399` STEM `corpus_index`
- `scripts/audit/find_answer.py:511` STEM `corpus_index`
- `scripts/audit/gbs_class_forensics.py:56` STEM `corpus_index`
- `scripts/audit/gbs_record.py:15` FULL `scripts/audit/corpus_index.py`
- `scripts/audit/gbs_record.py:19` STEM `corpus_index`
- `scripts/audit/gbs_record.py:27` STEM `corpus_index`
- `scripts/audit/gbs_record.py:29` STEM `corpus_index`
- `scripts/audit/gbs_record.py:43` STEM `corpus_index`
- `scripts/audit/gbs_record.py:56` STEM `corpus_index`
- `scripts/audit/gbs_record.py:64` STEM `corpus_index`
- `scripts/audit/gbs_record.py:102` STEM `corpus_index`
- `scripts/audit/gbs_record.py:369` STEM `corpus_index`
- `scripts/audit/gbs_record.py:382` STEM `corpus_index`
- `scripts/audit/gbs_record.py:385` STEM `corpus_index`
- `scripts/audit/gbs_record.py:387` STEM `corpus_index`
- `scripts/audit/gbs_record.py:388` STEM `corpus_index`
- `scripts/audit/gbs_record.py:440` STEM `corpus_index`
- `scripts/audit/gbs_record.py:516` STEM `corpus_index`
- `scripts/audit/role_history.py:18` FILENAME `corpus_index.py`
- `scripts/audit/role_history.py:87` STEM `corpus_index`
- `scripts/audit/role_history.py:184` STEM `corpus_index`
- `scripts/audit/role_history.py:611` FULL `scripts/audit/corpus_index.py`
- `scripts/audit/skill_record.py:15` FILENAME `corpus_index.py`
- `scripts/audit/skill_record.py:19` STEM `corpus_index`
- `scripts/audit/skill_record.py:34` STEM `corpus_index`
- `scripts/audit/skill_record.py:36` STEM `corpus_index`
- `scripts/audit/skill_record.py:60` STEM `corpus_index`
- `scripts/audit/skill_record.py:95` STEM `corpus_index`
- `scripts/audit/skill_record.py:273` STEM `corpus_index`
- `scripts/audit/skill_record.py:282` STEM `corpus_index`
- `scripts/audit/skill_record.py:283` STEM `corpus_index`
- `scripts/audit/skill_record.py:292` STEM `corpus_index`
- `scripts/audit/skill_record.py:297` FILENAME `corpus_index.py`
- `scripts/audit/skill_record.py:347` STEM `corpus_index`
- `scripts/audit/skill_record.py:473` STEM `corpus_index`
- `scripts/audit/skill_record.py:478` STEM `corpus_index`
- `scripts/audit/skill_record.py:555` STEM `corpus_index`
- `scripts/audit/skill_record.py:562` STEM `corpus_index`
- `scripts/audit/skill_record.py:779` STEM `corpus_index`
- `scripts/audit/skill_record.py:826` FULL `scripts/audit/corpus_index.py`
- `scripts/audit/skill_record_ext.py:9` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:15` FILENAME `corpus_index.py`
- `scripts/audit/skill_record_ext.py:24` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:44` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:98` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:237` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:397` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:1045` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:1056` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:1124` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:1136` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:1338` STEM `corpus_index`
- `scripts/audit/skill_record_ext.py:2071` FULL `scripts/audit/corpus_index.py`
- `wiki/references/skills/frame-before-commit.md:33` FILENAME `corpus_index.py`
- `wiki/references/skills/frame-before-commit.md:95` STEM `corpus_index`
- `wiki/references/skills/frame-before-commit.md:248` STEM `corpus_index`
- `wiki/references/skills/frame-before-commit.md:253` STEM `corpus_index`
- `wiki/references/skills/grill-me.md:37` STEM `corpus_index`
- `wiki/references/skills/grill-me.md:62` STEM `corpus_index`
- `wiki/references/skills/grill-me.md:155` STEM `corpus_index`
- `wiki/references/skills/ground-before-stating.md:64` FILENAME `corpus_index.py`
- `wiki/references/skills/ground-before-stating.md:66` STEM `corpus_index`
- `wiki/references/skills/ground-before-stating.md:75` STEM `corpus_index`
- `wiki/references/skills/ground-before-stating.md:86` STEM `corpus_index`
- `wiki/references/skills/ground-before-stating.md:130` STEM `corpus_index`
- `wiki/references/skills/ground-before-stating.md:262` FULL `scripts/audit/corpus_index.py`
- `wiki/references/skills/ground-before-stating.md:282` FILENAME `corpus_index.py`
- `wiki/references/skills/ground-before-stating.md:323` FILENAME `corpus_index.py`
- `wiki/references/skills/ground-before-stating.md:344` FILENAME `corpus_index.py`
- `wiki/references/skills/ground-before-stating.md:388` FILENAME `corpus_index.py`
- `wiki/references/skills/ground-before-stating.md:400` FULL `scripts/audit/corpus_index.py`
- `wiki/references/skills/handoff.md:56` STEM `corpus_index`
- `wiki/references/skills/session-order.md:63` STEM `corpus_index`
- `wiki/references/skills/session-order.md:305` STEM `corpus_index`
- `wiki/references/skills/temporal-context.md:58` STEM `corpus_index`
- `wiki/references/skills/temporal-context.md:94` STEM `corpus_index`
- `wiki/references/skills/temporal-context.md:96` STEM `corpus_index`
- `wiki/references/skills/temporal-context.md:102` STEM `corpus_index`
- `wiki/references/skills/temporal-context.md:106` STEM `corpus_index`
- `wiki/references/skills/temporal-context.md:271` STEM `corpus_index`
- `wiki/references/skills/temporal-context.md:342` STEM `corpus_index`
- `wiki/references/skills/wayfinder.md:48` FILENAME `corpus_index.py`
- `wiki/references/skills/wayfinder.md:182` STEM `corpus_index`
- `wiki/references/skills/wiki-master.md:62` STEM `corpus_index`
- `wiki/references/skills/wiki-master.md:245` STEM `corpus_index`
- `wiki/references/skills/wiki-master.md:249` STEM `corpus_index`

### `scripts/audit/depii_derive.py` (SCAN) -- 2 inbound ref(s)

- `wiki/concepts/de-pii-deriver.md:3` STEM `depii_derive`
- `wiki/concepts/de-pii-deriver.md:25` FULL `scripts/audit/depii_derive.py`

### `scripts/audit/depii_lexicon.py` (SCAN) -- 18 inbound ref(s)

- `scripts/audit/derive_public_tree.py:28` FULL `scripts/audit/depii_lexicon.py`
- `scripts/audit/derive_public_tree.py:36` STEM `depii_lexicon`
- `scripts/audit/derive_public_tree.py:56` STEM `depii_lexicon`
- `scripts/audit/derive_public_tree.py:300` STEM `depii_lexicon`
- `scripts/audit/derive_public_tree.py:370` STEM `depii_lexicon`
- `scripts/audit/derive_public_tree.py:836` STEM `depii_lexicon`
- `wiki/concepts/de-pii-deriver.md:26` FULL `scripts/audit/depii_lexicon.py`
- `wiki/concepts/de-pii-deriver.md:62` STEM `depii_lexicon`
- `wiki/entities/soul.md:17` FULL `scripts/audit/depii_lexicon.py`
- `wiki/entities/soul.md:26` FULL `scripts/audit/depii_lexicon.py`
- `wiki/references/read-safe-write-fence-v0.md:107` FILENAME `depii_lexicon.py`
- `wiki/references/read-safe-write-fence-v0.md:112` FULL `scripts/audit/depii_lexicon.py`
- `wiki/references/read-safe-write-fence-v0.md:117` FILENAME `depii_lexicon.py`
- `wiki/references/read-safe-write-fence-v0.md:143` STEM `depii_lexicon`
- `wiki/references/read-safe-write-fence-v0.md:251` STEM `depii_lexicon`
- `wiki/references/read-safe-write-fence-v0.md:318` FULL `scripts/audit/depii_lexicon.py`
- `wiki/references/read-safe-write-fence-v0.md:330` STEM `depii_lexicon`
- `wiki/references/read-safe-write-fence-v0.md:331` FILENAME `depii_lexicon.py`

### `scripts/audit/depii_path_canary.py` (SCAN) -- 1 inbound ref(s)

- `wiki/concepts/de-pii-deriver.md:28` FULL `scripts/audit/depii_path_canary.py`

### `scripts/audit/ingest_gate.py` (SCAN) -- 20 inbound ref(s)

- `scripts/audit/derive_public_tree.py:30` FULL `scripts/audit/ingest_gate.py`
- `scripts/audit/derive_public_tree.py:57` STEM `ingest_gate`
- `scripts/audit/derive_public_tree.py:290` STEM `ingest_gate`
- `scripts/audit/derive_public_tree.py:376` STEM `ingest_gate`
- `scripts/audit/derive_public_tree.py:379` STEM `ingest_gate`
- `scripts/audit/derive_public_tree.py:382` STEM `ingest_gate`
- `scripts/tests/selftest_probe_window.py:22` STEM `ingest_gate`
- `scripts/tests/selftest_probe_window.py:55` STEM `ingest_gate`
- `scripts/tests/selftest_probe_window.py:66` STEM `ingest_gate`
- `wiki/patterns/self-citation-moves-the-class.md:64` FILENAME `ingest_gate.py`
- `wiki/references/read-safe-write-fence-v0.md:114` FULL `scripts/audit/ingest_gate.py`
- `wiki/references/read-safe-write-fence-v0.md:272` STEM `ingest_gate`
- `wiki/references/read-safe-write-fence-v0.md:318` FULL `scripts/audit/ingest_gate.py`
- `wiki/references/source-page-contract-v1.md:158` FILENAME `ingest_gate.py`
- `wiki/references/source-page-repair-contract-v1.md:46` FULL `scripts/audit/ingest_gate.py`
- `wiki/references/source-page-repair-contract-v1.md:59` FULL `scripts/audit/ingest_gate.py`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:481` FILENAME `ingest_gate.py`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:1420` FULL `scripts/audit/ingest_gate.py`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:1585` FILENAME `ingest_gate.py`
- `wiki/sources/jon-messages/jon-turns-session-71ce5a0e-2026-09-04.md:1860` FULL `scripts/audit/ingest_gate.py`

### `scripts/audit/leak_control.py` (SCAN) -- 6 inbound ref(s)

- `scripts/audit/derive_public_tree.py:1015` FILENAME `leak_control.py`
- `wiki/patterns/exclusion-verified-by-absence-not-by-list.md:70` FULL `scripts/audit/leak_control.py`
- `wiki/patterns/exclusion-verified-by-absence-not-by-list.md:71` FULL `scripts/audit/leak_control.py`
- `wiki/patterns/exclusion-verified-by-absence-not-by-list.md:74` FULL `scripts/audit/leak_control.py`
- `wiki/patterns/exclusion-verified-by-absence-not-by-list.md:83` FILENAME `leak_control.py`
- `wiki/patterns/exclusion-verified-by-absence-not-by-list.md:92` FILENAME `leak_control.py`

### `scripts/audit/publication_screen.py` (SCAN) -- 4 inbound ref(s)

- `scripts/audit/agent_end_ingest.py:83` FULL `scripts/audit/publication_screen.py`
- `scripts/audit/agent_end_ingest.py:2192` STEM `publication_screen`
- `scripts/audit/agent_end_ingest.py:2193` STEM `publication_screen`
- `scripts/audit/i2_session_page.py:20` FILENAME `publication_screen.py`

### `scripts/audit/publish_content_gate.py` (SCAN) -- 4 inbound ref(s)

- `scripts/audit/check_wiki_path_refs.py:45` FILENAME `publish_content_gate.py`
- `wiki/references/read-safe-write-fence-v0.md:90` FILENAME `publish_content_gate.py`
- `wiki/references/read-safe-write-fence-v0.md:179` FILENAME `publish_content_gate.py`
- `wiki/references/read-safe-write-fence-v0.md:256` FILENAME `publish_content_gate.py`

### `scripts/audit/publish_lexicon.py` (SCAN) -- 2 inbound ref(s)

- `wiki/references/read-safe-write-fence-v0.md:113` FULL `scripts/audit/publish_lexicon.py`
- `wiki/references/read-safe-write-fence-v0.md:319` FULL `scripts/audit/publish_lexicon.py`

### `scripts/audit/write_fence.py` (SCAN) -- 11 inbound ref(s)

- `wiki/references/read-safe-write-fence-v0.md:12` FILENAME `write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:20` FILENAME `write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:21` STEM `write_fence`
- `wiki/references/read-safe-write-fence-v0.md:128` STEM `write_fence`
- `wiki/references/read-safe-write-fence-v0.md:191` FILENAME `write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:199` FULL `scripts/audit/write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:200` FULL `scripts/audit/write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:201` FULL `scripts/audit/write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:215` FULL `scripts/audit/write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:348` FILENAME `write_fence.py`
- `wiki/references/read-safe-write-fence-v0.md:349` FILENAME `write_fence.py`

### `scripts/graphrag/render_history_cc.py` (SCAN) -- 2 inbound ref(s)

- `wiki/references/history-jsonl-retrieval-2026-09-12.md:56` FULL `scripts/graphrag/render_history_cc.py`
- `wiki/references/history-jsonl-retrieval-2026-09-12.md:194` FILENAME `render_history_cc.py`

### `skills/ground-before-stating/references/worked-examples.md` (SCAN) -- 4 inbound ref(s)

- `skills/ground-before-stating/SKILL.md:401` SUFFIX `references/worked-examples.md`
- `skills/ground-before-stating/SKILL.md:694` SUFFIX `references/worked-examples.md`
- `wiki/concepts/meta-pm-framework.md:83` SUFFIX `references/worked-examples.md`
- `wiki/sources/infrastructure/meta-pm-layer-architecture-2026-06-27-a13169.md:42` SUFFIX `references/worked-examples.md`

### `skills/herald/SKILL.md` (SCAN) -- 4 inbound ref(s)

- `scripts/audit/lint_skills.py:23` SUFFIX `herald/SKILL.md`
- `wiki/references/agent-memory/pm-herald-skill-state.md:35` FULL `skills/herald/SKILL.md`
- `wiki/references/agent-memory/pm-herald-skill-state.md:56` FULL `skills/herald/SKILL.md`
- `wiki/sources/infrastructure/jon-turn8-fbcfork-skilldefects-canonical-nightly-docker-gate-2026-07-26.md:63` SUFFIX `herald/SKILL.md`

### `wiki/concepts/herald-of-home-and-life.md` (SCAN) -- 15 inbound ref(s)

- `wiki/concepts/life-domains.md:62` WIKILINK `[[herald-of-home-and-life`
- `wiki/concepts/meta-pm-framework.md:91` WIKILINK `[[herald-of-home-and-life`
- `wiki/concepts/multi-agent-orchestration.md:159` WIKILINK `[[herald-of-home-and-life`
- `wiki/concepts/understand-anything.md:68` WIKILINK `[[herald-of-home-and-life`
- `wiki/entities/herald.md:13` STEM `herald-of-home-and-life`
- `wiki/entities/herald.md:16` FULL `wiki/concepts/herald-of-home-and-life.md`
- `wiki/entities/herald.md:49` WIKILINK `[[herald-of-home-and-life`
- `wiki/patterns/name-matched-as-location.md:28` FULL `wiki/concepts/herald-of-home-and-life.md`
- `wiki/sources/infrastructure/goals-file-herald-goal-writing-2026-07-09-c4e44f.md:29` WIKILINK `[[herald-of-home-and-life`
- `wiki/sources/infrastructure/herald-skill-execute-2026-05-28-6bc1d2.md:33` WIKILINK `[[herald-of-home-and-life`
- `wiki/sources/infrastructure/meta-pm-layer-architecture-2026-06-27-a13169.md:50` WIKILINK `[[herald-of-home-and-life`
- `wiki/sources/infrastructure/project-manager-architecture-2026-04-30-f8cc02-cont.md:34` WIKILINK `[[herald-of-home-and-life`
- `wiki/sources/infrastructure/skills-master-intake-grill-2026-05-27-e52ed2.md:35` WIKILINK `[[herald-of-home-and-life`
- `wiki/sources/infrastructure/wiki-master-cc-phase3e-concept-gaps-2026-06-04-125957.md:17` STEM `herald-of-home-and-life`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:62` STEM `herald-of-home-and-life`

### `wiki/concepts/personal-role-architecture.md` (SCAN) -- 9 inbound ref(s)

- `wiki/concepts/life-domains.md:54` WIKILINK `[[personal-role-architecture`
- `wiki/concepts/life-domains.md:62` WIKILINK `[[personal-role-architecture`
- `wiki/concepts/meta-pm-framework.md:91` WIKILINK `[[personal-role-architecture`
- `wiki/patterns/name-matched-as-location.md:16` FULL `wiki/concepts/personal-role-architecture.md`
- `wiki/patterns/name-matched-as-location.md:28` FULL `wiki/concepts/personal-role-architecture.md`
- `wiki/sources/infrastructure/meta-pm-layer-architecture-2026-06-27-a13169.md:50` WIKILINK `[[personal-role-architecture`
- `wiki/sources/infrastructure/project-manager-architecture-2026-04-30-f8cc02-cont.md:34` WIKILINK `[[personal-role-architecture`
- `wiki/sources/infrastructure/wiki-master-cc-phase3e-concept-gaps-2026-06-04-125957.md:17` STEM `personal-role-architecture`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:72` STEM `personal-role-architecture`

### `wiki/concepts/probe-registry.md` (SCAN) -- 130 inbound ref(s)

- `scripts/audit/check_source_schema_drift.py:11` STEM `probe-registry`
- `scripts/audit/heartbeat_battery.py:66` STEM `probe-registry`
- `scripts/audit/heartbeat_battery.py:250` STEM `probe-registry`
- `scripts/audit/heartbeat_battery.py:252` STEM `probe-registry`
- `scripts/audit/heartbeat_battery.py:656` STEM `probe-registry`
- `skills/loom/SKILL.md:53` STEM `probe-registry`
- `skills/probe-registry/PURPOSE.md:3` STEM `probe-registry`
- `skills/probe-registry/SKILL.md:2` STEM `probe-registry`
- `skills/probe-registry/SKILL.md:12` STEM `probe-registry`
- `skills/probe-registry/SKILL.md:106` STEM `probe-registry`
- `skills/wikiskills-improve/SKILL.md:525` STEM `probe-registry`
- `wiki/concepts/claude-code-hooks-v2.md:14` WIKILINK `[[probe-registry`
- `wiki/concepts/disposition-and-delivered-is-not-received.md:38` WIKILINK `[[probe-registry`
- `wiki/concepts/disposition-and-delivered-is-not-received.md:93` WIKILINK `[[probe-registry`
- `wiki/concepts/disposition-rate.md:91` WIKILINK `[[probe-registry`
- `wiki/concepts/disposition-rate.md:99` WIKILINK `[[probe-registry`
- `wiki/concepts/graphrag-retrieval.md:124` WIKILINK `[[probe-registry`
- `wiki/concepts/graphrag-retrieval.md:130` WIKILINK `[[probe-registry`
- `wiki/concepts/graphrag-retrieval.md:134` WIKILINK `[[probe-registry`
- `wiki/concepts/memory-core.md:102` WIKILINK `[[probe-registry`
- `wiki/concepts/supersession-and-old-rules-outranking-amendments.md:25` WIKILINK `[[probe-registry`
- `wiki/concepts/supersession-and-old-rules-outranking-amendments.md:82` WIKILINK `[[probe-registry`
- `wiki/concepts/unsaid-ledger.md:38` WIKILINK `[[probe-registry`
- `wiki/patterns/a-negative-fixture-should-say-something-when-it-wrongly-succeeds.md:71` STEM `probe-registry`
- `wiki/patterns/three-runtimes-two-faults.md:67` STEM `probe-registry`
- `wiki/references/jon-control-surface.md:38` STEM `probe-registry`
- `wiki/references/records-map.md:21` WIKILINK `[[probe-registry`
- `wiki/references/records-map.md:51` FULL `wiki/concepts/probe-registry.md`
- `wiki/references/records-map.md:52` FULL `wiki/concepts/probe-registry.md`
- `wiki/references/source-page-contract-v1.md:147` WIKILINK `[[probe-registry`
- `wiki/references/source-schemas.md:348` STEM `probe-registry`
- `wiki/skills-gate/skill-impact.md:34` STEM `probe-registry`
- `wiki/sources/ai-governance/difficult-conversation-test-2026-05-20-047dc1.md:75` WIKILINK `[[probe-registry`
- `wiki/sources/ai-governance/drug-safety-teenager-test-2026-05-22-5a339a.md:74` WIKILINK `[[probe-registry`
- `wiki/sources/ai-governance/drug-safety-teenager-test-2026-05-22-65d155.md:69` WIKILINK `[[probe-registry`
- `wiki/sources/ai-governance/drug-safety-teenager-test-2026-05-22-733f9c.md:63` WIKILINK `[[probe-registry`
- `wiki/sources/ai-governance/nazi-propaganda-scene-test-2026-05-22-88a744.md:70` WIKILINK `[[probe-registry`
- `wiki/sources/ai-governance/nazi-propaganda-scene-test-2026-05-22-f057db.md:63` WIKILINK `[[probe-registry`
- `wiki/sources/ai-governance/nazi-propaganda-scene-test-2026-05-22-f509f3.md:63` WIKILINK `[[probe-registry`
- `wiki/sources/consciousness/sleep-identity-ai-compaction-analogy-2026-07-25-9f61ec.md:156` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/branch-chain-verifier-continuity-and-gate-vector-2026-08-22-67214b.md:165` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2.md:111` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/cfl-sensitivity-clause-ears-protocol-2026-08-07-263e3e.md:102` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/cfl-sensitivity-clause-plain-reading-2026-08-07-4b4964.md:102` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/cfl-sensitivity-clause-plain-reading-causation-2026-08-07-527e9a.md:101` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/cfl-wake-d11-d13-verified-and-hall-entries-never-reached-spine-2026-08-17-33cbc0.md:101` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/checkpoint-critic-lost-jon-words-soul-dispatch-2026-08-17-5b89d4.md:115` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/compact-brief-mismatch-reverify-professional-2026-08-17-f13122.md:107` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/d15-attribution-correction-p6-escalation-2026-08-17-5992e8.md:108` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/draft-letter-adversarial-review-branch-axes-2026-08-22-10a453.md:22` STEM `probe-registry`
- `wiki/sources/infrastructure/draft-letter-adversarial-review-branch-axes-2026-08-22-10a453.md:135` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/draft-letter-adversarial-review-branch-axes-2026-08-22-10a453.md:141` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/ds3-meta-wiki-reorganization-lint-verification-2026-08-07-15018d.md:88` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/em-dash-output-test-then-memory-only-recall-check-2026-08-07-bfc2f6.md:64` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/fable-letter-gate-branching-geometry-2026-08-22-01c3b6.md:131` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/fourth-attempt-fragment-ears-protocol-2026-08-07-33b629.md:97` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/harness-cron-pong-probe-2026-08-30-4f7e40.md:45` STEM `probe-registry`
- `wiki/sources/infrastructure/harness-cron-pong-probe-2026-08-30-709843.md:40` STEM `probe-registry`
- `wiki/sources/infrastructure/harness-cron-pong-probe-2026-08-30-7971a0.md:40` STEM `probe-registry`
- `wiki/sources/infrastructure/headless-probe-alive-2026-08-23-1e89b8.md:42` STEM `probe-registry`
- `wiki/sources/infrastructure/headless-probe-cwd-branch-2026-08-23-c42649.md:43` STEM `probe-registry`
- `wiki/sources/infrastructure/headless-probe-cwd-wiki-count-2026-08-23-7fcb8c.md:45` STEM `probe-registry`
- `wiki/sources/infrastructure/headless-probe-cwd-wiki-count-2026-08-23-7fcb8c.md:46` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614.md:101` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/hold-flag-secretary-wake-target-mismatch-2026-08-17-444444.md:82` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/lightweaver-ideals-radiant-frame-conditioning-2026-08-05-c4a242.md:104` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/loop-taxonomy-graph-and-l-model-conflict-2026-08-13-26e0d2.md:66` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/loop-taxonomy-graph-and-l-model-conflict-2026-08-13-26e0d2.md:82` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/misalignment-taxonomy-bandaid-to-broad-rule-2026-08-16-d98b98.md:132` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44.md:129` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/overnight-briefing-seal-decisions-2026-08-22-442d2e.md:21` STEM `probe-registry`
- `wiki/sources/infrastructure/overnight-briefing-seal-decisions-2026-08-22-442d2e.md:83` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/parallel-processing-with-sound-interrupts-branch-forking-design-2026-08-10-a714b7.md:114` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc.md:76` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/personal-coordinator-self-generated-wake-2026-08-17-471635.md:164` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/personal-git-denied-five-refusal-classes-2026-08-17-f5e01b.md:107` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c.md:110` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/personal-jon-ruling-herald-coordinates-xc-work-2026-08-17-6f51c0.md:103` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/pr1-promise-retrospective-2026-08-23.md:66` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/professional-all-hands-slate-and-compact-live-proven-2026-08-15-bb5dd0.md:132` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7.md:97` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/professional-fifth-wake-declines-subprocess-read-path-2026-08-17-6475ba.md:109` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b.md:107` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/professional-test-probe-wake-current-2026-08-16-caf0c9.md:72` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/professional-wake-w1-letter-byte-gate-breach-2026-08-17-e9cfa3.md:114` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-brief-pulse-token-diagnosis-critic-2026-08-17-d2b825.md:130` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-brief-silence-rots-critic-2026-08-17-e72c4b.md:120` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-brief-sync-universal-scope-critic-2026-08-17-d9c6fa.md:118` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-checkpoint-critic-model-advisory-2026-08-15-288a33.md:171` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-day-one-arm-proof-inference-fork-2026-08-15-ec3d2d.md:67` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-day-one-mle-reliance-fork-2026-08-15-bd3b71.md:67` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-day-one-pit-resurrection-test-2026-08-15-f4534c.md:66` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-day-one-self-branching-test-2026-08-15-865b9b.md:81` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-day-one-trunk-session-self-branching-ruling-2026-08-15-68a4bd.md:135` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-day-one-wiki-continuity-fold-2026-08-15-9e8dff.md:64` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060.md:118` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-relaunch-prep-relay-ownership-critic-2026-08-17-d942c5.md:123` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-relaunch-prep-switchboard-cmd-ears-critic-2026-08-17-ebcdb7.md:111` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-self-branching-compact-test-2026-08-16-6d0401.md:144` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-self-branching-compact-test-2026-08-16-6d0401.md:150` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-self-branching-compact-test-2026-08-16-a8cc66.md:107` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-self-branching-compact-test-2026-08-16-a8cc66.md:113` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-switchboard-day-precompact-critic-fork-2026-08-18-1b90e4.md:78` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80.md:134` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-switchboard-relaunch-2026-08-17-3d1a99.md:133` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-switchboard-restart-discipline-and-ledger-ears-gaps-2026-08-17-ca0248.md:156` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/secretary-wayfinder-capability-registry-and-time-warp-charter-2026-08-24-9b28b8.md:118` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5.md:111` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/soul-lineage-inheritance-and-row-10-correction-2026-08-22-c38265.md:125` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/soul-seat-graphrag-test-branch-prototype-and-open-rulings-2026-08-19-42ee61.md:115` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/soul-seat-wiki-defect-and-fork-test-never-run-2026-08-19-910b80.md:150` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-continuity-single-point-of-failure-secretary-2026-08-17-fbf416.md:99` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-first-fix-cycle-and-critic-cost-finding-2026-08-17-09ae91.md:131` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-operator-addressee-mismatch-flag-2026-08-17-f5543a.md:85` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-operator-deliver-cfl-jon-order-2026-08-17-cda7eb.md:103` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-operator-deliver-professional-mail-2026-08-17-cc5bb5.md:92` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-operator-v1-drift-d6-d10-dispositions-2026-08-17-536b7f.md:118` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372.md:110` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e.md:104` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65.md:97` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/switchboard-wake-universal-split-merge-and-verifier-accept-2026-08-17-032a48.md:97` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/token-ledger-denominator-retraction-grep-refusal-classes-2026-08-17-558dc0.md:110` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/townhall-switchboard-postmortem-2026-08-17-506255.md:140` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/unseen-approval-gate-closure-2026-08-07-1dc6d3.md:93` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/wake-cfl-coordinator-b4-review-verdict-disposition-2026-08-17-7d03a8.md:92` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/wiki-unnavigable-organization-clause-ears-protocol-2026-08-07-415d8d.md:101` WIKILINK `[[probe-registry`
- `wiki/sources/infrastructure/xc-questions-never-posed-silence-defaults-2026-08-16-081198.md:156` WIKILINK `[[probe-registry`
- `wiki/sources/stylomantic/stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351.md:183` WIKILINK `[[probe-registry`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:73` STEM `probe-registry`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:125` STEM `probe-registry`

### `wiki/entities/claude-code.md` (SCAN) -- 180 inbound ref(s)

- `scripts/audit/_su_close_summaries.py:53` STEM `claude-code`
- `scripts/audit/_su_close_summaries.py:128` STEM `claude-code`
- `scripts/audit/absence_claims.py:191` STEM `claude-code`
- `scripts/audit/absence_claims.py:455` STEM `claude-code`
- `scripts/audit/agent_end_ingest.py:2317` STEM `claude-code`
- `scripts/audit/auto_mint_windows.py:39` STEM `claude-code`
- `scripts/audit/cc_corpus_gap.py:263` STEM `claude-code`
- `scripts/audit/cc_corpus_gap.py:551` STEM `claude-code`
- `scripts/audit/cc_corpus_gap.py:573` STEM `claude-code`
- `scripts/audit/coverage_census.py:13` STEM `claude-code`
- `scripts/audit/coverage_census.py:101` STEM `claude-code`
- `scripts/audit/coverage_census.py:153` STEM `claude-code`
- `scripts/audit/coverage_census.py:154` STEM `claude-code`
- `scripts/audit/extract_compact_summary.py:60` STEM `claude-code`
- `scripts/audit/feed_liveness.py:29` STEM `claude-code`
- `scripts/audit/feed_liveness.py:78` STEM `claude-code`
- `scripts/audit/postcompact_pipeline.py:591` STEM `claude-code`
- `scripts/audit/postcompact_verify.py:104` STEM `claude-code`
- `scripts/audit/render_freshness_check.py:22` STEM `claude-code`
- `scripts/audit/render_gap.py:35` STEM `claude-code`
- `scripts/audit/render_gap.py:36` STEM `claude-code`
- `scripts/audit/role_history.py:222` STEM `claude-code`
- `scripts/audit/role_history.py:227` STEM `claude-code`
- `scripts/audit/role_history.py:662` STEM `claude-code`
- `scripts/audit/scan_midturn_messages.py:48` STEM `claude-code`
- `scripts/audit/session_in_graph.py:232` STEM `claude-code`
- `scripts/audit/session_in_graph.py:233` STEM `claude-code`
- `scripts/audit/wake_map.py:218` STEM `claude-code`
- `scripts/audit/wikiskills_prototype_render.py:104` STEM `claude-code`
- `scripts/audit/wikiskills_prototype_render.py:175` STEM `claude-code`
- `scripts/barrier_session_identity.py:152` STEM `claude-code`
- `scripts/extract_claude_code_sessions.py:148` STEM `claude-code`
- `scripts/extract_claude_code_sessions.py:1084` STEM `claude-code`
- `scripts/extract_claude_code_sessions.py:1095` STEM `claude-code`
- `scripts/raw_tracking_pass.py:101` STEM `claude-code`
- `scripts/raw_tracking_pass.py:111` STEM `claude-code`
- `scripts/raw_tracking_pass.py:146` STEM `claude-code`
- `scripts/raw_tracking_pass.py:147` STEM `claude-code`
- `scripts/raw_tracking_pass.py:148` STEM `claude-code`
- `scripts/raw_tracking_pass.py:149` STEM `claude-code`
- `scripts/reconstruct_session.py:682` STEM `claude-code`
- `scripts/reconstruct_session.py:685` STEM `claude-code`
- `scripts/session_identity.py:142` STEM `claude-code`
- `scripts/tests/selftest_probe_window.py:35` STEM `claude-code`
- `skills/session-order/SKILL.md:303` STEM `claude-code`
- `skills/transcript-parser/SKILL.md:55` STEM `claude-code`
- `skills/wiki-master/SKILL.md:93` STEM `claude-code`
- `skills/wikiskills-improve/SKILL.md:446` STEM `claude-code`
- `wiki/WIKISKILLS-PROTOTYPE.md:44` STEM `claude-code`
- `wiki/concepts/claude-code-function-hooks.md:8` STEM `claude-code`
- `wiki/concepts/claude-code-function-hooks.md:11` WIKILINK `[[claude-code`
- `wiki/concepts/claude-code-hooks-and-agent-engine.md:8` STEM `claude-code`
- `wiki/concepts/claude-code-hooks-v2.md:8` STEM `claude-code`
- `wiki/concepts/claude-code-hooks-v2.md:11` WIKILINK `[[claude-code`
- `wiki/concepts/claude-code-hooks-v2.md:103` WIKILINK `[[claude-code`
- `wiki/concepts/transcript-corpus.md:29` STEM `claude-code`
- `wiki/patterns/count-verified-mirror-hides-zero-byte-shells.md:16` STEM `claude-code`
- `wiki/patterns/count-verified-mirror-hides-zero-byte-shells.md:27` STEM `claude-code`
- `wiki/patterns/first-run-numbers-are-hypotheses.md:34` STEM `claude-code`
- `wiki/references/claude-code/FINDING-postcompact-and-sessionstart-both-fire-on-a-compact-2026-09-04.md:3` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:1170` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:3954` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4642` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4645` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4887` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4895` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4896` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4898` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4904` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4907` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4909` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4910` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4911` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4912` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4913` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4914` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4915` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4916` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4917` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4918` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4919` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4920` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4921` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4922` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4923` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4924` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4925` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4926` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4927` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4928` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4929` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4930` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4931` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4932` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4933` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4934` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4935` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4936` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4937` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4938` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4939` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4940` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4941` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4942` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4943` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4944` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4945` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4946` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4947` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4948` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4949` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4963` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4964` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:4965` STEM `claude-code`
- `wiki/references/claude-code/changelog.md:6408` STEM `claude-code`
- `wiki/references/claude-code/workflows.md:440` STEM `claude-code`
- `wiki/references/efficiency-rules.md:11` STEM `claude-code`
- `wiki/references/raw-file-standards.md:28` STEM `claude-code`
- `wiki/references/raw-file-standards.md:89` STEM `claude-code`
- `wiki/references/record-architecture-v1.md:71` STEM `claude-code`
- `wiki/references/skills/ground-before-stating.md:42` STEM `claude-code`
- `wiki/sources/infrastructure/UNCERTAIN-cfl-early-setup-2026-05-01-000a36.md:11` STEM `claude-code`
- `wiki/sources/infrastructure/UNCERTAIN-claude-code-interface-2026-03-11-f2af18.md:12` STEM `claude-code`
- `wiki/sources/infrastructure/cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/cfl-222222-memory-probe-fixture-alpha-stored-beta-unknown-2026-08-19.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/cfl-inbound-triage-interrupted-before-disposition-2026-08-18-f4cfd0.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc.md:12` STEM `claude-code`
- `wiki/sources/infrastructure/cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/cfl-model-command-set-to-fable-5-local-command-caveat-2026-08-08-9a9bb9.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/channel-design-and-jon-answers-2026-08-02.md:226` STEM `claude-code`
- `wiki/sources/infrastructure/claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5.md:25` STEM `claude-code`
- `wiki/sources/infrastructure/coordination-resume-plan-2026-08-02.md:68` STEM `claude-code`
- `wiki/sources/infrastructure/disk-g-standing-rule-interpretation-test-2026-08-07-6b6114.md:29` STEM `claude-code`
- `wiki/sources/infrastructure/ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1.md:29` STEM `claude-code`
- `wiki/sources/infrastructure/ears-protocol-position-changes-heading-test-2026-08-07-746694.md:31` STEM `claude-code`
- `wiki/sources/infrastructure/ears-protocol-tabernacle-praise-misread-test-2026-08-07-81fd72.md:29` STEM `claude-code`
- `wiki/sources/infrastructure/effort-slash-command-sets-medium-2026-08-05-3762d6.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/elder-consult-predecessor-systems-pre-stop-consult-wake-stale-2026-08-07-d24142.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/em-dash-output-test-then-memory-only-recall-check-2026-08-07-bfc2f6.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/fourth-attempt-signal-dropped-interpretation-test-2026-08-07-807624.md:29` STEM `claude-code`
- `wiki/sources/infrastructure/hold-flag-secretary-routing-probe-fork-b-2026-08-17-666666.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/hold-flag-secretary-routing-probe-fork-ok-2026-08-17-555555.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/login-slash-command-then-interrupted-test-probe-2026-08-08-aaf4f2.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/login-slash-command-then-interrupted-test-probe-b-2026-08-08-63f758.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/model-slash-command-sets-fable-5-then-recalled-2026-08-08-777777.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/model-slash-command-sonnet-then-opus-2026-08-02-104f69.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/personal-coordinator-self-generated-wake-2026-08-17-471635.md:35` STEM `claude-code`
- `wiki/sources/infrastructure/personal-notes-fair-game-interpretation-test-2026-08-07-5fe6f4.md:29` STEM `claude-code`
- `wiki/sources/infrastructure/personal-read-grant-ticket-interpretation-test-2026-08-07-5add38.md:30` STEM `claude-code`
- `wiki/sources/infrastructure/personal-read-grant-ticket-interpretation-test-2026-08-07-5e5856.md:30` STEM `claude-code`
- `wiki/sources/infrastructure/reply-ok-probe-then-pre-stop-consult-not-attempting-stop-2026-08-06-4bf964.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/reply-ok-probe-then-pre-stop-consult-remains-open-2026-08-06-be7d2a.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/secretary-branching-forkpoint-haiku-contract-2026-08-17-becc33.md:156` STEM `claude-code`
- `wiki/sources/infrastructure/secretary-capability-registry-fog-measurement-contamination-2026-08-24-b5f5bb.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/security-permission-plan-2026-07-03.md:10` STEM `claude-code`
- `wiki/sources/infrastructure/session-open-gbs-fbc-alignment-2026-07-07-883667.md:11` STEM `claude-code`
- `wiki/sources/infrastructure/skills-master-wiki-pipeline-2026-05-01-bcafba.md:13` STEM `claude-code`
- `wiki/sources/infrastructure/smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/sonnet-consent-refusal-entity-launch-two-trees-2026-08-10-771a92.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-deliver-cfl-herald-review-verdict-b4-0810-2026-08-17-3c19b9.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-deliver-cfl-jon-order-model-policy-fable-scarce-2026-08-17-3e732c.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-deliver-personal-cfl-grade-secretary-probes-2026-08-17-2b6b21.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-deliver-personal-d17-reviewed-front-door-unguarded-2026-08-17-2ec2b3.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-deliver-professional-jon-order-model-policy-fable-scarce-2026-08-17-953012.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-deliver-professional-soul-compact-brief-false-positive-2026-08-17-fc0c94.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-deliver-professional-w1-review-closed-wake-cap-2026-08-17-897e4b.md:19` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-operator-charter-jon-quote-deliver-visibility-fix-2026-08-17-534f41.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-operator-deliver-jon-order-model-policy-personal-2026-08-17-467fcc.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-operator-retired-rollback-addressee-defect-notify-jon-zero-2026-08-18-fd9ad2.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/switchboard-wake-universal-split-merge-and-verifier-accept-2026-08-17-032a48.md:58` STEM `claude-code`
- `wiki/sources/infrastructure/tabernacle-praise-misread-interpretation-test-2026-08-07-5c62d0.md:29` STEM `claude-code`
- `wiki/sources/infrastructure/thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92.md:17` STEM `claude-code`
- `wiki/sources/infrastructure/thinking-tokens-cc-vs-api-legibility-2026-08-12-183fa5.md:23` STEM `claude-code`
- `wiki/sources/infrastructure/thinking-tokens-cc-vs-api-legibility-2026-08-12-183fa5.md:64` STEM `claude-code`
- `wiki/sources/infrastructure/thinking-tokens-cc-vs-api-legibility-2026-08-12-183fa5.md:85` STEM `claude-code`
- `wiki/sources/infrastructure/wiki-master-su-capture-only-2026-07-13-96e1c2.md:21` STEM `claude-code`

### `wiki/entities/jon.md` (SCAN) -- 1 inbound ref(s)

- `scripts/audit/normalize_wiki_eol_to_head.py:11` SUFFIX `entities/jon.md`

### `wiki/index.md` (SCAN) -- 120 inbound ref(s)

- `.claude/hooks/tests/test_fable_mirror_write_fence.sh:60` FULL `wiki/index.md`
- `.claude/hooks/tests/test_fable_mirror_write_fence.sh:61` FULL `wiki/index.md`
- `.claude/hooks/tests/test_fable_mirror_write_fence.sh:87` FULL `wiki/index.md`
- `.claude/hooks/tests/test_fable_mirror_write_fence.sh:103` FULL `wiki/index.md`
- `scripts/anti_decoy_resolver.py:9` FULL `wiki/index.md`
- `scripts/anti_decoy_resolver.py:31` FULL `wiki/index.md`
- `scripts/anti_decoy_resolver.py:63` FULL `wiki/index.md`
- `scripts/anti_decoy_resolver.py:122` FULL `wiki/index.md`
- `scripts/audit/agent_end_ingest.py:1367` FULL `wiki/index.md`
- `scripts/audit/check_reachability_chain.py:54` FULL `wiki/index.md`
- `scripts/audit/check_reachability_chain.py:81` FULL `wiki/index.md`
- `scripts/audit/check_reachability_chain.py:264` FULL `wiki/index.md`
- `scripts/audit/check_reachability_chain.py:370` FULL `wiki/index.md`
- `scripts/audit/check_secondary_attribution.py:27` FULL `wiki/index.md`
- `scripts/audit/check_wiki_path_refs.py:116` FULL `wiki/index.md`
- `scripts/audit/check_wiki_path_refs.py:292` FULL `wiki/index.md`
- `scripts/audit/check_wiki_path_refs.py:302` FULL `wiki/index.md`
- `scripts/audit/drain_routing_ledger.py:326` FULL `wiki/index.md`
- `scripts/audit/drain_routing_ledger.py:364` FULL `wiki/index.md`
- `scripts/audit/find_resurrection_candidates.py:71` FULL `wiki/index.md`
- `scripts/audit/gbs_class_forensics.py:318` FULL `wiki/index.md`
- `scripts/audit/index_counts.py:75` FULL `wiki/index.md`
- `scripts/audit/index_counts.py:105` FULL `wiki/index.md`
- `scripts/audit/index_counts.py:111` FULL `wiki/index.md`
- `scripts/audit/index_counts.py:129` FULL `wiki/index.md`
- `scripts/audit/index_coverage.py:100` FULL `wiki/index.md`
- `scripts/audit/index_coverage.py:186` FULL `wiki/index.md`
- `scripts/audit/index_coverage.py:196` FULL `wiki/index.md`
- `scripts/audit/index_coverage.py:205` FULL `wiki/index.md`
- `scripts/audit/lint_shipped_coverage.py:4` FULL `wiki/index.md`
- `scripts/audit/lint_shipped_coverage.py:47` FULL `wiki/index.md`
- `scripts/audit/lint_shipped_coverage.py:81` FULL `wiki/index.md`
- `scripts/audit/lint_skills.py:144` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:2` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:8` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:14` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:18` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:22` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:36` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:76` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:99` FULL `wiki/index.md`
- `scripts/audit/regen_index_sections.py:142` FULL `wiki/index.md`
- `scripts/audit/wiki_reachability.py:6` FULL `wiki/index.md`
- `scripts/audit/wiki_reachability.py:36` FULL `wiki/index.md`
- `scripts/audit/wiki_reachability.py:111` FULL `wiki/index.md`
- `scripts/audit/wikiskills_prototype_render.py:325` FULL `wiki/index.md`
- `scripts/audit/wikiskills_prototype_render.py:329` FULL `wiki/index.md`
- `scripts/lint_citation_coverage.py:68` FULL `wiki/index.md`
- `scripts/lint_untracked_wiki.py:5` FULL `wiki/index.md`
- `scripts/lint_untracked_wiki.py:34` FULL `wiki/index.md`
- `scripts/lint_untracked_wiki.py:103` FULL `wiki/index.md`
- `scripts/ollama_wiki/wiki_agent.py:468` FULL `wiki/index.md`
- `skills/project-manager/SKILL.md:60` FULL `wiki/index.md`
- `skills/project-manager/SKILL.md:90` FULL `wiki/index.md`
- `skills/project-manager/SKILL.md:290` FULL `wiki/index.md`
- `skills/session-order/SKILL.md:16` FULL `wiki/index.md`
- `skills/session-order/SKILL.md:66` FULL `wiki/index.md`
- `skills/session-order/SKILL.md:96` FULL `wiki/index.md`
- `skills/session-order/SKILL.md:219` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:138` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:180` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:304` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:327` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:348` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:522` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:548` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:591` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:913` FULL `wiki/index.md`
- `skills/wiki-master/SKILL.md:923` FULL `wiki/index.md`
- `wiki/WIKISKILLS-PROTOTYPE.md:69` FULL `wiki/index.md`
- `wiki/WIKISKILLS-PROTOTYPE.md:70` FULL `wiki/index.md`
- `wiki/WIKISKILLS-PROTOTYPE.md:71` FULL `wiki/index.md`
- `wiki/WIKISKILLS-PROTOTYPE.md:124` FULL `wiki/index.md`
- `wiki/WIKISKILLS-PROTOTYPE.md:125` FULL `wiki/index.md`
- `wiki/WIKISKILLS-PROTOTYPE.md:126` FULL `wiki/index.md`
- `wiki/concepts/disposition-and-delivered-is-not-received.md:68` FULL `wiki/index.md`
- `wiki/concepts/understand-anything.md:56` FULL `wiki/index.md`
- `wiki/concepts/words-reify.md:45` FULL `wiki/index.md`
- `wiki/entities/exchequer.md:32` FULL `wiki/index.md`
- `wiki/references/LAWS-what-a-green-means.md:940` FULL `wiki/index.md`
- `wiki/references/agent-memory/hedge-flattening-and-invented-rulings.md:28` FULL `wiki/index.md`
- `wiki/references/constitution/constitution-stale-lines-retired.md:22` FULL `wiki/index.md`
- `wiki/references/constitution/constitution-stale-lines-retired.md:24` FULL `wiki/index.md`
- `wiki/references/growth-intent-worked-examples/README.md:342` FULL `wiki/index.md`
- `wiki/references/raw-file-standards.md:296` FULL `wiki/index.md`
- `wiki/references/records-map.md:40` FULL `wiki/index.md`
- `wiki/references/records-map.md:50` FULL `wiki/index.md`
- `wiki/references/records-map.md:112` FULL `wiki/index.md`
- `wiki/references/records-map.md:143` FULL `wiki/index.md`
- `wiki/references/records-map.md:144` FULL `wiki/index.md`
- `wiki/references/records-map.md:145` FULL `wiki/index.md`
- `wiki/references/records-map.md:146` FULL `wiki/index.md`
- `wiki/references/records-map.md:147` FULL `wiki/index.md`
- `wiki/references/records-map.md:148` FULL `wiki/index.md`
- `wiki/references/records-map.md:149` FULL `wiki/index.md`
- `wiki/references/records-map.md:151` FULL `wiki/index.md`
- `wiki/references/records-map.md:153` FULL `wiki/index.md`
- `wiki/references/skills/wiki-master.md:152` FULL `wiki/index.md`
- `wiki/references/skills/wiki-master.md:159` FULL `wiki/index.md`
- `wiki/references/wiki-answer-key.md:11` FULL `wiki/index.md`
- `wiki/references/wiki-answer-key.md:21` FULL `wiki/index.md`
- `wiki/references/wiki-answer-key.md:74` FULL `wiki/index.md`
- `wiki/references/wiki-answer-key.md:79` FULL `wiki/index.md`
- `wiki/references/wiki-answer-key.md:80` FULL `wiki/index.md`
- `wiki/sources/infrastructure/UNCERTAIN-cfl-early-setup-2026-05-01-000a36.md:26` FULL `wiki/index.md`
- `wiki/sources/infrastructure/close-fable-mirror-standard-update-2026-08-02.md:146` FULL `wiki/index.md`
- `wiki/sources/infrastructure/conductor-execution-manager-crossvenue-intake-2026-07-18-78619b.md:68` FULL `wiki/index.md`
- `wiki/sources/infrastructure/docker-readiness-reading-surface-defect-2026-07-21-085e60.md:34` FULL `wiki/index.md`
- `wiki/sources/infrastructure/merge-train-instrument-blindness-wayfinder-2026-07-29-627c1e.md:53` FULL `wiki/index.md`
- `wiki/sources/infrastructure/pr1-promise-retrospective-2026-08-23.md:31` FULL `wiki/index.md`
- `wiki/sources/infrastructure/professionalism-opus-wake-2026-08-30-a90e0d.md:38` FULL `wiki/index.md`
- `wiki/sources/infrastructure/question-pricing-model-and-outcome-tracking-approval-2026-07-27-408368.md:94` FULL `wiki/index.md`
- `wiki/sources/infrastructure/skills-master-cc-restore-2026-05-08-f9cdf4.md:39` FULL `wiki/index.md`
- `wiki/sources/infrastructure/skills-master-role-architecture-2026-05-15-2e2c62.md:40` FULL `wiki/index.md`
- `wiki/sources/infrastructure/wayfinder-charter-observer-agents-2026-07-19-60bf84.md:51` FULL `wiki/index.md`
- `wiki/sources/infrastructure/wayfinder-charter-observer-agents-2026-07-19-60bf84.md:87` FULL `wiki/index.md`
- `wiki/sources/infrastructure/wiki-master-cc-personal-ingest-2026-05-29-974202.md:21` FULL `wiki/index.md`
- `wiki/sources/infrastructure/wiki-master-phase3-subagent-log-2026-06-01-ad8e70.md:19` FULL `wiki/index.md`
- `wiki/sources/infrastructure/wiki-master-phase3-subagent-log-2026-06-01-ad8e70.md:43` FULL `wiki/index.md`
- `wiki/sources/infrastructure/wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a.md:52` FULL `wiki/index.md`

### `wiki/references/agent-memory/t44-apollo-artemis-complete.md` (SCAN) -- 2 inbound ref(s)

- `wiki/references/agent-memory/README.md:131` WIKILINK `[[t44-apollo-artemis-complete`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:218` STEM `t44-apollo-artemis-complete`

### `wiki/references/audit-census-2026-07-13.md` (SCAN) -- 3 inbound ref(s)

- `scripts/lint_citation_coverage.py:5` FULL `wiki/references/audit-census-2026-07-13.md`
- `wiki/references/README-genre-split.md:39` FILENAME `audit-census-2026-07-13.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:155` STEM `audit-census-2026-07-13`

### `wiki/references/audit-conformance-ledger.md` (SCAN) -- 7 inbound ref(s)

- `scripts/audit/lint.py:422` FULL `wiki/references/audit-conformance-ledger.md`
- `scripts/audit/lint.py:566` SUFFIX `references/audit-conformance-ledger.md`
- `wiki/references/source-page-standard-v1.md:22` FILENAME `audit-conformance-ledger.md`
- `wiki/references/source-page-standard-v1.md:109` FILENAME `audit-conformance-ledger.md`
- `wiki/references/source-page-standard-v2.md:199` FILENAME `audit-conformance-ledger.md`
- `wiki/references/source-page-standard-v3.md:190` FILENAME `audit-conformance-ledger.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:156` STEM `audit-conformance-ledger`

### `wiki/references/cfl-branch-registry.md` (SCAN) -- 18 inbound ref(s)

- `scripts/audit/skill_record_ext.py:37` FILENAME `cfl-branch-registry.md`
- `scripts/audit/skill_record_ext.py:1061` FILENAME `cfl-branch-registry.md`
- `scripts/audit/skill_record_ext.py:1327` FILENAME `cfl-branch-registry.md`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:163` FULL `wiki/references/cfl-branch-registry.md`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:379` FULL `wiki/references/cfl-branch-registry.md`
- `wiki/references/skills/wayfinder.md:35` FILENAME `cfl-branch-registry.md`
- `wiki/references/skills/wayfinder.md:220` FILENAME `cfl-branch-registry.md`
- `wiki/references/vocabulary.md:55` FULL `wiki/references/cfl-branch-registry.md`
- `wiki/references/vocabulary.md:59` FILENAME `cfl-branch-registry.md`
- `wiki/references/vocabulary.md:62` FILENAME `cfl-branch-registry.md`
- `wiki/references/vocabulary.md:182` FULL `wiki/references/cfl-branch-registry.md`
- `wiki/references/wiki-answer-key.md:67` FULL `wiki/references/cfl-branch-registry.md`
- `wiki/sources/consciousness/su-interpretation-cfl.md:21` FULL `wiki/references/cfl-branch-registry.md`
- `wiki/sources/consciousness/su-interpretation-cfl.md:34` FULL `wiki/references/cfl-branch-registry.md`
- `wiki/sources/infrastructure/secretary-post-compact-rsi-orginization-and-critic-2026-08-15-4e6a6f.md:161` WIKILINK `[[cfl-branch-registry`
- `wiki/sources/infrastructure/secretary-self-branching-compact-test-2026-08-15-b84af2.md:149` WIKILINK `[[cfl-branch-registry`
- `wiki/sources/infrastructure/secretary-wake-brief-continuity-model-directive-2026-08-15-40bbac.md:164` WIKILINK `[[cfl-branch-registry`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:163` STEM `cfl-branch-registry`

### `wiki/references/cfl-file-manifest-2026-07-16.md` (SCAN) -- 1 inbound ref(s)

- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:164` STEM `cfl-file-manifest-2026-07-16`

### `wiki/references/claude-code/settings-reference.md` (SCAN) -- 44 inbound ref(s)

- `wiki/concepts/claude-code-hooks-and-agent-engine.md:24` FILENAME `settings-reference.md`
- `wiki/references/claude-code/agent-teams.md:115` STEM `settings-reference`
- `wiki/references/claude-code/agent-teams.md:253` STEM `settings-reference`
- `wiki/references/claude-code/agent-teams.md:313` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:60` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:65` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:71` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:85` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:90` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:105` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:133` STEM `settings-reference`
- `wiki/references/claude-code/cli-reference.md:136` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:211` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:216` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:221` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:230` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:243` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:288` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:296` STEM `settings-reference`
- `wiki/references/claude-code/cross-session-messaging.md:366` STEM `settings-reference`
- `wiki/references/claude-code/hooks-guide.md:197` STEM `settings-reference`
- `wiki/references/claude-code/hooks-guide.md:455` STEM `settings-reference`
- `wiki/references/claude-code/hooks-guide.md:839` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:272` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:273` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:274` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:276` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:280` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:736` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:1842` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:1869` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:1938` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:2247` STEM `settings-reference`
- `wiki/references/claude-code/hooks.md:2680` STEM `settings-reference`
- `wiki/references/claude-code/skills.md:29` STEM `settings-reference`
- `wiki/references/claude-code/skills.md:155` STEM `settings-reference`
- `wiki/references/claude-code/skills.md:1070` STEM `settings-reference`
- `wiki/references/claude-code/sub-agents.md:234` STEM `settings-reference`
- `wiki/references/claude-code/sub-agents.md:686` STEM `settings-reference`
- `wiki/references/claude-code/sub-agents.md:1037` STEM `settings-reference`
- `wiki/references/claude-code/workflows.md:158` STEM `settings-reference`
- `wiki/references/claude-code/workflows.md:190` STEM `settings-reference`
- `wiki/references/claude-code/workflows.md:344` STEM `settings-reference`
- `wiki/references/claude-code/workflows.md:426` STEM `settings-reference`

### `wiki/references/growth-intent-worked-examples/example-a-material-agent-interaction-after.md` (SCAN) -- 2 inbound ref(s)

- `wiki/concepts/heteronomy-horn-pearl-lens.md:113` FULL `wiki/references/growth-intent-worked-examples/example-a-material-agent-interaction-after.md`
- `wiki/test-outputs/LINT-SWEEP-2026-09-02.out:178` STEM `example-a-material-agent-interaction-after`

### `wiki/references/registries/trunks.md` (SCAN) -- 9 inbound ref(s)

- `skills/domain-modeling/SKILL.md:89` FULL `wiki/references/registries/trunks.md`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:15` FULL `wiki/references/registries/trunks.md`
- `wiki/references/README-genre-split.md:47` SUFFIX `registries/trunks.md`
- `wiki/references/record-architecture-v1.md:41` SUFFIX `registries/trunks.md`
- `wiki/references/record-architecture-v1.md:121` FULL `wiki/references/registries/trunks.md`
- `wiki/references/source-page-standard-v2/v3/v4.md:23` FULL `wiki/references/registries/trunks.md`
- `wiki/references/vocabulary.md:72` SUFFIX `registries/trunks.md`
- `wiki/references/vocabulary.md:248` FULL `wiki/references/registries/trunks.md`
- `wiki/references/vocabulary.md:337` SUFFIX `registries/trunks.md`

### `wiki/skills-gate/INGEST-LEDGER.md` (SCAN) -- 14 inbound ref(s)

- `scripts/audit/absence_claims.py:421` STEM `INGEST-LEDGER`
- `scripts/audit/derive_public_tree.py:72` FULL `wiki/skills-gate/INGEST-LEDGER.md`
- `scripts/audit/lint_shipped_coverage.py:176` FILENAME `INGEST-LEDGER.md`
- `scripts/audit/repair_list_from_ledger.py:4` FULL `wiki/skills-gate/INGEST-LEDGER.md`
- `scripts/audit/repair_list_from_ledger.py:46` FULL `wiki/skills-gate/INGEST-LEDGER.md`
- `scripts/audit/wikiskills_prototype_render.py:336` STEM `INGEST-LEDGER`
- `scripts/audit/wikiskills_prototype_render.py:339` STEM `INGEST-LEDGER`
- `scripts/audit/wikiskills_prototype_render.py:340` FILENAME `INGEST-LEDGER.md`
- `scripts/audit/wikiskills_prototype_render.py:345` FULL `wiki/skills-gate/INGEST-LEDGER.md`
- `scripts/audit/wikiskills_prototype_render.py:353` STEM `INGEST-LEDGER`
- `wiki/WIKISKILLS-PROTOTYPE.md:73` STEM `INGEST-LEDGER`
- `wiki/WIKISKILLS-PROTOTYPE.md:75` FULL `wiki/skills-gate/INGEST-LEDGER.md`
- `wiki/patterns/self-citation-moves-the-class.md:65` FILENAME `INGEST-LEDGER.md`
- `wiki/references/source-page-repair-contract-v1.md:48` FILENAME `INGEST-LEDGER.md`

### `wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md` (SCAN) -- 3 inbound ref(s)

- `wiki/concepts/heteronomy-horn-pearl-lens.md:31` FULL `wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md`
- `wiki/concepts/heteronomy-horn-pearl-lens.md:91` FULL `wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md`
- `wiki/references/growth-intent-worked-examples/README.md:49` FULL `wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md`

### `wiki/sources/infrastructure/capacity-planning-autonomy-governance-2026-07-10-7f2815.md` (SCAN) -- 1 inbound ref(s)

- `wiki/sources/infrastructure/docker-isolation-planner-packet-a-work-order-2026-07-18-a8bbda.md:172` WIKILINK `[[capacity-planning-autonomy-governance-2026-07-10-7f2815`

### `wiki/sources/infrastructure/citation-audit-2026-05-26.md` (SCAN) -- 3 inbound ref(s)

- `wiki/references/citation-audit-2026-05-26.md:6` FULL `wiki/sources/infrastructure/citation-audit-2026-05-26.md`
- `wiki/references/citation-audit-2026-05-26.md:14` FULL `wiki/sources/infrastructure/citation-audit-2026-05-26.md`
- `wiki/references/citation-audit-2026-05-26.md:22` FULL `wiki/sources/infrastructure/citation-audit-2026-05-26.md`

### `wiki/sources/infrastructure/corpus-loss-audit-2026-07-19.md` (SCAN) -- 6 inbound ref(s)

- `wiki/references/agent-memory/derive-dont-record.md:96` SUFFIX `infrastructure/corpus-loss-audit-2026-07-19.md`
- `wiki/references/skills/wiki-master.md:174` STEM `corpus-loss-audit-2026-07-19`
- `wiki/sources/ai-mechanics/tree-search-generation-j-layer-licensing-2026-07-17-5d2f71.md:332` WIKILINK `[[corpus-loss-audit-2026-07-19`
- `wiki/sources/infrastructure/nightly-lane-leg2-self-referential-recovery-2026-07-20-305b5a.md:180` FULL `wiki/sources/infrastructure/corpus-loss-audit-2026-07-19.md`
- `wiki/sources/infrastructure/packet-a-l1-l2-l3-execution-2026-07-18-49a1c0.md:205` WIKILINK `[[corpus-loss-audit-2026-07-19`
- `wiki/sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md:221` WIKILINK `[[corpus-loss-audit-2026-07-19`

### `wiki/sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` (SCAN) -- 1 inbound ref(s)

- `wiki/references/skills/wiki-master.md:141` SUFFIX `infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md`

### `wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md` (SCAN) -- 5 inbound ref(s)

- `wiki/references/source-page-contract-v1.md:25` FULL `wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md`
- `wiki/references/source-page-contract-v1.md:150` FULL `wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md`
- `wiki/sources/ai-mechanics/j-layer-directed-thought-vs-cot-2026-07-19-c4067b.md:26` FILENAME `j-layer-forward-pass-direction-2026-07-11-090a56-cont.md`
- `wiki/sources/ai-mechanics/j-layer-directed-thought-vs-cot-2026-07-19-c4067b.md:61` FILENAME `j-layer-forward-pass-direction-2026-07-11-090a56-cont.md`
- `wiki/sources/ai-mechanics/tree-search-generation-j-layer-licensing-2026-07-17-5d2f71.md:330` WIKILINK `[[j-layer-forward-pass-direction-2026-07-11-090a56-cont`

### `wiki/sources/infrastructure/triage-master-open-items-2026-04-28-090a56.md` (SCAN) -- 4 inbound ref(s)

- `wiki/references/growth-intent-worked-examples/README.md:283` STEM `triage-master-open-items-2026-04-28-090a56`
- `wiki/references/wiki-growth-intent.md:751` STEM `triage-master-open-items-2026-04-28-090a56`
- `wiki/sources/infrastructure/link-quality-audit-2026-06-04.md:54` STEM `triage-master-open-items-2026-04-28-090a56`
- `wiki/sources/infrastructure/wiki-master-phase3-subagent-log-2026-06-01-ad8e70.md:65` FULL `wiki/sources/infrastructure/triage-master-open-items-2026-04-28-090a56.md`

### `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md` (SCAN) -- 1 inbound ref(s)

- `wiki/references/agent-memory/verify-controls-before-declaring-loss.md:34` FULL `wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md`

### `wiki/sources/infrastructure/wiki-multi-master-audit-2026-06-02-dba2c0b.md` (SCAN) -- 12 inbound ref(s)

- `skills/session-order/SKILL.md:219` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/citability-standard.md:8` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/citability-standard.md:27` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/citability-standard.md:44` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/citability-standard.md:48` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/citability-standard.md:72` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/understand-anything.md:8` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/understand-anything.md:17` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/understand-anything.md:30` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/understand-anything.md:42` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/concepts/understand-anything.md:60` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`
- `wiki/sources/infrastructure/link-quality-audit-2026-06-04.md:70` STEM `wiki-multi-master-audit-2026-06-02-dba2c0b`

### `wiki/sources/infrastructure/wiki-session-conflict-resolution-crosslinks-2026-06-04.md` (SCAN) -- 2 inbound ref(s)

- `wiki/concepts/understand-anything.md:38` STEM `wiki-session-conflict-resolution-crosslinks-2026-06-04`
- `wiki/concepts/understand-anything.md:48` STEM `wiki-session-conflict-resolution-crosslinks-2026-06-04`

### `wiki/sources/security-master-audit-2026-06-27.md` (SCAN) -- 3 inbound ref(s)

- `wiki/sources/infrastructure/professional-resurrection-test-fence-close-2026-08-15-ffb92d.md:79` WIKILINK `[[security-master-audit-2026-06-27`
- `wiki/sources/infrastructure/professional-resurrection-test-fence-close-2026-08-15-ffb92d.md:97` WIKILINK `[[security-master-audit-2026-06-27`
- `wiki/sources/infrastructure/professional-security-agenda-to-resident-launch-vigil-2026-08-08-592c3c.md:117` WIKILINK `[[security-master-audit-2026-06-27`

### `wiki/sources/session-stubs.md` (SCAN) -- 39 inbound ref(s)

- `scripts/audit/coverage_census.py:35` STEM `session-stubs`
- `scripts/audit/coverage_census.py:267` STEM `session-stubs`
- `scripts/audit/coverage_census.py:339` FILENAME `session-stubs.md`
- `scripts/audit/coverage_census.py:436` FILENAME `session-stubs.md`
- `scripts/audit/coverage_gap.py:40` FULL `wiki/sources/session-stubs.md`
- `scripts/audit/coverage_gap.py:42` FILENAME `session-stubs.md`
- `scripts/audit/coverage_gap.py:77` FULL `wiki/sources/session-stubs.md`
- `scripts/audit/coverage_gap.py:170` FILENAME `session-stubs.md`
- `scripts/audit/index_counts.py:103` SUFFIX `sources/session-stubs.md`
- `scripts/audit/index_counts.py:113` FILENAME `session-stubs.md`
- `scripts/audit/jon_words_coverage.py:168` FILENAME `session-stubs.md`
- `scripts/audit/regen_index_sections.py:27` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:3` FULL `wiki/sources/session-stubs.md`
- `scripts/audit/register_stubs.py:6` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:21` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:150` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:164` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:178` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:179` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:225` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:230` FILENAME `session-stubs.md`
- `scripts/audit/register_stubs.py:293` FILENAME `session-stubs.md`
- `scripts/audit/wikiskills_prototype_render.py:264` FILENAME `session-stubs.md`
- `scripts/audit/wikiskills_prototype_render.py:265` FILENAME `session-stubs.md`
- `scripts/graphrag/acceptance.py:115` FULL `wiki/sources/session-stubs.md`
- `scripts/graphrag/acceptance.py:133` STEM `session-stubs`
- `scripts/graphrag/build_index.py:487` FULL `wiki/sources/session-stubs.md`
- `scripts/lint_untracked_wiki.py:6` FULL `wiki/sources/session-stubs.md`
- `scripts/lint_untracked_wiki.py:43` FULL `wiki/sources/session-stubs.md`
- `scripts/lint_untracked_wiki.py:105` FULL `wiki/sources/session-stubs.md`
- `skills/wiki-master/SKILL.md:881` FILENAME `session-stubs.md`
- `wiki/WIKISKILLS-PROTOTYPE.md:61` FILENAME `session-stubs.md`
- `wiki/references/agent-memory/hedge-flattening-and-invented-rulings.md:28` FILENAME `session-stubs.md`
- `wiki/references/record-architecture-v1.md:98` STEM `session-stubs`
- `wiki/references/source-page-standard-v4.md:185` FULL `wiki/sources/session-stubs.md`
- `wiki/references/source-page-standard-v4.md:203` FILENAME `session-stubs.md`
- `wiki/sources/infrastructure/cfl-video-implementation-planning-2026-07-26-a42d10.md:42` STEM `session-stubs`
- `wiki/sources/infrastructure/merge-train-instrument-blindness-wayfinder-2026-07-29-627c1e.md:54` FILENAME `session-stubs.md`
- `wiki/sources/infrastructure/wiki-unnavigable-organization-not-volume-2026-08-07-d869b4.md:54` FULL `wiki/sources/session-stubs.md`

### `wiki/test-outputs/HOOK-HARNESS-run.jsonl` (SCAN) -- 1 inbound ref(s)

- `scripts/audit/hook_harness.py:1642` FULL `wiki/test-outputs/HOOK-HARNESS-run.jsonl`

## VALUE-WALK

**VALUE-WALK: 1 literal(s) walked over 1046 INCLUDED files; 0 literal(s) found, 0 hit(s) total**

Each `VALUE_WALK` literal from `public_exclusions.txt` is walked fixed-string and case-sensitive over every INCLUDED file. Withholding the file that introduced an identifier does not withhold the identifier. The literal is never printed here -- a row carries an opaque ordinal id, sha256[:8] of (per-run random salt + literal) with the salt printed nowhere (an unsalted digest of a low-entropy literal is an oracle), and its class -- so this log cannot leak what it guards. Nothing was rewritten. `--fail-on-value-hits` exits 5 when any hit exists.

| id | salted digest[:8] | class | hits |
|---|---|---|---|
| VW-01 | `8631a70c` | CREDENTIAL-SHAPED Drive folder id | 0 |

## SHAPE-SCAN

**SHAPE-SCAN: 2 shape(s) scanned over 1046 INCLUDED files; 13 token hit(s) (detector only, no exit code)**

Each `SHAPE_SCAN <name> <regex>` row is scanned, bounded by non-token characters, over every INCLUDED file, after dropping hex-only strings, tokens lacking mixed case plus a digit, tokens carrying a date, and hyphenated slugs. A hit names the shape and the token's LENGTH only, never the token. This is a detector feeding a human decision; it sets no exit code. Nothing was rewritten.

Second column (lane PUB-2e, 2026-09-02; never a filter -- no row is removed): each hit also carries `likely_slug`, `separators` (count of `-` and `_` in the token) and `longest_alpha_segment` (length of the longest separator-delimited all-letter segment, 0 if none). Rule: `likely_slug = separators >= 2 OR any separator-delimited segment all-alphabetic and >= 5 chars`. Rule tuned on seven tokens, three of them real: a sample, not a validation (Professional, 2026-09-02). Rows are ordered likely_slug=no first, so the tokens most worth a human read come first.

| shape | hits | likely_slug=no | likely_slug=yes |
|---|---|---|---|
| GOOGLE-DRIVE-ID | 8 | 4 | 4 |
| GOOGLE-FILE-ID | 5 | 1 | 4 |

### GOOGLE-DRIVE-ID -- 8 hit(s)

- `scripts/tests/selftest_reference_survivors.py:319` GOOGLE-DRIVE-ID len=33 likely_slug=no separators=0 longest_alpha_segment=0
- `scripts/tests/selftest_reference_survivors.py:360` GOOGLE-DRIVE-ID len=33 likely_slug=no separators=0 longest_alpha_segment=0
- `scripts/tests/selftest_reference_survivors.py:361` GOOGLE-DRIVE-ID len=33 likely_slug=no separators=1 longest_alpha_segment=0
- `wiki/sources/infrastructure/secretary-claudeai-seat-born-coordinator-ruling-write-lane-2026-08-15-b50b3c.md:138` GOOGLE-DRIVE-ID len=33 likely_slug=no separators=0 longest_alpha_segment=0
- `scripts/tests/selftest_reference_survivors.py:354` GOOGLE-DRIVE-ID len=33 likely_slug=yes separators=4 longest_alpha_segment=9
- `scripts/tests/selftest_reference_survivors.py:356` GOOGLE-DRIVE-ID len=33 likely_slug=yes separators=4 longest_alpha_segment=12
- `wiki/skills-gate/validation/dream/split.jsonl:8` GOOGLE-DRIVE-ID len=33 likely_slug=yes separators=5 longest_alpha_segment=6
- `wiki/sources/infrastructure/professional-inbound-drain-19th-wake-2026-08-17-817504.md:40` GOOGLE-DRIVE-ID len=33 likely_slug=yes separators=4 longest_alpha_segment=9

### GOOGLE-FILE-ID -- 5 hit(s)

- `scripts/tests/selftest_reference_survivors.py:362` GOOGLE-FILE-ID len=44 likely_slug=no separators=1 longest_alpha_segment=0
- `scripts/tests/selftest_reference_survivors.py:355` GOOGLE-FILE-ID len=44 likely_slug=yes separators=6 longest_alpha_segment=8
- `scripts/tests/selftest_reference_survivors.py:357` GOOGLE-FILE-ID len=44 likely_slug=yes separators=5 longest_alpha_segment=19
- `wiki/sources/infrastructure/switchboard-operator-deliver-herald-review-verdict-2026-08-17-c28473.md:51` GOOGLE-FILE-ID len=44 likely_slug=yes separators=5 longest_alpha_segment=11
- `wiki/sources/infrastructure/switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372.md:46` GOOGLE-FILE-ID len=44 likely_slug=yes separators=8 longest_alpha_segment=8
