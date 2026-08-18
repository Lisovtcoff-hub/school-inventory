import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../data/reports_api.dart';

class Oo2ReportScreen extends StatefulWidget {
  const Oo2ReportScreen({super.key});

  @override
  State<Oo2ReportScreen> createState() => _Oo2ReportScreenState();
}

class _Oo2ReportScreenState extends State<Oo2ReportScreen> {
  Map<String, dynamic>? data;
  String? error;
  bool initialized = false;
  final year = TextEditingController(text: DateTime.now().year.toString());
  late final ReportsApi api;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = ReportsApi(context.read<ApiClient>());
    _load();
  }

  @override
  void dispose() {
    year.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      data = await api.oo2(year: int.tryParse(year.text));
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    }
    if (mounted) setState(() {});
  }

  Future<void> _pdf() async {
    try {
      await api.oo2Pdf(year: int.tryParse(year.text));
    } catch (e) {
      setState(() => error = apiErrorText(e));
    }
  }

  List<dynamic> get _warnings => (data?['warnings'] ?? const []) as List<dynamic>;

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Отчёт ОО-2 · раздел 2.1',
        subtitle: 'Предварительный просмотр данных и скачивание PDF',
        actions: [
          SizedBox(
            width: 120,
            child: TextField(
              controller: year,
              decoration: const InputDecoration(labelText: 'Год'),
              onSubmitted: (_) => _load(),
            ),
          ),
          OutlinedButton(onPressed: _load, child: const Text('Обновить')),
          FilledButton.icon(onPressed: _pdf, icon: const Icon(Icons.picture_as_pdf), label: const Text('Скачать PDF')),
        ],
        child: error != null
            ? ErrorView(error!, onRetry: _load)
            : data == null
                ? const LoadingView()
                : SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  data!['title']?.toString() ?? 'ОО-2 раздел 2.1',
                                  style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                                ),
                                Text('${data!['organization_name']} · ${data!['report_year']}'),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        if (_warnings.isNotEmpty) ...[
                          _warningsCard(),
                          const SizedBox(height: 12),
                        ],
                        Card(
                          child: SingleChildScrollView(
                            scrollDirection: Axis.horizontal,
                            child: DataTable(
                              columns: const [
                                DataColumn(label: Text('Строка')),
                                DataColumn(label: Text('Название')),
                                DataColumn(label: Text('Всего')),
                                DataColumn(label: Text('Для обучения')),
                                DataColumn(label: Text('Доступно ученикам')),
                              ],
                              rows: ((data!['rows'] ?? []) as List)
                                  .map(
                                    (r) => DataRow(
                                      cells: [
                                        DataCell(Text(r['row_code'].toString())),
                                        DataCell(SizedBox(width: 420, child: Text(r['name']?.toString() ?? ''))),
                                        DataCell(Text('${r['total']}')),
                                        DataCell(Text('${r['used_for_education'] ?? '—'}')),
                                        DataCell(Text('${r['available_for_students'] ?? '—'}')),
                                      ],
                                    ),
                                  )
                                  .toList(),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
      );

  Widget _warningsCard() => Card(
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFFFFF8E1),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFE0D7B8)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.warning_amber),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text('Предупреждения перед сдачей отчета', style: TextStyle(fontWeight: FontWeight.w800)),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ..._warnings.map((w) {
                  final warning = Map<String, dynamic>.from(w as Map);
                  final code = warning['asset_code']?.toString();
                  return ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.info_outline),
                    title: Text(warning['message']?.toString() ?? 'Проверьте данные отчета'),
                    subtitle: code == null || code.isEmpty ? null : Text('Код техники: $code'),
                  );
                }),
              ],
            ),
          ),
        ),
      );
}
