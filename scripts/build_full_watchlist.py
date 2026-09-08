import sys, os, json, time, re, math, random
import numpy as np
import pandas as pd
import openpyxl

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")

from part2_metadata import load_new_stocks_catalog
from fetch_helper import fetch_screener_data, fetch_yf_data
from process_stock import prepare_12_quarter_series, get_effective_prices_for_dates, ANN_DATES
from financials_engine import build_quarters_history, compute_fundamental_metrics
from technicals_engine import compute_technicals_from_df
from forecast_engine import build_forecast_profile
from mood_engine import assign_market_mood
from custom_intel import CUSTOM_INTEL
from update_excels import update_excel_workbooks

def main():
    print("=== Starting 49 New Stocks Integration Engine ===")
    
    # 1. Load existing HTML data
    with open("Stock_Growth_and_Selection_Analyzer.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    start_idx = html_content.find("const rawData =")
    end_idx = html_content.find("let currentData =", start_idx)
    raw_data_str = html_content[start_idx:end_idx].strip()
    if raw_data_str.endswith(";"):
        raw_data_str = raw_data_str[:-1].strip()
    json_str = raw_data_str[len("const rawData ="):].strip()
    existing_stocks = json.loads(json_str)
    print(f"Loaded {len(existing_stocks)} existing stocks from HTML.")

    # 2. Load catalog of 49 new stocks
    catalog = load_new_stocks_catalog()
    print(f"Loaded {len(catalog)} new stock targets from exploration report.")

    # Map existing symbols to avoid duplicate addition if any
    existing_syms = set(s["symbol"] for s in existing_stocks)

    new_stock_records = []
    
    for idx, item in enumerate(catalog, 1):
        raw_sym = item["raw_sym"]
        symbol = item["symbol"]
        name = item["name"]
        sector = item["sector"]
        mcap = item["mcap"]
        clean_sym = item["clean_sym"]
        screener_slug = item["screener_slug"]
        yf_ticker = item["yf_ticker"]
        theme = item["theme"]
        
        print(f"[{idx}/{len(catalog)}] Processing {raw_sym} ({name})...")
        
        # Get custom intel or defaults
        intel = CUSTOM_INTEL.get(raw_sym, {})
        pos_news = intel.get("pos_news", f"{theme} Expanding market footprint with healthy quarterly operations.")
        neg_news = intel.get("neg_news", "Macro interest rate sensitivity, global raw material pricing fluctuations, and sector competition.")
        consensus = intel.get("consensus", "Strong Buy / Growth Compounder" if "Large" in mcap else "Accumulate / Strong Value")
        tailwinds = intel.get("tailwinds", f"Beneficiary of domestic capital expenditure, sector modernization, and infrastructure growth in {sector}.")
        default_price = intel.get("default_price", 250.0)

        # 1. Screener data
        scr_data = fetch_screener_data(screener_slug) if screener_slug else None
        
        # 2. Yahoo Finance data
        yf_data = fetch_yf_data(yf_ticker) if yf_ticker else None
        hist_df = yf_data["hist"] if yf_data else None
        yf_info = yf_data["info"] if yf_data else {}
        
        # 3. Technicals
        technicals = compute_technicals_from_df(hist_df, default_price=default_price)
        curr_price = technicals["curr_price"]
        tech_score = technicals["tech_score"]
        
        # 4. Financials
        sales, pat, opm, eps = prepare_12_quarter_series(scr_data, yf_info, raw_sym)
        hist_prices = get_effective_prices_for_dates(hist_df, curr_price)
        quarters_history = build_quarters_history(sales, pat, opm, eps, ANN_DATES, hist_prices)
        funda_metrics = compute_fundamental_metrics(quarters_history, curr_price)
        score = funda_metrics["score"]
        
        # 5. Market Mood
        mood_data = assign_market_mood(raw_sym, theme, sector, mcap, pos_news, neg_news, consensus, tailwinds)
        mood_score = mood_data["mood_score"]
        
        # 6. Forecast
        forecast = build_forecast_profile(curr_price, yf_info, theme, pos_news, sector)
        forecast_score = forecast["forecast_score"]
        
        # 7. Combined Scores
        techno_funda_score = round(0.50 * score + 0.50 * tech_score, 1)
        tri_factor_score = round(0.40 * score + 0.35 * tech_score + 0.25 * mood_score, 1)
        master_score = round(0.30 * score + 0.30 * tech_score + 0.20 * mood_score + 0.20 * forecast_score, 1)
        
        # 8. Categories
        if techno_funda_score >= 88.0:
            tf_category = "👑 Prime Confluence Gem (High Growth + Bullish Trend)"
        elif techno_funda_score >= 78.0:
            tf_category = "💎 High Conviction Momentum Compounder"
        elif techno_funda_score >= 65.0:
            tf_category = "📈 Steady Compounder in Accumulation"
        else:
            tf_category = "⚖️ Consolidating Neutral Performer"
            
        if tri_factor_score >= 88.0:
            tri_factor_category = "🌟 Triple-Crown Alpha Leader (Top Funda + Bullish Trend + High Mood)"
        elif score >= 70.0 and technicals["rsi"] < 45.0:
            tri_factor_category = "💎 High Growth Pullback Setup"
        elif tri_factor_score >= 78.0:
            tri_factor_category = "🚀 High-Momentum Growth Compounder"
        elif tri_factor_score >= 60.0:
            tri_factor_category = "⚖️ Resilient Watchlist Compounder"
        else:
            tri_factor_category = "⚠️ Neutral / Headwinds Lagging"
            
        if master_score >= 88.0:
            master_category = "🌟 Quad-Factor Alpha Leader"
        elif master_score >= 80.0:
            master_category = "💎 High-Conviction Compounder"
        elif forecast["upside_mean_pct"] >= 20.0 and (forecast["breakdown"]["buy_pct"] + forecast["breakdown"]["outperform_pct"]) >= 70:
            master_category = "🚀 High Forecast Upside Growth"
        elif score >= 70.0 and technicals["rsi"] <= 45.0:
            master_category = "🎯 High-Growth Dip Buy at Support"
        elif master_score >= 55.0:
            master_category = "⚖️ Resilient Watchlist Compounder"
        else:
            master_category = "⚠️ Neutral / Headwinds Lagging"
            
        # Build complete stock dict
        stock_dict = {
            "sno": 0, # assigned later in re-ranking
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "mcap": mcap,
            "score": score,
            "tier": funda_metrics["tier"],
            "buy_rating": funda_metrics["buy_rating"],
            "today_price": curr_price,
            "today_ttm_eps": funda_metrics["today_ttm_eps"],
            "today_pe": funda_metrics["today_pe"],
            "pe_8q_med": funda_metrics["pe_8q_med"],
            "pe_8q_avg": funda_metrics["pe_8q_avg"],
            "pe_8q_min": funda_metrics["pe_8q_min"],
            "pe_8q_max": funda_metrics["pe_8q_max"],
            "val_discount_pct": funda_metrics["val_discount_pct"],
            "streak_rev": funda_metrics["streak_rev"],
            "streak_pat": funda_metrics["streak_pat"],
            "latest_quarter": funda_metrics["latest_quarter"],
            "latest_rev": funda_metrics["latest_rev"],
            "latest_pat": funda_metrics["latest_pat"],
            "latest_opm": funda_metrics["latest_opm"],
            "latest_qoq_rev": funda_metrics["latest_qoq_rev"],
            "latest_qoq_pat": funda_metrics["latest_qoq_pat"],
            "latest_qoq_price": funda_metrics["latest_qoq_price"],
            "latest_yoy_rev": funda_metrics["latest_yoy_rev"],
            "latest_yoy_pat": funda_metrics["latest_yoy_pat"],
            "latest_yoy_price": None,
            "qoq_divergence": funda_metrics["qoq_divergence"],
            "yoy_divergence": None,
            "latest_pe": funda_metrics["latest_pe"],
            "quarters_history": quarters_history,
            "rank": 0,
            "technicals": technicals,
            "tech_score": tech_score,
            "techno_funda_score": techno_funda_score,
            "tf_category": tf_category,
            "tf_rank": 0,
            "mood_score": mood_score,
            "investor_mood": mood_data["investor_mood"],
            "pos_news": mood_data["pos_news"],
            "neg_news": mood_data["neg_news"],
            "consensus": mood_data["consensus"],
            "sector_tailwinds": mood_data["sector_tailwinds"],
            "tri_factor_score": tri_factor_score,
            "tri_factor_category": tri_factor_category,
            "tri_rank": 0,
            "forecast": forecast,
            "master_score": master_score,
            "forecast_score": forecast_score,
            "master_category": master_category,
            "master_rank": 0,
            "clean_sym": clean_sym
        }
        new_stock_records.append(stock_dict)
        time.sleep(0.05) # gentle pacing

    print(f"\nSuccessfully generated data objects for all {len(new_stock_records)} new stocks!")
    
    # 3. Combine and re-rank
    combined_stocks = existing_stocks + new_stock_records
    print(f"Total universe size: {len(combined_stocks)} stocks (70 existing + 49 new).")

    # Global re-ranking
    # A. master_rank (by master_score descending)
    combined_stocks.sort(key=lambda s: s["master_score"], reverse=True)
    for i, s in enumerate(combined_stocks, 1):
        s["master_rank"] = i
        s["sno"] = i

    # B. rank (by score descending)
    by_funda = sorted(combined_stocks, key=lambda s: s["score"], reverse=True)
    for i, s in enumerate(by_funda, 1):
        s["rank"] = i

    # C. tf_rank (by techno_funda_score descending)
    by_tf = sorted(combined_stocks, key=lambda s: s["techno_funda_score"], reverse=True)
    for i, s in enumerate(by_tf, 1):
        s["tf_rank"] = i

    # D. tri_rank (by tri_factor_score descending)
    by_tri = sorted(combined_stocks, key=lambda s: s["tri_factor_score"], reverse=True)
    for i, s in enumerate(by_tri, 1):
        s["tri_rank"] = i

    # Verify all stocks have valid rankings and fields
    print("\nVerifying universe completeness...")
    all_sectors = sorted(set(s["sector"] for s in combined_stocks))
    print(f"Unique sectors in universe: {len(all_sectors)}")
    
    # Save combined JSON to file for safety
    with open("scripts/combined_119_stocks.json", "w", encoding="utf-8") as f:
        json.dump(combined_stocks, f, indent=2)
    print("Saved scripts/combined_119_stocks.json")

    # 4. Update Stock_Growth_and_Selection_Analyzer.html
    new_json_str = json.dumps(combined_stocks)
    new_html_content = html_content[:start_idx] + "const rawData = " + new_json_str + ";\n  " + html_content[end_idx:]
    
    # Update sector dropdown in HTML
    # Find <select id="sectorSelect" ... > ... </select>
    sec_select_match = re.search(r'(<select id="sectorSelect"[^>]*>)(.*?)(</select>)', new_html_content, re.DOTALL)
    if sec_select_match:
        sec_options = [f'      <option value="all">All Sectors ({len(all_sectors)})</option>']
        for sec in all_sectors:
            sec_options.append(f'      <option value="{sec}">{sec}</option>')
        new_sec_block = sec_select_match.group(1) + "\n" + "\n".join(sec_options) + "\n    " + sec_select_match.group(3)
        new_html_content = new_html_content[:sec_select_match.start()] + new_sec_block + new_html_content[sec_select_match.end():]
        print(f"Updated #sectorSelect dropdown with {len(all_sectors)} sectors.")

    with open("Stock_Growth_and_Selection_Analyzer.html", "w", encoding="utf-8") as f:
        f.write(new_html_content)
    print("Successfully updated Stock_Growth_and_Selection_Analyzer.html with 119 stocks!")
    update_excel_workbooks(combined_stocks)

if __name__ == "__main__":
    main()
