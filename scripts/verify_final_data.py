import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/consistent_8q_stocks.json', 'r', encoding='utf-8') as f:
    stocks = {s['symbol']: s for s in json.load(f)}

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
all_data = {s['symbol']: s for s in json.loads(m.group(1))}

all_target_syms = [
    # List 1: GARP
    'GENUSPOWER', 'PREMIERENE', 'SKYGOLD', 'SJS', 'SAGILITY', 'M&M', 'DCBBANK', 'BLS', 'PRIVISCL', 'VINTAGE',
    # List 2: Predictability
    'AFFLE', 'PERSISTENT', 'PRIVISCL', 'KEI', 'NYKAA', 'M&M', 'POLICYBZR', 'IEX', 'AZAD', 'WABAG',
    # List 3: Capital Markets
    'MCX', 'BSE', 'POLICYBZR', 'PRUDENT', 'IEX', 'CRISIL', 'ANGELONE', 'CDSL', 'MOTILALOFS'
]

print(f"Verifying {len(set(all_target_syms))} unique stocks:")
for sym in set(all_target_syms):
    s = all_data.get(sym)
    if not s:
        print(f"Missing {sym}!")
        continue
    c = stocks.get(sym, {})
    pe = s.get('today_pe')
    peg = s.get('today_peg')
    cmp_p = s.get('today_price')
    mcap_cr = s.get('mcap_cr')
    score = s.get('master_score')
    funda = s.get('score')
    tier = s.get('tier')
    rev_f = c.get('min_rev', 'N/A')
    rev_a = c.get('avg_rev', 'N/A')
    pat_f = c.get('min_pat', 'N/A')
    pat_a = c.get('avg_pat', 'N/A')
    print(f"{sym:<11} CMP: ₹{cmp_p:<7} P/E: {pe:<5} PEG: {peg:<5} Score: {score:<4} Rev: [{rev_f}%, {rev_a}%] PAT: [{pat_f}%, {pat_a}%]")
