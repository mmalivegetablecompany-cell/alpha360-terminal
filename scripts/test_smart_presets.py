import sys, json
sys.stdout.reconfigure(encoding="utf-8")

stocks = json.load(open("scripts/combined_119_stocks.json", encoding="utf-8"))

def test_filter(name, condition_fn):
    matches = [s for s in stocks if condition_fn(s)]
    print(f"Preset [{name}]: {len(matches)} / {len(stocks)} stocks match")
    for s in matches[:3]:
        print(f"   -> {s['symbol']}: CMP ₹{s['today_price']}, Mcap ₹{s['mcap_cr']} Cr, PE {s.get('today_pe')}, PB {s.get('today_pb')}, PEG {s.get('today_peg')}, Score {s.get('master_score')}")

print("Testing Presets:")
# 1. Peter Lynch GARP: PEG <= 1.0, YoY PAT >= 20, Funda >= 70
test_filter("Peter Lynch GARP", lambda s: (
    isinstance(s.get("today_peg"), (int, float)) and 0 < s["today_peg"] <= 1.0 and
    isinstance(s.get("latest_yoy_pat"), (int, float)) and s["latest_yoy_pat"] >= 20.0 and
    s.get("score", 0) >= 70.0
))

# 2. Quad Alpha Leaders: Master >= 88, Trend Stage 2, Upside >= 15
test_filter("Quad Alpha Leaders", lambda s: (
    s.get("master_score", 0) >= 88.0 and
    "Stage 2" in s.get("technicals", {}).get("trend", "") and
    s.get("forecast", {}).get("upside_mean_pct", 0) >= 15.0
))

# 3. Deep Margin of Safety: PE <= 25, PB <= 4.0, Upside >= 20
test_filter("Deep Margin of Safety", lambda s: (
    isinstance(s.get("today_pe"), (int, float)) and s["today_pe"] <= 25.0 and
    isinstance(s.get("today_pb"), (int, float)) and s["today_pb"] <= 4.0 and
    s.get("forecast", {}).get("upside_mean_pct", 0) >= 20.0
))

# 4. Institutional Bluechips: Mcap >= 20000, Master >= 80, Upside >= 10
test_filter("Institutional Bluechips", lambda s: (
    s.get("mcap_cr", 0) >= 20000.0 and
    s.get("master_score", 0) >= 80.0 and
    s.get("forecast", {}).get("upside_mean_pct", 0) >= 10.0
))

# 5. Stage-2 Dip Buys: Stage 2, RSI < 48, Funda >= 70
test_filter("Stage-2 Dip Buys", lambda s: (
    "Stage 2" in s.get("technicals", {}).get("trend", "") and
    s.get("technicals", {}).get("rsi", 100) < 48.0 and
    s.get("score", 0) >= 70.0
))

# 6. Hyper-Growth Breakouts: YoY PAT >= 50%, RSI >= 55 and <= 72
test_filter("Hyper-Growth Breakouts", lambda s: (
    isinstance(s.get("latest_yoy_pat"), (int, float)) and s["latest_yoy_pat"] >= 50.0 and
    55.0 <= s.get("technicals", {}).get("rsi", 0) <= 72.0
))
