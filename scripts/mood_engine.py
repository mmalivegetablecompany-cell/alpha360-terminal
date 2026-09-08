def assign_market_mood(raw_sym, theme, sector, mcap, pos_news, neg_news, consensus, tailwinds):
    # Determine mood score based on high-priority themes
    high_priority_syms = ["ZENTEC", "POWERINDIA", "APOLLO", "TDPOWERSYS", "UNOMINDA", "RKFORGE", "GPIL", "HEROMOTOCO", "CDSL", "RELIANCE"]
    
    if raw_sym in high_priority_syms:
        mood_score = 92 if raw_sym in ["ZENTEC", "POWERINDIA", "CDSL"] else 90
        investor_mood = "🔥 Extremely Bullish / Retail & Institutional Consensus"
    elif "Solar" in sector or "Renewable" in sector or "Defence" in sector or "Electric" in sector:
        mood_score = 88
        investor_mood = "🔥 Strong Bullish / Institutional Accumulation"
    elif "Large Cap" in mcap or "PSU" in sector:
        mood_score = 84
        investor_mood = "🟢 Constructive / Positive Institutional Bias"
    elif "Small Cap" in mcap or "Mid Cap" in mcap:
        mood_score = 82
        investor_mood = "🟢 High Quality Compounder / Institutional Favor"
    else:
        mood_score = 75
        investor_mood = "⚖️ Neutral / Mixed Market Sentiment"
        
    return {
        "mood_score": mood_score,
        "investor_mood": investor_mood,
        "pos_news": pos_news,
        "neg_news": neg_news,
        "consensus": consensus,
        "sector_tailwinds": tailwinds
    }
