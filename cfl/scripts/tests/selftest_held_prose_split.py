"""T5: a page is withheld for a DECLARATION, not for a sentence.

Professional, 2026-09-13 00:1x, reporting CFL's defect: `HELD_VAL_RX` matches `\\bheld\\b` over the
whole field text and cut their LIVE page for prose about leading from the rigor seat.

The cause is ordinary English in the exclusion vocabulary. `scripts/audit/public_exclusions.txt`:
    FM_HELD_KEY    held-personal · held_personal · exposure_class · visibility
    FM_HELD_VALUE  HELD · held-personal · held_personal · personal · private
So any narrative value under a key as common as `visibility` trips it — `visibility: "LIVE, held to
the rigor standard"` withheld a live page.

⛔ **THE MATCH WAS NOT LOOSENED.** On a public surface, failing open is the dangerous direction and a
real marker buried in prose must still be caught. The VERDICT was split instead:
    FM-HELD-PERSONAL — the value IS the marker. Still CUTS.
    FM-HELD-PROSE    — a marker word inside a longer value. REPORTED, never cut, logged by name.

⚠️ **THIS TEST EXISTS BECAUSE CFL'S OWN TREE CANNOT EXERCISE THE FIX.** `[measured 2026-09-13 00:3x:
a full derive over N:/claude-cfl/clone produced 0 REPORT-ONLY rows.]` The false positive fires in
Professional's tree, not here — so without these fixtures the change would ship on reasoning alone,
and "it compiles and the live run is unchanged" is exactly what an ineffective fix looks like.

⭐ AND THE FIRST VERSION OF THE FIX WAS INEFFECTIVE IN PRECISELY THAT WAY: it returned FM-HELD-PROSE
as an ordinary classifier row, and the per-file loop does `if hits: continue`, so the page would have
been cut with a friendlier label. Caught by reading the call site. Arm 5 below is the regression test
for that: a report-only class must never reach the withholding list.

Run: python scripts/tests/selftest_held_prose_split.py
"""
import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = Path(__file__).resolve().parents[1] / "audit" / "derive_public_tree.py"
spec = importlib.util.spec_from_file_location("dpt", SRC)
dpt = importlib.util.module_from_spec(spec)
sys.argv = [str(SRC)]                      # the module parses argv at import in some paths
spec.loader.exec_module(dpt)

CASES = [
    # (name, frontmatter, expected class or None, must_be_report_only)
    ("prose under a common key is REPORTED, not cut",
     {"visibility": "LIVE — leading from the rigor seat, held to the rigor standard"},
     "FM-HELD-PROSE", True),
    ("a bare marker still CUTS",
     {"visibility": "private"}, "FM-HELD-PERSONAL", False),
    ("a marker with a short qualifier still CUTS",
     {"exposure_class": "HELD (jon)"}, "FM-HELD-PERSONAL", False),
    ("uppercase bare marker still CUTS",
     {"held-personal": "HELD"}, "FM-HELD-PERSONAL", False),
    ("a long value whose FIRST token is a marker is REPORTED, not cut",
     {"visibility": "personal reflections on how the fleet reads its own record over time"},
     "FM-HELD-PROSE", True),
    ("a value with no marker word at all yields NOTHING",
     {"visibility": "LIVE"}, None, False),
    ("a marker under a key that is NOT a held key yields NOTHING",
     {"title": "private thoughts"}, None, False),
]

# T5 SECOND CODE PATH, reopened by Professional as raiser after CFL declared the class closed.
# `status` has its OWN matcher -- re.search(r"HELD", status) -- three lines above the comment
# CFL wrote about the defect. One path was fixed, CFL's own tree exercised neither, and the page was
# still cut. A vocabulary defect lives in every matcher sharing the vocabulary, so the unit of repair
# is the CLASS, not the line. These arms are keyed on their EXACT page so the regression is theirs.
STATUS_CASES = [
    ("their page: prose in a LIVE status is REPORTED, not cut",
     {"status": "LIVE — positions held by this seat"}, "FM-STATUS-HELD-PROSE", True),
    ("a declared HELD status still CUTS",
     {"status": "HELD"}, "FM-STATUS-HELD", False),
    ("HELD with a short qualifier still CUTS",
     {"status": "HELD (jon)"}, "FM-STATUS-HELD", False),
    ("a plain LIVE status yields NOTHING",
     {"status": "LIVE"}, None, False),
]
CASES = CASES + STATUS_CASES

fails = []
for name, fm, expect, report_only in CASES:
    rows = dpt.frontmatter_exclusions("wiki/concepts/x.md", fm)
    classes = [r[0] for r in rows]
    held = [c for c in classes if c.startswith("FM-HELD") or c.startswith("FM-STATUS-HELD")]
    if expect is None:
        if held:
            fails.append(f"{name}: expected no held row, got {held}")
        continue
    if expect not in held:
        fails.append(f"{name}: expected {expect}, got {held or 'nothing'}")
        continue
    in_report_set = expect in dpt.REPORT_ONLY_CLASSES
    if report_only and not in_report_set:
        fails.append(f"{name}: {expect} is NOT in REPORT_ONLY_CLASSES, so the per-file loop would "
                     f"still withhold the file — the fix would be a rename")
    if (not report_only) and in_report_set:
        fails.append(f"{name}: {expect} is report-only, so a real declaration would NOT be withheld "
                     f"— that is failing OPEN on a public surface")

# Arm 5 as a standing invariant, independent of the cases above.
if "FM-HELD-PERSONAL" in dpt.REPORT_ONLY_CLASSES:
    fails.append("FM-HELD-PERSONAL must never be report-only: a declaration has to cut")
if "FM-HELD-PROSE" not in dpt.REPORT_ONLY_CLASSES:
    fails.append("FM-HELD-PROSE must be report-only or the T5 fix does nothing")
if "FM-STATUS-HELD" in dpt.REPORT_ONLY_CLASSES:
    fails.append("FM-STATUS-HELD must never be report-only: a declared HELD status has to cut")
if "FM-STATUS-HELD-PROSE" not in dpt.REPORT_ONLY_CLASSES:
    fails.append("FM-STATUS-HELD-PROSE must be report-only or the SECOND code path still cuts")

for f in fails:
    print("  FAIL " + f)
print(f"selftest: {'PASS' if not fails else 'FAIL'} — {len(CASES)} cases + 4 invariants, "
      f"{len(fails)} failure(s)")
sys.exit(0 if not fails else 1)
