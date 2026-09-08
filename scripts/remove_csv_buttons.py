import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove CSV button from header-actions
old_hdr_csv = re.search(r'<button class="btn-export"[^>]*>.*?</button>', html)
if old_hdr_csv:
    html = html.replace(old_hdr_csv.group(0), '')
    print("Removed Export CSV button from header actions.")

# 2. Remove CSV button from bucketActionBar
old_bar_csv = re.search(r'<button class="btn-export-csv"[^>]*onclick="exportBucketCSV\(\)"[^>]*>.*?</button>', html)
if old_bar_csv:
    html = html.replace(old_bar_csv.group(0), '')
    print("Removed Export Bucket (.csv) button from bucketActionBar.")

# 3. Remove CSV button from bucketModal
old_modal_csv = re.search(r'<button class="btn-export-csv"[^>]*onclick="exportBucketCSV\(\)"[^>]*>.*?</button>', html)
if old_modal_csv:
    html = html.replace(old_modal_csv.group(0), '')
    print("Removed Download CSV button from bucketModal.")

# Also check for any remaining btn-export-csv
html = re.sub(r'<button class="btn-export-csv"[^>]*>.*?</button>', '', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Finished removing CSV buttons.")
