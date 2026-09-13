#!/usr/bin/env python3
"""organize_exchange.py — file the flat exchange/ deposits into a mined scheme.

WHY THIS EXISTS
Jon, 2026-08-15 18:09: "the wiki being unorganized... the exchange is MONDO
unorganized". Measured: exchange/ root flat-file count is monotonic —
72 (08-01) -> 158 (08-08) -> 169 (08-12) -> 200 (08-14) -> 236 (08-15) — and
exchange/inbound/ + exchange/outbound/ hold hundreds more flat files with no
routing script touching them. This script is the mechanism. It does not
invent a taxonomy: the destination scheme below is MINED from what the
existing filenames already encode (see the distribution this script itself
reports with --report).

SAFETY
- Default action is --report. It moves NOTHING. Read the report before ever
  passing --apply.
- --apply never deletes. Every moved file gets `git mv`'d to its new home and
  a one-line redirect stub is left at the OLD path pointing to the NEW path.
  ("No deletion, ever" — Jon, standing constraint on this repo.)
- --apply is idempotent: a file that is already at (or redirected to) its
  computed destination is skipped and counted separately, not re-moved.
  Running the script twice in a row must report zero moves on the second run
  — this is proven in the deposit note, not asserted here.
- This script does NOT recurse into subdirectories that already look
  organized (su-close/, lanes/, staged/, fable-2026-07/, etc.) — only the
  FLAT files sitting directly in exchange/, exchange/inbound/, and
  exchange/outbound/ are candidates. A file already filed under a mined
  bucket (e.g. exchange/inbound/pro/2026-08/foo.md) is left alone.
- Never touches wiki/personal, wiki/home, wiki/pro (excluded trunks) — this
  script never touches wiki/ at all, only exchange/.

MINED SCHEME (see --report for live counts against the current tree)
Classification is priority-ordered; first matching rule wins.

1. TRUNK-TO-TRUNK exchange letters. Filenames already encode sender and
   recipient as a `<sender>-to-<recipient>-` prefix (e.g.
   `pro-to-cfl-ASOP1-...md`, `cfl-to-soul-OVERNIGHT-...md`,
   `personal-herald-to-cfl-...md`). Recognized trunk tokens: personal, pro,
   soul, herald, secretary, jon, cfl, and personal-herald / personal-soul /
   personal-ssp (compound personal sub-lanes seen in the corpus).
     - If CFL is the RECIPIENT  -> exchange/inbound/<sender>/<YYYY-MM>/<file>
     - If CFL is the SENDER     -> exchange/outbound/<recipient>/<YYYY-MM>/<file>
     - Neither side is cfl (e.g. herald-to-soul relays CFL is CC'd on)
                                -> exchange/relay/<sender>-<recipient>/<YYYY-MM>/<file>

2. INBOUND-FROM-<TRUNK> naming (older convention, e.g.
   `INBOUND-FROM-PERSONAL-...md`) -> exchange/inbound/<trunk lowercased>/<YYYY-MM>/<file>

3. `from-resident-run<N>` naming (resident-fleet run artifacts, e.g.
   `...from-resident-run3-...md`) -> exchange/inbound/resident/run<N>/<file>
   (no month subfolder — run number is the more useful key than date here,
   since a run can span a date boundary; date stays in the filename.)

4. Everything else with a trailing `-YYYY-MM-DD` (or embedded date) and no
   counterparty signal — these are CFL-internal artifacts deposited into
   exchange/ (plans, packets, reports, charters) rather than letters to a
   trunk -> exchange/internal/<YYYY-MM>/<file>

5. No date found at all (rare — READMEs, templates, EXAMPLE files) ->
   exchange/internal/undated/<file>

Buckets are never invented per-file; they fall out of rules 1-5 applied
mechanically, and the --report output is the evidence for the distribution.

USAGE
  python organize_exchange.py --report                 # default; read-only
  python organize_exchange.py --report --root <path>   # point at a scratch copy
  python organize_exchange.py --apply --root <path>    # perform git mv + stubs
"""

import argparse
import collections
import re
import subprocess
import sys
from pathlib import Path

TRUNK_TOKENS = [
    "personal-herald", "personal-soul", "personal-ssp",
    "personal", "pro", "soul", "herald", "secretary", "jon", "cfl", "all", "ssp",
]
# longest-first so "personal-herald" matches before "personal"
TRUNK_TOKENS.sort(key=len, reverse=True)
TRUNK_ALT = "|".join(re.escape(t) for t in TRUNK_TOKENS)

TRUNK_TO_TRUNK_RE = re.compile(rf"^({TRUNK_ALT})-to-({TRUNK_ALT})-")
INBOUND_FROM_RE = re.compile(r"INBOUND-FROM-([A-Za-z]+)")
RESIDENT_RUN_RE = re.compile(r"from-resident-run(\d+)")
DATE_RE = re.compile(r"(\d{4}-\d{2})-\d{2}")

REDIRECT_STUB_TEMPLATE = """# MOVED

This file was reorganized by `scripts/audit/organize_exchange.py`.

New location: `{new_path}`

No content was deleted. This stub exists so old links/citations still
resolve to something readable. Original filename preserved in the new path.
"""


def classify(filename: str):
    """Return (bucket_label, relative_dest_path) for a flat filename.

    relative_dest_path is relative to exchange/ (e.g.
    'inbound/pro/2026-08/pro-to-cfl-....md').
    """
    m = TRUNK_TO_TRUNK_RE.match(filename)
    if m:
        sender, recipient = m.group(1), m.group(2)
        dm = DATE_RE.search(filename)
        month = dm.group(1) if dm else "undated"
        # "all" is a broadcast recipient (observed in practice landing in
        # exchange/inbound/ when CFL isn't the sender, and exchange/outbound/
        # when CFL is the sender) — treat it like "cfl" is a recipient/sender
        # for routing purposes, since CFL is always among "all".
        if recipient in ("cfl", "all") and sender != "cfl":
            return (f"inbound/{sender}", f"inbound/{sender}/{month}/{filename}")
        if sender == "cfl":
            return (f"outbound/{recipient}", f"outbound/{recipient}/{month}/{filename}")
        return (
            f"relay/{sender}-{recipient}",
            f"relay/{sender}-{recipient}/{month}/{filename}",
        )

    m = INBOUND_FROM_RE.search(filename)
    if m:
        trunk = m.group(1).lower()
        dm = DATE_RE.search(filename)
        month = dm.group(1) if dm else "undated"
        return (f"inbound/{trunk}", f"inbound/{trunk}/{month}/{filename}")

    m = RESIDENT_RUN_RE.search(filename)
    if m:
        run = m.group(1)
        return (f"inbound/resident/run{run}", f"inbound/resident/run{run}/{filename}")

    dm = DATE_RE.search(filename)
    if dm:
        month = dm.group(1)
        return ("internal", f"internal/{month}/{filename}")

    return ("internal/undated", f"internal/undated/{filename}")


def scan_flat(dir_path: Path):
    """Top-level files only — do not recurse into already-organized subdirs."""
    if not dir_path.is_dir():
        return []
    return sorted(p for p in dir_path.iterdir() if p.is_file())


def already_at_destination(src: Path, dest: Path) -> bool:
    return src.resolve() == dest.resolve()


def is_redirect_stub(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:20]
    except OSError:
        return False
    return head.startswith("# MOVED")


def run_report(exchange_root: Path):
    scan_dirs = [
        ("exchange", exchange_root),
        ("exchange/inbound", exchange_root / "inbound"),
        ("exchange/outbound", exchange_root / "outbound"),
    ]

    bucket_counts = collections.Counter()
    total_flat = 0
    already_filed = 0
    plan = []

    for label, d in scan_dirs:
        for f in scan_flat(d):
            total_flat += 1
            bucket, rel_dest = classify(f.name)
            dest = exchange_root / rel_dest
            bucket_counts[bucket] += 1
            if already_at_destination(f, dest):
                already_filed += 1
                status = "ALREADY-FILED"
            elif is_redirect_stub(f):
                # A stub left behind by a prior --apply run. Its own computed
                # destination is occupied by the real moved file, so it is
                # correctly immovable — this is what makes a second run a
                # no-op rather than a stub-shuffling loop.
                already_filed += 1
                status = "ALREADY-FILED (redirect stub)"
            else:
                status = "WOULD-MOVE"
            plan.append((label, f.name, bucket, rel_dest, status))

    print(f"=== organize_exchange.py --report ===")
    print(f"exchange root: {exchange_root}")
    print(f"flat files scanned (exchange/, exchange/inbound/, exchange/outbound/ top-level only): {total_flat}")
    print(f"already at computed destination: {already_filed}")
    print(f"would move: {total_flat - already_filed}")
    print()
    print("=== bucket counts (mined distribution) ===")
    for bucket, count in bucket_counts.most_common():
        print(f"{count:4d}  {bucket}")
    print()
    print("=== per-file plan ===")
    for label, name, bucket, rel_dest, status in plan:
        print(f"[{status}] {label}/{name}  ->  exchange/{rel_dest}")

    return plan, bucket_counts, total_flat, already_filed


def run_apply(exchange_root: Path, plan):
    moved = 0
    skipped = 0
    for label, name, bucket, rel_dest, status in plan:
        src = (exchange_root if label == "exchange" else exchange_root / label.split("/", 1)[1]) / name
        dest = exchange_root / rel_dest
        if status.startswith("ALREADY-FILED"):
            skipped += 1
            continue
        if dest.exists():
            print(f"SKIP (destination already exists, not overwriting): {dest}")
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "mv", str(src), str(dest)],
            check=True,
            cwd=str(exchange_root.parent) if exchange_root.name == "exchange" else str(exchange_root),
        )
        stub = src
        stub.write_text(
            REDIRECT_STUB_TEMPLATE.format(new_path=f"exchange/{rel_dest}"),
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "add", str(stub)],
            check=True,
            cwd=str(exchange_root.parent) if exchange_root.name == "exchange" else str(exchange_root),
        )
        moved += 1
        print(f"MOVED: {src}  ->  {dest}  (stub left at old path)")
    print()
    print(f"moved: {moved}  skipped(already-filed-or-exists): {skipped}")
    return moved, skipped


def file_single(exchange_root: Path, target: Path, apply: bool = True):
    """File exactly one just-deposited flat file. Built for a deposit-time
    hook: cheap (touches only this file, not a full-tree scan), non-blocking
    by construction (the caller runs this AFTER the write already
    succeeded — a failure here never prevents the deposit from landing),
    and uses the same classify()/move/stub logic as bulk --apply so a later
    bulk run treats hook-filed files identically (no special-casing, no
    drift between the two paths)."""
    if not target.is_file():
        print(f"file-single: not a file, skipping: {target}")
        return False
    bucket, rel_dest = classify(target.name)
    dest = exchange_root / rel_dest
    if already_at_destination(target, dest):
        print(f"file-single: already at destination: {target}")
        return False
    if is_redirect_stub(target):
        print(f"file-single: is a redirect stub, skipping: {target}")
        return False
    if dest.exists():
        print(f"file-single: destination already exists, not overwriting, leaving flat: {target} -> {dest}")
        return False
    if not apply:
        print(f"file-single (report-only): would file {target} -> exchange/{rel_dest}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    repo_root = exchange_root.parent if exchange_root.name == "exchange" else exchange_root
    subprocess.run(["git", "mv", str(target), str(dest)], check=True, cwd=str(repo_root))
    target.write_text(REDIRECT_STUB_TEMPLATE.format(new_path=f"exchange/{rel_dest}"), encoding="utf-8")
    subprocess.run(["git", "add", str(target)], check=True, cwd=str(repo_root))
    print(f"file-single: filed {target} -> {dest}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="Perform git mv + redirect stubs. DEFAULT IS REPORT-ONLY.")
    ap.add_argument("--report", action="store_true", help="Explicit report-only run (this is also the default when --apply is omitted).")
    ap.add_argument("--root", type=str, default=None, help="Path to the exchange/ directory (defaults to repo's exchange/ next to this script's ancestor).")
    ap.add_argument("--file-single", type=str, default=None, help="Deposit-time mode: file exactly one just-written flat file (by path) into its computed bucket. Intended for a non-blocking PostToolUse hook. Combine with --apply to actually move it; without --apply it only reports.")
    args = ap.parse_args()

    if args.root:
        exchange_root = Path(args.root)
    else:
        # scripts/audit/organize_exchange.py -> repo root is parents[2]
        repo_root = Path(__file__).resolve().parents[2]
        exchange_root = repo_root / "exchange"

    if args.file_single:
        target = Path(args.file_single)
        if not target.is_absolute():
            target = exchange_root / target
        file_single(exchange_root, target, apply=args.apply)
        return

    if not exchange_root.is_dir():
        print(f"ERROR: exchange root not found: {exchange_root}", file=sys.stderr)
        sys.exit(1)

    plan, bucket_counts, total_flat, already_filed = run_report(exchange_root)

    if args.apply:
        print()
        print("=== APPLYING ===")
        run_apply(exchange_root, plan)


if __name__ == "__main__":
    main()
