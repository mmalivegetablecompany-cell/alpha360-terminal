import sys, os, json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

sys.stdout.reconfigure(encoding="utf-8")

def update_all_workbooks():
    print("==================================================================")
    print("=== UPDATING EXCEL WORKBOOKS: 3-PILLAR MASTER SCORE (NO MOOD) ===")
    print("==================================================================")
    
    with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)
        
    print(f"Loaded {len(stocks)} stocks from combined_master_stocks.json.")
    
    val_files = [
        "Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx",
        "Watchlist_Quarterly_Growth_and_Selection_Analysis.xlsx",
        "Watchlist_Quarterly_Growth_and_Selection_Analysis_Updated.xlsx"
    ]
    
    hdr_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    hdr_font = Font(name="Calibri", size=10, bold=True, color="38BDF8")
    hdr_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    et_hdr_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    et_hdr_font = Font(name="Calibri", size=10, bold=True, color="FBBF24")

    headers_to_add = [
        ("Daily Change %", 31, hdr_fill, hdr_font),
        ("Weekly Change %", 32, hdr_fill, hdr_font),
        ("Day Low (₹)", 33, hdr_fill, hdr_font),
        ("Day High (₹)", 34, hdr_fill, hdr_font),
        ("Traded Volume", 35, hdr_fill, hdr_font),
        ("Last Price Update", 36, hdr_fill, hdr_font),
        # 7 New ET Prime Columns
        ("ET Stock Score (1-10)", 37, et_hdr_fill, et_hdr_font),
        ("ET Score Outlook", 38, et_hdr_fill, et_hdr_font),
        ("ET Earnings Score (1-10)", 39, et_hdr_fill, et_hdr_font),
        ("ET Fundamental Score (1-10)", 40, et_hdr_fill, et_hdr_font),
        ("ET Rel Valuation Score (1-10)", 41, et_hdr_fill, et_hdr_font),
        ("ET Risk Score (1-10)", 42, et_hdr_fill, et_hdr_font),
        ("ET Price Momentum Score (1-10)", 43, et_hdr_fill, et_hdr_font)
    ]

    for val_path in val_files:
        if not os.path.exists(val_path):
            continue
        print(f"\nProcessing {val_path}...")
        wb = openpyxl.load_workbook(val_path)
        
        # Sheet 1: Tri-Factor Master Scorecard
        if "Tri-Factor Master Scorecard" in wb.sheetnames:
            ws1 = wb["Tri-Factor Master Scorecard"]
            
            # Update Headers to reflect new 35/25/20/20 Master Score
            c6 = ws1.cell(row=3, column=6, value="Master Score (0-100)")
            c6.fill = hdr_fill; c6.font = Font(name="Calibri", size=10, bold=True, color="FBBF24"); c6.alignment = hdr_align
            
            c7 = ws1.cell(row=3, column=7, value="Funda Score (35%)")
            c7.fill = hdr_fill; c7.font = hdr_font; c7.alignment = hdr_align

            c8 = ws1.cell(row=3, column=8, value="Tech Score (20%)")
            c8.fill = hdr_fill; c8.font = hdr_font; c8.alignment = hdr_align

            c9 = ws1.cell(row=3, column=9, value="Mood Sentiment (0% Excluded)")
            c9.fill = hdr_fill; c9.font = hdr_font; c9.alignment = hdr_align

            c10 = ws1.cell(row=3, column=10, value="Confluence Verdict")
            c10.fill = hdr_fill; c10.font = hdr_font; c10.alignment = hdr_align

            c22 = ws1.cell(row=3, column=22, value="Master Score (35%F + 25%ET_FC + 20%ET_Score + 20%T)")
            c22.fill = hdr_fill
            c22.font = Font(name="Calibri", size=10, bold=True, color="FBBF24")
            c22.alignment = hdr_align

            # Update Column 23 Header to reflect ET Forecast Score
            c23 = ws1.cell(row=3, column=23, value="ET Forecast Score (25%)")
            c23.fill = hdr_fill
            c23.font = hdr_font
            c23.alignment = hdr_align

            for text, col_idx, f_fill, f_font in headers_to_add:
                cell = ws1.cell(row=3, column=col_idx, value=text)
                cell.fill = f_fill
                cell.font = f_font
                cell.alignment = hdr_align
                
            # Clear existing data rows (row 4 onwards)
            max_r = ws1.max_row
            if max_r >= 4:
                ws1.delete_rows(4, max_r - 3)
                
            for s in stocks:
                t = s.get("technicals", {})
                f = s.get("forecast", {})
                b = f.get("breakdown", {})
                lm = s.get("live_movement", {})
                ep = s.get("et_prime", {})
                
                b_str = f"{b.get('strong_buy', 0)} SB / {b.get('buy', 0)} Buy / {b.get('hold', 0)} Hold / {b.get('sell', 0) + b.get('strong_sell', 0)} Sell"
                
                cmp_price = s.get("today_price") or lm.get("curr_price")
                day_chg_pct = s.get("day_change_pct") if s.get("day_change_pct") is not None else lm.get("day_change_pct", 0.0)
                week_chg_pct = s.get("week_change_pct") if s.get("week_change_pct") is not None else lm.get("week_change_pct", 0.0)
                day_low = lm.get("day_low", cmp_price)
                day_high = lm.get("day_high", cmp_price)
                vol = lm.get("volume", 0)
                last_upd = lm.get("last_updated", "Live Tick")

                row_data = [
                    s.get("master_rank"),
                    s.get("symbol"),
                    s.get("name"),
                    s.get("sector"),
                    s.get("mcap"),
                    s.get("master_score"),       # Master Score: 35% Funda + 25% ET FC + 20% ET Score + 20% Tech
                    s.get("score"),              # Funda (35%)
                    s.get("tech_score"),         # Tech (20%)
                    s.get("mood_score"),         # Mood Sentiment (0% Excluded from Master Score)
                    s.get("master_category"),    # Master Confluence Verdict
                    s.get("investor_mood"),
                    s.get("consensus"),
                    s.get("pos_news"),
                    s.get("neg_news"),
                    cmp_price,
                    s.get("today_pe"),
                    t.get("rsi"),
                    t.get("high_52w"),
                    t.get("dist_52w_high"),
                    t.get("trend"),
                    s.get("buy_rating"),
                    s.get("master_score"),       # Master Score (35%F + 25%ET_FC + 20%ET_Score + 20%T)
                    s.get("forecast_score"),     # ET Forecast Score (25%)
                    f.get("mean_target"),
                    f.get("high_target"),
                    f.get("low_target"),
                    f.get("upside_mean_pct"),
                    f.get("consensus_rating"),
                    f.get("num_analysts"),
                    b_str,
                    day_chg_pct,
                    week_chg_pct,
                    day_low,
                    day_high,
                    vol,
                    last_upd,
                    # New ET Prime features
                    ep.get("stock_score"),
                    ep.get("score_outlook"),
                    ep.get("earnings_score"),
                    ep.get("fundamental_score"),
                    ep.get("rv_score"),
                    ep.get("risk_score"),
                    ep.get("momentum_score")
                ]
                ws1.append(row_data)
            print(f"  Updated 'Tri-Factor Master Scorecard' with {len(stocks)} stock rows & 43 columns.")

        # Sheet 2: YoY Growth Matrix (8-Quarters)
        if "YoY Growth Matrix (8-Quarters)" in wb.sheetnames:
            ws2 = wb["YoY Growth Matrix (8-Quarters)"]
            max_r2 = ws2.max_row
            if max_r2 >= 4:
                ws2.delete_rows(4, max_r2 - 3)
                
            for s in stocks:
                qh = s.get("quarters_history", [])
                yoy_pats = [q.get("YoY_PAT") for q in qh]
                while len(yoy_pats) < 8:
                    yoy_pats.append(None)
                    
                row_data = [
                    s.get("master_rank"),
                    s.get("symbol"),
                    s.get("name"),
                    s.get("sector"),
                    s.get("latest_yoy_rev"),
                    s.get("latest_yoy_pat")
                ] + yoy_pats
                ws2.append(row_data)
            print(f"  Updated 'YoY Growth Matrix (8-Quarters)' with {len(stocks)} stock rows.")

        wb.save(val_path)
        wb.close()
        print(f"Saved {val_path} successfully!")

    # -------------------------------------------------------------
    # 2. Update Watchlist_8_Quarterly_Reports_Complete.xlsx
    # -------------------------------------------------------------
    wb_8q_path = "Watchlist_8_Quarterly_Reports_Complete.xlsx"
    if os.path.exists(wb_8q_path):
        print(f"\nProcessing {wb_8q_path}...")
        wb = openpyxl.load_workbook(wb_8q_path)
        
        # Sheet 1: Executive Watchlist Overview
        if "Executive Watchlist Overview" in wb.sheetnames:
            ws_exec = wb["Executive Watchlist Overview"]
            et_exec_headers = [
                ("ET Stock Score", 13),
                ("ET Potential Upside %", 14),
                ("ET 1Y Target (₹)", 15),
                ("ET Consensus Reco", 16)
            ]
            for text, col_idx in et_exec_headers:
                c = ws_exec.cell(row=4, column=col_idx, value=text)
                c.fill = hdr_fill
                c.font = hdr_font
                c.alignment = hdr_align

            max_r_exec = ws_exec.max_row
            if max_r_exec >= 5:
                ws_exec.delete_rows(5, max_r_exec - 4)
                
            for s in stocks:
                qh = s.get("quarters_history", [])
                last_q = qh[-1] if qh else {}
                ep = s.get("et_prime", {})
                fc = s.get("forecast", {})
                row_data = [
                    s.get("master_rank"),
                    s.get("clean_sym") or s.get("symbol"),
                    s.get("name"),
                    s.get("sector"),
                    s.get("mcap"),
                    "8 Qtrs",
                    s.get("latest_quarter"),
                    f"{(s.get('latest_rev') or 0):,.1f}",
                    f"{(s.get('latest_pat') or 0):,.1f}",
                    f"{(s.get('latest_opm') or 0):.0f}%",
                    last_q.get("Ann_Date", "2026-07-31"),
                    s.get("today_price"),
                    ep.get("stock_score"),
                    fc.get("upside_mean_pct"),
                    fc.get("mean_target"),
                    fc.get("consensus_rating")
                ]
                ws_exec.append(row_data)
            print(f"  Updated 'Executive Watchlist Overview' with {len(stocks)} stock rows.")

        wb.save(wb_8q_path)
        wb.close()
        print(f"Saved {wb_8q_path} successfully!")

    print("\n==================================================================")
    print("=== ALL EXCEL WORKBOOKS SYNCHRONIZED WITH 3-PILLAR MASTER SCORES! =")
    print("==================================================================")

if __name__ == "__main__":
    update_all_workbooks()
