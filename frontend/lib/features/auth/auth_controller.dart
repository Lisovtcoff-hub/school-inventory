import 'package:flutter/material.dart';
import '../../core/api/api_client.dart';
import '../../core/storage/token_storage.dart';
import 'data/auth_api.dart';
import 'models/auth_models.dart';

class AuthController extends ChangeNotifier {
  final ApiClient apiClient;
  final TokenStorage tokenStorage;
  late final AuthApi _api;

  /// Отдельный notifier только для GoRouter.
  /// Ошибки форм и loading не должны пересоздавать/сбрасывать маршруты.
  final ChangeNotifier routerRefresh = ChangeNotifier();

  bool isBootstrapped = false;
  bool isLoading = false;
  String? error;
  MeResponse? me;

  bool get isLoggedIn => me != null;

  AuthController(this.apiClient, this.tokenStorage) {
    _api = AuthApi(apiClient);
  }

  Future<void> bootstrap() async {
    try {
      if ((await tokenStorage.readToken()) != null) {
        me = await _api.me();
      }
    } catch (_) {
      await tokenStorage.clear();
    }
    isBootstrapped = true;
    notifyListeners();
    routerRefresh.notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    final normalizedEmail = email.trim();
    if (normalizedEmail.isEmpty) return _fail('Введите email.');
    if (normalizedEmail.length < 3) return _fail('Email должен быть не короче 3 символов.');
    if (password.isEmpty) return _fail('Введите пароль.');
    return _run(() async {
      await _api.login(normalizedEmail, password);
      me = await _api.me();
    }, authStateChangedOnSuccess: true);
  }

  Future<bool> activate(Map<String, dynamic> body) async {
    final license = (body['license_code'] ?? '').toString().trim();
    final organizationName = (body['organization_name'] ?? '').toString().trim();
    final adminEmail = (body['admin_email'] ?? '').toString().trim();
    final adminPassword = (body['admin_password'] ?? '').toString();
    final adminFullName = (body['admin_full_name'] ?? '').toString().trim();

    if (license.length < 3) return _fail('Лицензионный код должен быть не короче 3 символов.');
    if (organizationName.length < 2) return _fail('Название организации должно быть не короче 2 символов.');
    if (adminEmail.length < 3) return _fail('Email администратора должен быть не короче 3 символов.');
    if (adminPassword.length < 6) return _fail('Пароль администратора должен быть не короче 6 символов.');
    if (adminFullName.length < 2) return _fail('ФИО администратора должно быть не короче 2 символов.');

    return _run(() async {
      me = await _api.activate({
        ...body,
        'license_code': license,
        'organization_name': organizationName,
        'admin_email': adminEmail,
        'admin_full_name': adminFullName,
      });
    }, authStateChangedOnSuccess: true);
  }

  void clearError() {
    if (error == null) return;
    error = null;
    notifyListeners();
  }

  Future<void> logout() async {
    me = null;
    error = null;
    await tokenStorage.clear();
    notifyListeners();
    routerRefresh.notifyListeners();
  }

  Future<bool> _fail(String message) async {
    error = message;
    isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> _run(Future<void> Function() job, {bool authStateChangedOnSuccess = false}) async {
    isLoading = true;
    error = null;
    notifyListeners();
    try {
      await job();
      isLoading = false;
      notifyListeners();
      if (authStateChangedOnSuccess) routerRefresh.notifyListeners();
      return true;
    } catch (e) {
      error = apiErrorText(e);
      isLoading = false;
      notifyListeners();
      return false;
    }
  }

  @override
  void dispose() {
    routerRefresh.dispose();
    super.dispose();
  }
}
