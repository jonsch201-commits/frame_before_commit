#!/usr/bin/env python3
"""selftest_reference_survivors.py -- fixture selftest for the PUB-2d additions to
scripts/audit/derive_public_tree.py.

Run: python scripts/tests/selftest_reference_survivors.py      (no pytest dependency)

WHAT IT PROVES (each case exercises BOTH verdicts, per the 2026-08-17 lesson that an acceptance
test which can only pass is decoration):

  1. REFERENCE-SURVIVORS: a tiny fixture repo with ONE included page referring to ONE excluded
     page three ways (full repo-relative path, [[stem]] wikilink, bare filename) derives to a
     DERIVATION-LOG.md whose `## REFERENCE-SURVIVORS` section lists exactly 3 survivors with the
     correct `path:line` and matched form; `--fail-on-survivors` exits 4. A second fixture with
     ZERO references exits 0 under the same flag and reports 0 survivors.
  2. PATH_EXACT logging: the excluded PATH_EXACT row appears in the `Every exclusion` table
     exactly once, with class PATH-DENY-EXACT and the row's comment as its detail.
  3. --scope-note: the note's text is the first heading (`## SCOPE`) of the log; an EMPTY note
     aborts non-zero and writes no tree.
  4. --controls-dir: the tree holds neither MANIFEST.sha256 nor DERIVATION-LOG.md, and the
     manifest's row count equals the tree's file count.
  5. VALUE_WALK: the first VALUE_WALK literal from public_exclusions.txt planted in two included
     pages reports 2 hits as path:line under `## VALUE-WALK` and exits 5 under
     --fail-on-value-hits; zero hits exits 0. The literal is never printed by the deriver or by
     this selftest; the log row carries an opaque ordinal (VW-01), a digest of per-run salt +
     literal (so the UNSALTED sha256 of the literal must NOT appear -- that is asserted), and
     the class.
  6. SHAPE_SCAN: a fixture with one 33-char mixed-case-plus-digit id and one hyphenated slug of
     the same length reports exactly 1 hit under `## SHAPE-SCAN`, naming the shape and the
     token's length only; the id itself never appears in the log; no exit code (0).
  7. SHAPE_SCAN likely_slug column (PUB-2e): four synthetic look-alikes of the 2026-09-02 false
     positives flag likely_slug=yes, three synthetic base64-ish ids (33/33/44 chars, 0-1
     separators) flag no, no row is removed, no-rows come first, and the log carries the rule
     plus Professional's sample caveat verbatim.

HOW THE EXCLUDED PAGE IS CHOSEN. The deriver reads its exclusion set from
scripts/audit/public_exclusions.txt at import time (never inferred, never overridable), so the
fixture's excluded page is written AT the first real PATH_EXACT path from that file. Its body
here is synthetic; the real page is never read. If the file has no PATH_EXACT row the selftest
FAILS rather than skipping -- a gate whose fixture cannot be built is not a passing gate.

Scratch lives under %LOCALAPPDATA%\\Temp\\claude, never on G: and never in the working tree.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DERIVER = os.path.join(ROOT, "scripts", "audit", "derive_public_tree.py")
EXCL = os.path.join(ROOT, "scripts", "audit", "public_exclusions.txt")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                       "Temp", "claude", "pub2d-selftest")

FAILS = []


def check(name, cond, detail=""):
    print("  %s  %s%s" % ("PASS" if cond else "FAIL", name, ("  -- " + str(detail)) if detail else ""))
    if not cond:
        FAILS.append(name)


def first_path_exact():
    with open(EXCL, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("PATH_EXACT "):
                body = ln.split("  #", 1)[0].split(" #", 1)[0]
                comment = ln[len(body):].strip().lstrip("#").strip()
                return body.split(" ", 1)[1].strip(), comment
    return None, None


def write(root, rel, text):
    full = os.path.join(root, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def fresh(*parts):
    d = os.path.join(SCRATCH, *parts)
    if os.path.isdir(d):
        shutil.rmtree(d)
    return d


def run(args, env):
    r = subprocess.run([sys.executable, DERIVER] + args, env=env, capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")


def walk(root):
    out = []
    for dp, dn, fn in os.walk(root):
        for x in fn:
            out.append(os.path.relpath(os.path.join(dp, x), root).replace("\\", "/"))
    return sorted(out)


INCLUDED = "wiki/concepts/pub2d-selftest-included.md"


def build_fixture(name, excluded_path, with_refs):
    src = fresh(name, "src")
    fn = excluded_path.rsplit("/", 1)[-1]
    stem = fn.rsplit(".", 1)[0]
    write(src, excluded_path,
          "---\ntrunk: fl\n---\n# fixture: the withheld page\n\nSynthetic body. Nothing in here "
          "is a real record.\n")
    if with_refs:
        body = ("---\ntrunk: fl\n---\n"                                     # 1-3
                "# fixture: the included page\n"                            # 4
                "\n"                                                        # 5
                "See `%s` for the full account.\n" % excluded_path +         # 6  FULL
                "\n"                                                        # 7
                "Linked as [[%s]] from the concept index.\n" % stem +        # 8  WIKILINK
                "\n"                                                        # 9
                "The file %s was withheld from the public tree.\n" % fn)     # 10 FILENAME
    else:
        body = ("---\ntrunk: fl\n---\n# fixture: the included page\n\nThis page refers to "
                "nothing that was withheld.\n")
    write(src, INCLUDED, body)
    return src


def main():
    excluded_path, comment = first_path_exact()
    print("== 0. fixture inputs ==")
    check("public_exclusions.txt has a PATH_EXACT row", excluded_path is not None)
    if excluded_path is None:
        return finish()
    print("  excluded page (real PATH_EXACT path, synthetic body): %s" % excluded_path)
    print("  row comment: %r" % comment)

    os.makedirs(SCRATCH, exist_ok=True)
    gaz = os.path.join(SCRATCH, "selftest_gazetteer.txt")
    with open(gaz, "w", encoding="utf-8") as f:
        f.write("# synthetic fixture gazetteer -- not a real name\nThistlewaite\n")
    env = dict(os.environ)
    env["DEPII_GAZETTEER"] = gaz

    # ---- 1a. three references -> 3 survivors, exit 4 under --fail-on-survivors --------------
    print("== 1a. fixture WITH three references ==")
    src = build_fixture("with-refs", excluded_path, True)
    out = fresh("with-refs", "out")
    rc, txt = run(["--src-mode", "fs", "--src-root", src, "--out", out, "--fail-on-survivors"], env)
    check("exit code is 4 with --fail-on-survivors", rc == 4, rc)
    log_path = os.path.join(out, "DERIVATION-LOG.md")
    check("DERIVATION-LOG.md written despite exit 4", os.path.isfile(log_path))
    log = open(log_path, encoding="utf-8").read() if os.path.isfile(log_path) else ""
    check("excluded page absent from tree",
          not os.path.isfile(os.path.join(out, excluded_path.replace("/", os.sep))))
    check("included page present in tree",
          os.path.isfile(os.path.join(out, INCLUDED.replace("/", os.sep))))
    sec = log.split("## REFERENCE-SURVIVORS", 1)
    check("log has a ## REFERENCE-SURVIVORS section", len(sec) == 2)
    sec = sec[1] if len(sec) == 2 else ""
    fn = excluded_path.rsplit("/", 1)[-1]
    stem = fn.rsplit(".", 1)[0]
    expect = {("%s:6" % INCLUDED, "FULL", excluded_path),
              ("%s:8" % INCLUDED, "WIKILINK", "[[" + stem),
              ("%s:10" % INCLUDED, "FILENAME", fn)}
    got = set()
    for m in re.finditer(r"^- `([^`]+)` (FULL|SUFFIX|FILENAME|WIKILINK|STEM) `([^`]+)`$", sec, re.M):
        got.add((m.group(1), m.group(2), m.group(3)))
    check("section lists exactly the 3 survivors with correct lines and forms", got == expect,
          "got=%s" % sorted(got))
    check("per-file heading reports 3 inbound refs",
          ("### `%s` (PATH_EXACT) -- 3 inbound ref(s)" % excluded_path) in sec)
    check("summary line: 1 of 1 excluded files, 3 refs, PATH_EXACT 1 of 1",
          "1 of 1 excluded files have >= 1 inbound reference by name in an INCLUDED file (3 refs total); "
          "PATH_EXACT rows: 1 of 1 have survivors" in sec)
    check("stdout names the PATH_EXACT file on FAIL",
          "FAIL --fail-on-survivors: 1 PATH_EXACT file(s)" in txt and excluded_path in txt)

    # ---- 2. PATH_EXACT row logged exactly once, with its comment -----------------------------
    print("== 2. PATH_EXACT exclusion is logged with class and row comment ==")
    every = log.split("## Every exclusion", 1)[1].split("## REFERENCE-SURVIVORS", 1)[0] if "## Every exclusion" in log else ""
    rows = [ln for ln in every.split("\n") if ln.startswith("| `%s` |" % excluded_path)]
    check("exactly one exclusion row for the PATH_EXACT path", len(rows) == 1, rows)
    check("that row carries class PATH-DENY-EXACT", len(rows) == 1 and "| PATH-DENY-EXACT |" in rows[0])
    want_detail = comment if comment else "PATH_EXACT row (no comment)"
    check("that row carries the row's comment as detail", len(rows) == 1 and want_detail[:100] in rows[0],
          "want %r" % want_detail)
    check("EXCLUDED (distinct files) count includes it", "| EXCLUDED (distinct files) | 1 |" in log)
    check("stdout excluded_files=1", "excluded_files=1" in txt)

    # ---- 1b. zero references -> exit 0 under the same flag -----------------------------------
    print("== 1b. fixture with ZERO references ==")
    src0 = build_fixture("no-refs", excluded_path, False)
    out0 = fresh("no-refs", "out")
    rc0, txt0 = run(["--src-mode", "fs", "--src-root", src0, "--out", out0, "--fail-on-survivors"], env)
    check("exit code is 0 with --fail-on-survivors and no references", rc0 == 0, rc0)
    log0 = open(os.path.join(out0, "DERIVATION-LOG.md"), encoding="utf-8").read()
    check("summary line: 0 of 1 excluded files, 0 refs",
          "0 of 1 excluded files have >= 1 inbound reference by name in an INCLUDED file (0 refs total); "
          "PATH_EXACT rows: 0 of 1 have survivors" in log0)
    check("no per-file survivor heading", "inbound ref(s)" not in log0)
    check("PATH_EXACT row still logged once with zero references",
          log0.count("| `%s` | PATH-DENY-EXACT |" % excluded_path) == 1)

    # ---- 3. --scope-note ---------------------------------------------------------------------
    print("== 3. --scope-note ==")
    note = os.path.join(SCRATCH, "scope-note.txt")
    note_text = "SCOPE NOTE FIXTURE\nDenominator: 2 files. UNKNOWN to semantic reading: none. Pending: none.\n"
    with open(note, "w", encoding="utf-8", newline="\n") as f:
        f.write(note_text)
    out3 = fresh("scope", "out")
    rc3, txt3 = run(["--src-mode", "fs", "--src-root", src0, "--out", out3, "--scope-note", note], env)
    check("derive with --scope-note exits 0", rc3 == 0, rc3)
    log3 = open(os.path.join(out3, "DERIVATION-LOG.md"), encoding="utf-8").read() if rc3 == 0 else ""
    headings = [ln for ln in log3.split("\n") if ln.startswith("#")]
    check("first heading of the log is ## SCOPE", bool(headings) and headings[0] == "## SCOPE", headings[:2])
    check("scope text is present verbatim", note_text.rstrip("\n") in log3)
    check("## SCOPE precedes the # DERIVATION-LOG title",
          log3.find("## SCOPE") != -1 and log3.find("## SCOPE") < log3.find("# DERIVATION-LOG"))
    empty = os.path.join(SCRATCH, "scope-empty.txt")
    with open(empty, "w", encoding="utf-8") as f:
        f.write("   \n")
    out3e = fresh("scope-empty", "out")
    rc3e, txt3e = run(["--src-mode", "fs", "--src-root", src0, "--out", out3e, "--scope-note", empty], env)
    check("EMPTY --scope-note aborts non-zero", rc3e != 0, rc3e)
    check("EMPTY --scope-note writes no tree", not os.path.isdir(out3e) or not os.listdir(out3e))
    check("abort message names the flag", "--scope-note" in txt3e and "empty" in txt3e)

    # ---- 4. --controls-dir -------------------------------------------------------------------
    print("== 4. --controls-dir ==")
    out4 = fresh("controls", "out")
    ctl4 = fresh("controls", "controls")
    rc4, txt4 = run(["--src-mode", "fs", "--src-root", src, "--out", out4, "--controls-dir", ctl4], env)
    check("derive with --controls-dir exits 0 (no --fail-on-survivors)", rc4 == 0, rc4)
    tree_files = walk(out4)
    check("tree holds no MANIFEST.sha256", "MANIFEST.sha256" not in tree_files)
    check("tree holds no DERIVATION-LOG.md", "DERIVATION-LOG.md" not in tree_files)
    check("controls dir holds both", sorted(os.listdir(ctl4)) == ["DERIVATION-LOG.md", "MANIFEST.sha256"],
          sorted(os.listdir(ctl4)) if os.path.isdir(ctl4) else "missing")
    man = os.path.join(ctl4, "MANIFEST.sha256")
    man_rows = [ln for ln in open(man, encoding="utf-8").read().split("\n") if ln.strip()] if os.path.isfile(man) else []
    check("manifest row count == tree file count", len(man_rows) == len(tree_files),
          "%d rows vs %d files" % (len(man_rows), len(tree_files)))
    ok_hash = True
    for row in man_rows:
        h, b, rel = row.split("  ", 2)
        full = os.path.join(out4, rel.replace("/", os.sep))
        data = open(full, "rb").read() if os.path.isfile(full) else b""
        if hashlib.sha256(data).hexdigest() != h or str(len(data)) != b:
            ok_hash = False
    check("every manifest row hashes its file", ok_hash and bool(man_rows))
    log4 = open(os.path.join(ctl4, "DERIVATION-LOG.md"), encoding="utf-8").read() if os.path.isfile(os.path.join(ctl4, "DERIVATION-LOG.md")) else ""
    check("controls-dir log still carries the 3 survivors", "-- 3 inbound ref(s)" in log4)
    # controls dir == out must abort; a non-empty controls dir must abort
    rcx, txtx = run(["--src-mode", "fs", "--src-root", src, "--out", fresh("controls-same", "out"),
                     "--controls-dir", os.path.join(SCRATCH, "controls-same", "out")], env)
    check("--controls-dir equal to --out aborts", rcx != 0, rcx)
    rcy, txty = run(["--src-mode", "fs", "--src-root", src, "--out", fresh("controls-nonempty", "out"),
                     "--controls-dir", ctl4], env)
    check("non-empty --controls-dir aborts (fail-closed)", rcy != 0, rcy)

    # ---- 5. VALUE_WALK ----------------------------------------------------------------------
    # The literal is read from the real exclusion list and NEVER printed: this selftest names it
    # only by sha256[:8], exactly as the deriver does. Two included pages carry it -> 2 hits,
    # exit 5; the zero-reference fixture carries it nowhere -> exit 0.
    print("== 5. VALUE_WALK ==")
    lit, cls = first_value_walk()
    check("public_exclusions.txt has a VALUE_WALK row", lit is not None)
    if lit is not None:
        unsalted = hashlib.sha256(lit.encode("utf-8")).hexdigest()[:8]
        print("  first VALUE_WALK row: class=%r (literal withheld; digest is per-run salted, so "
              "not printed here either)" % cls)
        src5 = build_fixture("value-walk", excluded_path, False)
        write(src5, "wiki/concepts/pub2d-selftest-value-a.md",
              "---\ntrunk: fl\n---\n# fixture a\n\nlocator: %s\n" % lit)               # line 6
        write(src5, "wiki/references/pub2d-selftest-value-b.md",
              "---\ntrunk: fl\n---\n# fixture b\n\nprose\n\nsee %s here\n" % lit)     # line 8
        out5 = fresh("value-walk", "out")
        rc5, txt5 = run(["--src-mode", "fs", "--src-root", src5, "--out", out5,
                         "--fail-on-value-hits", "--fail-on-survivors"], env)
        check("exit code is 5 with --fail-on-value-hits and two hits", rc5 == 5, rc5)
        log5 = open(os.path.join(out5, "DERIVATION-LOG.md"), encoding="utf-8").read()
        check("literal never appears in the log", lit not in log5)
        check("literal never appears on stdout/stderr", lit not in txt5)
        vsec = log5.split("## VALUE-WALK", 1)
        check("log has a ## VALUE-WALK section", len(vsec) == 2)
        vsec = vsec[1] if len(vsec) == 2 else ""
        check("row VW-01 with the class shows 2 hits",
              re.search(r"^\| VW-01 \| `[0-9a-f]{8}` \| %s \| 2 \|$" % re.escape(cls), vsec, re.M) is not None)
        check("UNSALTED sha256(literal)[:8] does not appear in the log (oracle guard)",
              unsalted not in log5)
        check("no 'salt' value is printed (only the word in prose)",
              "salt=" not in log5 and "salt:" not in log5 and "salt=" not in txt5)
        check("both path:line hits listed",
              "- `wiki/concepts/pub2d-selftest-value-a.md:6`" in vsec
              and "- `wiki/references/pub2d-selftest-value-b.md:8`" in vsec)
        check("exit 5 takes precedence over exit 4 (PATH_EXACT survivors absent here anyway)", rc5 == 5)
        # zero hits -> exit 0 (the no-refs fixture from 1b never carried the literal)
        out5z = fresh("value-walk-zero", "out")
        rc5z, txt5z = run(["--src-mode", "fs", "--src-root", src0, "--out", out5z,
                           "--fail-on-value-hits"], env)
        check("exit code is 0 with --fail-on-value-hits and zero hits", rc5z == 0, rc5z)
        log5z = open(os.path.join(out5z, "DERIVATION-LOG.md"), encoding="utf-8").read() if rc5z == 0 else ""
        check("zero-hit row present with 0",
              re.search(r"^\| VW-01 \| `[0-9a-f]{8}` \| %s \| 0 \|$" % re.escape(cls), log5z, re.M) is not None)
        check("literal absent from zero-hit log", lit not in log5z)
        # the salted digest must differ between runs (otherwise it is the oracle again)
        d1 = re.search(r"^\| VW-01 \| `([0-9a-f]{8})`", vsec, re.M)
        d2 = re.search(r"^\| VW-01 \| `([0-9a-f]{8})`", log5z, re.M)
        check("salted digest differs between two runs", bool(d1 and d2) and d1.group(1) != d2.group(1))

    # ---- 6. SHAPE_SCAN ----------------------------------------------------------------------
    print("== 6. SHAPE_SCAN ==")
    shape = first_shape_scan()
    check("public_exclusions.txt has a SHAPE_SCAN row", shape is not None)
    if shape is not None:
        # synthetic 33-char mixed-case-plus-digit token (not a real resource id) and a 33-char
        # lowercase hyphenated slug -- same length, only one is id-shaped.
        token = "1zQ9kL3mN7pR2sT5vW8xY0aB4cD6eF1gH"          # 33 chars
        slug = "pub2d-selftest-shape-slug-fixture"           # 33 chars
        assert len(token) == 33 and len(slug) == 33
        src6 = build_fixture("shape-scan", excluded_path, False)
        write(src6, "wiki/concepts/pub2d-selftest-shape.md",
              "---\ntrunk: fl\n---\n# fixture shape\n\nfolder %s here\n\nslug %s here\n"
              % (token, slug))                                             # id line 6, slug line 8
        out6 = fresh("shape-scan", "out")
        rc6, txt6 = run(["--src-mode", "fs", "--src-root", src6, "--out", out6,
                         "--fail-on-value-hits", "--fail-on-survivors"], env)
        check("shape scan sets no exit code (exit 0)", rc6 == 0, rc6)
        log6 = open(os.path.join(out6, "DERIVATION-LOG.md"), encoding="utf-8").read() if rc6 == 0 else ""
        ssec = log6.split("## SHAPE-SCAN", 1)
        check("log has a ## SHAPE-SCAN section", len(ssec) == 2)
        ssec = ssec[1] if len(ssec) == 2 else ""
        rows = re.findall(ROW_RX, ssec, re.M)
        check("exactly 1 shape hit (the id, not the slug)",
              [r[:3] for r in rows] == [("wiki/concepts/pub2d-selftest-shape.md:6", shape, "33")], rows)
        check("token never appears in the log", token not in log6)
        check("token never appears on stdout", token not in txt6)
        check("stdout reports the count", "1 token hit(s)" in txt6)

    # ---- 7. SHAPE_SCAN likely_slug column (lane PUB-2e) -------------------------------------
    # Professional read all four 2026-09-02 SHAPE-SCAN hits and found all four false positives
    # (a test-expectation key, three letter-name fragments). The second column tags each hit
    # with likely_slug / separators / longest_alpha_segment; it NEVER removes a row. Fixture:
    # four synthetic look-alikes of the false-positive shapes (must flag yes) and three synthetic
    # base64-ish ids with 0-1 separators (must flag no); all seven must survive as rows, and the
    # likely_slug=no rows must come first. Nothing here is a real key or a real id.
    print("== 7. SHAPE_SCAN likely_slug column (PUB-2e) ==")
    shapes = all_shape_scans()
    check("public_exclusions.txt has at least two SHAPE_SCAN rows (33- and 44-char shapes)",
          len(shapes) >= 2, shapes)
    if shape is not None:
        yes_tokens = [
            "pub2E-selftests-Expect-keyName-x1",             # 33: 4 hyphens, 9-letter alpha segment
            "wake-Letter-fragment-Herald-2e-Q9zzA-reviews",  # 44: 6 hyphens, 8-letter alpha segment
            "Kx7_professional_reply_letter_Z3z",             # 33: 4 underscores, 12-letter segment
            "ab9Cd-selftestDeliverable-Lane2e-K1x-note8-Q",  # 44: 5 hyphens, 19-letter segment
        ]
        no_tokens = [
            "1zQ9kL3mN7pR2sT5vW8xY0aB4cD6eF1gH",                # 33: 0 separators
            "1aB2cD3eF4gH5iJ6kL7m_N8oP9qR0sT1u",                # 33: 1 underscore
            "1Ab2Cd3Ef4Gh5Ij6Kl7Mn8Op9Qr0St1Uv2Wx3Yz-4Ab5",     # 44: 1 hyphen
        ]
        assert [len(t) for t in yes_tokens] == [33, 44, 33, 44], [len(t) for t in yes_tokens]
        assert [len(t) for t in no_tokens] == [33, 33, 44], [len(t) for t in no_tokens]

        def oracle(t):
            # local restatement of the published rule, independent of the deriver's code
            segs = re.split(r"[-_]", t)
            seps = len(segs) - 1
            longest = max([len(x) for x in segs if x and x.isalpha()] or [0])
            return ("yes" if (seps >= 2 or longest >= 5) else "no"), seps, longest
        for t in yes_tokens:
            assert oracle(t)[0] == "yes", t
        for t in no_tokens:
            assert oracle(t)[0] == "no", t
        src7 = build_fixture("shape-slug", excluded_path, False)
        lines = ["---", "trunk: fl", "---", "# fixture slug column", ""]
        for t in yes_tokens + no_tokens:
            lines.append("token %s here" % t)
            lines.append("")
        write(src7, "wiki/concepts/pub2e-selftest-slug.md", "\n".join(lines) + "\n")
        out7 = fresh("shape-slug", "out")
        rc7, txt7 = run(["--src-mode", "fs", "--src-root", src7, "--out", out7,
                         "--fail-on-value-hits", "--fail-on-survivors"], env)
        check("slug column sets no exit code (exit 0)", rc7 == 0, rc7)
        log7 = open(os.path.join(out7, "DERIVATION-LOG.md"), encoding="utf-8").read() if rc7 == 0 else ""
        ssec7 = log7.split("## SHAPE-SCAN", 1)
        ssec7 = ssec7[1] if len(ssec7) == 2 else ""
        rows7 = re.findall(ROW_RX, ssec7, re.M)
        # The deriver's own SHAPE_SCAN regexes decide which of the seven are HITS at all; a
        # look-alike the regex does not match is not a row and cannot be graded. Grade every row
        # that exists; require the three ids to be rows; require no row to be dropped.
        by_line = {}
        for path_line, name, tlen, likely, seps, longest in rows7:
            by_line[int(path_line.rsplit(":", 1)[1])] = (likely, int(seps), int(longest))
        line_of = {6 + 2 * k: t for k, t in enumerate(yes_tokens + no_tokens)}   # token k on line 6+2k
        hit_yes = sorted(ln for ln, t in line_of.items() if t in yes_tokens and ln in by_line)
        hit_no = sorted(ln for ln, t in line_of.items() if t in no_tokens and ln in by_line)
        check("all three synthetic ids are hits (0-1 separators, len 33/33/44)",
              len(hit_no) == 3, sorted(by_line))
        check("all four false-positive look-alikes are hits (the shapes Professional read)",
              len(hit_yes) == 4, sorted(by_line))
        check("no row removed: row count == id hits + look-alike hits",
              len(rows7) == len(hit_yes) + len(hit_no), (len(rows7), len(hit_yes), len(hit_no)))
        wrong = [(ln, by_line[ln], oracle(line_of[ln])) for ln in by_line
                 if by_line[ln] != oracle(line_of[ln])]
        check("every hit's (likely_slug, separators, longest_alpha_segment) matches the rule",
              not wrong, wrong)
        check("every synthetic id flags likely_slug=no",
              hit_no and all(by_line[ln][0] == "no" for ln in hit_no))
        check("every look-alike hit flags likely_slug=yes",
              hit_yes and all(by_line[ln][0] == "yes" for ln in hit_yes))
        # rows are grouped per shape (### heading); within each group no-rows come first
        per_shape = [[r[3] for r in re.findall(ROW_RX, sec, re.M)]
                     for sec in ssec7.split("\n### ")[1:]]
        check("rows ordered likely_slug=no first within every shape group",
              per_shape and all(v == sorted(v, key=lambda x: x != "no") for v in per_shape), per_shape)
        check("summary table carries per-verdict counts",
              re.search(r"^\| \S+ \| \d+ \| \d+ \| \d+ \|$", ssec7, re.M) is not None)
        check("log carries the rule sentence", "likely_slug = separators >= 2 OR any "
              "separator-delimited segment all-alphabetic and >= 5 chars" in log7)
        check("log carries Professional's sample caveat verbatim",
              "Rule tuned on seven tokens, three of them real: a sample, not a validation "
              "(Professional, 2026-09-02)." in log7)
        check("no token appears in the log", not any(t in log7 for t in yes_tokens + no_tokens))
        check("no token appears on stdout", not any(t in txt7 for t in yes_tokens + no_tokens))

    return finish()


ROW_RX = (r"^- `([^`]+)` (\S+) len=(\d+) likely_slug=(yes|no) separators=(\d+) "
          r"longest_alpha_segment=(\d+)$")


def all_shape_scans():
    """Names of every SHAPE_SCAN row, in file order."""
    names = []
    with open(EXCL, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("SHAPE_SCAN "):
                body = ln.split("  #", 1)[0].split(" #", 1)[0]
                names.append(body.split(" ", 2)[1].strip())
    return names


def first_shape_scan():
    """Name of the first SHAPE_SCAN row, or None."""
    with open(EXCL, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("SHAPE_SCAN "):
                body = ln.split("  #", 1)[0].split(" #", 1)[0]
                return body.split(" ", 2)[1].strip()
    return None


def first_value_walk():
    """First VALUE_WALK row: (literal, class). The literal is sensitive input -- never print it."""
    with open(EXCL, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("VALUE_WALK "):
                body = ln.split("  #", 1)[0].split(" #", 1)[0]
                comment = ln[len(body):].strip().lstrip("#").strip()
                return body.split(" ", 1)[1].strip(), (comment or "(no class)")
    return None, None


def finish():
    print("")
    if FAILS:
        print("SELFTEST reference-survivors: FAIL (%d)" % len(FAILS))
        for x in FAILS:
            print("  - %s" % x)
        return 1
    print("SELFTEST reference-survivors: PASS -- survivors listed with lines and forms, exit 4 / 0 "
          "both exercised, PATH_EXACT logged once with its comment, scope block first, controls "
          "dir complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
