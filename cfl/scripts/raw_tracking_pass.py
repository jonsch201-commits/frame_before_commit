#!/usr/bin/env python3
"""
raw_tracking_pass.py — frontmatter-tag-aware classifier for the raw/ git-tracking policy
defined in raw/references/raw-file-standards.md v2.0 ("Git-Tracking Policy" section).

Why not a path-based rule alone: raw/sessions/claude-code/ has ~50 pre-existing flat files
(grandfathered — never moved into domain subfolders) whose domain is only knowable from their
`project:` frontmatter tag, not their path. This script reads that tag before classifying.

Categories (mirrors the PR-body reporting contract for the raw-sources-standardization plan):
  tracked_fl            — raw/sessions/fl/**, raw/sessions/how-to-use-claude/**, CC flat/subfoldered
                           files tagged fl (including the legacy value "Claude Foundational Layer")
                           or research (lean-track per plan)
  tracked_references     — raw/references/**
  tracked_intake          — raw/intake/** except files on FRIEND_PRIVACY_HOLD
  held_home_pending_confirm — raw/sessions/home/** (plan: "lean track" but flag, don't decide)
  excluded_personal      — raw/sessions/personal/**, CC files tagged/evidenced personal
  excluded_pro            — raw/sessions/pro/**, CC files tagged/evidenced pro
  held_unrouted           — new-sessions/, unassigned/, CC files with no project tag, and any
                           raw/ top-level directory this policy does not name at all
  excluded_archival_binary — Anthropic_zips/, jsonl-archive/, jsonl-backup/, _deprecated/,
                           Archive_20260526/, intake-archive/, agent-status/, tmp/ (binary or
                           "wrong tool for git" per the plan — reported for transparency, not
                           one of the plan's 7 named categories)
  held_flagged            — files requiring a specific one-off human confirm regardless of any
                           other rule (currently: the friend_privacy intake file)

Usage:
  python raw_tracking_pass.py                       # report only, no writes
  python raw_tracking_pass.py --apply --dest-root D  # copy trackable files into D (a worktree),
                                                       # preserving their raw/... relative path,
                                                       # and print the exact list to `git add`.
                                                       # Never copies held_*/excluded_* files.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")
RAW = ROOT / "raw"

# Files that need a specific one-off human confirm before tracking, regardless of directory
# policy. Keyed by path relative to ROOT. Value is the reason, surfaced in the report.
HELD_FLAGGED = {
    "raw/intake/2026-07-16-jon-moral-hierarchy-DISCORD-GROUND-TRUTH.md":
        "friend_privacy frontmatter field — names/describes a third party; already tracked in "
        "main as of commit ea4df6b (prior session), not newly added by this pass — flagged per "
        "policy regardless of prior tracking status.",
}

# Unconditionally excluded top-level raw/ subtrees (binary or archival — "wrong tool for git").
EXCLUDED_ARCHIVAL_DIRS = {
    "Anthropic_zips", "_deprecated", "Archive_20260526", "intake-archive", "agent-status", "tmp",
}

# CC flat-file project-tag values that mean "fl" (includes the pre-taxonomy legacy free-text value).
FL_TAG_VALUES = {"fl", "Claude Foundational Layer"}
RESEARCH_TAG_VALUES = {"research"}
PRO_TAG_VALUES = {"pro"}


def read_frontmatter_field(path, field):
    """Return the value of a top-level `field:` line in the file's YAML frontmatter, or ''."""
    try:
        with path.open('r', encoding='utf-8', errors='replace') as f:
            in_fm = False
            for i, line in enumerate(f):
                if i == 0 and line.strip() == '---':
                    in_fm = True
                    continue
                if in_fm and line.strip() == '---':
                    break
                if in_fm and line.startswith(f'{field}:'):
                    return line.split(':', 1)[1].strip()
                if i > 60:  # frontmatter is always short; don't scan the whole file
                    break
    except OSError:
        pass
    return ''


def classify_cc_flat(path):
    """Classify a raw/sessions/claude-code/*.md flat (grandfathered) file by its project tag."""
    rel = str(path.relative_to(ROOT)).replace('\\', '/')
    if rel in HELD_FLAGGED:
        return 'held_flagged', HELD_FLAGGED[rel]
    tag = read_frontmatter_field(path, 'project')
    if tag in FL_TAG_VALUES:
        return 'tracked_fl', f'project: {tag or "(none)"}'
    if tag in RESEARCH_TAG_VALUES:
        return 'tracked_fl', f'project: {tag} (research, lean-track)'
    if tag in PRO_TAG_VALUES:
        return 'excluded_pro', f'project: {tag}'
    if not tag:
        return 'held_unrouted', 'no project: frontmatter tag — content not classifiable by policy'
    return 'held_unrouted', f'unrecognized project tag {tag!r} — not fl/research/pro'


def classify_cc_subfoldered(path):
    """Classify a NEW (Phase-2) raw/sessions/claude-code/{fl,pro,research}/** file by folder name."""
    parts = path.relative_to(RAW / "sessions" / "claude-code").parts
    folder = parts[0] if parts else ''
    if folder in ('jsonl-archive', 'jsonl-backup'):
        return 'excluded_archival_binary', f'{folder}/ — raw JSONL backup, wrong tool for git'
    if folder == 'fl':
        return 'tracked_fl', 'domain-subfoldered fl/'
    if folder == 'research':
        return 'tracked_fl', 'domain-subfoldered research/ (lean-track)'
    if folder == 'pro':
        return 'excluded_pro', 'domain-subfoldered pro/'
    return 'held_unrouted', f'unrecognized claude-code subfolder {folder!r}'


def classify(path):
    """Return (category, reason) for one file under raw/."""
    rel = path.relative_to(RAW)
    top = rel.parts[0]
    rel_str = str(path.relative_to(ROOT)).replace('\\', '/')

    if rel_str in HELD_FLAGGED:
        return 'held_flagged', HELD_FLAGGED[rel_str]

    if top == 'references':
        return 'tracked_references', 'raw/references/**'

    if top == 'intake':
        return 'tracked_intake', 'raw/intake/**'

    if top in EXCLUDED_ARCHIVAL_DIRS:
        return 'excluded_archival_binary', f'{top}/ — binary/archival, not named in the plan\'s Track list'

    if top == 'sessions':
        sub = rel.parts[1] if len(rel.parts) > 1 else ''
        if sub == 'fl':
            return 'tracked_fl', 'raw/sessions/fl/**'
        if sub == 'how-to-use-claude':
            return 'tracked_fl', 'raw/sessions/how-to-use-claude/** (fl-adjacent per plan)'
        if sub == 'personal':
            return 'excluded_personal', 'raw/sessions/personal/**'
        if sub == 'pro':
            return 'excluded_pro', 'raw/sessions/pro/**'
        if sub == 'home':
            return 'held_home_pending_confirm', 'raw/sessions/home/** — plan says "lean track" but flags for confirm'
        if sub in ('new-sessions', 'unassigned'):
            return 'held_unrouted', f'raw/sessions/{sub}/** — not yet domain-routed'
        if sub == 'claude-code':
            # rel.parts = ('sessions', 'claude-code', filename) for a flat (grandfathered) file —
            # 3 parts. A file inside a claude-code subdirectory (fl/pro/research/jsonl-archive/
            # jsonl-backup) has a 4th part: ('sessions', 'claude-code', subdir, filename).
            if len(rel.parts) > 3:
                return classify_cc_subfoldered(path)
            return classify_cc_flat(path)
        return 'held_unrouted', f'raw/sessions/{sub}/** — not named in the plan\'s Track/Don\'t-track list'

    # Anything else directly under raw/ that the plan never named (Jon Private md files,
    # Jon Test Cases tbd, not in zip maybe, exports, fbc, stylomantic, general, EXPORT-LOG.md,
    # sessions/skip-registry.md-adjacent files, etc.) — safe default: don't track, surface it.
    return 'held_unrouted', f'raw/{top}/... — not enumerated in raw-file-standards.md v2.0 Track/Don\'t-track lists'


def walk_raw():
    for p in sorted(RAW.rglob('*')):
        if p.is_file():
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='Copy tracked_* files into --dest-root, preserving raw/... path')
    ap.add_argument('--dest-root', help='Worktree root to copy into (required with --apply)')
    ap.add_argument('--list-category', help='Print every file in one category (for spot-checking)')
    args = ap.parse_args()

    if args.apply and not args.dest_root:
        sys.exit('ERROR: --apply requires --dest-root')

    buckets = {}
    for path in walk_raw():
        cat, reason = classify(path)
        buckets.setdefault(cat, []).append((path, reason))

    if args.list_category:
        for path, reason in buckets.get(args.list_category, []):
            print(f'{path.relative_to(ROOT)}  —  {reason}')
        return

    print("=== raw/ tracking-pass classification ===\n")
    order = ['tracked_fl', 'tracked_references', 'tracked_intake', 'held_home_pending_confirm',
             'excluded_personal', 'excluded_pro', 'held_unrouted', 'excluded_archival_binary',
             'held_flagged']
    for cat in order:
        items = buckets.get(cat, [])
        print(f'{cat}: {len(items)}')
    other = set(buckets) - set(order)
    for cat in other:
        print(f'{cat} (unclassified category!): {len(buckets[cat])}')
    print(f'\nTOTAL files under raw/: {sum(len(v) for v in buckets.values())}')

    if args.apply:
        to_add = []
        for cat in ('tracked_fl', 'tracked_references', 'tracked_intake'):
            for path, reason in buckets.get(cat, []):
                rel = path.relative_to(ROOT)
                dest = Path(args.dest_root) / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(path.read_bytes())
                to_add.append(str(rel).replace('\\', '/'))
        print(f'\n--apply: copied {len(to_add)} file(s) into {args.dest_root}')
        manifest_path = Path(args.dest_root) / '_raw_tracking_pass_add_list.txt'
        manifest_path.write_text('\n'.join(to_add) + '\n', encoding='utf-8')
        print(f'Manifest of paths to `git add` written to {manifest_path}')


if __name__ == '__main__':
    main()
