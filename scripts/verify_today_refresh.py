import sys, re, json, datetime

sys.stdout.reconfigure(encoding='utf-8')

today_iso = datetime.datetime.now().strftime("%Y-%m-%d")
today_dmy = datetime.datetime.now().strftime("%d-%b-%Y")

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

m_sync = re.search(r'<div class="live-sync-time" id="liveSyncTime">.*?</div>', text)
m_breadth = re.search(r'<div class="live-breadth-chip" id="marketBreadthChip">.*?</div>', text)
print('Sync Time element:', m_sync.group(0) if m_sync else 'Not found')
print('Breadth element:', m_breadth.group(0) if m_breadth else 'Not found')

m_raw = re.search(r'const rawData = (\[.*?\]);', text)
if m_raw:
    data = json.loads(m_raw.group(1))
    print('Total stocks in HTML rawData:', len(data))
    
    updated_today = 0
    for s in data:
        lm = s.get('live_movement', {})
        if today_iso in str(lm.get('last_updated', '')):
            updated_today += 1
            
    print(f'Stocks updated with {today_iso} timestamp: {updated_today} / {len(data)}')
    
    # Check focus stocks
    focus = ['GENUSPOWER', 'DIXON', 'OBEROIRLTY', 'NATIONALUM', 'VINTAGE', 'HONASA', 'EMVEE']
    print('\nFocus stock verification:')
    for s in data:
        if s['symbol'] in focus:
            lm = s.get('live_movement', {})
            print(f"  {s['symbol']}: CMP Rs.{s.get('today_price')}, Prev: Rs.{lm.get('prev_close')}, 1D Chg: Rs.{lm.get('day_change')} ({lm.get('day_change_pct')}%), High: Rs.{lm.get('day_high')}, Low: Rs.{lm.get('day_low')}, Vol: {lm.get('volume')}")
else:
    print('rawData NOT found!')
