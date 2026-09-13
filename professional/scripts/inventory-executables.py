#!/usr/bin/env python3
"""INVENTORY the fleet's executable surface, so a Graph-RAG builder can ingest it.

DO NOT ADOPT THIS INTO YOUR LINT. RUN IT. It emits a manifest; it indexes nothing and it
owns no index. Index rebuild belongs to Personal/CFL; this trunk owes only the FEDERATED
rebuild under the not-smaller gate. What Professional can supply without touching anyone's
builder is the INPUT: one row per executable, with a stable entity id.

WHY IT EXISTS
-------------
`scripts/ACCEPTANCE-index-covers-executables.py` measures the gap (17 of 981 = 1.73%) and
correctly refuses to close it, because "is this exclusion deliberate?" is the builder
owner's question, not ours. A measurement with no ingestible artifact behind it leaves the
owner to re-derive the population themselves -- which is LAZY-2: curing our half by hand and
leaving nothing a stranger can run.

    The question this whole effort exists to make answerable is "does a tool for X already
    exist?" -- and on 2026-09-01 this seat answered it WRONG about a 1,406-line parser that
    was sitting on disk. The file was not in the corpus. Prose about it was.

THREE POPULATION BOUNDS, PRINTED EVERY RUN
------------------------------------------
  1. THE DENOMINATOR IS WIDER THAN .py/.sh. The acceptance test counts those two and says
     so; every % it prints is therefore an OVERSTATEMENT of coverage. This inventory counts
     .py .sh .ps1 .psm1 .js .mjs .R .Rmd .cmd .bat and prints the histogram, so the two
     numbers can be reconciled instead of silently disagreeing. `--strict-ext` reproduces
     the acceptance test's narrower population exactly.
  2. XC-Exchequer IS EXCLUDED BY INVARIANT, NOT BY OVERSIGHT. Standing fleet air-gap: never
     mirror, parse, or index XC-Exchequer. Its executables are counted-and-named-only in a
     separate line so the exclusion is VISIBLE rather than a quiet hole in a denominator.
     They never enter the manifest.
  3. A DIRECTORY WE CANNOT WALK IS UNKNOWN, NEVER ZERO. Unreadable roots are counted and
     printed separately and never shrink the denominator silently.

WHAT A ROW IS
-------------
    entity_id  script:<trunk>/<relpath>   stable across runs; POSIX separators always
    sha256     full-file digest, so a re-index can tell CHANGED from MOVED
    header     the first non-shebang, non-blank comment/docstring line, truncated

The header is the only inferred field. It is the file's OWN first line of self-description,
never a summary this script wrote: a generated gloss would put an unstamped claim of ours
into someone else's index, which P2 forbids.

EMPLOYER / EGRESS POSTURE, stated before it runs. Paths and file digests only -- no file
BODIES are copied. Output stays in this trunk, `git remote -v` is empty by standing Jon
gate, and nothing here can reach a git host.

Usage:
    python scripts/inventory-executables.py                 # measure + write manifest
    python scripts/inventory-executables.py --dry-run       # measure, write nothing
    python scripts/inventory-executables.py --strict-ext    # .py/.sh only (acceptance parity)
    python scripts/inventory-executables.py --selftest      # prove it can fail
Exit: 0 wrote a manifest over a non-empty population; 2 UNKNOWN (empty or unreadable).
"""
import hashlib
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WIDE_EXT = (".py", ".sh", ".ps1", ".psm1", ".js", ".mjs", ".r", ".rmd", ".cmd", ".bat")

# THE AUTHORED PREDICATE LIVES HERE, IN ONE PLACE, AND IS EMITTED AS A COLUMN.
#
# [m 2026-09-01 22:5x] This seat computed "the authored surface" FOUR times in one evening with
# four slightly different ad-hoc filters and got 910/679, 894/666, 814 and 817. Every one of
# those numbers was honestly measured and no two agreed, because the FILTER was retyped each
# time instead of being defined once. One of them -- 679 -- went out in a letter to four trunks
# and came back inside a fleet order as "679 unique Python source files", which is wrong three
# ways over: it was not Python-only, it was distinct DIGESTS rather than files, and the filter
# that produced it was never printed.
#
# CHECK THE DEFINITION BEFORE RE-MEASURING. A figure whose predicate is retyped per use is not
# a measurement, it is a family of measurements wearing one number's clothes. So the predicate
# is now a function, its result is a column in the manifest, and anyone quoting a subtotal can
# be asked which column value they filtered on.
NON_AUTHORED_MARKERS = ("shell-snapshots/", "/raw/", "/session-archive/")
NON_AUTHORED_PREFIXES = ("archive/", ".claude-projects-backup/")


def is_authored(relpath):
    """False for harness-generated files and for copies living inside an archive tree.

    NOT a judgment about quality or usefulness -- purely 'did a person write this HERE, or is
    this a machine's output or a mirrored copy of something authored elsewhere'.
    """
    p = relpath.replace("\\", "/")
    if any(m in p for m in NON_AUTHORED_MARKERS):
        return False
    return not p.startswith(NON_AUTHORED_PREFIXES)
STRICT_EXT = (".py", ".sh")
SKIP_DIRS = (".git", "__pycache__", "node_modules", ".venv", "site-packages", ".mypy_cache")

# ⛔ Air-gapped by standing fleet invariant. Named here, in one place, so that removing it
#    is a deliberate edit somebody has to make and not an accident of a changed glob.
AIRGAPPED = ("XC-Exchequer",)

CORPUS_ROOT = os.environ.get("PRO_CORPUS_ROOT", "G:/My Drive/Claude")
OUT_PATH = os.path.join(ROOT, "exchange", "inventory", "executables-manifest.tsv")


def sha256_of(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def header_line(path, limit=160):
    """The file's OWN first line of self-description. Never a gloss we invented."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i > 40:
                    break
                s = line.strip()
                if not s or s.startswith("#!"):
                    continue
                s = s.lstrip("#").lstrip('"').lstrip("'").lstrip("<").lstrip("-").strip()
                if s:
                    return s[:limit].replace("\t", " ")
    except OSError:
        return ""
    return ""


def walk(corpus_root, exts):
    """-> (rows, by_trunk, unreadable, airgapped_counts). Rows never include air-gapped."""
    rows, by_trunk, unreadable, air = [], {}, [], {}
    try:
        entries = sorted(os.listdir(corpus_root))
    except OSError as e:
        return [], {}, [getattr(e, "filename", corpus_root)], {}

    for name in entries:
        sub = os.path.join(corpus_root, name)
        if not os.path.isdir(sub):
            continue
        gapped = name in AIRGAPPED
        n = 0
        for dirpath, dirnames, filenames in os.walk(sub, onerror=unreadable.append):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if any(s in dirpath.replace("\\", "/").split("/") for s in SKIP_DIRS):
                continue
            for f in filenames:
                if not f.lower().endswith(exts):
                    continue
                n += 1
                if gapped:
                    continue                      # counted, never manifested, never read
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, corpus_root).replace("\\", "/")
                try:
                    st = os.stat(full)
                except OSError:
                    unreadable.append(full)
                    continue
                rows.append({
                    "entity_id": "script:" + rel,
                    "trunk": name,
                    "relpath": rel,
                    "ext": os.path.splitext(f)[1].lower(),
                    "bytes": st.st_size,
                    "mtime": int(st.st_mtime),
                    "sha256": sha256_of(full),
                    "header": header_line(full),
                    "authored": "1" if is_authored(rel) else "0",
                })
        if gapped:
            air[name] = n
        else:
            by_trunk[name] = n
    return rows, by_trunk, unreadable, air


def write_manifest(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ["entity_id", "trunk", "relpath", "ext", "bytes", "mtime", "sha256", "authored", "header"]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in sorted(rows, key=lambda r: r["entity_id"]):
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")
    return len(rows)


def main(argv):
    strict = "--strict-ext" in argv
    dry = "--dry-run" in argv
    exts = STRICT_EXT if strict else WIDE_EXT

    t0 = time.time()
    rows, by_trunk, unreadable, air = walk(CORPUS_ROOT, exts)

    print("corpus root : %s" % CORPUS_ROOT)
    print("extensions  : %s%s" % (" ".join(exts), "   [--strict-ext: acceptance parity]" if strict else ""))
    print("manifested  : %d executables in %.1fs" % (len(rows), time.time() - t0))
    print("by trunk    : %s" % (" ".join("%s=%d" % (k, v) for k, v in sorted(by_trunk.items())) or "<none>"))

    hist = {}
    for r in rows:
        hist[r["ext"]] = hist.get(r["ext"], 0) + 1
    print("by extension: %s" % " ".join("%s=%d" % (k, v) for k, v in sorted(hist.items(), key=lambda kv: -kv[1])))

    narrow = sum(v for k, v in hist.items() if k in STRICT_EXT)
    print("of these, .py/.sh only: %d  -- the acceptance test's population. The remaining %d "
          "are executables NO coverage figure in this trunk has ever counted, on either side "
          "of its ratio." % (narrow, len(rows) - narrow))

    if air:
        print("AIR-GAPPED, counted and NOT manifested (standing fleet invariant -- never "
              "mirror, parse, or index): %s" % " ".join("%s=%d" % (k, v) for k, v in sorted(air.items())))
    else:
        print("AIR-GAPPED: no air-gapped root present under this corpus root. That is an "
              "observation about THIS root, not proof the invariant is unneeded.")

    if unreadable:
        print("UNREADABLE (UNKNOWN, never counted as zero): %d -- %s"
              % (len(unreadable), ", ".join(str(u) for u in unreadable[:3])))

    in_skills = sum(1 for r in rows if "/skills/" in r["relpath"])
    print("inside a `skills/` directory: %d  -- the surface LAZY-2 pushes tools INTO and "
          "retrieval has been leaving OUT." % in_skills)

    auth = [r for r in rows if r["authored"] == "1"]
    for label, sel in (("all-ext", lambda r: True),
                       (".py+.sh", lambda r: r["ext"] in (".py", ".sh")),
                       (".py only", lambda r: r["ext"] == ".py")):
        sub = [r for r in auth if sel(r)]
        print("AUTHORED %-8s: %4d file(s), %4d distinct by sha256   <- quote BOTH the column and the "
              "extension set with any subtotal" % (label, len(sub), len({r["sha256"] for r in sub if r["sha256"]})))

    dupes = {}
    for r in rows:
        if r["sha256"]:
            dupes.setdefault(r["sha256"], []).append(r["relpath"])
    n_dupe_groups = sum(1 for v in dupes.values() if len(v) > 1)
    n_dupe_files = sum(len(v) for v in dupes.values() if len(v) > 1)
    print("byte-identical copies: %d file(s) in %d group(s). A builder that ingests these as "
          "distinct entities will report a larger surface than exists." % (n_dupe_files, n_dupe_groups))

    if not rows:
        print("VERDICT: UNKNOWN -- zero executables found. A zero population is UNKNOWN, "
              "never a pass; check the corpus root before believing this.")
        return 2

    if dry:
        print("VERDICT: dry-run, nothing written.")
        return 0

    n = write_manifest(rows, OUT_PATH)
    print("wrote %d rows -> %s" % (n, os.path.relpath(OUT_PATH, ROOT).replace("\\", "/")))
    print("VERDICT: manifest written. It is an INPUT offered to the index owners "
          "(Personal/CFL), not a claim that anything has been indexed. Nothing in this trunk "
          "may report improved coverage until an index REBUILD has read it.")
    return 0


def selftest():
    """Prove the walk can FAIL, in both directions, against a real temp tree."""
    import tempfile
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        # positive: two trunks, one air-gapped, one skipped dir, one wide-ext-only file
        os.makedirs(os.path.join(d, "TrunkA", "scripts"))
        os.makedirs(os.path.join(d, "TrunkA", "__pycache__"))
        os.makedirs(os.path.join(d, "XC-Exchequer", "scripts"))
        open(os.path.join(d, "TrunkA", "scripts", "a.py"), "w").write("#!/usr/bin/env python3\n# I am A\n")
        open(os.path.join(d, "TrunkA", "scripts", "b.ps1"), "w").write("# I am B\n")
        open(os.path.join(d, "TrunkA", "__pycache__", "junk.py"), "w").write("x\n")
        open(os.path.join(d, "XC-Exchequer", "scripts", "secret.py"), "w").write("x\n")

        rows, by_trunk, unread, air = walk(d, WIDE_EXT)
        got = sorted(r["relpath"] for r in rows)
        if got != ["TrunkA/scripts/a.py", "TrunkA/scripts/b.ps1"]:
            print("FAIL [walk] expected 2 TrunkA rows, got %r" % got); fails += 1
        else:
            print("PASS [walk] 2 rows; __pycache__ skipped")
        if air.get("XC-Exchequer") != 1 or any(r["trunk"] == "XC-Exchequer" for r in rows):
            print("FAIL [air-gap] XC-Exchequer must be COUNTED (1) and NOT manifested; got air=%r" % air); fails += 1
        else:
            print("PASS [air-gap] counted=1, manifested=0")

        srows, _, _, _ = walk(d, STRICT_EXT)
        if sorted(r["relpath"] for r in srows) != ["TrunkA/scripts/a.py"]:
            print("FAIL [strict-ext] expected only a.py"); fails += 1
        else:
            print("PASS [strict-ext] narrower population reproduces acceptance parity")

        hdr = next(r["header"] for r in rows if r["relpath"].endswith("a.py"))
        if hdr != "I am A":
            print("FAIL [header] shebang must be skipped; got %r" % hdr); fails += 1
        else:
            print("PASS [header] shebang skipped, file's own words kept")

        # negative: a root that does not exist must be UNKNOWN, not an empty pass
        rows2, _, unread2, _ = walk(os.path.join(d, "nope"), WIDE_EXT)
        if rows2 or not unread2:
            print("FAIL [unreadable] a missing root must report UNREADABLE, not zero rows"); fails += 1
        else:
            print("PASS [unreadable] missing root -> UNREADABLE, never a silent zero")

    print("---")
    print("SELFTEST: %s (%d failing)" % ("PASS" if fails == 0 else "FAIL", fails))
    return 0 if fails == 0 else 3


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main(sys.argv))
