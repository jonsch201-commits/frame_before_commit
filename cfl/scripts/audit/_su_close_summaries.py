#!/usr/bin/env python
"""_su_close_summaries.py — Q10 helper: does every conversation in THIS session have an L2 summary?

WHY THIS EXISTS — Jon audited the 2026-08-03 close and found the wiki lane wrote zero of 15
required conversation summaries. The root cause (raw/'s `## Summary` placeholder is destroyed by
every `--update` refresh) is documented in
`skills/intake/ready/summary-placeholder-is-unfillable-2026-08-03.md`. The fix moves summaries to
L2 (the wiki), which nothing overwrites. THIS SCRIPT IS THE CHECK THAT THE FIX ACTUALLY HAPPENED —
not a record that it should have.

SCOPE, determined from ground truth, never hand-maintained:
  - the parent session's own raw extract: raw/transcripts/claude-code/code-*-<session6>-*.md
    (excluding .sidecar.md)
  - every subagent extract under raw/transcripts/claude-code/subagents/<session6>/*.md
      (excluding .sidecar.md)
`session6` is the 6-hex-char session id prefix — passed explicitly (--session6) or read from
CLAUDE_CODE_SESSION_ID. Nothing here is a magic constant naming a specific session; a different
session's close finds its own scope. If neither is available, this is a hard UNKNOWN (rc=2), not a
silent zero.

VALUE = how many of that scope have an L2 summary. A conversation counts as summarized if any
markdown file in wiki/ (excluding wiki/intake-triage/ — routing area, not the durable artifact this
check is verifying) contains a line matching `^##+\\s+.*\\b<id>\\b` where <id> is the conversation's
6-hex-char id. This is intentionally loose (any heading naming the id counts) rather than requiring
one specific file layout, because the fix (session-9e21da-subagent-summaries-2026-08-03.md) chose a
single consolidated page; a future close might reasonably choose one file per conversation instead,
and the check must not assume its own current shape is the only correct one.

NEGATIVE CONTROL, built in: point --repo at an empty tree (no raw/, no wiki/) and the scope is
zero, so this prints `0 0` (value denom) and the caller's `classify()` reads that denominator as
zero and reports UNKNOWN — 0/0 is NOT A PASS, per su_close.sh's own contract. Verified by
`--self-test` below.

Usage:
  python _su_close_summaries.py --repo <path> [--session6 XXXXXX]
  python _su_close_summaries.py --self-test

Prints exactly one line: "<value> <denom>" (both integers), or "0 0" with a stderr note when scope
cannot be determined at all (denom genuinely zero — e.g. the session left no subagent transcripts).
Exit 0 always unless --self-test fails; su_close.sh's classify() derives UNKNOWN from denom==0, not
from this script's exit code, so this script exits 0 whenever it produced two integers.
"""
import argparse
import os
import re
import sys
from pathlib import Path


def find_scope(repo: Path, session6: str):
    """Return sorted list of 6-char ids in scope: [session6, subagent ids...]."""
    ids = []
    cc_dir = repo / "raw" / "transcripts" / "claude-code"
    if not cc_dir.is_dir():
        return ids
    # Parent extract: code-YYYY-MM-DD-<session6>-*.md, never the .sidecar.md companion.
    #
    # MUST BE RECURSIVE. A non-recursive `cc_dir.glob(...)` sees only the top level of
    # `raw/transcripts/claude-code/`, but the 2026-07-28 L1 move (Record Architecture v1)
    # routes primaries into per-branch children — `fl/`, `personal/`, `pro/`, `home/`,
    # `_routing/`. Measured 2026-08-06: **39 primaries at the top level, 63 in the children**
    # (fl 57, personal 2, _routing 4). The old glob could see 38% of the corpus and reported
    # the other 62% as absent — a migration silently blinding an instrument, which is the
    # failure class this program has already paid for twice.
    #
    # `subagents/` is excluded deliberately: a subagent extract is named for its AGENT id, so
    # an agent whose 6-char prefix collided with a session's would otherwise be counted as
    # that session's parent extract. Subagents are enumerated separately below, by directory.
    for p in cc_dir.rglob(f"code-*-{session6}-*.md"):
        if p.name.endswith(".sidecar.md"):
            continue
        if "subagents" in p.relative_to(cc_dir).parts:
            continue
        ids.append(session6)
        break
    sub_dir = cc_dir / "subagents" / session6
    if sub_dir.is_dir():
        for p in sorted(sub_dir.glob("code-*.md")):
            if p.name.endswith(".sidecar.md"):
                continue
            m = re.search(r"code-\d{4}-\d{2}-\d{2}-([0-9a-f]{6})-", p.name)
            if m:
                ids.append(m.group(1))
    return ids


def count_summarized(repo: Path, ids):
    """For each id, does any wiki/ page (outside intake-triage) carry a heading naming it?"""
    wiki_dir = repo / "wiki"
    if not wiki_dir.is_dir():
        return 0
    texts = []
    for p in wiki_dir.rglob("*.md"):
        if "intake-triage" in p.parts:
            continue
        try:
            texts.append(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    blob = "\n".join(texts)
    found = 0
    for cid in ids:
        pat = re.compile(r"^#{1,6}\s+.*\b" + re.escape(cid) + r"\b", re.M)
        if pat.search(blob):
            found += 1
    return found


def self_test():
    import tempfile
    fails = 0

    def t(name, expected, actual):
        nonlocal fails
        ok = expected == actual
        print(f"  {'PASS' if ok else 'FAIL'}  {name}  (expected {expected!r} got {actual!r})")
        if not ok:
            fails += 1

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # (a) NEGATIVE CONTROL — nothing on disk at all.
        ids = find_scope(root, "abc123")
        t("empty tree: scope is empty", [], ids)
        t("empty tree: count is 0", 0, count_summarized(root, ids))

        # (b) real scope, real summary present.
        cc = root / "raw" / "transcripts" / "claude-code"
        sub = cc / "subagents" / "abc123"
        sub.mkdir(parents=True)
        (cc / "code-2026-08-03-abc123-parent-session.md").write_text("parent", encoding="utf-8")
        (sub / "code-2026-08-03-def456-child-one.md").write_text("child1", encoding="utf-8")
        (sub / "code-2026-08-03-abc789-child-two.md").write_text("child2", encoding="utf-8")
        (sub / "code-2026-08-03-def456-child-one.sidecar.md").write_text("SIDECAR — must not count as a scope member", encoding="utf-8")
        ids = find_scope(root, "abc123")
        t("scope finds parent + 2 children, not the sidecar",
          {"abc123", "def456", "abc789"}, set(ids))
        t("scope has exactly 3 entries (no dupes, sidecar excluded)", 3, len(ids))

        wiki = root / "wiki" / "sources" / "infrastructure"
        wiki.mkdir(parents=True)
        (wiki / "summaries.md").write_text(
            "## abc123 — parent\nSummary text.\n\n## def456 — child one\nSummary text.\n",
            encoding="utf-8",
        )
        t("2 of 3 summarized", 2, count_summarized(root, ids))

        # (c) intake-triage is excluded — a routing deposit does not count as the durable artifact.
        triage = root / "wiki" / "intake-triage"
        triage.mkdir(parents=True)
        (triage / "routing-note.md").write_text("## abc789 — mentioned only in routing, not the wiki proper\n", encoding="utf-8")
        t("intake-triage mention does NOT count", 2, count_summarized(root, ids))

        # (d) once a real page covers it, it counts.
        (wiki / "summaries.md").write_text(
            (wiki / "summaries.md").read_text(encoding="utf-8") + "\n## abc789 — child two\nSummary text.\n",
            encoding="utf-8",
        )
        t("3 of 3 summarized once all three are covered", 3, count_summarized(root, ids))

    if fails:
        print(f"RESULT: FAIL — {fails} case(s)")
        return 1
    print("RESULT: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="where raw/transcripts/ lives (scope source)")
    ap.add_argument("--wiki-root", default="", help="where wiki/ lives, if different from --repo "
                     "(e.g. a linked worktree with no raw/ of its own — fence #2)")
    ap.add_argument("--session6", default="")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    session6 = args.session6 or os.environ.get("CLAUDE_CODE_SESSION_ID", "")[:6]
    repo = Path(args.repo)
    wiki_root = Path(args.wiki_root) if args.wiki_root else repo
    if not session6:
        print("0 0", flush=True)
        print("no session6 given and CLAUDE_CODE_SESSION_ID unset — scope is genuinely empty", file=sys.stderr)
        sys.exit(0)

    ids = find_scope(repo, session6)
    value = count_summarized(wiki_root, ids)
    print(f"{value} {len(ids)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
