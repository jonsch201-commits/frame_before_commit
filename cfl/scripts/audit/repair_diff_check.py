#!/usr/bin/env python3
"""repair_diff_check.py -- tier-2 acceptance for a source-page REPAIR (UC-0, contract v1 section 3).

    python scripts/audit/repair_diff_check.py <before.md> <after.md>
    python scripts/audit/repair_diff_check.py --selftest

A repair MAY change: the frontmatter block (first `---` ... `---`), and, in the body, only lines
whose change is (a) adding/altering a `:T<n>` anchor, (b) adding/altering a fidelity tag
(`[measured]`, `[relayed]`, `[recalled]`, `[SEM]`, `[TRANSCRIPT:...]`, `[THINKING-SUMMARY:...]`,
`[MIRROR-INFERENCE]`, `[COMPACT-SUMMARY:...]`), or (c) converting a bare token into a `[[slug]]` link.
Everything else in the body -- quoted Jon text above all -- must be byte-identical. A deleted body
line is always a violation (no deletion).

Exit 0 = only allowed regions changed. Exit 1 = a forbidden change, listed. Exit 2 = unreadable.
Nothing is written.
"""
import difflib
import os
import re
import sys
import tempfile

ANCHOR_RE = re.compile(r'\[?:T\d+\]?|\[[0-9a-f]{6}:T\d+\]')
# UR-alt R-1 (2026-09-03): tag BODIES were unbounded (`TRANSCRIPT:[^\]]*`, free qualifier tail), so
# `[verbatim, Jon never said this and the claim is withdrawn]` was stripped before compare and PASSED.
# Bodies are now bounded: TRANSCRIPT/THINKING-SUMMARY/COMPACT-SUMMARY take a date-like stamp only; the
# E3 qualifier tail takes at most two words from a closed list. Anything else is substantive text.
_QUAL = r'(?:cropped|trimmed|excerpt|partial|elided|paraphrased|summarized|reconstructed)'
TAG_RE = re.compile(r'\[(?:measured|relayed|recalled|SEM|MIRROR-INFERENCE|'
                    r'(?:TRANSCRIPT|THINKING-SUMMARY|COMPACT-SUMMARY):[0-9]{4}-[0-9]{2}-[0-9]{2}[0-9T:Z.+\- ]{0,20}|'
                    r'(?:verbatim|paraphrase|reconstructed|contextual|inferred|uncaptured)(?:\s*,\s*' + _QUAL + r'){0,2})\]')
LINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]')


def split(text):
    lines = text.splitlines()
    if lines and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                return lines[:i + 1], lines[i + 1:]
    return [], lines


def normalise(line: str) -> str:
    """Strip every allowed-to-change token so two lines that differ ONLY in those compare equal."""
    s = ANCHOR_RE.sub('', line)
    s = TAG_RE.sub('', s)
    s = LINK_RE.sub(lambda m: m.group(1), s)   # [[slug]] -> slug ; [[slug|text]] -> slug
    return re.sub(r'\s+', ' ', s).strip()


def check(before: str, after: str):
    _, b_body = split(before)
    _, a_body = split(after)
    sm = difflib.SequenceMatcher(a=b_body, b=a_body, autojunk=False)
    violations = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        b_chunk, a_chunk = b_body[i1:i2], a_body[j1:j2]
        if tag == 'delete' or (tag == 'replace' and len(a_chunk) < len(b_chunk)):
            violations.append((i1 + 1, 'DELETED body line(s)', b_chunk[:2]))
            continue
        if tag == 'insert':
            # inserted lines are allowed only if they are pure anchor/tag/blank additions
            for ln in a_chunk:
                if normalise(ln):
                    violations.append((j1 + 1, 'INSERTED substantive line', [ln]))
            continue
        # replace with equal-or-more lines: pair them up and compare normalised
        for k, ln in enumerate(b_chunk):
            new = a_chunk[k] if k < len(a_chunk) else ''
            if normalise(ln) != normalise(new):
                violations.append((i1 + k + 1, 'CHANGED outside allowed regions', [ln, new]))
        for ln in a_chunk[len(b_chunk):]:
            if normalise(ln):
                violations.append((j1 + 1, 'INSERTED substantive line', [ln]))
    return violations


def run(before_path, after_path) -> int:
    try:
        b = open(before_path, encoding='utf-8', errors='replace').read()
        a = open(after_path, encoding='utf-8', errors='replace').read()
    except OSError as e:
        print(f'UNREADABLE: {e}')
        return 2
    v = check(b, a)
    for ln, why, ctx in v:
        print(f'  L{ln:<5} {why}')
        for c in ctx:
            print(f'         | {c[:140]}')
    print(f'REPAIR-DIFF: {len(v)} forbidden change(s)  ({os.path.basename(before_path)} -> {os.path.basename(after_path)})')
    print('FAIL' if v else 'PASS')
    return 1 if v else 0


def selftest() -> int:
    base = ('---\nkind: source\nraw_sha256: old\n---\n# Page\n\n## Key Claims\n- Jon said "their are gates" here.\n'
            '- A claim about stylomantic.\n')
    cases = [
        ('frontmatter + anchor + tag + link only',
         base.replace('raw_sha256: old', 'raw_sha256: new').replace('here.', 'here. [013850:T12] [measured]')
             .replace('stylomantic', '[[stylomantic]]'), 0),
        ('quoted Jon text edited', base.replace('their are', 'there are'), 1),
        ('body line deleted', base.replace('- A claim about stylomantic.\n', ''), 1),
        ('substantive line inserted', base + '- A brand new claim.\n', 1),
        ('identical', base, 0),
        ('R-1: prose smuggled inside a TRANSCRIPT tag', base.replace('here.', 'here. [TRANSCRIPT: and Jon retracted this the next day]'), 1),
        ('R-1: prose smuggled inside a verbatim qualifier', base.replace('here.', 'here. [verbatim, Jon never said this and the claim is withdrawn]'), 1),
        ('R-1 control: bounded tags still allowed', base.replace('here.', 'here. [TRANSCRIPT:2026-07-19] [verbatim, cropped]'), 0),
        ('lint E3 tag added (UC-0 dry-run class)', base.replace('here.', 'here. [paraphrase]').replace('stylomantic.', 'stylomantic. [verbatim, cropped]'), 0),
    ]
    ok = True
    with tempfile.TemporaryDirectory() as d:
        bp = os.path.join(d, 'before.md')
        open(bp, 'w', encoding='utf-8').write(base)
        for label, after, want in cases:
            ap = os.path.join(d, 'after.md')
            open(ap, 'w', encoding='utf-8').write(after)
            got = run(bp, ap)
            good = got == want
            ok = ok and good
            print(f"  [{'ok  ' if good else 'FAIL'}] {label}: exit {got} (want {want})")
    ran = len(cases)
    print(f'SELFTEST {"PASS" if ok else "FAIL"} {sum(1 for _ in cases) if ok else "?"}/{ran}')
    return 0 if ok else 1


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(run(sys.argv[1], sys.argv[2]))
