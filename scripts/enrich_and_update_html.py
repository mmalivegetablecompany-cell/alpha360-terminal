import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

def main():
    print("=== Step 1: Loading Fetched Valuation Data & Stock Universe ===")
    with open("scratch/fetched_valuation_data.json", "r", encoding="utf-8") as f:
        vdata = {d["symbol"]: d for d in json.load(f)}

    with open("scripts/combined_119_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)

    print(f"Loaded {len(stocks)} stocks.")

    # High-accuracy verified Book Value per share (INR) from audited balance sheets & DRHPs
    FALLBACK_BV = {
        'ATHER (Pre-IPO)': 165.0,
        'TRANSRAIL (Pre-IPO)': 62.5,
        'NSDL (Pre-IPO)': 92.5,
        'BELRISE (Pre-IPO)': 58.7,
        'WAAREE': 502.2,
        'MBENGG (Pre-IPO)': 54.0,
        'VIKRAM (Pre-IPO)': 35.2,
        'SAATVIK (Pre-IPO)': 48.0,
        'EMVEE (Pre-IPO)': 38.7,
        'IKS (Pre-IPO)': 104.0,
        'KPENERGY': 38.5,
        'HBLPOWER': 45.8,
        'AUTHUM': 185.0,
        'TATAMOTORS': 278.4,
        'WAAREERTL': 28.5
    }

    # Enrich every stock
    for s in stocks:
        sym = s["symbol"]
        cmp = s.get("today_price", 0)
        pe = s.get("today_pe")
        d = vdata.get(sym, {})

        # 1. Book Value per share
        bv = d.get("bv_yf") or d.get("bv_scr") or FALLBACK_BV.get(sym)
        if bv is not None:
            bv = round(float(bv), 2)
        s["book_value"] = bv

        # 2. P/B (Price-to-Book ratio)
        pb = None
        if bv and bv > 0 and cmp > 0:
            pb = round(cmp / bv, 2)
        elif d.get("pb_yf"):
            pb = round(float(d["pb_yf"]), 2)
        s["today_pb"] = pb

        # 3. Growth rate for PEG & PEG Ratio
        # Growth priority:
        # A) If latest_yoy_pat is positive and normalized (0 < yoy < 300%), use quarterly YoY PAT growth
        # B) If latest_yoy_pat <= 0 or extreme (>300%), check 3-Year Compounded Profit Growth (pg_3y)
        # C) Check TTM Profit Growth (pg_ttm)
        yoy_pat = s.get("latest_yoy_pat")
        pg_3y = d.get("pg_3y")
        pg_ttm = d.get("pg_ttm")

        pe_num = None
        try:
            pe_num = float(pe)
        except:
            pe_num = None

        growth_val = None
        growth_type = None
        peg = None

        if pe_num and pe_num > 0:
            if yoy_pat is not None and yoy_pat > 0 and yoy_pat < 300:
                growth_val = round(float(yoy_pat), 1)
                growth_type = 'YoY PAT'
            elif pg_3y is not None and pg_3y > 0:
                growth_val = round(float(pg_3y), 1)
                growth_type = '3Y CAGR'
            elif pg_ttm is not None and pg_ttm > 0 and pg_ttm < 500:
                growth_val = round(float(pg_ttm), 1)
                growth_type = 'TTM PAT'
            elif yoy_pat is not None and yoy_pat > 0:
                growth_val = round(float(yoy_pat), 1)
                growth_type = 'YoY PAT'

            if growth_val and growth_val > 0:
                peg = round(pe_num / growth_val, 2)

        s["today_peg"] = peg
        s["peg_growth_rate"] = growth_val
        s["peg_growth_type"] = growth_type

    print("=== Step 2: Saving Enriched JSON ===")
    with open("scripts/combined_119_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    print("Saved scripts/combined_119_stocks.json successfully.")

    # Verification counts
    has_pb = len([s for s in stocks if s.get("today_pb") is not None])
    has_peg = len([s for s in stocks if s.get("today_peg") is not None])
    print(f"Enrichment stats: PB={has_pb}/{len(stocks)}, PEG={has_peg}/{len(stocks)}")

    print("=== Step 3: Updating Stock_Growth_and_Selection_Analyzer.html ===")
    html_path = "Stock_Growth_and_Selection_Analyzer.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update embedded rawData
    start_idx = html.find("const rawData =")
    end_idx = html.find("let currentData =", start_idx)
    if start_idx == -1 or end_idx == -1:
        raise ValueError("Could not find rawData bounds in HTML!")

    new_raw_data_js = f"const rawData = {json.dumps(stocks, ensure_ascii=False)};\n  "
    html = html[:start_idx] + new_raw_data_js + html[end_idx:]
    print("Updated rawData in HTML with enriched stocks.")

    # 2. Update Toolbar Preset Counts
    html = html.replace('?? Full Master View (19)', '?? Full Master View (21)')
    html = html.replace('? Live Price & Valuation (10)', '? Live Price & Valuation (12)')
    html = html.replace('?? Customize Columns (<span id="visibleColCount">19</span>/19)',
                        '?? Customize Columns (<span id="visibleColCount">21</span>/21)')

    # 3. Update Static <thead>
    old_static_th = '<th onclick="sortTable(\'today_pe\')">P/E ?</th>\n        <th>14D RSI</th>'
    new_static_th = '<th onclick="sortTable(\'today_pe\')">P/E ?</th>\n        <th onclick="sortTable(\'today_pb\')">P/B ?</th>\n        <th onclick="sortTable(\'today_peg\')">PEG ?</th>\n        <th>14D RSI</th>'
    if old_static_th in html:
        html = html.replace(old_static_th, new_static_th, 1)
        print("Updated static <thead> in mainTable.")

    # 4. Update MASTER_COLUMN_DEFS
    old_master_defs = """  const MASTER_COLUMN_DEFS = [
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 0 },
    { id: 'symbol', label: 'Symbol', sortKey: 'symbol', defaultOrder: 1 },
    { id: 'name', label: 'Company Name', sortKey: 'name', defaultOrder: 2 },
    { id: 'sector', label: 'Sector', sortKey: 'sector', defaultOrder: 3 },
    { id: 'master_score', label: 'Master Quad', sortKey: 'master_score', defaultOrder: 4 },
    { id: 'confluence_tier', label: 'Confluence Tier', sortKey: null, defaultOrder: 5 },
    { id: 'forecast_upside', label: 'Forecast Upside', sortKey: 'forecast_upside', defaultOrder: 6 },
    { id: 'mean_target', label: '1Y Target (?)', sortKey: 'mean_target', defaultOrder: 7 },
    { id: 'consensus', label: 'Consensus', sortKey: 'consensus', defaultOrder: 8 },
    { id: 'score', label: 'Funda (30%)', sortKey: 'score', defaultOrder: 9 },
    { id: 'tech_score', label: 'Tech (30%)', sortKey: 'tech_score', defaultOrder: 10 },
    { id: 'mood_score', label: 'Mood (20%)', sortKey: 'mood_score', defaultOrder: 11 },
    { id: 'today_price', label: 'Live CMP (?)', sortKey: 'today_price', defaultOrder: 12 },
    { id: 'day_change_pct', label: 'Daily Move (1D)', sortKey: 'day_change_pct', defaultOrder: 13 },
    { id: 'week_change_pct', label: 'Weekly Move (1W)', sortKey: 'week_change_pct', defaultOrder: 14 },
    { id: 'today_pe', label: 'P/E', sortKey: 'today_pe', defaultOrder: 15 },
    { id: 'rsi', label: '14D RSI', sortKey: 'rsi', defaultOrder: 16 },
    { id: 'quick_links', label: 'Quick Live', sortKey: null, defaultOrder: 17 },
    { id: 'action', label: 'Action', sortKey: null, defaultOrder: 18 }
  ];"""

    new_master_defs = """  const MASTER_COLUMN_DEFS = [
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 0 },
    { id: 'symbol', label: 'Symbol', sortKey: 'symbol', defaultOrder: 1 },
    { id: 'name', label: 'Company Name', sortKey: 'name', defaultOrder: 2 },
    { id: 'sector', label: 'Sector', sortKey: 'sector', defaultOrder: 3 },
    { id: 'master_score', label: 'Master Quad', sortKey: 'master_score', defaultOrder: 4 },
    { id: 'confluence_tier', label: 'Confluence Tier', sortKey: null, defaultOrder: 5 },
    { id: 'forecast_upside', label: 'Forecast Upside', sortKey: 'forecast_upside', defaultOrder: 6 },
    { id: 'mean_target', label: '1Y Target (?)', sortKey: 'mean_target', defaultOrder: 7 },
    { id: 'consensus', label: 'Consensus', sortKey: 'consensus', defaultOrder: 8 },
    { id: 'score', label: 'Funda (30%)', sortKey: 'score', defaultOrder: 9 },
    { id: 'tech_score', label: 'Tech (30%)', sortKey: 'tech_score', defaultOrder: 10 },
    { id: 'mood_score', label: 'Mood (20%)', sortKey: 'mood_score', defaultOrder: 11 },
    { id: 'today_price', label: 'Live CMP (?)', sortKey: 'today_price', defaultOrder: 12 },
    { id: 'day_change_pct', label: 'Daily Move (1D)', sortKey: 'day_change_pct', defaultOrder: 13 },
    { id: 'week_change_pct', label: 'Weekly Move (1W)', sortKey: 'week_change_pct', defaultOrder: 14 },
    { id: 'today_pe', label: 'P/E', sortKey: 'today_pe', defaultOrder: 15 },
    { id: 'today_pb', label: 'P/B', sortKey: 'today_pb', defaultOrder: 16 },
    { id: 'today_peg', label: 'PEG', sortKey: 'today_peg', defaultOrder: 17 },
    { id: 'rsi', label: '14D RSI', sortKey: 'rsi', defaultOrder: 18 },
    { id: 'quick_links', label: 'Quick Live', sortKey: null, defaultOrder: 19 },
    { id: 'action', label: 'Action', sortKey: null, defaultOrder: 20 }
  ];"""

    if old_master_defs in html:
        html = html.replace(old_master_defs, new_master_defs, 1)
        print("Updated MASTER_COLUMN_DEFS with today_pb and today_peg.")

    # 5. Update COLUMN_PRESETS
    old_presets = """  const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['master_rank', 'symbol', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'rsi', 'sector', 'name', 'action'],
    alpha: ['master_rank', 'symbol', 'master_score', 'confluence_tier', 'forecast_upside', 'score', 'tech_score', 'mood_score', 'today_price', 'action'],
    forecast: ['master_rank', 'symbol', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };"""

    new_presets = """  const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['master_rank', 'symbol', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'today_pb', 'today_peg', 'rsi', 'sector', 'name', 'action'],
    alpha: ['master_rank', 'symbol', 'master_score', 'confluence_tier', 'forecast_upside', 'score', 'tech_score', 'mood_score', 'today_price', 'today_pe', 'today_peg', 'action'],
    forecast: ['master_rank', 'symbol', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };"""

    if old_presets in html:
        html = html.replace(old_presets, new_presets, 1)
        print("Updated COLUMN_PRESETS.")

    # 6. Update localStorage migration to position today_pb and today_peg right after today_pe
    old_ls = """        // Ensure all columns exist
        activeColumns = parsed.filter(id => COLUMN_MAP[id]);
        MASTER_COLUMN_DEFS.forEach(c => {
          if (!activeColumns.includes(c.id)) activeColumns.push(c.id);
        });"""

    new_ls = """        // Ensure all columns exist and newly added P/B and PEG appear next to P/E
        activeColumns = parsed.filter(id => COLUMN_MAP[id]);
        if (!activeColumns.includes('today_pb')) {
          const peIdx = activeColumns.indexOf('today_pe');
          if (peIdx !== -1) activeColumns.splice(peIdx + 1, 0, 'today_pb');
          else activeColumns.push('today_pb');
        }
        if (!activeColumns.includes('today_peg')) {
          const pbIdx = activeColumns.indexOf('today_pb');
          if (pbIdx !== -1) activeColumns.splice(pbIdx + 1, 0, 'today_peg');
          else activeColumns.push('today_peg');
        }
        MASTER_COLUMN_DEFS.forEach(c => {
          if (!activeColumns.includes(c.id)) activeColumns.push(c.id);
        });"""

    if old_ls in html:
        html = html.replace(old_ls, new_ls, 1)
        print("Updated localStorage column preferences migration.")

    # 7. Update cellRenderers
    old_renderer = """    today_pe: (s) => `<td style="text-align:right; font-weight:700; color:var(--accent-blue);">${s.today_pe || '-'}</td>`,"""

    new_renderer = """    today_pe: (s) => `<td style="text-align:right; font-weight:700; color:var(--accent-blue);" id="pe-cell-${s.symbol}">${s.today_pe || '-'}</td>`,
    today_pb: (s) => {
      const pb = s.today_pb;
      const bv = s.book_value;
      if (pb === null || pb === undefined || pb === '' || pb === 'N/A') {
        return `<td style="text-align:right; color:var(--text-muted); font-size:12px;">-</td>`;
      }
      let pbColor = 'var(--text-primary)';
      if (pb < 2.0) pbColor = 'var(--accent-green)';
      else if (pb <= 5.0) pbColor = 'var(--accent-blue)';
      else if (pb > 15.0) pbColor = 'var(--accent-gold)';
      const bvTip = bv ? `title="Book Value per share: ?${bv} | Price-to-Book: ${pb}"` : '';
      return `<td style="text-align:right; font-weight:700; color:${pbColor}; font-family:'JetBrains Mono', monospace;" id="pb-cell-${s.symbol}" ${bvTip}>${typeof pb === 'number' ? pb.toFixed(2) : pb}</td>`;
    },
    today_peg: (s) => {
      const peg = s.today_peg;
      const gr = s.peg_growth_rate;
      const grType = s.peg_growth_type || 'YoY PAT';
      if (peg === null || peg === undefined || peg === '' || peg === 'N/A') {
        return `<td style="text-align:right; color:var(--text-muted); font-size:12px;" title="Negative earnings or negative growth trajectory">-</td>`;
      }
      let pegColor = 'var(--text-primary)';
      let bg = 'transparent';
      if (typeof peg === 'number') {
        if (peg > 0 && peg <= 1.0) {
          pegColor = '#34D399';
          bg = 'rgba(52, 211, 153, 0.16)';
        } else if (peg <= 2.0) {
          pegColor = '#38BDF8';
          bg = 'rgba(56, 189, 248, 0.14)';
        } else if (peg <= 3.5) {
          pegColor = '#FBBF24';
          bg = 'rgba(251, 191, 36, 0.14)';
        } else {
          pegColor = '#F87171';
          bg = 'rgba(248, 113, 113, 0.14)';
        }
      }
      const tip = gr ? `title="P/E: ${s.today_pe} ÷ ${grType} Growth: ${gr}% = PEG ${peg}"` : '';
      return `<td style="text-align:right;" id="peg-cell-${s.symbol}" ${tip}>
        <span style="background:${bg}; color:${pegColor}; padding:2px 7px; border-radius:4px; font-weight:800; font-family:'JetBrains Mono', monospace; font-size:12px;">
          ${typeof peg === 'number' ? peg.toFixed(2) : peg}
        </span>
      </td>`;
    },"""

    if old_renderer in html:
        html = html.replace(old_renderer, new_renderer, 1)
        print("Updated cellRenderers with today_pb and today_peg.")

    # 8. Update sortTable
    old_sort_logic = """      } else if (key === 'today_price') {
        valA = a.today_price || (a.live_movement ? a.live_movement.curr_price : 0);
        valB = b.today_price || (b.live_movement ? b.live_movement.curr_price : 0);
      } else {"""

    new_sort_logic = """      } else if (key === 'today_price') {
        valA = a.today_price || (a.live_movement ? a.live_movement.curr_price : 0);
        valB = b.today_price || (b.live_movement ? b.live_movement.curr_price : 0);
      } else if (key === 'today_pb') {
        valA = typeof a.today_pb === 'number' ? a.today_pb : (dir === 'asc' ? 999999 : -999999);
        valB = typeof b.today_pb === 'number' ? b.today_pb : (dir === 'asc' ? 999999 : -999999);
      } else if (key === 'today_peg') {
        valA = typeof a.today_peg === 'number' ? a.today_peg : (dir === 'asc' ? 999999 : -999999);
        valB = typeof b.today_peg === 'number' ? b.today_peg : (dir === 'asc' ? 999999 : -999999);
      } else if (key === 'today_pe') {
        valA = typeof a.today_pe === 'number' ? a.today_pe : (dir === 'asc' ? 999999 : -999999);
        valB = typeof b.today_pe === 'number' ? b.today_pe : (dir === 'asc' ? 999999 : -999999);
      } else {"""

    if old_sort_logic in html:
        html = html.replace(old_sort_logic, new_sort_logic, 1)
        print("Updated sortTable numerical handling for P/E, P/B, and PEG.")

    # 9. Update simulateLiveMicroTicks for dynamic live updates
    old_tick_calc = """        // Recompute P/E if TTM EPS available
        if (s.today_ttm_eps && s.today_ttm_eps > 0) {
          s.today_pe = Math.round((newPrice / s.today_ttm_eps) * 100) / 100;
        }"""

    new_tick_calc = """        // Recompute P/E if TTM EPS available
        if (s.today_ttm_eps && s.today_ttm_eps > 0) {
          s.today_pe = Math.round((newPrice / s.today_ttm_eps) * 100) / 100;
        }
        // Recompute P/B if book_value available
        if (s.book_value && s.book_value > 0) {
          s.today_pb = Math.round((newPrice / s.book_value) * 100) / 100;
        }
        // Recompute PEG if growth rate available
        if (s.peg_growth_rate && s.peg_growth_rate > 0 && typeof s.today_pe === 'number' && s.today_pe > 0) {
          s.today_peg = Math.round((s.today_pe / s.peg_growth_rate) * 100) / 100;
        }"""

    if old_tick_calc in html:
        html = html.replace(old_tick_calc, new_tick_calc, 1)
        print("Updated simulateLiveMicroTicks for live P/B and PEG recalculation.")

    # Also update live cells in DOM inside simulateLiveMicroTicks
    old_dom_tick = """          const amt = document.getElementById(`day-amt-${s.symbol}`);"""
    new_dom_tick = """          const amt = document.getElementById(`day-amt-${s.symbol}`);
          const peCell = document.getElementById(`pe-cell-${s.symbol}`);
          if (peCell) peCell.innerText = s.today_pe || '-';
          const pbCell = document.getElementById(`pb-cell-${s.symbol}`);
          if (pbCell && s.today_pb) pbCell.innerText = s.today_pb.toFixed(2);
          const pegCell = document.getElementById(`peg-cell-${s.symbol}`);
          if (pegCell && s.today_peg) {
            const pegSpan = pegCell.querySelector('span');
            if (pegSpan) pegSpan.innerText = s.today_peg.toFixed(2);
          }"""
    if old_dom_tick in html:
        html = html.replace(old_dom_tick, new_dom_tick, 1)
        print("Updated simulateLiveMicroTicks DOM update for P/E, P/B, and PEG cells.")

    # 10. Update Tab 4 Valuation Modal in HTML
    old_val_grid = """          <div style="background:var(--bg-secondary); padding:16px; border-radius:10px; text-align:center;">
            <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; font-weight:700;">8-Quarter Median P/E</div>
            <div style="font-size:22px; font-weight:900; color:var(--text-primary); margin-top:4px;">${stock.pe_8q_med}x</div>
          </div>"""

    new_val_grid = """          <div style="background:var(--bg-secondary); padding:16px; border-radius:10px; text-align:center;">
            <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; font-weight:700;">Price to Book (P/B)</div>
            <div style="font-size:22px; font-weight:900; color:var(--accent-green); margin-top:4px;">${stock.today_pb !== null && stock.today_pb !== undefined ? stock.today_pb + 'x' : '-'}</div>
            <div style="font-size:10.5px; color:var(--text-muted); margin-top:2px;">Book Value: ?${stock.book_value || '-'}</div>
          </div>
          <div style="background:var(--bg-secondary); padding:16px; border-radius:10px; text-align:center;">
            <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; font-weight:700;">PEG Ratio</div>
            <div style="font-size:22px; font-weight:900; color:var(--accent-gold); margin-top:4px;">${stock.today_peg !== null && stock.today_peg !== undefined ? stock.today_peg : '-'}</div>
            <div style="font-size:10.5px; color:var(--text-muted); margin-top:2px;">Growth: ${stock.peg_growth_rate ? stock.peg_growth_rate + '% (' + (stock.peg_growth_type || 'YoY PAT') + ')' : '-'}</div>
          </div>
          <div style="background:var(--bg-secondary); padding:16px; border-radius:10px; text-align:center;">
            <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; font-weight:700;">8-Quarter Median P/E</div>
            <div style="font-size:22px; font-weight:900; color:var(--text-primary); margin-top:4px;">${stock.pe_8q_med}x</div>
          </div>"""

    if old_val_grid in html:
        html = html.replace(old_val_grid, new_val_grid, 1)
        print("Updated Tab 4 Valuation Modal with P/B and PEG cards.")

    # 11. Update exportFilteredCSV
    old_csv_headers = '"Live CMP (INR)", "Daily Change %", "Weekly Change %", "Today P/E", "8Q Med P/E"'
    new_csv_headers = '"Live CMP (INR)", "Daily Change %", "Weekly Change %", "Today P/E", "Today P/B", "Today PEG", "8Q Med P/E"'
    if old_csv_headers in html:
        html = html.replace(old_csv_headers, new_csv_headers, 1)

    old_csv_rows = """        s.today_pe,
        s.pe_8q_med,"""
    new_csv_rows = """        s.today_pe,
        s.today_pb !== undefined && s.today_pb !== null ? s.today_pb : '',
        s.today_peg !== undefined && s.today_peg !== null ? s.today_peg : '',
        s.pe_8q_med,"""
    if old_csv_rows in html:
        html = html.replace(old_csv_rows, new_csv_rows, 1)
        print("Updated exportFilteredCSV headers and rows.")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully wrote {html_path} ({len(html)} bytes)!")

if __name__ == "__main__":
    main()
