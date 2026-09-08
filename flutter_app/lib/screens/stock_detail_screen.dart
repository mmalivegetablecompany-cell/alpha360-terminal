import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/stock.dart';
import '../providers/market_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/blueprint_slider.dart';
import '../widgets/position_sizing_dialog.dart';
import '../widgets/micro_animations.dart';

class StockDetailScreen extends StatelessWidget {
  final Stock stock;

  const StockDetailScreen({super.key, required this.stock});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();
    final currentStock = provider.stocks.firstWhere(
      (s) => s.symbol == stock.symbol,
      orElse: () => stock,
    );

    return Scaffold(
      backgroundColor: AppColors.bg(context),
      appBar: AppBar(
        backgroundColor: AppColors.surface(context),
        title: Row(
          children: [
            Hero(
              tag: 'stock-sym-${currentStock.symbol}',
              child: Material(
                color: Colors.transparent,
                child: Text(
                  currentStock.symbol,
                  style: TextStyle(
                    fontWeight: FontWeight.w900,
                    fontFamily: 'monospace',
                    color: AppColors.textPrimary(context),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: AppColors.blue(context).withAlpha(25),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                currentStock.mcapTier,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: AppColors.blue(context),
                ),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Previous Asset (←)',
            icon: const Icon(Icons.arrow_back_ios_rounded, size: 16),
            onPressed: () => provider.navigateToPreviousStock(),
          ),
          IconButton(
            tooltip: 'Next Asset (→)',
            icon: const Icon(Icons.arrow_forward_ios_rounded, size: 16),
            onPressed: () => provider.navigateToNextStock(),
          ),
          AnimatedFavoriteStar(
            isFavorite: currentStock.isBucket,
            onTap: () => provider.toggleStockInBucket(currentStock.symbol),
            size: 20,
          ),
          IconButton(
            tooltip: 'Toggle Theme',
            icon: Icon(
              AppColors.isDark(context) ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
              color: AppColors.isDark(context) ? AppTheme.amberGold : AppTheme.primaryBlue,
            ),
            onPressed: () => provider.toggleTheme(),
          ),
          const SizedBox(width: 6),
        ],
      ),
      body: StockDetailView(stock: currentStock),
    );
  }
}

class StockDetailView extends StatefulWidget {
  final Stock stock;
  final bool isEmbedded;

  const StockDetailView({
    super.key,
    required this.stock,
    this.isEmbedded = false,
  });

  @override
  State<StockDetailView> createState() => _StockDetailViewState();
}

class _StockDetailViewState extends State<StockDetailView> with SingleTickerProviderStateMixin {
  late TabController _tabController;

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

  void _copyTradeAlert(BuildContext context, Stock stock) {
    final alertText = '''
🚀 360° TRADE SETUP ALERT: ${stock.symbol}
🏢 Company: ${stock.name} (${stock.sector})
📊 CMP: ₹${stock.cmp.toStringAsFixed(2)} (${stock.dayChangePct >= 0 ? '+' : ''}${stock.dayChangePct.toStringAsFixed(2)}%)
⚡ Verdict: ${stock.action}
🎯 Recommended Entry: ₹${stock.cmp.toStringAsFixed(1)} - ₹${(stock.cmp * 1.02).toStringAsFixed(1)}
🛑 Hard Stop-Loss: ₹${stock.stopLoss.toStringAsFixed(1)}
🎯 Target 1: ₹${stock.target1.toStringAsFixed(1)}
🚀 Target 2: ₹${stock.target2.toStringAsFixed(1)}
⚖️ Risk / Reward: 1 : ${stock.rrRatio.toStringAsFixed(1)}
🌟 Master Alpha Score: ${stock.masterScore.toStringAsFixed(1)}/100
🔮 1-Year Target: ₹${(stock.forecast?.meanTarget ?? stock.target1).toStringAsFixed(1)} (+${(stock.forecast?.upsideMeanPct ?? 0).toStringAsFixed(1)}%)
''';
    Clipboard.setData(ClipboardData(text: alertText));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Copied ${stock.symbol} Trade Alert to Clipboard!')),
    );
  }

  Future<void> _launchUrlStr(String urlStr) async {
    final uri = Uri.parse(urlStr);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final stock = widget.stock;
    final provider = context.watch<MarketProvider>();
    final isUp = stock.dayChange >= 0;
    final chgColor = isUp ? AppColors.green(context) : AppColors.red(context);
    final chgSign = isUp ? '+' : '';
    final isTracked = provider.activeSignals.any((s) => s.symbol == stock.symbol && s.status == 'RUNNING');

    return Column(
      children: [
        // Top Header Summary Card
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.surface(context),
            border: Border(bottom: BorderSide(color: AppColors.border(context), width: 0.8)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Row 1: Symbol, Sector, Price, Day Change
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              stock.symbol,
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w900,
                                fontFamily: 'monospace',
                                color: AppColors.textPrimary(context),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppTheme.amberGold.withAlpha(25),
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(color: AppTheme.amberGold.withAlpha(80)),
                              ),
                              child: Text(
                                stock.action,
                                style: const TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.w800,
                                  color: AppTheme.amberGold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 2),
                        Text(
                          stock.name,
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary(context)),
                        ),
                        Text(
                          '${stock.sector} • ${stock.mcapTier}',
                          style: TextStyle(fontSize: 10, color: AppColors.textMuted(context)),
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      PriceFlashText(
                        value: stock.cmp,
                        formattedText: '₹${stock.cmp.toStringAsFixed(2)}',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                          fontFamily: 'monospace',
                          color: AppColors.textPrimary(context),
                        ),
                      ),
                      const SizedBox(height: 2),
                      PriceFlashText(
                        value: stock.dayChangePct,
                        formattedText: '$chgSign${stock.dayChange.toStringAsFixed(2)} ($chgSign${stock.dayChangePct.toStringAsFixed(2)}%)',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          color: chgColor,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // Action Buttons Strip
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isTracked
                            ? (AppColors.isDark(context) ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0))
                            : AppTheme.emeraldGreen,
                        foregroundColor: isTracked ? AppColors.textMuted(context) : Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                      ),
                      onPressed: isTracked ? null : () => provider.addTrackedSignal(stock),
                      icon: Icon(isTracked ? Icons.check : Icons.push_pin_rounded, size: 12),
                      label: Text(isTracked ? 'Tracking Active' : '📌 Track on Radar', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                    const SizedBox(width: 6),
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.amberGold,
                        foregroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                      ),
                      onPressed: () => showDialog(
                        context: context,
                        builder: (_) => PositionSizingDialog(stock: stock),
                      ),
                      icon: const Icon(Icons.calculate_rounded, size: 12),
                      label: const Text('📐 Size Calculator', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                    const SizedBox(width: 6),
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                      ),
                      onPressed: () => _copyTradeAlert(context, stock),
                      icon: const Icon(Icons.copy_rounded, size: 12),
                      label: const Text('📋 Copy Alert', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                    const SizedBox(width: 6),
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                      ),
                      onPressed: () => _launchUrlStr('https://in.tradingview.com/chart/?symbol=NSE:${stock.symbol}'),
                      icon: const Icon(Icons.show_chart_rounded, size: 12, color: Colors.blue),
                      label: const Text('TradingView ↗', style: TextStyle(fontSize: 10)),
                    ),
                    const SizedBox(width: 6),
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                      ),
                      onPressed: () => _launchUrlStr('https://www.screener.in/company/${stock.symbol}/'),
                      icon: const Icon(Icons.description_outlined, size: 12, color: Colors.teal),
                      label: const Text('Screener ↗', style: TextStyle(fontSize: 10)),
                    ),
                    const SizedBox(width: 6),
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                      ),
                      onPressed: () => _launchUrlStr('https://www.google.com/finance/quote/${stock.symbol}:NSE'),
                      icon: const Icon(Icons.public_rounded, size: 12, color: Colors.indigo),
                      label: const Text('Google Fin ↗', style: TextStyle(fontSize: 10)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // Tab Bar for the 4 Terminal Sections
        Container(
          color: AppColors.card(context),
          child: TabBar(
            controller: _tabController,
            isScrollable: true,
            indicatorColor: AppColors.blue(context),
            labelColor: AppColors.blue(context),
            unselectedLabelColor: AppColors.textSecondary(context),
            labelStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 11),
            unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 11),
            tabs: const [
              Tab(text: '🔮 360° Forecast'),
              Tab(text: '📊 8-Quarter Financials'),
              Tab(text: '📈 Technicals & Pivots'),
              Tab(text: '⚖️ Valuation & Safety'),
            ],
          ),
        ),

        // Tab View Body
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildForecastTab(context, stock),
              _buildFinancialsTab(context, stock),
              _buildTechnicalsTab(context, stock),
              _buildValuationTab(context, stock),
            ],
          ),
        ),
      ],
    );
  }

  // ==================== TAB 1: 360° FORECAST & TARGETS ====================
  Widget _buildForecastTab(BuildContext context, Stock stock) {
    final fc = stock.forecast;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Forecast Overview Banner
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('1-YEAR CONSENSUS TARGET', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                        const SizedBox(height: 2),
                        Text(
                          '₹${(fc?.meanTarget ?? stock.target1).toStringAsFixed(1)}',
                          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, fontFamily: 'monospace', color: AppColors.blue(context)),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppColors.green(context).withAlpha(20),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.green(context).withAlpha(80)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text('UPSIDE POTENTIAL', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppColors.green(context))),
                          Text(
                            '+${(fc?.upsideMeanPct ?? 0).toStringAsFixed(1)}%',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: AppColors.green(context), fontFamily: 'monospace'),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Divider(height: 1),
                const SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildMiniMetric(context, 'Low Target', '₹${(fc?.lowTarget ?? 0).toStringAsFixed(1)}'),
                    _buildMiniMetric(context, 'Median Target', '₹${(fc?.medianTarget ?? 0).toStringAsFixed(1)}'),
                    _buildMiniMetric(context, 'High Target', '₹${(fc?.highTarget ?? 0).toStringAsFixed(1)}'),
                    _buildMiniMetric(context, 'Coverage', '${fc?.numAnalysts ?? 0} Analysts'),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Consensus Rating & Breakdown Bar
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('ANALYST CONSENSUS RATING', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppColors.green(context).withAlpha(20),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        fc?.consensusRating ?? stock.consensus,
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: AppColors.green(context)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                // Breakdown Bar
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: Row(
                    children: [
                      if ((fc?.buyPct ?? 0) > 0)
                        Expanded(
                          flex: ((fc?.buyPct ?? 0) * 10).toInt(),
                          child: Container(height: 8, color: AppColors.green(context)),
                        ),
                      if ((fc?.outperformPct ?? 0) > 0)
                        Expanded(
                          flex: ((fc?.outperformPct ?? 0) * 10).toInt(),
                          child: Container(height: 8, color: Colors.teal),
                        ),
                      if ((fc?.holdPct ?? 0) > 0)
                        Expanded(
                          flex: ((fc?.holdPct ?? 0) * 10).toInt(),
                          child: Container(height: 8, color: AppTheme.amberGold),
                        ),
                      if ((fc?.sellPct ?? 0) > 0)
                        Expanded(
                          flex: ((fc?.sellPct ?? 0) * 10).toInt(),
                          child: Container(height: 8, color: AppColors.red(context)),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Buy: ${(fc?.buyPct ?? 0).toInt()}%', style: TextStyle(fontSize: 10, color: AppColors.green(context), fontWeight: FontWeight.bold)),
                    Text('Hold: ${(fc?.holdPct ?? 0).toInt()}%', style: const TextStyle(fontSize: 10, color: AppTheme.amberGold, fontWeight: FontWeight.bold)),
                    Text('Sell: ${(fc?.sellPct ?? 0).toInt()}%', style: TextStyle(fontSize: 10, color: AppColors.red(context), fontWeight: FontWeight.bold)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Institutional Research Desk Reports Table
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('INSTITUTIONAL RESEARCH REPORTS', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                const SizedBox(height: 10),
                if (fc != null && fc.reports.isNotEmpty) ...[
                  for (var rep in fc.reports) ...[
                    Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.bg(context),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.border(context).withAlpha(100)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(rep.firm, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppColors.textPrimary(context))),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: AppColors.green(context).withAlpha(20),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  '${rep.rating} • Target ₹${rep.targetPrice.toStringAsFixed(1)}',
                                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.green(context)),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(rep.rationale, style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context), height: 1.3)),
                        ],
                      ),
                    ),
                  ],
                ] else ...[
                  Text('No institutional reports indexed yet for ${stock.symbol}', style: TextStyle(fontSize: 11, color: AppColors.textMuted(context))),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ==================== TAB 2: 8-QUARTER FINANCIAL GROWTH ====================
  Widget _buildFinancialsTab(BuildContext context, Stock stock) {
    final qh = stock.quartersHistory;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Growth Streaks Summary Row
          Row(
            children: [
              Expanded(
                child: _buildMetricBadge(context, 'PAT Compounding Streak', '${stock.streakPat} Quarters', AppColors.green(context)),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildMetricBadge(context, 'Revenue Compounding Streak', '${stock.streakRev} Quarters', AppColors.blue(context)),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildMetricBadge(context, 'Operating Margin', '${stock.latestOpm.toStringAsFixed(1)}%', AppTheme.amberGold),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // 8-Quarter Financial Table
          Container(
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('8-QUARTER HISTORICAL COMPONDING MATRIX', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                      Text('${qh.length} Quarters Logged', style: TextStyle(fontSize: 10, color: AppColors.textSecondary(context), fontFamily: 'monospace')),
                    ],
                  ),
                ),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: DataTable(
                    headingRowHeight: 38,
                    dataRowMinHeight: 40,
                    dataRowMaxHeight: 40,
                    columns: const [
                      DataColumn(label: Text('QUARTER')),
                      DataColumn(label: Text('REVENUE (₹ CR)')),
                      DataColumn(label: Text('YOY REV %')),
                      DataColumn(label: Text('PAT (₹ CR)')),
                      DataColumn(label: Text('YOY PAT %')),
                      DataColumn(label: Text('OPM %')),
                      DataColumn(label: Text('EPS (₹)')),
                      DataColumn(label: Text('P/E')),
                    ],
                    rows: qh.map((q) {
                      final revUp = (q.yoyRev ?? 0) >= 0;
                      final patUp = (q.yoyPat ?? 0) >= 0;

                      return DataRow(
                        cells: [
                          DataCell(Text(q.quarter, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11))),
                          DataCell(Text('₹${q.revenue.toStringAsFixed(1)}', style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                          DataCell(
                            Text(
                              q.yoyRev != null ? '${revUp ? '+' : ''}${q.yoyRev!.toStringAsFixed(1)}%' : '-',
                              style: TextStyle(color: revUp ? AppColors.green(context) : AppColors.red(context), fontWeight: FontWeight.bold, fontFamily: 'monospace', fontSize: 11),
                            ),
                          ),
                          DataCell(Text('₹${q.pat.toStringAsFixed(1)}', style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                          DataCell(
                            Text(
                              q.yoyPat != null ? '${patUp ? '+' : ''}${q.yoyPat!.toStringAsFixed(1)}%' : '-',
                              style: TextStyle(color: patUp ? AppColors.green(context) : AppColors.red(context), fontWeight: FontWeight.bold, fontFamily: 'monospace', fontSize: 11),
                            ),
                          ),
                          DataCell(Text('${q.opm.toStringAsFixed(1)}%', style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                          DataCell(Text('₹${q.eps.toStringAsFixed(1)}', style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                          DataCell(Text('${q.pe.toStringAsFixed(1)}x', style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                        ],
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ==================== TAB 3: TECHNICALS & PIVOTS ====================
  Widget _buildTechnicalsTab(BuildContext context, Stock stock) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Hero Action Blueprint & Execution Levels
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(color: AppTheme.amberGold.withAlpha(20), borderRadius: BorderRadius.circular(6)),
                          child: Text(stock.action, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: AppTheme.amberGold)),
                        ),
                        const SizedBox(width: 8),
                        Text(stock.setupType, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textPrimary(context))),
                      ],
                    ),
                    Text('Tech Score: ${stock.techScore.toInt()}/100', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: AppColors.blue(context), fontFamily: 'monospace')),
                  ],
                ),
                const SizedBox(height: 10),
                Text('Pattern: ${stock.pattern} • Confluence: ${stock.confluenceScore.toInt()}%', style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context))),
                const SizedBox(height: 12),
                // 4-Column Execution Levels
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildExecutionPill(context, 'Entry Zone', '₹${stock.cmp.toStringAsFixed(1)} - ₹${(stock.cmp * 1.02).toStringAsFixed(1)}', AppColors.blue(context)),
                    _buildExecutionPill(context, 'Hard Stop-Loss', '₹${stock.stopLoss.toStringAsFixed(1)}', AppColors.red(context)),
                    _buildExecutionPill(context, 'Target 1 (Base)', '₹${stock.target1.toStringAsFixed(1)}', AppColors.green(context)),
                    _buildExecutionPill(context, 'Target 2 (Swing)', '₹${stock.target2.toStringAsFixed(1)}', Colors.teal),
                    _buildExecutionPill(context, 'Risk:Reward', '1 : ${stock.rrRatio.toStringAsFixed(1)}', AppTheme.purpleViolet),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Interactive Chart Card
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('PRICE ACTION & MOVING AVERAGES (D-CANDLES)', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                    Row(
                      children: [
                        _buildLegendPill('20 EMA', AppColors.blue(context)),
                        const SizedBox(width: 6),
                        _buildLegendPill('50 EMA', AppTheme.amberGold),
                        const SizedBox(width: 6),
                        _buildLegendPill('200 SMA', AppTheme.purpleViolet),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                SizedBox(
                  height: 200,
                  child: stock.candles.isNotEmpty
                      ? _buildInteractiveChart(context, stock)
                      : Center(child: Text('No candle history loaded', style: TextStyle(color: AppColors.textMuted(context)))),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Blueprint Slider
          BlueprintSlider(stock: stock),
          const SizedBox(height: 14),

          // Multi-Timeframe Confluence Matrix Table
          if (stock.timeframes.isNotEmpty) ...[
            Container(
              decoration: BoxDecoration(
                color: AppColors.card(context),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border(context)),
                boxShadow: [AppColors.softShadow(context)],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text('MULTI-TIMEFRAME CONFLUENCE MATRIX', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                  ),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      headingRowHeight: 36,
                      dataRowMinHeight: 38,
                      dataRowMaxHeight: 38,
                      columns: const [
                        DataColumn(label: Text('TIMEFRAME')),
                        DataColumn(label: Text('TREND')),
                        DataColumn(label: Text('RSI')),
                        DataColumn(label: Text('MACD')),
                        DataColumn(label: Text('SUPPORT')),
                        DataColumn(label: Text('RESISTANCE')),
                        DataColumn(label: Text('SETUP')),
                        DataColumn(label: Text('VERDICT')),
                      ],
                      rows: stock.timeframes.map((tf) {
                        return DataRow(
                          cells: [
                            DataCell(Text(tf.timeframe, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11))),
                            DataCell(Text(tf.trend, style: const TextStyle(fontSize: 11))),
                            DataCell(Text(tf.rsi.toStringAsFixed(1), style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                            DataCell(Text(tf.macd, style: const TextStyle(fontSize: 11))),
                            DataCell(Text('₹${tf.support.toStringAsFixed(1)}', style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                            DataCell(Text('₹${tf.resistance.toStringAsFixed(1)}', style: const TextStyle(fontFamily: 'monospace', fontSize: 11))),
                            DataCell(Text(tf.setup, style: const TextStyle(fontSize: 11))),
                            DataCell(
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                                decoration: BoxDecoration(
                                  color: (tf.verdict.contains('BUY') ? AppColors.green(context) : AppColors.blue(context)).withAlpha(20),
                                  borderRadius: BorderRadius.circular(3),
                                ),
                                child: Text(tf.verdict, style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: tf.verdict.contains('BUY') ? AppColors.green(context) : AppColors.blue(context))),
                              ),
                            ),
                          ],
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
          ],

          // 6-Panel Technical Indicator Deep-Dive
          _buildSixPanelTechnicals(context, stock),
        ],
      ),
    );
  }

  Widget _buildSixPanelTechnicals(BuildContext context, Stock stock) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildPanelBox(
                context,
                title: 'Moving Averages',
                badge: stock.isGoldenCross ? '🟢 Golden Cross' : '🔴 Death Cross',
                rows: [
                  {'EMA 9 / 20:': '₹${stock.ema9.toStringAsFixed(1)} / ₹${stock.ema20.toStringAsFixed(1)}'},
                  {'EMA 50:': '₹${stock.ema50.toStringAsFixed(1)}'},
                  {'SMA 200:': '₹${stock.sma200.toStringAsFixed(1)}'},
                  {'Dist 200 SMA:': '${stock.distSma200 >= 0 ? '+' : ''}${stock.distSma200.toStringAsFixed(1)}%'},
                ],
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildPanelBox(
                context,
                title: 'Oscillators & Trend',
                badge: stock.macdSignal,
                rows: [
                  {'14-Day RSI:': stock.rsi.toStringAsFixed(1)},
                  {'MACD Hist:': '${stock.macdHist >= 0 ? '+' : ''}${stock.macdHist.toStringAsFixed(2)}'},
                  {'Stoch (14,3):': '${stock.stochK.toInt()} / ${stock.stochD.toInt()}'},
                  {'ADX Power:': stock.adxStrength},
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildPanelBox(
                context,
                title: 'Volatility & Bands',
                badge: '14D ATR: ₹${stock.atr14.toStringAsFixed(1)}',
                rows: [
                  {'BB Upper:': '₹${stock.bbUpper.toStringAsFixed(1)}'},
                  {'BB Middle:': '₹${stock.bbMid.toStringAsFixed(1)}'},
                  {'BB Lower:': '₹${stock.bbLower.toStringAsFixed(1)}'},
                  {'Bandwidth:': '${stock.bbBandwidth.toStringAsFixed(1)}%'},
                ],
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildPanelBox(
                context,
                title: 'Classical Pivots',
                badge: 'Pivot: ₹${stock.pivot.toStringAsFixed(1)}',
                rows: [
                  {'Resist R1 / R2:': '₹${stock.r1.toStringAsFixed(1)} / ₹${stock.r2.toStringAsFixed(1)}'},
                  {'Extreme R3:': '₹${stock.r3.toStringAsFixed(1)}'},
                  {'Support S1 / S2:': '₹${stock.s1.toStringAsFixed(1)} / ₹${stock.s2.toStringAsFixed(1)}'},
                  {'Floor S3:': '₹${stock.s3.toStringAsFixed(1)}'},
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildPanelBox(
                context,
                title: 'Fibonacci Levels',
                badge: 'Golden: ₹${stock.fib61.toStringAsFixed(1)}',
                rows: [
                  {'23.6% / 38.2%:': '₹${stock.fib23.toStringAsFixed(1)} / ₹${stock.fib38.toStringAsFixed(1)}'},
                  {'50.0% Half:': '₹${stock.fib50.toStringAsFixed(1)}'},
                  {'61.8% Golden:': '₹${stock.fib61.toStringAsFixed(1)}'},
                  {'161.8% Ext:': '₹${stock.fib161.toStringAsFixed(1)}'},
                ],
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildPanelBox(
                context,
                title: 'Volume Dynamics',
                badge: '${stock.volRatio.toStringAsFixed(2)}x Surge',
                rows: [
                  {'Surge Multiple:': '${stock.volRatio.toStringAsFixed(2)}x'},
                  {'Today Volume:': '${(stock.volume / 1000).toStringAsFixed(1)}k'},
                  {'20D Avg Vol:': '${(stock.avgVol20d / 1000).toStringAsFixed(1)}k'},
                  {'Flow Status:': stock.volStatus},
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  // ==================== TAB 4: VALUATION & MARGIN OF SAFETY ====================
  Widget _buildValuationTab(BuildContext context, Stock stock) {
    final et = stock.etPrime;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Margin of Safety Banner
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('VALUATION DISCOUNT (MARGIN OF SAFETY)', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                    const SizedBox(height: 2),
                    Text(
                      '${stock.valDiscountPct >= 0 ? '+' : ''}${stock.valDiscountPct.toStringAsFixed(1)}%',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        fontFamily: 'monospace',
                        color: stock.valDiscountPct >= 15 ? AppColors.green(context) : AppTheme.amberGold,
                      ),
                    ),
                    Text('Vs 8-Quarter Median P/E (${stock.pe8qMed.toStringAsFixed(1)}x)', style: TextStyle(fontSize: 10, color: AppColors.textSecondary(context))),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppColors.blue(context).withAlpha(20),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.blue(context).withAlpha(80)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('CURRENT P/E', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppColors.blue(context))),
                      Text(
                        '${stock.todayPe.toStringAsFixed(1)}x',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: AppColors.blue(context), fontFamily: 'monospace'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // P/E Multiples Compounding Band
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('HISTORICAL 8-QUARTER P/E BAND', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildMiniMetric(context, 'Min P/E', '${stock.pe8qMin.toStringAsFixed(1)}x'),
                    _buildMiniMetric(context, 'Median P/E', '${stock.pe8qMed.toStringAsFixed(1)}x'),
                    _buildMiniMetric(context, 'Average P/E', '${stock.pe8qAvg.toStringAsFixed(1)}x'),
                    _buildMiniMetric(context, 'Max P/E', '${stock.pe8qMax.toStringAsFixed(1)}x'),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Core Valuation Multiples
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.card(context),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border(context)),
              boxShadow: [AppColors.softShadow(context)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('CORE VALUATION & ASSET MULTIPLES', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textMuted(context))),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildMiniMetric(context, 'P/B Ratio', '${stock.todayPb.toStringAsFixed(1)}x'),
                    _buildMiniMetric(context, 'PEG Ratio', stock.todayPeg.toStringAsFixed(2)),
                    _buildMiniMetric(context, 'Book Value', '₹${stock.bookValue.toStringAsFixed(1)}'),
                    _buildMiniMetric(context, 'Market Cap', '₹${stock.mcapCr.toStringAsFixed(0)} Cr'),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // ET Prime / Refinitiv Intelligence Suite
          if (et != null) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.card(context),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border(context)),
                boxShadow: [AppColors.softShadow(context)],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.verified_rounded, color: AppTheme.purpleViolet, size: 18),
                          const SizedBox(width: 6),
                          Text('ET PRIME REFINITIV DIAGNOSTIC', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.purpleViolet)),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(color: AppTheme.purpleViolet.withAlpha(20), borderRadius: BorderRadius.circular(6)),
                        child: Text('${et.stockScore}/10 (${et.scoreOutlook})', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.purpleViolet)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  // 5 Pillar Scores with Progress Bars
                  _buildEtScoreBar(context, 'Earnings Quality', et.earningsScore),
                  _buildEtScoreBar(context, 'Fundamental Health', et.fundamentalScore),
                  _buildEtScoreBar(context, 'Relative Valuation', et.rvScore),
                  _buildEtScoreBar(context, 'Risk Intolerance', et.riskScore),
                  _buildEtScoreBar(context, 'Price Momentum', et.momentumScore),
                  const SizedBox(height: 8),
                  if (et.pdfLink.isNotEmpty) ...[
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton.icon(
                        onPressed: () => _launchUrlStr(et.pdfLink),
                        icon: const Icon(Icons.picture_as_pdf_rounded, size: 14, color: Colors.red),
                        label: const Text('Download Full ET Stock Report (.PDF)', style: TextStyle(fontSize: 11, color: Colors.red, fontWeight: FontWeight.bold)),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ==================== HELPER WIDGETS ====================
  Widget _buildEtScoreBar(BuildContext context, String label, int score) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context))),
              Text('$score / 10', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
            ],
          ),
          const SizedBox(height: 3),
          ClipRRect(
            borderRadius: BorderRadius.circular(3),
            child: LinearProgressIndicator(
              value: (score / 10).clamp(0.0, 1.0),
              minHeight: 5,
              backgroundColor: AppColors.border(context),
              valueColor: AlwaysStoppedAnimation<Color>(
                score >= 7 ? AppColors.green(context) : (score >= 5 ? AppTheme.amberGold : AppColors.red(context)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPanelBox(BuildContext context, {required String title, required String badge, required List<Map<String, String>> rows}) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.bg(context),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border(context).withAlpha(100)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.blue(context))),
              Text(badge, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
            ],
          ),
          const SizedBox(height: 6),
          for (var r in rows) ...[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 1.5),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(r.keys.first, style: TextStyle(fontSize: 9, color: AppColors.textMuted(context))),
                  Text(r.values.first, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace', color: AppColors.textPrimary(context))),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMetricBadge(BuildContext context, String label, String val, Color color) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.card(context),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border(context)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(fontSize: 9, color: AppColors.textMuted(context))),
          const SizedBox(height: 2),
          Text(val, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w900, color: color, fontFamily: 'monospace')),
        ],
      ),
    );
  }

  Widget _buildMiniMetric(BuildContext context, String label, String val) {
    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 9, color: AppColors.textMuted(context))),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppColors.textPrimary(context), fontFamily: 'monospace')),
      ],
    );
  }

  Widget _buildExecutionPill(BuildContext context, String label, String val, Color color) {
    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 9, color: AppColors.textMuted(context))),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color, fontFamily: 'monospace')),
      ],
    );
  }

  Widget _buildLegendPill(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 6, height: 6, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(width: 3),
        Text(label, style: TextStyle(fontSize: 9, color: color, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildInteractiveChart(BuildContext context, Stock stock) {
    final spots = <FlSpot>[];
    for (int i = 0; i < stock.candles.length; i++) {
      spots.add(FlSpot(i.toDouble(), stock.candles[i].close));
    }

    final isUp = stock.dayChange >= 0;
    final chartColor = isUp ? AppColors.green(context) : AppColors.red(context);
    final isDark = AppColors.isDark(context);

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          getDrawingHorizontalLine: (val) => FlLine(
            color: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0),
            strokeWidth: 0.8,
            dashArray: [4, 4],
          ),
        ),
        titlesData: FlTitlesData(
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 45,
              getTitlesWidget: (val, meta) => Text(
                '₹${val.toInt()}',
                style: TextStyle(fontSize: 9, color: AppColors.textMuted(context), fontFamily: 'monospace'),
              ),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 18,
              getTitlesWidget: (val, meta) {
                final idx = val.toInt();
                if (idx == 0 || idx == (stock.candles.length ~/ 2) || idx == (stock.candles.length - 1)) {
                  if (idx >= 0 && idx < stock.candles.length) {
                    final d = stock.candles[idx].date;
                    return Text(
                      d.length >= 5 ? d.substring(d.length - 5) : d,
                      style: TextStyle(fontSize: 8, color: AppColors.textMuted(context), fontFamily: 'monospace'),
                    );
                  }
                }
                return const SizedBox.shrink();
              },
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                final idx = spot.spotIndex;
                final date = (idx >= 0 && idx < stock.candles.length) ? stock.candles[idx].date : '';
                return LineTooltipItem(
                  '₹${spot.y.toStringAsFixed(2)}\n$date',
                  TextStyle(
                    color: AppColors.textPrimary(context),
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                    fontFamily: 'monospace',
                  ),
                );
              }).toList();
            },
          ),
        ),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            curveSmoothness: 0.25,
            color: chartColor,
            barWidth: 2.2,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  chartColor.withAlpha(50),
                  chartColor.withAlpha(0),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
