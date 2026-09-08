import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:indian_stock_terminal/main.dart';
import 'package:indian_stock_terminal/models/stock.dart';
import 'package:indian_stock_terminal/providers/market_provider.dart';
import 'package:indian_stock_terminal/theme/app_theme.dart';
import 'package:indian_stock_terminal/widgets/sparkline_chart.dart';
import 'package:indian_stock_terminal/widgets/blueprint_slider.dart';
import 'package:indian_stock_terminal/widgets/market_breadth_bar.dart';
import 'package:indian_stock_terminal/widgets/position_sizing_dialog.dart';
import 'package:indian_stock_terminal/widgets/network_settings_dialog.dart';
import 'package:indian_stock_terminal/widgets/micro_animations.dart';
import 'package:indian_stock_terminal/services/alert_service.dart';
import 'package:indian_stock_terminal/models/radar_signal.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('Theme System Tests', () {
    test('Dark and Light themes are distinct and well-formed', () {
      expect(AppTheme.darkTheme.brightness, Brightness.dark);
      expect(AppTheme.lightTheme.brightness, Brightness.light);

      expect(AppTheme.darkBg, const Color(0xFF080D1A));
      expect(AppTheme.lightBg, const Color(0xFFF8FAFC));

      expect(AppTheme.emeraldGreen, const Color(0xFF10B981));
      expect(AppTheme.roseRed, const Color(0xFFF43F5E));
      expect(AppTheme.primaryBlue, const Color(0xFF0EA5E9));
    });

    testWidgets('AppColors resolves dynamically based on brightness', (tester) async {
      await tester.pumpWidget(
        Theme(
          data: AppTheme.darkTheme,
          child: Builder(
            builder: (context) {
              expect(AppColors.isDark(context), isTrue);
              expect(AppColors.bg(context), AppTheme.darkBg);
              expect(AppColors.surface(context), AppTheme.darkSurface);
              expect(AppColors.textPrimary(context), const Color(0xFFF8FAFC));
              return const SizedBox();
            },
          ),
        ),
      );

      await tester.pumpWidget(
        Theme(
          data: AppTheme.lightTheme,
          child: Builder(
            builder: (context) {
              expect(AppColors.isDark(context), isFalse);
              expect(AppColors.bg(context), AppTheme.lightBg);
              expect(AppColors.surface(context), AppTheme.lightSurface);
              expect(AppColors.textPrimary(context), const Color(0xFF0F172A));
              return const SizedBox();
            },
          ),
        ),
      );
    });

    test('MarketProvider toggles and manages theme correctly', () {
      final provider = MarketProvider();
      expect(provider.themeMode, ThemeMode.dark);
      expect(provider.isDarkMode, isTrue);

      provider.toggleTheme();
      expect(provider.themeMode, ThemeMode.light);
      expect(provider.isDarkMode, isFalse);

      provider.setThemeMode(ThemeMode.dark);
      expect(provider.themeMode, ThemeMode.dark);
      expect(provider.isDarkMode, isTrue);
    });
  });

  group('Stock Model Tests', () {
    test('Parses complete technical blueprint & pivots correctly', () {
      final json = {
        'symbol': 'TCS',
        'name': 'Tata Consultancy Services',
        'sector': 'Information Technology',
        'mcap_tier': 'Large Cap',
        'cmp': 3850.0,
        'prev_close': 3800.0,
        'day_change': 50.0,
        'day_change_pct': 1.32,
        'day_high': 3880.0,
        'day_low': 3790.0,
        'volume': 2500000,
        'vol_ratio': 1.45,
        'tech_score': 92.0,
        'action': 'STRONG BUY',
        'setup_type': 'Ascending Consolidation Breakout',
        'primary_pattern': 'Stage 2 Expansion',
        'high_52w': 4250.0,
        'low_52w': 3300.0,
        'today_pe': 29.5,
        'today_pb': 11.2,
        'mcap_cr': 1400000.0,
        'trade_blueprint': {
          'stop_loss': 3720.0,
          'target_1': 4020.0,
          'target_2': 4180.0,
          'target_3': 4350.0,
          'rr_ratio': 2.8,
          'win_rate_score': 94.0,
        },
        'oscillators': {
          'rsi': 64.5,
          'macd_signal': 'Strong Bullish Crossover',
          'adx': 31.0,
        },
        'moving_averages': {
          'alignment': 'Perfect Bullish Stack (9 > 20 > 50 > 200)',
          'ema20': 3810.0,
          'sma200': 3550.0,
        },
        'pivots': {
          'pivot': 3840.0,
          'r1': 3890.0,
          's1': 3800.0,
        },
        'master_score': 95.0,
        'candles': [
          {'date': '2026-09-01', 'open': 3800.0, 'high': 3840.0, 'low': 3790.0, 'close': 3830.0, 'volume': 2000000},
          {'date': '2026-09-02', 'open': 3830.0, 'high': 3860.0, 'low': 3810.0, 'close': 3850.0, 'volume': 2500000},
        ],
      };

      final stock = Stock.fromJson(json);
      expect(stock.symbol, 'TCS');
      expect(stock.cmp, 3850.0);
      expect(stock.dayChangePct, 1.32);
      expect(stock.techScore, 92.0);
      expect(stock.stopLoss, 3720.0);
      expect(stock.target1, 4020.0);
      expect(stock.target2, 4180.0);
      expect(stock.rrRatio, 2.8);
      expect(stock.winRateScore, 94.0);
      expect(stock.rsi, 64.5);
      expect(stock.macdSignal, 'Strong Bullish Crossover');
      expect(stock.maAlignment, 'Perfect Bullish Stack (9 > 20 > 50 > 200)');
      expect(stock.pivot, 3840.0);
      expect(stock.candles.length, 2);
    });
  });

  group('Custom Widgets Tests', () {
    testWidgets('SparklineChart renders with candles', (tester) async {
      final candles = [
        CandleData(date: '2026-09-01', open: 100, high: 105, low: 99, close: 102, volume: 500),
        CandleData(date: '2026-09-02', open: 102, high: 108, low: 101, close: 107, volume: 800),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SparklineChart(candles: candles, color: Colors.green),
          ),
        ),
      );

      expect(find.byType(SparklineChart), findsOneWidget);
    });

    testWidgets('BlueprintSlider renders target markers and ratios', (tester) async {
      final stock = Stock(
        symbol: 'INFY',
        name: 'Infosys Ltd',
        sector: 'IT',
        mcapTier: 'Large Cap',
        cmp: 1800.0,
        prevClose: 1780.0,
        dayChange: 20.0,
        dayChangePct: 1.12,
        dayHigh: 1810.0,
        dayLow: 1775.0,
        volume: 3000000,
        volRatio: 1.3,
        techScore: 88.0,
        action: 'STRONG BUY',
        setupType: 'Breakout',
        pattern: 'Consolidation',
        high52w: 1950.0,
        low52w: 1400.0,
        todayPe: 27.0,
        todayPb: 8.5,
        mcapCr: 750000.0,
        stopLoss: 1720.0,
        target1: 1890.0,
        target2: 1970.0,
        target3: 2050.0,
        rrRatio: 2.3,
        winRateScore: 91.0,
        rsi: 61.0,
        macdSignal: 'Bullish',
        adx: 28.0,
        maAlignment: 'Bullish Stack',
        ema20: 1770.0,
        sma200: 1620.0,
        pivot: 1790.0,
        r1: 1820.0,
        s1: 1760.0,
        masterScore: 92.0,
        masterCategory: 'Master Core',
        investorMood: 'Institutional Accumulation',
        consensus: 'Strong Buy',
        candles: [],
      );

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: BlueprintSlider(stock: stock),
          ),
        ),
      );

      expect(find.text('INSTITUTIONAL TRADE BLUEPRINT'), findsOneWidget);
      expect(find.text('R:R 1:2.3'), findsOneWidget);
      expect(find.text('₹1720.0'), findsOneWidget);
      expect(find.text('₹1890.0'), findsOneWidget);
    });

    testWidgets('MarketBreadthBar computes advances and declines accurately', (tester) async {
      final stockUp = Stock(
        symbol: 'RELIANCE',
        name: 'Reliance Industries',
        sector: 'Energy',
        mcapTier: 'Large Cap',
        cmp: 2950.0,
        prevClose: 2900.0,
        dayChange: 50.0,
        dayChangePct: 1.72,
        dayHigh: 2960.0,
        dayLow: 2890.0,
        volume: 4000000,
        volRatio: 1.5,
        techScore: 90.0,
        action: 'BUY ON DIPS',
        setupType: 'Trend Expansion',
        pattern: 'Bullish Flag',
        high52w: 3050.0,
        low52w: 2400.0,
        todayPe: 26.0,
        todayPb: 2.8,
        mcapCr: 2000000.0,
        stopLoss: 2840.0,
        target1: 3080.0,
        target2: 3190.0,
        target3: 3300.0,
        rrRatio: 2.6,
        winRateScore: 92.0,
        rsi: 62.0,
        macdSignal: 'Bullish',
        adx: 30.0,
        maAlignment: 'Bullish Stack',
        ema20: 2910.0,
        sma200: 2750.0,
        pivot: 2930.0,
        r1: 2970.0,
        s1: 2880.0,
        masterScore: 93.0,
        masterCategory: 'Master Core',
        investorMood: 'Institutional Accumulation',
        consensus: 'Buy',
        candles: [],
      );

      final stockDown = Stock(
        symbol: 'WIPRO',
        name: 'Wipro Ltd',
        sector: 'IT',
        mcapTier: 'Large Cap',
        cmp: 520.0,
        prevClose: 530.0,
        dayChange: -10.0,
        dayChangePct: -1.88,
        dayHigh: 532.0,
        dayLow: 518.0,
        volume: 1500000,
        volRatio: 0.9,
        techScore: 70.0,
        action: 'HOLD',
        setupType: 'Pullback',
        pattern: 'Consolidation',
        high52w: 580.0,
        low52w: 430.0,
        todayPe: 21.0,
        todayPb: 3.1,
        mcapCr: 270000.0,
        stopLoss: 500.0,
        target1: 550.0,
        target2: 570.0,
        target3: 590.0,
        rrRatio: 2.0,
        winRateScore: 78.0,
        rsi: 48.0,
        macdSignal: 'Neutral',
        adx: 20.0,
        maAlignment: 'Neutral',
        ema20: 525.0,
        sma200: 510.0,
        pivot: 526.0,
        r1: 535.0,
        s1: 515.0,
        masterScore: 75.0,
        masterCategory: 'Large Cap Core',
        investorMood: 'Neutral Consolidation',
        consensus: 'Hold',
        candles: [],
      );

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MarketBreadthBar(stocks: [stockUp, stockDown]),
          ),
        ),
      );

      expect(find.text('1 ADV'), findsOneWidget);
      expect(find.text('1 DEC'), findsOneWidget);
      expect(find.textContaining('RELIANCE'), findsOneWidget);
    });
  });

  testWidgets('IndianStockTerminalApp mounts with provider', (tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => MarketProvider()),
        ],
        child: const IndianStockTerminalApp(),
      ),
    );

    expect(find.byType(IndianStockTerminalApp), findsOneWidget);
  });

  group('Advanced 360° Features & Filter Engine Tests', () {
    test('Hydrates fundamental quarters, forecast, and valuation correctly', () {
      final stock = Stock(
        symbol: 'GENUSPOWER',
        name: 'Genus Power Infra',
        sector: 'Power & Electrical Equipment',
        mcapTier: 'Small Cap',
        cmp: 395.2,
        prevClose: 390.0,
        dayChange: 5.2,
        dayChangePct: 1.33,
        dayHigh: 400.0,
        dayLow: 388.0,
        volume: 500000,
        volRatio: 1.8,
        techScore: 88.0,
        action: 'STRONG BUY',
        setupType: 'RDSS Smart Meter Breakout',
        pattern: 'Stage 2 Expansion',
        high52w: 460.0,
        low52w: 210.0,
        todayPe: 22.5,
        todayPb: 4.1,
        mcapCr: 12000.0,
        stopLoss: 371.5,
        target1: 442.6,
        target2: 480.0,
        target3: 520.0,
        rrRatio: 2.5,
        winRateScore: 86.0,
        rsi: 61.5,
        macdSignal: 'Bullish',
        adx: 28.0,
        maAlignment: 'Bullish Stack',
        ema20: 388.0,
        sma200: 340.0,
        pivot: 392.0,
        r1: 405.0,
        s1: 385.0,
        masterScore: 89.5,
        masterCategory: 'Master Alpha Leader',
        investorMood: 'Euphoric Accumulation',
        consensus: 'Strong Buy',
        candles: [],
      );

      final fundamentalData = {
        'val_discount_pct': 24.5,
        'pe_8q_med': 28.0,
        'pe_8q_avg': 27.5,
        'pe_8q_min': 18.0,
        'pe_8q_max': 36.0,
        'streak_rev': 4,
        'streak_pat': 5,
        'latest_yoy_pat': 65.2,
        'latest_yoy_rev': 38.4,
        'today_peg': 0.85,
        'book_value': 96.5,
        'quarters_history': [
          {
            'Quarter': 'Dec 2024',
            'Revenue': 450.0,
            'YoY_Rev': 38.4,
            'PAT': 48.0,
            'YoY_PAT': 65.2,
            'OP': 82.0,
            'OPM': 18.2,
            'EPS': 16.5,
            'TTM_EPS': 64.0,
            'PE': 22.5,
            'Ann_Date': '2025-01-28',
          }
        ],
        'forecast': {
          'mean_target': 480.0,
          'median_target': 475.0,
          'high_target': 520.0,
          'low_target': 440.0,
          'upside_mean_pct': 21.5,
          'num_analysts': 4,
          'consensus_rating': 'Strong Buy',
          'breakdown': {
            'buy_pct': 100.0,
            'outperform_pct': 0.0,
            'hold_pct': 0.0,
            'sell_pct': 0.0,
          },
          'analyst_reports': [
            {
              'firm': 'Institutional Research',
              'rating': 'Strong Buy',
              'date': '2026-09-01',
              'target_price': 520.0,
              'upside_pct': 31.6,
              'rationale': 'Order book surge from RDSS smart metering mandate.'
            }
          ]
        },
        'et_prime': {
          'company_id': '12345',
          'seo_name': 'genus-power',
          'stock_score': 9,
          'score_outlook': 'POSITIVE',
          'earnings_score': 8,
          'fundamental_score': 9,
          'rv_score': 7,
          'risk_score': 8,
          'momentum_score': 10,
          'pdf_link': 'https://etprime.com/sample.pdf'
        }
      };

      stock.mergeFundamentalData(fundamentalData);

      expect(stock.valDiscountPct, 24.5);
      expect(stock.streakPat, 5);
      expect(stock.todayPeg, 0.85);
      expect(stock.quartersHistory.length, 1);
      expect(stock.quartersHistory.first.quarter, 'Dec 2024');
      expect(stock.quartersHistory.first.yoyPat, 65.2);
      expect(stock.forecast?.meanTarget, 480.0);
      expect(stock.forecast?.reports.length, 1);
      expect(stock.etPrime?.stockScore, 9);
      expect(stock.etPrime?.scoreOutlook, 'POSITIVE');
    });

    test('Custom Basket and Bucket management operates accurately', () async {
      final provider = MarketProvider();

      expect(provider.isInBucket('MCX'), isFalse);
      await provider.toggleStockInBucket('MCX');
      expect(provider.isInBucket('MCX'), isTrue);

      await provider.createCustomBasket('Green Power', 'Renewable picks', ['TATAPOWER', 'WAAREE']);
      expect(provider.userCustomBaskets.length, 1);
      expect(provider.userCustomBaskets.first.name, 'Green Power');
      expect(provider.userCustomBaskets.first.symbols.contains('WAAREE'), isTrue);

      final basketId = provider.userCustomBaskets.first.id;
      await provider.deleteCustomBasket(basketId);
      expect(provider.userCustomBaskets.isEmpty, isTrue);
    });

    test('Smart Screener filter state counts active filters and resets correctly', () {
      final provider = MarketProvider();
      expect(provider.activeSmartFiltersCount, 0);

      provider.setSmartFilter('max_pe', '25');
      provider.setSmartFilter('min_pat_growth', '20');
      provider.setSelectedSector('Power & Electrical Equipment');
      provider.setMinScoreSlider(80.0);

      expect(provider.activeSmartFiltersCount, 4);

      provider.resetSmartFilters();
      expect(provider.activeSmartFiltersCount, 0);
      expect(provider.selectedSector, 'All Sectors');
      expect(provider.minScoreSlider, 0.0);
    });

    test('Column sorting toggles ascending and descending', () {
      final provider = MarketProvider();
      expect(provider.sortColumn, 'tech_score');
      expect(provider.isAscending, isFalse);

      provider.sortByColumn('cmp');
      expect(provider.sortColumn, 'cmp');
      expect(provider.isAscending, isFalse);

      provider.sortByColumn('cmp');
      expect(provider.sortColumn, 'cmp');
      expect(provider.isAscending, isTrue);
    });
  });

  group('Position Sizing & Institutional Risk Calculator Tests', () {
    testWidgets('PositionSizingDialog renders calculations and order ticket accurately', (tester) async {
      final stock = Stock(
        symbol: 'GENUSPOWER',
        name: 'Genus Power Infra',
        sector: 'Power',
        mcapTier: 'Small Cap',
        cmp: 400.0,
        prevClose: 395.0,
        dayChange: 5.0,
        dayChangePct: 1.27,
        dayHigh: 405.0,
        dayLow: 392.0,
        volume: 300000,
        volRatio: 1.4,
        techScore: 90.0,
        action: 'STRONG BUY',
        setupType: 'Breakout',
        pattern: 'Consolidation',
        high52w: 450.0,
        low52w: 250.0,
        todayPe: 24.0,
        todayPb: 4.0,
        mcapCr: 12000.0,
        stopLoss: 375.0,
        target1: 440.0,
        target2: 475.0,
        target3: 510.0,
        rrRatio: 2.6,
        winRateScore: 92.0,
        rsi: 62.0,
        macdSignal: 'Bullish',
        adx: 29.0,
        maAlignment: 'Bullish Stack',
        ema20: 390.0,
        sma200: 340.0,
        pivot: 396.0,
        r1: 408.0,
        s1: 388.0,
        masterScore: 91.0,
        masterCategory: 'Tier 1 Alpha',
        investorMood: 'Accumulation',
        consensus: 'Strong Buy',
        candles: [],
      );

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: PositionSizingDialog(stock: stock),
          ),
        ),
      );

      expect(find.text('Position Sizing & Risk Model'), findsOneWidget);
      expect(find.text('TOTAL ACCOUNT CAPITAL'), findsOneWidget);
      expect(find.text('Copy Order Ticket'), findsOneWidget);
      expect(find.text('Recommended Position Size'), findsOneWidget);
    });
  });

  group('Network Gateway & Live Server Setting Tests', () {
    testWidgets('NetworkSettingsDialog renders connection presets and gateway controls', (tester) async {
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => MarketProvider()),
          ],
          child: MaterialApp(
            theme: AppTheme.darkTheme,
            home: const Scaffold(
              body: NetworkSettingsDialog(),
            ),
          ),
        ),
      );

      expect(find.text('Live Market Server Gateway'), findsOneWidget);
      expect(find.textContaining('PC Localhost'), findsOneWidget);
      expect(find.textContaining('Android Emulator'), findsOneWidget);
      expect(find.text('Save & Reconnect'), findsOneWidget);
    });
  });

  group('Alert System Tests', () {
    test('AlertService triggers real-time target hit and stop loss notifications', () async {
      final alertService = AlertService();
      alertService.clearAlertCache();

      MarketAlert? receivedAlert;
      final sub = alertService.alertStream.listen((alert) {
        receivedAlert = alert;
      });

      final signal = RadarSignal(
        id: 'TEST_SIG_1',
        symbol: 'TATAMOTORS',
        name: 'Tata Motors',
        horizon: 'SWING',
        entryPrice: 300.0,
        currentPrice: 335.0, // Target 1 is 330.0 -> Should trigger target hit
        maxPrice: 335.0,
        minPrice: 300.0,
        stopLoss: 285.0,
        target1: 330.0,
        target2: 350.0,
        target3: 370.0,
        rrRatio: 2.0,
        winRateScore: 88.0,
        status: 'RUNNING',
        pnlPct: 11.67,
        triggeredAt: DateTime.now().toIso8601String(),
        notes: 'Test',
      );

      alertService.checkSignalsForAlerts([signal]);
      await Future.delayed(const Duration(milliseconds: 50));

      expect(receivedAlert, isNotNull);
      expect(receivedAlert?.symbol, 'TATAMOTORS');
      expect(receivedAlert?.type, AlertType.targetHit);

      await sub.cancel();
    });
  });

  group('Micro-Animation System Tests', () {
    testWidgets('PriceFlashText renders initial value and updates', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: PriceFlashText(
              value: 1250.50,
              formattedText: '₹1,250.50',
            ),
          ),
        ),
      );

      expect(find.text('₹1,250.50'), findsOneWidget);

      // Re-pump with new tick value to trigger flash animation
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: PriceFlashText(
              value: 1275.00,
              formattedText: '₹1,275.00',
            ),
          ),
        ),
      );

      expect(find.text('₹1,275.00'), findsOneWidget);
      await tester.pump(const Duration(milliseconds: 200));
      await tester.pumpAndSettle();
    });

    testWidgets('PulseGlowDot mounts and animates pulse ring', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: PulseGlowDot(
              color: Color(0xFF00E676),
              size: 8.0,
              isPulsing: true,
            ),
          ),
        ),
      );

      expect(find.byType(PulseGlowDot), findsOneWidget);
      await tester.pump(const Duration(milliseconds: 400));
    });

    testWidgets('AnimatedFavoriteStar responds to tap with callback', (tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AnimatedFavoriteStar(
              isFavorite: false,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.star_outline_rounded), findsOneWidget);
      await tester.tap(find.byType(AnimatedFavoriteStar));
      await tester.pump(const Duration(milliseconds: 100));

      expect(tapped, isTrue);
      await tester.pumpAndSettle();
    });

    testWidgets('InteractiveScaleCard mounts and handles tap down and up', (tester) async {
      bool pressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: InteractiveScaleCard(
              onTap: () => pressed = true,
              child: const Text('Interactive Card Content'),
            ),
          ),
        ),
      );

      expect(find.text('Interactive Card Content'), findsOneWidget);
      await tester.tap(find.text('Interactive Card Content'));
      await tester.pumpAndSettle();

      expect(pressed, isTrue);
    });

    testWidgets('RadarScannerSweep paints circular radar sweep without error', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RadarScannerSweep(size: 40),
          ),
        ),
      );

      expect(find.byType(RadarScannerSweep), findsOneWidget);
      await tester.pump(const Duration(milliseconds: 200));
    });
  });
}

