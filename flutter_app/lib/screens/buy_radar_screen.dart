import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/market_provider.dart';
import '../models/stock.dart';
import '../models/radar_signal.dart';
import '../theme/app_theme.dart';
import '../widgets/sparkline_chart.dart';
import '../widgets/position_sizing_dialog.dart';
import '../widgets/micro_animations.dart';
import 'stock_detail_screen.dart';

class BuyRadarScreen extends StatefulWidget {
  const BuyRadarScreen({super.key});

  @override
  State<BuyRadarScreen> createState() => _BuyRadarScreenState();
}

class _BuyRadarScreenState extends State<BuyRadarScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _radarSetupFilter = 'ALL';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _copyRadarAlert(BuildContext context, Stock stock) {
    final alertText = '''
⚡ HIGH ALPHA RADAR BUY SETUP: ${stock.symbol}
🏢 Company: ${stock.name} (${stock.sector})
📊 CMP: ₹${stock.cmp.toStringAsFixed(2)}
🎯 Win-Rate: ${stock.winRateScore.toStringAsFixed(1)}% | R:R: 1:${stock.rrRatio.toStringAsFixed(1)}
🛑 Hard Stop-Loss: ₹${stock.stopLoss.toStringAsFixed(1)}
🎯 Target 1: ₹${stock.target1.toStringAsFixed(1)}
🚀 Target 2: ₹${stock.target2.toStringAsFixed(1)}
🌟 Master Alpha Score: ${stock.masterScore.toStringAsFixed(1)}/100
''';
    Clipboard.setData(ClipboardData(text: alertText));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Copied ${stock.symbol} Radar Alert to Clipboard!')),
    );
  }

  void _showCloseTradeDialog(BuildContext context, MarketProvider provider, RadarSignal sig) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.card(ctx),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.check_circle_outline_rounded, color: Colors.blue),
            const SizedBox(width: 8),
            Text('Close Trade: ${sig.symbol}', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary(ctx))),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Entry: ₹${sig.entryPrice.toStringAsFixed(2)}  •  Current: ₹${sig.currentPrice.toStringAsFixed(2)}  •  P&L: ${sig.pnlPct >= 0 ? '+' : ''}${sig.pnlPct.toStringAsFixed(2)}%',
              style: TextStyle(fontSize: 12, color: AppColors.textSecondary(ctx)),
            ),
            const SizedBox(height: 16),
            const Text('Select Exit Reason:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            _buildExitOption(ctx, provider, sig, 'TARGET_HIT', '🎯 Target Reached (Take Profit)'),
            _buildExitOption(ctx, provider, sig, 'MANUAL_EXIT', '💼 Manual Discretionary Exit'),
            _buildExitOption(ctx, provider, sig, 'SL_HIT', '🛑 Stop-Loss Breached'),
          ],
        ),
      ),
    );
  }

  Widget _buildExitOption(BuildContext ctx, MarketProvider provider, RadarSignal sig, String reasonCode, String label) {
    return ListTile(
      dense: true,
      contentPadding: EdgeInsets.zero,
      title: Text(label, style: const TextStyle(fontSize: 13)),
      trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14),
      onTap: () {
        Navigator.pop(ctx);
        provider.closeActiveTrade(sig.symbol, reasonCode);
        ScaffoldMessenger.of(ctx).showSnackBar(
          SnackBar(content: Text('Closed position for ${sig.symbol} ($label)')),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();

    return Scaffold(
      backgroundColor: AppColors.bg(context),
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(48),
        child: Container(
          color: AppColors.surface(context),
          child: TabBar(
            controller: _tabController,
            isScrollable: true,
            indicatorColor: AppColors.blue(context),
            indicatorWeight: 3,
            labelColor: AppColors.blue(context),
            unselectedLabelColor: AppColors.textSecondary(context),
            labelStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12),
            unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12),
            tabs: [
              Tab(text: '⚡ Live Radar (${provider.stocks.where((s) => s.techScore >= 80).length})'),
              Tab(text: '⏳ Active Trades (${provider.activeSignals.where((s) => s.status == "RUNNING").length})'),
              Tab(text: '📜 Historical Log (${provider.historicalSuggestions.length})'),
              Tab(text: '🏆 Trade Journal (${provider.completedJournal.length})'),
            ],
          ),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildCandidatesTab(context, provider),
          _buildRunningSignalsTab(context, provider),
          _buildHistoricalSuggestionsTab(context, provider),
          _buildJournalTab(context, provider),
        ],
      ),
    );
  }

  // ==================== TAB 1: LIVE RADAR CANDIDATES ====================
  Widget _buildCandidatesTab(BuildContext context, MarketProvider provider) {
    var candidates = provider.allStocks.where((s) => s.techScore >= 80 && s.volRatio >= 1.1).toList();

    if (_radarSetupFilter == 'INTRADAY') {
      candidates = candidates.where((s) => s.volRatio >= 1.3).toList();
    } else if (_radarSetupFilter == 'SWING') {
      candidates = candidates.where((s) => s.rrRatio >= 2.0).toList();
    } else if (_radarSetupFilter == 'PERFECT') {
      candidates = candidates.where((s) => s.techScore >= 85 && s.rrRatio >= 2.5 && s.winRateScore >= 80).toList();
    }

    candidates.sort((a, b) => b.techScore.compareTo(a.techScore));

    final isDesktop = MediaQuery.of(context).size.width >= 900;
    final trackedSyms = provider.activeSignals.where((s) => s.status == 'RUNNING').map((s) => s.symbol).toSet();

    return Column(
      children: [
        // Radar Sweep Telemetry Banner
        Container(
          margin: const EdgeInsets.fromLTRB(14, 10, 14, 4),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: AppColors.surface(context),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.border(context)),
            boxShadow: [AppColors.softShadow(context)],
          ),
          child: Row(
            children: [
              RadarScannerSweep(size: 36, beamColor: AppColors.neonGreen(context)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          'AI CONFLUENCE RADAR ACTIVE',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.5,
                            color: AppColors.neonGreen(context),
                            fontFamily: 'monospace',
                          ),
                        ),
                        const SizedBox(width: 6),
                        PulseGlowDot(color: AppColors.neonGreen(context), size: 6),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Multi-timeframe scans across 424 equities • High Win-Rate & R:R setups',
                      style: TextStyle(fontSize: 10, color: AppColors.textSecondary(context)),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.blue(context).withAlpha(25),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.blue(context).withAlpha(80), width: 0.8),
                ),
                child: Text(
                  '${candidates.length} Setups',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: AppColors.blue(context)),
                ),
              ),
            ],
          ),
        ),

        // Sub-filter chips for setups
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          color: AppColors.surface(context),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildSetupFilterChip('ALL', 'All Candidates (${provider.allStocks.where((s) => s.techScore >= 80 && s.volRatio >= 1.1).length})'),
                const SizedBox(width: 6),
                _buildSetupFilterChip('INTRADAY', '⚡ Intraday Radar'),
                const SizedBox(width: 6),
                _buildSetupFilterChip('SWING', '🚀 High R:R Swing'),
                const SizedBox(width: 6),
                _buildSetupFilterChip('PERFECT', '🎯 Perfect Confluence'),
              ],
            ),
          ),
        ),

        // List / Grid
        Expanded(
          child: candidates.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.radar_outlined, size: 48, color: AppColors.textMuted(context)),
                      const SizedBox(height: 10),
                      Text(
                        'No active radar setups matching $_radarSetupFilter filter',
                        style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textSecondary(context)),
                      ),
                    ],
                  ),
                )
              : isDesktop
                  ? GridView.builder(
                      padding: const EdgeInsets.all(16),
                      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                        maxCrossAxisExtent: 520,
                        mainAxisExtent: 225,
                        crossAxisSpacing: 14,
                        mainAxisSpacing: 14,
                      ),
                      itemCount: candidates.length,
                      itemBuilder: (context, index) {
                        final stock = candidates[index];
                        final isTracked = trackedSyms.contains(stock.symbol);
                        return _buildRadarCard(context, stock, provider, isTracked);
                      },
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: candidates.length,
                      itemBuilder: (context, index) {
                        final stock = candidates[index];
                        final isTracked = trackedSyms.contains(stock.symbol);
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: _buildRadarCard(context, stock, provider, isTracked),
                        );
                      },
                    ),
        ),
      ],
    );
  }

  Widget _buildSetupFilterChip(String key, String label) {
    final isSelected = _radarSetupFilter == key;
    return ChoiceChip(
      selected: isSelected,
      label: Text(label, style: TextStyle(fontSize: 11, fontWeight: isSelected ? FontWeight.bold : FontWeight.w600, color: isSelected ? Colors.white : null)),
      selectedColor: AppColors.blue(context),
      onSelected: (_) => setState(() => _radarSetupFilter = key),
    );
  }

  Widget _buildRadarCard(BuildContext context, Stock stock, MarketProvider provider, bool isTracked) {
    final isUp = stock.dayChange >= 0;
    final chgColor = isUp ? AppColors.green(context) : AppColors.red(context);

    return InteractiveScaleCard(
      onTap: () {
        provider.selectStock(stock);
        Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
      },
      borderRadius: BorderRadius.circular(14),
      hoverBorderColor: AppColors.blue(context),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: AppColors.cardDecoration(context, borderRadius: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Header Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Hero(
                      tag: 'stock-sym-${stock.symbol}',
                      child: Material(
                        color: Colors.transparent,
                        child: Text(
                          stock.symbol,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                            color: AppColors.textPrimary(context),
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppTheme.purpleViolet.withAlpha(25),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: AppTheme.purpleViolet.withAlpha(80), width: 0.8),
                      ),
                      child: const Text(
                        '🌟 ALPHA CONFLUENCE',
                        style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: AppTheme.purpleViolet),
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    SparklineChart(candles: stock.candles, color: chgColor, width: 50, height: 18),
                    const SizedBox(width: 8),
                    PriceFlashText(
                      value: stock.cmp,
                      formattedText: '₹${stock.cmp.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                        color: AppColors.textPrimary(context),
                        fontFamily: 'monospace',
                      ),
                    ),
                  ],
                ),
              ],
            ),

          // Setup Type & Subtitle
          Text(
            '${stock.setupType} • ${stock.pattern}',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary(context)),
          ),

          // Win-Rate & R:R Chips
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.green(context).withAlpha(20),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: AppColors.green(context).withAlpha(60), width: 0.8),
                ),
                child: Text(
                  '🎯 Win-Rate: ${stock.winRateScore.toStringAsFixed(1)}%',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: AppColors.green(context),
                    fontFamily: 'monospace',
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.blue(context).withAlpha(20),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: AppColors.blue(context).withAlpha(60), width: 0.8),
                ),
                child: Text(
                  '⚖️ R:R 1:${stock.rrRatio.toStringAsFixed(1)}',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: AppColors.blue(context),
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ],
          ),

          // Targets Strip
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.bg(context),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border(context).withAlpha(120)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildTargetCol(context, 'Stop-Loss', '₹${stock.stopLoss.toStringAsFixed(1)}', AppColors.red(context)),
                Container(width: 1, height: 20, color: AppColors.border(context)),
                _buildTargetCol(context, 'Target 1', '₹${stock.target1.toStringAsFixed(1)}', AppColors.green(context)),
                Container(width: 1, height: 20, color: AppColors.border(context)),
                _buildTargetCol(context, 'Target 2', '₹${stock.target2.toStringAsFixed(1)}', AppColors.blue(context)),
              ],
            ),
          ),

          // Action Buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  InkWell(
                    onTap: () {
                      provider.selectStock(stock);
                      Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
                    },
                    child: Row(
                      children: [
                        Text('360° Deep Dive', style: TextStyle(fontSize: 12, color: AppColors.blue(context), fontWeight: FontWeight.bold)),
                        Icon(Icons.arrow_outward_rounded, size: 14, color: AppColors.blue(context)),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  InkWell(
                    onTap: () => _copyRadarAlert(context, stock),
                    child: Row(
                      children: [
                        Icon(Icons.copy_rounded, size: 13, color: AppColors.textSecondary(context)),
                        const SizedBox(width: 2),
                        Text('Copy', style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context))),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  InkWell(
                    onTap: () => showDialog(context: context, builder: (_) => PositionSizingDialog(stock: stock)),
                    child: Row(
                      children: [
                        Icon(Icons.calculate_rounded, size: 13, color: AppTheme.amberGold),
                        const SizedBox(width: 2),
                        Text('Size', style: TextStyle(fontSize: 11, color: AppTheme.amberGold, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                ],
              ),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: isTracked
                      ? (AppColors.isDark(context) ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0))
                      : AppTheme.emeraldGreen,
                  foregroundColor: isTracked ? AppColors.textMuted(context) : Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: isTracked ? null : () => provider.addTrackedSignal(stock),
                icon: Icon(isTracked ? Icons.check : Icons.push_pin_rounded, size: 13),
                label: Text(
                  isTracked ? 'Tracking Active' : 'Auto-Track',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ],
      ),
    ),
  );
}

  // ==================== TAB 2: RUNNING ACTIVE SIGNALS ====================
  Widget _buildRunningSignalsTab(BuildContext context, MarketProvider provider) {
    final running = provider.activeSignals.where((s) => s.status == 'RUNNING').toList();

    if (running.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.hourglass_empty_rounded, size: 48, color: AppColors.textMuted(context)),
            const SizedBox(height: 10),
            Text(
              'No active trades currently running',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textSecondary(context)),
            ),
          ],
        ),
      );
    }

    final isDesktop = MediaQuery.of(context).size.width >= 900;

    if (isDesktop) {
      return GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
          maxCrossAxisExtent: 520,
          mainAxisExtent: 225,
          crossAxisSpacing: 14,
          mainAxisSpacing: 14,
        ),
        itemCount: running.length,
        itemBuilder: (context, index) => _buildRunningSignalCard(context, running[index], provider),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: running.length,
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _buildRunningSignalCard(context, running[index], provider),
        );
      },
    );
  }

  Widget _buildRunningSignalCard(BuildContext context, RadarSignal sig, MarketProvider provider) {
    final isUp = sig.pnlPct >= 0;
    final pnlColor = isUp ? AppColors.green(context) : AppColors.red(context);
    final pnlSign = isUp ? '+' : '';

    final span = (sig.target2 - sig.stopLoss).abs();
    final progress = span > 0 ? ((sig.currentPrice - sig.stopLoss) / span).clamp(0.0, 1.0) : 0.5;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.card(context),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.border(context)),
        boxShadow: [AppColors.softShadow(context)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Text(
                    sig.symbol,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w900,
                      color: AppColors.textPrimary(context),
                      fontFamily: 'monospace',
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.green(context).withAlpha(20),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      sig.horizon,
                      style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppColors.green(context)),
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: pnlColor.withAlpha(20),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: pnlColor.withAlpha(80)),
                ),
                child: Text(
                  '$pnlSign${sig.pnlPct.toStringAsFixed(2)}%',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w900,
                    color: pnlColor,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Entry: ₹${sig.entryPrice.toStringAsFixed(1)}',
                style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context), fontFamily: 'monospace'),
              ),
              Text(
                'Live CMP: ₹${sig.currentPrice.toStringAsFixed(1)}',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary(context),
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
          // Target Progress Bar
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: AppColors.bg(context),
              valueColor: AlwaysStoppedAnimation<Color>(pnlColor),
              minHeight: 6,
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('🛑 SL: ₹${sig.stopLoss.toStringAsFixed(1)}', style: TextStyle(fontSize: 10, color: AppColors.red(context), fontFamily: 'monospace')),
              Text('🎯 T1: ₹${sig.target1.toStringAsFixed(1)}', style: TextStyle(fontSize: 10, color: AppColors.green(context), fontFamily: 'monospace')),
              Text('🚀 T2: ₹${sig.target2.toStringAsFixed(1)}', style: TextStyle(fontSize: 10, color: AppColors.blue(context), fontFamily: 'monospace')),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '⏱️ ${sig.triggeredAt}',
                style: TextStyle(fontSize: 10, color: AppColors.textMuted(context), fontFamily: 'monospace'),
              ),
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.red,
                  side: const BorderSide(color: Colors.red, width: 0.8),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                onPressed: () => _showCloseTradeDialog(context, provider, sig),
                icon: const Icon(Icons.exit_to_app_rounded, size: 12),
                label: const Text('Close Trade', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ==================== TAB 3: HISTORICAL SUGGESTIONS ARCHIVE ====================
  Widget _buildHistoricalSuggestionsTab(BuildContext context, MarketProvider provider) {
    final history = provider.historicalSuggestions;

    if (history.isEmpty) {
      return Center(
        child: Text('No historical suggestions recorded yet', style: TextStyle(color: AppColors.textMuted(context))),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: history.length,
      itemBuilder: (context, index) {
        final h = history[index];
        final isUp = h.pnlPct >= 0;
        final pnlColor = isUp ? AppColors.green(context) : AppColors.red(context);

        return Container(
          margin: const EdgeInsets.only(bottom: 10),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.card(context),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppColors.border(context)),
            boxShadow: [AppColors.softShadow(context)],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        h.symbol,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w900,
                          color: AppColors.textPrimary(context),
                          fontFamily: 'monospace',
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        h.triggerDate,
                        style: TextStyle(fontSize: 10, color: AppColors.textMuted(context), fontFamily: 'monospace'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 3),
                  Text(
                    'Trigger CMP: ₹${h.triggerCmp} • Max: ₹${h.highestCmp}',
                    style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context), fontFamily: 'monospace'),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${h.pnlPct >= 0 ? '+' : ''}${h.pnlPct.toStringAsFixed(2)}%',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w900, color: pnlColor, fontFamily: 'monospace'),
                  ),
                  Text(
                    h.status,
                    style: TextStyle(fontSize: 10, color: AppColors.blue(context), fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  // ==================== TAB 4: COMPLETED JOURNAL ====================
  Widget _buildJournalTab(BuildContext context, MarketProvider provider) {
    final journal = provider.completedJournal;

    if (journal.isEmpty) {
      return Center(
        child: Text('No closed trades in journal yet', style: TextStyle(color: AppColors.textMuted(context))),
      );
    }

    final wins = journal.where((j) => j.pnlPct > 0).length;
    final winRate = journal.isNotEmpty ? ((wins / journal.length) * 100).toStringAsFixed(1) : '0';

    return Column(
      children: [
        Container(
          margin: const EdgeInsets.all(12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.card(context),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.border(context)),
            boxShadow: [AppColors.softShadow(context)],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildKpiBox(context, 'Win Rate', '$winRate%', AppColors.green(context)),
              _buildKpiBox(context, 'Closed Trades', '${journal.length}', AppColors.textPrimary(context)),
              _buildKpiBox(context, 'Winning Trades', '$wins', AppColors.blue(context)),
            ],
          ),
        ),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            itemCount: journal.length,
            separatorBuilder: (context, index) => Divider(height: 1, color: AppColors.border(context)),
            itemBuilder: (context, index) {
              final item = journal[index];
              final isWin = item.pnlPct >= 0;
              final pnlColor = isWin ? AppColors.green(context) : AppColors.red(context);

              return ListTile(
                title: Row(
                  children: [
                    Text(
                      item.symbol,
                      style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary(context)),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                      decoration: BoxDecoration(
                        color: pnlColor.withAlpha(20),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        item.status,
                        style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: pnlColor),
                      ),
                    ),
                  ],
                ),
                subtitle: Text(
                  'Trigger: ₹${item.entryPrice.toStringAsFixed(1)} → Exit: ₹${(item.exitPrice ?? item.currentPrice).toStringAsFixed(1)}',
                  style: TextStyle(color: AppColors.textSecondary(context), fontSize: 11),
                ),
                trailing: Text(
                  '${item.pnlPct >= 0 ? '+' : ''}${item.pnlPct.toStringAsFixed(2)}%',
                  style: TextStyle(fontWeight: FontWeight.bold, color: pnlColor, fontSize: 13, fontFamily: 'monospace'),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTargetCol(BuildContext context, String label, String val, Color color) {
    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 9, color: AppColors.textMuted(context))),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color, fontFamily: 'monospace')),
      ],
    );
  }

  Widget _buildKpiBox(BuildContext context, String title, String val, Color color) {
    return Column(
      children: [
        Text(title, style: TextStyle(fontSize: 11, color: AppColors.textMuted(context))),
        const SizedBox(height: 4),
        Text(val, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: color, fontFamily: 'monospace')),
      ],
    );
  }
}
