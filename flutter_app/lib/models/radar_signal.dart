class RadarSignal {
  final String id;
  final String symbol;
  final String name;
  final String horizon;
  final double entryPrice;
  double currentPrice;
  double maxPrice;
  double minPrice;
  final double stopLoss;
  final double target1;
  final double target2;
  final double target3;
  final double rrRatio;
  final double winRateScore;
  String status;
  double pnlPct;
  final String triggeredAt;
  String? closedAt;
  double? exitPrice;
  final String notes;

  RadarSignal({
    required this.id,
    required this.symbol,
    required this.name,
    required this.horizon,
    required this.entryPrice,
    required this.currentPrice,
    required this.maxPrice,
    required this.minPrice,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.target3,
    required this.rrRatio,
    required this.winRateScore,
    required this.status,
    required this.pnlPct,
    required this.triggeredAt,
    this.closedAt,
    this.exitPrice,
    required this.notes,
  });

  factory RadarSignal.fromJson(Map<String, dynamic> json) {
    return RadarSignal(
      id: json['id']?.toString() ?? '',
      symbol: json['symbol']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      horizon: json['horizon']?.toString() ?? 'SWING',
      entryPrice: (json['entry_price'] as num?)?.toDouble() ?? 0.0,
      currentPrice: (json['current_price'] as num?)?.toDouble() ?? 0.0,
      maxPrice: (json['max_price'] as num?)?.toDouble() ?? 0.0,
      minPrice: (json['min_price'] as num?)?.toDouble() ?? 0.0,
      stopLoss: (json['stop_loss'] as num?)?.toDouble() ?? 0.0,
      target1: (json['target_1'] as num?)?.toDouble() ?? 0.0,
      target2: (json['target_2'] as num?)?.toDouble() ?? 0.0,
      target3: (json['target_3'] as num?)?.toDouble() ?? 0.0,
      rrRatio: (json['rr_ratio'] as num?)?.toDouble() ?? 2.2,
      winRateScore: (json['win_rate_score'] as num?)?.toDouble() ?? 85.0,
      status: json['status']?.toString() ?? 'RUNNING',
      pnlPct: (json['pnl_pct'] as num?)?.toDouble() ?? 0.0,
      triggeredAt: json['triggered_at']?.toString() ?? '',
      closedAt: json['closed_at']?.toString(),
      exitPrice: (json['exit_price'] as num?)?.toDouble(),
      notes: json['notes']?.toString() ?? '',
    );
  }
}

class HistoricalSuggestion {
  final String id;
  final String symbol;
  final String name;
  final String signalType;
  final double triggerCmp;
  final String triggerDate;
  final String triggerTime;
  final double winRateScore;
  final double rrRatio;
  final double stopLoss;
  final double target1;
  final double target2;
  final String status;
  double currentCmp;
  final double highestCmp;
  double pnlPct;
  final String notes;

  HistoricalSuggestion({
    required this.id,
    required this.symbol,
    required this.name,
    required this.signalType,
    required this.triggerCmp,
    required this.triggerDate,
    required this.triggerTime,
    required this.winRateScore,
    required this.rrRatio,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.status,
    required this.currentCmp,
    required this.highestCmp,
    required this.pnlPct,
    required this.notes,
  });

  factory HistoricalSuggestion.fromJson(Map<String, dynamic> json) {
    return HistoricalSuggestion(
      id: json['id']?.toString() ?? '',
      symbol: json['symbol']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      signalType: json['signal_type']?.toString() ?? 'SWING',
      triggerCmp: (json['trigger_cmp'] as num?)?.toDouble() ?? 0.0,
      triggerDate: json['trigger_date']?.toString() ?? '',
      triggerTime: json['trigger_time']?.toString() ?? '',
      winRateScore: (json['win_rate_score'] as num?)?.toDouble() ?? 85.0,
      rrRatio: (json['rr_ratio'] as num?)?.toDouble() ?? 2.2,
      stopLoss: (json['stop_loss'] as num?)?.toDouble() ?? 0.0,
      target1: (json['target_1'] as num?)?.toDouble() ?? 0.0,
      target2: (json['target_2'] as num?)?.toDouble() ?? 0.0,
      status: json['status']?.toString() ?? 'RUNNING',
      currentCmp: (json['current_cmp'] as num?)?.toDouble() ?? 0.0,
      highestCmp: (json['highest_cmp'] as num?)?.toDouble() ?? 0.0,
      pnlPct: (json['pnl_pct'] as num?)?.toDouble() ?? 0.0,
      notes: json['notes']?.toString() ?? '',
    );
  }
}
