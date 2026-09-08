import json
with open('Advance_Technical_Analysis_424_Stocks.html', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = 'const STOCKS_DATA = '
start_idx = text.find(start_marker)
if start_idx != -1:
    end_idx = text.find(';', start_idx)
    json_str = text[start_idx + len(start_marker):end_idx]
    data = json.loads(json_str)
    print(f'Parsed {len(data)} stocks from embedded STOCKS_DATA in HTML!')
    for s in data:
        if s['symbol'] == 'TRANSRAIL':
            print('TRANSRAIL in HTML:')
            print('  CMP:', s['cmp'])
            print('  52W:', s['low_52w'], '-', s['high_52w'])
            print('  EMA20:', s['moving_averages']['ema20'])
            print('  EMA50:', s['moving_averages']['ema50'])
            print('  SMA200:', s['moving_averages']['sma200'])
            print('  BB Mid:', s['volatility']['bb_mid'], 'Upper:', s['volatility']['bb_upper'], '%B:', s['volatility']['bb_pct_b'])
            print('  Pivots S1/R1:', s['pivots']['s1'], '/', s['pivots']['r1'])
            print('  Timeframe 1D:', s['timeframes']['1D'])
            print('  Candles:', len(s['candles']), 'last:', s['candles'][-1])
            break
