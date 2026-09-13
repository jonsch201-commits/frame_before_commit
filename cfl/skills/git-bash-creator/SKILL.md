---
name: git-bash-creator
description: >-
  Creates a git bash (.sh) script file for a specific automation task. Use when Jon needs a shell
  script to sync files, set up a project, run a pipeline, or automate any file operation. Triggers
  include: "make a bash script", "create a sync script", "I need a shell script to...", "write a
  git bash file for...". Produces clean, readable, minimal bash — no unnecessary loops, no
  PowerShell. Explains every non-obvious line.
---

# Git Bash Creator

You are writing a bash script for Jon to run in Git Bash on Windows. Jon values legibility and learning — the script should teach as it executes.

---

## Principles

**Minimal over clever.** If 3 lines do the job, write 3 lines. Loops are only justified when the number of items is genuinely variable. For a fixed set of files, explicit copy commands are clearer than loops.

**Every non-obvious line gets a comment.** Jon is building knowledge. A script he can read is a script he can debug and improve.

**Fail loudly.** Use `set -e` at the top — stop on any error rather than continuing silently into a broken state.

**Portable paths.** On Windows Git Bash, `$HOME` is `C:\Users\YourName`. `~` works. `$USERPROFILE` does not — that's PowerShell. Use `$HOME` or `~`.

**Test before destructive operations.** Before removing or overwriting, check the source exists.

---

## Script Structure

Every script Jon needs follows this shape:

```bash
#!/bin/bash
# script-name.sh — one line description
# Usage: ./script-name.sh [optional args]
# What it does: 2-3 sentences max

set -e  # stop on error

# ── Configuration ──────────────────────────────
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # folder this script lives in
TARGET="$HOME/.claude"  # adjust per script

# ── Main ───────────────────────────────────────
echo "Starting: script-name"
echo "  From: $REPO_DIR"
echo "  To:   $TARGET"

# operations here

echo "Done."
```

The `$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)` line is the reliable way to get the folder the script lives in, regardless of where you run it from. Always use this — never hardcode paths.

---

## When to use cp vs rsync

**cp** — use when copying a known fixed set of files. Simple, readable, available everywhere.

```bash
cp "$REPO_DIR/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
```

**rsync** — use when syncing a whole directory where files may be added or deleted over time. The `--delete` flag removes files at the destination that no longer exist at the source.

```bash
rsync -a --delete "$REPO_DIR/skills/" "$HOME/.claude/skills/"
```

If rsync isn't available (uncommon in Git Bash but possible):
```bash
cp -r "$REPO_DIR/skills/." "$HOME/.claude/skills/"
```

Note the `/."` — this copies the *contents* of skills/, not the folder itself.

---

## Making directories safely

```bash
mkdir -p "$HOME/.claude/skills"
```

`-p` means: create all parent directories if needed, and don't error if it already exists. Always use `-p`.

---

## Execution Policy (Windows only)

Git Bash runs `.sh` files directly — no execution policy issue. But the file must be executable:

```bash
chmod +x script-name.sh
```

Run it:
```bash
./script-name.sh
```

Or from anywhere:
```bash
bash "/path/to/script-name.sh"
```

---

## Output format

When producing a script, always:
1. Show the complete script first
2. Explain any line that isn't obvious in plain English below it
3. State the exact command to run it
4. Note any one-time setup required (chmod, etc.)
