import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../models/stock.dart';
import '../theme/app_theme.dart';

class PositionSizingDialog extends StatefulWidget {
  final Stock stock;

  const PositionSizingDialog({super.key, required this.stock});

  @override
  State<PositionSizingDialog> createState() => _PositionSizingDialogState();
}

class _PositionSizingDialogState extends State<PositionSizingDialog> {
  final TextEditingController _capitalController = TextEditingController(text: '500000');
  double _riskPct = 1.0;
  final NumberFormat _currencyFormat = NumberFormat.currency(locale: 'en_IN', symbol: '₹', decimalDigits: 2);
  final NumberFormat _intFormat = NumberFormat('#,##,###');

  @override
  void dispose() {
    _capitalController.dispose();
    super.dispose();
  }

  void _copyOrderTicket(int qty, double totalValue, double riskAmt, double t1Profit, double t2Profit) {
    final s = widget.stock;
    final ticket = '''
📋 INSTITUTIONAL TRADE ORDER TICKET: ${s.symbol}
🏢 Company: ${s.name}
📊 Entry Price (CMP): ₹${s.cmp.toStringAsFixed(2)}
🛑 Hard Stop-Loss: ₹${s.stopLoss.toStringAsFixed(2)}
🎯 Target 1: ₹${s.target1.toStringAsFixed(2)}
🚀 Target 2: ₹${s.target2.toStringAsFixed(2)}
⚖️ Risk / Reward: 1:${s.rrRatio.toStringAsFixed(1)}
--------------------------------------------------
📦 Position Quantity: $qty Shares
💰 Capital Allocated: ₹${totalValue.toStringAsFixed(2)}
⚠️ Max Capital Risked: ₹${riskAmt.toStringAsFixed(2)} (${_riskPct.toStringAsFixed(1)}%)
🎯 Expected Gain (T1): +₹${t1Profit.toStringAsFixed(2)}
🚀 Expected Gain (T2): +₹${t2Profit.toStringAsFixed(2)}
--------------------------------------------------
''';
    Clipboard.setData(ClipboardData(text: ticket));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Order Ticket for ${s.symbol} copied to clipboard!')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = widget.stock;
    final capital = double.tryParse(_capitalController.text.replaceAll(',', '')) ?? 500000.0;
    final riskAmt = capital * (_riskPct / 100.0);
    final riskPerShare = max<double>(0.5, s.cmp - s.stopLoss);
    final qty = max<int>(1, (riskAmt / riskPerShare).floor());
    final totalCapital = qty * s.cmp;
    final capitalAllocPct = capital > 0 ? (totalCapital / capital) * 100 : 0.0;

    final double t1Profit = (qty * max<double>(0.0, s.target1 - s.cmp)).toDouble();
    final double t2Profit = (qty * max<double>(0.0, s.target2 - s.cmp)).toDouble();
    final double t3Profit = (qty * max<double>(0.0, s.target3 - s.cmp)).toDouble();

    return Dialog(
      backgroundColor: AppColors.surface(context),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AppTheme.amberGold.withAlpha(25),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(Icons.calculate_rounded, color: AppTheme.amberGold, size: 22),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Position Sizing & Risk Model',
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w900,
                                  color: AppColors.textPrimary(context),
                                ),
                              ),
                              Text(
                                '${s.symbol} • CMP: ₹${s.cmp.toStringAsFixed(2)} • SL: ₹${s.stopLoss.toStringAsFixed(2)}',
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context)),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 18),
                    color: AppColors.textSecondary(context),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Total Trading Capital Input
              Text(
                'TOTAL ACCOUNT CAPITAL',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.5,
                  color: AppColors.textMuted(context),
                ),
              ),
              const SizedBox(height: 6),
              TextField(
                controller: _capitalController,
                keyboardType: TextInputType.number,
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary(context)),
                onChanged: (_) => setState(() {}),
                decoration: InputDecoration(
                  prefixText: '₹ ',
                  prefixStyle: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary(context)),
                  filled: true,
                  fillColor: AppColors.bg(context),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide(color: AppColors.border(context)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide(color: AppColors.blue(context), width: 1.5),
                  ),
                ),
              ),
              const SizedBox(height: 14),

              // Max Risk % Selector
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      'RISK BUDGET PER TRADE',
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.5,
                        color: AppColors.textMuted(context),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${_riskPct.toStringAsFixed(1)}% (Max Loss: ₹${_intFormat.format(riskAmt.round())})',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.red(context)),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                children: [0.5, 1.0, 1.5, 2.0, 3.0].map((r) {
                  final isSelected = _riskPct == r;
                  return Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 3),
                      child: InkWell(
                        onTap: () => setState(() => _riskPct = r),
                        borderRadius: BorderRadius.circular(6),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: isSelected ? AppColors.blue(context) : AppColors.bg(context),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: isSelected ? AppColors.blue(context) : AppColors.border(context)),
                          ),
                          child: Center(
                            child: Text(
                              '$r%',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: isSelected ? Colors.white : AppColors.textPrimary(context),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),

              // Calculation Results Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.bg(context),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.border(context)),
                ),
                child: Column(
                  children: [
                    _buildResultRow('Recommended Position Size', '$qty Shares', highlight: true, color: AppColors.blue(context)),
                    const Divider(height: 16),
                    _buildResultRow('Total Trade Value', _currencyFormat.format(totalCapital)),
                    const SizedBox(height: 8),
                    _buildResultRow('Capital Allocation %', '${capitalAllocPct.toStringAsFixed(1)}% of Account'),
                    const SizedBox(height: 8),
                    _buildResultRow('Risk Per Share (SL Distance)', '₹${riskPerShare.toStringAsFixed(2)} (${((riskPerShare / s.cmp) * 100).toStringAsFixed(1)}%)', color: AppColors.red(context)),
                    const SizedBox(height: 8),
                    _buildResultRow('Target 1 Gain (1:${(s.target1 - s.cmp > 0 ? (s.target1 - s.cmp) / riskPerShare : 1.0).toStringAsFixed(1)})', '+${_currencyFormat.format(t1Profit)}', color: AppColors.green(context)),
                    const SizedBox(height: 8),
                    _buildResultRow('Target 2 Gain (1:${(s.target2 - s.cmp > 0 ? (s.target2 - s.cmp) / riskPerShare : 2.0).toStringAsFixed(1)})', '+${_currencyFormat.format(t2Profit)}', color: AppColors.green(context)),
                    const SizedBox(height: 8),
                    _buildResultRow('Target 3 Gain (1:${(s.target3 - s.cmp > 0 ? (s.target3 - s.cmp) / riskPerShare : 3.0).toStringAsFixed(1)})', '+${_currencyFormat.format(t3Profit)}', color: AppColors.green(context)),
                  ],
                ),
              ),
              const SizedBox(height: 18),

              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
                        side: BorderSide(color: AppColors.border(context)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: () => _copyOrderTicket(qty, totalCapital, riskAmt, t1Profit, t2Profit),
                      icon: const Icon(Icons.copy_rounded, size: 14),
                      label: const FittedBox(
                        fit: BoxFit.scaleDown,
                        child: Text('Copy Order Ticket', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.blue(context),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Done', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultRow(String label, String value, {bool highlight = false, Color? color}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              fontSize: highlight ? 13 : 11,
              fontWeight: highlight ? FontWeight.bold : FontWeight.w500,
              color: AppColors.textSecondary(context),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: highlight ? 15 : 12,
            fontWeight: FontWeight.w900,
            fontFamily: highlight ? 'monospace' : null,
            color: color ?? AppColors.textPrimary(context),
          ),
        ),
      ],
    );
  }
}
