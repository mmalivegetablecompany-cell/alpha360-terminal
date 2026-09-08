import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/market_provider.dart';
import '../theme/app_theme.dart';
import '../models/watchlist_constants.dart';

class SmartFilterDrawer extends StatelessWidget {
  const SmartFilterDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();
    final sf = provider.smartFilters;

    return Drawer(
      backgroundColor: AppColors.surface(context),
      width: 360,
      child: SafeArea(
        child: Column(
          children: [
            // Drawer Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              decoration: BoxDecoration(
                color: AppColors.card(context),
                border: Border(bottom: BorderSide(color: AppColors.border(context), width: 0.8)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(Icons.tune_rounded, color: AppColors.blue(context), size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Smart Screener',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w900,
                          color: AppColors.textPrimary(context),
                        ),
                      ),
                      if (provider.activeSmartFiltersCount > 0) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.blue(context),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            '${provider.activeSmartFiltersCount}',
                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                        ),
                      ],
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    color: AppColors.textSecondary(context),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),

            // Scrollable Filters Form
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Sector Selector
                  _buildDropdownTile(
                    context,
                    label: 'Economic Sector',
                    value: provider.selectedSector,
                    options: WatchlistConstants.allSectors.map((s) => DropdownMenuItem(value: s, child: Text(s, overflow: TextOverflow.ellipsis))).toList(),
                    onChanged: (val) => provider.setSelectedSector(val ?? 'All Sectors'),
                  ),

                  // Min Master Score Slider
                  const SizedBox(height: 12),
                  Text(
                    'Min Master Alpha Score: ${provider.minScoreSlider.toInt()}/100',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textPrimary(context)),
                  ),
                  Slider(
                    value: provider.minScoreSlider,
                    min: 0,
                    max: 95,
                    divisions: 19,
                    activeColor: AppColors.blue(context),
                    inactiveColor: AppColors.border(context),
                    onChanged: provider.setMinScoreSlider,
                  ),

                  const Divider(height: 24),
                  _buildSectionHeader(context, 'VALUATION MULTIPLES'),

                  // 1. Max P/E
                  _buildDropdownTile(
                    context,
                    label: 'P/E Multiple',
                    value: sf['max_pe'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any P/E')),
                      DropdownMenuItem(value: '15', child: Text('≤ 15 (Deep Value)')),
                      DropdownMenuItem(value: '25', child: Text('≤ 25 (Reasonable Value)')),
                      DropdownMenuItem(value: '40', child: Text('≤ 40 (Moderate Quality)')),
                      DropdownMenuItem(value: '60', child: Text('≤ 60 (Growth Valuation)')),
                      DropdownMenuItem(value: '80', child: Text('≤ 80 (High Multiple)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('max_pe', val ?? 'any'),
                  ),

                  // 2. Max P/B
                  _buildDropdownTile(
                    context,
                    label: 'P/B Ratio',
                    value: sf['max_pb'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any P/B')),
                      DropdownMenuItem(value: '2.0', child: Text('≤ 2.0 (Low Book Multiple)')),
                      DropdownMenuItem(value: '4.0', child: Text('≤ 4.0 (Balanced Asset Base)')),
                      DropdownMenuItem(value: '7.0', child: Text('≤ 7.0 (Capital Efficient)')),
                      DropdownMenuItem(value: '12.0', child: Text('≤ 12.0 (High ROE Premium)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('max_pb', val ?? 'any'),
                  ),

                  // 3. Max PEG
                  _buildDropdownTile(
                    context,
                    label: 'PEG Ratio (Peter Lynch)',
                    value: sf['max_peg'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any PEG')),
                      DropdownMenuItem(value: '1.0', child: Text('≤ 1.0 (Undervalued)')),
                      DropdownMenuItem(value: '1.5', child: Text('≤ 1.5 (Fair Growth Value)')),
                      DropdownMenuItem(value: '2.0', child: Text('≤ 2.0 (Reasonable Expansion)')),
                      DropdownMenuItem(value: '3.0', child: Text('≤ 3.0 (Momentum Growth)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('max_peg', val ?? 'any'),
                  ),

                  const Divider(height: 24),
                  _buildSectionHeader(context, 'FUNDAMENTAL COMPOUNDING'),

                  // 4. Min PAT Growth
                  _buildDropdownTile(
                    context,
                    label: 'YoY Net Profit (PAT) Growth',
                    value: sf['min_pat_growth'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any Growth')),
                      DropdownMenuItem(value: '15', child: Text('≥ +15% (Solid Compounder)')),
                      DropdownMenuItem(value: '20', child: Text('≥ +20% (High Growth)')),
                      DropdownMenuItem(value: '25', child: Text('≥ +25% (High Expansion)')),
                      DropdownMenuItem(value: '50', child: Text('≥ +50% (Hyper-Growth)')),
                      DropdownMenuItem(value: '100', child: Text('≥ +100% (Doubling Earnings)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('min_pat_growth', val ?? 'any'),
                  ),

                  // 5. Min Consecutive Growth Streak
                  _buildDropdownTile(
                    context,
                    label: 'Profit Growth Streak',
                    value: sf['min_streak'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any Streak')),
                      DropdownMenuItem(value: '2', child: Text('≥ 2 Quarters Streak')),
                      DropdownMenuItem(value: '3', child: Text('≥ 3 Quarters Streak')),
                      DropdownMenuItem(value: '4', child: Text('≥ 4 Quarters Streak')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('min_streak', val ?? 'any'),
                  ),

                  // 6. Min Fundamental Score
                  _buildDropdownTile(
                    context,
                    label: 'Fundamental Score',
                    value: sf['min_funda'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any Score')),
                      DropdownMenuItem(value: '60', child: Text('≥ 60 (Healthy Fundamentals)')),
                      DropdownMenuItem(value: '70', child: Text('≥ 70 (Strong Fundamentals)')),
                      DropdownMenuItem(value: '80', child: Text('≥ 80 (Elite Health)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('min_funda', val ?? 'any'),
                  ),

                  const Divider(height: 24),
                  _buildSectionHeader(context, 'TECHNICAL & MOMENTUM'),

                  // 7. RSI Zone
                  _buildDropdownTile(
                    context,
                    label: '14-Day RSI Zone',
                    value: sf['rsi_zone'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any RSI Zone')),
                      DropdownMenuItem(value: 'oversold', child: Text('Oversold / Dip (< 48)')),
                      DropdownMenuItem(value: 'bullish', child: Text('Bullish Accumulation (50 - 65)')),
                      DropdownMenuItem(value: 'momentum', child: Text('High Momentum (55 - 72)')),
                      DropdownMenuItem(value: 'extreme_oversold', child: Text('Extreme Oversold (< 35)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('rsi_zone', val ?? 'any'),
                  ),

                  // 8. Trend Posture
                  _buildDropdownTile(
                    context,
                    label: 'Moving Average Trend',
                    value: sf['trend'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any Trend')),
                      DropdownMenuItem(value: 'stage2', child: Text('Stage 2 Strong Uptrend Only')),
                      DropdownMenuItem(value: 'above_50dma', child: Text('Trading Above 50 EMA')),
                      DropdownMenuItem(value: 'above_200dma', child: Text('Trading Above 200 SMA')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('trend', val ?? 'any'),
                  ),

                  // 9. 52-Week High Proximity
                  _buildDropdownTile(
                    context,
                    label: 'Distance to 52-Week High',
                    value: sf['proximity_52w'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any Distance')),
                      DropdownMenuItem(value: 'near_high_5', child: Text('Within 5% of 52W High (Breakout)')),
                      DropdownMenuItem(value: 'near_high_12', child: Text('Within 12% of 52W High')),
                      DropdownMenuItem(value: 'within_20', child: Text('Within 20% of 52W High')),
                      DropdownMenuItem(value: 'pullback_20', child: Text('Deep Pullback (> 20% from High)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('proximity_52w', val ?? 'any'),
                  ),

                  const Divider(height: 24),
                  _buildSectionHeader(context, 'FORECASTS & TARGETS'),

                  // 10. 1-Year Forecast Upside
                  _buildDropdownTile(
                    context,
                    label: '1-Year Target Upside %',
                    value: sf['min_upside'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any Target')),
                      DropdownMenuItem(value: '10', child: Text('≥ +10% 1Y Upside')),
                      DropdownMenuItem(value: '15', child: Text('≥ +15% 1Y Upside')),
                      DropdownMenuItem(value: '20', child: Text('≥ +20% High Upside')),
                      DropdownMenuItem(value: '35', child: Text('≥ +35% Substantial Target')),
                      DropdownMenuItem(value: '50', child: Text('≥ +50% Multi-Bagger Target')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('min_upside', val ?? 'any'),
                  ),

                  // 11. Min Master Score
                  _buildDropdownTile(
                    context,
                    label: 'Master Alpha Score',
                    value: sf['min_master'] ?? 'any',
                    options: const [
                      DropdownMenuItem(value: 'any', child: Text('Any Master Score')),
                      DropdownMenuItem(value: '75', child: Text('≥ 75 (High Conviction)')),
                      DropdownMenuItem(value: '80', child: Text('≥ 80 (Top Tier Compounder)')),
                      DropdownMenuItem(value: '85', child: Text('≥ 85 (Superior Strength)')),
                      DropdownMenuItem(value: '88', child: Text('≥ 88 (🌟 Master Alpha Leader)')),
                    ],
                    onChanged: (val) => provider.setSmartFilter('min_master', val ?? 'any'),
                  ),
                ],
              ),
            ),

            // Footer Reset & Apply Bar
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.card(context),
                border: Border(top: BorderSide(color: AppColors.border(context), width: 0.8)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        side: BorderSide(color: AppColors.border(context)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: () => provider.resetSmartFilters(),
                      icon: const Icon(Icons.restart_alt_rounded, size: 16),
                      label: Text('Reset', style: TextStyle(color: AppColors.textPrimary(context), fontSize: 13)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.blue(context),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: () => Navigator.of(context).pop(),
                      child: Text(
                        'Show (${provider.stocks.length}) Stocks',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.8,
          color: AppColors.textMuted(context),
          fontFamily: 'monospace',
        ),
      ),
    );
  }

  Widget _buildDropdownTile(
    BuildContext context, {
    required String label,
    required String value,
    required List<DropdownMenuItem<String>> options,
    required ValueChanged<String?> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary(context)),
          ),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10),
            decoration: BoxDecoration(
              color: AppColors.bg(context),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border(context)),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: value,
                isExpanded: true,
                dropdownColor: AppColors.card(context),
                style: TextStyle(fontSize: 12, color: AppColors.textPrimary(context)),
                items: options,
                onChanged: onChanged,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
