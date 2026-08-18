import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../assets/data/assets_api.dart';

class QrScannerScreen extends StatefulWidget {
  const QrScannerScreen({super.key});

  @override
  State<QrScannerScreen> createState() => _QrScannerScreenState();
}

class _QrScannerScreenState extends State<QrScannerScreen> {
  bool busy = false;
  String? error;

  String? _extractAssetCode(String raw) {
    final text = raw.trim();
    if (text.startsWith('asset:')) return text.substring(6);
    if (RegExp(r'^\d{16}$').hasMatch(text)) return text;
    return null;
  }

  Future<void> _handle(String raw) async {
    if (busy) return;
    final code = _extractAssetCode(raw);
    if (code == null) {
      setState(() => error = 'QR-код не похож на код техники. Наведите камеру на наклейку, созданную в этом приложении.');
      return;
    }

    setState(() {
      busy = true;
      error = null;
    });

    try {
      final asset = await AssetsApi(context.read<ApiClient>()).getByCode(code);
      if (mounted) context.go('/assets/${asset.id}');
    } catch (e) {
      if (mounted) setState(() => error = apiErrorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Сканер QR',
        subtitle: 'На Android наведите камеру на наклейку техники',
        child: Column(
          children: [
            if (error != null) ErrorBanner(error!, margin: const EdgeInsets.only(bottom: 12)),
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: MobileScanner(
                  onDetect: (capture) {
                    final raw = capture.barcodes.isEmpty ? null : capture.barcodes.first.rawValue;
                    if (raw != null) _handle(raw);
                  },
                ),
              ),
            ),
          ],
        ),
      );
}
