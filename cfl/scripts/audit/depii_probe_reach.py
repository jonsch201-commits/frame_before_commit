#!/usr/bin/env python3
"""probe_reach.py -- BOTH-DIRECTIONS test for the de-PII derived branch (P2-5).

Direction A (leak):        does a family/third-party marker reach the derived tree?
Direction B (lost context): can a real CFL retrieval question still be answered from it?

Method: for each probe in wiki/tracker/PROBE-REGISTRY.md, take the rare term(s) the probe
turns on and count files containing it in (1) the SOURCE tree as staged from the ref, and
(2) the DERIVED tree. A term that exists in source and is gone from derived is LOST CONTEXT.
No retrieval ranking is simulated -- a term absent from the corpus cannot be ranked at all,
so presence is a strict UPPER BOUND on what retrieval could return.
"""
import os, sys, re

src, out = sys.argv[1], sys.argv[2]
TEXT = {".md", ".txt", ".py", ".sh", ".json", ".yaml", ".yml", ".jsonl", ".toml", ".cfg"}

PROBES = [
    ("P1",  "rare-term",       ["mirror_resident_volumes", "carry_letters"]),
    ("P2",  "rare-term",       ["b44513a"]),
    ("P3",  "supersession",    ["check_struck_gates", "11901"]),
    ("P4",  "supersession",    ["AMENDED BY JON 2026-08-19", "less concerned about PII"]),
    ("P5",  "neg-control",     ["AskUserQuestion"]),
    ("P7",  "imprecise",       ["First-Run Numbers Are Hypotheses", "resident-tickets"]),
    ("P8",  "typo/graphrag",   ["trigram", "retrieve.py"]),
    ("P10", "era",             ["frame-before-commit", "Frame-Before-Commit"]),
    ("P11", "attribution",     ["Focusing on 100%", "3653971690"]),
    ("P12", "tool-self",       ["resident docker volume", "mirror_resident"]),
    ("--", "GOVERNING RULING", ["2026-07-25", "14c0cadd"]),
    ("--", "GOVERNING RULING", ["third-party consent", "money identifiers"]),
]

def walk(root):
    for r, _d, ns in os.walk(root):
        for n in ns:
            if os.path.splitext(n)[1].lower() in TEXT:
                yield os.path.join(r, n)

def build(root):
    idx = []
    for fp in walk(root):
        try:
            idx.append((os.path.relpath(fp, root).replace(os.sep, "/"),
                        open(fp, encoding="utf-8", errors="replace").read()))
        except OSError:
            pass
    return idx

S, D = build(src), build(out)
print("source text files: %d   derived text files: %d\n" % (len(S), len(D)))
print("%-5s %-16s %-34s %6s %6s  %s" % ("id","class","term","src","der","verdict"))
print("-"*104)
lost = kept = 0
for pid, cls, terms in PROBES:
    for t in terms:
        ns = sum(1 for _p, c in S if t in c)
        nd = sum(1 for _p, c in D if t in c)
        if ns == 0:
            v = "n/a (absent from source)"
        elif nd == 0:
            v = "** LOST — unanswerable from derived **"; lost += 1
        elif nd < ns * 0.5:
            v = "DEGRADED (%.0f%% of files kept)" % (100.0*nd/ns); kept += 1
        else:
            v = "reachable"; kept += 1
        print("%-5s %-16s %-34s %6d %6d  %s" % (pid, cls, t[:34], ns, nd, v))
print("\nLOST terms: %d   reachable/degraded terms: %d" % (lost, kept))
