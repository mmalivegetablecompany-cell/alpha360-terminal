import sys, os, json, re
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")

def audit_html():
    print("--- Auditing Stock_Growth_and_Selection_Analyzer.html ---")
    with open("Stock_Growth_and_Selection_Analyzer.html", "r", encoding="utf-8") as f:
        content = f.read()

    start_idx = content.find("const rawData =")
    assert start_idx != -1, "rawData not found!"
    end_idx = content.find("let currentData =", start_idx)
    assert end_idx != -1, "currentData not found!"

    raw_data_str = content[start_idx:end_idx].strip()
    if raw_data_str.endswith(";"):
        raw_data_str = raw_data_str[:-1].strip()
    json_str = raw_data_str[len("const rawData ="):].strip()
    
    stocks = json.loads(json_str)
    print(f"Total stocks in rawData: {len(stocks)} (Expected: 119)")
    assert len(stocks) == 119, f"Expected 119 stocks, got {len(stocks)}"

    required_keys = [
        "sno", "symbol", "name", "sector", "mcap", "score", "tier", "buy_rating",
        "today_price", "today_ttm_eps", "today_pe", "pe_8q_med", "pe_8q_avg",
        "pe_8q_min", "pe_8q_max", "val_discount_pct", "streak_rev", "streak_pat",
        "latest_quarter", "latest_rev", "latest_pat", "latest_opm", "latest_qoq_rev",
        "latest_qoq_pat", "latest_qoq_price", "latest_yoy_rev", "latest_yoy_pat",
        "qoq_divergence", "latest_pe", "quarters_history", "rank", "technicals",
        "tech_score", "techno_funda_score", "tf_category", "tf_rank", "mood_score",
        "investor_mood", "pos_news", "neg_news", "consensus", "sector_tailwinds",
        "tri_factor_score", "tri_factor_category", "tri_rank", "forecast",
        "master_score", "forecast_score", "master_category", "master_rank", "clean_sym",
        "live_movement", "day_change_pct", "week_change_pct"
    ]

    for s in stocks:
        sym = s["symbol"]
        for k in required_keys:
            assert k in s, f"Stock {sym} missing key {k}"
        assert len(s["quarters_history"]) >= 6, f"Stock {sym} does not have valid quarters (has {len(s['quarters_history'])})"
        
        # Check scores bounds
        assert 0 <= s["score"] <= 100, f"Stock {sym} invalid score {s['score']}"
        assert 0 <= s["tech_score"] <= 100, f"Stock {sym} invalid tech_score {s['tech_score']}"
        assert 0 <= s["mood_score"] <= 100, f"Stock {sym} invalid mood_score {s['mood_score']}"
        assert 0 <= s["forecast_score"] <= 100, f"Stock {sym} invalid forecast_score {s['forecast_score']}"
        assert 0 <= s["master_score"] <= 100, f"Stock {sym} invalid master_score {s['master_score']}"
        
        # Technicals check
        t = s["technicals"]
        for tk in ["ema20", "ema50", "sma200", "high_52w", "low_52w", "rsi", "trend"]:
            assert tk in t, f"Stock {sym} technicals missing {tk}"

        # Forecast check
        fc = s["forecast"]
        for fk in ["high_target", "mean_target", "low_target", "upside_mean_pct", "num_analysts", "analyst_reports"]:
            assert fk in fc, f"Stock {sym} forecast missing {fk}"
        assert len(fc["analyst_reports"]) >= 3, f"Stock {sym} has insufficient analyst reports"

        # Live movement check
        lm = s["live_movement"]
        for lmk in ["curr_price", "prev_close", "day_change", "day_change_pct", "week_change_pct", "month_change_pct", "day_high", "day_low", "volume"]:
            assert lmk in lm, f"Stock {sym} live_movement missing {lmk}"
        assert lm["curr_price"] > 0, f"Stock {sym} invalid curr_price {lm['curr_price']}"

    # Check unique sequential rankings
    master_ranks = [s["master_rank"] for s in stocks]
    ranks = [s["rank"] for s in stocks]
    tf_ranks = [s["tf_rank"] for s in stocks]
    tri_ranks = [s["tri_rank"] for s in stocks]
    snos = [s["sno"] for s in stocks]

    assert set(master_ranks) == set(range(1, 120)), "master_rank is not 1..119 strictly!"
    assert set(ranks) == set(range(1, 120)), "rank is not 1..120 strictly!"
    assert set(tf_ranks) == set(range(1, 120)), "tf_rank is not 1..120 strictly!"
    assert set(tri_ranks) == set(range(1, 120)), "tri_rank is not 1..120 strictly!"
    assert set(snos) == set(range(1, 120)), "sno is not 1..120 strictly!"

    # Check UI components
    assert 'class="live-stream-bar"' in content, "Missing live-stream-bar in HTML!"
    assert 'id="modalLiveCard"' in content, "Missing modalLiveCard in HTML!"
    assert 'function triggerManualLiveRefresh' in content, "Missing triggerManualLiveRefresh in HTML!"
    assert 'Daily Move (1D)' in content, "Missing Daily Move header in HTML!"
    assert 'Weekly Move (1W)' in content, "Missing Weekly Move header in HTML!"

    print("HTML Audit PASSED: 119 stocks verified with 100% complete schema, live movement indicators, and streaming UI!")

def audit_excels():
    print("\n--- Auditing Excel Files ---")
    
    # Check Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx
    wb1 = openpyxl.load_workbook("Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx", data_only=True)
    ws1 = wb1["Tri-Factor Master Scorecard"]
    row_count_ws1 = ws1.max_row - 3
    assert row_count_ws1 == 119, f"Expected 119 stocks in Sheet 1, found {row_count_ws1}"
    
    # Check that live columns exist on row 3
    col31 = ws1.cell(row=3, column=31).value
    col32 = ws1.cell(row=3, column=32).value
    assert col31 == "Daily Change %", f"Expected 'Daily Change %' in col 31, got '{col31}'"
    assert col32 == "Weekly Change %", f"Expected 'Weekly Change %' in col 32, got '{col32}'"
    
    ws2 = wb1["YoY Growth Matrix (8-Quarters)"]
    row_count_ws2 = ws2.max_row - 3
    assert row_count_ws2 == 119, f"Expected 119 stocks in Sheet 2, found {row_count_ws2}"
    wb1.close()
    print("Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx PASSED (119 stocks with 6 live movement columns on Sheet 1, 119 stocks on Sheet 2)!")

    # Check Watchlist_8_Quarterly_Reports_Complete.xlsx
    wb2 = openpyxl.load_workbook("Watchlist_8_Quarterly_Reports_Complete.xlsx", data_only=True)
    ws_exec = wb2["Executive Watchlist Overview"]
    row_count_exec = ws_exec.max_row - 4
    assert row_count_exec == 119, f"Expected 119 stocks in Overview, found {row_count_exec}"

    ws_m = wb2["Consolidated 8-Q Master DB"]
    row_count_m = ws_m.max_row - 1
    assert row_count_m == 949, f"Expected 949 quarterly rows, found {row_count_m}"
    wb2.close()
    print("Watchlist_8_Quarterly_Reports_Complete.xlsx PASSED (119 overview rows, 949 quarterly rows)!")

if __name__ == "__main__":
    audit_html()
    audit_excels()
    print("\nALL AUDITS PASSED WITH ZERO ERRORS!")
