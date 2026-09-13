# Hook harness run — cfl — 2026-09-02T14:42:18.181237+00:00

Settings: `.claude\settings.json`  
Fixtures: `N:\claude-cfl\clone\scripts\tests\hook_fixtures`  
Hook entries in settings.json: **18**  
Baseline rows written: **18**  
Entries-with-a-row == settings-entry-count: **True**  
Baseline executed (subprocess actually ran): **16**  
DUPLICATE-WORK-SIGNATURE flagged (note, not a class): **1**

## Baseline — summary by class

| class | count |
|---|---|
| OK | 12 |
| FAIL-OPEN-SILENT | 4 |
| SKIPPED-DESTRUCTIVE | 2 |

## Baseline rows

| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | declared_timeout_s | harness_cap_s | ms | executed | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 571 | 120 | 120.0 | 54927.8 | True | OK |
| Stop | None | 0.1 | bash | .claude/hooks/pre-stop-consult.sh | 16917 | True | 0 | 1476 | 20 | 20.0 | 1117.1 | True | OK |
| SubagentStop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/route_agent_return.py | 36522 | True | 0 | 325 | 15 | 15.0 | 478.3 | True | OK |
| SubagentStop | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/agent_end_ingest.py | 165583 | True | 0 | 0 | 60 | 60.0 | 520.7 | True | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 60 | 60.0 | 1572.6 | True | OK |
| PreCompact | manual|auto | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 567 | 300 | 300.0 | 616.1 | True | OK |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | 60 | None | None | False | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_write_check.py | 4875 | True | 0 | 0 | 30 | 30.0 | 285.2 | True | FAIL-OPEN-SILENT |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 15 | 15.0 | 204.0 | True | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | 30 | None | None | False | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 600 | 600.0 | 558.6 | True | OK |
| SessionStart | startup|resume | 0.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_inbox.py | 51623 | True | 0 | 121229 | 120 | 120.0 | 10499.1 | True | OK |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/post-compact-wake.sh | 10025 | True | 0 | 1622 | 30 | 30.0 | 1252.9 | True | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/py_closed.sh;.claude/hooks/global-staleness-probe.py | 22636 | True | 0 | 612 | 30 | 30.0 | 1569.1 | True | OK |
| SessionStart | compact|clear | 1.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 600 | 600.0 | 371.9 | True | OK |
| SessionEnd | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_finalise.py | 45779 | True | 0 | 174 | 300 | 300.0 | 374.5 | True | OK |
| SessionEnd | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/i2_session_page.py | 43978 | True | 0 | 0 | 180 | 180.0 | 235.7 | True | FAIL-OPEN-SILENT |
| PostCompact | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_verify.py;scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 900 | 900.0 | 883.7 | True | OK |
