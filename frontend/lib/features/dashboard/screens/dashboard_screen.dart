import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../assets/data/assets_api.dart';
import '../../assets/models/asset_models.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late final AssetsApi api;
  AssetStatsResponse? stats;
  String? error;
  bool initialized = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = AssetsApi(context.read<ApiClient>());
    _load();
  }

  Future<void> _load() async {
    try {
      stats = await api.stats();
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    }
    if (mounted) setState(() {});
  }

  int _status(String key) => stats?.byStatus[key] ?? 0;

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Главная',
        subtitle: 'Главные показатели и быстрые действия',
        actions: [
          FilledButton.icon(
            onPressed: () => context.go('/assets/new'),
            icon: const Icon(Icons.add),
            label: const Text('Добавить технику'),
          ),
        ],
        child: error != null
            ? ErrorView(error!, onRetry: _load)
            : stats == null
                ? const LoadingView()
                : LayoutBuilder(
                    builder: (context, constraints) {
                      final statWidth = responsiveCardWidth(constraints.maxWidth, max: 300);
                      final actionWidth = responsiveCardWidth(constraints.maxWidth, min: 240, max: 320);

                      return SingleChildScrollView(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Wrap(
                              spacing: 12,
                              runSpacing: 12,
                              children: [
                                _stat('Всего техники', stats!.total.toString(), Icons.computer, statWidth),
                                _stat('В использовании', _status('in_use').toString(), Icons.check_circle_outline, statWidth),
                                _stat('В ремонте / требует ремонта', (_status('in_repair') + _status('needs_repair')).toString(), Icons.build_outlined, statWidth),
                                _stat('Списано / утеряно', (_status('written_off') + _status('lost')).toString(), Icons.archive_outlined, statWidth),
                              ],
                            ),
                            const SizedBox(height: 16),
                            Wrap(
                              spacing: 12,
                              runSpacing: 12,
                              children: [
                                _action(context, 'Список техники', '/assets', Icons.list, actionWidth),
                                _action(context, 'Сформировать QR-наклейки', '/qr-labels', Icons.qr_code_2, actionWidth),
                                _action(context, 'Сканировать QR', '/qr-scan', Icons.qr_code_scanner, actionWidth),
                                _action(context, 'Отчеты', '/reports', Icons.description_outlined, actionWidth),
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  ),
      );

  Widget _stat(String title, String value, IconData icon, double width) => SummaryStatCard(
        title: title,
        value: value,
        icon: icon,
        width: width,
      );

  Widget _action(BuildContext context, String title, String route, IconData icon, double width) => AppActionButton(
        icon: icon,
        label: title,
        onPressed: () => context.go(route),
        width: width,
      );
}
