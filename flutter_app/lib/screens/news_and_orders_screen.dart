import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/market_provider.dart';
import '../models/corporate_order.dart';
import '../models/news_item.dart';
import '../theme/app_theme.dart';
import '../widgets/micro_animations.dart';

class NewsAndOrdersScreen extends StatefulWidget {
  const NewsAndOrdersScreen({super.key});

  @override
  State<NewsAndOrdersScreen> createState() => _NewsAndOrdersScreenState();
}

class _NewsAndOrdersScreenState extends State<NewsAndOrdersScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _orderFilter = 'ALL';
  String _newsSentimentFilter = 'ALL';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();
    final isDesktop = MediaQuery.of(context).size.width >= 900;

    return Scaffold(
      backgroundColor: AppColors.bg(context),
      appBar: isDesktop
          ? null
          : PreferredSize(
              preferredSize: const Size.fromHeight(48),
              child: Container(
                color: AppColors.surface(context),
                child: TabBar(
                  controller: _tabController,
                  indicatorColor: AppColors.green(context),
                  labelColor: AppColors.green(context),
                  unselectedLabelColor: AppColors.textSecondary(context),
                  labelStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                  unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                  tabs: [
                    Tab(text: '🏆 Corporate Orders (${provider.corporateOrders.length})'),
                    Tab(text: '📰 Live Market News (${provider.news.length})'),
                  ],
                ),
              ),
            ),
      body: isDesktop
          ? _buildDesktopDualPane(context, provider)
          : TabBarView(
              controller: _tabController,
              children: [
                _buildCorporateOrdersSection(context, provider),
                _buildNewsListSection(context, provider),
              ],
            ),
    );
  }

  // ==================== DESKTOP DUAL PANE ====================
  Widget _buildDesktopDualPane(BuildContext context, MarketProvider provider) {
    return Row(
      children: [
        // Left Column: Corporate Announcements
        Expanded(
          flex: 1,
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: AppColors.surface(context),
                  border: Border(
                    bottom: BorderSide(color: AppColors.border(context), width: 0.8),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.military_tech_rounded, size: 18, color: AppTheme.amberGold),
                        const SizedBox(width: 8),
                        Text(
                          'CORPORATE ANNOUNCEMENTS & ORDERS',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.5,
                            color: AppColors.textPrimary(context),
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppTheme.amberGold.withAlpha(25),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${provider.corporateOrders.length} FILINGS',
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.amberGold),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(child: _buildCorporateOrdersSection(context, provider)),
            ],
          ),
        ),

        const VerticalDivider(width: 1, thickness: 1),

        // Right Column: Live Market News Feed
        Expanded(
          flex: 1,
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: AppColors.surface(context),
                  border: Border(
                    bottom: BorderSide(color: AppColors.border(context), width: 0.8),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.newspaper_rounded, size: 18, color: AppColors.blue(context)),
                        const SizedBox(width: 8),
                        Text(
                          'REAL-TIME MARKET NEWS WIRE',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.5,
                            color: AppColors.textPrimary(context),
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppColors.blue(context).withAlpha(25),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${provider.news.length} DISPATCHES',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.blue(context)),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(child: _buildNewsListSection(context, provider)),
            ],
          ),
        ),
      ],
    );
  }

  // ==================== CORPORATE ORDERS ====================
  Widget _buildCorporateOrdersSection(BuildContext context, MarketProvider provider) {
    if (provider.corporateOrders.isEmpty) {
      return Center(
        child: Text('No corporate announcements loaded', style: TextStyle(color: AppColors.textMuted(context))),
      );
    }

    final orders = _orderFilter == 'ALL'
        ? provider.corporateOrders
        : provider.corporateOrders.where((o) => o.category.contains(_orderFilter)).toList();

    return Column(
      children: [
        // Category Filter Chips
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          color: AppColors.surface(context),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterPill('ALL', 'All Filings', _orderFilter == 'ALL', (v) => setState(() => _orderFilter = v)),
                const SizedBox(width: 6),
                _buildFilterPill('ORDER', '🏆 Order Wins', _orderFilter == 'ORDER', (v) => setState(() => _orderFilter = v)),
                const SizedBox(width: 6),
                _buildFilterPill('CAPEX', '🏭 Capex Expansion', _orderFilter == 'CAPEX', (v) => setState(() => _orderFilter = v)),
                const SizedBox(width: 6),
                _buildFilterPill('DIVIDEND', '💰 Dividends / Results', _orderFilter == 'DIVIDEND', (v) => setState(() => _orderFilter = v)),
              ],
            ),
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: orders.length,
            separatorBuilder: (context, index) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final order = orders[index];
              return _buildOrderCard(context, order);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildOrderCard(BuildContext context, CorporateOrder order) {
    Color badgeColor = AppColors.blue(context);
    if (order.category.contains('ORDER')) badgeColor = AppTheme.amberGold;
    if (order.category.contains('CAPEX')) badgeColor = AppColors.green(context);
    if (order.category.contains('DIVIDEND')) badgeColor = AppTheme.purpleViolet;

    return InteractiveScaleCard(
      borderRadius: BorderRadius.circular(12),
      hoverBorderColor: badgeColor,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: AppColors.cardDecoration(context, borderRadius: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  order.symbol,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w900,
                    color: AppColors.textPrimary(context),
                    fontFamily: 'monospace',
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: badgeColor.withAlpha(25),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: badgeColor.withAlpha(80)),
                  ),
                  child: Text(
                    order.category,
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: badgeColor),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              order.headline,
              style: TextStyle(
                fontSize: 13,
                color: AppColors.textPrimary(context),
                height: 1.4,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Icon(Icons.calendar_today_rounded, size: 12, color: AppColors.textMuted(context)),
                const SizedBox(width: 4),
                Text(
                  order.dateTime,
                  style: TextStyle(fontSize: 11, color: AppColors.textMuted(context), fontFamily: 'monospace'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ==================== LIVE MARKET NEWS ====================
  Widget _buildNewsListSection(BuildContext context, MarketProvider provider) {
    if (provider.news.isEmpty) {
      return Center(
        child: Text('No news articles loaded', style: TextStyle(color: AppColors.textMuted(context))),
      );
    }

    final newsList = _newsSentimentFilter == 'ALL'
        ? provider.news
        : provider.news.where((n) => n.sentiment == _newsSentimentFilter).toList();

    return Column(
      children: [
        // Sentiment Filter Chips
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          color: AppColors.surface(context),
          child: Row(
            children: [
              _buildFilterPill('ALL', 'All News', _newsSentimentFilter == 'ALL', (v) => setState(() => _newsSentimentFilter = v)),
              const SizedBox(width: 6),
              _buildFilterPill('BULLISH', '🟢 Bullish Dispatches', _newsSentimentFilter == 'BULLISH', (v) => setState(() => _newsSentimentFilter = v)),
              const SizedBox(width: 6),
              _buildFilterPill('BEARISH', '🔴 Bearish Dispatches', _newsSentimentFilter == 'BEARISH', (v) => setState(() => _newsSentimentFilter = v)),
            ],
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: newsList.length,
            separatorBuilder: (context, index) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final item = newsList[index];
              return _buildNewsCard(context, item);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildNewsCard(BuildContext context, NewsItem item) {
    Color sentColor = AppColors.textSecondary(context);
    if (item.sentiment == 'BULLISH') sentColor = AppColors.neonGreen(context);
    if (item.sentiment == 'BEARISH') sentColor = AppColors.neonRed(context);

    return InteractiveScaleCard(
      borderRadius: BorderRadius.circular(12),
      hoverBorderColor: sentColor,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: AppColors.cardDecoration(context, borderRadius: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                  decoration: BoxDecoration(
                    color: sentColor.withAlpha(25),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: sentColor.withAlpha(90), width: 0.8),
                  ),
                  child: Text(
                    item.sentiment,
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: sentColor),
                  ),
                ),
                Row(
                  children: [
                    Icon(Icons.schedule_rounded, size: 12, color: AppColors.textMuted(context)),
                    const SizedBox(width: 4),
                    Text(
                      item.pubDate.length > 16 ? item.pubDate.substring(0, 16) : item.pubDate,
                      style: TextStyle(fontSize: 10, color: AppColors.textMuted(context)),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              item.title,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary(context),
                height: 1.35,
              ),
            ),
            const SizedBox(height: 8),
            if (item.link.isNotEmpty)
              InkWell(
                onTap: () async {
                  final uri = Uri.parse(item.link);
                  if (await canLaunchUrl(uri)) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                },
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Read Full Coverage',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.blue(context)),
                    ),
                    const SizedBox(width: 3),
                    Icon(Icons.open_in_new_rounded, size: 12, color: AppColors.blue(context)),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterPill(String value, String label, bool isSelected, Function(String) onSelect) {
    return InkWell(
      onTap: () => onSelect(value),
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.blue(context) : AppColors.bg(context),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.blue(context) : AppColors.border(context),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
            color: isSelected ? Colors.white : AppColors.textSecondary(context),
          ),
        ),
      ),
    );
  }
}

