import json
import sys
import yfinance as yf

sys.stdout.reconfigure(encoding="utf-8")

with open("html_424_stocks.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

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
    'GVT&D': 'GVT&D.NS',
    'EMVEE': 'EMMVEE.NS',
    'ATHER': 'ATHERENERG.NS',
    'TRANSRAIL': 'TRANSRAILL.NS',
    'NSDL': 'NSDL.BO',
    'MBENGG': 'MBEL.NS',
    'VIKRAM': 'VIKRAMSOLR.NS',
    'SAATVIK': 'SAATVIKGL.NS'
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

unique_tickers = sorted(list(set(stock_to_ticker.values())))
print(f"Testing {len(unique_tickers)} tickers in batches of 50...")

data = yf.download(unique_tickers, period="5d", group_by="ticker", progress=False)

failed_tickers = []
for t in unique_tickers:
    if t not in data or data[t].dropna().empty:
        failed_tickers.append(t)

print(f"\nResults: {len(unique_tickers) - len(failed_tickers)} / {len(unique_tickers)} succeeded!")
if failed_tickers:
    print(f"Failed tickers ({len(failed_tickers)}):", failed_tickers)
    for (sym, name), t in stock_to_ticker.items():
        if t in failed_tickers:
            print(f"  • {sym:12} ({name}): ticker={t}")
else:
    print("🎉 ALL TICKERS DOWNLOADED SUCCESSFULLY!")
