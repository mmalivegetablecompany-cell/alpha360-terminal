import sys, os, json, time
import concurrent.futures
import yfinance as yf
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/combined_119_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# Verified DRHP valuations (Cr) for Pre-IPO stocks and special mappings
PRE_IPO_MCAP = {
    'ATHER (Pre-IPO)': 11900.0,
    'TRANSRAIL (Pre-IPO)': 3200.0,
    'NSDL (Pre-IPO)': 10000.0,
    'BELRISE (Pre-IPO)': 14500.0,
    'MBENGG (Pre-IPO)': 1450.0,
    'VIKRAM (Pre-IPO)': 7500.0,
    'SAATVIK (Pre-IPO)': 2800.0,
    'EMVEE (Pre-IPO)': 6200.0,
    'IKS (Pre-IPO)': 35000.0
}

TICKER_OVERRIDE = {
    'KPENERGY': '539686.BO',
    'HBLPOWER': 'HBLPOWER.NS',
    'AUTHUM': '539867.BO',
    'TATAMOTORS': 'TATAMOTORS.NS',
    'WAAREE': 'WAAREEENER.NS',
    'WAAREERTL': '534618.BO',
    'BRIDGESE': '530249.BO',
    'VINTAGE': 'VINCOFE.BO',
    'ETERNAL': 'ETERNAL.BO',
    'MICEL': '532850.BO',
    'PENNARIND': 'PENIND.NS'
}

def get_stock_mcap(s):
    sym = s['symbol']
    clean = s.get('clean_sym', sym).split()[0]
    cmp = s.get('today_price', 0)
    
    if sym in PRE_IPO_MCAP:
        mcap_cr = PRE_IPO_MCAP[sym]
        shares = round((mcap_cr * 10000000.0) / cmp) if cmp > 0 else None
        return {'symbol': sym, 'cmp': cmp, 'mcap_cr': mcap_cr, 'shares': shares, 'source': 'DRHP'}
        
    # Check YF
    tk = TICKER_OVERRIDE.get(sym, f'{clean}.NS')
    mcap_cr = None
    shares = None
    try:
        t = yf.Ticker(tk)
        info = t.info
        if info:
            raw = info.get('marketCap')
            if raw:
                mcap_cr = round(float(raw) / 10000000.0, 1)
            sh = info.get('sharesOutstanding')
            if sh:
                shares = float(sh)
            elif mcap_cr and cmp > 0:
                shares = round((mcap_cr * 10000000.0) / cmp)
    except:
        pass
        
    return {'symbol': sym, 'cmp': cmp, 'mcap_cr': mcap_cr, 'shares': shares, 'source': 'YF'}

print(f'Fetching YF market caps for {len(stocks)} stocks...')
t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    results = list(executor.map(get_stock_mcap, stocks))

print(f'Fetched in {time.time()-t0:.2f}s')

missing = [r for r in results if r['mcap_cr'] is None]
print(f'Populated: {len(results)-len(missing)} / {len(results)}')
if missing:
    print('Missing:', [m['symbol'] for m in missing])

os.makedirs('scratch', exist_ok=True)
with open('scratch/all_119_mcaps.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print('Saved scratch/all_119_mcaps.json')
