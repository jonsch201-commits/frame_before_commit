#!/usr/bin/env python3
"""issuance_check.py — did the act reach the intended user's tree, or only my outbox?

THE RULE THIS MECHANISM EXISTS FOR (Professional, 2026-09-07, answering Secretary's co-review ask):

    A MATERIAL act is complete when its artifact exists at the destination the intended user
    reads, in the form the standard names, and a seat other than its author can verify both.

"Reached the intended user" is NOT checkable when the user is Jon -- no instrument on this machine
reports whether a person read a file. So the observable is a DESTINATION, never a mind. That is
ASOP 41's own division of responsibility: the actuary is responsible for ISSUING the communication,
not for the reader's comprehension.

TWO DEFECTS THIS IS SHAPED AROUND, both measured on 2026-09-07, both by seats that were at that
moment grading the other for it:

  1. THE GLOB THAT CANNOT EXPRESS A RECIPIENT. Secretary counted ECHOED receipts with `/n/claude-*`,
     which cannot match `antigravity-hub` IN PRINCIPLE -- so the number it returned was one no run
     of that instrument could ever have got right. Here: recipients come from an ENUMERATED ROSTER,
     never from a pattern over directory names.

  2. THE DEPTH THAT CANNOT REACH A RECIPIENT. Professional counted the same receipts with
     `find -maxdepth 3` and got 5 of 7, because `claude-cfl/clone/exchange/` is at depth 4. Here:
     each roster row names its inbound directory OUTRIGHT. Selftest case D is the control that
     keeps this honest -- a deep recipient must still be found.

AND THE FAILURE THAT LOOKS LIKE SUCCESS: a write that CREATES its own destination. If a recipient's
inbound directory does not exist, that is NO-DESTINATION -- never a pass, and never silently a
delivery. The constitution says it outright: "VERIFY THE TARGET BEFORE YOU DEPOSIT -- a write that
creates its own destination looks like delivery."

Exit codes: 0 = every recipient holds a byte-identical copy. 3 = at least one does not.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def read_roster(p: Path) -> list[tuple[str, Path]]:
    """name<TAB>inbound-directory, one per line. ENUMERATED, never globbed.

    A roster row is a claim that a recipient exists and where it reads. Comments (#) and blank
    lines are skipped; a row with no tab is a malformed roster and raises rather than being
    silently dropped -- a dropped recipient is exactly the silent-no-match this file exists for.
    """
    rows: list[tuple[str, Path]] = []
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError(f"{p}:{i}: roster row has no tab separator: {line!r}")
        name, _, inbound = line.partition("\t")
        rows.append((name.strip(), Path(inbound.strip())))
    return rows


def check(draft: Path, roster: list[tuple[str, Path]]):
    """Return (results, ok). One row per recipient; ok is True only if every row DELIVERED."""
    want = digest(draft)
    name_of = draft.name
    results = []
    for name, inbound in roster:
        # A ROSTER PATH IN THE WRONG FORM IS NOT A MISSING RECIPIENT, AND CONFLATING THE TWO IS
        # THE FALSE NEGATIVE THIS TOOL PRODUCED ON ITS OWN FIRST REAL RUN (2026-09-07 21:2x):
        # the roster carried git-bash paths (/n/claude-secretary/...), Python on Windows read
        # them as a backslash-n path under no drive, and four recipients that DID hold
        # byte-identical copies were all reported NO-DESTINATION. A checker that says
        # "not delivered" about a delivered letter teaches a seat to re-send or to stop
        # reading it -- the always-true alarm. So: if the path's own anchor does not exist,
        # the ROSTER is wrong, not the peer.
        anchor = Path(inbound.anchor) if inbound.anchor else None
        if anchor is not None and not anchor.exists():
            results.append((name, "BAD-ROSTER-PATH", f"{inbound} (anchor {inbound.anchor} does not exist)"))
            continue
        if not inbound.is_dir():
            results.append((name, "NO-DESTINATION", str(inbound)))
            continue
        landed = inbound / name_of
        if not landed.is_file():
            results.append((name, "NOT-DELIVERED", str(landed)))
        elif digest(landed) != want:
            results.append((name, "DIFFERS", str(landed)))
        else:
            results.append((name, "DELIVERED", str(landed)))
    ok = all(r[1] == "DELIVERED" for r in results)
    return results, ok


def cmd_check(draft: Path, roster_path: Path) -> int:
    roster = read_roster(roster_path)
    results, ok = check(draft, roster)
    print(f"ISSUANCE: {draft.name}")
    print(f"  recipients enumerated from roster: {len(roster)} (not globbed)")
    for name, verdict, where in results:
        print(f"  {verdict:<15} {name:<14} {where}")
    delivered = sum(1 for r in results if r[1] == "DELIVERED")
    print(f"  VERDICT: {'COMPLETE' if ok else 'INCOMPLETE'} "
          f"-- {delivered} of {len(results)} recipients hold a byte-identical copy")
    return 0 if ok else 3


# --------------------------------------------------------------------------- selftest

def _fixture(root: Path, name: str, depth_parts: tuple[str, ...]) -> Path:
    d = root.joinpath(*depth_parts) / "exchange" / "inbound"
    d.mkdir(parents=True, exist_ok=True)
    return d


def selftest() -> int:
    import tempfile

    fails: list[str] = []

    def expect(cond: bool, msg: str):
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        draft = root / "letter.md"
        draft.write_text("the body that must arrive unchanged\n", encoding="utf-8")

        shallow = _fixture(root, "secretary", ("secretary",))
        deep = _fixture(root, "cfl", ("cfl", "clone"))          # depth-4 recipient
        missing = root / "personal" / "exchange" / "inbound"     # never created

        # A -- every recipient holds a byte-identical copy => COMPLETE
        for d in (shallow, deep):
            (d / draft.name).write_bytes(draft.read_bytes())
        res, ok = check(draft, [("secretary", shallow), ("cfl", deep)])
        expect(ok, "A: two delivered recipients must be COMPLETE")

        # D -- CONTROL for the depth defect. The deep recipient is at clone/exchange/inbound,
        # which a find -maxdepth 3 cannot reach. If a future refactor reintroduces a depth walk,
        # this case goes red while A stays green.
        expect(dict((n, v) for n, v, _ in res)["cfl"] == "DELIVERED",
               "D control: a recipient nested one level deeper must still be found")

        # B -- one recipient missing the file => INCOMPLETE, and it is NAMED
        (deep / draft.name).unlink()
        res, ok = check(draft, [("secretary", shallow), ("cfl", deep)])
        expect(not ok, "B: a missing copy must be INCOMPLETE")
        expect(dict((n, v) for n, v, _ in res)["cfl"] == "NOT-DELIVERED",
               "B: the missing recipient must be named NOT-DELIVERED")

        # C -- CONTROL FOR INERTNESS. Case A must not be able to pass vacuously: with the file
        # gone from EVERY recipient the same call must go red. Without this, a check that always
        # returned DELIVERED would satisfy A and prove nothing.
        (shallow / draft.name).unlink()
        _, ok = check(draft, [("secretary", shallow), ("cfl", deep)])
        expect(not ok, "C inertness control: zero delivered copies must be INCOMPLETE")

        # E -- a nonexistent destination is NO-DESTINATION, never a silent pass. A write that
        # creates its own destination looks like delivery (constitution, "VERIFY THE TARGET").
        res, ok = check(draft, [("personal", missing)])
        expect(not ok, "E: a nonexistent inbound must not pass")
        expect(res[0][1] == "NO-DESTINATION",
               "E: a nonexistent inbound is NO-DESTINATION, not NOT-DELIVERED")

        # F -- same filename, different bytes => DIFFERS. Landing is not delivery if the body
        # changed in transit or a stale copy already sat there.
        shallow.mkdir(parents=True, exist_ok=True)
        (shallow / draft.name).write_text("a different body\n", encoding="utf-8")
        res, ok = check(draft, [("secretary", shallow)])
        expect(not ok, "F: a byte-differing copy must not pass")
        expect(res[0][1] == "DIFFERS", "F: a byte-differing copy is DIFFERS")

        # H -- CONTROL FOR THE FALSE NEGATIVE THIS TOOL ACTUALLY PRODUCED. A roster path whose
        # anchor does not exist is a BAD ROSTER, distinct from a missing recipient -- otherwise
        # a path-form mistake is indistinguishable from a peer who never received the letter.
        res, ok = check(draft, [("bogus", Path("Q:/no/such/drive/inbound"))])
        expect(not ok, "H: a bad roster path must not pass")
        expect(res[0][1] == "BAD-ROSTER-PATH",
               "H control: a path whose anchor does not exist is BAD-ROSTER-PATH, "
               "not NO-DESTINATION -- the false negative of 2026-09-07 21:2x")

        # G -- a malformed roster row RAISES rather than dropping a recipient silently.
        bad = root / "roster-bad.tsv"
        bad.write_text("secretary /no/tab/here\n", encoding="utf-8")
        try:
            read_roster(bad)
            fails.append("G: a roster row with no tab must raise, not drop the recipient")
        except ValueError:
            pass

    for f in fails:
        print("SELFTEST FAIL", f)
    print(f"SELFTEST {'FAIL' if fails else 'PASS'}: 8 cases "
          f"(A deliver, B one missing, C inertness control, D depth control, "
          f"E no-destination, F differing bytes, G malformed roster, H bad-roster-path control)")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--draft", type=Path, help="the artifact whose issuance is checked")
    ap.add_argument("--roster", type=Path, default=Path("exchange/RECIPIENTS.tsv"),
                    help="name<TAB>inbound-dir, one per line; ENUMERATED, never globbed")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.draft:
        ap.error("--draft is required (or use --selftest)")
    return cmd_check(a.draft, a.roster)


if __name__ == "__main__":
    sys.exit(main())
