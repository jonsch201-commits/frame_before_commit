"""Append text to a file without letting the text touch a shell, and RETURN A RECEIPT.

Jon, 2026-09-12 ~22:2x CDT, verbatim (typos his):
  "'previous log append failed due to a shell quoting error' - solvable foundational defect? Seen
   this kind of stuff in a number of places... I feel like if you sit with yourself you can find a
   foundational soution"

THE CLASS, stated precisely, because "quoting bug" is too vague to fix:
CONTENT IS BEING PASSED THROUGH A SHELL'S WORD-SPLITTING AND QUOTING LAYER WHEN ONLY THE PROGRAM AT
THE FAR END NEEDS IT. Four shapes, all measured in this fleet:

  1. content -> argv through a shell:  echo "$MSG" >> log  ·  python -c "...$VAR..."  ·  -p "a\nb"
     (measured: a multi-line -p prompt truncated at the first newline because shell=True on Windows
      hands it to cmd.exe, rc=0, and the callee answered fluently from the fragment)
  2. content -> heredoc: the tool layer can transform the bytes before the shell sees them
     (measured tonight: a `\\n` in heredoc content arrived as a real newline and broke the file;
      and a quoted heredoc died with "unexpected EOF looking for matching `''")
  3. path -> shell: Windows backslashes are eaten. C:\\Users\\JonSc\\.claude became
     C:\\Users\\JonSc.claude in a hook's own output tonight.
  4. compound `cd X && ...`: cannot be permission-checked, so a hook blocks it outright.

WHY IT IS WORTH A LIBRARY RATHER THAN CARE. The expensive instance in this repo's record was not a
crash. `wiki/intake-triage/main-thread/27cb04/...i1.md:324`: "my first copy loop for this trunk's
payload copied nothing, because a shell quoting error fed the copier a path that did not exist, and
I recorded 'done' from counts that had not moved." A QUOTING ERROR THAT PRODUCED A FALSE SUCCESS.
Care does not catch that; a receipt does.

SO THIS HELPER DOES TWO THINGS, AND THE SECOND IS THE IMPORTANT ONE:
  * the payload never appears in a command line -- it arrives as a file path or as stdin BYTES;
  * the append is VERIFIED by re-reading the destination, and a delta that does not equal the
    payload length is a FAILURE even when every syscall returned success.

Usage (from a shell, with no content in the command line):
    python scripts/lib/safe_append.py LOG.md --payload-file note.md
    printf '%s' "$text" | python scripts/lib/safe_append.py LOG.md --stdin
Usage (from python, preferred -- no shell at all):
    from safe_append import append
    rec = append("LOG.md", text)          # raises AppendError on an unverified write

Exit: 0 verified | 3 write happened but did NOT verify | 4 could not run (UNKNOWN)
"""
import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class AppendError(RuntimeError):
    pass


def _lock(path, timeout=20.0):
    """A cross-platform exclusive lock: an O_EXCL sidecar, polled. No fcntl, no msvcrt -- this runs
    on Windows under Git Bash, under PowerShell, and inside hooks, and the only primitive all three
    agree on is an atomic create. A STALE lock older than `timeout` is STOLEN and the theft is
    reported in the receipt, because a wedged writer must not silence every later append."""
    lk = Path(str(path) + ".lock")
    deadline = time.time() + timeout
    stolen = False
    while True:
        try:
            fd = os.open(str(lk), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lk, stolen
        except FileExistsError:
            try:
                age = time.time() - lk.stat().st_mtime
            except OSError:
                age = 0.0
            if age > timeout:
                try:
                    lk.unlink()
                    stolen = True
                    continue
                except OSError:
                    pass
            if time.time() > deadline:
                raise AppendError(f"could not acquire {lk} within {timeout}s")
            time.sleep(0.05)


def append(path, text, encoding="utf-8", newline_before=None):
    """Append `text` to `path` and verify by re-reading. Returns a receipt dict.

    `newline_before` defaults to True when the file exists, is non-empty, and does not already end
    in a newline -- the single most common corruption in an append-only log is two records sharing
    a line, and it is invisible in rendered markdown.
    """
    p = Path(path)
    payload = text if isinstance(text, bytes) else text.encode(encoding, "strict")
    lk = None
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        lk, stolen = _lock(p)
        before = p.stat().st_size if p.exists() else 0
        if newline_before is None:
            newline_before = False
            if before:
                with open(p, "rb") as f:
                    f.seek(-1, os.SEEK_END)
                    newline_before = f.read(1) != b"\n"
        block = (b"\n" if newline_before else b"") + payload
        with open(p, "ab") as f:
            f.write(block)
            f.flush()
            os.fsync(f.fileno())
        after = p.stat().st_size
        grew = after - before
        if grew != len(block):
            raise AppendError(
                f"UNVERIFIED: {p} grew {grew} bytes, payload was {len(block)}. The write returned "
                f"success and the file does not agree -- treat the append as NOT done.")
        with open(p, "rb") as f:
            f.seek(before)
            landed = f.read()
        if landed != block:
            raise AppendError(f"UNVERIFIED: the bytes read back from {p} differ from the payload")
        return {"path": str(p), "before": before, "after": after, "appended": len(block),
                "sha256": hashlib.sha256(block).hexdigest()[:16], "lock_stolen": stolen}
    finally:
        if lk is not None:
            try:
                lk.unlink()
            except OSError:
                pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split(chr(10))[0])
    ap.add_argument("path")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--payload-file", help="file holding the text to append (never a command line)")
    src.add_argument("--stdin", action="store_true", help="read the payload from stdin as BYTES")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.stdin:
            payload = sys.stdin.buffer.read()
        else:
            payload = Path(a.payload_file).read_bytes()
    except OSError as e:
        print(f"APPEND UNKNOWN -- could not read the payload: {e}")
        return 4
    if not payload:
        print("APPEND UNKNOWN -- payload is EMPTY. An empty append is never a success: it is "
              "indistinguishable from a payload that a shell ate on the way here.")
        return 4
    try:
        rec = append(a.path, payload)
    except AppendError as e:
        print(f"APPEND FAILED -- {e}")
        return 3
    except OSError as e:
        print(f"APPEND UNKNOWN -- {e}")
        return 4
    if not a.quiet:
        print(f"APPEND VERIFIED {rec['path']}: {rec['before']} -> {rec['after']} B "
              f"(+{rec['appended']}, sha {rec['sha256']})"
              + ("  [STALE LOCK STOLEN]" if rec["lock_stolen"] else ""))
    return 0


def selftest():
    import tempfile
    fails = []
    NL = chr(10)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)

        # 1. the payloads that break a shell must survive intact
        nasty = [
            'a "quoted" string',
            "it's an apostrophe",
            "back\\slash and \\n literal",
            "$VAR ${BRACE} `backtick` $(cmd)",
            "C:\\Users\\JonSc\\.claude\\projects",
            "multi" + NL + "line" + NL + "payload",
            "unicode: \u26d4 \u2014 \u2192 cp1252-hostile",
            "trailing spaces   ",
            "semi; colon && amp | pipe > redir",
        ]
        f = t / "log.md"
        for s in nasty:
            append(f, s)
        got = f.read_bytes().decode("utf-8")
        for s in nasty:
            if s not in got:
                fails.append(f"payload did not survive: {s!r}")

        # 2. every append is separated -- no two records share a line
        lines = [l for l in got.split(NL) if l.strip()]
        if len(lines) < len(nasty):
            fails.append(f"records merged: {len(lines)} non-blank lines for {len(nasty)} appends")

        # 3. an empty payload is UNKNOWN via the CLI, never a silent success
        (t / "empty").write_bytes(b"")
        if main([str(t / "l2.md"), "--payload-file", str(t / "empty")]) != 4:
            fails.append("empty payload did not return UNKNOWN")

        # 4. a missing payload file is UNKNOWN, not an empty append
        if main([str(t / "l3.md"), "--payload-file", str(t / "nope")]) != 4:
            fails.append("missing payload file did not return UNKNOWN")
        if (t / "l3.md").exists():
            fails.append("a failed append created the destination anyway")

        # 5. NEGATIVE ARM: a verification that cannot detect a short write is worthless, so prove
        #    the verifier fires. Monkeypatch the write to drop a byte.
        import builtins
        real_open = builtins.open

        def lying_open(p, mode="r", *a2, **k2):
            fh = real_open(p, mode, *a2, **k2)
            if "a" in mode:
                real_write = fh.write

                def short(b):
                    return real_write(b[:-1] if len(b) > 1 else b)
                fh.write = short
            return fh
        builtins.open = lying_open
        try:
            append(t / "l4.md", "this write will be short by one byte")
            fails.append("a SHORT WRITE was reported as verified -- the receipt is decorative")
        except AppendError:
            pass
        finally:
            builtins.open = real_open

        # 6. the payload is passed as bytes through stdin without a shell in the path
        rec = append(t / "l5.md", "bytes payload".encode("utf-8"))
        if rec["appended"] != len("bytes payload"):
            fails.append("bytes payload length mismatch")

        # 7. a file not ending in a newline gains one; a file that does, does not
        (t / "l6.md").write_bytes(b"no trailing newline")
        append(t / "l6.md", "next")
        if (t / "l6.md").read_bytes() != b"no trailing newline" + NL.encode() + b"next":
            fails.append("separator logic wrong on a file with no trailing newline")
        (t / "l7.md").write_bytes(b"has one" + NL.encode())
        append(t / "l7.md", "next")
        if (t / "l7.md").read_bytes() != b"has one" + NL.encode() + b"next":
            fails.append("separator logic added a blank line where the file already ended in one")

    for x in fails:
        print("  FAIL " + x)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} -- 7 groups, "
          f"{len(fails)} failure(s). The load-bearing arm is group 5: it makes the append lie by a "
          f"byte and asserts the receipt CATCHES it. Without that arm the verification is decoration.")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
