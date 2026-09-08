
# Ticker and slug mapping
STOCK_MAPPINGS = {
    '3MINDIA': {'clean_sym': '3MINDIA', 'screener': '3MINDIA', 'yf': '3MINDIA.NS', 'mcap': 'Large Cap'},
    'AVL': {'clean_sym': 'AVL', 'screener': 'AVL', 'yf': 'AVL.NS', 'mcap': 'Small Cap'},
    'APOLLO': {'clean_sym': 'APOLLO', 'screener': 'APOLLO', 'yf': 'APOLLO.NS', 'mcap': 'Small Cap'},
    'ASHOKLEY': {'clean_sym': 'ASHOKLEY', 'screener': 'ASHOKLEY', 'yf': 'ASHOKLEY.NS', 'mcap': 'Large Cap'},
    'BRIDGESE': {'clean_sym': '530249', 'screener': '530249', 'yf': '530249.BO', 'mcap': 'Micro Cap'},
    'CDSL': {'clean_sym': 'CDSL', 'screener': 'CDSL', 'yf': 'CDSL.NS', 'mcap': 'Mid Cap'},
    'CHENNPETRO': {'clean_sym': 'CHENNPETRO', 'screener': 'CHENNPETRO', 'yf': 'CHENNPETRO.NS', 'mcap': 'Mid Cap'},
    'DOLPHINOFF': {'clean_sym': 'DOLPHIN', 'screener': 'DOLPHIN', 'yf': 'DOLPHIN.NS', 'mcap': 'Micro Cap'},
    'ETERNAL': {'clean_sym': 'ETERNAL', 'screener': 'ETERNAL', 'yf': 'ETERNAL.BO', 'mcap': 'Micro Cap'},
    'FORCEMOT': {'clean_sym': 'FORCEMOT', 'screener': 'FORCEMOT', 'yf': 'FORCEMOT.NS', 'mcap': 'Small Cap'},
    'GENSOL': {'clean_sym': 'GENSOL', 'screener': 'GENSOL', 'yf': 'GENSOL.NS', 'mcap': 'Small Cap'},
    'GPIL': {'clean_sym': 'GPIL', 'screener': 'GPIL', 'yf': 'GPIL.NS', 'mcap': 'Mid Cap'},
    'GPECO': {'clean_sym': 'GPECO', 'screener': 'GPECO', 'yf': 'GPECO.NS', 'mcap': 'SME / Micro'},
    'GRANULES': {'clean_sym': 'GRANULES', 'screener': 'GRANULES', 'yf': 'GRANULES.NS', 'mcap': 'Mid Cap'},
    'GMDCLTD': {'clean_sym': 'GMDCLTD', 'screener': 'GMDCLTD', 'yf': 'GMDCLTD.NS', 'mcap': 'Mid Cap'},
    'HEROMOTOCO': {'clean_sym': 'HEROMOTOCO', 'screener': 'HEROMOTOCO', 'yf': 'HEROMOTOCO.NS', 'mcap': 'Large Cap'},
    'HINDALCO': {'clean_sym': 'HINDALCO', 'screener': 'HINDALCO', 'yf': 'HINDALCO.NS', 'mcap': 'Large Cap'},
    'POWERINDIA': {'clean_sym': 'POWERINDIA', 'screener': 'POWERINDIA', 'yf': 'POWERINDIA.NS', 'mcap': 'Large Cap'},
    'INTLCONV': {'clean_sym': 'INTLCONV', 'screener': 'INTLCONV', 'yf': 'INTLCONV.NS', 'mcap': 'Micro Cap'},
    'IRCON': {'clean_sym': 'IRCON', 'screener': 'IRCON', 'yf': 'IRCON.NS', 'mcap': 'Mid Cap'},
    'ITC': {'clean_sym': 'ITC', 'screener': 'ITC', 'yf': 'ITC.NS', 'mcap': 'Large Cap'},
    'JBMA': {'clean_sym': 'JBMA', 'screener': 'JBMA', 'yf': 'JBMA.NS', 'mcap': 'Mid Cap'},
    'KEC': {'clean_sym': 'KEC', 'screener': 'KEC', 'yf': 'KEC.NS', 'mcap': 'Mid Cap'},
    'KNRCON': {'clean_sym': 'KNRCON', 'screener': 'KNRCON', 'yf': 'KNRCON.NS', 'mcap': 'Small Cap'},
    'LICI': {'clean_sym': 'LICI', 'screener': 'LICI', 'yf': 'LICI.NS', 'mcap': 'Large Cap'},
    'MBENGG': {'clean_sym': 'MBENGG', 'screener': None, 'yf': None, 'mcap': 'IPO / Unlisted', 'symbol_name': 'MBENGG (Pre-IPO)'},
    'MASTEK': {'clean_sym': 'MASTEK', 'screener': 'MASTEK', 'yf': 'MASTEK.NS', 'mcap': 'Small Cap'},
    'MICEL': {'clean_sym': 'MICEL', 'screener': '532850', 'yf': 'MICEL.NS', 'mcap': 'Micro Cap'},
    'NSDL': {'clean_sym': 'NSDL', 'screener': None, 'yf': None, 'mcap': 'IPO / Unlisted', 'symbol_name': 'NSDL (Pre-IPO)'},
    'NTPC': {'clean_sym': 'NTPC', 'screener': 'NTPC', 'yf': 'NTPC.NS', 'mcap': 'Large Cap'},
    'NTPCGREEN': {'clean_sym': 'NTPCGREEN', 'screener': 'NTPCGREEN', 'yf': 'NTPCGREEN.NS', 'mcap': 'Large Cap'},
    'ONGC': {'clean_sym': 'ONGC', 'screener': 'ONGC', 'yf': 'ONGC.NS', 'mcap': 'Large Cap'},
    'MOBIKWIK': {'clean_sym': 'MOBIKWIK', 'screener': 'MOBIKWIK', 'yf': 'MOBIKWIK.NS', 'mcap': 'Small Cap'},
    'PENNARIND': {'clean_sym': 'PENIND', 'screener': '513228', 'yf': 'PENIND.NS', 'mcap': 'Small Cap'},
    'POWERGRID': {'clean_sym': 'POWERGRID', 'screener': 'POWERGRID', 'yf': 'POWERGRID.NS', 'mcap': 'Large Cap'},
    'PGINVIT': {'clean_sym': 'PGINVIT', 'screener': 'PGINVIT', 'yf': 'PGINVIT.NS', 'mcap': 'Mid Cap'},
    'RKFORGE': {'clean_sym': 'RKFORGE', 'screener': 'RKFORGE', 'yf': 'RKFORGE.NS', 'mcap': 'Mid Cap'},
    'RAYMOND': {'clean_sym': 'RAYMOND', 'screener': 'RAYMOND', 'yf': 'RAYMOND.NS', 'mcap': 'Mid Cap'},
    'REDINGTON': {'clean_sym': 'REDINGTON', 'screener': 'REDINGTON', 'yf': 'REDINGTON.NS', 'mcap': 'Mid Cap'},
    'REFEX': {'clean_sym': 'REFEX', 'screener': 'REFEX', 'yf': 'REFEX.NS', 'mcap': 'Small Cap'},
    'RELIANCE': {'clean_sym': 'RELIANCE', 'screener': 'RELIANCE', 'yf': 'RELIANCE.NS', 'mcap': 'Large Cap'},
    'RPOWER': {'clean_sym': 'RPOWER', 'screener': 'RPOWER', 'yf': 'RPOWER.NS', 'mcap': 'Small Cap'},
    'SENORES': {'clean_sym': 'SENORES', 'screener': 'SENORES', 'yf': 'SENORES.NS', 'mcap': 'Small Cap'},
    'TDPOWERSYS': {'clean_sym': 'TDPOWERSYS', 'screener': 'TDPOWERSYS', 'yf': 'TDPOWERSYS.NS', 'mcap': 'Small Cap'},
    'TRANSRAIL': {'clean_sym': 'TRANSRAIL', 'screener': None, 'yf': None, 'mcap': 'IPO / Unlisted', 'symbol_name': 'TRANSRAIL (Pre-IPO)'},
    'UNOMINDA': {'clean_sym': 'UNOMINDA', 'screener': 'UNOMINDA', 'yf': 'UNOMINDA.NS', 'mcap': 'Large Cap'},
    'VINTAGE': {'clean_sym': 'VINCOFE', 'screener': 'VINCOFE', 'yf': 'VINCOFE.BO', 'mcap': 'Micro Cap'},
    'ZENTEC': {'clean_sym': 'ZENTEC', 'screener': 'ZENTEC', 'yf': 'ZENTEC.NS', 'mcap': 'Mid Cap'},
    'ZENSARTECH': {'clean_sym': 'ZENSARTECH', 'screener': 'ZENSARTECH', 'yf': 'ZENSARTECH.NS', 'mcap': 'Mid Cap'}
}

def load_new_stocks_catalog():
    target_path = 'research/unique_watchlist_new_stocks_exploration_report.md' if os.path.exists('research/unique_watchlist_new_stocks_exploration_report.md') else 'unique_watchlist_new_stocks_exploration_report.md'
    with open(target_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    catalog = []
    for line in lines:
        if line.startswith('| **'):
            parts = [p.strip() for p in line.split('|')]
            sno = int(parts[1].replace('*', '').strip())
            name = parts[2].replace('*', '').strip()
            raw_sym = parts[3].replace(chr(96), '').strip()
            sector = parts[4].strip()
            mcap_tier = parts[5].strip()
            watchlists = parts[6].strip()
            theme = parts[7].strip()

            mapping = STOCK_MAPPINGS.get(raw_sym, {
                'clean_sym': raw_sym, 'screener': raw_sym, 'yf': raw_sym + '.NS', 'mcap': mcap_tier
            })

            symbol = mapping.get('symbol_name', raw_sym)
            catalog.append({
                'excel_sno': sno,
                'raw_sym': raw_sym,
                'symbol': symbol,
                'name': name,
                'sector': sector,
                'mcap': mapping.get('mcap', mcap_tier),
                'clean_sym': mapping.get('clean_sym', raw_sym),
                'screener_slug': mapping.get('screener'),
                'yf_ticker': mapping.get('yf'),
                'theme': theme,
                'watchlists': watchlists
            })
    return catalog
