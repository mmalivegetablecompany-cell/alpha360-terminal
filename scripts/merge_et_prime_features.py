import json, sys

sys.stdout.reconfigure(encoding="utf-8")

with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

with open("scratch/et_all_raw_data.json", "r", encoding="utf-8") as f:
    et_data = json.load(f)

with open("scratch/et_resolved_ids.json", "r", encoding="utf-8") as f:
    resolved = json.load(f)

resolved["PGINVIT"] = {"company_id": 2009359, "seo_name": "powergrid-infrastructure-investment-trust", "tag_name": "PowerGrid Infrastructure Investment Trust"}
resolved["TATAMOTORS"] = {"company_id": 12934, "seo_name": "tata-motors-ltd", "tag_name": "Tata Motors Ltd."}
resolved["KPENERGY"] = {"company_id": 63836, "seo_name": "k-p-energy-ltd", "tag_name": "K P Energy Ltd."}

def parse_int_score(val):
    if val is None or val == "" or val == "NR":
        return None
    try:
        return int(val)
    except:
        return None

def compute_forecast_score(upside_pct, bull_pct, num_analysts, downside_low_pct, high_upside_pct):
    pts = 0.0
    # Upside component (40 pts)
    if upside_pct is not None:
        if upside_pct >= 30: pts += 40.0
        elif upside_pct >= 20: pts += 32.0 + (upside_pct - 20) * 0.8
        elif upside_pct >= 10: pts += 22.0 + (upside_pct - 10) * 1.0
        elif upside_pct >= 0: pts += 12.0 + upside_pct * 1.0
        else: pts += max(2.0, 12.0 + upside_pct * 0.5)
    else:
        pts += 15.0

    # Bullish ratio (35 pts)
    if bull_pct is not None:
        if bull_pct >= 85: pts += 35.0
        elif bull_pct >= 70: pts += 28.0 + (bull_pct - 70) * (7.0 / 15.0)
        elif bull_pct >= 50: pts += 18.0 + (bull_pct - 50) * (10.0 / 20.0)
        else: pts += max(5.0, bull_pct * 0.36)
    else:
        pts += 15.0

    # Coverage breadth (15 pts)
    if num_analysts:
        if num_analysts >= 20: pts += 15.0
        elif num_analysts >= 12: pts += 12.5
        elif num_analysts >= 6: pts += 10.0
        elif num_analysts >= 2: pts += 8.0
        else: pts += 6.0
    else:
        pts += 5.0

    # Asymmetric spread (10 pts)
    if downside_low_pct is not None and downside_low_pct > -10: pts += 10.0
    elif high_upside_pct is not None and downside_low_pct is not None and abs(downside_low_pct) > 0:
        ratio = high_upside_pct / (abs(downside_low_pct) + 1e-5)
        if ratio >= 2.0: pts += 8.5
        else: pts += 6.0
    else:
        pts += 6.0

    return round(max(10.0, min(98.0, pts)), 1)

scores_found = 0
recos_found = 0

for s in stocks:
    sym = s["symbol"]
    cmp_price = s.get("today_price") or s.get("live_movement", {}).get("curr_price") or 1.0
    raw = et_data.get(sym)
    res_info = resolved.get(sym, {})

    if raw:
        sr = raw.get("refinitiveMetaByCompanyId") or {}
        pt = raw.get("priceTarget") or {}
        recos = raw.get("recommendations") or []
        tvc = raw.get("targetVsCurrent")

        stock_score = parse_int_score(sr.get("avgScore"))
        outlook = sr.get("avgScoreOutlook")
        earn_score = parse_int_score(sr.get("analystScore"))
        fund_score = parse_int_score(sr.get("fundScore"))
        rv_score = parse_int_score(sr.get("rvScore"))
        risk_score = parse_int_score(sr.get("riskScore"))
        pm_score = parse_int_score(sr.get("techScore"))
        pdf_link = sr.get("pdfLink", "")

        if stock_score is not None:
            scores_found += 1

        s["et_prime"] = {
            "company_id": res_info.get("company_id") or raw.get("companyId"),
            "seo_name": res_info.get("seo_name") or sr.get("seoname"),
            "stock_score": stock_score,
            "score_outlook": outlook or "NEUTRAL",
            "earnings_score": earn_score,
            "fundamental_score": fund_score,
            "rv_score": rv_score,
            "risk_score": risk_score,
            "momentum_score": pm_score,
            "pdf_link": pdf_link
        }

        mean_target = pt.get("Mean")
        median_target = pt.get("Median")
        high_target = pt.get("High")
        low_target = pt.get("Low")
        num_estimates = pt.get("NumberOfEstimates")

        latest_reco = recos[0] if recos else {}
        mean_reco_text = latest_reco.get("MeanText")
        reco_count = latest_reco.get("NumberOfRecommendations")
        num_analysts = reco_count or num_estimates

        stats_list = latest_reco.get("Statistics", {}).get("Statistic", [])
        stat_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for st in stats_list:
            r_type = st.get("Recommendation")
            if r_type in stat_counts:
                stat_counts[r_type] = st.get("NumberOfAnalysts", 0)

        strong_buy_cnt = stat_counts[1]
        buy_cnt = stat_counts[2]
        hold_cnt = stat_counts[3]
        sell_cnt = stat_counts[4]
        strong_sell_cnt = stat_counts[5]
        total_recos = strong_buy_cnt + buy_cnt + hold_cnt + sell_cnt + strong_sell_cnt

        upside_pct = None
        if tvc is not None:
            try: upside_pct = round(float(tvc), 1)
            except: pass
        if upside_pct is None and mean_target and cmp_price:
            upside_pct = round(((float(mean_target) - cmp_price) / cmp_price) * 100, 1)

        high_upside_pct = round(((float(high_target) - cmp_price) / cmp_price) * 100, 1) if high_target and cmp_price else (upside_pct or 0.0)
        downside_low_pct = round(((float(low_target) - cmp_price) / cmp_price) * 100, 1) if low_target and cmp_price else (0.0)

        bull_cnt = strong_buy_cnt + buy_cnt
        bull_pct = round((bull_cnt / total_recos * 100), 1) if total_recos > 0 else (75.0 if mean_reco_text in ["STRONG BUY", "BUY"] else 40.0)

        if mean_target is not None or mean_reco_text is not None:
            recos_found += 1
            consensus_display = mean_reco_text.title() if mean_reco_text else "Buy"
            fc_score = compute_forecast_score(upside_pct, bull_pct, num_analysts, downside_low_pct, high_upside_pct)

            s["forecast"] = {
                "source": "ET Markets (Economic Times)",
                "mean_target": round(float(mean_target), 2) if mean_target else None,
                "median_target": round(float(median_target), 2) if median_target else None,
                "high_target": round(float(high_target), 2) if high_target else None,
                "low_target": round(float(low_target), 2) if low_target else None,
                "upside_mean_pct": upside_pct,
                "upside_high_pct": high_upside_pct,
                "downside_low_pct": downside_low_pct,
                "num_analysts": num_analysts or total_recos,
                "consensus_rating": consensus_display,
                "breakdown": {
                    "strong_buy": strong_buy_cnt,
                    "buy": buy_cnt,
                    "hold": hold_cnt,
                    "sell": sell_cnt,
                    "strong_sell": strong_sell_cnt,
                    "outperform": 0,
                    "underperform": 0,
                    "buy_pct": bull_pct,
                    "outperform_pct": 0.0,
                    "hold_pct": round((hold_cnt / max(1, total_recos)) * 100, 1),
                    "underperform_pct": 0.0,
                    "sell_pct": round(((sell_cnt + strong_sell_cnt) / max(1, total_recos)) * 100, 1)
                },
                "forecast_score": fc_score,
                "analyst_reports": s.get("forecast", {}).get("analyst_reports", [])
            }
            s["forecast_score"] = fc_score
            s["consensus"] = f"{consensus_display} (ET Consensus: {upside_pct:+0.1f}% Upside)" if upside_pct is not None else f"{consensus_display} (ET Consensus)"
        else:
            # No active analyst forecast in ET Markets
            fc_score = round(max(30.0, min(85.0, (stock_score or 5) * 8.5)), 1)
            s["forecast_score"] = fc_score
            s["forecast"] = {
                "source": "No Active ET Consensus",
                "mean_target": None,
                "median_target": None,
                "high_target": None,
                "low_target": None,
                "upside_mean_pct": None,
                "upside_high_pct": None,
                "downside_low_pct": None,
                "num_analysts": 0,
                "consensus_rating": "NR (No Coverage)",
                "breakdown": {
                    "strong_buy": 0, "buy": 0, "hold": 0, "sell": 0, "strong_sell": 0,
                    "outperform": 0, "underperform": 0,
                    "buy_pct": 0.0, "outperform_pct": 0.0, "hold_pct": 0.0, "underperform_pct": 0.0, "sell_pct": 0.0
                },
                "forecast_score": fc_score,
                "analyst_reports": []
            }
            s["consensus"] = f"Stock Score {stock_score}/10 ({outlook or 'NR'})" if stock_score else "NR (No Coverage)"
    else:
        # Fallback for unlisted EMVEE
        s["et_prime"] = {
            "company_id": None,
            "seo_name": None,
            "stock_score": None,
            "score_outlook": "NR",
            "earnings_score": None,
            "fundamental_score": None,
            "rv_score": None,
            "risk_score": None,
            "momentum_score": None,
            "pdf_link": ""
        }
        s["forecast"] = {
            "source": "Pre-IPO / Unlisted",
            "mean_target": None, "median_target": None, "high_target": None, "low_target": None,
            "upside_mean_pct": None, "upside_high_pct": None, "downside_low_pct": None,
            "num_analysts": 0, "consensus_rating": "NR",
            "breakdown": {"strong_buy": 0, "buy": 0, "hold": 0, "sell": 0, "strong_sell": 0, "outperform": 0, "underperform": 0, "buy_pct": 0, "outperform_pct": 0, "hold_pct": 0, "underperform_pct": 0, "sell_pct": 0},
            "forecast_score": 50.0,
            "analyst_reports": []
        }
        s["forecast_score"] = 50.0

    # Recalculate Master Quad Score
    f_score = float(s.get("score") or 50.0)
    t_score = float(s.get("tech_score") or 50.0)
    m_score = float(s.get("mood_score") or 50.0)
    fc_score = float(s.get("forecast_score") or 50.0)

    quad_score = round(0.30 * f_score + 0.30 * t_score + 0.20 * m_score + 0.20 * fc_score, 1)
    s["master_score"] = quad_score

    # Confluence category
    if quad_score >= 88.0:
        s["master_category"] = "🌟 Quad-Factor Alpha Leader (Score ≥ 88)"
    elif quad_score >= 80.0:
        s["master_category"] = "💎 High-Conviction Compounder (Score 80–87.9)"
    elif s.get("forecast", {}).get("upside_mean_pct") is not None and s.get("forecast", {}).get("upside_mean_pct") >= 20.0:
        s["master_category"] = "🚀 High Forecast Upside Growth"
    elif f_score >= 70.0 and s.get("technicals", {}).get("rsi", 50) < 45:
        s["master_category"] = "🎯 High-Growth Dip Buy at Support"
    elif quad_score >= 55.0:
        s["master_category"] = "⚖️ Resilient Watchlist Compounder"
    else:
        s["master_category"] = "⚠️ Neutral / Headwinds Lagging"

# Sort by master_score and re-rank
stocks.sort(key=lambda x: x.get("master_score", 0), reverse=True)
for r, s in enumerate(stocks, 1):
    s["master_rank"] = r

with open("scripts/combined_master_stocks.json", "w", encoding="utf-8") as f:
    json.dump(stocks, f, indent=2, ensure_ascii=False)

print(f"Merge and synthesis complete!")
print(f"Total stocks: {len(stocks)}")
print(f"Stocks with ET Prime Stock Score: {scores_found}")
print(f"Stocks with ET Analyst Recos & Targets: {recos_found}")
print(f"Top 5 Ranked stocks:")
for s in stocks[:5]:
    ep = s.get("et_prime", {})
    fc = s.get("forecast", {})
    print(f"  #{s['master_rank']} {s['symbol']:<12} | Master: {s['master_score']} | ET Score: {ep.get('stock_score')}/10 | Upside: {fc.get('upside_mean_pct')}% | Target: ₹{fc.get('mean_target')} | Reco: {fc.get('consensus_rating')} ({fc.get('num_analysts')} ans)")
