import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("html_424_stocks.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

unlisted = {'ATHER', 'TRANSRAIL', 'NSDL', 'MBENGG', 'VIKRAM', 'SAATVIK', 'EMVEE'}

print("=== CHECKING THE 7 PREVIOUSLY MARKED 'UNLISTED' STOCKS ===")
for s in stocks:
    sym = s["symbol"]
    if sym in unlisted:
        print(f"Symbol: {sym:12} | Name: {s.get('name', ''):35} | CMP: {s.get('today_price')}")

print("\n=== CHECKING IF ANY OTHER STOCKS HAVE ISSUES OR DUMMY DATA ===")
ticker_overrides = {
    'PENNARIND': 'PENIND.NS',
    'DOLPHINOFF': 'DOLPHIN.NS',
    'AUTHUM': '539177.BO',
    'WAAREE': 'WAAREEENER.NS',
    'KPENERGY': 'KPEL.NS',
    'HBLPOWER': 'HBLENGINE.NS',
    'VINCOFE': 'VINCOFE.NS',
    'VINTAGE': 'VINCOFE.NS',
    'ETERNAL': 'ETERNAL.BO',
    '530249': '530249.BO',
    '532850': 'MICEL.NS',
    'SPICEJET': 'SPICEJET.BO',
    'BRIDGESE': 'BRIDGESE.BO',
    'M&M': 'M&M.NS',
    'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
    'GVT&D': 'GVT&D.NS'
}

stock_to_ticker = {}
for s in stocks:
    sym = s['symbol']
    name = s.get('name', '')
    if 'Tata Motors' in name:
        t = 'TMCV.NS' if 'Commercial' in name else 'TMPV.NS'
    elif sym in ticker_overrides:
        t = ticker_overrides[sym]
    elif sym.isdigit():
        t = f"{sym}.BO"
    else:
        t = f"{sym}.NS"
    stock_to_ticker[(sym, name)] = t

print(f"Total mapped tickers: {len(stock_to_ticker)}")
