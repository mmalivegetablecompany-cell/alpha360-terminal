import sys, re, json

sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    content = f.read()

checks = {
    'live-stream-bar': 'class="live-stream-bar"' in content,
    'today_gainers pill': 'today_gainers' in content,
    'Live CMP th': 'Live CMP (₹)' in content,
    'Daily Move th': 'Daily Move (1D)' in content,
    'Weekly Move th': 'Weekly Move (1W)' in content,
    'modalLiveCard': 'id="modalLiveCard"' in content,
    'triggerManualLiveRefresh': 'function triggerManualLiveRefresh' in content,
    'simulateLiveMicroTicks': 'function simulateLiveMicroTicks' in content,
    'toggleAutoRefresh': 'function toggleAutoRefresh' in content,
    'exportFilteredCSV': 'function exportFilteredCSV' in content,
    'Live CMP in export': 'Live CMP (INR)' in content
}

all_ok = True
for name, res in checks.items():
    status = "OK" if res else "FAIL"
    if not res:
        all_ok = False
    print(f'[{status}] {name}')

# Check rawData count
match = re.search(r'const rawData = (\[.*?\]);', content)
if match:
    data = json.loads(match.group(1))
    print(f'Total rawData stocks: {len(data)}')
    print('Sample stock 0 (GENUSPOWER) live_movement:', json.dumps(data[0].get('live_movement'), indent=2))
else:
    all_ok = False
    print('Could not parse rawData JSON!')

if all_ok:
    print("\n🎉 ALL HTML VERIFICATIONS PASSED 100%!")
else:
    print("\n❌ SOME VERIFICATIONS FAILED")
