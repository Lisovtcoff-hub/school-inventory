import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../data/organization_api.dart';

class OrganizationScreen extends StatefulWidget {
  const OrganizationScreen({super.key});

  @override
  State<OrganizationScreen> createState() => _OrganizationScreenState();
}

class _OrganizationScreenState extends State<OrganizationScreen> {
  late final OrganizationApi api;
  Map<String, dynamic>? data;
  String? error;
  bool initialized = false;

  final c = <String, TextEditingController>{};
  final fields = ['name', 'inn', 'kpp', 'ogrn', 'address', 'director_name', 'responsible_person', 'email', 'phone'];

  @override
  void initState() {
    super.initState();
    for (final f in fields) {
      c[f] = TextEditingController();
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = OrganizationApi(context.read<ApiClient>());
    _load();
  }

  @override
  void dispose() {
    for (final controller in c.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _load() async {
    try {
      data = await api.get();
      for (final f in fields) {
        c[f]!.text = data![f]?.toString() ?? '';
      }
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    }
    if (mounted) setState(() {});
  }

  Future<void> _save() async {
    try {
      data = await api.update({
        for (final f in fields) f: c[f]!.text.trim().isEmpty ? null : c[f]!.text.trim(),
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Профиль сохранён')));
      }
    } catch (e) {
      setState(() => error = apiErrorText(e));
    }
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Профиль организации',
        subtitle: 'Редактирование доступно admin',
        actions: [
          FilledButton.icon(onPressed: _save, icon: const Icon(Icons.save), label: const Text('Сохранить')),
        ],
        child: data == null
            ? error != null
                ? ErrorView(error!, onRetry: _load)
                : const LoadingView()
            : SingleChildScrollView(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(18),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (error != null) ErrorBanner(error!),
                        Wrap(
                          spacing: 12,
                          runSpacing: 12,
                          children: fields
                          .map(
                            (f) => SizedBox(
                              width: f == 'address' ? 580 : 280,
                              child: TextField(controller: c[f], decoration: InputDecoration(labelText: f)),
                            ),
                          )
                              .toList(),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
      );
}
