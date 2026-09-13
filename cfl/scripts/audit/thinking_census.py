#!/usr/bin/env python3
"""Thinking-fidelity census of a claude.ai export — is the thinking actually there?

WHY THIS EXISTS
---------------
The transcript parser stamps every extract with a note saying thinking is "preserved."
It never checks. On the 2026-07-26 export, every thinking block of a claude-fable-5
session arrived `thinking_hidden: true` — signature only, zero readable text — and the
extraction note said "preserved" anyway. That is the derive-don't-record defect in its
purest form: a claim written down once, then diverging from reality with nothing able
to notice. This census is the check the note never had.

The operating hypothesis it exists to test: claude.ai exports stopped carrying readable
thinking at the Fable model boundary. The census reads the export's conversations.json
directly from the zip (no extraction), counts readable vs hidden thinking per
conversation, recovers the per-block model where the block's signature carries it, and
reports the boundary — the latest conversation with readable thinking and the earliest
with all-hidden thinking.

WHAT IT REPORTS
---------------
  Per conversation : uuid, title, date range, thinking total / readable / hidden.
  Per month        : block-level readable/hidden counts (by block timestamp).
  Per model        : readable/hidden crosstab — the direct hypothesis test. The model
                     id is parsed from the thinking block's signature (a base64
                     protobuf that length-prefixes a plaintext model string in most
                     eras). Best-effort: older signatures carry no plaintext model and
                     are counted as "(unknown)". Do NOT treat "(unknown)" as a model.
  Boundary         : latest readable-thinking conversation vs earliest all-hidden one.

Classification: a block is READABLE when it has non-empty thinking text and
`thinking_hidden` is falsy; HIDDEN when `thinking_hidden` is true, or when the text is
empty but a signature is present (signature-only). Empty text with no signature is
counted hidden too, loudly, as "bare".

WHY IT IS ADVISORY AND NOT BLOCKING
-----------------------------------
Whether Anthropic ships readable thinking is not a defect in this repo's files, and a
gate that blocks on an upstream export format can never go green from here. The census
is loud, runs on demand, and blocks nothing. What it changes is downstream honesty:
extraction notes must say what THIS tool measured, not what the parser assumes.

Usage:
    python scripts/audit/thinking_census.py --zip raw/Anthropic_zips/data-...-batch-0000.zip
    python scripts/audit/thinking_census.py --zip ... --no-per-conversation   # summary only

Exit: 0 on success, 2 if the zip or conversations.json is unreadable.
"""
import argparse
import base64
import collections
import json
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

MODEL_PAT = re.compile(rb"claude-[a-z0-9][a-z0-9.\-]*")


def model_from_signature(sig):
    """Best-effort model id from a thinking-block signature.

    The signature is base64 of a protobuf; in most eras it length-prefixes a plaintext
    model string (e.g. ...\\x0eclaude-fable-5...). A bare regex over-captures the byte
    after the string, so the byte immediately before the match is read as the protobuf
    length and used to trim. Signatures with no plaintext model return None.
    """
    if not sig:
        return None
    try:
        raw = base64.b64decode(sig + "=" * (-len(sig) % 4))
    except Exception:
        return None
    m = MODEL_PAT.search(raw)
    if not m:
        return None
    s = m.start()
    ln = raw[s - 1] if s >= 1 else 0
    if 6 < ln < 60:
        return raw[s:s + ln].decode("ascii", "replace")
    return m.group().decode("ascii", "replace")


def classify(block):
    """-> 'readable' | 'hidden' | 'bare'. See module docstring."""
    text = (block.get("thinking") or "").strip()
    if block.get("thinking_hidden") or block.get("hidden"):
        return "hidden"
    if text:
        return "readable"
    return "hidden" if block.get("signature") else "bare"


def probe_schema(convs):
    """Fail loudly if the export schema is not what this tool was written against.

    The source_id-vs-uuid field bug produced a false 29-lost-sessions claim because a
    reader assumed a field name. This probe is the guard: verify the fields we rely on
    actually exist before deriving anything from their absence.
    """
    problems = []
    if not isinstance(convs, list):
        return ["conversations.json top level is %s, expected list" % type(convs).__name__]
    sample = convs[0] if convs else {}
    for f in ("uuid", "name", "created_at", "updated_at", "chat_messages"):
        if f not in sample:
            problems.append("conversation missing expected field %r" % f)
    seen_thinking_keys = None
    for c in convs:
        for m in c.get("chat_messages") or []:
            for b in m.get("content") or []:
                if b.get("type") == "thinking":
                    seen_thinking_keys = set(b.keys())
                    break
            if seen_thinking_keys:
                break
        if seen_thinking_keys:
            break
    if seen_thinking_keys is not None:
        for f in ("thinking", "thinking_hidden", "signature", "start_timestamp"):
            if f not in seen_thinking_keys:
                problems.append("thinking block missing expected field %r" % f)
    return problems


def month_of(ts):
    return (ts or "")[:7] or "(undated)"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--zip", required=True, help="claude.ai export zip (read in place, never extracted)")
    ap.add_argument("--json-name", default="conversations.json")
    ap.add_argument("--no-per-conversation", action="store_true", help="suppress the per-conversation table")
    a = ap.parse_args()

    try:
        with zipfile.ZipFile(a.zip) as z:
            with z.open(a.json_name) as fh:
                convs = json.load(fh)
    except (OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as e:
        print("ERROR: cannot read %s from %s: %s" % (a.json_name, a.zip, e), file=sys.stderr)
        return 2

    for p in probe_schema(convs):
        print("SCHEMA WARNING: %s — counts below may be derived from absence, not fact." % p,
              file=sys.stderr)

    rows = []                                  # per-conversation
    by_month = collections.defaultdict(collections.Counter)   # block month -> counts
    by_model = collections.defaultdict(collections.Counter)   # model -> counts
    latest_readable = None                     # (block_ts, conv)
    earliest_allhidden = None                  # (first_block_ts, conv, n_hidden)

    for c in convs:
        counts = collections.Counter()
        block_ts = []
        conv_models = collections.Counter()
        for m in c.get("chat_messages") or []:
            for b in m.get("content") or []:
                if b.get("type") != "thinking":
                    continue
                cls = classify(b)
                counts[cls] += 1
                ts = b.get("start_timestamp") or m.get("created_at") or ""
                block_ts.append(ts)
                by_month[month_of(ts)][cls] += 1
                model = model_from_signature(b.get("signature")) or "(unknown)"
                by_model[model][cls] += 1
                conv_models[model] += 1
                if cls == "readable" and ts and (latest_readable is None or ts > latest_readable[0]):
                    latest_readable = (ts, c)
        total = sum(counts.values())
        msgs = c.get("chat_messages") or []
        d0 = (msgs[0].get("created_at") if msgs else None) or c.get("created_at") or ""
        d1 = (msgs[-1].get("created_at") if msgs else None) or c.get("updated_at") or ""
        rows.append((d1, c.get("uuid", "?"), (c.get("name") or "(untitled)")[:40],
                     d0[:10], d1[:10], total, counts["readable"],
                     counts["hidden"] + counts["bare"], conv_models))
        if total and counts["readable"] == 0:
            first_ts = min(t for t in block_ts if t) if any(block_ts) else d0
            if earliest_allhidden is None or first_ts < earliest_allhidden[0]:
                earliest_allhidden = (first_ts, c, total)

    n_conv = len(rows)
    n_with = sum(1 for r in rows if r[5])
    print("=== THINKING-FIDELITY CENSUS ===\n")
    print("  zip           : %s" % a.zip)
    print("  conversations : %d  (%d with thinking blocks)" % (n_conv, n_with))
    g_total = sum(r[5] for r in rows); g_read = sum(r[6] for r in rows); g_hid = sum(r[7] for r in rows)
    print("  thinking      : %d total = %d readable + %d hidden/signature-only\n" % (g_total, g_read, g_hid))

    if not a.no_per_conversation:
        print("--- per conversation (sorted by last message) ---")
        print("%-10s %-10s %-36s %-40s %6s %6s %6s" % ("first", "last", "uuid", "title", "think", "read", "hidden"))
        for d1, uuid, title, s0, s1, tot, rd, hid, _m in sorted(rows):
            print("%-10s %-10s %-36s %-40s %6d %6d %6d" % (s0, s1, uuid, title, tot, rd, hid))
        print()

    print("--- by month (block timestamps) ---")
    print("%-10s %8s %10s %8s" % ("month", "blocks", "readable", "hidden"))
    for month in sorted(by_month):
        c = by_month[month]
        tot = sum(c.values())
        print("%-10s %8d %10d %8d" % (month, tot, c["readable"], c["hidden"] + c["bare"]))
    print()

    print("--- by model (parsed from block signature; best-effort) ---")
    print("%-34s %8s %10s %8s" % ("model", "blocks", "readable", "hidden"))
    for model in sorted(by_model, key=lambda k: -sum(by_model[k].values())):
        c = by_model[model]
        print("%-34s %8d %10d %8d" % (model, sum(c.values()), c["readable"], c["hidden"] + c["bare"]))
    print()

    print("--- boundary report ---")
    if latest_readable:
        ts, c = latest_readable
        print("  LATEST conversation with readable thinking:")
        print("    %s  %s  (block at %s)" % (c.get("uuid"), (c.get("name") or "(untitled)")[:60], ts))
    else:
        print("  No readable thinking anywhere in this export.")
    if earliest_allhidden:
        ts, c, n = earliest_allhidden
        print("  EARLIEST conversation with ALL thinking hidden (%d blocks):" % n)
        print("    %s  %s  (first block at %s)" % (c.get("uuid"), (c.get("name") or "(untitled)")[:60], ts))
    else:
        print("  No all-hidden conversation in this export.")
    print("\n  Advisory only. An extraction note may claim thinking is 'preserved' only for")
    print("  conversations this census counts as readable — anything else is derive-don't-record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
