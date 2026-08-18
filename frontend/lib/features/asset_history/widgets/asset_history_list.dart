import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../assets/models/asset_models.dart';
import '../data/asset_history_api.dart';
import '../models/asset_history.dart';

class AssetHistoryList extends StatefulWidget {
  final int assetId;
  const AssetHistoryList({super.key, required this.assetId});
  @override
  State<AssetHistoryList> createState() => _AssetHistoryListState();
}

class _AssetHistoryListState extends State<AssetHistoryList> {
  late final AssetHistoryApi api;
  List<AssetHistory>? items;
  String? error;
  final note = TextEditingController();
  bool initialized = false;
  bool adding = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = AssetHistoryApi(context.read<ApiClient>());
    _load();
  }

  @override
  void dispose() {
    note.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      items = await api.list(widget.assetId);
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    }
    if (mounted) setState(() {});
  }

  Future<void> _add() async {
    if (note.text.trim().isEmpty || adding) return;
    setState(() {
      adding = true;
      error = null;
    });
    try {
      await api.addNote(widget.assetId, note.text.trim());
      note.clear();
      await _load();
    } catch (e) {
      if (mounted) setState(() => error = apiErrorText(e));
    } finally {
      if (mounted) setState(() => adding = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('История', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 8),
        LayoutBuilder(
          builder: (context, constraints) {
            final button = FilledButton(onPressed: adding ? null : _add, child: Text(adding ? 'Добавляем...' : 'Добавить'));
            if (constraints.maxWidth < 620) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextField(controller: note, decoration: const InputDecoration(labelText: 'Ручная заметка: например, проведена чистка')),
                  const SizedBox(height: 8),
                  button,
                ],
              );
            }
            return Row(
              children: [
                Expanded(child: TextField(controller: note, decoration: const InputDecoration(labelText: 'Ручная заметка: например, проведена чистка'))),
                const SizedBox(width: 8),
                button,
              ],
            );
          },
        ),
        const SizedBox(height: 12),
        if (error != null)
          ErrorBanner(error!, margin: const EdgeInsets.only(bottom: 12))
        else if (items == null)
          const LinearProgressIndicator()
        else if (items!.isEmpty)
          const Text('История пока пустая')
        else
          ...items!.map(_item),
      ],
    );
  }

  Widget _item(AssetHistory h) {
    final parts = <String>[
      DateFormat('dd.MM.yyyy HH:mm').format(h.createdAt),
      dictLabel(h.eventType),
    ];
    if (h.fieldName != null) parts.add('${fieldLabel(h.fieldName!)}: ${_value(h.oldValue)} → ${_value(h.newValue)}');
    return ListTile(
      leading: const Icon(Icons.history),
      title: Text(h.message),
      subtitle: Text(parts.join(' · ')),
    );
  }

  String _value(String? value) {
    if (value == null || value.isEmpty) return '—';
    return dictLabel(value);
  }
}
