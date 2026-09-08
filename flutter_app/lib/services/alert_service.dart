import 'dart:async';
import '../models/stock.dart';
import '../models/radar_signal.dart';

enum AlertType {
  targetHit,
  stopLossHit,
  breakout52w,
  volumeSurge,
}

class MarketAlert {
  final String id;
  final String symbol;
  final String title;
  final String message;
  final AlertType type;
  final DateTime timestamp;

  MarketAlert({
    required this.id,
    required this.symbol,
    required this.title,
    required this.message,
    required this.type,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class AlertService {
  static final AlertService _instance = AlertService._internal();
  factory AlertService() => _instance;
  AlertService._internal();

  final StreamController<MarketAlert> _controller = StreamController<MarketAlert>.broadcast();
  final Set<String> _notifiedAlertKeys = {};

  Stream<MarketAlert> get alertStream => _controller.stream;

  void checkSignalsForAlerts(List<RadarSignal> signals) {
    for (final sig in signals) {
      if (sig.status == 'RUNNING') {
        final sym = sig.symbol;
        final cmp = sig.currentPrice;

        // Check Target 1
        if (cmp >= sig.target1 && sig.target1 > 0) {
          _trigger(
            key: '${sym}_T1',
            symbol: sym,
            title: '🎯 Target 1 Reached: $sym',
            message: 'Price ₹${cmp.toStringAsFixed(2)} hit Target 1 (₹${sig.target1.toStringAsFixed(2)})! Consider partial profit booking.',
            type: AlertType.targetHit,
          );
        }

        // Check Stop Loss
        if (cmp <= sig.stopLoss && sig.stopLoss > 0) {
          _trigger(
            key: '${sym}_SL',
            symbol: sym,
            title: '🛑 Hard Stop-Loss Breached: $sym',
            message: 'Price ₹${cmp.toStringAsFixed(2)} dropped below Stop-Loss (₹${sig.stopLoss.toStringAsFixed(2)}). Capital preservation advised.',
            type: AlertType.stopLossHit,
          );
        }
      }
    }
  }

  void checkStocksForBreakouts(List<Stock> stocks) {
    for (final s in stocks) {
      if (s.dist52wHigh >= -1.0 && s.high52w > 0) {
        _trigger(
          key: '${s.symbol}_52W',
          symbol: s.symbol,
          title: '⛰️ 52-Week High Breakout: ${s.symbol}',
          message: '${s.name} is trading at ₹${s.cmp.toStringAsFixed(2)}, within 1% of its 52W High (₹${s.high52w.toStringAsFixed(2)})!',
          type: AlertType.breakout52w,
        );
      }
    }
  }

  void _trigger({
    required String key,
    required String symbol,
    required String title,
    required String message,
    required AlertType type,
  }) {
    if (_notifiedAlertKeys.contains(key)) return;
    _notifiedAlertKeys.add(key);

    _controller.add(MarketAlert(
      id: 'ALT_${DateTime.now().millisecondsSinceEpoch}_$key',
      symbol: symbol,
      title: title,
      message: message,
      type: type,
    ));
  }

  void clearAlertCache() {
    _notifiedAlertKeys.clear();
  }

  void dispose() {
    _controller.close();
  }
}
