import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update MASTER_COLUMN_DEFS to include bucket as first column
old_defs = """  const MASTER_COLUMN_DEFS = [
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 0 },"""

new_defs = """  const MASTER_COLUMN_DEFS = [
    { id: 'bucket', label: '🧺 Bucket', sortKey: null, defaultOrder: 0 },
    { id: 'master_rank', label: 'Rank', sortKey: 'master_rank', defaultOrder: 1 },"""

if old_defs in html:
    html = html.replace(old_defs, new_defs, 1)
    # Renumber subsequent defaultOrders
    for order in range(1, 22):
        html = re.sub(rf"defaultOrder:\s*{order}\s*}}", f"defaultOrder: {order+1} }}", html)
    print("Updated MASTER_COLUMN_DEFS with bucket column.")

# 2. Update COLUMN_PRESETS
old_presets = """  const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['master_rank', 'symbol', 'mcap_cr', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'today_pb', 'today_peg', 'rsi', 'sector', 'name', 'action'],
    alpha: ['master_rank', 'symbol', 'mcap_cr', 'master_score', 'confluence_tier', 'forecast_upside', 'score', 'tech_score', 'mood_score', 'today_price', 'today_pe', 'today_peg', 'action'],
    forecast: ['master_rank', 'symbol', 'mcap_cr', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };"""

new_presets = """  const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['bucket', 'master_rank', 'symbol', 'mcap_cr', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'today_pb', 'today_peg', 'rsi', 'sector', 'name', 'action'],
    alpha: ['bucket', 'master_rank', 'symbol', 'mcap_cr', 'master_score', 'confluence_tier', 'forecast_upside', 'score', 'tech_score', 'mood_score', 'today_price', 'today_pe', 'today_peg', 'action'],
    forecast: ['bucket', 'master_rank', 'symbol', 'mcap_cr', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };"""

if old_presets in html:
    html = html.replace(old_presets, new_presets, 1)
    print("Updated COLUMN_PRESETS with bucket.")

# 3. LocalStorage migration
old_ls = """        if (!activeColumns.includes('mcap_cr')) {
          const secIdx = activeColumns.indexOf('sector');
          if (secIdx !== -1) activeColumns.splice(secIdx + 1, 0, 'mcap_cr');
          else activeColumns.push('mcap_cr');
        }"""

new_ls = """        if (!activeColumns.includes('mcap_cr')) {
          const secIdx = activeColumns.indexOf('sector');
          if (secIdx !== -1) activeColumns.splice(secIdx + 1, 0, 'mcap_cr');
          else activeColumns.push('mcap_cr');
        }
        if (!activeColumns.includes('bucket')) {
          activeColumns.unshift('bucket');
        }"""

if old_ls in html:
    html = html.replace(old_ls, new_ls, 1)
    print("Updated localStorage migration for bucket column.")

# 4. Insert cellRenderers.bucket
old_cell_anchor = """  const cellRenderers = {
    master_rank: (s, isSticky) => `<td style="font-weight:800; text-align:center;" class="${isSticky ? 'sticky-col-rank' : ''}">#${s.master_rank}</td>`,"""

new_cell_anchor = """  const cellRenderers = {
    bucket: (s) => {
      const inBucket = bucketSet.has(s.symbol);
      return `<td style="text-align:center;" onclick="event.stopPropagation();">
        <label style="cursor:pointer; display:inline-flex; align-items:center; justify-content:center; width:100%; height:100%;">
          <input type="checkbox" class="bucket-cb" id="bucket-cb-${s.symbol}" ${inBucket ? 'checked' : ''} onchange="toggleStockBucket('${s.symbol}', this.checked)" title="${inBucket ? 'In Bucket (click to remove)' : 'Add to Bucket'}">
        </label>
      </td>`;
    },
    master_rank: (s, isSticky) => `<td style="font-weight:800; text-align:center;" class="${isSticky ? 'sticky-col-rank' : ''}">#${s.master_rank}</td>`,"""

if old_cell_anchor in html and "bucket: (s) =>" not in html:
    html = html.replace(old_cell_anchor, new_cell_anchor, 1)
    print("Inserted cellRenderers.bucket.")

# 5. Update renderTableHeader for bucket checkbox
old_th_build = """    visibleCols.forEach((colId, idx) => {
      const colDef = COLUMN_MAP[colId];
      if (!colDef) return;"""

new_th_build = """    visibleCols.forEach((colId, idx) => {
      const colDef = COLUMN_MAP[colId];
      if (!colDef) return;

      if (colId === 'bucket') {
        const allVisibleSelected = currentData.length > 0 && currentData.every(s => bucketSet.has(s.symbol));
        trHtml += `
          <th class="draggable-th" data-col-id="bucket" data-col-index="${idx}" style="text-align:center; min-width:65px;" title="Drag to move | Select all in Bucket">
            <span class="drag-handle" title="Drag to reorder">⠿</span>
            <input type="checkbox" id="selectAllBucketCheckbox" ${allVisibleSelected ? 'checked' : ''} onchange="toggleSelectAllVisibleBucket(this.checked)" title="Select/Deselect all visible in Bucket" style="cursor:pointer; transform:scale(1.2); accent-color:#38BDF8; vertical-align:middle;">
            <span style="font-size:11px; margin-left:3px; vertical-align:middle;">🧺</span>
          </th>`;
        return;
      }"""

if old_th_build in html and "colId === 'bucket'" not in html:
    html = html.replace(old_th_build, new_th_build, 1)
    print("Updated renderTableHeader to handle bucket column.")

# 6. Update renderTable for row-in-bucket class and empty state
old_tr_create = """    data.forEach((s, idx) => {
      const tr = document.createElement('tr');
      const lm = s.live_movement || {};"""

new_tr_create = """    if (currentPill === 'bucket' && data.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td colspan="${visibleCols.length}" style="text-align:center; padding:40px 20px;">
          <div style="font-size:36px; margin-bottom:10px;">🧺</div>
          <div style="font-size:16px; font-weight:800; color:var(--text-primary); margin-bottom:6px;">Your Bucket is Currently Empty</div>
          <div style="font-size:12px; color:var(--text-muted); max-width:440px; margin:0 auto 14px auto;">
            Click the 🧺 checkboxes in the table to add stocks to your personalized bucket.
          </div>
          <button class="btn-bucket-sub" onclick="addAllFilteredToBucket()" style="padding:6px 14px; font-size:12px; background:var(--accent-blue); color:#0B1120; border:none; font-weight:800; border-radius:6px; cursor:pointer;">
            ➕ Add All 119 Watchlist Stocks to Bucket
          </button>
        </td>`;
      tbody.appendChild(tr);
      return;
    }

    data.forEach((s, idx) => {
      const tr = document.createElement('tr');
      if (bucketSet.has(s.symbol)) tr.classList.add('row-in-bucket');
      const lm = s.live_movement || {};"""

if old_tr_create in html:
    html = html.replace(old_tr_create, new_tr_create, 1)
    print("Updated renderTable for row-in-bucket and empty state.")

# 7. Update applyAllFilters for bucket pill and counters
old_pill_rule = "      if (currentPill === 'small_pre_ipo' && (!s.mcap.includes('Small') && !s.symbol.includes('Pre-IPO'))) return false;"

new_pill_rule = """      if (currentPill === 'small_pre_ipo' && (!s.mcap.includes('Small') && !s.symbol.includes('Pre-IPO'))) return false;
      if (currentPill === 'bucket' && !bucketSet.has(s.symbol)) return false;"""

if old_pill_rule in html:
    html = html.replace(old_pill_rule, new_pill_rule, 1)
    print("Added bucket pill rule to applyAllFilters.")

old_filter_end = """    currentData = filtered;
    renderTable(currentData);
    document.getElementById('matchCounter').innerText = `Showing ${currentData.length} of ${rawData.length} Stocks`;"""

new_filter_end = """    currentData = filtered;
    renderTable(currentData);
    document.getElementById('matchCounter').innerText = `Showing ${currentData.length} of ${rawData.length} Stocks`;
    const bfc = document.getElementById('barFilteredCount');
    if (bfc) bfc.innerText = currentData.length;
    const bcc = document.getElementById('btnCsvCount');
    if (bcc) bcc.innerText = currentData.length;
    updateBucketUI();"""

if old_filter_end in html:
    html = html.replace(old_filter_end, new_filter_end, 1)
    print("Updated applyAllFilters counter and updateBucketUI call.")

# 8. Update renderActiveTerminalStock to sync modal bucket button
old_modal_sync = "    document.getElementById('modalScoreBanner').innerHTML ="
new_modal_sync = """    updateModalBucketButton(stock.symbol);
    document.getElementById('modalScoreBanner').innerHTML ="""

if old_modal_sync in html:
    html = html.replace(old_modal_sync, new_modal_sync, 1)
    print("Updated renderActiveTerminalStock to sync modal bucket button.")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Step 3 (JS table integration) complete.")
