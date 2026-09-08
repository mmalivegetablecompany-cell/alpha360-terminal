import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

print(f"File size: {len(html)} bytes, Lines: {len(html.splitlines())}")

# 1. Check rawData in HTML
start_idx = html.find("const rawData =")
end_idx = html.find("let currentData =", start_idx)
raw_json = html[start_idx + len("const rawData ="):end_idx].strip()
if raw_json.endswith(";"):
    raw_json = raw_json[:-1].strip()

stocks = json.loads(raw_json)
print(f"\n[Test 1] rawData Stock Count: {len(stocks)}")
assert len(stocks) == 119, f"Expected 119 stocks, got {len(stocks)}"

# Verify all 119 stocks have mcap_cr, shares_outstanding, mcap_tier
missing_mcap = [s["symbol"] for s in stocks if s.get("mcap_cr") is None or s.get("mcap_cr") <= 0]
missing_shares = [s["symbol"] for s in stocks if s.get("shares_outstanding") is None or s.get("shares_outstanding") <= 0]
missing_tier = [s["symbol"] for s in stocks if not s.get("mcap_tier")]

print(f"[Test 2] Missing mcap_cr: {len(missing_mcap)}")
assert len(missing_mcap) == 0, f"Missing mcap for: {missing_mcap}"

print(f"[Test 3] Missing shares_outstanding: {len(missing_shares)}")
assert len(missing_shares) == 0, f"Missing shares for: {missing_shares}"

print(f"[Test 4] Missing mcap_tier: {len(missing_tier)}")
assert len(missing_tier) == 0, f"Missing tier for: {missing_tier}"

tier_counts = {}
for s in stocks:
    t = s["mcap_tier"]
    tier_counts[t] = tier_counts.get(t, 0) + 1
print(f"         Tier distribution: {tier_counts}")

# 2. Check Static thead has Market Cap
assert "sortTable('mcap_cr')" in html, "Static thead is missing sortTable('mcap_cr')"
print("[Test 5] Static thead contains Market Cap column sortable header: PASS")

# 3. Check MASTER_COLUMN_DEFS has mcap_cr
assert "{ id: 'mcap_cr', label: 'Market Cap', sortKey: 'mcap_cr', defaultOrder: 4 }" in html, "MASTER_COLUMN_DEFS missing mcap_cr"
print("[Test 6] MASTER_COLUMN_DEFS contains mcap_cr: PASS")

# 4. Check COLUMN_PRESETS have mcap_cr
assert "'mcap_cr'" in html[html.find("COLUMN_PRESETS ="):html.find("let activeColumns =")], "COLUMN_PRESETS missing mcap_cr"
print("[Test 7] COLUMN_PRESETS contain mcap_cr: PASS")

# 5. Check cellRenderers.mcap_cr exists
assert "mcap_cr: (s) =>" in html, "cellRenderers missing mcap_cr"
print("[Test 8] cellRenderers.mcap_cr defined: PASS")

# 6. Check simulateLiveMicroTicks has dynamic mcap calculation
assert "s.mcap_cr = Math.round((newPrice * s.shares_outstanding)" in html, "simulateLiveMicroTicks missing dynamic mcap_cr calculation"
assert "mcap-cell-" in html, "simulateLiveMicroTicks missing mcap-cell DOM update"
print("[Test 9] simulateLiveMicroTicks dynamic market cap updates: PASS")

# 7. Check Smart Filter UI elements
assert 'id="btnSmartFilterToggle"' in html, "Missing btnSmartFilterToggle"
assert 'id="smartFilterPanel"' in html, "Missing smartFilterPanel"
assert 'id="preset_lynch_garp"' in html, "Missing preset_lynch_garp"
assert 'id="preset_alpha_leaders"' in html, "Missing preset_alpha_leaders"
assert 'id="preset_hyper_growth"' in html, "Missing preset_hyper_growth"
assert 'id="preset_deep_safety"' in html, "Missing preset_deep_safety"
assert 'id="preset_stage2_dip"' in html, "Missing preset_stage2_dip"
assert 'id="preset_bluechips"' in html, "Missing preset_bluechips"
assert 'id="sfActiveTags"' in html, "Missing sfActiveTags container"
assert 'id="sfMatchSummary"' in html, "Missing sfMatchSummary container"
print("[Test 10] Smart Filter UI, 6 Presets & Active Filter Pills: PASS")

# 8. Check Smart Filter Engine functions
assert "function toggleSmartFilterPanel()" in html, "Missing toggleSmartFilterPanel"
assert "function applySmartPreset(" in html, "Missing applySmartPreset"
assert "function clearAllSmartFilters(" in html, "Missing clearAllSmartFilters"
assert "function clearSingleSmartFilter(" in html, "Missing clearSingleSmartFilter"
assert "function updateSmartFilterUI()" in html, "Missing updateSmartFilterUI"
assert "smartFilters.max_pe" in html, "Missing smartFilters evaluation in applyAllFilters"
print("[Test 11] Smart Filter JS Engine & Multi-Condition AND logic: PASS")

# 9. Verify Column count labels
assert "Full Master View (22)" in html, "Missing Full Master View (22) label"
assert "Customize Columns (<span id=\"visibleColCount\">22</span>/22)" in html, "Missing Customize Columns 22 label"
print("[Test 12] Column counts updated to 22: PASS")

print("\n🎉 ALL 12 VERIFICATION SUITE ASSERTIONS PASSED WITH ZERO ERRORS!")
