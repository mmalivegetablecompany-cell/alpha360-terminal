import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
data = json.loads(m.group(1))

for s in data:
    if s['symbol'] in ['ICICIBANK', 'FEDFINA', 'NYKAA', 'POLICYBZR', 'BSE', 'GENUSPOWER', 'MCX']:
        print(f"=== {s['symbol']} ({s['name']}) ===")
        for q in s.get('quarters_history', []):
            print(f"  {q['Quarter']}: Rev={q.get('Revenue')}, YoY_Rev={q.get('YoY_Rev')}, PAT={q.get('PAT')}, YoY_PAT={q.get('YoY_PAT')}")
