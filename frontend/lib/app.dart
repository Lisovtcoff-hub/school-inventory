import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'core/theme/app_theme.dart';
import 'features/auth/auth_controller.dart';
import 'features/auth/screens/activate_screen.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/dashboard/screens/dashboard_screen.dart';
import 'features/organization/screens/organization_screen.dart';
import 'features/users/screens/users_screen.dart';
import 'features/assets/screens/assets_list_screen.dart';
import 'features/assets/screens/asset_detail_screen.dart';
import 'features/assets/screens/asset_form_screen.dart';
import 'features/qr/screens/qr_labels_screen.dart';
import 'features/qr/screens/qr_scanner_screen.dart';
import 'features/reports/screens/oo2_report_screen.dart';
import 'features/reports/screens/reports_list_screen.dart';
import 'features/reports/screens/cabinet_passport_screen.dart';

class SchoolInventoryApp extends StatefulWidget {
  const SchoolInventoryApp({super.key});

  @override
  State<SchoolInventoryApp> createState() => _SchoolInventoryAppState();
}

class _SchoolInventoryAppState extends State<SchoolInventoryApp> {
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    final auth = context.read<AuthController>();
    _router = GoRouter(
      refreshListenable: auth.routerRefresh,
      initialLocation: '/dashboard',
      redirect: (context, state) {
        final isAuthRoute = state.matchedLocation == '/login' || state.matchedLocation == '/activate';
        if (!auth.isBootstrapped) return null;
        if (!auth.isLoggedIn && !isAuthRoute) return '/login';
        if (auth.isLoggedIn && isAuthRoute) return '/dashboard';
        return null;
      },
      routes: [
        GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
        GoRoute(path: '/activate', builder: (_, __) => const ActivateScreen()),
        ShellRoute(
          builder: (_, __, child) => AppScaffold(child: child),
          routes: [
            GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
            GoRoute(path: '/assets', builder: (_, __) => const AssetsListScreen()),
            GoRoute(path: '/assets/new', builder: (_, __) => const AssetFormScreen()),
            GoRoute(path: '/assets/:id', builder: (_, s) => AssetDetailScreen(assetId: int.parse(s.pathParameters['id']!))),
            GoRoute(path: '/assets/:id/edit', builder: (_, s) => AssetFormScreen(assetId: int.parse(s.pathParameters['id']!))),
            GoRoute(path: '/organization', builder: (_, __) => const OrganizationScreen()),
            GoRoute(path: '/users', builder: (_, __) => const UsersScreen()),
            GoRoute(
              path: '/qr-labels',
              builder: (_, s) {
                final raw = s.uri.queryParameters['ids'] ?? '';
                final ids = raw.split(',').map((e) => int.tryParse(e)).whereType<int>().toList();
                return QrLabelsScreen(preselectedIds: ids);
              },
            ),
            GoRoute(path: '/qr-scan', builder: (_, __) => const QrScannerScreen()),
            GoRoute(path: '/reports', builder: (_, __) => const ReportsListScreen()),
            GoRoute(path: '/reports/oo2', builder: (_, __) => const Oo2ReportScreen()),
            GoRoute(path: '/reports/cabinet-passport', builder: (_, __) => const CabinetPassportScreen()),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'Учёт техники школы',
      theme: AppTheme.light(),
      routerConfig: _router,
    );
  }
}

class AppScaffold extends StatelessWidget {
  final Widget child;
  const AppScaffold({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    final isAdmin = auth.me?.user.role == 'admin';
    return Scaffold(
      appBar: AppBar(
        title: LayoutBuilder(
          builder: (context, constraints) => Text(
            auth.me?.organization.name ?? 'Учёт техники',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        actions: [
          if (MediaQuery.sizeOf(context).width >= 760)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 260),
                child: Center(child: Text(auth.me?.user.fullName ?? '', maxLines: 1, overflow: TextOverflow.ellipsis)),
              ),
            ),
          IconButton(onPressed: () => auth.logout(), icon: const Icon(Icons.logout), tooltip: 'Выйти'),
        ],
      ),
      drawer: NavigationDrawer(
        selectedIndex: null,
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(24, 24, 24, 12),
            child: Text('Разделы', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
          ),
          _NavTile(icon: Icons.dashboard_outlined, label: 'Главная', route: '/dashboard'),
          _NavTile(icon: Icons.computer_outlined, label: 'Техника', route: '/assets'),
          _NavTile(icon: Icons.qr_code_scanner, label: 'Сканер QR', route: '/qr-scan'),
          _NavTile(icon: Icons.qr_code_2, label: 'QR-наклейки', route: '/qr-labels'),
          _NavTile(icon: Icons.description_outlined, label: 'Отчеты', route: '/reports'),
          if (isAdmin) _NavTile(icon: Icons.business_outlined, label: 'Организация', route: '/organization'),
          if (isAdmin) _NavTile(icon: Icons.people_outline, label: 'Пользователи', route: '/users'),
        ],
      ),
      body: child,
    );
  }
}

class _NavTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String route;
  const _NavTile({required this.icon, required this.label, required this.route});
  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon),
      title: Text(label),
      onTap: () {
        Navigator.of(context).pop();
        context.go(route);
      },
    );
  }
}
