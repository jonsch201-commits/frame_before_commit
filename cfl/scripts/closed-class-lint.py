#!/usr/bin/env python3
"""Closed-class linter (v1, PRESENCE check — proposes, never applies).
Flags governance-modal function words + untagged hedge markers in executor-facing spec lines.
Function words carry governance semantics that degrade silently downward (Fable, 2026-07-15)."""
import re, sys, glob, os
sys.stdout.reconfigure(encoding="utf-8")
GOV = r"\b(may|should|shall|must|will|can|each|all|any|with|from)\b"
HEDGE = r"\b(might|could|perhaps|possibly|probably|likely|seems|appears|arguably|tends to)\b"
TAG = re.compile(r"\[(verbatim|paraphrase|reconstructed|contextual|inferred|confidence|UNVERIFIED|weights|instance|cold-reading|lineage)")
def is_spec_line(l):
    s=l.strip()
    # executor-facing: bullets/numbered rules/imperatives; skip headings, code fences, tables
    if not s or s.startswith(("#","```","|","---",">")): return False
    return s.startswith(("-","*")) or re.match(r"^\d+[.)]",s) or s[:1].isupper()
def lint(path):
    out=[]
    for i,l in enumerate(open(path,encoding="utf-8",errors="ignore"),1):
        if not is_spec_line(l): continue
        gov=[m.group(1) for m in re.finditer(GOV,l)]
        hed=[m.group(1) for m in re.finditer(HEDGE,l)]
        tagged=bool(TAG.search(l))
        if hed and not tagged: out.append((i,"HEDGE-untagged",",".join(hed),l.strip()[:90]))
        elif gov: out.append((i,"GOV-modal",",".join(sorted(set(gov))),l.strip()[:90]))
    return out
targets=[]
for pat in ["exchange/*.md","exchange/**/*.md","scripts/*.sh"]:
    targets+=glob.glob(os.path.join(sys.argv[1],pat),recursive=True)
# a couple representative skill specs from main checkout
for sk in ["skills/frame-before-commit/SKILL.md","skills/wiki-master/SKILL.md"]:
    p=os.path.join(sys.argv[2],sk)
    if os.path.exists(p): targets.append(p)
print("# Closed-class lint (v1 PRESENCE check) — proposed patches, NEVER applied\n")
print("Flags governance-modals (may/should/shall/must/will/can/each/all/any/with/from) in spec lines,")
print("and hedge markers lacking a `[tag]`. Over-flags by design (presence, not correctness): a flag =")
print("'confirm this function word's governance meaning is intended + explicit', not 'this is wrong'.\n")
tot=0
for t in sorted(set(targets)):
    fl=lint(t); 
    if not fl: continue
    rel=os.path.relpath(t).replace("\\","/")
    hed=sum(1 for f in fl if f[1]=="HEDGE-untagged"); gov=sum(1 for f in fl if f[1]=="GOV-modal")
    print(f"## {rel} — {len(fl)} flags ({hed} untagged-hedge, {gov} gov-modal)")
    for i,k,w,txt in fl[:6]:
        print(f"  - L{i} [{k}: {w}] {txt}")
    if len(fl)>6: print(f"  … +{len(fl)-6} more")
    print()
    tot+=len(fl)
print(f"## Total flags: {tot}")
print("\nProposed disposition: HEDGE-untagged → add a fidelity/confidence tag or make the claim definite.")
print("GOV-modal in a governance/rule line → promote to an explicit clause (define WHO/WHEN the modal binds).")
