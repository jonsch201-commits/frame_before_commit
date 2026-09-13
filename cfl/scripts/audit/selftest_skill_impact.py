#!/usr/bin/env python3
"""
selftest_skill_impact.py — selftest suite for skill_impact_render.py

Tests:
(a) render with LEDGER copy that has one extra PROP index line without a section: must FAIL
(b) render normal: rows == count of skills/*/SKILL.md (derived, not hardcoded)
(c) modify one PURPOSE.md r_best in scratch and assert rendered row changes
"""

import json
import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def run_render_script(cwd='N:\\claude-cfl\\clone'):
    """Run the render script and return (exit code, stdout, stderr)."""
    result = subprocess.run(
        ['python3', 'scripts/audit/skill_impact_render.py'],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def count_table_rows(content):
    """Count table data rows (skip header rows)."""
    lines = content.strip().split('\n')
    # Skip frontmatter and header
    in_table = False
    row_count = 0
    for line in lines:
        if line.startswith('|') and not in_table:
            in_table = True
            continue
        if in_table and line.startswith('|'):
            # Skip separator rows (all dashes and pipes)
            if '---' not in line:
                row_count += 1
    return row_count

def test_parity_check():
    """Test (a): render with LEDGER that has extra PROP index line without a section.

    Must FAIL (exit 1) with parity error, and skill-impact.md must NOT be created/updated.
    """
    print("Test (a): Parity check on malformed LEDGER...")

    # Create temp directory
    tmpdir = tempfile.mkdtemp()
    try:
        # Copy clone to temp
        clone_path = 'N:\\claude-cfl\\clone'
        temp_clone = os.path.join(tmpdir, 'clone')
        shutil.copytree(clone_path, temp_clone)

        # Record baseline skill-impact.md timestamp
        output_path = os.path.join(temp_clone, 'wiki', 'skills-gate', 'skill-impact.md')
        baseline_mtime = os.path.getmtime(output_path) if os.path.exists(output_path) else None
        baseline_content = None
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                baseline_content = f.read()

        # Create malformed LEDGER with extra PROP index line without a matching section
        ledger_path = os.path.join(temp_clone, 'wiki', 'skills-gate', 'LEDGER.md')
        with open(ledger_path, 'r', encoding='utf-8') as f:
            ledger_content = f.read()

        # Add a PROP index line without a corresponding ## PROP-999 section
        # This creates a G1 parity error
        malformed_ledger = ledger_content + '\n- PROP-999 — orphan line — CREATE skills/orphan-skill — ACCEPTED\n'

        with open(ledger_path, 'w', encoding='utf-8') as f:
            f.write(malformed_ledger)

        # Run render script in temp clone
        result = subprocess.run(
            ['python3', 'scripts/audit/skill_impact_render.py'],
            cwd=temp_clone,
            capture_output=True,
            text=True
        )

        # Verify exit code is 1
        if result.returncode != 1:
            print(f"  FAIL: expected exit code 1, got {result.returncode}")
            return False

        # Verify error message names the PROP id
        if 'PROP-999' not in result.stderr:
            print(f"  FAIL: error message does not name PROP-999")
            print(f"  stderr: {result.stderr}")
            return False

        # Verify error message says "G1 parity error"
        if 'G1 parity error' not in result.stderr:
            print(f"  FAIL: error message does not mention 'G1 parity error'")
            print(f"  stderr: {result.stderr}")
            return False

        # Verify skill-impact.md is not written or is unchanged
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                after_content = f.read()
            if baseline_content is not None and baseline_content != after_content:
                print(f"  FAIL: skill-impact.md was modified after failed render")
                return False

        print("  PASS: render failed with G1 parity error, file unchanged")
        return True

    finally:
        # Cleanup temp directory
        shutil.rmtree(tmpdir, ignore_errors=True)

def expected_skill_count(cwd='N:\\claude-cfl\\clone'):
    """Derive the expected skill count from the same source of truth the
    render script walks (skills/*/SKILL.md), instead of a hardcoded number.
    Mirrors the DERIVE-42 fix in skill_impact_render.py: the count is a fact
    about the repo at run time, not a constant to keep bumping.
    """
    return len(list(Path(cwd, 'skills').glob('*/SKILL.md')))

def test_row_count(cwd='N:\\claude-cfl\\clone', output_path=None, label="Test (b)"):
    """Test (b): render normal and verify row count matches the number of
    skills/*/SKILL.md files actually present (derived, not hardcoded).

    cwd/output_path are overridable so the FIX-3 regression case below can exercise this exact
    function against a scratch clone instead of duplicating its logic.
    """
    expected = expected_skill_count(cwd=cwd)
    print(f"{label}: Row count == {expected} (derived from skills/*/SKILL.md)...")
    if output_path is None:
        output_path = os.path.join(cwd, 'wiki', 'skills-gate', 'skill-impact.md')

    # First, clean up and run render
    rc, stdout, stderr = run_render_script(cwd=cwd)
    if rc != 0:
        # 2026-09-05 FIX-3: a nonzero exit here means the render did NOT run — reading
        # skill-impact.md below would silently grade a STALE file from a prior successful
        # run as if it reflected this attempt. Fail loudly instead.
        print(f"  FAIL: render script exited {rc}, did not produce a fresh render")
        print(f"  stderr: {stderr.strip()}")
        return False

    # Read rendered file
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    row_count = count_table_rows(content)

    if row_count == expected:
        print(f"  PASS: {row_count} rows found")
        return True
    else:
        print(f"  FAIL: expected {expected} rows, got {row_count}")
        return False

def test_render_failure_not_read_as_stale_pass():
    """Regression (FIX-3, 2026-09-05): TRIAGE-8 found test_row_count()/test_purpose_modification()
    called run_render_script() and discarded its return code, so a FAILED render was silently
    graded against whatever skill-impact.md happened to already be on disk. This seeds a scratch
    clone with a stale skill-impact.md that genuinely has 42 rows, forces the render to fail
    (same malformed-LEDGER technique as test (a)), and asserts test_row_count() reports FAIL
    rather than reading the stale 42-row file as a pass.

    This case FAILS against the pre-fix test_row_count() (which ignored run_render_script()'s
    exit code) and PASSES against the fixed version.
    """
    print("Test (d): a failed render is not silently graded against a stale file...")

    tmpdir = tempfile.mkdtemp()
    try:
        clone_path = 'N:\\claude-cfl\\clone'
        temp_clone = os.path.join(tmpdir, 'clone')
        shutil.copytree(clone_path, temp_clone)

        output_path = os.path.join(temp_clone, 'wiki', 'skills-gate', 'skill-impact.md')
        stale_rows = '\n'.join(f'| stale-skill-{i} | x | x | x |' for i in range(42))
        stale_content = ("---\n_note: pre-seeded stale fixture\n---\n\n"
                          "| a | b | c | d |\n|---|---|---|---|\n" + stale_rows + "\n")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stale_content)

        # Sanity: the seeded stale file really does read back as exactly 42 rows — otherwise
        # this case would prove nothing.
        seeded_count = count_table_rows(stale_content)
        if seeded_count != 42:
            print(f"  FAIL: test setup invalid — seeded stale file has {seeded_count} rows, not 42")
            return False

        # Force the render to fail, same technique as test_parity_check.
        ledger_path = os.path.join(temp_clone, 'wiki', 'skills-gate', 'LEDGER.md')
        with open(ledger_path, 'r', encoding='utf-8') as f:
            ledger_content = f.read()
        with open(ledger_path, 'w', encoding='utf-8') as f:
            f.write(ledger_content +
                     '\n- PROP-998 — orphan line — CREATE skills/orphan-skill-2 — ACCEPTED\n')

        result = test_row_count(cwd=temp_clone, output_path=output_path, label="  (nested) Test (d)")

        if result:
            print("  FAIL: test_row_count() reported PASS against a stale file from a failed "
                  "render — the exit-code check is not load-bearing")
            return False

        print("  PASS: test_row_count() correctly refused to grade the stale file as a pass")
        return True
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_purpose_modification():
    """Test (c): modify PURPOSE.md r_best and verify rendered row changes."""
    print("Test (c): PURPOSE.md modification detection...")

    # First, get baseline
    rc, stdout, stderr = run_render_script()
    if rc != 0:
        # Same class as test (b): a failed render must not be read as a fresh baseline.
        print(f"  FAIL: baseline render script exited {rc}, did not produce a fresh render")
        print(f"  stderr: {stderr.strip()}")
        return False
    output_path = 'N:\\claude-cfl\\clone\\wiki\\skills-gate\\skill-impact.md'
    with open(output_path, 'r', encoding='utf-8') as f:
        baseline = f.read()

    # Find exchange-letters row in baseline
    baseline_rows = baseline.split('\n')
    exchange_letters_baseline = None
    for row in baseline_rows:
        if '| exchange-letters |' in row:
            exchange_letters_baseline = row
            break

    if not exchange_letters_baseline:
        print("  FAIL: exchange-letters row not found in baseline")
        return False

    # Now modify exchange-letters PURPOSE.md
    purpose_path = 'N:\\claude-cfl\\clone\\skills\\exchange-letters\\PURPOSE.md'
    with open(purpose_path, 'r', encoding='utf-8') as f:
        purpose_content = f.read()

    # Modify r_best from 1.0 to 0.95
    modified_purpose = purpose_content.replace('r_best: 1.0', 'r_best: 0.95')

    with open(purpose_path, 'w', encoding='utf-8') as f:
        f.write(modified_purpose)

    try:
        # Re-render
        rc, stdout, stderr = run_render_script()
        if rc != 0:
            print(f"  FAIL: modified-run render script exited {rc}, did not produce a fresh render")
            print(f"  stderr: {stderr.strip()}")
            return False

        # Read new rendered file
        with open(output_path, 'r', encoding='utf-8') as f:
            modified = f.read()

        # Find exchange-letters row in modified
        modified_rows = modified.split('\n')
        exchange_letters_modified = None
        for row in modified_rows:
            if '| exchange-letters |' in row:
                exchange_letters_modified = row
                break

        if not exchange_letters_modified:
            print("  FAIL: exchange-letters row not found in modified")
            return False

        if exchange_letters_baseline != exchange_letters_modified:
            print(f"  PASS: row changed after PURPOSE.md modification")
            print(f"    Baseline:  {exchange_letters_baseline[:80]}...")
            print(f"    Modified:  {exchange_letters_modified[:80]}...")
            return True
        else:
            print(f"  FAIL: row did not change after PURPOSE.md modification")
            return False

    finally:
        # Restore PURPOSE.md
        with open(purpose_path, 'w', encoding='utf-8') as f:
            f.write(purpose_content)

def main():
    """Run all tests."""
    print("=" * 70)
    print("Selftest Suite for skill_impact_render.py")
    print("=" * 70)

    results = {
        'parity_check': test_parity_check(),
        'row_count': test_row_count(),
        'purpose_modification': test_purpose_modification(),
        'render_failure_not_read_as_stale_pass': test_render_failure_not_read_as_stale_pass(),
    }

    print("=" * 70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
