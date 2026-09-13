#!/usr/bin/env python3
"""render_mirror_verdicts.py -- make the fable-mirror's own rulings findable by a default query.

WHY THIS EXISTS. Jon, 2026-09-12, two questions in a row: *"Fable mirror. All of its logs in the
graph?"* then *"Fable mirror is a target for wiki skills improvement?"* The measured answer to the
first is NO, and it is the second question's answer too.

`[measured 2026-09-12 18:4x CDT, all trunks, by `agentType` in
~/.claude/projects/**/subagents/agent-*.meta.json]`

  fable-mirror consults, all time      293
  transcripts on disk                  293 of 293, 129,574,548 B
  transcript rows by tier              queue 135 | provenance 577 | KNOWLEDGE 0
  transcript rows with no searchable    354 of 712  (heading '(whole transcript)')
  agent-end renders in CFL's tree      134, median 36,060 B, all queue, 0 summary-only

⛔ SO THE VERDICTS WERE NEVER LOST -- THEY ARE THE WRONG GRAIN IN THE WRONG TIER. A 36 KB
whole-transcript render exists per consult and is fully searchable, in a tier no default query
touches. The part a later seat needs -- the verdict sentence and the Jon locator behind it -- had no
artifact of its own anywhere. 293 consults, and a seat asking "what did the mirror already rule on
this" could not find out by querying, in the channel whose entire purpose is to stop a seat writing
"no primary exists."

This writes ONE SMALL FILE PER CONSULT under `wiki/references/mirror-verdicts/`, which `tier_of()`
files as `knowledge` -- the tier retrieval searches by default.

⛔ THE HAZARD THIS SCRIPT IS BUILT AROUND, AND IT IS THE WHOLE REASON THE TEMPLATE IS WHAT IT IS.
Moving a verdict into the default scope moves a claim OUT OF THE CONTEXT THAT QUALIFIED IT and into
a place where it reads as settled. That is this program's characteristic failure applied to its own
consult channel. Two measured instances of why it matters: one consult tonight COULD NOT REACH THE
CORPUS ROOT (three grep timeouts) and said so; another on 2026-09-06 was permission-fenced out of
`history.jsonl` entirely and had to answer NONE-FOUND-BY-ME. A verdict rendered without those bounds
is a confident answer wearing a receipt. ⭐ So EVERY rendered file carries, above the verdict: the
consult's date, its own freshness/bound lines where they can be found, its transcript path, and an
explicit EXTRACTION GRADE.

✅ EXTRACTION GRADE, because 293 of these predate the contract that makes extraction reliable:
  DECLARED  -- the reply opens with a `VERDICT BLOCK` heading (the contract landed 2026-09-12 ~19:0x
               in `.claude/agents/fable-mirror.md`). The block is quoted as the mirror wrote it.
  DERIVED   -- no such heading; the head of the largest assistant text block is quoted instead.
               ⚠️ A DERIVED extract may quote reasoning rather than a conclusion. It is labelled so a
               reader discounts it, exactly as `ask_elder.py` labels a derived ancestor account WEAK.
  UNKNOWN   -- no assistant text block found at all. The file is still written, saying so, because a
               consult that produced nothing readable is itself a fact about the channel.

⛔ WRITES NOTHING OUTSIDE `wiki/references/mirror-verdicts/`. Never touches a transcript, never
touches `~/.claude/`, never deletes. Idempotent: re-running overwrites only files whose content
changed.

Usage:
  python scripts/graphrag/render_mirror_verdicts.py --selftest
  python scripts/graphrag/render_mirror_verdicts.py --dry-run
  python scripts/graphrag/render_mirror_verdicts.py
"""
import datetime
import glob
import json
import os
import re
import sys

OUT_REL = os.path.join("wiki", "references", "mirror-verdicts")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS = os.path.join(os.environ.get("USERPROFILE", ""), ".claude", "projects")
VERDICT_RE = re.compile(r"^\s*#{0,4}\s*VERDICT\s*BLOCK\b", re.I | re.M)
STAMP_RE = re.compile(r"^.*(freshness|corpus (root|at)|UNREACHABLE|NONE-FOUND|not measured by me|"
                      r"RELAYED|newest).*$", re.I | re.M)
HEAD_CHARS = 2400


def _reconfig():
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass


def mirror_runs(projects=PROJECTS):
    """Every fable-mirror consult, by the AUTHORITATIVE field, not by a name match.

    ⛔ A first version of this census counted transcripts whose text contains the string
    'fable-mirror' and got 1,639 of 2,144 -- wrong by 5.6x, because that string is in the
    available-agents list of EVERY subagent's system prompt. It counted subagents that COULD have
    called the mirror. `meta.json`'s `agentType` is the field that means what it says.
    """
    out = []
    for m in glob.glob(os.path.join(projects, "**", "subagents", "agent-*.meta.json"),
                       recursive=True):
        try:
            d = json.load(open(m, encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if d.get("agentType") != "fable-mirror":
            continue
        j = m[: -len(".meta.json")] + ".jsonl"
        out.append({"agent": os.path.basename(m)[len("agent-"):-len(".meta.json")],
                    "jsonl": j,
                    "desc": d.get("description") or "",
                    "trunk": m.split(os.sep + "projects" + os.sep)[-1].split(os.sep)[0]
                    if os.sep + "projects" + os.sep in m else "UNKNOWN"})
    return sorted(out, key=lambda r: r["agent"])


def extract(jsonl):
    """-> (grade, text, stamp_lines, when).  Reads the transcript; writes nothing."""
    blocks = []
    when = None
    if not os.path.isfile(jsonl):
        return "UNKNOWN", "", [], None
    for line in open(jsonl, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        when = when or d.get("timestamp")
        msg = d.get("message") or {}
        if d.get("type") == "assistant" and isinstance(msg.get("content"), list):
            for c in msg["content"]:
                if c.get("type") == "text" and len(c.get("text", "")) > 200:
                    blocks.append(c["text"])
    if not blocks:
        return "UNKNOWN", "", [], when
    declared = [b for b in blocks if VERDICT_RE.search(b[:600])]
    if declared:
        return "DECLARED", declared[0][:HEAD_CHARS], STAMP_RE.findall(declared[0])[:0], when
    big = max(blocks, key=len)
    stamps = [m.group(0).strip() for m in STAMP_RE.finditer(big)][:4]
    return "DERIVED", big[:HEAD_CHARS], stamps, when


def page(run, grade, text, stamps, when):
    d = (when or "")[:10] or "unknown-date"
    hdr = [
        "---",
        'kind: mirror-verdict',
        'slug: "mirror-verdict-%s"' % run["agent"][:9],
        'consulted: "%s"' % (when or "UNKNOWN"),
        'agent: "%s"' % run["agent"],
        'trunk_of_caller: "%s"' % run["trunk"],
        'extraction: %s' % grade,
        'transcript: "%s"' % run["jsonl"].replace("\\", "/"),
        'reader_token_cost: "~700 tokens; this is an EXTRACT, the transcript is the record"',
        "---",
        "",
        "# Mirror verdict %s — %s" % (run["agent"][:9], run["desc"] or "(no description recorded)"),
        "",
        "⛔ **THIS IS AN EXTRACT OF A PAST JUDGMENT, RENDERED SO IT CAN BE FOUND. IT IS NOT A CURRENT"
        " RULING AND IT IS NOT A JON PRIMARY.** The mirror ratifies nothing and flips no status; a"
        " verdict here is one reading of the corpus **as that consult could reach it on %s**, which"
        " is not how it is reachable now." % d,
        "",
        "⚠️ **EXTRACTION GRADE: %s.**" % grade,
    ]
    if grade == "DERIVED":
        hdr.append("  ⛔ **No `VERDICT BLOCK` heading existed in this reply** — the contract requiring"
                   " one landed 2026-09-12 ~19:0x, and this consult predates it. What follows is the"
                   " HEAD OF THE LONGEST REPLY BLOCK and **may be reasoning rather than a"
                   " conclusion.** Discount it accordingly and open the transcript before relying.")
    elif grade == "UNKNOWN":
        hdr.append("  ⛔ **No assistant text block over 200 characters was found in this transcript.**"
                   " Nothing is quoted below. That a consult produced nothing readable is itself a"
                   " fact about this channel, which is why the file exists rather than being skipped.")
    else:
        hdr.append("  ✅ The reply opened with a `VERDICT BLOCK`, so the block below is quoted as the"
                   " mirror wrote it, in the shape the contract requires: verdict word, deciding"
                   " sentence, and Jon locators as `file:line` with dates.")
    if stamps:
        hdr += ["", "## The bounds this consult put on itself (quoted from its own reply)", ""]
        hdr += ["- " + s for s in stamps]
        hdr += ["", "⭐ **A verdict separated from these lines reads as settled when it was not.**"]
    else:
        hdr += ["", "⚠️ **No freshness or reachability line could be located in this reply.** That is"
                " UNKNOWN, not clean — treat the verdict's corpus coverage as unstated."]
    hdr += ["", "## Verdict as extracted", ""]
    body = text.strip() or "(nothing extractable — see the grade above)"
    hdr += ["> " + ln if ln.strip() else ">" for ln in body.splitlines()]
    hdr += ["", "---", "", "**The transcript is the record and this file is a pointer to it:**",
            "`%s`" % run["jsonl"].replace("\\", "/"), ""]
    return "\n".join(hdr) + "\n"


def run(dry=False, limit=None, all_grades=False):
    """⛔ DECLARED-ONLY BY DEFAULT, AND THE DRY RUN IS WHY -- this is a decision reversed by its own
    measurement, recorded here rather than quietly taken.

    I committed to Jon that I would "render the mirror's verdict blocks into the default-searchable
    tier." Then the dry run said what the corpus actually contains:

        `[measured 2026-09-12 19:06]`  295 consults -> DECLARED 1 | DERIVED 273 | UNKNOWN 21

    ⭐ So 273 of 295 are NOT verdict blocks. Writing them all would put 273 extracts that "may be
    reasoning rather than a conclusion" into the knowledge tier -- which is a 6% enlargement of the
    4,535-file default scope with material of UNKNOWN conclusiveness. That is precisely the haystack
    the tier exists to prevent, arriving through the door I opened to fix a coverage gap. The same
    trade the RS-7 lane refused for `history.jsonl` four hours ago, and I would have made it here
    without the dry run.

    ✅ So: DECLARED only. The scope grows one file per future consult, because the contract landed
    tonight makes every new reply DECLARED. `--all-grades` renders the DERIVED and UNKNOWN ones for
    anyone who decides the coverage is worth the noise -- the escape hatch exists, it is just not the
    default, and a reader of the count knows which they are looking at.
    ⚠️ The 273 DERIVED consults are NOT unreachable: their whole transcripts are already indexed in
    `queue`/`provenance` and their agent-end renders are fully searchable one flag away. Nothing is
    being hidden; only the DEFAULT scope is being kept precise.
    """
    _reconfig()
    outdir = os.path.join(REPO, OUT_REL)
    runs = mirror_runs()
    if limit:
        runs = runs[:limit]
    print("=== RENDER MIRROR VERDICTS ===")
    print("  consults found (agentType) : %d" % len(runs))
    print("  out dir                    : %s  (tier_of -> knowledge, the DEFAULT scope)" % outdir)
    if not dry:
        os.makedirs(outdir, exist_ok=True)
    grades = {"DECLARED": 0, "DERIVED": 0, "UNKNOWN": 0}
    wrote = same = 0
    skipped = 0
    for r in runs:
        g, txt, stamps, when = extract(r["jsonl"])
        grades[g] += 1
        if g != "DECLARED" and not all_grades:
            skipped += 1
            continue
        content = page(r, g, txt, stamps, when)
        dest = os.path.join(outdir, "mirror-verdict-%s.md" % r["agent"][:9])
        if dry:
            continue
        old = None
        if os.path.isfile(dest):
            old = open(dest, encoding="utf-8", errors="replace").read()
        if old == content:
            same += 1
        else:
            open(dest, "w", encoding="utf-8", newline="\n").write(content)
            wrote += 1
    print("  grades                     : DECLARED %d | DERIVED %d | UNKNOWN %d"
          % (grades["DECLARED"], grades["DERIVED"], grades["UNKNOWN"]))
    print("  written %d | unchanged %d%s" % (wrote, same, "  (DRY RUN -- nothing written)" if dry else ""))
    print("  ⚠️ DERIVED dominates by construction: every consult before 2026-09-12 ~19:0x predates")
    print("     the verdict-block contract, so its extract may be reasoning, not a conclusion.")
    return 0


def selftest():
    _reconfig()
    import tempfile
    ok = fail = 0

    def chk(name, cond):
        nonlocal ok, fail
        print(("PASS " if cond else "FAIL ") + name)
        if cond:
            ok += 1
        else:
            fail += 1

    tmp = tempfile.mkdtemp()
    proj = os.path.join(tmp, "projects", "T--trunk", "sess", "subagents")
    os.makedirs(proj)

    def mk(aid, atype, texts):
        json.dump({"agentType": atype, "description": "d-" + aid},
                  open(os.path.join(proj, "agent-%s.meta.json" % aid), "w", encoding="utf-8"))
        with open(os.path.join(proj, "agent-%s.jsonl" % aid), "w", encoding="utf-8") as f:
            for t in texts:
                f.write(json.dumps({"type": "assistant", "timestamp": "2026-09-12T00:00:00Z",
                                    "message": {"content": [{"type": "text", "text": t}]}}) + "\n")

    mk("a1", "fable-mirror", ["## VERDICT BLOCK\nCONTINUE because X\nFreshness: corpus REACHABLE\n" + "z" * 300])
    mk("a2", "fable-mirror", ["y" * 400, "Freshness stamp: corpus UNREACHABLE at root\n" + "w" * 900])
    mk("a3", "general-purpose", ["## VERDICT BLOCK\nnot a mirror run\n" + "q" * 300])
    mk("a4", "fable-mirror", [])
    runs = mirror_runs(os.path.join(tmp, "projects"))
    chk("census uses agentType, not a name match (3 mirror runs, general-purpose excluded)",
        len(runs) == 3 and all(r["agent"] != "a3" for r in runs))
    by = {r["agent"]: r for r in runs}
    g1, t1, s1, _ = extract(by["a1"]["jsonl"])
    chk("a VERDICT BLOCK heading grades DECLARED", g1 == "DECLARED")
    chk("DECLARED quotes the block, not the longest text", "CONTINUE because X" in t1)
    g2, t2, s2, _ = extract(by["a2"]["jsonl"])
    chk("no heading grades DERIVED (negative arm)", g2 == "DERIVED")
    chk("DERIVED carries the consult's own bound line", any("UNREACHABLE" in s for s in s2))
    g4, t4, s4, _ = extract(by["a4"]["jsonl"])
    chk("an empty transcript grades UNKNOWN, never DECLARED (negative arm)", g4 == "UNKNOWN")
    p = page(by["a2"], g2, t2, s2, "2026-09-12T00:00:00Z")
    chk("a DERIVED page says it may be reasoning rather than a conclusion",
        "may be reasoning" in p.lower() or "may be reasoning rather than a conclusion" in p)
    chk("every page states it is NOT a current ruling and NOT a Jon primary",
        "NOT A CURRENT" in p.upper() and "JON PRIMARY" in p.upper())
    p4 = page(by["a4"], g4, t4, s4, None)
    chk("an UNKNOWN page is still written and says why (no silent skip)",
        "nothing readable" in p4.lower() or "No assistant text block" in p4)
    chk("output path lands in the knowledge tier (not wiki/intake-triage, not raw/)",
        OUT_REL.startswith("wiki" + os.sep + "references"))
    print("\n%d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run(dry="--dry-run" in sys.argv))
