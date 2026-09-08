    // =========================================================================
    // 2. RENDER RADAR CANDIDATES (Ranked by High Win-Rate & High R:R)
    // =========================================================================
    function renderRadarCandidates() {
      const container = document.getElementById('radarCardsGrid');
      if (!container) return;

      let candidates = STOCKS_DATA.map(s => {
        const radar = evaluateBuyRadar(s);
        return { stock: s, radar };
      }).filter(item => item.radar.isIntraday || item.radar.isSwing || item.radar.isPerfect);

      if (activeRadarCandidateFilter === 'INTRADAY') {
        candidates = candidates.filter(item => item.radar.isIntraday);
      } else if (activeRadarCandidateFilter === 'SWING') {
        candidates = candidates.filter(item => item.radar.isSwing);
      } else if (activeRadarCandidateFilter === 'PERFECT') {
        candidates = candidates.filter(item => item.radar.isPerfect);
      }

      // Decisive Ranking: Highest Win-Rate & High R:R Alpha Rank
      candidates.sort((a, b) => b.radar.alphaRank - a.radar.alphaRank);

      const countPill = document.getElementById('radarCandidatesCountPill');
      if (countPill) countPill.textContent = candidates.length;

      const statusEl = document.getElementById('radarSummaryStatus');
      if (statusEl) {
        statusEl.innerHTML = '<span class="text-emerald-400 font-bold">' + candidates.length + ' High-Probability Setups</span> ranked by Win-Rate % and R:R Ratio';
      }

      if (candidates.length === 0) {
        container.innerHTML = '<div class="col-span-full py-12 text-center text-slate-500 font-mono"><span class="text-3xl">🔍</span><p class="mt-2 text-sm text-slate-400">No stocks currently matching the filter.</p></div>';
        return;
      }

      const trackedSet = new Set(getTrackedSignals().filter(x => x.status === 'RUNNING').map(x => x.symbol));
      const nowFormatted = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

      let html = '';
      candidates.forEach(({ stock: s, radar }) => {
        const isTracked = trackedSet.has(s.symbol);
        const tb = s.trade_blueprint || {};
        const rr = tb.rr_ratio || 2.2;
        
        let typeBadge = '';
        if (radar.isPerfect) {
          typeBadge = '<span class="px-2 py-0.5 rounded bg-purple-500/25 text-purple-300 border border-purple-500/40 text-[10px] font-black uppercase tracking-wider animate-pulse">🌟 PERFECT SETUP (ALPHA)</span>';
        } else if (radar.isIntraday) {
          typeBadge = '<span class="px-2 py-0.5 rounded bg-amber-500/25 text-amber-300 border border-amber-500/40 text-[10px] font-bold uppercase tracking-wider">⚡ INTRADAY BREAKOUT</span>';
        } else {
          typeBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/25 text-emerald-300 border border-emerald-500/40 text-[10px] font-bold uppercase tracking-wider">🚀 2-5D SWING</span>';
        }

        const isUp = s.day_change >= 0;
        const chgSign = isUp ? '+' : '';
        const chgClass = isUp ? 'text-emerald-400' : 'text-rose-400';

        html += '<div class="p-4 rounded-xl bg-slate-900/95 theme-card border ' + (radar.isPerfect ? 'border-purple-500/50 shadow-lg shadow-purple-950/20' : 'border-slate-800 theme-border') + ' hover:border-sky-500/50 transition flex flex-col justify-between gap-2.5">' +
          '<div>' +
            '<div class="flex items-start justify-between gap-2 pb-2.5 border-b border-slate-800/80">' +
              '<div>' +
                '<div class="flex items-center gap-1.5">' +
                  '<span class="font-mono font-bold text-white text-base">' + s.symbol + '</span>' +
                  '<span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono">' + s.mcap_tier + '</span>' +
                '</div>' +
                '<div class="text-xs text-slate-400 truncate max-w-[190px]">' + s.name + '</div>' +
              '</div>' +
              '<div class="text-right">' +
                '<div class="font-mono font-bold text-white text-base">₹' + s.cmp.toLocaleString('en-IN') + '</div>' +
                '<div class="flex items-center gap-1 text-[11px] font-mono justify-end">' +
                  '<span class="' + chgClass + ' font-semibold">' + chgSign + s.day_change_pct.toFixed(2) + '%</span>' +
                  '<span class="text-[10px] px-1 rounded bg-slate-800 text-sky-400">Vol: ' + (s.vol_ratio || 1.0) + 'x</span>' +
                '</div>' +
              '</div>' +
            '</div>' +

            '<div class="mt-2 flex items-center justify-between gap-2 flex-wrap">' +
              typeBadge +
              '<div class="flex items-center gap-2 font-mono text-xs">' +
                '<span class="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-500/30 font-bold">🎯 Win-Rate: ' + radar.winRatePct + '%</span>' +
                '<span class="px-2 py-0.5 rounded bg-sky-950/60 text-sky-300 border border-sky-500/30 font-bold">⚖️ R:R 1:' + rr + '</span>' +
              '</div>' +
            '</div>' +

            '<div class="mt-2 flex flex-wrap gap-1">' +
              radar.reasons.map(r => '<span class="px-1.5 py-0.5 rounded bg-slate-950 text-[10px] font-mono text-slate-300 border border-slate-800">' + r + '</span>').join('') +
            '</div>' +

            '<div class="mt-2.5 p-2 rounded-lg bg-slate-950/80 border border-slate-800/80 font-mono text-xs grid grid-cols-3 gap-1.5 text-center">' +
              '<div class="p-1 rounded bg-rose-950/30 text-rose-400"><span class="text-[9px] block text-rose-500/80">Stop-Loss</span><span class="font-bold">₹' + (tb.stop_loss || (s.cmp * 0.96).toFixed(1)) + '</span></div>' +
              '<div class="p-1 rounded bg-emerald-950/30 text-emerald-400"><span class="text-[9px] block text-emerald-500/80">Target 1</span><span class="font-bold">₹' + (tb.target_1 || (s.cmp * 1.04).toFixed(1)) + '</span></div>' +
              '<div class="p-1 rounded bg-sky-950/30 text-sky-300"><span class="text-[9px] block text-sky-500/80">Target 2</span><span class="font-bold">₹' + (tb.target_2 || (s.cmp * 1.08).toFixed(1)) + '</span></div>' +
            '</div>' +
          '</div>' +

          '<div class="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2 text-xs font-mono">' +
            '<span class="text-slate-500 text-[11px]">Signal Active Today</span>' +
            '<div class="flex items-center gap-2">' +
              '<button onclick="closeRadarModal(); openModal(' + "'" + s.symbol + "'" + ')" class="text-xs text-sky-400 hover:text-sky-300 font-semibold transition">360° View ↗</button>' +
              '<button onclick="addTrackedSignal(' + "'" + s.symbol + "', '" + (radar.isPerfect ? 'PERFECT' : (radar.isIntraday ? 'INTRADAY' : 'SWING')) + "'" + ')" class="px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 active:scale-95 ' + (isTracked ? 'bg-slate-800 text-slate-400 cursor-default' : 'bg-gradient-to-r from-amber-500 to-emerald-500 text-slate-950 hover:brightness-110 shadow-sm') + '">' +
                '<span>' + (isTracked ? '✓ Tracking' : '📌 Auto-Track') + '</span>' +
              '</button>' +
            '</div>' +
          '</div>' +
        '</div>';
      });

      container.innerHTML = html;
    }
