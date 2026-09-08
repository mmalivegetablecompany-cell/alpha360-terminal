import json
import yfinance as yf
import time

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
    'SAATVIK': 'SAATVIKGL.NS',
    'KNRCON': 'KNRCON.BO',
    'TURTLEMINT': 'TURTLEMINT.BO',
    'SHANTI': 'SHANTI.NS'
}

sym_to_ticker = {}
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
    sym_to_ticker[sym] = t

all_tickers = sorted(list(set(sym_to_ticker.values())))
print(f"Total tickers: {len(all_tickers)}")

# Test 1 batch of 30
batch = all_tickers[:30]
t0 = time.time()
data = yf.download(batch, period="1y", group_by="ticker", progress=False)
t1 = time.time()
print(f"Downloaded batch of {len(batch)} in {t1-t0:.2f}s")
valid_count = sum(1 for t in batch if t in data and len(data[t].dropna()) > 0)
print(f"Valid tickers with bars: {valid_count}/{len(batch)}")
