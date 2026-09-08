import sys, os, json, time
import concurrent.futures
import yfinance as yf
import requests
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/combined_119_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

CUSTOM_MAPPINGS = {
    'KPENERGY': {'slug': 'KPEL', 'yf': '539686.BO'},
    'HBLPOWER': {'slug': 'HBLENGINE', 'yf': 'HBLPOWER.NS'},
    'AUTHUM': {'slug': 'AIIL', 'yf': '539867.BO'},
    'TATAMOTORS': {'slug': 'TMPV', 'yf': 'TATAMOTORS.NS'},
    'WAAREE': {'slug': 'WAAREEENER', 'yf': 'WAAREEENER.NS'},
    'WAAREERTL': {'slug': 'WAAREERTL', 'yf': '534618.BO'},
    'BRIDGESE': {'slug': '530249', 'yf': '530249.BO'},
    'VINTAGE': {'slug': 'VINCOFE', 'yf': 'VINCOFE.BO'},
    'ETERNAL': {'slug': 'ETERNAL', 'yf': 'ETERNAL.BO'},
    'MICEL': {'slug': '532850', 'yf': '532850.BO'},
    'PENNARIND': {'slug': '513228', 'yf': 'PENIND.NS'},
    'EMVEE (Pre-IPO)': {'slug': 'EMMVEE', 'yf': None, 'drhp_mcap': 6200.0},
    'ATHER (Pre-IPO)': {'slug': 'ATHERENERG', 'yf': None, 'drhp_mcap': 11900.0},
    'MBENGG (Pre-IPO)': {'slug': 'MBEL', 'yf': None, 'drhp_mcap': 1450.0},
    'TRANSRAIL (Pre-IPO)': {'slug': 'TRANSRAILL', 'yf': None, 'drhp_mcap': 3200.0},
    'NSDL (Pre-IPO)': {'slug': '544467', 'yf': None, 'drhp_mcap': 10000.0},
    'BELRISE (Pre-IPO)': {'slug': 'BELRISE', 'yf': None, 'drhp_mcap': 14500.0},
    'IKS (Pre-IPO)': {'slug': 'IKS', 'yf': None, 'drhp_mcap': 35000.0},
    'VIKRAM (Pre-IPO)': {'slug': 'VIKRAMSOLR', 'yf': None, 'drhp_mcap': 7500.0},
    'SAATVIK (Pre-IPO)': {'slug': 'SAATVIKGL', 'yf': None, 'drhp_mcap': 2800.0}
}

headers = {'User-Agent': 'Mozilla/5.0'}

def fetch_mcap(s):
    sym = s['symbol']
    clean = s.get('clean_sym', sym).split()[0]
    cmp = s.get('today_price', 0)
    
    mapping = CUSTOM_MAPPINGS.get(sym, {})
    slug = mapping.get('slug', clean)
    yf_tk = mapping.get('yf', f'{clean}.NS')
    drhp_mcap = mapping.get('drhp_mcap')
    
    mcap_cr = None
    shares = None
    
    # 1. Try Screener top-ratios
    if slug:
        for mode in ['consolidated/', '']:
            try:
                r = requests.get(f'https://www.screener.in/company/{slug}/{mode}', headers=headers, timeout=3.5)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    top = soup.find('ul', id='top-ratios')
                    if top:
                        for li in top.find_all('li'):
                            txt = li.get_text(strip=True)
                            if 'Market Cap' in txt:
                                num = li.find('span', class_='number')
                                if num:
                                    mcap_cr = float(num.text.replace(',', ''))
                                    break
                    if mcap_cr:
                        break
            except:
                pass
                
    # 2. Try Yahoo Finance
    if not mcap_cr and yf_tk:
        try:
            t = yf.Ticker(yf_tk)
            info = t.info
            if info and info.get('marketCap'):
                raw = float(info['marketCap'])
                mcap_cr = round(raw / 10000000.0, 1)
                if info.get('sharesOutstanding'):
                    shares = float(info['sharesOutstanding'])
        except:
            pass

    # 3. Fallback DRHP
    if not mcap_cr and drhp_mcap:
        mcap_cr = drhp_mcap

    # Compute shares if not found
    if mcap_cr and cmp > 0 and not shares:
        shares = round((mcap_cr * 10000000.0) / cmp)

    return {
        'symbol': sym,
        'cmp': cmp,
        'mcap_cr': mcap_cr,
        'shares': shares
    }

print(f'Fetching market caps for all {len(stocks)} stocks...')
t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    results = list(executor.map(fetch_mcap, stocks))

print(f'Fetched in {time.time()-t0:.2f}s')

os.makedirs('scratch', exist_ok=True)
with open('scratch/all_119_mcaps.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

missing = [r for r in results if r['mcap_cr'] is None]
print(f'Populated: {len(results)-len(missing)} / {len(results)}')
if missing:
    print('Missing:', [m['symbol'] for m in missing])
