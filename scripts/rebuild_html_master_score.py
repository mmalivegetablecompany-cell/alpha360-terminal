import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

def update_html():
    print("==================================================================")
    print("=== REBUILDING HTML DASHBOARD: 35/25/20/20 MASTER SCORE FORMULA ===")
    print("==================================================================")

    with open("Stock_Growth_and_Selection_Analyzer.html", "r", encoding="utf-8") as f:
        html = f.read()

    with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)
    print(f"Loaded {len(stocks)} stocks from combined_master_stocks.json.")

    # 1. Update rawData
    s_idx = html.find("const rawData =")
    e_idx = html.find("let currentData =", s_idx)
    if s_idx == -1 or e_idx == -1:
        print("Error: Could not find rawData boundaries")
        return False

    new_json_str = json.dumps(stocks, ensure_ascii=False)
    html = html[:s_idx] + f"const rawData = {new_json_str};\n  " + html[e_idx:]
    print("✓ Successfully injected updated rawData (424 stocks).")

    # 2. Header subtitle
    html = re.sub(
        r'<p>(?:Quad-Factor Alpha Engine|Institutional Master Alpha Engine):.*?</p>',
        '<p>Institutional Master Alpha Engine: Fundamental Compounding (35%) + ET Forecast Suite (25%) + ET Prime Score (20%) + Technical Trends (20%)</p>',
        html,
        count=1
    )

    # 3. Stat Cards
    html = html.replace('🌟 Quad Alpha Leaders', '🌟 Master Alpha Leaders')
    html = html.replace('Master Quad Score &ge; 88.0', 'Master Score &ge; 88.0')

    # 4. Smart Filter preset button & dropdown
    html = html.replace('title="Master Score >= 88, Stage 2 Trend, Upside >= 15%">👑 Quad Alpha Leaders</button>',
                        'title="Master Score >= 88, Stage 2 Trend, Upside >= 15%">👑 Master Alpha Leaders</button>')
    html = html.replace('<label>Min Master Quad Score:</label>', '<label>Min Master Score:</label>')
    html = html.replace('&ge; 88 (🌟 Quad Alpha Leader)', '&ge; 88 (🌟 Master Alpha Leader)')

    # 5. Table Presets & Column Defs
    html = html.replace('🌟 Quad Alpha Core (10)', '🌟 Master Alpha Core (10)')
    html = html.replace("name: '👑 Quad Alpha Leaders'", "name: '👑 Master Alpha Leaders'")

    col_defs_pattern = r"const MASTER_COLUMN_DEFS = \[[\s\S]*?\];"
    new_col_defs = """const MASTER_COLUMN_DEFS = [
    { id: 'bucket', label: '🧺 Bucket', sortKey: null, defaultOrder: 0 },
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 22 },
    { id: 'symbol', label: 'Symbol', sortKey: 'symbol', defaultOrder: 22 },
    { id: 'name', label: 'Company Name', sortKey: 'name', defaultOrder: 22 },
    { id: 'sector', label: 'Sector', sortKey: 'sector', defaultOrder: 22 },
    { id: 'mcap_cr', label: 'Market Cap', sortKey: 'mcap_cr', defaultOrder: 22 },
    { id: 'master_score', label: 'Master Score (35/25/20/20)', sortKey: 'master_score', defaultOrder: 22 },
    { id: 'et_stock_score', label: 'ET Prime Score (20%)', sortKey: 'et_stock_score', defaultOrder: 22 },
    { id: 'confluence_tier', label: 'Confluence Tier', sortKey: null, defaultOrder: 22 },
    { id: 'forecast_upside', label: 'ET Potential Upside', sortKey: 'forecast_upside', defaultOrder: 22 },
    { id: 'mean_target', label: '1Y Target (₹)', sortKey: 'mean_target', defaultOrder: 22 },
    { id: 'consensus', label: 'Consensus', sortKey: 'consensus', defaultOrder: 22 },
    { id: 'score', label: 'Funda (35%)', sortKey: 'score', defaultOrder: 22 },
    { id: 'forecast_score', label: 'ET Forecast (25%)', sortKey: 'forecast_score', defaultOrder: 22 },
    { id: 'tech_score', label: 'Tech (20%)', sortKey: 'tech_score', defaultOrder: 22 },
    { id: 'today_price', label: 'Live CMP (₹)', sortKey: 'today_price', defaultOrder: 22 },
    { id: 'day_change_pct', label: 'Daily Move (1D)', sortKey: 'day_change_pct', defaultOrder: 22 },
    { id: 'week_change_pct', label: 'Weekly Move (1W)', sortKey: 'week_change_pct', defaultOrder: 22 },
    { id: 'today_pe', label: 'P/E', sortKey: 'today_pe', defaultOrder: 22 },
    { id: 'today_pb', label: 'P/B', sortKey: 'today_pb', defaultOrder: 22 },
    { id: 'today_peg', label: 'PEG', sortKey: 'today_peg', defaultOrder: 22 },
    { id: 'rsi', label: '14D RSI', sortKey: 'rsi', defaultOrder: 22 },
    { id: 'quick_links', label: 'Quick Live', sortKey: null, defaultOrder: 22 },
    { id: 'action', label: 'Action', sortKey: null, defaultOrder: 22 }
  ];"""
    html = re.sub(col_defs_pattern, new_col_defs, html, count=1)

    # Update COLUMN_PRESETS.alpha
    presets_pattern = r"const COLUMN_PRESETS = \{[\s\S]*?\};"
    new_presets = """const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['bucket', 'master_rank', 'symbol', 'mcap_cr', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'today_pb', 'today_peg', 'rsi', 'sector', 'name', 'action'],
    alpha: ['bucket', 'master_rank', 'symbol', 'mcap_cr', 'master_score', 'score', 'forecast_score', 'et_stock_score', 'tech_score', 'confluence_tier', 'forecast_upside', 'mean_target', 'today_price', 'today_pe', 'today_peg', 'action'],
    forecast: ['bucket', 'master_rank', 'symbol', 'mcap_cr', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };"""
    html = re.sub(presets_pattern, new_presets, html, count=1)

    # 6. Update Static Table Fallback Header
    html = html.replace('<th onclick="sortTable(\'master_score\')">Master Quad ↕</th>',
                        '<th onclick="sortTable(\'master_score\')">Master Score ↕</th>')

    # 7. Update Filter Pills
    html = html.replace("🌟 Tri-Pillar Leaders (&ge; 88)", "🌟 Master Alpha Leaders (&ge; 88)")
    html = html.replace("🌟 Quad Leaders (&ge; 88)", "🌟 Master Alpha Leaders (&ge; 88)")

    # 8. Update modalScoreBanner
    banner_pattern = r"document\.getElementById\('modalScoreBanner'\)\.innerHTML = `[\s\S]*?`;"
    new_banner = """document.getElementById('modalScoreBanner').innerHTML = `
      <div class="score-item" style="border-left:3px solid var(--accent-gold);">
        <div class="score-lbl">Master Score (0-100)</div>
        <div class="score-num" style="color:var(--accent-gold);">${stock.master_score}/100</div>
        <div style="font-size:11px; color:var(--text-muted);">${stock.master_category.split('(')[0]}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">Fundamental (35%)</div>
        <div class="score-num" style="color:var(--accent-green);">${stock.score}</div>
        <div style="font-size:11px; color:var(--text-muted);">Streak Rev:${stock.streak_rev} / PAT:${stock.streak_pat}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">ET Forecast (25%)</div>
        <div class="score-num" style="color:#06B6D4;">${f.forecast_score}</div>
        <div style="font-size:11px; color:var(--text-muted);">${f.consensus_rating || 'NR'} (${f.num_analysts || 0} Analysts)</div>
      </div>
      <div class="score-item" style="border-left: 2px solid rgba(168, 85, 247, 0.45);">
        <div class="score-lbl">ET Prime Score (20%)</div>
        <div class="score-num" style="color:#C084FC;">${(ep.stock_score !== null && ep.stock_score !== undefined) ? ep.stock_score + '/10 (' + (ep.stock_score * 10) + ')' : 'NR (50)'}</div>
        <div style="font-size:11px; color:var(--text-muted);">${ep.score_outlook || 'Refinitiv Score'}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">Technical (20%)</div>
        <div class="score-num" style="color:var(--accent-blue);">${stock.tech_score}</div>
        <div style="font-size:11px; color:var(--text-muted);">${t.trend ? t.trend.split(' ')[1] || 'Trend' : '-'}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">Master Rank</div>
        <div class="score-num" style="color:var(--accent-gold);">#${stock.master_rank}</div>
        <div style="font-size:11px; color:var(--text-muted);">of 424 Watchlist Equities</div>
      </div>
    `;"""
    html = re.sub(banner_pattern, new_banner, html, count=1)

    # 9. Update Export rows
    export_pattern = r'("Fundamental Score \(.*?\)"[\s\S]*?"Confluence Tier": s\.master_category \|\| "",)'
    new_export = """"Fundamental Score (35%)": s.score,
        "ET Forecast Score (25%)": s.forecast_score || (s.forecast ? s.forecast.forecast_score : 50),
        "ET Prime Score (20%)": s.et_prime ? s.et_prime.stock_score : null,
        "Technical Score (20%)": s.tech_score,
        "Master Score (35/25/20/20)": s.master_score,
        "Confluence Tier": s.master_category || "","""
    html = re.sub(export_pattern, new_export, html, count=1)

    # 10. Update Bucket table & stats
    html = html.replace('🌟 Avg Master Quad', '🌟 Avg Master Score')
    html = html.replace('<th style="text-align:center;">Master Quad</th>', '<th style="text-align:center;">Master Score</th>')

    # Save HTML
    with open("Stock_Growth_and_Selection_Analyzer.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Saved Stock_Growth_and_Selection_Analyzer.html ({len(html)/(1024*1024):.2f} MB)")
    return True

if __name__ == "__main__":
    update_html()
