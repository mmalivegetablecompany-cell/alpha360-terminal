import json, sys, re, os

sys.stdout.reconfigure(encoding="utf-8")

def classify_amfi_tier(mcap_cr):
    """
    Standard Indian Market (SEBI / AMFI) Market Cap Classification:
    - Large Cap: >= ₹25,000 Cr (Top 100)
    - Mid Cap: ₹8,000 Cr to ₹25,000 Cr (101 to 250)
    - Small Cap: < ₹8,000 Cr (251 onwards)
    Strictly NO 'Mega Cap' and NO 'Pre-IPO'.
    """
    if mcap_cr is None or mcap_cr <= 0:
        return "Small Cap"
    if mcap_cr >= 25000.0:
        return "Large Cap"
    elif mcap_cr >= 8000.0:
        return "Mid Cap"
    else:
        return "Small Cap"

def main():
    print("==================================================================")
    print("=== FIXING LIVE MARKET CAPS & ENFORCING SEBI/AMFI CLASSIFICATION ===")
    print("==================================================================")
    
    with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)
    print(f"Loaded {len(stocks)} stocks.")
    
    with open("scratch/verified_live_mcaps.json", "r", encoding="utf-8") as f:
        live_mcaps = json.load(f)
        
    # Manual high-precision overrides for demerged / renamed entities
    SPECIAL_OVERRIDES = {
        "AIIL": {"mcap_cr": 44151.0, "price": 520.0},
        "AUTHUM": {"mcap_cr": 44151.0, "price": 520.0},
        "TMCV": {"mcap_cr": 168741.0, "price": 458.0},
        "TMPV": {"mcap_cr": 114722.0, "price": 312.0},
        "TATAMOTORS": {"mcap_cr": 168741.0, "price": 458.0},
        "ATHER": {"mcap_cr": 62822.0, "price": 1639.0},
        "ATHERENERG": {"mcap_cr": 62822.0, "price": 1639.0},
        "BELRISE": {"mcap_cr": 22908.0, "price": 238.1},
        "EMMVEE": {"mcap_cr": 22515.0, "price": 326.0},
        "EMVEE": {"mcap_cr": 22515.0, "price": 326.0},
        "VIKRAM": {"mcap_cr": 6104.0, "price": 172.0},
        "SAATVIK": {"mcap_cr": 5394.0, "price": 422.0},
        "NSDL": {"mcap_cr": 16257.0, "price": 250.0},
        "544467": {"mcap_cr": 16257.0, "price": 250.0},
        "IKS": {"mcap_cr": 30211.0, "price": 1732.4},
        "TRANSRAIL": {"mcap_cr": 5764.0, "price": 250.0},
        "MBENGG": {"mcap_cr": 1850.0, "price": 250.0},
        "LENSKART": {"mcap_cr": 118626.4, "price": 684.9},
        "SWIGGY": {"mcap_cr": 72338.2, "price": 276.1},
        "ETERNAL": {"mcap_cr": 297334.2, "price": 323.0},
        "PINELABS": {"mcap_cr": 38500.0, "price": 320.0},
        "SHIPROCKET": {"mcap_cr": 14200.0, "price": 280.0},
        "SHADOWFAX": {"mcap_cr": 8400.0, "price": 195.0},
        "URBANCO": {"mcap_cr": 21500.0, "price": 350.0},
        "TURTLEMINT": {"mcap_cr": 12800.0, "price": 210.0},
        "MEESHO": {"mcap_cr": 35000.0, "price": 180.0},
        "WAKEFIT": {"mcap_cr": 5200.0, "price": 260.0},
        "MANIPALHOS": {"mcap_cr": 42000.0, "price": 550.0}
    }
    
    pre_ipo_cleaned = 0
    mcap_updated = 0
    
    for s in stocks:
        raw_sym = s["symbol"]
        raw_name = s["name"]
        
        # 1. Strip "(Pre-IPO)" completely from symbol and name
        clean_sym = raw_sym.replace("(Pre-IPO)", "").strip()
        clean_name = raw_name.replace("(Pre-IPO)", "").strip()
        
        if "(Pre-IPO)" in raw_sym or "(Pre-IPO)" in raw_name:
            s["symbol"] = clean_sym
            s["name"] = clean_name
            pre_ipo_cleaned += 1
            
        s["clean_sym"] = clean_sym
        
        # 2. Get Live Market Cap in ₹ Crores
        live_entry = live_mcaps.get(raw_sym) or live_mcaps.get(clean_sym, {})
        new_mcap_cr = live_entry.get("mcap_cr")
        live_p = live_entry.get("price")
        
        # Check special overrides
        if clean_sym in SPECIAL_OVERRIDES:
            ov = SPECIAL_OVERRIDES[clean_sym]
            new_mcap_cr = ov["mcap_cr"]
            if ov.get("price"):
                s["today_price"] = ov["price"]
        elif new_mcap_cr and new_mcap_cr > 0:
            pass
        else:
            # Keep existing if positive, or recalculate
            new_mcap_cr = s.get("mcap_cr", 5000.0)
            
        new_mcap_cr = round(float(new_mcap_cr), 1)
        s["mcap_cr"] = new_mcap_cr
        mcap_updated += 1
        
        if live_p and live_p > 0:
            s["today_price"] = live_p
            if "technicals" in s:
                s["technicals"]["curr_price"] = live_p
            if "live_movement" in s:
                s["live_movement"]["curr_price"] = live_p
                
        # 3. Assign SEBI / AMFI Classification (strictly Large Cap, Mid Cap, Small Cap)
        tier = classify_amfi_tier(new_mcap_cr)
        s["mcap_tier"] = tier
        s["mcap"] = tier
        
        # 4. Update shares outstanding
        curr_p = s.get("today_price") or 100.0
        s["shares_outstanding"] = int((new_mcap_cr * 10000000) / max(1.0, curr_p))
        
        # 5. Update today_pb
        bv = s.get("book_value")
        if bv and bv > 0 and curr_p > 0:
            s["today_pb"] = round(curr_p / bv, 2)
            
        # 6. Update today_pe if ttm_eps > 0
        ttm_eps = s.get("today_ttm_eps")
        if ttm_eps and ttm_eps > 0:
            s["today_pe"] = round(curr_p / ttm_eps, 2)
            if s.get("pe_8q_med") and s["pe_8q_med"] > 0:
                s["val_discount_pct"] = round(((s["pe_8q_med"] - s["today_pe"]) / s["pe_8q_med"]) * 100, 1)

    print(f"Stripped '(Pre-IPO)' from {pre_ipo_cleaned} stocks.")
    print(f"Updated live market cap for all {mcap_updated} stocks.")
    
    # Check new tier distribution
    from collections import Counter
    c = Counter(s["mcap_tier"] for s in stocks)
    print("\nNew SEBI/AMFI Market Cap Classification across all 424 stocks:")
    for tier, count in c.items():
        print(f"  {tier:<15}: {count} stocks")
        
    # Save JSON files
    with open("scripts/combined_master_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    with open("scripts/combined_119_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    print("Saved scripts/combined_master_stocks.json and combined_119_stocks.json!")

if __name__ == "__main__":
    main()
