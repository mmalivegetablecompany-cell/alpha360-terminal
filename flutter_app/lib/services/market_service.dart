import 'dart:convert';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/stock.dart';
import '../models/news_item.dart';
import '../models/corporate_order.dart';

class MarketService {
  static const String defaultLocalServerUrl = 'http://127.0.0.1:8765';
  static const String defaultEmulatorServerUrl = 'http://10.0.2.2:8765';

  String _serverUrl = defaultLocalServerUrl;

  String get serverUrl => _serverUrl;

  MarketService() {
    _initServerUrl();
  }

  Future<void> _initServerUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final saved = prefs.getString('custom_server_url');
      if (saved != null && saved.trim().isNotEmpty) {
        _serverUrl = saved.trim();
      } else {
        // Auto-detect Android emulator vs Desktop/Web
        if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
          _serverUrl = defaultEmulatorServerUrl;
        } else {
          _serverUrl = defaultLocalServerUrl;
        }
      }
    } catch (_) {
      _serverUrl = defaultLocalServerUrl;
    }
  }

  Future<void> setServerUrl(String url) async {
    _serverUrl = url.trim();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('custom_server_url', _serverUrl);
    } catch (_) {}
  }

  /// Test server connectivity and measure round-trip latency in milliseconds.
  Future<int?> testConnection([String? testUrl]) async {
    final target = (testUrl ?? _serverUrl).trim().replaceAll(RegExp(r'/+$'), '');
    final stopwatch = Stopwatch()..start();
    try {
      final resp = await http.get(Uri.parse('$target/api/health')).timeout(const Duration(seconds: 3));
      stopwatch.stop();
      if (resp.statusCode == 200) {
        return stopwatch.elapsedMilliseconds;
      }
    } catch (_) {}
    return null;
  }

  // 1. Load Initial Bundled Stocks & Merge Technical + Fundamental
  Future<List<Stock>> loadInitialStocks() async {
    // A. Try server API /api/stocks first
    try {
      final resp = await http.get(Uri.parse('$_serverUrl/api/stocks')).timeout(const Duration(seconds: 4));
      if (resp.statusCode == 200) {
        final dynamic data = json.decode(resp.body);
        if (data is Map) {
          final dynamic rawTech = data['technicals'];
          final dynamic rawFund = data['fundamentals'];
          final List<dynamic> techList = rawTech is List ? rawTech : [];
          final List<dynamic> fundList = rawFund is List ? rawFund : [];
        if (techList.isNotEmpty) {
          final fundMap = <String, Map<String, dynamic>>{};
          for (var item in fundList) {
            if (item is Map<String, dynamic>) {
              final sym = item['symbol']?.toString() ?? '';
              final name = item['name']?.toString() ?? '';
              fundMap['${sym}_$name'] = item;
              fundMap.putIfAbsent(sym, () => item);
            }
          }
          return techList.map((item) {
            final s = Stock.fromJson(item as Map<String, dynamic>);
            final fund = fundMap['${s.symbol}_${s.name}'] ?? fundMap[s.symbol];
            if (fund != null) {
              s.mergeFundamentalData(fund);
            }
            return s;
          }).toList();
        }
      }
    }
  } catch (_) {}

    // B. Fallback to bundled asset files
    try {
      String techStr = '';
      try {
        techStr = await rootBundle.loadString('assets/advanced_technicals_424.json');
      } catch (_) {
        try {
          techStr = await rootBundle.loadString('advanced_technicals_424.json');
        } catch (_) {}
      }

      String fundStr = '';
      try {
        fundStr = await rootBundle.loadString('assets/html_424_stocks.json');
      } catch (_) {
        try {
          fundStr = await rootBundle.loadString('html_424_stocks.json');
        } catch (_) {}
      }

      if (techStr.isNotEmpty && !techStr.trim().startsWith('<')) {
        if (kIsWeb) {
          return _parseAndHydrateStocks({'tech': techStr, 'fund': fundStr});
        } else {
          return await compute(_parseAndHydrateStocks, {'tech': techStr, 'fund': fundStr});
        }
      }
    } catch (e) {
      debugPrint('Error loading initial stocks: $e');
    }
    return [];
  }

  // 2. Load Radar Database (Active & Historical)
  Future<Map<String, dynamic>> loadRadarDatabase() async {
    try {
      final resp = await http.get(Uri.parse('$_serverUrl/api/radar/database')).timeout(const Duration(seconds: 2));
      if (resp.statusCode == 200) {
        return json.decode(resp.body) as Map<String, dynamic>;
      }
    } catch (_) {}

    try {
      final jsonStr = await rootBundle.loadString('assets/radar_signals_database.json');
      return json.decode(jsonStr) as Map<String, dynamic>;
    } catch (e) {
      return {'active_signals': [], 'historical_suggestions': [], 'completed_journal': []};
    }
  }

  // 3. Load News Articles
  Future<List<NewsItem>> loadNews() async {
    try {
      final resp = await http.get(Uri.parse('$_serverUrl/api/news')).timeout(const Duration(seconds: 2));
      if (resp.statusCode == 200) {
        final list = json.decode(resp.body) as List<dynamic>;
        return list.map((item) => NewsItem.fromJson(item as Map<String, dynamic>)).toList();
      }
    } catch (_) {}

    try {
      final jsonStr = await rootBundle.loadString('assets/stock_news.json');
      final list = json.decode(jsonStr) as List<dynamic>;
      return list.map((item) => NewsItem.fromJson(item as Map<String, dynamic>)).toList();
    } catch (e) {
      return [];
    }
  }

  // 4. Load Corporate Orders
  Future<List<CorporateOrder>> loadCorporateOrders() async {
    try {
      final resp = await http.get(Uri.parse('$_serverUrl/api/orders')).timeout(const Duration(seconds: 2));
      if (resp.statusCode == 200) {
        final list = json.decode(resp.body) as List<dynamic>;
        return list.map((item) => CorporateOrder.fromJson(item as Map<String, dynamic>)).toList();
      }
    } catch (_) {}

    try {
      final jsonStr = await rootBundle.loadString('assets/corporate_orders.json');
      final list = json.decode(jsonStr) as List<dynamic>;
      return list.map((item) => CorporateOrder.fromJson(item as Map<String, dynamic>)).toList();
    } catch (e) {
      return [];
    }
  }

  // 5. Fetch Live Real-Time Quotes (Poll)
  Future<Map<String, dynamic>?> fetchLiveQuotes() async {
    try {
      final resp = await http.get(Uri.parse('$_serverUrl/api/quotes')).timeout(const Duration(seconds: 2));
      if (resp.statusCode == 200) {
        final data = json.decode(resp.body) as Map<String, dynamic>;
        if (data['status'] == 'ok' && data['quotes'] != null) {
          return data['quotes'] as Map<String, dynamic>;
        }
      }
    } catch (_) {}
    return null;
  }

  // 6. Track Stock via Server
  Future<bool> trackStockOnServer(String symbol, String horizon, String notes, {String? tradeId}) async {
    try {
      final payload = {
        'symbol': symbol,
        'horizon': horizon,
        'notes': notes,
        if (tradeId != null) 'id': tradeId,
      };
      final resp = await http.post(
        Uri.parse('$_serverUrl/api/radar/track'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(payload),
      ).timeout(const Duration(seconds: 3));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 7. Close Active Trade via Server (Fixed API payload contract)
  Future<bool> closeTradeOnServer(
    String symbol,
    String exitReason, {
    String? tradeId,
    double? exitPrice,
  }) async {
    try {
      final payload = {
        'symbol': symbol,
        'trade_id': tradeId ?? symbol,
        'reason': exitReason,
        'exit_reason': exitReason,
        if (exitPrice != null && exitPrice > 0) 'exit_price': exitPrice,
      };
      final resp = await http.post(
        Uri.parse('$_serverUrl/api/radar/close'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(payload),
      ).timeout(const Duration(seconds: 3));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 8. Server-Sent Events (SSE) Live Quotes Stream
  Stream<Map<String, dynamic>> streamQuotes() async* {
    while (true) {
      http.Client client = http.Client();
      try {
        final request = http.Request('GET', Uri.parse('$_serverUrl/api/stream/quotes'));
        request.headers['Accept'] = 'text/event-stream';
        final response = await client.send(request);

        if (response.statusCode == 200) {
          await for (final line in response.stream.transform(utf8.decoder).transform(const LineSplitter())) {
            if (line.startsWith('data:')) {
              final jsonStr = line.substring(5).trim();
              if (jsonStr.isNotEmpty) {
                try {
                  final data = json.decode(jsonStr) as Map<String, dynamic>;
                  if (data['quotes'] != null) {
                    yield data['quotes'] as Map<String, dynamic>;
                  }
                } catch (_) {}
              }
            }
          }
        }
      } catch (_) {
        // Backoff and reconnect on network glitch
        await Future.delayed(const Duration(seconds: 5));
      } finally {
        client.close();
      }
    }
  }
}

/// Worker isolate top-level parser for large bundled datasets
List<Stock> _parseAndHydrateStocks(Map<String, String> inputs) {
  final techStr = inputs['tech'] ?? '';
  final fundStr = inputs['fund'] ?? '';

  if (techStr.isEmpty) return [];

  final decodedTech = json.decode(techStr);
  final List<dynamic> techList;
  if (decodedTech is List) {
    techList = decodedTech;
  } else if (decodedTech is Map && decodedTech['stocks'] is List) {
    techList = decodedTech['stocks'] as List<dynamic>;
  } else if (decodedTech is Map && decodedTech['technicals'] is List) {
    techList = decodedTech['technicals'] as List<dynamic>;
  } else if (decodedTech is Map) {
    techList = decodedTech.values.whereType<Map<String, dynamic>>().toList();
  } else {
    return [];
  }

  final stocks = techList.map((item) => Stock.fromJson(item as Map<String, dynamic>)).toList();

  if (fundStr.isNotEmpty) {
    try {
      final decodedFund = json.decode(fundStr);
      final List<dynamic> fundList;
      if (decodedFund is List) {
        fundList = decodedFund;
      } else if (decodedFund is Map && decodedFund['stocks'] is List) {
        fundList = decodedFund['stocks'] as List<dynamic>;
      } else if (decodedFund is Map && decodedFund['fundamentals'] is List) {
        fundList = decodedFund['fundamentals'] as List<dynamic>;
      } else if (decodedFund is Map) {
        fundList = decodedFund.values.whereType<Map<String, dynamic>>().toList();
      } else {
        fundList = [];
      }

      final fundMap = <String, Map<String, dynamic>>{};
      for (var item in fundList) {
        if (item is Map<String, dynamic>) {
          final sym = item['symbol']?.toString() ?? '';
          final name = item['name']?.toString() ?? '';
          fundMap['${sym}_$name'] = item;
          fundMap.putIfAbsent(sym, () => item);
        }
      }

      for (var s in stocks) {
        final f = fundMap['${s.symbol}_${s.name}'] ?? fundMap[s.symbol];
        if (f != null) {
          s.mergeFundamentalData(f);
        }
      }
    } catch (_) {}
  }

  return stocks;
}
