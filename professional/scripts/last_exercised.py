#!/usr/bin/env python3
"""last_exercised.py -- when was a capability LAST ACTUALLY RUN, machine-wide.

WHY THIS EXISTS
    The Secretary's capability-registry map (WAYFINDER-MAP-capability-registry-2026-08-24,
    b9cac79) put FOG-4 as possibly unmeasurable: "no instrument here can tell whether a
    file was READ."  It is measurable, by a different instrument than the one that was
    looked at.  Every Bash/PowerShell tool call on this machine is recorded in
    ~/.claude/projects/**/*.jsonl.  A script was EXERCISED iff its name appears inside a
    tool_use command string.  That is retroactive, machine-wide, and needs no registry.

    FOG-4 decides layer (A) vs (B) on their map -- "a path list is a phone book".  This
    supplies the column that stops it being a phone book.

THE TRAP THIS INSTRUMENT WAS BUILT AROUND, AND FELL INTO FIRST
    A NAME IN A TRANSCRIPT IS A MENTION, NOT AN EXECUTION.  Discussing a script puts its
    name in the corpus.  The naive grep -rl overcounts exercise by up to 16x (measured:
    `dream`, 552 files mention it, 35 ran it).  Worse, the FIRST run of this measurement
    reported every capability as last-exercised at the timestamp of the measuring command
    itself -- the probe's own Bash call named all nine targets, so the instrument
    registered ITSELF as an exercise of everything it was asking about.
      => --exclude-session is not a convenience.  It is the correctness fix.
      => Same class as the vocabulary-presence trap in the 2026-08-24 correction letter:
         a negative claim measured by name-presence self-falsifies when you write about it.

TWO BOUNDS, BOTH MEASURED, AND THE SECOND ONE INVERTS THE METRIC
    1. TOOL COVERAGE.  Only Bash and PowerShell tool_use records are read.  A Bash-only
       scan of index-check.ps1 missed 27 exec records in 5 files.  Both are scanned here;
       a third tool would be a third blind spot.
    2. HOOK-RUN SCRIPTS ARE INVISIBLE, AND THEY ARE THE BEST-AUTOMATED ONES.
       precompact-capture.sh, postcompact-brief.sh and lint_hook.sh are invoked from
       .claude/settings.json.  A hook invocation is NOT a tool_use record and can never
       appear here.  So the more thoroughly a capability is wired in, the LESS exercised
       it looks.  THE METRIC IS INVERTED FOR EXACTLY THE CASES YOU MOST WANT TO PASS.
       Hook-declared scripts are therefore reported in their own class, never as NEVER.

NOT WIRED TO A READER YET, AND THAT IS THIS SCRIPT'S OWN DEFECT.
    CFL: "a tenth instrument nobody opens is the defect wearing a lab coat."  This trunk
    already owns instance 5 of a-control-with-no-reader (exchange/letter-ledger.tsv, 265
    lines, dead since 08-17, no script reads it).  Wiring target is lint.sh C11, which
    already dereferences skill->script and prints the dead ones; this adds the
    when-last-run column.  Dated obligation in wiki/tracker/tracker.md, 2026-08-26.

USAGE
    python scripts/last_exercised.py --targets lint.sh dream retrieve.py
    python scripts/last_exercised.py --scan-scripts          # every script in scripts/
    python scripts/last_exercised.py --selftest
"""

import argparse
import collections
import glob
import json
import os
import re
import sys

# A SEARCH FOR A TOKEN CONTAINS THE TOKEN.  `grep -rl "dream"` names dream in a Bash
# command and is NOT an exercise of dream.  Measured 2026-08-24 after the Secretary's
# [SECRETARY] CLAUDE-STANDARDS 19: filtering these out collapses `dream` from 354 raw calls to 9,
# -97%, WORSE than the 94% collapse they measured on their own instruments.
# The unfiltered count produces FALSE GREENS -- a capability that was only ever grepped
# reads as alive -- which is the one measurement error with no reader.
SEARCH_VERBS = re.compile(
    r"\b(grep|rg|egrep|fgrep|find|ls|cat|head|tail|wc|sed|awk|sort|uniq|"
    r"Select-String|Get-ChildItem|Get-Content|test|stat|file|diff|cmp|"
    r"git\s+(log|grep|show|diff|status|add|commit|mv|rm))\b")
# An exercise needs the target in COMMAND POSITION -- not merely present in the text.
#
# THIS REPLACED A REGEX THAT WAS LARGELY INERT, 2026-08-24.  The old INTERP ended with
# a `.sh|.py|.ps1` alternative that fired on ANY mention followed by a space, so
# `echo "remember to update beta.sh tomorrow"` matched and counted as a run.
# MUTATION TESTING is what exposed it: switching the guard OFF killed no selftest,
# because no fixture depended on a guard that was already letting nearly everything
# through.  AN UNTESTED GUARD AND AN INERT GUARD LOOK IDENTICAL FROM THE OUTSIDE, AND
# BOTH REPORT GREEN.  This is the mutation score the 2026-08-24 re-derivation letter
# named as the external literature for "proven failable" -- applied to its own author.
INTERPRETERS = {"bash", "sh", "zsh", "python", "python3", "py", "pwsh",
                "powershell", "node", "source", "."}
_STRIP = "\"'`()"


def _runs(clause, target):
    """True iff `clause` puts `target` in COMMAND POSITION."""
    toks = clause.split()
    for i, tok in enumerate(toks):
        if target not in tok:
            continue
        if "=" in tok.split(target)[0]:
            continue                       # VAR=scripts/x.sh is an assignment, not a run
        bare = tok.strip(_STRIP)
        while bare[:2] in ("./", ".\\"):
            bare = bare[2:]
        if i == 0 and bare.endswith(target):
            return True                    # ./x.sh   .\x.ps1   x.sh
        if i > 0 and toks[i - 1].strip(_STRIP) in INTERPRETERS:
            return True                    # bash x.sh | python x.py
    return False


def _runs_anything(clause):
    """True iff the clause invokes SOMETHING -- used to judge a FLAG target."""
    toks = [t.strip(_STRIP) for t in clause.split()]
    return any(t in INTERPRETERS for t in toks) or bool(toks and toks[0].startswith("."))


def is_exercise(cmd, target, self_name="last_exercised"):
    """True iff `cmd` RAN `target`, rather than merely searching for it.

    Split on clause separators and judge only the clauses that name the target: a
    command can legitimately grep one thing and run another.
    """
    if self_name in cmd:
        return False                      # the instrument's own probe is not an exercise
    clauses = [c for c in re.split(r"[|;&" + chr(10) + r"]+", cmd) if target in c]
    if not clauses:
        return False
    if all(SEARCH_VERBS.search(c) for c in clauses):
        return False                      # searched, never run
    if target.startswith("-"):
        # A FLAG counts as used when it appears as a TOKEN in a clause that runs
        # something. A capability and its options have SEPARATE adoption curves --
        # the Secretary measured `--db` passed in ZERO of 58 retrieve.py runs.
        return any(target in c.split() and _runs_anything(c) for c in clauses)
    if not any(_runs(c, target) for c in clauses):
        return False                      # named, but nothing would have executed it
    return True

PROJECTS = os.path.expanduser("~/.claude/projects")
HOOK_SETTINGS = os.path.join(".claude", "settings.json")
EXEC_TOOLS = ("Bash", "PowerShell")


def hook_declared(settings_path=HOOK_SETTINGS):
    """Script names invoked from hooks. These can NEVER produce a tool_use record."""
    names = set()
    try:
        blob = open(settings_path, encoding="utf-8").read()
    except OSError:
        return names
    try:
        data = json.loads(blob)
    except ValueError:
        return names

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "command" and isinstance(v, str):
                    for tok in v.replace("\\", "/").split():
                        base = tok.rsplit("/", 1)[-1]
                        if "." in base:
                            names.add(base)
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    return names


def scan(targets, projects=PROJECTS, exclude_session=None):
    """Return {target: {mention_files, exec_files, exec_calls, last_ts}}.

    mention_files counts files where the NAME appears anywhere -- the naive signal.
    exec_files counts files carrying a Bash/PowerShell tool_use whose command names it.
    The gap between them is the naive method's error, and it is reported, not hidden.
    """
    stat = {t: {"mention_files": 0, "exec_files": 0, "exec_calls": 0,
                "raw_calls": 0, "last_ts": ""}
            for t in targets}
    scanned = skipped = unreadable = unparsed_lines = 0
    unreadable_names = []
    for path in glob.glob(os.path.join(projects, "**", "*.jsonl"), recursive=True):
        if exclude_session and exclude_session in path:
            skipped += 1
            continue
        try:
            blob = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            # A FILE THE GLOB ADMITTED AND THIS SCAN COULD NOT READ IS *UNKNOWN*, NOT ABSENT.
            # It used to `continue` here uncounted, so it appeared in NEITHER published number --
            # the summary prints "N scanned, M skipped as self-session" and a transient OSError on
            # a Drive mount put a file in neither class, silently. Four lines above, the
            # self-session skip DOES increment its counter: two enumerations of one rule, four
            # lines apart, and the second drifted to the weaker default.
            # Found 2026-09-01 by applying the Secretary's own discriminator to this trunk's
            # PYTHON after they found the identical shape (f.stat() OSError) in idle-beat.py.
            # The glob already admitted this path, so only the field extraction failed:
            # population EXCLUSION, not population definition.
            unreadable += 1
            unreadable_names.append(os.path.basename(path))
            continue
        scanned += 1
        hits = [t for t in targets if t in blob]
        if not hits:
            continue
        for t in hits:
            stat[t]["mention_files"] += 1
        seen = set()
        for line in blob.splitlines():
            if '"tool_use"' not in line:
                continue
            if not any(tool in line for tool in EXEC_TOOLS):
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                # Same class one level down: a line this scan cannot parse is UNKNOWN, and it is
                # counted rather than dropped so the exec-record figure carries its own bound.
                unparsed_lines += 1
                continue
            ts = rec.get("timestamp", "") or ""
            content = (rec.get("message", {}) or {}).get("content", []) or []
            for blk in content:
                if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                    continue
                if blk.get("name") not in EXEC_TOOLS:
                    continue
                cmd = str((blk.get("input") or {}).get("command", ""))
                for t in hits:
                    if t not in cmd:
                        continue
                    stat[t]["raw_calls"] += 1
                    if not is_exercise(cmd, t):
                        continue
                    seen.add(t)
                    stat[t]["exec_calls"] += 1
                    if ts > stat[t]["last_ts"]:
                        stat[t]["last_ts"] = ts
        for t in seen:
            stat[t]["exec_files"] += 1
    return stat, scanned, skipped, unreadable, unreadable_names, unparsed_lines


def report(stat, hooks, out=sys.stdout):
    out.write("%-24s %8s %8s %7s %7s %8s  %s\n" %
              ("capability", "M-files", "RAN-fil", "RAN", "naive", "collapse",
               "LAST EXERCISED (UTC)"))
    n_never = n_hookonly = 0
    for t in sorted(stat):
        s = stat[t]
        m, e = s["mention_files"], s["exec_files"]
        naive = ("%dx" % round(m / e)) if e else "INF"
        if s["last_ts"]:
            when = s["last_ts"][:19]
        elif t in hooks:
            when = "HOOK-RUN -- unmeasurable by design, NOT never"
            n_hookonly += 1
        else:
            when = "-- NEVER EXERCISED --"
            n_never += 1
        raw_n = s["raw_calls"]
        coll = ("-%d%%" % round(100 * (raw_n - s["exec_calls"]) / raw_n)) if raw_n else "--"
        out.write("%-24s %8d %8d %7d %7s %8s  %s\n"
                  % (t, m, e, s["exec_calls"], naive, coll, when))
    out.write("\n")
    out.write("  M-files = files MENTIONING it. RAN-fil = files that ACTUALLY RAN it.\n")
    out.write("  'naive' = how badly a grep -rl would overstate exercise (M-files / RAN-fil).\n")
    out.write("  'collapse' = share of raw name-hits that were SEARCH traffic, not runs.\n")
    out.write("  A LARGE collapse means the raw count was never a count. Measured: dream -97%.\n")
    if n_hookonly:
        out.write("  %d capability(ies) are HOOK-RUN: invisible here BECAUSE they are wired in.\n"
                  % n_hookonly)
        out.write("  THE METRIC INVERTS FOR THE BEST-AUTOMATED CASES. Do not read those as dead.\n")
    return n_never, n_hookonly


# --------------------------------------------------------------------------- selftest

def _seed(tmp, name, records):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    return path


def _rec(tool, cmd, ts):
    return {"timestamp": ts, "message": {"content": [
        {"type": "tool_use", "name": tool, "input": {"command": cmd}}]}}


def _text(body, ts):
    return {"timestamp": ts, "message": {"content": [{"type": "text", "text": body}]}}


def selftest():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="lastex-")
    fails = []
    try:
        _seed(tmp, "a.jsonl", [
            _text("we should really run alpha.sh someday", "2026-01-01T00:00:00Z"),
            _rec("Bash", "bash scripts/beta.sh --apply", "2026-01-02T00:00:00Z"),
        ])
        _seed(tmp, "b.jsonl", [
            _text("alpha.sh is a great idea", "2026-01-03T00:00:00Z"),
            _rec("PowerShell", ".\\gamma.ps1", "2026-01-04T00:00:00Z"),
        ])
        _seed(tmp, "self.jsonl", [
            # A REAL execution by the probing session. Was a `grep` until 2026-08-24,
            # which the RAN filter now excludes by itself -- so the fixture had quietly
            # stopped testing the exclusion it exists for. A selftest can rot into a
            # tautology when a DIFFERENT guard starts catching its fixture first.
            _rec("Bash", "bash alpha.sh --apply", "2026-06-06T00:00:00Z"),
        ])
        _seed(tmp, "searched.jsonl", [
            _rec("Bash", "grep -rl 'beta.sh' wiki/", "2026-01-05T00:00:00Z"),
            _rec("Bash", "ls -la scripts/beta.sh; wc -c < scripts/beta.sh",
                 "2026-01-06T00:00:00Z"),
        ])
        targets = ["alpha.sh", "beta.sh", "gamma.ps1", "delta.sh"]

        st, _, _, _unread, _unames, _unpl = scan(targets, projects=tmp, exclude_session="self")

        # S1 -- a MENTION is not an EXECUTION. This is the whole point of the instrument.
        if st["alpha.sh"]["mention_files"] != 2 or st["alpha.sh"]["exec_files"] != 0:
            fails.append("S1 mention-is-not-execution: got M=%d E=%d, want 2/0"
                         % (st["alpha.sh"]["mention_files"], st["alpha.sh"]["exec_files"]))
        # S2 -- a real Bash execution is found, with its timestamp.
        if st["beta.sh"]["exec_files"] != 1 or not st["beta.sh"]["last_ts"].startswith("2026-01-02"):
            fails.append("S2 bash-exec: got E=%d ts=%r"
                         % (st["beta.sh"]["exec_files"], st["beta.sh"]["last_ts"]))
        # S3 -- PowerShell is scanned too. A Bash-only scan missed 27 real records.
        if st["gamma.ps1"]["exec_files"] != 1:
            fails.append("S3 powershell-exec: got E=%d, want 1" % st["gamma.ps1"]["exec_files"])
        # S4 -- absent capability returns NEVER, not a false positive.
        #       Was DECORATIVE until 2026-08-24: no mutant could kill it, because it
        #       only asserted zeros and any broken scan still returns zeros for a name
        #       that appears nowhere. Now it also asserts the POSITIVE control in the
        #       same breath, so a scan that stops finding anything fails here too.
        if st["delta.sh"]["mention_files"] or st["delta.sh"]["exec_files"]:
            fails.append("S4 absent-is-never: got M=%d E=%d"
                         % (st["delta.sh"]["mention_files"], st["delta.sh"]["exec_files"]))
        if st["beta.sh"]["mention_files"] == 0:
            fails.append("S4 positive control dead: an all-zeros scan would pass S4 "
                         "silently, which is what made it decorative")
        # S9 -- AN UNREADABLE FILE IS *COUNTED*, NOT DROPPED. Added 2026-09-01 after the
        #       Secretary found the identical shape (f.stat() OSError, bare continue) in their
        #       own idle-beat.py and this scan turned out to carry it too: a file the glob
        #       ADMITTED and open() could not read appeared in NEITHER published number.
        #       Both directions asserted, because an untested guard and an inert guard look
        #       identical and both report green.
        _unreadable_dir = os.path.join(tmp, "unreadable-probe")
        os.makedirs(_unreadable_dir, exist_ok=True)
        _bad = os.path.join(_unreadable_dir, "cannot-open.jsonl")
        _real_open_setup = open
        _real_open_setup(_bad, "w", encoding="utf-8").write("{}" + chr(10))
        _real_open = open

        def _open_that_fails(path, *args, **kwargs):
            if str(path).endswith("cannot-open.jsonl"):
                raise OSError("seeded stat/open failure for S9")
            return _real_open(path, *args, **kwargs)

        import builtins as _bi
        _bi.open = _open_that_fails
        try:
            _st9, _sc9, _sk9, _unread9, _unames9, _unpl9 = scan(
                targets, projects=_unreadable_dir, exclude_session=None)
        finally:
            _bi.open = _real_open
        if _unread9 != 1:
            fails.append("S9 unreadable-is-counted: a file open() could not read did NOT reach "
                         "the unreadable counter (got %d, want 1) -- it left the population "
                         "silently, which is the defect this counter exists to end" % _unread9)
        if "cannot-open.jsonl" not in _unames9:
            fails.append("S9 unreadable-is-NAMED: counted but not named (%r) -- a finding you "
                         "cannot locate is not a finding" % (_unames9,))
        # POSITIVE CONTROL: on a readable corpus the counter must be ZERO, or it is a counter
        # that always fires and proves nothing.
        _st9b, _sc9b, _sk9b, _unread9b, _un9b, _up9b = scan(
            targets, projects=tmp, exclude_session=None)
        if _unread9b != 0:
            fails.append("S9 positive control: unreadable counter fired on a fully readable "
                         "corpus (got %d, want 0) -- a counter that always fires is not a "
                         "measurement" % _unread9b)

        # S5 -- SELF-CONTAMINATION. The bug that actually happened: without the exclusion
        #       the probe's own command counts as an exercise of what it searched for.
        st2, _, skipped, _u2, _un2, _up2 = scan(targets, projects=tmp, exclude_session=None)
        if skipped != 0:
            fails.append("S5 setup: expected 0 skipped when not excluding, got %d" % skipped)
        if st2["alpha.sh"]["exec_files"] != 1:
            fails.append("S5 self-contamination NOT REPRODUCED -- the guard is untested; "
                         "got E=%d, want 1" % st2["alpha.sh"]["exec_files"])
        st3, _, skipped3, _u3, _un3, _up3 = scan(targets, projects=tmp, exclude_session="self")
        if skipped3 != 1 or st3["alpha.sh"]["exec_files"] != 0:
            fails.append("S5 exclusion did not fix it: skipped=%d E=%d"
                         % (skipped3, st3["alpha.sh"]["exec_files"]))
        # S7 -- A SEARCH FOR A TOKEN CONTAINS THE TOKEN. Two commands NAME beta.sh and
        #       neither RUNS it. Counting them is how a capability that was only ever
        #       grepped reads as alive -- a FALSE GREEN, the error with no reader.
        #       Measured on the live corpus: `dream` 354 raw calls -> 9 real runs, -97%.
        if not is_exercise("bash scripts/beta.sh --apply", "beta.sh"):
            fails.append("S7 real run rejected")
        for probe in ("grep -rl 'beta.sh' wiki/",
                      "ls -la scripts/beta.sh",
                      "wc -c < scripts/beta.sh",
                      "git log --oneline -- scripts/beta.sh"):
            if is_exercise(probe, "beta.sh"):
                fails.append("S7 SEARCH counted as exercise: %r" % probe)
        # a command may legitimately grep one thing and run another in the same line
        if not is_exercise("grep -c x foo.txt; bash scripts/beta.sh", "beta.sh"):
            fails.append("S7 mixed clause: run-alongside-grep was rejected")

        # S8 -- A CAPABILITY AND ITS OPTION HAVE SEPARATE ADOPTION CURVES.
        #       Secretary [relayed+]: retrieve.py was run 58 times and NOT ONCE with
        #       --db. A registry that cannot say THE FLAG IS COLD WHILE THE TOOL IS WARM
        #       reports a half-adopted capability as adopted.
        if not is_exercise("python scripts/retrieve.py --db wiki.db", "--db"):
            fails.append("S8 flag-as-target not measurable")
        if is_exercise("python scripts/retrieve.py", "--db"):
            fails.append("S8 absent flag counted as used")

        # S9 -- THE INTERPRETER REQUIREMENT, which had NO test until 2026-08-24.
        #       Found by mutation: switching INTERP off killed nothing. S7's fixtures
        #       were all caught by SEARCH_VERBS first, so the second guard was
        #       undefended -- the rotted-fixture class, found mechanically this time
        #       instead of by luck of ordering.
        if is_exercise('echo "remember to update beta.sh tomorrow"', "beta.sh"):
            fails.append("S9 named-with-no-interpreter counted as a run")
        if is_exercise("BETA=scripts/beta.sh", "beta.sh"):
            fails.append("S9 assignment counted as a run")

        # S10 -- THE SELF-NAME EXCLUSION, likewise untested until mutation found it.
        #        The probe naming a target inside its own command is not an exercise
        #        of that target: the bug this instrument actually shipped with.
        if is_exercise("python scripts/last_exercised.py --targets beta.sh", "beta.sh"):
            fails.append("S10 the probe's own command counted as an exercise")
        if not is_exercise("bash scripts/beta.sh", "beta.sh"):
            fails.append("S10 over-applied: a real run was suppressed")

        # S6 -- a hook-declared script must NOT be reported as NEVER. Reporting the
        #       best-wired capability as dead is the worst available direction.
        settings = os.path.join(tmp, "settings.json")
        with open(settings, "w", encoding="utf-8") as fh:
            json.dump({"hooks": {"SessionStart": [
                {"hooks": [{"command": "bash scripts/delta.sh"}]}]}}, fh)
        hooks = hook_declared(settings)
        if "delta.sh" not in hooks:
            fails.append("S6 hook parse: delta.sh not found in %r" % sorted(hooks))
        else:
            import io
            buf = io.StringIO()
            n_never, n_hook = report({k: st[k] for k in ["delta.sh"]}, hooks, out=buf)
            if n_never != 0 or n_hook != 1:
                fails.append("S6 hook-run misclassified: never=%d hookonly=%d" % (n_never, n_hook))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print("FAIL " + f)
    print("SELFTEST %d/10 %s" % (10 - len(fails), "PASS" if not fails else "FAIL"))
    print()
    print("BOUND: S1/S3/S5/S6/S7 have DEMONSTRATED failures. S1, S5 and S7 are bugs this")
    print("       instrument actually shipped with -- S7 is the worst of them: for four hours")
    print("       it counted `grep dream` as an exercise of dream and published the number.")
    print("       S3/S6 are the two measured blind spots. S2/S4/S8 are asserted only.")
    print("BOUND: this proves the SCANNER. It does not prove that exec-in-a-transcript equals")
    print("       'the capability still works'. A capability can be exercised and broken.")
    return 1 if fails else 0


# --------------------------------------------------------------------------- mutate
#
# A SELFTEST CAN ROT WHEN A DIFFERENT GUARD STARTS CATCHING ITS FIXTURE FIRST, AND IT
# ROTS GREEN.  Measured here 2026-08-24: S5's fixture was a `grep`; when the search-verb
# filter was added it caught that fixture first, and S5 silently stopped testing the
# --exclude-session guard it exists for.  It went red only by luck of ordering.
#
# AND THE ROT MOVES.  Repairing the command-position guard made it strong enough to catch
# S7's search fixtures, at which point the SEARCH-VERB guard became the untested one.
# Strengthening any guard can silently retire another guard's fixtures. This is not a
# one-off to fix; it is an equilibrium to re-measure.
#
# BOUND, STATED BECAUSE THE SCORE INVITES THE WRONG READING: an unkilled mutant means the
# guard is REDUNDANT FOR THE CURRENT FIXTURES.  It does NOT distinguish belt-and-braces
# from inert.  The old INTERP regex was INERT and looked exactly like this.  Chasing the
# score to 10/10 by adding mutants until it passes is the tuning defect, not the fix.

def _mutants():
    """name -> f(module) that disables exactly one guard."""
    def off_search(m):
        m.SEARCH_VERBS = re.compile(r"(?!x)x")

    def off_position(m):
        m._runs = lambda clause, target: True

    def off_selfname(m):
        orig = m.is_exercise
        m.is_exercise = lambda c, t, s=chr(0): orig(c, t, s)

    def off_powershell(m):
        m.EXEC_TOOLS = ("Bash",)

    def off_hooks(m):
        m.hook_declared = lambda *a, **k: set()

    def off_exclusion(m):
        orig = m.scan
        m.scan = (lambda t, projects=None, exclude_session=None:
                  orig(t, projects=projects, exclude_session=None))

    def off_everything(m):
        m.is_exercise = lambda c, t, s="last_exercised": True

    def off_mentions(m):
        orig = m.scan

        def patched(t, projects=None, exclude_session=None):
            st, a, b = orig(t, projects=projects, exclude_session=exclude_session)
            for k in st:
                st[k]["mention_files"] = 0
            return st, a, b
        m.scan = patched

    return [("search-verb filter", off_search),
            ("command-position test", off_position),
            ("self-name exclusion", off_selfname),
            ("PowerShell in EXEC_TOOLS", off_powershell),
            ("hook-declared parser", off_hooks),
            ("--exclude-session", off_exclusion),
            ("mention counting", off_mentions),
            ("is_exercise entirely", off_everything)]


def mutate():
    """Disable each guard in turn; report which selftests notice."""
    import contextlib
    import importlib.util
    import io as _io

    spec = importlib.util.spec_from_file_location("_lx_mut", os.path.abspath(__file__))

    def fresh():
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def failures(mod):
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            mod.selftest()
        return set(re.findall(r"FAIL (S\d+)", buf.getvalue()))

    base = failures(fresh())
    if base:
        print("REFUSING TO SCORE: the suite is already RED (%s)." % ", ".join(sorted(base)))
        print("A mutation score against a failing baseline is meaningless.")
        return 2

    killed, n_killed, undef = set(), 0, []
    for name, mut in _mutants():
        mod = fresh()
        mut(mod)
        try:
            got = failures(mod) - base
        except Exception:
            got = {"(crash)"}
        if got:
            n_killed += 1
        else:
            undef.append(name)
        killed |= got
        print("  %-26s %s" % (name + " OFF",
                              ("caught by " + ", ".join(sorted(got))) if got
                              else "!! NOTHING NOTICES -- guard is UNDEFENDED"))
    total = len(_mutants())
    print()
    print("MUTATION SCORE: %d/%d guards defended by at least one selftest." % (n_killed, total))
    if undef:
        print("UNDEFENDED: %s" % ", ".join(undef))
        print("  An undefended guard is REDUNDANT FOR THE CURRENT FIXTURES. That is NOT the")
        print("  same as harmless: an INERT guard looks exactly like this, and one already did.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--targets", nargs="*", default=None)
    ap.add_argument("--scan-scripts", action="store_true",
                    help="use every file in scripts/ as a target")
    ap.add_argument("--projects", default=PROJECTS)
    ap.add_argument("--exclude-session", default=None,
                    help="substring of the CURRENT session id; omit it and the probe "
                         "counts itself as an exercise of everything it searches for")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mutate", action="store_true",
                    help="disable each guard in turn; report which selftests notice")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.mutate:
        return mutate()

    targets = list(a.targets or [])
    if a.scan_scripts:
        for p in sorted(glob.glob(os.path.join("scripts", "*"))):
            if os.path.isfile(p):
                targets.append(os.path.basename(p))
    targets = sorted(set(targets))
    if not targets:
        ap.error("give --targets or --scan-scripts")

    stat, scanned, skipped, unreadable, unreadable_names, unparsed_lines = scan(targets, projects=a.projects,
                                  exclude_session=a.exclude_session)
    print("corpus: %d jsonl scanned, %d skipped as self-session, "
          "%d UNREADABLE (open failed -- UNKNOWN, not absent%s), "
          "%d unparseable line(s) inside readable files"
          % (scanned, skipped, unreadable,
             (": " + ", ".join(unreadable_names[:5])) if unreadable_names else "",
             unparsed_lines))
    if unreadable:
        print("  WARNING: %d file(s) left the population without appearing in either the scanned "
              "or the skipped count until 2026-09-01. A figure below is a claim about what could "
              "be READ, not about what EXISTS." % unreadable)
    if not a.exclude_session:
        print("WARNING: --exclude-session not given. If this session has already named a")
        print("WARNING: target in a command, that self-reference is counted as an exercise.")
    print()
    report(stat, hook_declared())
    return 0


if __name__ == "__main__":
    sys.exit(main())
