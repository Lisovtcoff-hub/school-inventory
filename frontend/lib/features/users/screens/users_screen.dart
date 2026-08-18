import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_client.dart';
import '../../../core/widgets/common.dart';
import '../../assets/models/asset_models.dart';
import '../data/users_api.dart';

class UsersScreen extends StatefulWidget {
  const UsersScreen({super.key});
  @override
  State<UsersScreen> createState() => _UsersScreenState();
}

class _UsersScreenState extends State<UsersScreen> {
  late final UsersApi api;
  Map<String, dynamic>? data;
  String? error;
  final email = TextEditingController();
  final pass = TextEditingController();
  final name = TextEditingController();
  String role = 'viewer';
  bool initialized = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (initialized) return;
    initialized = true;
    api = UsersApi(context.read<ApiClient>());
    _load();
  }

  @override
  void dispose() {
    email.dispose();
    pass.dispose();
    name.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      data = await api.list();
      error = null;
    } catch (e) {
      error = apiErrorText(e);
    }
    if (mounted) setState(() {});
  }

  Future<void> _create() async {
    try {
      await api.create({'email': email.text.trim(), 'password': pass.text, 'full_name': name.text.trim(), 'role': role});
      email.clear();
      pass.clear();
      name.clear();
      await _load();
    } catch (e) {
      setState(() => error = apiErrorText(e));
    }
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Пользователи',
        subtitle: 'Создание администраторов, редакторов и наблюдателей внутри организации',
        child: SingleChildScrollView(
          child: Column(
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      SizedBox(width: 260, child: TextField(controller: email, decoration: const InputDecoration(labelText: 'Email'))),
                      SizedBox(width: 260, child: TextField(controller: name, decoration: const InputDecoration(labelText: 'ФИО'))),
                      SizedBox(width: 180, child: TextField(controller: pass, obscureText: true, decoration: const InputDecoration(labelText: 'Пароль'))),
                      SizedBox(
                        width: 220,
                        child: DropdownButtonFormField(
                          value: role,
                          isExpanded: true,
                          decoration: const InputDecoration(labelText: 'Роль'),
                          items: userRoles.map((r) => DropdownMenuItem(value: r, child: Text(dictLabel(r)))).toList(),
                          onChanged: (v) => setState(() => role = v!),
                        ),
                      ),
                      FilledButton(onPressed: _create, child: const Text('Создать')),
                      if (error != null && data != null) SizedBox(width: double.infinity, child: ErrorBanner(error!, margin: EdgeInsets.zero)),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              if (data == null && error != null)
                ErrorView(error!, onRetry: _load)
              else if (data == null)
                const LoadingView()
              else
                Card(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      columns: const [
                        DataColumn(label: Text('Email')),
                        DataColumn(label: Text('ФИО')),
                        DataColumn(label: Text('Роль')),
                        DataColumn(label: Text('Активен')),
                      ],
                      rows: ((data!['items'] ?? []) as List)
                          .map((u) => DataRow(cells: [
                                DataCell(Text(u['email'])),
                                DataCell(Text(u['full_name'])),
                                DataCell(Text(dictLabel(u['role']))),
                                DataCell(Text(u['is_active'] == true ? 'Да' : 'Нет')),
                              ]))
                          .toList(),
                    ),
                  ),
                ),
            ],
          ),
        ),
      );
}
