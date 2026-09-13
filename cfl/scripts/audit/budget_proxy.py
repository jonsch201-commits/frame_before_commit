#!/usr/bin/env python3
"""budget_proxy.py -- B-6: hourly token burn across ALL trunks' session JSONLs on C:, as a proxy for the
weekly Claude budget until the usage meter (US-1) publishes. Read-only over ~/.claude/projects/**/*.jsonl.
Exit 0 = row written; exit 2 = a JSONL could not be read (UNKNOWN dominates: no row is written as if clean).
Pre-stated loss condition for the first run: baseline_tokens_per_hour must be > 0 and today's hours > 0.
"""
import io, json, os, sys, glob, datetime, collections
HOME = os.path.expanduser('~')
ROOT = os.path.join(HOME, '.claude', 'projects')
OUT_DIR = r'N:\claude-gists-private'
RESET = datetime.datetime(2026, 8, 28, 14, 0)          # weekly reset (Fri 14:00 CDT)
PLAN_T0 = datetime.datetime(2026, 9, 2, 13, 0)  # recalibrated to the first meter reading (13:16); earlier rows in the log used t0 = 08:45 and are NOT comparable
PCT_USED_AT_T0 = 52.0  # MEASURED by usage_meter.py 2026-09-02 13:16 CDT (seven_day.utilization); was 20.0 from Jon's 08:4x '80% remaining', which the meter falsified
BASE_LO, BASE_HI = datetime.datetime(2026, 8, 29, 0, 0), datetime.datetime(2026, 9, 1, 0, 0)
TZ = datetime.timedelta(hours=-5)                      # CDT

def local(ts):
    t = datetime.datetime.strptime(ts[:19], '%Y-%m-%dT%H:%M:%S')
    return t + TZ

hours = collections.Counter(); files = 0; bad = []; seen = set()
for p in glob.glob(os.path.join(ROOT, '**', '*.jsonl'), recursive=True):
    files += 1
    try:
        with io.open(p, encoding='utf-8', errors='replace') as f:
            for line in f:
                if '"usage"' not in line: continue
                try: d = json.loads(line)
                except Exception: continue
                if d.get('type') != 'assistant': continue
                m = d.get('message') or {}; mid = m.get('id')
                if mid and (p, mid) in seen: continue
                if mid: seen.add((p, mid))
                u = m.get('usage') or {}
                ts = d.get('timestamp');
                if not ts: continue
                h = local(ts).replace(minute=0, second=0, microsecond=0)
                hours[h] += u.get('output_tokens', 0) + u.get('input_tokens', 0) \
                    + u.get('cache_creation_input_tokens', 0) + int(u.get('cache_read_input_tokens', 0) * 0.1)
    except OSError as e:
        bad.append((p, str(e)))
if bad:
    print('UNKNOWN: %d unreadable JSONL(s): %s' % (len(bad), bad[:3])); sys.exit(2)

base_hours = [v for k, v in hours.items() if BASE_LO <= k < BASE_HI]
base_rate = sum(base_hours) / max(1, (BASE_HI - BASE_LO).total_seconds() / 3600)
since_reset = sum(v for k, v in hours.items() if RESET <= k < PLAN_T0)
tokens_per_pct = since_reset / PCT_USED_AT_T0 if since_reset else 0
since_t0 = sum(v for k, v in hours.items() if k >= PLAN_T0)
now = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
last = hours.get(now - datetime.timedelta(hours=1), 0)
today = [v for k, v in hours.items() if k.date() == datetime.date.today()]
est_used_since_t0 = since_t0 / tokens_per_pct if tokens_per_pct else None
row = dict(ts=datetime.datetime.now().isoformat(timespec='seconds'), files=files,
           last_hour_tokens=last, weekend_hourly_mean=round(base_rate),
           ratio_last_hour_to_weekend=round(last / base_rate, 2) if base_rate else None,
           tokens_since_reset_to_t0=since_reset, tokens_per_pct=round(tokens_per_pct),
           tokens_since_t0=since_t0, est_pct_used_since_t0=round(est_used_since_t0, 2) if est_used_since_t0 is not None else None,
           est_pct_left=round(100 - PCT_USED_AT_T0 - est_used_since_t0, 2) if est_used_since_t0 is not None else None,
           today_nonzero_hours=sum(1 for v in today if v))
cache = None
try:
    cj = json.load(io.open(os.path.join(HOME, '.claude.json'), encoding='utf-8'))
    cache = cj.get('cachedUsageUtilization')
except Exception: pass
row['cached_util'] = cache
os.makedirs(OUT_DIR, exist_ok=True)
with io.open(os.path.join(OUT_DIR, 'BUDGET-PROXY-cfl.jsonl'), 'a', encoding='utf-8') as f:
    f.write(json.dumps(row) + '\n')
print(json.dumps(row))
if '--debug' in sys.argv:
    for k in sorted(hours):
        if k.date() == datetime.date.today(): print('  ', k, hours[k])
if base_rate == 0 or row['today_nonzero_hours'] == 0:
    print('PRE-STATED LOSS: baseline or today is zero -> instrument blind'); sys.exit(1)
