# Hook harness run — cfl — 2026-09-02T15:18:20.139078+00:00

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
| OK | 12 |
| FAIL-OPEN-SILENT | 4 |
| SKIPPED-DESTRUCTIVE | 2 |
| FAIL-CLOSED-VISIBLE | 1 |

## Baseline rows

| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | declared_timeout_s | harness_cap_s | ms | executed | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 571 | 120 | 120.0 | 50047.8 | True | OK |
| Stop | None | 0.1 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/pre-stop-consult.sh | 16917 | True | 0 | 1476 | 20 | 20.0 | 1211.2 | True | OK |
| SubagentStop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/route_agent_return.py | 36522 | True | 0 | 325 | 15 | 15.0 | 402.6 | True | OK |
| SubagentStop | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/agent_end_ingest.py | 165583 | True | 0 | 0 | 60 | 60.0 | 479.4 | True | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 60 | 60.0 | 1592.7 | True | OK |
| PreCompact | manual|auto | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 569 | 300 | 300.0 | 918.3 | True | OK |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | 60 | None | None | False | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_write_check.py | 4875 | True | 0 | 0 | 30 | 30.0 | 373.5 | True | FAIL-OPEN-SILENT |
| PostToolUse | Write|Edit|MultiEdit | 0.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/index_queue_enqueue.py | 3929 | False | 1 | 0 | 5 | 5.0 | 747.2 | True | FAIL-CLOSED-VISIBLE |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 15 | 15.0 | 645.2 | True | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | 30 | None | None | False | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 10041 | False | 0 | 429 | 600 | 600.0 | 594.5 | True | OK |
| SessionStart | startup|resume | 0.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_inbox.py | 51623 | True | 0 | 122786 | 120 | 120.0 | 11506.3 | True | OK |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/post-compact-wake.sh | 10025 | True | 0 | 1622 | 30 | 30.0 | 12582.5 | True | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/py_closed.sh;.claude/hooks/global-staleness-probe.py | 22636 | True | 0 | 612 | 30 | 30.0 | 2126.8 | True | OK |
| SessionStart | compact|clear | 1.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 10041 | False | 0 | 429 | 600 | 600.0 | 597.3 | True | OK |
| SessionEnd | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_finalise.py | 45779 | True | 0 | 174 | 300 | 300.0 | 1149.8 | True | OK |
| SessionEnd | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/i2_session_page.py | 43978 | True | 0 | 0 | 180 | 180.0 | 584.7 | True | FAIL-OPEN-SILENT |
| PostCompact | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_verify.py;scripts/audit/postcompact_pipeline.py | 10041 | False | 0 | 429 | 900 | 900.0 | 1383.1 | True | OK |
