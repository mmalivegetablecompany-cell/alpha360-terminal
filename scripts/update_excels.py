import sys, os, json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

sys.stdout.reconfigure(encoding="utf-8")

def update_excel_workbooks(combined_stocks):
    print("\n=== Updating Excel Workbooks with Real-Time Live Movements ===")
    
    # 1. Update Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx
    wb_val_path = "Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx"
    if os.path.exists(wb_val_path):
        wb = openpyxl.load_workbook(wb_val_path)
        
        # Sheet 1: Tri-Factor Master Scorecard
        ws1 = wb["Tri-Factor Master Scorecard"]
        
        # Ensure row 3 has live headers
        live_headers = [
            ("Daily Change %", 31),
            ("Weekly Change %", 32),
            ("Day Low (₹)", 33),
            ("Day High (₹)", 34),
            ("Traded Volume", 35),
            ("Last Price Update", 36)
        ]
        hdr_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        hdr_font = Font(name="Calibri", size=10, bold=True, color="38BDF8")
        hdr_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for text, col_idx in live_headers:
            cell = ws1.cell(row=3, column=col_idx, value=text)
            cell.fill = hdr_fill
            cell.font = hdr_font
            cell.alignment = hdr_align

        # Clear existing data rows (from row 4 onwards)
        max_r = ws1.max_row
        if max_r >= 4:
            ws1.delete_rows(4, max_r - 3)
            
        for s in combined_stocks:
            t = s.get("technicals", {})
            f = s.get("forecast", {})
            b = f.get("breakdown", {})
            lm = s.get("live_movement", {})
            
            b_str = f"{b.get('buy', 0)}/{b.get('outperform', 0)}/{b.get('hold', 0)}/{b.get('underperform', 0)}/{b.get('sell', 0)}"
            
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
                s.get("tri_factor_score"),
                s.get("score"),
                s.get("tech_score"),
                s.get("mood_score"),
                s.get("tri_factor_category"),
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
                s.get("master_score"),
                s.get("forecast_score"),
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
                last_upd
            ]
            ws1.append(row_data)
            
        print(f"Updated 'Tri-Factor Master Scorecard' with {len(combined_stocks)} rows and 6 live movement columns.")

        # Sheet 2: YoY Growth Matrix (8-Quarters)
        ws2 = wb["YoY Growth Matrix (8-Quarters)"]
        max_r2 = ws2.max_row
        if max_r2 >= 4:
            ws2.delete_rows(4, max_r2 - 3)
            
        for s in combined_stocks:
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
            
        print(f"Updated 'YoY Growth Matrix (8-Quarters)' with {len(combined_stocks)} rows.")
        wb.save(wb_val_path)
        wb.close()
        print(f"Saved {wb_val_path} successfully!")

    # 2. Update Watchlist_8_Quarterly_Reports_Complete.xlsx
    wb_8q_path = "Watchlist_8_Quarterly_Reports_Complete.xlsx"
    if os.path.exists(wb_8q_path):
        wb = openpyxl.load_workbook(wb_8q_path)
        
        # Sheet 1: Executive Watchlist Overview
        ws_exec = wb["Executive Watchlist Overview"]
        max_r_exec = ws_exec.max_row
        if max_r_exec >= 5:
            ws_exec.delete_rows(5, max_r_exec - 4)
            
        for s in combined_stocks:
            row_data = [
                s.get("sno"),
                s.get("clean_sym") or s.get("symbol"),
                s.get("name"),
                s.get("sector"),
                s.get("mcap"),
                "8 Qtrs",
                s.get("latest_quarter"),
                f"{(s.get('latest_rev') or 0):,.1f}",
                f"{(s.get('latest_pat') or 0):,.1f}",
                f"{(s.get('latest_opm') or 0):.0f}%"
            ]
            ws_exec.append(row_data)
            
        print(f"Updated 'Executive Watchlist Overview' with {len(combined_stocks)} rows.")

        # Sheet 2: Consolidated 8-Q Master DB
        ws_master = wb["Consolidated 8-Q Master DB"]
        max_r_m = ws_master.max_row
        if max_r_m >= 2:
            ws_master.delete_rows(2, max_r_m - 1)
            
        for s in combined_stocks:
            for q in s.get("quarters_history", []):
                ann_date = q.get("Ann_Date", "2026-07-31")
                row_data = [
                    s.get("sno"),
                    s.get("clean_sym") or s.get("symbol"),
                    s.get("name"),
                    s.get("sector"),
                    s.get("mcap"),
                    q.get("Quarter"),
                    ann_date,
                    "15:00:00",
                    "Market-Hours",
                    q.get("Effective_Price")
                ]
                ws_master.append(row_data)
                
        print(f"Updated 'Consolidated 8-Q Master DB' with {len(combined_stocks) * 8} quarterly rows.")
        wb.save(wb_8q_path)
        wb.close()
        print(f"Saved {wb_8q_path} successfully!")

if __name__ == "__main__":
    with open("scripts/combined_119_stocks.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    update_excel_workbooks(data)
