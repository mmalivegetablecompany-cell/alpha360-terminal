import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/market_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/network_settings_dialog.dart';
import '../widgets/micro_animations.dart';
import '../services/alert_service.dart';
import 'dashboard_screen.dart';
import 'buy_radar_screen.dart';
import 'news_and_orders_screen.dart';

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;
  bool _isSidebarExpanded = true;

  final List<Widget> _screens = const [
    DashboardScreen(),
    BuyRadarScreen(),
    NewsAndOrdersScreen(),
  ];

  StreamSubscription<MarketAlert>? _alertSub;

  @override
  void initState() {
    super.initState();
    _alertSub = AlertService().alertStream.listen((alert) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: alert.type == AlertType.stopLossHit ? const Color(0xFF991B1B) : const Color(0xFF0F172A),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            content: Row(
              children: [
                Icon(
                  alert.type == AlertType.stopLossHit ? Icons.warning_rounded : Icons.notifications_active_rounded,
                  color: alert.type == AlertType.stopLossHit ? Colors.white : AppTheme.amberGold,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(alert.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.white)),
                      Text(alert.message, style: const TextStyle(fontSize: 10, color: Colors.white70)),
                    ],
                  ),
                ),
              ],
            ),
            duration: const Duration(seconds: 4),
          ),
        );
      }
    });
  }

  @override
  void dispose() {
    _alertSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();
    final isDesktop = MediaQuery.of(context).size.width >= 900;
    final isDark = AppColors.isDark(context);

    return Scaffold(
      backgroundColor: AppColors.bg(context),
      appBar: isDesktop
          ? null
          : AppBar(
              backgroundColor: AppColors.surface(context),
              title: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF0284C7), Color(0xFF38BDF8)],
                      ),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text(
                      '360°',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: Colors.white),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Stock Terminal',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textPrimary(context),
                    ),
                  ),
                ],
              ),
              actions: [
                _buildLiveStatusPill(provider, compact: true),
                IconButton(
                  tooltip: isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode',
                  icon: Icon(
                    isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
                    color: isDark ? AppTheme.amberGold : AppTheme.primaryBlue,
                    size: 20,
                  ),
                  onPressed: () => provider.toggleTheme(),
                ),
                const SizedBox(width: 4),
              ],
            ),
      body: isDesktop
          ? Row(
              children: [
                // Custom Desktop Sidebar
                _buildDesktopSidebar(context, provider),
                const VerticalDivider(width: 1, thickness: 1),
                Expanded(child: _screens[_currentIndex]),
              ],
            )
          : _screens[_currentIndex],
      bottomNavigationBar: isDesktop
          ? null
          : NavigationBar(
              selectedIndex: _currentIndex,
              onDestinationSelected: (index) => setState(() => _currentIndex = index),
              destinations: [
                const NavigationDestination(
                  icon: Icon(Icons.candlestick_chart_outlined),
                  selectedIcon: Icon(Icons.candlestick_chart_rounded),
                  label: 'Screener',
                ),
                NavigationDestination(
                  icon: Badge(
                    label: Text('${provider.stocks.where((s) => s.techScore >= 80).length}'),
                    child: const Icon(Icons.radar_outlined),
                  ),
                  selectedIcon: Badge(
                    label: Text('${provider.stocks.where((s) => s.techScore >= 80).length}'),
                    child: const Icon(Icons.radar_rounded),
                  ),
                  label: 'Buy Radar',
                ),
                NavigationDestination(
                  icon: Badge(
                    label: Text('${provider.corporateOrders.length + provider.news.length}'),
                    child: const Icon(Icons.newspaper_outlined),
                  ),
                  selectedIcon: Badge(
                    label: Text('${provider.corporateOrders.length + provider.news.length}'),
                    child: const Icon(Icons.newspaper_rounded),
                  ),
                  label: 'News & Orders',
                ),
              ],
            ),
    );
  }

  Widget _buildDesktopSidebar(BuildContext context, MarketProvider provider) {
    final isDark = AppColors.isDark(context);
    final sidebarWidth = _isSidebarExpanded ? 230.0 : 74.0;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      width: sidebarWidth,
      color: AppColors.surface(context),
      child: Column(
        children: [
          // Sidebar Branding Header
          Container(
            padding: EdgeInsets.symmetric(
              horizontal: _isSidebarExpanded ? 14 : 10,
              vertical: 14,
            ),
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.border(context), width: 0.8)),
            ),
            child: Row(
              mainAxisAlignment: _isSidebarExpanded ? MainAxisAlignment.spaceBetween : MainAxisAlignment.center,
              children: [
                if (_isSidebarExpanded)
                  Expanded(
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 4),
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [Color(0xFF0284C7), Color(0xFF38BDF8)],
                            ),
                            borderRadius: BorderRadius.circular(6),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF0284C7).withAlpha(80),
                                blurRadius: 6,
                              ),
                            ],
                          ),
                          child: const Text(
                            '360°',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: Colors.white),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'TERMINAL',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w900,
                                  letterSpacing: 0.5,
                                  color: AppColors.textPrimary(context),
                                ),
                              ),
                              Text(
                                'Indian Equities',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.textMuted(context),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                IconButton(
                  icon: Icon(
                    _isSidebarExpanded ? Icons.chevron_left_rounded : Icons.chevron_right_rounded,
                    size: 20,
                    color: AppColors.textSecondary(context),
                  ),
                  tooltip: _isSidebarExpanded ? 'Collapse Sidebar' : 'Expand Sidebar',
                  onPressed: () => setState(() => _isSidebarExpanded = !_isSidebarExpanded),
                ),
              ],
            ),
          ),

          // Navigation Links
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
              children: [
                _buildNavItem(
                  context,
                  index: 0,
                  icon: Icons.candlestick_chart_rounded,
                  label: 'Watchlist & Screener',
                  badgeText: '${provider.stocks.length}',
                  badgeColor: AppColors.blue(context),
                ),
                const SizedBox(height: 4),
                _buildNavItem(
                  context,
                  index: 1,
                  icon: Icons.radar_rounded,
                  label: 'Institutional Radar',
                  badgeText: '${provider.stocks.where((s) => s.techScore >= 80).length} Setups',
                  badgeColor: AppTheme.amberGold,
                ),
                const SizedBox(height: 4),
                _buildNavItem(
                  context,
                  index: 2,
                  icon: Icons.newspaper_rounded,
                  label: 'Orders & News',
                  badgeText: '${provider.corporateOrders.length + provider.news.length}',
                  badgeColor: AppColors.green(context),
                ),
              ],
            ),
          ),

          // Sidebar Footer: Live Cloud Sync & Theme Switcher
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.border(context), width: 0.8)),
            ),
            child: Column(
              children: [
                _buildLiveStatusPill(provider, compact: !_isSidebarExpanded),
                const SizedBox(height: 10),
                // Theme Toggle Switcher Button
                InkWell(
                  onTap: () => provider.toggleTheme(),
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding: EdgeInsets.symmetric(
                      horizontal: _isSidebarExpanded ? 10 : 6,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: isDark ? const Color(0xFF131D31) : const Color(0xFFF1F5F9),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.border(context)),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          isDark ? Icons.dark_mode_rounded : Icons.light_mode_rounded,
                          size: 16,
                          color: isDark ? AppTheme.amberGold : AppTheme.primaryBlue,
                        ),
                        if (_isSidebarExpanded) ...[
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              isDark ? 'Dark Obsidian' : 'Clean Light',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: AppColors.textPrimary(context),
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                            decoration: BoxDecoration(
                              color: isDark ? Colors.white.withAlpha(20) : Colors.black.withAlpha(15),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              'SWITCH',
                              style: TextStyle(
                                fontSize: 8,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textSecondary(context),
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(
    BuildContext context, {
    required int index,
    required IconData icon,
    required String label,
    required String badgeText,
    required Color badgeColor,
  }) {
    final isSelected = _currentIndex == index;
    final isDark = AppColors.isDark(context);

    return Tooltip(
      message: _isSidebarExpanded ? '' : label,
      child: InkWell(
        onTap: () => setState(() => _currentIndex = index),
        borderRadius: BorderRadius.circular(10),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOutCubic,
          padding: EdgeInsets.symmetric(
            horizontal: _isSidebarExpanded ? 10 : 8,
            vertical: 10,
          ),
          decoration: BoxDecoration(
            color: isSelected
                ? (isDark ? const Color(0x280EA5E9) : const Color(0x1C0EA5E9))
                : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected ? AppTheme.primaryBlue.withAlpha(120) : Colors.transparent,
              width: 0.8,
            ),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: AppTheme.primaryBlue.withAlpha(25),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ]
                : null,
          ),
          child: Row(
            mainAxisAlignment: _isSidebarExpanded ? MainAxisAlignment.start : MainAxisAlignment.center,
            children: [
              if (isSelected && _isSidebarExpanded) ...[
                Container(
                  width: 3,
                  height: 16,
                  margin: const EdgeInsets.only(right: 8),
                  decoration: BoxDecoration(
                    color: AppColors.blue(context),
                    borderRadius: BorderRadius.circular(2),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.blue(context).withAlpha(150),
                        blurRadius: 6,
                      ),
                    ],
                  ),
                ),
              ],
              Icon(
                icon,
                size: 20,
                color: isSelected ? AppColors.blue(context) : AppColors.textMuted(context),
              ),
              if (_isSidebarExpanded) ...[
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    label,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                      color: isSelected ? AppColors.textPrimary(context) : AppColors.textSecondary(context),
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: badgeColor.withAlpha(25),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: badgeColor.withAlpha(50), width: 0.8),
                  ),
                  child: Text(
                    badgeText,
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                      color: badgeColor,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLiveStatusPill(MarketProvider provider, {bool compact = false}) {
    final isLive = provider.isLiveConnected;
    final color = isLive ? const Color(0xFF00E676) : const Color(0xFFFFB300);

    if (compact) {
      return InkWell(
        onTap: () => showDialog(context: context, builder: (_) => const NetworkSettingsDialog()),
        borderRadius: BorderRadius.circular(14),
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 6),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withAlpha(20),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: color.withAlpha(100), width: 0.8),
            boxShadow: [
              BoxShadow(
                color: color.withAlpha(30),
                blurRadius: 6,
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              PulseGlowDot(color: color, size: 6, isPulsing: isLive),
              const SizedBox(width: 5),
              Text(
                isLive ? 'LIVE' : 'OFFLINE',
                style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w900,
                  color: color,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
        ),
      );
    }

    return InkWell(
      onTap: () => showDialog(context: context, builder: (_) => const NetworkSettingsDialog()),
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: color.withAlpha(18),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withAlpha(90), width: 0.8),
          boxShadow: [
            BoxShadow(
              color: color.withAlpha(25),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            PulseGlowDot(color: color, size: 7, isPulsing: isLive),
            const SizedBox(width: 8),
            Text(
              isLive ? 'Live Cloud Sync' : 'Offline Mode',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                color: color,
                fontFamily: 'monospace',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

