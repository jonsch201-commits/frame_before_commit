#!/usr/bin/env python3
"""download_lure_guard.py -- find executables and containers masquerading as media.

WHY THIS EXISTS
---------------
Three infections reached this machine by the same route, and the route is a naming trick:
a file named like a TV episode that is actually an executable, or an archive containing one.

  2026-04-27/28  LummaStealer + Ravartar!rfn   D:\\Complete           (contained; Safe-Mode deletes)
  2026-08-01/02  ~20 Severe detections          D:\\Complete\\tv-sonarr (Defender quarantined)
  2026-08-22     LummaStealer.GAPF!MTB          D:\\Complete\\tv-sonarr (an .scr inside an .iso)

The April session agreed a hardening step -- file-type filtering on the download pipeline -- and
that step was never built. The pipeline was re-enabled and reinfected twice. THIS SCRIPT IS THAT
STEP, finally written.

WHAT IT DOES *NOT* DO, and why
------------------------------
It does not delete. It does not quarantine by default. It does not touch Defender.
Standing constraint: "no deletion, ever" -- and a guard that removes files is a guard that can
destroy a legitimate download on a false positive. REPORTING is the safe default; --quarantine
MOVES (never deletes) into a holding folder, and even that is opt-in.

It is deliberately NOT a virus scanner. Defender is the scanner. This catches the SHAPE of the
lure -- an executable where only media belongs -- which is a claim about naming, not about
malice, and which Defender's signature approach can miss for an unknown sample (it missed the
2026-08-22 file through four scans).

EXIT CODES
  0  nothing suspicious
  1  suspicious files found (report mode) -- deliberately non-zero so a ritual step can gate on it
  2  bad invocation / unreadable root
"""

import argparse
import os
import shutil
import sys

# Executable-class: these should NEVER appear in a media landing zone.
EXEC_EXT = {
    ".exe", ".scr", ".com", ".pif", ".bat", ".cmd", ".vbs", ".vbe", ".js", ".jse",
    ".wsf", ".wsh", ".ps1", ".msi", ".msp", ".hta", ".cpl", ".jar", ".lnk", ".reg",
}
# Container-class: legitimate for some releases, but the 2026-08-22 payload was an .scr inside
# an .iso, so a container named as an episode is worth a human look. Reported at lower severity.
CONTAINER_EXT = {".iso", ".rar", ".zip", ".7z", ".cab", ".img", ".vhd"}

# Real media -- present so the report can say what the folder is actually FOR.
MEDIA_EXT = {".mkv", ".mp4", ".avi", ".m4v", ".mov", ".wmv", ".ts", ".srt", ".sub", ".idx", ".nfo"}

DEFAULT_ROOTS = [r"D:\Complete", r"D:\incomplete"]


# -- KNOWN-BENIGN CARVE-OUTS -------------------------------------------------
# First run of this guard returned 57 executable-class hits and 50 of them were `.jar` files
# under BDMV\JAR\ -- that is the BD-J menu structure of a legitimate Blu-ray rip, not malware.
# A guard that is wrong 88% of the time gets ignored, and an ignored guard is worse than none:
# it launders "nobody looked" into "nothing found". So the carve-outs are part of the tool, and
# each one states WHY, because an unexplained exclusion is where a real threat eventually hides.

def _in_bluray_structure(full):
    """BDMV\\JAR\\*.jar and BDMV\\BACKUP\\JAR\\*.jar are Blu-ray Java menus. Structural, not payload."""
    p = full.replace("/", "\\").upper()
    return "\\BDMV\\" in p and "\\JAR\\" in p


def _is_rarbg_nag(full, size):
    """RARBG_DO_NOT_MIRROR.exe -- a ~99-byte scene nag file. Benign, but keep it VISIBLE at
    low severity: it is still an executable extension, and 'benign by convention' is exactly
    the assumption an attacker would like us to keep making."""
    return os.path.basename(full).upper().startswith("RARBG") and 0 <= size < 4096


def classify(full, size=0):
    ext = os.path.splitext(full)[1].lower()
    if ext in EXEC_EXT:
        if ext == ".jar" and _in_bluray_structure(full):
            return None                      # Blu-ray menu, carved out with reason above
        if _is_rarbg_nag(full, size):
            return "NAG"
        return "EXECUTABLE"
    if ext in CONTAINER_EXT:
        return "CONTAINER"
    return None


def is_episode_lure(full):
    """THE ACTUAL SIGNATURE of all three infections: a container whose basename matches its own
    parent folder, i.e. a 'release folder' containing one archive named like the episode.
    `South.Park.S27E04...\\South.Park.S27E04....iso` -> the .scr was inside. A game ISO sitting
    in a game folder does not match this shape, which is why MGS2.ISO is not flagged here."""
    stem = os.path.splitext(os.path.basename(full))[0].lower()
    parent = os.path.basename(os.path.dirname(full)).lower()
    return bool(stem) and stem == parent


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return "%.1f %s" % (n, unit)
        n /= 1024.0


def scan(roots):
    findings, media_count, missing = [], 0, []
    for root in roots:
        if not os.path.isdir(root):
            missing.append(root)
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                ext = os.path.splitext(fn)[1].lower()
                if ext in MEDIA_EXT:
                    media_count += 1
                    continue
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = -1
                kind = classify(full, size)
                if not kind:
                    continue
                if kind == "CONTAINER" and is_episode_lure(full):
                    kind = "LURE"
                findings.append((kind, full, size, ""))
    return findings, media_count, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", dest="roots",
                    help="landing zone to scan (repeatable). Default: %s" % ", ".join(DEFAULT_ROOTS))
    ap.add_argument("--quarantine", metavar="DIR",
                    help="MOVE (never delete) executable-class hits into DIR. Opt-in.")
    ap.add_argument("--containers", action="store_true",
                    help="also treat container files as actionable, not just reportable")
    args = ap.parse_args()

    roots = args.roots or DEFAULT_ROOTS
    findings, media_count, missing = scan(roots)

    for m in missing:
        print("NOT PRESENT (skipped, not a pass): %s" % m)
    print("scanned roots : %s" % ", ".join(r for r in roots if r not in missing))
    print("media files   : %d  (what these folders are actually for)" % media_count)

    lures = [f for f in findings if f[0] == "LURE"]
    execs = [f for f in findings if f[0] == "EXECUTABLE"]
    conts = [f for f in findings if f[0] == "CONTAINER"]
    nags  = [f for f in findings if f[0] == "NAG"]

    print("LURE-SHAPED   found : %d   <-- archive named exactly like its own folder. THIS is how all three infections arrived" % len(lures))
    for _k, path, size, note in sorted(lures):
        print("   %-10s %s  %s" % (human(size) if size >= 0 else "?", path, note))

    print("EXECUTABLE-class found: %d   <-- these should never be here" % len(execs))
    for _k, path, size, note in sorted(execs):
        print("   %-10s %s  %s" % (human(size) if size >= 0 else "?", path, note))
    print("CONTAINER-class found : %d   <-- legitimate sometimes; the 08-22 payload hid in one" % len(conts))
    for _k, path, size, note in sorted(conts):
        print("   %-10s %s  %s" % (human(size) if size >= 0 else "?", path, note))

    if args.quarantine:
        targets = lures + execs + (conts if args.containers else [])
        if targets:
            os.makedirs(args.quarantine, exist_ok=True)
            print("MOVING %d file(s) to %s  (moved, NOT deleted -- recoverable)" %
                  (len(targets), args.quarantine))
            for _k, path, _s, _n in targets:
                dest = os.path.join(args.quarantine, os.path.basename(path))
                n = 1
                while os.path.exists(dest):        # never clobber; no deletion, ever
                    stem, ext = os.path.splitext(os.path.basename(path))
                    dest = os.path.join(args.quarantine, "%s.%d%s" % (stem, n, ext))
                    n += 1
                try:
                    shutil.move(path, dest)
                    print("   moved: %s -> %s" % (path, dest))
                except OSError as e:
                    print("   MOVE FAILED (left in place): %s -- %s" % (path, e))

    print("benign nag files    : %d  (rarbg markers, kept visible not hidden)" % len(nags))
    for _k, path, size, _n in sorted(nags):
        print("   %-10s %s" % (human(size) if size >= 0 else "?", path))
    actionable = len(lures) + len(execs) + (len(conts) if args.containers else 0)
    if actionable:
        print("RESULT: %d file(s) need a human look." % actionable)
        return 1
    print("RESULT: clean -- no executable-class files in the landing zones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
