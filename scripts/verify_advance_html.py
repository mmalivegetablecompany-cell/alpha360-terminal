import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('Advance_Technical_Analysis_424_Stocks.html', 'r', encoding='utf-8') as f:
    html = f.read()

m_sync = re.search(r'id="lastSyncedText">\s*([^<\n]+)', html)
print('Last Synced Text:', m_sync.group(1).strip() if m_sync else 'Not found')

# Check occurrences of 07-Sep-2026
c_07 = html.count('07-Sep-2026')
print('Occurrences of 07-Sep-2026 in Advance Technical HTML:', c_07)

# Check STOCKS_DATA
m_data = re.search(r'const STOCKS_DATA = (\[.*?\]);', html)
if m_data:
    stocks = json.loads(m_data.group(1))
    print('Total stocks in STOCKS_DATA:', len(stocks))
    for sym in ['EMVEE', 'DIXON', 'RELIANCE', 'NATIONALUM']:
        s = next((x for x in stocks if x['symbol'] == sym), None)
        if s:
            print(f"  {sym}: CMP={s['cmp']}, 1D={s['day_change_pct']}%, Action={s['action']}, TechScore={s['tech_score']}, RSI={s['oscillators']['rsi']}")
else:
    print('STOCKS_DATA not found')
