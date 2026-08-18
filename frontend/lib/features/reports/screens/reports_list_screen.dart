import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../data/reports_api.dart';

class ReportsListScreen extends StatefulWidget {
  const ReportsListScreen({super.key});

  @override
  State<ReportsListScreen> createState() => _ReportsListScreenState();
}

class _ReportsListScreenState extends State<ReportsListScreen> {
  late final ReportsApi api;
  bool initialized = false;
  bool loading = true;
  String? error;
  List<Map<String, dynamic>> reports = const [];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = ReportsApi(context.read<ApiClient>());
    _load();
  }

  Future<void> _load() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      reports = await api.getReports();
    } catch (e) {
      error = apiErrorText(e);
    }

    if (mounted) {
      setState(() => loading = false);
    }
  }

  String? _routeFor(String code) => switch (code) {
        'OO2_SECTION_2_1' => '/reports/oo2',
        'CABINET_PASSPORT' => '/reports/cabinet-passport',
        _ => null,
      };

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Отчеты',
        subtitle: 'Доступные отчеты по технике образовательной организации',
        actions: [
          OutlinedButton.icon(
            onPressed: _load,
            icon: const Icon(Icons.refresh),
            label: const Text('Обновить'),
          ),
        ],
        child: error != null
            ? ErrorView(error!, onRetry: _load)
            : loading
                ? const LoadingView()
                : reports.isEmpty
                    ? const EmptyView('Backend не вернул доступные отчеты.')
                    : ListView.separated(
                        itemCount: reports.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 12),
                        itemBuilder: (context, index) {
                          final report = reports[index];
                          final code = report['code']?.toString() ?? '';
                          final route = _routeFor(code);

                          return Card(
                            child: ListTile(
                              contentPadding: const EdgeInsets.all(16),
                              leading: const Icon(Icons.description_outlined),
                              title: Text(
                                report['title']?.toString() ?? code,
                                style: const TextStyle(fontWeight: FontWeight.w800),
                              ),
                              subtitle: Padding(
                                padding: const EdgeInsets.only(top: 6),
                                child: Text(report['description']?.toString() ?? ''),
                              ),
                              trailing: route == null ? const Text('Недоступно') : const Icon(Icons.chevron_right),
                              onTap: route == null ? null : () => context.go(route),
                            ),
                          );
                        },
                      ),
      );
}
