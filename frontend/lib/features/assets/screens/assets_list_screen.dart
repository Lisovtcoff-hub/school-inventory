import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../data/assets_api.dart';
import '../models/asset_models.dart';

class AssetsListScreen extends StatefulWidget {
  const AssetsListScreen({super.key});
  @override
  State<AssetsListScreen> createState() => _AssetsListScreenState();
}

class _AssetsListScreenState extends State<AssetsListScreen> {
  late final AssetsApi api;
  AssetListResponse? data;
  String? error;
  bool loading = true;
  bool initialized = false;
  final search = TextEditingController();
  String? status;
  String? type;
  final selected = <int>{};
  int page = 1;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = AssetsApi(context.read<ApiClient>());
    _load();
  }

  @override
  void dispose() {
    search.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => loading = true);
    try {
      data = await api.list(query: {
        'search': search.text.trim(),
        'status': status,
        'type': type,
        'page': page,
        'page_size': 50,
      });
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }


  void _selectAllOnPage() {
    final items = data?.items ?? const <Asset>[];
    setState(() => selected.addAll(items.map((a) => a.id)));
  }

  void _toggleAllOnPage(bool? value) {
    final items = data?.items ?? const <Asset>[];
    setState(() {
      if (value == true) {
        selected.addAll(items.map((a) => a.id));
      } else {
        selected.removeAll(items.map((a) => a.id));
      }
    });
  }

  bool get _isWholePageSelected {
    final items = data?.items ?? const <Asset>[];
    return items.isNotEmpty && items.every((a) => selected.contains(a.id));
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Техника',
      subtitle: 'Поиск, фильтры, карточки и массовая генерация QR-наклеек',
      actions: [
        OutlinedButton.icon(
          onPressed: () {
            final ids = selected.join(',');
            context.go(ids.isEmpty ? '/qr-labels' : '/qr-labels?ids=$ids');
          },
          icon: const Icon(Icons.qr_code_2),
          label: Text('QR-наклейки (${selected.length})'),
        ),
        if (selected.isNotEmpty)
          OutlinedButton.icon(
            onPressed: _selectAllOnPage,
            icon: const Icon(Icons.select_all),
            label: const Text('Выделить все'),
          ),
        if (selected.isNotEmpty)
          OutlinedButton.icon(
            onPressed: () => setState(selected.clear),
            icon: const Icon(Icons.close),
            label: const Text('Снять выделение'),
          ),
        FilledButton.icon(
          onPressed: () => context.go('/assets/new'),
          icon: const Icon(Icons.add),
          label: const Text('Добавить'),
        ),
      ],
      child: Column(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Wrap(
                spacing: 12,
                runSpacing: 12,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  SizedBox(
                    width: 360,
                    child: TextField(
                      controller: search,
                      decoration: const InputDecoration(labelText: 'Поиск по названию, коду, кабинету, ответственному'),
                      onSubmitted: (_) => _load(),
                    ),
                  ),
                  SizedBox(
                    width: 240,
                    child: DropdownButtonFormField<String?>(
                      value: type,
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Тип'),
                      items: [
                        const DropdownMenuItem(value: null, child: Text('Все типы')),
                        ...assetTypes.map((e) => DropdownMenuItem(value: e, child: Text(dictLabel(e)))),
                      ],
                      onChanged: (v) {
                        type = v;
                        page = 1;
                        _load();
                      },
                    ),
                  ),
                  SizedBox(
                    width: 240,
                    child: DropdownButtonFormField<String?>(
                      value: status,
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Статус'),
                      items: [
                        const DropdownMenuItem(value: null, child: Text('Все статусы')),
                        ...assetStatuses.map((e) => DropdownMenuItem(value: e, child: Text(dictLabel(e)))),
                      ],
                      onChanged: (v) {
                        status = v;
                        page = 1;
                        _load();
                      },
                    ),
                  ),
                  FilledButton.tonal(onPressed: _load, child: const Text('Найти')),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Expanded(child: _body()),
        ],
      ),
    );
  }

  Widget _body() {
    if (loading) return const LoadingView();
    if (error != null) return ErrorView(error!, onRetry: _load);
    if (data == null || data!.items.isEmpty) {
      return EmptyView(
        'По заданным фильтрам техника не найдена',
        action: FilledButton(onPressed: () => context.go('/assets/new'), child: const Text('Добавить первую технику')),
      );
    }
    return LayoutBuilder(
      builder: (context, c) {
        if (c.maxWidth > 850) return _table();
        return ListView(children: data!.items.map(_card).toList());
      },
    );
  }

  Widget _table() => Card(
        child: Scrollbar(
          child: SingleChildScrollView(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: [
                  DataColumn(label: Tooltip(message: 'Выделить все на странице', child: Checkbox(value: _isWholePageSelected, onChanged: _toggleAllOnPage))),
                  const DataColumn(label: Text('Код')),
                  const DataColumn(label: Text('Название')),
                  const DataColumn(label: Text('Тип')),
                  const DataColumn(label: Text('Статус')),
                  const DataColumn(label: Text('Кабинет')),
                  const DataColumn(label: Text('Действия')),
                ],
                rows: data!.items.map((a) {
                  return DataRow(
                    selected: selected.contains(a.id),
                    cells: [
                      DataCell(Checkbox(value: selected.contains(a.id), onChanged: (v) => setState(() => v == true ? selected.add(a.id) : selected.remove(a.id)))),
                      DataCell(Text(a.assetCode)),
                      DataCell(SizedBox(width: 260, child: Text(a.name, overflow: TextOverflow.ellipsis))),
                      DataCell(Text(dictLabel(a.type))),
                      DataCell(Text(dictLabel(a.status))),
                      DataCell(Text(a.room ?? '—')),
                      DataCell(SizedBox(
                        width: 150,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(onPressed: () => context.go('/assets/${a.id}'), icon: const Icon(Icons.open_in_new), tooltip: 'Открыть'),
                            IconButton(onPressed: () => context.go('/assets/${a.id}/edit'), icon: const Icon(Icons.edit), tooltip: 'Редактировать'),
                            IconButton(onPressed: () async { await api.delete(a.id); _load(); }, icon: const Icon(Icons.delete_outline), tooltip: 'Удалить'),
                          ],
                        ),
                      )),
                    ],
                  );
                }).toList(),
              ),
            ),
          ),
        ),
      );

  Widget _card(Asset a) => Card(
        child: ListTile(
          leading: Checkbox(value: selected.contains(a.id), onChanged: (v) => setState(() => v == true ? selected.add(a.id) : selected.remove(a.id))),
          title: Text(a.name),
          subtitle: Text('${a.assetCode} · ${dictLabel(a.status)} · ${a.room ?? 'кабинет не указан'}'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => context.go('/assets/${a.id}'),
        ),
      );
}
