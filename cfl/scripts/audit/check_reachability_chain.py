#!/usr/bin/env python3
"""Reachability-chain check (Part 2a of the 2026-08-06 "poor memory" ticket).

WHY THIS EXISTS
----------------
Until 2026-08-06 the resume rule lived INSIDE `wiki/tracker/wayfinder-cfl.md`, and nothing
anywhere told a fresh session to open that file. `CLAUDE.md` never named `WAKE.md`; `WAKE.md`
never named the map. Each file individually was fine; the CHAIN between them did not exist,
and nothing noticed for an unknown number of sessions — a cold session could see repo state
(git status) but not role state (what it was mid-task on). The instruction and the thing it
governs must be reachable from the same starting point, or the instruction is decoration.

⚠️ CORRECTED 2026-09-02 — hop 3/4 were HARDCODED to `wiki/tracker/wayfinder-cfl.md`, which was
recorded SUPERSEDED on 2026-08-24. `.claude/commands/wake.md` was itself corrected on 2026-08-30
(found by the DB-2 cross-verifier review) to say the live maps are DERIVED — every
`wiki/tracker/wayfinder-*.md` with `kind: wayfinder:map` and `status: LIVE` — never a single
hardcoded basename. This script certified PASS through the dead map for six days because it
still hardcoded the pre-08-30 wording. The pre-compact elder witness caught it 2026-09-02.
That is the exact defect this script exists to catch, reproduced by the checker itself — a
structural check whose own structure went stale is not a structural check, it's a stale opinion
with a green light. Fixed here: hop 3 and hop 4 are now DERIVED against `wiki/tracker/`'s live
frontmatter at run time, the same way `.claude/commands/wake.md` Step 1.4 instructs a session to
do it. Nothing about this hop is hardcoded to one map's basename any more.

WHAT IT CHECKS
--------------
Walks the read-chain CLAUDE.md names at cold-open and verifies each hop is a REAL forward
reference, not just that both files happen to exist:

  1. CLAUDE.md       -> must name CARRIER.md
  2. CARRIER.md       -> must name WAKE.md
  3. WAKE.md          -> must name at least one LIVE wayfinder map by basename, OR contain the
                          "derived, don't hardcode" instruction (both "derived" and
                          "wayfinder:map" present). Naming a SUPERSEDED (or otherwise non-LIVE)
                          map is reported as a WARN, not counted toward a pass — that is the
                          exact 2026-08-06→2026-08-30→2026-09-02 defect chain, reproduced.
  4. every LIVE map   -> must name index.md. Reported per-map; any miss fails the hop and is
                          named, not summarized away.
  5. index.md must exist (terminal node — nothing downstream to check)

"LIVE wayfinder map" = a file under `wiki/tracker/wayfinder-*.md` whose YAML frontmatter has
`kind: wayfinder:map` and a `status:` value that starts with `LIVE` (after stripping a leading
quote character) — not `SUPERSEDED`, not `MERGED-INTO ...`, not absent. This mirrors
`.claude/commands/wake.md` Step 1.4's own instruction verbatim: "enumerate `kind: wayfinder:map`
files in `wiki/tracker/` whose frontmatter says `status: LIVE`."

A hop "names" a file if the next file's basename (or a stem match) appears literally in the
current file's text. This is the same substring-match philosophy as lint_untracked_wiki.py —
cheap, loose, and the point is presence of a forward pointer, not a citation-format audit.

WHAT THIS DOES NOT CHECK, honestly stated
------------------------------------------
It does not verify a file's CONTENT is followed correctly by an agent, only that the pointer
exists in text. It does not check that `wiki/index.md` itself is current. It does not verify a
LIVE map's first-unclosed-ticket is real or current. It is a structural check for a structural
failure (a missing or stale forward reference) — it would not catch a subtler defect like a
reference pointing at the wrong line, or a `status: LIVE` value on a map whose content is
actually finished.

USAGE
    python scripts/audit/check_reachability_chain.py [--root .]

Exit code: 0 if every hop resolves (all LIVE-map checks included); 1 if any hop is broken or
any LIVE map fails to name index.md (the exact failure mode this script exists to catch — fails
closed, like the parity check).
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Hops 1-2 are single fixed files; their edge markers live with the edge, not the node, same
# as before. Hops 3-4 (WAKE.md -> live maps -> index.md) are DERIVED at run time — see
# find_wayfinder_maps() / check_wake_hop() / check_index_hop() below. Kept as plain constants so
# a fixture root only needs these two fixed files plus a wiki/tracker/ directory.
CLAUDE_MD = "CLAUDE.md"
CARRIER_MD = "exchange/CARRIER.md"
WAKE_MD = "exchange/WAKE.md"
INDEX_MD = "wiki/index.md"
TRACKER_DIR = os.path.join("wiki", "tracker")

EDGE_MARKERS = {
    CLAUDE_MD: ["CARRIER.md"],
    CARRIER_MD: ["WAKE.md"],
}

FRONTMATTER_KV = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")


def read(root, rel):
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_frontmatter(text):
    """Return a dict of the first '---'-delimited YAML block's top-level scalar keys.

    Deliberately naive (no real YAML parser): every wayfinder map observed in this repo writes
    `kind:` and `status:` as single-line scalars, which is all this needs. Multi-line values are
    not supported and are not needed here.
    """
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    fm = {}
    in_block = False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_block = True
            continue
        if in_block and line.strip() == "---":
            break
        if not in_block:
            continue
        m = FRONTMATTER_KV.match(line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def is_live_status(status):
    """True if a frontmatter `status:` value is LIVE (not SUPERSEDED, MERGED-INTO, or absent)."""
    if not status:
        return False
    s = status.strip()
    # Strip one layer of surrounding quotes, e.g. `"LIVE — chartered ..."`.
    if len(s) >= 2 and s[0] in "\"'":
        s = s[1:]
    return bool(re.match(r"^LIVE\b", s))


def find_wayfinder_maps(root):
    """Scan wiki/tracker/wayfinder-*.md and split into (live, non_live) lists.

    Each entry is (basename, rel_path, text, status_value). `non_live` includes SUPERSEDED,
    MERGED-INTO, and files with no status field at all — anything that is not LIVE, kept so the
    WAKE.md check can report a WARN when one of these is what got named instead of a live map.
    """
    tracker_path = os.path.join(root, TRACKER_DIR)
    live, non_live = [], []
    if not os.path.isdir(tracker_path):
        return live, non_live
    for fname in sorted(os.listdir(tracker_path)):
        if not (fname.startswith("wayfinder-") and fname.endswith(".md")):
            continue
        rel = (TRACKER_DIR + "/" + fname).replace("\\", "/")
        text = read(root, rel)
        if text is None:
            continue
        fm = extract_frontmatter(text)
        if "wayfinder:map" not in fm.get("kind", ""):
            continue
        status = fm.get("status", "")
        entry = (fname, rel, text, status)
        if is_live_status(status):
            live.append(entry)
        else:
            non_live.append(entry)
    return live, non_live


def check_wake_hop(wake_text, live_maps, non_live_maps):
    """Hop 3: does exchange/WAKE.md point at the live-map set correctly?

    PASS if WAKE.md names at least one LIVE map's basename, OR contains the derive-don't-hardcode
    instruction (both "derived" and "wayfinder:map" present, case-insensitive for "derived").
    A non-LIVE map named instead is reported separately as a WARN — it is evidence of the exact
    stale-hardcode defect, not a forward pointer that counts toward the pass.
    """
    result = {"ok": False, "named_live": [], "named_non_live": [], "derived_phrase": False,
              "reason": None}
    if wake_text is None:
        result["reason"] = f"{WAKE_MD} does not exist"
        return result

    named_live = [fname for fname, _, _, _ in live_maps if fname in wake_text]
    named_non_live = [fname for fname, _, _, _ in non_live_maps if fname in wake_text]
    derived_phrase = ("derived" in wake_text.lower()) and ("wayfinder:map" in wake_text)

    result["named_live"] = named_live
    result["named_non_live"] = named_non_live
    result["derived_phrase"] = derived_phrase
    result["ok"] = bool(named_live) or derived_phrase
    if not result["ok"]:
        if named_non_live:
            result["reason"] = (
                f"{WAKE_MD} names {named_non_live!r} which is NOT status: LIVE, and contains no "
                f"other LIVE-map basename and no 'derived'+'wayfinder:map' instruction — this is "
                f"the stale-hardcoded-map defect")
        else:
            result["reason"] = (
                f"{WAKE_MD} names no LIVE wayfinder map by basename and contains no "
                f"'derived'+'wayfinder:map' instruction")
    return result


def check_index_hop(live_maps):
    """Hop 4: does every LIVE map name index.md? Returns (ok, [(fname, rel, has_index_md), ...])."""
    per_map = []
    for fname, rel, text, status in live_maps:
        has = "index.md" in text
        per_map.append((fname, rel, has))
    ok = bool(live_maps) and all(has for _, _, has in per_map)
    return ok, per_map


def check_chain(root):
    """Run all hops. Returns (results, live_maps, non_live_maps) — results is a list of dicts
    with 'type' in {'exists', 'edge', 'live_map_census', 'wake_hop', 'index_hop'}."""
    results = []

    claude_text = read(root, CLAUDE_MD)
    carrier_text = read(root, CARRIER_MD)
    wake_text = read(root, WAKE_MD)
    index_text = read(root, INDEX_MD)

    results.append({"type": "exists", "node": CLAUDE_MD, "ok": claude_text is not None})
    results.append({"type": "exists", "node": CARRIER_MD, "ok": carrier_text is not None})
    results.append({"type": "exists", "node": WAKE_MD, "ok": wake_text is not None})

    # Hops 1-2: fixed edges.
    for cur_rel, cur_text, nxt_rel in [
        (CLAUDE_MD, claude_text, CARRIER_MD),
        (CARRIER_MD, carrier_text, WAKE_MD),
    ]:
        if cur_text is None:
            results.append({"type": "edge", "from": cur_rel, "to": nxt_rel, "ok": False,
                             "reason": f"{cur_rel} does not exist"})
            continue
        markers = EDGE_MARKERS[cur_rel]
        found = any(m in cur_text for m in markers)
        results.append({
            "type": "edge", "from": cur_rel, "to": nxt_rel, "ok": found,
            "reason": None if found else
                      f"{cur_rel} does not contain any of {markers!r} — no forward pointer to {nxt_rel}",
        })

    # Derive the live-map set fresh every run — this is the fix. Nothing above this line hardcodes
    # a map's basename.
    live_maps, non_live_maps = find_wayfinder_maps(root)
    results.append({"type": "live_map_census", "live": [f for f, _, _, _ in live_maps],
                     "non_live": [(f, s) for f, _, _, s in non_live_maps]})

    # Hop 3: WAKE.md -> live map set.
    wake_hop = check_wake_hop(wake_text, live_maps, non_live_maps)
    results.append({"type": "wake_hop", **wake_hop})

    # Hop 4: every live map -> index.md.
    index_hop_ok, per_map = check_index_hop(live_maps)
    results.append({"type": "index_hop", "ok": index_hop_ok, "per_map": per_map,
                     "reason": None if index_hop_ok else
                     "at least one LIVE map does not name index.md, or no LIVE maps exist"})

    results.append({"type": "exists", "node": INDEX_MD, "ok": index_text is not None})

    return results, live_maps, non_live_maps


def write_frontmatter_map(path, kind="wayfinder:map", status="LIVE", extra_body="Then wiki/index.md.\n"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\nkind: {kind}\nstatus: {status}\n---\n\n{extra_body}")


def selftest():
    import tempfile, shutil
    fails = []
    tmp = tempfile.mkdtemp(prefix="reach-selftest-")
    try:
        os.makedirs(os.path.join(tmp, "exchange"))
        os.makedirs(os.path.join(tmp, TRACKER_DIR))

        def write(rel, content):
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)

        # --- Case 1: intact chain, one LIVE map named by basename, LIVE map names index.md. ---
        write(CLAUDE_MD, "Read exchange/CARRIER.md first.\n")
        write(CARRIER_MD, "Then exchange/WAKE.md.\n")
        write(WAKE_MD, "See wiki/tracker/wayfinder-current.md.\n")
        write_frontmatter_map(os.path.join(tmp, TRACKER_DIR, "wayfinder-current.md"))
        write(INDEX_MD, "Index.\n")

        results, live, non_live = check_chain(tmp)
        if not all(r["ok"] for r in results if "ok" in r):
            fails.append(f"FAIL intact-chain: expected all OK, got {[r for r in results if 'ok' in r and not r['ok']]}")
        if len(live) != 1 or live[0][0] != "wayfinder-current.md":
            fails.append(f"FAIL intact-chain: expected 1 live map 'wayfinder-current.md', got {live!r}")

        # --- Case 2: intact chain via the 'derived' + 'wayfinder:map' instruction instead of a
        #     basename — must also PASS (this is what the real fix's WAKE.md wording should do). ---
        write(WAKE_MD, "The live wayfinder maps are DERIVED — enumerate kind: wayfinder:map files "
                       "in wiki/tracker/ whose status is LIVE.\n")
        results2, _, _ = check_chain(tmp)
        wake_hop2 = next(r for r in results2 if r["type"] == "wake_hop")
        if not wake_hop2["ok"]:
            fails.append(f"FAIL derived-phrase-pass: expected wake_hop ok, got {wake_hop2!r}")

        # --- Case (a): WAKE.md names ONLY a SUPERSEDED map -> FAILS, reported as WARN not pass. ---
        write(WAKE_MD, "See wiki/tracker/wayfinder-old.md.\n")
        write_frontmatter_map(os.path.join(tmp, TRACKER_DIR, "wayfinder-old.md"), status="SUPERSEDED — retired")
        # wayfinder-current.md from case 1 is still LIVE and still on disk but NOT named by WAKE.md
        # here — the point of this case is that naming only a superseded map must not pass even
        # though an unrelated live map exists elsewhere in the tree.
        os.remove(os.path.join(tmp, TRACKER_DIR, "wayfinder-current.md"))
        results3, live3, non_live3 = check_chain(tmp)
        wake_hop3 = next(r for r in results3 if r["type"] == "wake_hop")
        if wake_hop3["ok"]:
            fails.append(f"FAIL superseded-only-detection: expected wake_hop NOT ok, got {wake_hop3!r}")
        if "wayfinder-old.md" not in wake_hop3["named_non_live"]:
            fails.append(f"FAIL superseded-only-detection: expected 'wayfinder-old.md' in named_non_live, got {wake_hop3!r}")
        overall3 = all(r["ok"] for r in results3 if "ok" in r)
        if overall3:
            fails.append("FAIL superseded-only-detection: expected overall chain to FAIL, got PASS")

        # --- Case (b): one LIVE map that does NOT name index.md -> FAILS, naming it. ---
        write(WAKE_MD, "See wiki/tracker/wayfinder-nolink.md.\n")
        write_frontmatter_map(os.path.join(tmp, TRACKER_DIR, "wayfinder-nolink.md"),
                               extra_body="No forward pointer here.\n")
        results4, live4, non_live4 = check_chain(tmp)
        index_hop4 = next(r for r in results4 if r["type"] == "index_hop")
        if index_hop4["ok"]:
            fails.append(f"FAIL missing-index-pointer: expected index_hop NOT ok, got {index_hop4!r}")
        missing_names = [f for f, _, has in index_hop4["per_map"] if not has]
        if "wayfinder-nolink.md" not in missing_names:
            fails.append(f"FAIL missing-index-pointer: expected 'wayfinder-nolink.md' named as missing, got {missing_names!r}")

        # --- Missing node entirely (original regression: index.md deleted). ---
        write(WAKE_MD, "See wiki/tracker/wayfinder-current.md.\n")
        write_frontmatter_map(os.path.join(tmp, TRACKER_DIR, "wayfinder-current.md"))
        os.remove(os.path.join(tmp, TRACKER_DIR, "wayfinder-nolink.md"))
        os.remove(os.path.join(tmp, TRACKER_DIR, "wayfinder-old.md"))
        os.remove(os.path.join(tmp, INDEX_MD))
        results5, _, _ = check_chain(tmp)
        missing = [r for r in results5 if r["type"] == "exists" and r["node"] == INDEX_MD and not r["ok"]]
        if len(missing) != 1:
            fails.append(f"FAIL missing-node-detection: got {missing!r}")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print(f)
    if fails:
        print(f"\nSELFTEST: {len(fails)} failure(s)")
        return 1
    print("SELFTEST: 6/6 checks passed")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    results, live_maps, non_live_maps = check_chain(a.root)
    print("=" * 78)
    print("REACHABILITY-CHAIN CHECK")
    print("  CLAUDE.md -> exchange/CARRIER.md -> exchange/WAKE.md ->")
    print("  [DERIVED: every LIVE wayfinder map] -> wiki/index.md")
    print("=" * 78)
    ok = True

    for r in results:
        if r["type"] == "exists":
            mark = "OK " if r["ok"] else "!! "
            print(f"  {mark}exists    {r['node']}")
            ok = ok and r["ok"]
        elif r["type"] == "edge":
            mark = "OK " if r["ok"] else "!! "
            print(f"  {mark}pointer   {r['from']} -> {r['to']}")
            if not r["ok"]:
                print(f"         reason: {r['reason']}")
            ok = ok and r["ok"]
        elif r["type"] == "live_map_census":
            print(f"  ..  derived   {len(r['live'])} LIVE wayfinder:map file(s) in {TRACKER_DIR}/:")
            for f in r["live"]:
                print(f"                - {f}")
            if r["non_live"]:
                print(f"      (non-LIVE, excluded from the derived set: "
                      f"{', '.join(f'{f} [{s.strip()[:40]}]' for f, s in r['non_live'])})")
        elif r["type"] == "wake_hop":
            mark = "OK " if r["ok"] else "!! "
            print(f"  {mark}pointer   {WAKE_MD} -> derived LIVE map set")
            if r["named_live"]:
                print(f"         names LIVE map(s): {r['named_live']!r}")
            if r["derived_phrase"]:
                print("         contains the 'derived' + 'wayfinder:map' instruction")
            if r["named_non_live"]:
                print(f"      WARN names non-LIVE map(s) instead/also: {r['named_non_live']!r} "
                      f"— stale-hardcode defect")
            if not r["ok"]:
                print(f"         reason: {r['reason']}")
            ok = ok and r["ok"]
        elif r["type"] == "index_hop":
            mark = "OK " if r["ok"] else "!! "
            print(f"  {mark}pointer   every LIVE wayfinder map -> {INDEX_MD}")
            for fname, rel, has in r["per_map"]:
                sub = "OK " if has else "!! "
                print(f"         {sub}{fname}")
            if not r["ok"]:
                print(f"         reason: {r['reason']}")
            ok = ok and r["ok"]

    print()
    print("RESULT: PASS — chain is intact end to end." if ok else
          "RESULT: FAIL — at least one node or forward pointer is broken (see !! lines above).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
