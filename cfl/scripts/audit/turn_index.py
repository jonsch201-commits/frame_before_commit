#!/usr/bin/env python3
"""Canonical turn-indexer for raw conversation sources.

The dominant defect found in v3.0 calibration (finding F3) was BROKEN turn-anchoring:
existing anchors drift 100+ turns across a session, cite non-existent turns, and the
turn-COUNT itself disagrees three ways on one page. Root cause: anchors were estimated,
never counted. This tool removes the estimation — it deterministically enumerates the
turn headers of a raw and emits an authoritative T-map + verified count. Every audit /
remediation must anchor against this, not against a guess.

Two header styles occur in the corpus:
  - claude.ai native exports:  lines beginning "## Human" / "## Assistant"
  - Claude Code / some exports: lines beginning "**Jon**" / "**Claude**" (often "**Jon** [ts]")
The tool auto-detects which style dominates and enumerates sequentially from the top.

"## Compaction Boundary" (role "C") counts as a turn (2026-07-24). Claude Code writes its
compaction summary as a `user` record with string content, so convert-claude-code.py used to
emit it under "## Human" — meaning those records are ALREADY baked into every existing turn
number for the affected sessions. Now that the parser labels them honestly, this indexer must
keep counting them, or every turn number after a boundary would shift down by one on
re-extraction and silently invalidate existing wiki citations. Counting them preserves
numbering exactly; the role letter ("C", not "H") is what carries the corrected attribution.

"## Tool Result" (role "R") counts as a turn (2026-07-25, turn-5 dispatch — "the dropped
record class"). convert-claude-code.py used to drop every tool_result-bearing user record
outright (content is a LIST, not a string); it now extracts them as their own turn, so this
indexer must recognize the header or every one of those turns would vanish from the count.

"## Dispatch" (role "D") counts as a turn (2026-07-25, subagent extraction). In a SUBAGENT
transcript the user-role string records are the ORCHESTRATING agent's brief, not Jon, so
convert-claude-code.py emits them under "## Dispatch". No existing wiki citation is affected
— subagent transcripts had never been extracted at all before this change — but the indexer
must recognize the header or every subagent file would index as Assistant-only. The distinct
role letter is the point: "D" is agent-authored instruction, never Jon's authority.

Usage:
  turn_index.py <raw>                 # summary: style + verified turn_count
  turn_index.py <raw> --json          # full T-map as JSON
  turn_index.py <raw> --line N        # which turn contains raw line N
  turn_index.py <raw> --turn K        # line range of turn K
  turn_index.py --self-test           # in-memory 2x2 fence-injection matrix
Headers inside fenced code / tool_result blocks are ignored (only true line-start headers count).

Fence detection (FIXED 2026-07-25 — turn-5 dispatch, "the fence detector inverts
protection"): the previous `FENCE = re.compile(r"^```")` was a naive PARITY TOGGLE —
every line starting with 3+ backticks flipped an in-fence boolean, regardless of how
many backticks it actually had. A 4-backtick wrapper fence (convert-claude-code.py's
fence_payload() escalates the wrapper past any backtick run already inside the
payload, precisely to survive a nested 3-backtick fence) and a 3-backtick inner
fence toggled IDENTICALLY under that regex, so the inner fence's close line could
flip the parser back OUT of the wrapper early — inverting protection for whatever
came after it. Measured 2x2 (ground truth 4 turns): header outside a nested fence
vs. inside one, crossed with a 3-backtick vs. 4-backtick wrapper — the naive toggle
got exactly one of those four cells right, by accident of line ordering, not by
correctness.

Fixed per CommonMark's own nesting rule: a fence closes ONLY on a line that is
itself a run of the SAME fence character with length >= the OPENING run's length
(optionally followed only by whitespace). A run shorter than the opening length —
e.g. a nested ``` inside a ```` wrapper — can never close the wrapper, so it (and
everything after it, up to the real closing line) stays protected regardless of
where inside the payload a bare header-shaped line happens to sit. _fence_mask()
below tracks the opening run length explicitly instead of a boolean.
"""
import re, sys, json, argparse

STYLES = {
    # The optional ` — [origin: …]` suffix is the speaker-provenance tag convert-claude-code.py
    # renders on `## Human` turns since 2026-08-21 (origin.kind carried from the JSONL record;
    # UNMARKED = field absent, which is UNKNOWN, never "machine"). Accepting it here is what
    # keeps turn numbering identical across tagged and untagged extracts — old files carry no
    # suffix and match exactly as before.
    "md":   re.compile(r"^##\s+(Human|Assistant|Compaction Boundary|Tool Result|Dispatch|Machine|Queue-operation)"
                       r"(?:\s+—\s+\[origin:[^\]]*\])?\s*$"),
    "bold": re.compile(r"^\*\*(Jon|Claude|Human|Assistant):?\*\*"),
}
ROLE = {"Human": "H", "Jon": "H", "Assistant": "A", "Claude": "A",
        "Compaction Boundary": "C", "Tool Result": "R", "Dispatch": "D"}

# A fence-opening line: a run of >=3 backticks, optionally followed by a non-backtick
# info string (language tag), consuming the WHOLE line. A fence-closing line: a run
# of >=3 backticks alone, optionally followed only by whitespace — nothing else.
FENCE_OPEN = re.compile(r"^(`{3,})([^`]*)$")
FENCE_CLOSE = re.compile(r"^(`{3,})\s*$")


def _fence_mask(lines):
    """Return a list of bools, one per line: True if that line must be excluded
    from header matching because it is the fence delimiter itself or lies inside
    an open fence. Run-length-aware (see module docstring) — a fence only closes
    on a same-or-longer run of the same character than the one that opened it, so
    a shorter nested fence can never leak the parser back out of an outer wrapper.
    """
    mask = []
    fence_run = 0  # 0 = not fenced; >0 = length of backtick run that opened it
    for ln in lines:
        s = ln.rstrip("\n").rstrip("\r")
        if fence_run:
            mask.append(True)
            m = FENCE_CLOSE.match(s)
            if m and len(m.group(1)) >= fence_run:
                fence_run = 0
            continue
        m = FENCE_OPEN.match(s)
        if m:
            fence_run = len(m.group(1))
            mask.append(True)
            continue
        mask.append(False)
    return mask


def index(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    mask = _fence_mask(lines)
    # count candidates per style outside fenced blocks to pick the dominant style
    counts = {k: 0 for k in STYLES}
    for ln, infence in zip(lines, mask):
        if infence: continue
        for k, rx in STYLES.items():
            if rx.match(ln): counts[k] += 1
    style = max(counts, key=counts.get)
    rx = STYLES[style]
    turns, t = [], 0
    for i, (ln, infence) in enumerate(zip(lines, mask), start=1):
        if infence: continue
        m = rx.match(ln)
        if m:
            t += 1
            turns.append({"t": t, "role": ROLE.get(m.group(1), "?"), "line": i})
    return {"file": path, "header_style": style, "style_counts": counts,
            "turn_count": t, "turns": turns, "total_lines": len(lines)}


def _matrix_fixture(wrapper_len, header_inside_nested):
    """Build one cell of the 2x2 injection matrix as literal markdown text.

    Ground truth: exactly 4 real turns (Human/Assistant/Human/Assistant). The
    Assistant turn's tool-result payload is wrapped in a fence of `wrapper_len`
    backticks. A fake '## Assistant' header line sits either INSIDE a nested
    marker or OUTSIDE it but still inside the outer wrapper — it must never be
    counted either way.

    wrapper_len mirrors the two states fence_payload() actually produces
    (`fence = max(3, max_run_in_payload + 1)`), so both matrix columns are
    states the real pipeline can reach — not an artificial combination:

      wrapper_len=3: the payload's own longest backtick run is <3 (no real
        fence inside it — e.g. inline double-backtick code like ``x``). The
        "nested" marker here is 2 backticks, which is NOT a fence at all per
        CommonMark (fences require >=3): this cell verifies short backtick
        runs are correctly ignored rather than misread as fence delimiters.

      wrapper_len=4: the payload's own longest run is exactly 3 (a genuine
        nested ``` fence), so fence_payload escalates the wrapper to 4 —
        strictly longer than the nested run, per its own doc comment. This
        cell verifies the real nested-fence case the corpus actually contains
        (agent-a8c9a0ace19099668.jsonl's own payload is exactly this shape).

      NOTE on the case this deliberately does NOT include: a wrapper equal in
      length to a genuine nested fence (3-vs-3) is not a turn_index.py defect
      to fix — it is CommonMark's own ambiguity (a same-length run always
      closes the outer fence, full stop; nesting equal-length fences has no
      correct reading). fence_payload's `+1` escalation exists precisely so
      the real pipeline never produces that state; turn_index.py's job is to
      correctly honor whatever length IS chosen, which this matrix verifies.
    """
    wrapper = "`" * wrapper_len
    nested = "``" if wrapper_len == 3 else "```"
    if header_inside_nested:
        payload = (
            f"{wrapper}\n"
            "intro text\n"
            f"{nested}\n"
            "## Assistant\n"
            "fake header, nested — must not count\n"
            f"{nested}\n"
            "trailing text\n"
            f"{wrapper}"
        )
    else:
        payload = (
            f"{wrapper}\n"
            "## Assistant\n"
            "fake header, outside the nested marker but inside the wrapper — must not count\n"
            f"{nested}\n"
            "nested marker content\n"
            f"{nested}\n"
            "trailing text\n"
            f"{wrapper}"
        )
    return (
        "## Human\n\nQuestion.\n\n---\n\n"
        f"## Assistant\n\nText before.\n\n[tool_result]\n\n{payload}\n\n---\n\n"
        "## Human\n\nThanks.\n\n---\n\n"
        "## Assistant\n\nYou're welcome.\n"
    )


def self_test():
    """2x2 fence-injection matrix (turn-5 dispatch, 2026-07-25). All four cells
    must report turn_count == 4 — a bare '## Assistant' line inside a tool-result
    payload must never be counted, regardless of nesting depth or wrapper length.
    """
    import tempfile
    from pathlib import Path

    results = {}
    for wrapper_len in (3, 4):
        for header_inside_nested in (False, True):
            text = _matrix_fixture(wrapper_len, header_inside_nested)
            tmp = Path(tempfile.mkdtemp()) / "fixture.md"
            tmp.write_text(text, encoding="utf-8")
            idx = index(str(tmp))
            key = (wrapper_len, header_inside_nested)
            results[key] = idx["turn_count"]

    for (wrapper_len, header_inside_nested), count in results.items():
        assert count == 4, (
            f"wrapper={wrapper_len} backticks, header_inside_nested={header_inside_nested}: "
            f"turn_index reports {count} turns, expected 4 (2x2 matrix: {results})"
        )

    print(f"self-test OK — 2x2 fence-injection matrix all report 4 turns: {results}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--line", type=int)
    ap.add_argument("--turn", type=int)
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.raw:
        ap.error("raw is required unless --self-test is passed")
    idx = index(a.raw)
    if a.line is not None:
        hit = None
        for tr in idx["turns"]:
            if tr["line"] <= a.line: hit = tr
            else: break
        print(f"line {a.line} -> {('T'+str(hit['t'])+' ('+hit['role']+', starts line '+str(hit['line'])+')') if hit else 'before T1'}")
        return
    if a.turn is not None:
        ts = idx["turns"]
        if 1 <= a.turn <= len(ts):
            start = ts[a.turn-1]["line"]
            end = ts[a.turn]["line"]-1 if a.turn < len(ts) else idx["total_lines"]
            print(f"T{a.turn} ({ts[a.turn-1]['role']}): raw lines {start}-{end}")
        else:
            print(f"T{a.turn} out of range (file has T1..T{len(ts)})")
        return
    if a.json:
        print(json.dumps(idx, indent=0)); return
    print(f"{idx['file']}")
    print(f"  header_style: {idx['header_style']}  (candidates: {idx['style_counts']})")
    print(f"  VERIFIED turn_count: {idx['turn_count']}   total_lines: {idx['total_lines']}")
    if idx["turns"]:
        print(f"  T1 @ line {idx['turns'][0]['line']} ... T{idx['turn_count']} @ line {idx['turns'][-1]['line']}")

if __name__ == "__main__":
    main()
