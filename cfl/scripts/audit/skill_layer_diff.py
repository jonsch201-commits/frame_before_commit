import os, io, hashlib, sys

repo = os.path.abspath("skills")
dep = os.path.expanduser("~/.claude/skills")


def tree(base, n):
    out = {}
    root = os.path.join(base, n)
    for dp, _, fns in os.walk(root):
        for f in fns:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            rel = "/".join(rel.split(os.sep))
            try:
                out[rel] = hashlib.sha256(io.open(p, "rb").read()).hexdigest()
            except OSError:
                out[rel] = "<unreadable>"
    return out


rn = {n for n in os.listdir(repo) if os.path.isdir(os.path.join(repo, n))}
dn = {n for n in os.listdir(dep) if os.path.isdir(os.path.join(dep, n))}
names = sorted(rn & dn)

clean = 0
issues = []
for n in names:
    a, b = tree(repo, n), tree(dep, n)
    onlyR = sorted(set(a) - set(b))
    onlyD = sorted(set(b) - set(a))
    diff = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    if not (onlyR or onlyD or diff):
        clean += 1
    else:
        issues.append((n, onlyR, onlyD, diff))

print("FULL-TREE identical: %d of %d shared skills" % (clean, len(names)))
for n, oR, oD, df in issues:
    print("\n  " + n)
    if df:
        print("    CONTENT DIFFERS (%d): %s" % (len(df), df[:6]))
    if oR:
        print("    in repo, NOT deployed (%d): %s" % (len(oR), oR[:6]))
    if oD:
        print("    deployed, NOT in repo (%d): %s" % (len(oD), oD[:6]))

print("\nrepo-only dirs: %s" % sorted(rn - dn))
print("deployed-only dirs: %s" % sorted(dn - rn))
print("'New folder' in skills/: %s" % os.path.isdir(os.path.join(repo, "New folder")))
