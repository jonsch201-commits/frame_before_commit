"""WW-1c selftest -- does step 9 tell the FIXED ORDER apart from a CRASH?

Why this file exists: on 2026-09-12 the SessionStart:compact banner reached a seat's context as
"POSTCOMPACT-STATUS: FAIL ... reds: ... 9 summary vs tail" while the verdict written to disk two
minutes later was PASS-WITH-SKIPS. The late-regrade (WW-1b) fixed the FILE; the banner is the
surface the seat actually reads, and it still cried wolf on every compact. A detector that is red
by construction at a known moment trains its reader to ignore it.

Every arm below violates EXACTLY ONE condition, so a pass cannot come from two errors cancelling.
Run: python scripts/tests/selftest_postcompact_step9_order.py
"""
import importlib.util, json, sys, tempfile, unittest
from datetime import datetime, timedelta
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "audit" / "postcompact_pipeline.py"
spec = importlib.util.spec_from_file_location("pcp", SRC)
pcp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pcp)

SESS = "aaaaaaaa-1111-2222-3333-444444444444"


class Case:
    """Builds a fake tree: precompact receipts, postcompact artifacts, and a session jsonl."""

    def __init__(self, tmp, boundary_record=True, artifact="fresh"):
        self.root = Path(tmp)
        pre = self.root / "exchange" / "su-close" / "precompact"
        post = self.root / "exchange" / "su-close" / "postcompact"
        pre.mkdir(parents=True); post.mkdir(parents=True)
        # one receipt, stamped now, named the way the real ones are
        now = datetime.now().replace(microsecond=0)
        self.receipt = pre / (now.strftime("%Y%m%dT%H%M%S") + "-" + SESS[:8] + ".md")
        self.receipt.write_text("receipt", encoding="utf-8")
        if artifact == "fresh":
            a = post / (now.strftime("%Y%m%dT%H%M%S") + "999999Z-" + SESS[:8] + ".md")
            a.write_text("VERDICT: CHECKED (0)", encoding="utf-8")
        elif artifact == "stale":
            a = post / "20260101T000000000000Z-old.md"
            a.write_text("VERDICT: CHECKED (0)", encoding="utf-8")
            import os
            old = (now - timedelta(days=2)).timestamp()
            os.utime(a, (old, old))
        # the session jsonl lives under a home-shaped path the module resolves itself
        proj = self.root / "home" / ".claude" / "projects" / "N--claude-cfl-clone"
        proj.mkdir(parents=True)
        lines = [json.dumps({"type": "user", "message": {}})]
        if boundary_record:
            # the real records are UTC; the module subtracts 5h to reach CDT
            ts = (now + timedelta(hours=5, seconds=30)).isoformat()
            lines.append(json.dumps({"type": "system", "subtype": "compact_boundary",
                                     "timestamp": ts}))
        (proj / (SESS + ".jsonl")).write_text("\n".join(lines), encoding="utf-8")
        self.home = self.root / "home"
        self.receipts = sorted(pre.glob("*.md"))

    def grade(self):
        pcp.ROOT = self.root
        pcp.Path.home = staticmethod(lambda h=self.home: h)
        return pcp.grade_step9(self.receipts, SESS)


class T(unittest.TestCase):
    def run_case(self, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            return Case(tmp, **kw).grade()

    def test_fixed_order_no_artifact_is_pending_not_fail(self):
        """THE ARM THIS FILE WAS WRITTEN FOR: first wiring, no artifact, no boundary record."""
        step, verdict, note = self.run_case(boundary_record=False, artifact="none")
        self.assertEqual(verdict, "SKIPPED-PENDING-ORDER", note)
        self.assertIn("not in the jsonl yet", note)
        # and it must still be UNKNOWN-class to both aggregators
        self.assertTrue(verdict.startswith("SKIPPED"))

    def test_crash_no_artifact_but_boundary_recorded_is_FAIL(self):
        """ONE condition differs from the arm above: the boundary record exists."""
        step, verdict, note = self.run_case(boundary_record=True, artifact="none")
        self.assertEqual(verdict, "FAIL", note)

    def test_stale_artifact_pre_boundary_is_pending(self):
        step, verdict, note = self.run_case(boundary_record=False, artifact="stale")
        self.assertEqual(verdict, "SKIPPED-PENDING-ORDER", note)

    def test_stale_artifact_with_boundary_recorded_is_FAIL(self):
        step, verdict, note = self.run_case(boundary_record=True, artifact="stale")
        self.assertEqual(verdict, "FAIL", note)
        self.assertIn("PREDATES", note)

    def test_fresh_artifact_passes_either_way(self):
        for rec in (True, False):
            step, verdict, note = self.run_case(boundary_record=rec, artifact="fresh")
            self.assertEqual(verdict, "PASS", f"boundary_record={rec}: {note}")

    def test_no_session_id_cannot_claim_pending(self):
        """A missing instrument must make this STRICTER, never quieter."""
        with tempfile.TemporaryDirectory() as tmp:
            c = Case(tmp, boundary_record=False, artifact="none")
            pcp.ROOT = c.root
            pcp.Path.home = staticmethod(lambda h=c.home: h)
            self.assertEqual(pcp.grade_step9(c.receipts, None)[1], "FAIL")

    def test_unreadable_jsonl_cannot_claim_pending(self):
        """Second negative arm: the jsonl is absent, so the second method never agreed."""
        with tempfile.TemporaryDirectory() as tmp:
            c = Case(tmp, boundary_record=False, artifact="none")
            (c.home / ".claude" / "projects" / "N--claude-cfl-clone" / (SESS + ".jsonl")).unlink()
            pcp.ROOT = c.root
            pcp.Path.home = staticmethod(lambda h=c.home: h)
            self.assertEqual(pcp.grade_step9(c.receipts, SESS)[1], "FAIL")

    def test_no_receipts_cannot_claim_pending(self):
        """Third negative arm: no receipt means no boundary to be pending ABOUT."""
        with tempfile.TemporaryDirectory() as tmp:
            c = Case(tmp, boundary_record=False, artifact="none")
            c.receipt.unlink()
            pcp.ROOT = c.root
            pcp.Path.home = staticmethod(lambda h=c.home: h)
            self.assertFalse(pcp._boundary_record_pending(SESS))


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False, verbosity=2).result.wasSuccessful() else 1)
