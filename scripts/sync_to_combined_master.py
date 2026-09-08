import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('market_technicals_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

for path in ['scripts/combined_master_stocks.json', 'scripts/combined_119_stocks.json']:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        stocks = json.load(f)
    
    updated = 0
    for s in stocks:
        sym = s['symbol']
        c_item = cache.get(sym)
        if not c_item:
            continue
        updated += 1
        cmp = c_item['cmp']
        prev_close = c_item['prev_close']
        day_high = c_item['day_high']
        day_low = c_item['day_low']
        volume = c_item['volume']
        high_52w = c_item['high_52w']
        low_52w = c_item['low_52w']
        
        s['today_price'] = cmp
        s['high_52w'] = high_52w
        s['low_52w'] = low_52w
        s['volume'] = volume
        
        if 'technicals' not in s or not isinstance(s['technicals'], dict):
            s['technicals'] = {}
        t = s['technicals']
        t['curr_price'] = cmp
        t['ema20'] = c_item['ema20']
        t['ema50'] = c_item['ema50']
        t['sma200'] = c_item['sma200']
        t['rsi'] = c_item['rsi']
        t['high_52w'] = high_52w
        t['low_52w'] = low_52w
        t['dist_52w_high'] = round(((cmp - high_52w) / high_52w) * 100, 2)
        t['dist_200_sma'] = round(((cmp - c_item['sma200']) / c_item['sma200']) * 100, 2)
        t['support_lvl'] = c_item['pivots']['s1']
        t['resist_lvl'] = c_item['pivots']['r1']
        
        if 'live_movement' not in s or not isinstance(s['live_movement'], dict):
            s['live_movement'] = {}
        lm = s['live_movement']
        lm['curr_price'] = cmp
        lm['prev_close'] = prev_close
        lm['day_change'] = round(cmp - prev_close, 2)
        lm['day_change_pct'] = round(((cmp - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0
        lm['day_high'] = day_high
        lm['day_low'] = day_low
        lm['volume'] = volume
        
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stocks, f, indent=2, ensure_ascii=False)
    print(f'Updated {updated} stocks in {path}')

