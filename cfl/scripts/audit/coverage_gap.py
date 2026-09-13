#!/usr/bin/env python3
"""Corpus-vs-wiki coverage gap — the conversations that have NO page at all.

WHY THIS EXISTS, AND WHY EVERY OTHER INSTRUMENT IS BLIND TO IT
--------------------------------------------------------------
Jon, 2026-07-26, correcting the coordinator's read of "wiki complete":

    "Beyond all 218 FL pages. I expect CFL is missing key pages that should exist
     based on raw conversations."

Every method in `lint_citation_coverage.py` — all five — measures **pages that exist**.
M1 asks whether a claim is anchored. M2 asks whether a page is fully covered. None of
them can see a conversation that was never written up at all: a missing page contributes
nothing to any numerator OR denominator, so **it is invisible to every ratio** — it
neither helps nor hurts the score.

That invisibility is the defect. **A coverage ratio cannot distinguish a complete,
well-anchored wiki from a partial, well-anchored wiki.** Both read 100%. The wiki could
reach every threshold in `source-page-standard-v4.md` while silently omitting a third of
what happened, and no instrument in this repo would say a word.

(An earlier draft of this docstring claimed the aggregate *rises* when a page is omitted,
"because the remaining pages are the better-tended ones." That was a causal claim about
pages that do not exist, and it is unfalsifiable — the coverage a page WOULD have had
cannot be measured. Corrected rather than left standing, because a comment that overstates
its own evidence is the same defect as a page that does.)

That is the failure this file exists to make impossible: a completeness measure that
cannot detect absence is not a completeness measure. It is a quality measure wearing the
wrong name.

WHAT COUNTS AS COVERED
----------------------
A conversation is covered if a wiki page points at it — by `source_file:` (authoritative)
or by hash match on the page slug (the corpus's own convention: every transcript filename
carries a 6-hex conversation id, and page slugs end with it).

WHAT COUNTS AS DELIBERATELY UNCOVERED
-------------------------------------
`wiki/sources/session-stubs.md` is the ratified register of conversations reviewed and
judged below ingest threshold. Per CLAUDE.md: *"If a session is referenced in
session-stubs.md but has no source page, it is below ingest threshold — not absent."*
A stub is a DECISION, and decisions are not gaps. They are reported separately so the
distinction stays visible instead of being averaged away.

WHAT IS EXCLUDED FROM THE DENOMINATOR, AND WHY
----------------------------------------------
- `claude-code/subagents/` — agent transcripts, not Jon conversations. 377 of them; they
  would swamp the number and none is a candidate for a source page.
- `jsonl-archive/`, `jsonl-backup/` — recovery copies, not distinct conversations.
Counting either would inflate the gap and make it useless, which is its own way of lying.

Usage:
    python scripts/audit/coverage_gap.py             # summary + per-domain table
    python scripts/audit/coverage_gap.py --list      # every uncovered conversation
    python scripts/audit/coverage_gap.py --min-kb 20 # only conversations above a size floor
    python scripts/audit/coverage_gap.py --strict    # exit 1 if any gap remains
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from turn_index import index  # the ratified turn enumerator — same authority E2 uses

CORPUS = "raw/transcripts"
EXCLUDE_DIRS = ("subagents", "jsonl-archive", "jsonl-backup", "_quarantine")
# `.sidecar.md` is a manifest-v2 COMPANION to a transcript (block timestamps, tool-read logs,
# thinking fidelity tags) — additive metadata, never a conversation. The 2026-07-26 export
# ingest wrote 208 of them, and counting them as conversations would have inflated the corpus
# denominator by 76% and made the coverage gap look better than it is, because every sidecar
# trivially "has no page" while never being a candidate for one.
EXCLUDE_SUFFIXES = (".sidecar.md",)
WIKI_GLOBS = ["wiki/sources", "wiki/personal/sources", "wiki/home/sources", "wiki/pro/sources"]
STUBS = "wiki/sources/session-stubs.md"
QUEUE = "wiki/references/ingest-queue.md"
HEX6 = re.compile(r"[0-9a-f]{6}")


def is_conversation(path):
    """True if the file is an actual multi-turn transcript.

    CALIBRATION, and it moved the headline number by a third. The first run reported 61
    uncovered. Twenty of those were not conversations at all:

      - 4 operational notes living in the corpus tree (AUDIT-NOTES.md, skip-registry.md,
        a pre-nap note, an ingest note) and 1 session-complete stub
      - **15 `*-untitled.md` exports with `char_count: 0`** — genuinely EMPTY on
        claude.ai's side, each marked `extraction_completeness: FULL`, so empty by origin
        rather than truncated in transit. Checked two directly rather than assuming.

    Reporting 61 would have inflated the gap by 49% and put a third of the "missing pages"
    backlog on files that can never have a page. A number that overstates the work is not
    conservative; it is wrong in the direction that wastes Jon's time.

    Uses turn_index.py — the same ratified enumerator E2 anchors resolve against — so
    "is this a conversation" is answered by the repo's one authority on turn structure
    rather than a second guess about filenames.
    """
    try:
        return index(path)["turn_count"] >= 2
    except Exception:
        return False


def conversations(root, require_turns=True):
    """Every corpus conversation transcript, excluding agent/archive material."""
    out = []
    base = os.path.join(root, CORPUS)
    for dirpath, dirnames, files in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in files:
            if fn.endswith(".md") and not fn.endswith(EXCLUDE_SUFFIXES):
                p = os.path.join(dirpath, fn)
                if require_turns and not is_conversation(p):
                    continue
                out.append(p)
    return sorted(out)


def wiki_pages(root):
    """Return (source_file values referenced, hashes present in page slugs)."""
    refs, hashes = set(), set()
    for g in WIKI_GLOBS:
        d = os.path.join(root, g)
        if not os.path.isdir(d):
            continue
        for dirpath, _, files in os.walk(d):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                slug = fn[:-3]
                for h in HEX6.findall(slug):
                    hashes.add(h)
                p = os.path.join(dirpath, fn)
                head = open(p, encoding="utf-8", errors="ignore").read(4000)
                m = re.search(r"^source_file:\s*(.+)$", head, re.M)
                if m:
                    v = m.group(1).split("#")[0].strip()
                    if v and v.lower() not in ("none", "n/a"):
                        refs.add(os.path.normpath(v).replace("\\", "/"))
    return refs, hashes


def stub_hashes(root):
    p = os.path.join(root, STUBS)
    if not os.path.isfile(p):
        return set(), 0
    text = open(p, encoding="utf-8", errors="ignore").read()
    ids = set()
    reclassified = 0
    for line in text.splitlines():
        m = re.match(r"^\|\s*([0-9a-f]{6})\s*\|", line)
        if m:
            # A RECLASSIFIED row means the stub decision was reversed and a page now
            # exists. Counting it as still-a-stub would hide a page that was written.
            if "RECLASSIFIED" in line:
                reclassified += 1
                continue
            ids.add(m.group(1))
    return ids, reclassified


def queue_hashes(root):
    """Conversations with a recorded row in the INGEST QUEUE — a second decision register.

    FOUND 2026-07-26, and it moved the headline number. This script only ever read
    `session-stubs.md`, so a conversation examined and *queued for ingest* in
    `wiki/references/ingest-queue.md` was reported as "no page, no stub decision" — i.e.
    indistinguishable from one nobody had ever looked at. A mirror dispatch surfaced it:
    9 of 14 conversations this script called undispositioned had rows in the queue.

    That is this program's own characteristic failure, one level up: TWO registers record the
    same class of decision and the instrument knew about one of them. The wiki was right and the
    measurement was wrong, which is exactly the precedence the repo already ratified (wiki wins).

    WHY QUEUED IS ITS OWN BUCKET AND NOT FOLDED INTO STUBBED. They are opposite decisions:
      - a STUB says "examined, below threshold, NO page is owed"  -> closed
      - a QUEUE row says "examined, a page IS owed, not yet written" -> open work
    Merging them would hide committed-but-unwritten work inside a bucket labelled "decided,"
    which is how a backlog disappears. Both are distinct from UNCOVERED, which means unexamined —
    and it is the unexamined class Jon's coverage goalpost is actually aimed at.

    Ids appear both as table rows and in prose roll-ups ("Still open from prior queue: `a3e6cf`,
    `44a95b`…", "Skipped this SU with note: `7f2022`…"), all of which are recorded dispositions,
    so backticked ids are harvested from the whole file rather than from one table.
    """
    p = os.path.join(root, QUEUE)
    if not os.path.isfile(p):
        return set()
    text = open(p, encoding="utf-8", errors="ignore").read()
    return set(re.findall(r"`([0-9a-f]{6})`", text))


def domain_of(path):
    p = os.path.normpath(path).replace("\\", "/")
    parts = p.split("/")
    i = parts.index("sessions") if "sessions" in parts else -1
    if i >= 0 and i + 2 < len(parts):
        return parts[i + 1]
    return "(loose)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true", help="print every uncovered conversation")
    ap.add_argument("--min-kb", type=float, default=0.0,
                    help="only count conversations at least this large (materiality floor)")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--include-nonconv", action="store_true",
                    help="do not filter out zero/one-turn files (shows what the filter removes)")
    a = ap.parse_args()

    convs = conversations(a.root, require_turns=not a.include_nonconv)
    refs, hashes = wiki_pages(a.root)
    stubs, reclassified = stub_hashes(a.root)
    queue = queue_hashes(a.root)

    # DEDUPE BY CONVERSATION, NOT BY FILE. Measured 2026-07-26: 288 transcript files but only
    # 259 distinct conversations — the same conversation is exported more than once when it is
    # both domain-routed and re-exported later (`090a56` had three copies, `576125` three).
    # Counting files inflated the denominator ~9% and, worse, let one conversation appear in
    # BOTH the covered and uncovered buckets. A conversation is covered if ANY of its copies
    # has a page; its size is the largest copy, since a truncated earlier export is not
    # evidence about how material the conversation is.
    groups = {}
    for p in convs:
        rel = os.path.relpath(p, a.root).replace(os.sep, "/")
        ids = HEX6.findall(os.path.basename(p)[:-3])
        key = ids[0] if ids else rel          # no id -> the file is its own conversation
        groups.setdefault(key, []).append(rel)

    covered, stubbed, queued, gap = [], [], [], []
    conflicts = []
    for key, rels in groups.items():
        size_kb = max(os.path.getsize(os.path.join(a.root, r)) for r in rels) / 1024.0
        h = {key} if HEX6.fullmatch(key) else set()
        rep = max(rels, key=lambda r: os.path.getsize(os.path.join(a.root, r)))
        in_stub, in_queue = bool(h & stubs), bool(h & queue)
        # Both registers claiming the same conversation is a real finding, not a tie to break
        # silently: one says no page is owed, the other says one is. Reported, then resolved
        # toward the queue, because "a page is owed" is the claim that costs something if wrong.
        if in_stub and in_queue:
            conflicts.append(key)
        if any(r in refs for r in rels) or (h & hashes):
            covered.append((rep, size_kb))
        elif in_queue:
            queued.append((rep, size_kb))
        elif in_stub:
            stubbed.append((rep, size_kb))
        else:
            gap.append((rep, size_kb))

    gap = [g for g in gap if g[1] >= a.min_kb]
    total = len(groups)
    n_files = len(convs)

    print("=== CORPUS-vs-WIKI COVERAGE GAP — conversations with NO page at all ===\n")
    print("Every method in lint_citation_coverage.py measures pages that EXIST. A missing")
    print("page contributes to no numerator and no denominator, so omitting one makes the")
    print("aggregate go UP. This is the instrument that can see absence.\n")
    print(f"  distinct conversations (deduped by id)          : {total}")
    print(f"  transcript files behind them                    : {n_files}")
    print(f"  covered by a wiki page                          : {len(covered)}"
          f"  ({100*len(covered)//total if total else 0}%)")
    print(f"  deliberately stubbed — no page owed             : {len(stubbed)}")
    print(f"  QUEUED for ingest — a page IS owed, unwritten   : {len(queued)}")
    print(f"  UNCOVERED — unexamined, no record anywhere      : {len(gap)}"
          f"  ({100*len(gap)//total if total else 0}%)"
          + (f"   [size floor {a.min_kb:g}KB]" if a.min_kb else ""))
    if reclassified:
        print(f"  (stub rows marked RECLASSIFIED, i.e. a page was later written: {reclassified})")
    if conflicts:
        print(f"\n  !! {len(conflicts)} conversation(s) in BOTH registers — one says no page is owed,")
        print(f"     the other says one is. Resolved toward QUEUED here; the disagreement is real:")
        print(f"     {', '.join(sorted(conflicts))}")
    print("\n  STUBBED and QUEUED are both DECISIONS and neither is the gap. UNCOVERED means")
    print("  unexamined — nobody has looked, and the wiki cannot tell that from 'not worth it'.")
    print("  That distinction is what the coverage goalpost is aimed at (Jon, 2026-07-26).")

    by = {}
    for rel, kb in gap:
        d = domain_of(rel)
        by.setdefault(d, []).append((rel, kb))
    if by:
        print(f"\n  {'domain':<22} {'uncovered':>9} {'total KB':>9}  {'largest uncovered':<50}")
        print(f"  {'-'*22} {'-'*9} {'-'*9}  {'-'*50}")
        for d in sorted(by, key=lambda k: -sum(x[1] for x in by[k])):
            items = sorted(by[d], key=lambda x: -x[1])
            print(f"  {d:<22} {len(items):>9} {sum(x[1] for x in items):>9.0f}  "
                  f"{os.path.basename(items[0][0])[:50]}")

    if a.list:
        print(f"\n  --- every uncovered conversation, largest first ---")
        for rel, kb in sorted(gap, key=lambda x: -x[1]):
            print(f"    {kb:>8.1f}KB  {rel}")
    elif gap:
        print(f"\n  --- 15 largest uncovered (rerun --list for all) ---")
        for rel, kb in sorted(gap, key=lambda x: -x[1])[:15]:
            print(f"    {kb:>8.1f}KB  {rel}")

    print()
    if gap:
        print(f"{len(gap)} conversations have no page and no recorded decision not to write one.")
        print("Each is either a page that should exist, or a stub row that was never added.")
        print("Both are work; neither is visible to any other instrument in this repo.")
        return 1 if a.strict else 0
    print("No gap: every conversation has a page or a recorded stub decision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
