#!/usr/bin/env python3
"""check_secondary_attribution.py — is this Jon quote cited to Jon, or to someone quoting Jon?

PROTOTYPE. Not wired into su_gate.sh. Advisory by design until its false-positive rate is
measured against a real corpus pass.

WHY THIS EXISTS
---------------
`verify_quotes.py` answers "does this string exist in the source this page cites?" It
resolves the cited source, finds the string, and returns SUPPORTED. It has NO view on
whether the cited source is *itself a quotation*. So a page can quote Jon by citing an
agent's packet that quoted Jon, and the gate passes.

Three instances in one session, 2026-08-02, each losing the load-bearing clause:

  1. `sources/reference/jon-messages-to-mirror-2026-08-02.md` — a PRIMARY-EVIDENCE page —
     carried Message 9 quoted from a work order rather than the JSONL. The work order's
     version is an unmarked elision: it drops the two-thirds of the message where Jon
     ratifies the interpretation-summary artifact, and the closing question that started
     the whole close.
  2. `SCHEMA.md:NNN` citations quoted via another project's page, flagged one-hop by their
     own author.
  3. A work order quoting a CODE COMMENT that described a historical defect, presented as
     current state.

And the class's most expensive prior instance, already in the record: an agent packet
invented a Jon ruling, `wiki/index.md` cited the packet, and the citation resolved. Nothing
in the loop had primary evidence.

THE RULE
--------
A quote attributed to Jon must cite a PRIMARY source — something under `raw/transcripts/`
(a transcript) or `raw/originals/` (capture bytes). Citing any other artifact for Jon's
words is SECONDARY-ATTRIBUTION: possibly true, but unverifiable at the citation.

Exit 0 = no secondary attributions.  Exit 1 = at least one.  Exit 2 = nothing scanned.

DELIBERATELY NOT DONE
---------------------
- Does not judge whether the quote is accurate. That is `verify_quotes.py`'s job.
- Does not fire on quotes NOT attributed to Jon. Agent-to-agent quotation is normal.
- Prints a 40-char fingerprint only. `raw/` is Jon's personal history.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FILE_CITE_RE = re.compile(r"`((?:raw/|wiki/|exchange/|skills/|scripts/)[^`]+?\.(?:md|py))(?::(\d+))?`")
ANCHOR_RE = re.compile(r"\[([a-zA-Z0-9][a-zA-Z0-9_\-]*):T(\d+)(?:\.P\d+)?\]")
GRADE_RE = re.compile(r"\[(TRANSCRIPT|THINKING-SUMMARY|verbatim|LIVE-SESSION)[^\]]*\]", re.I)

# A line attributes to Jon when it names him as speaker near a quote or grade.
JON_ATTRIB_RE = re.compile(
    r"\b(Jon(?:'s)?\s+(?:said|says|words|own words|verbatim|ruling|ruled|instruction|quote)"
    r"|Jon,\s+(?:verbatim|20\d\d-)|\bJon\b[^.\n]{0,40}\[verbatim)",
    re.I,
)

PRIMARY_PREFIXES = ("raw/transcripts/", "raw/originals/", "raw/sessions/")

# A page whose own source_file is primary is citing primary by default.
def frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"\'')
    return fm


def is_primary(path):
    p = path.replace("\\", "/").lstrip("./")
    return p.startswith(PRIMARY_PREFIXES)


def scan_page(path):
    """Return list of (lineno, fingerprint, cited, reason) findings for one page."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    fm = frontmatter(text)
    page_source = fm.get("source_file", "")
    page_source_primary = is_primary(page_source) if page_source else False

    out = []
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if not JON_ATTRIB_RE.search(line):
            continue
        if not (GRADE_RE.search(line) or '"' in line or "“" in line or line.lstrip().startswith(">")):
            continue

        # Gather citations on this line and the two after it (grades often trail).
        window = " ".join(lines[i - 1:i + 2])
        cites = [c for c, _ln in FILE_CITE_RE.findall(window)]
        anchors = ANCHOR_RE.findall(window)

        if anchors:
            continue  # a [slug:Tn] anchor resolves through the turn index to a transcript
        if any(is_primary(c) for c in cites):
            continue  # explicitly cites a primary
        if cites:
            out.append((i, _fp(line), cites[0],
                        "cites a non-primary artifact for Jon's words"))
            continue
        if page_source_primary:
            continue  # page-level source_file is primary; inherits
        if page_source:
            out.append((i, _fp(line), page_source,
                        "page-level source_file is not primary"))
        else:
            out.append((i, _fp(line), "(none)",
                        "no source_file and no inline primary cite"))
    return out


def _fp(line):
    m = re.search(r'[">]\s*([^"<\n]{8,})', line)
    s = (m.group(1) if m else line).strip()
    return " ".join(s.split())[:40]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(REPO / "wiki"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    root = Path(args.root)
    if not root.is_dir():
        print(f"[exit 2] root not found: {root}", file=sys.stderr)
        return 2

    pages = [p for p in root.rglob("*.md") if ".understand-anything" not in str(p)]
    if not pages:
        print(f"[exit 2] scanned 0 pages under {root}", file=sys.stderr)
        return 2

    findings = []
    for p in pages:
        for f in scan_page(p):
            findings.append((p, *f))

    print("=== SECONDARY-ATTRIBUTION SCAN (prototype, advisory) ===")
    print(f"  pages scanned          : {len(pages)}")
    print(f"  SECONDARY-ATTRIBUTION  : {len(findings)}")
    print()
    for p, ln, fp, cited, reason in findings[:args.limit]:
        rel = p.relative_to(REPO).as_posix()
        print(f"  {rel}:{ln}")
        print(f"      fp={fp!r}")
        print(f"      cites={cited}  -- {reason}")
    if len(findings) > args.limit:
        print(f"  ... {len(findings) - args.limit} more (raise --limit)")

    if findings:
        print("\nRESULT: FINDINGS — Jon's words cited to something other than a primary.")
        return 1
    print("\nRESULT: CLEAN")
    return 0


def self_test():
    """Negative control. Must fire on a known-bad and stay silent on a known-good."""
    import tempfile, os
    bad = ('---\ntitle: t\n---\n\n'
           'Jon, verbatim: *"Yes ratified."* `[verbatim, per '
           '`exchange/some-packet-2026-08-02.md`]`\n')
    good = ('---\ntitle: t\nsource_file: raw/transcripts/claude-code/fl/x.md\n---\n\n'
            'Jon, verbatim: *"Yes ratified."* `[TRANSCRIPT:2026-08-02]`\n')
    good2 = ('---\ntitle: t\n---\n\n'
             'Jon said this `[verbatim]` — see `raw/transcripts/claude-code/fl/x.md:12`\n')
    neutral = ('---\ntitle: t\n---\n\n'
               'The agent noted *"something"* in `exchange/packet.md`\n')

    res = {}
    for name, body in (("bad", bad), ("good-fm", good), ("good-cite", good2),
                       ("neutral", neutral)):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as tf:
            tf.write(body)
            tmp = tf.name
        res[name] = len(scan_page(Path(tmp)))
        os.unlink(tmp)

    checks = [
        ("known-bad fires", res["bad"] >= 1),
        ("primary source_file stays silent", res["good-fm"] == 0),
        ("inline primary cite stays silent", res["good-cite"] == 0),
        ("non-Jon quote ignored", res["neutral"] == 0),
    ]
    print("=== SELF-TEST (negative control) ===")
    for label, ok in checks:
        print(f"  {label:<38} {'PASS' if ok else 'FAIL'}")
    allok = all(ok for _, ok in checks)
    print(f"\nRESULT: {'PASS — can both fire and stay silent.' if allok else 'FAIL — not trustworthy.'}")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
