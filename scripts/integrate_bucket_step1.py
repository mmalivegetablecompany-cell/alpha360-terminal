import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Script injection in <head>
SCRIPT_TAG = """  <script src="xlsx.full.min.js"></script>
  <script>
    if (typeof XLSX === 'undefined') {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"><\\/script>');
    }
  </script>
</head>"""

if "xlsx.full.min.js" not in html:
    html = html.replace("</head>", SCRIPT_TAG)
    print("Injected SheetJS script tag into <head>.")

# 2. CSS injection
BUCKET_CSS = """
  /* ==========================================================================
     BUCKET PORTFOLIO & EXCEL EXPORT STYLING
     ========================================================================== */
  .btn-bucket-header {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.22), rgba(56, 189, 248, 0.22));
    border: 1px solid #F59E0B;
    color: #FBBF24;
    padding: 7px 16px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 800;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    transition: all 0.2s ease;
  }
  .btn-bucket-header:hover {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.35), rgba(56, 189, 248, 0.35));
    box-shadow: 0 0 14px rgba(245, 158, 11, 0.4);
    transform: translateY(-1px);
  }
  .btn-export-excel {
    background: linear-gradient(135deg, #10B981, #059669);
    border: 1px solid #10B981;
    color: #FFFFFF;
    padding: 7px 15px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 800;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s ease;
  }
  .btn-export-excel:hover {
    background: linear-gradient(135deg, #059669, #047857);
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    transform: translateY(-1px);
  }
  .bucket-action-bar {
    background: var(--bg-card);
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
  }
  .bucket-bar-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .bucket-bar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .btn-bucket-main {
    background: rgba(245, 158, 11, 0.16);
    border: 1px solid rgba(245, 158, 11, 0.5);
    color: #FBBF24;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;
  }
  .btn-bucket-main:hover {
    background: rgba(245, 158, 11, 0.28);
    border-color: #F59E0B;
    transform: translateY(-1px);
  }
  .bucket-pill-badge {
    background: #F59E0B;
    color: #0B1120;
    font-size: 11px;
    font-weight: 900;
    padding: 1px 7px;
    border-radius: 10px;
    margin-left: 2px;
  }
  .btn-bucket-action {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn-bucket-action:hover {
    border-color: var(--accent-blue);
    color: var(--accent-blue);
  }
  .btn-bucket-clear {
    background: transparent;
    border: 1px dashed var(--border-color);
    color: var(--text-secondary);
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn-bucket-clear:hover {
    color: var(--accent-red);
    border-color: var(--accent-red);
  }
  tr.row-in-bucket td {
    background-color: rgba(56, 189, 248, 0.05);
  }
  tr.row-in-bucket {
    border-left: 3px solid #38BDF8 !important;
  }
  tr.row-in-bucket:hover td {
    background-color: rgba(56, 189, 248, 0.1) !important;
  }
  .bucket-cb {
    cursor: pointer;
    transform: scale(1.25);
    accent-color: #38BDF8;
  }
  .filter-pill.pill-bucket {
    background: rgba(245, 158, 11, 0.15);
    border-color: rgba(245, 158, 11, 0.4);
    color: #FBBF24;
    font-weight: 700;
  }
  .filter-pill.pill-bucket:hover {
    background: rgba(245, 158, 11, 0.25);
    border-color: #F59E0B;
  }
  .filter-pill.pill-bucket.active {
    background: #F59E0B;
    color: #0B1120;
    border-color: #F59E0B;
  }
  .tool-btn.bucket {
    border-color: #F59E0B;
    color: #FBBF24;
    background: rgba(245, 158, 11, 0.12);
    cursor: pointer;
    font-weight: 700;
  }
  .tool-btn.bucket:hover {
    background: rgba(245, 158, 11, 0.25);
  }
  .tool-btn.bucket.in-bucket {
    background: #F59E0B;
    color: #0B1120;
    font-weight: 800;
    border-color: #F59E0B;
  }

  /* Modal styling */
  .bucket-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .bucket-modal-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(11, 17, 32, 0.85);
    backdrop-filter: blur(6px);
  }
  .bucket-modal-content {
    position: relative;
    background: var(--bg-card);
    border: 1px solid rgba(245, 158, 11, 0.4);
    border-radius: 16px;
    width: 92vw;
    max-width: 1200px;
    max-height: 88vh;
    overflow-y: auto;
    padding: 24px 28px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
    z-index: 10;
  }
  .bucket-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
  }
  .bm-title {
    font-size: 20px;
    font-weight: 900;
    color: #FBBF24;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .bm-subtitle {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 3px;
  }
  .bm-header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .bm-btn-view {
    background: rgba(56, 189, 248, 0.16);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #38BDF8;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }
  .bm-btn-view:hover {
    background: rgba(56, 189, 248, 0.28);
  }
  .bm-btn-clear {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }
  .bm-btn-clear:hover {
    color: var(--accent-red);
    border-color: var(--accent-red);
  }
  .bm-btn-close {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    width: 32px;
    height: 32px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }
  .bm-btn-close:hover {
    background: var(--accent-red);
    border-color: var(--accent-red);
    color: #FFF;
  }
  .bucket-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 18px;
  }
  .b-stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
  }
  .b-stat-lbl {
    font-size: 10.5px;
    font-weight: 800;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  .b-stat-val {
    font-size: 20px;
    font-weight: 900;
    color: var(--accent-gold);
    font-family: 'JetBrains Mono', monospace;
  }
  .b-stat-sub {
    font-size: 10px;
    color: var(--text-muted);
    margin-top: 3px;
  }
  .bucket-sectors-section {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .b-sec-title {
    font-size: 11.5px;
    font-weight: 800;
    color: var(--text-secondary);
    white-space: nowrap;
  }
  .b-sec-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  .b-sec-chip {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #38BDF8;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
  }
  .bucket-modal-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 10px;
  }
  .bm-tool-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .bm-tool-lbl {
    font-size: 11.5px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
  }
  .bucket-table-container {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    overflow-x: auto;
    background: var(--bg-secondary);
    max-height: 400px;
    overflow-y: auto;
  }
  .bucket-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }
  .bucket-table th {
    background: rgba(0, 0, 0, 0.3);
    padding: 10px 12px;
    text-align: left;
    font-size: 11px;
    font-weight: 800;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 2;
  }
  .bucket-table td {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
  }
  .bucket-table tr:hover td {
    background-color: rgba(255, 255, 255, 0.03);
  }
  .bucket-btn-remove {
    background: transparent;
    border: 1px solid rgba(248, 113, 113, 0.3);
    color: #F87171;
    padding: 2px 7px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.15s;
  }
  .bucket-btn-remove:hover {
    background: #EF4444;
    color: #FFF;
    border-color: #EF4444;
  }
  .bucket-empty-state {
    padding: 40px 20px;
    text-align: center;
  }
"""

if "btn-bucket-header" not in html:
    idx = html.find("/* ==========================================================================\n     RESPONSIVE BREAKPOINTS")
    if idx == -1:
        idx = html.find(".table-container {")
    if idx != -1:
        html = html[:idx] + BUCKET_CSS + "\n  " + html[idx:]
        print("Inserted Bucket & Excel CSS.")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Step 1 (Scripts & CSS) complete.")
