import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/market_provider.dart';
import '../theme/app_theme.dart';

class CustomBasketDialog extends StatefulWidget {
  final String? existingBasketId;

  const CustomBasketDialog({super.key, this.existingBasketId});

  @override
  State<CustomBasketDialog> createState() => _CustomBasketDialogState();
}

class _CustomBasketDialogState extends State<CustomBasketDialog> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _descController = TextEditingController();
  final TextEditingController _stockSearchController = TextEditingController();
  final Set<String> _selectedSymbols = {};
  String _stockFilter = '';

  @override
  void initState() {
    super.initState();
    final provider = context.read<MarketProvider>();
    if (widget.existingBasketId != null) {
      final b = provider.userCustomBaskets.firstWhere((x) => x.id == widget.existingBasketId);
      _nameController.text = b.name;
      _descController.text = b.desc;
      _selectedSymbols.addAll(b.symbols);
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descController.dispose();
    _stockSearchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();
    final allStocks = provider.allStocks;
    final filtered = _stockFilter.isEmpty
        ? allStocks
        : allStocks.where((s) {
            final q = _stockFilter.toLowerCase();
            return s.symbol.toLowerCase().contains(q) || s.name.toLowerCase().contains(q);
          }).toList();

    return Dialog(
      backgroundColor: AppColors.card(context),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        width: 500,
        height: 600,
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Text('🧺', style: TextStyle(fontSize: 20)),
                    const SizedBox(width: 8),
                    Text(
                      widget.existingBasketId == null ? 'Create Custom Basket' : 'Edit Basket',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w900,
                        color: AppColors.textPrimary(context),
                      ),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close, size: 20),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Name Field
            TextField(
              controller: _nameController,
              style: TextStyle(color: AppColors.textPrimary(context), fontSize: 13),
              decoration: InputDecoration(
                labelText: 'Basket Name',
                hintText: 'e.g. High ROE Compounders, Renewable Energy',
                filled: true,
                fillColor: AppColors.bg(context),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 10),

            // Description Field
            TextField(
              controller: _descController,
              style: TextStyle(color: AppColors.textPrimary(context), fontSize: 13),
              decoration: InputDecoration(
                labelText: 'Description (Optional)',
                hintText: 'Short notes on strategy or allocation',
                filled: true,
                fillColor: AppColors.bg(context),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 14),

            // Stock Picker Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Select Stocks (${_selectedSymbols.length} selected)',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary(context),
                  ),
                ),
                TextButton(
                  onPressed: () {
                    setState(() {
                      if (_selectedSymbols.length == allStocks.length) {
                        _selectedSymbols.clear();
                      } else {
                        _selectedSymbols.addAll(allStocks.map((s) => s.symbol));
                      }
                    });
                  },
                  child: Text(
                    _selectedSymbols.length == allStocks.length ? 'Clear All' : 'Select All',
                    style: TextStyle(fontSize: 11, color: AppColors.blue(context), fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),

            // Stock Search Filter
            TextField(
              controller: _stockSearchController,
              onChanged: (val) => setState(() => _stockFilter = val.trim()),
              style: TextStyle(color: AppColors.textPrimary(context), fontSize: 12),
              decoration: InputDecoration(
                hintText: 'Filter stock universe...',
                prefixIcon: const Icon(Icons.search, size: 16),
                isDense: true,
                filled: true,
                fillColor: AppColors.bg(context),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 8),

            // Stock Universe List
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: AppColors.bg(context),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.border(context)),
                ),
                child: ListView.builder(
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final stock = filtered[index];
                    final isChecked = _selectedSymbols.contains(stock.symbol);

                    return CheckboxListTile(
                      dense: true,
                      value: isChecked,
                      onChanged: (val) {
                        setState(() {
                          if (val == true) {
                            _selectedSymbols.add(stock.symbol);
                          } else {
                            _selectedSymbols.remove(stock.symbol);
                          }
                        });
                      },
                      title: Text(
                        stock.symbol,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontFamily: 'monospace',
                          color: AppColors.textPrimary(context),
                        ),
                      ),
                      subtitle: Text(
                        '${stock.name} • ${stock.sector}',
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(fontSize: 10, color: AppColors.textSecondary(context)),
                      ),
                      secondary: Text(
                        '₹${stock.cmp.toStringAsFixed(1)}',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          fontFamily: 'monospace',
                          color: AppColors.textPrimary(context),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
            const SizedBox(height: 14),

            // Actions
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: Text('Cancel', style: TextStyle(color: AppColors.textSecondary(context))),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.blue(context),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  onPressed: () {
                    final name = _nameController.text.trim();
                    if (name.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Please enter a basket name')),
                      );
                      return;
                    }
                    if (_selectedSymbols.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Please select at least one stock')),
                      );
                      return;
                    }

                    if (widget.existingBasketId == null) {
                      provider.createCustomBasket(name, _descController.text.trim(), _selectedSymbols.toList());
                    } else {
                      provider.editCustomBasket(widget.existingBasketId!, name, _descController.text.trim(), _selectedSymbols.toList());
                    }

                    Navigator.of(context).pop();
                  },
                  child: Text(widget.existingBasketId == null ? 'Create Basket' : 'Save Changes'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
