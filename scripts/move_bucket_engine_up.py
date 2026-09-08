import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Locate the bucket engine at the bottom of script
start_marker = "  /* ==========================================================================\n     CUSTOM STOCK BUCKET / PORTFOLIO BASKET ENGINE"
end_marker = "  updateBucketUI();\n</script>"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx != -1 and end_idx != -1:
    bucket_code = html[start_idx:end_idx]
    # Remove from bottom
    html = html[:start_idx] + "  updateBucketUI();\n" + html[end_idx:]
    print("Extracted bucket engine from bottom.")
else:
    print("ERROR: could not find bucket engine markers!")
    sys.exit(1)

# Also remove old exportFilteredCSV function if present
old_csv_fn = re.search(r'function exportFilteredCSV\(\)\s*\{[\s\S]*?link\.click\(\);\s*document\.body\.removeChild\(link\);\s*\}', html)
if old_csv_fn:
    html = html.replace(old_csv_fn.group(0), '')
    print("Removed old exportFilteredCSV function.")

# 2. Insert bucket_code right after activeStockIndex = 0;
insert_anchor = "let activeStockIndex = 0;"
if insert_anchor in html:
    html = html.replace(insert_anchor, insert_anchor + "\n\n" + bucket_code, 1)
    print("Inserted bucket engine at top right after activeStockIndex = 0.")
else:
    print("ERROR: could not find insert anchor!")
    sys.exit(1)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully relocated Bucket & Excel engine to top of script.")
