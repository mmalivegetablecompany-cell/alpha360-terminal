import json
import time
import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print('=' * 70)
print('STARTING REAL MARKET OHLCV EXTRACTION & TECHNICAL RECALCULATION')
print('=' * 70)

# Load existing 424 stocks
with open('html_424_stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

print(f'Total stocks to process: {len(stocks)}')

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

unique_tickers = sorted(list(set(sym_to_ticker.values())))
print(f'Unique market tickers to query: {len(unique_tickers)}')

# Batch download in chunks of 25
BATCH_SIZE = 25
all_data = {}

for i in range(0, len(unique_tickers), BATCH_SIZE):
    chunk = unique_tickers[i:i + BATCH_SIZE]
    batch_num = (i // BATCH_SIZE) + 1
    total_batches = ((len(unique_tickers) - 1) // BATCH_SIZE) + 1
    print(f'Fetching batch {batch_num}/{total_batches} ({len(chunk)} tickers)...', end='', flush=True)
    t0 = time.time()
    try:
        df = yf.download(chunk, period='1y', group_by='ticker', progress=False)
        t1 = time.time()
        print(f' done in {t1-t0:.2f}s')
        if len(chunk) == 1:
            t = chunk[0]
            all_data[t] = df
        else:
            for t in chunk:
                if t in df:
                    all_data[t] = df[t]
    except Exception as e:
        print(f' error: {e}')

print(f'\nTotal ticker datasets cached: {len(all_data)}')

# Recalculate indicators for all 424 stocks
computed_technicals = {}
real_count = 0
synthetic_count = 0

for s in stocks:
    sym = s['symbol']
    name = s.get('name', '')
    ticker = sym_to_ticker[sym]
    cmp_fallback = float(s.get('today_price') or 100.0)
    
    df_raw = all_data.get(ticker)
    has_real_data = False
    
    if df_raw is not None and not df_raw.empty:
        df_clean = df_raw.dropna(subset=['Close'])
        if len(df_clean) >= 5:
            has_real_data = True
            
    if has_real_data:
        real_count += 1
        close_series = df_clean['Close']
        high_series = df_clean['High']
        low_series = df_clean['Low']
        open_series = df_clean['Open']
        vol_series = df_clean['Volume']
        
        cmp = round(float(close_series.iloc[-1]), 2)
        prev_close = round(float(close_series.iloc[-2]), 2) if len(close_series) >= 2 else cmp
        day_high = round(float(high_series.iloc[-1]), 2)
        day_low = round(float(low_series.iloc[-1]), 2)
        volume = int(vol_series.iloc[-1]) if pd.notna(vol_series.iloc[-1]) else int(s.get('volume') or 100000)
        
        high_52w = round(float(high_series.max()), 2)
        low_52w = round(float(low_series.min()), 2)
        
        ema9 = round(float(close_series.ewm(span=9, adjust=False).mean().iloc[-1]), 2)
        ema20 = round(float(close_series.ewm(span=20, adjust=False).mean().iloc[-1]), 2)
        ema50 = round(float(close_series.ewm(span=50, adjust=False).mean().iloc[-1]), 2)
        ema100 = round(float(close_series.ewm(span=100, adjust=False).mean().iloc[-1]), 2)
        sma200 = round(float(close_series.rolling(window=min(200, len(close_series))).mean().iloc[-1]), 2)
        
        # Wilder's 14 RSI
        delta = close_series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=13, adjust=False).mean()
        avg_loss = loss.ewm(com=13, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        rsi_series = 100 - (100 / (1 + rs))
        rsi = round(float(rsi_series.iloc[-1]), 1)
        if np.isnan(rsi):
            rsi = 55.0
            
        # ATR 14
        tr1 = high_series - low_series
        tr2 = (high_series - close_series.shift(1)).abs()
        tr3 = (low_series - close_series.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_val = round(float(tr.ewm(com=13, adjust=False).mean().iloc[-1]), 2)
        if np.isnan(atr_val) or atr_val <= 0:
            atr_val = round(cmp * 0.02, 2)
            
        # Bollinger Bands (20, 2)
        bb_mid = ema20
        rolling_std = float(close_series.rolling(window=min(20, len(close_series))).std().iloc[-1])
        if np.isnan(rolling_std) or rolling_std <= 0:
            rolling_std = atr_val * 0.9
        bb_upper = round(bb_mid + (2.0 * rolling_std), 2)
        bb_lower = round(max(0.1, bb_mid - (2.0 * rolling_std)), 2)
        bb_bandwidth = round(((bb_upper - bb_lower) / (bb_mid + 1e-6)) * 100, 2)
        bb_pct_b = round(((cmp - bb_lower) / (bb_upper - bb_lower + 1e-6)) * 100, 2)
        
        # Pivots
        pivot_p = round((day_high + day_low + cmp) / 3.0, 2)
        r1 = round(2 * pivot_p - day_low, 2)
        s1 = round(2 * pivot_p - day_high, 2)
        r2 = round(pivot_p + (day_high - day_low), 2)
        s2 = round(pivot_p - (day_high - day_low), 2)
        r3 = round(day_high + 2 * (pivot_p - day_low), 2)
        s3 = round(day_low - 2 * (day_high - pivot_p), 2)
        
        # Fibonacci
        diff_52 = high_52w - low_52w
        fib_236 = round(high_52w - 0.236 * diff_52, 2)
        fib_382 = round(high_52w - 0.382 * diff_52, 2)
        fib_500 = round(high_52w - 0.500 * diff_52, 2)
        fib_618 = round(high_52w - 0.618 * diff_52, 2)
        fib_786 = round(high_52w - 0.786 * diff_52, 2)
        fib_1618 = round(high_52w + 0.618 * diff_52, 2)
        
        # 60 Real Candlestick Bars
        candles = []
        recent_df = df_clean.tail(60)
        for date_idx, row in recent_df.iterrows():
            d_str = date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx)[:10]
            c_op = round(float(row['Open']), 2) if pd.notna(row['Open']) else cmp
            c_hi = round(float(row['High']), 2) if pd.notna(row['High']) else cmp
            c_lo = round(float(row['Low']), 2) if pd.notna(row['Low']) else cmp
            c_cl = round(float(row['Close']), 2) if pd.notna(row['Close']) else cmp
            c_vo = int(row['Volume']) if pd.notna(row['Volume']) else 100000
            candles.append({
                'date': d_str,
                'open': c_op,
                'high': c_hi,
                'low': c_lo,
                'close': c_cl,
                'volume': c_vo
            })
            
    else:
        synthetic_count += 1
        cmp = cmp_fallback
        prev_close = round(cmp * 0.998, 2)
        day_high = round(cmp * 1.015, 2)
        day_low = round(cmp * 0.985, 2)
        volume = int(s.get('volume') or 150000)
        
        high_52w = round(cmp * 1.18, 2)
        low_52w = round(cmp * 0.78, 2)
        
        ema9 = round(cmp * 0.995, 2)
        ema20 = round(cmp * 0.985, 2)
        ema50 = round(cmp * 0.960, 2)
        ema100 = round(cmp * 0.935, 2)
        sma200 = round(cmp * 0.900, 2)
        
        rsi = 56.5
        atr_val = round(cmp * 0.022, 2)
        bb_mid = ema20
        bb_upper = round(bb_mid + (2.0 * atr_val * 1.5), 2)
        bb_lower = round(max(0.1, bb_mid - (2.0 * atr_val * 1.5)), 2)
        bb_bandwidth = round(((bb_upper - bb_lower) / bb_mid) * 100, 2)
        bb_pct_b = round(((cmp - bb_lower) / (bb_upper - bb_lower + 1e-6)) * 100, 2)
        
        pivot_p = round((day_high + day_low + cmp) / 3.0, 2)
        r1 = round(2 * pivot_p - day_low, 2)
        s1 = round(2 * pivot_p - day_high, 2)
        r2 = round(pivot_p + (day_high - day_low), 2)
        s2 = round(pivot_p - (day_high - day_low), 2)
        r3 = round(day_high + 2 * (pivot_p - day_low), 2)
        s3 = round(day_low - 2 * (day_high - pivot_p), 2)
        
        diff_52 = high_52w - low_52w
        fib_236 = round(high_52w - 0.236 * diff_52, 2)
        fib_382 = round(high_52w - 0.382 * diff_52, 2)
        fib_500 = round(high_52w - 0.500 * diff_52, 2)
        fib_618 = round(high_52w - 0.618 * diff_52, 2)
        fib_786 = round(high_52w - 0.786 * diff_52, 2)
        fib_1618 = round(high_52w + 0.618 * diff_52, 2)
        
        # Synthetic candles
        candles = []
        base_date = datetime.now() - timedelta(days=90)
        curr_synth = round(cmp * 0.94, 2)
        days_added = 0
        for di in range(90):
            dt = base_date + timedelta(days=di)
            if dt.weekday() >= 5: # weekend
                continue
            days_added += 1
            if days_added > 60:
                break
            drift = (cmp - curr_synth) / (65 - days_added)
            step_c = round(curr_synth + drift + ((di % 5) - 2) * (atr_val * 0.2), 2)
            step_o = round(curr_synth, 2)
            step_h = round(max(step_o, step_c) + atr_val * 0.3, 2)
            step_l = round(min(step_o, step_c) - atr_val * 0.3, 2)
            curr_synth = step_c
            candles.append({
                'date': dt.strftime('%Y-%m-%d'),
                'open': step_o,
                'high': step_h,
                'low': step_l,
                'close': step_c,
                'volume': int(volume * (0.8 + (di % 5) * 0.1))
            })
        if candles:
            candles[-1]['close'] = cmp
            candles[-1]['high'] = day_high
            candles[-1]['low'] = day_low

    computed_technicals[sym] = {
        'symbol': sym,
        'name': name,
        'ticker': ticker,
        'has_real_data': has_real_data,
        'cmp': cmp,
        'prev_close': prev_close,
        'day_high': day_high,
        'day_low': day_low,
        'volume': volume,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'ema9': ema9,
        'ema20': ema20,
        'ema50': ema50,
        'ema100': ema100,
        'sma200': sma200,
        'rsi': rsi,
        'atr': atr_val,
        'bb_mid': bb_mid,
        'bb_upper': bb_upper,
        'bb_lower': bb_lower,
        'bb_bandwidth': bb_bandwidth,
        'bb_pct_b': bb_pct_b,
        'pivots': {
            'pivot': pivot_p,
            's1': s1, 's2': s2, 's3': s3,
            'r1': r1, 'r2': r2, 'r3': r3
        },
        'fibonacci': {
            'fib_236': fib_236,
            'fib_382': fib_382,
            'fib_500': fib_500,
            'fib_618': fib_618,
            'fib_786': fib_786,
            'fib_1618': fib_1618
        },
        'candles': candles
    }

print(f'\nRecalculation complete: {real_count} stocks with real market history, {synthetic_count} stocks with synthetic bounds.')

# Save to cache
with open('market_technicals_cache.json', 'w', encoding='utf-8') as f:
    json.dump(computed_technicals, f, indent=2, ensure_ascii=False)

print('Saved market_technicals_cache.json successfully!')

# Check key focus stocks
for sym in ['TRANSRAIL', 'WAAREE', 'KPENERGY', 'AUTHUM', 'NSDL', 'EMVEE', 'ATHER']:
    if sym in computed_technicals:
        ct = computed_technicals[sym]
        c = ct['cmp']
        e20 = ct['ema20']
        e50 = ct['ema50']
        s200 = ct['sma200']
        l52 = ct['low_52w']
        h52 = ct['high_52w']
        rd = ct['has_real_data']
        print(f"{sym}: CMP={c}, EMA20={e20}, EMA50={e50}, SMA200={s200}, 52W=({l52} - {h52}), Real={rd}")
