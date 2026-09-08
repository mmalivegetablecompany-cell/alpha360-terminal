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

analyzed = []

for s in data:
    qh = s.get('quarters_history', [])
    rev_yoys = [q['YoY_Rev'] for q in qh if q.get('YoY_Rev') is not None]
    pat_yoys = [q['YoY_PAT'] for q in qh if q.get('YoY_PAT') is not None]
    
    total_q = len(qh)
    valid_rev_q = len(rev_yoys)
    valid_pat_q = len(pat_yoys)
    
    pos_rev = sum(1 for y in rev_yoys if y > 0)
    pos_pat = sum(1 for y in pat_yoys if y > 0)
    
    both_pos = 0
    for q in qh:
        if q.get('YoY_Rev') is not None and q.get('YoY_PAT') is not None:
            if q['YoY_Rev'] > 0 and q['YoY_PAT'] > 0:
                both_pos += 1
                
    # Revenue metrics
    avg_rev = float(np.mean(rev_yoys)) if rev_yoys else 0.0
    med_rev = float(np.median(rev_yoys)) if rev_yoys else 0.0
    min_rev = float(np.min(rev_yoys)) if rev_yoys else 0.0
    max_rev = float(np.max(rev_yoys)) if rev_yoys else 0.0
    std_rev = float(np.std(rev_yoys)) if len(rev_yoys) > 1 else 0.0
    
    # PAT metrics
    avg_pat = float(np.mean(pat_yoys)) if pat_yoys else 0.0
    med_pat = float(np.median(pat_yoys)) if pat_yoys else 0.0
    min_pat = float(np.min(pat_yoys)) if pat_yoys else 0.0
    max_pat = float(np.max(pat_yoys)) if pat_yoys else 0.0
    std_pat = float(np.std(pat_yoys)) if len(pat_yoys) > 1 else 0.0

    # Consistency Score Calculation:
    # 1. Base points for 8/8 positive quarters:
    # If 8/8 both positive: 40 pts
    # If 7/8: 30 pts, etc.
    pct_both_pos = (both_pos / max(valid_rev_q, 1)) * 40.0
    
    # 2. Minimum growth floor bonus (how high is the lowest quarter?):
    # If lowest rev > 15%, max 15 pts; if > 10%, 10 pts; if > 5%, 5 pts
    floor_rev_pts = 0
    if min_rev >= 20: floor_rev_pts = 15
    elif min_rev >= 15: floor_rev_pts = 12
    elif min_rev >= 10: floor_rev_pts = 8
    elif min_rev >= 5: floor_rev_pts = 4
    elif min_rev > 0: floor_rev_pts = 2
    
    floor_pat_pts = 0
    if min_pat >= 20: floor_pat_pts = 15
    elif min_pat >= 15: floor_pat_pts = 12
    elif min_pat >= 10: floor_pat_pts = 8
    elif min_pat >= 5: floor_pat_pts = 4
    elif min_pat > 0: floor_pat_pts = 2

    # 3. Average growth rate points (up to 20 pts):
    growth_pts = 0
    if avg_rev >= 25 and avg_pat >= 25: growth_pts = 20
    elif avg_rev >= 20 and avg_pat >= 20: growth_pts = 16
    elif avg_rev >= 15 and avg_pat >= 15: growth_pts = 12
    elif avg_rev >= 10 and avg_pat >= 10: growth_pts = 8
    else: growth_pts = 4

    # 4. Volatility penalty (low std relative to mean):
    # Coeff of variation
    cv_rev = (std_rev / avg_rev) if avg_rev > 0 else 2.0
    cv_pat = (std_pat / avg_pat) if avg_pat > 0 else 2.0
    stability_pts = max(0, 10 - min(10, (cv_rev + cv_pat) * 2))

    consistency_score = round(pct_both_pos + floor_rev_pts + floor_pat_pts + growth_pts + stability_pts, 1)

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
        'valid_rev_q': valid_rev_q,
        'valid_pat_q': valid_pat_q,
        'pos_rev': pos_rev,
        'pos_pat': pos_pat,
        'both_pos': both_pos,
        'avg_rev': round(avg_rev, 1),
        'min_rev': round(min_rev, 1),
        'max_rev': round(max_rev, 1),
        'avg_pat': round(avg_pat, 1),
        'min_pat': round(min_pat, 1),
        'max_pat': round(max_pat, 1),
        'std_rev': round(std_rev, 1),
        'std_pat': round(std_pat, 1),
        'consistency_score': consistency_score,
        'quarters_history': qh
    })

# Sort by consistency_score descending, then master_score descending
analyzed.sort(key=lambda x: (x['both_pos'], x['consistency_score'], x['master_score']), reverse=True)

print("Top 30 Most Consistent Growth Stocks (8 Quarters YoY):")
print("-" * 120)
print(f"{'Rank':<4} {'Symbol':<10} {'Company Name':<28} {'Sector':<22} {'BothPos':<8} {'MinRev%':<8} {'AvgRev%':<8} {'MinPAT%':<8} {'AvgPAT%':<8} {'PE':<6} {'Score':<6}")
print("-" * 120)

for idx, st in enumerate(analyzed[:35], 1):
    print(f"{idx:<4} {st['symbol']:<10} {st['name'][:27]:<28} {st['sector'][:21]:<22} {st['both_pos']}/8     {st['min_rev']:<8} {st['avg_rev']:<8} {st['min_pat']:<8} {st['avg_pat']:<8} {st['today_pe']:<6} {st['master_score']:<6}")
