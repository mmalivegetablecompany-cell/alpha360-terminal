import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/market_provider.dart';
import '../theme/app_theme.dart';

class NetworkSettingsDialog extends StatefulWidget {
  const NetworkSettingsDialog({super.key});

  @override
  State<NetworkSettingsDialog> createState() => _NetworkSettingsDialogState();
}

class _NetworkSettingsDialogState extends State<NetworkSettingsDialog> {
  late TextEditingController _urlController;
  int? _latencyMs;
  bool _isTesting = false;
  String? _testStatus;

  @override
  void initState() {
    super.initState();
    final provider = context.read<MarketProvider>();
    _urlController = TextEditingController(text: provider.serverUrl);
    _testPing();
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _testPing() async {
    setState(() {
      _isTesting = true;
      _testStatus = null;
    });

    final provider = context.read<MarketProvider>();
    final latency = await provider.testServerConnection(_urlController.text.trim());

    if (mounted) {
      setState(() {
        _isTesting = false;
        _latencyMs = latency;
        if (latency != null) {
          _testStatus = 'Connected (${latency}ms) • Live & Ready';
        } else {
          _testStatus = 'Unreachable • Falling back to bundled offline assets';
        }
      });
    }
  }

  void _applyPreset(String url) {
    _urlController.text = url;
    _testPing();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();
    final isDark = AppColors.isDark(context);

    return Dialog(
      backgroundColor: AppColors.surface(context),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.blue(context).withAlpha(25),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(Icons.hub_rounded, color: AppColors.blue(context), size: 22),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Live Market Server Gateway',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textPrimary(context),
                          ),
                        ),
                        Text(
                          'Configure connection to Python Live Server',
                          style: TextStyle(fontSize: 11, color: AppColors.textSecondary(context)),
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

              // Live Status Card
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.bg(context),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: _latencyMs != null
                        ? AppColors.green(context).withAlpha(100)
                        : (_testStatus != null ? AppColors.red(context).withAlpha(80) : AppColors.border(context)),
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isTesting
                            ? AppTheme.amberGold
                            : (_latencyMs != null ? AppColors.green(context) : AppColors.red(context)),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _isTesting
                            ? 'Pinging server on ${_urlController.text}...'
                            : (_testStatus ?? 'Checking connection...'),
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: _latencyMs != null
                              ? AppColors.green(context)
                              : (_testStatus != null ? AppColors.red(context) : AppColors.textPrimary(context)),
                        ),
                      ),
                    ),
                    if (!_isTesting)
                      InkWell(
                        onTap: _testPing,
                        borderRadius: BorderRadius.circular(6),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                          child: Row(
                            children: [
                              Icon(Icons.refresh_rounded, size: 14, color: AppColors.blue(context)),
                              const SizedBox(width: 4),
                              Text('Ping', style: TextStyle(fontSize: 11, color: AppColors.blue(context), fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Presets
              Text(
                'QUICK CONNECTION PRESETS',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.5,
                  color: AppColors.textMuted(context),
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  ActionChip(
                    label: const Text('🖥️ PC Localhost (127.0.0.1)'),
                    labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                    onPressed: () => _applyPreset('http://127.0.0.1:8765'),
                  ),
                  ActionChip(
                    label: const Text('📱 Android Emulator (10.0.2.2)'),
                    labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                    onPressed: () => _applyPreset('http://10.0.2.2:8765'),
                  ),
                ],
              ),
              const SizedBox(height: 14),

              // Custom URL input
              Text(
                'SERVER ENDPOINT URL',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.5,
                  color: AppColors.textMuted(context),
                ),
              ),
              const SizedBox(height: 6),
              TextField(
                controller: _urlController,
                style: TextStyle(
                  fontSize: 13,
                  fontFamily: 'monospace',
                  color: AppColors.textPrimary(context),
                ),
                decoration: InputDecoration(
                  hintText: 'http://192.168.1.xxx:8765',
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
              const SizedBox(height: 20),

              // Actions
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Cancel', style: TextStyle(color: AppColors.textSecondary(context))),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.blue(context),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    ),
                    onPressed: () async {
                      final url = _urlController.text.trim();
                      if (url.isNotEmpty) {
                        await provider.updateServerUrl(url);
                        if (context.mounted) {
                          Navigator.pop(context);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Server endpoint updated to: $url')),
                          );
                        }
                      }
                    },
                    icon: const Icon(Icons.check_rounded, size: 16),
                    label: const Text('Save & Reconnect', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
