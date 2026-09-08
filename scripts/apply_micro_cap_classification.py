import json, re, sys, os
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

def classify_amfi_4tier(mcap_cr):
    """
    4-Tier Indian Market Cap Classification:
    - Large Cap: >= 100,000 Cr (1 Lakh Cr)
    - Mid Cap  : 30,000 Cr to 100,000 Cr
    - Small Cap: 5,000 Cr to 30,000 Cr
    - Micro Cap: < 5,000 Cr (0 to 5,000 Cr)
    """
    if mcap_cr is None or mcap_cr <= 0:
        return "Micro Cap"
    if mcap_cr >= 100000.0:
        return "Large Cap"
    elif mcap_cr >= 30000.0:
        return "Mid Cap"
    elif mcap_cr >= 5000.0:
        return "Small Cap"
    else:
        return "Micro Cap"

def main():
    print("==================================================================")
    print("=== APPLYING 4-TIER MARKET CAP CLASSIFICATION (INCL. MICRO CAP) ===")
    print("=== Micro Cap: < 5,000 Cr   | Small Cap: 5,000 - 30,000 Cr    ===")
    print("=== Mid Cap: 30,000-100,000 | Large Cap: >= 100,000 Cr        ===")
    print("==================================================================")
    
    with open("scripts/combined_master_stocks.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)
    print(f"Loaded {len(stocks)} stocks from combined_master_stocks.json.")
    
    for s in stocks:
        mcr = s.get("mcap_cr", 0.0)
        tier = classify_amfi_4tier(mcr)
        s["mcap_tier"] = tier
        s["mcap"] = tier
        
    c = Counter(s["mcap_tier"] for s in stocks)
    print(f"\nNew 4-Tier Breakdown:")
    print(f"  [Large Cap] (>= 1 Lakh Cr)      : {c['Large Cap']} stocks")
    print(f"  [Mid Cap]   (30,000 - 1 Lakh Cr): {c['Mid Cap']} stocks")
    print(f"  [Small Cap] (5,000 - 30,000 Cr) : {c['Small Cap']} stocks")
    print(f"  [Micro Cap] (< 5,000 Cr)        : {c['Micro Cap']} stocks")
    print(f"  Total                           : {sum(c.values())} stocks")
    
    # Save master JSONs
    with open("scripts/combined_master_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    with open("scripts/combined_119_stocks.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    print("Saved scripts/combined_master_stocks.json and combined_119_stocks.json successfully!")
    
    # -------------------------------------------------------------
    # Update HTML Dashboard
    # -------------------------------------------------------------
    html_path = "Stock_Growth_and_Selection_Analyzer.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # 1. Ensure CSS has .tier-micro badge
    if ".tier-micro" not in html:
        tier_small_css = """.tier-small {
    background: rgba(20, 184, 166, 0.18);
    color: #2DD4BF;
    border: 1px solid rgba(20, 184, 166, 0.35);
  }"""
        tier_micro_css = """.tier-small {
    background: rgba(20, 184, 166, 0.18);
    color: #2DD4BF;
    border: 1px solid rgba(20, 184, 166, 0.35);
  }
  .tier-micro {
    background: rgba(239, 68, 68, 0.18);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
  }"""
        if tier_small_css in html:
            html = html.replace(tier_small_css, tier_micro_css, 1)
            print("Added .tier-micro CSS badge.")
        else:
            html = html.replace(".tier-small {", ".tier-micro {\n    background: rgba(239, 68, 68, 0.18);\n    color: #F87171;\n    border: 1px solid rgba(239, 68, 68, 0.35);\n  }\n  .tier-small {", 1)
            print("Added .tier-micro CSS badge (fallback).")
    else:
        print(".tier-micro already in CSS.")

    # 2. Update <select id="sf_mcap_tier">
    old_select_pattern = r'(<select id="sf_mcap_tier"[^>]*>)(.*?)(</select>)'
    new_select_content = """
            <option value="any">Any Market Cap</option>
            <option value="large">Large Cap (&ge; ₹1,00,000 Cr)</option>
            <option value="mid">Mid Cap (₹30,000 to ₹1,00,000 Cr)</option>
            <option value="small">Small Cap (₹5,000 to ₹30,000 Cr)</option>
            <option value="micro">Micro Cap (&lt; ₹5,000 Cr)</option>
          """
    m = re.search(old_select_pattern, html, re.DOTALL)
    if m:
        html = html[:m.start()] + m.group(1) + new_select_content + m.group(3) + html[m.end():]
        print("Updated #sf_mcap_tier select options to 4 tiers.")
        
    # 3. Update smartFilters.mcap_tier logic in applyAllFilters
    new_filter_logic = """      if (smartFilters.mcap_tier !== 'any') {
        const mcr = s.mcap_cr || 0;
        const mtier = s.mcap_tier || '';
        if (smartFilters.mcap_tier === 'large' && (mcr < 100000.0 && mtier !== 'Large Cap')) return false;
        if (smartFilters.mcap_tier === 'mid' && ((mcr < 30000.0 || mcr >= 100000.0) && mtier !== 'Mid Cap')) return false;
        if (smartFilters.mcap_tier === 'small' && ((mcr < 5000.0 || mcr >= 30000.0) && mtier !== 'Small Cap')) return false;
        if (smartFilters.mcap_tier === 'micro' && (mcr >= 5000.0 && mtier !== 'Micro Cap')) return false;
      }"""
      
    html = re.sub(
        r"if \(smartFilters\.mcap_tier !== 'any'\) \{.*?\n      \}",
        new_filter_logic.strip(),
        html,
        flags=re.DOTALL
    )
    print("Updated smartFilters.mcap_tier filtering logic in HTML.")

    # 4. Update filter pill badge generator
    old_pill = "mcap_tier: (v) => `Mcap: ${v.replace(/_/g, ' ')}`,"
    new_pill = "mcap_tier: (v) => 'Mcap: ' + (v === 'large' ? 'Large Cap' : v === 'mid' ? 'Mid Cap' : v === 'small' ? 'Small Cap' : v === 'micro' ? 'Micro Cap' : v),"
    if old_pill in html:
        html = html.replace(old_pill, new_pill, 1)
        print("Updated filter pill formatting for mcap_tier.")

    # 5. Update renderTable tier badge class assignment
    old_tier_js = """      let tier = s.mcap_tier || 'Mid Cap';
      let tierClass = 'tier-mid';
      if (tier === 'Large Cap') tierClass = 'tier-large';
      else if (tier === 'Small Cap') tierClass = 'tier-small';
      else tierClass = 'tier-mid';"""
      
    new_tier_js = """      let tier = s.mcap_tier || 'Small Cap';
      let tierClass = 'tier-small';
      if (tier === 'Large Cap') tierClass = 'tier-large';
      else if (tier === 'Mid Cap') tierClass = 'tier-mid';
      else if (tier === 'Small Cap') tierClass = 'tier-small';
      else if (tier === 'Micro Cap') tierClass = 'tier-micro';"""
      
    if old_tier_js in html:
        html = html.replace(old_tier_js, new_tier_js, 1)
        print("Updated renderTable tier badge class assignment.")
    else:
        pattern = r"let tier = s\.mcap_tier.*?;.*?else tierClass = 'tier-mid';"
        if re.search(pattern, html, re.DOTALL):
            html = re.sub(pattern, new_tier_js, html, flags=re.DOTALL)
            print("Updated renderTable tier badge (via regex).")

    # 6. Replace rawData with latest stocks JSON
    start_idx = html.find("const rawData =")
    end_idx = html.find("let currentData =", start_idx)
    new_json_str = json.dumps(stocks)
    html = html[:start_idx] + "const rawData = " + new_json_str + ";\n  " + html[end_idx:]
    print("Re-embedded 424 stocks master rawData into HTML.")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully saved {html_path}!")

    # -------------------------------------------------------------
    # Update all Excel Workbooks
    # -------------------------------------------------------------
    sys.path.append(os.path.abspath("scripts"))
    from update_all_excels_412 import update_all_workbooks
    update_all_workbooks()
    
    print("\nAll 4-tier updates complete!")

if __name__ == "__main__":
    main()
