import sys, os, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove CSV button in header-actions
html = re.sub(r'<button class="btn-export" onclick="exportFilteredCSV\(\)"[^>]*>[\s\S]*?</button>', '', html)

# 2. Remove CSV button in bucketActionBar
html = re.sub(r'<button class="btn-export-csv" onclick="exportBucketCSV\(\)"[^>]*>[\s\S]*?</button>', '', html)

# 3. Remove CSV button in bucketModal
html = re.sub(r'<button class="btn-export-csv" onclick="exportBucketCSV\(\)">[\s\S]*?</button>', '', html)

# 4. Remove any remaining btn-export-csv
html = re.sub(r'<button class="btn-export-csv"[^>]*>[\s\S]*?</button>', '', html)

# 5. Remove exportBucketCSV function from JS
html = re.sub(r'function exportBucketCSV\(\)\s*\{[\s\S]*?downloadRowsCSV\(rows,[^\}]*\}\s*', '', html)

# 6. Remove bcc / btnCsvCount update in applyAllFilters
html = re.sub(r'const bcc = document\.getElementById\(\'btnCsvCount\'\);[\s\S]*?if \(bcc\) bcc\.innerText = currentData\.length;', '', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Finished thorough removal of CSV buttons and functions.")
