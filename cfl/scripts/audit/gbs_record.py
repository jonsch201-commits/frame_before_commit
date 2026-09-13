#!/usr/bin/env python3
"""gbs_record.py — the accumulated session record for `ground-before-stating`, three classes.

WHY THIS EXISTS — Jon, verbatim, 2026-08-06
---------------------------------------------
    "For each skill, in the wiki, accumulated session record. Not just explicit uses, but
     implicit ones. Opportunitys where you might have considered using it but did not, and
     cases where you did and cases where you kinda did. If that's too much, triage the order
     but the wiki shpuld help you improve the skill. Key for gbs to the same degree."

**The acceptance test is "the wiki should help improve the skill", not completeness.**

WHAT THIS IS NOT — it is not a sixth scanner over the corpus
--------------------------------------------------------------
`scripts/audit/corpus_index.py` already indexes 1,167 transcripts and already implements a
three-class query. Its own docstring names its intended consumer and says the consumer should
"import rather than re-derive". So this file **imports** it:

  * `corpus_index.walk_corpus` / `.load_prior` / `.load_skills` / `.three_class` — the corpus
    walk, the on-disk index, the generated trigger table, and the reference query. `CORPUS`
    therefore still resolves, transitively, to `coverage_gap.CORPUS`. One corpus root.
  * `turn_index.index` — the ratified, fence-aware turn enumerator. Roles are H/A/C/R/D;
    **`D` is an orchestrating agent's dispatch, never Jon**, which is why Rule 7 below fires on
    `H` only. Getting that wrong would attribute an agent's brief to Jon.
  * `jon_utterances.normalize` — the one normalisation.

THE THING corpus_index CANNOT SEE, AND WHY THIS FILE HAD TO EXIST ANYWAY
--------------------------------------------------------------------------
`corpus_index --query-skill ground-before-stating` returns **APPLICABLE_NOT_USED = 5** out of
1,167. That number is not a finding about the record; it is a finding about the detector. Its
trigger table is GENERATED from SKILL.md frontmatter, and **every phrase in that frontmatter is
a meta-request** — `/gbs`, "ground before stating", "show your work", "ASOP <n>". So the class it
computes is "Jon asked for grounding and no label appeared", which is a rare event by
construction.

**A GBS rule's applicability is not signalled by Jon asking for it.** It is signalled by the
object-level precursor — the situation the rule exists to catch. Claude Personal's audit
(`exchange/personal-to-cfl-gbs-trigger-gap-audit-2026-08-06.md`) established exactly this:
*"None of the seven rules has a trigger tied to its own object-level precursor."*

Two further consequences, both load-bearing:

 1. **Rule 6's precursor lives in the ASSISTANT's turns, not Jon's.** `corpus_index` restricts
    APPLICABLE-NOT-USED to `triggers_human` — deliberately and correctly for a skill Jon
    invokes. But "an unverified absolutist claim was asserted" is something *Claude* does. A
    detector that only reads Jon's turns is structurally blind to the highest-frequency
    grounding failure. That single scoping difference is most of the gap between 5 and the
    number below.
 2. **The precursor patterns are not invented here.** They are lifted from the two hooks built
    on 2026-08-06 against this exact gap — `.claude/hooks/gbs-rule6-trigger.sh` and
    `gbs-rule7-trigger.sh` (commit `b42393e`, draft PR #245) — each of which ships its own
    self-test with negative controls. Re-deriving a second pattern list would be the divergence
    defect. **Those hooks are UNMERGED as of this writing**, which is itself the central finding:
    for the whole period this record covers, **no object-level trigger was ever live.**

CLASS DEFINITIONS — and where they deliberately differ from corpus_index
--------------------------------------------------------------------------
| class | here |
|---|---|
| USED | a GBS invocation marker present AND at least one System-1 label emitted |
| PARTIAL ("kinda did") | invoked, but its own labels absent — no `[unverified]`, `[training]`, `[VTT assumed]`, no reliance disclosure |
| APPLICABLE-NOT-USED | a **rule's object-level precursor** present, and no invocation and no label |

`corpus_index.MARKERS["ground-before-stating"]` uses the *labels themselves* as the marker and
declares no completion literal, so its PARTIAL is UNDETECTABLE. That is not wrong — it is a
different question ("did labelled output appear"). **Both answers are printed side by side
below** so the divergence is visible rather than silent, which is the one thing this repo has
repeatedly paid for getting wrong.

WHAT IT CANNOT SEE — printed, never silently zeroed
-----------------------------------------------------
Rules 1, 3, 5 have **no declared object-level precursor** anywhere — not in SKILL.md, not in a
hook. Their non-use is therefore **UNKNOWN, not zero**, and is reported that way. Rule 4's
precursor (VTT garble) is detectable in principle but only via a hand-curated misspelling list,
which is a divergence generator; declared UNDETECTABLE rather than guessed at.

Exit code is **always 0.** An instrument, not a gate. It only ever READS `raw/`.

Usage:
  gbs_record.py                 # full report with denominators
  gbs_record.py --limit N       # paths shown per class
  gbs_record.py --rule 6        # drill into one rule's candidates
  gbs_record.py --self-test     # negative controls
"""
import argparse
import json
import re
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

import corpus_index as CI                      # noqa: E402  corpus walk + index + reference query
from turn_index import index as turn_index     # noqa: E402  ratified enumerator (H/A/C/R/D)

REPO = CI.REPO

# =================================================================================================
# GBS's OWN OUTPUT SURFACE — taken from SKILL.md, not recalled
# =================================================================================================
# System-1 labels, skills/ground-before-stating/SKILL.md:86-99 (the `[ ]` Source/Basis table).
LABELS = re.compile(
    r"\[unverified\]|\[training\]|\[vtt assumed|\[retrieved\]|\[reliance|\[stale\?\]|"
    r"\[partial\]|\[sufficient for now\]",
    re.IGNORECASE,
)
# Invocations, SKILL.md:127 ("Invocations:") + the ASOP lexical trigger, SKILL.md:129-131.
INVOKE = re.compile(
    r"(?:^|\s)/gbs\b|(?:^|\s)/ground-before-stating\b|ground before stating|gbs check|"
    r"show your epistemic work|\bASOP\s+\d+\b",
    re.IGNORECASE,
)

# =================================================================================================
# PRECURSOR REGISTRY — per rule. `src` says where each pattern came from; nothing is invented.
# =================================================================================================
# A precursor is the OBJECT-LEVEL situation a rule exists to catch. `role` is whose turns it can
# occur in. `state=None` means no declared precursor exists -> the rule reports UNKNOWN.
#
# Rules 6 and 7 reuse the two hooks verbatim. Rule 2's booster set and Rule 8's citation shape are
# read out of SKILL.md's own text at the cited lines. Rules 1/3/4/5 are UNDECLARED and say so.

# .claude/hooks/gbs-rule6-trigger.sh (commit b42393e) — RISK, verbatim.
R6_RISK = re.compile(
    r"\b(confirmed|is unwritable|cannot be written|can't be written|"
    r"already settled|as (?:already )?established|permanently (?:lost|gone|deleted|the case)|"
    r"never (?:works|possible|happened)|we already know|it is known that)\b",
    re.IGNORECASE,
)
# Same hook — EXEMPT, verbatim. An honestly-labeled claim, or an adjacent real verification.
R6_EXEMPT = re.compile(
    r"\[unverified\]|\[stale\??\]|\[training\]|\[retrieved\]|\[verified\]|\[reliance|"
    r"git (?:log|show|diff|status|pull|fetch)",
    re.IGNORECASE,
)
# The corpus is markdown, not JSONL, so the hook's "was a verify TOOL called this turn" test has
# no direct analogue. The corpus analogue is the tool-call trace the extractor leaves in the same
# assistant turn. Named explicitly because it is the one place this detector is WEAKER than the
# hook it borrows from.
R6_VERIFY_NEARBY = re.compile(
    r"\b(?:Read|Grep|Glob|Bash)\b\s*[\(:]|`git |tool_use|Tool call|\bReading\b|\bgrep\b",
    re.IGNORECASE,
)

# .claude/hooks/gbs-rule7-trigger.sh (commit b42393e) — DECISION, verbatim.
R7_DECISION = re.compile(
    r"^\s*(yes|yep|yeah|approved?|go ahead|do it|ratify(?:ied)?|confirmed?)\b"
    r"|\bdraft\[|\bratify\b",
    re.IGNORECASE,
)
# Rule 7's compliance shape, SKILL.md:61 ("read it back in your own words before recording it").
R7_READBACK = re.compile(
    r"read(?:ing)? (?:that |this |it )?back|to read that back|my own words|"
    r"what I take you to mean|as I understand (?:it|you)|you'?re saying that|"
    r"before I record",
    re.IGNORECASE,
)

# SKILL.md:51 (Rule 2) — the booster set the rule itself names: "'Confirmed X' when X is inferred".
R2_BOOST = re.compile(
    r"\b(confirmed that|confirmed[:,]|verified that|definitely|certainly|"
    r"there is no doubt|clearly the case|proves that)\b",
    re.IGNORECASE,
)
# SKILL.md:63-67 (Rule 8) — a Jon citation being made.
R8_CITE = re.compile(
    r"jon,? verbatim|jon ruled|jon'?s ruling|per jon|jon said|jon stated|jon approved",
    re.IGNORECASE,
)
# SKILL.md:63 — Rule 8's own three required carries: what he responded to / corrected / direction.
R8_GRADIENT = re.compile(
    r"\bgradient\b|direction of travel|what he was (?:responding to|correcting)|"
    r"in response to|was correcting|which instance",
    re.IGNORECASE,
)

RULES = {
    1: dict(name="Modal precision", role=None, state=None,
            why="`must`/`should`/`may` occur in almost every turn. A precursor with no "
                "specificity produces a candidate list the size of the corpus, which is the "
                "same as no detector. No narrower precursor is declared in SKILL.md or any hook."),
    2: dict(name="Inference != fact", role="A", state="declared",
            src="skills/ground-before-stating/SKILL.md:51 — the rule names its own booster set",
            pat=R2_BOOST, exempt=R6_EXEMPT, turn_verify=True),
    3: dict(name="Reliance disclosure", role=None, state=None,
            why="The precursor is 'a load-bearing claim rests on Jon/a source/model weights'. "
                "That is a fact about a claim's provenance, which is not on the page. Nothing "
                "lexical distinguishes a disclosed reliance from an undisclosed one."),
    4: dict(name="Voice-to-text", role=None, state=None,
            why="Detectable in principle (Jon's VTT garbles are real and frequent) but only via "
                "a hand-curated misspelling list. A hand list is a divergence generator and this "
                "record refuses to seed one. UNDECLARED, not zero."),
    5: dict(name="Training attribution", role=None, state=None,
            why="The precursor is 'this claim came from model weights rather than a read source'. "
                "That is invisible in the output text by construction — it is precisely the fact "
                "the label exists to add."),
    6: dict(name="Read before asserting", role="A", state="declared",
            src=".claude/hooks/gbs-rule6-trigger.sh (b42393e) — RISK/EXEMPT reused verbatim",
            pat=R6_RISK, exempt=R6_EXEMPT, nearby=R6_VERIFY_NEARBY, turn_verify=True),
    7: dict(name="Read-back on decisions", role="H", state="declared",
            src=".claude/hooks/gbs-rule7-trigger.sh (b42393e) — DECISION reused verbatim",
            pat=R7_DECISION, follow=R7_READBACK),
    8: dict(name="Gradient, not position", role="A", state="declared",
            src="skills/ground-before-stating/SKILL.md:63-67 — the rule's own three carries",
            pat=R8_CITE, follow=R8_GRADIENT, born="2026-08-06"),
}


def spans(path):
    """{role: [text, ...]} for one transcript, via the ratified enumerator.

    `D` (dispatch) is kept SEPARATE from `H`. In a subagent transcript every user-role record is
    an orchestrating agent's brief; folding it into `H` would attribute an agent's instruction to
    Jon, which is the single most expensive misattribution class this program has recorded.
    """
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    lines = text.splitlines()
    try:
        ti = turn_index(str(path))
        turns = ti["turns"]
    except Exception:
        return {}
    out = {}
    for i, t in enumerate(turns):
        start = t["line"]
        end = turns[i + 1]["line"] - 1 if i + 1 < len(turns) else len(lines)
        out.setdefault(t["role"], []).append("\n".join(lines[start:end]))
    # ordered (role, text) too — Rule 7/8 need "what came AFTER this turn"
    seq = []
    for i, t in enumerate(turns):
        start = t["line"]
        end = turns[i + 1]["line"] - 1 if i + 1 < len(turns) else len(lines)
        seq.append((t["role"], "\n".join(lines[start:end])))
    out["__seq__"] = seq
    return out


# Two patterns in one sentence are ONE occurrence, not two. "Confirmed: settings.json is
# unwritable" matches R6_RISK twice ("confirmed", "is unwritable") and counting it as two
# failures would inflate every headline number by an unknown factor that varies with how
# many synonyms the pattern list happens to carry. Merged at 120 chars — below a sentence's
# typical length, so two genuinely separate claims in one paragraph still count separately.
MERGE_CHARS = 120


def _verified_in_turn(seq):
    """[bool] per position: has a Tool Result landed since the last human/dispatch turn?

    THIS REPLACES A PROXY THAT DID NOT WORK, AND THE MEASUREMENT IS THE REASON.
    The Rule 6 hook's real test is "did a verify tool fire THIS TURN", which it reads from the
    JSONL's `tool_use` records. The first port of this file approximated that with a text pattern
    in a +/-200 char window, and hand-checking 28 sampled candidate windows found essentially
    ALL of them false positives of one specific shape: *reports of a check that had just run* --
    "Directory listing confirmed exactly three files", "CONFIRMED: 25 compaction boundaries",
    "confirmed via a second, unmodified file". The window was too small to contain the evidence,
    because the evidence is not in the prose at all -- it is in a SEPARATE TURN.

    The markdown corpus does carry that signal: `turn_index` emits role `R` for `## Tool Result`.
    A `R` turn between the last `H`/`D` turn and the assistant text IS the corpus analogue of the
    hook's tool_use check, at turn granularity rather than call granularity. That is still weaker
    than the hook -- it proves SOME tool ran this turn, not the RIGHT one -- and the hook says the
    same of itself. But it is the real signal rather than a guess at where the signal might be.
    """
    out, seen = [], False
    for role, _ in seq:
        if role in ("H", "D"):
            seen = False
        out.append(seen)
        if role == "R":
            seen = True
    return out


def hits_rule(n, sp):
    """Unanswered precursor OCCURRENCES for rule `n` in this file. None when UNDECLARED."""
    spec = RULES[n]
    if spec["state"] is None:
        return None
    seq = sp.get("__seq__", [])
    if not seq:
        return 0
    verified = _verified_in_turn(seq) if spec.get("turn_verify") else None
    count = 0
    for i, (role, txt) in enumerate(seq):
        if role != spec["role"]:
            continue
        if verified is not None and verified[i]:
            continue
        kept_end = None
        for m in spec["pat"].finditer(txt):
            window = txt[max(0, m.start() - 200): m.end() + 200]
            if spec.get("exempt") and spec["exempt"].search(window):
                continue
            if spec.get("nearby") and spec["nearby"].search(window):
                continue
            if spec.get("follow"):
                # compliance may land in this turn's own window or in the next turn
                nxt = seq[i + 1][1] if i + 1 < len(seq) else ""
                if spec["follow"].search(window) or spec["follow"].search(nxt[:2000]):
                    continue
            if LABELS.search(window):
                continue
            if kept_end is not None and m.start() - kept_end <= MERGE_CHARS:
                kept_end = m.end()          # same occurrence, extend it
                continue
            kept_end = m.end()
            count += 1
    return count


def scan(rows, limit_files=None):
    res = []
    paths = sorted(rows)
    if limit_files:
        paths = paths[:limit_files]
    for rel in paths:
        row = rows[rel]
        p = REPO / rel
        if not p.is_file():
            continue
        sp = spans(p)
        if not sp:
            continue
        whole = "\n".join(t for _, t in sp.get("__seq__", []))
        rec = {
            "path": rel, "date": row.get("date", "UNKNOWN"), "kind": row.get("kind"),
            "venue": row.get("venue"), "trunk": row.get("trunk"),
            "invoked": bool(INVOKE.search(whole)),
            "labeled": bool(LABELS.search(whole)),
            "n_labels": len(LABELS.findall(whole)),
        }
        for n in RULES:
            rec[f"r{n}"] = hits_rule(n, sp)
        res.append(rec)
    return res


# =================================================================================================
# REPORT — denominators in the output, not the docstring
# =================================================================================================
def report(recs, rows, limit=12, only_rule=None):
    N = len(recs)
    detectable = [n for n in RULES if RULES[n]["state"]]
    undet = [n for n in RULES if not RULES[n]["state"]]

    used = [r for r in recs if r["invoked"] and r["labeled"]]
    partial = [r for r in recs if r["invoked"] and not r["labeled"]]
    anu = [r for r in recs
           if not r["invoked"] and not r["labeled"]
           and any((r[f"r{n}"] or 0) > 0 for n in detectable)]

    print()
    print("=" * 84)
    print("GBS ACCUMULATED SESSION RECORD — three classes over the transcript corpus")
    print("=" * 84)
    print("--- DENOMINATORS -------------------------------------------------------------")
    print(f"  transcripts in corpus_index      : {len(rows)}")
    print(f"  transcripts SCANNED here         : {N}")
    print(f"  GBS rules total                  : {len(RULES)}")
    print(f"  rules with a DECLARED precursor  : {len(detectable)}  -> {sorted(detectable)}")
    print(f"  rules with NONE                  : {len(undet)}  -> {sorted(undet)}  "
          f"(non-use is UNKNOWN for these, never zero)")
    print()
    print("--- THE THREE CLASSES  (denominator = "
          f"{N} transcripts) -------------------------")
    print(f"  USED                 {len(used):>5}   invocation present AND labels emitted")
    print(f"  PARTIAL  'kinda did' {len(partial):>5}   invoked, no label anywhere in the file")
    print(f"  APPLICABLE-NOT-USED  {len(anu):>5}   precursor present, never invoked, never labeled")
    print()
    print("--- SIDE BY SIDE WITH corpus_index (divergence made visible, not silent) ------")
    q = CI.three_class(sorted(rows.values(), key=lambda r: r["path"]),
                       "ground-before-stating", CI.load_skills())
    print(f"  corpus_index USED                : {len(q['USED'])}   "
          f"(its marker = the LABELS themselves)")
    print(f"  corpus_index PARTIAL             : UNDETECTABLE (no completion literal declared)")
    print(f"  corpus_index APPLICABLE_NOT_USED : {len(q['APPLICABLE_NOT_USED'] or [])}   "
          f"(its triggers are META-REQUESTS in JON'S turns only)")
    print(f"  this file  APPLICABLE-NOT-USED   : {len(anu)}   "
          f"(object-level precursors, ASSISTANT turns included)")
    print("  The two are answering different questions. Neither supersedes the other; the")
    print("  ratio is the measure of how much of GBS's applicability Jon never asks for.")
    print()
    print("--- PER-RULE  (precursor occurrences unanswered by any GBS label) -------------")
    print(f"  {'rule':<4} {'name':<26} {'files':>6} {'occurrences':>12}   basis")
    for n in sorted(RULES):
        spec = RULES[n]
        if not spec["state"]:
            print(f"  {n:<4} {spec['name']:<26} {'UNKNOWN':>6} {'UNKNOWN':>12}   "
                  f"no declared precursor")
            continue
        f = sum(1 for r in recs if (r[f"r{n}"] or 0) > 0)
        o = sum((r[f"r{n}"] or 0) for r in recs)
        note = spec["src"][:46]
        if spec.get("born"):
            print(f"  {n:<4} {spec['name']:<26} {f:>6} {o:>12}   {note}")
            pre = sum(1 for r in recs
                      if (r[f"r{n}"] or 0) > 0 and r["date"] < spec["born"])
            print(f"       {'':<26} {'':>6} {'':>12}   of those, {pre} files PREDATE the rule "
                  f"({spec['born']}) — not failures")
        else:
            print(f"  {n:<4} {spec['name']:<26} {f:>6} {o:>12}   {note}")
    print()
    print("--- WHY THE UNDETECTABLE RULES ARE UNDETECTABLE ------------------------------")
    for n in sorted(undet):
        print(f"  Rule {n} ({RULES[n]['name']}): {RULES[n]['why']}")
    print()

    if only_rule:
        n = only_rule
        print(f"--- RULE {n} CANDIDATES (top by occurrence count) ---------------------------")
        top = sorted((r for r in recs if (r[f"r{n}"] or 0) > 0),
                     key=lambda r: -(r[f"r{n}"] or 0))[:limit * 3]
        for r in top:
            print(f"  {r[f'r{n}']:>4}x  {r['date']}  {r['path']}")
        print()
        return

    print("--- APPLICABLE-NOT-USED, top files by total unanswered precursors ------------")
    top = sorted(anu, key=lambda r: -sum((r[f"r{n}"] or 0) for n in detectable))[:limit]
    for r in top:
        per = " ".join(f"R{n}={r[f'r{n}']}" for n in detectable if (r[f"r{n}"] or 0) > 0)
        print(f"  {r['date']}  {per:<34} {r['path']}")
    if len(anu) > limit:
        print(f"  ... {len(anu) - limit} more")
    print()
    print("--- WHAT WOULD MAKE THIS RECORD LIE ------------------------------------------")
    print("  1. PRESENCE IS NOT USE, AND PRECURSOR IS NOT FAILURE. Every count here is a")
    print("     CANDIDATE count. `corpus_index` learned this the expensive way: 4 of 4 FBC")
    print("     candidates opened by hand were Jon DISCUSSING the protocol, not asking for it.")
    print("  2. THE MARKDOWN CORPUS HAS NO TOOL-CALL RECORD. The Rule 6 hook's real test is")
    print("     'did a verify tool fire THIS TURN'; here that is approximated by nearby text.")
    print("     This detector is strictly WEAKER than the hook it borrows from, and over-counts.")
    print("  3. FOUR OF EIGHT RULES CANNOT BE SEEN AT ALL. Any total is a total over half the")
    print("     skill. A low number for Rules 1/3/4/5 does not exist — UNKNOWN was printed.")
    print("  4. RULE 8 WAS BORN 2026-08-06. Occurrences before that date are not non-use of a")
    print("     rule; they are the evidence that motivated writing it.")
    print("  5. SUBAGENT TRANSCRIPTS HAVE NO JON. Rule 7 fires on role `H` only, so its count")
    print("     is over main sessions and structurally excludes ~1,300 subagent files.")
    print()


def self_test():
    ok = True

    def chk(label, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    print("=== SELF-TEST — gbs_record (negative controls first) ===")

    # NEGATIVE CONTROL — the direction that matters is the one that INFLATES.
    chk("plain prose with no precursor scores 0 on every rule",
        all((hits_rule(n, {"__seq__": [("A", "Next step is to draft the page and self-test it.")]})
             or 0) == 0 for n in RULES if RULES[n]["state"]))
    # Rule 6 positive, then its two documented exemptions.
    r6 = lambda t: hits_rule(6, {"__seq__": [("A", t)]})
    chk("R6 fires on an unlabeled absolutist claim",
        r6("Confirmed: settings.json is unwritable.") == 1)
    chk("two patterns in ONE sentence merge to one occurrence, not two",
        r6("Confirmed: it is unwritable.") == 1)
    chk("two claims far apart count separately",
        r6("Confirmed: A holds." + " " * 400 + "It is known that B holds.") == 2)
    chk("R6 does NOT fire when the claim is honestly labeled",
        r6("[unverified] settings.json may be unwritable.") == 0)
    chk("R6 does NOT fire when a git check sits beside the claim",
        r6("I ran `git log -3` on it. Confirmed: settings.json is unwritable.") == 0)
    chk("R6 ignores JON's turns (precursor is an ASSISTANT act)",
        hits_rule(6, {"__seq__": [("H", "Confirmed: it is permanently gone.")]}) == 0)
    # THE TURN-SCOPED CHECK. Added after hand-verification showed the text-window proxy was
    # producing ~all false positives of one shape: reports of a check that had just run.
    chk("R6 exempt when a Tool Result landed earlier in the SAME turn",
        hits_rule(6, {"__seq__": [("H", "q"), ("R", "ls output"),
                                  ("A", "Confirmed: exactly three files.")]}) == 0)
    chk("R6 still fires when no Tool Result preceded the claim",
        hits_rule(6, {"__seq__": [("H", "q"),
                                  ("A", "Confirmed: exactly three files.")]}) == 1)
    chk("a Tool Result does NOT carry across a new human turn",
        hits_rule(6, {"__seq__": [("H", "q1"), ("R", "ls output"), ("A", "ok"),
                                  ("H", "q2"),
                                  ("A", "Confirmed: exactly three files.")]}) == 1)
    # Rule 7 positives and the hook's own documented negative.
    r7 = lambda seq: hits_rule(7, {"__seq__": seq})
    chk("R7 fires on a bare 'yes' with no read-back",
        r7([("H", "yes"), ("A", "Done, landed it.")]) == 1)
    chk("R7 does NOT fire when the next turn reads the decision back",
        r7([("H", "yes"), ("A", "Reading that back: you are approving the register fix.")]) == 0)
    chk("R7 does NOT fire on 'yesterday' (the hook's own negative control)",
        r7([("H", "yesterday's numbers were off"), ("A", "ok")]) == 0)
    chk("R7 does NOT fire on a DISPATCH turn — an agent brief is not Jon",
        r7([("D", "yes, go ahead"), ("A", "Done.")]) == 0)
    # Rule 8.
    r8 = lambda seq: hits_rule(8, {"__seq__": seq})
    chk("R8 fires on a bare Jon citation with no gradient",
        r8([("A", "Jon ruled that the mirror is required.")]) == 1)
    chk("R8 does NOT fire when the gradient is carried",
        r8([("A", "Jon ruled the mirror is required — said in response to being shown "
                  "it was 29% of spend.")]) == 0)
    # UNDECLARED must be None, never 0.
    chk("undeclared rules return None (UNKNOWN), not 0",
        all(hits_rule(n, {"__seq__": [("A", "anything")]}) is None
            for n in RULES if not RULES[n]["state"]))
    # Corpus reuse, not redefinition.
    chk("CORPUS resolves transitively to coverage_gap's, via corpus_index",
        CI.CORPUS == __import__("coverage_gap").CORPUS)

    # STALE-SCHEMA POSTURE — both directions. Temp index only; the real one is never touched.
    import tempfile
    with tempfile.TemporaryDirectory() as _td:
        _p = Path(_td) / "idx.jsonl"

        def _at(schema, n=3):
            _p.write_text("#" + json.dumps({"schema": schema, "rows": n}) + "\n" + "".join(
                json.dumps({"path": f"a/{i}.md"}) + "\n" for i in range(n)), encoding="utf-8")
            return CI.read_index(_p)

        _f, _s = _at(CI.SCHEMA_VERSION), _at("corpus-index-v0")
        chk("FRESH temp index -> FRESH", _f.fresh)
        chk("STALE temp index -> STALE_SCHEMA, NOT the ABSENT message this file used to print",
            _s.status == CI.INDEX_STALE and not _s.fresh)
        chk("STALE read names 3 rows on disk — the denominator that separates it from ABSENT",
            _s.n_rows_on_disk == 3)
        chk("absent index -> ABSENT with 0 rows on disk",
            CI.read_index(Path(_td) / "nope.jsonl").status == CI.INDEX_ABSENT)
        chk("FRESH raises no banner (the RATIO_FLOOR lesson: an alarm that always fires is noise)",
            _f.banner("gbs_record") == "")
    # raw/ untouched.
    sample = [p for p, _ in CI.walk_corpus()][::97]
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    rows, _ = CI.load_prior()
    scan(dict(list(rows.items())[:40]))
    after = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    chk(f"a scan leaves raw/ byte- and mtime-identical ({len(sample)} sampled)", before == after)

    print("\nRESULT: " + ("PASS — controls fire in both directions." if ok
                          else "FAIL — do not trust its counts."))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--rule", type=int, default=None, help="drill into one rule's candidates")
    ap.add_argument("--max-files", type=int, default=None, help="scan only the first N (testing)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    # `CI.load_prior()` + `if not rows` printed "[no corpus index on disk]" on 2026-08-06 while
    # 1,172 rows sat on disk under a schema this code no longer spoke. ABSENT and STALE are not
    # the same finding and must not share a message: one means nothing was ever built, the other
    # means the build is fine and THIS CODE moved. `require_index` separates them and prints the
    # denominator (`rows on disk`) that proves which one it is.
    read = CI.require_index("gbs_record")
    rows, bad = read.rows, read.n_malformed
    if not read.fresh:
        print(f"GBS record = UNKNOWN, not zero  [{read.status}] — {read.one_line()}",
              file=sys.stderr)
        print("This is NOT a result. Nothing was scanned.", file=sys.stderr)
        return 0
    recs = scan(rows, limit_files=args.max_files)
    report(recs, rows, limit=args.limit, only_rule=args.rule)
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
