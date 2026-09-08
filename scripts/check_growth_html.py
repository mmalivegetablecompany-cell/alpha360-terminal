import json, sys
sys.stdout.reconfigure(encoding='utf-8')
text = open('Stock_Growth_and_Selection_Analyzer.html', encoding='utf-8').read()
start_marker = 'const rawData = '
idx = text.find(start_marker)
if idx != -1:
    end_idx = text.find(';\n', idx)
    stocks = json.loads(text[idx + len(start_marker):end_idx])
    print(f'Total stocks in Stock_Growth HTML: {len(stocks)}')
    for s in stocks:
        if s['symbol'] == 'TRANSRAIL':
            print('TRANSRAIL in Stock_Growth HTML:')
            print('  today_price:', s.get('today_price'))
            print('  technicals:', s.get('technicals'))
            print('  live_movement:', s.get('live_movement'))
            break
