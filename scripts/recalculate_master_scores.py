import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

def recalculate_master_scores():
    print("==================================================================")
    print("=== RECALCULATING MASTER SCORES (35%F + 25%ET_FC + 20%ET + 20%T) =")
    print("==================================================================")

    with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)

    print(f"Loaded {len(stocks)} stocks.")

    for s in stocks:
        f_score = float(s.get("score") or 50.0)
        fc_score = float(s.get("forecast_score") or 50.0)
        t_score = float(s.get("tech_score") or 50.0)
        
        ep = s.get("et_prime", {})
        raw_et_score = ep.get("stock_score")
        et_score_100 = (float(raw_et_score) * 10.0) if raw_et_score is not None else 50.0
        
        # New Master Score Formula:
        # 35% Fundamental + 25% ET Forecast + 20% ET Prime Score + 20% Technical
        master_score = round(0.35 * f_score + 0.25 * fc_score + 0.20 * et_score_100 + 0.20 * t_score, 1)
        s["master_score"] = master_score
        s["et_score_100"] = et_score_100

        # Confluence category
        upside = s.get("forecast", {}).get("upside_mean_pct")
        rsi = s.get("technicals", {}).get("rsi", 50)
        if master_score >= 88.0:
            s["master_category"] = "🌟 Master Alpha Leader (Score ≥ 88)"
        elif master_score >= 80.0:
            s["master_category"] = "💎 High-Conviction Compounder (Score 80–87.9)"
        elif upside is not None and upside >= 20.0:
            s["master_category"] = "🚀 High ET Forecast Upside"
        elif f_score >= 70.0 and rsi < 45:
            s["master_category"] = "🎯 High-Growth Dip Buy at Support"
        elif master_score >= 55.0:
            s["master_category"] = "⚖️ Resilient Watchlist Compounder"
        else:
            s["master_category"] = "⚠️ Neutral / Headwinds Lagging"

    # Sort descending by master_score, then secondary by (funda + et_fc)
    stocks.sort(key=lambda x: (x.get("master_score", 0), (x.get("score", 0) + x.get("forecast_score", 0))), reverse=True)

    # Re-assign master_rank 1 to 424
    for r, s in enumerate(stocks, 1):
        s["master_rank"] = r

    with open("scripts/combined_master_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2, ensure_ascii=False)

    print(f"✓ Successfully updated scripts/combined_master_stocks.json with {len(stocks)} stocks.")
    print("\n--- TOP 15 STOCKS UNDER NEW FORMULA ---")
    for s in stocks[:15]:
        ep = s.get("et_prime", {})
        fc = s.get("forecast", {})
        print(f"#{s['master_rank']:<2} {s['symbol']:<12} | Master: {s['master_score']:<5} | Funda(35%): {s['score']:<4} | ET_FC(25%): {s['forecast_score']:<4} | ET_Score(20%): {ep.get('stock_score')}/10 | Tech(20%): {s['tech_score']:<4} | Upside: {fc.get('upside_mean_pct')}% | Target: ₹{fc.get('mean_target')}")

if __name__ == "__main__":
    recalculate_master_scores()
