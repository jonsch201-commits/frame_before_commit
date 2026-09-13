#!/usr/bin/env python3
"""usage_meter.py -- US-1 (lane B-4): a programmatic read of the account's weekly usage
percentages (what `/usage` prints), sampled every 30 minutes without a keystroke.

Reverse-engineered from the installed Claude Code bundle (bin/claude.exe), 2026-09-02:
  - endpoint:      GET https://api.anthropic.com/api/oauth/usage
  - headers:       anthropic-version: 2023-06-01
                    anthropic-beta: oauth-2025-04-20
                    Authorization: Bearer <access token>
  - token source:  ~/.claude/.credentials.json -> claudeAiOauth.accessToken
                    (same file the CLI itself reads; NOT the Windows Credential Manager
                    on this machine -- that file exists on disk in plaintext JSON)
  - the CLI's own in-app help text documents the identical pattern for a sibling endpoint:
    `curl -H 'anthropic-version: 2023-06-01' -H 'anthropic-beta: oauth-2025-04-20'
     -H "Authorization: Bearer $CLAUDE_CODE_OAUTH_TOKEN" https://api.anthropic.com/v1/mcp_servers`

SECURITY / REDACTION DISCIPLINE (binding, do not relax):
  - The access/refresh token is read into memory only to build the Authorization header.
  - It is NEVER written to a file, printed, logged, or included in any exception message.
  - Every payload this script writes to disk passes through `assert_no_token_leak()` first,
    which scans the serialized bytes for any 8-character substring of the live token and
    refuses to write (raises) if found. `--selftest` exercises this guard directly.
  - On failure, the response head written to USAGE-IMPOSSIBLE-cfl.md is also passed through
    the same guard before writing.

Exit codes: 0 = wrote USAGE-CURRENT/USAGE-LOG. 3 = non-200/auth failure after retries,
wrote USAGE-IMPOSSIBLE-cfl.md. 2 = token could not be located at all (also writes
USAGE-IMPOSSIBLE-cfl.md). 1 = --selftest failure.
"""
import io
import json
import os
import sys
import time
import datetime
import urllib.request
import urllib.error

HOME = os.path.expanduser('~')
CREDS_PATH = os.path.join(HOME, '.claude', '.credentials.json')
OUT_DIR = r'N:\claude-gists-private'
CURRENT_PATH = os.path.join(OUT_DIR, 'USAGE-CURRENT-cfl.json')
LOG_PATH = os.path.join(OUT_DIR, 'USAGE-LOG-cfl.jsonl')
IMPOSSIBLE_PATH = os.path.join(OUT_DIR, 'USAGE-IMPOSSIBLE-cfl.md')

API_URL = 'https://api.anthropic.com/api/oauth/usage'
ANTHROPIC_VERSION = '2023-06-01'
ANTHROPIC_BETA = 'oauth-2025-04-20'

FIELDS = [
    'five_hour', 'seven_day', 'seven_day_oauth', 'seven_day_opus', 'seven_day_sonnet',
    'seven_day_overage', 'resets_at',
]

LOOP_INTERVAL_S = 1800
MAX_ATTEMPTS = 3
RETRY_DELAY_S = 60


class TokenNotFound(Exception):
    pass


def load_token():
    """Read the OAuth access token the same way the CLI does: from
    ~/.claude/.credentials.json, key claudeAiOauth.accessToken. Returns the raw
    token string. Caller must never write/print/log this value or any substring
    of it -- see assert_no_token_leak()."""
    if not os.path.exists(CREDS_PATH):
        raise TokenNotFound('no credentials file at %s' % CREDS_PATH)
    with io.open(CREDS_PATH, encoding='utf-8') as f:
        data = json.load(f)
    oauth = data.get('claudeAiOauth') or {}
    token = oauth.get('accessToken')
    if not token or not isinstance(token, str):
        raise TokenNotFound('claudeAiOauth.accessToken missing or empty in %s' % CREDS_PATH)
    return token


def redact_len(s):
    """Length-only redaction: never emit the value itself."""
    return '<redacted, len=%d>' % len(s) if s else '<empty>'


def assert_no_token_leak(payload_text, token):
    """Refuse to write if any 8-char substring of the live token appears in
    payload_text. This is the mechanical guard behind the --selftest check and
    behind every disk write in this script."""
    if not token:
        return
    n = 8
    if len(token) < n:
        # token shorter than the window: fall back to whole-token containment
        if token in payload_text:
            raise RuntimeError('REDACTION GUARD TRIPPED: full token found in payload meant for disk')
        return
    for i in range(0, len(token) - n + 1):
        chunk = token[i:i + n]
        if chunk in payload_text:
            raise RuntimeError(
                'REDACTION GUARD TRIPPED: an 8-char token substring was found in a '
                'payload meant for disk. Write refused.'
            )


def fetch_usage(token):
    """GET the usage endpoint. Returns (status_code, response_text_or_None, headers_dict).
    Never raises on HTTP-level errors (401/403/etc) -- returns the status and body instead
    so the caller can write a proper USAGE-IMPOSSIBLE report."""
    req = urllib.request.Request(
        API_URL,
        method='GET',
        headers={
            'anthropic-version': ANTHROPIC_VERSION,
            'anthropic-beta': ANTHROPIC_BETA,
            'Authorization': 'Bearer %s' % token,
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return e.code, body, dict(e.headers or {})
    except urllib.error.URLError as e:
        return None, str(e.reason), {}


def redact_response_head(text, token, n=300):
    """First n chars of a response body/reason, with any token substring scrubbed
    (defense in depth -- an error body should never echo the bearer token, but
    check anyway before this ever reaches disk)."""
    head = (text or '')[:n]
    if token:
        window = 8
        if len(token) >= window:
            for i in range(0, len(token) - window + 1):
                chunk = token[i:i + window]
                if chunk and chunk in head:
                    head = head.replace(chunk, '<redacted>')
        elif token in head:
            head = head.replace(token, '<redacted>')
    return head


def write_impossible(reason, status, body_head, token):
    os.makedirs(OUT_DIR, exist_ok=True)
    lines = [
        '# USAGE-IMPOSSIBLE (cfl)',
        '',
        '`generated_at:` %s' % datetime.datetime.now().isoformat(timespec='seconds'),
        '',
        '## Reason',
        '',
        reason,
        '',
        '## Request shape',
        '',
        '```',
        'GET %s' % API_URL,
        'anthropic-version: %s' % ANTHROPIC_VERSION,
        'anthropic-beta: %s' % ANTHROPIC_BETA,
        'Authorization: Bearer %s' % redact_len(token) if token else 'Authorization: Bearer <no token loaded>',
        '```',
        '',
        '## HTTP status',
        '',
        str(status),
        '',
        '## Response head (first 300 chars, redacted)',
        '',
        '```',
        body_head or '(none)',
        '```',
    ]
    text = '\n'.join(lines) + '\n'
    assert_no_token_leak(text, token)
    with io.open(IMPOSSIBLE_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    return IMPOSSIBLE_PATH


def extract_record(data):
    fetched_at = datetime.datetime.now().isoformat(timespec='seconds')
    rec = {'fetched_at': fetched_at}
    for k in FIELDS:
        rec[k] = data.get(k)
    rec['raw_keys'] = sorted(data.keys())
    return rec


def write_current_and_log(rec, token):
    os.makedirs(OUT_DIR, exist_ok=True)
    text = json.dumps(rec, indent=2, ensure_ascii=False)
    assert_no_token_leak(text, token)
    with io.open(CURRENT_PATH, 'w', encoding='utf-8') as f:
        f.write(text + '\n')
    log_line = json.dumps(rec, ensure_ascii=False)
    assert_no_token_leak(log_line, token)
    with io.open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')


def run_once():
    try:
        token = load_token()
    except TokenNotFound as e:
        path = write_impossible(
            'Token could not be located: %s' % e, None, None, None,
        )
        print('TOKEN NOT FOUND: %s' % e)
        print('Wrote %s' % path)
        return 2

    last_status, last_body = None, None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        status, body, _headers = fetch_usage(token)
        last_status, last_body = status, body
        if status == 200:
            try:
                data = json.loads(body)
            except Exception as e:
                path = write_impossible(
                    'HTTP 200 but response body was not valid JSON: %s' % e,
                    status, redact_response_head(body, token), token,
                )
                print('BAD JSON on 200. Wrote %s' % path)
                return 3
            rec = extract_record(data)
            write_current_and_log(rec, token)
            print('OK 200. fields=%s raw_keys=%s' % (
                {k: rec.get(k) for k in FIELDS}, rec['raw_keys']))
            print('Wrote %s' % CURRENT_PATH)
            print('Appended %s' % LOG_PATH)
            return 0
        if status in (401, 403):
            # auth failure: no point retrying with the same token
            break
        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_DELAY_S)

    reason = 'Non-200 response (or transport error) after %d attempt(s). status=%s' % (
        min(attempt, MAX_ATTEMPTS), last_status)
    path = write_impossible(
        reason, last_status, redact_response_head(last_body, token), token,
    )
    print('FAILED: %s' % reason)
    print('Wrote %s' % path)
    return 3


def run_loop():
    while True:
        rc = run_once()
        print('--- sleeping %ds (rc=%d) ---' % (LOOP_INTERVAL_S, rc))
        time.sleep(LOOP_INTERVAL_S)


def run_selftest():
    """Assert the redaction guard actually trips: construct a payload that
    contains an 8-char substring of a fake 'token' and confirm assert_no_token_leak
    refuses it, then confirm a clean payload passes."""
    fake_token = 'sk-ant-oat01-ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    leaking_payload = json.dumps({'note': 'oops this has ' + fake_token[10:18] + ' in it'})
    tripped = False
    try:
        assert_no_token_leak(leaking_payload, fake_token)
    except RuntimeError:
        tripped = True
    if not tripped:
        print('SELFTEST FAIL: guard did not trip on a leaking payload')
        return 1

    clean_payload = json.dumps({'note': 'nothing sensitive here', 'five_hour': 12})
    try:
        assert_no_token_leak(clean_payload, fake_token)
    except RuntimeError:
        print('SELFTEST FAIL: guard tripped on a clean payload (false positive)')
        return 1

    # also confirm redact_response_head scrubs a token substring
    body = 'error body containing ' + fake_token[5:13] + ' leaked'
    head = redact_response_head(body, fake_token)
    if fake_token[5:13] in head:
        print('SELFTEST FAIL: redact_response_head did not scrub the substring')
        return 1

    print('SELFTEST OK: redaction guard trips on leaking payload, passes clean payload, '
          'and redact_response_head scrubs token substrings from error bodies.')
    return 0


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        sys.exit(run_selftest())
    if '--loop' in args:
        run_loop()
        return
    # default / --once
    sys.exit(run_once())


if __name__ == '__main__':
    main()
