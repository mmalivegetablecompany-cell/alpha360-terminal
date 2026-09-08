import json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

def update_html_clean():
    print("==================================================================")
    print("=== REBUILDING HTML DASHBOARD WITH CLEAN MODAL INTEGRATION =======")
    print("==================================================================")

    # Start from clean backup
    with open("Stock_Growth_and_Selection_Analyzer.html.pre_et_prime.bak", "r", encoding="utf-8") as f:
        html = f.read()

    with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)
    print(f"Loaded {len(stocks)} stocks from combined_master_stocks.json.")

    # 1. Replace rawData
    s_idx = html.find("const rawData =")
    e_idx = html.find("let currentData =", s_idx)
    if s_idx == -1 or e_idx == -1:
        print("Error: Could not find rawData boundaries")
        return False

    new_json_str = json.dumps(stocks, ensure_ascii=False)
    html = html[:s_idx] + f"const rawData = {new_json_str};\n  " + html[e_idx:]
    print("✓ Successfully replaced rawData in HTML.")

    # 2. Add et_stock_score to MASTER_COLUMN_DEFS
    target = "{ id: 'master_score', label: 'Master Quad', sortKey: 'master_score', defaultOrder: 22 },"
    replacement = target + "\n    { id: 'et_stock_score', label: 'ET Prime Score', sortKey: 'et_stock_score', defaultOrder: 22 },"
    html = html.replace(target, replacement, 1)
    print("✓ Added et_stock_score to MASTER_COLUMN_DEFS.")

    # 3. Add et_stock_score renderer to cellRenderers
    target = "master_score: (s) => `<td style=\"text-align:right; font-weight:900; color:var(--accent-gold); font-size:15px;\">${s.master_score}</td>`,"
    replacement = target + """
    et_stock_score: (s) => {
      const ep = s.et_prime || {};
      const sc = ep.stock_score;
      if (sc === null || sc === undefined) {
        return `<td style="text-align:center; color:var(--text-muted); font-size:11.5px; font-weight:700;">NR</td>`;
      }
      let bg = 'rgba(52, 211, 153, 0.18)'; let color = '#34D399';
      if (sc <= 3) { bg = 'rgba(239, 68, 68, 0.18)'; color = '#EF4444'; }
      else if (sc <= 7) { bg = 'rgba(251, 191, 36, 0.18)'; color = '#FBBF24'; }
      return `<td style="text-align:center;">
        <span style="background:${bg}; color:${color}; padding:2px 8px; border-radius:6px; font-weight:800; font-size:12.5px; display:inline-block;">${sc}/10</span>
        <div style="font-size:9.5px; color:var(--text-muted); margin-top:1px; font-weight:600;">${ep.score_outlook || ''}</div>
      </td>`;
    },"""
    html = html.replace(target, replacement, 1)
    print("✓ Added et_stock_score to cellRenderers.")

    # 4. Add sortTable logic for et_stock_score
    target = "if (key === 'forecast_upside') {"
    replacement = """if (key === 'et_stock_score') {
        valA = (a.et_prime && a.et_prime.stock_score !== null && a.et_prime.stock_score !== undefined) ? a.et_prime.stock_score : -1;
        valB = (b.et_prime && b.et_prime.stock_score !== null && b.et_prime.stock_score !== undefined) ? b.et_prime.stock_score : -1;
      } else if (key === 'forecast_upside') {"""
    html = html.replace(target, replacement, 1)
    print("✓ Added et_stock_score to sortTable.")

    # 5. Add localStorage activeColumns migration for et_stock_score
    target = "if (!activeColumns.includes('today_pb')) {"
    replacement = """if (!activeColumns.includes('et_stock_score')) {
          const msIdx = activeColumns.indexOf('master_score');
          if (msIdx !== -1) activeColumns.splice(msIdx + 1, 0, 'et_stock_score');
          else activeColumns.push('et_stock_score');
        }
        if (!activeColumns.includes('today_pb')) {"""
    html = html.replace(target, replacement, 1)
    print("✓ Added et_stock_score localStorage activeColumns migration.")

    # 6. Add ET button in top nav
    target = '<a id="linkScreener" class="tool-btn" target="_blank" href="#">📑 Screener.in</a>'
    replacement = target + '\n      <a id="linkET" class="tool-btn" target="_blank" href="#" style="border-color:#F97316; color:#FB923C;">📰 ET Markets</a>'
    html = html.replace(target, replacement, 1)
    print("✓ Added linkET button to top nav.")

    # 7. Update linkET in renderActiveTerminalStock
    target = "document.getElementById('linkScreener').href = `https://www.screener.in/company/${cleanSym}/consolidated/`;"
    replacement = target + """
    const linkET = document.getElementById('linkET');
    if (linkET) {
      if (ep.seo_name && ep.company_id) {
        linkET.href = `https://economictimes.indiatimes.com/${ep.seo_name}/stocks/companyid-${ep.company_id}.cms`;
        linkET.style.display = 'inline-flex';
      } else {
        linkET.style.display = 'none';
      }
    }"""
    html = html.replace(target, replacement, 1)
    print("✓ Added linkET href update in renderActiveTerminalStock.")

    # 8. Ensure ep is defined in renderActiveTerminalStock
    target = "const t = stock.technicals || {};"
    replacement = "const t = stock.technicals || {};\n    const ep = stock.et_prime || {};"
    html = html.replace(target, replacement, 1)
    print("✓ Ensured ep is defined in renderActiveTerminalStock.")

    # 9. Add ET Prime score to modalScoreBanner
    target = """<div class="score-item">
        <div class="score-lbl">Master Quad Score</div>"""
    replacement = """<div class="score-item" style="border-left: 2px solid rgba(168, 85, 247, 0.45);">
        <div class="score-lbl">ET Prime Score</div>
        <div class="score-num" style="color:#C084FC;">${(ep.stock_score !== null && ep.stock_score !== undefined) ? ep.stock_score + '/10' : 'NR'}</div>
        <div style="font-size:11px; color:var(--text-muted);">${ep.score_outlook || 'No Rating'}</div>
      </div>
      <div class="score-item">
        <div class="score-lbl">Master Quad Score</div>"""
    html = html.replace(target, replacement, 1)
    print("✓ Added ET Prime Score block to modalScoreBanner.")

    # 10. Replace ONLY tab-forecast (from its start to its terminating `;)
    tf_start_marker = "document.getElementById('tab-forecast').innerHTML = `"
    tf_start_pos = html.find(tf_start_marker)
    if tf_start_pos == -1:
        print("Error: Could not find tab-forecast start marker")
        return False
        
    tf_end_pos = html.find("`;", tf_start_pos)
    if tf_end_pos == -1:
        print("Error: Could not find tab-forecast end marker (`;)")
        return False
        
    tf_end_pos += 2 # include `;

    upgraded_tab_forecast = """document.getElementById('tab-forecast').innerHTML = `
      <div class="forecast-box" style="background:#FFFFFF; color:#0F172A; border-radius:12px; padding:20px; box-shadow:0 4px 20px rgba(0,0,0,0.06); border:1px solid #E2E8F0;">
        <div class="forecast-header" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; padding-bottom:12px; border-bottom:1px solid #E2E8F0;">
          <div style="display:flex; align-items:center; gap:10px;">
            <h2 style="margin:0; font-size:18px; font-weight:900; letter-spacing:0.5px; color:#0F172A;">ET MARKETS & ET PRIME INSTITUTIONAL INTELLIGENCE</h2>
            <span class="badge-new-pill" style="background:#8B5CF6; color:#FFF; font-size:10px; font-weight:800; padding:2px 8px; border-radius:12px; text-transform:uppercase;">Official ET Feeds</span>
          </div>
          <span style="font-size:12px; color:#64748B; font-weight:600;">Refinitiv Research • 12M Price Horizon</span>
        </div>

        <!-- TWO CORE CARDS MATCHING USER SCREENSHOT -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(440px, 1fr)); gap:18px; margin-bottom:20px;">
          
          <!-- CARD 1: Stock Recommendations (ET Markets) -->
          <div style="border:1px solid #E2E8F0; border-radius:12px; padding:18px; background:#FAFAFA;">
            <div style="font-size:14px; font-weight:800; color:#1E293B; margin-bottom:14px; display:flex; align-items:center; justify-content:space-between;">
              <span>Stock Recommendations</span>
              <span style="font-size:11px; font-weight:700; color:#0284C7; background:#E0F2FE; padding:2px 8px; border-radius:4px; border:1px solid #BAE6FD;">
                ${f.num_analysts || 0} Analyst Coverage
              </span>
            </div>

            <!-- Top 3 Stat Cards -->
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:16px;">
              
              <!-- Potential Upside -->
              <div style="background:${f.upside_mean_pct < 0 ? '#FEF2F2' : '#ECFDF5'}; border:1px solid ${f.upside_mean_pct < 0 ? '#FECACA' : '#A7F3D0'}; border-radius:8px; padding:12px 10px; text-align:center;">
                <div style="font-size:22px; font-weight:900; color:${f.upside_mean_pct < 0 ? '#DC2626' : '#059669'}; font-family:'JetBrains Mono', monospace;">
                  ${f.upside_mean_pct !== null && f.upside_mean_pct !== undefined ? (f.upside_mean_pct > 0 ? '+' : '') + f.upside_mean_pct + '%' : 'NR'}
                </div>
                <div style="font-size:11px; font-weight:700; color:#64748B; margin-top:2px;">Potential Upside*</div>
              </div>

              <!-- 1 Year Target -->
              <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:12px 10px; text-align:center;">
                <div style="font-size:20px; font-weight:900; color:#0F172A; font-family:'JetBrains Mono', monospace;">
                  ${f.mean_target ? '₹' + Math.round(f.mean_target).toLocaleString('en-IN') : 'NR'}
                </div>
                <div style="font-size:11px; font-weight:700; color:#64748B; margin-top:2px;">1 Year Target</div>
              </div>

              <!-- Mean Recos -->
              <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:12px 10px; text-align:center;">
                <div style="font-size:18px; font-weight:900; color:${f.consensus_rating && f.consensus_rating.toLowerCase().includes('buy') ? '#059669' : (f.consensus_rating && f.consensus_rating.toLowerCase().includes('hold') ? '#D97706' : '#DC2626')};">
                  ${f.consensus_rating || 'NR'}
                </div>
                <div style="font-size:10.5px; font-weight:700; color:#64748B; margin-top:2px;">Mean Recos by ${f.num_analysts || 0} Analysts</div>
              </div>
            </div>

            <!-- Analyst Recommendation Distribution Bars -->
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:12px 14px;">
              <div style="font-size:11.5px; font-weight:800; color:#475569; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.5px;">
                Analyst Recommendation Breakdown
              </div>
              <div style="display:flex; align-items:flex-end; justify-content:space-around; height:75px; padding-bottom:6px; border-bottom:1px solid #E2E8F0;">
                
                <!-- Strong Sell -->
                <div style="display:flex; flex-direction:column; align-items:center; width:65px;">
                  <span style="font-size:11px; font-weight:800; color:#DC2626;">${b.strong_sell || 0}</span>
                  <div style="width:30px; height:${Math.max(4, (b.strong_sell || 0) * 8)}px; max-height:50px; background:#DC2626; border-radius:3px 3px 0 0; margin-top:3px;"></div>
                </div>

                <!-- Sell -->
                <div style="display:flex; flex-direction:column; align-items:center; width:65px;">
                  <span style="font-size:11px; font-weight:800; color:#F87171;">${b.sell || 0}</span>
                  <div style="width:30px; height:${Math.max(4, (b.sell || 0) * 8)}px; max-height:50px; background:#F87171; border-radius:3px 3px 0 0; margin-top:3px;"></div>
                </div>

                <!-- Hold -->
                <div style="display:flex; flex-direction:column; align-items:center; width:65px;">
                  <span style="font-size:11px; font-weight:800; color:#94A3B8;">${b.hold || 0}</span>
                  <div style="width:30px; height:${Math.max(4, (b.hold || 0) * 8)}px; max-height:50px; background:#CBD5E1; border-radius:3px 3px 0 0; margin-top:3px;"></div>
                </div>

                <!-- Buy -->
                <div style="display:flex; flex-direction:column; align-items:center; width:65px;">
                  <span style="font-size:11px; font-weight:800; color:#10B981;">${b.buy || 0}</span>
                  <div style="width:30px; height:${Math.max(4, (b.buy || 0) * 8)}px; max-height:50px; background:#10B981; border-radius:3px 3px 0 0; margin-top:3px;"></div>
                </div>

                <!-- Strong Buy -->
                <div style="display:flex; flex-direction:column; align-items:center; width:65px;">
                  <span style="font-size:11px; font-weight:800; color:#059669;">${b.strong_buy || 0}</span>
                  <div style="width:30px; height:${Math.max(4, (b.strong_buy || 0) * 8)}px; max-height:50px; background:#059669; border-radius:3px 3px 0 0; margin-top:3px;"></div>
                </div>
              </div>

              <!-- Bar Labels -->
              <div style="display:flex; justify-content:space-around; font-size:10px; font-weight:700; color:#64748B; margin-top:6px; text-align:center;">
                <span style="width:65px;">Strong Sell</span>
                <span style="width:65px;">Sell</span>
                <span style="width:65px;">Hold</span>
                <span style="width:65px;">Buy</span>
                <span style="width:65px;">Strong Buy</span>
              </div>
            </div>

            <div style="font-size:10px; color:#94A3B8; margin-top:10px; font-style:italic;">
              * Investments in securities are subject to market risks. These are indicative and should not be interpreted as investment advice or guaranteed returns.
            </div>
          </div>

          <!-- CARD 2: Stock Reports Plus (Refinitiv / ET Prime) -->
          <div style="border:1px solid #E2E8F0; border-radius:12px; padding:18px; background:#FAFAFA;">
            <div style="font-size:14px; font-weight:800; color:#1E293B; margin-bottom:14px; display:flex; align-items:center; justify-content:space-between;">
              <span>Stock Reports Plus</span>
              <span style="font-size:11px; font-weight:700; color:#7C3AED; background:#EDE9FE; padding:2px 8px; border-radius:4px; border:1px solid #DDD6FE;">
                Powered by Refinitiv
              </span>
            </div>

            <div style="display:grid; grid-template-columns:140px 1fr; gap:16px; align-items:center;">
              
              <!-- Left Score Block -->
              <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:16px 12px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
                <div style="font-size:32px; font-weight:900; color:#0F172A; font-family:'JetBrains Mono', monospace; line-height:1;">
                  ${ep.stock_score !== null && ep.stock_score !== undefined ? ep.stock_score + '<span style="font-size:18px; color:#64748B; font-weight:600;">/10</span>' : 'NR'}
                </div>
                <div style="font-size:11px; font-weight:800; color:#475569; text-transform:uppercase; margin-top:6px; letter-spacing:0.5px;">
                  Stock Score
                </div>
                ${ep.score_outlook ? `<div style="display:inline-block; font-size:10px; font-weight:800; color:${ep.score_outlook === 'POSITIVE' ? '#059669' : (ep.score_outlook === 'NEGATIVE' ? '#DC2626' : '#D97706')}; background:${ep.score_outlook === 'POSITIVE' ? '#ECFDF5' : (ep.score_outlook === 'NEGATIVE' ? '#FEF2F2' : '#FFFBEB')}; padding:1px 6px; border-radius:4px; margin-top:4px;">${ep.score_outlook}</div>` : ''}
                
                <div style="margin-top:12px;">
                  ${ep.pdf_link ? `<a href="${ep.pdf_link}" target="_blank" style="display:inline-flex; align-items:center; gap:5px; background:#DC2626; color:#FFFFFF; font-size:11px; font-weight:800; padding:6px 10px; border-radius:6px; text-decoration:none; box-shadow:0 2px 4px rgba(220,38,38,0.25);">
                    <span style="font-size:13px;">📄</span> View Report
                  </a>` : `<span style="font-size:10.5px; color:#94A3B8;">No PDF Available</span>`}
                </div>
              </div>

              <!-- Right Score Meters -->
              <div style="display:flex; flex-direction:column; gap:8px;">
                ${[
                  { label: 'Earnings', val: ep.earnings_score },
                  { label: 'Fundamentals', val: ep.fundamental_score },
                  { label: 'Relative Valuation', val: ep.rv_score },
                  { label: 'Risk', val: ep.risk_score },
                  { label: 'Price Momentum', val: ep.momentum_score }
                ].map(m => {
                  const score = m.val;
                  const isNR = score === null || score === undefined;
                  let barColor = '#64748B';
                  if (!isNR) {
                    if (score >= 8) barColor = '#10B981';
                    else if (score >= 4) barColor = '#F59E0B';
                    else barColor = '#EF4444';
                  }
                  const barWidth = isNR ? 0 : (score * 10);
                  return `
                    <div style="display:flex; align-items:center; font-size:11.5px;">
                      <span style="width:115px; font-weight:700; color:#334155; flex-shrink:0;">${m.label}</span>
                      <div style="flex:1; background:#E2E8F0; height:8px; border-radius:4px; overflow:hidden; margin:0 10px; position:relative;">
                        <div style="width:${barWidth}%; background:${barColor}; height:100%; border-radius:4px;"></div>
                      </div>
                      <span style="width:26px; text-align:right; font-weight:800; color:${barColor}; font-family:'JetBrains Mono', monospace;">
                        ${isNR ? 'NR' : score}
                      </span>
                    </div>
                  `;
                }).join('')}

                <!-- Meter Legend -->
                <div style="display:flex; justify-content:flex-end; gap:12px; font-size:9.5px; font-weight:700; color:#64748B; margin-top:4px; border-top:1px solid #E2E8F0; padding-top:6px;">
                  <span><span style="color:#64748B;">●</span> No Rating</span>
                  <span><span style="color:#EF4444;">●</span> Negative (1-3)</span>
                  <span><span style="color:#F59E0B;">●</span> Neutral (4-7)</span>
                  <span><span style="color:#10B981;">●</span> Positive (8-10)</span>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- 12-MONTH TARGET PRICE PROJECTIONS HIGHLIGHTS (IMAGE 2) -->
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:16px 20px; margin-bottom:20px; display:grid; grid-template-columns:1.5fr 1fr; gap:20px; align-items:center;">
          <div>
            <div style="font-size:12px; font-weight:800; color:#475569; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">
              💡 HIGHLIGHTS & CONSENSUS TRAJECTORY
            </div>
            <div style="font-size:13px; line-height:1.5; color:#1E293B; font-weight:500;">
              <strong>${stock.name}</strong> has a 12-month median price target of <strong style="color:#0F172A;">₹${f.median_target ? f.median_target.toLocaleString('en-IN') : (f.mean_target ? f.mean_target.toLocaleString('en-IN') : '-')}</strong> by <strong style="color:#0284C7;">${f.num_analysts || 0} analysts</strong>. Covering research desks have provided an institutional high estimate of <strong style="color:#059669;">₹${f.high_target ? f.high_target.toLocaleString('en-IN') : '-'}</strong> and a low conservative support of <strong style="color:#DC2626;">₹${f.low_target ? f.low_target.toLocaleString('en-IN') : '-'}</strong>.
            </div>
          </div>

          <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:12px 16px;">
            <div style="font-size:11px; font-weight:800; color:#64748B; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">
              12 MONTH TARGET PRICE RANGE
            </div>
            <div style="display:flex; flex-direction:column; gap:6px; font-size:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#475569;"><span style="color:#10B981; font-weight:900;">●</span> High:</span>
                <span style="font-weight:800; color:#059669; font-family:'JetBrains Mono', monospace;">
                  ₹${f.high_target ? f.high_target.toLocaleString('en-IN') : '-'} <span style="font-size:11px;">(↑ ${f.upside_high_pct ? (f.upside_high_pct > 0 ? '+' : '') + f.upside_high_pct + '%' : '0%'})</span>
                </span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#475569;"><span style="color:#64748B; font-weight:900;">●</span> Median:</span>
                <span style="font-weight:800; color:#0F172A; font-family:'JetBrains Mono', monospace;">
                  ₹${f.median_target ? f.median_target.toLocaleString('en-IN') : '-'}
                </span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#475569;"><span style="color:#EF4444; font-weight:900;">●</span> Low:</span>
                <span style="font-weight:800; color:#DC2626; font-family:'JetBrains Mono', monospace;">
                  ₹${f.low_target ? f.low_target.toLocaleString('en-IN') : '-'} <span style="font-size:11px;">(↓ ${f.downside_low_pct ? f.downside_low_pct + '%' : '0%'})</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- SHARE PRICE FORECAST CHART -->
        <div style="border:1px solid #E2E8F0; border-radius:10px; padding:18px; margin-bottom:20px; background:#FFFFFF;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <span style="font-size:12px; font-weight:800; color:#1E293B; text-transform:uppercase; letter-spacing:0.5px;">
              SHARE PRICE FORECAST FAN CHART <span title="12-Month forward projection fan based on covering institutional analysts" style="cursor:help; color:#94A3B8;">ⓘ</span>
            </span>
            <span style="font-size:11px; font-weight:700; color:#059669; background:#ECFDF5; padding:2px 8px; border-radius:4px; border:1px solid #A7F3D0;">12M Projection</span>
          </div>
          
          ${generateForecastSvg(stock)}
          
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; padding-top:12px; border-top:1px dashed #CBD5E1; font-size:12px;">
            <div><span style="color:#64748B;">Low Support:</span> <strong style="color:#DC2626;">₹${f.low_target ? f.low_target.toLocaleString('en-IN') : '-'} (${f.downside_low_pct > 0 ? '+' : ''}${f.downside_low_pct || 0}%)</strong></div>
            <div><span style="color:#64748B;">Consensus Mean:</span> <strong style="color:#0F172A; font-size:13.5px;">₹${f.mean_target ? f.mean_target.toLocaleString('en-IN') : '-'} (${f.upside_mean_pct > 0 ? '+' : ''}${f.upside_mean_pct || 0}%)</strong></div>
            <div><span style="color:#64748B;">Bull High:</span> <strong style="color:#059669;">₹${f.high_target ? f.high_target.toLocaleString('en-IN') : '-'} (${f.upside_high_pct > 0 ? '+' : ''}${f.upside_high_pct || 0}%)</strong></div>
          </div>
        </div>

        <!-- INSTITUTIONAL REPORTS TABLE -->
        <div style="border-top:1px solid #E2E8F0; padding-top:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:12.5px; font-weight:800; color:#1E293B; text-transform:uppercase; letter-spacing:0.5px;">
              RECENT INSTITUTIONAL BROKER RESEARCH COVERAGE (${stock.forecast && stock.forecast.analyst_reports ? stock.forecast.analyst_reports.length : 0} DESKS)
            </span>
            <span style="font-size:11px; color:#64748B; font-weight:600;">Direct Institutional Coverage Feed</span>
          </div>
          
          <table style="width:100%; border-collapse:collapse; font-size:12px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; overflow:hidden;">
            <thead>
              <tr style="background:#F8FAFC; border-bottom:2px solid #E2E8F0; text-align:left;">
                <th style="padding:8px 14px; font-weight:800; color:#475569;">Brokerage House</th>
                <th style="padding:8px 14px; font-weight:800; color:#475569;">Recommendation</th>
                <th style="padding:8px 14px; font-weight:800; color:#475569;">Report Date</th>
                <th style="padding:8px 14px; font-weight:800; color:#475569; text-align:right;">Target Price (₹)</th>
                <th style="padding:8px 14px; font-weight:800; color:#475569; text-align:right;">Implied Upside %</th>
                <th style="padding:8px 14px; font-weight:800; color:#475569;">Core Investment Catalyst</th>
              </tr>
            </thead>
            <tbody>
              ${analystRows}
            </tbody>
          </table>
        </div>

      </div>
    `;"""

    html = html[:tf_start_pos] + upgraded_tab_forecast + html[tf_end_pos:]
    print("✓ Successfully replaced ONLY tab-forecast while preserving Tab 2 (Financial Growth Matrix) variables!")

    # Write to target HTML file
    target_path = "Stock_Growth_and_Selection_Analyzer.html"
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"==================================================================")
    print(f"✓ Successfully wrote {target_path} ({len(html)/(1024*1024):.2f} MB)")
    print("==================================================================")
    return True

if __name__ == "__main__":
    update_html_clean()
