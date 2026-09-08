import json
import re
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
data = json.loads(m.group(1))

analyzed = []

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
                
    if is_synth or len(rev_yoys) != 8 or both_pos != 8:
        continue
        
    analyzed.append({
        'symbol': s.get('symbol'),
        'name': s.get('name'),
        'sector': s.get('sector'),
        'mcap': s.get('mcap'),
        'mcap_cr': s.get('mcap_cr', 0),
        'master_score': s.get('master_score', 0),
        'funda_score': s.get('score', 0),
        'tech_score': s.get('tech_score', 0),
        'et_score': s.get('et_score_100', 0),
        'today_price': s.get('today_price', 0),
        'today_pe': s.get('today_pe', 0),
        'today_pb': s.get('today_pb', 0),
        'today_peg': s.get('today_peg', 0),
        'consensus': s.get('consensus', ''),
        'tier': s.get('tier', ''),
        'buy_rating': s.get('buy_rating', ''),
        'forecast_upside': s.get('forecast', {}).get('upside_mean_pct', 0),
        'avg_rev': round(float(np.mean(rev_yoys)), 2),
        'min_rev': round(float(np.min(rev_yoys)), 2),
        'max_rev': round(float(np.max(rev_yoys)), 2),
        'avg_pat': round(float(np.mean(pat_yoys)), 2),
        'min_pat': round(float(np.min(pat_yoys)), 2),
        'max_pat': round(float(np.max(pat_yoys)), 2),
        'qh': qh
    })

print(f"Total 8/8 Real Stocks: {len(analyzed)}")

# Output details for each stock
output = []
for s in analyzed:
    quarters_detail = []
    for q in s['qh']:
        quarters_detail.append({
            'q': q['Quarter'],
            'rev_yoy': q['YoY_Rev'],
            'pat_yoy': q['YoY_PAT'],
            'rev': q['Revenue'],
            'pat': q['PAT']
        })
    s['q_details'] = quarters_detail
    del s['qh']
    output.append(s)

with open('scripts/consistent_8q_stocks.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print("Saved to scripts/consistent_8q_stocks.json")
