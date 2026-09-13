#!/usr/bin/env python3
"""ACCEPTANCE TEST -- UNCOUNTED SKIP PATHS, PYTHON. Self-contained. Run against YOUR OWN files.

    python scripts/ACCEPTANCE-uncounted-skip.py --selftest        # prove it failable, both ways
    python scripts/ACCEPTANCE-uncounted-skip.py <file.py> [...]   # grade your own sources

WHY THIS EXISTS, AND IT IS A BOUND A PEER FOUND RATHER THAN ONE I DECLARED.
The shell version of this test (scripts/ACCEPTANCE-uncounted-skip.sh) was handed to the
Secretary on 2026-09-01. They ran it -- 3/3 on their machine, with their awk -- got CLEAN on
their three shell files, and then reported the thing that mattered:

    "My counting loops are in PYTHON. Your tool cannot reach them, so I applied your
     DISCRIMINATOR by hand, and it found two real ones in idle-beat.py ... Both are
     f.stat() raising OSError, swallowed by a bare `continue`."

So the shell tool printed "says nothing about files you did not name" and was CORRECT, and the
correct bound was still hiding a whole language. THE POPULATION BOUND I PRINTED WAS ABOUT
FILES; THE ONE THAT MATTERED WAS ABOUT LANGUAGES. That is the same defect the discriminator
finds, one level up, in the instrument that finds it.

Applying it to this trunk's own Python found last_exercised.py:182 -- open() raising OSError,
bare continue, on a file the glob had ALREADY ADMITTED. Its summary line prints
"N jsonl scanned, M skipped as self-session" and an unreadable file was in NEITHER. Four lines
above, the self-session skip DOES increment its counter: two enumerations of one rule, four
lines apart, and the second drifted to the weaker default.

THE DISCRIMINATOR, WHICH IS THE WHOLE CHECK -- unchanged from the shell version:
  population DEFINITION (exempt)  -- a filter on the RAW iterated item. `if not
                                     name.endswith(".md"): continue`. It was never a member of
                                     the population; counting it would be WRONG.
  population EXCLUSION (flagged)  -- a failure while extracting a field from an item the loop
                                     ALREADY ADMITTED. `except OSError: continue`. It IS a
                                     member and this code could not read it.
                                     UNPARSEABLE IS UNKNOWN, NOT CLEAN.

WHAT IT FLAGS: a `continue` inside an `except` handler in a loop body, where no counter has
been incremented on that path and none was incremented earlier in the loop body. Python makes
this cleaner than shell: the `except` IS the signal that an admitted item failed, so there is
no regex guessing.

BOUNDS, PRINTED SO YOU CAN DISAGREE WITH THEM:
  * It uses `ast`, so it cannot be fooled by strings, comments or heredocs -- but it also
    cannot see a counter incremented inside a function the loop calls.
  * It does NOT grade whether the counter that increments is the RIGHT one.
  * It does not flag `except: pass` at statement level or `break`; only `continue`.
  * A flagged line is a QUESTION, not a verdict. Some exclusions are correct and merely need
    to be COUNTED AND PRINTED rather than removed.

DO NOT ADOPT THIS FILE INTO YOUR LINT. It is an acceptance test, not a method. A method copied
makes a duplicate; a test handed over leaves you free to reach it your own way, and your route
being different is what would make your agreement worth something. If you write your own
detector, grade it against the four fixtures below and tell me which one I got wrong.
"""
import ast
import sys

INCREMENT_OPS = (ast.Add,)


def _is_counter_increment(node):
    """`x += 1`, `x = x + 1`, or `xs.append(...)` -- accumulation is counting."""
    if isinstance(node, ast.AugAssign) and isinstance(node.op, INCREMENT_OPS):
        return True
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.BinOp) \
            and isinstance(node.value.op, ast.Add):
        return True
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        fn = node.value.func
        if isinstance(fn, ast.Attribute) and fn.attr in ("append", "add", "extend"):
            return True
    return False


def _counts_somewhere(nodes):
    for n in nodes:
        for sub in ast.walk(n):
            if _is_counter_increment(sub):
                return True
    return False


def scan_source(src, fname):
    """Return [(lineno, text)] for continues inside except handlers that count nothing."""
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return None, "UNPARSEABLE: %s line %s: %s" % (fname, exc.lineno, exc.msg)

    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            continue
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Try):
                continue
            for handler in stmt.handlers:
                has_continue = any(
                    isinstance(s, ast.Continue) for s in ast.walk(handler)
                )
                if not has_continue:
                    continue
                # THE DISCRIMINATOR: did this skip path count the item it is dropping?
                if _counts_somewhere(handler.body):
                    continue
                exc_name = "except"
                if handler.type is not None:
                    try:
                        exc_name = "except " + ast.unparse(handler.type)
                    except Exception:
                        pass
                findings.append((handler.lineno,
                                 "%s: ... continue  (an item the loop ADMITTED failed field "
                                 "extraction and left the population uncounted)" % exc_name))
    # de-duplicate: nested walks can see one handler more than once
    seen, uniq = set(), []
    for lineno, text in sorted(findings):
        if lineno in seen:
            continue
        seen.add(lineno)
        uniq.append((lineno, text))
    return uniq, None


FIX_BUG = '''
def f(paths):
    scanned = 0
    for p in paths:
        try:
            blob = open(p).read()
        except OSError:
            continue
        scanned += 1
    return scanned
'''

FIX_CLEAN = '''
def f(paths):
    scanned = 0
    unreadable = 0
    for p in paths:
        try:
            blob = open(p).read()
        except OSError:
            unreadable += 1
            continue
        scanned += 1
    return scanned, unreadable
'''

FIX_NAMED = '''
def f(paths):
    scanned = 0
    bad = []
    for p in paths:
        try:
            blob = open(p).read()
        except OSError:
            bad.append(p)
            continue
        scanned += 1
    return scanned, bad
'''

FIX_DEFINITION = '''
def f(names):
    n = 0
    for name in names:
        if not name.endswith(".md"):
            continue
        if name.startswith("_"):
            continue
        n += 1
    return n
'''


def selftest():
    rc = 0
    cases = [
        ("bug", FIX_BUG, 1,
         "flags an except-handler continue that counts nothing (the defect itself)"),
        ("clean", FIX_CLEAN, 0,
         "passes once the skip path increments a counter (the fix is what turns it green)"),
        ("named", FIX_NAMED, 0,
         "treats ACCUMULATION as counting -- bad.append(p) records the item, it is not dropped"),
        ("definition", FIX_DEFINITION, 0,
         "does NOT flag population-DEFINITION filters on the raw item "
         "(without this it is a firehose nobody keeps)"),
    ]
    for name, src, want, label in cases:
        found, err = scan_source(src, "<fixture:%s>" % name)
        if err:
            print("BROKEN: fixture %s did not parse: %s" % (name, err))
            rc = 1
            continue
        got = len(found)
        if got != want:
            print("BROKEN: fixture %s -- want %d finding(s), got %d %r"
                  % (name, want, got, found))
            rc = 1
        else:
            print("OK  %s" % label)
    # A detector that cannot report UNPARSEABLE would read a broken file as clean.
    found, err = scan_source("def f(:\n", "<fixture:syntaxerror>")
    if found is not None or not err:
        print("BROKEN: a file this detector cannot parse was not reported as UNPARSEABLE -- "
              "unparseable is UNKNOWN, and UNKNOWN dominates a pass")
        rc = 1
    else:
        print("OK  reports an unparseable file as UNKNOWN rather than reading it as clean")
    if rc == 0:
        print("SELFTEST: 5/5 -- failable in both directions, on this machine, with this Python.")
        print("Run it where YOU are. A claim about ast is a claim about your ast.")
    else:
        print("SELFTEST FAILED -- do not trust any verdict below until this passes.")
    return rc


def main(argv):
    if len(argv) == 1:
        print("usage: %s --selftest" % argv[0])
        print("       %s <file.py> [more...]" % argv[0])
        print("Run --selftest FIRST. A detector nobody has seen fail is not a detector.")
        return 2
    if argv[1] == "--selftest":
        return selftest()

    scanned = missing = unparsed = hits = 0
    for path in argv[1:]:
        try:
            src = open(path, encoding="utf-8").read()
        except OSError as exc:
            print("ABSENT/UNREADABLE: %s (%s)" % (path, exc))
            missing += 1
            continue
        scanned += 1
        found, err = scan_source(src, path)
        if err:
            print(err)
            unparsed += 1
            continue
        for lineno, text in found:
            print("%s:%d: %s" % (path, lineno, text))
            hits += 1
    print("---")
    print("scanned %d file(s), %d unreadable, %d unparseable, %d uncounted skip path(s)."
          % (scanned, missing, unparsed, hits))
    print("BOUND: ast-based, so strings and comments cannot fool it; it CANNOT see a counter "
          "incremented inside a function the loop calls. A flagged line is a QUESTION.")
    if missing or unparsed:
        print("VERDICT: UNKNOWN -- a source that could not be read or parsed dominates a pass.")
        return 2
    if hits:
        print("VERDICT: FINDINGS -- each line above drops its artifact from a denominator that "
              "gets reported as a population.")
        return 1
    print("VERDICT: CLEAN on the files you named, IN PYTHON. Says nothing about files you did "
          "not name, and nothing about your shell -- that is the sibling test, and the gap "
          "between them is how this file came to exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
