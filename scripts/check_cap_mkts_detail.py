import json
import re
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
data = json.loads(m.group(1))

syms = ['MCX', 'BSE', 'POLICYBZR', 'PRUDENT', 'IEX', 'NSDL', 'ANGELONE', 'CDSL', 'CRISIL', 'ICRA', 'MOTILALOFS', 'MUTHOOTFIN']
for s in data:
    if s['symbol'] in syms:
        qh = s.get('quarters_history', [])
        rev_yoys = [q['YoY_Rev'] for q in qh if q.get('YoY_Rev') is not None]
        pat_yoys = [q['YoY_PAT'] for q in qh if q.get('YoY_PAT') is not None]
        both_pos = sum(1 for q in qh if q.get('YoY_Rev') is not None and q.get('YoY_PAT') is not None and q['YoY_Rev'] > 0 and q['YoY_PAT'] > 0)
        avg_r = round(float(np.mean(rev_yoys)), 1) if rev_yoys else 0
        min_r = round(float(np.min(rev_yoys)), 1) if rev_yoys else 0
        avg_p = round(float(np.mean(pat_yoys)), 1) if pat_yoys else 0
        min_p = round(float(np.min(pat_yoys)), 1) if pat_yoys else 0
        print(f"Symbol: {s['symbol']:<11} Name: {s['name'][:24]:<25} 8Q Pos: {both_pos}/{len(rev_yoys)} | P/E: {s.get('today_pe'):>5.1f} | PEG: {s.get('today_peg')} | Score: {s.get('master_score')} | Rev: min {min_r}% avg {avg_r}% | PAT: min {min_p}% avg {avg_p}%")
