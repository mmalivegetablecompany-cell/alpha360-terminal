import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

build_script_path = 'scripts/build_advanced_technical_html.py'
with open(build_script_path, 'r', encoding='utf-8') as f:
    code = f.read()

print(f'Read build script: {len(code)} characters')

# 1. Add Radar Button in Top Navigation Bar
nav_btn = '''        <!-- Buy Radar & Signal Tracker Button -->
        <button id="buyRadarBtn" onclick="openRadarModal()" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500/20 via-sky-500/20 to-emerald-500/20 hover:from-amber-500/30 hover:to-emerald-500/30 border border-emerald-500/50 text-white text-xs font-black transition active:scale-95 shadow-md shadow-emerald-500/10">
          <span class="animate-pulse text-amber-400 text-sm">⚡</span>
          <span>BUY RADAR &amp; TRACKER</span>
          <span id="radarActiveCountBadge" class="px-1.5 py-0.2 rounded-full bg-emerald-500 text-slate-950 font-mono text-[11px] font-black">0</span>
        </button>

        <!-- Theme Toggle Button -->'''

code = code.replace('        <!-- Theme Toggle Button -->', nav_btn, 1)

# 2. Add Presets in Presets Bar
presets_addition = '''          <button onclick="setPreset('ALL')" id="presetBtn-ALL" class="filter-chip active px-2.5 py-1 rounded-lg bg-sky-500 text-white font-semibold">
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
          </button>'''

code = code.replace('''          <button onclick="setPreset('ALL')" id="presetBtn-ALL" class="filter-chip active px-2.5 py-1 rounded-lg bg-sky-500 text-white font-semibold">
            All Presets
          </button>''', presets_addition, 1)

# 3. Add 5M % Header to Table
th_old = '''            <th class="p-3.5 text-right sortable" onclick="sortTable('cmp')">CMP (₹) <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('day_change_pct')">1D % <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('action')"><span id="tableHeaderVerdict">Verdict (1D)</span> <span class="sort-icon">▲▼</span></th>'''

th_new = '''            <th class="p-3.5 text-right sortable" onclick="sortTable('cmp')">CMP (₹) <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('day_change_pct')">1D % <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-right sortable" onclick="sortTable('chg_5m_pct')">5M % <span class="sort-icon">▲▼</span></th>
            <th class="p-3.5 text-center sortable" onclick="sortTable('action')"><span id="tableHeaderVerdict">Verdict (1D)</span> <span class="sort-icon">▲▼</span></th>'''

code = code.replace(th_old, th_new, 1)

# 4. Table empty state colspan: 17 -> 18
code = code.replace('colspan="17"', 'colspan="18"')

# 5. Add 5M % Cell and Track button in Table Rows
td_old = '''            <td class="p-3 text-right font-mono font-bold ">
              %
            </td>
            <td class="p-3 text-center" id="tbl-verdict-">'''

td_new = '''            <td class="p-3 text-right font-mono font-bold ">
              %
            </td>
            <td class="p-3 text-right font-mono font-bold" id="tbl-5m-">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold ">
                %
              </span>
            </td>
            <td class="p-3 text-center" id="tbl-verdict-">'''

code = code.replace(td_old, td_new, 1)

inspect_old = '''            <td class="p-3 text-center">
              <button onclick="event.stopPropagation(); openModal('')" class="px-2 py-1 rounded bg-sky-500/20 text-sky-400 hover:bg-sky-500/30 text-xs font-mono transition">
                Inspect ↗
              </button>
            </td>'''

inspect_new = '''            <td class="p-3 text-center">
              <div class="flex items-center justify-center gap-1.5" onclick="event.stopPropagation()">
                <button onclick="openModal('')" class="px-2 py-1 rounded bg-sky-500/20 text-sky-400 hover:bg-sky-500/30 text-xs font-mono transition">
                  360° ↗
                </button>
                <button onclick="addTrackedSignal('')" title="Track in Signal Journal" class="px-2 py-1 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 text-xs font-mono transition">
                  📌 Track
                </button>
              </div>
            </td>'''

code = code.replace(inspect_old, inspect_new, 1)

# 6. Add "Track on Radar" button in Hero Box of 360° Modal
modal_hero_btn_old = '''              <button onclick="copyTradeAlert()" class="px-3 py-2 rounded-xl bg-sky-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow hover:bg-sky-400 transition">
                📋 Copy Alert
              </button>'''

modal_hero_btn_new = '''              <button onclick="copyTradeAlert()" class="px-3 py-2 rounded-xl bg-sky-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow hover:bg-sky-400 transition">
                📋 Copy Alert
              </button>
              <button onclick="trackStockFromModal()" class="px-3 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-emerald-500 text-slate-950 font-extrabold text-xs flex items-center gap-1.5 shadow hover:brightness-110 transition active:scale-95">
                📌 Track on Radar
              </button>'''

code = code.replace(modal_hero_btn_old, modal_hero_btn_new, 1)

# 7. Add case 'chg_5m_pct' in sortTable
sort_old = '''          case 'day_change_pct':
            valA = a.day_change_pct || 0;
            valB = b.day_change_pct || 0;
            break;'''

sort_new = '''          case 'day_change_pct':
            valA = a.day_change_pct || 0;
            valB = b.day_change_pct || 0;
            break;
          case 'chg_5m_pct':
            valA = a.chg_5m_pct || 0;
            valB = b.chg_5m_pct || 0;
            break;'''

code = code.replace(sort_old, sort_new, 1)

# 8. Add strategy preset filter branches
preset_filter_old = '''      } else if (activePreset === 'STAGE_2_UPTREND') {'''

preset_filter_new = '''      } else if (activePreset === 'INTRADAY_RADAR') {
        filtered = filtered.filter(s => evaluateBuyRadar(s).isIntraday);
      } else if (activePreset === 'SWING_RADAR') {
        filtered = filtered.filter(s => evaluateBuyRadar(s).isSwing);
      } else if (activePreset === 'PERFECT_RADAR') {
        filtered = filtered.filter(s => evaluateBuyRadar(s).isPerfect);
      } else if (activePreset === 'RADAR_TRACKER') {
        const trackedSyms = new Set(getTrackedSignals().map(x => x.symbol));
        filtered = filtered.filter(s => trackedSyms.has(s.symbol));
      } else if (activePreset === 'STAGE_2_UPTREND') {'''

code = code.replace(preset_filter_old, preset_filter_new, 1)

# 9. Excel export include 5M change
excel_old = '''          '1D Change (%)': s.day_change_pct,
          'Day Change (Rs)': s.day_change,'''

excel_new = '''          '1D Change (%)': s.day_change_pct,
          '5M Change (%)': s.chg_5m_pct || 0,
          'Day Change (Rs)': s.day_change,'''

code = code.replace(excel_old, excel_new, 1)

# 10. Inject Radar Modal HTML and Floating Toast markup right before <script>
radar_modal_html = '''
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

        <!-- TAB 3: SIGNAL JOURNAL & WIN-RATE ANALYTICS -->
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
'''

code = code.replace('  <!-- EMBEDDED COMPLETE 424 STOCKS DATASET & APPLICATION ENGINE -->', radar_modal_html + '\n  <!-- EMBEDDED COMPLETE 424 STOCKS DATASET & APPLICATION ENGINE -->', 1)

with open(build_script_path, 'w', encoding='utf-8') as f:
    f.write(code)

print('Successfully injected HTML structure into build_advanced_technical_html.py!')
