#!/usr/bin/env python3
"""check_memory_refs.py — resolve every file path a memory names, and FLAG the ones that are gone.

⛔ WHY THIS EXISTS (ticket M-3). Memories record what was true WHEN WRITTEN. Several name specific
scripts, flags and fields — `cc_corpus_gap.py`, `convert-export.py:812`, `RATIO_FLOOR`,
`cleanupPeriodDays`. Nothing verifies any of them, and a memory is loaded into context at session
open where it reads as current fact. A memory naming a script that was renamed six weeks ago is
worse than no memory: it sends a session to a path that does not exist and the failure looks like
the session's own mistake.

⚠️ FLAG, NEVER DELETE. Jon's standing ruling is "Yeah no deletion." A dead reference is EVIDENCE —
it usually means a migration half-landed, which is a defect in the repo, not in the memory. This
script writes nothing and removes nothing. It prints.

⭐ AND IT REPORTS ITS OWN BOUND, which is the part that keeps a green from lying. A checker over
free prose cannot decide what is a path; it can only decide what is path-SHAPED. So it prints, next
to the failures, HOW MANY backticked tokens it declined to test and why. "0 unresolvable" then reads
as "0 of the N I could test", never as "the memories are clean" — the distinction that turned a
`source_id:` field-name mismatch into a published 29-session 'permanently lost' registry.

Usage:  python scripts/audit/check_memory_refs.py [--memory-dir DIR] [--strict] [--self-test]
Exit:   0 clean, 1 unresolvable references found (--strict only), 2 the memory dir is unreachable.
"""
import argparse
import os
import re
import sys

# Windows consoles default to cp1252 and this file's own output contains ⛔/⚠️/⭐. Without this the
# script dies MID-REPORT, after printing the counts and before printing the failures — the worst
# possible place, because the numbers look like a completed run.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HOME = os.path.expanduser("~")
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_MEM = os.path.join(
    HOME, ".claude", "projects",
    "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer", "memory")

# Roots a bare relative path may be written against. ORDER IS NOT PRECEDENCE — a hit in ANY root
# resolves the reference, because a memory saying `settings.json` is not claiming a location.
ROOTS = [REPO, os.path.join(HOME, ".claude"), HOME]

EXTS = (".py", ".sh", ".ps1", ".md", ".json", ".jsonl", ".yaml", ".yml", ".txt", ".r", ".sql")

# ⛔ EVERY SKIP REASON IS PRINTED. A silent skip is how a screen shrinks its own denominator without
# anyone noticing — the class this repo has hit with `md✗`, with RATIO_FLOOR, and with a deny list
# that was applied and never verified.
def classify(tok):
    """Returns (kind, reason). kind is 'test' or 'skip'."""
    t = tok.strip()
    if not t:
        return "skip", "empty"
    if t.startswith(("http://", "https://", "git@")):
        return "skip", "URL, not a local path"
    if "..." in t or "…" in t:
        return "skip", "elided path — cannot be resolved by construction"
    if re.match(r"^[%$]", t) or "%" in t:
        return "skip", "environment-variable path — expands per machine"
    if "*" in t or "?" in t or "<" in t:
        return "skip", "glob or placeholder, not a concrete path"
    if "[" in t or "]" in t:
        return "skip", "bracketed notation, not a filename"
    if re.match(r"^(read|run|see|use|open|check|grep|cat|edit)\s", t, re.I):
        return "skip", "prose instruction that happens to contain a path"
    # ⛔ SECOND OVER-REPORT, same run: SHELL COMMANDS. `git log origin/main`,
    # `echo {} | route_agent_return.py`, `git checkout -b build/…` all contain a `/` and were
    # reported DEAD. They are invocations, not files. ⭐ Two false-positive classes in one first
    # run, both found by reading the list rather than trusting the count.
    if re.match(r"^(git|echo|python|python3|bash|sh|docker|cd|find|sed|awk|npm|node|pwsh|"
                r"powershell|sha256sum|wc|cp|mv|ls|gh|schtasks)\b", t, re.I):
        return "skip", "shell command, not a path"
    if "|" in t or t.startswith("-"):
        return "skip", "command fragment (pipe or flag), not a path"
    if re.match(r"^[a-z0-9.-]+\.(com|org|net|io|dev)(/|$)", t, re.I):
        return "skip", "domain/URL without a scheme"
    if t.startswith("/") and "/" not in t[1:] and not t.lower().endswith(EXTS):
        return "skip", "slash-command, not a path"
    if t.startswith(".") and "/" not in t and "\\" not in t:
        return "skip", "bare extension, names a file TYPE not a file"
    has_sep = "/" in t or "\\" in t
    if not (has_sep or t.lower().endswith(EXTS)):
        return "skip", "not path-shaped"
    return "test", ""


LINEREF = re.compile(r":\d+(?:-\d+)?$")


def resolve(tok):
    """True if the path exists under any root (or absolutely). Trailing :NN is stripped first."""
    p = LINEREF.sub("", tok).rstrip("/\\").replace("\\", "/")
    if not p:
        return False
    if os.path.isabs(p) or re.match(r"^[A-Za-z]:", p):
        return os.path.exists(p)
    if any(os.path.exists(os.path.join(r, p)) for r in ROOTS):
        return True
    # ⛔ THE FIRST RUN OF THIS SCRIPT REPORTED 88 DEAD OF 194 AND MOST OF IT WAS THIS.
    # A memory writing `CARRIER.md`, `SCHEMA.md` or `agent_end_ingest.py` is naming a FILE, not
    # asserting it sits at the repo root — every one of those exists, one or two directories down.
    # Root-relative resolution alone therefore reported real, current files as dead, and a report
    # that is mostly false positives gets skimmed, which is the same end state as no report.
    # ⭐ This is the "first-run numbers are hypotheses" pattern exactly: the over-report arrived in
    # the direction this file's own docstring warned about, and it was caught by READING the list
    # instead of publishing the count.
    # ⚠️ A basename hit is WEAKER evidence than a path hit — it proves a file of that name exists
    # somewhere, not that the memory's file does. It is the right call anyway: the alternative is
    # flagging live files, and the failure this script exists to catch is a name that is GONE.
    if "/" not in p and "\\" not in p:
        return os.path.basename(p).lower() in _basenames()
    # ⭐ GIT REFS. `integration/mirror-pipeline-2026-07-21` and `build/pocock-incorporation-plan`
    # are branch names — slash-shaped, extension-free, and NOT files. A branch that still exists is
    # a live reference and reporting it as a dead path is simply wrong. Resolved against the real
    # ref list rather than pattern-guessed, so a DELETED branch still flags, which is the case worth
    # catching: a memory pointing at a merged-and-pruned branch is stale in exactly the way M-3 means.
    if "." not in os.path.basename(p) and p.lower() in _gitrefs():
        return True
    return False


_REFS = None


def _gitrefs():
    global _REFS
    if _REFS is None:
        import subprocess
        _REFS = set()
        try:
            out = subprocess.run(["git", "-C", REPO, "for-each-ref", "--format=%(refname:short)"],
                                 capture_output=True, text=True, timeout=60)
            for line in out.stdout.splitlines():
                line = line.strip()
                if line:
                    _REFS.add(line.lower())
                    _REFS.add(line.split("/", 1)[-1].lower() if line.startswith("origin/") else line.lower())
        except Exception:
            # ⚠️ UNKNOWN, not empty: if git cannot be reached, every ref reads as dead. Say so.
            print("  ⚠️  git ref list unavailable — branch-shaped references may over-report")
    return _REFS


_BN = None


def _basenames():
    """Every filename in the repo and in ~/.claude, lowercased. Built once."""
    global _BN
    if _BN is None:
        _BN = set()
        for root in (REPO, os.path.join(HOME, ".claude")):
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames
                               if d not in (".git", "node_modules", "__pycache__", ".venv")]
                for f in filenames:
                    _BN.add(f.lower())
    return _BN


def scan(mem_dir):
    files = sorted(f for f in os.listdir(mem_dir) if f.endswith(".md"))
    tested, skipped, dead = {}, {}, []
    for fn in files:
        path = os.path.join(mem_dir, fn)
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for n, line in enumerate(fh, 1):
                for tok in re.findall(r"`([^`]+)`", line):
                    kind, reason = classify(tok)
                    if kind == "skip":
                        skipped.setdefault(reason, set()).add(tok)
                        continue
                    tested.setdefault(tok, []).append((fn, n))
    for tok, sites in sorted(tested.items()):
        if not resolve(tok):
            dead.append((tok, sites))
    return files, tested, skipped, dead


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--memory-dir", default=DEFAULT_MEM)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when unresolvable references exist")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    if not os.path.isdir(a.memory_dir):
        print(f"⛔ UNKNOWN — memory dir unreachable: {a.memory_dir}", file=sys.stderr)
        print("   A check that could not run is UNKNOWN, never a pass.", file=sys.stderr)
        return 2

    files, tested, skipped, dead = scan(a.memory_dir)
    n_skip = sum(len(v) for v in skipped.values())
    print("=== check_memory_refs ===")
    print(f"  memory dir : {a.memory_dir}")
    print(f"  files      : {len(files)}")
    print(f"  tested     : {len(tested)} distinct path-shaped references")
    print(f"  resolved   : {len(tested) - len(dead)}")
    print(f"  UNRESOLVED : {len(dead)}")
    print()
    if dead:
        print("  ⚠️  These are FLAGGED, not deleted. A dead reference usually means a migration")
        print("      half-landed — that is a defect in the repo, not in the memory.")
        for tok, sites in dead:
            where = ", ".join(f"{f}:{n}" for f, n in sites[:3])
            print(f"      DEAD  {tok}")
            print(f"            named in {where}")
        print()
    # ⭐ THE BOUND, printed whether or not anything failed. This is the line that stops a clean run
    # from reading as "the memories are clean".
    print(f"  ⚠️  BOUND: {n_skip} distinct backticked tokens were NOT tested. This report is")
    print(f"      '{len(dead)} dead of {len(tested)} testable', NEVER 'the memories are accurate'.")
    for reason, toks in sorted(skipped.items(), key=lambda kv: -len(kv[1])):
        print(f"        {len(toks):>4}  {reason}")
    print()
    print("  ⛔ NOT COVERED AT ALL, and naming it is the point: SYMBOLS. A memory naming a flag,")
    print("     a field or a function — RATIO_FLOOR, cleanupPeriodDays, source_id: — is skipped as")
    print("     'not path-shaped'. Those are exactly the references that went stale on this repo")
    print("     before (a field name mismatch produced a published 'permanently lost' registry),")
    print("     and resolving them needs a language-aware pass this script does not attempt.")
    return 1 if (dead and a.strict) else 0


def self_test():
    """Fixtures for the two things that can silently break: what gets TESTED and what gets SKIPPED."""
    import tempfile
    fails = []
    cases_skip = [
        ("https://example.com/x.md", "URL"),
        (".../scratchpad/thing/", "elided"),
        ("%LOCALAPPDATA%\\cfl-lanes\\snap.json", "env var"),
        (".claude/agents/*.md", "glob"),
        ("/teach", "slash-command"),
        (".jsonl", "bare extension"),
        ("RATIO_FLOOR", "symbol, not path-shaped"),
    ]
    for tok, label in cases_skip:
        if classify(tok)[0] != "skip":
            fails.append(f"{label}: '{tok}' should be SKIPPED, was tested")
    for tok, label in [("scripts/audit/check_memory_refs.py", "repo-relative path"),
                       ("CLAUDE.md", "bare filename with a known extension"),
                       ("settings.json", "resolves under ~/.claude, not the repo")]:
        if classify(tok)[0] != "test":
            fails.append(f"{label}: '{tok}' should be TESTED, was skipped")

    # A real file must resolve; a plausible-looking dead one must not. ⭐ Both halves: a resolver
    # that returns True for everything passes the first test alone.
    if not resolve("scripts/audit/check_memory_refs.py"):
        fails.append("a file that exists did not resolve")
    if resolve("scripts/audit/this-file-does-not-exist-9f3a.py"):
        fails.append("a file that does not exist resolved — the resolver is not discriminating")
    # Trailing line refs must be stripped, or every `file.md:25-26` citation reads as dead.
    if not resolve("scripts/audit/check_memory_refs.py:12-14"):
        fails.append("a :line-range suffix was not stripped before resolution")

    # End-to-end over a fixture dir, so the reporting path itself is exercised.
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, "m.md"), "w", encoding="utf-8") as fh:
            fh.write("names `CLAUDE.md` and `scripts/audit/gone-forever-8b21.py` and `/teach`\n")
        _f, tested, skipped, dead = scan(td)
        if len(dead) != 1:
            fails.append(f"fixture: expected exactly 1 dead ref, got {len(dead)}")
        if len(tested) != 2:
            fails.append(f"fixture: expected 2 testable refs, got {len(tested)}")
        if not skipped:
            fails.append("fixture: the skip ledger was empty — the bound would print as zero")

    print("=== SELF-TEST — check_memory_refs.py ===")
    if fails:
        for f in fails:
            print(f"  FAIL: {f}")
        print(f"\nRESULT: FAIL — {len(fails)} failure(s)")
        return 1
    checks = [
        "URLs, elisions, env vars, globs, slash-commands, bare exts skipped",
        "symbols skipped and counted, never silently dropped",
        "repo-relative and ~/.claude-relative paths are tested",
        "an existing file resolves",
        "a non-existent file does NOT resolve (resolver discriminates)",
        "a trailing :line or :line-range is stripped before resolving",
        "end-to-end scan reports 1 dead of 2 testable, with a non-empty bound",
    ]
    for c in checks:
        print(f"  {c:<62}: PASS")
    print(f"\nRESULT: PASS — {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
