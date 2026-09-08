import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/market_provider.dart';
import '../models/stock.dart';
import '../models/watchlist_constants.dart';
import '../theme/app_theme.dart';
import '../widgets/sparkline_chart.dart';
import '../widgets/market_breadth_bar.dart';
import '../widgets/smart_filter_drawer.dart';
import '../widgets/custom_basket_dialog.dart';
import '../widgets/micro_animations.dart';
import 'stock_detail_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final TextEditingController _searchController = TextEditingController();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();
    final isDesktop = MediaQuery.of(context).size.width >= 1000;

    if (provider.isLoading) {
      return Scaffold(
        backgroundColor: AppColors.bg(context),
        body: Column(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              color: AppColors.surface(context),
              child: Row(
                children: [
                  PulseGlowDot(color: AppColors.blue(context), size: 8),
                  const SizedBox(width: 10),
                  Text(
                    'HYDRATING 424 ASSETS & LIVE QUOTES...',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.5,
                      color: AppColors.textSecondary(context),
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ),
            const Expanded(child: ShimmerLoadingList(itemCount: 8)),
          ],
        ),
      );
    }

    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: AppColors.bg(context),
      endDrawer: const SmartFilterDrawer(),
      body: isDesktop
          ? _buildDesktopLayout(context, provider)
          : _buildMobileLayout(context, provider),
    );
  }

  // ==================== DESKTOP MASTER-DETAIL LAYOUT ====================
  Widget _buildDesktopLayout(BuildContext context, MarketProvider provider) {
    final selectedStock = provider.selectedStock;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Left Master Pane: Filters, Search, Presets, and Stock Content
        Expanded(
          flex: provider.viewMode == 'TABLE' ? 10 : 6,
          child: Column(
            children: [
              _buildHeaderSearchAndActions(context, provider),
              _buildWatchlistBasketsBar(context, provider),
              _buildStrategyPresetsBar(context, provider),
              MarketBreadthBar(stocks: provider.allStocks),
              _buildControlBanner(context, provider, isDesktop: true),
              Expanded(
                child: provider.stocks.isEmpty
                    ? _buildEmptyState(context, provider)
                    : _buildStockContent(context, provider, isDesktop: true),
              ),
            ],
          ),
        ),

        // Right Detail Inspection Panel (Master-Detail)
        if (provider.viewMode != 'TABLE') ...[
          const VerticalDivider(width: 1, thickness: 1),
          Expanded(
            flex: 5,
            child: selectedStock == null
                ? Center(
                    child: Text(
                      'Select an asset to view 360° deep dive',
                      style: TextStyle(color: AppColors.textMuted(context)),
                    ),
                  )
                : StockDetailView(stock: selectedStock, isEmbedded: true),
          ),
        ],
      ],
    );
  }

  // ==================== MOBILE LAYOUT ====================
  Widget _buildMobileLayout(BuildContext context, MarketProvider provider) {
    return Column(
      children: [
        _buildHeaderSearchAndActions(context, provider),
        _buildWatchlistBasketsBar(context, provider),
        _buildStrategyPresetsBar(context, provider),
        MarketBreadthBar(stocks: provider.allStocks),
        _buildControlBanner(context, provider, isDesktop: false),
        Expanded(
          child: provider.stocks.isEmpty
              ? _buildEmptyState(context, provider)
              : ListView.separated(
                  itemCount: provider.stocks.length,
                  separatorBuilder: (context, index) => Divider(
                    height: 1,
                    color: AppColors.border(context).withAlpha(120),
                  ),
                  itemBuilder: (context, index) {
                    final stock = provider.stocks[index];
                    return _buildMobileStockTile(context, stock, provider);
                  },
                ),
        ),
      ],
    );
  }

  // ==================== HEADER SEARCH & ACTION BUTTONS ====================
  Widget _buildHeaderSearchAndActions(BuildContext context, MarketProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.surface(context),
        border: Border(bottom: BorderSide(color: AppColors.border(context), width: 0.8)),
      ),
      child: Row(
        children: [
          // Search Field
          Expanded(
            child: TextField(
              controller: _searchController,
              onChanged: provider.setSearchQuery,
              style: TextStyle(color: AppColors.textPrimary(context), fontSize: 13),
              decoration: InputDecoration(
                hintText: 'Search 424 stocks by Symbol, Company, Sector...',
                hintStyle: TextStyle(color: AppColors.textMuted(context), fontSize: 12),
                prefixIcon: Icon(Icons.search, color: AppColors.blue(context), size: 18),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 16),
                        color: AppColors.textSecondary(context),
                        onPressed: () {
                          _searchController.clear();
                          provider.setSearchQuery('');
                        },
                      )
                    : null,
                filled: true,
                fillColor: AppColors.bg(context),
                isDense: true,
                contentPadding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppColors.border(context)),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppColors.border(context)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppColors.blue(context), width: 1.2),
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),

          // Smart Screener Button with Active Badge
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: provider.activeSmartFiltersCount > 0
                  ? AppColors.blue(context)
                  : (AppColors.isDark(context) ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0)),
              foregroundColor: provider.activeSmartFiltersCount > 0
                  ? Colors.white
                  : AppColors.textPrimary(context),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              elevation: 0,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () => _scaffoldKey.currentState?.openEndDrawer(),
            icon: Icon(
              Icons.tune_rounded,
              size: 15,
              color: provider.activeSmartFiltersCount > 0 ? Colors.white : AppColors.blue(context),
            ),
            label: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('Filters', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                if (provider.activeSmartFiltersCount > 0) ...[
                  const SizedBox(width: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${provider.activeSmartFiltersCount}',
                      style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: AppColors.blue(context)),
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 6),

          // New Basket Button
          IconButton(
            tooltip: 'Create New Stock Basket',
            icon: const Icon(Icons.add_circle_outline_rounded, size: 20),
            color: AppColors.textSecondary(context),
            onPressed: () => showDialog(context: context, builder: (_) => const CustomBasketDialog()),
          ),
        ],
      ),
    );
  }

  // ==================== WATCHLIST BASKETS BAR ====================
  Widget _buildWatchlistBasketsBar(BuildContext context, MarketProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      color: AppColors.surface(context),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            _buildBasketPill(context, provider, id: 'ALL', label: '🌐 All Universe', count: provider.allStocks.length),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'MY_BUCKET', label: '🧺 My Bucket', count: provider.userBucketSymbols.length),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'STAR_STOCKS', label: '⭐ Star Stocks', count: 23),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: '35_MASTER', label: '🌐 35 Master', count: 35),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'ACTIVE_CORE', label: '🎯 Active Core', count: 16),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'READY_TO_BUY', label: '🟢 Ready to Buy', count: 10),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'WAIT_ALERT', label: '⏸️ Wait Alert', count: 6),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'FAVORITES', label: '⭐ Favorites', count: 5),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'QUARANTINE', label: '⚠️ Quarantine', count: 8),
            const SizedBox(width: 6),
            _buildBasketPill(context, provider, id: 'ELIMINATED', label: '❌ Eliminated', count: 6),
            // User Custom Baskets
            for (var cb in provider.userCustomBaskets) ...[
              const SizedBox(width: 6),
              _buildBasketPill(context, provider, id: cb.id, label: '📁 ${cb.name}', count: cb.symbols.length, isCustom: true),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildBasketPill(
    BuildContext context,
    MarketProvider provider, {
    required String id,
    required String label,
    required int count,
    bool isCustom = false,
  }) {
    final isSelected = provider.activeBasket == id;

    return InkWell(
      onTap: () => provider.setBasket(id),
      onLongPress: isCustom
          ? () {
              showModalBottomSheet(
                context: context,
                builder: (_) => SafeArea(
                  child: Wrap(
                    children: [
                      ListTile(
                        leading: const Icon(Icons.edit),
                        title: const Text('Edit Basket'),
                        onTap: () {
                          Navigator.pop(context);
                          showDialog(context: context, builder: (_) => CustomBasketDialog(existingBasketId: id));
                        },
                      ),
                      ListTile(
                        leading: const Icon(Icons.delete, color: Colors.red),
                        title: const Text('Delete Basket', style: TextStyle(color: Colors.red)),
                        onTap: () {
                          Navigator.pop(context);
                          provider.deleteCustomBasket(id);
                        },
                      ),
                    ],
                  ),
                ),
              );
            }
          : null,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.blue(context) : AppColors.card(context),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? AppColors.blue(context) : AppColors.border(context),
            width: isSelected ? 1.2 : 0.8,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                color: isSelected ? Colors.white : AppColors.textPrimary(context),
              ),
            ),
            const SizedBox(width: 5),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
              decoration: BoxDecoration(
                color: isSelected ? Colors.white.withAlpha(50) : AppColors.border(context),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                '$count',
                style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                  color: isSelected ? Colors.white : AppColors.textSecondary(context),
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ==================== STRATEGY PRESETS BAR ====================
  Widget _buildStrategyPresetsBar(BuildContext context, MarketProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.surface(context),
        border: Border(bottom: BorderSide(color: AppColors.border(context), width: 0.8)),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: kStrategyPresets.map((preset) {
            final isSelected = provider.activePreset == preset.key;
            return Padding(
              padding: const EdgeInsets.only(right: 6),
              child: Tooltip(
                message: preset.tooltip,
                child: FilterChip(
                  selected: isSelected,
                  showCheckmark: false,
                  avatar: Text(preset.icon, style: const TextStyle(fontSize: 11)),
                  label: Text(
                    preset.label,
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                      color: isSelected ? Colors.white : AppColors.textSecondary(context),
                    ),
                  ),
                  backgroundColor: AppColors.card(context),
                  selectedColor: AppColors.blue(context),
                  side: BorderSide(
                    color: isSelected ? AppColors.blue(context) : AppColors.border(context),
                    width: 0.8,
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 0),
                  onSelected: (_) => provider.setActivePreset(preset.key),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  // ==================== CONTROL & SORT BANNER ====================
  Widget _buildControlBanner(BuildContext context, MarketProvider provider, {required bool isDesktop}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      color: AppColors.surface(context),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Text(
                '${provider.stocks.length} ASSETS ACTIVE',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textSecondary(context),
                  fontFamily: 'monospace',
                  letterSpacing: 0.5,
                ),
              ),
              if (provider.activeSmartFiltersCount > 0 || provider.activePreset != 'ALL' || provider.activeBasket != 'ALL') ...[
                const SizedBox(width: 8),
                InkWell(
                  onTap: () => provider.resetSmartFilters(),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.red.withAlpha(20),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: Colors.red.withAlpha(80), width: 0.8),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.close, size: 11, color: Colors.red),
                        SizedBox(width: 2),
                        Text('Reset All', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.red)),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
          Row(
            children: [
              // When in Table view, provide switch between Technical and Fundamental columns
              if (provider.viewMode == 'TABLE') ...[
                Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    color: AppColors.bg(context),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.border(context)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _buildTableModeBtn(context, provider, mode: 'TECHNICAL', label: 'Technical', icon: Icons.trending_up_rounded),
                      _buildTableModeBtn(context, provider, mode: 'FUNDAMENTAL', label: 'Fundamental', icon: Icons.pie_chart_outline_rounded),
                    ],
                  ),
                ),
                const SizedBox(width: 10),
              ],

              if (isDesktop) ...[
                // View Mode Switcher on Desktop
                Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    color: AppColors.bg(context),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.border(context)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _buildViewBtn(context, provider, mode: 'SPLIT', icon: Icons.view_sidebar_rounded, tip: 'Split Master-Detail View'),
                      _buildViewBtn(context, provider, mode: 'TABLE', icon: Icons.table_chart_rounded, tip: 'Dense Institutional Table'),
                      _buildViewBtn(context, provider, mode: 'GRID', icon: Icons.grid_view_rounded, tip: 'Card Grid View'),
                    ],
                  ),
                ),
                const SizedBox(width: 10),
              ],

              // Sort Popup
              PopupMenuButton<String>(
                onSelected: (col) => provider.sortByColumn(col),
                itemBuilder: (context) => const [
                  PopupMenuItem(value: 'tech_score', child: Text('Sort by Tech Score')),
                  PopupMenuItem(value: 'master_score', child: Text('Sort by Master Alpha Score')),
                  PopupMenuItem(value: 'dayChangePct', child: Text('Sort by 1D % Change')),
                  PopupMenuItem(value: 'chg5mPct', child: Text('Sort by 5M % Change')),
                  PopupMenuItem(value: 'upside', child: Text('Sort by 1Y Forecast Upside')),
                  PopupMenuItem(value: 'todayPe', child: Text('Sort by P/E Ratio')),
                  PopupMenuItem(value: 'valDiscount', child: Text('Sort by Margin of Safety Discount')),
                  PopupMenuItem(value: 'mcapCr', child: Text('Sort by Market Cap')),
                  PopupMenuItem(value: 'volume', child: Text('Sort by Volume')),
                  PopupMenuItem(value: 'cmp', child: Text('Sort by CMP Price')),
                  PopupMenuItem(value: 'symbol', child: Text('Sort by Symbol (A-Z)')),
                ],
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.blue(context).withAlpha(20),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: AppColors.blue(context).withAlpha(80)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.sort_rounded, size: 14, color: AppColors.blue(context)),
                      const SizedBox(width: 4),
                      Text(
                        'Sort: ${provider.sortColumn.replaceAll('_', ' ')} ${provider.isAscending ? '▲' : '▼'}',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppColors.blue(context),
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTableModeBtn(BuildContext context, MarketProvider provider, {required String mode, required String label, required IconData icon}) {
    final isSelected = provider.tableMode == mode;
    return InkWell(
      onTap: () => provider.setTableMode(mode),
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.blue(context) : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 13, color: isSelected ? Colors.white : AppColors.textSecondary(context)),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                color: isSelected ? Colors.white : AppColors.textSecondary(context),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildViewBtn(BuildContext context, MarketProvider provider, {required String mode, required IconData icon, required String tip}) {
    final isSelected = provider.viewMode == mode;
    return Tooltip(
      message: tip,
      child: InkWell(
        onTap: () => provider.setViewMode(mode),
        borderRadius: BorderRadius.circular(6),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.blue(context) : Colors.transparent,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Icon(
            icon,
            size: 16,
            color: isSelected ? Colors.white : AppColors.textSecondary(context),
          ),
        ),
      ),
    );
  }

  // ==================== CONTENT ROUTER ====================
  Widget _buildStockContent(BuildContext context, MarketProvider provider, {required bool isDesktop}) {
    if (provider.viewMode == 'TABLE') {
      return _buildInstitutionalTable(context, provider);
    } else if (provider.viewMode == 'GRID') {
      return _buildGridContent(context, provider);
    }
    // Default SPLIT list
    return ListView.separated(
      itemCount: provider.stocks.length,
      separatorBuilder: (context, index) => Divider(
        height: 1,
        color: AppColors.border(context).withAlpha(120),
      ),
      itemBuilder: (context, index) {
        final stock = provider.stocks[index];
        final isSelected = provider.selectedStock?.symbol == stock.symbol;
        return _buildDesktopStockTile(context, stock, provider, isSelected: isSelected);
      },
    );
  }

  // ==================== INSTITUTIONAL TABLE VIEW ====================
  Widget _buildInstitutionalTable(BuildContext context, MarketProvider provider) {
    final isTech = provider.tableMode == 'TECHNICAL';

    return SingleChildScrollView(
      scrollDirection: Axis.vertical,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(AppColors.surface(context)),
          headingTextStyle: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w800,
            color: AppColors.textMuted(context),
            letterSpacing: 0.5,
          ),
          dataRowMinHeight: 46,
          dataRowMaxHeight: 46,
          showCheckboxColumn: false,
          columns: isTech ? _buildTechnicalColumns(provider) : _buildFundamentalColumns(provider),
          rows: provider.stocks.map((stock) {
            return isTech
                ? _buildTechnicalRow(context, stock, provider)
                : _buildFundamentalRow(context, stock, provider);
          }).toList(),
        ),
      ),
    );
  }

  List<DataColumn> _buildTechnicalColumns(MarketProvider provider) {
    return [
      const DataColumn(label: Text('⭐')),
      _sortableCol(provider, 'SYMBOL', 'symbol'),
      _sortableCol(provider, 'COMPANY', 'name'),
      _sortableCol(provider, 'CMP (₹)', 'cmp'),
      _sortableCol(provider, '1D %', 'dayChangePct'),
      _sortableCol(provider, '5M %', 'chg5mPct'),
      _sortableCol(provider, 'ACTION / VERDICT', 'action'),
      const DataColumn(label: Text('ENTRY ZONE')),
      const DataColumn(label: Text('HARD SL')),
      const DataColumn(label: Text('TARGET 1 / 2')),
      _sortableCol(provider, 'R:R', 'rrRatio'),
      const DataColumn(label: Text('PIVOT S1/R1')),
      _sortableCol(provider, 'RSI (14)', 'rsi'),
      _sortableCol(provider, 'DIST 52W', 'dist52wHigh'),
      _sortableCol(provider, 'TECH', 'tech_score'),
      _sortableCol(provider, 'MASTER', 'master_score'),
      _sortableCol(provider, 'UPSIDE %', 'upside'),
      const DataColumn(label: Text('INSPECT')),
    ];
  }

  List<DataColumn> _buildFundamentalColumns(MarketProvider provider) {
    return [
      const DataColumn(label: Text('⭐')),
      _sortableCol(provider, 'RANK', 'rank'),
      _sortableCol(provider, 'SYMBOL', 'symbol'),
      _sortableCol(provider, 'COMPANY', 'name'),
      _sortableCol(provider, 'SECTOR', 'sector'),
      _sortableCol(provider, 'MCAP (₹ CR)', 'mcapCr'),
      _sortableCol(provider, 'MASTER SCORE', 'master_score'),
      const DataColumn(label: Text('CONFLUENCE TIER')),
      _sortableCol(provider, 'FORECAST UPSIDE', 'upside'),
      _sortableCol(provider, '1Y TARGET', 'target_price'),
      const DataColumn(label: Text('CONSENSUS')),
      _sortableCol(provider, 'FUNDA (30%)', 'fundaScore'),
      _sortableCol(provider, 'TECH (30%)', 'tech_score'),
      _sortableCol(provider, 'MOOD (20%)', 'moodScore'),
      _sortableCol(provider, 'LIVE CMP (₹)', 'cmp'),
      _sortableCol(provider, '1D MOVE', 'dayChangePct'),
      _sortableCol(provider, '1W MOVE', 'weekChangePct'),
      _sortableCol(provider, 'P/E', 'todayPe'),
      _sortableCol(provider, 'P/B', 'todayPb'),
      _sortableCol(provider, 'PEG', 'todayPeg'),
      _sortableCol(provider, 'STREAK', 'streakPat'),
      const DataColumn(label: Text('ACTION')),
    ];
  }

  DataColumn _sortableCol(MarketProvider provider, String title, String colKey) {
    final isSelected = provider.sortColumn == colKey;
    final arrow = isSelected ? (provider.isAscending ? ' ▲' : ' ▼') : '';
    return DataColumn(
      label: InkWell(
        onTap: () => provider.sortByColumn(colKey),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(title, style: TextStyle(color: isSelected ? AppColors.blue(context) : null, fontWeight: FontWeight.w800)),
            Text(arrow, style: TextStyle(color: AppColors.blue(context), fontSize: 10)),
          ],
        ),
      ),
    );
  }

  DataRow _buildTechnicalRow(BuildContext context, Stock stock, MarketProvider provider) {
    final isUp = stock.dayChange >= 0;
    final chgColor = isUp ? AppColors.green(context) : AppColors.red(context);
    final chgSign = isUp ? '+' : '';
    final m5Up = stock.chg5mPct >= 0;
    final m5Color = m5Up ? AppColors.green(context) : AppColors.red(context);

    return DataRow(
      onSelectChanged: (_) {
        provider.selectStock(stock);
        if (MediaQuery.of(context).size.width < 1000) {
          Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
        }
      },
      cells: [
        DataCell(
          IconButton(
            icon: Icon(
              stock.isBucket ? Icons.star_rounded : Icons.star_outline_rounded,
              color: stock.isBucket ? AppTheme.amberGold : AppColors.textMuted(context),
              size: 18,
            ),
            onPressed: () => provider.toggleStockInBucket(stock.symbol),
          ),
        ),
        DataCell(
          Text(stock.symbol, style: TextStyle(fontWeight: FontWeight.w900, fontFamily: 'monospace', color: AppColors.textPrimary(context))),
        ),
        DataCell(
          SizedBox(
            width: 140,
            child: Text(stock.name, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context))),
          ),
        ),
        DataCell(
          Text('₹${stock.cmp.toStringAsFixed(2)}', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, fontFamily: 'monospace', color: AppColors.textPrimary(context))),
        ),
        DataCell(
          Text('$chgSign${stock.dayChangePct.toStringAsFixed(2)}%', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: chgColor, fontFamily: 'monospace')),
        ),
        DataCell(
          Text('${stock.chg5mPct >= 0 ? '+' : ''}${stock.chg5mPct.toStringAsFixed(2)}%', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: m5Color, fontFamily: 'monospace')),
        ),
        DataCell(
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: AppTheme.amberGold.withAlpha(20),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(stock.action, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.amberGold)),
          ),
        ),
        DataCell(
          Text('₹${stock.cmp.toStringAsFixed(1)} - ₹${(stock.cmp * 1.02).toStringAsFixed(1)}', style: const TextStyle(fontSize: 10, fontFamily: 'monospace')),
        ),
        DataCell(
          Text('₹${stock.stopLoss.toStringAsFixed(1)}', style: TextStyle(fontSize: 11, color: AppColors.red(context), fontFamily: 'monospace', fontWeight: FontWeight.w700)),
        ),
        DataCell(
          Text('₹${stock.target1.toStringAsFixed(1)} / ₹${stock.target2.toStringAsFixed(1)}', style: TextStyle(fontSize: 11, color: AppColors.green(context), fontFamily: 'monospace', fontWeight: FontWeight.w700)),
        ),
        DataCell(
          Text('1:${stock.rrRatio.toStringAsFixed(1)}', style: const TextStyle(fontSize: 11, fontFamily: 'monospace', fontWeight: FontWeight.w700)),
        ),
        DataCell(
          Text('₹${stock.s1.toStringAsFixed(1)} / ₹${stock.r1.toStringAsFixed(1)}', style: const TextStyle(fontSize: 10, fontFamily: 'monospace')),
        ),
        DataCell(
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
            decoration: BoxDecoration(
              color: (stock.rsi > 70 ? AppColors.red(context) : (stock.rsi < 35 ? AppColors.green(context) : AppColors.blue(context))).withAlpha(20),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(stock.rsi.toStringAsFixed(1), style: const TextStyle(fontSize: 10, fontFamily: 'monospace', fontWeight: FontWeight.bold)),
          ),
        ),
        DataCell(
          Text('${stock.dist52wHigh >= 0 ? '+' : ''}${stock.dist52wHigh.toStringAsFixed(1)}%', style: const TextStyle(fontSize: 11, fontFamily: 'monospace')),
        ),
        DataCell(
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(color: AppColors.blue(context).withAlpha(20), borderRadius: BorderRadius.circular(4)),
            child: Text('${stock.techScore.toInt()}', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: AppColors.blue(context), fontFamily: 'monospace')),
          ),
        ),
        DataCell(
          Text(stock.masterScore.toStringAsFixed(1), style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900, fontFamily: 'monospace', color: AppTheme.amberGold)),
        ),
        DataCell(
          Text('+${(stock.forecast?.upsideMeanPct ?? 0).toStringAsFixed(1)}%', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.green(context), fontFamily: 'monospace')),
        ),
        DataCell(
          IconButton(
            icon: const Icon(Icons.arrow_forward_ios_rounded, size: 12),
            onPressed: () {
              provider.selectStock(stock);
              Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
            },
          ),
        ),
      ],
    );
  }

  DataRow _buildFundamentalRow(BuildContext context, Stock stock, MarketProvider provider) {
    final isUp = stock.dayChange >= 0;
    final chgColor = isUp ? AppColors.green(context) : AppColors.red(context);
    final chgSign = isUp ? '+' : '';

    return DataRow(
      onSelectChanged: (_) {
        provider.selectStock(stock);
        if (MediaQuery.of(context).size.width < 1000) {
          Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
        }
      },
      cells: [
        DataCell(
          IconButton(
            icon: Icon(
              stock.isBucket ? Icons.star_rounded : Icons.star_outline_rounded,
              color: stock.isBucket ? AppTheme.amberGold : AppColors.textMuted(context),
              size: 18,
            ),
            onPressed: () => provider.toggleStockInBucket(stock.symbol),
          ),
        ),
        DataCell(Text('#${stock.rank}', style: const TextStyle(fontSize: 10, fontFamily: 'monospace'))),
        DataCell(Text(stock.symbol, style: TextStyle(fontWeight: FontWeight.w900, fontFamily: 'monospace', color: AppColors.textPrimary(context)))),
        DataCell(
          SizedBox(
            width: 140,
            child: Text(stock.name, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context))),
          ),
        ),
        DataCell(Text(stock.sector, style: TextStyle(fontSize: 10, color: AppColors.textMuted(context)))),
        DataCell(Text('₹${stock.mcapCr.toStringAsFixed(0)} Cr', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(color: AppTheme.amberGold.withAlpha(20), borderRadius: BorderRadius.circular(4)),
            child: Text(stock.masterScore.toStringAsFixed(1), style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: AppTheme.amberGold, fontFamily: 'monospace')),
          ),
        ),
        DataCell(Text(stock.masterCategory, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600))),
        DataCell(
          Text('+${(stock.forecast?.upsideMeanPct ?? 0).toStringAsFixed(1)}%', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.green(context), fontFamily: 'monospace')),
        ),
        DataCell(Text('₹${(stock.forecast?.meanTarget ?? 0).toStringAsFixed(1)}', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(color: AppColors.green(context).withAlpha(20), borderRadius: BorderRadius.circular(4)),
            child: Text(stock.consensus, style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppColors.green(context))),
          ),
        ),
        DataCell(Text('${stock.fundaScore.toInt()}', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(Text('${stock.techScore.toInt()}', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(Text('${stock.moodScore.toInt()}', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(Text('₹${stock.cmp.toStringAsFixed(2)}', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace'))),
        DataCell(Text('$chgSign${stock.dayChangePct.toStringAsFixed(2)}%', style: TextStyle(fontSize: 11, color: chgColor, fontWeight: FontWeight.bold, fontFamily: 'monospace'))),
        DataCell(Text('${stock.weekChangePct >= 0 ? '+' : ''}${stock.weekChangePct.toStringAsFixed(1)}%', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(Text('${stock.todayPe.toStringAsFixed(1)}x', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(Text('${stock.todayPb.toStringAsFixed(1)}x', style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(Text(stock.todayPeg.toStringAsFixed(2), style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
        DataCell(Text('${stock.streakPat} Qtrs', style: const TextStyle(fontSize: 10, fontFamily: 'monospace'))),
        DataCell(
          IconButton(
            icon: const Icon(Icons.arrow_forward_ios_rounded, size: 12),
            onPressed: () {
              provider.selectStock(stock);
              Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
            },
          ),
        ),
      ],
    );
  }

  // ==================== CARD GRID VIEW ====================
  Widget _buildGridContent(BuildContext context, MarketProvider provider) {
    return GridView.builder(
      padding: const EdgeInsets.all(12),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 350,
        mainAxisExtent: 160,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
      ),
      itemCount: provider.stocks.length,
      itemBuilder: (context, index) {
        final stock = provider.stocks[index];
        final isSelected = provider.selectedStock?.symbol == stock.symbol;
        final isUp = stock.dayChange >= 0;
        final chgColor = isUp ? AppColors.green(context) : AppColors.red(context);
        final chgSign = isUp ? '+' : '';

        return InteractiveScaleCard(
          onTap: () {
            provider.selectStock(stock);
            if (MediaQuery.of(context).size.width < 1000) {
              Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
            }
          },
          borderRadius: BorderRadius.circular(12),
          hoverBorderColor: AppColors.blue(context),
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: AppColors.cardDecoration(context, isSelected: isSelected),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
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
                                fontSize: 14,
                                fontWeight: FontWeight.w900,
                                fontFamily: 'monospace',
                                color: AppColors.textPrimary(context),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                          decoration: BoxDecoration(
                            color: AppColors.blue(context).withAlpha(20),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            '${stock.techScore.toInt()}',
                            style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.blue(context)),
                          ),
                        ),
                      ],
                    ),
                    AnimatedFavoriteStar(
                      isFavorite: stock.isBucket,
                      onTap: () => provider.toggleStockInBucket(stock.symbol),
                      size: 19,
                    ),
                  ],
                ),
                Text(
                  stock.name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context)),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    PriceFlashText(
                      value: stock.cmp,
                      formattedText: '₹${stock.cmp.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                        fontFamily: 'monospace',
                        color: AppColors.textPrimary(context),
                      ),
                    ),
                    PriceFlashText(
                      value: stock.dayChangePct,
                      formattedText: '$chgSign${stock.dayChangePct.toStringAsFixed(2)}%',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: chgColor,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Target: ₹${(stock.forecast?.meanTarget ?? stock.target1).toStringAsFixed(1)} (+${(stock.forecast?.upsideMeanPct ?? 0).toStringAsFixed(1)}%)',
                      style: TextStyle(fontSize: 10, color: AppColors.green(context), fontWeight: FontWeight.bold),
                    ),
                    Text(
                      'P/E: ${stock.todayPe.toStringAsFixed(1)}x',
                      style: TextStyle(fontSize: 10, color: AppColors.textMuted(context), fontFamily: 'monospace'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // ==================== MASTER LIST TILE (SPLIT VIEW) ====================
  Widget _buildDesktopStockTile(BuildContext context, Stock stock, MarketProvider provider, {required bool isSelected}) {
    final isUp = stock.dayChange >= 0;
    final chgColor = isUp ? AppColors.green(context) : AppColors.red(context);
    final chgSign = isUp ? '+' : '';

    return InkWell(
      onTap: () => provider.selectStock(stock),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.blue(context).withAlpha(22) : Colors.transparent,
          border: isSelected
              ? Border(left: BorderSide(color: AppColors.blue(context), width: 3))
              : null,
        ),
        child: Row(
          children: [
            AnimatedFavoriteStar(
              isFavorite: stock.isBucket,
              onTap: () => provider.toggleStockInBucket(stock.symbol),
              size: 18,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
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
                              fontSize: 13,
                              fontWeight: FontWeight.w900,
                              fontFamily: 'monospace',
                              color: AppColors.textPrimary(context),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                        decoration: BoxDecoration(
                          color: AppColors.blue(context).withAlpha(20),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '${stock.techScore.toInt()}',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.blue(context)),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    stock.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context)),
                  ),
                ],
              ),
            ),
            SparklineChart(candles: stock.candles, color: chgColor, width: 50, height: 18),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                PriceFlashText(
                  value: stock.cmp,
                  formattedText: '₹${stock.cmp.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    fontFamily: 'monospace',
                    color: AppColors.textPrimary(context),
                  ),
                ),
                PriceFlashText(
                  value: stock.dayChangePct,
                  formattedText: '$chgSign${stock.dayChangePct.toStringAsFixed(2)}%',
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
      ),
    );
  }

  // ==================== MOBILE LIST TILE ====================
  Widget _buildMobileStockTile(BuildContext context, Stock stock, MarketProvider provider) {
    final isUp = stock.dayChange >= 0;
    final chgColor = isUp ? AppColors.green(context) : AppColors.red(context);
    final chgSign = isUp ? '+' : '';

    return InteractiveScaleCard(
      onTap: () {
        provider.selectStock(stock);
        Navigator.of(context).push(MaterialPageRoute(builder: (_) => StockDetailScreen(stock: stock)));
      },
      borderRadius: BorderRadius.circular(10),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Row(
          children: [
            AnimatedFavoriteStar(
              isFavorite: stock.isBucket,
              onTap: () => provider.toggleStockInBucket(stock.symbol),
              size: 20,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
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
                              fontSize: 14,
                              fontWeight: FontWeight.w900,
                              fontFamily: 'monospace',
                              color: AppColors.textPrimary(context),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                        decoration: BoxDecoration(
                          color: AppColors.blue(context).withAlpha(20),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '${stock.techScore.toInt()}',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.blue(context)),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        stock.action,
                        style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.amberGold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${stock.name} • ${stock.sector}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context)),
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
                    fontSize: 14,
                    fontWeight: FontWeight.w900,
                    fontFamily: 'monospace',
                    color: AppColors.textPrimary(context),
                  ),
                ),
                PriceFlashText(
                  value: stock.dayChangePct,
                  formattedText: '$chgSign${stock.dayChangePct.toStringAsFixed(2)}%',
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
      ),
    );
  }

  // ==================== EMPTY STATE ====================
  Widget _buildEmptyState(BuildContext context, MarketProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.filter_alt_off_rounded, size: 48, color: AppColors.textMuted(context)),
          const SizedBox(height: 12),
          Text(
            'No stocks match your filter criteria',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary(context)),
          ),
          const SizedBox(height: 4),
          Text(
            'Try resetting your smart filters or choosing a different basket',
            style: TextStyle(fontSize: 12, color: AppColors.textSecondary(context)),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.blue(context),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () => provider.resetSmartFilters(),
            icon: const Icon(Icons.refresh_rounded, size: 16),
            label: const Text('Reset All Filters'),
          ),
        ],
      ),
    );
  }
}
