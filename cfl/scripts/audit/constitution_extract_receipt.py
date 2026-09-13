"""Did anything LEAVE CLAUDE.md without landing, byte-for-byte, in the wiki?

Jon, 2026-09-12 ~21:1x CDT, verbatim (typos his): "query - item 4 in your claude.md under wiki,
starting like 140 feels like a draft and reference material that might belong in the wiki rather than
in your actual claude.md. Same for some other sections - feels unprofessional. I get why a lot of this
may have needed to go here.... but.... yeah please...."

So case history moves to wiki/references/constitution/ and the RULE stays in the constitution. The
hazard of that move is obvious and it is this program's oldest one: a "move" that is really a delete,
discovered months later when a literal grep for a Jon sentence returns nothing. "Yeah no deletion.
And no writing PII to Github." (Jon, 2026-08-09) binds this edit.

WHAT THIS CHECKS -- and it is a DERIVATION, never a recorded list of what was moved:
  for every line present in `git show <ref>:CLAUDE.md` and ABSENT from the working CLAUDE.md,
  that exact line must be byte-present in some file under wiki/references/constitution/.

  A line that is neither in the constitution nor in an extract page is reported as LOST. Reworded
  lines are expected to appear as LOST -- the check cannot tell a rewrite from a deletion, so it
  prints them and lets a reader decide. That is the point: the residual is small enough to READ.

  ⚠️ It does NOT verify the reverse (that the extracts add nothing), and it does not grade whether the
  rewrite kept the rule. Both are judgment. This is the no-silent-deletion gate only.

Usage:  python scripts/audit/constitution_extract_receipt.py [--ref HEAD] [--file CLAUDE.md]
        python scripts/audit/constitution_extract_receipt.py --selftest
Exit:   0 clean (no unaccounted line) | 3 unaccounted lines exist | 4 could not run (UNKNOWN, never a pass)
"""
import subprocess, sys
from pathlib import Path

# cp1252 stdout is the standing hazard on this machine: the LOST lines carry the same
# emoji-and-em-dash markup the constitution does, and printing one crashed this script on
# its first real run -- AFTER it had already printed a correct non-zero count, which is the
# worst place to die: the number was right and the evidence for it never reached the reader.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
EXTRACTS = ROOT / "wiki" / "references" / "constitution"
NOISE = {"", "---", "|---|---|", "|---|---|---|", ">"}

# 2026-09-12, second run of the day: Jon read the rewritten file and said "I don't get why their are
# so many emojis". Taking 52 decorative glyphs out of CLAUDE.md rewrites the lines that carried them,
# and this check could then only report them as LOST -- 60-odd rows of pure formatting noise burying
# the one row that might be a real deletion. A receipt that goes unreadable the first time the file is
# reformatted is a receipt nobody runs twice. So both sides are normalised through the SAME glyph set
# before comparison: the check keeps its whole power over deleted WORDS and stops objecting to
# markup. It is the marker glyphs only -- no text, no punctuation, no whitespace is normalised.
GLYPHS = ("⛔", "⚠️", "⚠", "⭐", "✅")


def norm(line, ignore_glyphs):
    if not ignore_glyphs:
        return line
    for g in GLYPHS:
        line = line.replace(g, "")
    return " ".join(line.split())


def read_ref(ref, rel):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{rel}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return None, f"git show {ref}:{rel} failed rc={r.returncode}: {r.stderr.strip()[:200]}"
    return r.stdout.split(chr(10)), None


def audit(ref="HEAD", rel="CLAUDE.md", extracts=None, ignore_glyphs=False):
    extracts = extracts if extracts is not None else EXTRACTS
    before, err = read_ref(ref, rel)
    if before is None:
        return 4, [err], {}
    now = (ROOT / rel)
    if not now.is_file():
        return 4, [f"{rel} not on disk"], {}
    now_lines = {norm(l, ignore_glyphs) for l in now.read_text(encoding="utf-8").split(chr(10))}
    if not extracts.is_dir():
        pool, files = set(), []
    else:
        files = sorted(extracts.rglob("*.md"))
        pool = set()
        for f in files:
            pool |= {norm(l, ignore_glyphs) for l in f.read_text(encoding="utf-8", errors="replace").split(chr(10))}
    gone = [l for l in before if l.strip() and l.strip() not in NOISE
            and norm(l, ignore_glyphs) not in now_lines]
    lost = [l for l in gone if norm(l, ignore_glyphs) not in pool]
    return (3 if lost else 0), lost, {"before": len([l for l in before if l.strip()]),
                                      "gone": len(gone), "lost": len(lost),
                                      "pages": len(files)}


def main():
    if "--selftest" in sys.argv:
        return selftest()
    ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else "HEAD"
    rel = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "CLAUDE.md"
    ig = "--ignore-glyphs" in sys.argv
    rc, lost, stats = audit(ref, rel, ignore_glyphs=ig)
    print(f"=== constitution extract receipt: {rel} vs {ref} ==="
          + ("  [marker glyphs normalised on BOTH sides]" if ig else ""))
    if rc == 4:
        print("UNKNOWN -- could not run: " + "; ".join(lost))
        print("A check that could not run is UNKNOWN and dominates a pass.")
        return 4
    print(f"non-blank lines at {ref} : {stats['before']}")
    print(f"no longer in {rel}       : {stats['gone']}")
    print(f"extract pages read       : {stats['pages']} under {EXTRACTS.relative_to(ROOT)}")
    print(f"UNACCOUNTED (not in either): {stats['lost']}")
    if lost:
        print()
        print("Each line below left the constitution and is byte-present in NO extract page.")
        print("A rewrite looks identical to a deletion here -- read them, do not assume.")
        for l in lost:
            print("  LOST| " + l[:160])
    else:
        print("CLEAN: every line that left the constitution is byte-present in an extract page.")
    return rc


def selftest():
    import tempfile
    NL = chr(10)
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "wiki" / "references" / "constitution").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(t)], check=True)
        subprocess.run(["git", "-C", str(t), "config", "user.email", "s@t"], check=True)
        subprocess.run(["git", "-C", str(t), "config", "user.name", "s"], check=True)
        (t / "CLAUDE.md").write_text("rule A" + NL + "history B" + NL + "history C" + NL, encoding="utf-8")
        subprocess.run(["git", "-C", str(t), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(t), "commit", "-qm", "base"], check=True)

        global ROOT, EXTRACTS
        ROOT, EXTRACTS = t, t / "wiki" / "references" / "constitution"

        # arm 1: both history lines moved to a page -> CLEAN
        (t / "CLAUDE.md").write_text("rule A" + NL + "see the wiki" + NL, encoding="utf-8")
        (EXTRACTS / "p.md").write_text("history B" + NL + "history C" + NL, encoding="utf-8")
        rc, lost, st = audit()
        if rc != 0 or lost:
            fails.append(f"arm 1 (clean move) -> rc={rc} lost={lost}")

        # arm 2: ONE condition differs -- one line was never written to a page
        (EXTRACTS / "p.md").write_text("history B" + NL, encoding="utf-8")
        rc, lost, st = audit()
        if rc != 3 or lost != ["history C"]:
            fails.append(f"arm 2 (silent deletion) -> rc={rc} lost={lost}")

        # arm 3: a tidied line (whitespace changed) must be reported, not forgiven
        (EXTRACTS / "p.md").write_text("history B" + NL + "  history C" + NL, encoding="utf-8")
        rc, lost, st = audit()
        if rc != 3 or lost != ["history C"]:
            fails.append(f"arm 3 (retyped tidier) -> rc={rc} lost={lost}")

        # arm 4: no extract dir at all -> every moved line is LOST, never a pass
        import shutil
        shutil.rmtree(EXTRACTS)
        rc, lost, st = audit()
        if rc != 3 or len(lost) != 2:
            fails.append(f"arm 4 (no extracts dir) -> rc={rc} lost={lost}")
        EXTRACTS.mkdir(parents=True)

        # arm 4b: a line that differs ONLY by a marker glyph is clean under --ignore-glyphs
        #         and LOST without it -- one condition, both directions asserted.
        (t / "CLAUDE.md").write_text("rule A" + NL + "see the wiki" + NL, encoding="utf-8")
        (EXTRACTS / "p.md").write_text("⛔ history B" + NL + "history C" + NL, encoding="utf-8")
        rc_s, lost_s, _ = audit()
        rc_g, lost_g, _ = audit(ignore_glyphs=True)
        if not (rc_s == 3 and lost_s == ["history B"]):
            fails.append(f"arm 4b strict -> rc={rc_s} lost={lost_s}")
        if not (rc_g == 0 and not lost_g):
            fails.append(f"arm 4b normalised -> rc={rc_g} lost={lost_g}")

        # arm 5: a bad ref is UNKNOWN, never clean
        rc, lost, st = audit(ref="no-such-ref")
        if rc != 4:
            fails.append(f"arm 5 (bad ref) -> rc={rc}")

        # arm 6: nothing removed at all -> clean with zero gone
        (t / "CLAUDE.md").write_text("rule A" + NL + "history B" + NL + "history C" + NL, encoding="utf-8")
        rc, lost, st = audit()
        if rc != 0 or st["gone"] != 0:
            fails.append(f"arm 6 (no-op) -> rc={rc} gone={st.get('gone')}")

    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {7 - len(fails)}/7 arms passed")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
