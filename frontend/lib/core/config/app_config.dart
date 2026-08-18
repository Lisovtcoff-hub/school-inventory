class AppConfig {
  // Windows local backend: http://127.0.0.1:8000/api/v1
  // Android emulator: http://10.0.2.2:8000/api/v1
  // Real Android phone: use your PC LAN IP, e.g. http://192.168.1.10:8000/api/v1
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000/api/v1',
  );
}
