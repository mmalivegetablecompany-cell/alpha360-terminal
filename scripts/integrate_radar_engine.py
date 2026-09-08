import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

build_script_path = 'scripts/build_advanced_technical_html.py'
with open(build_script_path, 'r', encoding='utf-8') as f:
    code = f.read()

print(f'Original build script length: {len(code)}')

# 1. Read radar modules 1, 2, and 3
with open('scripts/radar_module_part1.js', 'r', encoding='utf-8') as f:
    radar1 = f.read()
with open('scripts/radar_module_part2.js', 'r', encoding='utf-8') as f:
    radar2 = f.read()
with open('scripts/radar_module_part3.js', 'r', encoding='utf-8') as f:
    radar3 = f.read()

combined_radar_js = '\n\n' + radar1.strip() + '\n\n' + radar2.strip() + '\n\n' + radar3.strip() + '\n\n'

# 2. Add 5M % cell into renderTable
row_5m_target = """            <td class="p-3 text-right font-mono font-bold ${chgClass}">
              ${chgSign}${s.day_change_pct.toFixed(2)}%
            </td>
            <td class="p-3 text-center" id="tbl-verdict-${s.symbol}">"""

row_5m_replacement = """            <td class="p-3 text-right font-mono font-bold ${chgClass}">
              ${chgSign}${s.day_change_pct.toFixed(2)}%
            </td>
            <td class="p-3 text-right font-mono font-bold" id="tbl-5m-${s.symbol}">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold ${((s.chg_5m_pct || 0) > 0 ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : ((s.chg_5m_pct || 0) < 0 ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30' : 'bg-slate-800 text-slate-400'))}">
                ${((s.chg_5m_pct || 0) > 0 ? '+' : '')}${Number(s.chg_5m_pct || 0).toFixed(2)}%
              </span>
            </td>
            <td class="p-3 text-center" id="tbl-verdict-${s.symbol}">"""

if row_5m_target in code:
    code = code.replace(row_5m_target, row_5m_replacement, 1)
    print('✓ Injected 5M % cell into renderTable')
else:
    print('! Warning: row_5m_target not found')

# 3. Add 360° + Track buttons into renderTable row action cell
inspect_target = """            <td class="p-3 text-center">
              <button onclick="event.stopPropagation(); openModal('${s.symbol}')" class="px-2 py-1 rounded bg-sky-500/20 text-sky-400 hover:bg-sky-500/30 text-xs font-mono transition">
                Inspect ↗
              </button>
            </td>"""

inspect_replacement = """            <td class="p-3 text-center">
              <div class="flex items-center justify-center gap-1.5" onclick="event.stopPropagation()">
                <button onclick="openModal('${s.symbol}')" class="px-2 py-1 rounded bg-sky-500/20 text-sky-400 hover:bg-sky-500/30 text-xs font-mono transition">
                  360° ↗
                </button>
                <button onclick="addTrackedSignal('${s.symbol}')" title="Track on Buy Radar" class="px-2 py-1 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 text-xs font-mono transition font-bold">
                  📌 Track
                </button>
              </div>
            </td>"""

if inspect_target in code:
    code = code.replace(inspect_target, inspect_replacement, 1)
    print('✓ Injected 360° + Track buttons into renderTable')
else:
    print('! Warning: inspect_target not found')

# 4. Add updateRadarBadges() in DOMContentLoaded
dom_target = """      updateBreadthStats();
      updateKpiCardCounts();
      updateActionTabs();
      applyFiltersAndRender();"""

dom_replacement = """      updateBreadthStats();
      updateKpiCardCounts();
      updateActionTabs();
      updateRadarBadges();
      applyFiltersAndRender();"""

if dom_target in code:
    code = code.replace(dom_target, dom_replacement, 1)
    print('✓ Added updateRadarBadges() into DOMContentLoaded')
else:
    print('! Warning: dom_target not found')

# 5. Enhance applyLiveQuotes with 5M dynamic updates and signal tracking
live_target = """function applyLiveQuotes(quotes) {
      let changed = 0;
      const updatedSymbols = new Set();

      STOCKS_DATA.forEach(s => {
        const q = quotes[s.symbol];
        if (q && q.curr_price > 0 && Math.abs(q.curr_price - s.cmp) > 0.001) {
          recalculateStockTechnicals(s, q);
          updatedSymbols.add(s.symbol);
          changed++;
        }
      });"""

live_replacement = """function applyLiveQuotes(quotes) {
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
      }"""

if live_target in code:
    code = code.replace(live_target, live_replacement, 1)
    print('✓ Enhanced applyLiveQuotes with 5M % and live tracking')
else:
    print('! Warning: live_target not found')

# 6. Inject Radar Engine JS before applyLiveQuotes
if 'function evaluateBuyRadar' not in code:
    code = code.replace('    function applyLiveQuotes(quotes) {', combined_radar_js + '    function applyLiveQuotes(quotes) {', 1)
    print('✓ Injected combined Radar & Tracker Engine JS')
else:
    print('! Warning: evaluateBuyRadar already in code')

with open(build_script_path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'Successfully completed integration! New build script length: {len(code)}')
