import json, urllib.request, urllib.parse, time, concurrent.futures, os, sys

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def resolve_et_id(s):
    sym = s["symbol"].replace(".NS", "").replace(".BO", "").strip()
    name = s["name"].strip()
    
    # Manual overrides
    overrides = {
        "PGINVIT": (2009359, "powergrid-infrastructure-investment-trust", "PowerGrid Infrastructure Investment Trust"),
        "TATAMOTORS": (12934, "tata-motors-ltd", "Tata Motors Ltd."),
        "KPENERGY": (63836, "k-p-energy-ltd", "K P Energy Ltd."),
        "EMVEE": (None, None, "Emvee Photovoltaic Power")
    }
    if sym in overrides:
        return sym, overrides[sym][0], overrides[sym][1], overrides[sym][2]
        
    # Search by ticker
    url = f"https://etsearch.indiatimes.com/etspeeds/etsearchMdata.ep?matchCompanyName=true&realstate=true&pp=new&dvr=new&idr=new&trust=true&mcx=false&mf=false&nps=false&detail=false&forex=false&index=false&mecklai=false&etf=false&nonList=false&pagesize=10&outputtype=json&ticker={urllib.parse.quote(sym)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req, timeout=6).read().decode("utf-8")
        data = json.loads(res)
        for item in data:
            if item.get("entityType") == "company" and (item.get("symbol") == sym or item.get("scripCode2") == sym or item.get("scripCode") == sym):
                return sym, item.get("tagId"), item.get("tagSeoName"), item.get("tagName")
        for item in data:
            if item.get("entityType") == "company":
                return sym, item.get("tagId"), item.get("tagSeoName"), item.get("tagName")
    except Exception:
        pass

    # Search by clean name
    clean_name = name.replace(" Limited", "").replace(" Ltd.", "").replace(" Ltd", "").replace(" (India)", "").replace(" India", "")
    url = f"https://etsearch.indiatimes.com/etspeeds/etsearchMdata.ep?matchCompanyName=true&realstate=true&pp=new&dvr=new&idr=new&trust=true&mcx=false&mf=false&nps=false&detail=false&forex=false&index=false&mecklai=false&etf=false&nonList=false&pagesize=10&outputtype=json&ticker={urllib.parse.quote(clean_name)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req, timeout=6).read().decode("utf-8")
        data = json.loads(res)
        for item in data:
            if item.get("entityType") == "company":
                return sym, item.get("tagId"), item.get("tagSeoName"), item.get("tagName")
    except Exception:
        pass

    return sym, None, None, None

def fetch_et_stock_data(company_id):
    if not company_id:
        return None
    url = f"https://etelection.indiatimes.com/et_refinitiv/companyEstimateSummary?companyid={company_id}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        res = urllib.request.urlopen(req, timeout=8).read().decode("utf-8")
        return json.loads(res)
    except Exception as e:
        return None

def calculate_et_forecast_score(upside_pct, buy_pct, num_analysts, downside_low_pct, high_upside_pct):
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
    if buy_pct is not None:
        if buy_pct >= 85: pts += 35.0
        elif buy_pct >= 70: pts += 28.0 + (buy_pct - 70) * (7.0 / 15.0)
        elif buy_pct >= 50: pts += 18.0 + (buy_pct - 50) * (10.0 / 20.0)
        else: pts += max(5.0, buy_pct * 0.36)
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

def main():
    print("==================================================================")
    print("=== EXTRACTING ET PRIME SCORES & ET MARKETS RECOS FOR WATCHLIST ==")
    print("==================================================================")

    master_file = "scripts/combined_master_stocks.json"
    with open(master_file, "r", encoding="utf-8") as f:
        stocks = json.load(f)
    print(f"Loaded {len(stocks)} stocks from {master_file}.")

    # Step 1: Resolve all stocks to ET IDs
    print("\nStep 1: Resolving ET Company IDs...")
    id_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(resolve_et_id, s): s for s in stocks}
        for fut in concurrent.futures.as_completed(futures):
            sym, cid, seo, tag_name = fut.result()
            if cid:
                id_map[sym] = {"company_id": cid, "seo_name": seo, "tag_name": tag_name}

    print(f"Mapped {len(id_map)} / {len(stocks)} stocks.")

    # Step 2: Fetch ET data
    print("\nStep 2: Fetching ET Prime & Recommendations Data...")
    et_data_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        fut_to_sym = {}
        for s in stocks:
            sym = s["symbol"]
            info = id_map.get(sym)
            if info and info["company_id"]:
                fut = executor.submit(fetch_et_stock_data, info["company_id"])
                fut_to_sym[fut] = (sym, info)
                
        for fut in concurrent.futures.as_completed(fut_to_sym):
            sym, info = fut_to_sym[fut]
            res = fut.result()
            if res:
                et_data_map[sym] = (info, res)

    print(f"Successfully fetched ET data for {len(et_data_map)} / {len(stocks)} stocks.")

    # Step 3: Parse and merge into stocks
    print("\nStep 3: Merging ET Prime features & replacing forecast data...")
    prime_count = 0
    reco_count = 0

    for s in stocks:
        sym = s["symbol"]
        cmp_price = s.get("today_price") or s.get("live_movement", {}).get("curr_price") or 1.0

        if sym in et_data_map:
            info, data = et_data_map[sym]
            sr = data.get("refinitiveMetaByCompanyId") or {}
            pt = data.get("priceTarget") or {}
            recos = data.get("recommendations") or []
            tvc = data.get("targetVsCurrent")

            # Prime features
            avg_score = sr.get("avgScore")
            avg_outlook = sr.get("avgScoreOutlook")
            earn_score = sr.get("analystScore")
            fund_score = sr.get("fundScore")
            rv_score = sr.get("rvScore")
            risk_score = sr.get("riskScore")
            pm_score = sr.get("techScore")
            pdf_link = sr.get("pdfLink")

            # Clean integer values if valid
            def parse_score_val(v):
                if v is None or v == "" or v == "NR": return None
                try: return int(v)
                except: return None

            stock_score_val = parse_score_val(avg_score)
            earn_val = parse_score_val(earn_score)
            fund_val = parse_score_val(fund_score)
            rv_val = parse_score_val(rv_score)
            risk_val = parse_score_val(risk_score)
            pm_val = parse_score_val(pm_score)

            if stock_score_val is not None:
                prime_count += 1

            s["et_prime"] = {
                "company_id": info["company_id"],
                "seo_name": info["seo_name"],
                "stock_score": stock_score_val,
                "score_outlook": avg_outlook or "NEUTRAL",
                "earnings_score": earn_val,
                "fundamental_score": fund_val,
                "rv_score": rv_val,
                "risk_score": risk_val,
                "momentum_score": pm_val,
                "pdf_link": pdf_link or ""
            }

            # Recommendations & Price Target from ET Market
            mean_target = pt.get("Mean")
            median_target = pt.get("Median")
            high_target = pt.get("High")
            low_target = pt.get("Low")
            num_estimates = pt.get("NumberOfEstimates")

            latest_reco = recos[0] if recos else {}
            mean_reco_text = latest_reco.get("MeanText")
            reco_count_val = latest_reco.get("NumberOfRecommendations")
            total_analysts = reco_count_val or num_estimates

            # Parse stats
            stats_list = latest_reco.get("Statistics", {}).get("Statistic", [])
            stat_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for st in stats_list:
                rec_type = st.get("Recommendation")
                cnt = st.get("NumberOfAnalysts", 0)
                if rec_type in stat_counts:
                    stat_counts[rec_type] = cnt

            strong_buy_cnt = stat_counts[1]
            buy_cnt = stat_counts[2]
            hold_cnt = stat_counts[3]
            sell_cnt = stat_counts[4]
            strong_sell_cnt = stat_counts[5]

            # Potential upside
            upside_pct = None
            if tvc is not None:
                try: upside_pct = round(float(tvc), 1)
                except: pass
            if upside_pct is None and mean_target and cmp_price:
                upside_pct = round(((float(mean_target) - cmp_price) / cmp_price) * 100, 1)

            high_upside_pct = round(((float(high_target) - cmp_price) / cmp_price) * 100, 1) if high_target and cmp_price else (upside_pct or 0.0)
            downside_low_pct = round(((float(low_target) - cmp_price) / cmp_price) * 100, 1) if low_target and cmp_price else (0.0)

            total_recos = strong_buy_cnt + buy_cnt + hold_cnt + sell_cnt + strong_sell_cnt
            bull_cnt = strong_buy_cnt + buy_cnt
            bull_pct = round((bull_cnt / total_recos * 100), 1) if total_recos > 0 else (75.0 if mean_reco_text in ["STRONG BUY", "BUY"] else 40.0)

            if mean_target is not None or mean_reco_text is not None:
                reco_count += 1
                # Format consensus rating nicely e.g. "Strong Buy" / "Buy" / "Hold"
                consensus_display = mean_reco_text.title() if mean_reco_text else "Buy"

                # Calculate forecast score using real ET data
                fc_score = calculate_et_forecast_score(upside_pct, bull_pct, total_analysts, downside_low_pct, high_upside_pct)

                s["forecast"] = {
                    "source": "ET Markets (Economic Times)",
                    "mean_target": round(float(mean_target), 2) if mean_target else None,
                    "median_target": round(float(median_target), 2) if median_target else None,
                    "high_target": round(float(high_target), 2) if high_target else None,
                    "low_target": round(float(low_target), 2) if low_target else None,
                    "upside_mean_pct": upside_pct,
                    "upside_high_pct": high_upside_pct,
                    "downside_low_pct": downside_low_pct,
                    "num_analysts": total_analysts or total_recos,
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
                # No active analyst coverage in ET Markets (common for smaller microcaps)
                # We align forecast_score with the ET stock score if available
                fc_score = round(max(30.0, min(85.0, (stock_score_val or 5) * 8.5)), 1)
                s["forecast_score"] = fc_score
                s["forecast"]["source"] = "No Active ET Consensus"
                s["forecast"]["forecast_score"] = fc_score
        else:
            # Fallback for unmapped (e.g. unlisted EMVEE)
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

        # Step 4: Recalculate Master Quad Score
        # Quad = 0.30*Funda + 0.30*Tech + 0.20*Mood + 0.20*Forecast
        f_score = float(s.get("score") or 50.0)
        t_score = float(s.get("tech_score") or 50.0)
        m_score = float(s.get("mood_score") or 50.0)
        fc_score = float(s.get("forecast_score") or 50.0)

        quad_score = round(0.30 * f_score + 0.30 * t_score + 0.20 * m_score + 0.20 * fc_score, 1)
        s["master_score"] = quad_score

        # Confluence classification
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

    # Step 5: Sort by Master Score and assign Master Rank
    stocks.sort(key=lambda x: x.get("master_score", 0), reverse=True)
    for r, s in enumerate(stocks, 1):
        s["master_rank"] = r

    # Save to JSON
    with open(master_file, "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2, ensure_ascii=False)

    print(f"\n==================================================================")
    print(f"Extraction & Synthesis complete!")
    print(f"Total stocks: {len(stocks)}")
    print(f"Stocks with ET Prime Stock Score: {prime_count}")
    print(f"Stocks with ET Analyst Recos & Targets: {reco_count}")
    print(f"Saved updated master data to {master_file}")
    print("==================================================================")

if __name__ == "__main__":
    main()
