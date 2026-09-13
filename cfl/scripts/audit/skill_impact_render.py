#!/usr/bin/env python3
"""
skill_impact_render.py — render wiki/skills-gate/skill-impact.md table.

Reads: wiki/skills-gate/LEDGER.md, skills/*/PURPOSE.md, wiki/skills-gate/validation/*/baseline.json,
       wiki/skills-gate/validation/*/blind-run1-full.json

Renders: wiki/skills-gate/skill-impact.md with frontmatter, table body, and checksums.

--check mode: render to memory, exit 1 if differs from on-disk file.
"""

import json
import os
import sys
import hashlib
import re
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def sha256_file(path):
    """Compute SHA256 of a file."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except (FileNotFoundError, IOError):
        return None

def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter from markdown."""
    if not content.startswith('---'):
        return {}
    lines = content.split('\n')[1:]
    fm = {}
    for line in lines:
        if line.strip() == '---':
            break
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"\'')
    return fm

def read_purpose_data(skill_name):
    """Read PURPOSE.md for a skill and extract frontmatter."""
    path = Path(f'skills/{skill_name}/PURPOSE.md')
    if not path.exists():
        return {
            'motivating_pattern': 'UNKNOWN',
            'r_best': 'UNKNOWN',
        }

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    fm = parse_yaml_frontmatter(content)
    return {
        'motivating_pattern': fm.get('motivating_pattern', 'UNKNOWN'),
        'r_best': fm.get('r_best', 'UNKNOWN'),
    }

def parse_ledger():
    """Parse LEDGER.md and extract proposal mappings and verdicts.

    Enforces G1 parity: every PROP index line must have a matching ## PROP-nnn section,
    and every ## PROP-nnn section must have a matching index line.

    Raises: RuntimeError if parity check fails, naming the offending PROP id.
    """
    proposals_by_skill = defaultdict(list)
    last_verdict_by_skill = {}
    skill_name_from_prop = {}
    index_props = set()
    section_props = set()

    with open('wiki/skills-gate/LEDGER.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract index line PROPs (- PROP-nnn)
    for line in content.split('\n'):
        if line.strip().startswith('- PROP-'):
            # Extract PROP id (e.g., "PROP-001" or "PROP-004 v2")
            prop_match = re.match(r'^- (PROP-\d+(?:\s+v\d+)?)', line)
            if prop_match:
                prop_id = prop_match.group(1).strip()
                index_props.add(prop_id)

                # Extract verdict (ACCEPTED/REJECTED)
                verdict = None
                if ' ACCEPTED' in line:
                    verdict = 'ACCEPTED'
                elif ' REJECTED' in line:
                    verdict = 'REJECTED'

                # Extract skill name from the line (CREATE|AMEND skills/skillname)
                skill_match = re.search(r'(?:CREATE|AMEND) skills/([a-z0-9-]+)', line)
                if skill_match:
                    skill_name = skill_match.group(1)
                    proposals_by_skill[skill_name].append(prop_id)
                    skill_name_from_prop[prop_id] = skill_name
                    if verdict:
                        last_verdict_by_skill[skill_name] = verdict

    # Extract section PROPs (## PROP-nnn)
    for line in content.split('\n'):
        section_match = re.match(r'^## (PROP-\d+(?:\s+v\d+)?)', line)
        if section_match:
            prop_id = section_match.group(1).strip()
            section_props.add(prop_id)

    # G1 Parity check: every index line must have a section, every section must have an index line
    orphan_index = index_props - section_props
    orphan_section = section_props - index_props

    if orphan_index:
        # Index line without matching section
        prop_id = sorted(orphan_index)[0]
        raise RuntimeError(f"G1 parity error: PROP index line {prop_id} has no matching section")

    if orphan_section:
        # Section without matching index line
        prop_id = sorted(orphan_section)[0]
        raise RuntimeError(f"G1 parity error: PROP section {prop_id} has no matching index line")

    return proposals_by_skill, last_verdict_by_skill

def read_validation_data(skill_name):
    """Read validation JSON files for a skill."""
    validation_dir = Path(f'wiki/skills-gate/validation/{skill_name}')

    data = {
        'R_blind': 'UNKNOWN',
        'R_degraded': 'UNKNOWN',
        'split_sha8': 'UNKNOWN',
        'last_regression_check': 'none',
    }

    # Read baseline.json
    baseline_path = validation_dir / 'baseline.json'
    if baseline_path.exists():
        try:
            with open(baseline_path, 'r', encoding='utf-8') as f:
                baseline = json.load(f)
            data['R_degraded'] = baseline.get('R_degraded', 'UNKNOWN')
            split_sha = baseline.get('split_sha256', '')
            if split_sha:
                data['split_sha8'] = split_sha[:8]
            # run_ts is the baseline measurement timestamp
            run_ts = baseline.get('run_ts')
            if run_ts:
                # Parse ISO timestamp and extract date
                data['last_regression_check'] = run_ts.split('T')[0]
        except (json.JSONDecodeError, IOError):
            pass

    # Read blind-run1-full.json
    blind_path = validation_dir / 'blind-run1-full.json'
    if blind_path.exists():
        try:
            with open(blind_path, 'r', encoding='utf-8') as f:
                blind = json.load(f)
            data['R_blind'] = blind.get('R', 'UNKNOWN')
            # Prefer blind run timestamp if available
            meta = blind.get('meta', {})
            run_ts = meta.get('run_ts')
            if run_ts:
                data['last_regression_check'] = run_ts.split('T')[0]
        except (json.JSONDecodeError, IOError):
            pass

    return data

def get_all_skills():
    """Get list of all skills with SKILL.md files."""
    skills = []
    skills_dir = Path('skills')
    for item in sorted(skills_dir.iterdir()):
        if item.is_dir():
            skill_md = item / 'SKILL.md'
            if skill_md.exists():
                skills.append(item.name)
    return skills

def render_table(skills_data):
    """Render markdown table from skills data."""
    # Header
    lines = [
        "| skill | proposals | last verdict | R_best | R_blind | R_degraded | split sha8 | motivating_pattern | last regression check |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    # Rows (one per skill)
    for skill_name in sorted(skills_data.keys()):
        data = skills_data[skill_name]

        # Format cells
        skill_cell = data['skill_name']
        proposals_cell = ', '.join(data['proposals']) if data['proposals'] else '—'
        verdict_cell = data['last_verdict'] if data['last_verdict'] else '—'
        r_best_cell = str(data['r_best']) if data['r_best'] != 'UNKNOWN' else '—'
        r_blind_cell = str(round(data['R_blind'], 4)) if data['R_blind'] != 'UNKNOWN' else '—'
        r_degraded_cell = str(round(data['R_degraded'], 4)) if data['R_degraded'] != 'UNKNOWN' else '—'
        split_sha8_cell = data['split_sha8'] if data['split_sha8'] != 'UNKNOWN' else '—'
        motivating_cell = data['motivating_pattern'] if data['motivating_pattern'] else '—'
        regression_cell = data['last_regression_check'] if data['last_regression_check'] else '—'

        line = f"| {skill_cell} | {proposals_cell} | {verdict_cell} | {r_best_cell} | {r_blind_cell} | {r_degraded_cell} | {split_sha8_cell} | {motivating_cell} | {regression_cell} |"
        lines.append(line)

    return '\n'.join(lines)

def render_file(skills, proposals_by_skill, last_verdict_by_skill, skills_data):
    """Render the complete skill-impact.md file with frontmatter."""

    table_body = render_table(skills_data)

    # Compute checksums
    ledger_sha = sha256_file('wiki/skills-gate/LEDGER.md')
    body_sha = hashlib.sha256(table_body.encode('utf-8')).hexdigest()

    # Build frontmatter
    now_ts = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
    frontmatter = f"""---
format: cfl-page/v1
kind: reference
slug: skill-impact
generated_by: scripts/audit/skill_impact_render.py
rendered_at: {now_ts}Z
source_ledger_sha256: {ledger_sha}
rendered_sha256: {body_sha}
_note: This file is auto-generated. Do not hand-edit.
---

"""

    # Build full content
    content = frontmatter + table_body

    return content, body_sha, ledger_sha

def main():
    """Main entry point."""
    # cp1252-class guard: this file's own em-dash cells/messages have raised
    # UnicodeEncodeError on a native Windows console (non-utf8 stdout). Same
    # fix already applied to five other files today.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')

    check_mode = '--check' in sys.argv

    # Get all skills with SKILL.md
    skills = get_all_skills()
    if len(skills) == 0:
        print("ERROR: get_all_skills() found zero skills — walk likely broken "
              "(wrong cwd, missing skills/ dir, or empty glob)", file=sys.stderr)
        sys.exit(1)
    # Cross-check against an independently-computed enumeration of the same
    # source of truth (skills/*/SKILL.md) so a partial/broken walk in
    # get_all_skills() is caught without pinning the count to a magic number
    # that goes stale the next time a skill is added or removed.
    independent_skills = sorted(p.parent.name for p in Path('skills').glob('*/SKILL.md'))
    if sorted(skills) != independent_skills:
        only_in_walk = sorted(set(skills) - set(independent_skills))
        only_in_glob = sorted(set(independent_skills) - set(skills))
        print(
            "ERROR: get_all_skills() disagrees with an independent skills/*/SKILL.md glob "
            f"({len(skills)} vs {len(independent_skills)}). "
            f"only in get_all_skills(): {only_in_walk}; only in glob: {only_in_glob}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse LEDGER for proposals and verdicts
    try:
        proposals_by_skill, last_verdict_by_skill = parse_ledger()
    except RuntimeError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Build skills data
    skills_data = {}
    for skill_name in skills:
        purpose_data = read_purpose_data(skill_name)
        validation_data = read_validation_data(skill_name)

        skills_data[skill_name] = {
            'skill_name': skill_name,
            'proposals': proposals_by_skill.get(skill_name, []),
            'last_verdict': last_verdict_by_skill.get(skill_name, '—'),
            'r_best': purpose_data['r_best'],
            'R_blind': validation_data['R_blind'],
            'R_degraded': validation_data['R_degraded'],
            'split_sha8': validation_data['split_sha8'],
            'motivating_pattern': purpose_data['motivating_pattern'],
            'last_regression_check': validation_data['last_regression_check'],
        }

    # Render file
    content, body_sha, ledger_sha = render_file(skills, proposals_by_skill, last_verdict_by_skill, skills_data)

    output_path = Path('wiki/skills-gate/skill-impact.md')

    if check_mode:
        # Check if file differs
        if output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                existing = f.read()
            if existing == content:
                print("OK: skill-impact.md up to date")
                sys.exit(0)
            else:
                print("FAIL: skill-impact.md differs from rendered content")
                sys.exit(1)
        else:
            print("FAIL: skill-impact.md does not exist")
            sys.exit(1)
    else:
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Print summary
        print(f"Rendered {len(skills)} skills to {output_path}")
        print(f"Body SHA256: {body_sha}")
        print(f"Ledger SHA256: {ledger_sha}")

if __name__ == '__main__':
    main()
