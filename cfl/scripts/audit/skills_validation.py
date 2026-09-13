#!/usr/bin/env python3
"""skills_validation.py -- held-out validation runner for the CFL skills gate (GT-1, 2026-09-02).

WHY: GATE-SPEC's own "What this is not (yet)" section says the gate has no held-out task
split -- it gates on cold-reader panels. The WikiSkill mechanism CFL adopted gates on
STRICT IMPROVEMENT OVER A HELD-OUT SPLIT vs best-so-far. Without a split there is no
number, and without a number "strict improvement" is prose. This is the number.

WHAT IT MEASURES: not task success in the world -- the LETTER'S OWN CHECKABLE PROPERTIES.
A letter is produced by an inference agent that has the skill text in context; this runner
scores the produced letter against properties sealed in the split BEFORE any run.

A SCRIPT CANNOT DISPATCH A SUBAGENT, so production is out-of-band and this runner has
three modes:

  --emit-packets DIR   one self-contained prompt packet per task (skill text + fixture +
                       instruction) plus one grading packet per task. The packet is
                       everything the producing agent gets; no other context.
  --score DIR          apply the MECHANICAL checks to <DIR>/<id>.md and emit R + rows.
                       Properties prefixed `cold:` are NOT mechanically checkable and are
                       emitted as UNKNOWN. UNKNOWN NEVER ROUNDS TO PASS: it is excluded
                       from the mechanical denominator and reported separately.
  --merge-cold JSON    fold a cold-grader lane's verdicts ({id: {property: PASS|FAIL}})
                       into a scored run and emit the combined R.

REPRODUCIBILITY: tasks are processed in sorted-id order, properties in split order, and
every check is a pure function of the letter bytes -- no sampling, no model call, no clock.
`seed` is recorded as "n/a-deterministic" because nothing here is stochastic; recording it
is the seal, recording a fake number would not be.

CANNOT-DETECT (stated, per house rule): whether the letter is TRUE, whether its quotes have
primaries, whether the on_silence default is the RIGHT default, and whether a cold reader
can actually act on it. Those are the `cold:` half and the grading packets exist for them.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import lint_silence_clause as LSC        # noqa: E402  (rule 8's mechanism, reused not reimplemented)
import on_silence_report as OSR          # noqa: E402  (rule 9's mechanism, reused not reimplemented)
from gt2_properties import gt2_check     # noqa: E402  (GT-2 2026-09-02: wake/dream/su-compact/wayfinder vocabularies)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- letter parsing

def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if m:
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def quoted_spans(text):
    """Double-quoted spans and blockquote lines -- the places a Jon quote lives."""
    spans = [m.group(0) for m in re.finditer(r'"[^"\n]{8,}"', text)]
    spans += [ln for ln in text.splitlines() if ln.lstrip().startswith(">")]
    return spans


# ---------------------------------------------------------------- property checks
# Each returns (verdict, note). verdict in {PASS, FAIL}. Never UNKNOWN here: a mechanical
# check that cannot decide must not exist -- it would be an UNKNOWN wearing a PASS costume.

ACTING = LSC.ACTING
STATE_WORDS = {
    "undelivered": r"\bundelivered\b",
    "unreceipted": r"\bunreceipted\b|\bunread\b",
    "declined": r"\bdeclined?\b",
}


def check(prop, path, text, fm):
    if prop.startswith("fm:"):
        key = prop[3:]
        v = fm.get(key, "")
        return ("PASS" if v else "FAIL"), "%s=%r" % (key, v)

    if prop.startswith("contains_exact:"):
        needle = prop[len("contains_exact:"):]
        return ("PASS" if needle in text else "FAIL"), "literal substring present=%s" % (needle in text)

    if prop == "expires_parseable":
        v = fm.get("expires", "")
        dl = OSR.parse_expiry(v) if v else None
        return ("PASS" if dl else "FAIL"), "expires=%r -> %s" % (v, dl)

    if prop == "on_silence_acting_label":
        v = fm.get("on_silence", "")
        return ("PASS" if v and ACTING.search(v) else "FAIL"), "on_silence=%r" % v

    if prop == "on_silence_sentence_not_label":
        v = fm.get("on_silence", "")
        words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", v))
        ok = bool(v) and words >= 6 and bool(ACTING.search(v))
        return ("PASS" if ok else "FAIL"), "words=%d acting=%s v=%r" % (words, bool(ACTING.search(v)), v)

    if prop == "silence_lint_pass":
        problems = LSC.lint(Path(path))
        return ("PASS" if not problems else "FAIL"), ("clean" if not problems else problems[0])

    if prop == "no_expires_and_unclocked_declared_deliberate":
        has_exp = bool(fm.get("expires"))
        declared = bool(re.search(r"unclocked", text, re.I)) and bool(
            re.search(r"deliberat|standing (letter|notice|offer)|does not expire|no deadline", text, re.I))
        ok = (not has_exp) and declared
        return ("PASS" if ok else "FAIL"), "expires_present=%s deliberateness_declared=%s" % (has_exp, declared)

    if prop == "receipt_mark_present":
        ok = bool(re.search(r"^\s*receipt\s*:", text, re.I | re.M)) or bool(
            re.search(r"^#{1,6}\s*receipt\b", text, re.I | re.M)) or bool(
            re.search(r"\bRECEIPT\b", text))
        return ("PASS" if ok else "FAIL"), "receipt mark=%s" % ok

    if prop == "undispositioned_state_reported":
        ok = bool(re.search(r"undispositioned|receipted[^.\n]{0,40}not (yet )?dispositioned|"
                            r"read[^.\n]{0,30}not (yet )?decided", text, re.I))
        return ("PASS" if ok else "FAIL"), "undispositioned state named=%s" % ok

    if prop == "delivery_state_ladder":
        hits = [w for w in ("DELIVERED", "RECEIPTED", "DISPOSITIONED") if w in text.upper()]
        return ("PASS" if len(hits) == 3 else "FAIL"), "ladder terms present=%s" % hits

    if prop == "three_states_named":
        missing = [k for k, rx in STATE_WORDS.items() if not re.search(rx, text, re.I)]
        return ("PASS" if not missing else "FAIL"), "missing=%s" % missing

    if prop == "unreceipted_not_declined":
        has = bool(re.search(r"\bunreceipted\b", text, re.I))
        conflates = bool(re.search(r"silence\s+(is|means|=|counts as)\s+[^.\n]{0,20}declin", text, re.I))
        ok = has and not conflates
        return ("PASS" if ok else "FAIL"), "unreceipted=%s conflation=%s" % (has, conflates)

    if prop == "no_emphasis_inside_quote":
        bad = [s[:60] for s in quoted_spans(text) if re.search(r"\*\*|__|~~", s)]
        return ("PASS" if not bad else "FAIL"), "emphasised quoted spans=%s" % bad

    if prop == "byte_verify_named":
        ok = bool(re.search(r"\bcmp\b|byte[- ]verif", text, re.I))
        return ("PASS" if ok else "FAIL"), "byte-verification named=%s" % ok

    if prop == "deadline_three_actions":
        acts = 0
        for ln in text.splitlines():
            present = [k for k, rx in STATE_WORDS.items() if re.search(rx, ln, re.I)]
            if len(present) == 1 and re.search(r"\bwill\b|\bfires?\b|\bacts?\b|->", ln):
                acts += 1
        return ("PASS" if acts >= 3 else "FAIL"), "lines naming exactly one state with an action=%d" % acts

    if prop == "size_le_1200_bytes":
        n = len(text.encode("utf-8"))
        return ("PASS" if n <= 1200 else "FAIL"), "%d bytes" % n

    # GT-2 2026-09-02: append-only delegation. gt2_check owns ONLY names that did not
    # exist above, so exchange-letters scoring is byte-identical before and after.
    _gt2 = gt2_check(prop, path, text, fm)
    if _gt2 is not None:
        return _gt2

    return "FAIL", "UNIMPLEMENTED PROPERTY %r -- a check that does not exist is not a pass" % prop


# ---------------------------------------------------------------- modes

def load_split(p):
    rows = [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]
    return sorted(rows, key=lambda r: r["id"])


def emit_packets(rows, skill_text, skill_path, outdir, tier):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for r in rows:
        fixture = (ROOT / r["fixture_path"]).read_text(encoding="utf-8")
        produce = (
            "# Production packet %s (tier: %s)\n\n"
            "You are a CFL letter writer. You have exactly the skill text below and the\n"
            "situation below. Use NOTHING else. Output ONE letter, markdown with YAML\n"
            "frontmatter, and nothing but the letter. Save it as `%s.md`.\n\n"
            "## SKILL TEXT (%s)\n\n%s\n\n## SITUATION\n\n%s\n"
        ) % (r["id"], tier, r["id"], skill_path, skill_text, fixture)
        (outdir / ("%s-PRODUCE.md" % r["id"])).write_text(produce, encoding="utf-8")
        cold_list = "".join("  - %s\n" % e for e in r["expected"] if e.startswith("cold:"))
        grade = (
            "# Cold-grading packet %s\n\n"
            "You have ONLY the produced letter `%s.md`. You have not seen the skill,\n"
            "the situation, or the expected properties. Do not infer them.\n\n"
            "## INSTRUCTION\n\n%s\n\n"
            "## RETURN\n\nJSON: {\"%s\": {\"<cold property>\": \"PASS\"|\"FAIL\"}}\n"
            "Cold properties for this task:\n%s"
        ) % (r["id"], r["id"], r["grader_instruction"], r["id"], cold_list)
        (outdir / ("%s-GRADE.md" % r["id"])).write_text(grade, encoding="utf-8")
    return len(rows) * 2


def score(rows, letters_dir):
    letters_dir = Path(letters_dir)
    out_rows = []
    for r in rows:
        lp = letters_dir / ("%s.md" % r["id"])
        if not lp.is_file():
            out_rows.append(dict(id=r["id"], letter=None, properties=[
                dict(property=e, verdict="UNKNOWN" if e.startswith("cold:") else "FAIL",
                     note="letter not produced -- absence is never a pass")
                for e in r["expected"]]))
            continue
        text = lp.read_text(encoding="utf-8")
        fm = frontmatter(text)
        props = []
        for e in r["expected"]:
            if e.startswith("cold:"):
                props.append(dict(property=e, verdict="UNKNOWN",
                                  note="cold-reader property; not mechanically checkable"))
            else:
                v, note = check(e, lp, text, fm)
                props.append(dict(property=e, verdict=v, note=note))
        out_rows.append(dict(id=r["id"], letter=str(lp), bytes=len(text.encode("utf-8")),
                             sha256=sha256_file(lp), properties=props))
    return out_rows


def tally(out_rows):
    p = f = u = 0
    for r in out_rows:
        for pr in r["properties"]:
            if pr["verdict"] == "PASS":
                p += 1
            elif pr["verdict"] == "FAIL":
                f += 1
            else:
                u += 1
    return p, f, u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--skill-file", required=True)
    ap.add_argument("--split", required=True)
    ap.add_argument("--tier", required=True)
    ap.add_argument("--out")
    ap.add_argument("--emit-packets")
    ap.add_argument("--score")
    ap.add_argument("--merge-cold")
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    split_p = Path(a.split)
    rows = load_split(split_p)
    skill_p = Path(a.skill_file)
    skill_text = skill_p.read_text(encoding="utf-8")

    meta = dict(skill=a.skill, skill_file=str(skill_p), skill_sha256=sha256_file(skill_p),
                split=str(split_p), split_sha256=sha256_file(split_p), tier=a.tier,
                runner_sha256=sha256_file(Path(__file__)), seed="n/a-deterministic",
                run_ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                label=a.label, tasks=len(rows))

    if a.emit_packets:
        n = emit_packets(rows, skill_text, skill_p, a.emit_packets, a.tier)
        print("emitted %d packets (%d produce + %d grade) -> %s" % (n, len(rows), len(rows), a.emit_packets))
        return 0

    if not a.score:
        print("UNKNOWN: no mode given (--emit-packets | --score | with --merge-cold)")
        return 2

    out_rows = score(rows, a.score)
    if a.merge_cold:
        cold = json.loads(Path(a.merge_cold).read_text(encoding="utf-8"))
        for r in out_rows:
            for pr in r["properties"]:
                if pr["verdict"] == "UNKNOWN":
                    v = cold.get(r["id"], {}).get(pr["property"])
                    if v in ("PASS", "FAIL"):
                        pr["verdict"] = v
                        pr["note"] = "cold grader"

    p, f, u = tally(out_rows)
    denom = p + f
    R = round(p / denom, 4) if denom else 0.0
    print("=== skills_validation %s [%s] tier=%s ===" % (a.skill, a.label or "unlabelled", a.tier))
    print("skill_sha256 %s  split_sha256 %s  runner_sha256 %s  seed %s"
          % (meta["skill_sha256"][:8], meta["split_sha256"][:8], meta["runner_sha256"][:8], meta["seed"]))
    for r in out_rows:
        rp = sum(1 for x in r["properties"] if x["verdict"] == "PASS")
        rf = sum(1 for x in r["properties"] if x["verdict"] == "FAIL")
        ru = sum(1 for x in r["properties"] if x["verdict"] == "UNKNOWN")
        tail = ("   [%s B]" % r.get("bytes")) if r.get("bytes") else "   [NO LETTER]"
        print("  %s  PASS %2d  FAIL %2d  UNKNOWN %2d%s" % (r["id"], rp, rf, ru, tail))
        for x in r["properties"]:
            if x["verdict"] == "FAIL":
                print("        FAIL %s  (%s)" % (x["property"], x["note"]))
    print("R = %d/%d = %s   (UNKNOWN %d - excluded from the denominator; UNKNOWN never rounds to PASS)"
          % (p, denom, R, u))
    result = dict(meta=meta, R=R, passed=p, failed=f, unknown=u, rows=out_rows)
    if a.out:
        Path(a.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
