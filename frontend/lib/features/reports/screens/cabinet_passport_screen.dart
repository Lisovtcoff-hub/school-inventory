import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../assets/models/asset_models.dart';
import '../data/reports_api.dart';

class CabinetPassportScreen extends StatefulWidget {
  const CabinetPassportScreen({super.key});

  @override
  State<CabinetPassportScreen> createState() => _CabinetPassportScreenState();
}

class _CabinetPassportScreenState extends State<CabinetPassportScreen> {
  late final ReportsApi api;
  bool initialized = false;
  bool loadingLocations = true;
  bool loadingReport = false;
  String? error;
  List<String> locations = const [];
  String? selectedLocation;
  Map<String, dynamic>? data;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = ReportsApi(context.read<ApiClient>());
    _loadLocations();
  }

  Future<void> _loadLocations() async {
    setState(() {
      loadingLocations = true;
      error = null;
    });

    try {
      locations = await api.getCabinetPassportLocations();
      if (locations.isNotEmpty) {
        selectedLocation ??= locations.first;
      }
    } catch (e) {
      error = apiErrorText(e);
    }

    if (mounted) {
      setState(() => loadingLocations = false);
    }
  }

  Future<void> _generate() async {
    final location = selectedLocation;
    if (location == null || location.trim().isEmpty) return;

    setState(() {
      loadingReport = true;
      error = null;
    });

    try {
      data = await api.getCabinetPassport(location);
    } catch (e) {
      error = apiErrorText(e);
    }

    if (mounted) {
      setState(() => loadingReport = false);
    }
  }

  Future<void> _pdf() async {
    final location = selectedLocation;
    if (location == null || location.trim().isEmpty) return;

    try {
      await api.cabinetPassportPdf(location);
    } catch (e) {
      setState(() => error = apiErrorText(e));
    }
  }

  List<dynamic> get _warnings => (data?['warnings'] ?? const []) as List<dynamic>;
  List<dynamic> get _assets => (data?['assets'] ?? const []) as List<dynamic>;
  List<dynamic> get _sections => (data?['sections'] ?? const []) as List<dynamic>;

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Паспорт учебного кабинета',
        subtitle: 'Автоматическое формирование паспорта кабинета на основе заведенной техники',
        actions: [
          SizedBox(
            width: 280,
            child: DropdownButtonFormField<String>(
              value: selectedLocation,
              isExpanded: true,
              decoration: const InputDecoration(labelText: 'Кабинет / локация'),
              items: locations
                  .map((location) => DropdownMenuItem(
                        value: location,
                        child: Text(location, maxLines: 1, overflow: TextOverflow.ellipsis),
                      ))
                  .toList(),
              onChanged: loadingLocations
                  ? null
                  : (value) {
                      setState(() {
                        selectedLocation = value;
                        data = null;
                      });
                    },
            ),
          ),
          FilledButton.icon(
            onPressed: selectedLocation == null || loadingReport ? null : _generate,
            icon: const Icon(Icons.play_arrow),
            label: const Text('Сформировать', maxLines: 1, overflow: TextOverflow.ellipsis),
          ),
          OutlinedButton.icon(
            onPressed: data == null ? null : _pdf,
            icon: const Icon(Icons.picture_as_pdf),
            label: const Text('Скачать PDF', maxLines: 1, overflow: TextOverflow.ellipsis),
          ),
        ],
        child: error != null
            ? ErrorView(error!, onRetry: locations.isEmpty ? _loadLocations : _generate)
            : loadingLocations
                ? const LoadingView()
                : locations.isEmpty
                    ? EmptyView(
                        'Кабинеты не найдены. Заполните поле «Кабинет» хотя бы у одной карточки техники.',
                        action: OutlinedButton(onPressed: _loadLocations, child: const Text('Проверить снова')),
                      )
                    : loadingReport
                        ? const LoadingView()
                        : data == null
                            ? EmptyView(
                                'Выберите кабинет и нажмите «Сформировать».',
                                action: FilledButton(onPressed: _generate, child: const Text('Сформировать')),
                              )
                            : _reportBody(context),
      );

  Widget _reportBody(BuildContext context) {
    final summary = Map<String, dynamic>.from((data!['summary'] as Map?) ?? const {});
    final organization = Map<String, dynamic>.from((data!['organization'] as Map?) ?? const {});

    return SingleChildScrollView(
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
                    data!['title']?.toString() ?? 'Паспорт учебного кабинета',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 4),
                  Text('${organization['name'] ?? 'Организация'} · ${data!['location'] ?? selectedLocation ?? ''}'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          LayoutBuilder(
            builder: (context, constraints) {
              final width = responsiveCardWidth(constraints.maxWidth, max: 280);
              return Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  _summaryCard('Всего техники', summary['total_assets'] ?? 0, Icons.inventory_2_outlined, width),
                  _summaryCard('В работе', summary['working_assets'] ?? 0, Icons.check_circle_outline, width),
                  _summaryCard('Ремонт / требует ремонта', summary['needs_repair'] ?? 0, Icons.build_outlined, width),
                  _summaryCard('Списано', summary['written_off'] ?? 0, Icons.archive_outlined, width),
                ],
              );
            },
          ),
          const SizedBox(height: 12),
          if (_warnings.isNotEmpty) ...[
            _warningsCard(),
            const SizedBox(height: 12),
          ],
          _sectionsCard(),
          const SizedBox(height: 12),
          _assetsTable(),
        ],
      ),
    );
  }

  Widget _summaryCard(String title, dynamic value, IconData icon, double width) => SummaryStatCard(
        title: title,
        value: value.toString(),
        icon: icon,
        width: width,
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
                ..._warnings.map((item) {
                  final warning = Map<String, dynamic>.from(item as Map);
                  return ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.info_outline),
                    title: Text(warning['message']?.toString() ?? 'Проверьте данные отчета'),
                  );
                }),
              ],
            ),
          ),
        ),
      );

  Widget _sectionsCard() => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Разделы паспорта', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _sections.map((item) {
                  final section = Map<String, dynamic>.from(item as Map);
                  final items = (section['items'] ?? const []) as List<dynamic>;
                  return Chip(
                    label: Text('${section['title'] ?? 'Раздел'}: ${items.length}'),
                    side: const BorderSide(color: Color(0xFFD0D0D0)),
                  );
                }).toList(),
              ),
            ],
          ),
        ),
      );

  Widget _assetsTable() => Card(
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columns: const [
              DataColumn(label: Text('Код')),
              DataColumn(label: Text('Название')),
              DataColumn(label: Text('Тип')),
              DataColumn(label: Text('Модель')),
              DataColumn(label: Text('Серийный №')),
              DataColumn(label: Text('Инв. №')),
              DataColumn(label: Text('Статус')),
              DataColumn(label: Text('Ответственный')),
              DataColumn(label: Text('Учебное')),
            ],
            rows: _assets.map((item) {
              final asset = Map<String, dynamic>.from(item as Map);
              return DataRow(
                cells: [
                  DataCell(SelectableText(asset['asset_code']?.toString() ?? '—')),
                  DataCell(SizedBox(width: 220, child: Text(asset['name']?.toString() ?? '—'))),
                  DataCell(Text(dictLabel(asset['type']?.toString() ?? ''))),
                  DataCell(Text(asset['model']?.toString() ?? '—')),
                  DataCell(Text(asset['serial_number']?.toString() ?? '—')),
                  DataCell(Text(asset['inventory_number']?.toString() ?? '—')),
                  DataCell(Text(dictLabel(asset['status']?.toString() ?? ''))),
                  DataCell(Text(asset['responsible_person']?.toString() ?? '—')),
                  DataCell(Text(asset['is_used_for_education'] == true ? 'Да' : 'Нет')),
                ],
              );
            }).toList(),
          ),
        ),
      );
}
