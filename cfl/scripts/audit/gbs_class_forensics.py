#!/usr/bin/env python3
"""gbs_class_forensics.py — WHY a transcript landed in PARTIAL or APPLICABLE-NOT-USED.

WHAT QUESTION THIS ANSWERS THAT `gbs_record.py` DOES NOT
----------------------------------------------------------
`gbs_record.py` produces the three classes and is not forked here — every class, rule,
pattern, span-splitter and merge rule below is IMPORTED from it. What it cannot say is
**what put a file in a class**, and on 2026-08-07 that turned out to be the whole finding:

  * **PARTIAL is not mostly "kinda did".** 129 of 171 PARTIAL files had NO invocation
    evidence except an `ASOP <n>` number, and 117 of 171 had every invocation sitting
    inside a **Tool Result** — a grep hit, a wiki page being read, a quoted commit line.
    `INVOKE` is file-scoped and role-blind, so a session that merely READ a page about
    ASOP 56 scores the same as Jon typing `/gbs`.
  * **APPLICABLE-NOT-USED measures the detector.** 578 of 1,106 precursor occurrences in
    that class carry at least one mechanical false-positive signature, and hand-reading 51
    windows across 25 sampled files found 51 of 51 to be false positives — including the
    sharpest shape, a file whose whole purpose is Rule-8 provenance discipline being scored
    as a Rule-8 violation because its provenance block sits outside the +/-200-char window.

WHAT IT DELIBERATELY DOES NOT DO
-----------------------------------
It **changes no class and edits no skill.** It is a forensic read of an existing instrument.
The five false-positive signatures are a **LOWER BOUND on detector error**, never an upper
bound on it, and never a claim that the remainder are true misses: an occurrence with no FP
signature is UNADJUDICATED, not confirmed.

**A file with no FP signature is not a GBS failure.** Saying so would repeat the exact error
this file exists to document.

Exit code is **always 0.** An instrument, not a gate. It only ever READS `raw/`.

Usage:
  gbs_class_forensics.py --cls PARTIAL     # what put each file in PARTIAL
  gbs_class_forensics.py --cls ANU         # FP signatures over every ANU occurrence
  gbs_class_forensics.py --both
  gbs_class_forensics.py --self-test
"""
import argparse
import re
import sys
from collections import Counter
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

import corpus_index as CI                      # noqa: E402
import gbs_record as GR                        # noqa: E402  classes + rules, IMPORTED not forked

REPO = GR.REPO

# =================================================================================================
# PARTIAL — which alternative of `gbs_record.INVOKE` fired, and in whose turn
# =================================================================================================
# `INVOKE` is one alternation; splitting it here is the only way to attribute a hit. Each row is
# a VERBATIM sub-pattern of gbs_record.INVOKE (SKILL.md:127-131), not a paraphrase of it.
ALTS = [
    ("ASOP-number",                  re.compile(r"\bASOP\s+\d+\b", re.I)),
    ("/gbs",                         re.compile(r"(?:^|\s)/gbs\b", re.I)),
    ("/ground-before-stating",       re.compile(r"(?:^|\s)/ground-before-stating\b", re.I)),
    ("gbs check",                    re.compile(r"gbs check", re.I)),
    ("show your epistemic work",     re.compile(r"show your epistemic work", re.I)),
    ("ground before stating (prose)", re.compile(r"ground before stating", re.I)),
]
# The skill being NAMED (a path, a heading, an inventory row, a commit line) rather than invoked.
NAMED = re.compile(
    r"ground-before-stating|skills[\\/]|`gbs`|\(gbs\)|GBS \(Ground|"
    r"the (?:gbs|ground before stating) skill|Skills (?:Loaded|Active)|skill (?:file|name|slug)",
    re.I)

# =================================================================================================
# ANU — five mechanical false-positive signatures, each traced to a window read by hand
# =================================================================================================
# A: a HEDGE counted as a booster. `R2_BOOST` lists `certainly`, which is inside `almost certainly`
#    — the modal hedge Rules 1 and 2 exist to REWARD. Every "almost certainly" in the corpus is
#    scored as an unhedged assertion.
FP_HEDGE = re.compile(r"\b(?:almost|not|nearly|near|less than|far from|hardly)\s+certainly\b", re.I)
# B: `confirmed` as an ACKNOWLEDGMENT token — "Q1 — Confirmed.", "Is this confirmed?" — which is a
#    speech act about a DECISION, not an unverified claim about the world.
FP_ACK = re.compile(r"^\s*(?:Q\d+\s*[^\w\s]\s*)?confirmed[.,:]?\s*$|"
                    r"\b(?:is|are|was|were)\s+(?:this|that|it)\s+confirmed\b|"
                    r"\bconfirmed\?|\bplease confirm|\bcan you confirm|^\s*[-*]\s*confirmed\b",
                    re.I | re.M)
# C: the claim carries its OWN grounding in the window — a serial number off a photo, a file:line,
#    a commit sha, a stated confidence. Rule 6 asks for grounding; this IS grounding.
FP_SELFGROUND = re.compile(
    r"\b\d{1,3}\s*[-–]\s*\d{1,3}\s*%|\bconfidence\b|\bS/N[: ]|\bserial\b|"
    r"\.(?:md|py|sh|json|jsonl|txt)\b|\bline \d+|:\d+:|\b[0-9a-f]{7,40}\b|"
    r"\bper (?:the )?(?:spec|frontmatter|manifest|photo|image|sticker|label|receipt)\b|"
    r"\bimage \d|\bphoto\b|\bscreenshot\b", re.I)
# D: Rule 7 firing on a `yes` that OPENS a new instruction rather than ratifying a prior decision.
#    "Yes, make that into a packet for me" is not a decision to read back.
FP_NEWINSTR = re.compile(r"^\s*(?:yes|yeah|yep|ok|okay)[,.]?\s+(?:make|draft|create|write|add|do|"
                         r"please|and\b|now\b|also\b|go\b|build|run|set|put)", re.I)
# E: the precursor sits inside a TOOL-CALL PAYLOAD or fenced code — an `Edit` new_string, a Bash
#    heredoc, a JSON blob. That is not the assistant asserting anything.
FP_PAYLOAD = re.compile(r'"(?:old_string|new_string|content|command|file_path)"\s*:|'
                        r"\[tool_result|```|tool_use|^\s{4,}[\"'{]", re.I | re.M)
# F: Rule 8 was born 2026-08-06 (gbs_record.RULES[8]['born']). An occurrence before that date is
#    the EVIDENCE THAT MOTIVATED the rule, not a failure to follow it. Read from gbs_record so the
#    date lives in one place and cannot diverge.
R8_BORN = GR.RULES[8]["born"]

SIGNATURES = ["A-hedge-as-booster", "B-ack-token", "C-self-grounded",
              "D-new-instruction", "E-tool-payload", "F-predates-rule"]


def classes(recs):
    det = [n for n in GR.RULES if GR.RULES[n]["state"]]
    used = [r for r in recs if r["invoked"] and r["labeled"]]
    partial = [r for r in recs if r["invoked"] and not r["labeled"]]
    anu = [r for r in recs if not r["invoked"] and not r["labeled"]
           and any((r[f"r{n}"] or 0) > 0 for n in det)]
    return used, partial, anu, det


def fp_tags(rule_n, txt, m, window, date):
    """[signature, ...] for one occurrence. EMPTY means UNADJUDICATED, never 'true miss'."""
    out = []
    hit = txt[m.start():m.end()]
    pre = txt[max(0, m.start() - 40): m.start()]
    if rule_n in (2, 6):
        if FP_HEDGE.search(pre + hit):
            out.append("A-hedge-as-booster")
        if FP_ACK.search(window):
            out.append("B-ack-token")
        if FP_SELFGROUND.search(window):
            out.append("C-self-grounded")
    if rule_n == 7 and FP_NEWINSTR.search(txt.strip()[:200]):
        out.append("D-new-instruction")
    if FP_PAYLOAD.search(window):
        out.append("E-tool-payload")
    if rule_n == 8 and date != "UNKNOWN" and date < R8_BORN:
        out.append("F-predates-rule")
    return out


def report_partial(recs, partial):
    N = len(partial)
    alt_files, alt_hits = Counter(), Counter()
    role_files, role_hits = Counter(), Counter()
    only_asop = only_r = jon_real_files = 0
    for r in partial:
        seq = GR.spans(REPO / r["path"]).get("__seq__", [])
        seen_alt, seen_role, jon_real = set(), set(), 0
        for role, txt in seq:
            for m in GR.INVOKE.finditer(txt):
                frag = txt[max(0, m.start() - 120): m.end() + 120]
                lab = next((nm for nm, rx in ALTS if rx.search(txt[m.start():m.end()])), "other")
                seen_alt.add(lab)
                alt_hits[lab] += 1
                seen_role.add(role)
                role_hits[role] += 1
                if role == "H" and lab != "ASOP-number" and not NAMED.search(frag):
                    jon_real += 1
        for a in seen_alt:
            alt_files[a] += 1
        for ro in seen_role:
            role_files[ro] += 1
        if seen_alt == {"ASOP-number"}:
            only_asop += 1
        if seen_role and seen_role <= {"R"}:
            only_r += 1
        if jon_real:
            jon_real_files += 1

    print()
    print("=" * 88)
    print("WHY THESE FILES ARE `PARTIAL` — gbs_record's 'kinda did' class, opened up")
    print("=" * 88)
    print(f"  DENOMINATOR: PARTIAL = {N} files of {len(recs)} scanned")
    print()
    print("--- WHICH ALTERNATIVE OF `INVOKE` FIRED --------------------------------------")
    for k, _ in ALTS:
        print(f"  {k:<32} files {alt_files[k]:>4} of {N}    hits {alt_hits[k]:>5}")
    print(f"  ** files whose ONLY invocation evidence is an ASOP number : {only_asop} of {N} "
          f"({100.0 * only_asop / N:.1f}%) **")
    print("     `ASOP <n>` is a LEXICAL trigger (SKILL.md:129-131) meant to fire a modal check")
    print("     when Jon cites a standard. It fires equally on a wiki page ABOUT ASOP 56 being")
    print("     read, on a concept-gap tracker row, and on an agent brief. It is scoped to no")
    print("     one's turn.")
    print()
    print("--- IN WHOSE TURN  (H=Jon  A=assistant  D=dispatch  R=tool-result  C=compact) --")
    for ro in sorted(role_files):
        print(f"  role {ro} : files {role_files[ro]:>4} of {N}    hits {role_hits[ro]:>5}")
    print(f"  ** files where EVERY invocation sits in a TOOL RESULT : {only_r} of {N} "
          f"({100.0 * only_r / N:.1f}%) **")
    print("  files with >=1 invocation in JON'S turn that is neither an ASOP number nor a")
    print(f"    bare naming of the skill                            : {jon_real_files} of {N} "
          f"({100.0 * jon_real_files / N:.1f}%)")
    print()
    print("--- WHAT THIS DOES NOT ESTABLISH ---------------------------------------------")
    print("  The Jon-turn survivors are CANDIDATES, not confirmed 'kinda did' runs. Hand-")
    print("  reading all of them on 2026-08-07 found 2 genuine invocations that produced no")
    print("  label, 1 whose label the LABELS regex missed because it carried a qualifier")
    print("  (`[training, UNGROUNDED for current claude.ai]` does not match `[training]`),")
    print("  and 2 where Jon was DISCUSSING the skill rather than invoking it.")
    print()


def report_anu(recs, anu, det):
    N = len(anu)
    occ = 0
    tags = Counter()
    per_rule, per_rule_fp = Counter(), Counter()
    clean_files = set()
    for r in anu:
        seq = GR.spans(REPO / r["path"]).get("__seq__", [])
        file_clean = False
        for n in det:
            if (r[f"r{n}"] or 0) == 0:
                continue
            spec = GR.RULES[n]
            vf = GR._verified_in_turn(seq) if spec.get("turn_verify") else None
            for i, (role, txt) in enumerate(seq):
                if role != spec["role"]:
                    continue
                if vf is not None and vf[i]:
                    continue
                kept_end = None
                for m in spec["pat"].finditer(txt):
                    w = txt[max(0, m.start() - 200): m.end() + 200]
                    if spec.get("exempt") and spec["exempt"].search(w):
                        continue
                    if spec.get("nearby") and spec["nearby"].search(w):
                        continue
                    if spec.get("follow"):
                        nxt = seq[i + 1][1] if i + 1 < len(seq) else ""
                        if spec["follow"].search(w) or spec["follow"].search(nxt[:2000]):
                            continue
                    if GR.LABELS.search(w):
                        continue
                    if kept_end is not None and m.start() - kept_end <= GR.MERGE_CHARS:
                        kept_end = m.end()
                        continue
                    kept_end = m.end()
                    occ += 1
                    per_rule[n] += 1
                    t = fp_tags(n, txt, m, w, r["date"])
                    if t:
                        per_rule_fp[n] += 1
                        for x in t:
                            tags[x] += 1
                    else:
                        file_clean = True
        if file_clean:
            clean_files.add(r["path"])

    print()
    print("=" * 88)
    print("WHY THESE FILES ARE `APPLICABLE-NOT-USED` — five false-positive signatures")
    print("=" * 88)
    print(f"  DENOMINATOR: ANU = {N} files of {len(recs)} scanned; "
          f"{occ} precursor occurrences inside them")
    print()
    print("--- PER RULE -----------------------------------------------------------------")
    for n in sorted(per_rule):
        tot, fp = per_rule[n], per_rule_fp[n]
        print(f"  Rule {n} ({GR.RULES[n]['name']:<24}) : {tot:>5} occurrences, {fp:>5} carry "
              f">=1 FP signature ({100.0 * fp / tot:.1f}%)")
    tot_fp = sum(per_rule_fp.values())
    if occ:
        print(f"  ALL DETECTABLE RULES                          : {occ:>5} occurrences, "
              f"{tot_fp:>5} carry >=1 FP signature ({100.0 * tot_fp / occ:.1f}%)")
    print()
    print("--- WHICH SIGNATURE (one occurrence may carry more than one) ------------------")
    for k in SIGNATURES:
        pct = (100.0 * tags[k] / occ) if occ else 0.0
        print(f"  {k:<22} {tags[k]:>6}   ({pct:.1f}% of {occ} occurrences)")
    print()
    print("--- FILE LEVEL ---------------------------------------------------------------")
    print(f"  ANU files where EVERY occurrence carries an FP signature : "
          f"{N - len(clean_files)} of {N}  ({100.0 * (N - len(clean_files)) / N:.1f}%)")
    print(f"  ANU files with >=1 UNADJUDICATED occurrence              : "
          f"{len(clean_files)} of {N}  ({100.0 * len(clean_files) / N:.1f}%)")
    print("  ** UNADJUDICATED IS NOT 'TRUE MISS'. ** These five signatures are a LOWER BOUND")
    print("  on detector error. The hand read of 25 sampled files (51 windows) on 2026-08-07")
    print("  found 51 of 51 to be false positives, INCLUDING shapes no signature here can see:")
    print("    * a file whose entire purpose is Rule-8 provenance discipline, scored as a")
    print("      Rule-8 violation because its status legend (RATIFIED / PROPOSED / JON-GATE)")
    print("      sits further from the citation than the +/-200-char `follow` window reaches;")
    print("    * an assistant ENFORCING Rule 8 on someone else — \"no first-person Jon ruling")
    print("      exists; don't let the wiki render it as 'Jon ruled that...'\" — scored as")
    print("      committing the violation it is naming.")
    print("  A window is not a document, and neither of those is fixed by a wider window.")
    print()


def self_test():
    ok = True

    def chk(label, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    print("=== SELF-TEST — gbs_class_forensics (negative controls first) ===")
    # Every signature must be able to say NO. A signature that always fires is the RATIO_FLOOR
    # defect: an alarm calibrated so it can never be silent.
    chk("A does NOT fire on a bare booster — that one is a REAL Rule-2 precursor",
        not FP_HEDGE.search("this is certainly the cause"))
    chk("A fires on the hedge the rule exists to reward",
        bool(FP_HEDGE.search("this is almost certainly the cause")))
    chk("B fires on an acknowledgment token",
        bool(FP_ACK.search("Q1 - Confirmed.")))
    chk("B does NOT fire on an assertion about the world",
        not FP_ACK.search("Confirmed: settings.json is unwritable."))
    chk("C fires when the claim carries a file:line",
        bool(FP_SELFGROUND.search("confirmed at wiki/index.md:42")))
    chk("C does NOT fire on a bare claim",
        not FP_SELFGROUND.search("confirmed, it is gone"))
    chk("D fires on a 'yes' that opens a new instruction",
        bool(FP_NEWINSTR.search("Yes, make that into a packet for me")))
    chk("D does NOT fire on a bare ratifying 'yes'",
        not FP_NEWINSTR.search("yes"))
    chk("E fires inside an Edit payload",
        bool(FP_PAYLOAD.search('"new_string": "RTX 2060 confirmed"')))
    chk("E does NOT fire on ordinary prose",
        not FP_PAYLOAD.search("The GPU is confirmed as an RTX 2060."))
    chk("F's born date is READ from gbs_record, never written twice",
        R8_BORN == GR.RULES[8]["born"])
    chk("an occurrence with no signature returns an EMPTY list — the report must render that "
        "UNADJUDICATED and never 'true miss'",
        fp_tags(6, "Confirmed it is gone.", re.search(r"Confirmed", "Confirmed it is gone."),
                "Confirmed it is gone.", "2026-01-01") == [])
    chk("F fires on a pre-2026-08-06 Rule-8 occurrence (evidence, not failure)",
        "F-predates-rule" in fp_tags(8, "per Jon", re.search(r"per Jon", "per Jon"),
                                     "per Jon", "2026-07-13"))
    chk("F does NOT fire on a post-birth occurrence",
        "F-predates-rule" not in fp_tags(8, "per Jon", re.search(r"per Jon", "per Jon"),
                                         "per Jon", "2026-08-07"))
    # REUSE, not redefinition.
    chk("CORPUS resolves transitively to coverage_gap's",
        CI.CORPUS == __import__("coverage_gap").CORPUS)
    chk("span splitter is gbs_record's, not a second copy",
        GR.spans is __import__("gbs_record").spans)
    chk("the rule registry is gbs_record's, not a second copy",
        GR.RULES is __import__("gbs_record").RULES)
    print("\nRESULT: " + ("PASS — every signature can say no." if ok
                          else "FAIL — do not trust its counts."))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cls", choices=["PARTIAL", "ANU"], default=None)
    ap.add_argument("--both", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    read = CI.require_index("gbs_class_forensics")
    if not read.fresh:
        print(f"Forensics = UNKNOWN, not zero  [{read.status}] — {read.one_line()}",
              file=sys.stderr)
        print("This is NOT a result. Nothing was scanned.", file=sys.stderr)
        return 0
    recs = GR.scan(read.rows)
    used, partial, anu, det = classes(recs)
    print(f"CLASS TOTALS over {len(recs)} transcripts re-read of {len(read.rows)} in index: "
          f"USED {len(used)} / PARTIAL {len(partial)} / ANU {len(anu)} "
          f"(sum {len(used) + len(partial) + len(anu)})")
    do_p = args.both or args.cls in (None, "PARTIAL")
    do_a = args.both or args.cls in (None, "ANU")
    if do_p:
        report_partial(recs, partial)
    if do_a:
        report_anu(recs, anu, det)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(0)
