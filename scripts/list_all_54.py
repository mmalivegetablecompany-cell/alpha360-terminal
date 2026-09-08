import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/consistent_8q_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# Sort by Master Score descending
stocks.sort(key=lambda x: x['master_score'], reverse=True)

print(f"=== All 54 Stocks with 8/8 Quarters Positive YoY Growth Sorted by Master Score ===")
print(f"{'Rank':<4} {'Symbol':<11} {'Name':<26} {'Sector':<20} {'Mcap':<10} {'CMP':<8} {'P/E':<6} {'Score':<6} {'Rev Floor':<10} {'Avg Rev':<9} {'PAT Floor':<10} {'Avg PAT':<9}")
print("-" * 135)
for i, s in enumerate(stocks, 1):
    print(f"{i:<4} {s['symbol']:<11} {s['name'][:25]:<26} {s['sector'][:19]:<20} {s['mcap'][:9]:<10} {s['today_price']:>7.1f} {s['today_pe']:>6.1f} {s['master_score']:>6.1f} {s['min_rev']:>8.1f}% {s['avg_rev']:>7.1f}% {s['min_pat']:>8.1f}% {s['avg_pat']:>7.1f}%")
