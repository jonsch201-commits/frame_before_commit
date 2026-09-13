# Hook harness run — CFL — 2026-09-02T14:02:42.342410+00:00

Settings: `.claude\settings.json`  
Hook entries in settings.json: **18**  
Rows written: **18**  
Entries-with-a-row == settings-entry-count: **True**

## Summary by class

| class | count |
|---|---|
| OK | 9 |
| FAIL-OPEN-SILENT | 7 |
| SKIPPED-DESTRUCTIVE | 2 |

## Rows

| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | ms | class |
|---|---|---|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | bash | scripts/audit/session_store_capture.py | 24971 | True | 0 | 571 | 38909.4 | OK |
| Stop | None | 0.1 | bash | .claude/hooks/pre-stop-consult.sh | 16915 | True | 0 | 0 | 880.9 | FAIL-OPEN-SILENT |
| SubagentStop | None | 0.0 | bash | scripts/audit/route_agent_return.py | 24903 | True | 0 | 325 | 140.8 | OK |
| SubagentStop | None | 0.1 | bash | scripts/audit/agent_end_ingest.py | 165583 | True | 0 | 0 | 247.9 | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 1263.7 | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.1 | bash | scripts/audit/session_store_capture.py | 24971 | True | 0 | 569 | 804.1 | OK |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | None | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | scripts/audit/exchange_write_check.py | 4875 | True | 0 | 0 | 100.6 | FAIL-OPEN-SILENT |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 186.6 | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | None | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 265.2 | OK |
| SessionStart | startup|resume | 0.2 | bash | scripts/audit/exchange_inbox.py | 51623 | False | 0 | 0 | 159.5 | FAIL-OPEN-SILENT |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/post-compact-wake.sh | 10025 | False | 0 | 1570 | 1720.5 | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/global-staleness-probe.py | 22636 | True | 0 | 630 | 2297.6 | OK |
| SessionStart | compact|clear | 1.2 | bash | scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 292.1 | OK |
| SessionEnd | None | 0.0 | bash | scripts/audit/session_finalise.py | 45779 | True | 0 | 174 | 420.7 | OK |
| SessionEnd | None | 0.1 | bash | scripts/audit/i2_session_page.py | 43978 | True | 0 | 0 | 128.7 | FAIL-OPEN-SILENT |
| PostCompact | None | 0.0 | bash | scripts/audit/postcompact_verify.py;scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 361.3 | OK |
