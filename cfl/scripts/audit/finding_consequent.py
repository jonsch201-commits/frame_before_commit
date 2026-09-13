#!/usr/bin/env python3
"""finding_consequent.py — CB-3. Give postcompact_verify.py's findings a consequent.

THE TICKET, verbatim from wiki/tracker/wayfinder-compact-barrier-2026-09-04.md:
  "Give postcompact_verify.py a consequent. Today it emitted 12 findings and nothing consumed
   them. Decide the minimum honest one: does each finding become a ticket row, a wiki candidate,
   or an exit code that blocks the next dispatch?"
  And the map's own note: "The verifier caught it, reported it, and NOTHING CHANGED as a result.
   A finding with no consequent is a log line."

THE DECISION, and the reasoning is the deliverable:

  NOT an exit code that blocks the next dispatch. A verifier fault would then wedge every lane in
  the fleet over an infra bug rather than a policy decision -- the same reasoning that keeps
  py_closed.sh's --block opt-in and off Stop/SessionEnd. ⛔ A consequent that can halt the program
  is not the MINIMUM one.

  NOT a wiki candidate per finding. C2 ("branch not named in the summary") recurs at EVERY compact
  until fixed; one page per occurrence would bury the wiki in 60 copies of one sentence.

  ⭐ A DURABLE, DEDUPLICATED LEDGER ROW WITH A STATE, whose OPEN count is printed where somebody
  already looks. That is the smallest thing that makes an unconsumed finding COUNTABLE instead of
  invisible, and it is the whole gap the map names.

DEDUP IS THE LOAD-BEARING PART, not a nicety. A finding recurs every compact until fixed, so an
accumulating log would report 60 open findings that are one open finding -- a number that is
technically true and operationally a lie. Rows are keyed on (check_code, detail), NOT on the
timestamp, so a recurrence updates last_seen and n_seen and never adds a row.

⛔ NOTHING HERE DELETES. States move; rows stay (Jon: "Yeah no deletion").

  finding_consequent.py                  # ingest newest verdicts, print the OPEN table
  finding_consequent.py --count          # one integer: OPEN rows (for the gate line)
  finding_consequent.py --all            # ingest EVERY verdict file on disk, not just new ones
  finding_consequent.py --close CODE --reason "..."   # move a row to CLOSED, with a reason
  finding_consequent.py --self-test
"""
import argparse
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))          # .../scripts/audit
_SCRIPTS = os.path.dirname(_HERE)                            # .../scripts
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(_SCRIPTS)

VERDICT_DIR = os.path.join(ROOT, "exchange", "su-close", "postcompact")
LEDGER = os.path.join(ROOT, "exchange", "su-close", "FINDINGS-LEDGER.jsonl")

# "- C2 branch: current branch `x` NOT named in the summary"
FINDING_RE = re.compile(r"^\s*-\s+([A-Z]\d+)\s+([^:]{1,40}):\s*(.+?)\s*$")
HDR_RE = re.compile(r"^###\s+Findings\b", re.IGNORECASE)
NEXT_HDR_RE = re.compile(r"^#{1,6}\s+")


def parse_findings(text):
    """Findings ONLY from under the '### Findings' heading.

    ⛔ Scanning the whole file would swallow the '### Checks run' bullets, which describe checks
    that PASSED -- turning every clean run into findings. That is the same defect class as a
    matcher that reads its own author's idiom: the bug is in what the pattern REACHES, never in
    the pattern itself.
    """
    out, inside = [], False
    for line in text.splitlines():
        if HDR_RE.match(line):
            inside = True
            continue
        if inside and NEXT_HDR_RE.match(line):
            break
        if inside:
            m = FINDING_RE.match(line)
            if m:
                out.append((m.group(1), m.group(2).strip(), m.group(3).strip()))
    return out


def load_ledger():
    rows = {}
    if not os.path.isfile(LEDGER):
        return rows
    with io.open(LEDGER, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            rows[r.get("key")] = r          # append-only file, last write wins
    return rows


def append(row):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with io.open(LEDGER, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def key_of(code, detail):
    # the timestamp is deliberately NOT in the key -- see DEDUP note in the docstring
    return "%s|%s" % (code, re.sub(r"`[^`]*`", "`*`", detail)[:160])


def ingest(only_new=True):
    if not os.path.isdir(VERDICT_DIR):
        return 0, 0, "no verdict dir at %s" % VERDICT_DIR
    rows = load_ledger()
    files = sorted(f for f in os.listdir(VERDICT_DIR) if f.endswith(".md"))
    if only_new:
        seen_files = {r.get("last_file") for r in rows.values()}
        files = files[-5:] if not seen_files else [f for f in files if f not in seen_files][-25:] or files[-1:]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new = upd = 0
    for fn in files:
        try:
            txt = io.open(os.path.join(VERDICT_DIR, fn), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for code, label, detail in parse_findings(txt):
            k = key_of(code, detail)
            if k in rows:
                r = rows[k]
                # ⛔ n_seen COUNTED THIS SCRIPT'S OWN RUNS, not occurrences. Measured 2026-09-04
                # 21:3x: three invocations took one finding from 165 to 585 while reporting
                # "0 new" -- re-reading the same verdict files re-incremented every key. The
                # DISTINCT count (the number the gate line prints) stayed correct throughout,
                # but n_seen had become a measure of how often I looked. Same class as the
                # substring scan that counted this session's own transcript: an instrument
                # measuring its own activity and reporting it as evidence about the world.
                # A finding is now counted ONCE PER VERDICT FILE it actually appears in.
                if r.get("state") == "OPEN" and fn not in (r.get("seen_files") or []):
                    sf = list(r.get("seen_files") or [])
                    sf.append(fn)
                    r["seen_files"] = sf[-200:]      # bounded; nothing is deleted from the ledger
                    r["n_seen"] = len(sf)
                    r["last_seen"] = now
                    r["last_file"] = fn
                    append(r); upd += 1
            else:
                r = {"key": k, "code": code, "label": label, "detail": detail,
                     "state": "OPEN", "first_seen": now, "last_seen": now,
                     "n_seen": 1, "seen_files": [fn], "last_file": fn}
                rows[k] = r
                append(r); new += 1
    return new, upd, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", action="store_true", help="print one integer: OPEN rows")
    ap.add_argument("--all", action="store_true", help="ingest every verdict file, not just new")
    ap.add_argument("--close", metavar="CODE")
    ap.add_argument("--reason", default="")
    ap.add_argument("--match", default="", help="substring of the finding detail, to "
                    "disambiguate when several OPEN rows share a code")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    if a.close:
        if not a.reason.strip():
            print("REFUSED: --close needs --reason. A state change with no reason is the "
                  "undispositioned-deferral defect wearing a green.")
            return 2
        rows = load_ledger()
        hit = [r for r in rows.values() if r.get("code") == a.close and r.get("state") == "OPEN"]
        if a.match:
            hit = [r for r in hit if a.match.lower() in (r.get("detail") or "").lower()]
        if not hit:
            print("no OPEN row with code %s%s" % (a.close, " matching %r" % a.match if a.match else ""))
            return 1
        # ⛔ REFUSE A BLIND BULK CLOSE. Two of the four real findings tonight were both `C1` with
        # DIFFERENT details -- one genuinely fixed, one merely informational. Closing by code alone
        # would have dispositioned both on the evidence for one, which is the "tidy the board"
        # failure the no-reason refusal above already guards against, wearing a different shape.
        if len(hit) > 1 and not a.match:
            print("REFUSED: %d OPEN rows share code %s. Disambiguate with --match <substring>:"
                  % (len(hit), a.close))
            for r in hit:
                print("   - %s" % (r.get("detail") or "")[:100])
            return 2
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for r in hit:
            r = dict(r)
            r["state"] = "CLOSED"
            r["closed_at"] = now
            r["closed_reason"] = a.reason.strip()
            append(r)
        print("closed %d row(s) for %s" % (len(hit), a.close))
        return 0

    new, upd, err = ingest(only_new=not a.all)
    rows = load_ledger()
    open_rows = [r for r in rows.values() if r.get("state") == "OPEN"]
    if a.count:
        # ⛔ THIS RETURNED A CLEAN `0` WHEN THE VERDICT DIR DID NOT EXIST -- measured on this
        # script's own first real run, 2026-09-04. Secretary's rule, already quoted at the top of
        # postcompact_pipeline.py: never render missing bytes as a clean zero. A caller reading
        # `0` cannot tell "no open findings" from "I could not look", and the gate line that
        # consumes this would have printed a green derived from an error.
        if err:
            print("UNKNOWN", file=sys.stderr)
            print("UNKNOWN")
            return 1
        print(len(open_rows))
        return 0
    print("=== FINDING CONSEQUENT (CB-3) === a finding with no consequent is a log line")
    if err:
        print("  UNKNOWN -- %s" % err)
        return 1
    print("  ingested: %d new, %d recurrences\n" % (new, upd))
    if not open_rows:
        print("  0 OPEN findings. (Distinct findings, deduplicated -- not a count of log lines.)")
    for r in sorted(open_rows, key=lambda x: (-int(x.get("n_seen", 1)), x.get("code", ""))):
        print("  OPEN  %-4s x%-3d %s" % (r.get("code"), r.get("n_seen", 1), r.get("detail", "")[:90]))
    print("\n  %d OPEN, %d total tracked. Close with --close CODE --reason '...'"
          % (len(open_rows), len(rows)))
    return 0


def self_test():
    import tempfile
    global VERDICT_DIR, LEDGER
    print("=== SELF-TEST -- finding_consequent ===")
    np = nf = 0

    def ok(name, got, want):
        nonlocal np, nf
        if got == want:
            np += 1; print("  PASS  %s" % name)
        else:
            nf += 1; print("  FAIL  %s\n        want: %r\n        got : %r" % (name, want, got))

    doc = (
        "# header\n\n## VERDICT: FINDINGS (2)\n\n### Findings\n\n"
        "- C2 branch: current branch `week-x` NOT named in the summary\n"
        "- C1 live-map: 3 LIVE maps absent from the summary\n\n"
        "### Checks run\n\n"
        "- C3 spine: WAKE names no spine (nothing to check)\n"
        "- C4 quotes: no >=25-char quoted spans\n"
    )
    f = parse_findings(doc)
    # 1 findings come ONLY from under the Findings heading
    ok("1 parses exactly the 2 real findings", len(f), 2)
    # 2 NEGATIVE CONTROL: 'Checks run' bullets are not findings
    ok("2 'Checks run' bullets excluded", [c for c, _l, _d in f], ["C2", "C1"])
    # 3 a clean verdict yields nothing
    ok("3 no Findings heading -> 0", len(parse_findings("## VERDICT: CHECKED\n\n### Checks run\n- C1 x: ok\n")), 0)
    # 4 DEDUP: the same finding with a different backticked value is ONE key
    k1 = key_of("C2", "current branch `week-a` NOT named in the summary")
    k2 = key_of("C2", "current branch `week-b` NOT named in the summary")
    ok("4 dedup ignores backticked values", k1, k2)
    # 5 NEGATIVE CONTROL for 4 -- genuinely different findings stay distinct
    ok("5 different detail -> different key",
       key_of("C2", "branch missing") != key_of("C1", "branch missing"), True)

    d = tempfile.mkdtemp()
    VERDICT_DIR = os.path.join(d, "v"); os.makedirs(VERDICT_DIR)
    LEDGER = os.path.join(d, "L.jsonl")
    io.open(os.path.join(VERDICT_DIR, "a.md"), "w", encoding="utf-8").write(doc)
    ingest(only_new=False)
    ok("6 two OPEN rows after ingest", len([r for r in load_ledger().values() if r["state"] == "OPEN"]), 2)
    # 7 THE ONE THAT MATTERS: a recurrence must not create a second row
    io.open(os.path.join(VERDICT_DIR, "b.md"), "w", encoding="utf-8").write(doc)
    ingest(only_new=False)
    rows = load_ledger()
    ok("7 recurrence updates, never adds", len(rows), 2)
    ok("8 recurrence counted (n_seen>1)", max(int(r["n_seen"]) for r in rows.values()) > 1, True)
    # 9 closing is durable and the row is KEPT, never removed
    r = dict([x for x in rows.values() if x["code"] == "C2"][0])
    r.update(state="CLOSED", closed_reason="fixed in the summary template")
    append(r)
    rows2 = load_ledger()
    ok("9 closed row still present (no deletion)", len(rows2), 2)
    ok("10 OPEN count drops to 1", len([x for x in rows2.values() if x["state"] == "OPEN"]), 1)
    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
