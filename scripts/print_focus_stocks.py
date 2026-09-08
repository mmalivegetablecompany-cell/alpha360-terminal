import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/consistent_8q_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# Let's inspect top picks across criteria:
# 1. Sky Gold (SKYGOLD)
# 2. Genus Power (GENUSPOWER)
# 3. BSE Ltd (BSE)
# 4. MCX (MCX)
# 5. PB Fintech (POLICYBZR)
# 6. Vintage Coffee (VINTAGE)
# 7. Solar Industries (SOLARINDS)
# 8. Affle (AFFLE)
# 9. Privi Speciality (PRIVISCL)
# 10. Sagility India (SAGILITY)
# 11. Netweb Tech (NETWEB)
# 12. Mahindra & Mahindra (M&M)
# 13. Premier Energies (PREMIERENE)
# 14. Coforge (COFORGE)
# 15. BLS International (BLS)
# 16. TD Power Systems (TDPOWERSYS)
# 17. S.J.S. Enterprises (SJS)

focus_symbols = [
    'GENUSPOWER', 'BSE', 'MCX', 'SKYGOLD', 'POLICYBZR', 'VINTAGE',
    'AFFLE', 'SOLARINDS', 'PRIVISCL', 'SAGILITY', 'NETWEB', 'M&M',
    'PREMIERENE', 'COFORGE', 'BLS', 'TDPOWERSYS', 'SJS', 'VIJAYA'
]

stock_map = {s['symbol']: s for s in stocks}

for sym in focus_symbols:
    if sym not in stock_map: continue
    s = stock_map[sym]
    print(f"\n=======================================================")
    print(f"{s['symbol']} - {s['name']} | Sector: {s['sector']} | Mcap: {s['mcap']} (₹{s['mcap_cr']:,.0f} Cr)")
    print(f"CMP: ₹{s['today_price']} | P/E: {s['today_pe']} | P/B: {s['today_pb']} | PEG: {s['today_peg']} | Score: {s['master_score']} | Tier: {s['tier']}")
    print(f"Consensus: {s['consensus']} | Buy Rating: {s['buy_rating']}")
    print(f"Summary: Rev Floor +{s['min_rev']}% (Avg +{s['avg_rev']}%) | PAT Floor +{s['min_pat']}% (Avg +{s['avg_pat']}%)")
    print("Quarterly YoY Progression:")
    q_str = " | ".join([f"{q['q'][:3]+q['q'][-2:]}: R+{q['rev_yoy']}%/P+{q['pat_yoy']}%" for q in s['q_details']])
    print(f"  {q_str}")
