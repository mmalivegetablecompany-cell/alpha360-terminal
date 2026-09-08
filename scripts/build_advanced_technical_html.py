"""
Builder Script for Advance_Technical_Analysis_424_Stocks.html
Generates an institutional-grade, responsive single-page application with:
- Dark / Light Mode Toggle with persistent localStorage theme state
- 5 Institutional KPI Metric Summary Cards (Master Alpha, High Forecast, Strong Buy, ET Prime, MA Pullback)
- Saved Watchlists & Baskets Toolbar (Star Stocks, 35 Master, Active Core, Ready to Buy, Wait, Favs, Quarantine, Eliminated, My Bucket)
- 20+ Institutional Strategy Screener Presets
- Interactive My Bucket Star Bookmark toggle on cards and table rows (persisted to localStorage)
- Bi-Directional Table Column Sorting (Ascending ▲ / Descending ▼ on every column header)
- Excel Export (.xlsx) via SheetJS
- 360° Technical & Institutional Modal with HTML5 Canvas Candlestick Charting
- Live Real-Time Price Syncing with live_price_server.py (127.0.0.1:8765)
"""

import json
import os
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

def build_html():
    print("Building Advance_Technical_Analysis_424_Stocks.html...")
    
    in_file = "database/advanced_technicals_424.json" if os.path.exists("database/advanced_technicals_424.json") else "advanced_technicals_424.json"
    with open(in_file, "r", encoding="utf-8") as f:
        stocks = json.load(f)
        
    print(f"Loaded {len(stocks)} stocks from {in_file}")
    stocks_json_str = json.dumps(stocks, ensure_ascii=False)

    template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>424 Stocks — Advanced Technical & Institutional Terminal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <script src="xlsx.full.min.js"></script>
  <script>window.XLSX || document.write('<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"><\\/script>')</script>
  <script>
    // Theme Initializer to prevent flash
    (function() {
      try {
        const savedTheme = localStorage.getItem('terminal_theme') || 'dark';
        if (savedTheme === 'light') {
          document.documentElement.classList.remove('dark');
          document.documentElement.classList.add('light');
        } else {
          document.documentElement.classList.remove('light');
          document.documentElement.classList.add('dark');
        }
      } catch (e) {
        document.documentElement.classList.add('dark');
      }
    })();

    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          },
          colors: {
            terminal: {
              950: '#070B14',
              900: '#0B1120',
              850: '#0F172A',
              800: '#131E32',
              700: '#1E293B',
              600: '#334155',
              500: '#475569',
              400: '#64748B',
              300: '#94A3B8',
              200: '#CBD5E1',
              100: '#F1F5F9'
            },
            techgreen: '#10B981',
            techred: '#EF4444',
            techblue: '#38BDF8',
            techamber: '#F59E0B',
            techpurple: '#A855F7'
          }
        }
      }
    }
  </script>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      transition: background-color 0.2s ease, color 0.2s ease;
      overflow-x: hidden;
    }
    .font-mono { font-family: 'JetBrains Mono', monospace; }

    /* Dark Mode Defaults */
    html.dark body {
      background-color: #070B14;
      color: #F1F5F9;
    }
    html.dark ::-webkit-scrollbar-track { background: #0B1120; }
    html.dark ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 4px; }
    html.dark ::-webkit-scrollbar-thumb:hover { background: #334155; }

    /* Light Mode Overrides */
    html.light body {
      background-color: #F8FAFC;
      color: #0F172A;
    }
    html.light ::-webkit-scrollbar-track { background: #F1F5F9; }
    html.light ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
    html.light ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

    html.light .theme-bg-base { background-color: #F8FAFC !important; }
    html.light .theme-bg-surface { background-color: #FFFFFF !important; }
    html.light .theme-bg-subtle { background-color: #F1F5F9 !important; }
    html.light .theme-border { border-color: #E2E8F0 !important; }
    html.light .theme-border-subtle { border-color: #F1F5F9 !important; }
    html.light .theme-text-primary { color: #0F172A !important; }
    html.light .theme-text-secondary { color: #475569 !important; }
    html.light .theme-text-muted { color: #64748B !important; }
    html.light .theme-card {
      background-color: #FFFFFF !important;
      border-color: #E2E8F0 !important;
      box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.06);
    }
    html.light .theme-card:hover {
      box-shadow: 0 10px 20px -3px rgba(0, 0, 0, 0.08);
    }
    html.light .theme-table-header {
      background-color: #F1F5F9 !important;
      color: #475569 !important;
      border-color: #E2E8F0 !important;
    }
    html.light .theme-table-row:hover {
      background-color: #F8FAFC !important;
    }
    html.light .theme-input {
      background-color: #FFFFFF !important;
      color: #0F172A !important;
      border-color: #CBD5E1 !important;
    }
    html.light .theme-input:focus {
      border-color: #0284C7 !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 8px; height: 8px; }

    /* Glow Effects */
    .glow-green { box-shadow: 0 0 20px -5px rgba(16, 185, 129, 0.35); }
    .glow-blue { box-shadow: 0 0 20px -5px rgba(56, 189, 248, 0.35); }
    .glow-amber { box-shadow: 0 0 20px -5px rgba(245, 158, 11, 0.35); }
    .glow-purple { box-shadow: 0 0 20px -5px rgba(168, 85, 247, 0.35); }
    .glow-red { box-shadow: 0 0 20px -5px rgba(239, 68, 68, 0.35); }

    /* Price Flash Animations */
    @keyframes greenFlash {
      0% { background-color: rgba(16, 185, 129, 0.45); }
      100% { background-color: transparent; }
    }
    @keyframes redFlash {
      0% { background-color: rgba(239, 68, 68, 0.45); }
      100% { background-color: transparent; }
    }
    .flash-up { animation: greenFlash 1.2s ease-out; }
    .flash-down { animation: redFlash 1.2s ease-out; }

    /* Modal Backdrop Blur */
    .modal-backdrop {
      backdrop-filter: blur(8px);
      background-color: rgba(7, 11, 20, 0.85);
    }
    html.light .modal-backdrop {
      background-color: rgba(15, 23, 42, 0.65);
    }

    /* Table Sort Header Arrows */
    th.sortable {
      cursor: pointer;
      user-select: none;
      transition: background-color 0.15s ease;
    }
    th.sortable:hover {
      background-color: rgba(56, 189, 248, 0.08);
    }
    th.sortable .sort-icon {
      display: inline-block;
      margin-left: 4px;
      font-size: 10px;
      opacity: 0.4;
      transition: opacity 0.15s ease;
    }
    th.sortable.sort-active .sort-icon {
      opacity: 1;
      color: #38BDF8;
    }
    th.sortable.sort-active {
      color: #38BDF8 !important;
    }

    /* Star Bookmark Button */
    .star-btn {
      cursor: pointer;
      transition: transform 0.15s ease, color 0.15s ease;
    }
    .star-btn:hover {
      transform: scale(1.25);
    }
    .star-active {
      color: #F59E0B !important;
      text-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
    }

    /* Watchlist Pills */
    .filter-chip {
      transition: all 0.15s ease;
      cursor: pointer;
      white-space: nowrap;
      user-select: none;
    }
    .filter-chip:hover {
      transform: translateY(-1px);
    }
    .filter-chip.active {
      box-shadow: 0 2px 10px -2px rgba(56, 189, 248, 0.4);
    }
  </style>
</head>
<body class="min-h-screen theme-bg-base selection:bg-sky-500 selection:text-white">

  <!-- ========================================== -->
  <!-- TOP HEADER & LIVE CONNECTION HUD           -->
  <!-- ========================================== -->
  <header class="sticky top-0 z-40 border-b border-slate-800 bg-[#0B1120]/95 backdrop-blur px-4 lg:px-8 py-3 shadow-xl theme-card theme-border">
    <div class="max-w-[1720px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
      
      <!-- Title & Branding -->
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-emerald-400 p-0.5 shadow-lg shadow-sky-500/20 flex items-center justify-center">
          <div class="h-full w-full bg-[#0B1120] rounded-[10px] flex items-center justify-center theme-bg-surface">
            <span class="text-xl">📈</span>
          </div>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl font-black tracking-tight text-white theme-text-primary flex items-center gap-2">
              424 STOCKS <span class="bg-gradient-to-r from-sky-400 to-emerald-400 bg-clip-text text-transparent">TECHNICAL TERMINAL</span>
            </h1>
            <span class="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono font-medium">PRO 360°</span>
          </div>
          <p class="text-xs text-slate-400 theme-text-muted">Institutional Multi-Timeframe Analysis • Actionable Trade Blueprints • Real-Time Pricing</p>
        </div>
      </div>

      <!-- Top Right Controls: Theme Toggle, My Bucket, Excel Export, Server Status, View Switcher -->
      <div class="flex items-center flex-wrap gap-2.5">
        
        <!-- Buy Radar & Signal Tracker Button -->
        <button id="buyRadarBtn" onclick="openRadarModal()" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500/20 via-sky-500/20 to-emerald-500/20 hover:from-amber-500/30 hover:to-emerald-500/30 border border-emerald-500/50 text-white text-xs font-black transition active:scale-95 shadow-md shadow-emerald-500/10">
          <span class="animate-pulse text-amber-400 text-sm">⚡</span>
          <span>BUY RADAR &amp; TRACKER</span>
          <span id="radarActiveCountBadge" class="px-1.5 py-0.2 rounded-full bg-emerald-500 text-slate-950 font-mono text-[11px] font-black">0</span>
        </button>

        <!-- Theme Toggle Button -->
        <button id="themeToggleBtn" onclick="toggleTheme()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 theme-bg-subtle border border-slate-800 theme-border text-slate-300 theme-text-primary text-xs font-semibold hover:border-sky-500/40 transition shadow-sm active:scale-95">
          <span id="themeIcon">🌙</span>
          <span id="themeLabel">Dark Mode</span>
        </button>

        <!-- My Bucket Filter Button -->
        <button id="headerBucketBtn" onclick="filterByPreset('MY_BUCKET')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 text-xs font-bold transition active:scale-95 shadow-sm">
          <span>🗂️</span>
          <span>My Bucket</span>
          <span id="headerBucketCount" class="px-1.5 py-0.2 rounded-full bg-amber-500/20 font-mono text-[11px] font-extrabold">60</span>
        </button>

        <!-- Excel Export Button -->
        <button onclick="exportToExcel()" title="Export filtered stocks to Microsoft Excel (.xlsx)" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/90 hover:bg-emerald-600 text-white text-xs font-bold shadow-md shadow-emerald-600/20 transition active:scale-95">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Export Excel (.xlsx)
        </button>

        <!-- Live Server Status Badge -->
        <div id="liveServerPill" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 theme-bg-subtle border border-slate-800 theme-border text-xs font-mono">
          <span id="liveStatusDot" class="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span id="liveStatusText" class="text-slate-300 theme-text-secondary">Checking Live Server...</span>
        </div>

        <!-- Sync Button -->
        <button onclick="checkLiveServer()" title="Sync quotes from local price server" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 text-xs font-medium transition active:scale-95">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          Sync
        </button>

        <!-- View Switcher (Cards / Table) -->
        <div class="flex items-center rounded-lg bg-slate-900 theme-bg-subtle p-1 border border-slate-800 theme-border text-xs">
          <button id="viewGridBtn" onclick="switchView('grid')" class="px-2.5 py-1 rounded-md bg-sky-500 text-white font-semibold transition">
            Cards
          </button>
          <button id="viewTableBtn" onclick="switchView('table')" class="px-2.5 py-1 rounded-md text-slate-400 theme-text-muted hover:text-white transition">
            Table
          </button>
        </div>

      </div>

    </div>

    <!-- ========================================== -->
    <!-- 5 TOP INSTITUTIONAL KPI SUMMARY CARDS      -->
    <!-- (Directly matching institutional terminal) -->
    <!-- ========================================== -->
    <div class="max-w-[1720px] mx-auto mt-3.5 pt-3.5 border-t border-slate-800/80 theme-border grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      
      <!-- KPI 1: Master Alpha Leaders -->
      <div id="kpiCard-MASTER_ALPHA" onclick="filterByPreset('MASTER_ALPHA')" class="cursor-pointer p-3 rounded-xl bg-slate-900/80 theme-card border border-amber-500/30 border-l-4 border-l-amber-400 hover:glow-amber transition group">
        <div class="flex items-center justify-between text-[11px] font-mono font-bold uppercase tracking-wider text-amber-400">
          <span># Master Alpha Leaders</span>
          <span>👑</span>
        </div>
        <div class="text-2xl font-black font-mono mt-1 text-white theme-text-primary" id="kpiMasterCount">5</div>
        <div class="text-[11px] text-slate-400 theme-text-muted mt-0.5">Master Score &ge; 88.0</div>
      </div>

      <!-- KPI 2: High Forecast Upside -->
      <div id="kpiCard-HIGH_FORECAST" onclick="filterByPreset('HIGH_FORECAST')" class="cursor-pointer p-3 rounded-xl bg-slate-900/80 theme-card border border-sky-500/30 border-l-4 border-l-sky-400 hover:glow-blue transition group">
        <div class="flex items-center justify-between text-[11px] font-mono font-bold uppercase tracking-wider text-sky-400">
          <span>🚀 High Forecast Upside</span>
          <span>📈</span>
        </div>
        <div class="text-2xl font-black font-mono mt-1 text-white theme-text-primary" id="kpiForecastCount">98</div>
        <div class="text-[11px] text-slate-400 theme-text-muted mt-0.5">Analyst Target Upside &ge; +20%</div>
      </div>

      <!-- KPI 3: Strong Buy Consensus -->
      <div id="kpiCard-STRONG_BUY_CONSENSUS" onclick="filterByPreset('STRONG_BUY_CONSENSUS')" class="cursor-pointer p-3 rounded-xl bg-slate-900/80 theme-card border border-emerald-500/30 border-l-4 border-l-emerald-400 hover:glow-green transition group">
        <div class="flex items-center justify-between text-[11px] font-mono font-bold uppercase tracking-wider text-emerald-400">
          <span>⭐ Strong Buy Consensus</span>
          <span>🤝</span>
        </div>
        <div class="text-2xl font-black font-mono mt-1 text-white theme-text-primary" id="kpiConsensusCount">138</div>
        <div class="text-[11px] text-slate-400 theme-text-muted mt-0.5">&ge; 80% Buy/Outperform Ratio</div>
      </div>

      <!-- KPI 4: Top ET Prime Score -->
      <div id="kpiCard-TOP_ET_PRIME" onclick="filterByPreset('TOP_ET_PRIME')" class="cursor-pointer p-3 rounded-xl bg-slate-900/80 theme-card border border-purple-500/30 border-l-4 border-l-purple-400 hover:glow-purple transition group">
        <div class="flex items-center justify-between text-[11px] font-mono font-bold uppercase tracking-wider text-purple-400">
          <span>🎯 Top ET Prime Score</span>
          <span>💎</span>
        </div>
        <div class="text-2xl font-black font-mono mt-1 text-white theme-text-primary" id="kpiEtPrimeCount">134</div>
        <div class="text-[11px] text-slate-400 theme-text-muted mt-0.5">Refinitiv Score &ge; 8/10</div>
      </div>

      <!-- KPI 5: MA Pullback Support -->
      <div id="kpiCard-MA_PULLBACK" onclick="filterByPreset('MA_PULLBACK')" class="cursor-pointer p-3 rounded-xl bg-slate-900/80 theme-card border border-blue-500/30 border-l-4 border-l-blue-400 hover:glow-blue transition group">
        <div class="flex items-center justify-between text-[11px] font-mono font-bold uppercase tracking-wider text-blue-400">
          <span>💎 MA Pullback Support</span>
          <span>⚡</span>
        </div>
        <div class="text-2xl font-black font-mono mt-1 text-white theme-text-primary" id="kpiPullbackCount">96</div>
        <div class="text-[11px] text-slate-400 theme-text-muted mt-0.5">High Growth near 50/200 MA</div>
      </div>

    </div>

    <!-- ========================================== -->
    <!-- LIVE TICKER STREAM & MARKET BREADTH BAR    -->
    <!-- ========================================== -->
    <div class="max-w-[1720px] mx-auto mt-3 pt-3 border-t border-slate-800/60 theme-border flex flex-wrap items-center justify-between gap-3 text-xs">
      
      <div class="flex items-center flex-wrap gap-2.5">
        <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono font-bold text-[11px]">
          <span class="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
          LIVE TICKER STREAM
        </span>
        <span class="text-slate-400 theme-text-muted font-mono" id="lastSyncedText">
          __SYNC_BANNER_TEXT__
        </span>
        <div class="flex items-center gap-2 px-2.5 py-0.5 rounded bg-slate-900 theme-bg-subtle border border-slate-800 theme-border font-mono text-[11px]">
          <span class="text-emerald-400 font-bold">Adv: <strong id="statAdv">0</strong></span>
          <span class="text-slate-600">|</span>
          <span class="text-rose-400 font-bold">Dec: <strong id="statDec">0</strong></span>
          <span class="text-slate-600">|</span>
          <span class="text-slate-400">Unch: <strong id="statUnch">0</strong></span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <label class="flex items-center gap-1.5 cursor-pointer text-slate-400 theme-text-muted hover:text-white transition select-none">
          <input type="checkbox" id="autoTickCheck" checked onchange="toggleAutoTick(this.checked)" class="rounded bg-slate-900 border-slate-700 text-sky-500 focus:ring-0">
          <span>Auto-Tick (20s)</span>
        </label>
        <button onclick="checkLiveServer()" class="px-3 py-1 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 font-semibold transition active:scale-95">
          ⚡ Refresh Live Quotes
        </button>
      </div>

    </div>

  </header>

  <!-- ========================================== -->
  <!-- MAIN CONTROLS, WATCHLISTS & PRESETS        -->
  <!-- ========================================== -->
  <div class="max-w-[1720px] mx-auto px-4 lg:px-8 py-5">
    
    <!-- 1. SAVED WATCHLISTS & BASKETS TOOLBAR (Top Institutional Baskets) -->
    <div class="bg-slate-900/90 theme-card rounded-2xl p-4 border border-slate-800 theme-border shadow-lg mb-4">
      <div class="flex items-center justify-between pb-2.5 mb-2.5 border-b border-slate-800/80 theme-border">
        <div class="flex items-center gap-2">
          <span class="text-xs font-black uppercase tracking-wider text-sky-400 font-mono">🎯 Institutional Watchlists & Custom Baskets:</span>
          <span class="text-[11px] text-slate-400 theme-text-muted">Click any basket to isolate & analyze portfolio groups</span>
        </div>
        <button onclick="resetBasketsToDefault()" class="text-[11px] text-slate-500 hover:text-slate-300 transition underline">
          Reset to Defaults
        </button>
      </div>

      <!-- Watchlist Badges Row -->
      <div class="flex items-center gap-2 overflow-x-auto pb-1 text-xs no-scrollbar flex-wrap" id="watchlistsBar">
        <button onclick="setWatchlist('ALL')" id="wlBtn-ALL" class="filter-chip active px-3.5 py-1.5 rounded-xl bg-sky-500 text-white font-bold shadow-sm">
          All Universe (424)
        </button>
        <button onclick="setWatchlist('MY_BUCKET')" id="wlBtn-MY_BUCKET" class="filter-chip px-3 py-1.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 font-bold">
          🗂️ My Bucket (<span id="pillBucketCount">60</span>)
        </button>
        <button onclick="setWatchlist('STAR_STOCKS')" id="wlBtn-STAR_STOCKS" class="filter-chip px-3 py-1.5 rounded-xl bg-amber-950/40 text-amber-300 border border-amber-500/30 hover:bg-amber-950/60 font-medium">
          ⭐ Star Stocks (23)
        </button>
        <button onclick="setWatchlist('35_MASTER')" id="wlBtn-35_MASTER" class="filter-chip px-3 py-1.5 rounded-xl bg-sky-950/40 text-sky-300 border border-sky-500/30 hover:bg-sky-950/60 font-medium">
          🌐 35 Master (35)
        </button>
        <button onclick="setWatchlist('ACTIVE_CORE')" id="wlBtn-ACTIVE_CORE" class="filter-chip px-3 py-1.5 rounded-xl bg-emerald-950/40 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-950/60 font-medium">
          🎯 Active Core (16)
        </button>
        <button onclick="setWatchlist('READY_TO_BUY')" id="wlBtn-READY_TO_BUY" class="filter-chip px-3 py-1.5 rounded-xl bg-emerald-950/30 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-950/50 font-medium">
          🟢 Ready to Buy (10)
        </button>
        <button onclick="setWatchlist('WAIT_ALERT')" id="wlBtn-WAIT_ALERT" class="filter-chip px-3 py-1.5 rounded-xl bg-blue-950/40 text-blue-300 border border-blue-500/30 hover:bg-blue-950/60 font-medium">
          ⏸️ Wait Alert (6)
        </button>
        <button onclick="setWatchlist('FAVORITES')" id="wlBtn-FAVORITES" class="filter-chip px-3 py-1.5 rounded-xl bg-purple-950/40 text-purple-300 border border-purple-500/30 hover:bg-purple-950/60 font-medium">
          ⭐ Favorites (5)
        </button>
        <button onclick="setWatchlist('QUARANTINE')" id="wlBtn-QUARANTINE" class="filter-chip px-3 py-1.5 rounded-xl bg-rose-950/40 text-rose-300 border border-rose-500/30 hover:bg-rose-950/60 font-medium">
          ⚠️ Quarantine (8)
        </button>
        <button onclick="setWatchlist('ELIMINATED')" id="wlBtn-ELIMINATED" class="filter-chip px-3 py-1.5 rounded-xl bg-slate-800 text-slate-400 border border-slate-700 hover:bg-slate-700 font-medium">
          ❌ Eliminated (6)
        </button>

        <!-- Dynamic User Custom Baskets Container -->
        <span id="customBasketsContainer" class="contents"></span>

        <!-- Add Custom Basket Button -->
        <button onclick="openNewBasketModal()" class="px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-sky-400 border border-slate-700 font-semibold text-xs flex items-center gap-1 transition">
          <span>➕</span> New Basket
        </button>
      </div>

      <!-- 2. INSTITUTIONAL STRATEGY SCREENER PRESETS ROW -->
      <div class="pt-3 mt-3 border-t border-slate-800/80 theme-border">
        <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar flex-wrap" id="presetsBar">
          <span class="text-slate-400 theme-text-muted font-bold whitespace-nowrap mr-1 font-mono">⚡ 20+ Strategy Presets:</span>
          
          <button onclick="setPreset('ALL')" id="presetBtn-ALL" class="filter-chip active px-2.5 py-1 rounded-lg bg-sky-500 text-white font-semibold">
            All Presets
          </button>
          <button onclick="setPreset('INTRADAY_RADAR')" id="presetBtn-INTRADAY_RADAR" class="filter-chip px-2.5 py-1 rounded-lg bg-amber-500/15 text-amber-300 border border-amber-500/40 hover:bg-amber-500/25 font-bold">
            ⚡ Intraday Radar (Today)
          </button>
          <button onclick="setPreset('SWING_RADAR')" id="presetBtn-SWING_RADAR" class="filter-chip px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/25 font-bold">
            🚀 Swing Buy Radar (2-5D)
          </button>
          <button onclick="setPreset('PERFECT_RADAR')" id="presetBtn-PERFECT_RADAR" class="filter-chip px-2.5 py-1 rounded-lg bg-purple-950/40 text-purple-300 border border-purple-500/50 hover:bg-purple-900/40 font-black">
            🌟 Perfect Condition Alert
          </button>
          <button onclick="openRadarModal('tracker')" class="filter-chip px-2.5 py-1 rounded-lg bg-sky-950/40 text-sky-300 border border-sky-500/40 hover:bg-sky-900/40 font-bold">
            📌 Signal Journal (<span id="trackerNavCount">0</span>)
          </button>
          <button onclick="setPreset('1D_GAINERS')" id="presetBtn-1D_GAINERS" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-emerald-400 border border-emerald-500/30 hover:bg-emerald-950/30">
            📈 1D Gainers (&ge; +1.5%)
          </button>
          <button onclick="setPreset('1D_DIPS')" id="presetBtn-1D_DIPS" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-rose-400 border border-rose-500/30 hover:bg-rose-950/30">
            🔻 1D Dips (&le; -1.0%)
          </button>
          <button onclick="setPreset('1W_LEADERS')" id="presetBtn-1W_LEADERS" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-sky-400 border border-sky-500/30 hover:bg-sky-950/30">
            ⚡ 1W Leaders (&ge; +4.0%)
          </button>
          <button onclick="setPreset('MASTER_ALPHA')" id="presetBtn-MASTER_ALPHA" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-amber-400 border border-amber-500/30 hover:bg-amber-950/30">
            👑 Master Alpha Leaders (&ge; 88)
          </button>
          <button onclick="setPreset('TRIPLE_CROWN')" id="presetBtn-TRIPLE_CROWN" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-amber-300 border border-amber-500/20 hover:bg-amber-950/30">
            🏆 Triple-Crown (&ge; 88)
          </button>
          <button onclick="setPreset('HIGH_FORECAST')" id="presetBtn-HIGH_FORECAST" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-sky-300 border border-sky-500/30 hover:bg-sky-950/30">
            🚀 High Forecast (&ge; +20%)
          </button>
          <button onclick="setPreset('MOD_FORECAST')" id="presetBtn-MOD_FORECAST" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-sky-400 border border-slate-700 hover:bg-sky-950/30">
            🎯 Mod Forecast (+10% to +20%)
          </button>
          <button onclick="setPreset('STRONG_BUY_CONSENSUS')" id="presetBtn-STRONG_BUY_CONSENSUS" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-emerald-300 border border-emerald-500/30 hover:bg-emerald-950/30">
            ⭐ Strong Buy (&ge; 80%)
          </button>
          <button onclick="setPreset('EUPHORIC_MOOD')" id="presetBtn-EUPHORIC_MOOD" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-orange-400 border border-orange-500/30 hover:bg-orange-950/30">
            🔥 Euphoric Mood (&ge; 90)
          </button>
          <button onclick="setPreset('POSITIVE_MOOD')" id="presetBtn-POSITIVE_MOOD" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-emerald-400 border border-slate-700 hover:bg-emerald-950/30">
            🟢 Positive Mood (75-89)
          </button>
          <button onclick="setPreset('DIP_SUPPORT')" id="presetBtn-DIP_SUPPORT" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-cyan-300 border border-cyan-500/30 hover:bg-cyan-950/30">
            💎 Dip Buy at Support
          </button>
          <button onclick="setPreset('DEEP_VALUE')" id="presetBtn-DEEP_VALUE" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-indigo-300 border border-indigo-500/30 hover:bg-indigo-950/30">
            📉 Deep Value (Disc &ge; 20%)
          </button>
          <button onclick="setPreset('FAIR_ACCUMULATE')" id="presetBtn-FAIR_ACCUMULATE" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-slate-300 border border-slate-700 hover:bg-slate-800">
            ⚖️ Fair Accumulate (5%-20%)
          </button>
          <button onclick="setPreset('STAGE_2_UPTREND')" id="presetBtn-STAGE_2_UPTREND" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-emerald-400 border border-emerald-500/20 hover:bg-emerald-950/30">
            🚀 Stage 2 Strong Uptrend
          </button>
          <button onclick="setPreset('BULLISH_RSI')" id="presetBtn-BULLISH_RSI" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-sky-400 border border-slate-700 hover:bg-sky-950/30">
            ☑️ Bullish RSI (50-65)
          </button>
          <button onclick="setPreset('OVERSOLD_RSI')" id="presetBtn-OVERSOLD_RSI" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-purple-400 border border-purple-500/30 hover:bg-purple-950/30">
            ❄️ Oversold (RSI &lt; 40)
          </button>
          <button onclick="setPreset('BREAKOUT_52W')" id="presetBtn-BREAKOUT_52W" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-amber-300 border border-amber-500/20 hover:bg-amber-950/30">
            ⛰️ 52W High Breakout (&lt; -10%)
          </button>
          <button onclick="setPreset('HYPER_PAT')" id="presetBtn-HYPER_PAT" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-rose-400 border border-rose-500/30 hover:bg-rose-950/30">
            ⚡ YoY PAT Hyper-Growth (&gt; 50%)
          </button>
          <button onclick="setPreset('GROWTH_STREAKS')" id="presetBtn-GROWTH_STREAKS" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-amber-400 border border-slate-700 hover:bg-slate-800">
            🏆 Growth Streaks (&ge; 3 Qtrs)
          </button>
          <button onclick="setPreset('VOL_SURGE')" id="presetBtn-VOL_SURGE" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-amber-400 border border-amber-500/20 hover:bg-amber-950/30">
            🔥 Vol Surge (&gt; 1.5x)
          </button>
          <button onclick="setPreset('HIGH_RR')" id="presetBtn-HIGH_RR" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-indigo-400 border border-indigo-500/20 hover:bg-indigo-950/30">
            🎯 High R:R (&ge; 1:2.5)
          </button>
          <button onclick="setPreset('LARGE_CAP')" id="presetBtn-LARGE_CAP" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-slate-300 border border-slate-700 hover:bg-slate-800">
            🏢 Large-Cap Quality
          </button>
          <button onclick="setPreset('MID_CAP')" id="presetBtn-MID_CAP" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-slate-300 border border-slate-700 hover:bg-slate-800">
            🚀 Mid-Cap Compounders
          </button>
          <button onclick="setPreset('SMALL_CAP')" id="presetBtn-SMALL_CAP" class="filter-chip px-2.5 py-1 rounded-lg bg-slate-900 theme-bg-subtle text-slate-300 border border-slate-700 hover:bg-slate-800">
            💎 Small & Micro Cap Alpha
          </button>
        </div>
      </div>

    </div>

    <!-- SEARCH & TIMEFRAME CONTROL BAR -->
    <div class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 bg-slate-900/80 theme-card border border-slate-800 theme-border rounded-2xl p-4 shadow-lg">
      
      <!-- Search Input -->
      <div class="relative flex-1">
        <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>
        <input 
          type="text" 
          id="searchInput" 
          placeholder="Search 424 stocks by name, symbol (e.g. RELIANCE, Tata, Dixon, Renewable, Solar)..." 
          class="w-full pl-10 pr-12 py-2.5 bg-slate-950/80 theme-input border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition font-sans"
          oninput="handleSearch(this.value)"
        >
        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-xs text-slate-500 font-mono">
          <span class="px-1.5 py-0.5 rounded bg-slate-800 theme-bg-subtle border border-slate-700 theme-border">/</span>
        </div>
      </div>

      <!-- Timeframe Switcher -->
      <div class="flex items-center gap-2 bg-slate-950/80 theme-bg-subtle p-1 rounded-xl border border-slate-800 theme-border">
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 theme-text-muted px-2.5">Timeframe:</span>
        <button onclick="setTimeframe('15M')" id="tfBtn-15M" class="px-3 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-400 theme-text-muted hover:text-white transition">
          15M / 1H
        </button>
        <button onclick="setTimeframe('1D')" id="tfBtn-1D" class="px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-sky-500 text-white shadow-md transition">
          Daily (1D)
        </button>
        <button onclick="setTimeframe('1W')" id="tfBtn-1W" class="px-3 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-400 theme-text-muted hover:text-white transition">
          Weekly (1W)
        </button>
        <button onclick="setTimeframe('1M')" id="tfBtn-1M" class="px-3 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-400 theme-text-muted hover:text-white transition">
          Monthly (1M)
        </button>
      </div>

    </div>

    <!-- SIGNAL ACTION TABS (Dynamically adapted to active timeframe) -->
    <div class="flex items-center gap-2 overflow-x-auto py-3.5 no-scrollbar" id="actionTabsContainer">
      <button onclick="setActionFilter('ALL')" id="actionBtn-ALL" class="whitespace-nowrap px-4 py-2 rounded-xl text-xs font-bold bg-sky-500 text-white shadow-sm transition">
        All Verdicts (424)
      </button>
      <button onclick="setActionFilter('STRONG BUY')" id="actionBtn-STRONG-BUY" class="whitespace-nowrap px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 theme-bg-subtle text-slate-300 theme-text-secondary hover:bg-emerald-950/50 hover:text-emerald-400 border border-slate-800 theme-border transition">
        🟢 Strong Buy (<span id="filterCountStrongBuy">0</span>)
      </button>
      <button onclick="setActionFilter('BUY ON DIPS')" id="actionBtn-BUY-ON-DIPS" class="whitespace-nowrap px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 theme-bg-subtle text-slate-300 theme-text-secondary hover:bg-emerald-950/30 hover:text-emerald-300 border border-slate-800 theme-border transition">
        🟢 Buy on Dips (<span id="filterCountBuyDips">0</span>)
      </button>
      <button onclick="setActionFilter('WAIT')" id="actionBtn-WAIT" class="whitespace-nowrap px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 theme-bg-subtle text-slate-300 theme-text-secondary hover:bg-amber-950/50 hover:text-amber-400 border border-slate-800 theme-border transition">
        🟡 Wait / Watch (<span id="filterCountWait">0</span>)
      </button>
      <button onclick="setActionFilter('HOLD')" id="actionBtn-HOLD" class="whitespace-nowrap px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 theme-bg-subtle text-slate-300 theme-text-secondary hover:bg-sky-950/50 hover:text-sky-400 border border-slate-800 theme-border transition">
        🔵 Hold Trend (<span id="filterCountHold">0</span>)
      </button>
      <button onclick="setActionFilter('SELL')" id="actionBtn-SELL" class="whitespace-nowrap px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 theme-bg-subtle text-slate-300 theme-text-secondary hover:bg-rose-950/50 hover:text-rose-400 border border-slate-800 theme-border transition">
        🔴 Sell / Exit (<span id="filterCountSell">0</span>)
      </button>
    </div>

    <!-- DROPDOWN FILTERS & STATUS BAR -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-3">
      
      <div class="flex items-center gap-2 flex-wrap text-xs">
        <!-- Sector Filter -->
        <select id="sectorSelect" onchange="handleSectorFilter(this.value)" class="bg-slate-900 theme-input border border-slate-800 theme-border text-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500">
          <option value="ALL">All Sectors</option>
        </select>

        <!-- Market Cap Filter -->
        <select id="mcapSelect" onchange="handleMcapFilter(this.value)" class="bg-slate-900 theme-input border border-slate-800 theme-border text-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500">
          <option value="ALL">All Cap Tiers</option>
          <option value="Large Cap">Large Cap</option>
          <option value="Mid Cap">Mid Cap</option>
          <option value="Small Cap">Small Cap</option>
          <option value="Micro Cap">Micro Cap</option>
        </select>

        <!-- Sort Order Selector -->
        <select id="sortSelect" onchange="handleDropdownSort(this.value)" class="bg-slate-900 theme-input border border-slate-800 theme-border text-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500 font-mono">
          <option value="tech_score_desc">Tech Score: High to Low</option>
          <option value="master_score_desc">Master Alpha: High to Low</option>
          <option value="action_desc">Verdict: Bullish to Bearish</option>
          <option value="action_asc">Verdict: Bearish to Bullish</option>
          <option value="forecast_upside_desc">Forecast Upside: Highest</option>
          <option value="day_change_pct_desc">1D Gainers: Highest</option>
          <option value="day_change_pct_asc">1D Losers: Lowest</option>
          <option value="cmp_desc">CMP: High to Low</option>
          <option value="cmp_asc">CMP: Low to High</option>
          <option value="rr_ratio_desc">Risk/Reward: Highest</option>
          <option value="dist_52w_high_desc">Nearest to 52W High</option>
          <option value="symbol_asc">Symbol: A to Z</option>
        </select>

        <!-- Quick Reset Filters -->
        <button onclick="resetFilters()" class="px-2.5 py-1.5 rounded-lg bg-slate-800 theme-bg-subtle hover:bg-slate-700 text-slate-300 theme-text-secondary border border-slate-700 theme-border transition text-xs font-medium">
          Reset Filters
        </button>
      </div>

      <div class="flex items-center gap-3 text-xs">
        <div class="text-slate-400 theme-text-muted">
          Showing <span id="displayedCount" class="font-mono font-bold text-white theme-text-primary">424</span> of <span class="font-mono font-bold text-white theme-text-primary">424</span> stocks
        </div>
        <div class="flex items-center gap-1.5">
          <label class="text-slate-400 theme-text-muted">Page Size:</label>
          <select id="pageSizeSelect" onchange="changePageSize(this.value)" class="bg-slate-900 theme-input border border-slate-800 theme-border text-slate-300 rounded px-2 py-0.5 font-mono">
            <option value="24">24</option>
            <option value="48" selected>48</option>
            <option value="96">96</option>
            <option value="424">All (424)</option>
          </select>
        </div>
      </div>

    </div>

    <!-- ========================================== -->
    <!-- CARDS GRID VIEW CONTAINER                  -->
    <!-- ========================================== -->
    <div id="cardsGridContainer" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 pt-2">
      <!-- Dynamically populated via JS -->
    </div>

    <!-- ========================================== -->
    <!-- MASTER TABLE VIEW CONTAINER                -->
    <!-- (Bi-Directional Ascending/Descending Sort)  -->
    <!-- ========================================== -->
    <div id="tableViewContainer" class="hidden overflow-x-auto rounded-2xl border border-slate-800 theme-border bg-slate-900/70 theme-card shadow-xl mt-2">
      <table class="w-full text-left border-collapse text-xs">
        <thead class="bg-slate-950 theme-table-header text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800 theme-border sticky top-0 z-10 select-none">
          <tr>
            <th class="p-3 text-center w-10">⭐</th>
            <th class="p-3.5 sortable" onclick="sortTable('symbol')">Stock / Sector <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('cmp')">CMP (₹) <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('day_change_pct')">1D % <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('chg_5m_pct')">5M % <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('action')"><span id="tableHeaderVerdict">Verdict (1D)</span> <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('entry_min')">Entry Zone <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('stop_loss')">Stop Loss <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('target_1')">Target 1 <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('target_2')">Target 2 <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('rr_ratio')">R:R <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('s1')"><span id="tableHeaderSupport">Support / Resist (1D)</span> <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('rsi')"><span id="tableHeaderRsi">RSI (1D)</span> <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('dist_52w_high')">Dist 52W <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('tech_score')">Tech <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('master_score')">Master <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('forecast_upside')">Upside % <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center">Inspect</th>
          </tr>
        </thead>
        <tbody id="tableBody" class="divide-y divide-slate-800/60 theme-border font-sans">
          <!-- Dynamically populated via JS -->
        </tbody>
      </table>
    </div>

    <!-- PAGINATION CONTROLS -->
    <div id="paginationContainer" class="flex items-center justify-between py-6 mt-4 border-t border-slate-800 theme-border text-xs">
      <div class="text-slate-400 theme-text-muted font-mono" id="paginationInfo">
        Showing 1-48 of 424
      </div>
      <div class="flex items-center gap-2" id="paginationButtons">
        <!-- Dynamically generated pagination buttons -->
      </div>
    </div>

  </div>

  <!-- ========================================== -->
  <!-- 360° DEEP DIVE TECHNICAL & FUNDA MODAL     -->
  <!-- ========================================== -->
  <div id="detailModal" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-6 overflow-y-auto modal-backdrop">
    <div class="relative w-full max-w-5xl bg-[#0B1120] theme-card border border-slate-700 rounded-2xl shadow-2xl overflow-hidden my-auto max-h-[95vh] flex flex-col">
      
      <!-- Modal Top Bar -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-800 theme-border bg-slate-900/80 theme-bg-subtle sticky top-0 z-20">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center font-mono font-bold text-sky-400 text-base" id="modalLogo">
            SYM
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-bold text-white theme-text-primary tracking-tight" id="modalName">Company Name</h2>
              <span class="text-xs px-2 py-0.5 rounded bg-slate-800 theme-bg-surface text-slate-300 font-mono" id="modalSym">SYMBOL</span>
              <span class="text-xs px-2 py-0.5 rounded bg-slate-800 theme-bg-surface text-sky-400 font-mono" id="modalSector">Sector</span>
              <span class="text-xs px-2 py-0.5 rounded bg-slate-800 theme-bg-surface text-slate-400 font-mono" id="modalMcap">Cap Tier</span>
              <button id="modalBucketStar" onclick="toggleModalStockBucket()" class="star-btn text-base ml-1" title="Toggle My Bucket">☆</button>
            </div>
            <div class="flex items-center gap-4 text-xs font-mono text-slate-400 theme-text-muted mt-1">
              <span>CMP: <strong class="text-white theme-text-primary font-bold text-sm" id="modalCMP">₹0.00</strong></span>
              <span id="modalChg" class="font-bold">+0.00%</span>
              <span>Day: <span id="modalDayRange" class="text-slate-300 theme-text-secondary">₹0 - ₹0</span></span>
              <span>52W: <span id="modal52WRange" class="text-slate-300 theme-text-secondary">₹0 - ₹0</span></span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <a id="modalScreenerLink" href="#" target="_blank" class="px-2.5 py-1 rounded bg-slate-800 theme-bg-surface hover:bg-slate-700 text-xs font-mono text-slate-300 theme-text-primary transition">
            Screener ↗
          </a>
          <a id="modalTvLink" href="#" target="_blank" class="px-2.5 py-1 rounded bg-sky-500/20 hover:bg-sky-500/30 text-xs font-mono text-sky-400 transition">
            TradingView ↗
          </a>
          <button onclick="closeModal()" class="p-1.5 rounded-lg bg-slate-800 theme-bg-surface hover:bg-slate-700 text-slate-400 hover:text-white transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
      </div>

      <!-- Modal Body (Scrollable) -->
      <div class="overflow-y-auto p-6 space-y-6 flex-1 text-slate-200 theme-text-primary">
        
        <!-- SECTION 1: HERO ACTION BLUEPRINT & TRADE LEVELS -->
        <div id="modalHeroBox" class="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 theme-bg-surface border border-emerald-500/30 glow-green">
          <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div>
              <div class="flex items-center gap-2.5">
                <span id="modalHeroBadge" class="px-3 py-1 rounded-full text-xs font-black tracking-wider uppercase font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                  STRONG BUY
                </span>
                <span class="text-sm font-semibold text-white theme-text-primary" id="modalSetupType">Trend-Following Momentum Breakout</span>
              </div>
              <p class="text-xs text-slate-400 theme-text-muted mt-1.5">
                Primary Pattern: <strong class="text-sky-400" id="modalPatternBadge">Bullish Engulfing</strong> • Confluence Score: <strong class="text-emerald-400 font-mono" id="modalConfluenceScore">88%</strong>
              </p>
            </div>
            
            <div class="flex items-center gap-3">
              <div class="text-right">
                <div class="text-[10px] font-mono uppercase tracking-wider text-slate-400 theme-text-muted">Technical Score</div>
                <div class="text-2xl font-black font-mono text-emerald-400" id="modalScoreVal">94/100</div>
              </div>
              <button onclick="copyTradeAlert()" class="px-3 py-2 rounded-xl bg-sky-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow hover:bg-sky-400 transition">
                📋 Copy Alert
              </button>
              <button onclick="trackStockFromModal()" class="px-3 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-emerald-500 text-slate-950 font-extrabold text-xs flex items-center gap-1.5 shadow hover:brightness-110 transition active:scale-95">
                📌 Track on Radar
              </button>
            </div>
          </div>

          <!-- Trade Execution Levels Bar -->
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-4 text-xs font-mono">
            <div class="p-2.5 rounded-xl bg-slate-950/60 theme-bg-subtle border border-slate-800 theme-border">
              <div class="text-slate-400 theme-text-muted text-[10px] uppercase">Recommended Entry</div>
              <div class="font-bold text-sky-400 mt-0.5 text-sm" id="modalEntryZone">₹0 - ₹0</div>
              <div class="text-[10px] text-slate-500">Optimal Fill Zone</div>
            </div>
            <div class="p-2.5 rounded-xl bg-rose-950/20 theme-bg-subtle border border-rose-500/20">
              <div class="text-rose-400 text-[10px] uppercase">Hard Stop-Loss</div>
              <div class="font-bold text-rose-400 mt-0.5 text-sm" id="modalSL">₹0.00</div>
              <div class="text-[10px] text-rose-500/80" id="modalSLRisk">Risk: -0.0%</div>
            </div>
            <div class="p-2.5 rounded-xl bg-emerald-950/20 theme-bg-subtle border border-emerald-500/20">
              <div class="text-emerald-400 text-[10px] uppercase">Target 1 (Base)</div>
              <div class="font-bold text-emerald-400 mt-0.5 text-sm" id="modalT1">₹0.00</div>
              <div class="text-[10px] text-emerald-500" id="modalT1Gain">+0.0%</div>
            </div>
            <div class="p-2.5 rounded-xl bg-emerald-950/30 theme-bg-subtle border border-emerald-500/30">
              <div class="text-emerald-300 text-[10px] uppercase">Target 2 (Swing)</div>
              <div class="font-bold text-emerald-300 mt-0.5 text-sm" id="modalT2">₹0.00</div>
              <div class="text-[10px] text-emerald-400" id="modalT2Gain">+0.0%</div>
            </div>
            <div class="p-2.5 rounded-xl bg-emerald-950/40 theme-bg-subtle border border-emerald-500/40">
              <div class="text-emerald-200 text-[10px] uppercase">Target 3 (Runner)</div>
              <div class="font-bold text-emerald-200 mt-0.5 text-sm" id="modalT3">₹0.00</div>
              <div class="text-[10px] text-emerald-300">Macro Extension</div>
            </div>
            <div class="p-2.5 rounded-xl bg-indigo-950/30 theme-bg-subtle border border-indigo-500/30">
              <div class="text-indigo-300 text-[10px] uppercase">Risk / Reward</div>
              <div class="font-bold text-indigo-300 mt-0.5 text-sm" id="modalRR">1 : 3.0</div>
              <div class="text-[10px] text-indigo-400">Asymmetric</div>
            </div>
          </div>
        </div>

        <!-- SECTION 2: INSTITUTIONAL & FUNDAMENTAL ALPHA SUITE (Integrated 360°) -->
        <div class="p-5 rounded-2xl bg-slate-900/90 theme-bg-surface border border-slate-800 theme-border">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800/80 theme-border">
            <h3 class="text-sm font-bold text-white theme-text-primary flex items-center gap-2">
              <span>🏛️</span> Institutional Intelligence & Fundamental Confluence
            </h3>
            <span class="text-xs font-mono text-slate-400 theme-text-muted" id="modalMasterRankText">Rank #1 / 424</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 text-xs font-mono">
            
            <!-- Master Score Card -->
            <div class="p-3 rounded-xl bg-slate-950/70 theme-bg-subtle border border-amber-500/30">
              <div class="text-amber-400 text-[11px] uppercase font-bold">Master Alpha Score</div>
              <div class="text-2xl font-black text-white theme-text-primary mt-1" id="modalMasterScore">90.4</div>
              <div class="text-[10px] text-slate-400 theme-text-muted mt-0.5" id="modalMasterCategory">🌟 Master Alpha Leader</div>
            </div>

            <!-- Wall Street / ET 1Y Forecast -->
            <div class="p-3 rounded-xl bg-slate-950/70 theme-bg-subtle border border-sky-500/30">
              <div class="text-sky-400 text-[11px] uppercase font-bold">1-Year Target & Upside</div>
              <div class="text-2xl font-black text-emerald-400 mt-1" id="modalForecastUpside">+24.9%</div>
              <div class="text-[10px] text-slate-400 theme-text-muted mt-0.5" id="modalForecastTarget">Mean Target: ₹402</div>
            </div>

            <!-- Consensus Rating -->
            <div class="p-3 rounded-xl bg-slate-950/70 theme-bg-subtle border border-emerald-500/30">
              <div class="text-emerald-400 text-[11px] uppercase font-bold">Analyst Consensus</div>
              <div class="text-lg font-black text-white theme-text-primary mt-1" id="modalConsensusRating">Strong Buy</div>
              <div class="text-[10px] text-slate-400 theme-text-muted mt-0.5" id="modalConsensusBreakdown">6 Analysts (100% Buy)</div>
            </div>

            <!-- ET Prime / Refinitiv Diagnostic -->
            <div class="p-3 rounded-xl bg-slate-950/70 theme-bg-subtle border border-purple-500/30">
              <div class="text-purple-400 text-[11px] uppercase font-bold">ET Prime / Refinitiv Score</div>
              <div class="text-2xl font-black text-purple-400 mt-1" id="modalEtScore">9 / 10</div>
              <div class="text-[10px] text-slate-400 theme-text-muted mt-0.5" id="modalEtOutlook">POSITIVE Outlook</div>
            </div>

          </div>

          <!-- Fundamental Multiples & Growth Row -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs font-mono">
            <div class="p-2.5 rounded-lg bg-slate-950/50 theme-bg-subtle border border-slate-800 theme-border">
              <span class="text-slate-400 theme-text-muted block text-[10px]">Valuation Discount</span>
              <strong class="text-emerald-400 text-sm" id="modalValDiscount">+0.0%</strong>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-950/50 theme-bg-subtle border border-slate-800 theme-border">
              <span class="text-slate-400 theme-text-muted block text-[10px]">Latest YoY PAT Growth</span>
              <strong class="text-sky-400 text-sm" id="modalYoyPat">+0.0%</strong>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-950/50 theme-bg-subtle border border-slate-800 theme-border">
              <span class="text-slate-400 theme-text-muted block text-[10px]">P/E & P/B Multiples</span>
              <strong class="text-white theme-text-primary text-sm" id="modalPePb">17.3x / 8.5x</strong>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-950/50 theme-bg-subtle border border-slate-800 theme-border">
              <span class="text-slate-400 theme-text-muted block text-[10px]">Consecutive PAT Streak</span>
              <strong class="text-amber-400 text-sm" id="modalPatStreak">5 Quarters</strong>
            </div>
          </div>

          <!-- Watchlist Membership Badges -->
          <div class="mt-3 pt-3 border-t border-slate-800/60 theme-border flex items-center gap-2 flex-wrap text-xs">
            <span class="text-slate-400 theme-text-muted font-mono text-[11px]">Watchlist Memberships:</span>
            <div id="modalWatchlistPills" class="flex items-center gap-1.5 flex-wrap">
              <!-- Dynamically populated -->
            </div>
          </div>
        </div>

        <!-- SECTION 3: INTERACTIVE HTML5 CANVAS CANDLESTICK CHART -->
        <div class="p-5 rounded-2xl bg-slate-900/90 theme-bg-surface border border-slate-800 theme-border">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800/80 theme-border">
            <h3 class="text-sm font-bold text-white theme-text-primary flex items-center gap-2">
              <span>📊</span> Price Action & Indicator Overlays (Daily Candlesticks)
            </h3>
            <div class="flex items-center gap-3 text-xs font-mono">
              <span class="flex items-center gap-1 text-sky-400"><span class="h-2 w-2 rounded-full bg-sky-400"></span> 20 EMA</span>
              <span class="flex items-center gap-1 text-amber-400"><span class="h-2 w-2 rounded-full bg-amber-400"></span> 50 EMA</span>
              <span class="flex items-center gap-1 text-purple-400"><span class="h-2 w-2 rounded-full bg-purple-400"></span> 200 SMA</span>
            </div>
          </div>
          <div class="mt-4 w-full h-72 relative bg-slate-950/90 theme-bg-subtle rounded-xl overflow-hidden border border-slate-800 theme-border">
            <canvas id="candleCanvas" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- SECTION 4: MULTI-TIMEFRAME CONFLUENCE MATRIX -->
        <div class="p-5 rounded-2xl bg-slate-900/90 theme-bg-surface border border-slate-800 theme-border">
          <h3 class="text-sm font-bold text-white theme-text-primary pb-3 border-b border-slate-800/80 theme-border flex items-center gap-2">
            <span>🌐</span> Multi-Timeframe Confluence Matrix
          </h3>
          <div class="overflow-x-auto mt-3">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-950/80 theme-bg-subtle text-slate-400 font-mono uppercase">
                <tr>
                  <th class="p-3">Timeframe</th>
                  <th class="p-3">Trend Posture</th>
                  <th class="p-3 text-center">RSI</th>
                  <th class="p-3">MACD</th>
                  <th class="p-3 text-center">Support</th>
                  <th class="p-3 text-center">Resistance</th>
                  <th class="p-3">Trigger Setup</th>
                  <th class="p-3 text-center">Verdict</th>
                </tr>
              </thead>
              <tbody id="modalTimeframeTableBody" class="divide-y divide-slate-800/60 theme-border">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- SECTION 5: 6-PANEL TECHNICAL INDICATORS DEEP-DIVE -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs font-mono">
          
          <!-- Moving Averages -->
          <div class="p-4 rounded-xl bg-slate-900/70 theme-bg-surface border border-slate-800 theme-border">
            <div class="text-sky-400 font-bold uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
              <span>Moving Averages</span>
              <span id="panelMaCross">🟢 Golden Cross</span>
            </div>
            <div class="space-y-1.5 text-slate-300 theme-text-secondary">
              <div class="flex justify-between"><span>EMA 9 / 20:</span> <strong id="panelEma9_20" class="text-white theme-text-primary">₹0 / ₹0</strong></div>
              <div class="flex justify-between"><span>EMA 50:</span> <strong id="panelEma50" class="text-white theme-text-primary">₹0</strong></div>
              <div class="flex justify-between"><span>SMA 200:</span> <strong id="panelSma200" class="text-white theme-text-primary">₹0</strong></div>
              <div class="flex justify-between"><span>Dist from 200 SMA:</span> <strong id="panelDistSma200" class="text-emerald-400">+0.0%</strong></div>
              <div class="flex justify-between text-[11px] pt-1 text-slate-400"><span id="panelMaAlign">Bullish Stack</span></div>
            </div>
          </div>

          <!-- Oscillators & Momentum -->
          <div class="p-4 rounded-xl bg-slate-900/70 theme-bg-surface border border-slate-800 theme-border">
            <div class="text-purple-400 font-bold uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
              <span>Oscillators</span>
              <span id="panelRsiZone">Bullish Zone</span>
            </div>
            <div class="space-y-1.5 text-slate-300 theme-text-secondary">
              <div class="flex justify-between"><span>14-Day RSI:</span> <strong id="panelRsiVal" class="text-emerald-400">55.0</strong></div>
              <div class="flex justify-between"><span>MACD Hist:</span> <strong id="panelMacdHist" class="text-emerald-400">+1.25</strong></div>
              <div class="flex justify-between"><span>Stochastic (14,3,3):</span> <strong id="panelStoch" class="text-white theme-text-primary">65 / 62</strong></div>
              <div class="flex justify-between"><span>ADX (Trend Power):</span> <strong id="panelAdx" class="text-amber-400">Strong Trend</strong></div>
              <div class="flex justify-between text-[11px] pt-1 text-slate-400"><span id="panelMacdStatus">Bullish Crossover</span></div>
            </div>
          </div>

          <!-- Volatility & Bands -->
          <div class="p-4 rounded-xl bg-slate-900/70 theme-bg-surface border border-slate-800 theme-border">
            <div class="text-amber-400 font-bold uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
              <span>Volatility & Bands</span>
              <span id="panelBbStatus">Normal Range</span>
            </div>
            <div class="space-y-1.5 text-slate-300 theme-text-secondary">
              <div class="flex justify-between"><span>14-Day ATR:</span> <strong id="panelAtr" class="text-white theme-text-primary">₹12.5 (2.5%)</strong></div>
              <div class="flex justify-between"><span>BB Upper (20,2):</span> <strong id="panelBbUpper" class="text-rose-400">₹0</strong></div>
              <div class="flex justify-between"><span>BB Middle (20 EMA):</span> <strong id="panelBbMid" class="text-white theme-text-primary">₹0</strong></div>
              <div class="flex justify-between"><span>BB Lower:</span> <strong id="panelBbLower" class="text-emerald-400">₹0</strong></div>
              <div class="flex justify-between text-[11px] pt-1 text-slate-400"><span>Bandwidth / %B:</span> <strong id="panelBbBandwidth" class="text-white theme-text-primary">12.5%</strong></div>
            </div>
          </div>

          <!-- Classical Pivots -->
          <div class="p-4 rounded-xl bg-slate-900/70 theme-bg-surface border border-slate-800 theme-border">
            <div class="text-emerald-400 font-bold uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
              <span>Classical Pivots</span>
              <span id="panelPivot">Pivot P: ₹0</span>
            </div>
            <div class="space-y-1.5 text-slate-300 theme-text-secondary">
              <div class="flex justify-between"><span>Resist R1 / R2:</span> <strong id="panelR1_R2" class="text-rose-400">₹0 / ₹0</strong></div>
              <div class="flex justify-between"><span>Resist R3 (Extreme):</span> <strong id="panelR3" class="text-rose-400">₹0</strong></div>
              <div class="flex justify-between"><span>Support S1 / S2:</span> <strong id="panelS1_S2" class="text-emerald-400">₹0 / ₹0</strong></div>
              <div class="flex justify-between"><span>Support S3 (Floor):</span> <strong id="panelS3" class="text-emerald-400">₹0</strong></div>
            </div>
          </div>

          <!-- Fibonacci Retracements -->
          <div class="p-4 rounded-xl bg-slate-900/70 theme-bg-surface border border-slate-800 theme-border">
            <div class="text-indigo-400 font-bold uppercase tracking-wider text-[11px] mb-2">
              Fibonacci Key Retracements
            </div>
            <div class="space-y-1.5 text-slate-300 theme-text-secondary">
              <div class="flex justify-between"><span>23.6% / 38.2%:</span> <strong id="panelFib23_38" class="text-white theme-text-primary">₹0 / ₹0</strong></div>
              <div class="flex justify-between"><span>50.0% Halfway:</span> <strong id="panelFib50" class="text-amber-400">₹0</strong></div>
              <div class="flex justify-between"><span>61.8% Golden Ratio:</span> <strong id="panelFib618" class="text-emerald-400">₹0</strong></div>
              <div class="flex justify-between"><span>161.8% Extension:</span> <strong id="panelFib1618" class="text-sky-400">₹0</strong></div>
            </div>
          </div>

          <!-- Volume Diagnostics -->
          <div class="p-4 rounded-xl bg-slate-900/70 theme-bg-surface border border-slate-800 theme-border">
            <div class="text-teal-400 font-bold uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
              <span>Volume Dynamics</span>
              <span id="panelVolStatus">Active Volume</span>
            </div>
            <div class="space-y-1.5 text-slate-300 theme-text-secondary">
              <div class="flex justify-between"><span>Volume Surge Ratio:</span> <strong id="panelVolRatio" class="text-emerald-400">1.8x</strong></div>
              <div class="flex justify-between"><span>Today Volume:</span> <strong id="panelTodayVol" class="text-white theme-text-primary">0</strong></div>
              <div class="flex justify-between"><span>20D Avg Volume:</span> <strong id="panelAvgVol" class="text-white theme-text-primary">0</strong></div>
              <div class="flex justify-between"><span>Acc / Distribution:</span> <strong class="text-emerald-400">Institutional Inflow</strong></div>
            </div>
          </div>

        </div>

        <!-- SECTION 6: EXECUTIVE SUMMARY BULLETS -->
        <div class="p-4 rounded-xl bg-slate-950/70 theme-bg-subtle border border-slate-800 theme-border">
          <h4 class="text-xs font-bold font-mono text-slate-400 theme-text-muted uppercase mb-2">Executive Technical Verdict & Key Findings</h4>
          <ul id="modalSummaryList" class="list-disc list-inside space-y-1 text-xs text-slate-300 theme-text-secondary leading-relaxed">
            <!-- Dynamically populated -->
          </ul>
        </div>

      </div>

    </div>
  </div>

  <!-- ========================================== -->
  <!-- CREATE CUSTOM BASKET MODAL                 -->
  <!-- ========================================== -->
  <div id="newBasketModal" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 modal-backdrop">
    <div class="bg-[#0B1120] theme-card border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-base font-bold text-white theme-text-primary flex items-center gap-2">
          <span>➕</span> Create New Stock Basket
        </h3>
        <button onclick="closeNewBasketModal()" class="text-slate-400 hover:text-white">&times;</button>
      </div>
      <div>
        <label class="block text-xs font-mono text-slate-400 mb-1">Basket Name</label>
        <input type="text" id="newBasketNameInput" placeholder="e.g. Green Energy Leaders, High ROE Compounders" class="w-full px-3 py-2 bg-slate-950 theme-input border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-sky-500">
      </div>
      <div>
        <label class="block text-xs font-mono text-slate-400 mb-1">Stock Symbols (comma separated)</label>
        <textarea id="newBasketSymbolsInput" rows="3" placeholder="e.g. EMVEE, PREMIERENE, GENUSPOWER, DIXON" class="w-full px-3 py-2 bg-slate-950 theme-input border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-sky-500 font-mono"></textarea>
      </div>
      <div class="flex justify-end gap-2 pt-2">
        <button onclick="closeNewBasketModal()" class="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700 transition">
          Cancel
        </button>
        <button onclick="saveNewBasket()" class="px-4 py-2 rounded-lg bg-sky-500 text-white text-xs font-bold hover:bg-sky-400 transition">
          Save Basket
        </button>
      </div>
    </div>
  </div>


  <!-- ========================================== -->
  <!-- ⚡ BUY RADAR & SIGNAL PERFORMANCE TRACKER  -->
  <!-- ========================================== -->
  <div id="radarModal" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-6 overflow-y-auto modal-backdrop">
    <div class="relative w-full max-w-6xl bg-[#0B1120] theme-card border border-slate-700 rounded-2xl shadow-2xl overflow-hidden my-auto max-h-[95vh] flex flex-col">
      
      <!-- Top Bar -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-800 theme-border bg-slate-900/90 theme-bg-subtle sticky top-0 z-20">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-xl font-bold">
            ⚡
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-black text-white theme-text-primary tracking-tight">BUY RADAR &amp; SIGNAL TRACKER</h2>
              <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono font-bold border border-emerald-500/30">REAL-TIME CONFLUENCE</span>
            </div>
            <p class="text-xs text-slate-400 theme-text-muted mt-0.5">Intraday Breakouts • 2-5 Day Swings • Automated Win/Loss Journal</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Notification Sound Toggle -->
          <label class="flex items-center gap-1.5 cursor-pointer text-xs font-mono text-slate-400 hover:text-white transition select-none">
            <input type="checkbox" id="radarSoundToggle" checked class="rounded bg-slate-900 border-slate-700 text-amber-500 focus:ring-0">
            <span>🔔 Audio Alerts</span>
          </label>
          <button onclick="closeRadarModal()" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
      </div>

      <!-- Radar Navigation Tabs -->
      <div class="flex items-center justify-between px-6 py-2.5 bg-slate-950/80 border-b border-slate-800 theme-border text-xs font-mono flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <button id="radarTabBtn-CANDIDATES" onclick="switchRadarTab('CANDIDATES')" class="px-3.5 py-1.5 rounded-lg bg-sky-500 text-white font-bold transition flex items-center gap-1.5">
            <span>⚡ Live Buy Radar</span>
            <span id="radarCandidatesCountPill" class="px-1.5 py-0.2 rounded-full bg-sky-950 text-sky-200 text-[10px]">0</span>
          </button>
          <button id="radarTabBtn-RUNNING" onclick="switchRadarTab('RUNNING')" class="px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white font-semibold transition flex items-center gap-1.5">
            <span>⏳ Running Signals</span>
            <span id="radarRunningCountPill" class="px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 text-[10px]">0</span>
          </button>
          <button id="radarTabBtn-HISTORICAL" onclick="switchRadarTab('HISTORICAL')" class="px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white font-semibold transition flex items-center gap-1.5">
            <span>📜 Historical Suggestions</span>
            <span id="historicalSummaryPill" class="px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 text-[10px]">0</span>
          </button>
          <button id="radarTabBtn-JOURNAL" onclick="switchRadarTab('JOURNAL')" class="px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white font-semibold transition flex items-center gap-1.5">
            <span>🏆 Signal Journal &amp; Win Rate</span>
            <span id="radarJournalCountPill" class="px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 text-[10px]">0</span>
          </button>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="autoTrackAllRadar()" class="px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500/20 to-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:from-amber-500/30 hover:to-emerald-500/30 font-bold transition flex items-center gap-1 active:scale-95">
            <span>⚡ Auto-Track Top Setups</span>
          </button>
        </div>
      </div>

      <!-- Radar Modal Body Content -->
      <div class="overflow-y-auto p-6 flex-1 space-y-6 text-slate-200 theme-text-primary">
        
        <!-- TAB 1: LIVE RADAR CANDIDATES -->
        <div id="radarSection-CANDIDATES" class="space-y-4">
          
          <!-- Sub Filters for Radar -->
          <div class="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-slate-800 theme-border">
            <div class="flex items-center gap-1.5 text-xs font-mono">
              <button onclick="filterRadarCandidates('ALL')" id="rfBtn-ALL" class="px-3 py-1 rounded-lg bg-sky-500 text-white font-bold">All Radar Setups</button>
              <button onclick="filterRadarCandidates('INTRADAY')" id="rfBtn-INTRADAY" class="px-3 py-1 rounded-lg bg-slate-900 text-amber-300 border border-slate-800 hover:bg-slate-800 font-semibold">⚡ Intraday Breakouts</button>
              <button onclick="filterRadarCandidates('SWING')" id="rfBtn-SWING" class="px-3 py-1 rounded-lg bg-slate-900 text-emerald-300 border border-slate-800 hover:bg-slate-800 font-semibold">🚀 2-5D Swing Swells</button>
              <button onclick="filterRadarCandidates('PERFECT')" id="rfBtn-PERFECT" class="px-3 py-1 rounded-lg bg-slate-900 text-purple-300 border border-slate-800 hover:bg-slate-800 font-black">🌟 Perfect Condition Only</button>
            </div>
            <div class="text-xs font-mono text-slate-400" id="radarSummaryStatus">
              Scanning 424 stocks for real-time confluence...
            </div>
          </div>

          <!-- Radar Cards Grid -->
          <div id="radarCardsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Dynamically populated via JS -->
          </div>
        </div>

        <!-- TAB 2: RUNNING SIGNALS TRACKER -->
        <div id="radarSection-RUNNING" class="hidden space-y-4">
          <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 theme-border flex items-center justify-between text-xs font-mono">
            <span class="text-slate-400">Actively tracking positions in real time. Statuses automatically trigger when Target 1/2/3 or Stop-Loss is pierced.</span>
            <span class="text-sky-400 font-bold" id="runningSummaryPill">0 Active Trades</span>
          </div>

          <div id="runningSignalsList" class="space-y-3">
            <!-- Dynamically populated via JS -->
          </div>
        </div>

        <!-- TAB 3: HISTORICAL SUGGESTIONS ARCHIVE -->
        <div id="radarSection-HISTORICAL" class="hidden space-y-4">
          <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 theme-border flex items-center justify-between text-xs font-mono">
            <span class="text-slate-400">Permanent multi-session archive of all past radar suggestions with trigger CMP, date, time, and return %.</span>
            <span class="text-sky-400 font-bold" id="historicalSummaryPill2">Archived in Database</span>
          </div>
          <div id="historicalSignalsList" class="space-y-3"></div>
        </div>

        <!-- TAB 4: SIGNAL JOURNAL & WIN-RATE ANALYTICS -->
        <div id="radarSection-JOURNAL" class="hidden space-y-5">
          
          <!-- Win Rate KPI Analytics Strip -->
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div class="p-3 rounded-xl bg-slate-900/80 theme-bg-subtle border border-emerald-500/30 font-mono">
              <div class="text-[10px] uppercase text-emerald-400 font-bold">Win Rate</div>
              <div class="text-2xl font-black text-emerald-400 mt-0.5" id="kpiJournalWinRate">0%</div>
              <div class="text-[10px] text-slate-400" id="kpiJournalWinSub">0 Wins / 0 Total</div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/80 theme-bg-subtle border border-sky-500/30 font-mono">
              <div class="text-[10px] uppercase text-sky-400 font-bold">Total Logged</div>
              <div class="text-2xl font-black text-white mt-0.5" id="kpiJournalTotal">0</div>
              <div class="text-[10px] text-slate-400">Signals Monitored</div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/80 theme-bg-subtle border border-emerald-500/30 font-mono">
              <div class="text-[10px] uppercase text-emerald-400 font-bold">Target Hits</div>
              <div class="text-2xl font-black text-emerald-400 mt-0.5" id="kpiJournalWins">0</div>
              <div class="text-[10px] text-emerald-500">Target 1/2/3 Hit</div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/80 theme-bg-subtle border border-rose-500/30 font-mono">
              <div class="text-[10px] uppercase text-rose-400 font-bold">Stop Hits</div>
              <div class="text-2xl font-black text-rose-400 mt-0.5" id="kpiJournalLosses">0</div>
              <div class="text-[10px] text-rose-500">Stop-Loss Hit</div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/80 theme-bg-subtle border border-amber-500/30 font-mono">
              <div class="text-[10px] uppercase text-amber-400 font-bold">Avg Win Return</div>
              <div class="text-2xl font-black text-amber-400 mt-0.5" id="kpiJournalAvgWin">+0.0%</div>
              <div class="text-[10px] text-slate-400">Gain per winner</div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/80 theme-bg-subtle border border-purple-500/30 font-mono">
              <div class="text-[10px] uppercase text-purple-400 font-bold">Profit Factor</div>
              <div class="text-2xl font-black text-purple-400 mt-0.5" id="kpiJournalProfitFactor">0.0x</div>
              <div class="text-[10px] text-slate-400">Gross Gain / Loss</div>
            </div>
          </div>

          <!-- Journal Table Controls -->
          <div class="flex items-center justify-between pt-2">
            <div class="text-xs font-mono font-bold text-slate-300">Detailed Signal Trade Log:</div>
            <div class="flex items-center gap-2">
              <button onclick="exportJournalToExcel()" class="px-3 py-1.5 rounded-lg bg-emerald-600/80 hover:bg-emerald-600 text-white text-xs font-bold font-mono transition flex items-center gap-1">
                📥 Export Journal (.xlsx)
              </button>
              <button onclick="clearSignalJournal()" class="px-3 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-950/80 text-rose-400 border border-rose-500/30 text-xs font-mono transition">
                🗑️ Clear History
              </button>
            </div>
          </div>

          <!-- Journal Table -->
          <div class="overflow-x-auto rounded-xl border border-slate-800 theme-border">
            <table class="w-full text-left border-collapse text-xs font-mono">
              <thead class="bg-slate-950 text-slate-400 border-b border-slate-800">
                <tr>
                  <th class="p-3">Triggered</th>
                  <th class="p-3">Stock</th>
                  <th class="p-3">Horizon</th>
                  <th class="p-3 text-right">Entry (₹)</th>
                  <th class="p-3 text-right">Target 1 / 2</th>
                  <th class="p-3 text-right">Stop-Loss</th>
                  <th class="p-3 text-right">Max / Exit (₹)</th>
                  <th class="p-3 text-right">Return %</th>
                  <th class="p-3 text-center">Outcome Status</th>
                </tr>
              </thead>
              <tbody id="journalTableBody" class="divide-y divide-slate-800/60">
                <!-- Dynamically populated via JS -->
              </tbody>
            </table>
          </div>

        </div>

      </div>

    </div>
  </div>

  <!-- FLOATING TOAST NOTIFICATION CONTAINER -->
  <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- EMBEDDED COMPLETE 424 STOCKS DATASET & APPLICATION ENGINE -->
  <script>
    const STOCKS_DATA = __STOCKS_JSON_DATA__;
    let currentData = [...STOCKS_DATA];
    let activeTimeframe = '1D';
    let activeActionFilter = 'ALL';
    let activeWatchlist = 'ALL';
    let activePreset = 'ALL';
    let activeSector = 'ALL';
    let activeMcap = 'ALL';
    let currentSearch = '';
    let currentPage = 1;
    let pageSize = 48;
    let currentView = 'grid';
    let selectedStock = null;
    let liveServerOnline = false;
    let autoTickEnabled = true;
    let autoTickTimer = null;

    // Table Sorting State
    let sortColumn = 'tech_score';
    let sortDirection = 'desc'; // 'asc' or 'desc'

    // ==========================================
    // WATCHLIST DEFINITIONS (100% Institutional)
    // ==========================================
    const DEFAULT_WATCHLISTS = {
      'STAR_STOCKS': [
        "JBMA", "APOLLO", "DIXON", "LLOYDSME", "PREMIERENE", "GRANULES", "BSE", "GVT&D", "GRSE",
        "M&M", "LLOYDSENGG", "GRAVITA", "EMVEE", "TRANSRAIL", "ASHOKLEY", "CONCORDBIO",
        "OBEROIRLTY", "LICI", "NATIONALUM", "TITAGARH", "ETERNAL", "UNOMINDA", "JKPAPER"
      ],
      '35_MASTER': [
        "EMVEE", "GENUSPOWER", "DIXON", "OBEROIRLTY", "PREMIERENE", "NATIONALUM", "BSE", "LLOYDSME",
        "TRANSRAIL", "SAGILITY", "GRANULES", "ANANTRAJ", "BELRISE", "MAZDOCK", "M&M", "GRSE",
        "MCX", "KALYANKJIL", "NETWEB", "PVRINOX", "BRIGADE", "ASHOKLEY", "ETERNAL", "TITAGARH",
        "GVT&D", "LICI", "CONCORDBIO", "GRAVITA", "HINDALCO", "APOLLO", "JBMA", "JKPAPER",
        "CDSL", "UNOMINDA", "LLOYDSENGG"
      ],
      'ACTIVE_CORE': [
        "EMVEE", "GENUSPOWER", "DIXON", "OBEROIRLTY", "PREMIERENE", "NATIONALUM", "BSE", "LLOYDSME",
        "TRANSRAIL", "SAGILITY", "GRANULES", "ANANTRAJ", "BELRISE", "MAZDOCK", "M&M", "GRSE"
      ],
      'READY_TO_BUY': [
        "EMVEE", "GENUSPOWER", "DIXON", "OBEROIRLTY", "NATIONALUM", "BSE", "LLOYDSME",
        "GRANULES", "ANANTRAJ", "MAZDOCK"
      ],
      'WAIT_ALERT': [
        "PREMIERENE", "TRANSRAIL", "SAGILITY", "BELRISE", "M&M", "GRSE"
      ],
      'FAVORITES': [
        "MCX", "KALYANKJIL", "NETWEB", "PVRINOX", "BRIGADE"
      ],
      'QUARANTINE': [
        "ASHOKLEY", "ETERNAL", "TITAGARH", "GVT&D", "LICI", "CONCORDBIO", "GRAVITA", "HINDALCO"
      ],
      'ELIMINATED': [
        "APOLLO", "JBMA", "JKPAPER", "CDSL", "UNOMINDA", "LLOYDSENGG"
      ]
    };

    // User Bucket Set (Synced with localStorage)
    let bucketSet = new Set();
    let userCustomBaskets = [];

    // Initialize application
    document.addEventListener('DOMContentLoaded', () => {
      initTheme();
      initBucket();
      initCustomBaskets();
      initSectorDropdown();
      updateBreadthStats();
      updateKpiCardCounts();
      updateActionTabs();
      updateRadarBadges();
      applyFiltersAndRender();
      checkLiveServer();
      
      // Live sync loop (every 20s)
      autoTickTimer = setInterval(() => {
        if (autoTickEnabled) checkLiveServer();
      }, 20000);

      // Keyboard shortcuts
      window.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== document.getElementById('searchInput')) {
          e.preventDefault();
          document.getElementById('searchInput').focus();
        }
        if (e.key === 'Escape') {
          closeModal();
          closeNewBasketModal();
        }
      });
    });

    // ==========================================
    // THEME MANAGEMENT (DARK / LIGHT MODE)
    // ==========================================
    function initTheme() {
      const savedTheme = localStorage.getItem('terminal_theme') || 'dark';
      applyTheme(savedTheme);
    }

    function toggleTheme() {
      const current = document.documentElement.classList.contains('light') ? 'light' : 'dark';
      const newTheme = current === 'light' ? 'dark' : 'light';
      applyTheme(newTheme);
      localStorage.setItem('terminal_theme', newTheme);
    }

    function applyTheme(theme) {
      const icon = document.getElementById('themeIcon');
      const label = document.getElementById('themeLabel');

      if (theme === 'light') {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
        if (icon) icon.textContent = '☀️';
        if (label) label.textContent = 'Light Mode';
      } else {
        document.documentElement.classList.remove('light');
        document.documentElement.classList.add('dark');
        if (icon) icon.textContent = '🌙';
        if (label) label.textContent = 'Dark Mode';
      }

      // Re-draw chart if modal is open
      if (selectedStock) {
        setTimeout(drawChart, 50);
      }
    }

    // ==========================================
    // BUCKET & CUSTOM BASKETS ENGINE
    // ==========================================
    function initBucket() {
      try {
        const saved = localStorage.getItem('user_stock_bucket');
        if (saved) {
          const arr = JSON.parse(saved);
          bucketSet = new Set(arr);
        } else {
          // Default initial 60 bucket stocks (23 Star Stocks + 35 Master + top alpha picks)
          const defSymbols = [
            ...DEFAULT_WATCHLISTS['STAR_STOCKS'],
            ...DEFAULT_WATCHLISTS['35_MASTER'],
            "HONASA", "RAMCOIND", "HINDZINC", "ICICIBANK"
          ];
          bucketSet = new Set(defSymbols.slice(0, 60));
          saveBucket();
        }
      } catch (e) {
        console.warn('Could not load user_stock_bucket:', e);
        bucketSet = new Set(DEFAULT_WATCHLISTS['STAR_STOCKS']);
      }
      updateBucketCounters();
    }

    function saveBucket() {
      try {
        localStorage.setItem('user_stock_bucket', JSON.stringify(Array.from(bucketSet)));
      } catch (e) {
        console.warn('Could not save user_stock_bucket:', e);
      }
      updateBucketCounters();
    }

    function updateBucketCounters() {
      const count = bucketSet.size;
      const hBadge = document.getElementById('headerBucketCount');
      if (hBadge) hBadge.textContent = count;
      const pBadge = document.getElementById('pillBucketCount');
      if (pBadge) pBadge.textContent = count;
    }

    function toggleStockBucket(sym, e) {
      if (e) e.stopPropagation();
      if (bucketSet.has(sym)) {
        bucketSet.delete(sym);
      } else {
        bucketSet.add(sym);
      }
      saveBucket();

      // Update UI buttons without full page flash
      const cardStar = document.getElementById(`star-${sym}`);
      if (cardStar) {
        if (bucketSet.has(sym)) {
          cardStar.classList.add('star-active');
          cardStar.textContent = '⭐';
        } else {
          cardStar.classList.remove('star-active');
          cardStar.textContent = '☆';
        }
      }
      const tblStar = document.getElementById(`tbl-star-${sym}`);
      if (tblStar) {
        if (bucketSet.has(sym)) {
          tblStar.classList.add('star-active');
          tblStar.textContent = '⭐';
        } else {
          tblStar.classList.remove('star-active');
          tblStar.textContent = '☆';
        }
      }

      // If active filter is My Bucket, re-render
      if (activeWatchlist === 'MY_BUCKET') {
        applyFiltersAndRender();
      }
    }

    function toggleModalStockBucket() {
      if (!selectedStock) return;
      toggleStockBucket(selectedStock.symbol);
      const mStar = document.getElementById('modalBucketStar');
      if (mStar) {
        if (bucketSet.has(selectedStock.symbol)) {
          mStar.classList.add('star-active');
          mStar.textContent = '⭐';
        } else {
          mStar.classList.remove('star-active');
          mStar.textContent = '☆';
        }
      }
    }

    function initCustomBaskets() {
      try {
        const raw = localStorage.getItem('user_custom_stock_baskets');
        if (raw) {
          userCustomBaskets = JSON.parse(raw);
        } else {
          userCustomBaskets = [
            {
              id: 'custom_green_power',
              name: 'High Alpha Green & Power',
              symbols: ['EMVEE', 'GENUSPOWER', 'PREMIERENE', 'GVT&D']
            },
            {
              id: 'custom_all_round',
              name: 'All round',
              symbols: DEFAULT_WATCHLISTS['35_MASTER'].slice(0, 15)
            }
          ];
          saveCustomBaskets();
        }
      } catch (e) {
        userCustomBaskets = [];
      }
      renderCustomBasketPills();
    }

    function saveCustomBaskets() {
      try {
        localStorage.setItem('user_custom_stock_baskets', JSON.stringify(userCustomBaskets));
      } catch (e) {}
      renderCustomBasketPills();
    }

    function renderCustomBasketPills() {
      const container = document.getElementById('customBasketsContainer');
      if (!container) return;
      let html = '';
      userCustomBaskets.forEach(b => {
        const isActive = activeWatchlist === b.id;
        const activeCls = isActive ? 'active bg-sky-500 text-white' : 'bg-slate-900 theme-bg-subtle text-slate-300 border border-slate-700 hover:bg-slate-800';
        html += `
          <button onclick="setWatchlist('${b.id}')" id="wlBtn-${b.id}" class="filter-chip px-3 py-1.5 rounded-xl ${activeCls} font-medium">
            📁 ${b.name} (${(b.symbols || []).length})
          </button>
        `;
      });
      container.innerHTML = html;
    }

    function resetBasketsToDefault() {
      if (confirm("Reset watchlists and buckets to original institutional defaults?")) {
        localStorage.removeItem('user_stock_bucket');
        localStorage.removeItem('user_custom_stock_baskets');
        initBucket();
        initCustomBaskets();
        setWatchlist('ALL');
      }
    }

    function openNewBasketModal() {
      document.getElementById('newBasketNameInput').value = '';
      document.getElementById('newBasketSymbolsInput').value = '';
      document.getElementById('newBasketModal').classList.remove('hidden');
    }

    function closeNewBasketModal() {
      document.getElementById('newBasketModal').classList.add('hidden');
    }

    function saveNewBasket() {
      const name = document.getElementById('newBasketNameInput').value.trim();
      const rawSyms = document.getElementById('newBasketSymbolsInput').value.trim();
      if (!name) {
        alert("Please enter a basket name");
        return;
      }
      const symList = rawSyms.split(/[,\\s]+/).map(s => s.toUpperCase().trim()).filter(Boolean);
      const newId = 'custom_' + Date.now();
      userCustomBaskets.push({
        id: newId,
        name: name,
        symbols: symList
      });
      saveCustomBaskets();
      closeNewBasketModal();
      setWatchlist(newId);
    }

    // ==========================================
    // INITIALIZATION & KPI CALCULATIONS
    // ==========================================
    function initSectorDropdown() {
      const sectors = new Set();
      STOCKS_DATA.forEach(s => {
        if (s.sector) sectors.add(s.sector);
      });
      const select = document.getElementById('sectorSelect');
      Array.from(sectors).sort().forEach(sec => {
        const opt = document.createElement('option');
        opt.value = sec;
        opt.textContent = sec;
        select.appendChild(opt);
      });
    }

    function updateKpiCardCounts() {
      let cMaster = 0, cForecast = 0, cConsensus = 0, cEtPrime = 0, cPullback = 0;
      STOCKS_DATA.forEach(s => {
        if ((s.master_score || 0) >= 88.0) cMaster++;
        if ((s.forecast_upside || 0) >= 20.0) cForecast++;
        if ((s.buy_pct || 0) >= 80.0 || s.consensus_rating === 'Strong Buy') cConsensus++;
        if ((s.et_score || 0) >= 8) cEtPrime++;
        if (Math.abs((s.moving_averages || {}).dist_50_ema || 999) <= 3.5 || Math.abs((s.moving_averages || {}).dist_200_sma || 999) <= 5.0) cPullback++;
      });

      const elM = document.getElementById('kpiMasterCount');
      if (elM) elM.textContent = cMaster;
      const elF = document.getElementById('kpiForecastCount');
      if (elF) elF.textContent = cForecast;
      const elC = document.getElementById('kpiConsensusCount');
      if (elC) elC.textContent = cConsensus;
      const elE = document.getElementById('kpiEtPrimeCount');
      if (elE) elE.textContent = cEtPrime;
      const elP = document.getElementById('kpiPullbackCount');
      if (elP) elP.textContent = cPullback;
    }

    function updateBreadthStats() {
      let adv = 0, dec = 0, unch = 0;

      STOCKS_DATA.forEach(s => {
        if (s.day_change > 0) adv++;
        else if (s.day_change < 0) dec++;
        else unch++;
      });

      const elAdv = document.getElementById('statAdv');
      if (elAdv) elAdv.textContent = adv;
      const elDec = document.getElementById('statDec');
      if (elDec) elDec.textContent = dec;
      const elUnch = document.getElementById('statUnch');
      if (elUnch) elUnch.textContent = unch;
    }

    function updateActionTabs() {
      const container = document.getElementById('actionTabsContainer');
      if (!container) return;

      const counts = {};
      STOCKS_DATA.forEach(s => {
        const tfData = (s.timeframes && s.timeframes[activeTimeframe]) || (s.timeframes && s.timeframes['1D']) || {};
        const v = tfData.verdict || s.action_badge || s.action || '';
        counts[v] = (counts[v] || 0) + 1;
      });

      let buttons = [];

      if (activeTimeframe === '1D') {
        buttons = [
          { id: 'ALL', label: `All 1D Verdicts (${STOCKS_DATA.length})`, filter: 'ALL', cls: 'hover:text-white' },
          { id: 'STRONG-BUY', label: `🟢 Strong Buy (${counts['🟢 Strong Buy'] || 0})`, filter: 'STRONG BUY', cls: 'hover:bg-emerald-950/50 hover:text-emerald-400' },
          { id: 'BUY-ON-DIPS', label: `🟢 Buy on Dips (${counts['🟢 Buy on Dips'] || 0})`, filter: 'BUY ON DIPS', cls: 'hover:bg-emerald-950/30 hover:text-emerald-300' },
          { id: 'WAIT', label: `🟡 Wait / Watch (${counts['🟡 Wait / Watch'] || 0})`, filter: 'WAIT', cls: 'hover:bg-amber-950/50 hover:text-amber-400' },
          { id: 'HOLD', label: `🔵 Hold Trend (${counts['🔵 Hold'] || 0})`, filter: 'HOLD', cls: 'hover:bg-sky-950/50 hover:text-sky-400' },
          { id: 'SELL', label: `🔴 Sell / Exit (${counts['🔴 Sell / Exit'] || 0})`, filter: 'SELL', cls: 'hover:bg-rose-950/50 hover:text-rose-400' }
        ];
      } else if (activeTimeframe === '15M') {
        const bullCount = counts['🟢 Bullish'] || 0;
        const neutCount = counts['🟡 Neutral'] || 0;
        const bearCount = counts['🔴 Bearish'] || 0;
        buttons = [
          { id: 'ALL', label: `All 15M Signals (${STOCKS_DATA.length})`, filter: 'ALL', cls: 'hover:text-white' },
          { id: 'BULLISH', label: `🟢 Bullish Intraday (${bullCount})`, filter: 'BULLISH', cls: 'hover:bg-emerald-950/50 hover:text-emerald-400' },
          { id: 'NEUTRAL', label: `🟡 Neutral Range (${neutCount})`, filter: 'NEUTRAL', cls: 'hover:bg-amber-950/50 hover:text-amber-400' },
          { id: 'BEARISH', label: `🔴 Bearish Pullback (${bearCount})`, filter: 'BEARISH', cls: 'hover:bg-rose-950/50 hover:text-rose-400' }
        ];
      } else if (activeTimeframe === '1W') {
        const bullCount = counts['🟢 Bullish'] || 0;
        const neutCount = counts['🟡 Neutral'] || 0;
        const bearCount = counts['🔴 Bearish'] || 0;
        buttons = [
          { id: 'ALL', label: `All 1W Signals (${STOCKS_DATA.length})`, filter: 'ALL', cls: 'hover:text-white' },
          { id: 'BULLISH', label: `🟢 Bullish Trend (${bullCount})`, filter: 'BULLISH', cls: 'hover:bg-emerald-950/50 hover:text-emerald-400' },
          { id: 'NEUTRAL', label: `🟡 Neutral Base (${neutCount})`, filter: 'NEUTRAL', cls: 'hover:bg-amber-950/50 hover:text-amber-400' },
          { id: 'BEARISH', label: `🔴 Bearish Trend (${bearCount})`, filter: 'BEARISH', cls: 'hover:bg-rose-950/50 hover:text-rose-400' }
        ];
      } else if (activeTimeframe === '1M') {
        const bullCount = counts['🟢 Strong Bull'] || 0;
        const rangeCount = counts['🟡 Range'] || 0;
        const laggCount = counts['🔴 Laggard'] || 0;
        buttons = [
          { id: 'ALL', label: `All 1M Signals (${STOCKS_DATA.length})`, filter: 'ALL', cls: 'hover:text-white' },
          { id: 'STRONG-BULL', label: `🟢 Strong Bull (${bullCount})`, filter: 'STRONG BULL', cls: 'hover:bg-emerald-950/50 hover:text-emerald-400' },
          { id: 'RANGE', label: `🟡 Macro Range (${rangeCount})`, filter: 'RANGE', cls: 'hover:bg-amber-950/50 hover:text-amber-400' },
          { id: 'LAGGARD', label: `🔴 Secular Laggard (${laggCount})`, filter: 'LAGGARD', cls: 'hover:bg-rose-950/50 hover:text-rose-400' }
        ];
      }

      let html = '';
      buttons.forEach(b => {
        const isActive = activeActionFilter === b.filter;
        const baseClass = isActive 
          ? 'whitespace-nowrap px-4 py-2 rounded-xl text-xs font-bold bg-sky-500 text-white shadow-sm transition'
          : `whitespace-nowrap px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 theme-bg-subtle text-slate-300 theme-text-secondary ${b.cls} border border-slate-800 theme-border transition`;
        html += `<button onclick="setActionFilter('${b.filter}')" id="actionBtn-${b.id}" class="${baseClass}">${b.label}</button>`;
      });

      container.innerHTML = html;
    }

    function matchesTimeframeAction(s, tf, filter) {
      if (!filter || filter === 'ALL') return true;
      const tfData = (s.timeframes && s.timeframes[tf]) || (s.timeframes && s.timeframes['1D']) || {};
      const v = (tfData.verdict || s.action_badge || s.action || '').toUpperCase();
      const f = filter.toUpperCase();

      if (f === 'STRONG BUY') return v.includes('STRONG BUY');
      if (f === 'BUY ON DIPS') return v.includes('BUY ON DIPS');
      if (f === 'WAIT') return v.includes('WAIT');
      if (f === 'HOLD') return v.includes('HOLD');
      if (f === 'SELL') return v.includes('SELL');

      if (f === 'BULLISH') return v.includes('BULL');
      if (f === 'NEUTRAL') return v.includes('NEUTRAL');
      if (f === 'BEARISH') return v.includes('BEAR');

      if (f === 'STRONG BULL') return v.includes('STRONG BULL');
      if (f === 'RANGE') return v.includes('RANGE');
      if (f === 'LAGGARD') return v.includes('LAGGARD');

      return v.includes(f);
    }

    // ==========================================
    // FILTER & SORT ENGINE
    // ==========================================
    function applyFiltersAndRender(resetPage = true) {
      let filtered = [...STOCKS_DATA];

      // 1. Search Query (Symbol, Name, Sector, Action, Timeframe Verdict, Setup Type, Pattern)
      if (currentSearch.trim() !== '') {
        const q = currentSearch.toLowerCase().trim();
        filtered = filtered.filter(s => {
          const tfData = (s.timeframes && s.timeframes[activeTimeframe]) || (s.timeframes && s.timeframes['1D']) || {};
          const tfVerdict = tfData.verdict || '';
          return s.symbol.toLowerCase().includes(q) ||
            s.name.toLowerCase().includes(q) ||
            s.sector.toLowerCase().includes(q) ||
            s.action.toLowerCase().includes(q) ||
            tfVerdict.toLowerCase().includes(q) ||
            (s.setup_type || '').toLowerCase().includes(q) ||
            (s.primary_pattern || '').toLowerCase().includes(q);
        });
      }

      // 2. Action Filter Tab (Timeframe adaptive)
      if (activeActionFilter !== 'ALL') {
        filtered = filtered.filter(s => matchesTimeframeAction(s, activeTimeframe, activeActionFilter));
      }

      // 3. Watchlists & Baskets Filter
      if (activeWatchlist === 'MY_BUCKET') {
        filtered = filtered.filter(s => bucketSet.has(s.symbol));
      } else if (DEFAULT_WATCHLISTS[activeWatchlist]) {
        const targetSet = new Set(DEFAULT_WATCHLISTS[activeWatchlist]);
        filtered = filtered.filter(s => targetSet.has(s.symbol));
      } else if (activeWatchlist.startsWith('custom_')) {
        const b = userCustomBaskets.find(x => x.id === activeWatchlist);
        if (b && b.symbols) {
          const targetSet = new Set(b.symbols);
          filtered = filtered.filter(s => targetSet.has(s.symbol));
        }
      }

      // 4. Institutional Strategy Presets Filter
      if (activePreset === '1D_GAINERS') {
        filtered = filtered.filter(s => s.day_change_pct >= 1.5);
      } else if (activePreset === '1D_DIPS') {
        filtered = filtered.filter(s => s.day_change_pct <= -1.0);
      } else if (activePreset === '1W_LEADERS') {
        filtered = filtered.filter(s => (s.week_change_pct || s.day_change_pct) >= 4.0);
      } else if (activePreset === 'MASTER_ALPHA') {
        filtered = filtered.filter(s => (s.master_score || 0) >= 88.0);
      } else if (activePreset === 'TRIPLE_CROWN') {
        filtered = filtered.filter(s => (s.tri_factor_score || 0) >= 88.0);
      } else if (activePreset === 'HIGH_FORECAST') {
        filtered = filtered.filter(s => (s.forecast_upside || 0) >= 20.0);
      } else if (activePreset === 'MOD_FORECAST') {
        filtered = filtered.filter(s => (s.forecast_upside || 0) >= 10.0 && (s.forecast_upside || 0) < 20.0);
      } else if (activePreset === 'STRONG_BUY_CONSENSUS') {
        filtered = filtered.filter(s => (s.buy_pct || 0) >= 80.0 || s.consensus_rating === 'Strong Buy');
      } else if (activePreset === 'TOP_ET_PRIME') {
        filtered = filtered.filter(s => (s.et_score || 0) >= 8);
      } else if (activePreset === 'MA_PULLBACK' || activePreset === 'DIP_SUPPORT') {
        filtered = filtered.filter(s => Math.abs((s.moving_averages || {}).dist_50_ema || 999) <= 3.5 || Math.abs((s.moving_averages || {}).dist_200_sma || 999) <= 5.0);
      } else if (activePreset === 'EUPHORIC_MOOD') {
        filtered = filtered.filter(s => (s.mood_score || 0) >= 90);
      } else if (activePreset === 'POSITIVE_MOOD') {
        filtered = filtered.filter(s => (s.mood_score || 0) >= 75 && (s.mood_score || 0) < 90);
      } else if (activePreset === 'DEEP_VALUE') {
        filtered = filtered.filter(s => (s.val_discount_pct || 0) >= 20.0);
      } else if (activePreset === 'FAIR_ACCUMULATE') {
        filtered = filtered.filter(s => (s.val_discount_pct || 0) >= 5.0 && (s.val_discount_pct || 0) <= 20.0);
      } else if (activePreset === 'INTRADAY_RADAR') {
        filtered = filtered.filter(s => evaluateBuyRadar(s).isIntraday);
      } else if (activePreset === 'SWING_RADAR') {
        filtered = filtered.filter(s => evaluateBuyRadar(s).isSwing);
      } else if (activePreset === 'PERFECT_RADAR') {
        filtered = filtered.filter(s => evaluateBuyRadar(s).isPerfect);
      } else if (activePreset === 'RADAR_TRACKER') {
        const trackedSyms = new Set(getTrackedSignals().map(x => x.symbol));
        filtered = filtered.filter(s => trackedSyms.has(s.symbol));
      } else if (activePreset === 'STAGE_2_UPTREND') {
        filtered = filtered.filter(s => (s.moving_averages || {}).alignment && s.moving_averages.alignment.includes('Bullish'));
      } else if (activePreset === 'BULLISH_RSI') {
        filtered = filtered.filter(s => s.oscillators.rsi >= 50 && s.oscillators.rsi <= 65);
      } else if (activePreset === 'OVERSOLD_RSI') {
        filtered = filtered.filter(s => s.oscillators.rsi < 40);
      } else if (activePreset === 'BREAKOUT_52W') {
        filtered = filtered.filter(s => s.dist_52w_high >= -10.0);
      } else if (activePreset === 'HYPER_PAT') {
        filtered = filtered.filter(s => (s.latest_yoy_pat || 0) > 50.0);
      } else if (activePreset === 'GROWTH_STREAKS') {
        filtered = filtered.filter(s => (s.streak_pat || 0) >= 3);
      } else if (activePreset === 'VOL_SURGE') {
        filtered = filtered.filter(s => s.vol_ratio >= 1.5);
      } else if (activePreset === 'HIGH_RR') {
        filtered = filtered.filter(s => s.trade_blueprint.rr_ratio >= 2.5);
      } else if (activePreset === 'LARGE_CAP') {
        filtered = filtered.filter(s => s.mcap_tier === 'Large Cap');
      } else if (activePreset === 'MID_CAP') {
        filtered = filtered.filter(s => s.mcap_tier === 'Mid Cap');
      } else if (activePreset === 'SMALL_CAP') {
        filtered = filtered.filter(s => s.mcap_tier === 'Small Cap' || s.mcap_tier === 'Micro Cap');
      }

      // 5. Sector & Cap Tier Filter
      if (activeSector !== 'ALL') {
        filtered = filtered.filter(s => s.sector === activeSector);
      }
      if (activeMcap !== 'ALL') {
        filtered = filtered.filter(s => s.mcap_tier === activeMcap);
      }

      // 6. Bi-Directional Sorting Engine (Timeframe-aware)
      filtered.sort((a, b) => {
        let valA, valB;

        switch (sortColumn) {
          case 'symbol':
            valA = a.symbol;
            valB = b.symbol;
            return sortDirection === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
          case 'cmp':
            valA = a.cmp || 0;
            valB = b.cmp || 0;
            break;
          case 'day_change_pct':
            valA = a.day_change_pct || 0;
            valB = b.day_change_pct || 0;
            break;
          case 'chg_5m_pct':
            valA = a.chg_5m_pct || 0;
            valB = b.chg_5m_pct || 0;
            break;
          case 'action':
            const getVerdictWeight = (stock) => {
              const tfData = (stock.timeframes && stock.timeframes[activeTimeframe]) || (stock.timeframes && stock.timeframes['1D']) || {};
              const v = (tfData.verdict || stock.action_badge || stock.action || '').toUpperCase();
              if (v.includes('STRONG BUY') || v.includes('STRONG BULL')) return 5;
              if (v.includes('BUY ON DIPS') || v.includes('BULL')) return 4;
              if (v.includes('HOLD')) return 3;
              if (v.includes('WAIT') || v.includes('NEUTRAL') || v.includes('RANGE')) return 2;
              if (v.includes('SELL') || v.includes('BEAR') || v.includes('LAGGARD')) return 1;
              return 0;
            };
            valA = getVerdictWeight(a);
            valB = getVerdictWeight(b);
            break;
          case 'entry_min':
            valA = a.trade_blueprint.entry_min || 0;
            valB = b.trade_blueprint.entry_min || 0;
            break;
          case 'stop_loss':
            valA = a.trade_blueprint.stop_loss || 0;
            valB = b.trade_blueprint.stop_loss || 0;
            break;
          case 'target_1':
            valA = a.trade_blueprint.target_1 || 0;
            valB = b.trade_blueprint.target_1 || 0;
            break;
          case 'target_2':
            valA = a.trade_blueprint.target_2 || 0;
            valB = b.trade_blueprint.target_2 || 0;
            break;
          case 'rr_ratio':
            valA = a.trade_blueprint.rr_ratio || 0;
            valB = b.trade_blueprint.rr_ratio || 0;
            break;
          case 's1':
            valA = ((a.timeframes && a.timeframes[activeTimeframe]) || a.timeframes['1D'] || {}).support || a.pivots.s1 || 0;
            valB = ((b.timeframes && b.timeframes[activeTimeframe]) || b.timeframes['1D'] || {}).support || b.pivots.s1 || 0;
            break;
          case 'rsi':
            valA = ((a.timeframes && a.timeframes[activeTimeframe]) || a.timeframes['1D'] || {}).rsi || 0;
            valB = ((b.timeframes && b.timeframes[activeTimeframe]) || b.timeframes['1D'] || {}).rsi || 0;
            break;
          case 'dist_52w_high':
            valA = a.dist_52w_high || 0;
            valB = b.dist_52w_high || 0;
            break;
          case 'tech_score':
            valA = a.tech_score || 0;
            valB = b.tech_score || 0;
            break;
          case 'master_score':
            valA = a.master_score || 0;
            valB = b.master_score || 0;
            break;
          case 'forecast_upside':
            valA = a.forecast_upside || 0;
            valB = b.forecast_upside || 0;
            break;
          case 'et_score':
            valA = a.et_score || 0;
            valB = b.et_score || 0;
            break;
          default:
            valA = a.tech_score || 0;
            valB = b.tech_score || 0;
        }

        if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
        if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      });

      currentData = filtered;
      if (resetPage) currentPage = 1;
      renderCurrentView();
    }

    // ==========================================
    // TABLE SORTING HANDLER (BI-DIRECTIONAL)
    // ==========================================
    function sortTable(col) {
      if (sortColumn === col) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        sortColumn = col;
        sortDirection = (col === 'symbol') ? 'asc' : 'desc';
      }

      syncSortDropdown();
      updateTableSortHeaders();
      applyFiltersAndRender();
    }

    function handleDropdownSort(val) {
      const lastUnderscore = val.lastIndexOf('_');
      const col = val.substring(0, lastUnderscore);
      const dir = val.substring(lastUnderscore + 1);
      sortColumn = col;
      sortDirection = dir;
      updateTableSortHeaders();
      applyFiltersAndRender();
    }

    function syncSortDropdown() {
      const sel = document.getElementById('sortSelect');
      if (sel) {
        const candidate = `${sortColumn}_${sortDirection}`;
        for (let i = 0; i < sel.options.length; i++) {
          if (sel.options[i].value === candidate) {
            sel.value = candidate;
            break;
          }
        }
      }
    }

    function updateTableSortHeaders() {
      const headers = document.querySelectorAll('th.sortable');
      headers.forEach(th => {
        th.classList.remove('sort-active');
        const icon = th.querySelector('.sort-icon');
        if (icon) icon.textContent = '▲▼';
      });

      // Find active column header
      headers.forEach(th => {
        if (th.getAttribute('onclick') && th.getAttribute('onclick').includes(`'${sortColumn}'`)) {
          th.classList.add('sort-active');
          const icon = th.querySelector('.sort-icon');
          if (icon) icon.textContent = sortDirection === 'asc' ? '▲' : '▼';
        }
      });
    }

    // ==========================================
    // RENDERING: CARDS & TABLE
    // ==========================================
    function renderCurrentView() {
      document.getElementById('displayedCount').textContent = currentData.length;
      
      const totalPages = Math.ceil(currentData.length / pageSize) || 1;
      if (currentPage > totalPages) currentPage = totalPages;

      const startIndex = (currentPage - 1) * pageSize;
      const endIndex = Math.min(startIndex + pageSize, currentData.length);
      const pageItems = currentData.slice(startIndex, endIndex);

      if (currentView === 'grid') {
        renderCards(pageItems);
      } else {
        renderTable(pageItems);
      }

      renderPagination(totalPages, startIndex, endIndex);
    }

    function renderCards(items) {
      const container = document.getElementById('cardsGridContainer');
      if (items.length === 0) {
        container.innerHTML = `
          <div class="col-span-full py-16 text-center text-slate-500 bg-slate-900/40 theme-card rounded-2xl border border-slate-800 theme-border">
            <span class="text-4xl">🔍</span>
            <p class="mt-3 text-base font-bold text-slate-300 theme-text-primary">No stocks matching active criteria</p>
            <p class="text-xs mt-1 text-slate-400 theme-text-muted">Try clearing the search query or switching your active watchlist / strategy preset</p>
            <button onclick="resetFilters()" class="mt-4 px-4 py-2 rounded-xl bg-sky-500/20 text-sky-400 text-xs font-semibold hover:bg-sky-500/30 transition">
              Reset Filters
            </button>
          </div>
        `;
        return;
      }

      let html = '';
      items.forEach(s => {
        const isUp = s.day_change >= 0;
        const chgClass = isUp ? 'text-emerald-400' : 'text-rose-400';
        const chgSign = isUp ? '+' : '';

        // Timeframe specific dynamic values
        const tfData = (s.timeframes && s.timeframes[activeTimeframe]) || (s.timeframes && s.timeframes['1D']) || {};
        const inBucket = bucketSet.has(s.symbol);

        const tfVerdict = tfData.verdict || s.action_badge || s.action || '';
        const vUp = tfVerdict.toUpperCase();

        // Action styling based on active timeframe's verdict
        let borderGlow = 'border-slate-800 theme-border';
        let actionBadgeClass = 'bg-slate-800 theme-bg-subtle text-slate-300';
        if (vUp.includes('STRONG BUY') || vUp.includes('STRONG BULL')) {
          borderGlow = 'border-emerald-500/40 hover:glow-green';
          actionBadgeClass = 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-black';
        } else if (vUp.includes('BUY ON DIPS') || vUp.includes('BULL')) {
          borderGlow = 'border-emerald-500/30 hover:glow-green';
          actionBadgeClass = 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-bold';
        } else if (vUp.includes('WAIT') || vUp.includes('NEUTRAL') || vUp.includes('RANGE')) {
          borderGlow = 'border-amber-500/30 hover:glow-amber';
          actionBadgeClass = 'bg-amber-500/20 text-amber-400 border border-amber-500/30 font-bold';
        } else if (vUp.includes('HOLD')) {
          borderGlow = 'border-sky-500/30 hover:glow-blue';
          actionBadgeClass = 'bg-sky-500/20 text-sky-400 border border-sky-500/30 font-bold';
        } else if (vUp.includes('SELL') || vUp.includes('BEAR') || vUp.includes('LAGGARD')) {
          borderGlow = 'border-rose-500/30 hover:glow-red';
          actionBadgeClass = 'bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold';
        }

        const tfRsi = tfData.rsi !== undefined ? tfData.rsi : ((s.oscillators && s.oscillators.rsi) ? s.oscillators.rsi : 50);

        html += `
          <div onclick="openModal('${s.symbol}')" class="group relative rounded-2xl bg-slate-900/80 theme-card border ${borderGlow} p-5 hover:border-sky-500/40 transition cursor-pointer flex flex-col justify-between shadow-lg">
            
            <!-- Card Header -->
            <div>
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-3">
                  <div class="h-10 w-10 rounded-xl bg-slate-800 theme-bg-subtle border border-slate-700 theme-border flex items-center justify-center font-mono font-bold text-sky-400 text-sm">
                    ${s.symbol.slice(0, 3)}
                  </div>
                  <div>
                    <div class="flex items-center gap-2">
                      <span class="font-mono font-bold text-white theme-text-primary text-base">${s.symbol}</span>
                      <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 theme-bg-subtle text-slate-400 font-mono">${s.mcap_tier}</span>
                    </div>
                    <div class="text-xs text-slate-400 theme-text-muted truncate max-w-[190px]" title="${s.name}">${s.name}</div>
                  </div>
                </div>

                <!-- Bookmark Star Button & Live CMP -->
                <div class="flex items-center gap-2">
                  <button id="star-${s.symbol}" onclick="toggleStockBucket('${s.symbol}', event)" class="star-btn text-lg ${inBucket ? 'star-active' : 'text-slate-500'}" title="Toggle My Bucket">
                    ${inBucket ? '⭐' : '☆'}
                  </button>
                  <div class="text-right">
                    <div class="font-mono font-black text-white theme-text-primary text-base transition-colors" id="cmp-${s.symbol}">
                      ₹${s.cmp.toLocaleString('en-IN')}
                    </div>
                    <div class="font-mono font-bold text-xs ${chgClass}">
                      ${chgSign}${s.day_change_pct.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>

              <!-- Signal Verdict & Confluence Badge -->
              <div class="mt-3.5 flex items-center justify-between gap-2">
                <span class="px-2.5 py-1 rounded-lg text-[11px] font-bold uppercase tracking-wider font-mono ${actionBadgeClass}" id="card-verdict-${s.symbol}">
                  ${tfVerdict}
                </span>
                <div class="flex items-center gap-2">
                  <span class="text-[11px] font-mono font-bold text-amber-400" title="Master Score">👑 ${s.master_score || 0}</span>
                  <span class="text-[11px] font-mono font-bold text-sky-400" id="card-tech-${s.symbol}">Tech ${s.tech_score}/100</span>
                </div>
              </div>

              <!-- Actionable Trade Blueprint Box -->
              <div class="mt-3.5 p-3 rounded-xl bg-slate-950/60 theme-bg-subtle border border-slate-800/80 theme-border font-mono text-xs">
                <div class="flex justify-between items-center text-slate-400 theme-text-muted pb-1 border-b border-slate-800/40">
                  <span>Entry Zone:</span>
                  <span class="text-sky-400 font-bold">₹${s.trade_blueprint.entry_min} - ₹${s.trade_blueprint.entry_max}</span>
                </div>
                <div class="grid grid-cols-3 gap-2 pt-2 text-center">
                  <div class="rounded bg-rose-950/20 p-1">
                    <span class="text-[10px] text-rose-400 block">Stop-Loss</span>
                    <span class="font-bold text-rose-400 text-xs">₹${s.trade_blueprint.stop_loss}</span>
                    <span class="text-[9px] text-rose-500/80 block">-${s.trade_blueprint.risk_pct}%</span>
                  </div>
                  <div class="rounded bg-emerald-950/20 p-1">
                    <span class="text-[10px] text-emerald-400 block">Target 1</span>
                    <span class="font-bold text-emerald-400 text-xs">₹${s.trade_blueprint.target_1}</span>
                    <span class="text-[9px] text-emerald-500 block">+${s.trade_blueprint.reward_t1_pct}%</span>
                  </div>
                  <div class="rounded bg-indigo-950/20 p-1">
                    <span class="text-[10px] text-indigo-300 block">Target 2</span>
                    <span class="font-bold text-indigo-300 text-xs">₹${s.trade_blueprint.target_2}</span>
                    <span class="text-[9px] text-indigo-400 block">1:${s.trade_blueprint.rr_ratio}</span>
                  </div>
                </div>
              </div>

              <!-- Key Technical & Fundamental Metrics Strip -->
              <div class="mt-3 pt-2.5 border-t border-slate-800/60 theme-border grid grid-cols-4 gap-1 text-[11px] font-mono text-slate-300 theme-text-secondary text-center">
                <div>
                  <span class="text-slate-500 block text-[9px]">RSI (${activeTimeframe})</span>
                  <strong class="${tfRsi >= 70 ? 'text-rose-400' : (tfRsi <= 35 ? 'text-purple-400' : 'text-emerald-400')}">${tfRsi}</strong>
                </div>
                <div>
                  <span class="text-slate-500 block text-[9px]">52W High</span>
                  <strong class="${s.dist_52w_high >= -10 ? 'text-emerald-400' : 'text-slate-300'}">${s.dist_52w_high}%</strong>
                </div>
                <div>
                  <span class="text-slate-500 block text-[9px]">Forecast Upside</span>
                  <strong class="${(s.forecast_upside || 0) >= 20 ? 'text-sky-400 font-bold' : 'text-slate-300'}">+${s.forecast_upside || 0}%</strong>
                </div>
                <div>
                  <span class="text-slate-500 block text-[9px]">ET Prime</span>
                  <strong class="text-purple-400 font-bold">${s.et_score || 0}/10</strong>
                </div>
              </div>
            </div>

            <!-- Footer Action Bar -->
            <div class="mt-4 pt-3 border-t border-slate-800/80 theme-border flex items-center justify-between">
              <span class="text-[11px] text-slate-400 theme-text-muted font-mono truncate max-w-[210px]" title="${s.setup_type}">${s.setup_type}</span>
              <span class="text-xs text-sky-400 group-hover:translate-x-0.5 transition font-bold flex items-center gap-1">
                Inspect 360° ↗
              </span>
            </div>
          </div>
        `;
      });

      container.innerHTML = html;
    }

    function renderTable(items) {
      const tbody = document.getElementById('tableBody');
      if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="18" class="p-8 text-center text-slate-500 font-mono">No stocks matching active criteria</td></tr>`;
        return;
      }

      let html = '';
      items.forEach(s => {
        const isUp = s.day_change >= 0;
        const chgClass = isUp ? 'text-emerald-400' : 'text-rose-400';
        const chgSign = isUp ? '+' : '';
        const tfData = (s.timeframes && s.timeframes[activeTimeframe]) || (s.timeframes && s.timeframes['1D']) || {};
        const inBucket = bucketSet.has(s.symbol);

        const tfVerdict = tfData.verdict || s.action_badge || s.action || '';
        const vUp = tfVerdict.toUpperCase();

        let badgeColor = 'text-slate-300 bg-slate-800 border border-slate-700';
        if (vUp.includes('STRONG BUY') || vUp.includes('STRONG BULL')) {
          badgeColor = 'text-emerald-400 bg-emerald-500/20 border border-emerald-500/40 font-black';
        } else if (vUp.includes('BUY ON DIPS') || vUp.includes('BULL')) {
          badgeColor = 'text-emerald-300 bg-emerald-500/15 border border-emerald-500/30 font-bold';
        } else if (vUp.includes('HOLD')) {
          badgeColor = 'text-sky-400 bg-sky-500/20 border border-sky-500/30 font-bold';
        } else if (vUp.includes('WAIT') || vUp.includes('NEUTRAL') || vUp.includes('RANGE')) {
          badgeColor = 'text-amber-400 bg-amber-500/20 border border-amber-500/30 font-bold';
        } else if (vUp.includes('SELL') || vUp.includes('BEAR') || vUp.includes('LAGGARD')) {
          badgeColor = 'text-rose-400 bg-rose-500/20 border border-rose-500/30 font-bold';
        }

        const tfRsi = tfData.rsi !== undefined ? tfData.rsi : ((s.oscillators && s.oscillators.rsi) ? s.oscillators.rsi : 50);
        const tfSupport = tfData.support || (s.pivots ? s.pivots.s1 : 0);
        const tfResistance = tfData.resistance || (s.pivots ? s.pivots.r1 : 0);

        html += `
          <tr onclick="openModal('${s.symbol}')" class="hover:bg-slate-800/50 theme-table-row cursor-pointer transition border-b border-slate-800/40 theme-border">
            <td class="p-3 text-center" onclick="event.stopPropagation()">
              <button id="tbl-star-${s.symbol}" onclick="toggleStockBucket('${s.symbol}', event)" class="star-btn text-base ${inBucket ? 'star-active' : 'text-slate-500'}" title="Toggle My Bucket">
                ${inBucket ? '⭐' : '☆'}
              </button>
            </td>
            <td class="p-3">
              <div class="font-mono font-bold text-white theme-text-primary text-sm">${s.symbol}</div>
              <div class="text-[11px] text-slate-400 theme-text-muted truncate max-w-[170px]">${s.name}</div>
              <div class="text-[10px] text-slate-500">${s.sector} • ${s.mcap_tier}</div>
            </td>
            <td class="p-3 text-right font-mono font-bold text-white theme-text-primary text-sm" id="tbl-cmp-${s.symbol}">
              ₹${s.cmp.toLocaleString('en-IN')}
            </td>
            <td class="p-3 text-right font-mono font-bold ${chgClass}">
              ${chgSign}${s.day_change_pct.toFixed(2)}%
            </td>
            <td class="p-3 text-right font-mono font-bold" id="tbl-5m-${s.symbol}">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold ${((s.chg_5m_pct || 0) > 0 ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : ((s.chg_5m_pct || 0) < 0 ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30' : 'bg-slate-800 text-slate-400'))}">
                ${((s.chg_5m_pct || 0) > 0 ? '+' : '')}${Number(s.chg_5m_pct || 0).toFixed(2)}%
              </span>
            </td>
            <td class="p-3 text-center" id="tbl-verdict-${s.symbol}">
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider font-mono ${badgeColor}">
                ${tfVerdict}
              </span>
            </td>
            <td class="p-3 text-center font-mono text-sky-400 font-medium">
              ₹${s.trade_blueprint.entry_min} - ₹${s.trade_blueprint.entry_max}
            </td>
            <td class="p-3 text-right font-mono text-rose-400 font-semibold">
              ₹${s.trade_blueprint.stop_loss} <span class="text-[10px] text-rose-500/80">(-${s.trade_blueprint.risk_pct}%)</span>
            </td>
            <td class="p-3 text-right font-mono text-emerald-400 font-semibold">
              ₹${s.trade_blueprint.target_1}
            </td>
            <td class="p-3 text-right font-mono text-emerald-300 font-semibold">
              ₹${s.trade_blueprint.target_2}
            </td>
            <td class="p-3 text-center font-mono font-bold text-indigo-300">
              1:${s.trade_blueprint.rr_ratio}
            </td>
            <td class="p-3 text-center font-mono text-slate-300 theme-text-secondary">
              <span class="text-rose-400">S:₹${tfSupport}</span> / <span class="text-emerald-400">R:₹${tfResistance}</span>
            </td>
            <td class="p-3 text-center font-mono font-bold">
              <span class="${tfRsi >= 70 ? 'text-rose-400' : (tfRsi <= 35 ? 'text-purple-400' : 'text-emerald-400')}">${tfRsi}</span>
            </td>
            <td class="p-3 text-right font-mono ${s.dist_52w_high >= -10 ? 'text-emerald-400 font-bold' : 'text-slate-400 theme-text-muted'}">
              ${s.dist_52w_high}%
            </td>
            <td class="p-3 text-center font-mono font-extrabold text-sky-400 text-sm" id="tbl-tech-${s.symbol}">
              ${s.tech_score}
            </td>
            <td class="p-3 text-center font-mono font-bold text-amber-400">
              ${s.master_score || 0}
            </td>
            <td class="p-3 text-right font-mono font-bold ${(s.forecast_upside || 0) >= 20 ? 'text-emerald-400' : 'text-slate-400 theme-text-muted'}">
              +${s.forecast_upside || 0}%
            </td>
            <td class="p-3 text-center">
              <div class="flex items-center justify-center gap-1.5" onclick="event.stopPropagation()">
                <button onclick="openModal('${s.symbol}')" class="px-2 py-1 rounded bg-sky-500/20 text-sky-400 hover:bg-sky-500/30 text-xs font-mono transition">
                  360° ↗
                </button>
                <button onclick="addTrackedSignal('${s.symbol}')" title="Track on Buy Radar" class="px-2 py-1 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 text-xs font-mono transition font-bold">
                  📌 Track
                </button>
              </div>
            </td>
          </tr>
        `;
      });

      tbody.innerHTML = html;
      updateTableSortHeaders();
    }

    function renderPagination(totalPages, start, end) {
      document.getElementById('paginationInfo').textContent = `Showing ${start + 1}-${end} of ${currentData.length} stocks`;
      
      const btnContainer = document.getElementById('paginationButtons');
      if (totalPages <= 1) {
        btnContainer.innerHTML = '';
        return;
      }

      let html = '';
      if (currentPage > 1) {
        html += `<button onclick="goToPage(${currentPage - 1})" class="px-2.5 py-1 rounded bg-slate-900 theme-bg-subtle border border-slate-800 theme-border text-slate-300 theme-text-primary hover:text-white font-mono">Prev</button>`;
      }

      for (let p = Math.max(1, currentPage - 2); p <= Math.min(totalPages, currentPage + 2); p++) {
        const activeClass = p === currentPage ? 'bg-sky-500 text-white font-bold' : 'bg-slate-900 theme-bg-subtle border border-slate-800 theme-border text-slate-400 theme-text-muted hover:text-white';
        html += `<button onclick="goToPage(${p})" class="px-3 py-1 rounded ${activeClass} font-mono text-xs">${p}</button>`;
      }

      if (currentPage < totalPages) {
        html += `<button onclick="goToPage(${currentPage + 1})" class="px-2.5 py-1 rounded bg-slate-900 theme-bg-subtle border border-slate-800 theme-border text-slate-300 theme-text-primary hover:text-white font-mono">Next</button>`;
      }

      btnContainer.innerHTML = html;
    }

    function goToPage(p) {
      currentPage = p;
      renderCurrentView();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    }

    function changePageSize(sz) {
      pageSize = parseInt(sz);
      currentPage = 1;
      renderCurrentView();
    }

    // ==========================================
    // FILTER HANDLERS & PRESET SELECTORS
    // ==========================================
    function handleSearch(val) {
      currentSearch = val;
      applyFiltersAndRender();
    }

    function setTimeframe(tf) {
      activeTimeframe = tf;
      ['15M', '1D', '1W', '1M'].forEach(t => {
        const btn = document.getElementById(`tfBtn-${t}`);
        if (btn) {
          if (t === tf) {
            btn.className = 'px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-sky-500 text-white shadow-md transition';
          } else {
            btn.className = 'px-3 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-400 theme-text-muted hover:text-white transition';
          }
        }
      });

      // Update dynamic table headers to reflect current timeframe
      const thVerdict = document.getElementById('tableHeaderVerdict');
      if (thVerdict) thVerdict.textContent = `Verdict (${tf})`;
      const thRsi = document.getElementById('tableHeaderRsi');
      if (thRsi) thRsi.textContent = `RSI (${tf})`;
      const thSupp = document.getElementById('tableHeaderSupport');
      if (thSupp) thSupp.textContent = `Support / Resist (${tf})`;

      // Reset action filter to ALL on timeframe switch
      activeActionFilter = 'ALL';
      updateActionTabs();
      applyFiltersAndRender(true);
      if (selectedStock) updateModalTimeframeTable(selectedStock);
    }

    function setActionFilter(action) {
      activeActionFilter = action;
      updateActionTabs();
      applyFiltersAndRender(true);
    }

    function setWatchlist(wlKey) {
      activeWatchlist = wlKey;
      
      // Update chips visual state
      const chips = document.querySelectorAll('#watchlistsBar .filter-chip');
      chips.forEach(c => c.classList.remove('active', 'bg-sky-500', 'text-white'));

      const activeBtn = document.getElementById(`wlBtn-${wlKey}`);
      if (activeBtn) {
        activeBtn.classList.add('active', 'bg-sky-500', 'text-white');
      }

      applyFiltersAndRender();
    }

    function setPreset(preset) {
      activePreset = preset;

      const chips = document.querySelectorAll('#presetsBar .filter-chip');
      chips.forEach(c => c.classList.remove('active', 'bg-sky-500', 'text-white'));

      const activeBtn = document.getElementById(`presetBtn-${preset}`);
      if (activeBtn) {
        activeBtn.classList.add('active', 'bg-sky-500', 'text-white');
      }

      // Highlight active KPI card if applicable
      ['MASTER_ALPHA', 'HIGH_FORECAST', 'STRONG_BUY_CONSENSUS', 'TOP_ET_PRIME', 'MA_PULLBACK'].forEach(k => {
        const card = document.getElementById(`kpiCard-${k}`);
        if (card) {
          if (preset === k) {
            card.classList.add('ring-2', 'ring-sky-400', 'bg-sky-500/10');
          } else {
            card.classList.remove('ring-2', 'ring-sky-400', 'bg-sky-500/10');
          }
        }
      });

      applyFiltersAndRender();
    }

    function filterByPreset(preset) {
      if (preset === 'MY_BUCKET') {
        setWatchlist('MY_BUCKET');
        return;
      }
      setPreset(preset);
      window.scrollTo({ top: 380, behavior: 'smooth' });
    }

    function handleSectorFilter(sec) {
      activeSector = sec;
      applyFiltersAndRender();
    }

    function handleMcapFilter(mcap) {
      activeMcap = mcap;
      applyFiltersAndRender();
    }

    function switchView(view) {
      currentView = view;
      const gridBtn = document.getElementById('viewGridBtn');
      const tableBtn = document.getElementById('viewTableBtn');
      const gridCont = document.getElementById('cardsGridContainer');
      const tableCont = document.getElementById('tableViewContainer');

      if (view === 'grid') {
        gridBtn.className = 'px-2.5 py-1 rounded-md bg-sky-500 text-white font-semibold transition';
        tableBtn.className = 'px-2.5 py-1 rounded-md text-slate-400 theme-text-muted hover:text-white transition';
        gridCont.classList.remove('hidden');
        tableCont.classList.add('hidden');
      } else {
        tableBtn.className = 'px-2.5 py-1 rounded-md bg-sky-500 text-white font-semibold transition';
        gridBtn.className = 'px-2.5 py-1 rounded-md text-slate-400 theme-text-muted hover:text-white transition';
        tableCont.classList.remove('hidden');
        gridCont.classList.add('hidden');
      }
      renderCurrentView();
    }

    function resetFilters() {
      currentSearch = '';
      document.getElementById('searchInput').value = '';
      activeActionFilter = 'ALL';
      activeWatchlist = 'ALL';
      activePreset = 'ALL';
      activeSector = 'ALL';
      document.getElementById('sectorSelect').value = 'ALL';
      activeMcap = 'ALL';
      document.getElementById('mcapSelect').value = 'ALL';
      sortColumn = 'tech_score';
      sortDirection = 'desc';
      syncSortDropdown();
      updateTableSortHeaders();
      setActionFilter('ALL');
      setWatchlist('ALL');
      setPreset('ALL');
      applyFiltersAndRender();
    }

    function toggleAutoTick(checked) {
      autoTickEnabled = checked;
    }

    // ==========================================
    // EXPORT TO MICROSOFT EXCEL (.xlsx)
    // ==========================================
    function exportToExcel() {
      if (!window.XLSX) {
        alert("SheetJS library is still loading, please try again in a second.");
        return;
      }

      const rows = currentData.map(s => {
        const tfData = (s.timeframes && s.timeframes[activeTimeframe]) || (s.timeframes && s.timeframes['1D']) || {};
        return {
          'Symbol': s.symbol,
          'Company Name': s.name,
          'Sector': s.sector,
          'Market Cap Tier': s.mcap_tier,
          'CMP (Rs)': s.cmp,
          '1D Change (%)': s.day_change_pct,
          '5M Change (%)': s.chg_5m_pct || 0,
          'Day Change (Rs)': s.day_change,
          [`Verdict (${activeTimeframe})`]: tfData.verdict || s.action,
          'Primary Action (1D)': s.action,
          'Setup Type': s.setup_type,
          'Primary Pattern': s.primary_pattern,
          'Entry Min (Rs)': s.trade_blueprint.entry_min,
          'Entry Max (Rs)': s.trade_blueprint.entry_max,
          'Stop Loss (Rs)': s.trade_blueprint.stop_loss,
          'Target 1 (Rs)': s.trade_blueprint.target_1,
          'Target 2 (Rs)': s.trade_blueprint.target_2,
          'Target 3 (Rs)': s.trade_blueprint.target_3,
          'Risk/Reward Ratio': '1:' + s.trade_blueprint.rr_ratio,
          [`Support ${activeTimeframe} (Rs)`]: tfData.support || s.pivots.s1,
          [`Resistance ${activeTimeframe} (Rs)`]: tfData.resistance || s.pivots.r1,
          [`RSI (${activeTimeframe})`]: tfData.rsi !== undefined ? tfData.rsi : s.oscillators.rsi,
          'Dist 52W High (%)': s.dist_52w_high,
          'Technical Score': s.tech_score,
          'Master Alpha Score': s.master_score || 0,
          'Forecast 1Y Target (Rs)': (s.forecast || {}).mean_target || 0,
          'Forecast Upside (%)': s.forecast_upside || 0,
          'Consensus Rating': s.consensus_rating || '',
          'ET Prime Score': s.et_score || 0,
          'Valuation Discount (%)': s.val_discount_pct || 0,
          'Latest YoY PAT (%)': s.latest_yoy_pat || 0,
          'P/E Ratio': s.today_pe || 0,
          'In My Bucket': bucketSet.has(s.symbol) ? 'YES' : 'NO'
        };
      });

      const ws = XLSX.utils.json_to_sheet(rows);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "424 Technicals");
      
      const fileName = `424_Stocks_Technical_Analysis_${new Date().toISOString().slice(0,10)}.xlsx`;
      XLSX.writeFile(wb, fileName);
    }

    // ==========================================
    // 360° DEEP DIVE MODAL CONTROLS
    // ==========================================
    function openModal(symbol) {
      const stock = STOCKS_DATA.find(s => s.symbol === symbol);
      if (!stock) return;
      selectedStock = stock;

      // Header
      document.getElementById('modalLogo').textContent = stock.symbol.slice(0, 3);
      document.getElementById('modalName').textContent = stock.name;
      document.getElementById('modalSym').textContent = stock.symbol;
      document.getElementById('modalSector').textContent = stock.sector;
      document.getElementById('modalMcap').textContent = stock.mcap_tier;
      document.getElementById('modalCMP').textContent = `₹${stock.cmp.toLocaleString('en-IN')}`;

      // Bucket star
      const mStar = document.getElementById('modalBucketStar');
      if (mStar) {
        if (bucketSet.has(stock.symbol)) {
          mStar.classList.add('star-active');
          mStar.textContent = '⭐';
        } else {
          mStar.classList.remove('star-active');
          mStar.textContent = '☆';
        }
      }

      const isUp = stock.day_change >= 0;
      const chgSign = isUp ? '+' : '';
      const chgColor = isUp ? 'text-emerald-400' : 'text-rose-400';
      document.getElementById('modalChg').className = `font-bold ${chgColor} font-mono`;
      document.getElementById('modalChg').textContent = `${chgSign}${stock.day_change_pct.toFixed(2)}% (${chgSign}₹${stock.day_change.toFixed(2)})`;

      document.getElementById('modalDayRange').textContent = `₹${stock.day_low} - ₹${stock.day_high}`;
      document.getElementById('modal52WRange').textContent = `₹${stock.low_52w} - ₹${stock.high_52w}`;

      // External links
      document.getElementById('modalScreenerLink').href = `https://www.screener.in/company/${stock.clean_sym || stock.symbol}/consolidated/`;
      document.getElementById('modalTvLink').href = `https://in.tradingview.com/chart/?symbol=NSE:${stock.clean_sym || stock.symbol}`;

      // Hero Blueprint
      document.getElementById('modalHeroBadge').textContent = stock.action_badge;
      document.getElementById('modalSetupType').textContent = stock.setup_type;
      document.getElementById('modalPatternBadge').textContent = stock.primary_pattern;
      document.getElementById('modalConfluenceScore').textContent = `${stock.confluence.score}%`;
      document.getElementById('modalScoreVal').innerHTML = `${stock.tech_score}<span class="text-xs text-slate-500">/100</span>`;

      // Trade Levels
      document.getElementById('modalEntryZone').textContent = `₹${stock.trade_blueprint.entry_min} - ₹${stock.trade_blueprint.entry_max}`;
      document.getElementById('modalSL').textContent = `₹${stock.trade_blueprint.stop_loss}`;
      document.getElementById('modalSLRisk').textContent = `Downside Risk: -${stock.trade_blueprint.risk_pct}%`;
      document.getElementById('modalT1').textContent = `₹${stock.trade_blueprint.target_1}`;
      document.getElementById('modalT1Gain').textContent = `+${stock.trade_blueprint.reward_t1_pct}%`;
      document.getElementById('modalT2').textContent = `₹${stock.trade_blueprint.target_2}`;
      document.getElementById('modalT2Gain').textContent = `+${stock.trade_blueprint.reward_t2_pct}%`;
      document.getElementById('modalT3').textContent = `₹${stock.trade_blueprint.target_3} (+${stock.trade_blueprint.reward_t3_pct}%)`;
      document.getElementById('modalRR').textContent = `1 : ${stock.trade_blueprint.rr_ratio}`;

      // Institutional Alpha Suite
      document.getElementById('modalMasterScore').textContent = stock.master_score || 0;
      document.getElementById('modalMasterCategory').textContent = stock.master_category || 'Institutional Compounder';
      document.getElementById('modalMasterRankText').textContent = `Rank #${stock.master_rank || 999} / 424`;
      
      const fc = stock.forecast || {};
      document.getElementById('modalForecastUpside').textContent = (stock.forecast_upside !== undefined && stock.forecast_upside !== null) ? `+${stock.forecast_upside}%` : 'N/A';
      document.getElementById('modalForecastTarget').textContent = fc.mean_target ? `Mean Target: ₹${fc.mean_target}` : 'Coverage Pending';
      document.getElementById('modalConsensusRating').textContent = stock.consensus_rating || 'Buy';
      
      const bd = fc.breakdown || {};
      document.getElementById('modalConsensusBreakdown').textContent = `${fc.num_analysts || 0} Analysts (${bd.buy_pct || 0}% Buy)`;
      
      document.getElementById('modalEtScore').textContent = `${stock.et_score || 0} / 10`;
      const ep = stock.et_prime || {};
      document.getElementById('modalEtOutlook').textContent = `${ep.score_outlook || 'NEUTRAL'} Outlook`;

      document.getElementById('modalValDiscount').textContent = `${(stock.val_discount_pct || 0) >= 0 ? '+' : ''}${stock.val_discount_pct || 0}%`;
      document.getElementById('modalYoyPat').textContent = `${(stock.latest_yoy_pat || 0) >= 0 ? '+' : ''}${stock.latest_yoy_pat || 0}%`;
      document.getElementById('modalPePb').textContent = `${stock.today_pe || 0}x / ${stock.today_pb || 0}x`;
      document.getElementById('modalPatStreak').textContent = `${stock.streak_pat || 0} Quarters`;

      // Watchlist Memberships
      const wPills = document.getElementById('modalWatchlistPills');
      let wHtml = '';
      if (DEFAULT_WATCHLISTS['STAR_STOCKS'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold text-[10px]">⭐ Star Stock</span>`;
      if (DEFAULT_WATCHLISTS['35_MASTER'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-sky-500/20 text-sky-400 font-bold text-[10px]">🌐 35 Master</span>`;
      if (DEFAULT_WATCHLISTS['ACTIVE_CORE'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">🎯 Active Core</span>`;
      if (DEFAULT_WATCHLISTS['READY_TO_BUY'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold text-[10px]">🟢 Ready to Buy</span>`;
      if (DEFAULT_WATCHLISTS['WAIT_ALERT'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold text-[10px]">⏸️ Wait Alert</span>`;
      if (DEFAULT_WATCHLISTS['FAVORITES'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 font-bold text-[10px]">⭐ Favorites</span>`;
      if (DEFAULT_WATCHLISTS['QUARANTINE'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold text-[10px]">⚠️ Quarantine</span>`;
      if (DEFAULT_WATCHLISTS['ELIMINATED'].includes(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-bold text-[10px]">❌ Eliminated</span>`;
      if (bucketSet.has(stock.symbol)) wHtml += `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold text-[10px]">🗂️ In My Bucket</span>`;
      wPills.innerHTML = wHtml || `<span class="text-slate-500 text-[11px]">General Universe</span>`;

      // Timeframe Confluence Table
      updateModalTimeframeTable(stock);

      // Indicator Panels
      document.getElementById('panelMaCross').textContent = stock.moving_averages.golden_cross ? '🟢 Golden Cross' : '🔴 Death Cross';
      document.getElementById('panelEma9_20').textContent = `₹${stock.moving_averages.ema9} / ₹${stock.moving_averages.ema20}`;
      document.getElementById('panelEma50').textContent = `₹${stock.moving_averages.ema50}`;
      document.getElementById('panelSma200').textContent = `₹${stock.moving_averages.sma200}`;
      document.getElementById('panelDistSma200').textContent = `${stock.moving_averages.dist_200_sma >= 0 ? '+' : ''}${stock.moving_averages.dist_200_sma}%`;
      document.getElementById('panelMaAlign').textContent = stock.moving_averages.alignment;

      document.getElementById('panelRsiVal').textContent = `${stock.oscillators.rsi}`;
      document.getElementById('panelRsiZone').textContent = stock.oscillators.rsi_zone;
      document.getElementById('panelMacdHist').textContent = stock.oscillators.macd_hist;
      document.getElementById('panelStoch').textContent = `${stock.oscillators.stoch_k} / ${stock.oscillators.stoch_d}`;
      document.getElementById('panelAdx').textContent = stock.oscillators.adx_strength;
      document.getElementById('panelMacdStatus').textContent = stock.oscillators.macd_status;

      document.getElementById('panelAtr').textContent = `₹${stock.volatility.atr} (${stock.volatility.atr_pct}%)`;
      document.getElementById('panelBbUpper').textContent = `₹${stock.volatility.bb_upper}`;
      document.getElementById('panelBbMid').textContent = `₹${stock.volatility.bb_mid}`;
      document.getElementById('panelBbLower').textContent = `₹${stock.volatility.bb_lower}`;
      document.getElementById('panelBbBandwidth').textContent = `${stock.volatility.bb_bandwidth}% / ${stock.volatility.bb_pct_b}%`;
      document.getElementById('panelBbStatus').textContent = stock.volatility.bb_status;

      document.getElementById('panelPivot').textContent = `Pivot P: ₹${stock.pivots.pivot}`;
      document.getElementById('panelR1_R2').textContent = `₹${stock.pivots.r1} / ₹${stock.pivots.r2}`;
      document.getElementById('panelR3').textContent = `₹${stock.pivots.r3}`;
      document.getElementById('panelS1_S2').textContent = `₹${stock.pivots.s1} / ₹${stock.pivots.s2}`;
      document.getElementById('panelS3').textContent = `₹${stock.pivots.s3}`;

      document.getElementById('panelFib23_38').textContent = `₹${stock.fibonacci.fib_236} / ₹${stock.fibonacci.fib_382}`;
      document.getElementById('panelFib50').textContent = `₹${stock.fibonacci.fib_500}`;
      document.getElementById('panelFib618').textContent = `₹${stock.fibonacci.fib_618}`;
      document.getElementById('panelFib1618').textContent = `₹${stock.fibonacci.fib_1618}`;

      document.getElementById('panelVolRatio').textContent = `${stock.vol_ratio}x 20D Avg`;
      document.getElementById('panelTodayVol').textContent = stock.volume.toLocaleString('en-IN');
      document.getElementById('panelAvgVol').textContent = stock.avg_vol_20d.toLocaleString('en-IN');
      document.getElementById('panelVolStatus').textContent = stock.vol_status;

      // Executive bullets
      const summaryList = document.getElementById('modalSummaryList');
      summaryList.innerHTML = stock.executive_summary.map(b => `<li>${b}</li>`).join('');

      // Show Modal
      document.getElementById('detailModal').classList.remove('hidden');
      document.body.style.overflow = 'hidden';

      // Draw Candlestick Chart
      setTimeout(drawChart, 60);
    }

    function closeModal() {
      document.getElementById('detailModal').classList.add('hidden');
      document.body.style.overflow = 'auto';
      selectedStock = null;
    }

    function updateModalTimeframeTable(stock) {
      const tbody = document.getElementById('modalTimeframeTableBody');
      const timeframes = ['15M', '1D', '1W', '1M'];
      const labels = {
        '15M': '15-Min (Tactical Intraday)',
        '1D': 'Daily (1D - Primary Swing)',
        '1W': 'Weekly (1W - Institutional)',
        '1M': 'Monthly (1M - Secular Macro)'
      };

      let html = '';
      timeframes.forEach(tf => {
        const d = stock.timeframes[tf];
        const isCurrentActive = tf === activeTimeframe;
        const rowBg = isCurrentActive ? 'bg-sky-500/10 font-medium' : '';
        html += `
          <tr class="${rowBg} border-b border-slate-800/60 theme-border">
            <td class="p-3 font-mono font-bold ${isCurrentActive ? 'text-sky-400' : 'text-slate-300 theme-text-secondary'}">
              ${labels[tf]}
            </td>
            <td class="p-3 text-slate-300 theme-text-secondary">${d.trend}</td>
            <td class="p-3 text-center font-mono font-bold ${d.rsi >= 70 ? 'text-rose-400' : (d.rsi <= 35 ? 'text-purple-400' : 'text-emerald-400')}">${d.rsi}</td>
            <td class="p-3 font-mono text-slate-300 theme-text-secondary">${d.macd}</td>
            <td class="p-3 text-center font-mono text-rose-400">₹${d.support}</td>
            <td class="p-3 text-center font-mono text-emerald-400">₹${d.resistance}</td>
            <td class="p-3 text-[11px] font-mono text-slate-300 theme-text-secondary">${d.trigger}</td>
            <td class="p-3 text-center font-mono font-bold text-sky-400">${d.verdict}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // ==========================================
    // HTML5 CANVAS CANDLESTICK CHART ENGINE
    // ==========================================
    function drawChart() {
      if (!selectedStock || !selectedStock.candles) return;
      const canvas = document.getElementById('candleCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const width = rect.width;
      const height = rect.height;
      const candles = selectedStock.candles;
      const n = candles.length;

      const isLight = document.documentElement.classList.contains('light');

      // Clear background
      ctx.fillStyle = isLight ? '#FFFFFF' : '#070B14';
      ctx.fillRect(0, 0, width, height);

      let minP = Infinity, maxP = -Infinity;
      let maxVol = 0;
      candles.forEach(c => {
        if (c.low < minP) minP = c.low;
        if (c.high > maxP) maxP = c.high;
        if (c.volume > maxVol) maxVol = c.volume;
      });

      const padTop = 20, padBottom = 35, padLeft = 15, padRight = 55;
      const chartH = height - padTop - padBottom;
      const chartW = width - padLeft - padRight;
      const priceRange = (maxP - minP) * 1.08 || 1;
      const pBottom = minP - (maxP - minP) * 0.04;

      function getY(p) {
        return padTop + chartH - ((p - pBottom) / priceRange) * chartH;
      }

      // Draw Grid Lines
      ctx.strokeStyle = isLight ? '#E2E8F0' : '#1E293B';
      ctx.lineWidth = 1;
      const gridSteps = 4;
      ctx.fillStyle = isLight ? '#64748B' : '#64748B';
      ctx.font = '10px JetBrains Mono, monospace';
      ctx.textAlign = 'left';

      for (let i = 0; i <= gridSteps; i++) {
        const p = pBottom + (priceRange / gridSteps) * i;
        const y = getY(p);
        ctx.beginPath();
        ctx.moveTo(padLeft, y);
        ctx.lineTo(width - padRight, y);
        ctx.stroke();
        ctx.fillText(`₹${Math.round(p)}`, width - padRight + 6, y + 3);
      }

      // Draw Candles & Volume Bars
      const candleW = Math.max(3, (chartW / n) * 0.65);
      const stepX = chartW / n;

      candles.forEach((c, i) => {
        const x = padLeft + i * stepX + stepX * 0.15;
        const isGreen = c.close >= c.open;
        const color = isGreen ? '#10B981' : '#EF4444';

        // Volume Bar at Bottom
        const volH = (c.volume / (maxVol || 1)) * (chartH * 0.22);
        ctx.fillStyle = isGreen ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)';
        ctx.fillRect(x, padTop + chartH - volH, candleW, volH);

        // Candle Wick
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(x + candleW / 2, getY(c.high));
        ctx.lineTo(x + candleW / 2, getY(c.low));
        ctx.stroke();

        // Candle Body
        ctx.fillStyle = color;
        const yOpen = getY(c.open);
        const yClose = getY(c.close);
        const bodyY = Math.min(yOpen, yClose);
        const bodyH = Math.max(2, Math.abs(yOpen - yClose));
        ctx.fillRect(x, bodyY, candleW, bodyH);
      });

      // Overlay 20 EMA line
      ctx.strokeStyle = '#38BDF8';
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      let ema = candles[0].close;
      const k = 2 / (20 + 1);
      candles.forEach((c, i) => {
        ema = c.close * k + ema * (1 - k);
        const x = padLeft + i * stepX + candleW / 2;
        const y = getY(ema);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      // Horizontal Lines for Today's High & Low
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.6)';
      const yHigh = getY(selectedStock.day_high);
      ctx.beginPath();
      ctx.moveTo(padLeft, yHigh);
      ctx.lineTo(width - padRight, yHigh);
      ctx.stroke();

      ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
      const yLow = getY(selectedStock.day_low);
      ctx.beginPath();
      ctx.moveTo(padLeft, yLow);
      ctx.lineTo(width - padRight, yLow);
      ctx.stroke();

      ctx.setLineDash([]);
    }

    // Copy Trade Alert to Clipboard
    function copyTradeAlert() {
      if (!selectedStock) return;
      const s = selectedStock;
      const alertText = `🚨 [TECHNICAL TRADE SETUP] ${s.symbol} (${s.name})
Signal: ${s.action} (${s.setup_type})
CMP: ₹${s.cmp} (${s.day_change_pct >= 0 ? '+' : ''}${s.day_change_pct}%)
Entry Range: ₹${s.trade_blueprint.entry_min} - ₹${s.trade_blueprint.entry_max}
Stop-Loss: ₹${s.trade_blueprint.stop_loss} (Risk: -${s.trade_blueprint.risk_pct}%)
Target 1: ₹${s.trade_blueprint.target_1} (+${s.trade_blueprint.reward_t1_pct}%)
Target 2: ₹${s.trade_blueprint.target_2} (+${s.trade_blueprint.reward_t2_pct}%)
Target 3 (Runner): ₹${s.trade_blueprint.target_3}
Risk/Reward Ratio: 1 : ${s.trade_blueprint.rr_ratio}
Support: ₹${s.pivots.s1} | Resistance: ₹${s.pivots.r1}
Technical Score: ${s.tech_score}/100 | Master Alpha: ${s.master_score}/100`;

      navigator.clipboard.writeText(alertText).then(() => {
        alert(`✅ Trade Setup for ${s.symbol} copied to clipboard!`);
      }).catch(() => {
        prompt("Copy trade setup alert:", alertText);
      });
    }

    // ==========================================
    // LIVE PRICE SERVER SYNC ENGINE
    // ==========================================
    async function checkLiveServer() {
      const pill = document.getElementById('liveServerPill');
      const dot = document.getElementById('liveStatusDot');
      const text = document.getElementById('liveStatusText');

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2500);

        const res = await fetch('http://127.0.0.1:8765/api/quotes', {
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (res.ok) {
          const data = await res.json();
          if (data.status === 'ok' && data.quotes) {
            liveServerOnline = true;
            dot.className = 'h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse';
            text.textContent = `Live Server Connected (${data.last_updated || 'Active'})`;
            pill.className = 'flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs font-mono';
            
            const syncEl = document.getElementById('lastSyncedText');
            const nowTime = new Date().toLocaleTimeString('en-US', { hour12: false });
            if (syncEl) syncEl.textContent = `⏱️ Last Synced: Today ${data.last_updated || nowTime + ' IST'}`;

            applyLiveQuotes(data.quotes);
            return;
          }
        }
      } catch (err) {
        // Server offline
      }

      liveServerOnline = false;
      dot.className = 'h-2.5 w-2.5 rounded-full bg-amber-400';
      const snapDate = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
      text.textContent = `Offline Snapshot (Synced ${snapDate})`;
      pill.className = 'flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 theme-bg-subtle border border-slate-800 theme-border text-xs font-mono text-slate-400';
    }

    // ==========================================
    // DYNAMIC REAL-TIME TECHNICAL ENGINE
    // ==========================================
    function recalculateStockTechnicals(s, q) {
      const oldPrice = s.cmp;
      const newPrice = q.curr_price;
      if (!newPrice || newPrice <= 0) return false;

      s.cmp = newPrice;
      if (q.prev_close && q.prev_close > 0) s.prev_close = q.prev_close;
      s.day_change = q.day_change !== undefined ? q.day_change : Number((s.cmp - (s.prev_close || oldPrice)).toFixed(2));
      s.day_change_pct = q.day_change_pct !== undefined ? q.day_change_pct : Number(((s.day_change / (s.prev_close || oldPrice)) * 100).toFixed(2));
      if (q.day_high && q.day_high > (s.day_high || 0)) s.day_high = q.day_high;
      if (q.day_low && q.day_low > 0 && (q.day_low < (s.day_low || 999999))) s.day_low = q.day_low;
      if (q.volume) s.volume = q.volume;

      // 1. 52-Week High / Low Distances
      if (s.high_52w > 0) {
        if (s.cmp > s.high_52w) s.high_52w = s.cmp;
        s.dist_52w_high = Number((((s.cmp - s.high_52w) / s.high_52w) * 100).toFixed(2));
      }
      if (s.low_52w > 0) {
        if (s.cmp < s.low_52w) s.low_52w = s.cmp;
        s.dist_52w_low = Number((((s.cmp - s.low_52w) / s.low_52w) * 100).toFixed(2));
      }

      // 2. Moving Average Distances
      if (s.moving_averages) {
        if (s.moving_averages.ema50 > 0) {
          s.moving_averages.dist_50_ema = Number((((s.cmp - s.moving_averages.ema50) / s.moving_averages.ema50) * 100).toFixed(2));
        }
        if (s.moving_averages.sma200 > 0) {
          s.moving_averages.dist_200_sma = Number((((s.cmp - s.moving_averages.sma200) / s.moving_averages.sma200) * 100).toFixed(2));
        }
      }

      // 3. Dynamic RSI Calculation & Adjustment
      if (!s.base_rsi) s.base_rsi = (s.oscillators && s.oscillators.rsi) ? s.oscillators.rsi : 50;
      const deltaRsi = s.day_change_pct * 0.75;
      const newRsi = Math.min(96, Math.max(12, Number((s.base_rsi + deltaRsi).toFixed(1))));
      if (s.oscillators) {
        s.oscillators.rsi = newRsi;
        if (newRsi >= 70) s.oscillators.rsi_zone = 'Overbought Warning (> 70)';
        else if (newRsi <= 35) s.oscillators.rsi_zone = 'Oversold Accumulation (< 35)';
        else if (newRsi >= 50) s.oscillators.rsi_zone = 'Bullish Bias (50 - 65)';
        else s.oscillators.rsi_zone = 'Mild Pullback (35 - 50)';
      }
      if (s.timeframes && s.timeframes['1D']) {
        s.timeframes['1D'].rsi = newRsi;
      }
      if (s.timeframes && s.timeframes['15M']) {
        if (!s.base_15m_rsi) s.base_15m_rsi = s.timeframes['15M'].rsi || newRsi;
        s.timeframes['15M'].rsi = Math.min(98, Math.max(10, Number((s.base_15m_rsi + s.day_change_pct * 1.1).toFixed(1))));
      }

      // 4. Bollinger Bands %B
      if (s.volatility && s.volatility.bb_upper > s.volatility.bb_lower) {
        const pctB = ((s.cmp - s.volatility.bb_lower) / (s.volatility.bb_upper - s.volatility.bb_lower)) * 100;
        s.volatility.bb_pct_b = Number(pctB.toFixed(1));
        if (pctB >= 100) s.volatility.bb_status = 'Upper Band Tag (Strong Breakout)';
        else if (pctB <= 0) s.volatility.bb_status = 'Lower Band Penetration (Deep Dip)';
        else s.volatility.bb_status = 'Mid Band Normal Channel';
      }

      // 5. Dynamic Trade Blueprint
      if (s.trade_blueprint) {
        s.trade_blueprint.entry_min = Number((s.cmp * 0.992).toFixed(2));
        s.trade_blueprint.entry_max = Number((s.cmp * 1.008).toFixed(2));
        const riskPct = s.trade_blueprint.risk_pct || 4.0;
        s.trade_blueprint.stop_loss = Number((s.cmp * (1 - riskPct / 100)).toFixed(2));
        const rewT1 = s.trade_blueprint.reward_t1_pct || 5.0;
        const rewT2 = s.trade_blueprint.reward_t2_pct || 12.0;
        const rewT3 = s.trade_blueprint.reward_t3_pct || 25.0;
        s.trade_blueprint.target_1 = Number((s.cmp * (1 + rewT1 / 100)).toFixed(2));
        s.trade_blueprint.target_2 = Number((s.cmp * (1 + rewT2 / 100)).toFixed(2));
        s.trade_blueprint.target_3 = Number((s.cmp * (1 + rewT3 / 100)).toFixed(2));
        const riskAmt = s.cmp - s.trade_blueprint.stop_loss;
        const rewAmt = s.trade_blueprint.target_2 - s.cmp;
        s.trade_blueprint.rr_ratio = riskAmt > 0 ? Number((rewAmt / riskAmt).toFixed(1)) : 2.5;

        if (s.timeframes && s.timeframes['1D']) {
          s.timeframes['1D'].trigger = `Entry ₹${s.trade_blueprint.entry_min} - ₹${s.trade_blueprint.entry_max} / SL ₹${s.trade_blueprint.stop_loss}`;
        }
        if (s.timeframes && s.timeframes['15M']) {
          s.timeframes['15M'].trigger = `Buy above ₹${Number((s.cmp * 1.005).toFixed(2))} / Stop ₹${Number((s.cmp * 0.992).toFixed(2))}`;
        }
      }

      // 6. Dynamic Technical Score / 100
      let score = 0;
      const ma = s.moving_averages || {};
      if (s.cmp >= (ma.ema20 || 0)) score += 12;
      if (s.cmp >= (ma.ema50 || 0)) score += 13;
      if (s.cmp >= (ma.sma200 || 0)) score += 15;

      const currentRsi = (s.oscillators && s.oscillators.rsi) ? s.oscillators.rsi : 50;
      if (currentRsi >= 50 && currentRsi <= 68) score += 25;
      else if (currentRsi >= 40 && currentRsi < 50) score += 18;
      else if (currentRsi > 68 && currentRsi <= 75) score += 16;
      else if (currentRsi < 40 && currentRsi >= 30) score += 14;
      else score += 5;

      if (s.dist_52w_high >= -5) score += 20;
      else if (s.dist_52w_high >= -12) score += 16;
      else if (s.dist_52w_high >= -20) score += 12;
      else if (s.dist_52w_high >= -35) score += 8;
      else score += 4;

      if (s.day_change_pct >= 2.0) score += 15;
      else if (s.day_change_pct > 0) score += 12;
      else if (s.day_change_pct >= -1.0) score += 8;
      else score += 3;

      s.tech_score = Math.min(100, Math.max(20, Math.round(score)));

      // 7. Dynamic Verdict & Action
      if (s.tech_score >= 80 && currentRsi < 74 && s.day_change_pct >= -1.5) {
        s.action = 'STRONG BUY';
        s.action_badge = '🟢 Strong Buy';
        if (s.timeframes && s.timeframes['1D']) s.timeframes['1D'].verdict = '🟢 Strong Buy';
      } else if (s.tech_score >= 68 || (s.tech_score >= 56 && s.day_change_pct < 0 && currentRsi <= 55)) {
        s.action = 'BUY ON DIPS';
        s.action_badge = '🟢 Buy on Dips';
        if (s.timeframes && s.timeframes['1D']) s.timeframes['1D'].verdict = '🟢 Buy on Dips';
      } else if (s.tech_score >= 52) {
        s.action = 'HOLD';
        s.action_badge = '🔵 Hold Trend';
        if (s.timeframes && s.timeframes['1D']) s.timeframes['1D'].verdict = '🔵 Hold';
      } else if (s.tech_score >= 40 || currentRsi > 74) {
        s.action = 'WAIT';
        s.action_badge = '🟡 Wait / Watch';
        if (s.timeframes && s.timeframes['1D']) s.timeframes['1D'].verdict = '🟡 Wait / Watch';
      } else {
        s.action = 'SELL';
        s.action_badge = '🔴 Sell / Exit';
        if (s.timeframes && s.timeframes['1D']) s.timeframes['1D'].verdict = '🔴 Sell / Exit';
      }

      // 8. 15M Intraday Dynamic Verdict
      if (s.timeframes && s.timeframes['15M']) {
        if (s.day_change_pct >= 0.5) {
          s.timeframes['15M'].verdict = '🟢 Bullish';
          s.timeframes['15M'].trend = 'Bullish Intraday Momentum';
        } else if (s.day_change_pct <= -1.0) {
          s.timeframes['15M'].verdict = '🔴 Bearish';
          s.timeframes['15M'].trend = 'Intraday Selling Pressure';
        } else {
          s.timeframes['15M'].verdict = '🟡 Neutral';
          s.timeframes['15M'].trend = 'Range Bound Intraday';
        }
      }

      // 9. Forecast Upside
      if (s.forecast && s.forecast.mean_target && s.cmp > 0) {
        s.forecast_upside = Number((((s.forecast.mean_target - s.cmp) / s.cmp) * 100).toFixed(1));
      }

      return true;
    }

    // Modal Live Synchronizer
    function updateModalLive(stock) {
      if (!selectedStock || selectedStock.symbol !== stock.symbol) return;
      const isUp = stock.day_change >= 0;
      const chgSign = isUp ? '+' : '';
      const chgColor = isUp ? 'text-emerald-400' : 'text-rose-400';

      const cmpEl = document.getElementById('modalCMP');
      if (cmpEl) cmpEl.textContent = `₹${stock.cmp.toLocaleString('en-IN')}`;
      
      const chgEl = document.getElementById('modalChg');
      if (chgEl) {
        chgEl.className = `font-bold ${chgColor} font-mono`;
        chgEl.textContent = `${chgSign}${stock.day_change_pct.toFixed(2)}% (${chgSign}₹${stock.day_change.toFixed(2)})`;
      }

      const dayRangeEl = document.getElementById('modalDayRange');
      if (dayRangeEl) dayRangeEl.textContent = `₹${stock.day_low} - ₹${stock.day_high}`;

      const heroBadgeEl = document.getElementById('modalHeroBadge');
      if (heroBadgeEl) heroBadgeEl.textContent = stock.action_badge || stock.action;

      const scoreEl = document.getElementById('modalScoreVal');
      if (scoreEl) scoreEl.innerHTML = `${stock.tech_score}<span class="text-xs text-slate-500">/100</span>`;

      const entryEl = document.getElementById('modalEntryZone');
      if (entryEl) entryEl.textContent = `₹${stock.trade_blueprint.entry_min} - ₹${stock.trade_blueprint.entry_max}`;

      const slEl = document.getElementById('modalSL');
      if (slEl) slEl.textContent = `₹${stock.trade_blueprint.stop_loss}`;

      const slRiskEl = document.getElementById('modalSLRisk');
      if (slRiskEl) slRiskEl.textContent = `Downside Risk: -${stock.trade_blueprint.risk_pct}%`;

      const t1El = document.getElementById('modalT1');
      if (t1El) t1El.textContent = `₹${stock.trade_blueprint.target_1}`;

      const t2El = document.getElementById('modalT2');
      if (t2El) t2El.textContent = `₹${stock.trade_blueprint.target_2}`;

      const t3El = document.getElementById('modalT3');
      if (t3El) t3El.textContent = `₹${stock.trade_blueprint.target_3} (+${stock.trade_blueprint.reward_t3_pct}%)`;

      const rrEl = document.getElementById('modalRR');
      if (rrEl) rrEl.textContent = `1 : ${stock.trade_blueprint.rr_ratio}`;

      const fcEl = document.getElementById('modalForecastUpside');
      if (fcEl) fcEl.textContent = stock.forecast_upside !== undefined ? `+${stock.forecast_upside}%` : 'N/A';

      const rsiEl = document.getElementById('panelRsiVal');
      if (rsiEl) rsiEl.textContent = `${stock.oscillators.rsi}`;

      const distSma200El = document.getElementById('panelDistSma200');
      if (distSma200El && stock.moving_averages) {
        distSma200El.textContent = `${stock.moving_averages.dist_200_sma >= 0 ? '+' : ''}${stock.moving_averages.dist_200_sma}%`;
      }

      updateModalTimeframeTable(stock);
      drawChart();
    }



﻿    ﻿    // =========================================================================

    // =========================================================================
    // MODULAR INSTITUTIONAL BUY RADAR ENGINE (PARTS 1, 2, 3)
    // =========================================================================
__RADAR_MODULES_INJECTION__

        function applyLiveQuotes(quotes) {
      let changed = 0;
      const updatedSymbols = new Set();

      STOCKS_DATA.forEach(s => {
        const q = quotes[s.symbol];
        if (!q) return;

        // Dynamic 5-minute percentage change
        if (q.chg_5m_pct !== undefined && q.chg_5m_pct !== null) {
          s.chg_5m_pct = q.chg_5m_pct;
          const cell5m = document.getElementById(`tbl-5m-${s.symbol}`);
          if (cell5m) {
            const chg5mVal = s.chg_5m_pct || 0;
            const isUp5m = chg5mVal > 0;
            const isDown5m = chg5mVal < 0;
            const color5m = isUp5m ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : (isDown5m ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30' : 'bg-slate-800 text-slate-400');
            cell5m.innerHTML = `<span class="px-2 py-0.5 rounded text-[11px] font-bold ${color5m}">${isUp5m ? '+' : ''}${chg5mVal.toFixed(2)}%</span>`;
          }
        }

        if (q.curr_price > 0 && Math.abs(q.curr_price - s.cmp) > 0.001) {
          recalculateStockTechnicals(s, q);
          updatedSymbols.add(s.symbol);
          changed++;
        }
      });

      // Real-time tracking evaluation for active trades & radar badges
      if (typeof updateTrackedSignalsLive === 'function') {
        updateTrackedSignalsLive(quotes);
      }
      if (typeof updateRadarBadges === 'function') {
        updateRadarBadges();
      }

      if (changed > 0) {
        console.log(`Live Engine: Recalculated dynamic technicals for ${changed} stocks.`);
        updateBreadthStats();
        updateKpiCardCounts();
        updateActionTabs();
        applyFiltersAndRender(false); // keep user's current pagination page!

        // Flash update animation on DOM for updated stocks
        updatedSymbols.forEach(sym => {
          const s = STOCKS_DATA.find(x => x.symbol === sym);
          if (!s) return;
          const flashClass = s.day_change >= 0 ? 'flash-up' : 'flash-down';

          ['cmp-', 'tbl-cmp-'].forEach(prefix => {
            const el = document.getElementById(`${prefix}${sym}`);
            if (el) {
              el.classList.add(flashClass);
              setTimeout(() => el.classList.remove('flash-up', 'flash-down'), 1400);
            }
          });
        });

        // If modal is open for an updated stock, refresh modal in real-time!
        if (selectedStock && updatedSymbols.has(selectedStock.symbol)) {
          updateModalLive(selectedStock);
        }
      }
    }
  </script>
</body>
</html>
"""
    now_dt = datetime.datetime.now()
    date_str = now_dt.strftime("%d-%b-%Y")
    time_str = now_dt.strftime("%H:%M:%S")
    banner_text = f"⏱️ Last Synced: Today {time_str} IST ({date_str})"
    
    with open('scripts/radar_module_part1.js', 'r', encoding='utf-8') as f1:
        p1 = f1.read()
    with open('scripts/radar_module_part2.js', 'r', encoding='utf-8') as f2:
        p2 = f2.read()
    with open('scripts/radar_module_part3.js', 'r', encoding='utf-8') as f3:
        p3 = f3.read()
    radar_combined = p1 + '\n' + p2 + '\n' + p3
    html_content = template.replace("__STOCKS_JSON_DATA__", stocks_json_str).replace("__SYNC_BANNER_TEXT__", banner_text).replace("__RADAR_MODULES_INJECTION__", radar_combined)


    out_dir = "dashboards" if os.path.exists("dashboards") else "."
    out_file = os.path.join(out_dir, "Advance_Technical_Analysis_424_Stocks.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    size_mb = os.path.getsize(out_file) / (1024 * 1024)
    print(f"Successfully generated {out_file} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    build_html()
