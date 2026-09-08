import json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

def update_html_3pillar():
    print("==================================================================")
    print("=== REBUILDING HTML DASHBOARD: 3-PILLAR MASTER SCORE (NO MOOD) ===")
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
    print("✓ Successfully replaced rawData in HTML.")

    # 2. Update MASTER_COLUMN_DEFS: rename labels and remove mood_score
    col_defs_pattern = r"const MASTER_COLUMN_DEFS = \[[\s\S]*?\];"
    new_col_defs = """const MASTER_COLUMN_DEFS = [
    { id: 'bucket', label: '🧺 Bucket', sortKey: null, defaultOrder: 0 },
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 22 },
    { id: 'symbol', label: 'Symbol', sortKey: 'symbol', defaultOrder: 22 },
    { id: 'name', label: 'Company Name', sortKey: 'name', defaultOrder: 22 },
    { id: 'sector', label: 'Sector', sortKey: 'sector', defaultOrder: 22 },
    { id: 'mcap_cr', label: 'Market Cap', sortKey: 'mcap_cr', defaultOrder: 22 },
    { id: 'master_score', label: 'Master Score (3-Pillar)', sortKey: 'master_score', defaultOrder: 22 },
    { id: 'et_stock_score', label: 'ET Prime Score', sortKey: 'et_stock_score', defaultOrder: 22 },
    { id: 'confluence_tier', label: 'Confluence Tier', sortKey: null, defaultOrder: 22 },
    { id: 'forecast_upside', label: 'ET Potential Upside', sortKey: 'forecast_upside', defaultOrder: 22 },
    { id: 'mean_target', label: '1Y Target (₹)', sortKey: 'mean_target', defaultOrder: 22 },
    { id: 'consensus', label: 'Consensus', sortKey: 'consensus', defaultOrder: 22 },
    { id: 'score', label: 'Funda (40%)', sortKey: 'score', defaultOrder: 22 },
    { id: 'tech_score', label: 'Tech (35%)', sortKey: 'tech_score', defaultOrder: 22 },
    { id: 'forecast_score', label: 'ET Forecast (25%)', sortKey: 'forecast_score', defaultOrder: 22 },
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
    print("✓ Updated MASTER_COLUMN_DEFS with 3-Pillar weights (40% Funda, 35% Tech, 25% ET Forecast).")

    # 3. Add forecast_score renderer to cellRenderers if not present
    if "forecast_score:" not in html:
        target = "tech_score: (s) => `<td style=\"text-align:right; font-weight:600; color:var(--accent-blue);\">${s.tech_score}</td>`,"
        replacement = target + """
    forecast_score: (s) => `<td style="text-align:right; font-weight:700; color:#06B6D4;">${s.forecast_score || (s.forecast ? s.forecast.forecast_score : '-')}</td>`,"""
        html = html.replace(target, replacement, 1)
        print("✓ Added forecast_score to cellRenderers.")

    # 4. Add sortTable logic for forecast_score
    if "key === 'forecast_score'" not in html:
        target = "if (key === 'et_stock_score') {"
        replacement = """if (key === 'forecast_score') {
        valA = a.forecast_score !== undefined ? a.forecast_score : (a.forecast ? a.forecast.forecast_score : 0);
        valB = b.forecast_score !== undefined ? b.forecast_score : (b.forecast ? b.forecast.forecast_score : 0);
      } else if (key === 'et_stock_score') {"""
        html = html.replace(target, replacement, 1)
        print("✓ Added forecast_score to sortTable.")

    # 5. Clean localStorage activeColumns to remove mood_score
    target = "activeColumns = parsed.filter(id => COLUMN_MAP[id]);"
    replacement = "activeColumns = parsed.filter(id => COLUMN_MAP[id] && id !== 'mood_score');"
    html = html.replace(target, replacement, 1)
    print("✓ Filtered out mood_score from localStorage activeColumns.")

    # 6. Update Stat Card for Mood -> Top ET Prime
    old_mood_card = """  <div class="stat-card orange">
    <div class="stat-label">🔥 Euphoric Market Mood</div>
    <div class="stat-val" id="stat-mood-kings">0</div>
    <div class="stat-sub">Investor Sentiment &ge; 90/100</div>
  </div>"""
    new_et_prime_card = """  <div class="stat-card purple">
    <div class="stat-label">🎯 Top ET Prime Score</div>
    <div class="stat-val" id="stat-et-prime-kings">0</div>
    <div class="stat-sub">Refinitiv Score &ge; 8/10</div>
  </div>"""
    html = html.replace(old_mood_card, new_et_prime_card, 1)
    print("✓ Replaced Mood stat card with Top ET Prime Score stat card.")

    # 7. Update renderTable stat counter calculation
    html = html.replace(
        "document.getElementById('stat-mood-kings').innerText = rawData.filter(x => x.mood_score >= 90).length;",
        "document.getElementById('stat-et-prime-kings').innerText = rawData.filter(x => x.et_prime && x.et_prime.stock_score >= 8).length;"
    )

    # 8. Update Filter Pills: replace Mood pills with ET Prime filter pills
    old_pills = """  <button class="filter-pill" onclick="setFilterPill('euphoric_mood', this)">🔥 Euphoric Mood (&ge; 90)</button>
  <button class="filter-pill" onclick="setFilterPill('positive_mood', this)">🟢 Positive Mood (75-89)</button>"""
    new_pills = """  <button class="filter-pill" onclick="setFilterPill('et_prime_top', this)">🎯 Top ET Prime (&ge; 8/10)</button>
  <button class="filter-pill" onclick="setFilterPill('et_prime_positive', this)">⚡ High ET Prime (6-7/10)</button>"""
    html = html.replace(old_pills, new_pills, 1)

    # Update Quad Leaders pill label
    html = html.replace("🌟 Quad Leaders (&ge; 88)", "🌟 Tri-Pillar Leaders (&ge; 88)")

    # 9. Update setFilterPill in applyAllFilters
    html = html.replace(
        "if (currentPill === 'euphoric_mood' && s.mood_score < 90) return false;\n      if (currentPill === 'positive_mood' && (s.mood_score < 75 || s.mood_score >= 90)) return false;",
        "if (currentPill === 'et_prime_top' && (!s.et_prime || s.et_prime.stock_score < 8)) return false;\n      if (currentPill === 'et_prime_positive' && (!s.et_prime || s.et_prime.stock_score < 6 || s.et_prime.stock_score >= 8)) return false;"
    )
    print("✓ Updated filter pills for ET Prime scores.")

    # 10. Update modalScoreBanner: Remove Mood (20%) and set clean 3-Pillar display
    # Find modalScoreBanner assignment
    banner_pattern = r"document\.getElementById\('modalScoreBanner'\)\.innerHTML = `[\s\S]*?`;"
    new_banner = """document.getElementById('modalScoreBanner').innerHTML = `
      <div class="score-item" style="border-left:3px solid var(--accent-gold);">
        <div class="score-lbl">Master Tri-Score</div>
        <div class="score-num" style="color:var(--accent-gold);">${stock.master_score}/100</div>
        <div style="font-size:11px; color:var(--text-muted);">${stock.master_category.split('(')[0]}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">Fundamental (40%)</div>
        <div class="score-num" style="color:var(--accent-green);">${stock.score}</div>
        <div style="font-size:11px; color:var(--text-muted);">Streak Rev:${stock.streak_rev} / PAT:${stock.streak_pat}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">Technical (35%)</div>
        <div class="score-num" style="color:var(--accent-blue);">${stock.tech_score}</div>
        <div style="font-size:11px; color:var(--text-muted);">${t.trend ? t.trend.split(' ')[1] || 'Trend' : '-'}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">ET Forecast (25%)</div>
        <div class="score-num" style="color:#06B6D4;">${f.forecast_score}</div>
        <div style="font-size:11px; color:var(--text-muted);">${f.consensus_rating || 'NR'} (${f.num_analysts || 0} Analysts)</div>
      </div>
      <div class="score-item" style="border-left: 2px solid rgba(168, 85, 247, 0.45);">
        <div class="score-lbl">ET Prime Score</div>
        <div class="score-num" style="color:#C084FC;">${(ep.stock_score !== null && ep.stock_score !== undefined) ? ep.stock_score + '/10' : 'NR'}</div>
        <div style="font-size:11px; color:var(--text-muted);">${ep.score_outlook || 'Refinitiv Score'}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">Master Rank</div>
        <div class="score-num" style="color:var(--accent-gold);">#${stock.master_rank}</div>
        <div style="font-size:11px; color:var(--text-muted);">of 424 Watchlist Equities</div>
      </div>
    `;"""
    html = re.sub(banner_pattern, new_banner, html, count=1)
    print("✓ Updated modalScoreBanner: Mood completely removed, 3 Pillars (Funda 40%, Tech 35%, ET FC 25%) displayed.")

    # 11. Remove tab-mood button from terminal modal tabs
    html = html.replace('<button class="t-tab" onclick="switchTerminalTab(\'tab-mood\', this)">📰 Market Mood & Policy Tailwinds</button>', '')
    print("✓ Removed Market Mood tab button from terminal modal.")

    # Write updated HTML
    with open("Stock_Growth_and_Selection_Analyzer.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"==================================================================")
    print(f"✓ Saved Stock_Growth_and_Selection_Analyzer.html ({len(html)/(1024*1024):.2f} MB)")
    print("==================================================================")
    return True

if __name__ == "__main__":
    update_html_3pillar()
