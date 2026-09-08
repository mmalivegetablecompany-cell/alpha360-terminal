import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
if not m:
    print("Could not find rawData")
    sys.exit(1)

data = json.loads(m.group(1))
print(f"Total stocks loaded: {len(data)}")

q_lens = set(len(s.get('quarters_history', [])) for s in data)
print(f"Distinct lengths of quarters_history: {q_lens}")

for s in data[:5]:
    print(f"Symbol: {s.get('symbol')} , Name: {s.get('name')} , streak_rev: {s.get('streak_rev')} , streak_pat: {s.get('streak_pat')}")
    qh = s.get('quarters_history', [])
    for q in qh:
        print(f"   Q: {q.get('Quarter')}, Rev: {q.get('Revenue')}, PrevRev: {q.get('Prev_Yr_Revenue')}, YoY_Rev: {q.get('YoY_Rev')}%, PAT: {q.get('PAT')}, PrevPAT: {q.get('Prev_Yr_PAT')}, YoY_PAT: {q.get('YoY_PAT')}%")
