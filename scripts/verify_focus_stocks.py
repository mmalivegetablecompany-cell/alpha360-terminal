import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("Stock_Growth_and_Selection_Analyzer.html", "r", encoding="utf-8") as f:
    html1 = f.read()

m1 = re.search(r'const rawData = (\[.*?\]);', html1, re.DOTALL)
data1 = json.loads(m1.group(1))

with open("Advance_Technical_Analysis_424_Stocks.html", "r", encoding="utf-8") as f:
    html2 = f.read()

m2 = re.search(r'const STOCKS_DATA = (\[.*?\]);', html2, re.DOTALL)
data2 = json.loads(m2.group(1))

focus_syms = ['EMVEE', 'ATHER', 'TRANSRAIL', 'NSDL', 'MBENGG', 'VIKRAM', 'SAATVIK', 'KNRCON', 'TURTLEMINT', 'SHANTI']
print("=" * 85)
print("VERIFYING LIVE CURRENT REAL DATA ACROSS BOTH HTML DASHBOARDS")
print("=" * 85)

for sym in focus_syms:
    s1 = [x for x in data1 if x["symbol"] == sym][0]
    s2 = [x for x in data2 if x["symbol"] == sym][0]
    
    print(f"Symbol: {sym:12} | Name: {s1['name'][:28]:28}")
    print(f"  • Stock Growth Analyzer : CMP ₹{s1['today_price']} | 1D: {s1['day_change_pct']:+.2f}% | Vol: {s1['volume']:,} | Day Range: ₹{s1['day_low']} - ₹{s1['day_high']}")
    print(f"  • Advance Technical HTML: CMP ₹{s2['cmp']} | Action: {s2['action']:12} | Entry: ₹{s2['trade_blueprint']['entry_min']} - ₹{s2['trade_blueprint']['entry_max']} | SL: ₹{s2['trade_blueprint']['stop_loss']} | T1: ₹{s2['trade_blueprint']['target_1']}")
    print("-" * 85)
