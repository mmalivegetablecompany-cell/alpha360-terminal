import json
import sys
import time
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
    # Newly resolved listed tickers:
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
print(f"Total stocks: {len(stocks)}, unique tickers: {len(unique_tickers)}")

# Test downloading in batches
data = yf.download(unique_tickers, period="1mo", group_by="ticker", progress=False)

failed = []
success = []
for (sym, name), t in stock_to_ticker.items():
    has_data = False
    if t in data:
        df = data[t].dropna()
        if len(df) >= 1:
            has_data = True
            c = float(df['Close'].iloc[-1])
            success.append((sym, name, t, c))
    if not has_data:
        failed.append((sym, name, t))

print(f"\n✅ Succeeded: {len(success)} / {len(stocks)}")
print(f"❌ Failed: {len(failed)} / {len(stocks)}")

if failed:
    print("\nFailed stocks details:")
    for sym, name, t in failed:
        print(f"  • {sym:12} | {name:35} | Ticker: {t}")
else:
    print("\n🎉 100% OF ALL 424 STOCKS ARE FULLY VERIFIED WITH LIVE REAL MARKET DATA!")
    print("\nSample of newly verified stocks:")
    for sym in ['EMVEE', 'ATHER', 'TRANSRAIL', 'NSDL', 'MBENGG', 'VIKRAM', 'SAATVIK', 'KNRCON', 'TURTLEMINT', 'SHANTI']:
        match = [s for s in success if s[0] == sym]
        if match:
            s_sym, s_name, s_t, s_c = match[0]
            print(f"  • {s_sym:12} ({s_name[:25]}): Ticker {s_t:15} => Live CMP ₹{s_c:.2f}")
