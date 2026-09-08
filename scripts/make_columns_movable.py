import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

def make_columns_movable():
    html_path = "Stock_Growth_and_Selection_Analyzer.html"

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    print(f"Loaded {html_path} ({len(html)} bytes)")

    # 1. CSS FOR DRAGGABLE COLUMNS, VIEW TOOLBAR & MODAL
    toolbar_css = """
  /* ==========================================================================
     MOVABLE COLUMNS, VIEW PRESETS & COLUMN MANAGER STYLES
     ========================================================================== */
  .table-view-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 10px 18px;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 14px;
  }
  .view-presets-group {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .toolbar-lbl {
    font-size: 11.5px;
    font-weight: 800;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .btn-view-preset {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn-view-preset:hover {
    color: var(--accent-blue);
    border-color: var(--accent-blue);
  }
  .btn-view-preset.active {
    background: rgba(56, 189, 248, 0.16);
    border-color: var(--accent-blue);
    color: var(--accent-blue);
    font-weight: 800;
  }
  .column-actions-group {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .btn-col-manager, .btn-col-reset {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;
  }
  .btn-col-manager:hover {
    border-color: var(--accent-gold);
    color: var(--accent-gold);
  }
  .btn-col-reset:hover {
    border-color: var(--accent-red);
    color: var(--accent-red);
  }
  .drag-hint {
    font-size: 11px;
    color: var(--text-muted);
    font-style: italic;
  }

  /* Table Container adjust with toolbar */
  .table-container {
    border-top-left-radius: 0 !important;
    border-top-right-radius: 0 !important;
  }

  /* Draggable TH styles */
  th.draggable-th {
    cursor: grab !important;
    position: relative;
    user-select: none;
    transition: background-color 0.15s, border 0.15s, transform 0.1s;
    white-space: nowrap;
  }
  th.draggable-th:active {
    cursor: grabbing !important;
  }
  th.draggable-th.dragging {
    opacity: 0.35;
    background-color: var(--bg-card-hover) !important;
  }
  th.draggable-th.drag-over-left {
    border-left: 3px solid var(--accent-blue) !important;
    background-color: rgba(56, 189, 248, 0.15) !important;
  }
  th.draggable-th.drag-over-right {
    border-right: 3px solid var(--accent-blue) !important;
    background-color: rgba(56, 189, 248, 0.15) !important;
  }
  .drag-handle {
    font-size: 11px;
    color: var(--text-muted);
    margin-right: 5px;
    opacity: 0.65;
    cursor: grab;
    display: inline-block;
  }
  th.draggable-th:hover .drag-handle {
    opacity: 1;
    color: var(--accent-blue);
  }

  /* Sticky First Two Columns for Smooth Horizontal Scanning */
  th.sticky-col-rank, td.sticky-col-rank {
    position: sticky;
    left: 0;
    z-index: 3;
    background-color: var(--table-header-bg);
  }
  tbody td.sticky-col-rank {
    background-color: var(--bg-card);
  }
  tbody tr:hover td.sticky-col-rank {
    background-color: var(--bg-card-hover);
  }

  th.sticky-col-symbol, td.sticky-col-symbol {
    position: sticky;
    left: 55px;
    z-index: 3;
    background-color: var(--table-header-bg);
    box-shadow: 3px 0 8px rgba(0, 0, 0, 0.18);
  }
  tbody td.sticky-col-symbol {
    background-color: var(--bg-card);
  }
  tbody tr:hover td.sticky-col-symbol {
    background-color: var(--bg-card-hover);
  }

  /* Column Customizer Modal */
  .col-modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.65);
    z-index: 999999;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
    animation: modalFadeIn 0.2s ease-out;
  }
  .col-modal-card {
    background: var(--modal-card-bg);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    width: 100%;
    max-width: 580px;
    box-shadow: var(--card-shadow);
    display: flex;
    flex-direction: column;
    max-height: 85vh;
  }
  .col-modal-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .col-modal-header h3 {
    font-size: 16px;
    font-weight: 800;
    color: var(--text-primary);
  }
  .col-modal-body {
    padding: 16px 20px;
    overflow-y: auto;
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .col-checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
    cursor: pointer;
    padding: 7px 10px;
    border-radius: 6px;
    background: var(--bg-secondary);
    border: 1px solid transparent;
    transition: all 0.15s;
  }
  .col-checkbox-label:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent-blue);
  }
  .col-checkbox-label input {
    accent-color: var(--accent-blue);
    width: 15px;
    height: 15px;
    cursor: pointer;
  }
  .col-modal-footer {
    padding: 14px 20px;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .btn-col-action {
    background: var(--accent-blue);
    border: 1px solid var(--accent-blue);
    color: #0B1120;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
  }
"""

    if "/* ==========================================================================\n     MOVABLE COLUMNS, VIEW PRESETS & COLUMN MANAGER STYLES" not in html:
        html = html.replace("</style>", toolbar_css + "\n</style>", 1)
        print("Injected movable columns CSS styles.")

    # 2. INSERT TOOLBAR ABOVE MAIN TABLE
    toolbar_html = """<!-- Table View & Movable Column Toolbar -->
<div class="table-view-toolbar">
  <div class="view-presets-group">
    <span class="toolbar-lbl">👁️ Table Views:</span>
    <button class="btn-view-preset active" id="viewPresetAll" onclick="setColumnPreset('all')">📋 Full Master View (19)</button>
    <button class="btn-view-preset" id="viewPresetPrice" onclick="setColumnPreset('price')">⚡ Live Price & Valuation (10)</button>
    <button class="btn-view-preset" id="viewPresetAlpha" onclick="setColumnPreset('alpha')">🌟 Quad Alpha Core (10)</button>
    <button class="btn-view-preset" id="viewPresetForecast" onclick="setColumnPreset('forecast')">🔮 Forecast & Targets (9)</button>
  </div>
  <div class="column-actions-group">
    <button class="btn-col-manager" onclick="openColumnManagerModal()">
      ⚙️ Customize Columns (<span id="visibleColCount">19</span>/19)
    </button>
    <button class="btn-col-reset" onclick="resetColumnOrder()" title="Reset column positions to default">
      ↺ Reset Order
    </button>
    <span class="drag-hint">💡 Drag any column header to rearrange</span>
  </div>
</div>
"""

    if 'class="table-view-toolbar"' not in html:
        target = '<!-- Main Table -->'
        html = html.replace(target, toolbar_html + "\n" + target, 1)
        print("Injected table view & column customizer toolbar.")

    # 3. INSERT COLUMN CUSTOMIZER MODAL AT END OF BODY
    col_modal_html = """<!-- Column Customizer Modal -->
<div id="colManagerModal" class="col-modal-backdrop" onclick="if(event.target===this) closeColumnManagerModal()">
  <div class="col-modal-card">
    <div class="col-modal-header">
      <h3>⚙️ Customize Visible Columns</h3>
      <button class="btn-reset" onclick="closeColumnManagerModal()" style="padding:4px 10px; font-size:14px;">✕</button>
    </div>
    <div style="padding: 10px 20px 0 20px; font-size:12px; color:var(--text-secondary); display:flex; justify-content:space-between; align-items:center;">
      <span>Toggle columns to fit your screen without scrolling:</span>
      <div>
        <button class="btn-reset" onclick="setAllColumnsVisible(true)" style="padding:3px 8px; margin-right:4px;">Check All</button>
        <button class="btn-reset" onclick="setAllColumnsVisible(false)" style="padding:3px 8px;">Uncheck All</button>
      </div>
    </div>
    <div class="col-modal-body" id="colModalList"></div>
    <div class="col-modal-footer">
      <button class="btn-reset" onclick="resetColumnOrder()">↺ Reset to Default Order</button>
      <button class="btn-col-action" onclick="closeColumnManagerModal()">Done / Apply View</button>
    </div>
  </div>
</div>
"""

    if 'id="colManagerModal"' not in html:
        target = '</body>'
        html = html.replace(target, col_modal_html + "\n" + target, 1)
        print("Injected colManagerModal dialog into HTML.")

    # 4. JAVASCRIPT COLUMN ENGINE
    js_column_engine = """
  /* ==========================================================================
     MOVABLE COLUMNS & DYNAMIC TABLE HEADER ENGINE
     ========================================================================== */
  const MASTER_COLUMN_DEFS = [
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
    { id: 'rsi', label: '14D RSI', sortKey: 'rsi', defaultOrder: 16 },
    { id: 'quick_links', label: 'Quick Live', sortKey: null, defaultOrder: 17 },
    { id: 'action', label: 'Action', sortKey: null, defaultOrder: 18 }
  ];

  const COLUMN_MAP = {};
  MASTER_COLUMN_DEFS.forEach(c => { COLUMN_MAP[c.id] = c; });

  const COLUMN_PRESETS = {
    all: MASTER_COLUMN_DEFS.map(c => c.id),
    price: ['master_rank', 'symbol', 'today_price', 'day_change_pct', 'week_change_pct', 'today_pe', 'rsi', 'sector', 'name', 'action'],
    alpha: ['master_rank', 'symbol', 'master_score', 'confluence_tier', 'forecast_upside', 'score', 'tech_score', 'mood_score', 'today_price', 'action'],
    forecast: ['master_rank', 'symbol', 'today_price', 'mean_target', 'forecast_upside', 'consensus', 'sector', 'quick_links', 'action']
  };

  let activeColumns = [...COLUMN_PRESETS.all];
  let columnVisibility = {};
  MASTER_COLUMN_DEFS.forEach(c => { columnVisibility[c.id] = true; });
  let currentPreset = 'all';

  // Load saved column preferences from localStorage
  try {
    const savedOrder = localStorage.getItem('watchlist_column_order');
    if (savedOrder) {
      const parsed = JSON.parse(savedOrder);
      if (Array.isArray(parsed) && parsed.length > 0) {
        // Ensure all columns exist
        activeColumns = parsed.filter(id => COLUMN_MAP[id]);
        MASTER_COLUMN_DEFS.forEach(c => {
          if (!activeColumns.includes(c.id)) activeColumns.push(c.id);
        });
      }
    }
    const savedVis = localStorage.getItem('watchlist_column_visibility');
    if (savedVis) {
      columnVisibility = Object.assign(columnVisibility, JSON.parse(savedVis));
    }
  } catch (e) {
    console.error('Error loading column preferences:', e);
  }

  const cellRenderers = {
    master_rank: (s, isSticky) => `<td style="font-weight:800; text-align:center;" class="${isSticky ? 'sticky-col-rank' : ''}">#${s.master_rank}</td>`,
    symbol: (s, isSticky) => `<td class="${isSticky ? 'sticky-col-symbol' : ''}"><strong style="color:var(--accent-blue); font-size:13.5px;">${s.symbol}</strong></td>`,
    name: (s) => `<td><strong>${s.name}</strong></td>`,
    sector: (s) => `<td style="font-size:12.5px;"><strong style="color:var(--text-primary); font-size:12px;">${s.sector}</strong><br><span style="color:var(--text-muted); font-size:10.5px;">${s.sub_industry || ""}</span></td>`,
    master_score: (s) => `<td style="text-align:right; font-weight:900; color:var(--accent-gold); font-size:15px;">${s.master_score}</td>`,
    confluence_tier: (s) => {
      let badgeClass = 'badge-compounder';
      if (s.master_category.includes('Alpha Leader')) badgeClass = 'badge-triple';
      else if (s.master_category.includes('Dip Buy')) badgeClass = 'badge-dip';
      else if (s.master_category.includes('Forecast Upside')) badgeClass = 'badge-forecast';
      return `<td><span class="badge ${badgeClass}">${s.master_category.split('(')[0]}</span></td>`;
    },
    forecast_upside: (s) => {
      const f = s.forecast || {};
      const upsideVal = f.upside_mean_pct !== undefined ? f.upside_mean_pct : 0;
      let upsideColor = 'var(--text-primary)';
      if (upsideVal >= 20) upsideColor = 'var(--accent-green)';
      else if (upsideVal >= 10) upsideColor = 'var(--accent-blue)';
      else if (upsideVal < 0) upsideColor = 'var(--accent-red)';
      return `<td style="text-align:right; font-weight:800; color:${upsideColor};">${upsideVal > 0 ? '+' : ''}${upsideVal}%</td>`;
    },
    mean_target: (s) => {
      const f = s.forecast || {};
      return `<td style="text-align:right; font-weight:700;">₹${f.mean_target ? f.mean_target.toLocaleString() : '-'}</td>`;
    },
    consensus: (s) => {
      const f = s.forecast || {};
      let consensusBadge = '<span style="color:var(--text-muted);">-</span>';
      if (f.consensus_rating) {
        let cBg = 'rgba(52, 211, 153, 0.18)'; let cColor = '#34D399';
        if (f.consensus_rating === 'Hold') { cBg = 'rgba(251, 191, 36, 0.18)'; cColor = '#FBBF24'; }
        else if (f.consensus_rating === 'Underperform') { cBg = 'rgba(248, 113, 113, 0.18)'; cColor = '#F87171'; }
        consensusBadge = `<span style="background:${cBg}; color:${cColor}; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:700;">${f.consensus_rating} (${f.num_analysts})</span>`;
      }
      return `<td>${consensusBadge}</td>`;
    },
    score: (s) => `<td style="text-align:right; font-weight:600;">${s.score}</td>`,
    tech_score: (s) => `<td style="text-align:right; font-weight:600; color:var(--accent-blue);">${s.tech_score}</td>`,
    mood_score: (s) => `<td style="text-align:right; font-weight:600; color:var(--accent-orange);">${s.mood_score || '-'}</td>`,
    today_price: (s) => {
      const lm = s.live_movement || {};
      const cmp = s.today_price || lm.curr_price || 0;
      const cmpDisplay = typeof cmp === 'number' ? '₹' + cmp.toLocaleString('en-IN', {minimumFractionDigits: 1, maximumFractionDigits: 2}) : cmp;
      return `<td style="text-align:right; font-weight:800; font-family:'JetBrains Mono', monospace; font-size:13.5px;" id="price-cell-${s.symbol}">${cmpDisplay}</td>`;
    },
    day_change_pct: (s) => {
      const lm = s.live_movement || {};
      const dayChgPct = s.day_change_pct !== undefined ? s.day_change_pct : (lm.day_change_pct || 0);
      const dayChgAmt = s.day_change !== undefined ? s.day_change : (lm.day_change || 0);
      let dayPillClass = 'move-pill-unch';
      let dayIcon = '•';
      if (dayChgPct > 0) { dayPillClass = 'move-pill-up'; dayIcon = '▲'; }
      else if (dayChgPct < 0) { dayPillClass = 'move-pill-down'; dayIcon = '▼'; }
      const dayAmtDisplay = (dayChgAmt > 0 ? '+' : (dayChgAmt < 0 ? '-' : '')) + '₹' + Math.abs(dayChgAmt).toFixed(2);
      return `<td style="text-align:right;">
        <span class="move-pill ${dayPillClass}" id="day-pill-${s.symbol}">
          ${dayIcon} ${dayChgPct > 0 ? '+' : ''}${typeof dayChgPct === 'number' ? dayChgPct.toFixed(2) : dayChgPct}%
        </span>
        <div class="price-sub-amt" id="day-amt-${s.symbol}">${dayAmtDisplay}</div>
      </td>`;
    },
    week_change_pct: (s) => {
      const lm = s.live_movement || {};
      const weekChgPct = s.week_change_pct !== undefined ? s.week_change_pct : (lm.week_change_pct || 0);
      let weekPillClass = 'move-pill-unch';
      let weekIcon = '•';
      if (weekChgPct > 0) { weekPillClass = 'move-pill-up'; weekIcon = '▲'; }
      else if (weekChgPct < 0) { weekPillClass = 'move-pill-down'; weekIcon = '▼'; }
      return `<td style="text-align:right;">
        <span class="move-pill ${weekPillClass}" id="week-pill-${s.symbol}">
          ${weekIcon} ${weekChgPct > 0 ? '+' : ''}${typeof weekChgPct === 'number' ? weekChgPct.toFixed(2) : weekChgPct}%
        </span>
      </td>`;
    },
    today_pe: (s) => `<td style="text-align:right; font-weight:700; color:var(--accent-blue);">${s.today_pe || '-'}</td>`,
    rsi: (s) => {
      const t = s.technicals || {};
      let rsiColor = 'var(--text-primary)';
      if (t.rsi >= 50 && t.rsi <= 65) rsiColor = 'var(--accent-green)';
      else if (t.rsi > 70) rsiColor = 'var(--accent-red)';
      else if (t.rsi < 35) rsiColor = 'var(--accent-gold)';
      return `<td style="text-align:right; font-weight:700; color:${rsiColor};">${t.rsi || '-'}</td>`;
    },
    quick_links: (s) => {
      const cleanSym = s.clean_sym || s.symbol;
      const gFinUrl = `https://www.google.com/finance/quote/${cleanSym}:NSE`;
      const tvUrl = `https://www.tradingview.com/symbols/NSE-${cleanSym}/`;
      return `<td style="text-align:center;">
        <a href="${gFinUrl}" target="_blank" title="Google Finance Live Quote" style="text-decoration:none; margin-right:6px; font-size:14px;">🌐</a>
        <a href="${tvUrl}" target="_blank" title="TradingView Live Chart" style="text-decoration:none; font-size:14px;">📈</a>
      </td>`;
    },
    action: (s) => `<td style="text-align:center;">
      <button style="background:var(--bg-secondary); border:1px solid var(--accent-gold); color:var(--accent-gold); padding:4px 10px; border-radius:6px; cursor:pointer; font-size:11px; font-weight:800;" onclick="openStockTerminal('${s.symbol}')">360° Intel</button>
    </td>`
  };

  function renderTableHeader() {
    const thead = document.querySelector('#mainTable thead');
    if (!thead) return;

    const visibleCols = activeColumns.filter(id => columnVisibility[id] !== false);
    document.getElementById('visibleColCount').innerText = visibleCols.length;

    let trHtml = '<tr>';
    visibleCols.forEach((colId, idx) => {
      const colDef = COLUMN_MAP[colId];
      if (!colDef) return;
      const sortAttr = colDef.sortKey ? `onclick="sortTable('${colDef.sortKey}')"` : '';
      const sortArrow = colDef.sortKey ? ' ↕' : '';
      const isStickyRank = (colId === 'master_rank' && idx === 0);
      const isStickySymbol = (colId === 'symbol' && (idx === 0 || idx === 1));
      let stickyClass = '';
      if (isStickyRank) stickyClass = 'sticky-col-rank';
      else if (isStickySymbol) stickyClass = 'sticky-col-symbol';

      trHtml += `
        <th draggable="true" 
            data-col-id="${colId}"
            data-col-index="${idx}"
            class="draggable-th ${stickyClass}"
            title="Drag to move column | Click to sort"
            ${sortAttr}>
          <span class="drag-handle" title="Drag to reorder">⠿</span>
          ${colDef.label}${sortArrow}
        </th>`;
    });
    trHtml += '</tr>';
    thead.innerHTML = trHtml;

    attachHeaderDragEvents();
  }

  let draggedColId = null;

  function attachHeaderDragEvents() {
    const ths = document.querySelectorAll('th.draggable-th');
    ths.forEach(th => {
      th.addEventListener('dragstart', (e) => {
        draggedColId = th.getAttribute('data-col-id');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedColId);
        setTimeout(() => th.classList.add('dragging'), 0);
      });

      th.addEventListener('dragend', (e) => {
        th.classList.remove('dragging');
        document.querySelectorAll('th.draggable-th').forEach(el => {
          el.classList.remove('drag-over-left', 'drag-over-right');
        });
      });

      th.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        const rect = th.getBoundingClientRect();
        const mid = rect.left + rect.width / 2;
        th.classList.remove('drag-over-left', 'drag-over-right');
        if (e.clientX < mid) {
          th.classList.add('drag-over-left');
        } else {
          th.classList.add('drag-over-right');
        }
      });

      th.addEventListener('dragleave', (e) => {
        th.classList.remove('drag-over-left', 'drag-over-right');
      });

      th.addEventListener('drop', (e) => {
        e.preventDefault();
        th.classList.remove('drag-over-left', 'drag-over-right');
        const targetColId = th.getAttribute('data-col-id');
        if (!draggedColId || draggedColId === targetColId) return;

        const rect = th.getBoundingClientRect();
        const insertBefore = e.clientX < (rect.left + rect.width / 2);

        // Reorder activeColumns array
        const fromIdx = activeColumns.indexOf(draggedColId);
        if (fromIdx === -1) return;
        activeColumns.splice(fromIdx, 1);

        let toIdx = activeColumns.indexOf(targetColId);
        if (!insertBefore) toIdx++;
        activeColumns.splice(toIdx, 0, draggedColId);

        // Save order
        localStorage.setItem('watchlist_column_order', JSON.stringify(activeColumns));

        // Re-render
        renderTableHeader();
        renderTable(currentData);
      });
    });
  }

  function setColumnPreset(presetKey) {
    currentPreset = presetKey;
    document.querySelectorAll('.btn-view-preset').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById('viewPreset' + presetKey.charAt(0).toUpperCase() + presetKey.slice(1));
    if (btn) btn.classList.add('active');

    if (presetKey === 'all') {
      activeColumns = MASTER_COLUMN_DEFS.map(c => c.id);
      MASTER_COLUMN_DEFS.forEach(c => { columnVisibility[c.id] = true; });
    } else {
      const presetCols = COLUMN_PRESETS[presetKey];
      if (presetCols) {
        activeColumns = [...presetCols];
        MASTER_COLUMN_DEFS.forEach(c => {
          columnVisibility[c.id] = presetCols.includes(c.id);
        });
      }
    }

    localStorage.setItem('watchlist_column_order', JSON.stringify(activeColumns));
    localStorage.setItem('watchlist_column_visibility', JSON.stringify(columnVisibility));

    renderTableHeader();
    renderTable(currentData);
  }

  function resetColumnOrder() {
    activeColumns = MASTER_COLUMN_DEFS.map(c => c.id);
    MASTER_COLUMN_DEFS.forEach(c => { columnVisibility[c.id] = true; });
    localStorage.removeItem('watchlist_column_order');
    localStorage.removeItem('watchlist_column_visibility');

    document.querySelectorAll('.btn-view-preset').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById('viewPresetAll');
    if (btn) btn.classList.add('active');

    renderTableHeader();
    renderTable(currentData);
    populateColumnModalList();
  }

  function openColumnManagerModal() {
    populateColumnModalList();
    document.getElementById('colManagerModal').style.display = 'flex';
  }

  function closeColumnManagerModal() {
    document.getElementById('colManagerModal').style.display = 'none';
    localStorage.setItem('watchlist_column_visibility', JSON.stringify(columnVisibility));
    renderTableHeader();
    renderTable(currentData);
  }

  function populateColumnModalList() {
    const container = document.getElementById('colModalList');
    if (!container) return;
    container.innerHTML = '';

    MASTER_COLUMN_DEFS.forEach(col => {
      const isChecked = columnVisibility[col.id] !== false;
      const lbl = document.createElement('label');
      lbl.className = 'col-checkbox-label';
      lbl.innerHTML = `
        <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="toggleColumnVisibility('${col.id}', this.checked)">
        <span>${col.label}</span>
      `;
      container.appendChild(lbl);
    });
  }

  function toggleColumnVisibility(colId, isVisible) {
    columnVisibility[colId] = isVisible;
    if (isVisible && !activeColumns.includes(colId)) {
      activeColumns.push(colId);
    }
  }

  function setAllColumnsVisible(visible) {
    MASTER_COLUMN_DEFS.forEach(c => {
      columnVisibility[c.id] = visible;
    });
    populateColumnModalList();
  }
"""

    if "MASTER_COLUMN_DEFS" not in html:
        # insert right above renderTable
        target = "function renderTable(data) {"
        html = html.replace(target, js_column_engine + "\n  " + target, 1)
        print("Injected JS movable column engine & presets.")

    # 5. UPDATE renderTable TO USE DYNAMIC COLUMNS
    old_render_fn = re.search(r"function renderTable\(data\) \{[\s\S]*?let sortDirections = \{\};", html)
    if old_render_fn:
        new_render_fn = """function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    let advCount = 0, decCount = 0, unchCount = 0;
    const visibleCols = activeColumns.filter(id => columnVisibility[id] !== false);

    data.forEach((s, idx) => {
      const tr = document.createElement('tr');
      const lm = s.live_movement || {};
      const dayChgPct = s.day_change_pct !== undefined ? s.day_change_pct : (lm.day_change_pct || 0);

      // Breadth tally
      if (dayChgPct > 0) advCount++;
      else if (dayChgPct < 0) decCount++;
      else unchCount++;

      tr.onclick = (e) => {
        if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;
        openStockTerminal(s.symbol);
      };

      // Build TD cells dynamically in active column order
      let cellsHtml = '';
      visibleCols.forEach((colId, colIdx) => {
        const renderer = cellRenderers[colId];
        if (renderer) {
          const isStickyRank = (colId === 'master_rank' && colIdx === 0);
          const isStickySymbol = (colId === 'symbol' && (colIdx === 0 || colIdx === 1));
          cellsHtml += renderer(s, isStickyRank || isStickySymbol);
        }
      });

      tr.innerHTML = cellsHtml;
      tbody.appendChild(tr);
    });
    
    // Update summary counters
    document.getElementById('stat-quad-leaders').innerText = rawData.filter(x => x.master_score >= 88.0).length;
    document.getElementById('stat-high-forecast').innerText = rawData.filter(x => (x.forecast && x.forecast.upside_mean_pct >= 20.0)).length;
    document.getElementById('stat-strong-buy').innerText = rawData.filter(x => (x.forecast && ((x.forecast.breakdown.buy_pct + x.forecast.breakdown.outperform_pct) >= 80.0))).length;
    document.getElementById('stat-mood-kings').innerText = rawData.filter(x => x.mood_score >= 90).length;
    document.getElementById('stat-pullbacks').innerText = rawData.filter(x => x.score >= 70 && (x.technicals && x.technicals.rsi < 45)).length;

    // Update Market Breadth Chip
    const breadthEl = document.getElementById('marketBreadthChip');
    if (breadthEl) {
      breadthEl.innerText = `📈 Adv: ${advCount} | Dec: ${decCount} | Unch: ${unchCount}`;
    }
  }

  let sortDirections = {};"""
        html = html.replace(old_render_fn.group(0), new_render_fn, 1)
        print("Updated renderTable to dynamically render cells according to movable column order.")

    # 6. INITIALIZE RENDER TABLE HEADER AT APP STARTUP
    # Find initTheme(); renderTable(currentData);
    old_init = "initTheme();\n  renderTable(currentData);"
    new_init = "initTheme();\n  renderTableHeader();\n  renderTable(currentData);"
    if old_init in html:
        html = html.replace(old_init, new_init, 1)
        print("Updated startup initialization to call renderTableHeader().")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully saved updated {html_path} ({len(html)} bytes)!")

if __name__ == "__main__":
    make_columns_movable()
