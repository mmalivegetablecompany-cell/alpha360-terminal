import 'package:flutter/material.dart';
import '../models/stock.dart';
import '../theme/app_theme.dart';

class MarketBreadthBar extends StatelessWidget {
  final List<Stock> stocks;

  const MarketBreadthBar({super.key, required this.stocks});

  @override
  Widget build(BuildContext context) {
    if (stocks.isEmpty) return const SizedBox.shrink();

    int advances = 0;
    int declines = 0;
    int neutral = 0;

    Stock? topGainer;
    for (final s in stocks) {
      if (s.dayChangePct > 0) {
        advances++;
        if (topGainer == null || s.dayChangePct > topGainer.dayChangePct) {
          topGainer = s;
        }
      } else if (s.dayChangePct < 0) {
        declines++;
      } else {
        neutral++;
      }
    }

    final total = (advances + declines + neutral);
    final advRatio = total > 0 ? (advances / total) : 0.5;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.surface(context),
        border: Border(
          bottom: BorderSide(color: AppColors.border(context), width: 0.8),
        ),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isVeryWide = constraints.maxWidth >= 850;

          final statsRow = Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Advances
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.arrow_drop_up_rounded, color: AppColors.green(context), size: 20),
                  Text(
                    '$advances ADV',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: AppColors.green(context),
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 8),

              // Visual Mini Breadth Bar
              SizedBox(
                width: 60,
                height: 6,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(3),
                  child: Row(
                    children: [
                      Expanded(
                        flex: (advRatio * 100).toInt().clamp(1, 99),
                        child: Container(color: AppColors.green(context)),
                      ),
                      Expanded(
                        flex: ((1.0 - advRatio) * 100).toInt().clamp(1, 99),
                        child: Container(color: AppColors.red(context)),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 8),

              // Declines
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.arrow_drop_down_rounded, color: AppColors.red(context), size: 20),
                  Text(
                    '$declines DEC',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: AppColors.red(context),
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ],
          );

          return Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    statsRow,
                    if (isVeryWide) ...[
                      const SizedBox(width: 16),
                      Text(
                        'Market Breadth: ${(advRatio * 100).toStringAsFixed(0)}% Bullish',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textSecondary(context),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (topGainer != null)
                Flexible(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      if (isVeryWide)
                        Text(
                          'TOP GAINER: ',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textMuted(context),
                          ),
                        ),
                      Flexible(
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.green(context).withAlpha(25),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: AppColors.green(context).withAlpha(60), width: 0.8),
                          ),
                          child: Text(
                            '🔥 ${topGainer.symbol} +${topGainer.dayChangePct.toStringAsFixed(1)}%',
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: AppColors.green(context),
                              fontFamily: 'monospace',
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}
