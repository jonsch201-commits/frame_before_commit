# Hook harness run — cfl — 2026-09-02T14:19:55.529873+00:00

Settings: `.claude\settings.json`  
Fixtures: `N:\claude-cfl\clone\scripts\tests\hook_fixtures`  
Hook entries in settings.json: **18**  
Rows written: **18**  
Entries-with-a-row == settings-entry-count: **True**  
Executed (subprocess actually ran): **16**

## Summary by class

| class | count |
|---|---|
| FAIL-CLOSED-VISIBLE | 11 |
| FAIL-OPEN-SILENT | 4 |
| SKIPPED-DESTRUCTIVE | 2 |
| OK | 1 |

## Rows

| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | ms | executed | class |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 67.9 | True | FAIL-CLOSED-VISIBLE |
| Stop | None | 0.1 | bash | .claude/hooks/pre-stop-consult.sh | 16917 | False | 0 | 0 | 840.4 | True | FAIL-OPEN-SILENT |
| SubagentStop | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 50.7 | True | FAIL-CLOSED-VISIBLE |
| SubagentStop | None | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 59.3 | True | FAIL-CLOSED-VISIBLE |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 1150.4 | True | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 49.5 | True | FAIL-CLOSED-VISIBLE |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | None | False | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 54.3 | True | FAIL-CLOSED-VISIBLE |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 216.3 | True | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | None | False | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 63.7 | True | FAIL-CLOSED-VISIBLE |
| SessionStart | startup|resume | 0.2 | bash | .claude/hooks/py_closed.sh | 5441 | False | 0 | 0 | 66.1 | True | FAIL-OPEN-SILENT |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/post-compact-wake.sh | 10025 | True | 0 | 1622 | 1935.6 | True | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 64.5 | True | FAIL-CLOSED-VISIBLE |
| SessionStart | compact|clear | 1.2 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 61.3 | True | FAIL-CLOSED-VISIBLE |
| SessionEnd | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 56.3 | True | FAIL-CLOSED-VISIBLE |
| SessionEnd | None | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 56.8 | True | FAIL-CLOSED-VISIBLE |
| PostCompact | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 126.8 | True | FAIL-CLOSED-VISIBLE |
