import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update MASTER_COLUMN_DEFS
old_defs = """  const MASTER_COLUMN_DEFS = [
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 0 },
    { id: 'symbol', label: 'Symbol', sortKey: 'symbol', defaultOrder: 1 },
    { id: 'name', label: 'Company Name', sortKey: 'name', defaultOrder: 2 },
    { id: 'sector', label: 'Sector', sortKey: 'sector', defaultOrder: 3 },
    { id: 'master_score', label: 'Master Quad', sortKey: 'master_score', defaultOrder: 4 },
    { id: 'confluence_tier', label: 'Confluence Tier', sortKey: null, defaultOrder: 5 },
    { id: 'forecast_upside', label: 'Forecast Upside', sortKey: 'forecast_upside', defaultOrder: 6 },
    { id: 'mean_target', label: '1Y Target (₹)', sortKey: 'mean_target', defaultOrder: 7 },
    { id: 'consensus', label: 'Consensus', sortKey: 'consensus', defaultOrder: 8 },
    { id: 'score', label: 'Funda (30%)', sortKey: 'score', defaultOrder: 9 },
    { id: 'tech_score', label: 'Tech (30%)', sortKey: 'tech_score', defaultOrder: 10 },
    { id: 'mood_score', label: 'Mood (20%)', sortKey: 'mood_score', defaultOrder: 11 },
    { id: 'today_price', label: 'Live CMP (₹)', sortKey: 'today_price', defaultOrder: 12 },
    { id: 'day_change_pct', label: 'Daily Move (1D)', sortKey: 'day_change_pct', defaultOrder: 13 },
    { id: 'week_change_pct', label: 'Weekly Move (1W)', sortKey: 'week_change_pct', defaultOrder: 14 },
    { id: 'today_pe', label: 'P/E', sortKey: 'today_pe', defaultOrder: 15 },
    { id: 'today_pb', label: 'P/B', sortKey: 'today_pb', defaultOrder: 16 },
    { id: 'today_peg', label: 'PEG', sortKey: 'today_peg', defaultOrder: 17 },
    { id: 'rsi', label: '14D RSI', sortKey: 'rsi', defaultOrder: 18 },
    { id: 'quick_links', label: 'Quick Live', sortKey: null, defaultOrder: 19 },
    { id: 'action', label: 'Action', sortKey: null, defaultOrder: 20 }
  ];"""

new_defs = """  const MASTER_COLUMN_DEFS = [
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 0 },
    { id: 'symbol', label: 'Symbol', sortKey: 'symbol', defaultOrder: 1 },
    { id: 'name', label: 'Company Name', sortKey: 'name', defaultOrder: 2 },
    { id: 'sector', label: 'Sector', sortKey: 'sector', defaultOrder: 3 },
    { id: 'mcap_cr', label: 'Market Cap', sortKey: 'mcap_cr', defaultOrder: 4 },
    { id: 'master_score', label: 'Master Quad', sortKey: 'master_score', defaultOrder: 5 },
    { id: 'confluence_tier', label: 'Confluence Tier', sortKey: null, defaultOrder: 6 },
    { id: 'forecast_upside', label: 'Forecast Upside', sortKey: 'forecast_upside', defaultOrder: 7 },
    { id: 'mean_target', label: '1Y Target (₹)', sortKey: 'mean_target', defaultOrder: 8 },
    { id: 'consensus', label: 'Consensus', sortKey: 'consensus', defaultOrder: 9 },
    { id: 'score', label: 'Funda (30%)', sortKey: 'score', defaultOrder: 10 },
    { id: 'tech_score', label: 'Tech (30%)', sortKey: 'tech_score', defaultOrder: 11 },
    { id: 'mood_score', label: 'Mood (20%)', sortKey: 'mood_score', defaultOrder: 12 },
    { id: 'today_price', label: 'Live CMP (₹)', sortKey: 'today_price', defaultOrder: 13 },
    { id: 'day_change_pct', label: 'Daily Move (1D)', sortKey: 'day_change_pct', defaultOrder: 14 },
    { id: 'week_change_pct', label: 'Weekly Move (1W)', sortKey: 'week_change_pct', defaultOrder: 15 },
    { id: 'today_pe', label: 'P/E', sortKey: 'today_pe', defaultOrder: 16 },
    { id: 'today_pb', label: 'P/B', sortKey: 'today_pb', defaultOrder: 17 },
    { id: 'today_peg', label: 'PEG', sortKey: 'today_peg', defaultOrder: 18 },
    { id: 'rsi', label: '14D RSI', sortKey: 'rsi', defaultOrder: 19 },
    { id: 'quick_links', label: 'Quick Live', sortKey: null, defaultOrder: 20 },
    { id: 'action', label: 'Action', sortKey: null, defaultOrder: 21 }
  ];"""

if old_defs in html:
    html = html.replace(old_defs, new_defs)
    print("Updated MASTER_COLUMN_DEFS.")

# 2. Update COLUMN_PRESETS
old_presets = """  const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['master_rank', 'symbol', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'today_pb', 'today_peg', 'rsi', 'sector', 'name', 'action'],
    alpha: ['master_rank', 'symbol', 'master_score', 'confluence_tier', 'forecast_upside', 'score', 'tech_score', 'mood_score', 'today_price', 'today_pe', 'today_peg', 'action'],
    forecast: ['master_rank', 'symbol', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };"""

new_presets = """  const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['master_rank', 'symbol', 'mcap_cr', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'today_pb', 'today_peg', 'rsi', 'sector', 'name', 'action'],
    alpha: ['master_rank', 'symbol', 'mcap_cr', 'master_score', 'confluence_tier', 'forecast_upside', 'score', 'tech_score', 'mood_score', 'today_price', 'today_pe', 'today_peg', 'action'],
    forecast: ['master_rank', 'symbol', 'mcap_cr', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };"""

if old_presets in html:
    html = html.replace(old_presets, new_presets)
    print("Updated COLUMN_PRESETS.")

# 3. Update localStorage column migration
old_ls_mig = """        if (!activeColumns.includes('today_peg')) {
          const pbIdx = activeColumns.indexOf('today_pb');
          if (pbIdx !== -1) activeColumns.splice(pbIdx + 1, 0, 'today_peg');
          else activeColumns.push('today_peg');
        }"""

new_ls_mig = """        if (!activeColumns.includes('today_peg')) {
          const pbIdx = activeColumns.indexOf('today_pb');
          if (pbIdx !== -1) activeColumns.splice(pbIdx + 1, 0, 'today_peg');
          else activeColumns.push('today_peg');
        }
        if (!activeColumns.includes('mcap_cr')) {
          const secIdx = activeColumns.indexOf('sector');
          if (secIdx !== -1) activeColumns.splice(secIdx + 1, 0, 'mcap_cr');
          else activeColumns.push('mcap_cr');
        }"""

if old_ls_mig in html:
    html = html.replace(old_ls_mig, new_ls_mig)
    print("Updated localStorage migration logic for mcap_cr.")

# 4. Insert cellRenderers.mcap_cr
old_renderer_anchor = """    sector: (s) => `<td style="font-size:12.5px;"><strong style="color:var(--text-primary); font-size:12px;">${s.sector}</strong><br><span style="color:var(--text-muted); font-size:10.5px;">${s.sub_industry || ""}</span></td>`,"""

new_renderer_anchor = """    sector: (s) => `<td style="font-size:12.5px;"><strong style="color:var(--text-primary); font-size:12px;">${s.sector}</strong><br><span style="color:var(--text-muted); font-size:10.5px;">${s.sub_industry || ""}</span></td>`,
    mcap_cr: (s) => {
      const mcap = s.mcap_cr;
      if (mcap === null || mcap === undefined || mcap <= 0) {
        return `<td style="text-align:right; color:var(--text-muted); font-size:12px;">-</td>`;
      }
      let tier = s.mcap_tier || 'Mid Cap';
      let tierClass = 'tier-mid';
      if (tier === 'Mega Cap') tierClass = 'tier-mega';
      else if (tier === 'Large Cap') tierClass = 'tier-large';
      else if (tier === 'Small Cap') tierClass = 'tier-small';
      else if (tier === 'Pre-IPO') tierClass = 'tier-preipo';
      
      const mcapFmt = '₹' + Math.round(mcap).toLocaleString('en-IN') + ' Cr';
      return `<td style="text-align:right;" id="mcap-cell-${s.symbol}">
        <span class="mcap-val" style="font-weight:700; font-family:'JetBrains Mono', monospace; font-size:12.5px; color:var(--text-primary);">${mcapFmt}</span>
        <div style="font-size:10px; margin-top:2px;"><span class="mcap-tier-badge ${tierClass}">${tier}</span></div>
      </td>`;
    },"""

if old_renderer_anchor in html and "mcap_cr: (s) =>" not in html:
    html = html.replace(old_renderer_anchor, new_renderer_anchor)
    print("Inserted cellRenderers.mcap_cr.")

# 5. Update sortTable for mcap_cr
old_sort_anchor = """      } else if (key === 'today_peg') {
        valA = typeof a.today_peg === 'number' ? a.today_peg : (dir === 'asc' ? 999999 : -999999);
        valB = typeof b.today_peg === 'number' ? b.today_peg : (dir === 'asc' ? 999999 : -999999);"""

new_sort_anchor = """      } else if (key === 'today_peg') {
        valA = typeof a.today_peg === 'number' ? a.today_peg : (dir === 'asc' ? 999999 : -999999);
        valB = typeof b.today_peg === 'number' ? b.today_peg : (dir === 'asc' ? 999999 : -999999);
      } else if (key === 'mcap_cr') {
        valA = typeof a.mcap_cr === 'number' ? a.mcap_cr : (dir === 'asc' ? 999999999 : -999999999);
        valB = typeof b.mcap_cr === 'number' ? b.mcap_cr : (dir === 'asc' ? 999999999 : -999999999);"""

if old_sort_anchor in html and "key === 'mcap_cr'" not in html:
    html = html.replace(old_sort_anchor, new_sort_anchor)
    print("Updated sortTable for mcap_cr.")

# 6. Update simulateLiveMicroTicks for mcap dynamic update
old_tick_calc = """        // Recompute PEG if growth rate available
        if (s.peg_growth_rate && s.peg_growth_rate > 0 && typeof s.today_pe === 'number' && s.today_pe > 0) {
          s.today_peg = Math.round((s.today_pe / s.peg_growth_rate) * 100) / 100;
        }"""

new_tick_calc = """        // Recompute PEG if growth rate available
        if (s.peg_growth_rate && s.peg_growth_rate > 0 && typeof s.today_pe === 'number' && s.today_pe > 0) {
          s.today_peg = Math.round((s.today_pe / s.peg_growth_rate) * 100) / 100;
        }
        // Recompute Market Cap dynamically from latest CMP and shares_outstanding
        if (s.shares_outstanding && s.shares_outstanding > 0) {
          s.mcap_cr = Math.round((newPrice * s.shares_outstanding) / 10000000.0 * 10) / 10;
        }"""

if old_tick_calc in html:
    html = html.replace(old_tick_calc, new_tick_calc)
    print("Updated simulateLiveMicroTicks calculation for mcap_cr.")

old_dom_update = """          const pegCell = document.getElementById(`peg-cell-${s.symbol}`);
          if (pegCell && s.today_peg) {
            const pegSpan = pegCell.querySelector('span');
            if (pegSpan) pegSpan.innerText = s.today_peg.toFixed(2);
          }"""

new_dom_update = """          const pegCell = document.getElementById(`peg-cell-${s.symbol}`);
          if (pegCell && s.today_peg) {
            const pegSpan = pegCell.querySelector('span');
            if (pegSpan) pegSpan.innerText = s.today_peg.toFixed(2);
          }
          const mcapCell = document.getElementById(`mcap-cell-${s.symbol}`);
          if (mcapCell && s.mcap_cr) {
            const mcapVal = mcapCell.querySelector('.mcap-val');
            if (mcapVal) mcapVal.innerText = '₹' + Math.round(s.mcap_cr).toLocaleString('en-IN') + ' Cr';
          }"""

if old_dom_update in html:
    html = html.replace(old_dom_update, new_dom_update)
    print("Updated simulateLiveMicroTicks DOM update for mcap_cr.")

# 7. Update exportFilteredCSV
old_csv_hdr = """"Master Rank", "Symbol", "Company Name", "Sector", "Market Cap","""
new_csv_hdr = """"Master Rank", "Symbol", "Company Name", "Sector", "Market Cap Tier", "Market Cap (INR Cr)","""

if old_csv_hdr in html:
    html = html.replace(old_csv_hdr, new_csv_hdr)
    print("Updated CSV export headers.")

old_csv_row = """        s.master_rank,
        `"${s.symbol}"`,
        `"${s.name}"`,
        `"${s.sector}"`,
        `"${s.mcap}"`,`"""

new_csv_row = """        s.master_rank,
        `"${s.symbol}"`,
        `"${s.name}"`,
        `"${s.sector}"`,
        `"${s.mcap_tier || s.mcap}"`,
        s.mcap_cr || '',"""

if old_csv_row in html:
    html = html.replace(old_csv_row, new_csv_row)
    print("Updated CSV export row values.")

# 8. Update renderActiveTerminalStock modal tags
old_tags_js = """    document.getElementById('modalTags').innerHTML = `
      <span class="badge badge-compounder">${stock.sector}</span>
      <span class="badge badge-forecast">${stock.mcap}</span>
      <span class="badge badge-triple">Master Rank #${stock.master_rank}</span>
      ${stock.sub_industry ? `<span class="badge badge-dip" style="font-size:11px;">${stock.sub_industry}</span>` : ''}
    `;"""

new_tags_js = """    const mcapDisplay = stock.mcap_cr ? `₹${Math.round(stock.mcap_cr).toLocaleString('en-IN')} Cr` : stock.mcap;
    const mcapTag = stock.mcap_cr ? `${stock.mcap_tier || stock.mcap} (${mcapDisplay})` : stock.mcap;
    document.getElementById('modalTags').innerHTML = `
      <span class="badge badge-compounder">${stock.sector}</span>
      <span class="badge badge-forecast">${mcapTag}</span>
      <span class="badge badge-triple">Master Rank #${stock.master_rank}</span>
      ${stock.sub_industry ? `<span class="badge badge-dip" style="font-size:11px;">${stock.sub_industry}</span>` : ''}
    `;"""

if old_tags_js in html:
    html = html.replace(old_tags_js, new_tags_js)
    print("Updated terminal modal tags with market cap.")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Part 2 (Market Cap integration) complete.")
