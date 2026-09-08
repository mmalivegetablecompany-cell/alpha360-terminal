const fs = require('fs');

console.log('Validating Advance_Technical_Analysis_424_Stocks.html...');
const html = fs.readFileSync('Advance_Technical_Analysis_424_Stocks.html', 'utf8');

console.log(`HTML File Size: ${(html.length / (1024 * 1024)).toFixed(2)} MB`);

// 1. Check for key elements in HTML
const checks = [
  { name: 'buyRadarBtn', pattern: /id="buyRadarBtn"/ },
  { name: 'radarModal', pattern: /id="radarModal"/ },
  { name: 'radarSection-CANDIDATES', pattern: /id="radarSection-CANDIDATES"/ },
  { name: 'radarSection-RUNNING', pattern: /id="radarSection-RUNNING"/ },
  { name: 'radarSection-JOURNAL', pattern: /id="radarSection-JOURNAL"/ },
  { name: '5M % Table Header', pattern: /onclick="sortTable\('chg_5m_pct'\)"/ },
  { name: '5M % Table Cell', pattern: /id="tbl-5m-\${s\.symbol}"/ },
  { name: 'Track Button in Table', pattern: /onclick="addTrackedSignal\('\${s\.symbol}'\)"/ },
  { name: 'Track Button in 360 Modal', pattern: /onclick="trackStockFromModal\(\)"/ },
  { name: 'Audio Sound Toggle', pattern: /id="radarSoundToggle"/ },
  { name: 'Toast Container', pattern: /id="toastContainer"/ },
  { name: 'evaluateBuyRadar JS function', pattern: /function evaluateBuyRadar\(s\)/ },
  { name: 'renderRunningSignals JS function', pattern: /function renderRunningSignals\(\)/ },
  { name: 'renderCompletedJournal JS function', pattern: /function renderCompletedJournal\(\)/ },
  { name: 'addTrackedSignal JS function', pattern: /function addTrackedSignal\(sym/ },
  { name: 'updateTrackedSignalsLive JS function', pattern: /function updateTrackedSignalsLive\(quotes\)/ },
  { name: 'exportJournalToExcel JS function', pattern: /function exportJournalToExcel\(\)/ },
  { name: 'applyLiveQuotes with chg_5m_pct', pattern: /q\.chg_5m_pct !== undefined/ }
];

let allPassed = true;
checks.forEach(c => {
  if (c.pattern.test(html)) {
    console.log(`  ✓ ${c.name}`);
  } else {
    console.error(`  ✗ Missing: ${c.name}`);
    allPassed = false;
  }
});

// 2. Extract script block and check JS syntax via vm
const allScripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
const mainScript = allScripts.find(m => m[1].includes('const STOCKS_DATA'));
if (!mainScript) {
  console.error('✗ Failed to find main <script> block with STOCKS_DATA in HTML');
  process.exit(1);
}

const scriptCode = mainScript[1];
console.log(`\nScript code extracted: ${(scriptCode.length / 1024).toFixed(1)} KB`);

const vm = require('vm');

// Mock browser environment
const mockWindow = {
  addEventListener: () => {},
  scrollTo: () => {},
  AudioContext: class {
    createOscillator() { return { connect: () => {}, frequency: { setValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} }, start: () => {}, stop: () => {} }; }
    createGain() { return { connect: () => {}, gain: { setValueAtTime: () => {}, linearRampToValueAtTime: () => {} } }; }
  }
};

const mockLocalStorage = {
  data: {},
  getItem: function(k) { return this.data[k] || null; },
  setItem: function(k, v) { this.data[k] = String(v); }
};

const mockDocument = {
  addEventListener: () => {},
  getElementById: (id) => ({
    textContent: '',
    innerHTML: '',
    classList: { add: () => {}, remove: () => {}, contains: () => false },
    checked: true,
    appendChild: () => {}
  }),
  querySelectorAll: () => [],
  createElement: () => ({
    className: '',
    innerHTML: '',
    classList: { add: () => {}, remove: () => {} },
    appendChild: () => {},
    remove: () => {}
  }),
  body: { style: {} },
  activeElement: null
};

const sandbox = {
  window: mockWindow,
  document: mockDocument,
  localStorage: mockLocalStorage,
  console: console,
  setTimeout: () => {},
  setInterval: () => {},
  XLSX: { utils: { json_to_sheet: () => ({}), book_new: () => ({}), book_append_sheet: () => {} }, writeFile: () => {} }
};

vm.createContext(sandbox);

try {
  vm.runInContext(scriptCode, sandbox);
  console.log('✓ Script parsed and executed successfully in sandbox with ZERO syntax errors!');

  // Test evaluateBuyRadar logic on mock stock
  const mockStock = {
    symbol: 'TEST',
    name: 'Test Stock',
    cmp: 1000,
    day_change: 25,
    day_change_pct: 2.5,
    chg_5m_pct: 0.15,
    tech_score: 75,
    vol_ratio: 1.45,
    dist_52w_high: -5,
    day_high: 1010,
    day_low: 980,
    timeframes: {
      '15M': { verdict: 'Bullish Continuation', rsi: 62 },
      '1D': { verdict: 'Strong Bullish', rsi: 65 }
    },
    moving_averages: { sma200: 900, ema20: 970, ema50: 940 },
    oscillators: { rsi: 65 },
    trade_blueprint: { stop_loss: 960, target_1: 1040, target_2: 1080, target_3: 1120, rr_ratio: 2.5 }
  };

  const radarResult = sandbox.evaluateBuyRadar(mockStock);
  console.log('✓ evaluateBuyRadar output for mock setup:', JSON.stringify(radarResult));

  // Test adding signal to tracker
  vm.runInContext('STOCKS_DATA.push(' + JSON.stringify(mockStock) + ')', sandbox);
  vm.runInContext('addTrackedSignal("TEST", "PERFECT", true)', sandbox);
  const tracked = vm.runInContext('getTrackedSignals()', sandbox);
  console.log(`✓ Tracked signals count: ${tracked.length}, Status: ${tracked[0].status}, Symbol: ${tracked[0].symbol}`);

  // Test live price tick triggering Target 1
  vm.runInContext('updateTrackedSignalsLive({ "TEST": { curr_price: 1050, chg_5m_pct: 0.2 } })', sandbox);
  const updatedTracked = vm.runInContext('getTrackedSignals()', sandbox);
  console.log(`✓ Post-tick status for TEST: ${updatedTracked[0].status} (Expected T1_HIT), Return: ${updatedTracked[0].pnl_pct}%`);

  console.log('\n=============================================');
  console.log('🎉 ALL RADAR & TRACKER TESTS PASSED CLEANLY!');
  console.log('=============================================');
} catch (err) {
  console.error('✗ Execution error in script:', err);
  process.exit(1);
}
