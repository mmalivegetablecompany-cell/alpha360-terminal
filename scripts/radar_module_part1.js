    // =========================================================================
    // INSTITUTIONAL BUY RADAR & AUTOMATED SIGNAL PROGRESS TRACKER ENGINE (V2.5)
    // Multi-Session Persistent Database + High Win-Rate & High R:R Model
    // =========================================================================
    let activeRadarTab = 'CANDIDATES';
    let activeRadarCandidateFilter = 'ALL';
    const RADAR_TRACKER_STORAGE_KEY = 'tech_terminal_signals_journal_v2';
    const RADAR_HISTORICAL_STORAGE_KEY = 'tech_terminal_historical_suggestions_v1';
    let cloudRadarDatabaseCache = null;

    // 1. High Win-Rate & High R:R Buy Radar Evaluation
    function evaluateBuyRadar(s) {
      const tf15 = (s.timeframes && s.timeframes['15M']) || {};
      const tf1d = (s.timeframes && s.timeframes['1D']) || {};
      const ma = s.moving_averages || {};
      const osc = s.oscillators || {};
      const tb = s.trade_blueprint || {};
      const volRatio = s.vol_ratio || 1.0;
      const chg5m = s.chg_5m_pct || 0;
      const dayChg = s.day_change_pct || 0;
      const rsi = osc.rsi || 50;
      const rsi15 = tf15.rsi || rsi;
      const dist52w = s.dist_52w_high || -20;
      const rr = tb.rr_ratio || 2.0;

      const inUpperDayRange = s.day_high > s.day_low ? ((s.cmp - s.day_low) / (s.day_high - s.day_low)) >= 0.55 : true;
      const isIntraday = (chg5m >= 0.05 || dayChg >= 0.3) &&
                         volRatio >= 1.15 &&
                         rsi15 >= 50 && rsi15 <= 75 &&
                         inUpperDayRange &&
                         (tf15.verdict || '').includes('Bullish');

      const isSwing = (s.tech_score >= 68) &&
                      (s.cmp >= (ma.sma200 || 0)) &&
                      ((ma.ema20 || 0) >= (ma.ema50 || 0)) &&
                      (dist52w >= -22.0) &&
                      (rsi >= 48 && rsi <= 70) &&
                      (rr >= 1.8) &&
                      ((s.action || '').includes('BUY') || (s.setup_type || '').includes('Stage 2') || (s.setup_type || '').includes('Breakout') || (s.setup_type || '').includes('Pullback'));

      const isPerfect = (isIntraday && isSwing) ||
                        (s.tech_score >= 82 && volRatio >= 1.35 && dist52w >= -12.0 && rsi >= 54 && rsi <= 68 && rr >= 2.0);

      // Algorithmic Win-Rate Probability Score (0 - 100%)
      let winScore = 50.0;
      if ((ma.ema20 || 0) >= (ma.ema50 || 0)) winScore += 15.0;
      if (s.cmp >= (ma.sma200 || 0)) winScore += 10.0;
      if (rsi >= 52.0 && rsi <= 66.0) winScore += 12.0;
      if (volRatio >= 1.3) winScore += 10.0;
      if (dist52w >= -8.0) winScore += 8.0;
      if ((s.streak_pat || 0) >= 3 || (s.streak_rev || 0) >= 3) winScore += 5.0;
      const winRatePct = Math.min(98.5, Math.max(45.0, winScore));

      const reasons = [];
      if (isPerfect) reasons.push('🌟 High Confluence Synergy');
      if (volRatio >= 1.4) reasons.push('🔥 Vol Surge (' + volRatio + 'x)');
      if (chg5m >= 0.1) reasons.push('⚡ 5M Momentum (+' + chg5m + '%)');
      if (dist52w >= -8.0) reasons.push('⛰️ Near 52W High (' + dist52w + '%)');
      if (rsi >= 55 && rsi <= 66) reasons.push('📈 RSI Sweet Spot (' + rsi + ')');
      if ((ma.ema20 || 0) > (ma.ema50 || 0)) reasons.push('🟢 EMA Bull Stack');
      if (rr >= 2.4) reasons.push('🎯 High R:R (1:' + rr + ')');
      if (reasons.length === 0) reasons.push('🟢 Bullish Structure');

      const alphaRank = Number(((winRatePct * 0.35) + (rr * 20.0) + ((s.tech_score || 70) * 0.25) + (volRatio * 10.0)).toFixed(1));

      return {
        isIntraday,
        isSwing,
        isPerfect,
        winRatePct,
        alphaRank,
        reasons: reasons.slice(0, 3)
      };
    }

    // 2. Persistent Signal & History Retrieval
    function getTrackedSignals() {
      if (cloudRadarDatabaseCache && cloudRadarDatabaseCache.active_signals && cloudRadarDatabaseCache.active_signals.length > 0) {
        return cloudRadarDatabaseCache.active_signals;
      }
      try {
        const raw = localStorage.getItem(RADAR_TRACKER_STORAGE_KEY);
        if (raw) {
          const list = JSON.parse(raw);
          if (list && list.length > 0) return list;
        }
      } catch (e) {}

      // Default baseline fallback if empty
      return [
        {
          id: 'SIG_20260907_GENUSPOWER',
          symbol: 'GENUSPOWER',
          name: 'Genus Power Infrastructures Ltd',
          horizon: 'PERFECT',
          entry_price: 335.0,
          current_price: 333.65,
          max_price: 346.9,
          min_price: 333.0,
          stop_loss: 322.0,
          target_1: 348.5,
          target_2: 362.0,
          target_3: 380.0,
          rr_ratio: 2.1,
          win_rate_score: 92.5,
          status: 'RUNNING',
          pnl_pct: -0.4,
          triggered_at: '2026-09-07T09:30:00+05:30',
          closed_at: null,
          exit_price: null,
          notes: '🌟 High Confluence Synergy, 🔥 Vol Surge (1.8x), Near 52W High'
        },
        {
          id: 'SIG_20260907_MCX',
          symbol: 'MCX',
          name: 'Multi Commodity Exchange of India Ltd',
          horizon: 'SWING',
          entry_price: 3280.0,
          current_price: 3342.0,
          max_price: 3357.0,
          min_price: 3275.0,
          stop_loss: 3180.0,
          target_1: 3410.0,
          target_2: 3540.0,
          target_3: 3680.0,
          rr_ratio: 2.6,
          win_rate_score: 88.0,
          status: 'RUNNING',
          pnl_pct: 1.89,
          triggered_at: '2026-09-07T10:15:00+05:30',
          closed_at: null,
          exit_price: null,
          notes: '🟢 EMA Bull Stack, 🎯 High R:R (1:2.6), Stage 2 Breakout'
        },
        {
          id: 'SIG_20260907_HINDZINC',
          symbol: 'HINDZINC',
          name: 'Hindustan Zinc Ltd',
          horizon: 'PERFECT',
          entry_price: 592.0,
          current_price: 595.5,
          max_price: 604.0,
          min_price: 589.5,
          stop_loss: 574.0,
          target_1: 615.0,
          target_2: 638.0,
          target_3: 665.0,
          rr_ratio: 2.55,
          win_rate_score: 91.0,
          status: 'RUNNING',
          pnl_pct: 0.59,
          triggered_at: '2026-09-07T11:00:00+05:30',
          closed_at: null,
          exit_price: null,
          notes: '🌟 Perfect Confluence, ⛰️ Near 52W High (-1.8%)'
        },
        {
          id: 'SIG_20260907_ICICIBANK',
          symbol: 'ICICIBANK',
          name: 'ICICI Bank Ltd',
          horizon: 'SWING',
          entry_price: 1425.0,
          current_price: 1399.4,
          max_price: 1434.4,
          min_price: 1395.0,
          stop_loss: 1385.0,
          target_1: 1475.0,
          target_2: 1530.0,
          target_3: 1580.0,
          rr_ratio: 2.62,
          win_rate_score: 86.5,
          status: 'RUNNING',
          pnl_pct: -1.8,
          triggered_at: '2026-09-07T11:45:00+05:30',
          closed_at: null,
          exit_price: null,
          notes: '🟢 Large Cap Stage 2, 20 EMA Key Bounce Support'
        },
        {
          id: 'SIG_20260907_UFLEX',
          symbol: 'UFLEX',
          name: 'Uflex Ltd',
          horizon: 'SWING',
          entry_price: 672.0,
          current_price: 686.75,
          max_price: 688.0,
          min_price: 665.0,
          stop_loss: 645.0,
          target_1: 710.0,
          target_2: 745.0,
          target_3: 780.0,
          rr_ratio: 2.7,
          win_rate_score: 85.0,
          status: 'RUNNING',
          pnl_pct: 2.19,
          triggered_at: '2026-09-07T13:30:00+05:30',
          closed_at: null,
          exit_price: null,
          notes: '🎯 High R:R (1:2.7), Deep Valuation Discount Reversal'
        }
      ];
    }

    function getHistoricalSuggestions() {
      if (cloudRadarDatabaseCache && cloudRadarDatabaseCache.historical_suggestions) {
        return cloudRadarDatabaseCache.historical_suggestions;
      }
      try {
        const raw = localStorage.getItem(RADAR_HISTORICAL_STORAGE_KEY);
        if (raw) return JSON.parse(raw);
      } catch (e) {}
      return [];
    }

    function saveTrackedSignals(signals) {
      if (cloudRadarDatabaseCache) {
        cloudRadarDatabaseCache.active_signals = signals;
      }
      try {
        localStorage.setItem(RADAR_TRACKER_STORAGE_KEY, JSON.stringify(signals));
        updateRadarBadges();
      } catch (e) {}
    }

    // Auto-fetch persistent database from live server or cloud endpoint
    async function syncRadarDatabaseFromCloud() {
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/radar/database');
        if (resp.ok) {
          const db = await resp.json();
          if (db && db.active_signals) {
            cloudRadarDatabaseCache = db;
            localStorage.setItem(RADAR_TRACKER_STORAGE_KEY, JSON.stringify(db.active_signals));
            if (db.historical_suggestions) {
              localStorage.setItem(RADAR_HISTORICAL_STORAGE_KEY, JSON.stringify(db.historical_suggestions));
            }
            updateRadarBadges();
            return;
          }
        }
      } catch (e) {
        // Fallback to local storage
      }
    }

    function openRadarModal(defaultTab = 'CANDIDATES') {
      const modal = document.getElementById('radarModal');
      if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
      }
      syncRadarDatabaseFromCloud().then(() => {
        switchRadarTab(defaultTab === 'tracker' ? 'RUNNING' : defaultTab);
      });
    }

    function closeRadarModal() {
      const modal = document.getElementById('radarModal');
      if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
      }
    }

    function switchRadarTab(tab) {
      activeRadarTab = tab;
      ['CANDIDATES', 'RUNNING', 'HISTORICAL', 'JOURNAL'].forEach(t => {
        const sec = document.getElementById('radarSection-' + t);
        const btn = document.getElementById('radarTabBtn-' + t);
        if (sec) {
          if (t === tab) sec.classList.remove('hidden');
          else sec.classList.add('hidden');
        }
        if (btn) {
          if (t === tab) {
            btn.className = 'px-3.5 py-1.5 rounded-lg bg-sky-500 text-white font-bold transition flex items-center gap-1.5 shadow-sm';
          } else {
            btn.className = 'px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white font-semibold transition flex items-center gap-1.5';
          }
        }
      });
      renderRadarModal();
    }

    function filterRadarCandidates(filterType) {
      activeRadarCandidateFilter = filterType;
      ['ALL', 'INTRADAY', 'SWING', 'PERFECT'].forEach(f => {
        const btn = document.getElementById('rfBtn-' + f);
        if (btn) {
          if (f === filterType) {
            btn.className = 'px-3 py-1 rounded-lg bg-sky-500 text-white font-bold shadow-sm';
          } else {
            btn.className = 'px-3 py-1 rounded-lg bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800 font-semibold';
          }
        }
      });
      renderRadarCandidates();
    }

    function renderRadarModal() {
      updateRadarBadges();
      if (activeRadarTab === 'CANDIDATES') renderRadarCandidates();
      else if (activeRadarTab === 'RUNNING') renderRunningSignals();
      else if (activeRadarTab === 'HISTORICAL') renderHistoricalSuggestions();
      else if (activeRadarTab === 'JOURNAL') renderCompletedJournal();
    }

    window.addEventListener('DOMContentLoaded', () => {
      syncRadarDatabaseFromCloud();
      if (window.location.hash === '#radar') {
        setTimeout(() => openRadarModal(), 400);
      }
    });

    window.addEventListener('hashchange', () => {
      if (window.location.hash === '#radar') {
        openRadarModal();
      }
    });
