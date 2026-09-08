import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"
JSON_PATH = "scripts/combined_119_stocks.json"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    stocks = json.load(f)

print(f"Loaded {len(stocks)} stocks from {JSON_PATH}")

# 1. CSS Injection
SMART_FILTER_CSS = """
  /* Advanced Smart Multi-Filter & Screener Styling */
  .btn-smart-filter-toggle {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.16), rgba(245, 158, 11, 0.16));
    border: 1px solid rgba(56, 189, 248, 0.45);
    color: #38BDF8;
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    transition: all 0.2s ease;
  }
  .btn-smart-filter-toggle:hover {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.28), rgba(245, 158, 11, 0.28));
    border-color: #38BDF8;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
  }
  .btn-smart-filter-toggle.active {
    background: rgba(56, 189, 248, 0.25);
    border-color: #38BDF8;
    color: #FFFFFF;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
  }
  .smart-filter-badge {
    background: #F59E0B;
    color: #0B1120;
    font-size: 10.5px;
    font-weight: 900;
    padding: 1px 6px;
    border-radius: 10px;
    letter-spacing: -0.2px;
  }
  .smart-filter-panel {
    background: var(--bg-secondary);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 12px;
    padding: 18px 20px;
    margin-top: 14px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.4);
  }
  .smart-filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
  }
  .sf-title {
    font-size: 14.5px;
    font-weight: 800;
    color: #38BDF8;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .sf-subtitle {
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 3px;
  }
  .sf-actions {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .sf-match-summary {
    font-size: 12px;
    font-weight: 700;
    color: var(--accent-gold);
    background: rgba(245, 158, 11, 0.14);
    padding: 4px 10px;
    border-radius: 6px;
    border: 1px solid rgba(245, 158, 11, 0.3);
  }
  .sf-btn-clear, .sf-btn-close {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 5px 11px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }
  .sf-btn-clear:hover {
    color: var(--accent-red);
    border-color: var(--accent-red);
  }
  .sf-btn-close:hover {
    color: var(--text-primary);
    border-color: var(--text-secondary);
  }
  .sf-presets-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
    padding: 9px 13px;
    background: rgba(0, 0, 0, 0.22);
    border-radius: 8px;
    border: 1px dashed rgba(255, 255, 255, 0.12);
  }
  .sf-presets-label {
    font-size: 11.5px;
    font-weight: 800;
    color: var(--accent-gold);
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }
  .sf-preset-btn {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 5px 11px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .sf-preset-btn:hover {
    border-color: var(--accent-blue);
    color: var(--accent-blue);
    transform: translateY(-1px);
  }
  .sf-preset-btn.active {
    background: rgba(56, 189, 248, 0.22);
    border-color: #38BDF8;
    color: #38BDF8;
    font-weight: 800;
  }
  .sf-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 14px;
    margin-bottom: 12px;
  }
  .sf-box {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px 14px;
  }
  .sf-box-header {
    font-size: 11.5px;
    font-weight: 800;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 5px;
  }
  .sf-control-row {
    margin-bottom: 8px;
  }
  .sf-control-row:last-child {
    margin-bottom: 0;
  }
  .sf-control-row label {
    display: block;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 3px;
    font-weight: 600;
  }
  .sf-control-row select {
    width: 100%;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 11.5px;
    font-family: inherit;
    outline: none;
    cursor: pointer;
  }
  .sf-control-row select:focus {
    border-color: var(--accent-blue);
  }
  .sf-active-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    padding-top: 10px;
    border-top: 1px solid var(--border-color);
  }
  .sf-active-label {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
  }
  .sf-active-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  .sf-chip {
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #38BDF8;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .sf-chip-close {
    cursor: pointer;
    font-weight: 800;
    font-size: 12px;
    color: #F87171;
  }
  .sf-chip-close:hover {
    color: #EF4444;
  }

  /* Market Cap Badges */
  .mcap-tier-badge {
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 9.5px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    display: inline-block;
  }
  .tier-mega {
    background: rgba(168, 85, 247, 0.18);
    color: #C084FC;
    border: 1px solid rgba(168, 85, 247, 0.35);
  }
  .tier-large {
    background: rgba(59, 130, 246, 0.18);
    color: #60A5FA;
    border: 1px solid rgba(59, 130, 246, 0.35);
  }
  .tier-mid {
    background: rgba(245, 158, 11, 0.18);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.35);
  }
  .tier-small {
    background: rgba(20, 184, 166, 0.18);
    color: #2DD4BF;
    border: 1px solid rgba(20, 184, 166, 0.35);
  }
  .tier-preipo {
    background: rgba(244, 63, 94, 0.18);
    color: #FB7185;
    border: 1px solid rgba(244, 63, 94, 0.35);
  }
"""

if "btn-smart-filter-toggle" not in html:
    # Insert before .table-container
    idx = html.find(".table-container {")
    if idx != -1:
        html = html[:idx] + SMART_FILTER_CSS + "\n  " + html[idx:]
        print("Inserted Smart Filter CSS.")

# 2. Add Smart Filter Toggle Button and Panel HTML
SMART_FILTER_HTML = """
    <button class="btn-smart-filter-toggle" id="btnSmartFilterToggle" onclick="toggleSmartFilterPanel()" title="Toggle Advanced Multi-Condition Screener Panel">
      ⚡ Advanced Smart Multi-Filter <span id="smartFilterActiveCount" class="smart-filter-badge" style="display:none;">0</span> ▾
    </button>
"""

SMART_FILTER_PANEL_HTML = """
  <!-- ADVANCED SMART MULTI-CONDITION FILTER PANEL -->
  <div id="smartFilterPanel" class="smart-filter-panel" style="display:none;">
    <div class="smart-filter-header">
      <div>
        <div class="sf-title">⚡ Advanced Multi-Condition Smart Screener</div>
        <div class="sf-subtitle">Filter across fundamental, valuation, momentum, scale & target criteria simultaneously (AND logic)</div>
      </div>
      <div class="sf-actions">
        <span id="sfMatchSummary" class="sf-match-summary">Matching 119/119 Stocks</span>
        <button class="sf-btn-clear" onclick="clearAllSmartFilters()">↺ Clear Smart Filters</button>
        <button class="sf-btn-close" onclick="toggleSmartFilterPanel()">✕ Close</button>
      </div>
    </div>

    <!-- 1-Click Institutional Presets Bar -->
    <div class="sf-presets-bar">
      <span class="sf-presets-label">⚡ 1-Click Smart Presets:</span>
      <button class="sf-preset-btn" id="preset_lynch_garp" onclick="applySmartPreset('lynch_garp')" title="PEG <= 1.0, YoY PAT >= 20%, Funda >= 70">🎯 Peter Lynch GARP</button>
      <button class="sf-preset-btn" id="preset_alpha_leaders" onclick="applySmartPreset('alpha_leaders')" title="Master Score >= 88, Stage 2 Trend, Upside >= 15%">👑 Quad Alpha Leaders</button>
      <button class="sf-preset-btn" id="preset_hyper_growth" onclick="applySmartPreset('hyper_growth')" title="YoY PAT >= 50%, High Momentum RSI 55-72">⚡ Hyper-Growth Breakouts</button>
      <button class="sf-preset-btn" id="preset_deep_safety" onclick="applySmartPreset('deep_safety')" title="P/E <= 25, P/B <= 4.0, Upside >= 20%">🛡️ Deep Margin of Safety</button>
      <button class="sf-preset-btn" id="preset_stage2_dip" onclick="applySmartPreset('stage2_dip')" title="Stage 2 Trend, RSI < 48, Funda >= 70">💎 Stage-2 Dip Buys</button>
      <button class="sf-preset-btn" id="preset_bluechips" onclick="applySmartPreset('bluechips')" title="Market Cap >= 20k Cr, Master >= 80, Upside >= 10%">🏛️ Institutional Bluechips</button>
    </div>

    <!-- Multi-Condition Filter Grid -->
    <div class="sf-grid">
      <!-- Valuation Multiples Box -->
      <div class="sf-box">
        <div class="sf-box-header">📊 Valuation Multiples</div>
        <div class="sf-control-row">
          <label>Max P/E Multiple:</label>
          <select id="sf_max_pe" onchange="onSmartFilterChange()">
            <option value="any">Any P/E</option>
            <option value="15">&le; 15 (Deep Value)</option>
            <option value="25">&le; 25 (Reasonable Value)</option>
            <option value="40">&le; 40 (Moderate Quality)</option>
            <option value="60">&le; 60 (Growth Valuation)</option>
            <option value="80">&le; 80 (High Multiple)</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>Max P/B Multiple:</label>
          <select id="sf_max_pb" onchange="onSmartFilterChange()">
            <option value="any">Any P/B</option>
            <option value="2.0">&le; 2.0 (Low Book Multiple)</option>
            <option value="4.0">&le; 4.0 (Balanced Asset Base)</option>
            <option value="7.0">&le; 7.0 (Capital Efficient)</option>
            <option value="12.0">&le; 12.0 (High ROE Premium)</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>Max PEG Ratio:</label>
          <select id="sf_max_peg" onchange="onSmartFilterChange()">
            <option value="any">Any PEG</option>
            <option value="1.0">&le; 1.0 (Peter Lynch Undervalued)</option>
            <option value="1.5">&le; 1.5 (Fair Growth Value)</option>
            <option value="2.0">&le; 2.0 (Reasonable Expansion)</option>
            <option value="3.0">&le; 3.0 (Momentum Growth)</option>
          </select>
        </div>
      </div>

      <!-- Growth & Quality Box -->
      <div class="sf-box">
        <div class="sf-box-header">🚀 Growth & Financial Quality</div>
        <div class="sf-control-row">
          <label>Min YoY PAT Growth:</label>
          <select id="sf_min_pat_growth" onchange="onSmartFilterChange()">
            <option value="any">Any Growth</option>
            <option value="15">&ge; +15% (Solid Compounder)</option>
            <option value="20">&ge; +20% (High Growth)</option>
            <option value="25">&ge; +25% (High Expansion)</option>
            <option value="50">&ge; +50% (Hyper-Growth)</option>
            <option value="100">&ge; +100% (Doubling Earnings)</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>Min Profit Streaks:</label>
          <select id="sf_min_streak" onchange="onSmartFilterChange()">
            <option value="any">Any Streak</option>
            <option value="2">&ge; 2 Quarters</option>
            <option value="3">&ge; 3 Quarters</option>
            <option value="4">&ge; 4 Quarters</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>Min Funda Quality Score:</label>
          <select id="sf_min_funda" onchange="onSmartFilterChange()">
            <option value="any">Any Score</option>
            <option value="60">&ge; 60 (Healthy Fundamentals)</option>
            <option value="70">&ge; 70 (Strong Fundamentals)</option>
            <option value="80">&ge; 80 (Elite Financial Health)</option>
          </select>
        </div>
      </div>

      <!-- Technical & Momentum Box -->
      <div class="sf-box">
        <div class="sf-box-header">📈 Technicals & Momentum</div>
        <div class="sf-control-row">
          <label>14D RSI Range:</label>
          <select id="sf_rsi_zone" onchange="onSmartFilterChange()">
            <option value="any">Any RSI Zone</option>
            <option value="oversold">Oversold / Dip (&lt; 48)</option>
            <option value="bullish">Bullish Accumulation (50 - 65)</option>
            <option value="momentum">High Momentum (55 - 72)</option>
            <option value="extreme_oversold">Extreme Oversold (&lt; 35)</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>Trend Structure:</label>
          <select id="sf_trend" onchange="onSmartFilterChange()">
            <option value="any">Any Trend</option>
            <option value="stage2">Stage 2 Strong Uptrend Only</option>
            <option value="above_50dma">Trading Above 50 DMA</option>
            <option value="above_200dma">Trading Above 200 DMA</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>52W High Proximity:</label>
          <select id="sf_proximity_52w" onchange="onSmartFilterChange()">
            <option value="any">Any Distance</option>
            <option value="near_high_5">Within 5% of 52W High (Breakout Pivot)</option>
            <option value="near_high_12">Within 12% of 52W High</option>
            <option value="within_20">Within 20% of 52W High</option>
            <option value="pullback_20">Deep Pullback (&gt; 20% from High)</option>
          </select>
        </div>
      </div>

      <!-- Capital Scale & Forecast Box -->
      <div class="sf-box">
        <div class="sf-box-header">🏛️ Market Cap & Targets</div>
        <div class="sf-control-row">
          <label>Market Cap Tier (₹ Cr):</label>
          <select id="sf_mcap_tier" onchange="onSmartFilterChange()">
            <option value="any">Any Market Cap</option>
            <option value="mega_large">Mega & Large Cap (&ge; ₹20,000 Cr)</option>
            <option value="mega">Mega Cap (&ge; ₹1,00,000 Cr)</option>
            <option value="large">Large Cap (₹20k to ₹1L Cr)</option>
            <option value="mid">Mid Cap (₹5k to ₹20k Cr)</option>
            <option value="small">Small / Micro Cap (&lt; ₹5,000 Cr)</option>
            <option value="preipo">Pre-IPO Alpha</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>Min 1Y Forecast Upside:</label>
          <select id="sf_min_upside" onchange="onSmartFilterChange()">
            <option value="any">Any Target</option>
            <option value="10">&ge; +10% 1Y Upside</option>
            <option value="15">&ge; +15% 1Y Upside</option>
            <option value="20">&ge; +20% High Upside</option>
            <option value="35">&ge; +35% Substantial Target</option>
            <option value="50">&ge; +50% Multi-Bagger Target</option>
          </select>
        </div>
        <div class="sf-control-row">
          <label>Min Master Quad Score:</label>
          <select id="sf_min_master" onchange="onSmartFilterChange()">
            <option value="any">Any Master Score</option>
            <option value="75">&ge; 75 (High Conviction)</option>
            <option value="80">&ge; 80 (Top Tier Compounder)</option>
            <option value="85">&ge; 85 (Superior Strength)</option>
            <option value="88">&ge; 88 (🌟 Quad Alpha Leader)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Active Filter Badges Bar -->
    <div class="sf-active-bar" id="sfActiveBar" style="display:none;">
      <span class="sf-active-label">Active Conditions:</span>
      <div class="sf-active-tags" id="sfActiveTags"></div>
    </div>
  </div>
"""

# Insert toggle button right after <button class="btn-reset" onclick="resetFilters()">↺ Reset Filters</button>
target_btn = '<button class="btn-reset" onclick="resetFilters()">↺ Reset Filters</button>'
if target_btn in html and "btnSmartFilterToggle" not in html:
    html = html.replace(target_btn, target_btn + "\n" + SMART_FILTER_HTML)
    print("Inserted btnSmartFilterToggle.")

# Insert smart filter panel right after multi-filter-row closing tag
row_end_idx = html.find('</div>\n</div>\n\n<!-- Table View & Movable Column Toolbar -->')
if row_end_idx != -1 and "smartFilterPanel" not in html:
    html = html[:row_end_idx+6] + "\n" + SMART_FILTER_PANEL_HTML + html[row_end_idx+6:]
    print("Inserted smartFilterPanel HTML.")
elif "smartFilterPanel" not in html:
    # Alternative insertion before <!-- Table View & Movable Column Toolbar -->
    tb_idx = html.find('<!-- Table View & Movable Column Toolbar -->')
    if tb_idx != -1:
        html = html[:tb_idx] + SMART_FILTER_PANEL_HTML + "\n" + html[tb_idx:]
        print("Inserted smartFilterPanel HTML (fallback target).")

# 3. Update Table Header & Column View Counts
# Update "Full Master View (21)" -> "Full Master View (22)"
html = re.sub(r'Full Master View \(21\)', 'Full Master View (22)', html)
html = re.sub(r'Customize Columns \(<span id="visibleColCount">21</span>/21\)', 'Customize Columns (<span id="visibleColCount">22</span>/22)', html)

# Static thead: Add <th onclick="sortTable('mcap_cr')">Market Cap ↕</th> after Sector
target_th = '<th onclick="sortTable(\'sector\')">Sector ↕</th>'
new_th = '<th onclick="sortTable(\'sector\')">Sector ↕</th>\n        <th onclick="sortTable(\'mcap_cr\')">Market Cap ↕</th>'
if target_th in html and "sortTable('mcap_cr')" not in html:
    html = html.replace(target_th, new_th, 1)
    print("Inserted static thead Market Cap th.")

# 4. Replace rawData with combined_119_stocks.json
start_idx = html.find("const rawData =")
end_idx = html.find("let currentData =", start_idx)
if start_idx != -1 and end_idx != -1:
    json_str = json.dumps(stocks, ensure_ascii=False)
    html = html[:start_idx] + f"const rawData = {json_str};\n  " + html[end_idx:]
    print("Updated rawData in HTML with all 119 stocks containing accurate mcap_cr, shares_outstanding, mcap_tier!")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Part 1 (HTML/CSS/Data) complete.")
