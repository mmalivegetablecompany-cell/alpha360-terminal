    // =========================================================================
    // 3. RENDER RUNNING SIGNALS & AUTO-TRACKER ENGINE
    // =========================================================================
    function renderRunningSignals() {
      const container = document.getElementById('runningSignalsList');
      if (!container) return;

      const signals = getTrackedSignals().filter(s => s.status === 'RUNNING');
      const pill = document.getElementById('runningSummaryPill');
      if (pill) pill.textContent = signals.length + ' Active Trades';

      if (signals.length === 0) {
        container.innerHTML = '<div class="p-12 text-center text-slate-500 font-mono rounded-xl bg-slate-900/40 border border-slate-800">' +
          '<span class="text-3xl">📭</span>' +
          '<p class="mt-2 text-sm text-slate-400 font-semibold">No signals currently running.</p>' +
          '<p class="text-xs text-slate-500 mt-1">Select setups from "Live Buy Radar" or click "⚡ Auto-Track Top Setups" to track them live.</p>' +
          '</div>';
        return;
      }

      let html = '';
      signals.forEach(sig => {
        const stock = STOCKS_DATA.find(s => s.symbol === sig.symbol);
        const cmp = stock ? stock.cmp : (sig.current_price || sig.entry_price);
        const pnl = cmp - sig.entry_price;
        const pnlPct = sig.entry_price > 0 ? ((cmp - sig.entry_price) / sig.entry_price) * 100 : 0;
        const isUp = pnl >= 0;
        const pnlClass = isUp ? 'text-emerald-400' : 'text-rose-400';
        const pnlSign = isUp ? '+' : '';

        // Progress Calculation towards T1/T2
        const spanTotal = Math.max(0.01, (sig.target_2 || (sig.entry_price * 1.08)) - (sig.stop_loss || (sig.entry_price * 0.96)));
        let progressPct = Math.min(100, Math.max(0, ((cmp - sig.stop_loss) / spanTotal) * 100));

        let horizonBadge = '';
        if (sig.horizon === 'PERFECT') {
          horizonBadge = '<span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 text-[10px] font-black uppercase">🌟 PERFECT</span>';
        } else if (sig.horizon === 'INTRADAY') {
          horizonBadge = '<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold uppercase">⚡ INTRADAY</span>';
        } else {
          horizonBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-bold uppercase">🚀 SWING</span>';
        }

        const trigDate = new Date(sig.triggered_at);
        const triggeredStr = !isNaN(trigDate) ? trigDate.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) + ' ' + trigDate.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : (sig.triggered_at || '');

        html += '<div class="p-4 rounded-xl bg-slate-900/90 theme-card border border-slate-800 theme-border shadow-md hover:border-sky-500/30 transition flex flex-col gap-3">' +
          '<div class="flex items-center justify-between flex-wrap gap-2">' +
            '<div class="flex items-center gap-2">' +
              '<span class="font-mono font-bold text-white text-base">' + sig.symbol + '</span>' +
              horizonBadge +
              '<span class="text-xs text-slate-400 truncate max-w-[180px]">' + (sig.name || '') + '</span>' +
            '</div>' +
            '<div class="flex items-center gap-4">' +
              '<div class="text-right font-mono">' +
                '<span class="text-xs text-slate-400 block">Trigger CMP: ₹' + sig.entry_price.toLocaleString('en-IN') + '</span>' +
                '<span class="font-bold text-white text-sm">Live CMP: ₹' + cmp.toLocaleString('en-IN') + '</span>' +
              '</div>' +
              '<div class="px-3 py-1 rounded-lg bg-slate-950 border border-slate-800 text-right font-mono">' +
                '<span class="text-[10px] text-slate-400 block">Live P&L</span>' +
                '<span class="text-sm font-black ' + pnlClass + '">' + pnlSign + pnlPct.toFixed(2) + '%</span>' +
              '</div>' +
            '</div>' +
          '</div>' +

          '<div class="space-y-1.5 font-mono text-xs">' +
            '<div class="flex justify-between text-[11px] text-slate-400">' +
              '<span class="text-rose-400">🛑 SL: ₹' + sig.stop_loss + '</span>' +
              '<span>Entry: ₹' + sig.entry_price + '</span>' +
              '<span class="' + (cmp >= sig.target_1 ? 'text-emerald-400 font-bold' : 'text-slate-300') + '">🎯 T1: ₹' + sig.target_1 + '</span>' +
              '<span class="' + (cmp >= sig.target_2 ? 'text-emerald-300 font-bold' : 'text-slate-300') + '">🚀 T2: ₹' + sig.target_2 + '</span>' +
            '</div>' +
            '<div class="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden border border-slate-800 p-0.5">' +
              '<div class="h-full rounded-full bg-gradient-to-r ' + (isUp ? 'from-amber-400 via-emerald-400 to-sky-400' : 'from-rose-500 to-amber-500') + ' transition-all duration-500" style="width: ' + progressPct + '%"></div>' +
            '</div>' +
          '</div>' +

          '<div class="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs font-mono">' +
            '<span class="text-slate-400 text-[11px]">⏱️ Triggered: ' + triggeredStr + (sig.notes ? ' • ' + sig.notes : '') + '</span>' +
            '<div class="flex items-center gap-2">' +
              '<button onclick="closeRadarModal(); openModal(' + "'" + sig.symbol + "'" + ')" class="px-2.5 py-1 rounded bg-sky-500/15 hover:bg-sky-500/25 text-sky-400 transition font-bold">' +
                '360° View ↗' +
              '</button>' +
              '<button onclick="closeTrackedSignal(' + "'" + sig.id + "', 'MANUAL_EXIT'" + ')" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition font-semibold">' +
                '⏹️ Close Trade' +
              '</button>' +
            '</div>' +
          '</div>' +
        '</div>';
      });

      container.innerHTML = html;
    }

    // =========================================================================
    // 4. RENDER HISTORICAL SUGGESTIONS (Yesterday & Prior Days Log)
    // =========================================================================
    function renderHistoricalSuggestions() {
      const container = document.getElementById('historicalSignalsList');
      if (!container) return;

      const history = getHistoricalSuggestions();
      const countEl = document.getElementById('historicalSummaryPill');
      if (countEl) countEl.textContent = history.length + ' Suggestions Archived';

      if (history.length === 0) {
        container.innerHTML = '<div class="p-12 text-center text-slate-500 font-mono rounded-xl bg-slate-900/40 border border-slate-800">' +
          '<span class="text-3xl">📜</span>' +
          '<p class="mt-2 text-sm text-slate-400 font-semibold">No past suggestions recorded yet.</p>' +
          '</div>';
        return;
      }

      let html = '<div class="overflow-x-auto"><table class="w-full text-left font-mono text-xs border-collapse">' +
        '<thead>' +
          '<tr class="border-b border-slate-800 text-slate-400 bg-slate-950/60">' +
            '<th class="p-3">Trigger Date & Time</th>' +
            '<th class="p-3">Stock Symbol</th>' +
            '<th class="p-3">Setup Type</th>' +
            '<th class="p-3 text-right">Trigger CMP</th>' +
            '<th class="p-3 text-right">Targets (T1 / T2)</th>' +
            '<th class="p-3 text-right">Stop Loss</th>' +
            '<th class="p-3 text-right">Live CMP</th>' +
            '<th class="p-3 text-right">Max High</th>' +
            '<th class="p-3 text-right">Return %</th>' +
            '<th class="p-3 text-center">Status</th>' +
            '<th class="p-3 text-center">Action</th>' +
          '</tr>' +
        '</thead>' +
        '<tbody>';

      history.forEach(h => {
        const stock = STOCKS_DATA.find(s => s.symbol === h.symbol);
        const liveCmp = stock ? stock.cmp : (h.current_cmp || h.trigger_cmp);
        const pnl = liveCmp - h.trigger_cmp;
        const pnlPct = h.trigger_cmp > 0 ? ((liveCmp - h.trigger_cmp) / h.trigger_cmp) * 100 : 0;
        const isUp = pnl >= 0;
        const pnlClass = isUp ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold';
        const pnlSign = isUp ? '+' : '';

        let statusBadge = '<span class="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/40 text-[10px] font-bold">RUNNING</span>';
        if (h.status === 'T2_HIT' || h.status === 'T3_HIT') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-bold">🎯 TARGET HIT</span>';
        } else if (h.status === 'SL_HIT') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 text-[10px] font-bold">🛑 STOPPED</span>';
        }

        html += '<tr class="border-b border-slate-800/60 hover:bg-slate-800/40 transition">' +
          '<td class="p-3 text-slate-400 whitespace-nowrap"><span class="font-bold text-slate-200">' + (h.trigger_date || '') + '</span> <span class="text-[10px] text-sky-400">' + (h.trigger_time || '') + '</span></td>' +
          '<td class="p-3 whitespace-nowrap"><span class="font-bold text-white text-sm">' + h.symbol + '</span> <span class="text-slate-400 text-[11px] block truncate max-w-[140px]">' + (h.name || '') + '</span></td>' +
          '<td class="p-3 whitespace-nowrap"><span class="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">' + (h.signal_type || 'SWING') + '</span></td>' +
          '<td class="p-3 text-right font-bold text-amber-300">₹' + (h.trigger_cmp ? h.trigger_cmp.toLocaleString('en-IN') : '-') + '</td>' +
          '<td class="p-3 text-right text-emerald-400">₹' + (h.target_1 || '-') + ' / ₹' + (h.target_2 || '-') + '</td>' +
          '<td class="p-3 text-right text-rose-400">₹' + (h.stop_loss || '-') + '</td>' +
          '<td class="p-3 text-right font-bold text-white">₹' + liveCmp.toLocaleString('en-IN') + '</td>' +
          '<td class="p-3 text-right text-sky-400">₹' + (h.highest_cmp || liveCmp) + '</td>' +
          '<td class="p-3 text-right ' + pnlClass + '">' + pnlSign + pnlPct.toFixed(2) + '%</td>' +
          '<td class="p-3 text-center whitespace-nowrap">' + statusBadge + '</td>' +
          '<td class="p-3 text-center whitespace-nowrap">' +
            '<button onclick="closeRadarModal(); openModal(' + "'" + h.symbol + "'" + ')" class="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 hover:bg-sky-500/30 text-[10px] font-bold transition">View ↗</button>' +
          '</td>' +
        '</tr>';
      });

      html += '</tbody></table></div>';
      container.innerHTML = html;
    }

    // =========================================================================
    // 5. RENDER COMPLETED JOURNAL & WIN-RATE ANALYTICS
    // =========================================================================
    function renderCompletedJournal() {
      let closed = [];
      if (cloudRadarDatabaseCache && cloudRadarDatabaseCache.completed_journal) {
        closed = cloudRadarDatabaseCache.completed_journal;
      } else {
        const list = getTrackedSignals();
        closed = list.filter(s => s.status !== 'RUNNING');
      }

      const wins = closed.filter(s => ['T1_HIT', 'T2_HIT', 'T3_HIT'].includes(s.status) || ((s.pnl_pct || 0) > 0)).length;
      const losses = closed.filter(s => s.status === 'SL_HIT' || ((s.pnl_pct || 0) <= 0)).length;
      const winRate = closed.length > 0 ? ((wins / closed.length) * 100) : 0;

      const grossGains = closed.filter(s => (s.pnl_pct || 0) > 0).reduce((acc, s) => acc + (s.pnl_pct || 0), 0);
      const grossLosses = Math.abs(closed.filter(s => (s.pnl_pct || 0) < 0).reduce((acc, s) => acc + (s.pnl_pct || 0), 0));
      const avgWin = wins > 0 ? (grossGains / wins) : 0;
      const profitFactor = grossLosses > 0 ? (grossGains / grossLosses) : (grossGains > 0 ? 9.9 : 0.0);

      const elWinRate = document.getElementById('kpiJournalWinRate');
      if (elWinRate) elWinRate.textContent = winRate.toFixed(1) + '%';
      const elWinSub = document.getElementById('kpiJournalWinSub');
      if (elWinSub) elWinSub.textContent = wins + ' Wins / ' + closed.length + ' Closed';
      const elTotal = document.getElementById('kpiJournalTotal');
      if (elTotal) elTotal.textContent = closed.length;
      const elWins = document.getElementById('kpiJournalWins');
      if (elWins) elWins.textContent = wins;
      const elLosses = document.getElementById('kpiJournalLosses');
      if (elLosses) elLosses.textContent = losses;
      const elAvgWin = document.getElementById('kpiJournalAvgWin');
      if (elAvgWin) elAvgWin.textContent = (avgWin > 0 ? '+' : '') + avgWin.toFixed(2) + '%';
      const elPF = document.getElementById('kpiJournalProfitFactor');
      if (elPF) elPF.textContent = profitFactor.toFixed(2) + 'x';

      const tbody = document.getElementById('journalTableBody');
      if (!tbody) return;

      if (closed.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="p-8 text-center text-slate-500 font-mono">No closed trades in journal yet. When a target or stop-loss hits, it is automatically archived here.</td></tr>';
        return;
      }

      let rows = '';
      closed.forEach(sig => {
        const isWin = (sig.pnl_pct || 0) >= 0;
        const pnlClass = isWin ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold';
        const pnlSign = isWin ? '+' : '';
        const triggeredStr = new Date(sig.triggered_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });

        let statusBadge = '';
        if (sig.status === 'T3_HIT') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 font-bold">🎯 TARGET 3 HIT</span>';
        } else if (sig.status === 'T2_HIT') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-bold">🎯 TARGET 2 HIT</span>';
        } else if (sig.status === 'T1_HIT') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold">🎯 TARGET 1 HIT</span>';
        } else if (sig.status === 'SL_HIT') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 font-bold">🛑 STOP HIT</span>';
        } else {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-medium">⏹️ EXITED</span>';
        }

        rows += '<tr class="hover:bg-slate-800/40 transition">' +
          '<td class="p-3 text-slate-400 text-[11px] whitespace-nowrap">' + triggeredStr + '</td>' +
          '<td class="p-3 whitespace-nowrap"><span class="font-bold text-white">' + sig.symbol + '</span> <span class="text-slate-400 text-[11px]">' + (sig.name || '') + '</span></td>' +
          '<td class="p-3 whitespace-nowrap"><span class="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">' + sig.horizon + '</span></td>' +
          '<td class="p-3 text-right text-slate-200">₹' + (sig.entry_price ? sig.entry_price.toLocaleString('en-IN') : '-') + '</td>' +
          '<td class="p-3 text-right text-emerald-400">₹' + (sig.target_1 || '-') + ' / ₹' + (sig.target_2 || '-') + '</td>' +
          '<td class="p-3 text-right text-rose-400">₹' + (sig.stop_loss || '-') + '</td>' +
          '<td class="p-3 text-right text-white font-bold">₹' + (sig.exit_price ? sig.exit_price.toLocaleString('en-IN') : '-') + '</td>' +
          '<td class="p-3 text-right ' + pnlClass + '">' + pnlSign + (sig.pnl_pct || 0).toFixed(2) + '%</td>' +
          '<td class="p-3 text-center whitespace-nowrap">' + statusBadge + '</td>' +
        '</tr>';
      });

      tbody.innerHTML = rows;
    }

    // =========================================================================
    // 6. SIGNAL MANAGEMENT ACTIONS (Dual Cloud & Local Persistence)
    // =========================================================================
    async function addTrackedSignal(sym, horizon = 'SWING', silent = false) {
      const s = STOCKS_DATA.find(x => x.symbol === sym);
      if (!s) return;

      const list = getTrackedSignals();
      const existing = list.find(x => x.symbol === sym && x.status === 'RUNNING');
      if (existing) {
        if (!silent) showToast(sym + ' is already actively tracked!', 'info');
        return;
      }

      const tb = s.trade_blueprint || {};
      const radar = evaluateBuyRadar(s);
      const chosenHorizon = horizon || (radar.isPerfect ? 'PERFECT' : (radar.isIntraday ? 'INTRADAY' : 'SWING'));

      const sig = {
        id: 'SIG_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5),
        symbol: s.symbol,
        name: s.name,
        horizon: chosenHorizon,
        entry_price: s.cmp,
        current_price: s.cmp,
        max_price: s.cmp,
        min_price: s.cmp,
        stop_loss: tb.stop_loss || Number((s.cmp * 0.96).toFixed(1)),
        target_1: tb.target_1 || Number((s.cmp * 1.04).toFixed(1)),
        target_2: tb.target_2 || Number((s.cmp * 1.08).toFixed(1)),
        target_3: tb.target_3 || Number((s.cmp * 1.12).toFixed(1)),
        status: 'RUNNING',
        pnl_pct: 0,
        triggered_at: new Date().toISOString(),
        closed_at: null,
        exit_price: null,
        notes: radar.reasons.join(', ')
      };

      list.unshift(sig);
      saveTrackedSignals(list);

      // Async post to live server
      try {
        fetch('http://127.0.0.1:8765/api/radar/track', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symbol: s.symbol, horizon: chosenHorizon, notes: radar.reasons.join(', ') })
        }).catch(() => {});
      } catch (e) {}

      if (!silent) {
        showToast('📌 Started tracking ' + s.symbol + ' @ ₹' + s.cmp, 'success');
        playAlertBeep('start');
      }

      updateRadarBadges();
      const radarModal = document.getElementById('radarModal');
      if (radarModal && !radarModal.classList.contains('hidden')) {
        renderRadarModal();
      }
    }

    function autoTrackAllRadar() {
      const runningSyms = new Set(getTrackedSignals().filter(x => x.status === 'RUNNING').map(x => x.symbol));
      let candidates = STOCKS_DATA.map(s => ({ stock: s, radar: evaluateBuyRadar(s) }))
        .filter(item => (item.radar.isPerfect || item.radar.isIntraday || item.radar.isSwing) && !runningSyms.has(item.stock.symbol));

      candidates.sort((a, b) => b.radar.alphaRank - a.radar.alphaRank);

      const top = candidates.slice(0, 5);
      if (top.length === 0) {
        showToast('All top radar setups are already tracked!', 'info');
        return;
      }

      top.forEach(c => {
        addTrackedSignal(c.stock.symbol, c.radar.isPerfect ? 'PERFECT' : (c.radar.isIntraday ? 'INTRADAY' : 'SWING'), true);
      });

      showToast('⚡ Auto-tracked ' + top.length + ' top high-probability radar setups!', 'success');
      playAlertBeep('start');
      renderRadarModal();
    }

    function closeTrackedSignal(id, reason = 'MANUAL_EXIT') {
      const list = getTrackedSignals();
      const sig = list.find(x => x.id === id);
      if (!sig || sig.status !== 'RUNNING') return;

      const stock = STOCKS_DATA.find(x => x.symbol === sig.symbol);
      sig.exit_price = stock ? stock.cmp : (sig.current_price || sig.entry_price);
      sig.status = reason;
      sig.closed_at = new Date().toISOString();
      sig.pnl_pct = sig.entry_price > 0 ? Number((((sig.exit_price - sig.entry_price) / sig.entry_price) * 100).toFixed(2)) : 0;

      saveTrackedSignals(list);
      showToast('Closed trade on ' + sig.symbol + ' (' + (sig.pnl_pct >= 0 ? '+' : '') + sig.pnl_pct + '%)', sig.pnl_pct >= 0 ? 'success' : 'warning');
      renderRadarModal();
    }

    // Real-Time Tracking Evaluator (called on every price quote sync)
    function updateTrackedSignalsLive(quotes) {
      const list = getTrackedSignals();
      let updatedAny = false;

      list.forEach(sig => {
        if (sig.status !== 'RUNNING') return;

        const q = quotes ? quotes[sig.symbol] : null;
        let currentPrice = q && q.curr_price > 0 ? q.curr_price : null;
        if (!currentPrice) {
          const s = STOCKS_DATA.find(x => x.symbol === sig.symbol);
          if (s) currentPrice = s.cmp;
        }
        if (!currentPrice || currentPrice <= 0) return;

        sig.current_price = currentPrice;
        sig.max_price = Math.max(sig.max_price || sig.entry_price, currentPrice);
        sig.min_price = Math.min(sig.min_price || sig.entry_price, currentPrice);
        sig.pnl_pct = sig.entry_price > 0 ? Number((((currentPrice - sig.entry_price) / sig.entry_price) * 100).toFixed(2)) : 0;

        if (currentPrice >= sig.target_3) {
          sig.status = 'T3_HIT';
          sig.exit_price = currentPrice;
          sig.closed_at = new Date().toISOString();
          updatedAny = true;
        } else if (currentPrice >= sig.target_2) {
          sig.status = 'T2_HIT';
          sig.exit_price = currentPrice;
          sig.closed_at = new Date().toISOString();
          updatedAny = true;
        } else if (currentPrice >= sig.target_1 && sig.status === 'RUNNING') {
          sig.status = 'T1_HIT';
          updatedAny = true;
        } else if (currentPrice <= sig.stop_loss) {
          sig.status = 'SL_HIT';
          sig.exit_price = currentPrice;
          sig.closed_at = new Date().toISOString();
          updatedAny = true;
        }
      });

      if (updatedAny) {
        saveTrackedSignals(list);
      }
    }
