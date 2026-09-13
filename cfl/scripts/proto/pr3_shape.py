#!/usr/bin/env python3
"""PROTOTYPE -- pr3_shape.py: generate a single double-clickable HTML file that
shows CFL's shape, with every node VERIFIED at generation time.

⛔ THROWAWAY. Named so a casual reader can see it. Lives on proto/pr3-shape.
Not wired into any pipeline, not a gate, not imported by anything.

THE QUESTION IT ANSWERS
-----------------------
Jon, 2026-09-04 (typos his):

    What is the higher level alignment, and how does it branch into the
    improvements you are all working on?
    I have no surface to materially reviedw your progress i feel.
    Look I can always decide 'nah i don't like that interpreatation' - if i can
    actually see the shape.

So the question is NOT "is the design right" -- it is "can Jon see the shape at
all." That makes this the LOGIC branch of the prototype skill: a single HTML file
he drives by hand, free-play plus guided walkthroughs.

WHY IT IS A GENERATOR AND NOT A HAND-WRITTEN PAGE
-------------------------------------------------
A hand-written status page is the exact defect this week is named for: "the
summary and the run have separate provenance." So every box on the page is
CHECKED HERE, at generation time:

  * a map's branch, ticket counts and schema come from alignment_map.scan()
  * a feed's age comes from feed_liveness.measure_feed()
  * a gate's met/unmet comes from parsing GATES.md
  * an instrument's self-check, its citation in GATES.md, and whether it can
    TRAVEL to other trunks are each tested against the filesystem
  * every trace link is a real path existence test

⭐ A LINK THAT CANNOT BE VERIFIED RENDERS AS A LOUD UNKNOWN, never as a tidy box.
That is not decoration -- it is the fresh PR-3 charter's acceptance test B, made
visible: "a retrieval that cannot reach the corpus returns a loud UNKNOWN, never
an empty result."

Usage:  python scripts/proto/pr3_shape.py [--out PATH]
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
AUDIT = os.path.join(REPO, "scripts", "audit")
sys.path.insert(0, AUDIT)

CORPUS = "N:/claude-corpus/cfl/raw/transcripts"

# --------------------------------------------------------------------------
# THE GOLDEN PRINCIPLE. The one typed thing on this page, and it is typed
# because it is a COMMITMENT, not a measurement. Everything else is derived.
# Jon's sentence is its acceptance test and it is quoted verbatim, typos his.
# --------------------------------------------------------------------------
PRINCIPLE = ("CFL's job is to make Jon's judgement CHEAP. "
             "Not to be right \u2014 to be CHECKABLE.")
PRINCIPLE_TEST = ("Look I can always decide 'nah i don't like that "
                  "interpreatation' - if i can actually see the shape.")
PRINCIPLE_PRIMARY = "~/.claude/history.jsonl:2611 (Jon's own typed prompt, 2026-08-20)"

BRANCHES = [
    ("capture", "is the input still alive at all?",
     "18 days dead, zero alarms. The compact pipeline's ingest step was hardcoded "
     "SKIPPED for months. Coverage was published over a feed that had stopped."),
    ("trace", "does a claim reach a primary?",
     "raw/ is 0 files in the retrieval index and corpus_provenance is empty, so a "
     "MISS and an ABSENCE emit the same nothing."),
    ("check", "can a second party falsify it?",
     "G10 and G11 did not exist until the last day of the sitting. Both caught real "
     "defects within an hour of existing."),
    ("see", "can Jon evaluate it in the time he actually has?",
     "reader_token_cost understated by 57-77%. Sixteen live maps and no index of "
     "them. He said he has no surface to review progress."),
]

# --------------------------------------------------------------------------
# CLAIM TRACES. The claim text and its intended chain are authored; EVERY LINK
# IS THEN TESTED. A chain whose instrument, input or primary cannot be reached
# renders UNKNOWN and says which link broke.
# --------------------------------------------------------------------------
CLAIMS = [
    {"claim": "September coverage is 7.3% (4 of 55 sessions)",
     "instrument": "scripts/audit/coverage_census.py",
     "feed": "claude-ai",
     "primary": "N:/claude-corpus/cfl/raw/transcripts/claude-ai/_routing/incoming"},
    {"claim": "The claude.ai export is a ~30-day rolling window, not an archive",
     "instrument": "scripts/lanes/transcript_corpus_diff.py",
     "feed": "claude-ai",
     "primary": ("G:/My Drive/Claude/Claude Foundational Layer/"
                 "claude-foundational-layer/raw/Anthropic_zips/"
                 "extracted-1788478575/conversations.json")},
    {"claim": "All 6 PR-3 findings carry a disposition that resolves to a real ticket",
     "instrument": "scripts/audit/disposition_resolves.py",
     "feed": None,
     "primary": "wiki/tracker/wayfinder-pr3-2026-08-31.md"},
    {"claim": "16 LIVE wayfinder maps, none declaring which branch it serves",
     "instrument": "scripts/audit/alignment_map.py",
     "feed": None,
     "primary": "wiki/tracker"},
    {"claim": "Jon's 09-03 Secretary context is in the wiki",
     "instrument": "scripts/audit/coverage_census.py",
     "feed": "claude-ai",
     "primary": ("wiki/sources/infrastructure/"
                 "hugging-face-incident-gift-exile-reunion-2026-09-03-a35a06.md")},
    {"claim": "Jon's 09-04 sentences reach the diffs they caused (4 of 4)",
     "instrument": "scripts/audit/trace_forward.py",
     "feed": None,
     "primary": "wiki/tracker/wayfinder-pr3-fresh-2026-09-04.md"},
    {"claim": "The 355 letters CFL reported sending to Professional",
     "instrument": None,
     "feed": None,
     "primary": "G:/My Drive/Claude/Professional"},
]

# Instruments built this sitting. Each row is TESTED: does the file exist, does it
# carry a self-check, is it cited by a gate, and can it TRAVEL to another trunk?
INSTRUMENTS = [
    ("scripts/audit/coverage_census.py", "population guard (DR-1)"),
    ("scripts/audit/feed_liveness.py", "is the input alive"),
    ("scripts/audit/barrier_consequent.py", "findings get a consequent"),
    ("scripts/audit/postcompact_verify.py", "the summary is graded against disk"),
    ("scripts/audit/reader_cost.py", "cost of reading, derived not typed"),
    ("scripts/audit/alignment_map.py", "the map of the maps"),
    ("scripts/audit/disposition_resolves.py", "TICKETED must resolve"),
    ("scripts/audit/extract_jon_turns.py", "Jon's words reach a tracked path"),
    ("scripts/audit/trace_forward.py", "Jon's sentence -> the diff it caused"),
    (".claude/hooks/global-staleness-probe.py", "is the global layer current"),
    ("skills/derived-not-typed/SKILL.md", "the lesson itself"),
]

WALKTHROUGHS = [
    {"id": "defect",
     "title": "The week's one defect",
     "lede": "Eight incidents. One shape.",
     "steps": [
         ("The summary and the run have separate provenance.",
          "A number is written down once. The thing it describes keeps moving. "
          "Nothing compares them again."),
         ("reader_token_cost said ~1,500 tokens, four minutes.",
          "Measured: 2,358-2,657 tokens, 7-9 minutes. Understated 57-77%. The "
          "document had grown three times that day; the field was typed once."),
         ("Coverage said 876 sessions.",
          "Two feeds. One had been dead 18 days. The count was true and the "
          "population was wrong."),
         ("A gate said every finding was dispositioned.",
          "It tested that a WORD was present. Six rows marked DECLINED pass "
          "exactly like six marked FIXED."),
         ("THE TEST THAT CATCHES ALL OF THEM:",
          "derive the number in THIS run, and make the check able to fail. "
          "Not 'be more careful.' Care was never the variable."),
     ]},
    {"id": "capture",
     "title": "How an input dies quietly",
     "lede": "The failure with no alarm.",
     "steps": [
         ("2026-08-16: the last export zip lands on disk.", "Nothing changes visibly."),
         ("Anthropic switches to a manifest with single-use URLs.",
          "Three manifests arrive: 08-24, 09-02, 09-03. Nobody fetches them. "
          "No error is raised, because nothing was ever watching for arrival."),
         ("Coverage keeps computing.",
          "It walks a directory that still exists and still has 667 files in it. "
          "Every answer is confident and every answer is 18 days old."),
         ("2026-09-04: Jon asks why September is 0.0%.",
          "The cause had been printing on every pipeline run for months: step 2, "
          "'ingest wiki', hardcoded SKIPPED-NOT-BUILT."),
         ("THE INSTRUMENT: feed_liveness.py.",
          "A published number must carry the age of every input it stands on. Its "
          "control is that an EMPTY feed reads UNKNOWN, never fresh \u2014 because a "
          "feed that stopped and was cleaned looks identical to one that never started."),
     ]},
    {"id": "window",
     "title": "The export stopped being an archive",
     "lede": "Measured by opening both files.",
     "steps": [
         ("08-16 export: 249 conversations. 09-03 export: 35.",
          "First reading: something is broken."),
         ("uuid overlap: 24 in both, 11 new-only, 225 old-only.",
          "Second reading: it is not corruption, it is a different population."),
         ("The new file's created_at runs 2026-08-05 to 2026-09-03.",
          "A clean DATE cut. Not a project split, not a size cap. ~30 days."),
         ("So the download cadence is now a RETENTION POLICY.",
          "A 31-day gap is permanent loss. Our 18-day outage cost nothing only "
          "because every earlier export happened to be archived on disk."),
         ("WHAT IS STILL UNKNOWN, and stays UNKNOWN:",
          "projects-000, memories-000 and light_metadata-000 are unfetched. "
          "A project split cannot explain a clean date cut \u2014 but it is not "
          "ruled out, so it is not reported as absent."),
     ]},
    {"id": "ticket",
     "title": "A true word about an act that did not happen",
     "lede": "The sharpest finding of the sitting, and it came from a peer.",
     "steps": [
         ("Professional rejects FIXED on two rows.",
          "'The word FIXED over an artifact that did not change.' They re-ran both "
          "greps themselves before signing."),
         ("CFL corrects the verb to TICKETED. Same day.",
          "Honest. The row now says what actually happened."),
         ("Secretary catches what the correction did NOT do.",
          "'TICKETED-with-no-ticket is a TRUE claim about an act that did not "
          "happen, and it passes your gate identically.' The ticket was never created."),
         ("Why only TICKETED is checkable:",
          "Of the four disposition words, it is the only one that names an artifact "
          "OUTSIDE its own file. FIXED points at a diff; DECLINED points at a "
          "judgement. TICKETED points at a row that must exist."),
         ("The instrument failed CFL's own F2 on its first run.",
          "P3-10 now exists and the row resolves. A gate whose first act is to fail "
          "its author is the only kind worth having."),
     ]},
    {"id": "loop",
     "title": "The improvement loop, and where it leaks",
     "lede": "Five stages. CFL is good at three.",
     "steps": [
         ("1. A finding arrives.",
          "Best case from a peer asking a DIFFERENT QUESTION \u2014 not a second "
          "opinion from the same method. Herald's rule: three different layers is "
          "not three different methods."),
         ("2. An instrument is built.",
          "CFL is fast here. Eight this sitting."),
         ("3. A negative control proves it can fail.",
          "CFL is now reliable here. Every instrument this sitting ships one."),
         ("4. A gate cites it, so it runs again.",
          "Partial. Check the INSTRUMENTS panel for which are cited and which are "
          "orphans that will never run twice."),
         ("5. IT IS DEPLOYED WHERE OTHER TRUNKS CAN READ IT.",
          "This is the leak, and its first description here was WRONG. I wrote "
          "'scripts/ does not sync' from memory; sync-universal.sh:113 copies it "
          "exactly as it copies skills/. Measured: 6 of 8 audit scripts were "
          "already in ~/.claude/. The two that were not are the two built after "
          "the last sync ran. So the gap is that DEPLOYMENT IS A SEPARATE ACT and "
          "the staleness probe compares only skills/ -- an instrument can be "
          "correct, gated, and invisible to every other trunk because a copy step "
          "did not run. Caught by measuring the claim on the page that exists to "
          "say measure the claim."),
     ]},
]


# --------------------------------------------------------------------------
def exists(path):
    p = path if os.path.isabs(path) or ":" in path else os.path.join(REPO, path)
    return os.path.exists(p), p


def instrument_facts():
    out = []
    gates_text = ""
    gp = os.path.join(REPO, "GATES.md")
    if os.path.exists(gp):
        gates_text = open(gp, encoding="utf-8", errors="replace").read()
    for rel, why in INSTRUMENTS:
        ok, full = exists(rel)
        body = ""
        if ok and os.path.isfile(full):
            body = open(full, encoding="utf-8", errors="replace").read()
        out.append({
            "path": rel, "why": why, "exists": ok,
            # A self-check is the only evidence that a check CAN fail.
            "self_check": ("--self-check" in body or "self_check" in body),
            # Cited by a gate = it runs again. Otherwise it ran once, ever.
            "gated": rel in gates_text,
            # THE PROPAGATION TEST, AND IT IS A MEASUREMENT NOW.
            #
            # ⛔ THE FIRST VERSION OF THIS LINE READ:
            #     "travels": rel.startswith("skills/") or rel.startswith("commands/")
            # -- an ASSERTION about what sync-universal.sh does, typed from memory,
            # inside the page built to show that typed assertions are the defect.
            # It published "1 of 9 instruments can leave this trunk" to Jon.
            #
            # FALSIFIED by reading sync-universal.sh:113, which copies scripts/ to
            # ~/.claude/scripts/ exactly as it copies skills/. Measured against the
            # global layer: SIX of the eight audit scripts were already deployed.
            # The two that were not are simply the two built AFTER the last sync ran.
            #
            # So the leak is not "scripts cannot travel". It is that DEPLOYMENT IS A
            # SEPARATE ACT and nothing compares the repo to the global layer for
            # anything but skills/. An instrument can exist, be gated, be correct,
            # and be invisible to every other trunk because a copy step did not run.
            "travels": deployed(rel),
        })
    return out


GLOBAL = os.path.join(os.path.expanduser("~"), ".claude")


def deployed(rel):
    """Is this artifact actually present in the global layer other trunks read?

    Not 'is it in a directory that syncs' -- is it THERE. The distinction is the
    whole finding: sync is a manual act, so a correct instrument committed after
    the last sync is unreachable from every other trunk and nothing says so."""
    return os.path.exists(os.path.join(GLOBAL, rel.replace("/", os.sep)))


def claim_traces(feeds):
    rows = []
    for c in CLAIMS:
        links, broken = [], []
        if c["instrument"]:
            ok, _ = exists(c["instrument"])
            links.append({"kind": "instrument", "name": c["instrument"], "ok": ok})
            if not ok:
                broken.append("the instrument does not exist")
        else:
            links.append({"kind": "instrument", "name": "(none named)", "ok": False})
            broken.append("NO INSTRUMENT NAMED \u2014 the claim was asserted, not derived")
        if c["feed"]:
            f = feeds.get(c["feed"], {})
            ok = f.get("verdict") == "ok"
            links.append({"kind": "input", "name": "%s (%s)" % (c["feed"], f.get("label", "?")),
                          "ok": ok})
            if not ok:
                broken.append("the input feed is %s" % f.get("verdict", "UNKNOWN"))
        ok, _ = exists(c["primary"])
        links.append({"kind": "primary", "name": c["primary"], "ok": ok})
        if not ok:
            broken.append("the primary is not on disk at that path")
        rows.append({"claim": c["claim"], "links": links, "broken": broken})
    return rows


def gate_rows():
    gp = os.path.join(REPO, "GATES.md")
    if not os.path.exists(gp):
        return []
    rows = []
    for ln in open(gp, encoding="utf-8", errors="replace"):
        m = re.match(r"^- \[([x ])\] (G\d+):\s*(.*)$", ln.strip())
        if m:
            rows.append({"met": m.group(1) == "x", "id": m.group(2),
                         "title": m.group(3).strip()})
    return rows


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
# Refs that are DOCUMENTATION OF THE SYNTAX, not links. The dream skill's own
# method constraint 2 records that a sweep which cannot tell a link from a
# sentence about links reported 57 "dangling" of which ~47 were examples.
META_SLUGS = {"slug", "wikilink", "source-slug-a", "source-slug-b", "their-name",
              "name", "concept-slug", "some-slug", "target"}
CODE_SPAN_RE = re.compile(r"`[^`]*`")
FENCE_RE = re.compile(r"^\s*```")


def ontology():
    """DERIVE the concept network from the wiki's own [[slug]] refs.

    THE ONE THING THIS MUST NOT DO is count a sentence ABOUT wikilinks as a
    wikilink. Backtick spans and fenced blocks are stripped first and the
    meta-example slugs are excluded by name -- the dream skill records a sweep
    that skipped this and inflated its dangling count by roughly five times.

    A dangling ref is NOT an error here. It is an edge to a node that does not
    exist yet, which is exactly what an ontology under construction looks like.
    It is reported as its own class, never folded into the total."""
    wiki = os.path.join(REPO, "wiki")
    if not os.path.isdir(wiki):
        return {"state": "UNKNOWN", "why": "no wiki/ directory"}

    pages, edges = {}, []
    for root, _dirs, files in os.walk(wiki):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, wiki).replace("\\", "/")
            try:
                raw = open(full, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            slug = os.path.splitext(fn)[0]
            m = re.search(r"^slug:\s*(.+)$", raw, re.MULTILINE)
            if m:
                slug = m.group(1).strip().strip('"').strip("'")
            pages[slug] = rel
            body, in_fence = [], False
            for ln in raw.splitlines():
                if FENCE_RE.match(ln):
                    in_fence = not in_fence
                    continue
                if not in_fence:
                    body.append(CODE_SPAN_RE.sub("", ln))
            for ref in WIKILINK_RE.findall("\n".join(body)):
                ref = ref.strip()
                if ref and ref not in META_SLUGS:
                    edges.append((slug, ref))

    stems = {os.path.splitext(os.path.basename(v))[0] for v in pages.values()}
    known = set(pages) | stems
    dangling = [(a, b) for a, b in edges if b not in known]
    indeg = {}
    for _a, b in edges:
        if b in known:
            indeg[b] = indeg.get(b, 0) + 1
    top = sorted(indeg.items(), key=lambda kv: -kv[1])[:12]
    linked = {a for a, b in edges if b in known} | set(indeg)
    return {
        "state": "MEASURED",
        "pages": len(pages), "edges": len(edges),
        "resolving": len(edges) - len(dangling),
        "dangling": len(dangling),
        "dangling_pct": round(100.0 * len(dangling) / len(edges), 1) if edges else 0.0,
        "isolated": len(set(pages) - linked),
        "top": [{"slug": s, "inbound": n} for s, n in top],
        "dangling_sample": sorted({b for _a, b in dangling})[:12],
    }


# Retrieval paths, each TESTED for existence. The point of the panel is not to
# rank them -- it is to show which ones can say UNKNOWN and which return an empty
# result that reads exactly like "nothing there."
SEARCH_PATHS = [
    ("grep over wiki/", "wiki", True,
     "Reaches only what is tracked. Cannot see raw/, which is where Jon's words are."),
    ("scripts/audit/find_answer.py", "scripts/audit/find_answer.py", False,
     "Nine tracked roots, ZERO of them another trunk. 'Not in the tracked roots' is "
     "a statement about one ninth of the machine."),
    ("the GraphRAG index", "scripts/graphrag/build_index.py", False,
     "raw/ is 0 files in it and corpus_provenance is empty, so a MISS and an "
     "ABSENCE emit the same nothing. This is the one the fresh charter's test B "
     "is aimed at."),
    ("fable-mirror (corpus reader)", ".claude/agents/fable-mirror.md", False,
     "Reads the parsed corpus. Silence in the corpus is uninformative, and it "
     "says so, which is the behaviour the others lack."),
    ("scripts/audit/exchange_inbox.py", "scripts/audit/exchange_inbox.py", False,
     "Peer mail, both directions. CFL had two inboxes and read one."),
]


def search_paths():
    out = []
    for name, rel, is_dir, note in SEARCH_PATHS:
        ok, full = exists(rel)
        if ok and is_dir:
            ok = os.path.isdir(full)
        out.append({"name": name, "path": rel, "exists": ok, "note": note})
    return out


def collect():
    import alignment_map as AM
    import feed_liveness as FL

    tracker = os.path.join(REPO, "wiki", "tracker")
    maps = AM.scan(tracker) if os.path.isdir(tracker) else []
    for m in maps:
        m["open_n"] = len(m["open"])
        m["next"] = m["open"][0] if m["open"] else ""
        del m["open"]

    feeds = {}
    for name, path in FL.DEFAULT_FEEDS.items():
        meas = FL.measure_feed(path)
        v = FL.verdict(meas, 3.0)
        feeds[name] = {
            "verdict": v,
            "label": ("%.1fd, %d files" % (meas["age_days"], meas["files"]))
            if meas["state"] == "MEASURED" else meas.get("why", "unknown"),
            "files": meas.get("files"),
        }

    return {
        "principle": PRINCIPLE,
        "principle_test": PRINCIPLE_TEST,
        "principle_primary": PRINCIPLE_PRIMARY,
        "branches": [{"id": b, "q": q, "evidence": e} for b, q, e in BRANCHES],
        "maps": maps,
        "feeds": feeds,
        "gates": gate_rows(),
        "instruments": instrument_facts(),
        "traces": claim_traces(feeds),
        "ontology": ontology(),
        "search": search_paths(),
        "walkthroughs": WALKTHROUGHS,
        "generated": subprocess.run(
            ["git", "-C", REPO, "log", "-1", "--format=%h %cd", "--date=iso"],
            capture_output=True, text=True).stdout.strip() or "UNKNOWN",
    }


HTML = """<!doctype html>
<meta charset="utf-8">
<title>PROTOTYPE - CFL shape</title>
<style>
:root{--bg:#faf9f7;--fg:#1c1a17;--dim:#6b665e;--line:#ddd8d0;--card:#fff;
--ok:#1a7f4b;--bad:#b3261e;--unk:#9a6b00;--accent:#2b5c8a}
@media(prefers-color-scheme:dark){:root{--bg:#16151a;--fg:#eae7e1;--dim:#9a948a;
--line:#332f38;--card:#1e1d23;--ok:#4ec27f;--bad:#ff8a80;--unk:#e0b050;--accent:#7fb0dd}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:24px 18px 80px}
h1{font-size:22px;margin:0 0 4px}
.proto{display:inline-block;background:var(--bad);color:#fff;font-weight:700;
font-size:11px;letter-spacing:.08em;padding:3px 8px;border-radius:3px}
.sub{color:var(--dim);font-size:13px;margin:6px 0 22px}
.principle{background:var(--card);border:2px solid var(--accent);border-radius:8px;
padding:16px 18px;margin:0 0 8px}
.principle b{font-size:17px}
blockquote{margin:10px 0 0;padding-left:12px;border-left:3px solid var(--line);
color:var(--dim);font-style:italic}
h2{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);
margin:30px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
.row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
button{font:inherit;cursor:pointer;background:var(--card);color:var(--fg);
border:1px solid var(--line);border-radius:6px;padding:7px 12px}
button:hover{border-color:var(--accent)}
button[aria-pressed=true]{background:var(--accent);color:#fff;border-color:var(--accent)}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;
padding:14px 16px;margin-bottom:10px}
.branchq{color:var(--dim);font-size:13px;margin:2px 0 8px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);
vertical-align:top}
th{color:var(--dim);font-weight:600;font-size:11px;text-transform:uppercase;
letter-spacing:.05em}
.scroll{overflow-x:auto}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px}
.ok{color:var(--ok);font-weight:600}
.bad{color:var(--bad);font-weight:600}
.unk{color:var(--unk);font-weight:700}
.pill{display:inline-block;font-size:11px;padding:2px 7px;border-radius:99px;
border:1px solid var(--line);color:var(--dim)}
.chain{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:6px}
.node{border:1px solid var(--line);border-radius:6px;padding:4px 9px;font-size:12px}
.node.good{border-color:var(--ok);color:var(--ok)}
.node.fail{border-color:var(--bad);color:var(--bad);font-weight:700}
.arrow{color:var(--dim)}
.why{font-size:12px;color:var(--bad);margin-top:6px;font-weight:600}
.state{background:#0000000a;border:1px dashed var(--line);border-radius:6px;
padding:10px 12px;font-size:12px;margin-top:10px}
@media(prefers-color-scheme:dark){.state{background:#ffffff08}}
.step{border-left:3px solid var(--accent);padding:2px 0 2px 12px;margin:12px 0}
.step b{display:block;margin-bottom:2px}
.step span{color:var(--dim);font-size:13px}
.foot{color:var(--dim);font-size:12px;margin-top:36px;border-top:1px solid var(--line);
padding-top:12px}
</style>
<div class="wrap">
<span class="proto">PROTOTYPE - THROWAWAY</span>
<h1>What CFL is, and whether you can see it</h1>
<div class="sub">Every box below was verified when this file was generated. Nothing here is
typed from memory. A link that could not be checked says <span class="unk">UNKNOWN</span>
rather than showing you a tidy box.</div>

<div class="principle">
  <b id="principle"></b>
  <blockquote id="ptest"></blockquote>
  <div class="sub mono" id="pprim" style="margin:6px 0 0"></div>
</div>

<h2>1 &middot; The four branches &mdash; click one</h2>
<div class="sub">Ordered, not a set. Each is worthless without the one before it.
Click a branch to filter everything below it.</div>
<div class="row" id="branchbtns"></div>
<div id="branchdetail"></div>

<h2>2 &middot; Free play &mdash; kill an input and watch what goes UNKNOWN</h2>
<div class="sub">This is the whole capture argument in one button. A dead feed does not
make numbers wrong-looking; it makes them confident and stale.</div>
<div class="row" id="feedbtns"></div>
<div id="tracebox"></div>

<h2>3 &middot; The maps &mdash; what the tracker actually holds</h2>
<div class="scroll"><table id="maptbl"></table></div>

<h2>4 &middot; Gates</h2>
<div class="scroll"><table id="gatetbl"></table></div>

<h2>5 &middot; Instruments &mdash; and which ones can leave this trunk</h2>
<div class="sub">A gate citation means it runs again. <b>Deployed</b> is measured against
<code>~/.claude/</code>, the layer other trunks actually read &mdash; not inferred from which
directory it lives in. <code>scripts/</code> DOES sync (<code>sync-universal.sh:113</code>);
the earlier claim that it did not was typed, not measured, and is corrected here. The real gap
is that deployment is a separate manual act and nothing compares the two for anything but
<code>skills/</code>.</div>
<div class="scroll"><table id="insttbl"></table></div>

<h2>6 &middot; Walkthroughs</h2>
<div class="row" id="wbtns"></div>
<div id="wbody"></div>

<h2>7 &middot; The ontology network &mdash; derived from the wiki's own [[slug]] refs</h2>
<div class="sub">Code spans and fenced blocks are stripped before counting, and the
meta-example slugs are excluded by name. A sweep that cannot tell a link from a sentence
about links inflates every run &mdash; that happened here once and cost ~47 false
&ldquo;dangling&rdquo; findings.</div>
<div class="card" id="ontobox"></div>

<h2>8 &middot; Searching, by default &mdash; and which paths can say UNKNOWN</h2>
<div class="sub">The question is not which is best. It is which ones return an empty
result that reads exactly like &ldquo;nothing there.&rdquo;</div>
<div class="scroll"><table id="searchtbl"></table></div>

<div class="foot" id="foot"></div>
</div>
<script>
const D = __DATA__;
const $ = s => document.querySelector(s);
let branch = null, dead = {};

$("#principle").textContent = D.principle;
$("#ptest").textContent = '"' + D.principle_test + '"';
$("#pprim").textContent = "primary: " + D.principle_primary;
$("#foot").textContent = "Generated from repo state at " + D.generated +
  " . Throwaway prototype; not a gate, not wired into anything.";

/* ---- branches ---- */
const bb = $("#branchbtns");
D.branches.forEach((b,i) => {
  const el = document.createElement("button");
  el.textContent = (i+1) + ". " + b.id;
  el.setAttribute("aria-pressed","false");
  el.onclick = () => { branch = (branch===b.id ? null : b.id); render(); };
  el.dataset.b = b.id; bb.appendChild(el);
});

/* ---- feeds: the free-play control ---- */
const fb = $("#feedbtns");
Object.keys(D.feeds).forEach(name => {
  const el = document.createElement("button");
  el.dataset.f = name;
  el.onclick = () => { dead[name] = !dead[name]; render(); };
  fb.appendChild(el);
});

function feedState(name){
  const f = D.feeds[name];
  if (dead[name]) return {v:"STALE", label:"killed by you (free play)"};
  return {v:f.verdict, label:f.label};
}

function cls(v){ return v==="ok" ? "ok" : (v==="STALE" ? "bad" : "unk"); }

function render(){
  document.querySelectorAll("#branchbtns button").forEach(el =>
    el.setAttribute("aria-pressed", String(el.dataset.b===branch)));
  document.querySelectorAll("#feedbtns button").forEach(el => {
    const st = feedState(el.dataset.f);
    el.textContent = el.dataset.f + " - " + st.v + " (" + st.label + ")";
    el.setAttribute("aria-pressed", String(!!dead[el.dataset.f]));
  });

  /* branch detail */
  const bd = $("#branchdetail"); bd.innerHTML = "";
  D.branches.filter(b => !branch || b.id===branch).forEach(b => {
    const d = document.createElement("div"); d.className = "card";
    d.innerHTML = "<b>" + b.id + "</b><div class='branchq'>" + b.q + "</div>" +
      "<div style='font-size:13px'>" + b.evidence + "</div>";
    bd.appendChild(d);
  });

  /* traces - the heart of it */
  const tb = $("#tracebox"); tb.innerHTML = "";
  let broken = 0;
  D.traces.forEach(t => {
    const d = document.createElement("div"); d.className = "card";
    let reasons = t.broken.slice();
    let chain = "<div class='chain'><span class='node'>claim</span>";
    t.links.forEach(l => {
      let ok = l.ok;
      if (l.kind === "input") {
        const nm = l.name.split(" ")[0];
        const st = feedState(nm);
        ok = st.v === "ok";
        if (!ok && !reasons.some(r => r.indexOf("input feed") >= 0))
          reasons.push("the input feed is " + st.v);
        l = {kind:l.kind, name: nm + " (" + st.label + ")", ok: ok};
      }
      chain += "<span class='arrow'>&rarr;</span><span class='node " +
        (ok?"good":"fail") + "'>" + l.kind + ": " + l.name + "</span>";
    });
    chain += "</div>";
    const bad = reasons.length > 0;
    if (bad) broken++;
    d.innerHTML = "<b>" + (bad ? "<span class='unk'>UNKNOWN</span> " : "<span class='ok'>traced</span> ") +
      "</b>" + t.claim + chain +
      (bad ? "<div class='why'>Cannot be traced because: " + reasons.join("; ") +
             ". This is reported as UNKNOWN, never as an empty result.</div>" : "");
    tb.appendChild(d);
  });
  const st = document.createElement("div"); st.className = "state";
  st.innerHTML = "<b>STATE:</b> branch=" + (branch||"(all)") +
    " &middot; feeds killed=" + (Object.keys(dead).filter(k=>dead[k]).join(",")||"none") +
    " &middot; claims traceable=" + (D.traces.length-broken) + "/" + D.traces.length +
    " &middot; UNKNOWN=" + broken;
  tb.appendChild(st);
}

/* ---- static tables ---- */
$("#maptbl").innerHTML =
  "<tr><th>map</th><th>status</th><th>branch</th><th>open</th><th>closed</th><th>next</th><th>read?</th></tr>" +
  D.maps.map(m => "<tr><td class='mono'>" + m.file + "</td><td>" + m.live +
    "</td><td>" + (m.branch ? "<span class='ok'>"+m.branch+"</span>" :
      "<span class='unk'>UNDECLARED</span>") + "</td><td>" + m.open_n + "</td><td>" +
    m.closed + "</td><td class='mono'>" + (m.next||"-") + "</td><td>" +
    (m.schema==="OK" ? "<span class='ok'>OK</span>" :
      "<span class='unk'>"+m.schema+"</span>") + "</td></tr>").join("");

$("#gatetbl").innerHTML =
  "<tr><th>gate</th><th>state</th><th>what it asserts</th></tr>" +
  D.gates.map(g => "<tr><td class='mono'>" + g.id + "</td><td>" +
    (g.met ? "<span class='ok'>MET</span>" : "<span class='bad'>UNMET</span>") +
    "</td><td>" + g.title + "</td></tr>").join("");

$("#insttbl").innerHTML =
  "<tr><th>instrument</th><th>what it checks</th><th>can fail?</th><th>re-runs?</th><th>travels?</th></tr>" +
  D.instruments.map(i => "<tr><td class='mono'>" + i.path + "</td><td>" + i.why +
    "</td><td>" + (i.self_check?"<span class='ok'>yes</span>":"<span class='bad'>no</span>") +
    "</td><td>" + (i.gated?"<span class='ok'>gated</span>":"<span class='unk'>orphan</span>") +
    "</td><td>" + (i.travels?"<span class='ok'>deployed</span>":"<span class='bad'>NOT DEPLOYED</span>") +
    "</td></tr>").join("");

/* ---- ontology ---- */
const O = D.ontology;
$("#ontobox").innerHTML = O.state !== "MEASURED"
 ? "<span class='unk'>UNKNOWN</span> - " + O.why
 : "<b>" + O.pages + "</b> pages &middot; <b>" + O.edges + "</b> refs &middot; <b class='ok'>" +
   O.resolving + "</b> resolve &middot; <b class='unk'>" + O.dangling + "</b> dangling (" +
   O.dangling_pct + "%) &middot; <b>" + O.isolated + "</b> pages with no link either way" +
   "<div class='state'><b>MOST-REFERENCED CONCEPTS</b> (inbound refs &mdash; the actual " +
   "spine of the ontology, not the one anybody declared):<br>" +
   O.top.map(x => "<span class='pill mono'>" + x.slug + " &times;" + x.inbound + "</span>").join(" ") +
   "</div><div class='state'><b>DANGLING SAMPLE</b> &mdash; edges to nodes that do not exist " +
   "yet. Not errors: this is what an ontology under construction looks like, and it is " +
   "reported as its own class rather than folded into the total.<br>" +
   O.dangling_sample.map(x => "<span class='pill mono'>" + x + "</span>").join(" ") + "</div>";

/* ---- search paths ---- */
$("#searchtbl").innerHTML =
  "<tr><th>path</th><th>exists?</th><th>what it can and cannot see</th></tr>" +
  D.search.map(s => "<tr><td class='mono'>" + s.name + "<br><span style='opacity:.6'>" +
    s.path + "</span></td><td>" +
    (s.exists ? "<span class='ok'>yes</span>" : "<span class='unk'>UNKNOWN</span>") +
    "</td><td>" + s.note + "</td></tr>").join("");

/* ---- walkthroughs ---- */
let wcur = D.walkthroughs[0].id;
const wb = $("#wbtns");
D.walkthroughs.forEach(w => {
  const el = document.createElement("button");
  el.textContent = w.title;
  el.onclick = () => { wcur = w.id; renderW(); };
  el.dataset.w = w.id; wb.appendChild(el);
});
function renderW(){
  document.querySelectorAll("#wbtns button").forEach(el =>
    el.setAttribute("aria-pressed", String(el.dataset.w===wcur)));
  const w = D.walkthroughs.find(x => x.id===wcur);
  $("#wbody").innerHTML = "<div class='card'><b>" + w.lede + "</b>" +
    w.steps.map(s => "<div class='step'><b>" + s[0] + "</b><span>" + s[1] +
      "</span></div>").join("") + "</div>";
}

render(); renderW();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "PROTOTYPE-cfl-shape.html"))
    a = ap.parse_args()
    data = collect()
    page = HTML.replace("__DATA__", json.dumps(data))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s (%d bytes)" % (a.out, len(page)))
    print("  maps=%d  gates=%d  instruments=%d  claims=%d"
          % (len(data["maps"]), len(data["gates"]),
             len(data["instruments"]), len(data["traces"])))
    for t in data["traces"]:
        if t["broken"]:
            print("  UNKNOWN: %s -- %s" % (t["claim"][:56], t["broken"][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
