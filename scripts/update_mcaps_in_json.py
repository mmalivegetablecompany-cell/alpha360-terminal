import json

stocks = json.load(open("scripts/combined_119_stocks.json", encoding="utf-8"))
mcaps = json.load(open("scratch/all_119_mcaps.json", encoding="utf-8"))

OVERRIDES = {
    "MICEL": (885.5, 241011560),
    "HBLPOWER": (19464.6, 277195008),
    "AUTHUM": (44087.5, 849225500),
    "TATAMOTORS_114": (168976.4, 3673400000),
    "TATAMOTORS_115": (114242.7, 3673400000)
}

for i, s in enumerate(stocks):
    sym = s["symbol"]
    sno = s.get("sno", i+1)
    m = mcaps[i]
    
    mcap_cr = m.get("mcap_cr")
    shares = m.get("shares")
    
    if sym == "TATAMOTORS":
        key = f"TATAMOTORS_{sno}"
        if key in OVERRIDES:
            mcap_cr, shares = OVERRIDES[key]
    elif sym in OVERRIDES:
        mcap_cr, shares = OVERRIDES[sym]
        
    if mcap_cr is None:
        raise ValueError(f"Missing mcap for {sym} sno {sno}")
    
    if shares is None or shares <= 0:
        cmp = s.get("today_price", 0)
        if cmp > 0:
            shares = round((mcap_cr * 10000000.0) / cmp)
        else:
            shares = 10000000
            
    mcap_cr = round(float(mcap_cr), 1)
    shares = int(shares)
    
    if "Pre-IPO" in sym:
        tier = "Pre-IPO"
    elif mcap_cr >= 100000.0:
        tier = "Mega Cap"
    elif mcap_cr >= 20000.0:
        tier = "Large Cap"
    elif mcap_cr >= 5000.0:
        tier = "Mid Cap"
    else:
        tier = "Small Cap"
        
    s["mcap_cr"] = mcap_cr
    s["shares_outstanding"] = shares
    s["mcap_tier"] = tier

with open("scripts/combined_119_stocks.json", "w", encoding="utf-8") as f:
    json.dump(stocks, f, indent=2, ensure_ascii=False)

print(f"Successfully updated all {len(stocks)} stocks in scripts/combined_119_stocks.json!")
tiers = {}
for s in stocks:
    tiers[s["mcap_tier"]] = tiers.get(s["mcap_tier"], 0) + 1
print("Tier distribution:", tiers)
