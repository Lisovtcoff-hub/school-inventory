import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../asset_history/widgets/asset_history_list.dart';
import '../data/assets_api.dart';
import '../models/asset_models.dart';

class AssetDetailScreen extends StatefulWidget {
  final int assetId;
  const AssetDetailScreen({super.key, required this.assetId});
  @override
  State<AssetDetailScreen> createState() => _AssetDetailScreenState();
}

class _AssetDetailScreenState extends State<AssetDetailScreen> {
  late final AssetsApi api;
  late final ApiClient client;
  Asset? asset;
  Uint8List? qr;
  String? error;
  bool loading = true;
  bool cloning = false;
  bool initialized = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    client = context.read<ApiClient>();
    api = AssetsApi(client);
    _load();
  }

  Future<void> _load() async {
    setState(() => loading = true);
    try {
      asset = await api.get(widget.assetId);
      final qrResponse = await client.dio.get<List<int>>('/assets/${widget.assetId}/qr.png', options: Options(responseType: ResponseType.bytes));
      qr = Uint8List.fromList(qrResponse.data ?? const <int>[]);
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _showCloneDialog() async {
    final count = TextEditingController(text: '1');
    var keepNumbers = false;
    final result = await showDialog<int>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Создать похожую технику'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Будут скопированы тип, название, производитель, модель, кабинет, ответственный, ОС, статус и поля ОО-2. Код техники и QR backend создаст новые.'),
                const SizedBox(height: 12),
                TextField(controller: count, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Количество копий')),
                CheckboxListTile(
                  value: keepNumbers,
                  onChanged: (v) => setDialogState(() => keepNumbers = v ?? false),
                  title: const Text('Скопировать серийный и инвентарный номера'),
                  subtitle: const Text('Обычно у одинаковых устройств эти номера разные, поэтому лучше оставить выключенным.'),
                  contentPadding: EdgeInsets.zero,
                  controlAffinity: ListTileControlAffinity.leading,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Отмена')),
            FilledButton(onPressed: () => Navigator.of(dialogContext).pop(int.tryParse(count.text) ?? 1), child: const Text('Создать')),
          ],
        ),
      ),
    );
    count.dispose();
    if (result == null || result < 1 || asset == null) return;
    final safeCount = result.clamp(1, 100).toInt();
    await _clone(safeCount, keepNumbers: keepNumbers);
  }

  Future<void> _clone(int count, {required bool keepNumbers}) async {
    setState(() => cloning = true);
    try {
      Asset? last;
      for (var i = 0; i < count; i++) {
        last = await api.create(asset!.toCreateJson(keepInventoryAndSerial: keepNumbers));
      }
      if (mounted && last != null) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Создано похожих карточек: $count')));
        context.go('/assets/${last.id}');
      }
    } catch (e) {
      setState(() => error = apiErrorText(e));
    } finally {
      if (mounted) setState(() => cloning = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Карточка техники',
      actions: [
        OutlinedButton.icon(onPressed: asset == null || cloning ? null : _showCloneDialog, icon: const Icon(Icons.copy_all_outlined), label: Text(cloning ? 'Создаём...' : 'Создать похожую')),
        OutlinedButton.icon(onPressed: () => context.go('/assets/${widget.assetId}/edit'), icon: const Icon(Icons.edit), label: const Text('Редактировать')),
      ],
      child: loading
          ? const LoadingView()
          : error != null
              ? ErrorView(error!, onRetry: _load)
              : SingleChildScrollView(
                  child: Column(
                    children: [
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(18),
                          child: LayoutBuilder(
                            builder: (context, c) {
                              final a = asset!;
                              return Wrap(
                                spacing: 28,
                                runSpacing: 18,
                                children: [
                                  SizedBox(
                                    width: 420,
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        SelectableText(a.assetCode, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
                                        const SizedBox(height: 4),
                                        Chip(label: Text(dictLabel(a.status))),
                                        const SizedBox(height: 18),
                                        LabeledText('Название', a.name),
                                        LabeledText('Тип', dictLabel(a.type)),
                                        LabeledText('Производитель', a.manufacturer),
                                        LabeledText('Модель', a.model),
                                        LabeledText('Серийный номер', a.serialNumber),
                                        LabeledText('Инвентарный номер', a.inventoryNumber),
                                      ],
                                    ),
                                  ),
                                  SizedBox(
                                    width: 360,
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        LabeledText('Кабинет', a.room),
                                        LabeledText('Ответственный', a.responsiblePerson),
                                        LabeledText('Категория пользователей', a.userCategory == null ? null : dictLabel(a.userCategory!)),
                                        LabeledText('Операционная система', a.os),
                                        LabeledText('Год ввода', a.commissioningYear?.toString()),
                                        LabeledText('Описание', a.description),
                                      ],
                                    ),
                                  ),
                                  SizedBox(
                                    width: 260,
                                    child: Column(
                                      children: [
                                        Text('QR-код', style: Theme.of(context).textTheme.titleMedium),
                                        const SizedBox(height: 8),
                                        if (qr == null) const Text('QR не загружен') else Image.memory(qr!, width: 220, height: 220),
                                      ],
                                    ),
                                  ),
                                ],
                              );
                            },
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Card(child: Padding(padding: const EdgeInsets.all(18), child: AssetHistoryList(assetId: widget.assetId))),
                    ],
                  ),
                ),
    );
  }
}
