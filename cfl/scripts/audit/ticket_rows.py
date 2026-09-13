#!/usr/bin/env python3
"""ticket_rows.py -- THE ONE ticket-row matcher for wayfinder maps (MI-13, 2026-09-06).

Three conventions exist in wiki/tracker/ and every instrument that grew up beside one of them
mis-reported the others as "no tickets":

  table    | **EAR-6** | ... | status cell | ...          (08-29 maps; alignment_map.py ROW_RE)
  bullet   - **MI-1 -- task -- UNCLAIMED -- title**        (09-05 maps; ticket_queried.py TICKET)
  heading  ## MI-13 -- task -- UNCLAIMED -- title          (09-05 maps, later sections; NEITHER parser)
           ### MI-17 -- task -- UNCLAIMED -- title

[measured 2026-09-06 06:5x] ticket_queried.py read 7 of 18 tickets on the memory-identity map -- the
map that carries MI-13 was invisible to the instrument that grades it, one section past the point
where its author switched from bullets to headings. alignment_map.py read the same map as
open=0 closed=0 [NO-TICKETS]. Both parsers were correct about the one shape they knew.

Interface, deliberately small:
    parse_tickets(text) -> [Row(id, form, status, closed, queried, line)]
`closed` is True only on an explicit closure word in the status text (table: the status cell;
bullet/heading: the words after the id, including strike-through of UNCLAIMED). Anything else --
including an empty status -- is OPEN. `queried` is True when a `queried:` field is attached to the
row (indented continuation for bullets; any line before the next heading for heading-form; a
`queried` column or cell text for tables).

Selftest plants one of each shape plus a decoy and asserts counts:  python ticket_rows.py --selftest
"""
import io
import re
import sys
from dataclasses import dataclass

ID = r"([A-Z][A-Z0-9]*-\d+[a-z]?)"
TABLE_RE = re.compile(r"^\|\s*\**" + ID + r"\**\s*\|")
BULLET_RE = re.compile(r"^-\s+\*\*" + ID + r"\b(.*)$")
HEADING_RE = re.compile(r"^#{1,6}\s+\**" + ID + r"\**\s*(?:—|--|-|:)\s*(.*)$")
ANY_HEADING = re.compile(r"^#{1,6}\s")
FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?`?queried`?\s*:", re.I)
CLOSED_RE = re.compile(r"\b(CLOSED|DONE|RESOLVED|LANDED|MERGED|WITHDRAWN|SUPERSEDED|FALSIFIED)\b")
STATUS_HDR_RE = re.compile(r"^(status|state|disposition|verdict)\b", re.I)


@dataclass
class Row:
    id: str
    form: str        # table | bullet | heading
    status: str      # raw status text the closure test ran on
    closed: bool
    queried: bool
    line: int        # 1-based line number of the row


def _cells(ln):
    return [c.strip() for c in ln.strip().strip("|").split("|")]


def parse_tickets(text):
    lines = text.splitlines()
    rows = []
    cur = None            # the bullet/heading row collecting continuation lines
    cur_form = None
    status_idx = None     # status column of the table currently being read
    queried_idx = None
    for n, ln in enumerate(lines, 1):
        # ---- table rows ----
        if ln.lstrip().startswith("|"):
            cells = _cells(ln)
            hdr = [i for i, c in enumerate(cells) if STATUS_HDR_RE.match(c.strip("*` "))]
            if hdr:
                status_idx = hdr[0]
                q = [i for i, c in enumerate(cells) if c.strip("*` ").lower().startswith("queried")]
                queried_idx = q[0] if q else None
                continue
            m = TABLE_RE.match(ln)
            if m:
                status = cells[status_idx] if status_idx is not None and status_idx < len(cells) else ""
                qcell = cells[queried_idx] if queried_idx is not None and queried_idx < len(cells) else ""
                rows.append(Row(m.group(1), "table", status, bool(CLOSED_RE.search(status)),
                                bool(qcell.strip()) or ("queried:" in ln.lower()), n))
            cur = None
            continue
        # ---- heading rows (a heading that IS a ticket) ----
        if ANY_HEADING.match(ln):
            m = HEADING_RE.match(ln)
            if m:
                status = m.group(2)
                cur = Row(m.group(1), "heading", status, bool(CLOSED_RE.search(status)), False, n)
                cur_form = "heading"
                rows.append(cur)
            else:
                cur = None
            continue
        # ---- bullet rows ----
        m = BULLET_RE.match(ln)
        if m:
            status = m.group(2)
            cur = Row(m.group(1), "bullet", status, bool(CLOSED_RE.search(status)), False, n)
            cur_form = "bullet"
            rows.append(cur)
            continue
        # ---- continuation: does a queried: field attach to the open row? ----
        if cur is None:
            continue
        if not ln.strip():
            continue
        if cur_form == "bullet" and not ln.startswith((" ", "\t")):
            # a non-indented non-bullet line ends a bullet's continuation -- but a bare
            # `queried:` line directly under a bullet still belongs to it (09-05 maps do this)
            if FIELD_RE.match(ln):
                cur.queried = True
            cur = None
            continue
        if FIELD_RE.match(ln):
            cur.queried = True
    # A closure on ANY row of an id closes every row of that id: the 09-05 maps open a ticket as a
    # bullet and resolve it later as a "## MI-1 -- RESOLVED" heading, leaving the bullet untouched.
    # [measured 2026-09-06] MI-1 and MI-9 read OPEN from their bullets and closed from their headings.
    closed_ids = {r.id for r in rows if r.closed}
    for r in rows:
        if r.id in closed_ids:
            r.closed = True
    return rows


def merged(text):
    """One Row per ticket id, in first-seen order: form/line from the first row, closed if ANY row is
    closed, queried if ANY row carries the field. The 09-05 maps mention a ticket as a bullet, again as
    a heading when partially answered, and again when resolved -- three rows, one ticket."""
    out = {}
    for r in parse_tickets(text):
        if r.id in out:
            out[r.id].closed = out[r.id].closed or r.closed
            out[r.id].queried = out[r.id].queried or r.queried
        else:
            out[r.id] = Row(r.id, r.form, r.status, r.closed, r.queried, r.line)
    return list(out.values())


def open_rows(text):
    return [r for r in merged(text) if not r.closed]


def self_test():
    fixture = """---
kind: wayfinder:map
status: LIVE
---

## Tickets

- **B-1 — task — UNCLAIMED — bullet with indented queried**
  queried: "x" -> a.py
- **B-2 — task — UNCLAIMED — bullet with bare queried line**
queried: "y" -> b.py
- **B-3 — task — ~~UNCLAIMED~~ FALSIFIED — struck bullet**
- **B-4 — task — UNCLAIMED — bullet with nothing**
- **B-5 — task — UNCLAIMED — bullet later resolved by a heading**

| ticket | status | queried | note |
|---|---|---|---|
| **T-1** | OPEN | q1 | table open with queried |
| **T-2** | CLOSED | | table closed |
| **T-3** | | | table empty status is OPEN |

## H-1 — task — UNCLAIMED — heading form
queried: "z" -> c.py
prose that is not a field
### H-2 -- task -- UNCLAIMED -- heading dashes, no queried
## H-3 — RESOLVED 2026-09-05. heading closed
## B-5 — RESOLVED 2026-09-06. closes the bullet above
## Not a ticket heading
- not a ticket bullet **X** either
"""
    rows = merged(fixture)
    got = {r.id: (r.form, r.closed, r.queried) for r in rows}
    want = {
        "B-1": ("bullet", False, True), "B-2": ("bullet", False, True),
        "B-3": ("bullet", True, False), "B-4": ("bullet", False, False), "B-5": ("bullet", True, False),
        "T-1": ("table", False, True), "T-2": ("table", True, False), "T-3": ("table", False, False),
        "H-1": ("heading", False, True), "H-2": ("heading", False, False), "H-3": ("heading", True, False),
    }
    fails = 0
    for k, v in want.items():
        ok = got.get(k) == v
        fails += 0 if ok else 1
        print(("PASS " if ok else "FAIL ") + f"{k}: got {got.get(k)} want {v}")
    extra = set(got) - set(want)
    ok = not extra
    fails += 0 if ok else 1
    print(("PASS " if ok else "FAIL ") + f"no decoys matched: {sorted(extra)}")
    n_open = len(open_rows(fixture))
    ok = n_open == 7
    fails += 0 if ok else 1
    print(("PASS " if ok else "FAIL ") + f"open rows = {n_open} (want 7)")
    print(f"selftest: {len(want) + 2 - fails}/{len(want) + 2}")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(self_test())
    for p in sys.argv[1:]:
        t = io.open(p, encoding="utf-8", errors="replace").read()
        rs = parse_tickets(t)
        print(f"{p}: {len(rs)} tickets, {len([r for r in rs if not r.closed])} open, "
              f"forms={sorted(set(r.form for r in rs))}")
        for r in rs:
            print(f"  {'closed' if r.closed else 'OPEN  '} {'q' if r.queried else '-'} {r.form:7s} {r.id}  L{r.line}")
