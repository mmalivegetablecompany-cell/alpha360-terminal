import numpy as np

def build_quarters_history(raw_sales, raw_pat, raw_opm, raw_eps, ann_dates, hist_prices):
    """
    raw_sales, raw_pat, raw_opm, raw_eps: lists of 12 numbers:
    Indices 0..3: Sep 2023, Dec 2023, Mar 2024, Jun 2024 (prior year)
    Indices 4..11: Sep 2024, Dec 2024, Mar 2025, Jun 2025, Sep 2025, Dec 2025, Mar 2026, Jun 2026 (the 8 target quarters)
    """
    quarters_labels = [
        ("Sep 2024", "Sep 2023", 4, 0),
        ("Dec 2024", "Dec 2023", 5, 1),
        ("Mar 2025", "Mar 2024", 6, 2),
        ("Jun 2025", "Jun 2024", 7, 3),
        ("Sep 2025", "Sep 2024", 8, 4),
        ("Dec 2025", "Dec 2024", 9, 5),
        ("Mar 2026", "Mar 2025", 10, 6),
        ("Jun 2026", "Jun 2025", 11, 7)
    ]
    
    quarters_history = []
    
    for i, (q_name, prev_q_name, cur_idx, prev_idx) in enumerate(quarters_labels):
        rev = float(raw_sales[cur_idx])
        prev_rev = float(raw_sales[prev_idx])
        yoy_rev = round(((rev - prev_rev) / abs(prev_rev)) * 100, 2) if prev_rev != 0 else 0.0
        
        pat = float(raw_pat[cur_idx])
        prev_pat = float(raw_pat[prev_idx])
        yoy_pat = round(((pat - prev_pat) / abs(prev_pat)) * 100, 2) if prev_pat != 0 else 0.0
        
        opm = float(raw_opm[cur_idx])
        op = round(rev * (opm / 100.0), 1)
        eps = float(raw_eps[cur_idx])
        
        # 4Q TTM EPS
        ttm_eps = round(sum([float(raw_eps[cur_idx - k]) for k in range(4)]), 2)
        
        ann_date = ann_dates[i]
        eff_price = float(hist_prices[i])
        
        pe = round(eff_price / ttm_eps, 2) if ttm_eps > 0 else None
        
        # QoQ calculations (relative to previous quarter in target sequence)
        if i == 0:
            qoq_rev = None
            qoq_pat = None
            qoq_price = None
            qoq_div = None
        else:
            prior_rev = float(raw_sales[cur_idx - 1])
            prior_pat = float(raw_pat[cur_idx - 1])
            prior_price = float(hist_prices[i - 1])
            
            qoq_rev = round(((rev - prior_rev) / abs(prior_rev)) * 100, 2) if prior_rev != 0 else 0.0
            qoq_pat = round(((pat - prior_pat) / abs(prior_pat)) * 100, 2) if prior_pat != 0 else 0.0
            qoq_price = round(((eff_price - prior_price) / prior_price) * 100, 2) if prior_price != 0 else 0.0
            qoq_div = round(qoq_pat - qoq_price, 2)
        
        q_obj = {
            "Quarter": q_name,
            "Prev_Yr_Quarter": prev_q_name,
            "Revenue": rev,
            "Prev_Yr_Revenue": prev_rev,
            "YoY_Rev": yoy_rev,
            "PAT": pat,
            "Prev_Yr_PAT": prev_pat,
            "YoY_PAT": yoy_pat,
            "OP": op,
            "OPM": opm,
            "EPS": eps,
            "TTM_EPS": ttm_eps,
            "Effective_Price": eff_price,
            "Prev_Yr_Price": None,
            "YoY_Price": None,
            "YoY_Div": None,
            "PE": pe,
            "Ann_Date": ann_date,
            "QoQ_Rev": qoq_rev,
            "QoQ_PAT": qoq_pat,
            "QoQ_Price": qoq_price,
            "QoQ_Div": qoq_div
        }
        quarters_history.append(q_obj)
        
    return quarters_history

def compute_fundamental_metrics(quarters_history, today_price):
    q_latest = quarters_history[-1]
    today_ttm_eps = q_latest["TTM_EPS"]
    today_pe = round(today_price / today_ttm_eps, 2) if today_ttm_eps > 0 else 0.0
    
    pe_list = [q["PE"] for q in quarters_history if q["PE"] is not None and q["PE"] > 0]
    if pe_list:
        pe_8q_med = round(float(np.median(pe_list)), 2)
        pe_8q_avg = round(float(np.mean(pe_list)), 2)
        pe_8q_min = round(float(np.min(pe_list)), 2)
        pe_8q_max = round(float(np.max(pe_list)), 2)
    else:
        pe_8q_med = today_pe
        pe_8q_avg = today_pe
        pe_8q_min = today_pe
        pe_8q_max = today_pe
        
    val_discount_pct = round(((pe_8q_med - today_pe) / pe_8q_med) * 100, 1) if pe_8q_med > 0 else 0.0
    
    # Streaks (from latest quarter backward)
    streak_rev = 0
    for q in reversed(quarters_history):
        if q["QoQ_Rev"] is not None and q["QoQ_Rev"] > 0:
            streak_rev += 1
        elif q["QoQ_Rev"] is not None:
            break
            
    streak_pat = 0
    for q in reversed(quarters_history):
        if q["QoQ_PAT"] is not None and q["QoQ_PAT"] > 0:
            streak_pat += 1
        elif q["QoQ_PAT"] is not None:
            break
            
    # Buy rating
    if val_discount_pct >= 20.0:
        buy_rating = "🌟 Deep Value / Strong Buy"
    elif val_discount_pct >= 5.0:
        buy_rating = "✅ Accumulate (Discount to Median)"
    elif val_discount_pct >= -10.0:
        buy_rating = "⚖️ Fair Value"
    else:
        buy_rating = "⚠️ Overextended (Hold/Trim)"
        
    # Fundamental Score
    pts = 50.0
    pts += min(9.0, streak_rev * 3.0)
    pts += min(9.0, streak_pat * 3.0)
    
    yp = q_latest["YoY_PAT"] or 0.0
    if yp > 100: pts += 16
    elif yp >= 50: pts += 12
    elif yp >= 25: pts += 8
    elif yp >= 10: pts += 4
    elif yp < -20: pts -= 14
    elif yp < 0: pts -= 7
    
    yr = q_latest["YoY_Rev"] or 0.0
    if yr > 50: pts += 10
    elif yr >= 25: pts += 7
    elif yr >= 10: pts += 4
    elif yr < 0: pts -= 6
    
    if val_discount_pct > 20: pts += 8
    elif val_discount_pct > 5: pts += 4
    elif val_discount_pct < -25: pts -= 8
    
    div = q_latest["QoQ_Div"] or 0.0
    if div > 30: pts += 6
    
    score = round(max(5.0, min(98.0, pts)), 1)
    
    # Tier
    if score >= 88.0 and val_discount_pct >= 10.0:
        tier = "Tier 1: Prime Alpha (High Growth & Undervalued)"
    elif score >= 80.0:
        tier = "Tier 2: Strong Momentum Compounder"
    elif score >= 65.0:
        tier = "Tier 3: Steady Watchlist Performer"
    elif score >= 50.0:
        tier = "Tier 4: Neutral / Cyclical"
    else:
        tier = "Tier 5: Avoid / Growth Deceleration"
        
    return {
        "today_ttm_eps": today_ttm_eps,
        "today_pe": today_pe,
        "pe_8q_med": pe_8q_med,
        "pe_8q_avg": pe_8q_avg,
        "pe_8q_min": pe_8q_min,
        "pe_8q_max": pe_8q_max,
        "val_discount_pct": val_discount_pct,
        "streak_rev": streak_rev,
        "streak_pat": streak_pat,
        "latest_quarter": q_latest["Quarter"],
        "latest_rev": q_latest["Revenue"],
        "latest_pat": q_latest["PAT"],
        "latest_opm": q_latest["OPM"],
        "latest_qoq_rev": q_latest["QoQ_Rev"],
        "latest_qoq_pat": q_latest["QoQ_PAT"],
        "latest_qoq_price": q_latest["QoQ_Price"],
        "latest_yoy_rev": q_latest["YoY_Rev"],
        "latest_yoy_pat": q_latest["YoY_PAT"],
        "latest_yoy_price": None,
        "qoq_divergence": q_latest["QoQ_Div"],
        "yoy_divergence": None,
        "latest_pe": q_latest["PE"],
        "buy_rating": buy_rating,
        "score": score,
        "tier": tier
    }
