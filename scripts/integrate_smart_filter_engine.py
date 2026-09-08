import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Smart Filter Engine Definition
ENGINE_CODE = """
  /* ==========================================================================
     ADVANCED MULTI-CONDITION SMART SCREENER & PRESETS ENGINE
     ========================================================================== */
  const smartFilters = {
    max_pe: 'any',
    max_pb: 'any',
    max_peg: 'any',
    min_pat_growth: 'any',
    min_streak: 'any',
    min_funda: 'any',
    rsi_zone: 'any',
    trend: 'any',
    proximity_52w: 'any',
    mcap_tier: 'any',
    min_upside: 'any',
    min_master: 'any'
  };

  let activeSmartPreset = null;

  const SMART_PRESETS = {
    lynch_garp: {
      id: 'preset_lynch_garp',
      name: '🎯 Peter Lynch GARP',
      values: { max_peg: '1.0', min_pat_growth: '20', min_funda: '70' }
    },
    alpha_leaders: {
      id: 'preset_alpha_leaders',
      name: '👑 Quad Alpha Leaders',
      values: { min_master: '88', trend: 'stage2', min_upside: '15' }
    },
    hyper_growth: {
      id: 'preset_hyper_growth',
      name: '⚡ Hyper-Growth Breakouts',
      values: { min_pat_growth: '50', rsi_zone: 'momentum' }
    },
    deep_safety: {
      id: 'preset_deep_safety',
      name: '🛡️ Deep Margin of Safety',
      values: { max_pe: '25', max_pb: '4.0', min_upside: '20' }
    },
    stage2_dip: {
      id: 'preset_stage2_dip',
      name: '💎 Stage-2 Dip Buys',
      values: { trend: 'stage2', rsi_zone: 'oversold', min_funda: '70' }
    },
    bluechips: {
      id: 'preset_bluechips',
      name: '🏛️ Institutional Bluechips',
      values: { mcap_tier: 'mega_large', min_master: '80', min_upside: '10' }
    }
  };

  function toggleSmartFilterPanel() {
    const p = document.getElementById('smartFilterPanel');
    const btn = document.getElementById('btnSmartFilterToggle');
    if (!p) return;
    const isHidden = (p.style.display === 'none' || !p.style.display);
    p.style.display = isHidden ? 'block' : 'none';
    if (btn) btn.classList.toggle('active', isHidden);
  }

  function onSmartFilterChange() {
    activeSmartPreset = null;
    document.querySelectorAll('.sf-preset-btn').forEach(b => b.classList.remove('active'));

    for (const key in smartFilters) {
      const el = document.getElementById(`sf_${key}`);
      if (el) smartFilters[key] = el.value;
    }
    updateSmartFilterUI();
    applyAllFilters();
  }

  function applySmartPreset(presetKey) {
    const preset = SMART_PRESETS[presetKey];
    if (!preset) return;

    // Reset all selects to any first
    for (const key in smartFilters) {
      smartFilters[key] = 'any';
      const el = document.getElementById(`sf_${key}`);
      if (el) el.value = 'any';
    }

    // Apply preset values
    for (const [k, v] of Object.entries(preset.values)) {
      smartFilters[k] = v;
      const el = document.getElementById(`sf_${k}`);
      if (el) el.value = v;
    }

    activeSmartPreset = presetKey;
    document.querySelectorAll('.sf-preset-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`preset_${presetKey}`);
    if (btn) btn.classList.add('active');

    // Make sure panel is open
    const p = document.getElementById('smartFilterPanel');
    if (p && (p.style.display === 'none' || !p.style.display)) {
      toggleSmartFilterPanel();
    }

    updateSmartFilterUI();
    applyAllFilters();
  }

  function clearAllSmartFilters(doApply = true) {
    for (const key in smartFilters) {
      smartFilters[key] = 'any';
      const el = document.getElementById(`sf_${key}`);
      if (el) el.value = 'any';
    }
    activeSmartPreset = null;
    document.querySelectorAll('.sf-preset-btn').forEach(b => b.classList.remove('active'));
    updateSmartFilterUI();
    if (doApply) applyAllFilters();
  }

  function clearSingleSmartFilter(key) {
    if (smartFilters.hasOwnProperty(key)) {
      smartFilters[key] = 'any';
      const el = document.getElementById(`sf_${key}`);
      if (el) el.value = 'any';
      activeSmartPreset = null;
      document.querySelectorAll('.sf-preset-btn').forEach(b => b.classList.remove('active'));
      updateSmartFilterUI();
      applyAllFilters();
    }
  }

  function updateSmartFilterUI() {
    const tagsContainer = document.getElementById('sfActiveTags');
    const activeBar = document.getElementById('sfActiveBar');
    const badge = document.getElementById('smartFilterActiveCount');
    if (!tagsContainer) return;

    tagsContainer.innerHTML = '';
    let count = 0;

    const LABELS = {
      max_pe: (v) => `Max P/E ≤ ${v}`,
      max_pb: (v) => `Max P/B ≤ ${v}`,
      max_peg: (v) => `Max PEG ≤ ${v}`,
      min_pat_growth: (v) => `Min PAT YoY ≥ +${v}%`,
      min_streak: (v) => `Min Streak ≥ ${v}Q`,
      min_funda: (v) => `Min Funda ≥ ${v}`,
      rsi_zone: (v) => `RSI: ${v.replace(/_/g, ' ')}`,
      trend: (v) => `Trend: ${v.replace(/_/g, ' ')}`,
      proximity_52w: (v) => `52W High: ${v.replace(/_/g, ' ')}`,
      mcap_tier: (v) => `Mcap: ${v.replace(/_/g, ' ')}`,
      min_upside: (v) => `Min 1Y Upside ≥ +${v}%`,
      min_master: (v) => `Min Master Score ≥ ${v}`
    };

    for (const [k, v] of Object.entries(smartFilters)) {
      if (v !== 'any') {
        count++;
        const lblFn = LABELS[k] || ((val) => `${k}: ${val}`);
        const tag = document.createElement('span');
        tag.className = 'sf-chip';
        tag.innerHTML = `${lblFn(v)} <span class="sf-chip-close" onclick="clearSingleSmartFilter('${k}')" title="Remove condition">&times;</span>`;
        tagsContainer.appendChild(tag);
      }
    }

    if (activeBar) {
      activeBar.style.display = count > 0 ? 'flex' : 'none';
    }
    if (badge) {
      badge.innerText = count;
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
  }
"""

anchor_setFilterPill = "  function setFilterPill(pillType, el) {"
if anchor_setFilterPill in html and "const smartFilters =" not in html:
    html = html.replace(anchor_setFilterPill, ENGINE_CODE + "\n" + anchor_setFilterPill)
    print("Inserted Smart Filter Engine functions.")

# 2. Insert Smart Filter evaluation logic inside applyAllFilters()
SMART_EVAL_CODE = """
      // 6. Advanced Multi-Condition Smart Filters (AND logic)
      if (smartFilters.max_pe !== 'any') {
        const peLimit = parseFloat(smartFilters.max_pe);
        if (typeof s.today_pe !== 'number' || s.today_pe > peLimit) return false;
      }
      if (smartFilters.max_pb !== 'any') {
        const pbLimit = parseFloat(smartFilters.max_pb);
        if (typeof s.today_pb !== 'number' || s.today_pb > pbLimit) return false;
      }
      if (smartFilters.max_peg !== 'any') {
        const pegLimit = parseFloat(smartFilters.max_peg);
        if (typeof s.today_peg !== 'number' || s.today_peg <= 0 || s.today_peg > pegLimit) return false;
      }
      if (smartFilters.min_pat_growth !== 'any') {
        const patLimit = parseFloat(smartFilters.min_pat_growth);
        if (typeof s.latest_yoy_pat !== 'number' || s.latest_yoy_pat < patLimit) return false;
      }
      if (smartFilters.min_streak !== 'any') {
        const streakLimit = parseInt(smartFilters.min_streak);
        if ((s.streak_pat || 0) < streakLimit) return false;
      }
      if (smartFilters.min_funda !== 'any') {
        const fundaLimit = parseFloat(smartFilters.min_funda);
        if ((s.score || 0) < fundaLimit) return false;
      }
      if (smartFilters.rsi_zone !== 'any') {
        const rsiVal = t.rsi !== undefined ? t.rsi : 50;
        if (smartFilters.rsi_zone === 'oversold' && rsiVal >= 48) return false;
        if (smartFilters.rsi_zone === 'bullish' && (rsiVal < 50 || rsiVal > 65)) return false;
        if (smartFilters.rsi_zone === 'momentum' && (rsiVal < 55 || rsiVal > 72)) return false;
        if (smartFilters.rsi_zone === 'extreme_oversold' && rsiVal >= 35) return false;
      }
      if (smartFilters.trend !== 'any') {
        const trendStr = t.trend || '';
        if (smartFilters.trend === 'stage2' && !trendStr.includes('Stage 2')) return false;
        if (smartFilters.trend === 'above_50dma' && t.dma_50 && (s.today_price || 0) < t.dma_50) return false;
        if (smartFilters.trend === 'above_200dma' && t.dma_200 && (s.today_price || 0) < t.dma_200) return false;
      }
      if (smartFilters.proximity_52w !== 'any') {
        const d52 = t.dist_52w_high !== undefined ? t.dist_52w_high : -99;
        if (smartFilters.proximity_52w === 'near_high_5' && (d52 === null || d52 < -5.0)) return false;
        if (smartFilters.proximity_52w === 'near_high_12' && (d52 === null || d52 < -12.0)) return false;
        if (smartFilters.proximity_52w === 'within_20' && (d52 === null || d52 < -20.0)) return false;
        if (smartFilters.proximity_52w === 'pullback_20' && (d52 === null || d52 >= -20.0)) return false;
      }
      if (smartFilters.mcap_tier !== 'any') {
        const mcr = s.mcap_cr || 0;
        const mtier = s.mcap_tier || '';
        if (smartFilters.mcap_tier === 'mega_large' && (mcr < 20000.0 && !mtier.includes('Mega') && !mtier.includes('Large'))) return false;
        if (smartFilters.mcap_tier === 'mega' && (mcr < 100000.0 && !mtier.includes('Mega'))) return false;
        if (smartFilters.mcap_tier === 'large' && ((mcr < 20000.0 || mcr >= 100000.0) && !mtier.includes('Large'))) return false;
        if (smartFilters.mcap_tier === 'mid' && ((mcr < 5000.0 || mcr >= 20000.0) && !mtier.includes('Mid'))) return false;
        if (smartFilters.mcap_tier === 'small' && (mcr >= 5000.0 || mtier.includes('Mega') || mtier.includes('Large') || mtier.includes('Mid'))) return false;
        if (smartFilters.mcap_tier === 'preipo' && (!s.symbol.includes('Pre-IPO') && mtier !== 'Pre-IPO')) return false;
      }
      if (smartFilters.min_upside !== 'any') {
        const upsideLimit = parseFloat(smartFilters.min_upside);
        const upVal = f.upside_mean_pct !== undefined ? f.upside_mean_pct : -99;
        if (upVal < upsideLimit) return false;
      }
      if (smartFilters.min_master !== 'any') {
        const masterLimit = parseFloat(smartFilters.min_master);
        if ((s.master_score || 0) < masterLimit) return false;
      }
"""

eval_anchor = """      // 5. Search query
      if (q) {
        const inSym = s.symbol.toLowerCase().includes(q);
        const inName = s.name.toLowerCase().includes(q);
        const inSec = s.sector.toLowerCase().includes(q) || (s.sub_industry && s.sub_industry.toLowerCase().includes(q));
        const inCat = s.pos_news && s.pos_news.toLowerCase().includes(q);
        const inCons = f.consensus_rating && f.consensus_rating.toLowerCase().includes(q);
        if (!inSym && !inName && !inSec && !inCat && !inCons) return false;
      }"""

if eval_anchor in html and "smartFilters.max_pe" not in html:
    html = html.replace(eval_anchor, eval_anchor + "\n" + SMART_EVAL_CODE)
    print("Inserted Smart Filter evaluation logic inside applyAllFilters.")

# 3. Update summary counter in applyAllFilters
old_counter = "document.getElementById('matchCounter').innerText = `Showing ${currentData.length} of ${rawData.length} Stocks`;"
new_counter = """document.getElementById('matchCounter').innerText = `Showing ${currentData.length} of ${rawData.length} Stocks`;
    const sfSummary = document.getElementById('sfMatchSummary');
    if (sfSummary) {
      sfSummary.innerText = `Matching ${currentData.length}/${rawData.length} Stocks`;
    }"""

if old_counter in html and "sfMatchSummary" not in html:
    html = html.replace(old_counter, new_counter)
    print("Updated sfMatchSummary update.")

# 4. Update resetFilters()
old_reset = """  function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('sectorSelect').value = 'all';
    document.getElementById('mcapSelect').value = 'all';
    document.getElementById('scoreSlider').value = '30';
    document.getElementById('scoreSliderVal').innerText = '30';
    setFilterPill('all', document.querySelector('.filter-pill'));
  }"""

new_reset = """  function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('sectorSelect').value = 'all';
    document.getElementById('mcapSelect').value = 'all';
    document.getElementById('scoreSlider').value = '30';
    document.getElementById('scoreSliderVal').innerText = '30';
    clearAllSmartFilters(false);
    setFilterPill('all', document.querySelector('.filter-pill'));
  }"""

if old_reset in html:
    html = html.replace(old_reset, new_reset)
    print("Updated resetFilters() to also reset smart filters.")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Part 3 (Smart Filter Engine integration) complete.")
