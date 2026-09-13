#!/usr/bin/env python3
"""Measure the 08-16 export corpus gap by FULL uuid, not by a filename proxy.

Why this exists (CFL, 2026-08-17 15:5x):
  wiki/tracker/wayfinder-cfl.md carries "Corpus gap -- 08-16 export: 16 conversations /
  157 thinking blocks absent." That figure was ITSELF a correction of an earlier 13/147,
  which came from differencing two different populations (zip's 249 vs an extracted dir's
  236). The tracker's own note says the correct method is a set difference against the
  CORPUS, not against another extract.

  A first pass here matched on the 6-hex prefix embedded in corpus FILENAMES. That is a
  detection proxy, and this repo's most expensive recurring defect is trusting one. A
  6-hex prefix can collide, and a filename convention can drift -- either way the proxy
  fails toward "present", which is the dangerous direction: it reports a closed gap.

  So this resolves FULL 36-char uuids out of each corpus file's frontmatter and differences
  those. Both field spellings are accepted: `uuid:` and `source_id:`. Reading only
  `source_id:` is the exact bug that made cc_corpus_gap.py report 26 present extracts as
  LOST on 2026-07-27 -- it was not finding losses, it was finding a field name.

Exit codes: 0 gap measured (0 or more) - 2 export or corpus unreadable.
"""

import glob
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EXPORT = "raw/Anthropic_zips/extracted-1786933322/conversations.json"
CORPUS_GLOB = "raw/transcripts/**/*.md"
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
HEAD_BYTES = 4000


def thinking_count(conv):
    n = 0
    for m in conv.get("chat_messages") or []:
        for ct in m.get("content") or []:
            if ct.get("type") == "thinking":
                n += 1
    return n


def main():
    if not os.path.isfile(EXPORT):
        print("FAIL export not found: " + EXPORT, file=sys.stderr)
        return 2
    convs = json.load(open(EXPORT, encoding="utf-8"))
    by_uuid = dict()
    for c in convs:
        by_uuid[c["uuid"]] = c
    uuids = set(by_uuid)
    print("export conversations : %d  (distinct uuids %d)" % (len(convs), len(uuids)))

    files = glob.glob(CORPUS_GLOB, recursive=True)
    print("corpus md files      : %d" % len(files))

    found = set()
    for p in files:
        try:
            head = open(p, encoding="utf-8", errors="replace").read(HEAD_BYTES)
        except Exception:
            continue
        for u in UUID_RE.findall(head):
            if u in uuids:
                found.add(u)

    print("matched by FULL uuid : %d" % len(found))
    missing = sorted(uuids - found, key=lambda u: by_uuid[u].get("updated_at") or "")
    print("MISSING              : %d" % len(missing))

    total_think = 0
    for u in missing:
        c = by_uuid[u]
        tb = thinking_count(c)
        total_think += tb
        name = (c.get("name") or "(untitled)")[:58]
        print("   %s  %s  msgs=%-4d think=%-4d %s"
              % ((c.get("updated_at") or "")[:19], u[:8],
                 len(c.get("chat_messages") or []), tb, name))
    print("thinking blocks in missing: %d" % total_think)

    print("\n[!] BOUND: presence means a corpus file's first %d bytes carry the uuid." % HEAD_BYTES)
    print("    A parsed file that records no uuid at all would read as MISSING here --")
    print("    that direction is safe (over-reports the gap). The unsafe direction, a")
    print("    filename-prefix collision reporting a gap as CLOSED, is what this avoids.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
