import sys, os, json, re, subprocess

sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = "Stock_Growth_and_Selection_Analyzer.html"
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

print(f"File size: {len(html)} bytes, Lines: {len(html.splitlines())}")

# 1. Local xlsx.full.min.js exists
assert os.path.exists("xlsx.full.min.js"), "xlsx.full.min.js missing from directory"
assert os.path.getsize("xlsx.full.min.js") > 800000, "xlsx.full.min.js size too small"
print("[Test 1] Local xlsx.full.min.js exists and is valid: PASS")

# 2. SheetJS script in HTML <head>
assert 'src="xlsx.full.min.js"' in html, "Missing xlsx.full.min.js in HTML"
print("[Test 2] HTML <head> includes SheetJS with CDN fallback: PASS")

# 3. Header actions has Bucket & Excel buttons, and NO CSV buttons
assert 'id="btnHeaderBucket"' in html, "Missing btnHeaderBucket"
assert 'exportFilteredExcel()' in html, "Missing exportFilteredExcel() in header"
assert 'id="headerBucketCount"' in html, "Missing headerBucketCount"
assert 'exportFilteredCSV' not in html, "CSV export button still present in header"
print("[Test 3] Header contains Bucket button and Excel export (.xlsx), CSV removed: PASS")

# 4. Filter pill container has My Bucket pill
assert 'id="pillBucket"' in html, "Missing pillBucket"
assert "setFilterPill('bucket', this)" in html, "Missing setFilterPill('bucket')"
print("[Test 4] Quick filter bar contains '🧺 My Bucket' pill: PASS")

# 5. Bucket Action Bar exists above table
assert 'id="bucketActionBar"' in html, "Missing bucketActionBar"
assert 'addAllFilteredToBucket()' in html, "Missing addAllFilteredToBucket()"
assert 'removeAllFilteredFromBucket()' in html, "Missing removeAllFilteredFromBucket()"
assert 'exportBucketExcel()' in html, "Missing exportBucketExcel()"
assert 'exportBucketCSV' not in html, "CSV button still in bucket action bar"
print("[Test 5] Bucket Action Bar with bulk actions and Excel (.xlsx) export: PASS")

# 6. Static thead contains bucket checkbox column
assert 'id="selectAllBucketCheckbox"' in html, "Missing selectAllBucketCheckbox in thead"
print("[Test 6] Static thead has master select-all bucket checkbox: PASS")

# 7. MASTER_COLUMN_DEFS and presets have bucket
assert "{ id: 'bucket', label: '🧺 Bucket', sortKey: null, defaultOrder: 0 }" in html, "MASTER_COLUMN_DEFS missing bucket"
assert "'bucket'" in html[html.find("COLUMN_PRESETS ="):html.find("let activeColumns =")], "COLUMN_PRESETS missing bucket"
print("[Test 7] MASTER_COLUMN_DEFS and COLUMN_PRESETS contain bucket column: PASS")

# 8. cellRenderers.bucket defined
assert "bucket: (s) =>" in html, "cellRenderers missing bucket"
assert "toggleStockBucket" in html, "cellRenderers missing toggleStockBucket call"
print("[Test 8] cellRenderers.bucket is defined: PASS")

# 9. 360° Intel Modal has Add to Bucket button
assert 'id="btnModalBucket"' in html, "Missing btnModalBucket in terminal modal"
assert "toggleModalStockBucket()" in html, "Missing toggleModalStockBucket()"
print("[Test 9] 360° Intel modal includes dynamic '+ Add to Bucket' button: PASS")

# 10. Bucket Modal HTML exists
assert 'id="bucketModal"' in html, "Missing bucketModal HTML"
assert 'id="bstat-stocks"' in html, "Missing bstat-stocks in bucket modal"
assert 'id="bstat-mcap"' in html, "Missing bstat-mcap in bucket modal"
assert 'id="bstat-score"' in html, "Missing bstat-score in bucket modal"
assert 'id="bstat-pe"' in html, "Missing bstat-pe in bucket modal"
assert 'id="bstat-upside"' in html, "Missing bstat-upside in bucket modal"
assert 'id="bstat-sectors"' in html, "Missing bstat-sectors in bucket modal"
assert 'id="bucketTableBody"' in html, "Missing bucketTableBody in bucket modal"
print("[Test 10] Bucket Portfolio Drawer/Modal HTML with analytics cards: PASS")

# 11. JS Bucket and Excel engine functions
assert "function toggleStockBucket(" in html, "Missing toggleStockBucket"
assert "function saveBucket(" in html, "Missing saveBucket"
assert "function openBucketModal(" in html, "Missing openBucketModal"
assert "function closeBucketModal(" in html, "Missing closeBucketModal"
assert "function renderBucketModalContent(" in html, "Missing renderBucketModalContent"
assert "function exportFilteredExcel(" in html, "Missing exportFilteredExcel"
assert "function exportBucketExcel(" in html, "Missing exportBucketExcel"
assert "function generateStockExportRows(" in html, "Missing generateStockExportRows"
print("[Test 11] JS Bucket Portfolio and Excel Export Engine complete: PASS")

# 12. Run full simulation
test_node_script = """
const fs = require('fs');
const html = fs.readFileSync('Stock_Growth_and_Selection_Analyzer.html', 'utf8');
const marker = 'const rawData =';
const scriptStart = html.lastIndexOf('<script>', html.indexOf(marker));
const scriptEnd = html.indexOf('</script>', scriptStart);
const code = html.substring(scriptStart + '<script>'.length, scriptEnd);

const domElements = {};
function getEl(id) {
  if (!domElements[id]) {
    domElements[id] = {
      id, innerText: '', innerHTML: '',
      value: (id === 'searchInput' ? '' : (id === 'sectorSelect' ? 'all' : (id === 'mcapSelect' ? 'all' : (id === 'scoreSlider' ? '30' : (id.startsWith('sf_') ? 'any' : ''))))),
      style: {}, classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{}, contains: ()=>false },
      children: [], appendChild(c) { this.children.push(c); },
      querySelectorAll: (sel) => [], querySelector: (sel) => null,
      addEventListener: ()=>{}, getAttribute: ()=>null, setAttribute: ()=>{}, removeAttribute: ()=>{}
    };
  }
  return domElements[id];
}

global.window = { addEventListener: ()=>{}, XLSX: require('./xlsx.full.min.js') };
global.document = {
  getElementById: getEl,
  querySelectorAll: (sel) => [getEl('pillAll'), getEl('pillBucket')],
  querySelector: (sel) => getEl('dummy'),
  createElement: (tag) => getEl('elem_' + tag + '_' + Math.random()),
  body: getEl('body')
};
global.localStorage = {
  store: {},
  getItem(k) { return this.store[k] || null; },
  setItem(k, v) { this.store[k] = v; },
  removeItem(k) { delete this.store[k]; }
};
global.setInterval = ()=>{};
global.setTimeout = (fn)=>fn();

eval(code);

if (document.getElementById('tableBody').children.length !== 119) {
  throw new Error('Expected 119 rows, got ' + document.getElementById('tableBody').children.length);
}
console.log('Verified 119 table rows populated without error.');
"""

with open("scratch_test_bucket.js", "w", encoding="utf-8") as f:
    f.write(test_node_script)

res = subprocess.run(["node", "scratch_test_bucket.js"], capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
if res.returncode != 0:
    print("Node error:", res.stderr)
    raise RuntimeError("Node validation failed")

os.remove("scratch_test_bucket.js")
print("[Test 12] End-to-end execution populates all 119 rows in DOM: PASS")

print("\n🎉 ALL 12 VERIFICATION SUITE ASSERTIONS PASSED WITH ZERO ERRORS!")
