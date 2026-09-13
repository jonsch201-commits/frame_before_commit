"""Did Jon's LATEST word on a standing rule ever reach the constitution?

WHY THIS EXISTS -- one case, measured, and it cost a month.

Jon, 2026-09-12 ~21:5x CDT, verbatim (typos his):
  "And, the pii issue. THis is a defect and wrong and its caused me more headaches than I can count.
   Look their is pii that can't go to a *public* github.... but.... No wonder you've been wrong about
   my PII preferences so many times. I kept correcting you, and you never fixed the claude.md."

He was right. CLAUDE.md's PII bullet was headed "NO WRITING PII TO GITHUB -- binds every write path"
and [measured] this repo is PRIVATE, so the rule fenced a private tree on every commit. The quotes in
it were all genuinely his. THE DEFECT WAS PRECEDENCE: his 2026-08-09 line, said about one consent
record, was the HEADING, while the 08-11 and 08-19 rulings that narrow it sat beneath as commentary.
The oldest quote governed and the newest footnoted it. Seven further corrections were in
history.jsonl and none reached the file.

So the gap this checks is not "is there a rule" and not "is the rule true". It is:

  FOR EACH STANDING-CONSTRAINT BULLET, IS THE NEWEST JON QUOTE IN THE FILE ALSO THE NEWEST THING
  JON HAS SAID ON THAT SUBJECT?

WHAT IT DOES NOT DO, stated plainly because a checker that overstates gets switched off:
  * It does not judge whether a later utterance CHANGES the rule. Many will not. Every row is a
    CANDIDATE for a human read, never a verdict, and the output says so on every run.
  * Its topic keywords are DERIVED from the bullet headings in the constitution itself, not from a
    list maintained here -- so a new bullet is covered the day it is written ([[derive-dont-record]]).
    That also means a badly-worded heading gets badly-chosen keywords; the fix is the heading.
  * It reads ONE venue (~/.claude/history.jsonl, Jon's typed prompts). It is therefore a LOWER BOUND
    on unlanded corrections, in the honest direction. The other venues are catalogued at
    wiki/references/constitution/constitution-where-jons-words-live.md and a full sweep needs them.
  * A zero from this script is a claim about this ONE venue until a second method agrees (Rule 15).

Usage:
    python scripts/audit/correction_landed.py                   # CLAUDE.md
    python scripts/audit/correction_landed.py --file CLAUDE-UNIVERSAL.md
    python scripts/audit/correction_landed.py --selftest
Exit: 0 no candidate gaps | 3 candidates found (a report, never a block) | 4 could not run (UNKNOWN)
"""
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
HISTORY = Path.home() / ".claude" / "history.jsonl"
CDT = timezone(timedelta(hours=-5))

# A SECOND, INDEPENDENT CONDITION -- not a tuned threshold.
# After the rarity filter the check still returned ~1 real row in 8, because "a later prompt on the
# same subject" is not the same thing as "a correction". These are the words Jon actually uses when
# he is telling a seat it has the rule wrong; the PII message that started this carries four of them
# ("defect", "wrong", "kept correcting", "never fixed"). Declared here so a reader can argue with the
# list, and widened only by adding a phrase HE has used -- never by whatever makes today's output
# look tidier. Soul, tonight: "a definition tuned until its output is comfortable is the test
# calibrated to current behaviour."
CORRECTION = ("wrong", "defect", "kept correcting", "keep correcting", "never fixed", "not fixed",
              "i told you", "i fucking told you", "stop making me", "i said", "thats not what",
              "that's not what", "you never", "still not", "why did you", "you were wrong",
              "no wonder", "do better", "you should have learned", "this is bad", "thats bad",
              "that's bad", "fix claude.md", "fix the claude.md")

# Words too common to identify a subject. Deliberately short: a long stop-list is a topic model
# nobody reviewed, and this script's whole claim is that its keywords come from the file.
STOP = set("""the a an and or but not is are was were be been being to of in on for with from by at
as it its this that these those his her their our your my me you he she they we i if then than so
such no nor only own same too very can will just don't should now what which who whom when where why
how all any both each few more most other some own s t just binds every write path rule rules jon
word words said says say quote quotes primary primaries standing constraint constraints one two three
never always must fine bad good thing things way ways""".split())


def topics(text):
    """Derive (heading, keywords, newest_quote_date) per standing-constraint bullet.

    A bullet is a top-level `- **...**` item; its quotes are the `> *"..."*` lines beneath it and its
    dates are any YYYY-MM-DD or `2026-08-09`-style stamps inside the bullet.
    """
    out = []
    lines = text.split(chr(10))
    starts = [i for i, l in enumerate(lines) if re.match(r"^- \*\*", l)]
    for n, i in enumerate(starts):
        j = starts[n + 1] if n + 1 < len(starts) else len(lines)
        body = chr(10).join(lines[i:j])
        head = re.sub(r"[*`]", "", lines[i][2:]).strip()
        kw = {w for w in re.findall(r"[a-z][a-z'-]{2,}", head.lower()) if w not in STOP}
        dates = re.findall(r"(20\d{2})-(\d{2})-(\d{2})", body)
        newest = None
        for y, m, d in dates:
            try:
                dt = datetime(int(y), int(m), int(d), tzinfo=CDT)
            except ValueError:
                continue
            if newest is None or dt > newest:
                newest = dt
        # POPULATION FIX, 2026-09-12: only a bullet that QUOTES JON is in scope. The first three
        # runs swept every `- **` item in the file -- Repo Hygiene, the corpus bullets, the mirror's
        # contract -- none of which carries a Jon quote, so "has his newest word landed" is not a
        # question they can fail. That was a scoping error and it produced most of the noise. It is
        # not a threshold; widening the population back would not find more corrections, only more
        # rows.
        if not re.search(r'^\s*> \*"', body, re.M):
            continue
        out.append({"line": i + 1, "head": head, "kw": kw, "newest": newest, "body": body})
    return out


def jon_prompts(path=None):
    """Jon's typed prompts as (line_no, datetime, text). A missing file returns None, not []."""
    path = path or HISTORY
    if not Path(path).is_file():
        return None
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8", errors="replace").split(chr(10)), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        txt = r.get("display") or r.get("prompt") or ""
        ts = r.get("timestamp")
        if not txt or not isinstance(ts, (int, float)):
            continue
        try:
            dt = datetime.fromtimestamp(ts / 1000, tz=CDT)
        except (OverflowError, OSError, ValueError):
            continue
        rows.append((n, dt, txt))
    return rows


def audit(rel="CLAUDE.md", history=None, min_kw=2, root=None, df_max=0.02,
          corrections_only=True):
    root = root or ROOT
    f = Path(root) / rel
    if not f.is_file():
        return 4, [], {"why": f"{rel} not on disk under {root}"}
    prompts = jon_prompts(history)
    if prompts is None:
        return 4, [], {"why": f"no typed-prompt history at {history or HISTORY} -- "
                              f"UNKNOWN, and a check that could not run dominates a pass"}
    tps = topics(f.read_text(encoding="utf-8"))
    if not tps:
        return 4, [], {"why": f"no `- **...**` standing-constraint bullets parsed out of {rel} -- "
                              f"an empty denominator is never a pass"}
    flat = " ".join(f.read_text(encoding="utf-8").lower().split())

    # A DERIVED STOP-LIST, because the hand-written one above cannot know this corpus.
    # First run of this script, before this filter: 8 CANDIDATE rows of which ONE was real. The
    # noise all came from heading words that are common in Jon's prose -- "read", "has", "means",
    # "assume", "agent", "reason" -- so two of them co-occur in almost any prompt and the check
    # matched on vocabulary rather than on subject. A keyword earns its place by being RARE: if it
    # appears in more than `df_max` of his prompts it identifies nothing.
    # This is the same defect as every other instrument here on its first run, and in the same
    # direction its own docstring predicted.
    from collections import Counter
    df = Counter()
    for _n, _dt, _txt in prompts:
        for w in set(re.findall(r"[a-z][a-z'-]{2,}", _txt.lower())):
            df[w] += 1
    ceiling = max(1, int(len(prompts) * df_max))
    for t in tps:
        t["common"] = {k for k in t["kw"] if df[k] > ceiling}
        t["kw"] = t["kw"] - t["common"]
    gaps = []
    for t in tps:
        if t["newest"] is None or len(t["kw"]) < min_kw:
            gaps.append({"kind": "UNGRADED", "topic": t, "why":
                         "no date in the bullet" if t["newest"] is None
                         else f"heading yields {len(t['kw'])} distinctive keyword(s), under "
                              f"min {min_kw} (dropped as too common in his prose: "
                              f"{', '.join(sorted(t.get('common', ()))[:6]) or 'none'})"})
            continue
        later = []
        for n, dt, txt in prompts:
            if dt <= t["newest"]:
                continue
            low = txt.lower()
            hit = {k for k in t["kw"] if k in low}
            if len(hit) < min_kw:
                continue
            sig = [c for c in CORRECTION if c in low]
            if corrections_only and not sig:
                continue
            later.append((n, dt, txt, sorted(hit) + ["!" + sig[0]] if sig else sorted(hit)))
        # A later utterance whose own distinctive wording is ALREADY in the file has landed --
        # that is the whole point of the check and it must be able to come back clean. The test is a
        # run of >=25 characters from the prompt appearing verbatim in the file, which is what
        # quoting him actually produces.
        unlanded = []
        for n, dt, txt, hit in later:
            runs = [" ".join(r.split()) for r in re.findall(r"[A-Za-z][A-Za-z',. -]{24,}", txt)]
            if any(r.lower() in flat for r in runs if len(r) >= 25):
                continue
            unlanded.append((n, dt, txt, hit))
        if unlanded:
            gaps.append({"kind": "CANDIDATE", "topic": t, "later": unlanded})
    rc = 3 if any(g["kind"] == "CANDIDATE" for g in gaps) else 0
    return rc, gaps, {"bullets": len(tps), "prompts": len(prompts)}


def main():
    rel = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "CLAUDE.md"
    co = "--all-later" not in sys.argv
    rc, gaps, stats = audit(rel, corrections_only=co)
    print(f"=== correction-landed check: {rel} ===")
    if rc == 4:
        print("UNKNOWN -- could not run: " + stats["why"])
        return 4
    print(f"bullets QUOTING JON, in scope       : {stats['bullets']}  "
          f"(a bullet with no Jon quote cannot fail this check)")
    print(f"Jon typed prompts read             : {stats['prompts']}  (ONE venue -- lower bound)")
    print(f"keyword ceiling                    : a heading word appearing in >2% of his prompts "
          f"identifies nothing and is dropped")
    print("second condition                   : " + ("ON -- the later prompt must also carry a "
          "correction signal (--all-later to disable)" if co else "OFF -- every later prompt on the "
          "subject is listed, expect noise"))
    print()
    cands = [g for g in gaps if g["kind"] == "CANDIDATE"]
    ung = [g for g in gaps if g["kind"] == "UNGRADED"]
    for g in cands:
        t = g["topic"]
        print(f"CANDIDATE  CLAUDE.md:{t['line']}  newest quote in file: {t['newest'].date()}")
        print(f"           rule: {t['head'][:110]}")
        for n, dt, txt, hit in g["later"][-4:]:
            print(f"           later Jon prompt history.jsonl:{n} {dt.date()} on {','.join(hit)}")
            print(f"             {' '.join(txt.split())[:180]}")
        print()
    for g in ung:
        print(f"UNGRADED   CLAUDE.md:{g['topic']['line']}  {g['why']}  -- not a pass")
        print(f"           rule: {g['topic']['head'][:110]}")
    print()
    print("EVERY ROW IS A CANDIDATE FOR A HUMAN READ, NEVER A VERDICT. A later utterance on the same")
    print("subject often does not change the rule. What this cannot do is stay silent while the")
    print("newest thing Jon said on a subject sits outside the file that states the rule.")
    return rc


def selftest():
    import tempfile
    NL = chr(10)
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        hist = t / "history.jsonl"

        def ms(y, m, d):
            return int(datetime(y, m, d, 12, 0, tzinfo=CDT).timestamp() * 1000)

        def write_hist(rows):
            hist.write_text(NL.join(json.dumps(r) for r in rows) + NL, encoding="utf-8")

        RULE = ("- **PII scrubbing binds every github repository**" + NL
                + "  Jon, **2026-08-09**:" + NL
                + '  > *"no writing pii to github"*' + NL)

        # arm 1: a LATER Jon prompt on the same subject -> CANDIDATE
        (t / "CLAUDE.md").write_text(RULE, encoding="utf-8")
        write_hist([{"timestamp": ms(2026, 9, 12),
                     "display": "the pii issue is a defect, pii cannot go to a public github repository"}])
        rc, gaps, st = audit(history=hist, root=t)
        if rc != 3 or not any(g["kind"] == "CANDIDATE" for g in gaps):
            fails.append(f"arm 1 (later utterance) -> rc={rc} gaps={[g['kind'] for g in gaps]}")

        # arm 2: ONE condition differs -- the same prompt is EARLIER than the quote
        write_hist([{"timestamp": ms(2026, 8, 1),
                     "display": "the pii issue is a defect, pii cannot go to a public github repository"}])
        rc, gaps, st = audit(history=hist, root=t)
        if rc != 0:
            fails.append(f"arm 2 (earlier utterance) -> rc={rc}")

        # arm 3: later, but on an unrelated subject -> no candidate
        write_hist([{"timestamp": ms(2026, 9, 12), "display": "please rebuild the graph index tonight"}])
        rc, gaps, st = audit(history=hist, root=t)
        if rc != 0:
            fails.append(f"arm 3 (unrelated) -> rc={rc}")

        # arm 4: a bullet with NO date is UNGRADED, never a pass
        (t / "CLAUDE.md").write_text("- **PII scrubbing binds every github repository**" + NL
                                     + '  > *"no writing pii to github"*' + NL, encoding="utf-8")
        rc, gaps, st = audit(history=hist, root=t)
        if not any(g["kind"] == "UNGRADED" for g in gaps):
            fails.append("arm 4 (undated bullet) -> no UNGRADED row")

        # arm 4b: a heading whose only words are COMMON in his prose must go UNGRADED, not
        #         CANDIDATE -- the first run of this script produced 8 rows, 1 of them real.
        (t / "CLAUDE.md").write_text("- **Read the thing and assume it means what it says**" + NL
                                     + "  Jon, **2026-08-09**:" + NL
                                     + '  > *"read it"*' + NL, encoding="utf-8")
        write_hist([{"timestamp": ms(2026, 8, i % 28 + 1),
                     "display": "please read that and assume it means the thing it says"}
                    for i in range(60)]
                   + [{"timestamp": ms(2026, 9, 12),
                       "display": "read this and assume it means something else entirely"}])
        rc, gaps, st = audit(history=hist, root=t)
        if not any(g["kind"] == "UNGRADED" for g in gaps):
            fails.append("arm 4b (all-common heading) -> graded on common words instead of UNGRADED")

        # arm 4c: a LATER prompt on the subject that is NOT a correction must not be listed;
        #         the same prompt with a correction signal must be. One condition, both directions.
        (t / "CLAUDE.md").write_text(RULE, encoding="utf-8")
        write_hist([{"timestamp": ms(2026, 9, 12),
                     "display": "remind me how the pii rule works for a public github repository"}])
        rc_q, _g, _ = audit(history=hist, root=t)
        write_hist([{"timestamp": ms(2026, 9, 12),
                     "display": "the pii rule for a public github repository is wrong"}])
        rc_c, _g2, _ = audit(history=hist, root=t)
        if rc_q != 0:
            fails.append(f"arm 4c question-not-correction -> rc={rc_q}, should be silent")
        if rc_c != 3:
            fails.append(f"arm 4c correction -> rc={rc_c}, should be a candidate")

        # arm 4d: a bullet with NO Jon quote is out of the population, not a silent pass --
        #         with only such bullets the file has an empty denominator and grades UNKNOWN.
        (t / "CLAUDE.md").write_text("- **Binaries live in Drive, not the repo, and pii and public "
                                     "github rules apply**" + NL
                                     + "  2026-08-09: gitignored." + NL, encoding="utf-8")
        write_hist([{"timestamp": ms(2026, 9, 12),
                     "display": "the pii rule for a public github repository is wrong"}])
        rc_np, _g3, st_np = audit(history=hist, root=t)
        if rc_np != 4:
            fails.append(f"arm 4d unquoted bullet -> rc={rc_np}, should be UNKNOWN empty population")

        # arm 5: missing history -> UNKNOWN, never clean
        (t / "CLAUDE.md").write_text(RULE, encoding="utf-8")
        rc, gaps, st = audit(history=t / "nope.jsonl", root=t)
        if rc != 4:
            fails.append(f"arm 5 (no history) -> rc={rc}")

        # arm 6: a file with no bullets -> UNKNOWN (empty denominator), never clean
        (t / "CLAUDE.md").write_text("# just prose" + NL, encoding="utf-8")
        rc, gaps, st = audit(history=hist, root=t)
        if rc != 4:
            fails.append(f"arm 6 (no bullets) -> rc={rc}")

    for f_ in fails:
        print("  FAIL " + f_)
    print(f"selftest: {9 - len(fails)}/9 arms passed")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
