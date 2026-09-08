import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/consistent_8q_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# Sort by different criteria
print(f"Loaded {len(stocks)} stocks.")

# Let's see:
# Tier 1: Hyper-Growth (Min Rev >= 20% and Min PAT >= 20%)
t1 = [s for s in stocks if s['min_rev'] >= 20.0 and s['min_pat'] >= 20.0]
print(f"\n--- Tier 1: Hyper-Growth (Min Rev >= 20% & Min PAT >= 20% in all 8Q): {len(t1)} stocks ---")
for s in sorted(t1, key=lambda x: x['min_rev'], reverse=True):
    print(f"{s['symbol']:<10} {s['name'][:24]:<25} Rev Floor: +{s['min_rev']}% (Avg {s['avg_rev']}%) | PAT Floor: +{s['min_pat']}% (Avg {s['avg_pat']}%) | P/E: {s['today_pe']} | Score: {s['master_score']}")

# Tier 2: Double-Digit High Consistency (Min Rev >= 15% and Min PAT >= 15%)
t2 = [s for s in stocks if s['min_rev'] >= 15.0 and s['min_pat'] >= 15.0 and s not in t1]
print(f"\n--- Tier 2: Strong Double-Digit (Min Rev >= 15% & Min PAT >= 15% in all 8Q): {len(t2)} stocks ---")
for s in sorted(t2, key=lambda x: x['min_rev'], reverse=True):
    print(f"{s['symbol']:<10} {s['name'][:24]:<25} Rev Floor: +{s['min_rev']}% (Avg {s['avg_rev']}%) | PAT Floor: +{s['min_pat']}% (Avg {s['avg_pat']}%) | P/E: {s['today_pe']} | Score: {s['master_score']}")

# Tier 3: Solid Double-Digit (Min Rev >= 10% and Min PAT >= 10%)
t3 = [s for s in stocks if s['min_rev'] >= 10.0 and s['min_pat'] >= 10.0 and s not in t1 and s not in t2]
print(f"\n--- Tier 3: Solid Double-Digit (Min Rev >= 10% & Min PAT >= 10% in all 8Q): {len(t3)} stocks ---")
for s in sorted(t3, key=lambda x: x['min_rev'], reverse=True):
    print(f"{s['symbol']:<10} {s['name'][:24]:<25} Rev Floor: +{s['min_rev']}% (Avg {s['avg_rev']}%) | PAT Floor: +{s['min_pat']}% (Avg {s['avg_pat']}%) | P/E: {s['today_pe']} | Score: {s['master_score']}")

# Tier 4: The remaining 8/8 stocks (Positive every single quarter, high average growth)
t4 = [s for s in stocks if s not in t1 and s not in t2 and s not in t3]
print(f"\n--- Tier 4: Consistent Compounders (8/8 Positive Qtrs, high avg growth): {len(t4)} stocks ---")
for s in sorted(t4, key=lambda x: (x['avg_pat'] + x['avg_rev']), reverse=True)[:15]:
    print(f"{s['symbol']:<10} {s['name'][:24]:<25} Rev Floor: +{s['min_rev']}% (Avg {s['avg_rev']}%) | PAT Floor: +{s['min_pat']}% (Avg {s['avg_pat']}%) | P/E: {s['today_pe']} | Score: {s['master_score']}")

