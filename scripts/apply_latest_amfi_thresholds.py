import json, re, sys, os

sys.stdout.reconfigure(encoding="utf-8")

def classify_latest_amfi(mcap_cr):
    """
    Latest Indian Market Cutoff (2026 Thresholds as specified):
    - Large Cap: >= ₹1,00,000 Cr (1 Lakh Cr)
    - Mid Cap: ₹30,000 Cr to ₹1,00,000 Cr
    - Small Cap: < ₹30,000 Cr (0 to 30,000 Cr)
    """
    if mcap_cr is None or mcap_cr <= 0:
        return "Small Cap"
    if mcap_cr >= 100000.0:
        return "Large Cap"
    elif mcap_cr >= 30000.0:
        return "Mid Cap"
    else:
        return "Small Cap"

def main():
    print("==================================================================")
    print("=== APPLYING LATEST INDIAN MARKET CAP THRESHOLDS (2026 RULE) ===")
    print("=== Large Cap: >= ₹1,00,000 Cr | Mid Cap: ₹30k-1L Cr | Small: < ₹30k Cr ===")
    print("==================================================================")
    
    with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)
    print(f"Loaded {len(stocks)} stocks.")
    
    for s in stocks:
        mcr = s.get("mcap_cr", 0.0)
        tier = classify_latest_amfi(mcr)
        s["mcap_tier"] = tier
        s["mcap"] = tier
        
    from collections import Counter
    c = Counter(s["mcap_tier"] for s in stocks)
    print(f"\nNew Breakdown:")
    print(f"  🏛️ Large Cap (>= ₹1 Lakh Cr)    : {c['Large Cap']} stocks")
    print(f"  📈 Mid Cap (₹30,000 - 1 Lakh Cr) : {c['Mid Cap']} stocks")
    print(f"  🚀 Small Cap (< ₹30,000 Cr)      : {c['Small Cap']} stocks")
    
    # Save master JSONs
    with open("scripts/combined_master_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    with open("scripts/combined_119_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    print("Saved scripts/combined_master_stocks.json and combined_119_stocks.json!")
    
    # -------------------------------------------------------------
    # Update HTML Dashboard
    # -------------------------------------------------------------
    html_path = "Stock_Growth_and_Selection_Analyzer.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # 1. Replace rawData
    start_idx = html.find("const rawData =")
    end_idx = html.find("let currentData =", start_idx)
    new_json_str = json.dumps(stocks)
    html = html[:start_idx] + "const rawData = " + new_json_str + ";\n  " + html[end_idx:]
    
    # 2. Update <select id="sf_mcap_tier">
    old_select_pattern = r'(<select id="sf_mcap_tier"[^>]*>)(.*?)(</select>)'
    new_select_content = """
            <option value="any">Any Market Cap</option>
            <option value="large">Large Cap (&ge; ₹1,00,000 Cr)</option>
            <option value="mid">Mid Cap (₹30,000 to ₹1,00,000 Cr)</option>
            <option value="small">Small Cap (&lt; ₹30,000 Cr)</option>
          """
    m = re.search(old_select_pattern, html, re.DOTALL)
    if m:
        html = html[:m.start()] + m.group(1) + new_select_content + m.group(3) + html[m.end():]
        print("Updated #sf_mcap_tier select options.")
        
    # 3. Update smartFilters.mcap_tier logic in applyAllFilters
    new_filter_logic = """      if (smartFilters.mcap_tier !== 'any') {
        const mcr = s.mcap_cr || 0;
        const mtier = s.mcap_tier || '';
        if (smartFilters.mcap_tier === 'large' && (mcr < 100000.0 && mtier !== 'Large Cap')) return false;
        if (smartFilters.mcap_tier === 'mid' && ((mcr < 30000.0 || mcr >= 100000.0) && mtier !== 'Mid Cap')) return false;
        if (smartFilters.mcap_tier === 'small' && (mcr >= 30000.0 && mtier !== 'Small Cap')) return false;
      }"""
      
    html = re.sub(
        r"if \(smartFilters\.mcap_tier !== 'any'\) \{.*?\n      \}",
        new_filter_logic.strip(),
        html,
        flags=re.DOTALL
    )
    print("Updated smartFilters.mcap_tier filtering logic in HTML.")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully saved {html_path}!")

    # -------------------------------------------------------------
    # Update all Excel Workbooks
    # -------------------------------------------------------------
    sys.path.append(os.path.abspath("scripts"))
    from update_all_excels_412 import update_all_workbooks
    update_all_workbooks()
    
    print("\nAll updates complete!")

if __name__ == "__main__":
    main()
