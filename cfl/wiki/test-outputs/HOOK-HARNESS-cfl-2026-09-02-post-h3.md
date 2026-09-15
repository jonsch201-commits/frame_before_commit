# Hook harness run — cfl — 2026-09-02T14:14:47.329086+00:00

Settings: `.claude\settings.json`  
Hook entries in settings.json: **18**  
Rows written: **18**  
Entries-with-a-row == settings-entry-count: **True**

## Summary by class

| class | count |
|---|---|
| FAIL-CLOSED-VISIBLE | 11 |
| FAIL-OPEN-SILENT | 4 |
| SKIPPED-DESTRUCTIVE | 2 |
| OK | 1 |

## Rows

| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | ms | class |
|---|---|---|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 51.4 | FAIL-CLOSED-VISIBLE |
| Stop | None | 0.1 | bash | .claude/hooks/pre-stop-consult.sh | 16917 | False | 0 | 0 | 665.1 | FAIL-OPEN-SILENT |
| SubagentStop | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 50.1 | FAIL-CLOSED-VISIBLE |
| SubagentStop | None | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 51.8 | FAIL-CLOSED-VISIBLE |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 1114.4 | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 60.4 | FAIL-CLOSED-VISIBLE |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | None | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 51.8 | FAIL-CLOSED-VISIBLE |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 230.8 | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | None | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 62.8 | FAIL-CLOSED-VISIBLE |
| SessionStart | startup|resume | 0.2 | bash | .claude/hooks/py_closed.sh | 5441 | False | 0 | 0 | 70.4 | FAIL-OPEN-SILENT |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/post-compact-wake.sh | 10025 | True | 0 | 1622 | 2017.3 | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 74.1 | FAIL-CLOSED-VISIBLE |
| SessionStart | compact|clear | 1.2 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 81.3 | FAIL-CLOSED-VISIBLE |
| SessionEnd | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 69.5 | FAIL-CLOSED-VISIBLE |
| SessionEnd | None | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 85.4 | FAIL-CLOSED-VISIBLE |
| PostCompact | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | False | 127 | 0 | 103.0 | FAIL-CLOSED-VISIBLE |
