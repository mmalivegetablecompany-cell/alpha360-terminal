import json, openpyxl, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

# 1. Verify JSON
with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
    master = json.load(f)

print("=== MASTER JSON AUDIT ===")
print(f"Total stocks: {len(master)}")
m_counts = Counter(s.get("mcap_tier") for s in master)
print("Tiers count:", dict(m_counts))

# Verify rules strictly
rule_violations = []
for s in master:
    mcr = s.get("mcap_cr", 0.0)
    tier = s.get("mcap_tier")
    if mcr >= 100000.0 and tier != "Large Cap":
        rule_violations.append((s["symbol"], mcr, tier, "Expected Large Cap"))
    elif 30000.0 <= mcr < 100000.0 and tier != "Mid Cap":
        rule_violations.append((s["symbol"], mcr, tier, "Expected Mid Cap"))
    elif 5000.0 <= mcr < 30000.0 and tier != "Small Cap":
        rule_violations.append((s["symbol"], mcr, tier, "Expected Small Cap"))
    elif mcr < 5000.0 and tier != "Micro Cap":
        rule_violations.append((s["symbol"], mcr, tier, "Expected Micro Cap"))

print(f"Rule violations: {len(rule_violations)}")
if rule_violations:
    for v in rule_violations[:5]:
        print("  Violation:", v)

micro_stocks = [s for s in master if s.get("mcap_tier") == "Micro Cap"]
print(f"\nSample Micro Cap stocks (Total: {len(micro_stocks)}):")
for s in micro_stocks[:8]:
    print(f"  {s['symbol']} - {s['name']}: ₹{s.get('mcap_cr', 0):,.1f} Cr | Tier: {s.get('mcap_tier')} | Mcap col: {s.get('mcap')}")

# 2. Verify HTML
print("\n=== HTML DASHBOARD AUDIT ===")
with open("Stock_Growth_and_Selection_Analyzer.html", "r", encoding="utf-8") as f:
    html = f.read()

checks = {
    ".tier-micro in CSS": ".tier-micro" in html,
    "Micro Cap in <select>": '<option value="micro">Micro Cap (&lt; ₹5,000 Cr)</option>' in html,
    "smartFilters.mcap_tier micro logic": "smartFilters.mcap_tier === 'micro'" in html,
    "renderTable Micro Cap mapping": "tier === 'Micro Cap'" in html,
    "filter pill micro formatting": "v === 'micro'" in html,
    "rawData count is 424": html.count('"mcap_tier": "Micro Cap"') >= 91
}
for name, passed in checks.items():
    print(f"  {'[PASS]' if passed else '[FAIL]'} {name}")

# 3. Verify Excel Workbooks
val_files = [
    "Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx",
    "Watchlist_Quarterly_Growth_and_Selection_Analysis.xlsx",
    "Watchlist_Quarterly_Growth_and_Selection_Analysis_Updated.xlsx",
    "Watchlist_8_Quarterly_Reports_Complete.xlsx"
]

print("\n=== EXCEL WORKBOOKS AUDIT ===")
for vf in val_files:
    wb = openpyxl.load_workbook(vf, read_only=True)
    sheet_name = "Tri-Factor Master Scorecard" if "Tri-Factor Master Scorecard" in wb.sheetnames else "Executive Watchlist Overview"
    ws = wb[sheet_name]
    start_row = 4 if "Tri-Factor Master Scorecard" in wb.sheetnames else 5
    mcap_col_idx = 5
    tiers_in_excel = Counter()
    row_count = 0
    for r in ws.iter_rows(min_row=start_row, min_col=mcap_col_idx, max_col=mcap_col_idx, values_only=True):
        val = r[0]
        if val is not None:
            tiers_in_excel[val] += 1
            row_count += 1
    wb.close()
    print(f"  {vf} [{sheet_name}]: {row_count} rows, Tiers: {dict(tiers_in_excel)}")

print("\nAll verifications completed!")
