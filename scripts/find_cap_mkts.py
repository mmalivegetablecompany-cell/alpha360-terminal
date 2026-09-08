import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
data = json.loads(m.group(1))

print("Searching for financial / capital market related companies...")
for s in data:
    sec = s.get('sector', '')
    sub = s.get('sub_industry', '')
    sym = s.get('symbol', '')
    name = s.get('name', '')
    
    keywords = ['market', 'exchange', 'depository', 'broker', 'wealth', 'securities', 'amc', 'advisory', 'fintech', 'capital']
    combined_str = f"{sec} {sub} {sym} {name}".lower()
    
    if any(k in combined_str for k in ['exchange', 'depository', 'broker', 'wealth', 'capital market', 'securities', 'prudent', 'angel', 'motilal', 'cdsl', 'bse', 'mcx', 'iex']):
        qh = s.get('quarters_history', [])
        rev_yoys = [q['YoY_Rev'] for q in qh if q.get('YoY_Rev') is not None]
        pat_yoys = [q['YoY_PAT'] for q in qh if q.get('YoY_PAT') is not None]
        both_pos = sum(1 for q in qh if q.get('YoY_Rev') is not None and q.get('YoY_PAT') is not None and q['YoY_Rev'] > 0 and q['YoY_PAT'] > 0)
        
        print(f"Symbol: {sym:<12} Name: {name[:28]:<30} Sec: {sec[:20]:<22} 8Q Pos: {both_pos}/{len(rev_yoys)} PE: {s.get('today_pe')} PEG: {s.get('today_peg')} Score: {s.get('master_score')}")
