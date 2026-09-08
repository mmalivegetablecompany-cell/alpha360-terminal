import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Fix exportFilteredCSV row mapping so it matches the headers:
old_csv_map = """        s.master_rank,
        `"${s.symbol}"`,
        `"${s.name}"`,
        `"${s.sector}"`,
        `"${s.mcap}"`,`"""

new_csv_map = """        s.master_rank,
        `"${s.symbol}"`,
        `"${s.name}"`,
        `"${s.sector}"`,
        `"${s.mcap_tier || s.mcap}"`,
        s.mcap_cr || '',"""

if old_csv_map in html:
    html = html.replace(old_csv_map, new_csv_map, 1)
    print("Fixed CSV row mapping for Market Cap Tier and Market Cap (INR Cr).")

BUCKET_AND_EXCEL_ENGINE = """
  /* ==========================================================================
     CUSTOM STOCK BUCKET / PORTFOLIO BASKET ENGINE
     ========================================================================== */
  let bucketSet = new Set();
  try {
    const savedBucket = localStorage.getItem('user_stock_bucket');
    if (savedBucket) {
      const parsed = JSON.parse(savedBucket);
      if (Array.isArray(parsed)) {
        bucketSet = new Set(parsed);
      }
    }
  } catch (e) {
    console.error('Error loading stock bucket:', e);
  }

  function saveBucket() {
    try {
      localStorage.setItem('user_stock_bucket', JSON.stringify(Array.from(bucketSet)));
    } catch (e) {
      console.error('Error saving stock bucket:', e);
    }
    updateBucketUI();
  }

  function toggleStockBucket(sym, forceState) {
    if (forceState !== undefined) {
      if (forceState) bucketSet.add(sym);
      else bucketSet.delete(sym);
    } else {
      if (bucketSet.has(sym)) bucketSet.delete(sym);
      else bucketSet.add(sym);
    }
    saveBucket();

    if (currentPill === 'bucket') {
      applyAllFilters();
    } else {
      updateRowBucketState(sym);
    }
  }

  function updateRowBucketState(sym) {
    const cb = document.getElementById(`bucket-cb-${sym}`);
    if (cb) cb.checked = bucketSet.has(sym);

    const cells = document.querySelectorAll(`[id="price-cell-${sym}"]`);
    cells.forEach(c => {
      const tr = c.closest('tr');
      if (tr) tr.classList.toggle('row-in-bucket', bucketSet.has(sym));
    });
  }

  function addAllFilteredToBucket() {
    if (!currentData || currentData.length === 0) return;
    currentData.forEach(s => bucketSet.add(s.symbol));
    saveBucket();
    if (currentPill === 'bucket') {
      applyAllFilters();
    } else {
      renderTable(currentData);
    }
  }

  function removeAllFilteredFromBucket() {
    if (!currentData || currentData.length === 0) return;
    currentData.forEach(s => bucketSet.delete(s.symbol));
    saveBucket();
    if (currentPill === 'bucket') {
      applyAllFilters();
    } else {
      renderTable(currentData);
    }
  }

  function clearBucketWithConfirm() {
    if (bucketSet.size === 0) {
      alert("Your Bucket is already empty.");
      return;
    }
    if (confirm(`Clear all ${bucketSet.size} stocks from your custom bucket?`)) {
      bucketSet.clear();
      saveBucket();
      if (currentPill === 'bucket') {
        applyAllFilters();
      } else {
        renderTable(currentData);
      }
      renderBucketModalContent();
    }
  }

  function toggleSelectAllVisibleBucket(checked) {
    if (!currentData || currentData.length === 0) return;
    currentData.forEach(s => {
      if (checked) bucketSet.add(s.symbol);
      else bucketSet.delete(s.symbol);
    });
    saveBucket();
    if (currentPill === 'bucket') {
      applyAllFilters();
    } else {
      renderTable(currentData);
    }
  }

  function toggleModalStockBucket() {
    const stock = currentData[activeStockIndex];
    if (!stock) return;
    toggleStockBucket(stock.symbol);
    updateModalBucketButton(stock.symbol);
  }

  function updateModalBucketButton(sym) {
    const btn = document.getElementById('btnModalBucket');
    const icon = document.getElementById('modalBucketIcon');
    const txt = document.getElementById('modalBucketText');
    if (!btn || !txt) return;
    const inB = bucketSet.has(sym);
    btn.classList.toggle('in-bucket', inB);
    txt.innerText = inB ? 'In Bucket ✓' : '+ Add to Bucket';
    if (icon) icon.innerText = inB ? '🧺' : '➕';
  }

  function updateBucketUI() {
    const count = bucketSet.size;

    const elH = document.getElementById('headerBucketCount');
    if (elH) elH.innerText = count;
    const elP = document.getElementById('bucketPillCount');
    if (elP) elP.innerText = count;
    const elB = document.getElementById('barBucketCount');
    if (elB) elB.innerText = count;
    const elV = document.getElementById('bmViewCount');
    if (elV) elV.innerText = count;

    const selectAllCb = document.getElementById('selectAllBucketCheckbox');
    if (selectAllCb) {
      const allVisibleSelected = currentData.length > 0 && currentData.every(s => bucketSet.has(s.symbol));
      selectAllCb.checked = allVisibleSelected;
    }
  }

  function openBucketModal() {
    renderBucketModalContent();
    const m = document.getElementById('bucketModal');
    if (m) m.style.display = 'flex';
  }

  function closeBucketModal() {
    const m = document.getElementById('bucketModal');
    if (m) m.style.display = 'none';
  }

  function viewBucketInMainTable() {
    closeBucketModal();
    const pillBtn = document.getElementById('pillBucket');
    setFilterPill('bucket', pillBtn);
  }

  function renderBucketModalContent() {
    const bucketStocks = rawData.filter(s => bucketSet.has(s.symbol));
    const count = bucketStocks.length;

    let totalMcap = 0;
    let sumScore = 0;
    let peSum = 0, peCount = 0;
    let upsideSum = 0, upsideCount = 0;
    let moveSum = 0;
    const sectorCounts = {};

    bucketStocks.forEach(s => {
      totalMcap += (s.mcap_cr || 0);
      sumScore += (s.master_score || 0);
      if (typeof s.today_pe === 'number' && s.today_pe > 0) {
        peSum += s.today_pe;
        peCount++;
      }
      const up = (s.forecast && s.forecast.upside_mean_pct !== undefined) ? s.forecast.upside_mean_pct : 0;
      upsideSum += up;
      upsideCount++;

      const lm = s.live_movement || {};
      const dayChg = s.day_change_pct !== undefined ? s.day_change_pct : (lm.day_change_pct || 0);
      moveSum += dayChg;

      sectorCounts[s.sector] = (sectorCounts[s.sector] || 0) + 1;
    });

    const avgScore = count > 0 ? (sumScore / count).toFixed(1) : '0.0';
    const avgPE = peCount > 0 ? (peSum / peCount).toFixed(1) : '-';
    const avgUpside = upsideCount > 0 ? (upsideSum / upsideCount).toFixed(1) : '0.0';
    const avgMove = count > 0 ? (moveSum / count).toFixed(2) : '0.00';
    const mcapFmt = totalMcap >= 100000 
      ? `₹${(totalMcap / 100000).toFixed(2)} L Cr`
      : `₹${Math.round(totalMcap).toLocaleString('en-IN')} Cr`;

    document.getElementById('bstat-stocks').innerText = `${count} / ${rawData.length}`;
    document.getElementById('bstat-mcap').innerText = count > 0 ? mcapFmt : '₹0 Cr';
    document.getElementById('bstat-score').innerText = avgScore;
    document.getElementById('bstat-pe').innerText = avgPE !== '-' ? `${avgPE}x` : '-';
    document.getElementById('bstat-upside').innerText = `${avgUpside > 0 ? '+' : ''}${avgUpside}%`;

    const moveEl = document.getElementById('bstat-daymove');
    if (moveEl) {
      moveEl.innerText = `${avgMove > 0 ? '+' : ''}${avgMove}%`;
      moveEl.style.color = avgMove > 0 ? 'var(--accent-green)' : (avgMove < 0 ? 'var(--accent-red)' : 'var(--text-primary)');
    }

    const secContainer = document.getElementById('bstat-sectors');
    if (secContainer) {
      secContainer.innerHTML = '';
      if (count === 0) {
        secContainer.innerHTML = '<span style="font-size:11px; color:var(--text-muted);">No sectors yet</span>';
      } else {
        Object.entries(sectorCounts).sort((a, b) => b[1] - a[1]).forEach(([sec, cnt]) => {
          const chip = document.createElement('span');
          chip.className = 'b-sec-chip';
          chip.innerText = `${sec}: ${cnt}`;
          secContainer.appendChild(chip);
        });
      }
    }

    const tbody = document.getElementById('bucketTableBody');
    const emptyState = document.getElementById('bucketEmptyState');
    const tableSummary = document.getElementById('bucketTableSummary');
    if (tableSummary) tableSummary.innerText = `${count} stocks in bucket`;

    if (tbody) {
      tbody.innerHTML = '';
      if (count === 0) {
        if (emptyState) emptyState.style.display = 'block';
      } else {
        if (emptyState) emptyState.style.display = 'none';
        bucketStocks.sort((a, b) => a.master_rank - b.master_rank).forEach(s => {
          const tr = document.createElement('tr');
          const f = s.forecast || {};
          const lm = s.live_movement || {};
          const dayChg = s.day_change_pct !== undefined ? s.day_change_pct : (lm.day_change_pct || 0);
          const up = f.upside_mean_pct !== undefined ? f.upside_mean_pct : 0;

          tr.innerHTML = `
            <td style="font-weight:800; text-align:center;">#${s.master_rank}</td>
            <td><strong style="color:var(--accent-blue); font-size:13px;">${s.symbol}</strong></td>
            <td><strong>${s.name}</strong></td>
            <td style="font-size:11.5px; color:var(--text-secondary);">${s.sector}</td>
            <td style="text-align:right; font-family:'JetBrains Mono', monospace; font-weight:700;">₹${Math.round(s.mcap_cr || 0).toLocaleString('en-IN')} Cr</td>
            <td style="text-align:right; font-weight:800; font-family:'JetBrains Mono', monospace;">₹${(s.today_price || 0).toLocaleString('en-IN', {minimumFractionDigits:1})}</td>
            <td style="text-align:right; color:${dayChg > 0 ? 'var(--accent-green)' : (dayChg < 0 ? 'var(--accent-red)' : 'inherit')}; font-weight:700;">
              ${dayChg > 0 ? '▲ +' : (dayChg < 0 ? '▼ ' : '• ')}${typeof dayChg === 'number' ? dayChg.toFixed(2) : dayChg}%
            </td>
            <td style="text-align:right; color:var(--accent-blue); font-weight:700;">${s.today_pe || '-'}</td>
            <td style="text-align:right; font-weight:700;">₹${f.mean_target ? f.mean_target.toLocaleString('en-IN') : '-'}</td>
            <td style="text-align:right; color:${up > 0 ? 'var(--accent-green)' : (up < 0 ? 'var(--accent-red)' : 'inherit')}; font-weight:800;">
              ${up > 0 ? '+' : ''}${up}%
            </td>
            <td style="text-align:center; font-weight:900; color:var(--accent-gold);">${s.master_score}</td>
            <td style="text-align:center;">
              <button class="bucket-btn-remove" onclick="toggleStockBucket('${s.symbol}', false); renderBucketModalContent();" title="Remove from Bucket">✕</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }
    }
  }

  /* ==========================================================================
     EXCEL (.XLSX) AND CSV EXPORT ENGINE
     ========================================================================== */
  function generateStockExportRows(stockList) {
    return stockList.map((s, idx) => {
      const f = s.forecast || {};
      const t = s.technicals || {};
      const lm = s.live_movement || {};
      return {
        "S.No": idx + 1,
        "Master Rank": s.master_rank,
        "Symbol": s.symbol,
        "Company Name": s.name,
        "Sector": s.sector,
        "Sub-Industry": s.sub_industry || "",
        "Market Cap (INR Cr)": s.mcap_cr || "",
        "Market Cap Tier": s.mcap_tier || s.mcap || "",
        "Live CMP (INR)": s.today_price || lm.curr_price || "",
        "Daily Change %": s.day_change_pct !== undefined ? s.day_change_pct : (lm.day_change_pct || 0),
        "Weekly Change %": s.week_change_pct !== undefined ? s.week_change_pct : (lm.week_change_pct || 0),
        "Today P/E": s.today_pe !== undefined && s.today_pe !== null ? s.today_pe : "",
        "Today P/B": s.today_pb !== undefined && s.today_pb !== null ? s.today_pb : "",
        "Today PEG": s.today_peg !== undefined && s.today_peg !== null ? s.today_peg : "",
        "8Q Med P/E": s.pe_8q_med || "",
        "14D RSI": t.rsi || "",
        "Trend Regime": t.trend || "",
        "52W High (INR)": t.high_52w || "",
        "1Y Mean Target (INR)": f.mean_target || "",
        "Forecast Upside %": f.upside_mean_pct !== undefined ? f.upside_mean_pct : 0,
        "Analyst Consensus": f.consensus_rating || "",
        "Covering Analysts": f.num_analysts || 0,
        "Fundamental Score (30%)": s.score,
        "Technical Score (30%)": s.tech_score,
        "Market Mood Score (20%)": s.mood_score,
        "Master Quad Score": s.master_score,
        "Confluence Tier": s.master_category || "",
        "Latest Quarter": s.latest_quarter || "",
        "Latest YoY PAT %": s.latest_yoy_pat !== undefined && s.latest_yoy_pat !== null ? s.latest_yoy_pat : "",
        "Profit Streak (Qtrs)": s.streak_pat || 0,
        "Primary Catalyst / Positives": s.pos_news || ""
      };
    });
  }

  function downloadWorkbook(rows, filename, sheetName = "Watchlist") {
    if (window.XLSX) {
      try {
        const ws = XLSX.utils.json_to_sheet(rows);
        const colWidths = Object.keys(rows[0] || {}).map(key => {
          let maxLen = key.length;
          rows.slice(0, 50).forEach(r => {
            const valStr = r[key] !== null && r[key] !== undefined ? String(r[key]) : '';
            if (valStr.length > maxLen) maxLen = valStr.length;
          });
          return { wch: Math.min(Math.max(maxLen + 3, 10), 45) };
        });
        ws['!cols'] = colWidths;
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, sheetName);
        
        if (XLSX.writeFile) {
          XLSX.writeFile(wb, `${filename}.xlsx`);
        } else {
          const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
          const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${filename}.xlsx`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }
        return;
      } catch (err) {
        console.warn('XLSX export fallback to CSV:', err);
      }
    }
    downloadRowsCSV(rows, `${filename}.csv`);
  }

  function downloadRowsCSV(rows, filename) {
    if (!rows || rows.length === 0) return;
    const headers = Object.keys(rows[0]);
    const csvLines = [headers.join(',')];
    rows.forEach(r => {
      const line = headers.map(h => {
        const v = r[h];
        if (v === null || v === undefined) return '""';
        const str = String(v).replace(/"/g, '""');
        return `"${str}"`;
      }).join(',');
      csvLines.push(line);
    });
    const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(csvLines.join('\\n'));
    const link = document.createElement("a");
    link.setAttribute("href", csvContent);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function exportFilteredExcel() {
    if (!currentData || currentData.length === 0) {
      alert("No stocks match current filter to export.");
      return;
    }
    const rows = generateStockExportRows(currentData);
    const dateStr = new Date().toISOString().slice(0, 10);
    downloadWorkbook(rows, `Indian_Equities_Filtered_Watchlist_${dateStr}`, "Stock Analysis");
  }

  function exportBucketExcel() {
    const bucketStocks = rawData.filter(s => bucketSet.has(s.symbol));
    if (bucketStocks.length === 0) {
      alert("Your Bucket is empty. Please select stocks using the 🧺 checkboxes first!");
      return;
    }
    const rows = generateStockExportRows(bucketStocks);
    const dateStr = new Date().toISOString().slice(0, 10);
    downloadWorkbook(rows, `My_Stock_Bucket_Portfolio_${dateStr}`, "Bucket Portfolio");
  }

  function exportBucketCSV() {
    const bucketStocks = rawData.filter(s => bucketSet.has(s.symbol));
    if (bucketStocks.length === 0) {
      alert("Your Bucket is empty. Please select stocks using the 🧺 checkboxes first!");
      return;
    }
    const rows = generateStockExportRows(bucketStocks);
    const dateStr = new Date().toISOString().slice(0, 10);
    downloadRowsCSV(rows, `My_Stock_Bucket_Portfolio_${dateStr}.csv`);
  }
"""

if "function toggleStockBucket(" not in html:
    # Insert right before </script> at the end of the file
    idx = html.rfind("</script>")
    if idx != -1:
        html = html[:idx] + BUCKET_AND_EXCEL_ENGINE + "\n  updateBucketUI();\n" + html[idx:]
        print("Inserted Bucket & Excel Export functions and startup initialization.")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Step 4 (JS Engine Integration) complete.")
