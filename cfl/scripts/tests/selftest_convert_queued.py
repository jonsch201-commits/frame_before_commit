#!/usr/bin/env python3
"""selftest_convert_queued.py — acceptance test for RP-27b (2026-09-02):
convert-claude-code.py must render Jon's mid-turn `queued_command` messages
and the `queue-operation` bookkeeping rows, and must leave every JSONL that
has neither byte-identical to the pre-RP-27b render.

This is the check Professional ran by hand on 2026-09-02 12:50, made into a
script so it can FAIL. Four parts:

  1. SYNTHETIC fixture (always runs, no real data): a user turn, an assistant
     turn, one attachment/queued_command with commandMode=prompt carrying a
     unique sentinel sentence, one with commandMode=task-notification, one
     queue-operation enqueue that echoes the sentinel bytes (as the harness
     really does), and one queue-operation remove carrying a Monitor-kill
     payload that never became a queued_command. Asserts, on the NEW converter:
       - the sentinel appears exactly once in the .md, and under `## Human (queued`
       - the task-notification text is rendered, and NOT under a Human heading
       - both queue-operation rows appear; the echo is a pointer (no repeat),
         the Monitor-kill payload is rendered in full
  2. OLD converter (`git show <old-ref>:<path>`): the same fixture renders the
     sentinel 0 times — proving the test can fail, and that the defect was real.
  3. DIFF-0: every CFL session JSONL under ~/.claude/projects/<CFL>/ with zero
     queued_command / queue-operation records is rendered by OLD and NEW; the
     primary .md AND the .sidecar.md must be byte-identical for each.
  4. REAL: session 9041f3b0 rendered by NEW; the sealed sentence from JSONL
     line 11509 ("I bet we don't even have the full knowledge base") must appear
     exactly once under a `## Human (queued` heading. The file-wide count is
     reported too: the compaction summary at line 11561 quotes the sentence
     (twice, as machine paraphrase under `## Compaction Boundary`) and that
     was already true of the OLD render — so file-wide is expected 3, of
     which exactly 1 is Jon's own turn.

Parts 3 and 4 need this machine's real JSONLs; a missing file is reported as
UNKNOWN and counts as a failure (UNKNOWN dominates PASS). Nothing is written
under raw/ or N:\\claude-corpus — outputs go to a tempdir.

Usage:
    python scripts/tests/selftest_convert_queued.py [--old-ref ff48bbbf] [--keep]
Exit 0 only if every check passes.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
CONVERTER_REL = 'skills/chat-exporter/scripts/convert-claude-code.py'
CONVERTER = os.path.join(REPO, *CONVERTER_REL.split('/'))
# Last commit on week-2026-09-02-corpus BEFORE the RP-27b converter change.
DEFAULT_OLD_REF = 'ff48bbbf'

CFL_PROJECT_DIR = os.path.join(
    os.path.expanduser('~'), '.claude', 'projects',
    'G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer')
REAL_JSONL = os.path.join(CFL_PROJECT_DIR, '9041f3b0-5102-4a06-a459-b076681a76bd.jsonl')
REAL_SENTINEL = "I bet we don't even have the full knowledge base"

SENTINEL = 'RP27B-SENTINEL the quick zebra typed this while the turn was still running'
TASK_NOTE = ('<task-notification>\n<task-id>bfixture01</task-id>\n<summary>Monitor event: '
             'RP27B-TASKNOTE fixture watch fired</summary>\n</task-notification>')
MONITOR_KILL = ('<task-notification>\n<task-id>bfixture02</task-id>\n<summary>Monitor event: '
                'RP27B-MONITORKILL this row never became a queued_command</summary>\n'
                '</task-notification>')

failures = []


def check(name, ok, detail=''):
    print('%s %s%s' % ('PASS' if ok else 'FAIL', name, (' — ' + str(detail)) if detail else ''))
    if not ok:
        failures.append(name)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def fixture_events():
    sid = 'fixture0-0000-4000-8000-000000000000'
    base = {'isSidechain': False, 'sessionId': sid, 'version': '2.1.251', 'cwd': 'C:\\fixture'}
    return [
        dict(base, type='user', uuid='u1', parentUuid=None, timestamp='2026-09-02T00:00:00.000Z',
             origin={'kind': 'human'},
             message={'role': 'user', 'content': 'Opening question from Jon about the converter.'}),
        dict(base, type='assistant', uuid='a1', parentUuid='u1', timestamp='2026-09-02T00:00:01.000Z',
             message={'role': 'assistant', 'model': 'claude-fable-5-1',
                      'content': [{'type': 'text', 'text': 'Working on it.'}]}),
        {'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': '2026-09-02T00:00:02.000Z',
         'sessionId': sid, 'content': SENTINEL},
        dict(base, type='attachment', uuid='q1', parentUuid='a1', timestamp='2026-09-02T00:00:03.000Z',
             attachment={'type': 'queued_command', 'prompt': SENTINEL, 'source_uuid': 'src-1',
                         'commandMode': 'prompt', 'origin': {'kind': 'human'},
                         'timestamp': '2026-09-02T00:00:03.000Z'}),
        dict(base, type='attachment', uuid='q2', parentUuid='q1', timestamp='2026-09-02T00:00:04.000Z',
             attachment={'type': 'queued_command', 'prompt': TASK_NOTE, 'source_uuid': 'src-2',
                         'commandMode': 'task-notification',
                         'timestamp': '2026-09-02T00:00:04.000Z'}),
        {'type': 'queue-operation', 'operation': 'remove', 'timestamp': '2026-09-02T00:00:05.000Z',
         'sessionId': sid, 'content': MONITOR_KILL, 'reason': 'absorbed_mid_turn'},
        {'type': 'queue-operation', 'operation': 'dequeue', 'timestamp': '2026-09-02T00:00:06.000Z',
         'sessionId': sid},
        dict(base, type='assistant', uuid='a2', parentUuid='q2', timestamp='2026-09-02T00:00:07.000Z',
             message={'role': 'assistant', 'model': 'claude-fable-5-1',
                      'content': [{'type': 'text', 'text': 'Done.'}]}),
    ]


def write_fixture(tmp):
    path = os.path.join(tmp, 'fixture0-0000-4000-8000-000000000000.jsonl')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for e in fixture_events():
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    return path


def run_converter(script, jsonl, out_dir):
    """Run one converter script on one JSONL; return (exit, primary_md_path, sidecar_path, stdout)."""
    os.makedirs(out_dir, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, script, '--run', jsonl, '--out', out_dir, '--force'],
                       capture_output=True, encoding='utf-8', errors='replace', env=env)
    md = sidecar = None
    for line in (r.stdout or '').splitlines():
        m = re.match(r'WROTE: (.+?\.md)\s', line)
        if m:
            p = m.group(1)
            if p.endswith('.sidecar.md'):
                sidecar = p
            else:
                md = p
    return r.returncode, md, sidecar, r.stdout + r.stderr


def heading_of(lines, idx):
    """Nearest `## ` heading at or above line idx (0-based)."""
    for i in range(idx, -1, -1):
        if lines[i].startswith('## '):
            return lines[i]
    return None


def occurrences(text, needle):
    lines = text.split('\n')
    hits = [(i, heading_of(lines, i)) for i, ln in enumerate(lines) if needle in ln]
    return hits


def old_converter_source(old_ref, tmp):
    r = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (old_ref, CONVERTER_REL)],
                       capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode('utf-8', 'replace')
    path = os.path.join(tmp, 'convert_old.py')
    with open(path, 'wb') as f:
        f.write(r.stdout)
    return path, ''


def has_queue_records(jsonl):
    n = 0
    with open(jsonl, encoding='utf-8', errors='replace') as f:
        for line in f:
            if '"queue-operation"' not in line and '"queued_command"' not in line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get('type') == 'queue-operation':
                n += 1
            elif e.get('type') == 'attachment' and (e.get('attachment') or {}).get('type') == 'queued_command':
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--old-ref', default=DEFAULT_OLD_REF,
                    help='git ref holding the pre-RP-27b converter (default %s)' % DEFAULT_OLD_REF)
    ap.add_argument('--keep', action='store_true', help='keep the tempdir and print its path')
    ap.add_argument('--skip-real', action='store_true',
                    help='skip parts 3-4 (reported as UNKNOWN = failure unless --allow-unknown)')
    ap.add_argument('--allow-unknown', action='store_true')
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix='rp27b-')
    print('tempdir:', tmp)
    print('converter (NEW):', CONVERTER, sha256_file(CONVERTER))

    # ---- 1. synthetic fixture on NEW ---------------------------------------
    fx = write_fixture(tmp)
    rc, md, sc, out = run_converter(CONVERTER, fx, os.path.join(tmp, 'new'))
    check('new: converter exit 0 on fixture', rc == 0, out.strip()[-300:] if rc else '')
    check('new: primary md written', bool(md), out.strip()[-300:] if not md else '')
    if md:
        text = open(md, encoding='utf-8').read()
        hits = occurrences(text, SENTINEL)
        check('new: prompt sentinel appears exactly once', len(hits) == 1, [h[1] for h in hits])
        check('new: sentinel sits under `## Human (queued`',
              bool(hits) and all(h[1] and h[1].startswith('## Human (queued') for h in hits),
              [h[1] for h in hits])
        check('new: sentinel heading names commandMode=prompt and origin human',
              bool(hits) and 'commandMode=prompt' in (hits[0][1] or '') and '[origin: human]' in (hits[0][1] or ''),
              hits[0][1] if hits else None)
        tn = occurrences(text, 'RP27B-TASKNOTE')
        check('new: task-notification text is rendered', len(tn) >= 1)
        check('new: task-notification is NOT under a Human heading',
              bool(tn) and all(h[1] and not h[1].startswith('## Human') for h in tn), [h[1] for h in tn])
        check('new: task-notification is under `## Machine (queued`',
              bool(tn) and all(h[1].startswith('## Machine (queued') for h in tn), [h[1] for h in tn])
        qo = [ln for ln in text.split('\n') if ln.startswith('## Queue-operation')]
        check('new: queue-operation rows appear (enqueue, remove, dequeue)',
              len(qo) == 3 and any('enqueue' in q for q in qo) and any('remove' in q for q in qo)
              and any('dequeue' in q for q in qo), qo)
        mk = occurrences(text, 'RP27B-MONITORKILL')
        check('new: Monitor-kill payload (never a queued_command) rendered in full under Queue-operation',
              len(mk) == 1 and mk[0][1].startswith('## Queue-operation'), [h[1] for h in mk])
        check('new: enqueue echo of the sentinel is a pointer, not a repeat',
              'not repeated here' in text)
        check('new: remove row carries reason', '- reason: absorbed_mid_turn' in text)
        check('new: real `## Human` turn still present', '## Human — [origin: human]' in text)
        if sc:
            sct = open(sc, encoding='utf-8').read()
            check('new: sidecar carries queued_commandMode rows', sct.count('- queued_commandMode:') == 2)
            check('new: sidecar carries queue_operation rows', sct.count('- queue_operation:') == 3)
            # Every `## ` line in the fixture body is a turn heading except the
            # `## Summary` placeholder (fixture payloads carry no `## ` lines).
            n_turn_headings = len([l for l in text.split('\n')
                                   if l.startswith('## ') and not l.startswith('## Summary')])
            check('new: sidecar turns_covered == primary turn-heading count (%d)' % n_turn_headings,
                  ('turns_covered: %d' % n_turn_headings) in sct)

    # ---- 2. OLD converter must render the sentinel 0 times -----------------
    old_path, err = old_converter_source(args.old_ref, tmp)
    check('old: `git show %s:%s` readable' % (args.old_ref, CONVERTER_REL), bool(old_path), err.strip())
    if old_path:
        print('converter (OLD):', args.old_ref, sha256_file(old_path))
        rc_o, md_o, sc_o, out_o = run_converter(old_path, fx, os.path.join(tmp, 'old'))
        check('old: converter exit 0 on fixture', rc_o == 0, out_o.strip()[-300:] if rc_o else '')
        if md_o:
            text_o = open(md_o, encoding='utf-8').read()
            check('old: sentinel appears 0 times (the defect was real; this test can fail)',
                  SENTINEL not in text_o)
            check('old: no `## Human (queued` heading', '## Human (queued' not in text_o)
            check('old: no `## Queue-operation` heading', '## Queue-operation' not in text_o)

    # ---- 3. DIFF-0 on every real JSONL with no queue records -----------------
    if args.skip_real:
        check('diff0: UNKNOWN (--skip-real)', args.allow_unknown)
        check('real: UNKNOWN (--skip-real)', args.allow_unknown)
    else:
        if not os.path.isdir(CFL_PROJECT_DIR) or not old_path:
            check('diff0: UNKNOWN — CFL project dir or old converter unavailable', args.allow_unknown,
                  CFL_PROJECT_DIR)
        else:
            baselines = sorted(f for f in os.listdir(CFL_PROJECT_DIR) if f.endswith('.jsonl')
                               and has_queue_records(os.path.join(CFL_PROJECT_DIR, f)) == 0)
            print('diff0: %d CFL session JSONLs with zero queued_command/queue-operation records' % len(baselines))
            identical = 0
            rendered = 0
            for f in baselines:
                j = os.path.join(CFL_PROJECT_DIR, f)
                rc_a, md_a, sc_a, _ = run_converter(old_path, j, os.path.join(tmp, 'd0old'))
                rc_b, md_b, sc_b, _ = run_converter(CONVERTER, j, os.path.join(tmp, 'd0new'))
                if not (md_a and md_b):
                    # e.g. a JSONL with no turns at all: both converters exit 1 identically
                    same = (rc_a == rc_b and md_a is None and md_b is None)
                else:
                    rendered += 1
                    same = (sha256_file(md_a) == sha256_file(md_b) and
                            os.path.basename(md_a) == os.path.basename(md_b) and
                            (sc_a is None) == (sc_b is None) and
                            (sc_a is None or sha256_file(sc_a) == sha256_file(sc_b)))
                if same:
                    identical += 1
                else:
                    print('   DIFF:', f, md_a, md_b)
            check('diff0: every zero-record JSONL renders byte-identical (md + sidecar) old vs new',
                  identical == len(baselines) and len(baselines) > 0,
                  '%d/%d identical (%d rendered, %d no-turn exits)' % (identical, len(baselines), rendered, len(baselines) - rendered))

        # ---- 4. REAL 9041f3b0 --------------------------------------------------
        if not os.path.isfile(REAL_JSONL):
            check('real: UNKNOWN — 9041f3b0 JSONL not on this machine', args.allow_unknown, REAL_JSONL)
        else:
            rc_r, md_r, sc_r, out_r = run_converter(CONVERTER, REAL_JSONL, os.path.join(tmp, 'real'))
            check('real: converter exit 0 on 9041f3b0', rc_r == 0, out_r.strip()[-300:] if rc_r else '')
            if md_r:
                text_r = open(md_r, encoding='utf-8').read()
                hits_r = occurrences(text_r, REAL_SENTINEL)
                under_h = [h for h in hits_r if h[1] and h[1].startswith('## Human (queued')]
                others = [h[1] for h in hits_r if h not in under_h]
                check('real: sealed sentence (JSONL:11509) appears exactly once under `## Human (queued`',
                      len(under_h) == 1, '%d under Human (queued); other hits under: %s' % (len(under_h), others))
                check('real: no other hit sits under a Human heading',
                      all(not (h[1] or '').startswith('## Human') for h in hits_r if h not in under_h), others)
                print('real: file-wide count = %d (%d Jon-typed, %d inside compaction/other blocks)'
                      % (len(hits_r), len(under_h), len(hits_r) - len(under_h)))
                print('real: md =', md_r, sha256_file(md_r))
                if sc_r:
                    print('real: sidecar =', sc_r, sha256_file(sc_r))

    print()
    if failures:
        print('FAILED %d check(s): %s' % (len(failures), failures))
    else:
        print('ALL PASS')
    if args.keep:
        print('kept:', tmp)
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
