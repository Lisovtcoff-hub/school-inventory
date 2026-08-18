import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../../core/widgets/suggestion_text_field.dart';
import '../data/assets_api.dart';
import '../models/asset_models.dart';

class AssetFormScreen extends StatefulWidget {
  final int? assetId;
  const AssetFormScreen({super.key, this.assetId});
  @override
  State<AssetFormScreen> createState() => _AssetFormScreenState();
}

class _AssetFormScreenState extends State<AssetFormScreen> {
  late final AssetsApi api;
  bool loading = false;
  bool initialized = false;
  String? error;
  final f = <String, TextEditingController>{};
  final suggestions = <String, List<String>>{};
  String type = 'computer';
  String status = 'in_use';
  String? userCategory;
  String? reportCategory;
  String? ownershipType;
  final bools = {
    'is_used_for_education': false,
    'is_available_for_students': false,
    'has_lan': false,
    'has_internet': false,
    'has_intranet': false,
    'received_in_current_year': false,
    'include_in_reports': true,
  };

  @override
  void initState() {
    super.initState();
    for (final k in ['name', 'manufacturer', 'model', 'serial_number', 'inventory_number', 'commissioning_year', 'room', 'responsible_person', 'os', 'description']) {
      f[k] = TextEditingController();
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = AssetsApi(context.read<ApiClient>());
    _loadSuggestions();
    if (widget.assetId != null) _load();
  }

  @override
  void dispose() {
    for (final c in f.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _loadSuggestions() async {
    try {
      final items = (await api.list(query: {'page_size': 200})).items;
      List<String> values(String Function(Asset a) pick) => items.map(pick).where((v) => v.trim().isNotEmpty).toSet().toList()..sort();
      suggestions['name'] = values((a) => a.name);
      suggestions['manufacturer'] = values((a) => a.manufacturer ?? '');
      suggestions['model'] = values((a) => a.model ?? '');
      suggestions['room'] = values((a) => a.room ?? '');
      suggestions['responsible_person'] = values((a) => a.responsiblePerson ?? '');
      suggestions['os'] = values((a) => a.os ?? '');
      if (mounted) setState(() {});
    } catch (_) {
      // Подсказки не критичны: если backend недоступен, форма всё равно должна открыться.
    }
  }

  Future<void> _load() async {
    setState(() => loading = true);
    try {
      final a = await api.get(widget.assetId!);
      type = a.type;
      status = a.status;
      userCategory = a.userCategory;
      reportCategory = a.reportCategory;
      ownershipType = a.ownershipType;
      f['name']!.text = a.name;
      f['manufacturer']!.text = a.manufacturer ?? '';
      f['model']!.text = a.model ?? '';
      f['serial_number']!.text = a.serialNumber ?? '';
      f['inventory_number']!.text = a.inventoryNumber ?? '';
      f['commissioning_year']!.text = a.commissioningYear?.toString() ?? '';
      f['room']!.text = a.room ?? '';
      f['responsible_person']!.text = a.responsiblePerson ?? '';
      f['os']!.text = a.os ?? '';
      f['description']!.text = a.description ?? '';
      bools['is_used_for_education'] = a.isUsedForEducation;
      bools['is_available_for_students'] = a.isAvailableForStudents;
      bools['has_lan'] = a.hasLan;
      bools['has_internet'] = a.hasInternet;
      bools['has_intranet'] = a.hasIntranet;
      bools['received_in_current_year'] = a.receivedInCurrentYear;
      bools['include_in_reports'] = a.includeInReports;
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Map<String, dynamic> body() => {
        'type': type,
        'name': f['name']!.text.trim(),
        'manufacturer': n('manufacturer'),
        'model': n('model'),
        'serial_number': n('serial_number'),
        'inventory_number': n('inventory_number'),
        'commissioning_year': int.tryParse(f['commissioning_year']!.text),
        'room': n('room'),
        'responsible_person': n('responsible_person'),
        'user_category': userCategory,
        'status': status,
        'os': n('os'),
        'description': n('description'),
        'report_category': reportCategory,
        ...bools,
        'ownership_type': ownershipType,
      };

  String? n(String k) => f[k]!.text.trim().isEmpty ? null : f[k]!.text.trim();

  Future<void> save() async {
    if (f['name']!.text.trim().length < 2) {
      setState(() => error = 'Название техники должно быть не короче 2 символов.');
      return;
    }
    setState(() => loading = true);
    try {
      final a = widget.assetId == null ? await api.create(body()) : await api.update(widget.assetId!, body());
      if (mounted) context.go('/assets/${a.id}');
    } catch (e) {
      setState(() => error = apiErrorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: widget.assetId == null ? 'Добавление техники' : 'Редактирование техники',
      subtitle: 'Код техники, номер в организации и QR-код создаёт backend',
      actions: [FilledButton.icon(onPressed: loading ? null : save, icon: const Icon(Icons.save), label: const Text('Сохранить'))],
      child: loading
          ? const LoadingView()
          : SingleChildScrollView(
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (error != null) ErrorBanner(error!),
                      const Text('Поля с иконкой поиска предлагают значения из уже заведённой техники.', style: TextStyle(color: Color(0xFF6B6B6B))),
                      _section('Основные данные'),
                      Wrap(spacing: 12, runSpacing: 12, children: [
                        dd('type', 'Тип', type, assetTypes, (v) => setState(() => type = v!)),
                        tf('name', 'Название', req: true),
                        tf('manufacturer', 'Производитель'),
                        tf('model', 'Модель'),
                        plainTf('serial_number', 'Серийный номер'),
                        plainTf('inventory_number', 'Инвентарный номер'),
                      ]),
                      _section('Размещение и состояние'),
                      Wrap(spacing: 12, runSpacing: 12, children: [
                        tf('room', 'Кабинет'),
                        tf('responsible_person', 'Ответственный'),
                        dd('user_category', 'Категория пользователей', userCategory, userCategories, (v) => setState(() => userCategory = v)),
                        dd('status', 'Статус', status, assetStatuses, (v) => setState(() => status = v!)),
                        tf('os', 'Операционная система'),
                        plainTf('commissioning_year', 'Год ввода'),
                      ]),
                      _section('Отчётность ОО-2'),
                      const Text(
                        'Раздел 2.1 ОО-2 считает компьютеры, локальную сеть, Интернет, Интранет, поступление в отчётном году и отдельные виды оборудования. Подсказки под чекбоксами сделаны по указаниям к заполнению формы.',
                        style: TextStyle(color: Color(0xFF6B6B6B)),
                      ),
                      const SizedBox(height: 8),
                      Wrap(spacing: 12, runSpacing: 12, children: [
                        dd('report_category', 'Категория ОО-2', reportCategory, reportCategories, (v) => setState(() => reportCategory = v)),
                        dd('ownership_type', 'Право владения', ownershipType, ownershipTypes, (v) => setState(() => ownershipType = v)),
                        ...bools.keys.map((k) => SizedBox(
                              width: 430,
                              child: CheckboxListTile(
                                value: bools[k],
                                onChanged: (v) => setState(() => bools[k] = v ?? false),
                                title: Text(fieldLabel(k)),
                                subtitle: fieldHelp(k) == null ? null : Text(fieldHelp(k)!, style: const TextStyle(fontSize: 12)),
                                controlAffinity: ListTileControlAffinity.leading,
                                contentPadding: EdgeInsets.zero,
                              ),
                            )),
                      ]),
                      _section('Описание'),
                      SuggestionTextField(controller: f['description']!, label: 'Описание', suggestions: const [], maxLines: 4),
                    ],
                  ),
                ),
              ),
            ),
    );
  }

  Widget _section(String t) => Padding(
        padding: const EdgeInsets.only(top: 18, bottom: 8),
        child: Text(t, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
      );

  Widget tf(String k, String label, {bool req = false}) => SizedBox(
        width: 280,
        child: SuggestionTextField(controller: f[k]!, label: label, required: req, suggestions: suggestions[k] ?? const []),
      );

  Widget plainTf(String k, String label) => SizedBox(width: 280, child: TextField(controller: f[k], decoration: InputDecoration(labelText: label)));

  Widget dd(String key, String label, String? val, List<String> items, ValueChanged<String?> onChanged) => SizedBox(
        width: 280,
        child: DropdownButtonFormField<String?>(
          value: val,
          isExpanded: true,
          decoration: InputDecoration(labelText: label),
          items: [
            const DropdownMenuItem(value: null, child: Text('Не выбрано')),
            ...items.map((e) => DropdownMenuItem(value: e, child: Text(choiceLabel(key, e)))),
          ],
          onChanged: onChanged,
        ),
      );
}
