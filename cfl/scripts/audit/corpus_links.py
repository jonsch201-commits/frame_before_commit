#!/usr/bin/env python3
"""corpus_links.py — the two capture measurements the standard update had no row for.

WHY THIS EXISTS
---------------
Jon audited the 2026-08-03 standard update and found two gaps. Both were real, both had
been true for over a week, and NEITHER APPEARED IN ANY INSTRUMENT — su_close.sh had
capture rows and wiki rows and no temporal row and no link row. Fixing the extractor and
stopping there would have left the next session to rediscover the same two facts by hand.
So the fix and its instrument land together:

  temporal.subagents   — subagent extracts carrying per-turn timestamps, over all subagent
                         extracts. The extract a future session reads had NO turn-level
                         time at all: a citation into one could say only
                         [TRANSCRIPT:session-date] while the JSONL knew the minute.

  links.bidirectional  — extracts whose parent/child link block is CORRECT, over extracts
                         that should have one. All 14 subagent extracts of the audited
                         session named their parent; nothing named the children, and
                         nothing named siblings.

HOW `links.bidirectional` AVOIDS BEING SATISFIABLE BY EDITING A RECORD
----------------------------------------------------------------------
su_close.sh's property 3 says no check may read a number a previous run wrote down. A link
block IS text written into a file, so verifying "a block is present" would violate that
outright — a hand-typed block would pass. Instead this re-derives the block THIS FILE
SHOULD CARRY, using the extractor's own `corpus_link_block()` against the corpus on disk,
and compares. The only edit that passes is the one the deriver would have made, so the
record cannot be edited into compliance; it can only be made correct.

Importing the extractor rather than reimplementing its rules is the same discipline: two
copies of "what a correct link looks like" would be one more fact written down twice and
then diverging with nothing able to notice.

WHAT COUNTS AS A PER-TURN TEMPORAL RECORD
-----------------------------------------
The companion `<stem>.sidecar.md` must exist AND actually carry per-turn timestamps — a
present-but-empty sidecar is the "detection proxy lies" failure (`md✗` was not a capture
signal either). So the file is opened and its `- timestamp:` rows counted; zero rows is a
MISS, not a hit, and the sidecar's own `turns_covered:` is not taken on trust.

Usage:
  python scripts/audit/corpus_links.py [--repo DIR] [--json]
  python scripts/audit/corpus_links.py --self-test

Output (stdout, one metric per line, `name: value / denominator`):
  temporal.subagents: 583 / 583
  links.bidirectional: 688 / 688

Exit: 0 measured cleanly
      2 could not run (corpus absent, extractor unimportable, empty denominator)
        — an unrunnable check is UNKNOWN, never a pass.
"""

# --- cp1252 guard, added 2026-09-11 ------------------------------------------------
# This script's own output carries em-dashes and warning glyphs. On this machine Python's
# stdout is cp1252 when piped, so a bare print() of them raises UnicodeEncodeError and the
# whole run dies AFTER doing its work -- the measurement is taken and then thrown away.
#
# Confirmed live here: `corpus_links.py --help` crashed with UnicodeEncodeError at 19:5x.
# Soul reported the same crash killing federated_query.py --help in Personal the same hour,
# and it took out my own consult extraction at 19:0x.
#
# errors='replace' rather than 'strict': a glyph that will not encode should degrade to '?'
# and let the measurement through. Losing a character is a cosmetic defect; losing the run
# is a measurement defect, and only one of those is worth crashing over.
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    _sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass  # older interpreters, or a stream that does not support it -- never fatal


import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

TIMESTAMP_ROW = re.compile(r'^- timestamp: (?!\(absent\))\S', re.M)


def load_extractor(repo):
    """Import extract_claude_code_sessions.py from `repo` as a module.

    By path, not by package name: this must measure the checkout it was pointed at, and
    a plain `import` would silently pick up whichever copy happened to be importable —
    the exact CODE_ROOT/ROOT split that once paired a new extractor with an old converter
    and reported 376 successful files rendered by the wrong parser.
    """
    p = Path(repo) / 'scripts' / 'extract_claude_code_sessions.py'
    if not p.is_file():
        return None
    spec = importlib.util.spec_from_file_location('_cl_extractor', p)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    # CAPABILITY GATE, not a version string — the same guard the extractor itself uses
    # before trusting the converter. An extractor that predates the link pass imports
    # perfectly well and then raises AttributeError deep inside measure(), which would
    # surface as a confusing traceback rather than as "this check could not run". A
    # partial deploy (instrument merged, extractor not) must read UNKNOWN, loudly.
    for attr in ('scan_corpus_relations', 'corpus_link_block', 'sidecar_for',
                 'LINK_BEGIN', 'LINK_END', 'OUT_DIR'):
        if not hasattr(mod, attr):
            print(f'ERROR: {p} predates bidirectional corpus links — missing {attr!r}. '
                  f'This check cannot run against it.', file=sys.stderr)
            return None
    return mod


def sidecar_has_turn_times(md, X):
    """True when the extract's companion exists and holds >=1 real per-turn timestamp."""
    side = X.sidecar_for(md)
    if not side.is_file():
        return False
    try:
        return bool(TIMESTAMP_ROW.search(side.read_text(encoding='utf-8', errors='replace')))
    except OSError:
        return False


def measure(X):
    """Return (metrics dict, misses dict). X is the loaded extractor module."""
    primaries, children = X.scan_corpus_relations()
    kids = [p for v in children.values() for p, _ in v]
    every = list(primaries.values()) + kids

    temporal_ok, temporal_miss = 0, []
    for md in kids:
        if sidecar_has_turn_times(md, X):
            temporal_ok += 1
        else:
            temporal_miss.append(md)

    links_ok, links_miss = 0, []
    for md in every:
        want = X.corpus_link_block(md, primaries, children)
        try:
            text = md.read_text(encoding='utf-8', errors='replace')
        except OSError:
            links_miss.append(md)
            continue
        start = text.find(X.LINK_BEGIN)
        end = text.find(X.LINK_END, start) if start != -1 else -1
        have = text[start:end + len(X.LINK_END)] if end != -1 else ''
        if have == want:
            links_ok += 1
        else:
            links_miss.append(md)

    return (
        {'temporal.subagents': (temporal_ok, len(kids)),
         'links.bidirectional': (links_ok, len(every))},
        {'temporal.subagents': temporal_miss, 'links.bidirectional': links_miss},
    )


def self_test():
    """Prove BOTH metrics can FAIL. A guard that has never fired is not known to work.

    Built against a real temporary corpus with real files, then damaged three ways:
    a removed sidecar, a sidecar present but carrying no timestamps (the detection-proxy
    trap), and a hand-edited link block (the record-editing trap).
    """
    import tempfile, shutil
    fails = []

    def t(name, expected, actual):
        ok = expected == actual
        print(f'  {name:<58} {"PASS" if ok else f"FAIL (want {expected} got {actual})"}')
        if not ok:
            fails.append(name)

    repo = Path(__file__).resolve().parents[2]
    X = load_extractor(repo)
    if X is None:
        print('  cannot import extractor — self-test cannot run')
        return 2

    tmp = Path(tempfile.mkdtemp())
    try:
        X.OUT_DIR = tmp
        (tmp / 'fl').mkdir(parents=True)
        (tmp / 'subagents' / 'aaaaaa').mkdir(parents=True)
        parent = tmp / 'fl' / 'code-2026-08-03-aaaaaa-parent.md'
        child = tmp / 'subagents' / 'aaaaaa' / 'code-2026-08-03-bbbbbb-child.md'
        for f in (parent, child):
            f.write_text('---\nsource_id: x\ndate: 2026-08-03\n---\n\n'
                         '# Title\n\n## Summary\n\ntext\n\n---\n\n## Human\n\nhi\n',
                         encoding='utf-8')
        for f in (parent, child):
            X.sidecar_for(f).write_text(
                '---\nturns_covered: 1\n---\n\n### T1 — Human\n\n'
                '- timestamp: 2026-08-03T00:00:00.000Z\n- model: (none)\n', encoding='utf-8')

        # Undamaged corpus, links applied -> both metrics whole.
        X.write_corpus_links()
        m, _ = measure(X)
        t('baseline temporal 1/1', (1, 1), m['temporal.subagents'])
        t('baseline links 2/2', (2, 2), m['links.bidirectional'])

        # NEGATIVE CONTROL 1 — the exact defect this row was added for: a subagent
        # extract with no per-turn temporal companion at all.
        X.sidecar_for(child).unlink()
        m, _ = measure(X)
        t('NEG temporal: sidecar removed -> 0/1', (0, 1), m['temporal.subagents'])

        # NEGATIVE CONTROL 2 — detection proxies lie. A sidecar that EXISTS but carries
        # no real timestamp must not count; presence is not the signal.
        X.sidecar_for(child).write_text(
            '---\nturns_covered: 900\n---\n\n### T1 — Human\n\n- timestamp: (absent)\n',
            encoding='utf-8')
        m, _ = measure(X)
        t('NEG temporal: empty sidecar is a MISS -> 0/1', (0, 1), m['temporal.subagents'])

        # NEGATIVE CONTROL 3 — a broken link. The parent extract is renamed, so the
        # child's recorded link points at a file that is not there.
        # 0/2, not 1/2: the first draft of this control asserted 1/2 and the instrument
        # said 0/2 — the instrument was right. A rename invalidates BOTH sides at once
        # (the child's back-link AND the parent's own companion reference), which is
        # exactly the bidirectionality this row exists to enforce. The expectation was
        # corrected to the measurement, not the other way round.
        parent.rename(parent.with_name('code-2026-08-03-aaaaaa-renamed.md'))
        m, _ = measure(X)
        t('NEG links: parent renamed breaks BOTH sides -> 0/2', (0, 2),
          m['links.bidirectional'])

        # NEGATIVE CONTROL 4 — the record-editing trap. A hand-typed block that LOOKS
        # right must not pass; only the derived block does.
        X.write_corpus_links()
        m, _ = measure(X)
        t('links repaired by re-derivation -> 2/2', (2, 2), m['links.bidirectional'])
        txt = child.read_text(encoding='utf-8')
        child.write_text(txt.replace('**Parent session:**', '**Parent session (edited):**'),
                         encoding='utf-8')
        m, _ = measure(X)
        t('NEG links: hand-edited block does NOT pass -> 1/2', (1, 2), m['links.bidirectional'])

        # NEGATIVE CONTROL 5 — an empty corpus must produce an EMPTY DENOMINATOR, which
        # su_close.sh classifies UNKNOWN. It must never read as a clean 0/0 pass here.
        empty = Path(tempfile.mkdtemp())
        X.OUT_DIR = empty
        m, _ = measure(X)
        t('NEG empty corpus -> 0/0 denominators', (0, 0), m['links.bidirectional'])
        t('NEG empty corpus -> temporal 0/0', (0, 0), m['temporal.subagents'])
        shutil.rmtree(empty, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        print(f'RESULT: FAIL — {len(fails)} case(s). Do not trust this instrument.')
        return 1
    print('RESULT: PASS — both metrics were made to fail on a removed companion, on a')
    print('        present-but-empty companion, on a broken link, and on a hand-edited')
    print('        record. They are known to work because they were made to fire.')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--list-misses', action='store_true',
                    help='print the paths behind each shortfall (paths only, never content)')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    X = load_extractor(args.repo)
    if X is None:
        print(f'ERROR: could not import the extractor from {args.repo}', file=sys.stderr)
        sys.exit(2)
    if not X.OUT_DIR.is_dir():
        print(f'ERROR: corpus not present at {X.OUT_DIR}', file=sys.stderr)
        sys.exit(2)

    metrics, misses = measure(X)
    if args.json:
        print(json.dumps({k: {'value': v, 'denominator': d}
                          for k, (v, d) in metrics.items()}, indent=2))
    else:
        for k, (v, d) in metrics.items():
            print(f'{k}: {v} / {d}')
    if args.list_misses:
        for k, paths in misses.items():
            for p in paths:
                print(f'MISS {k} {p}', file=sys.stderr)

    # An empty denominator is not a pass. su_close.sh enforces that too, but an
    # instrument that shrugs at measuring nothing is how a clean zero gets believed.
    if any(d == 0 for _, d in metrics.values()):
        print('ERROR: empty denominator — nothing was measured, which is not a pass.',
              file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == '__main__':
    main()
