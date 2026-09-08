import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('Stock_Growth_and_Selection_Analyzer.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f'HTML Size: {len(html)} bytes')

m = re.search(r'const rawData = (\[[\s\S]*?\]);', html)
if not m:
    print('FAIL: rawData not found!')
    sys.exit(1)

stocks = json.loads(m.group(1))
print(f'PASS: rawData contains {len(stocks)} stocks.')

has_pb = len([s for s in stocks if s.get('today_pb') is not None])
has_bv = len([s for s in stocks if s.get('book_value') is not None])
has_peg = len([s for s in stocks if s.get('today_peg') is not None])

print(f'  Stocks with Book Value: {has_bv}/{len(stocks)}')
print(f'  Stocks with Today P/B:  {has_pb}/{len(stocks)}')
print(f'  Stocks with Today PEG:  {has_peg}/{len(stocks)}')

assert "id: 'today_pb'" in html, 'today_pb missing from MASTER_COLUMN_DEFS'
assert "id: 'today_peg'" in html, 'today_peg missing from MASTER_COLUMN_DEFS'
print('PASS: MASTER_COLUMN_DEFS contains today_pb and today_peg.')

assert "'today_pb', 'today_peg'" in html, 'today_pb and today_peg missing from COLUMN_PRESETS'
print('PASS: COLUMN_PRESETS contains today_pb and today_peg.')

assert "today_pb: (s) =>" in html, 'today_pb missing from cellRenderers'
assert "today_peg: (s) =>" in html, 'today_peg missing from cellRenderers'
print('PASS: cellRenderers contains today_pb and today_peg.')

assert "key === 'today_pb'" in html, 'today_pb missing from sortTable'
assert "key === 'today_peg'" in html, 'today_peg missing from sortTable'
print('PASS: sortTable handles today_pb and today_peg.')

assert "Price to Book (P/B)" in html, 'Price to Book card missing from Valuation Modal'
assert "PEG Ratio" in html, 'PEG Ratio card missing from Valuation Modal'
print('PASS: Valuation Modal contains P/B and PEG benchmark cards.')

assert '"Today P/B", "Today PEG"' in html, 'Today P/B and Today PEG missing from exportFilteredCSV'
print('PASS: exportFilteredCSV contains Today P/B and Today PEG.')

assert "Full Master View (21)" in html, 'Toolbar count for Full Master View is not 21'
assert "Live Price & Valuation (12)" in html, 'Toolbar count for Live Price is not 12'
assert 'visibleColCount">21</span>/21' in html, 'Customize columns count is not 21/21'
print('PASS: Toolbar counts are 21 and 12.')

print('\nALL VERIFICATIONS PASSED 100% PERFECTLY!')
