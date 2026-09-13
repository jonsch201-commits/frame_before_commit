# Hook harness run — CFL — 2026-09-03T04:27:44.518775+00:00

Settings: `.claude\settings.json`  
Fixtures: `N:\claude-cfl\clone\scripts\tests\hook_fixtures`  
Hook entries in settings.json: **19**  
Baseline rows written: **19**  
Entries-with-a-row == settings-entry-count: **True**  
Baseline executed (subprocess actually ran): **17**  
DUPLICATE-WORK-SIGNATURE flagged (note, not a class): **1**

## Baseline — summary by class

| class | count |
|---|---|
| OK | 13 |
| FAIL-OPEN-SILENT | 4 |
| SKIPPED-DESTRUCTIVE | 2 |

## Baseline rows

| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | declared_timeout_s | harness_cap_s | ms | executed | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 571 | 120 | 120.0 | 39003.6 | True | OK |
| Stop | None | 0.1 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/pre-stop-consult.sh | 16917 | True | 0 | 1476 | 20 | 20.0 | 965.9 | True | OK |
| SubagentStop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/route_agent_return.py | 36522 | True | 0 | 325 | 15 | 15.0 | 365.6 | True | OK |
| SubagentStop | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/agent_end_ingest.py | 165583 | True | 0 | 0 | 60 | 60.0 | 467.0 | True | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 60 | 60.0 | 1432.9 | True | OK |
| PreCompact | manual|auto | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 567 | 300 | 300.0 | 506.4 | True | OK |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | 60 | None | None | False | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_write_check.py | 4875 | True | 0 | 0 | 30 | 30.0 | 273.0 | True | FAIL-OPEN-SILENT |
| PostToolUse | Write|Edit|MultiEdit | 0.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/index_queue_enqueue.py | 3929 | True | 0 | 0 | 5 | 5.0 | 327.7 | True | OK |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 15 | 15.0 | 425.1 | True | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | 30 | None | None | False | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 10041 | True | 0 | 468 | 600 | 600.0 | 646.5 | True | OK |
| SessionStart | startup|resume | 0.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_inbox.py | 51623 | True | 0 | 187305 | 120 | 120.0 | 7825.0 | True | OK |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/post-compact-wake.sh | 10025 | True | 0 | 1653 | 30 | 30.0 | 1109.0 | True | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/py_closed.sh;.claude/hooks/global-staleness-probe.py | 22636 | True | 0 | 613 | 30 | 30.0 | 978.9 | True | OK |
| SessionStart | compact|clear | 1.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 10041 | True | 0 | 468 | 600 | 600.0 | 419.6 | True | OK |
| SessionEnd | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_finalise.py | 45779 | True | 0 | 174 | 300 | 300.0 | 413.2 | True | OK |
| SessionEnd | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/i2_session_page.py | 43978 | True | 0 | 0 | 180 | 180.0 | 221.0 | True | FAIL-OPEN-SILENT |
| PostCompact | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_verify.py;scripts/audit/postcompact_pipeline.py | 10041 | True | 0 | 468 | 900 | 900.0 | 670.4 | True | OK |
