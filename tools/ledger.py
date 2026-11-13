#!/usr/bin/env python3
"""Small helper for seen-jobs.tsv so nobody has to read the whole ledger.

  ledger.py days                  days to search: since the last first_seen date (min 1, max 31)
  ledger.py count <site>          number of IDs for a site seen in the last 35 days (the browser cache holds the same set)
  ledger.py seen <site>           those IDs as a JSON object {id: "YYYY-MM-DD"}, for reseeding the browser cache
  ledger.py add                   append rows from stdin, one per line: "<id> <site> <status>"; skips IDs already present and lists them
  ledger.py set <id> <status>     change one ID's status
  ledger.py counts                totals by status
  ledger.py start                 record that a sweep has just been launched (cleared by stamp)
  ledger.py stamp "<summary>"     record that a search just ran, with a one-line result summary
  ledger.py since                 any sweep still running (or lost), then hours since the last search and its summary
  ledger.py prefix <site>         the line to put before seek-search.js / linkedin-search.js (days, expected count, locations and search terms from me/config.json)
"""
import json
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / 'data' / 'seen-jobs.tsv'
LAST = ROOT / 'data' / 'last-search.txt'
RUNNING = ROOT / 'data' / 'search-running.txt'
CONFIG = ROOT / 'me' / 'config.json'
RECENT_DAYS = 35
LOST_MINUTES = 30
HEADER = 'job_id\tsite\tfirst_seen\tstatus\n'


def rows():
    lines = LEDGER.read_text().splitlines()[1:]
    return [dict(zip(('id', 'site', 'date', 'status'), line.split('\t'))) for line in lines if line.strip()]


def recent(site):
    cutoff = (date.today() - timedelta(days=RECENT_DAYS)).isoformat()
    return {r['id']: r['date'] for r in rows() if r['site'] == site and r['date'] >= cutoff}


def main(argv):
    cmd = argv[0] if argv else ''
    if cmd == 'days':
        last = max(date.fromisoformat(r['date']) for r in rows())
        print(min(31, max(1, (date.today() - last).days + 1)))
    elif cmd == 'count':
        print(len(recent(argv[1])))
    elif cmd == 'seen':
        print(json.dumps(recent(argv[1]), separators=(',', ':')))
    elif cmd == 'add':
        have = {r['id'] for r in rows()}
        today = date.today().isoformat()
        added = 0
        skipped = []
        with LEDGER.open('a') as f:
            for line in sys.stdin:
                parts = line.split()
                if len(parts) != 3:
                    continue
                if parts[0] in have:
                    skipped.append(parts[0])
                    continue
                f.write(f'{parts[0]}\t{parts[1]}\t{today}\t{parts[2]}\n')
                have.add(parts[0])
                added += 1
        print(f'added {added}')
        if skipped:
            print(f"skipped {len(skipped)} already in the ledger (don't queue these): {' '.join(skipped)}")
    elif cmd == 'set':
        text = LEDGER.read_text().splitlines(keepends=True)
        hits = 0
        for i, line in enumerate(text):
            cols = line.rstrip('\n').split('\t')
            if cols[0] == argv[1]:
                cols[3] = argv[2]
                text[i] = '\t'.join(cols) + '\n'
                hits += 1
        LEDGER.write_text(''.join(text))
        print(f'updated {hits}')
    elif cmd == 'counts':
        all_rows = rows()
        print(dict(Counter(r['status'] for r in all_rows)), 'total', len(all_rows),
              'last search', max(r['date'] for r in all_rows))
    elif cmd == 'start':
        RUNNING.write_text(datetime.now().isoformat(timespec='minutes') + '\n')
        print('sweep started')
    elif cmd == 'stamp':
        LAST.write_text(f"{datetime.now().isoformat(timespec='minutes')}\t{' '.join(argv[1:])}\n")
        RUNNING.unlink(missing_ok=True)
        print('stamped')
    elif cmd == 'since':
        if RUNNING.exists():
            started = RUNNING.read_text().strip()
            minutes = (datetime.now() - datetime.fromisoformat(started)).total_seconds() / 60
            if minutes <= LOST_MINUTES:
                print(f'SWEEP RUNNING: started {minutes:.0f} min ago ({started}), report not processed yet')
            else:
                print(f'SWEEP LOST: started {minutes:.0f} min ago ({started}) and never processed; '
                      'its listings come back on the next search (via a reseed)')
        if not LAST.exists():
            print('never')
            return
        when, _, summary = LAST.read_text().strip().partition('\t')
        hours = (datetime.now() - datetime.fromisoformat(when)).total_seconds() / 3600
        print(f'{hours:.1f} hours ago ({when}): {summary}')
    elif cmd == 'prefix':
        site = argv[1]
        s = json.loads(CONFIG.read_text())['search']
        last = max(date.fromisoformat(r['date']) for r in rows())
        days = min(31, max(1, (date.today() - last).days + 1))
        terms = s['seek_slugs'] if site == 'seek' else s['linkedin_keywords']
        locs = s['seek_locations'] if site == 'seek' else s['linkedin_locations']
        print(f"var DAYS = {days}, EXPECT = {len(recent(site))}, LOCATIONS = {json.dumps(locs)}, "
              f"TERMS = {json.dumps(terms)}, ENTRY_TERMS = {json.dumps(s.get('linkedin_entry_filter_keywords', []))}, "
              f"BAD = new RegExp({json.dumps(s['title_exclude'])}, 'i'), MAX_PAY_K = {s['max_salary_k']};")
    else:
        print(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
