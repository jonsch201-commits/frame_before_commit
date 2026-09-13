#!/usr/bin/env python3
"""find_resurrection_candidates.py — an echo with no ruling behind it.

Built 2026-08-06 in answer to Jon's second question that day: *"when should we resurrect
a json to help the wiki?"*

WHY THIS EXISTS, AND WHAT IT IS THE MIRROR OF
-----------------------------------------------
`find_unechoed_rulings.py` (ARM B) scans `wiki/log.md` for ruling-shaped quoted lines and
asks: is this echoed anywhere else in the tracked corpus? A ruling with zero echo is a
finding — nothing refers back to it.

This script asks the opposite question over the opposite direction of the same edge: a
claim attributed to Jon (a quote, a "Jon ruled" line, a cited position) that appears
somewhere in the tracked corpus — is its citation a PRIMARY source (something under
`raw/transcripts/` or `raw/originals/`), or does it cite only ANOTHER WIKI/EXCHANGE/SKILLS
PAGE? The second case is `derive-don't-record`: a fact written down once, then cited by
everything downstream, with nothing that ever goes back to the transcript that is the only
thing that can settle what was actually said — and, per Jon's 2026-08-06 ruling on
gradient (`skills/ground-before-stating/SKILL.md` Rule 8;
`wiki/intake-triage/jon-ruling-gradient-not-position-2026-08-06.md`), the only thing that
can recover WHAT HE WAS RESPONDING TO, not just what he concluded. The gradient lives in
the transcript and nowhere else, so a claim with only a secondary citation is exactly the
class of thing worth resurrecting a JSONL to settle.

NOT A FRESH SCANNER — REUSES THE ALREADY-BUILT DETECTOR
----------------------------------------------------------
`check_secondary_attribution.py` (PROTOTYPE, advisory, not wired into `su_gate.sh`) already
answers "is this Jon-attributed line cited to a primary?" — built 2026-08-02, self-tested,
and it is the correct predicate for this question. Writing a second implementation of "is
this line Jon-attributed" and "is this citation primary" would be exactly the kind of
divergent second copy the skills-master conventions warn against. So this script imports
`is_primary`, `frontmatter`, and `scan_page` from that module directly rather than
reimplementing them — see the `sys.path` shim below.

What this script changes is the CORPUS, not the detector. `check_secondary_attribution.py`
defaults to `--root wiki` only. The brief for this ticket says explicitly: "do not write a
second scanner with a different corpus definition" — read as binding this script to
`find_unechoed_rulings.py`'s `ECHO_CORPUS_GLOBS` (wiki/**, exchange/**, skills/**,
CLAUDE.md, README.md — the same published-surface set `regenerate_canonical.sh:36` defines),
so the "echo corpus" and the "resurrection-candidate corpus" are the SAME set of files,
scanned by both scripts. A claim can now be a finding in `find_unechoed_rulings.py` (nothing
echoes it) or in this script (it IS echoed, but never to a primary) without the two scripts
silently disagreeing about what counts as "the tracked corpus."

WHAT THIS SCRIPT CANNOT DO, STATED BEFORE THE OUTPUT
--------------------------------------------------------
It cannot tell you whether a primary actually EXISTS for a flagged claim, or whether
resurrecting it would change anything. That requires opening `raw/transcripts/` — which,
per the standing fence, a worktree does not have; the verification tool that opens it
(`verify_quotes.py`) must be pointed at the MAIN checkout's raw/ explicitly via ITS OWN
`--raw-root` flag. THIS script defines no `--raw-root` flag — only `--root`, `--limit`,
`--self-test` (see `main()` below). It does not touch raw/ at all; it only tells you
WHICH claims are worth spending that lookup on, and prints the exact next command
(`git log -S "<fingerprint>" --all` from the main checkout, same manual step
`find_unechoed_rulings.py` already recommends for its own zero-echo class) so the
disambiguation stays a human/agent judgment call, not an automated verdict.

THE RESURRECTION TRIGGER, STATED AS A RULE
----------------------------------------------
Resurrect a JSONL when a wiki claim's only citation is another wiki/exchange/skills page
(never a primary) AND at least one of:
  (a) the claim carries a ruling/decision Jon is on record making (not just background
      description) — because a decision's gradient (what provoked it) is exactly what a
      secondary citation drops first;
  (b) the claim is load-bearing for something ELSE downstream (cited again from a third
      page) — the "derive-don't-record" chain gets longer, not shorter, the longer it goes
      unresurrected;
  (c) the secondary citation is itself an agent packet or work order, not a wiki concept
      page — the failure class named explicitly in `check_secondary_attribution.py`'s own
      docstring ("an agent packet invented a Jon ruling, wiki/index.md cited the packet, and
      the citation resolved. Nothing in the loop had primary evidence").
A claim with a secondary citation but NONE of (a)-(c) is lower priority — logged as a
candidate, not escalated.

USAGE
    python scripts/audit/find_resurrection_candidates.py
    python scripts/audit/find_resurrection_candidates.py --limit 60
    python scripts/audit/find_resurrection_candidates.py --self-test

Exit 0 always (this is a candidate finder, not a gate — same posture as ARM B of
find_unechoed_rulings.py; see that script's docstring for why a finder should not fail a
CI gate on judgment calls it cannot itself make).
"""
import argparse
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_secondary_attribution import scan_page, is_primary  # noqa: E402  (reused detector)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# SAME SET find_unechoed_rulings.py calls ECHO_CORPUS_GLOBS — kept identical on purpose (see
# docstring). If that script's set ever changes, this one must change with it.
CORPUS_GLOBS = [
    "wiki/**/*.md",
    "exchange/**/*.md",
    "skills/**/*.md",
    "CLAUDE.md",
    "README.md",
]

# A secondary citation into one of these paths is a packet/work-order, not a wiki concept
# page — trigger class (c) in the docstring's rule.
PACKET_LIKE_PREFIXES = ("exchange/", "wiki/intake-triage/")


def corpus_files(root, globs):
    out = []
    for pat in globs:
        out.extend(glob.glob(os.path.join(root, pat), recursive=True))
    # de-dupe, stable order
    seen = set()
    result = []
    for p in out:
        norm = os.path.normpath(p)
        if norm not in seen and os.path.isfile(p):
            seen.add(norm)
            result.append(p)
    return sorted(result)


def classify(cite, line_text):
    """Return the trigger tags this finding matches — (a)/(b)/(c) from the docstring rule.

    (b) requires corpus-wide context this per-file pass does not have (whether the claim is
    cited again elsewhere) — left as a manual judgment call and NOT auto-tagged, to avoid a
    heuristic quietly overclaiming precision it doesn't have (the exact overclaim
    `find_unechoed_rulings.py` was renamed to stop making). (a) and (c) ARE mechanically
    checkable: (a) from the FULL line text (the "ruled"/"ratified" wording sits before the
    quote mark, not inside the fingerprint scan_page() extracts — pass the whole line, not
    the fingerprint); (c) from whether the cited artifact is a packet/work-order path rather
    than a settled wiki concept page.
    """
    tags = []
    if cite != "(none)" and any(cite.startswith(p) for p in PACKET_LIKE_PREFIXES):
        tags.append("(c) secondary citation is a packet/work-order, not a concept page")
    if any(w in line_text.lower() for w in ("ruled", "ruling", "ratified", "decided")):
        tags.append("(a) claim reads as a decision, not background")
    return tags


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=REPO_ROOT)
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    files = corpus_files(args.root, CORPUS_GLOBS)
    if not files:
        print(f"[exit 2 would apply] scanned 0 files under {args.root}", file=sys.stderr)
        return 2

    findings = []
    for p in files:
        from pathlib import Path
        try:
            file_lines = open(p, encoding="utf-8", errors="ignore").read().split("\n")
        except OSError:
            file_lines = []
        for lineno, fp, cite, reason in scan_page(Path(p)):
            full_line = file_lines[lineno - 1] if 0 < lineno <= len(file_lines) else fp
            findings.append((p, lineno, fp, cite, reason, full_line))

    print("=== RESURRECTION-CANDIDATE SCAN (mirror of find_unechoed_rulings.py ARM B) ===")
    print(f"  corpus definition       : ECHO_CORPUS_GLOBS (wiki/**, exchange/**, skills/**, "
          f"CLAUDE.md, README.md) — identical set to find_unechoed_rulings.py")
    print(f"  files scanned                       : {len(files)} files")
    print(f"  Jon-attributed claim lines checked : {'see check_secondary_attribution scan '
          'internals (per-line, not separately counted here)'}")
    print(f"  RESURRECTION CANDIDATES (secondary-attribution only) : {len(findings)} findings"
          f"  [findings, NOT a fraction of the {len(files)} files above — different unit,"
          f" do not divide the two lines]")
    print()

    tagged, untagged = 0, 0
    for p, lineno, fp, cite, reason, full_line in findings[:args.limit]:
        rel = os.path.relpath(p, args.root).replace("\\", "/")
        tags = classify(cite, full_line)
        if tags:
            tagged += 1
        else:
            untagged += 1
        print(f"  {rel}:{lineno}")
        print(f"      fp={fp!r}")
        print(f"      secondary cite={cite}  -- {reason}")
        if tags:
            print(f"      trigger tags: {'; '.join(tags)}")
        print(f"      next step (from the MAIN checkout, not this worktree):")
        print(f"        git log -S \"{fp}\" --all")
        print(f"        (a hit = the text was in some commit already — check whether it")
        print(f"         traces to a raw/transcripts primary before resurrecting anything;")
        print(f"         no hit = worth pulling the JSONL if raw/transcripts has a candidate)")
    if len(findings) > args.limit:
        print(f"  ... {len(findings) - args.limit} more (raise --limit)")

    print()
    print(f"  of the {min(len(findings), args.limit)} printed above: {tagged} carry at least one")
    print(f"  mechanical trigger tag, {untagged} do not (logged as lower-priority candidates,")
    print(f"  per the docstring's rule — a secondary citation alone is not sufficient to")
    print(f"  escalate a resurrection).")

    print()
    print("MOST LIKELY FALSE-POSITIVE CLASS (read before acting on any finding above):")
    print("  A claim whose page-level `source_file:` IS primary but the specific in-line")
    print("  citation on that line points at a second, corroborating wiki page (e.g. a")
    print("  cross-reference added for the reader's convenience, not as the claim's actual")
    print("  source). check_secondary_attribution.py's own logic treats a primary")
    print("  page-level source_file as clearing the whole page, so this specific shape is")
    print("  already suppressed upstream — but a page with NO source_file at all and a")
    print("  same-topic cross-link to a sibling concept page will still flag here even when")
    print("  a primary citation exists two paragraphs earlier on the same page, outside the")
    print("  3-line window scan_page() checks. Not corrected here — see")
    print("  check_secondary_attribution.py's own FALSE-POSITIVE note; this script inherits")
    print("  that scanner's precision characteristics unchanged.")

    return 0


def self_test():
    """Negative control — mirrors check_secondary_attribution.py's own self-test shape,
    extended to prove the CORPUS (not just the detector) is doing what this script claims."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix="resurrection-selftest-")
    fails = []
    try:
        os.makedirs(os.path.join(tmp, "wiki", "concepts"))
        os.makedirs(os.path.join(tmp, "exchange"))
        os.makedirs(os.path.join(tmp, "skills"))
        # secondary-only: should be flagged, and tagged (c) because it cites exchange/
        with open(os.path.join(tmp, "wiki", "concepts", "bad.md"), "w", encoding="utf-8") as f:
            f.write('---\ntitle: t\n---\n\nJon ruled, verbatim: "widgets ship blue." '
                    '`[verbatim, per `exchange/some-packet-2026-08-02.md`]`\n')
        # primary-cited: should NOT be flagged
        with open(os.path.join(tmp, "wiki", "concepts", "good.md"), "w", encoding="utf-8") as f:
            f.write('---\ntitle: t\nsource_file: raw/transcripts/claude-code/fl/x.md\n---\n\n'
                    'Jon, verbatim: "widgets ship blue." `[TRANSCRIPT:2026-08-02]`\n')
        # a skills/ file — proves the corpus includes skills/, not just wiki/, unlike
        # check_secondary_attribution.py's own default --root wiki
        with open(os.path.join(tmp, "skills", "s.md"), "w", encoding="utf-8") as f:
            f.write('---\ntitle: t\n---\n\nJon ruled, verbatim: "gadgets ship red." '
                    '`[verbatim, per `wiki/concepts/other.md`]`\n')

        files = corpus_files(tmp, CORPUS_GLOBS)
        rels = {os.path.relpath(p, tmp).replace("\\", "/") for p in files}
        if "skills/s.md" not in rels:
            fails.append("FAIL corpus does not include skills/ — corpus definition mismatch "
                         "with find_unechoed_rulings.py's ECHO_CORPUS_GLOBS")
        if "wiki/concepts/bad.md" not in rels or "wiki/concepts/good.md" not in rels:
            fails.append("FAIL corpus does not include wiki/**")

        from pathlib import Path
        bad_findings = scan_page(Path(os.path.join(tmp, "wiki", "concepts", "bad.md")))
        good_findings = scan_page(Path(os.path.join(tmp, "wiki", "concepts", "good.md")))
        skill_findings = scan_page(Path(os.path.join(tmp, "skills", "s.md")))

        if len(bad_findings) != 1:
            fails.append(f"FAIL known-bad should flag exactly 1, got {len(bad_findings)}")
        if len(good_findings) != 0:
            fails.append(f"FAIL known-good (primary source_file) should flag 0, got "
                         f"{len(good_findings)}")
        if len(skill_findings) != 1:
            fails.append(f"FAIL skills/ file with secondary cite should flag 1, got "
                         f"{len(skill_findings)}")
        else:
            skill_line = open(os.path.join(tmp, "skills", "s.md"),
                               encoding="utf-8").read().split("\n")[skill_findings[0][0] - 1]
            if not classify(skill_findings[0][2], skill_line):
                fails.append("FAIL skills/ finding should carry at least one trigger tag "
                             "('ruled' -> tag (a))")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    print("=== SELF-TEST (negative control + corpus-definition check) ===")
    for f in fails:
        print(f"  {f}")
    ok = not fails
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} — {len(fails)} failure(s)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
