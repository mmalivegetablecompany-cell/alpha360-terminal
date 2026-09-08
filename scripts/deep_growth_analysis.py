import json
import re
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
if not m:
    print("Could not find rawData")
    sys.exit(1)

data = json.loads(m.group(1))

stocks = []
for s in data:
    qh = s.get('quarters_history', [])
    revs = [q.get('Revenue') for q in qh]
    is_synth = (len(revs) == 8 and revs[0] == 324.0 and revs[-1] == 450.0)
    
    rev_yoys = [q['YoY_Rev'] for q in qh if q.get('YoY_Rev') is not None]
    pat_yoys = [q['YoY_PAT'] for q in qh if q.get('YoY_PAT') is not None]
    
    pos_rev = sum(1 for y in rev_yoys if y > 0)
    pos_pat = sum(1 for y in pat_yoys if y > 0)
    
    both_pos = 0
    for q in qh:
        if q.get('YoY_Rev') is not None and q.get('YoY_PAT') is not None:
            if q['YoY_Rev'] > 0 and q['YoY_PAT'] > 0:
                both_pos += 1

    item = {
        'symbol': s.get('symbol'),
        'name': s.get('name'),
        'sector': s.get('sector'),
        'mcap': s.get('mcap'),
        'mcap_cr': s.get('mcap_cr', 0),
        'master_score': s.get('master_score', 0),
        'funda_score': s.get('score', 0),
        'today_price': s.get('today_price', 0),
        'today_pe': s.get('today_pe', 0),
        'today_pb': s.get('today_pb', 0),
        'today_peg': s.get('today_peg', 0),
        'consensus': s.get('consensus', ''),
        'tier': s.get('tier', ''),
        'is_synth': is_synth,
        'valid_q': len(rev_yoys),
        'pos_rev': pos_rev,
        'pos_pat': pos_pat,
        'both_pos': both_pos,
        'avg_rev': round(float(np.mean(rev_yoys)), 2) if rev_yoys else 0.0,
        'min_rev': round(float(np.min(rev_yoys)), 2) if rev_yoys else 0.0,
        'max_rev': round(float(np.max(rev_yoys)), 2) if rev_yoys else 0.0,
        'std_rev': round(float(np.std(rev_yoys)), 2) if rev_yoys else 0.0,
        'avg_pat': round(float(np.mean(pat_yoys)), 2) if pat_yoys else 0.0,
        'min_pat': round(float(np.min(pat_yoys)), 2) if pat_yoys else 0.0,
        'max_pat': round(float(np.max(pat_yoys)), 2) if pat_yoys else 0.0,
        'std_pat': round(float(np.std(pat_yoys)), 2) if pat_yoys else 0.0,
        'rev_yoys': rev_yoys,
        'pat_yoys': pat_yoys,
        'quarters_history': qh
    }
    stocks.append(item)

print("\n--- Recently Listed / Partial History Stocks with 100% Positive YoY Growth ---")
for s in stocks:
    if not s['is_synth'] and 0 < s['valid_q'] < 8:
        if s['pos_rev'] == s['valid_q'] and s['pos_pat'] == s['valid_q']:
            print(f"{s['symbol']} ({s['name']}): {s['valid_q']}/{s['valid_q']} Qtrs Pos YoY | Rev YoY: {s['min_rev']}% to {s['max_rev']}% (Avg {s['avg_rev']}%) | PAT YoY: {s['min_pat']}% to {s['max_pat']}% (Avg {s['avg_pat']}%) | Score: {s['master_score']}")

# Also let's check stocks with 7/8 positive YoY (nearly perfect consistency)
print("\n--- Real Stocks with 7/8 Quarters Positive YoY Growth (High Consistency) ---")
near_perfect = [s for s in stocks if not s['is_synth'] and s['valid_q'] == 8 and s['both_pos'] == 7]
near_perfect.sort(key=lambda x: (x['avg_pat'] + x['avg_rev'], x['master_score']), reverse=True)
for s in near_perfect[:15]:
    print(f"{s['symbol']:<10} {s['name'][:25]:<26} Rev: min {s['min_rev']:>5.1f}%, avg {s['avg_rev']:>5.1f}% | PAT: min {s['min_pat']:>5.1f}%, avg {s['avg_pat']:>5.1f}% | PE: {s['today_pe']:>6.1f} | Score: {s['master_score']}")
