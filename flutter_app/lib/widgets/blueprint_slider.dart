import 'package:flutter/material.dart';
import '../models/stock.dart';
import '../theme/app_theme.dart';

class BlueprintSlider extends StatelessWidget {
  final Stock stock;

  const BlueprintSlider({super.key, required this.stock});

  @override
  Widget build(BuildContext context) {
    final slPct = stock.cmp > 0 ? ((stock.stopLoss - stock.cmp) / stock.cmp * 100) : 0.0;
    final t1Pct = stock.cmp > 0 ? ((stock.target1 - stock.cmp) / stock.cmp * 100) : 0.0;
    final t2Pct = stock.cmp > 0 ? ((stock.target2 - stock.cmp) / stock.cmp * 100) : 0.0;
    final t3Pct = stock.cmp > 0 ? ((stock.target3 - stock.cmp) / stock.cmp * 100) : 0.0;

    final isDark = AppColors.isDark(context);

    return Container(
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
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppTheme.primaryBlue,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'INSTITUTIONAL TRADE BLUEPRINT',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: AppColors.blue(context),
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.amberGold.withAlpha(25),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: AppTheme.amberGold.withAlpha(80)),
                ),
                child: Text(
                  'R:R 1:${stock.rrRatio.toStringAsFixed(1)}',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.amberGold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Horizontal Visual Bar
          LayoutBuilder(
            builder: (context, constraints) {
              final w = constraints.maxWidth;
              // Range from SL to T3
              final minVal = stock.stopLoss;
              final maxVal = stock.target3 > stock.target2 ? stock.target3 : (stock.target2 * 1.05);
              final totalSpan = (maxVal - minVal) <= 0 ? 1.0 : (maxVal - minVal);

              double getPos(double val) {
                final ratio = ((val - minVal) / totalSpan).clamp(0.0, 1.0);
                return (ratio * (w - 20)) + 10;
              }

              final cmpPos = getPos(stock.cmp);
              final t1Pos = getPos(stock.target1);
              final t2Pos = getPos(stock.target2);

              return Column(
                children: [
                  // Track bar
                  Stack(
                    alignment: Alignment.centerLeft,
                    children: [
                      Container(
                        height: 8,
                        decoration: BoxDecoration(
                          color: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                      // Loss zone (SL to CMP)
                      Positioned(
                        left: 10,
                        width: (cmpPos - 10).clamp(0.0, w),
                        child: Container(
                          height: 8,
                          decoration: BoxDecoration(
                            color: AppColors.red(context).withAlpha(120),
                            borderRadius: const BorderRadius.horizontal(left: Radius.circular(4)),
                          ),
                        ),
                      ),
                      // Profit zone (CMP to T3)
                      Positioned(
                        left: cmpPos,
                        width: (w - cmpPos - 10).clamp(0.0, w),
                        child: Container(
                          height: 8,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                AppColors.green(context).withAlpha(140),
                                AppTheme.primaryBlue.withAlpha(140),
                                AppTheme.purpleViolet.withAlpha(140),
                              ],
                            ),
                            borderRadius: const BorderRadius.horizontal(right: Radius.circular(4)),
                          ),
                        ),
                      ),
                      // T1 Tick
                      Positioned(
                        left: t1Pos - 1,
                        child: Container(width: 2, height: 10, decoration: BoxDecoration(color: Colors.white.withAlpha(200), borderRadius: BorderRadius.circular(1))),
                      ),
                      // T2 Tick
                      Positioned(
                        left: t2Pos - 1,
                        child: Container(width: 2, height: 10, decoration: BoxDecoration(color: Colors.white.withAlpha(200), borderRadius: BorderRadius.circular(1))),
                      ),
                      // Current CMP indicator dot
                      Positioned(
                        left: cmpPos - 6,
                        child: Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                            border: Border.all(color: AppTheme.amberGold, width: 2.5),
                            boxShadow: [
                              BoxShadow(
                                color: AppTheme.amberGold.withAlpha(100),
                                blurRadius: 4,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                ],
              );
            },
          ),

          // Blueprint 4-Column Levels
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF090E1C) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border(context).withAlpha(100)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildLevel(
                  context,
                  label: '🛑 Stop-Loss',
                  val: '₹${stock.stopLoss.toStringAsFixed(1)}',
                  sub: '${slPct.toStringAsFixed(1)}%',
                  color: AppColors.red(context),
                ),
                Container(width: 1, height: 28, color: AppColors.border(context)),
                _buildLevel(
                  context,
                  label: '🎯 Target 1',
                  val: '₹${stock.target1.toStringAsFixed(1)}',
                  sub: '+${t1Pct.toStringAsFixed(1)}%',
                  color: AppColors.green(context),
                ),
                Container(width: 1, height: 28, color: AppColors.border(context)),
                _buildLevel(
                  context,
                  label: '🚀 Target 2',
                  val: '₹${stock.target2.toStringAsFixed(1)}',
                  sub: '+${t2Pct.toStringAsFixed(1)}%',
                  color: AppColors.blue(context),
                ),
                Container(width: 1, height: 28, color: AppColors.border(context)),
                _buildLevel(
                  context,
                  label: '💎 Target 3',
                  val: '₹${stock.target3.toStringAsFixed(1)}',
                  sub: '+${t3Pct.toStringAsFixed(1)}%',
                  color: AppTheme.purpleViolet,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLevel(
    BuildContext context, {
    required String label,
    required String val,
    required String sub,
    required Color color,
  }) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary(context),
          ),
        ),
        const SizedBox(height: 2),
        Text(
          val,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w800,
            color: color,
            fontFamily: 'monospace',
          ),
        ),
        Text(
          sub,
          style: TextStyle(
            fontSize: 9,
            fontWeight: FontWeight.w700,
            color: color.withAlpha(200),
          ),
        ),
      ],
    );
  }
}
