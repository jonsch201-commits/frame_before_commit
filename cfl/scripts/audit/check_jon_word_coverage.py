#!/usr/bin/env python3
"""check_jon_word_coverage.py — measure Jon's own standard against the record.

THE STANDARD, VERBATIM
-----------------------
    "Every word I've ever said should likely impact at least one concept, or have it's
     negative citation explained. You should consider if the explanation is valid."

THE FINDING THAT COMES BEFORE ANY NUMBER
------------------------------------------
Until 2026-08-06 this standard was **not merely unmet — it was unmeasurable.** A standard of the
form *"every X should do Y"* is a fraction, and **nothing in this repo enumerated X.** There was
no list of the things Jon had said. `scripts/audit/jon_utterances.py` is that list and this script
is the fraction; they are separate files on purpose, so that a change to the impact matcher can
never quietly change how many utterances there were.

WHAT THIS MEASURES, AND THE THREE STATES IT REFUSES TO COLLAPSE
----------------------------------------------------------------
For each utterance, where did it land? The classes are ordered, the first hit wins, and **every**
class that hit is recorded so a reader can see near-misses:

  CONCEPT       `wiki/concepts/**`  — the surface Jon's standard actually names.
  DURABLE-WIKI  the rest of the tracked wiki: `log.md`, `sources/`, `references/`, `tracker/`,
                `index.md`. Durable, citable, but NOT a concept. Named separately because
                collapsing it into "covered" is how a wiki reports completeness it does not have.
  DURABLE-OTHER `exchange/`, `skills/`, `scripts/`, `docs/`, `CLAUDE.md`, `.claude/agents/`.
  QUEUE         `wiki/intake-triage/**` — packets awaiting disposition. **A deposit is not a
                concept.** The brief that commissioned this instrument is explicit: *"An
                `intake-triage/` deposit is not a concept — it is a queue."* A queue entry is
                evidence that something was noticed, and evidence of nothing else.
  CAPTURE-ONLY  `wiki/intake-triage/{agent-end,main-thread}/**` — the mechanical I1 extracts.
                **This class exists to defuse a trap this instrument would otherwise fall into;
                see below.** Mechanical capture is not impact.
  NONE          no tracked surface in this repo contains this utterance.

  UNMATCHABLE   the utterance is too short to fingerprint (`YOU STOPPED!`, `Fuck you.`). Reported
                as its own state with its own count. **It is neither a pass nor a fail** — the
                instrument simply cannot see these, and saying so is the honest report.

THE TRAP, NAMED, BECAUSE IT WOULD HAVE PRODUCED A 100% PASS
-------------------------------------------------------------
`main_thread_ingest.py` writes every one of Jon's utterances, verbatim, into a TRACKED file under
`wiki/intake-triage/main-thread/`. A matcher that searched "all of `wiki/`" would therefore find
every single utterance — **in the file this same session wrote an hour ago** — and report perfect
coverage. The instrument would be satisfied by its own output.

This is not hypothetical. `agent_end_ingest.py`'s own header records the near-miss: an `.i1.md`
placed next to the transcript would have made `scan_midturn_messages.py` report Jon's quotes
"present in the corpus" even if extraction had failed — *"an instrument built to prove Jon's words
are not dropped would have been satisfied by this script's own output."* Same shape, one layer up.

So CAPTURE-ONLY is a **distinct terminal state**, ranked below QUEUE, and a hit there is reported
as `capture, no impact`. Recording that Jon said something is not the same as anything having
happened because he said it.

THE SECOND STATE THAT IS NOT A PASS: SILENCE
----------------------------------------------
Jon's standard permits a negative citation — an utterance may have no concept impact **if the
reason is explained.** It does not permit silence. So every non-CONCEPT utterance is additionally
checked for an explanation, and the result is one of:

  EXPLAINED  a negative citation that actually references this utterance exists.
  SILENT     nothing anywhere explains it.

**SILENT is rendered as its own state and never as a pass.** The distinction is the whole point of
the second clause of the standard.

The Negative Citation mechanism is real and ratified — `wiki/concepts/wiki-ingest-methodology.md`,
established 2026-05-27, Type 1 (Inward Gap) discharged by an `## Uncaptured Content` section using
a four-category taxonomy. **But it operates at SOURCE-PAGE granularity and Jon's standard is at
WORD granularity.** A page-level "unfollowed threads" bullet does not explain why utterance J27 hit
nothing. That granularity mismatch is reported as a finding, not silently treated as coverage.

MATCHING — AND WHAT WOULD MAKE IT LIE
---------------------------------------
Whitespace-collapsed, case-folded windows (`jon_utterances.normalize`, the same normalisation used
everywhere, which `find_unechoed_rulings.py` needed after five zero-echo flags turned out to be
five markdown line-wraps). Windows of WINDOW chars at STRIDE, any one hit counts.

This is a VERBATIM-ECHO matcher. It answers *"do these words appear on this surface"* and nothing
more. Every way it can be wrong is printed in the report itself, under
`WHAT WOULD MAKE THIS REPORT A FALSE PASS` — not left in a docstring nobody opens.

Exit code is **always 0**. This is a measurement, not a gate. A high number here should make the
reader suspicious of the matcher before it makes them satisfied: Jon, 2026-08-06 — *"Getting worse
is getting better if worse is more true than the prior measure."*

Usage:
  check_jon_word_coverage.py                     # every CFL session that has a transcript
  check_jon_word_coverage.py --session f01909    # one session
  check_jon_word_coverage.py --full              # print every utterance, not just the head
  check_jon_word_coverage.py --json PATH         # machine-readable alongside the report
  check_jon_word_coverage.py --self-test         # negative controls
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent
for _p in (str(_SCRIPTS), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import extract_claude_code_sessions as X   # noqa: E402
import jon_utterances as JU                # noqa: E402

# ⛔ Same defect as main_thread_ingest.py:114, fixed the same hour: this script walks "the
# tracked prose surfaces," so REPO must be THE WORKING CLONE. X.ROOT is the CORPUS root, pinned
# to the G: clone, which is on a stale branch -- so this coverage report was grading a tree that
# is not the one being committed. A coverage number measured against the wrong tree is not a low
# score, it is NOT A MEASUREMENT. Pattern taken verbatim from agent_end_ingest.py:172 (2026-09-03).
# ⛔ THE FALLBACK USED TO BE `or X.ROOT`, AND X.ROOT IS A HARDCODED ABSOLUTE PATH TO THE
# G: CLONE (extract_claude_code_sessions.py:69). So a hand run with CLAUDE_PROJECT_DIR unset
# wrote TRACKED FILES INTO A STALE CHECKOUT ON ANOTHER BRANCH, silently and successfully.
# [measured 2026-09-04 22:4x: the G: tree's uncommitted count GREW 3,140 -> 3,462 -> 3,491
# across twenty minutes while nobody was editing it -- Professional's restart gate R1.]
# ⭐ DERIVE THE CHECKOUT FROM THIS FILE, never from a recorded path: parents[2] of
# scripts/audit/<this>.py IS the repo that contains the code being run, in EVERY clone, and
# it cannot name a tree the caller is not in. (derive-don't-record, the trunk's own named
# characteristic failure.) X.ROOT remains correct where it is used as the CORPUS root.
_CHECKOUT = Path(__file__).resolve().parents[2]
REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR") or _CHECKOUT)

# --- MATCHER PARAMETERS. Printed in the report, not just declared here. -----------------------
WINDOW = 40      # chars of normalised text per fingerprint window
STRIDE = 20      # overlap, so a match spanning a window boundary is still caught
MIN_MATCHABLE = 30   # below this an utterance has no distinctive fingerprint at all

# --- SURFACE CLASSES, IN PRIORITY ORDER. First hit wins; all hits are recorded. ---------------
# `roots` are repo-relative; `exclude` prunes subtrees that belong to a LATER class, so a file is
# in exactly one class and the classes partition the corpus rather than overlapping.
SURFACES = [
    ("CONCEPT", ["wiki/concepts"], []),
    ("DURABLE-WIKI", ["wiki"], ["wiki/concepts", "wiki/intake-triage"]),
    ("DURABLE-OTHER", ["exchange", "skills", "scripts", "docs", "CLAUDE.md", "README.md"], []),
    ("QUEUE", ["wiki/intake-triage"],
     ["wiki/intake-triage/agent-end", "wiki/intake-triage/main-thread"]),
    ("CAPTURE-ONLY", ["wiki/intake-triage/agent-end", "wiki/intake-triage/main-thread"], []),
]
CLASS_ORDER = [s[0] for s in SURFACES] + ["NONE"]
IMPACT_CLASSES = ("CONCEPT", "DURABLE-WIKI", "DURABLE-OTHER")

# Where a per-utterance negative citation could possibly be recorded. The ratified mechanism is
# `## Uncaptured Content` on a source page (wiki/concepts/wiki-ingest-methodology.md, 2026-05-27).
UNCAPTURED_HEADING = "## uncaptured content"


def load_class(roots, excludes):
    """([(relpath, normalised_text)], bytes_read). Markdown only; the tracked prose surfaces."""
    files, nbytes = [], 0
    ex = [str(REPO / e).replace("\\", "/").rstrip("/") for e in excludes]
    for r in roots:
        p = REPO / r
        if p.is_file():
            cands = [p]
        elif p.is_dir():
            cands = sorted(p.rglob("*.md"))
        else:
            continue
        for f in cands:
            s = str(f).replace("\\", "/")
            if any(s == e or s.startswith(e + "/") for e in ex):
                continue
            try:
                raw = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            nbytes += len(raw)
            files.append((os.path.relpath(f, REPO).replace("\\", "/"), JU.normalize(raw)))
    return files, nbytes


def build_corpus():
    """{class -> (files, blob, nbytes)}. The blob is a cheap pre-filter; files give evidence."""
    out = {}
    for name, roots, ex in SURFACES:
        files, nbytes = load_class(roots, ex)
        out[name] = (files, "\n".join(t for _, t in files), nbytes)
    return out


def windows(norm):
    """Fingerprint windows for one normalised utterance, or [] when it is too short."""
    if len(norm) < MIN_MATCHABLE:
        return []
    if len(norm) <= WINDOW:
        return [norm]
    return [norm[i:i + WINDOW] for i in range(0, len(norm) - WINDOW + 1, STRIDE)]


def classify(utt, corpus):
    """(winning_class, all_hits, evidence_path). NONE / UNMATCHABLE handled by the caller."""
    norm = JU.normalize(utt["text"])
    wins = windows(norm)
    if not wins:
        return "UNMATCHABLE", [], None
    hits, evidence = [], None
    for name, _roots, _ex in SURFACES:
        files, blob, _n = corpus[name]
        if not any(w in blob for w in wins):
            continue
        hits.append(name)
        if evidence is None:
            for rel, text in files:
                if any(w in text for w in wins):
                    evidence = rel
                    break
    return (hits[0] if hits else "NONE"), hits, evidence


def find_explanation(utt, corpus, session_uuid6):
    """(state, evidence). EXPLAINED only when something actually references THIS utterance.

    Two admissible forms, both requiring a reference to the utterance itself:
      1. The utterance's own text appears under an `## Uncaptured Content` heading — the ratified
         Type 1 negative citation.
      2. Its turn anchor (`<uuid6>` + `T{n}`) appears within an Uncaptured Content section.

    A page-level "unfollowed threads" bullet that names no utterance is NOT an explanation for a
    specific utterance, and counting it as one is precisely the collapse this instrument exists to
    prevent. When in doubt the answer is SILENT, because SILENT is the state the standard forbids
    and an instrument that resolves doubt in the direction of a pass is decoration.
    """
    norm = JU.normalize(utt["text"])
    wins = windows(norm)
    anchor = f"{session_uuid6} t{utt['turn']}" if utt.get("turn") else None
    for name in ("CONCEPT", "DURABLE-WIKI", "DURABLE-OTHER", "QUEUE"):
        files, _blob, _n = corpus[name]
        for rel, text in files:
            i = text.find(UNCAPTURED_HEADING)
            if i < 0:
                continue
            section = text[i:i + 6000]      # the section, not the whole page
            if wins and any(w in section for w in wins):
                return "EXPLAINED", rel
            if anchor and anchor in section:
                return "EXPLAINED", rel
    return "SILENT", None


def report(sessions, corpus, full, out_json):
    tot_utts = tot_records = 0
    tot_midturn_raw = tot_dupes = 0
    ledger = {}
    rows = []

    for s in sessions:
        enum = s["enum"]
        tot_records += sum(enum["class_counts"].values())
        tot_midturn_raw += enum["midturn_raw"]
        tot_dupes += enum["midturn_dupes"]
        for k, v in enum["class_counts"].items():
            ledger[k] = ledger.get(k, 0) + v
        for u in enum["utterances"]:
            tot_utts += 1
            cls, hits, evid = classify(u, corpus)
            expl, expl_evid = ("N/A", None)
            if cls != "CONCEPT":
                expl, expl_evid = find_explanation(u, corpus, s["uuid6"])
            rows.append({
                "session": s["uuid6"], "n": u["n"], "cls": u["cls"],
                "turn": u["turn"], "chars": u["chars"],
                "text": " ".join(u["text"].split()),
                "impact": cls, "all_hits": hits, "evidence": evid,
                "explanation": expl, "explanation_evidence": expl_evid,
            })

    # ================= DENOMINATORS FIRST. Not in a docstring — in the output. =================
    print()
    print("=" * 78)
    print("JON WORD COVERAGE — measured against Jon's own standard")
    print("=" * 78)
    print('  "Every word I\'ve ever said should likely impact at least one concept,')
    print('   or have it\'s negative citation explained."')
    print()
    print("--- DENOMINATORS ---------------------------------------------------------")
    print(f"  sessions scanned                : {len(sessions)}")
    for s in sessions:
        print(f"      {s['uuid6']}  {len(s['enum']['utterances']):>3} utterance(s)  "
              f"{Path(s['jsonl']).name[:14]}")
    print(f"  `type: user` records read       : {tot_records}")
    print(f"  record class ledger             : {json.dumps(ledger, sort_keys=True)}")
    print(f"      counted as utterances       : {', '.join(JU.COUNTED_CLASSES)}")
    print(f"  mid-turn raw hits / duplicates  : {tot_midturn_raw} / {tot_dupes} "
          f"(one message to N running agents lands N times; it is ONE utterance)")
    print()
    print(f"  ***  JON UTTERANCES (THE DENOMINATOR) : {tot_utts}  ***")
    print()
    matchable = [r for r in rows if r["impact"] != "UNMATCHABLE"]
    unmatchable = [r for r in rows if r["impact"] == "UNMATCHABLE"]
    print(f"  matchable (>= {MIN_MATCHABLE} normalised chars) : {len(matchable)}")
    print(f"  UNMATCHABLE by length             : {len(unmatchable)}  "
          f"— neither a pass nor a fail; the matcher cannot see these")
    for r in unmatchable:
        print(f"      J{r['n']} ({r['chars']} chars) {r['text'][:52]!r}")
    print()
    print("--- SEARCH CORPUS --------------------------------------------------------")
    for name, _roots, _ex in SURFACES:
        files, _blob, nbytes = corpus[name]
        print(f"  {name:<14} {len(files):>4} file(s)  {nbytes:>9,} chars")
    print(f"  matcher: {WINDOW}-char windows, stride {STRIDE}, whitespace-collapsed + case-folded")
    print()

    # ================= THE SPLIT =================
    print("--- IMPACT SPLIT ---------------------------------------------------------")
    counts = {c: 0 for c in CLASS_ORDER}
    for r in matchable:
        counts[r["impact"]] = counts.get(r["impact"], 0) + 1
    den = len(matchable) or 1
    labels = {
        "CONCEPT": "concept page — MEETS the standard",
        "DURABLE-WIKI": "other durable wiki surface — NOT a concept",
        "DURABLE-OTHER": "exchange/skills/scripts/docs — NOT a concept",
        "QUEUE": "intake-triage packet — A QUEUE, NOT AN IMPACT",
        "CAPTURE-ONLY": "mechanical I1 extract only — CAPTURE, NOT IMPACT",
        "NONE": "NO IMPACT RECORDED ANYWHERE",
    }
    for c in CLASS_ORDER:
        print(f"  {c:<14} {counts[c]:>4}  ({counts[c] / den:5.1%})  {labels[c]}")
    impacted = sum(counts[c] for c in IMPACT_CLASSES)
    print()
    print(f"  concept impact       : {counts['CONCEPT']}/{len(matchable)} "
          f"({counts['CONCEPT'] / den:.1%})  <- the standard's own numerator")
    print(f"  any durable surface  : {impacted}/{len(matchable)} ({impacted / den:.1%})")
    print(f"  no durable surface   : {len(matchable) - impacted}/{len(matchable)} "
          f"({(len(matchable) - impacted) / den:.1%})")
    # THE COUNTERFACTUAL, PRINTED. CAPTURE-ONLY is not a stable property of the record — it is a
    # property of a file this pipeline wrote. Without that file these utterances read NONE. Saying
    # so keeps a capture layer from looking like a coverage improvement, which is exactly how a
    # measure gets gamed by the thing it measures.
    from_mainthread = sum(
        1 for r in matchable
        if r["impact"] == "CAPTURE-ONLY" and (r["evidence"] or "").startswith(
            "wiki/intake-triage/main-thread/"))
    print(f"  of the {counts['CAPTURE-ONLY']} CAPTURE-ONLY, {from_mainthread} are evidenced ONLY by "
          f"a main-thread I1 extract")
    print(f"  written by this same pipeline. **Delete that file and they read NONE.** Capture is "
          f"not coverage;")
    print(f"  the pre-capture equivalent of 'no impact recorded' is "
          f"{counts['CAPTURE-ONLY'] + counts['NONE']}/{len(matchable)} "
          f"({(counts['CAPTURE-ONLY'] + counts['NONE']) / den:.1%}).")
    print()

    # ================= THE SECOND CLAUSE =================
    print("--- NEGATIVE CITATION: IS THE ABSENCE EXPLAINED? -------------------------")
    need = [r for r in matchable if r["impact"] != "CONCEPT"]
    explained = [r for r in need if r["explanation"] == "EXPLAINED"]
    silent = [r for r in need if r["explanation"] == "SILENT"]
    print(f"  utterances with no concept impact : {len(need)}")
    print(f"    EXPLAINED (negative citation)   : {len(explained)}")
    print(f"    SILENT                          : {len(silent)}  <- the state the standard forbids")
    print()
    print("  The Negative Citation mechanism EXISTS and is ratified — "
          "wiki/concepts/wiki-ingest-methodology.md,")
    print("  2026-05-27, Type 1 (Inward Gap), discharged by an `## Uncaptured Content` section.")
    print("  **It operates at SOURCE-PAGE granularity. Jon's standard is at WORD granularity.**")
    print("  A page-level 'unfollowed threads' bullet does not explain why one utterance landed")
    print("  nowhere, and is not counted here as though it did.")
    print()

    # ================= THE ENUMERATION =================
    print("--- ENUMERATION ----------------------------------------------------------")
    print("  This list IS the denominator. It did not exist in this repo before 2026-08-06.")
    print()
    shown = rows if full else [r for r in rows if r["impact"] not in ("CONCEPT",)]
    if not full:
        print(f"  (showing {len(shown)} of {len(rows)}; --full prints every utterance)")
    hdr = f"  {'#':>4} {'sess':<7} {'anchor':<8} {'kind':<10} {'impact':<13} {'expl':<9} text"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for r in shown:
        anchor = f"T{r['turn']}" if r["turn"] else "-"
        print(f"  J{r['n']:<3} {r['session']:<7} {anchor:<8} {r['cls']:<10} "
              f"{r['impact']:<13} {r['explanation']:<9} {r['text'][:58]}")
        if r["evidence"]:
            print(f"       -> {r['evidence']}")
    print()

    # ================= FALSIFICATION, PRINTED =================
    print("--- WHAT WOULD MAKE THIS REPORT A FALSE PASS -----------------------------")
    print("  Read this before believing any number above. Every item is a way the matcher")
    print("  reports MORE coverage than exists.")
    print()
    print("  1. SELF-SATISFACTION. main_thread_ingest.py writes every utterance verbatim into")
    print("     wiki/intake-triage/main-thread/. Search 'all of wiki/' and coverage is 100%,")
    print("     found in a file this same session wrote. That is why CAPTURE-ONLY is a separate")
    print("     terminal class ranked below QUEUE. **If CAPTURE-ONLY is ever folded into a")
    print("     'covered' bucket, this instrument becomes decoration.**")
    print("  2. VERBATIM-ECHO ONLY. A concept page that acts on Jon's ruling in its own words,")
    print("     citing no quote, reads as NONE here. The instrument UNDER-reports real impact of")
    print("     that kind — the same blindness find_unechoed_rulings.py documents, where R12 was")
    print("     echoed everywhere and obeyed nowhere. Echo and impact are different predicates;")
    print("     this measures echo.")
    print("  3. QUOTATION IS NOT ACTION. An utterance pasted into a dispatch brief in exchange/")
    print("     scores DURABLE-OTHER. Something quoted him. Nothing necessarily changed.")
    print(f"  4. SHORT UTTERANCES ARE INVISIBLE. {len(unmatchable)} fell under the "
          f"{MIN_MATCHABLE}-char floor and are")
    print("     excluded from the ratio denominator entirely. They are counted and listed above,")
    print("     never averaged away — but a smaller denominator flatters every percentage.")
    print("  5. LIVE SESSION. A running session's transcript grows; utterances after the last")
    print("     read are outside the denominator. The count is a floor.")
    print("  6. EXPLANATION DETECTION IS NARROW. Only `## Uncaptured Content` sections are read,")
    print("     and only when they reference the utterance. A negative citation written in some")
    print("     other form scores SILENT. This direction is deliberate: doubt resolves toward")
    print("     SILENT, because SILENT is the state the standard forbids.")
    print()
    print("  A first run reporting HIGH coverage is evidence of a broken matcher, not of a")
    print("  well-tended wiki.  Jon, 2026-08-06: \"Getting worse is getting better if worse is")
    print("  more true than the prior measure.\"")
    print()
    print("--- WHAT THIS INSTRUMENT DOES NOT DO -------------------------------------")
    print("  It does not promote anything to wiki/concepts/. Promotion is I2/I3 — judgment,")
    print("  wiki-master's, in an interactive session. This measures the gap; it does not close")
    print("  it. \"Recording is not gated on merit; synthesis is.\"")
    print()

    if out_json:
        payload = {
            "denominator": tot_utts, "matchable": len(matchable),
            "unmatchable": len(unmatchable), "impact_counts": counts,
            "explained": len(explained), "silent": len(silent),
            "record_ledger": ledger, "rows": rows,
            "matcher": {"window": WINDOW, "stride": STRIDE, "min": MIN_MATCHABLE},
        }
        Path(out_json).write_text(json.dumps(payload, indent=1), encoding="utf-8")
        print(f"  json written: {out_json}")
    return 0


def gather(session_filter):
    """[{uuid6, jsonl, enum}] for every top-level CFL session with utterances."""
    out = []
    for _proj, jf in X.iter_session_jsonls():
        if session_filter and session_filter not in jf.stem:
            continue
        uuid6 = jf.stem[:6]
        mds = X.existing_mds(uuid6)
        sidecar = X.sidecar_for(mds[0]) if mds else None
        enum = JU.enumerate_session(jf, sidecar if sidecar and sidecar.exists() else None)
        if not enum["utterances"]:
            continue
        out.append({"uuid6": uuid6, "jsonl": str(jf), "enum": enum})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="session uuid substring")
    ap.add_argument("--full", action="store_true", help="print every utterance")
    ap.add_argument("--json", dest="out_json", help="write machine-readable results here")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    corpus = build_corpus()
    sessions = gather(args.session)
    if not sessions:
        # Zero scanned is not zero findings. Say so; never print a pass.
        print("[no sessions matched] — this is NOT a pass. Nothing was measured.", file=sys.stderr)
        return 0
    return report(sessions, corpus, args.full, args.out_json)


def self_test():
    """Negative controls. The direction that matters is the one that inflates coverage."""
    ok = True
    print("=== SELF-TEST — check_jon_word_coverage ===")
    corpus = build_corpus()

    def probe(text, turn=None):
        return classify({"text": text, "turn": turn}, corpus)

    # 1. A string that cannot be on any surface must report NONE.
    absent = ("zzqx negative control " + "9f3a7c1e" * 5 +
              " this sentence exists in no tracked file whatsoever")
    cls, hits, _ = probe(absent)
    good = cls == "NONE" and not hits
    ok = ok and good
    print(f"  {'PASS' if good else 'FAIL'}  absent text reports NONE (the check can fire)")

    # 2. A string known to be in a concept page must report CONCEPT.
    concepts = corpus["CONCEPT"][0]
    seed, seed_src = None, None
    for rel, text in concepts:
        if len(text) > 4000:
            seed, seed_src = text[2000:2000 + 120], rel
            break
    if seed:
        cls, hits, evid = probe(seed)
        good = cls == "CONCEPT"
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  known concept text reports CONCEPT "
              f"(evidence: {evid or '-'})")
    else:
        print("  SKIP  no concept page large enough to seed the positive control")

    # 3. THE TRAP. Text present ONLY in an I1 extract must report CAPTURE-ONLY, never CONCEPT
    #    and never any DURABLE class. This is the control that keeps the instrument from being
    #    satisfied by its own output.
    cap_files = corpus["CAPTURE-ONLY"][0]
    trapped = None
    for rel, text in cap_files:
        # Look for a long verbatim span unique to the extract: its own banner sentence.
        i = text.find("mid-session snapshot, not the final extract")
        if i >= 0:
            trapped = text[i:i + 120]
            break
    if trapped:
        cls, hits, evid = probe(trapped)
        good = cls == "CAPTURE-ONLY" and "CONCEPT" not in hits
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  extract-only text reports CAPTURE-ONLY, "
              f"not CONCEPT  (the self-satisfaction trap)")
    else:
        print("  SKIP  no I1 extract on disk to seed the self-satisfaction control")

    # 4. Short text must be UNMATCHABLE, not silently NONE — a wrong pass in the other direction
    #    (a 4-char utterance would match everywhere).
    cls, _h, _e = probe("YOU STOPPED!")
    good = cls == "UNMATCHABLE"
    ok = ok and good
    print(f"  {'PASS' if good else 'FAIL'}  short utterance reports UNMATCHABLE, not NONE")

    # 5. Classes must PARTITION: no file may appear in two classes, or a hit would be
    #    attributed to whichever class was checked first and the counts would double.
    seen, dup = {}, []
    for name, _r, _e in SURFACES:
        for rel, _t in corpus[name][0]:
            if rel in seen:
                dup.append((rel, seen[rel], name))
            seen[rel] = name
    good = not dup
    ok = ok and good
    print(f"  {'PASS' if good else 'FAIL'}  surface classes partition the corpus "
          f"({len(seen)} files, {len(dup)} in two classes)")

    # 6. An explanation must not be granted by an `## Uncaptured Content` heading alone.
    st, _ev = find_explanation({"text": absent, "turn": None}, corpus, "zzzzzz")
    good = st == "SILENT"
    ok = ok and good
    print(f"  {'PASS' if good else 'FAIL'}  an Uncaptured Content section that names nothing "
          f"does NOT explain")

    print("\nRESULT: " + ("PASS — the instrument can fire, and cannot be satisfied by its own "
                          "output." if ok else "FAIL — do not report its numbers."))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(0)     # never blocks
