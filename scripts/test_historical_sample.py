import json
import yfinance as yf

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
        t = f'{sym}.BO'
    else:
        t = f'{sym}.NS'
    sym_to_ticker[sym] = t

test_syms = ['TRANSRAIL', 'WAAREE', 'KPENERGY', 'AUTHUM', 'NSDL', 'M&M', 'TATAELXSI']
test_tickers = [sym_to_ticker[s] for s in test_syms]
print('Testing test tickers:', test_tickers)
df = yf.download(test_tickers, period='1y', group_by='ticker', progress=False)

for sym in test_syms:
    t = sym_to_ticker[sym]
    if t in df:
        sub = df[t].dropna()
        if len(sub) > 0:
            lc = sub['Close'].iloc[-1]
            h52 = sub['High'].max()
            l52 = sub['Low'].min()
            ema20 = sub['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ema50 = sub['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            sma200 = sub['Close'].rolling(window=min(200, len(sub))).mean().iloc[-1]
            print(f'{sym} ({t}): bars={len(sub)}, Close={lc:.2f}, EMA20={ema20:.2f}, EMA50={ema50:.2f}, SMA200={sma200:.2f}, 52W=({l52:.2f} - {h52:.2f})')
        else:
            print(f'{sym} ({t}): NO DATA')
