import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../assets/data/assets_api.dart';
import '../../assets/models/asset_models.dart';
import '../data/qr_api.dart';

class QrLabelsScreen extends StatefulWidget {
  final List<int> preselectedIds;
  const QrLabelsScreen({super.key, this.preselectedIds = const []});

  @override
  State<QrLabelsScreen> createState() => _QrLabelsScreenState();
}

class _QrLabelsScreenState extends State<QrLabelsScreen> {
  List<Asset>? assets;
  final selected = <int>{};
  String? error;
  bool loading = false;
  bool initialized = false;

  final w = TextEditingController(text: '5.0');
  final h = TextEditingController(text: '5.5');
  final q = TextEditingController(text: '3.0');
  final cols = TextEditingController(text: '3');

  @override
  void initState() {
    super.initState();
    selected.addAll(widget.preselectedIds);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    _load();
  }

  @override
  void dispose() {
    w.dispose();
    h.dispose();
    q.dispose();
    cols.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      assets = (await AssetsApi(context.read<ApiClient>()).list(query: {'page_size': 200})).items;
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    }
    if (mounted) setState(() {});
  }

  void _selectAll() {
    final items = assets ?? const <Asset>[];
    setState(() => selected.addAll(items.map((a) => a.id)));
  }

  Future<void> _pdf() async {
    setState(() => loading = true);
    try {
      await QrApi(context.read<ApiClient>()).generateLabelsPdf({
        'asset_ids': selected.toList(),
        'label_width_cm': double.tryParse(w.text) ?? 5.0,
        'label_height_cm': double.tryParse(h.text) ?? 5.5,
        'qr_size_cm': double.tryParse(q.text) ?? 3.0,
        'columns': int.tryParse(cols.text),
        'include_asset_code': true,
        'include_asset_name': true,
        'include_room': true,
      });
    } catch (e) {
      setState(() => error = apiErrorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'QR-наклейки',
        subtitle: 'Выберите технику и сформируйте PDF-лист QR-наклеек',
        actions: [
          if (selected.isNotEmpty)
            OutlinedButton.icon(
              onPressed: _selectAll,
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
            onPressed: selected.isEmpty || loading ? null : _pdf,
            icon: const Icon(Icons.picture_as_pdf),
            label: Text('Сформировать PDF (${selected.length})'),
          ),
        ],
        child: assets == null
            ? error != null
                ? ErrorView(error!, onRetry: _load)
                : const LoadingView()
            : Column(
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Wrap(
                        spacing: 12,
                        runSpacing: 12,
                        children: [
                          _num(w, 'Ширина наклейки, см'),
                          _num(h, 'Высота наклейки, см'),
                          _num(q, 'QR, см'),
                          _num(cols, 'Колонки'),
                        ],
                      ),
                    ),
                  ),
                  if (error != null) ErrorBanner(error!, margin: const EdgeInsets.only(top: 8, bottom: 8)),
                  Expanded(
                    child: Scrollbar(
                      child: ListView(
                        children: assets!
                            .map(
                              (a) => CheckboxListTile(
                                value: selected.contains(a.id),
                                onChanged: (v) => setState(() => v == true ? selected.add(a.id) : selected.remove(a.id)),
                                title: Text(a.name),
                                subtitle: Text('${a.assetCode} · ${a.room ?? 'кабинет не указан'}'),
                              ),
                            )
                            .toList(),
                      ),
                    ),
                  ),
                ],
              ),
      );

  Widget _num(TextEditingController c, String label) => SizedBox(
        width: 190,
        child: TextField(controller: c, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: label)),
      );
}
