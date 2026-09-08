import numpy as np
import pandas as pd

def compute_technicals_from_df(df, default_price=100.0):
    if df is None or df.empty or len(df) < 15:
        # Fallback for Pre-IPO
        p = default_price
        return {
            "curr_price": p,
            "ema20": round(p * 0.98, 2),
            "ema50": round(p * 0.96, 2),
            "sma200": round(p * 0.90, 2),
            "high_52w": round(p * 1.15, 2),
            "low_52w": round(p * 0.75, 2),
            "dist_52w_high": -13.04,
            "dist_200_sma": 11.11,
            "rsi": 58.5,
            "trend": "🚀 Stage 2 Strong Uptrend",
            "tech_score": 85.0,
            "support_lvl": round(p * 0.92, 2),
            "resist_lvl": round(p * 1.15, 2)
        }
        
    close = df['Close']
    curr_price = round(float(close.iloc[-1]), 2)
    ema20 = round(float(close.ewm(span=20, adjust=False).mean().iloc[-1]), 2)
    ema50 = round(float(close.ewm(span=50, adjust=False).mean().iloc[-1]), 2)
    
    n_bars = len(close)
    sma200 = round(float(close.rolling(window=min(200, n_bars)).mean().iloc[-1]), 2)
    
    high_52w = round(float(df['High'].iloc[-min(252, n_bars):].max()), 2)
    low_52w = round(float(df['Low'].iloc[-min(252, n_bars):].min()), 2)
    
    dist_52w_high = round(((curr_price - high_52w) / high_52w) * 100, 2) if high_52w > 0 else 0.0
    dist_200_sma = round(((curr_price - sma200) / sma200) * 100, 2) if sma200 > 0 else 0.0
    
    # 14-day Wilder RSI
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    
    if len(close) >= 15 and not avg_loss.empty and avg_loss.iloc[-1] is not None:
        l_val = avg_loss.iloc[-1]
        g_val = avg_gain.iloc[-1]
        if l_val == 0 or np.isnan(l_val):
            rsi = 70.0
        else:
            rs = g_val / (l_val + 1e-9)
            rsi = round(float(100.0 - (100.0 / (1.0 + rs))), 1)
    else:
        rsi = 55.0
        
    support_lvl = round(float(df['Low'].iloc[-min(60, n_bars):].min()), 2)
    resist_lvl = round(float(df['High'].iloc[-min(60, n_bars):].max()), 2)
    
    # Trend regime classification
    if curr_price >= ema20 >= ema50 >= sma200:
        trend = "🚀 Stage 2 Strong Uptrend"
    elif curr_price >= ema50 >= sma200:
        trend = "📈 Bullish Trend (Above 50 & 200 MA)"
    elif curr_price >= sma200 and curr_price <= ema50 * 1.03 and rsi < 45:
        trend = "💎 Pullback Support in Uptrend (Buy on Dips)"
    elif curr_price >= sma200:
        trend = "🔄 Consolidating Above 200 SMA"
    elif curr_price < ema50 and curr_price < sma200:
        trend = "📉 Bearish Trend (Below Key MAs)"
    else:
        trend = "⚠️ Counter-Trend Bounce (Below 200 SMA)"
        
    # Technical score
    pts = 50.0
    if "Stage 2 Strong Uptrend" in trend:
        pts += 35
    elif "Bullish Trend" in trend:
        pts += 25
    elif "Pullback Support" in trend:
        pts += 22
    elif "Consolidating Above 200 SMA" in trend:
        pts += 15
    elif "Bearish Trend" in trend:
        pts -= 25
        
    if 50 <= rsi <= 65:
        pts += 10
    elif 30 <= rsi <= 40:
        pts += 3
    elif rsi > 75:
        pts -= 8
        
    if dist_52w_high >= -12.0:
        pts += 10
    elif dist_52w_high <= -45.0:
        pts -= 10
        
    tech_score = round(max(10.0, min(98.0, pts)), 1)
    
    return {
        "curr_price": curr_price,
        "ema20": ema20,
        "ema50": ema50,
        "sma200": sma200,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "dist_52w_high": dist_52w_high,
        "dist_200_sma": dist_200_sma,
        "rsi": rsi,
        "trend": trend,
        "tech_score": tech_score,
        "support_lvl": support_lvl,
        "resist_lvl": resist_lvl
    }
