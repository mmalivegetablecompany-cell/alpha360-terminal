import json
import os

with open('html_424_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

with open('market_technicals_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

updated_count = 0
for s in stocks:
    sym = s['symbol']
    name = s.get('name', '')
    
    # Handle Tata Motors
    cache_item = cache.get(sym)
    if not cache_item:
        continue
        
    updated_count += 1
    cmp = cache_item['cmp']
    prev_close = cache_item['prev_close']
    day_high = cache_item['day_high']
    day_low = cache_item['day_low']
    volume = cache_item['volume']
    high_52w = cache_item['high_52w']
    low_52w = cache_item['low_52w']
    
    s['today_price'] = cmp
    s['high_52w'] = high_52w
    s['low_52w'] = low_52w
    s['volume'] = volume
    
    if 'technicals' not in s or not isinstance(s['technicals'], dict):
        s['technicals'] = {}
        
    s['technicals']['ema20'] = cache_item['ema20']
    s['technicals']['ema50'] = cache_item['ema50']
    s['technicals']['sma200'] = cache_item['sma200']
    s['technicals']['rsi'] = cache_item['rsi']
    s['technicals']['high_52w'] = high_52w
    s['technicals']['low_52w'] = low_52w
    
    if 'live_movement' not in s or not isinstance(s['live_movement'], dict):
        s['live_movement'] = {}
        
    s['live_movement']['curr_price'] = cmp
    s['live_movement']['prev_close'] = prev_close
    day_chg = round(cmp - prev_close, 2)
    day_chg_pct = round((day_chg / prev_close) * 100, 2) if prev_close > 0 else 0.0
    s['live_movement']['day_change'] = day_chg
    s['live_movement']['day_change_pct'] = day_chg_pct
    s['live_movement']['day_high'] = day_high
    s['live_movement']['day_low'] = day_low
    s['live_movement']['volume'] = volume

with open('html_424_stocks.json', 'w', encoding='utf-8') as f:
    json.dump(stocks, f, indent=2, ensure_ascii=False)

print(f'Successfully updated {updated_count} stocks in html_424_stocks.json!')
