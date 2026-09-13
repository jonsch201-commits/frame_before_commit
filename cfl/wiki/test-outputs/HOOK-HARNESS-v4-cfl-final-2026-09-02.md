# Hook harness run — cfl — 2026-09-02T14:54:54.903678+00:00

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
| Stop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 571 | 120 | 120.0 | 33237.3 | True | OK |
| Stop | None | 0.1 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/pre-stop-consult.sh | 16917 | True | 0 | 1476 | 20 | 20.0 | 876.9 | True | OK |
| SubagentStop | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/route_agent_return.py | 36522 | True | 0 | 325 | 15 | 15.0 | 272.9 | True | OK |
| SubagentStop | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/agent_end_ingest.py | 165583 | True | 0 | 0 | 60 | 60.0 | 338.5 | True | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 60 | 60.0 | 1188.6 | True | OK |
| PreCompact | manual|auto | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_store_capture.py | 24971 | True | 0 | 567 | 300 | 300.0 | 437.6 | True | OK |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | 60 | None | None | False | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_write_check.py | 4875 | True | 0 | 0 | 30 | 30.0 | 468.0 | True | FAIL-OPEN-SILENT |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 15 | 15.0 | 489.1 | True | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | 30 | None | None | False | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 600 | 600.0 | 423.7 | True | OK |
| SessionStart | startup|resume | 0.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/exchange_inbox.py | 51623 | True | 0 | 122020 | 120 | 120.0 | 8652.6 | True | OK |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/sh_closed.sh;.claude/hooks/post-compact-wake.sh | 10025 | True | 0 | 1622 | 30 | 30.0 | 1281.7 | True | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/py_closed.sh;.claude/hooks/global-staleness-probe.py | 22636 | True | 0 | 612 | 30 | 30.0 | 1235.0 | True | OK |
| SessionStart | compact|clear | 1.2 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 600 | 600.0 | 341.7 | True | OK |
| SessionEnd | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/session_finalise.py | 45779 | True | 0 | 174 | 300 | 300.0 | 493.0 | True | OK |
| SessionEnd | None | 0.1 | bash | .claude/hooks/py_closed.sh;scripts/audit/i2_session_page.py | 43978 | True | 0 | 0 | 180 | 180.0 | 373.2 | True | FAIL-OPEN-SILENT |
| PostCompact | None | 0.0 | bash | .claude/hooks/py_closed.sh;scripts/audit/postcompact_verify.py;scripts/audit/postcompact_pipeline.py | 8744 | True | 0 | 429 | 900 | 900.0 | 770.3 | True | OK |

## Degraded phase — 13 primary script(s) truncated to 0 bytes: `['.claude/hooks/fable-mirror-write-fence.sh', '.claude/hooks/global-staleness-probe.py', '.claude/hooks/post-compact-wake.sh', '.claude/hooks/pre-compact-su.sh', '.claude/hooks/pre-stop-consult.sh', 'scripts/audit/agent_end_ingest.py', 'scripts/audit/exchange_inbox.py', 'scripts/audit/exchange_write_check.py', 'scripts/audit/i2_session_page.py', 'scripts/audit/postcompact_pipeline.py', 'scripts/audit/route_agent_return.py', 'scripts/audit/session_finalise.py', 'scripts/audit/session_store_capture.py']`

Degraded rows re-run: **16**  
Degraded executed: **16**  
Expectation per row: *wrapper/interpreter should fail CLOSED and VISIBLE*

## Degraded — summary by class

| class | count |
|---|---|
| FAIL-CLOSED-VISIBLE | 16 |

## Degraded rows

| event | matcher | idx | primary (truncated) | exit | stdout_bytes | class | finding |
|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | scripts/audit/session_store_capture.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| Stop | None | 0.1 | .claude/hooks/pre-stop-consult.sh | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SubagentStop | None | 0.0 | scripts/audit/route_agent_return.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SubagentStop | None | 0.1 | scripts/audit/agent_end_ingest.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| PreCompact | manual|auto | 0.0 | .claude/hooks/pre-compact-su.sh | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| PreCompact | manual|auto | 0.1 | scripts/audit/session_store_capture.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | scripts/audit/exchange_write_check.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | .claude/hooks/fable-mirror-write-fence.sh | 2 | 0 | FAIL-CLOSED-VISIBLE |  |
| SessionStart | startup|resume | 0.1 | scripts/audit/postcompact_pipeline.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SessionStart | startup|resume | 0.2 | scripts/audit/exchange_inbox.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SessionStart | compact|clear | 1.0 | .claude/hooks/post-compact-wake.sh | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SessionStart | compact|clear | 1.1 | .claude/hooks/global-staleness-probe.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SessionStart | compact|clear | 1.2 | scripts/audit/postcompact_pipeline.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SessionEnd | None | 0.0 | scripts/audit/session_finalise.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| SessionEnd | None | 0.1 | scripts/audit/i2_session_page.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
| PostCompact | None | 0.0 | scripts/audit/postcompact_pipeline.py | 1 | 0 | FAIL-CLOSED-VISIBLE |  |
