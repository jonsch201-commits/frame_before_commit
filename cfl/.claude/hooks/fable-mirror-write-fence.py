#!/usr/bin/env python
# fable-mirror-write-fence.py — mechanical Write-fence evaluator for the fable-mirror subagent.
#
# PURPOSE
#   fable-mirror (.claude/agents/fable-mirror.md) holds the Write tool but is charter-bound
#   (prose only) to write nothing except escalation packets under wiki/intake-triage/ — the
#   single OUT-crossing of its membrane. Agent-def frontmatter cannot path-scope a granted
#   tool, so that fence is prose-only. This PreToolUse evaluator makes it MECHANICAL: it
#   blocks (exit 2) any Write/Edit/MultiEdit/NotebookEdit issued BY fable-mirror whose
#   resolved target is outside wiki/intake-triage/.
#
# SCOPING (the crux)
#   Per CC docs, PreToolUse input carries `agent_type`, which for a custom subagent is the
#   frontmatter `name` field. This evaluator ENFORCES only when agent_type == "fable-mirror".
#   For every other caller (other agents; the main thread, where the field is absent) it
#   exits 0 and leaves normal permission flow untouched. That is the whole guarantee: the
#   fence is scoped to one agent by identity, not applied repo-wide.
#
# POSTURE
#   Fail-closed for fable-mirror: unparseable input, missing path, or missing anchor => block.
#
# Docs verified 2026-07-22 at code.claude.com/docs/en/hooks:
#   - PreToolUse stdin: tool_name, tool_input (file_path for file tools / notebook_path for
#     NotebookEdit), cwd, and inside a subagent agent_id + agent_type.
#   - Exit 2 => blocking error; stderr is returned to the model; the tool call is prevented.
#   - CLAUDE_PROJECT_DIR is exported to all hook command processes.

import sys, os, json

GUARDED_AGENT = "fable-mirror"
ALLOWED_SUBDIR = os.path.join("wiki", "intake-triage")


def block(detail):
    sys.stderr.write("fable-mirror write-fence: BLOCKED. " + detail + "\n")
    sys.stderr.write(
        "fable-mirror may Write only under wiki/intake-triage/ "
        "(its single membrane OUT-crossing). Re-target the escalation packet there.\n"
    )
    sys.exit(2)


def main():
    raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except Exception:
        # Cannot parse. Only fail closed if it looks like a fable-mirror call; otherwise
        # never interfere with other callers.
        if '"fable-mirror"' in raw and "agent_type" in raw:
            block("unparseable PreToolUse input for a fable-mirror call")
        sys.exit(0)

    if data.get("agent_type") != GUARDED_AGENT:
        sys.exit(0)  # not fable-mirror -> defer to normal permission flow

    tool = data.get("tool_name", "")
    tinput = data.get("tool_input") or {}
    path = tinput.get("file_path") or tinput.get("notebook_path") or ""
    cwd = data.get("cwd") or ""
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")

    if not path:
        block("no target path in tool_input for %s" % (tool or "write"))
    if not proj:
        block("CLAUDE_PROJECT_DIR unset; cannot anchor the allow-root")

    # Resolve relative paths against the tool call's cwd (falling back to project root).
    if not os.path.isabs(path):
        path = os.path.join(cwd or proj, path)

    # normpath collapses '.' and '..' without touching the filesystem (Write creates the
    # file, so it may not exist yet). normcase makes the compare case-insensitive and
    # separator-insensitive, matching the Windows filesystem.
    target = os.path.normcase(os.path.normpath(os.path.abspath(path)))
    allow = os.path.normcase(
        os.path.normpath(os.path.abspath(os.path.join(proj, ALLOWED_SUBDIR)))
    )

    if target == allow or target.startswith(allow + os.sep):
        sys.exit(0)  # inside the allow-root -> permitted

    block("%s -> %s resolves outside wiki/intake-triage/" % (tool or "write", target))


if __name__ == "__main__":
    main()
