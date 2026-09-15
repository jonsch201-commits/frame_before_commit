# Hook harness run — cfl — 2026-09-02T14:28:20.446777+00:00

Settings: `.claude\settings.json`  
Fixtures: `N:\claude-cfl\clone\scripts\tests\hook_fixtures`  
Hook entries in settings.json: **18**  
Rows written: **18**  
Entries-with-a-row == settings-entry-count: **True**  
Executed (subprocess actually ran): **16**

## Summary by class

| class | count |
|---|---|
| OK | 12 |
| FAIL-OPEN-SILENT | 4 |
| SKIPPED-DESTRUCTIVE | 2 |

## Rows

| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | ms | executed | class |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Stop | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 571 | 40602.3 | True | OK |
| Stop | None | 0.1 | bash | .claude/hooks/pre-stop-consult.sh | 16917 | True | 0 | 1476 | 815.3 | True | OK |
| SubagentStop | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 325 | 323.0 | True | OK |
| SubagentStop | None | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 0 | 467.1 | True | FAIL-OPEN-SILENT |
| PreCompact | manual|auto | 0.0 | bash | .claude/hooks/pre-compact-su.sh | 9896 | True | 0 | 0 | 1139.4 | True | OK |
| PreCompact | manual|auto | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 567 | 759.4 | True | OK |
| PostToolUse | Write|Edit|MultiEdit | 0.0 | bash | .claude/hooks/post-skills-sync.sh | 4870 | True | None | None | None | False | SKIPPED-DESTRUCTIVE |
| PostToolUse | Write|Edit|MultiEdit | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 0 | 518.3 | True | FAIL-OPEN-SILENT |
| PreToolUse | Write|Edit|MultiEdit|NotebookEdit | 0.0 | bash | .claude/hooks/fable-mirror-write-fence.sh | 3876 | True | 0 | 0 | 249.9 | True | FAIL-OPEN-SILENT |
| SessionStart | startup|resume | 0.0 | bash | sync-universal.sh | 9293 | True | None | None | None | False | SKIPPED-DESTRUCTIVE |
| SessionStart | startup|resume | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 429 | 643.1 | True | OK |
| SessionStart | startup|resume | 0.2 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 121229 | 9865.5 | True | OK |
| SessionStart | compact|clear | 1.0 | bash | .claude/hooks/post-compact-wake.sh | 10025 | True | 0 | 1622 | 1129.5 | True | OK |
| SessionStart | compact|clear | 1.1 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 630 | 1339.2 | True | OK |
| SessionStart | compact|clear | 1.2 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 429 | 563.0 | True | OK |
| SessionEnd | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 174 | 654.0 | True | OK |
| SessionEnd | None | 0.1 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 0 | 364.2 | True | FAIL-OPEN-SILENT |
| PostCompact | None | 0.0 | bash | .claude/hooks/py_closed.sh | 5441 | True | 0 | 429 | 739.8 | True | OK |
