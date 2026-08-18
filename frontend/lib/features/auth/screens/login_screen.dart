import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/widgets/common.dart';
import '../auth_controller.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final email = TextEditingController();
  final password = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) context.read<AuthController>().clearError();
    });
  }

  @override
  void dispose() {
    email.dispose();
    password.dispose();
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
                  constraints: const BoxConstraints(maxWidth: 420),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(28),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Вход в систему',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Введите email и пароль пользователя вашей организации.',
                            style: TextStyle(color: Color(0xFF6B6B6B)),
                          ),
                          const SizedBox(height: 18),
                          TextField(controller: email, decoration: const InputDecoration(labelText: 'Email')),
                          const SizedBox(height: 12),
                          TextField(controller: password, obscureText: true, decoration: const InputDecoration(labelText: 'Пароль')),
                          const SizedBox(height: 16),
                          if (auth.error != null) ErrorBanner(auth.error!),
                          FilledButton(
                            onPressed: auth.isLoading
                                ? null
                                : () async {
                                    final ok = await auth.login(email.text.trim(), password.text);
                                    if (ok && mounted) context.go('/dashboard');
                                  },
                            child: Text(auth.isLoading ? 'Входим...' : 'Войти'),
                          ),
                          TextButton(
                            onPressed: auth.isLoading ? null : () => context.go('/activate'),
                            child: const Text('Активировать организацию'),
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
