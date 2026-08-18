import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/widgets/common.dart';
import '../auth_controller.dart';

class ActivateScreen extends StatefulWidget {
  const ActivateScreen({super.key});
  @override
  State<ActivateScreen> createState() => _ActivateScreenState();
}

class _ActivateScreenState extends State<ActivateScreen> {
  final license = TextEditingController();
  final org = TextEditingController();
  final email = TextEditingController();
  final pass = TextEditingController();
  final name = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) context.read<AuthController>().clearError();
    });
  }

  @override
  void dispose() {
    license.dispose();
    org.dispose();
    email.dispose();
    pass.dispose();
    name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) => SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight - 32),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 520),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(28),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Активация организации',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Введите лицензионный код и создайте первого администратора школы.',
                            style: TextStyle(color: Color(0xFF6B6B6B)),
                          ),
                          const SizedBox(height: 18),
                          TextField(controller: license, decoration: const InputDecoration(labelText: 'Лицензионный код')),
                          const SizedBox(height: 12),
                          TextField(controller: org, decoration: const InputDecoration(labelText: 'Название организации')),
                          const SizedBox(height: 12),
                          TextField(controller: email, decoration: const InputDecoration(labelText: 'Email администратора')),
                          const SizedBox(height: 12),
                          TextField(controller: pass, obscureText: true, decoration: const InputDecoration(labelText: 'Пароль администратора')),
                          const SizedBox(height: 12),
                          TextField(controller: name, decoration: const InputDecoration(labelText: 'ФИО администратора')),
                          const SizedBox(height: 16),
                          if (auth.error != null) ErrorBanner(auth.error!),
                          FilledButton(
                            onPressed: auth.isLoading
                                ? null
                                : () async {
                                    final ok = await auth.activate({
                                      'license_code': license.text.trim(),
                                      'organization_name': org.text.trim(),
                                      'admin_email': email.text.trim(),
                                      'admin_password': pass.text,
                                      'admin_full_name': name.text.trim(),
                                    });
                                    if (ok && mounted) context.go('/dashboard');
                                  },
                            child: Text(auth.isLoading ? 'Активируем...' : 'Активировать организацию'),
                          ),
                          TextButton(
                            onPressed: auth.isLoading ? null : () => context.go('/login'),
                            child: const Text('Уже есть аккаунт — войти'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
