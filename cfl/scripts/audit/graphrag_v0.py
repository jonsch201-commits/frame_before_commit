#!/usr/bin/env python3
"""
⛔ SUPERSEDED 2026-08-17 18:0x CDT, BEFORE IT WAS EVER USED. DO NOT RUN THIS. DO NOT EXTEND IT.

USE `scripts/graphrag/` INSTEAD — `build_index.py`, `retrieve.py`, `acceptance.py`, `README.md`.

WHY THIS FILE IS STILL HERE: no deletion. It is kept as the EXHIBIT for a defect that cost real
money and real time, and the defect is not in the code below.

⭐ WHAT HAPPENED: a CFL session built the assigned GraphRAG v0 in `scripts/graphrag/` between
17:12 and 17:47. ANOTHER CFL session — this one — started building this parallel implementation at
~17:55, in the same repo, against the same assignment letter, and did not discover the existing
work until it hit a `.gitignore` line referring to `scripts/graphrag/build_index.py`. TWO SEATS OF
THE SAME TRUNK WORKED THE SAME TICKET CONCURRENTLY AND NEITHER KNEW.

⛔ AND THE MISS WAS NOT SUBTLE. The existing implementation announced itself in at least four
places this session had already read or could have read in one command:
  - `.gitignore:16-19`, naming `scripts/graphrag/build_index.py` by path
  - `RECAPS-ALL-TRUNKS.md`, CFL session J at 17:12, naming GraphRAG as its own work in progress
  - the trunk's own git log
  - `ls scripts/`
**The check that would have prevented it costs one command and was never run: look for the thing
before building the thing.**

⚠️ THE COST, stated rather than smoothed: a redundant index build, and — worse — this file's
default `--db` pointed INSIDE the tracked tree, so a 61 MB generated sqlite carrying 300-char
previews of EVERY indexed passage (including `wiki/personal`) was committed and pushed to GitHub.
The standing ruling is absolute — *"no writing PII to Github"* / *"Not in the github, yes on G."*
The prior session had ALREADY made the correct call and written it into `.gitignore`: *"Default
location is OFF Drive … It is a DERIVED artifact."* **The right answer was on disk before the
mistake was made.**

⭐ THE GENERALISABLE FINDING, which is why this is an exhibit and not just an apology: this trunk
has NO intra-trunk work registry. Wakes deliver to a TRUNK DIRECTORY, several sessions can be live
in one trunk at once (measured today: 3 CFL sessions in `claude agents`), and nothing tells one
what another is holding. Cross-trunk mail is solved; SEAT-TO-SEAT INSIDE A TRUNK IS NOT. That is
the same root as the Secretary's V2 (`owner: CFL`, due 08-19) seen from the inside, and this file
is its first measured cost.

The only thing below worth carrying forward is a bug already fixed in place and worth remembering:
`df_cut = int(max_df * n_chunks)` evaluates to 0 on a small corpus, so the prune kept n-grams with
df <= 0 — nothing — and the index built "successfully", printed its size, and could never match
anything. An empty denominator dressed as a clean build, caught only because the self-test asserted
the POSITIVE direction too.

Original module docstring follows, unaltered.
"""

"""
graphrag_v0.py — typo-tolerant retrieval over the wiki + the trunk constitutions.

WHY THIS EXISTS, and it is Jon's constraint in his own words:

    "think about all my typos and imprecise language and the stylomantic differences
     between trunks."

`grep` and every word-level index share one property: they cannot match a word that was
not spelled the way it was indexed. Jon's standing corpus is FULL of his own typos, and
those typos are load-bearing -- `CLAUDE.md` says so directly: "Typos are his and stay
his. A 'corrected' quote is an unverifiable quote." So the retrieval layer has to absorb
misspelling rather than ask him to spell things the way the index did.

CHARACTER N-GRAMS ARE TYPO-TOLERANT BY CONSTRUCTION. "embeding" and "embedding" share
almost every 3-gram; "blocer" and "blocker" likewise. A word-level match scores both at
zero. That is the whole mechanism, and it needs no model and no install.

⛔ THE HONEST LIMITATION, STATED IN THE INSTRUMENT'S OWN OUTPUT rather than in a letter:
this captures SURFACE similarity, not meaning. It will not connect "the fence is wider"
to "do not over-gate" unless they share characters. A dense-embedding model is a QUALITY
UPGRADE on this baseline, not a prerequisite for it. Do not oversell it.

DESIGN, and the reason for each choice:

  - chunks are HEADING-SCOPED with byte ranges retained, so every hit can name
    file + heading + byte range. A retrieval hit that cannot say where it came from is a
    claim without a citation, which is the defect this repo has paid for most often.
  - the index is a SPARSE INVERTED INDEX in ONE sqlite file. Durable means "survives a
    reboot", so it is a file, not a warm process. A query touches only the postings for
    the query's own n-grams -- it never scans the corpus.
  - high-document-frequency n-grams are PRUNED (they are the " the " of character space:
    all cost, no discrimination). The cutoff is recorded IN THE DATABASE so a later
    reader can see what the index cannot see. An index that silently drops features is
    an index that lies about its own recall.
  - build time and on-disk size are PRINTED, per spec, so the cost of keeping it fresh is
    visible from day one rather than discovered later.

TWO-SIDED SELF-TEST. `--self-test` builds a tiny fixture in memory and asserts BOTH
directions: a misspelled query MUST retrieve the right passage (positive), and an
unrelated query MUST NOT (negative). A check that can only pass is a mute button --
this repo retired RATIO_FLOOR for exactly that.

Usage:
    python scripts/audit/graphrag_v0.py build [--db PATH] [--max-df 0.35]
    python scripts/audit/graphrag_v0.py query "vector embeding" [-k 5]
    python scripts/audit/graphrag_v0.py accept        # Jon's typos, vs grep, in public
    python scripts/audit/graphrag_v0.py --self-test
"""

import argparse
import io
import math
import os
import re
import sqlite3
import struct
import sys
import time
import zlib

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DB = os.path.join(REPO, "wiki", "tracker", "graphrag-v0.sqlite")

NGRAM_SIZES = (3, 4, 5)
CHUNK_TARGET = 1600          # chars; headings shorter than this stay whole
CHUNK_OVERLAP = 200          # chars of overlap when a section must be split
DEFAULT_MAX_DF = 0.35        # prune n-grams appearing in >35% of chunks
MIN_CHUNK_CHARS = 40

# The four trunk constitutions. Read-only, and ABSOLUTE because they live in sibling
# trunks -- a relative path here would silently index this trunk's copy under another
# trunk's name, which is the exact false-green the switchboard config hit today.
CONSTITUTIONS = [
    os.path.join(REPO, "CLAUDE.md"),
    os.path.join(REPO, "CLAUDE-UNIVERSAL.md"),
    "G:/My Drive/Claude/Claude Personal/CLAUDE.md",
    "G:/My Drive/Claude/Claude Professional/claude-professional/CLAUDE.md",
    "G:/My Drive/Claude/Claude Secretary/CLAUDE.md",
    "G:/My Drive/Claude/Claude Secretary/CLAUDE-STANDARDS.md",
]

WS = re.compile(r"\s+")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.M)


def normalize(text):
    """Lowercase + whitespace-collapse. Deliberately does NOT strip punctuation:
    Jon's typos and his `--flag` / `path/like/this` tokens are signal."""
    return WS.sub(" ", text.lower()).strip()


def ngrams(text):
    """Character n-grams, deduplicated with counts. Operates on NORMALIZED text."""
    counts = {}
    n_text = len(text)
    for n in NGRAM_SIZES:
        if n_text < n:
            continue
        for i in range(n_text - n + 1):
            g = text[i:i + n]
            counts[g] = counts.get(g, 0) + 1
    return counts


def gram_id(g):
    """Stable 32-bit id. zlib.crc32 is deterministic across runs and processes --
    hash() is NOT (PYTHONHASHSEED randomization), and an index keyed on hash() would
    silently fail to match itself after a restart."""
    return zlib.crc32(g.encode("utf-8")) & 0xFFFFFFFF


def split_sections(text):
    """Yield (heading, start_byte, end_byte, body) using markdown headings.
    Byte offsets are into the ORIGINAL text so provenance survives."""
    marks = [(m.start(), m.group(2)) for m in HEADING.finditer(text)]
    if not marks:
        yield ("(no heading)", 0, len(text), text)
        return
    if marks[0][0] > 0:
        yield ("(preamble)", 0, marks[0][0], text[:marks[0][0]])
    for i, (pos, head) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        yield (head, pos, end, text[pos:end])


def chunk_file(path, text):
    """Heading-scoped chunks, split with overlap when a section is long."""
    out = []
    for head, s, e, body in split_sections(text):
        if len(body.strip()) < MIN_CHUNK_CHARS:
            continue
        if len(body) <= CHUNK_TARGET:
            out.append((head, s, e, body))
            continue
        step = CHUNK_TARGET - CHUNK_OVERLAP
        for off in range(0, len(body), step):
            piece = body[off:off + CHUNK_TARGET]
            if len(piece.strip()) < MIN_CHUNK_CHARS:
                continue
            out.append((head, s + off, s + off + len(piece), piece))
            if off + CHUNK_TARGET >= len(body):
                break
    return out


def collect_sources(repo):
    """Wiki pages + the trunk constitutions. Missing sibling trunks are REPORTED,
    never silently skipped -- an index that quietly covers less than it claims is the
    empty-denominator defect wearing a different hat."""
    files, missing = [], []
    wiki = os.path.join(repo, "wiki")
    for root, dirs, names in os.walk(wiki):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        for nm in names:
            if nm.endswith(".md"):
                files.append(os.path.join(root, nm))
    for c in CONSTITUTIONS:
        (files if os.path.isfile(c) else missing).append(c)
    return files, missing


def build(db_path, repo=REPO, max_df=DEFAULT_MAX_DF, verbose=True):
    t0 = time.time()
    files, missing = collect_sources(repo)

    chunks = []           # (file, heading, start, end, normalized_text)
    for path in files:
        try:
            raw = io.open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for head, s, e, body in chunk_file(path, raw):
            nb = normalize(body)
            if len(nb) >= MIN_CHUNK_CHARS:
                rel = os.path.relpath(path, repo) if path.startswith(repo) else path
                chunks.append((rel, head, s, e, nb))

    n_chunks = len(chunks)
    if n_chunks == 0:
        raise SystemExit("no chunks -- refusing to write an empty index")

    # pass 1: document frequency
    df = {}
    per_chunk = []
    for _, _, _, _, nb in chunks:
        g = ngrams(nb)
        per_chunk.append(g)
        for k in g:
            df[k] = df.get(k, 0) + 1

    # ⛔ FIRST RUN OF THE SELF-TEST FAILED HERE, and the failure is worth keeping in
    # the comment because it is this repo's signature defect in a new place. The line
    # was `df_cut = int(max_df * n_chunks)`. On a 2-chunk fixture that is int(0.7) = 0,
    # so the prune kept only n-grams with df <= 0 -- i.e. NOTHING. The index built
    # "successfully", reported its size, and could never match anything: an EMPTY
    # DENOMINATOR dressed as a clean build. It was caught by the POSITIVE control
    # failing, not by re-reading the build output, which is the standing lesson.
    # A prune threshold below 1 is not a threshold; floor it.
    df_cut = max(1, int(round(max_df * n_chunks)))
    kept = {k: v for k, v in df.items() if v <= df_cut}
    pruned = len(df) - len(kept)

    # pass 2: tf-idf, L2-normalized per chunk
    postings = {}         # gram_id -> list[(chunk_idx, weight)]
    for idx, g in enumerate(per_chunk):
        vec = {}
        for k, tf in g.items():
            d = kept.get(k)
            if not d:
                continue
            vec[k] = (1.0 + math.log(tf)) * math.log(n_chunks / d)
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        for k, w in vec.items():
            postings.setdefault(gram_id(k), []).append((idx, w / norm))

    if os.path.exists(db_path):
        os.remove(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript("""
        PRAGMA journal_mode=OFF;
        CREATE TABLE meta   (k TEXT PRIMARY KEY, v TEXT);
        CREATE TABLE chunk  (id INTEGER PRIMARY KEY, file TEXT, heading TEXT,
                             start INTEGER, end INTEGER, preview TEXT);
        CREATE TABLE post   (gram INTEGER PRIMARY KEY, data BLOB);
        CREATE TABLE idf    (gram INTEGER PRIMARY KEY, v REAL);
        CREATE INDEX chunk_file ON chunk(file);
    """)
    for i, (f, h, s, e, nb) in enumerate(chunks):
        cur.execute("INSERT INTO chunk VALUES (?,?,?,?,?,?)",
                    (i, f, h, s, e, nb[:300]))
    for gid, lst in postings.items():
        blob = b"".join(struct.pack("<If", ci, w) for ci, w in lst)
        cur.execute("INSERT INTO post VALUES (?,?)", (gid, blob))
    for k, d in kept.items():
        cur.execute("INSERT OR REPLACE INTO idf VALUES (?,?)",
                    (gram_id(k), math.log(n_chunks / d)))
    elapsed = time.time() - t0
    for k, v in [
        ("n_chunks", n_chunks), ("n_files", len(files)),
        ("n_grams_kept", len(kept)), ("n_grams_pruned", pruned),
        ("max_df", max_df), ("df_cut", df_cut),
        ("ngram_sizes", ",".join(map(str, NGRAM_SIZES))),
        ("built_at", time.strftime("%Y-%m-%d %H:%M:%S")),
        ("build_seconds", round(elapsed, 2)),
        ("missing_sources", ";".join(missing)),
        ("limitation", "surface similarity only, not semantics -- char n-grams "
                       "match spelling, not meaning"),
    ]:
        cur.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (k, str(v)))
    con.commit()
    con.close()

    size = os.path.getsize(db_path)
    if verbose:
        print("=== graphrag v0 — index built ===")
        print("  files indexed  : %d" % len(files))
        print("  chunks         : %d" % n_chunks)
        print("  n-grams kept   : %d   (pruned %d at df > %d = %.0f%% of chunks)"
              % (len(kept), pruned, df_cut, max_df * 100))
        print("  build time     : %.2f s" % elapsed)
        print("  index size     : %s (%d bytes)" % (human(size), size))
        print("  db             : %s" % db_path)
        if missing:
            print("  ⚠️  MISSING SOURCES (reported, not skipped silently):")
            for m in missing:
                print("        %s" % m)
        print("  ⛔ LIMITATION  : surface similarity, NOT semantics. Char n-grams match")
        print("                   spelling, not meaning. Dense embeddings are the v1 upgrade.")
    return {"chunks": n_chunks, "files": len(files), "seconds": elapsed, "size": size}


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return "%.1f %s" % (n, u)
        n /= 1024.0
    return "%.1f TB" % n


def query(db_path, text, k=5):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    qn = normalize(text)
    g = ngrams(qn)
    if not g:
        return []
    ids = {gram_id(x): tf for x, tf in g.items()}
    idf = {}
    qm = ",".join("?" * len(ids))
    for gid, v in cur.execute("SELECT gram,v FROM idf WHERE gram IN (%s)" % qm,
                              list(ids)):
        idf[gid] = v
    qvec = {gid: (1.0 + math.log(tf)) * idf[gid]
            for gid, tf in ids.items() if gid in idf}
    if not qvec:
        con.close()
        return []
    qnorm = math.sqrt(sum(w * w for w in qvec.values())) or 1.0

    scores = {}
    for gid, w in qvec.items():
        row = cur.execute("SELECT data FROM post WHERE gram=?", (gid,)).fetchone()
        if not row:
            continue
        blob = row[0]
        qw = w / qnorm
        for off in range(0, len(blob), 8):
            ci, cw = struct.unpack_from("<If", blob, off)
            scores[ci] = scores.get(ci, 0.0) + qw * cw

    top = sorted(scores.items(), key=lambda kv: -kv[1])[:k]
    out = []
    for ci, sc in top:
        f, h, s, e, prev = cur.execute(
            "SELECT file,heading,start,end,preview FROM chunk WHERE id=?", (ci,)
        ).fetchone()
        out.append({"score": sc, "file": f, "heading": h,
                    "start": s, "end": e, "preview": prev})
    con.close()
    return out


def grep_count(repo, needle):
    """How many files contain this string EXACTLY. This is the baseline the index has
    to beat -- and reporting it is what makes the demo honest rather than a claim."""
    hits = 0
    for root, dirs, names in os.walk(os.path.join(repo, "wiki")):
        dirs[:] = [d for d in dirs if d != ".git"]
        for nm in names:
            if not nm.endswith(".md"):
                continue
            try:
                t = io.open(os.path.join(root, nm), encoding="utf-8",
                            errors="replace").read()
            except Exception:
                continue
            if needle.lower() in t.lower():
                hits += 1
    for c in CONSTITUTIONS:
        if os.path.isfile(c):
            try:
                if needle.lower() in io.open(c, encoding="utf-8",
                                             errors="replace").read().lower():
                    hits += 1
            except Exception:
                pass
    return hits


# Jon's own misspellings, taken from the spec and from his verbatim record.
# `expect` is what a correct hit looks like -- a substring that must appear in the
# retrieved file path, heading or preview. Written BEFORE running, so the criterion
# cannot be tuned to whatever the index happened to return.
ACCEPT_CASES = [
    ("vector embeding",                    ["embed"]),
    ("stylomantic difference between trunks", ["stylomantic", "trunk"]),
    ("fense is wider than you assume",     ["fense", "fence", "gate"]),
    ("blocer questions",                   ["blocer", "block"]),
    ("Shoudl consider hjelping the coordinator", ["hjelping", "coordinat"]),
    ("focusing on 100% makes performance worse", ["100%", "performance"]),
]


def accept(db_path, repo=REPO):
    print("=== ACCEPTANCE — Jon's own misspellings, index vs grep ===")
    print("Rule: the index must retrieve the right passage where an EXACT grep FAILS.")
    print("Criteria were written before the run; nothing here was tuned to the output.\n")
    passed = failed = 0
    for q, expect in ACCEPT_CASES:
        g = grep_count(repo, q)
        res = query(db_path, q, k=3)
        ok = False
        for r in res:
            hay = (r["file"] + " " + r["heading"] + " " + r["preview"]).lower()
            if any(x.lower() in hay for x in expect):
                ok = True
                break
        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
        print("  QUERY   %r" % q)
        print("    grep exact-string hits : %d %s" % (g, "(grep FAILS — as expected)"
                                                      if g == 0 else "(grep also finds it)"))
        if res:
            r = res[0]
            print("    index top hit         : %.4f  %s :: %s  [bytes %d-%d]"
                  % (r["score"], r["file"], r["heading"][:48], r["start"], r["end"]))
            print("      %s" % r["preview"][:150].replace("\n", " "))
        else:
            print("    index top hit         : NONE")
        print("    VERDICT               : %s\n" % ("PASS" if ok else "FAIL"))
    print("RESULT: %d PASS / %d FAIL   denominator %d" % (passed, failed, len(ACCEPT_CASES)))
    return failed == 0


def self_test():
    """Two-sided: the positive AND the negative must both be exercised, or the test
    cannot fail in one direction and is decoration."""
    import tempfile
    print("=== SELF-TEST — graphrag_v0 ===")
    root = tempfile.mkdtemp(prefix="grag")
    os.makedirs(os.path.join(root, "wiki"), exist_ok=True)
    io.open(os.path.join(root, "wiki", "a.md"), "w", encoding="utf-8").write(
        "# Vector embeddings\n\nDense vector embeddings map text into a metric space "
        "for semantic retrieval and nearest neighbour search over documents.\n")
    io.open(os.path.join(root, "wiki", "b.md"), "w", encoding="utf-8").write(
        "# Roof drainage\n\nGutter maintenance, downspout clearance, and seasonal "
        "leaf removal for a two storey house with a steep pitch.\n")
    db = os.path.join(root, "t.sqlite")
    fails = []

    global CONSTITUTIONS
    saved, CONSTITUTIONS = CONSTITUTIONS, []
    try:
        build(db, repo=root, verbose=False)

        r = query(db, "vector embeding", k=2)          # POSITIVE: typo must still hit
        if not r or "a.md" not in r[0]["file"]:
            fails.append("positive: misspelled 'embeding' did not retrieve a.md")
        print("  POSITIVE  misspelled query retrieves the right page      : %s"
              % ("PASS" if not fails else "FAIL"))

        r2 = query(db, "vector embeding", k=2)
        top_is_roof = bool(r2) and "b.md" in r2[0]["file"]
        if top_is_roof:
            fails.append("negative: unrelated page outranked the right one")
        print("  NEGATIVE  unrelated page does NOT outrank it             : %s"
              % ("FAIL" if top_is_roof else "PASS"))

        r3 = query(db, "gutter downspout", k=1)        # the index must discriminate
        if not r3 or "b.md" not in r3[0]["file"]:
            fails.append("discrimination: roof query did not retrieve b.md")
        print("  DISCRIM   a different query retrieves the OTHER page     : %s"
              % ("PASS" if r3 and "b.md" in r3[0]["file"] else "FAIL"))

        r4 = query(db, "zzzz qqqq xxxx", k=1)          # nonsense must not score high
        junk_high = bool(r4) and r4[0]["score"] > 0.30
        if junk_high:
            fails.append("noise floor: nonsense query scored %.3f" % r4[0]["score"])
        print("  NOISE     nonsense query stays below the floor           : %s"
              % ("FAIL" if junk_high else "PASS"))

        con = sqlite3.connect(db)
        n = con.execute("SELECT v FROM meta WHERE k='n_chunks'").fetchone()[0]
        con.close()
        if int(n) < 2:
            fails.append("denominator: fixture produced %s chunks" % n)
        print("  DENOM     index has a non-zero denominator (%s chunks)     : %s"
              % (n, "PASS" if int(n) >= 2 else "FAIL"))
    finally:
        CONSTITUTIONS = saved

    print()
    if fails:
        for f in fails:
            print("  FAIL: %s" % f)
        print("RESULT: FAIL — %d/5" % (5 - len(fails)))
        return False
    print("RESULT: PASS — 5/5")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="query",
                    choices=["build", "query", "accept"])
    ap.add_argument("text", nargs="?", default="")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--max-df", type=float, default=DEFAULT_MAX_DF)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        sys.exit(0 if self_test() else 4)
    if a.cmd == "build":
        build(a.db, max_df=a.max_df)
        return
    if a.cmd == "accept":
        sys.exit(0 if accept(a.db) else 4)
    if not a.text:
        ap.error("query needs text")
    if not os.path.exists(a.db):
        raise SystemExit("no index at %s — run: build" % a.db)
    for r in query(a.db, a.text, k=a.k):
        print("%.4f  %s :: %s  [bytes %d-%d]"
              % (r["score"], r["file"], r["heading"][:60], r["start"], r["end"]))
        print("        %s" % r["preview"][:180].replace("\n", " "))


if __name__ == "__main__":
    main()
