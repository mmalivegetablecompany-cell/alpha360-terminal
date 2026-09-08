import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Header Actions
old_header_actions = """  <div class="header-actions">
    <button id="themeToggle" class="btn-theme" onclick="toggleTheme()">☀️ Light Mode</button>
    <button class="btn-export" onclick="exportFilteredCSV()">📥 Export CSV (119)</button>
  </div>"""

new_header_actions = """  <div class="header-actions">
    <button id="themeToggle" class="btn-theme" onclick="toggleTheme()">☀️ Light Mode</button>
    <button class="btn-bucket-header" id="btnHeaderBucket" onclick="openBucketModal()" title="Open My Stock Bucket Portfolio">
      🧺 My Bucket (<span id="headerBucketCount">0</span>)
    </button>
    <button class="btn-export-excel" onclick="exportFilteredExcel()" title="Export currently filtered stocks to Microsoft Excel (.xlsx)">
      📗 Export Excel (.xlsx)
    </button>
    <button class="btn-export" onclick="exportFilteredCSV()" title="Export currently filtered stocks to CSV">
      📥 Export CSV (<span id="btnCsvCount">119</span>)
    </button>
  </div>"""

if old_header_actions in html:
    html = html.replace(old_header_actions, new_header_actions)
    print("Updated header actions with Bucket and Excel export buttons.")

# 2. Add Bucket Pill in quick filter bar
target_all_pill = '<button class="filter-pill active" onclick="setFilterPill(\'all\', this)">All Universe (119)</button>'
bucket_pill = """<button class="filter-pill active" onclick="setFilterPill('all', this)">All Universe (119)</button>
    <button class="filter-pill pill-bucket" id="pillBucket" onclick="setFilterPill('bucket', this)" title="View only stocks in your custom bucket">🧺 My Bucket (<span id="bucketPillCount">0</span>)</button>"""

if target_all_pill in html and "pillBucket" not in html:
    html = html.replace(target_all_pill, bucket_pill, 1)
    print("Inserted Bucket filter pill in filter-pills-container.")

# 3. Add Bucket Action Bar right between table-view-toolbar and main table
BUCKET_ACTION_BAR = """
<!-- BUCKET ACTION & PORTFOLIO BAR -->
<div class="bucket-action-bar" id="bucketActionBar">
  <div class="bucket-bar-left">
    <button class="btn-bucket-main" onclick="openBucketModal()" title="Open 360° Portfolio Bucket & Analytics">
      🧺 My Stock Bucket: <span id="barBucketCount" class="bucket-pill-badge">0</span> stocks
    </button>
    <button class="btn-bucket-action" onclick="addAllFilteredToBucket()" title="Add all currently filtered stocks to Bucket">
      ➕ Add Visible (<span id="barFilteredCount">119</span>) to Bucket
    </button>
    <button class="btn-bucket-action" onclick="removeAllFilteredFromBucket()" title="Remove currently filtered stocks from Bucket">
      ➖ Remove Visible
    </button>
    <button class="btn-bucket-clear" onclick="clearBucketWithConfirm()" title="Clear all stocks from Bucket">
      🗑️ Clear
    </button>
  </div>
  <div class="bucket-bar-right">
    <button class="btn-export-excel" onclick="exportBucketExcel()" title="Export current bucketed stocks directly to Excel (.xlsx)">
      📗 Export Bucket (.xlsx)
    </button>
    <button class="btn-export-csv" onclick="exportBucketCSV()" title="Export current bucketed stocks to CSV">
      📄 Export Bucket (.csv)
    </button>
  </div>
</div>
"""

target_main_table = "<!-- Main Table -->"
if target_main_table in html and "bucketActionBar" not in html:
    html = html.replace(target_main_table, BUCKET_ACTION_BAR + "\n" + target_main_table, 1)
    print("Inserted bucketActionBar above Main Table.")

# 4. Update static thead to have bucket checkbox th as first column
old_thead_tr = """    <thead>
      <tr>
        <th onclick="sortTable('master_rank')">Rank ↕</th>"""

new_thead_tr = """    <thead>
      <tr>
        <th style="text-align:center; min-width:65px;" title="Select/Deselect all visible in Bucket">
          <input type="checkbox" id="selectAllBucketCheckbox" onchange="toggleSelectAllVisibleBucket(this.checked)" title="Select/Deselect all visible in Bucket" style="cursor:pointer; transform:scale(1.2); accent-color:#38BDF8; vertical-align:middle;">
          <span style="font-size:11px; margin-left:3px; vertical-align:middle;">🧺</span>
        </th>
        <th onclick="sortTable('master_rank')">Rank ↕</th>"""

if old_thead_tr in html and "selectAllBucketCheckbox" not in html:
    html = html.replace(old_thead_tr, new_thead_tr, 1)
    print("Inserted static thead bucket column.")

# 5. Add Modal Bucket button in 360° Intel Modal nav
target_nav_actions = '<div class="nav-right-actions">'
modal_btn = """<div class="nav-right-actions">
      <button id="btnModalBucket" class="tool-btn bucket" onclick="toggleModalStockBucket()"><span id="modalBucketIcon">🧺</span> <span id="modalBucketText">+ Add to Bucket</span></button>"""

if target_nav_actions in html and "btnModalBucket" not in html:
    html = html.replace(target_nav_actions, modal_btn, 1)
    print("Inserted btnModalBucket in 360° Intel modal nav.")

# 6. Insert Bucket Modal HTML before </body>
BUCKET_MODAL_HTML = """
<!-- BUCKET PORTFOLIO MODAL -->
<div id="bucketModal" class="bucket-modal" style="display:none;">
  <div class="bucket-modal-backdrop" onclick="closeBucketModal()"></div>
  <div class="bucket-modal-content">
    <div class="bucket-modal-header">
      <div class="bm-title-group">
        <div class="bm-title">🧺 My Stock Bucket Portfolio</div>
        <div class="bm-subtitle">Personalized watchlist & custom basket for tracking, rebalancing and export</div>
      </div>
      <div class="bm-header-actions">
        <button class="bm-btn-view" onclick="viewBucketInMainTable()">👁️ View in Main Table (<span id="bmViewCount">0</span>)</button>
        <button class="bm-btn-clear" onclick="clearBucketWithConfirm()">🗑️ Clear Bucket</button>
        <button class="bm-btn-close" onclick="closeBucketModal()">✕</button>
      </div>
    </div>

    <!-- Bucket Aggregate Statistics Cards -->
    <div class="bucket-stats-grid">
      <div class="b-stat-card">
        <div class="b-stat-lbl">🧺 Total Stocks</div>
        <div class="b-stat-val" id="bstat-stocks">0 / 119</div>
        <div class="b-stat-sub">Stocks in Basket</div>
      </div>
      <div class="b-stat-card">
        <div class="b-stat-lbl">🏛️ Combined Mcap</div>
        <div class="b-stat-val" id="bstat-mcap">₹0 Cr</div>
        <div class="b-stat-sub">Aggregate Valuation</div>
      </div>
      <div class="b-stat-card">
        <div class="b-stat-lbl">🌟 Avg Master Quad</div>
        <div class="b-stat-val" id="bstat-score">0.0</div>
        <div class="b-stat-sub">Portfolio Quality</div>
      </div>
      <div class="b-stat-card">
        <div class="b-stat-lbl">⚖️ Avg P/E Multiple</div>
        <div class="b-stat-val" id="bstat-pe">-</div>
        <div class="b-stat-sub">Valuation Level</div>
      </div>
      <div class="b-stat-card">
        <div class="b-stat-lbl">🎯 Avg 1Y Upside</div>
        <div class="b-stat-val" id="bstat-upside">0.0%</div>
        <div class="b-stat-sub">Analyst Target Return</div>
      </div>
      <div class="b-stat-card">
        <div class="b-stat-lbl">📈 Avg Daily Move</div>
        <div class="b-stat-val" id="bstat-daymove">0.00%</div>
        <div class="b-stat-sub">Today's Basket Return</div>
      </div>
    </div>

    <!-- Sector Diversification Bar -->
    <div class="bucket-sectors-section">
      <div class="b-sec-title">🏢 Sector Diversification:</div>
      <div class="b-sec-tags" id="bstat-sectors">
        <span style="font-size:11px; color:var(--text-muted);">No sectors yet</span>
      </div>
    </div>

    <!-- Bucket Actions & Export Bar -->
    <div class="bucket-modal-toolbar">
      <div class="bm-tool-left">
        <span class="bm-tool-lbl">Export Basket:</span>
        <button class="btn-export-excel" onclick="exportBucketExcel()">
          📗 Download Excel (.xlsx)
        </button>
        <button class="btn-export-csv" onclick="exportBucketCSV()">
          📄 Download CSV
        </button>
      </div>
      <div class="bm-tool-right">
        <span id="bucketTableSummary" style="font-size:12px; color:var(--text-muted); font-weight:600;">0 stocks</span>
      </div>
    </div>

    <!-- Bucket Stocks Table -->
    <div class="bucket-table-container">
      <table class="bucket-table">
        <thead>
          <tr>
            <th style="width:50px;">Rank</th>
            <th>Symbol</th>
            <th>Company Name</th>
            <th>Sector</th>
            <th style="text-align:right;">Market Cap</th>
            <th style="text-align:right;">CMP (₹)</th>
            <th style="text-align:right;">1D Move</th>
            <th style="text-align:right;">P/E</th>
            <th style="text-align:right;">1Y Target</th>
            <th style="text-align:right;">Upside</th>
            <th style="text-align:center;">Master Quad</th>
            <th style="text-align:center; width:60px;">Action</th>
          </tr>
        </thead>
        <tbody id="bucketTableBody">
        </tbody>
      </table>
      <div id="bucketEmptyState" class="bucket-empty-state" style="display:none;">
        <div style="font-size:36px; margin-bottom:10px;">🧺</div>
        <div style="font-size:16px; font-weight:800; color:var(--text-primary); margin-bottom:6px;">Your Bucket is Empty</div>
        <div style="font-size:12px; color:var(--text-muted); max-width:400px; margin:0 auto 16px auto;">
          Select stocks from the main table using the 🧺 checkboxes or "+ Add to Bucket" buttons to track your portfolio.
        </div>
        <button class="btn-bucket-sub" onclick="addAllFilteredToBucket(); closeBucketModal();" style="padding:7px 16px; font-size:12px; background:var(--accent-blue); color:#0B1120; border:none; font-weight:800; border-radius:6px; cursor:pointer;">
          ➕ Add All Currently Filtered Stocks to Bucket
        </button>
      </div>
    </div>
  </div>
</div>
"""

if "id=\"bucketModal\"" not in html:
    idx = html.rfind("</body>")
    if idx != -1:
        html = html[:idx] + BUCKET_MODAL_HTML + "\n" + html[idx:]
        print("Inserted bucketModal HTML before </body>.")

# 7. Update column count labels from 22 to 23
html = re.sub(r'Full Master View \(22\)', 'Full Master View (23)', html)
html = re.sub(r'Customize Columns \(<span id="visibleColCount">22</span>/22\)', 'Customize Columns (<span id="visibleColCount">23</span>/23)', html)
print("Updated toolbar column counts from 22 to 23.")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Step 2 (HTML updates) complete.")
