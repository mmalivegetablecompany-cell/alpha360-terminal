import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/stock.dart';
import '../models/radar_signal.dart';
import '../models/news_item.dart';
import '../models/corporate_order.dart';
import '../models/custom_basket.dart';
import '../models/watchlist_constants.dart';
import '../services/market_service.dart';
import '../services/alert_service.dart';

class MarketProvider extends ChangeNotifier {
  final MarketService _service = MarketService();

  List<Stock> _allStocks = [];
  List<Stock> _filteredStocks = [];
  List<RadarSignal> _activeSignals = [];
  List<HistoricalSuggestion> _historicalSuggestions = [];
  List<RadarSignal> _completedJournal = [];
  List<NewsItem> _news = [];
  List<CorporateOrder> _corporateOrders = [];

  // Watchlists & Custom Baskets
  Set<String> _userBucketSymbols = {};
  List<CustomBasket> _userCustomBaskets = [];
  String _activeBasket = 'ALL';

  // Strategy Presets & Screener Filters
  String _activePreset = 'ALL';
  String _selectedSector = 'All Sectors';
  String _activeMcapTier = 'ALL';
  double _minScoreSlider = 0.0;

  final Map<String, String> _smartFilters = {
    'max_pe': 'any',
    'max_pb': 'any',
    'max_peg': 'any',
    'min_pat_growth': 'any',
    'min_streak': 'any',
    'min_funda': 'any',
    'rsi_zone': 'any',
    'trend': 'any',
    'proximity_52w': 'any',
    'mcap_tier': 'any',
    'min_upside': 'any',
    'min_master': 'any',
  };

  // Sorting & Display
  String _sortBy = 'TECH_SCORE';
  String _sortColumn = 'tech_score';
  bool _isAscending = false;
  String _viewMode = 'SPLIT'; // SPLIT, TABLE, GRID
  String _tableMode = 'TECHNICAL'; // TECHNICAL, FUNDAMENTAL
  String _searchQuery = '';
  Stock? _selectedStock;
  ThemeMode _themeMode = ThemeMode.dark;
  Timer? _pollingTimer;

  bool _isLoading = true;
  bool _isLiveConnected = false;

  // Getters
  List<Stock> get stocks => _filteredStocks;
  List<Stock> get allStocks => _allStocks;
  List<RadarSignal> get activeSignals => _activeSignals;
  List<HistoricalSuggestion> get historicalSuggestions => _historicalSuggestions;
  List<RadarSignal> get completedJournal => _completedJournal;
  List<NewsItem> get news => _news;
  List<CorporateOrder> get corporateOrders => _corporateOrders;

  Set<String> get userBucketSymbols => _userBucketSymbols;
  List<CustomBasket> get userCustomBaskets => _userCustomBaskets;
  String get activeBasket => _activeBasket;
  String get activePreset => _activePreset;
  String get selectedSector => _selectedSector;
  String get activeMcapTier => _activeMcapTier;
  double get minScoreSlider => _minScoreSlider;
  Map<String, String> get smartFilters => _smartFilters;

  String get sortBy => _sortBy;
  String get sortColumn => _sortColumn;
  bool get isAscending => _isAscending;
  String get viewMode => _viewMode;
  String get tableMode => _tableMode;
  String get searchQuery => _searchQuery;
  Stock? get selectedStock => _selectedStock;
  ThemeMode get themeMode => _themeMode;
  bool get isDarkMode => _themeMode == ThemeMode.dark;
  bool get isLoading => _isLoading;
  bool get isLiveConnected => _isLiveConnected;

  String get serverUrl => _service.serverUrl;

  Future<int?> testServerConnection([String? url]) => _service.testConnection(url);

  Future<void> updateServerUrl(String url) async {
    await _service.setServerUrl(url);
    await fetchLiveTick();
  }

  int get activeSmartFiltersCount {
    int count = 0;
    _smartFilters.forEach((k, v) {
      if (v != 'any') count++;
    });
    if (_selectedSector != 'All Sectors') count++;
    if (_minScoreSlider > 0) count++;
    return count;
  }

  MarketProvider() {
    init();
  }

  Future<void> init() async {
    _isLoading = true;
    notifyListeners();

    // 0. Load Preferences & Custom Baskets
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedTheme = prefs.getString('app_theme_mode');
      if (savedTheme == 'light') {
        _themeMode = ThemeMode.light;
      } else if (savedTheme == 'system') {
        _themeMode = ThemeMode.system;
      } else {
        _themeMode = ThemeMode.dark;
      }

      final bucketList = prefs.getStringList('user_bucket_symbols') ?? [];
      _userBucketSymbols.addAll(bucketList);

      final customJson = prefs.getString('user_custom_baskets');
      if (customJson != null) {
        final decoded = json.decode(customJson) as List<dynamic>;
        final loadedBaskets = decoded.map((b) => CustomBasket.fromJson(b as Map<String, dynamic>)).toList();
        for (var b in loadedBaskets) {
          if (!_userCustomBaskets.any((existing) => existing.id == b.id)) {
            _userCustomBaskets.add(b);
          }
        }
      }
    } catch (_) {}

    // 1. Load stocks (merges technical + fundamental)
    _allStocks = await _service.loadInitialStocks();

    // Update isBucket flags
    for (var s in _allStocks) {
      s.isBucket = _userBucketSymbols.contains(s.symbol);
    }

    _applyFilters();

    // 2. Load Radar Database
    final radarDb = await _service.loadRadarDatabase();
    final rawActive = radarDb['active_signals'] as List<dynamic>? ?? [];
    _activeSignals = rawActive.map((x) => RadarSignal.fromJson(x as Map<String, dynamic>)).toList();

    final rawHist = radarDb['historical_suggestions'] as List<dynamic>? ?? [];
    _historicalSuggestions = rawHist.map((x) => HistoricalSuggestion.fromJson(x as Map<String, dynamic>)).toList();

    final rawJourn = radarDb['completed_journal'] as List<dynamic>? ?? [];
    _completedJournal = rawJourn.map((x) => RadarSignal.fromJson(x as Map<String, dynamic>)).toList();

    // 3. Load News & Corporate Orders
    _news = await _service.loadNews();
    _corporateOrders = await _service.loadCorporateOrders();

    _isLoading = false;
    notifyListeners();

    // 4. Start live price polling timer (every 4 seconds)
    _startPolling();
  }

  void _startPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(const Duration(seconds: 4), (_) => fetchLiveTick());
  }

  Future<void> fetchLiveTick() async {
    final quotes = await _service.fetchLiveQuotes();
    if (quotes != null) {
      _isLiveConnected = true;
      for (var s in _allStocks) {
        final q = quotes[s.symbol];
        if (q != null && q['curr_price'] != null) {
          final oldCmp = s.cmp;
          s.cmp = (q['curr_price'] as num).toDouble();
          s.prevClose = (q['prev_close'] as num?)?.toDouble() ?? s.prevClose;
          s.dayChange = (q['day_change'] as num?)?.toDouble() ?? (s.cmp - s.prevClose);
          s.dayChangePct = (q['day_change_pct'] as num?)?.toDouble() ?? (s.prevClose > 0 ? (s.dayChange / s.prevClose) * 100 : 0.0);
          s.chg5mPct = (q['chg_5m_pct'] as num?)?.toDouble() ?? s.chg5mPct;
          s.volume = (q['volume'] as num?)?.toInt() ?? s.volume;

          // Dynamic Indicator Recalculations on Tick
          if (s.high52w > 0) {
            if (s.cmp > s.high52w) s.high52w = s.cmp;
            s.dist52wHigh = ((s.cmp - s.high52w) / s.high52w) * 100;
          }
          if (s.low52w > 0) {
            if (s.cmp < s.low52w) s.low52w = s.cmp;
            s.dist52wLow = ((s.cmp - s.low52w) / s.low52w) * 100;
          }
          if (s.sma200 > 0) {
            s.distSma200 = ((s.cmp - s.sma200) / s.sma200) * 100;
          }
          if (s.todayPe > 0 && oldCmp > 0) {
            s.todayPe = double.parse((s.todayPe * (s.cmp / oldCmp)).toStringAsFixed(2));
          }
          // Dynamic RSI momentum shift
          final rsiDelta = s.dayChangePct * 0.3;
          s.rsi = (s.rsi + rsiDelta).clamp(15.0, 95.0);

          // Dynamic Action Badge
          if (s.techScore >= 85) {
            s.action = 'STRONG BUY';
            s.actionBadge = 'STRONG BUY';
          } else if (s.techScore >= 70) {
            s.action = 'BUY ON DIPS';
            s.actionBadge = 'BUY ON DIPS';
          } else if (s.techScore >= 50) {
            s.action = 'HOLD';
            s.actionBadge = 'HOLD';
          } else {
            s.action = 'WAIT';
            s.actionBadge = 'WAIT';
          }
        }
      }

      // Update active signals
      for (var sig in _activeSignals) {
        if (sig.status == 'RUNNING') {
          final q = quotes[sig.symbol];
          if (q != null && q['curr_price'] != null) {
            final p = (q['curr_price'] as num).toDouble();
            sig.currentPrice = p;
            sig.maxPrice = sig.maxPrice > p ? sig.maxPrice : p;
            sig.minPrice = sig.minPrice < p ? sig.minPrice : p;
            if (sig.entryPrice > 0) {
              sig.pnlPct = double.parse((((p - sig.entryPrice) / sig.entryPrice) * 100).toStringAsFixed(2));
            }
          }
        }
      }

      // Check real-time alerts
      AlertService().checkSignalsForAlerts(_activeSignals);
      AlertService().checkStocksForBreakouts(_allStocks);

      _applyFilters();
      notifyListeners();
    } else {
      if (_isLiveConnected) {
        _isLiveConnected = false;
        notifyListeners();
      }
    }
  }

  // ==================== THEME CONTROLS ====================
  Future<void> toggleTheme() async {
    _themeMode = _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('app_theme_mode', _themeMode == ThemeMode.dark ? 'dark' : 'light');
    } catch (_) {}
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    _themeMode = mode;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      String modeStr = 'system';
      if (mode == ThemeMode.dark) modeStr = 'dark';
      if (mode == ThemeMode.light) modeStr = 'light';
      await prefs.setString('app_theme_mode', modeStr);
    } catch (_) {}
  }


  // ==================== BASKET CONTROLS ====================
  bool isInBucket(String symbol) => _userBucketSymbols.contains(symbol);

  Future<void> toggleStockInBucket(String symbol) async {
    if (_userBucketSymbols.contains(symbol)) {
      _userBucketSymbols.remove(symbol);
    } else {
      _userBucketSymbols.add(symbol);
    }

    for (var s in _allStocks) {
      if (s.symbol == symbol) {
        s.isBucket = _userBucketSymbols.contains(symbol);
      }
    }

    _applyFilters();
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('user_bucket_symbols', _userBucketSymbols.toList());
    } catch (_) {}
  }

  Future<void> createCustomBasket(String name, String desc, List<String> symbols) async {
    final newId = 'custom_${DateTime.now().millisecondsSinceEpoch}';
    final basket = CustomBasket(id: newId, name: name, desc: desc, symbols: symbols);
    _userCustomBaskets.add(basket);
    _activeBasket = newId;
    _applyFilters();
    notifyListeners();
    _saveCustomBaskets();
  }

  Future<void> editCustomBasket(String id, String name, String desc, List<String> symbols) async {
    final idx = _userCustomBaskets.indexWhere((b) => b.id == id);
    if (idx != -1) {
      _userCustomBaskets[idx].name = name;
      _userCustomBaskets[idx].desc = desc;
      _userCustomBaskets[idx].symbols = symbols;
      _applyFilters();
      notifyListeners();
      _saveCustomBaskets();
    }
  }

  Future<void> deleteCustomBasket(String id) async {
    _userCustomBaskets.removeWhere((b) => b.id == id);
    if (_activeBasket == id) {
      _activeBasket = 'ALL';
    }
    _applyFilters();
    notifyListeners();
    _saveCustomBaskets();
  }

  Future<void> _saveCustomBaskets() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = _userCustomBaskets.map((b) => b.toJson()).toList();
      await prefs.setString('user_custom_baskets', json.encode(list));
    } catch (_) {}
  }

  void setBasket(String basket) {
    _activeBasket = basket;
    _applyFilters();
    notifyListeners();
  }

  // ==================== PRESET & SCREENER CONTROLS ====================
  void setActivePreset(String preset) {
    _activePreset = preset;
    _applyFilters();
    notifyListeners();
  }

  void setSelectedSector(String sector) {
    _selectedSector = sector;
    _applyFilters();
    notifyListeners();
  }

  void setMcapTier(String tier) {
    _activeMcapTier = tier;
    _applyFilters();
    notifyListeners();
  }

  void setMinScoreSlider(double val) {
    _minScoreSlider = val;
    _applyFilters();
    notifyListeners();
  }

  void setSmartFilter(String key, String value) {
    _smartFilters[key] = value;
    _applyFilters();
    notifyListeners();
  }

  void resetSmartFilters() {
    _smartFilters.forEach((k, _) {
      _smartFilters[k] = 'any';
    });
    _selectedSector = 'All Sectors';
    _activeMcapTier = 'ALL';
    _minScoreSlider = 0.0;
    _activePreset = 'ALL';
    _applyFilters();
    notifyListeners();
  }

  // ==================== SEARCH & VIEW CONTROLS ====================
  void setSearchQuery(String query) {
    _searchQuery = query;
    _applyFilters();
    notifyListeners();
  }

  void setViewMode(String mode) {
    _viewMode = mode;
    notifyListeners();
  }

  void setTableMode(String mode) {
    _tableMode = mode;
    notifyListeners();
  }

  void selectStock(Stock? stock) {
    _selectedStock = stock;
    notifyListeners();
  }

  void navigateToPreviousStock() {
    if (_filteredStocks.isEmpty || _selectedStock == null) return;
    final idx = _filteredStocks.indexWhere((s) => s.symbol == _selectedStock!.symbol);
    if (idx > 0) {
      _selectedStock = _filteredStocks[idx - 1];
      notifyListeners();
    }
  }

  void navigateToNextStock() {
    if (_filteredStocks.isEmpty || _selectedStock == null) return;
    final idx = _filteredStocks.indexWhere((s) => s.symbol == _selectedStock!.symbol);
    if (idx != -1 && idx < _filteredStocks.length - 1) {
      _selectedStock = _filteredStocks[idx + 1];
      notifyListeners();
    }
  }

  // ==================== SORTING CONTROLS ====================
  void setSortBy(String sort) {
    _sortBy = sort;
    _applyFilters();
    notifyListeners();
  }

  void sortByColumn(String column) {
    if (_sortColumn == column) {
      _isAscending = !_isAscending;
    } else {
      _sortColumn = column;
      _isAscending = false;
    }
    _applyFilters();
    notifyListeners();
  }

  // ==================== MASTER FILTERING PIPELINE ====================
  void _applyFilters() {
    List<Stock> list = List.from(_allStocks);

    // 1. Min Master Score Slider
    if (_minScoreSlider > 0) {
      list = list.where((s) => s.masterScore >= _minScoreSlider).toList();
    }

    // 2. Sector Dropdown
    if (_selectedSector != 'All Sectors') {
      list = list.where((s) => s.sector.toLowerCase() == _selectedSector.toLowerCase()).toList();
    }

    // 3. Market Cap Tier Filter (Chip)
    if (_activeMcapTier != 'ALL') {
      list = list.where((s) => s.mcapTier.toLowerCase() == _activeMcapTier.toLowerCase()).toList();
    }

    // 4. Watchlist Basket Filter
    if (_activeBasket == 'MY_BUCKET') {
      list = list.where((s) => _userBucketSymbols.contains(s.symbol)).toList();
    } else if (_activeBasket == 'STAR_STOCKS') {
      list = list.where((s) => WatchlistConstants.starStocks.contains(s.symbol)).toList();
    } else if (_activeBasket == '35_MASTER') {
      list = list.where((s) => WatchlistConstants.master35.contains(s.symbol)).toList();
    } else if (_activeBasket == 'ACTIVE_CORE') {
      list = list.where((s) => WatchlistConstants.activeCore.contains(s.symbol)).toList();
    } else if (_activeBasket == 'READY_TO_BUY') {
      list = list.where((s) => WatchlistConstants.readyToBuy.contains(s.symbol)).toList();
    } else if (_activeBasket == 'WAIT_ALERT') {
      list = list.where((s) => WatchlistConstants.waitAlert.contains(s.symbol)).toList();
    } else if (_activeBasket == 'FAVORITES') {
      list = list.where((s) => WatchlistConstants.favorites.contains(s.symbol)).toList();
    } else if (_activeBasket == 'QUARANTINE') {
      list = list.where((s) => WatchlistConstants.quarantine.contains(s.symbol)).toList();
    } else if (_activeBasket == 'ELIMINATED') {
      list = list.where((s) => WatchlistConstants.eliminated.contains(s.symbol)).toList();
    } else if (_activeBasket.startsWith('custom_')) {
      final cb = _userCustomBaskets.firstWhere((b) => b.id == _activeBasket, orElse: () => CustomBasket(id: '', name: '', symbols: []));
      final symSet = cb.symbols.toSet();
      list = list.where((s) => symSet.contains(s.symbol)).toList();
    }

    // 5. Strategy Preset Filter
    if (_activePreset != 'ALL') {
      list = list.where((s) {
        final fc = s.forecast;
        final disc = s.valDiscountPct;

        switch (_activePreset) {
          case '1D_GAINERS':
            return s.dayChangePct >= 1.5;
          case '1D_DIPS':
            return s.dayChangePct <= -1.0;
          case '1W_LEADERS':
            return s.weekChangePct >= 4.0;
          case 'MASTER_ALPHA':
            return s.masterScore >= 88.0;
          case 'TRIPLE_CROWN':
            return s.triFactorScore >= 88.0;
          case 'HIGH_FORECAST':
            return (fc?.upsideMeanPct ?? 0) >= 20.0;
          case 'MOD_FORECAST':
            final u = fc?.upsideMeanPct ?? 0;
            return u >= 10.0 && u < 20.0;
          case 'STRONG_BUY':
            final b = (fc?.buyPct ?? 0) + (fc?.outperformPct ?? 0);
            return b >= 80.0;
          case 'EUPHORIC_MOOD':
            return s.moodScore >= 90.0;
          case 'POSITIVE_MOOD':
            return s.moodScore >= 75.0 && s.moodScore < 90.0;
          case 'DIP_BUYS':
            return s.fundaScore >= 70.0 || s.rsi < 45.0;
          case 'DEEP_VALUE':
            return disc >= 20.0;
          case 'FAIR_VALUE':
            return disc >= 5.0 && disc < 20.0;
          case 'STAGE2_TREND':
            return s.setupType.contains('Stage 2') || s.pattern.contains('Stage 2') || s.maAlignment.contains('Bullish');
          case 'RSI_BULL':
            return s.rsi >= 50.0 && s.rsi <= 65.0;
          case 'RSI_OVERSOLD':
            return s.rsi < 40.0;
          case 'BREAKOUT_52W':
            return s.dist52wHigh >= -10.0;
          case 'HYPER_GROWTH':
            return (s.latestYoyPat ?? 0) >= 50.0;
          case 'PROFIT_STREAKS':
            return s.streakPat >= 3;
          case 'VOL_SURGE':
            return s.volRatio >= 1.5;
          case 'HIGH_RR':
            return s.rrRatio >= 2.5;
          case 'LARGE_QUALITY':
            return s.mcapTier.toLowerCase().contains('large');
          case 'MID_COMPOUNDERS':
            return s.mcapTier.toLowerCase().contains('mid');
          case 'SMALL_MICRO':
            return s.mcapTier.toLowerCase().contains('small') || s.mcapTier.toLowerCase().contains('micro');
          case 'INTRADAY_RADAR':
            return s.techScore >= 80.0 && s.volRatio >= 1.3;
          case 'SWING_RADAR':
            return s.techScore >= 80.0 && s.rrRatio >= 2.0;
          case 'PERFECT_RADAR':
            return s.techScore >= 85.0 && s.rrRatio >= 2.5 && s.winRateScore >= 80.0;
          default:
            return true;
        }
      }).toList();
    }

    // 6. Multi-Condition Smart Screener Filters
    if (_smartFilters['max_pe'] != 'any') {
      final limit = double.tryParse(_smartFilters['max_pe']!) ?? 999.0;
      list = list.where((s) => s.todayPe > 0 && s.todayPe <= limit).toList();
    }
    if (_smartFilters['max_pb'] != 'any') {
      final limit = double.tryParse(_smartFilters['max_pb']!) ?? 999.0;
      list = list.where((s) => s.todayPb > 0 && s.todayPb <= limit).toList();
    }
    if (_smartFilters['max_peg'] != 'any') {
      final limit = double.tryParse(_smartFilters['max_peg']!) ?? 999.0;
      list = list.where((s) => s.todayPeg > 0 && s.todayPeg <= limit).toList();
    }
    if (_smartFilters['min_pat_growth'] != 'any') {
      final limit = double.tryParse(_smartFilters['min_pat_growth']!) ?? 0.0;
      list = list.where((s) => (s.latestYoyPat ?? 0) >= limit).toList();
    }
    if (_smartFilters['min_streak'] != 'any') {
      final limit = int.tryParse(_smartFilters['min_streak']!) ?? 0;
      list = list.where((s) => s.streakPat >= limit).toList();
    }
    if (_smartFilters['min_funda'] != 'any') {
      final limit = double.tryParse(_smartFilters['min_funda']!) ?? 0.0;
      list = list.where((s) => s.fundaScore >= limit).toList();
    }
    if (_smartFilters['rsi_zone'] != 'any') {
      final zone = _smartFilters['rsi_zone'];
      if (zone == 'oversold') {
        list = list.where((s) => s.rsi < 48).toList();
      } else if (zone == 'bullish') {
        list = list.where((s) => s.rsi >= 50 && s.rsi <= 65).toList();
      } else if (zone == 'momentum') {
        list = list.where((s) => s.rsi >= 55 && s.rsi <= 72).toList();
      } else if (zone == 'extreme_oversold') {
        list = list.where((s) => s.rsi < 35).toList();
      }
    }
    if (_smartFilters['trend'] != 'any') {
      final tr = _smartFilters['trend'];
      if (tr == 'stage2') {
        list = list.where((s) => s.setupType.contains('Stage 2') || s.pattern.contains('Stage 2')).toList();
      } else if (tr == 'above_50dma') {
        list = list.where((s) => s.cmp >= s.ema50).toList();
      } else if (tr == 'above_200dma') {
        list = list.where((s) => s.cmp >= s.sma200).toList();
      }
    }
    if (_smartFilters['proximity_52w'] != 'any') {
      final prox = _smartFilters['proximity_52w'];
      if (prox == 'near_high_5') {
        list = list.where((s) => s.dist52wHigh >= -5.0).toList();
      } else if (prox == 'near_high_12') {
        list = list.where((s) => s.dist52wHigh >= -12.0).toList();
      } else if (prox == 'within_20') {
        list = list.where((s) => s.dist52wHigh >= -20.0).toList();
      } else if (prox == 'pullback_20') {
        list = list.where((s) => s.dist52wHigh < -20.0).toList();
      }
    }
    if (_smartFilters['mcap_tier'] != 'any') {
      final tier = _smartFilters['mcap_tier']!;
      list = list.where((s) => s.mcapTier.toLowerCase().contains(tier.toLowerCase())).toList();
    }
    if (_smartFilters['min_upside'] != 'any') {
      final limit = double.tryParse(_smartFilters['min_upside']!) ?? 0.0;
      list = list.where((s) => (s.forecast?.upsideMeanPct ?? 0) >= limit).toList();
    }
    if (_smartFilters['min_master'] != 'any') {
      final limit = double.tryParse(_smartFilters['min_master']!) ?? 0.0;
      list = list.where((s) => s.masterScore >= limit).toList();
    }

    // 7. Search Query
    if (_searchQuery.isNotEmpty) {
      final q = _searchQuery.toLowerCase().trim();
      list = list.where((s) {
        return s.symbol.toLowerCase().contains(q) ||
            s.name.toLowerCase().contains(q) ||
            s.sector.toLowerCase().contains(q) ||
            s.subIndustry.toLowerCase().contains(q) ||
            s.consensus.toLowerCase().contains(q);
      }).toList();
    }

    // 8. Sorting by Column or Preset Sort
    list.sort((a, b) {
      int cmp = 0;
      switch (_sortColumn) {
        case 'symbol':
          cmp = a.symbol.compareTo(b.symbol);
          break;
        case 'name':
          cmp = a.name.compareTo(b.name);
          break;
        case 'sector':
          cmp = a.sector.compareTo(b.sector);
          break;
        case 'cmp':
          cmp = a.cmp.compareTo(b.cmp);
          break;
        case 'dayChangePct':
          cmp = a.dayChangePct.compareTo(b.dayChangePct);
          break;
        case 'chg5mPct':
          cmp = a.chg5mPct.compareTo(b.chg5mPct);
          break;
        case 'tech_score':
          cmp = a.techScore.compareTo(b.techScore);
          break;
        case 'master_score':
          cmp = a.masterScore.compareTo(b.masterScore);
          break;
        case 'upside':
          final uA = a.forecast?.upsideMeanPct ?? 0;
          final uB = b.forecast?.upsideMeanPct ?? 0;
          cmp = uA.compareTo(uB);
          break;
        case 'target_price':
          final tA = a.forecast?.meanTarget ?? 0;
          final tB = b.forecast?.meanTarget ?? 0;
          cmp = tA.compareTo(tB);
          break;
        case 'todayPe':
          cmp = a.todayPe.compareTo(b.todayPe);
          break;
        case 'todayPb':
          cmp = a.todayPb.compareTo(b.todayPb);
          break;
        case 'todayPeg':
          cmp = a.todayPeg.compareTo(b.todayPeg);
          break;
        case 'mcapCr':
          cmp = a.mcapCr.compareTo(b.mcapCr);
          break;
        case 'rsi':
          cmp = a.rsi.compareTo(b.rsi);
          break;
        case 'volRatio':
          cmp = a.volRatio.compareTo(b.volRatio);
          break;
        case 'volume':
          cmp = a.volume.compareTo(b.volume);
          break;
        case 'winRateScore':
          cmp = a.winRateScore.compareTo(b.winRateScore);
          break;
        case 'rrRatio':
          cmp = a.rrRatio.compareTo(b.rrRatio);
          break;
        case 'fundaScore':
          cmp = a.fundaScore.compareTo(b.fundaScore);
          break;
        case 'valDiscount':
          cmp = a.valDiscountPct.compareTo(b.valDiscountPct);
          break;
        case 'dist52wHigh':
          cmp = a.dist52wHigh.compareTo(b.dist52wHigh);
          break;
        default:
          cmp = a.techScore.compareTo(b.techScore);
      }
      return _isAscending ? cmp : -cmp;
    });

    _filteredStocks = list;

    // Ensure selected stock is valid
    if (_selectedStock == null && _filteredStocks.isNotEmpty) {
      _selectedStock = _filteredStocks.first;
    } else if (_selectedStock != null && !_filteredStocks.any((s) => s.symbol == _selectedStock!.symbol)) {
      _selectedStock = _filteredStocks.isNotEmpty ? _filteredStocks.first : null;
    }
  }

  // ==================== RADAR CONTROLS ====================
  Future<void> addTrackedSignal(Stock stock, {String horizon = 'SWING', String notes = 'Tracked via App'}) async {
    final existing = _activeSignals.any((s) => s.symbol == stock.symbol && s.status == 'RUNNING');
    if (existing) return;

    final sig = RadarSignal(
      id: 'SIG_${DateTime.now().millisecondsSinceEpoch}_${stock.symbol}',
      symbol: stock.symbol,
      name: stock.name,
      horizon: horizon,
      entryPrice: stock.cmp,
      currentPrice: stock.cmp,
      maxPrice: stock.cmp,
      minPrice: stock.cmp,
      stopLoss: stock.stopLoss,
      target1: stock.target1,
      target2: stock.target2,
      target3: stock.target3,
      rrRatio: stock.rrRatio,
      winRateScore: stock.winRateScore,
      status: 'RUNNING',
      pnlPct: 0.0,
      triggeredAt: DateTime.now().toIso8601String(),
      notes: notes,
    );

    _activeSignals.insert(0, sig);
    notifyListeners();

    // Sync with server using exact trade ID
    _service.trackStockOnServer(stock.symbol, horizon, notes, tradeId: sig.id);
  }

  Future<void> closeActiveTrade(String symbol, String exitReason) async {
    final idx = _activeSignals.indexWhere((s) => s.symbol == symbol && s.status == 'RUNNING');
    if (idx != -1) {
      final sig = _activeSignals[idx];
      sig.status = exitReason == 'SL_HIT'
          ? 'SL_HIT'
          : (exitReason == 'TARGET_HIT' ? 'T1_HIT' : 'MANUAL_EXIT');
      sig.closedAt = DateTime.now().toIso8601String();
      sig.exitPrice = sig.currentPrice;

      _activeSignals.removeAt(idx);
      _completedJournal.insert(0, sig);
      notifyListeners();

      // Sync with server with exact trade ID and exit price
      _service.closeTradeOnServer(symbol, exitReason, tradeId: sig.id, exitPrice: sig.exitPrice);
    }
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }
}
