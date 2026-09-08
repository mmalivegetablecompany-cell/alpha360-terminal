import json
import re
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# Load the 54 consistent stocks
with open('scripts/consistent_8q_stocks.json', 'r', encoding='utf-8') as f:
    consistent_stocks = json.load(f)

# Also load rawData from HTML to check all 424 stocks for Capital Markets
with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(?:const|var|let)\s+rawData\s*=\s*(\[.*?\]);', html, re.DOTALL)
data = json.loads(m.group(1))

# ----------------------------------------------------
# 1. EXPAND & RANK LIST 1: GARP / Deep Value
# Criteria: Low PEG (< 1.2), Reasonable P/E (< 40 or high discount), High Score, 8/8 Positive Quarters
# ----------------------------------------------------
garp_candidates = []
for s in consistent_stocks:
    pe = s.get('today_pe') or 999
    peg = s.get('today_peg') or 999
    avg_pat = s.get('avg_pat') or 0
    avg_rev = s.get('avg_rev') or 0
    min_pat = s.get('min_pat') or 0
    score = s.get('master_score') or 0
    
    # GARP criteria: PEG <= 1.25 or (P/E <= 35 and avg_pat >= 20)
    if (0 < peg <= 1.25) or (pe <= 35 and avg_pat >= 20):
        # Composite GARP Score:
        # Lower PEG is better, lower PE is better, higher Master Score is better, higher growth is better
        # garp_rank_score = Master_Score / (PEG * sqrt(PE))
        garp_metric = round((score * 1.5) / (max(0.2, peg) * np.sqrt(max(5.0, pe))), 2)
        garp_candidates.append({
            **s,
            'garp_metric': garp_metric
        })

garp_candidates.sort(key=lambda x: x['garp_metric'], reverse=True)

print("=== LIST 1: TOP GARP / DEEP VALUE CANDIDATES ===")
for i, s in enumerate(garp_candidates[:12], 1):
    print(f"{i:<2} {s['symbol']:<11} {s['name'][:22]:<23} PE: {s['today_pe']:>5.1f} | PEG: {s['today_peg']:>4.2f} | RevAvg: +{s['avg_rev']:>5.1f}% | PATAvg: +{s['avg_pat']:>6.1f}% | Score: {s['master_score']:>4.1f} | Metric: {s['garp_metric']}")

# ----------------------------------------------------
# 2. EXPAND & RANK LIST 2: Predictability (Lowest Volatility, Steady Compounders)
# Criteria: 8/8 Positive Quarters, High growth floor, Low Coefficient of Variation (CV)
# ----------------------------------------------------
pred_candidates = []
for s in consistent_stocks:
    rev_yoys = [q['rev_yoy'] for q in s['q_details']]
    pat_yoys = [q['pat_yoy'] for q in s['q_details']]
    
    mean_r = np.mean(rev_yoys)
    std_r = np.std(rev_yoys)
    cv_r = std_r / mean_r if mean_r > 0 else 999
    
    mean_p = np.mean(pat_yoys)
    std_p = np.std(pat_yoys)
    cv_p = std_p / mean_p if mean_p > 0 else 999
    
    # Combined CV (lower is much more predictable)
    combined_cv = round(float(cv_r * 0.6 + cv_p * 0.4), 3)
    
    # Predictability Score: Higher floor + low CV + solid master score
    # Min Rev floor + Min PAT floor divided by combined_cv
    growth_floor_sum = s['min_rev'] + s['min_pat']
    pred_score = round(float((growth_floor_sum * 0.5 + s['master_score'] * 0.5) / (1.0 + combined_cv)), 2)
    
    pred_candidates.append({
        **s,
        'cv_rev': round(float(cv_r), 2),
        'cv_pat': round(float(cv_p), 2),
        'combined_cv': combined_cv,
        'pred_score': pred_score
    })

# Sort by lowest combined_cv (pure predictability) and high floor
pred_candidates.sort(key=lambda x: (x['combined_cv'], -x['min_rev']))

print("\n=== LIST 2: HIGHEST PREDICTABILITY (LOWEST VOLATILITY / STEADY COMPOUNDERS) ===")
for i, s in enumerate(pred_candidates[:12], 1):
    print(f"{i:<2} {s['symbol']:<11} {s['name'][:22]:<23} Rev Range: {s['min_rev']:>4.1f}%-{s['max_rev']:>5.1f}% | PAT Range: {s['min_pat']:>4.1f}%-{s['max_pat']:>5.1f}% | CV(R): {s['cv_rev']:>4.2f} | CV(P): {s['cv_pat']:>4.2f} | Combined CV: {s['combined_cv']}")

# ----------------------------------------------------
# 3. EXPAND & RANK LIST 3: Capital Markets & Financial Intermediaries Operating Leverage Giants
# Check all stocks in rawData in Capital Markets, Exchanges, Brokers, Depositories, Wealth, Financials
# ----------------------------------------------------
print("\n=== LIST 3: CAPITAL MARKETS & FINANCIAL INTERMEDIARIES CANDIDATES IN 424 WATCHLIST ===")
cap_mkts_candidates = []
for s in data:
    sec = s.get('sector', '')
    sub = s.get('sub_industry', '')
    name = s.get('name', '')
    sym = s.get('symbol', '')
    
    # Keywords for capital markets
    is_cap_mkt = False
    if 'capital market' in sec.lower() or 'exchange' in sec.lower() or 'exchange' in name.lower() or 'invest' in sub.lower() or 'wealth' in sub.lower() or 'brok' in sub.lower() or 'depository' in sub.lower():
        is_cap_mkt = True
    elif sym in ['BSE', 'MCX', 'IEX', 'CDSL', 'CAMS', 'KFINTECH', 'PRUDENT', 'ANGELONE', 'MOTILALOFS', 'ANANDRATHI', 'NUVAMA', 'UTIAMC', 'HDFCAMC']:
        is_cap_mkt = True
        
    if is_cap_mkt:
        qh = s.get('quarters_history', [])
        rev_yoys = [q['YoY_Rev'] for q in qh if q.get('YoY_Rev') is not None]
        pat_yoys = [q['YoY_PAT'] for q in qh if q.get('YoY_PAT') is not None]
        
        pos_rev = sum(1 for y in rev_yoys if y > 0)
        pos_pat = sum(1 for y in pat_yoys if y > 0)
        both_pos = 0
        for q in qh:
            if q.get('YoY_Rev') is not None and q.get('YoY_PAT') is not None:
                if q['YoY_Rev'] > 0 and q['YoY_PAT'] > 0:
                    both_pos += 1
                    
        cap_mkts_candidates.append({
            'symbol': sym,
            'name': name,
            'sector': sec,
            'sub_industry': sub,
            'mcap_cr': s.get('mcap_cr', 0),
            'mcap': s.get('mcap', ''),
            'today_price': s.get('today_price', 0),
            'today_pe': s.get('today_pe', 0),
            'today_peg': s.get('today_peg', 0),
            'master_score': s.get('master_score', 0),
            'tier': s.get('tier', ''),
            'both_pos': both_pos,
            'total_q': len(rev_yoys),
            'avg_rev': round(float(np.mean(rev_yoys)), 1) if rev_yoys else 0,
            'min_rev': round(float(np.min(rev_yoys)), 1) if rev_yoys else 0,
            'avg_pat': round(float(np.mean(pat_yoys)), 1) if pat_yoys else 0,
            'min_pat': round(float(np.min(pat_yoys)), 1) if pat_yoys else 0,
        })

print(f"Total Capital Markets / Intermediaries found: {len(cap_mkts_candidates)}")
cap_mkts_candidates.sort(key=lambda x: (x['both_pos'], x['master_score']), reverse=True)
for i, s in enumerate(cap_mkts_candidates, 1):
    print(f"{i:<2} {s['symbol']:<11} {s['name'][:24]:<25} 8Q Pos: {s['both_pos']}/{s['total_q']} | PE: {s['today_pe']:>5.1f} | PEG: {s['today_peg']:>4.2f} | RevAvg: +{s['avg_rev']:>5.1f}% | PATAvg: +{s['avg_pat']:>6.1f}% | Score: {s['master_score']:>4.1f}")
