class CandleData {
  final String date;
  final double open;
  final double high;
  final double low;
  final double close;
  final int volume;

  CandleData({
    required this.date,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.volume,
  });

  factory CandleData.fromJson(Map<String, dynamic> json) {
    return CandleData(
      date: json['date']?.toString() ?? '',
      open: (json['open'] as num?)?.toDouble() ?? 0.0,
      high: (json['high'] as num?)?.toDouble() ?? 0.0,
      low: (json['low'] as num?)?.toDouble() ?? 0.0,
      close: (json['close'] as num?)?.toDouble() ?? 0.0,
      volume: (json['volume'] as num?)?.toInt() ?? 0,
    );
  }
}

class QuarterData {
  final String quarter;
  final double revenue;
  final double? yoyRev;
  final double pat;
  final double? yoyPat;
  final double op;
  final double opm;
  final double eps;
  final double ttmEps;
  final double pe;
  final String annDate;
  final double? qoqRev;
  final double? qoqPat;
  final double? effectivePrice;

  QuarterData({
    required this.quarter,
    required this.revenue,
    this.yoyRev,
    required this.pat,
    this.yoyPat,
    required this.op,
    required this.opm,
    required this.eps,
    required this.ttmEps,
    required this.pe,
    required this.annDate,
    this.qoqRev,
    this.qoqPat,
    this.effectivePrice,
  });

  factory QuarterData.fromJson(Map<String, dynamic> json) {
    return QuarterData(
      quarter: json['Quarter']?.toString() ?? '',
      revenue: (json['Revenue'] as num?)?.toDouble() ?? 0.0,
      yoyRev: (json['YoY_Rev'] as num?)?.toDouble(),
      pat: (json['PAT'] as num?)?.toDouble() ?? 0.0,
      yoyPat: (json['YoY_PAT'] as num?)?.toDouble(),
      op: (json['OP'] as num?)?.toDouble() ?? 0.0,
      opm: (json['OPM'] as num?)?.toDouble() ?? 0.0,
      eps: (json['EPS'] as num?)?.toDouble() ?? 0.0,
      ttmEps: (json['TTM_EPS'] as num?)?.toDouble() ?? 0.0,
      pe: (json['PE'] as num?)?.toDouble() ?? 0.0,
      annDate: json['Ann_Date']?.toString() ?? '',
      qoqRev: (json['QoQ_Rev'] as num?)?.toDouble(),
      qoqPat: (json['QoQ_PAT'] as num?)?.toDouble(),
      effectivePrice: (json['Effective_Price'] as num?)?.toDouble(),
    );
  }
}

class AnalystReport {
  final String firm;
  final String rating;
  final String date;
  final double targetPrice;
  final double upsidePct;
  final String rationale;

  AnalystReport({
    required this.firm,
    required this.rating,
    required this.date,
    required this.targetPrice,
    required this.upsidePct,
    required this.rationale,
  });

  factory AnalystReport.fromJson(Map<String, dynamic> json) {
    return AnalystReport(
      firm: json['firm']?.toString() ?? 'Research Desk',
      rating: json['rating']?.toString() ?? 'Buy',
      date: json['date']?.toString() ?? '',
      targetPrice: (json['target_price'] as num?)?.toDouble() ?? 0.0,
      upsidePct: (json['upside_pct'] as num?)?.toDouble() ?? 0.0,
      rationale: json['rationale']?.toString() ?? '',
    );
  }
}

class ForecastData {
  final double meanTarget;
  final double medianTarget;
  final double highTarget;
  final double lowTarget;
  final double upsideMeanPct;
  final double upsideHighPct;
  final double downsideLowPct;
  final int numAnalysts;
  final String consensusRating;
  final double buyPct;
  final double outperformPct;
  final double holdPct;
  final double sellPct;
  final double forecastScore;
  final List<AnalystReport> reports;

  ForecastData({
    required this.meanTarget,
    required this.medianTarget,
    required this.highTarget,
    required this.lowTarget,
    required this.upsideMeanPct,
    required this.upsideHighPct,
    required this.downsideLowPct,
    required this.numAnalysts,
    required this.consensusRating,
    required this.buyPct,
    required this.outperformPct,
    required this.holdPct,
    required this.sellPct,
    required this.forecastScore,
    required this.reports,
  });

  factory ForecastData.fromJson(Map<String, dynamic> json) {
    final b = json['breakdown'] as Map<String, dynamic>? ?? {};
    final repList = (json['analyst_reports'] as List<dynamic>?)
            ?.map((r) => AnalystReport.fromJson(r as Map<String, dynamic>))
            .toList() ??
        [];

    return ForecastData(
      meanTarget: (json['mean_target'] as num?)?.toDouble() ?? 0.0,
      medianTarget: (json['median_target'] as num?)?.toDouble() ?? 0.0,
      highTarget: (json['high_target'] as num?)?.toDouble() ?? 0.0,
      lowTarget: (json['low_target'] as num?)?.toDouble() ?? 0.0,
      upsideMeanPct: (json['upside_mean_pct'] as num?)?.toDouble() ?? 0.0,
      upsideHighPct: (json['upside_high_pct'] as num?)?.toDouble() ?? 0.0,
      downsideLowPct: (json['downside_low_pct'] as num?)?.toDouble() ?? 0.0,
      numAnalysts: (json['num_analysts'] as num?)?.toInt() ?? 0,
      consensusRating: json['consensus_rating']?.toString() ?? 'Hold',
      buyPct: (b['buy_pct'] as num?)?.toDouble() ?? 0.0,
      outperformPct: (b['outperform_pct'] as num?)?.toDouble() ?? 0.0,
      holdPct: (b['hold_pct'] as num?)?.toDouble() ?? 0.0,
      sellPct: (b['sell_pct'] as num?)?.toDouble() ?? 0.0,
      forecastScore: (json['forecast_score'] as num?)?.toDouble() ?? 70.0,
      reports: repList,
    );
  }
}

class EtPrimeData {
  final String companyId;
  final String seoName;
  final int stockScore;
  final String scoreOutlook;
  final int earningsScore;
  final int fundamentalScore;
  final int rvScore;
  final int riskScore;
  final int momentumScore;
  final String pdfLink;

  EtPrimeData({
    required this.companyId,
    required this.seoName,
    required this.stockScore,
    required this.scoreOutlook,
    required this.earningsScore,
    required this.fundamentalScore,
    required this.rvScore,
    required this.riskScore,
    required this.momentumScore,
    required this.pdfLink,
  });

  factory EtPrimeData.fromJson(Map<String, dynamic> json) {
    return EtPrimeData(
      companyId: json['company_id']?.toString() ?? '',
      seoName: json['seo_name']?.toString() ?? '',
      stockScore: (json['stock_score'] as num?)?.toInt() ?? 5,
      scoreOutlook: json['score_outlook']?.toString() ?? 'NEUTRAL',
      earningsScore: (json['earnings_score'] as num?)?.toInt() ?? 5,
      fundamentalScore: (json['fundamental_score'] as num?)?.toInt() ?? 5,
      rvScore: (json['rv_score'] as num?)?.toInt() ?? 5,
      riskScore: (json['risk_score'] as num?)?.toInt() ?? 5,
      momentumScore: (json['momentum_score'] as num?)?.toInt() ?? 5,
      pdfLink: json['pdf_link']?.toString() ?? '',
    );
  }
}

class TimeframeItem {
  final String timeframe;
  final String trend;
  final double rsi;
  final String macd;
  final double support;
  final double resistance;
  final String setup;
  final String verdict;

  TimeframeItem({
    required this.timeframe,
    required this.trend,
    required this.rsi,
    required this.macd,
    required this.support,
    required this.resistance,
    required this.setup,
    required this.verdict,
  });

  factory TimeframeItem.fromJson(Map<String, dynamic> json) {
    return TimeframeItem(
      timeframe: json['timeframe']?.toString() ?? 'Daily (1D)',
      trend: json['trend']?.toString() ?? 'Neutral',
      rsi: (json['rsi'] as num?)?.toDouble() ?? 50.0,
      macd: json['macd']?.toString() ?? 'Neutral',
      support: (json['support'] as num?)?.toDouble() ?? 0.0,
      resistance: (json['resistance'] as num?)?.toDouble() ?? 0.0,
      setup: json['setup']?.toString() ?? 'Consolidation',
      verdict: json['verdict']?.toString() ?? 'HOLD',
    );
  }
}

class Stock {
  final String symbol;
  final String name;
  final String sector;
  final String mcapTier;
  double cmp;
  double prevClose;
  double dayChange;
  double dayChangePct;
  double chg5mPct;
  double dayHigh;
  double dayLow;
  int volume;
  int avgVol20d;
  double volRatio;
  String volStatus;
  double techScore;
  String action;
  String actionBadge;
  String setupType;
  String pattern;
  double high52w;
  double low52w;
  double dist52wHigh;
  double dist52wLow;
  double confluenceScore;
  double todayPe;
  double todayPb;
  double todayPeg;
  double pegGrowthRate;
  double bookValue;
  double sharesOutstanding;
  double mcapCr;
  double stopLoss;
  double target1;
  double target2;
  double target3;
  double rrRatio;
  double winRateScore;
  double rsi;
  String macdSignal;
  double macdHist;
  double stochK;
  double stochD;
  double adx;
  String adxStrength;
  String maAlignment;
  double ema9;
  double ema20;
  double ema50;
  double sma200;
  double distSma200;
  bool isGoldenCross;
  double atr14;
  double atrPct;
  double bbUpper;
  double bbMid;
  double bbLower;
  double bbBandwidth;
  double pivot;
  double r1;
  double r2;
  double r3;
  double s1;
  double s2;
  double s3;
  double fib23;
  double fib38;
  double fib50;
  double fib61;
  double fib161;
  double masterScore;
  String masterCategory;
  int masterRank;
  double triFactorScore;
  String triFactorCategory;
  double forecastScore;
  double moodScore;
  String investorMood;
  String consensus;
  double valDiscountPct;
  double pe8qMed;
  double pe8qAvg;
  double pe8qMin;
  double pe8qMax;
  int streakRev;
  int streakPat;
  String latestQuarter;
  double latestRev;
  double latestPat;
  double latestOpm;
  double? latestQoqRev;
  double? latestQoqPat;
  double? latestYoyRev;
  double? latestYoyPat;
  double weekChangePct;
  double monthChangePct;
  int rank;
  String subIndustry;
  String macroSector;
  double fundaScore;
  List<CandleData> candles;
  List<TimeframeItem> timeframes;
  List<QuarterData> quartersHistory;
  ForecastData? forecast;
  EtPrimeData? etPrime;
  List<String> summaryBullets;
  bool isBucket;

  Stock({
    required this.symbol,
    required this.name,
    required this.sector,
    required this.mcapTier,
    required this.cmp,
    required this.prevClose,
    required this.dayChange,
    required this.dayChangePct,
    this.chg5mPct = 0.0,
    required this.dayHigh,
    required this.dayLow,
    required this.volume,
    this.avgVol20d = 100000,
    required this.volRatio,
    this.volStatus = 'Normal',
    required this.techScore,
    required this.action,
    this.actionBadge = 'BUY ON DIPS',
    required this.setupType,
    required this.pattern,
    required this.high52w,
    required this.low52w,
    this.dist52wHigh = 0.0,
    this.dist52wLow = 0.0,
    this.confluenceScore = 80.0,
    required this.todayPe,
    required this.todayPb,
    this.todayPeg = 1.2,
    this.pegGrowthRate = 15.0,
    this.bookValue = 100.0,
    this.sharesOutstanding = 10.0,
    required this.mcapCr,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.target3,
    required this.rrRatio,
    required this.winRateScore,
    required this.rsi,
    required this.macdSignal,
    this.macdHist = 0.0,
    this.stochK = 60.0,
    this.stochD = 58.0,
    required this.adx,
    this.adxStrength = 'Moderate Trend',
    required this.maAlignment,
    this.ema9 = 0.0,
    required this.ema20,
    this.ema50 = 0.0,
    required this.sma200,
    this.distSma200 = 0.0,
    this.isGoldenCross = true,
    this.atr14 = 10.0,
    this.atrPct = 2.0,
    this.bbUpper = 0.0,
    this.bbMid = 0.0,
    this.bbLower = 0.0,
    this.bbBandwidth = 10.0,
    required this.pivot,
    required this.r1,
    this.r2 = 0.0,
    this.r3 = 0.0,
    required this.s1,
    this.s2 = 0.0,
    this.s3 = 0.0,
    this.fib23 = 0.0,
    this.fib38 = 0.0,
    this.fib50 = 0.0,
    this.fib61 = 0.0,
    this.fib161 = 0.0,
    required this.masterScore,
    required this.masterCategory,
    this.masterRank = 1,
    this.triFactorScore = 80.0,
    this.triFactorCategory = 'High Conviction',
    this.forecastScore = 75.0,
    this.moodScore = 80.0,
    required this.investorMood,
    required this.consensus,
    this.valDiscountPct = 0.0,
    this.pe8qMed = 25.0,
    this.pe8qAvg = 25.0,
    this.pe8qMin = 15.0,
    this.pe8qMax = 35.0,
    this.streakRev = 3,
    this.streakPat = 3,
    this.latestQuarter = 'Dec 2024',
    this.latestRev = 1000.0,
    this.latestPat = 100.0,
    this.latestOpm = 15.0,
    this.latestQoqRev,
    this.latestQoqPat,
    this.latestYoyRev,
    this.latestYoyPat,
    this.weekChangePct = 0.0,
    this.monthChangePct = 0.0,
    this.rank = 1,
    this.subIndustry = '',
    this.macroSector = '',
    this.fundaScore = 75.0,
    required this.candles,
    this.timeframes = const [],
    this.quartersHistory = const [],
    this.forecast,
    this.etPrime,
    this.summaryBullets = const [],
    this.isBucket = false,
  });

  static double _toDouble(dynamic val, [double fallback = 0.0]) {
    if (val == null) return fallback;
    if (val is num) return val.toDouble();
    if (val is String) {
      return double.tryParse(val) ?? fallback;
    }
    return fallback;
  }

  static double? _toDoubleOrNull(dynamic val) {
    if (val == null) return null;
    if (val is num) return val.toDouble();
    if (val is String) {
      return double.tryParse(val);
    }
    return null;
  }

  static int _toInt(dynamic val, [int fallback = 0]) {
    if (val == null) return fallback;
    if (val is num) return val.toInt();
    if (val is String) {
      return int.tryParse(val) ?? fallback;
    }
    return fallback;
  }

  factory Stock.fromJson(Map<String, dynamic> json) {
    final tb = json['trade_blueprint'] is Map ? Map<String, dynamic>.from(json['trade_blueprint'] as Map) : <String, dynamic>{};
    final osc = json['oscillators'] is Map ? Map<String, dynamic>.from(json['oscillators'] as Map) : <String, dynamic>{};
    final ma = json['moving_averages'] is Map ? Map<String, dynamic>.from(json['moving_averages'] as Map) : <String, dynamic>{};
    final vol = json['volatility'] is Map ? Map<String, dynamic>.from(json['volatility'] as Map) : <String, dynamic>{};
    final piv = json['pivots'] is Map ? Map<String, dynamic>.from(json['pivots'] as Map) : <String, dynamic>{};
    final fib = json['fibonacci'] is Map ? Map<String, dynamic>.from(json['fibonacci'] as Map) : <String, dynamic>{};
    final conf = json['confluence'] is Map ? Map<String, dynamic>.from(json['confluence'] as Map) : <String, dynamic>{};

    final List<CandleData> candleList = [];
    final rawCandles = json['candles'];
    if (rawCandles is List) {
      for (var c in rawCandles) {
        if (c is Map) {
          candleList.add(CandleData.fromJson(Map<String, dynamic>.from(c)));
        }
      }
    }

    final List<TimeframeItem> tfList = [];
    final rawTf = json['timeframes'];
    if (rawTf is Map) {
      rawTf.forEach((k, v) {
        if (v is Map) {
          final m = Map<String, dynamic>.from(v);
          m.putIfAbsent('timeframe', () => k.toString());
          tfList.add(TimeframeItem.fromJson(m));
        }
      });
    } else if (rawTf is List) {
      for (var t in rawTf) {
        if (t is Map) {
          tfList.add(TimeframeItem.fromJson(Map<String, dynamic>.from(t)));
        }
      }
    }

    final List<QuarterData> qhList = [];
    final rawQh = json['quarters_history'];
    if (rawQh is List) {
      for (var q in rawQh) {
        if (q is Map) {
          qhList.add(QuarterData.fromJson(Map<String, dynamic>.from(q)));
        }
      }
    }

    ForecastData? fc;
    if (json['forecast'] != null && json['forecast'] is Map) {
      fc = ForecastData.fromJson(Map<String, dynamic>.from(json['forecast'] as Map));
    }

    EtPrimeData? et;
    if (json['et_prime'] != null && json['et_prime'] is Map) {
      et = EtPrimeData.fromJson(Map<String, dynamic>.from(json['et_prime'] as Map));
    }

    final List<String> bullets = [];
    final rawBullets = json['summary_bullets'];
    if (rawBullets is List) {
      bullets.addAll(rawBullets.map((b) => b.toString()));
    }

    final price = _toDouble(json['cmp'] ?? json['today_price'], 100.0);
    final pClose = _toDouble(json['prev_close'], price);
    final chg = _toDouble(json['day_change'], price - pClose);
    final chgPct = _toDouble(json['day_change_pct'], pClose > 0 ? ((chg / pClose) * 100) : 0.0);

    return Stock(
      symbol: json['symbol']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      sector: json['sector']?.toString() ?? 'Diversified',
      mcapTier: json['mcap_tier']?.toString() ?? 'Mid Cap',
      cmp: price,
      prevClose: pClose,
      dayChange: chg,
      dayChangePct: chgPct,
      chg5mPct: _toDouble(json['chg_5m_pct'], 0.0),
      dayHigh: _toDouble(json['day_high'], price * 1.01),
      dayLow: _toDouble(json['day_low'], price * 0.99),
      volume: _toInt(json['volume'], 100000),
      avgVol20d: _toInt(json['avg_vol_20d'], 100000),
      volRatio: _toDouble(json['vol_ratio'], 1.0),
      volStatus: json['vol_status']?.toString() ?? 'Active Inflow',
      techScore: _toDouble(json['tech_score'], 75.0),
      action: json['action']?.toString() ?? 'BUY ON DIPS',
      actionBadge: json['action_badge']?.toString() ?? (json['action']?.toString() ?? 'BUY ON DIPS'),
      setupType: json['setup_type']?.toString() ?? 'Stage 2 Momentum',
      pattern: json['primary_pattern']?.toString() ?? 'Consolidation Breakout',
      high52w: _toDouble(json['high_52w'], price * 1.15),
      low52w: _toDouble(json['low_52w'], price * 0.75),
      dist52wHigh: _toDouble(json['dist_52w_high'], -10.0),
      dist52wLow: _toDouble(json['dist_52w_low'], 25.0),
      confluenceScore: _toDouble(conf['confluence_score'], 82.0),
      todayPe: _toDouble(json['today_pe'], 25.0),
      todayPb: _toDouble(json['today_pb'], 3.0),
      todayPeg: _toDouble(json['today_peg'], 1.2),
      pegGrowthRate: _toDouble(json['peg_growth_rate'], 18.0),
      bookValue: _toDouble(json['book_value'], 100.0),
      sharesOutstanding: _toDouble(json['shares_outstanding'], 10.0),
      mcapCr: _toDouble(json['mcap_cr'], 5000.0),
      stopLoss: _toDouble(tb['stop_loss'], price * 0.95),
      target1: _toDouble(tb['target_1'], price * 1.05),
      target2: _toDouble(tb['target_2'], price * 1.09),
      target3: _toDouble(tb['target_3'], price * 1.14),
      rrRatio: _toDouble(tb['rr_ratio'], 2.2),
      winRateScore: _toDouble(tb['win_rate_score'], 85.0),
      rsi: _toDouble(osc['rsi'], 55.0),
      macdSignal: osc['macd_signal']?.toString() ?? 'Bullish',
      macdHist: _toDouble(osc['macd_hist'], 1.2),
      stochK: _toDouble(osc['stoch_k'], 62.0),
      stochD: _toDouble(osc['stoch_d'], 58.0),
      adx: _toDouble(osc['adx'], 25.0),
      adxStrength: osc['adx_trend']?.toString() ?? 'Strong Trend',
      maAlignment: ma['alignment']?.toString() ?? 'Bullish Alignment',
      ema9: _toDouble(ma['ema9'], price),
      ema20: _toDouble(ma['ema20'], price),
      ema50: _toDouble(ma['ema50'], price * 0.98),
      sma200: _toDouble(ma['sma200'], price * 0.92),
      distSma200: _toDouble(ma['dist_sma200_pct'], 8.5),
      isGoldenCross: ma['golden_cross'] == true || (ma['alignment']?.toString().contains('Bullish') ?? true),
      atr14: _toDouble(vol['atr14'], price * 0.025),
      atrPct: _toDouble(vol['atr_pct'], 2.5),
      bbUpper: _toDouble(vol['bb_upper'], price * 1.05),
      bbMid: _toDouble(vol['bb_mid'], price),
      bbLower: _toDouble(vol['bb_lower'], price * 0.95),
      bbBandwidth: _toDouble(vol['bb_bandwidth'], 10.0),
      pivot: _toDouble(piv['pivot'], price),
      r1: _toDouble(piv['r1'], price * 1.02),
      r2: _toDouble(piv['r2'], price * 1.04),
      r3: _toDouble(piv['r3'], price * 1.07),
      s1: _toDouble(piv['s1'], price * 0.98),
      s2: _toDouble(piv['s2'], price * 0.96),
      s3: _toDouble(piv['s3'], price * 0.93),
      fib23: _toDouble(fib['fib_236'], price * 1.02),
      fib38: _toDouble(fib['fib_382'], price * 1.04),
      fib50: _toDouble(fib['fib_500'], price * 1.05),
      fib61: _toDouble(fib['fib_618'], price * 1.06),
      fib161: _toDouble(fib['fib_1618'], price * 1.15),
      masterScore: _toDouble(json['master_score'], 80.0),
      masterCategory: json['master_category']?.toString() ?? 'Master Alpha',
      masterRank: _toInt(json['master_rank'], 1),
      triFactorScore: _toDouble(json['tri_factor_score'], 80.0),
      triFactorCategory: json['tri_factor_category']?.toString() ?? 'High Conviction',
      forecastScore: _toDouble(json['forecast_score'], 75.0),
      moodScore: _toDouble(json['mood_score'], 80.0),
      investorMood: json['investor_mood']?.toString() ?? 'Bullish Accumulation',
      consensus: json['consensus']?.toString() ?? 'Buy',
      valDiscountPct: _toDouble(json['val_discount_pct'], 0.0),
      pe8qMed: _toDouble(json['pe_8q_med'], 25.0),
      pe8qAvg: _toDouble(json['pe_8q_avg'], 25.0),
      pe8qMin: _toDouble(json['pe_8q_min'], 15.0),
      pe8qMax: _toDouble(json['pe_8q_max'], 35.0),
      streakRev: _toInt(json['streak_rev'], 3),
      streakPat: _toInt(json['streak_pat'], 3),
      latestQuarter: json['latest_quarter']?.toString() ?? 'Dec 2024',
      latestRev: _toDouble(json['latest_rev'], 1000.0),
      latestPat: _toDouble(json['latest_pat'], 100.0),
      latestOpm: _toDouble(json['latest_opm'], 15.0),
      latestQoqRev: _toDoubleOrNull(json['latest_qoq_rev']),
      latestQoqPat: _toDoubleOrNull(json['latest_qoq_pat']),
      latestYoyRev: _toDoubleOrNull(json['latest_yoy_rev']),
      latestYoyPat: _toDoubleOrNull(json['latest_yoy_pat']),
      weekChangePct: _toDouble(json['week_change_pct'], 0.0),
      monthChangePct: _toDouble(json['month_change_pct'], 0.0),
      rank: _toInt(json['rank'], 1),
      subIndustry: json['sub_industry']?.toString() ?? '',
      macroSector: json['macro_sector']?.toString() ?? '',
      fundaScore: _toDouble(json['score'], 75.0),
      candles: candleList,
      timeframes: tfList,
      quartersHistory: qhList,
      forecast: fc,
      etPrime: et,
      summaryBullets: bullets,
    );
  }

  /// Hydrate / merge fundamental data from html_424_stocks.json
  void mergeFundamentalData(Map<String, dynamic> f) {
    if (f['quarters_history'] != null && f['quarters_history'] is List) {
      quartersHistory = (f['quarters_history'] as List<dynamic>)
          .map((q) => QuarterData.fromJson(q as Map<String, dynamic>))
          .toList();
    }
    if (f['forecast'] != null && f['forecast'] is Map<String, dynamic>) {
      forecast = ForecastData.fromJson(f['forecast'] as Map<String, dynamic>);
    }
    if (f['et_prime'] != null && f['et_prime'] is Map<String, dynamic>) {
      etPrime = EtPrimeData.fromJson(f['et_prime'] as Map<String, dynamic>);
    }
    if (f['val_discount_pct'] != null) {
      valDiscountPct = (f['val_discount_pct'] as num).toDouble();
    }
    if (f['pe_8q_med'] != null) pe8qMed = (f['pe_8q_med'] as num).toDouble();
    if (f['pe_8q_avg'] != null) pe8qAvg = (f['pe_8q_avg'] as num).toDouble();
    if (f['pe_8q_min'] != null) pe8qMin = (f['pe_8q_min'] as num).toDouble();
    if (f['pe_8q_max'] != null) pe8qMax = (f['pe_8q_max'] as num).toDouble();
    if (f['streak_rev'] != null) streakRev = (f['streak_rev'] as num).toInt();
    if (f['streak_pat'] != null) streakPat = (f['streak_pat'] as num).toInt();
    if (f['latest_quarter'] != null) latestQuarter = f['latest_quarter'].toString();
    if (f['latest_rev'] != null) latestRev = (f['latest_rev'] as num).toDouble();
    if (f['latest_pat'] != null) latestPat = (f['latest_pat'] as num).toDouble();
    if (f['latest_opm'] != null) latestOpm = (f['latest_opm'] as num).toDouble();
    if (f['latest_qoq_rev'] != null) latestQoqRev = (f['latest_qoq_rev'] as num).toDouble();
    if (f['latest_qoq_pat'] != null) latestQoqPat = (f['latest_qoq_pat'] as num).toDouble();
    if (f['latest_yoy_rev'] != null) latestYoyRev = (f['latest_yoy_rev'] as num).toDouble();
    if (f['latest_yoy_pat'] != null) latestYoyPat = (f['latest_yoy_pat'] as num).toDouble();
    if (f['week_change_pct'] != null) weekChangePct = (f['week_change_pct'] as num).toDouble();
    if (f['month_change_pct'] != null) monthChangePct = (f['month_change_pct'] as num).toDouble();
    if (f['sub_industry'] != null) subIndustry = f['sub_industry'].toString();
    if (f['macro_sector'] != null) macroSector = f['macro_sector'].toString();
    if (f['book_value'] != null) bookValue = (f['book_value'] as num).toDouble();
    if (f['today_peg'] != null) todayPeg = (f['today_peg'] as num).toDouble();
    if (f['peg_growth_rate'] != null) pegGrowthRate = (f['peg_growth_rate'] as num).toDouble();
    if (f['shares_outstanding'] != null) sharesOutstanding = (f['shares_outstanding'] as num).toDouble();
    if (f['rank'] != null) rank = (f['rank'] as num).toInt();
    if (f['score'] != null) fundaScore = (f['score'] as num).toDouble();
    if (f['tri_factor_score'] != null) triFactorScore = (f['tri_factor_score'] as num).toDouble();
    if (f['tri_factor_category'] != null) triFactorCategory = f['tri_factor_category'].toString();
    if (f['forecast_score'] != null) forecastScore = (f['forecast_score'] as num).toDouble();
    if (f['master_score'] != null) masterScore = (f['master_score'] as num).toDouble();
    if (f['master_category'] != null) masterCategory = f['master_category'].toString();
    if (f['master_rank'] != null) masterRank = (f['master_rank'] as num).toInt();
  }
}
