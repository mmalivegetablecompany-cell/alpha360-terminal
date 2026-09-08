import sys, os, json, re
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")

SECTOR_MAP = {
    # Defence & Aerospace (11)
    'Aerospace & Defence Electronics': 'Defence & Aerospace',
    'Defence & Aerospace': 'Defence & Aerospace',
    'Defence & Shipbuilding': 'Defence & Aerospace',
    'Defence Electronics': 'Defence & Aerospace',
    'Defence Simulators & Anti-Drone Systems': 'Defence & Aerospace',
    'Defence, Mining & Rail': 'Defence & Aerospace',
    'Defence, Railways & Batteries': 'Defence & Aerospace',

    # Renewable Energy & Green Power (17)
    'Renewable Energy / Solar': 'Renewable Energy & Green Power',
    'Renewable Energy / Solar EPC': 'Renewable Energy & Green Power',
    'Renewable Energy / Wind': 'Renewable Energy & Green Power',
    'Renewable Energy Pure-Play (IPP)': 'Renewable Energy & Green Power',
    'Renewable Energy / Green NBFC': 'Renewable Energy & Green Power',
    'Solar Energy & Inverter Distribution': 'Renewable Energy & Green Power',
    'Solar Turnkey EPC & EV Fleet Leasing': 'Renewable Energy & Green Power',
    'Power Generation (Thermal + Renewable)': 'Renewable Energy & Green Power',

    # Power & Electrical Equipment (8)
    'Power Equipment & Smart Meters': 'Power & Electrical Equipment',
    'Power Transmission & Equipment': 'Power & Electrical Equipment',
    'Power Transmission & Grid Automation': 'Power & Electrical Equipment',
    'Power Transmission Utility (PSU)': 'Power & Electrical Equipment',
    'Power Generation (Thermal & Solar)': 'Power & Electrical Equipment',
    'Power T&D Infrastructure & Civil EPC': 'Power & Electrical Equipment',
    'AC Generators & Electrical Machinery': 'Power & Electrical Equipment',
    'Transmission Towers & High-Mast Lighting': 'Power & Electrical Equipment',

    # Railways & Mass Transit (6)
    'Railways & Metro': 'Railways & Mass Transit',
    'Railways Finance / NBFC': 'Railways & Mass Transit',
    'Railways Infrastructure': 'Railways & Mass Transit',
    'Railway & Infrastructure EPC (PSU)': 'Railways & Mass Transit',
    'Railway Displays & Telecommunications': 'Railways & Mass Transit',
    'Telecom & Railways Tech': 'Railways & Mass Transit',

    # Automobiles & Auto Components (12)
    'Automobiles & EV': 'Automobiles & Auto Components',
    'Automobiles & Farm Equipment': 'Automobiles & Auto Components',
    'Automotive & Railway Heavy Forgings': 'Automobiles & Auto Components',
    'Automotive Components': 'Automobiles & Auto Components',
    'Two-Wheelers / Automotive': 'Automobiles & Auto Components',
    'Commercial Vehicles': 'Automobiles & Auto Components',
    'Commercial Vehicles / Auto': 'Automobiles & Auto Components',
    'Electric Buses & Auto Components': 'Automobiles & Auto Components',
    'Specialized Auto & Engine Manufacturing': 'Automobiles & Auto Components',
    'Auto Components & EV Electronics': 'Automobiles & Auto Components',

    # Banking & Financial Services (BFSI) (9)
    'Banking & Financials': 'Banking & Financial Services (BFSI)',
    'Financial Services & Holdings': 'Banking & Financial Services (BFSI)',
    'Financial Services & NBFC': 'Banking & Financial Services (BFSI)',
    'NBFC & Financial Services': 'Banking & Financial Services (BFSI)',
    'Housing & Infra Finance / NBFC': 'Banking & Financial Services (BFSI)',
    'Power Finance / NBFC': 'Banking & Financial Services (BFSI)',
    'Life Insurance Monopoly (PSU)': 'Banking & Financial Services (BFSI)',
    'Credit Rating & Analytics': 'Banking & Financial Services (BFSI)',
    'Fintech & Digital Lending': 'Banking & Financial Services (BFSI)',

    # Capital Markets & Exchanges (6)
    'Capital Markets & Broking': 'Capital Markets & Exchanges',
    'Capital Markets & Exchanges': 'Capital Markets & Exchanges',
    'Capital Markets / Depository': 'Capital Markets & Exchanges',
    'Capital Markets / Financial Services': 'Capital Markets & Exchanges',

    # IT & Cloud Technologies (5)
    'IT Services & Consulting': 'IT & Cloud Technologies',
    'IT Services & Digital Transformation': 'IT & Cloud Technologies',
    'IT Enterprise Solutions & Cloud Services': 'IT & Cloud Technologies',
    'IT Hardware & AI Systems': 'IT & Cloud Technologies',
    'IT Hardware & Cloud Software Distribution': 'IT & Cloud Technologies',

    # Consumer Electronics & EMS (3)
    'Consumer Electronics & EMS': 'Consumer Electronics & EMS',

    # Metals, Mining & Steel (11)
    'Metals & Mining / Aluminium': 'Metals, Mining & Steel',
    'Metals & Mining / Iron Ore': 'Metals, Mining & Steel',
    'Metals Recycling & Circular Economy': 'Metals, Mining & Steel',
    'Metals, Mining & Energy': 'Metals, Mining & Steel',
    'Mining, High-Grade Pellets & Power': 'Metals, Mining & Steel',
    'Non-Ferrous Metals (Aluminium & Copper)': 'Metals, Mining & Steel',
    'Iron & Steel Products / Pipes': 'Metals, Mining & Steel',
    'Mineral & Lignite Mining (PSU)': 'Metals, Mining & Steel',
    'Pre-Engineered Buildings & Structures': 'Metals, Mining & Steel',
    'Engineered Steel Products & Pre-Fab': 'Metals, Mining & Steel',

    # Oil, Gas & Petrochemicals (4)
    'Oil & Gas Exploration & Production (PSU)': 'Oil, Gas & Petrochemicals',
    'Oil Refining & Petrochemicals': 'Oil, Gas & Petrochemicals',
    'O2C, Telecom, Retail & Clean Energy': 'Oil, Gas & Petrochemicals',
    'Offshore Marine & Oilfield Services': 'Oil, Gas & Petrochemicals',

    # Infrastructure, EPC & Logistics (7)
    'Infrastructure & Construction': 'Infrastructure, EPC & Logistics',
    'Highways, Roads & Irrigation EPC': 'Infrastructure, EPC & Logistics',
    'Heavy Engineering & Capital Goods': 'Infrastructure, EPC & Logistics',
    'Industrial Conveyor Belts': 'Infrastructure, EPC & Logistics',
    'Fly Ash Handling & Green Logistics': 'Infrastructure, EPC & Logistics',
    'Infrastructure Investment Trust': 'Infrastructure, EPC & Logistics',
    'Logistics & Supply Chain': 'Infrastructure, EPC & Logistics',

    # Real Estate & Urban Development (5)
    'Real Estate Development': 'Real Estate & Urban Development',
    'Real Estate & Co-working': 'Real Estate & Urban Development',
    'Real Estate & Data Centers': 'Real Estate & Urban Development',
    'Real Estate & Agri-Business': 'Real Estate & Urban Development',

    # Pharmaceuticals & Healthcare (5)
    'Pharmaceuticals & Biotech': 'Pharmaceuticals & Healthcare',
    'Pharmaceuticals (APIs & Formulations)': 'Pharmaceuticals & Healthcare',
    'Specialty Formulations & Generics': 'Pharmaceuticals & Healthcare',
    'Healthcare & IT Services': 'Pharmaceuticals & Healthcare',

    # Consumer Retail & Apparel (5)
    'Consumer Apparel & Retail': 'Consumer Retail & Apparel',
    'Consumer Retail & Fashion': 'Consumer Retail & Apparel',
    'Consumer Retail & Jewellery': 'Consumer Retail & Apparel',
    'Consumer Electronics Retail': 'Consumer Retail & Apparel',
    'Lifestyle Apparel, Suiting & Real Estate': 'Consumer Retail & Apparel',

    # FMCG & Consumer Products (4)
    'Diversified FMCG, Hotels, Agri & Paper': 'FMCG & Consumer Products',
    'Packaged Beverages & Instant Coffee': 'FMCG & Consumer Products',
    'Paper & Forest Products': 'FMCG & Consumer Products',
    'Diversified MNC / Industrial & Healthcare': 'FMCG & Consumer Products',

    # Media & Entertainment (1)
    'Media & Entertainment': 'Media & Entertainment'
}

def update_sectors():
    json_path = "scripts/combined_119_stocks.json"
    html_path = "Stock_Growth_and_Selection_Analyzer.html"

    with open(json_path, "r", encoding="utf-8") as f:
        stocks = json.load(f)

    print(f"Loaded {len(stocks)} stocks from {json_path}")

    # 1. Update each stock in JSON
    sector_counts = {}
    for s in stocks:
        current_sec = s.get("sector")
        # if already mapped or in SECTOR_MAP
        if current_sec in SECTOR_MAP:
            s["sub_industry"] = s.get("sub_industry") or current_sec
            s["sector"] = SECTOR_MAP[current_sec]
            s["macro_sector"] = SECTOR_MAP[current_sec]
        else:
            # check if sub_industry was saved
            sub = s.get("sub_industry")
            if sub and sub in SECTOR_MAP:
                s["sector"] = SECTOR_MAP[sub]
                s["macro_sector"] = SECTOR_MAP[sub]

        m_sec = s["sector"]
        sector_counts[m_sec] = sector_counts.get(m_sec, 0) + 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stocks, f, indent=2)
    print(f"Updated {len(stocks)} stocks in {json_path} across {len(sector_counts)} macro sectors.")

    # 2. Build new <select id="sectorSelect"> options
    options_html = ['    <select id="sectorSelect" class="select-input" onchange="applyAllFilters()">']
    options_html.append(f'      <option value="all">All Sectors ({len(sector_counts)})</option>')
    for sec_name in sorted(sector_counts.keys()):
        cnt = sector_counts[sec_name]
        options_html.append(f'      <option value="{sec_name}">{sec_name} ({cnt})</option>')
    options_html.append('    </select>')
    new_select_str = "\n".join(options_html)

    # 3. Update HTML file
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Replace <select id="sectorSelect"> ... </select>
    select_pattern = re.search(r'<select id="sectorSelect"[\s\S]*?</select>', html)
    if select_pattern:
        html = html[:select_pattern.start()] + new_select_str + html[select_pattern.end():]
        print(f"Replaced sectorSelect dropdown in HTML with {len(sector_counts)} merged macro sectors.")
    else:
        print("WARNING: sectorSelect not found via regex!")

    # Replace rawData in HTML
    raw_start = html.find("const rawData = [")
    if raw_start != -1:
        raw_end = html.find("\n", raw_start)
        html = html[:raw_start] + f"const rawData = {json.dumps(stocks)};" + html[raw_end:]
        print("Updated rawData in HTML with macro-sector mapped stocks.")

    # Update renderTable in HTML to show macro-sector + sub_industry subtitle
    old_td = '<td style="color:var(--text-secondary); font-size:12px;">${s.sector}</td>'
    new_td = '<td style="font-size:12.5px;"><strong style="color:var(--text-primary); font-size:12px;">${s.sector}</strong><br><span style="color:var(--text-muted); font-size:10.5px;">${s.sub_industry || ""}</span></td>'
    if old_td in html:
        html = html.replace(old_td, new_td)
        print("Updated table rendering to display Macro-Sector and Sub-Industry.")

    # Update applyAllFilters search query to search both sector and sub_industry
    old_search = "const inSec = s.sector.toLowerCase().includes(q);"
    new_search = "const inSec = s.sector.toLowerCase().includes(q) || (s.sub_industry && s.sub_industry.toLowerCase().includes(q));"
    if old_search in html:
        html = html.replace(old_search, new_search)
        print("Updated applyAllFilters search to query both Macro-Sector and Sub-Industry.")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully saved {html_path} ({len(html)} bytes)!")

    # 4. Update Excel Workbooks with the clean macro-sector
    import update_excels
    update_excels.update_excel_workbooks(stocks)

if __name__ == "__main__":
    update_sectors()
