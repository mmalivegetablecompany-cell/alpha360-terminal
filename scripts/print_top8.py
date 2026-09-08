import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/consistent_8q_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

stock_map = {s['symbol']: s for s in stocks}

for sym in ['GENUSPOWER', 'BSE', 'MCX', 'SKYGOLD', 'POLICYBZR', 'VINTAGE', 'GVT&D', 'NYKAA']:
    s = stock_map[sym]
    print(f"=== {s['symbol']} - {s['name']} ===")
    print(f"Mcap: {s['mcap']} (₹{s['mcap_cr']:,.0f} Cr) | CMP: ₹{s['today_price']} | P/E: {s['today_pe']} | PEG: {s['today_peg']} | Master Score: {s['master_score']}")
    print(f"Rev Floor: +{s['min_rev']}% (Avg +{s['avg_rev']}%) | PAT Floor: +{s['min_pat']}% (Avg +{s['avg_pat']}%)")
    for q in s['q_details']:
        print(f"  {q['q']}: Rev ₹{q['rev']}Cr (+{q['rev_yoy']}%) | PAT ₹{q['pat']}Cr (+{q['pat_yoy']}%)")
    print()
