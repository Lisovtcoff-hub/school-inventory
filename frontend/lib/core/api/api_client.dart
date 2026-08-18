import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import '../config/app_config.dart';
import '../storage/token_storage.dart';
import 'api_exception.dart';

class ApiClient {
  final TokenStorage tokenStorage;
  late final Dio dio;

  ApiClient(this.tokenStorage) {
    dio = Dio(BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 12),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await tokenStorage.readToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) => handler.reject(_humanize(error)),
    ));
  }

  DioException _humanize(DioException error) {
    final code = error.response?.statusCode;
    final message = _extractApiMessage(error, code);
    return error.copyWith(error: ApiException(message, statusCode: code));
  }

  String _extractApiMessage(DioException error, int? code) {
    final data = _normalizeResponseData(error.response?.data);
    final serverMessage = _messageFromResponseData(data);
    if (serverMessage != null && serverMessage.trim().isNotEmpty) {
      return serverMessage.trim();
    }

    if (code == 400) return 'Некорректный запрос. Проверьте введённые данные.';
    if (code == 401) return 'Неверный email или пароль. Проверьте данные и попробуйте ещё раз.';
    if (code == 403) return 'Недостаточно прав для этого действия.';
    if (code == 404) return 'Запись не найдена или уже недоступна.';
    if (code == 409) return 'Конфликт данных. Обновите страницу и попробуйте ещё раз.';
    if (code == 422) return 'Проверьте корректность заполнения формы.';
    if (code != null && code >= 500) return 'Ошибка сервера. Попробуйте позже или обратитесь к администратору.';

    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'Сервер не отвечает. Проверьте подключение и попробуйте ещё раз.';
      case DioExceptionType.connectionError:
        return 'Не удалось подключиться к серверу. Проверьте адрес backend и сеть.';
      case DioExceptionType.cancel:
        return 'Запрос был отменён.';
      default:
        break;
    }

    if (error.error is SocketException) {
      return 'Не удалось подключиться к серверу. Проверьте адрес backend и сеть.';
    }

    return 'Неизвестная ошибка. Попробуйте повторить действие.';
  }

  dynamic _normalizeResponseData(dynamic data) {
    if (data is List<int>) {
      try {
        final decoded = utf8.decode(data);
        return jsonDecode(decoded);
      } catch (_) {
        return null;
      }
    }

    if (data is String) {
      final text = data.trim();
      if (text.isEmpty) return null;
      try {
        return jsonDecode(text);
      } catch (_) {
        return text;
      }
    }

    return data;
  }

  String? _messageFromResponseData(dynamic data) {
    if (data == null) return null;

    if (data is String) {
      return _cleanServerText(data);
    }

    if (data is Map) {
      final explicitMessage = data['message'] ?? data['error'];
      if (explicitMessage != null) {
        final message = _messageFromResponseData(explicitMessage);
        if (message != null && message.isNotEmpty) return message;
      }

      if (data['detail'] != null) {
        return _messageFromDetail(data['detail']);
      }
    }

    if (data is List) {
      return _messageFromValidationList(data);
    }

    return null;
  }

  String _messageFromDetail(dynamic detail) {
    if (detail is String) return _cleanServerText(detail);
    if (detail is List) return _messageFromValidationList(detail);
    if (detail is Map) {
      if (detail['msg'] != null || detail['type'] != null || detail['loc'] != null) {
        return _messageFromValidationItem(detail);
      }
      final nested = _messageFromResponseData(detail);
      if (nested != null && nested.isNotEmpty) return nested;
    }
    return _cleanServerText(detail.toString());
  }

  String _messageFromValidationList(List detail) {
    final messages = <String>[];
    for (final item in detail) {
      final message = item is Map ? _messageFromValidationItem(item) : _messageFromDetail(item);
      if (message.trim().isNotEmpty && !messages.contains(message)) {
        messages.add(message);
      }
    }

    if (messages.isEmpty) return 'Проверьте корректность заполнения формы.';
    if (messages.length == 1) return messages.first;
    return messages.take(4).join('\n');
  }

  String _messageFromValidationItem(Map item) {
    final type = item['type']?.toString() ?? '';
    final msg = item['msg']?.toString() ?? '';
    final ctx = item['ctx'];
    final loc = item['loc'];
    final field = _fieldLabelFromLoc(loc);

    int? intCtx(String key) {
      if (ctx is Map && ctx[key] != null) return int.tryParse(ctx[key].toString());
      return null;
    }

    num? numCtx(String key) {
      if (ctx is Map && ctx[key] != null) return num.tryParse(ctx[key].toString());
      return null;
    }

    if (type == 'missing') return 'Заполните поле «$field».';

    final fieldType = ctx is Map ? ctx['field_type']?.toString().toLowerCase() : null;
    final isListLengthError = type.contains('list_too_short') ||
        type.contains('list_too_long') ||
        ((type == 'too_short' || type == 'too_long') && fieldType == 'list');

    if (isListLengthError) {
      final min = intCtx('min_length') ?? intCtx('limit_value');
      if (min != null) return 'Выберите минимум $min элемент.';
      return 'Выберите хотя бы один элемент.';
    }

    if (type.contains('string_too_short') || type == 'too_short') {
      final min = intCtx('min_length') ?? intCtx('limit_value');
      if (min != null) return 'Поле «$field» должно быть не короче $min символов.';
      return 'Поле «$field» заполнено слишком коротко.';
    }

    if (type.contains('string_too_long') || type == 'too_long') {
      final max = intCtx('max_length') ?? intCtx('limit_value');
      if (max != null) return 'Поле «$field» должно быть не длиннее $max символов.';
      return 'Поле «$field» заполнено слишком длинно.';
    }

    if (type.contains('greater_than_equal')) {
      final value = numCtx('ge') ?? numCtx('limit_value');
      if (value != null) return 'Поле «$field» должно быть не меньше $value.';
    }

    if (type.contains('less_than_equal')) {
      final value = numCtx('le') ?? numCtx('limit_value');
      if (value != null) return 'Поле «$field» должно быть не больше $value.';
    }

    if (type.contains('int_parsing') || type.contains('float_parsing')) {
      return 'Поле «$field» должно быть числом.';
    }

    if (type.contains('bool_parsing')) {
      return 'Поле «$field» должно быть выбрано корректно.';
    }

    if (type.contains('value_error')) {
      return _cleanServerText(msg.isNotEmpty ? msg : 'Проверьте поле «$field».');
    }

    final cleaned = _cleanServerText(msg);
    if (cleaned.isNotEmpty && cleaned != msg) return cleaned;
    if (cleaned.isNotEmpty && !cleaned.toLowerCase().contains('string should')) return cleaned;

    return 'Проверьте поле «$field».';
  }

  String _fieldLabelFromLoc(dynamic loc) {
    if (loc is List && loc.isNotEmpty) {
      for (final part in loc.reversed) {
        final value = part.toString();
        if (value != 'body' && value != 'query' && value != 'path') {
          return _fieldLabel(value);
        }
      }
    }
    if (loc is String && loc.isNotEmpty) return _fieldLabel(loc);
    return 'данные';
  }

  String _fieldLabel(String field) {
    const labels = {
      'email': 'Email',
      'admin_email': 'Email администратора',
      'password': 'Пароль',
      'admin_password': 'Пароль администратора',
      'full_name': 'ФИО',
      'admin_full_name': 'ФИО администратора',
      'license_code': 'Лицензионный код',
      'organization_name': 'Название организации',
      'name': 'Название',
      'type': 'Тип техники',
      'manufacturer': 'Производитель',
      'model': 'Модель',
      'serial_number': 'Серийный номер',
      'inventory_number': 'Инвентарный номер',
      'commissioning_year': 'Год ввода',
      'room': 'Кабинет/локация',
      'location': 'Кабинет/локация',
      'responsible_person': 'Ответственный',
      'status': 'Статус',
      'os': 'Операционная система',
      'description': 'Описание',
      'report_category': 'Категория для отчёта',
      'ownership_type': 'Тип владения',
      'asset_ids': 'Выбранная техника',
      'label_width_cm': 'Ширина наклейки',
      'label_height_cm': 'Высота наклейки',
      'qr_size_cm': 'Размер QR-кода',
      'columns': 'Количество колонок',
      'message': 'Сообщение',
      'event_type': 'Тип события',
      'role': 'Роль',
      'inn': 'ИНН',
      'kpp': 'КПП',
      'ogrn': 'ОГРН',
      'address': 'Адрес',
      'director_name': 'Директор',
      'phone': 'Телефон',
    };
    return labels[field] ?? field.replaceAll('_', ' ');
  }

  String _cleanServerText(String text) {
    var result = text.trim();
    if (result.startsWith('Value error, ')) result = result.substring('Value error, '.length);
    if (result.startsWith('Exception: ')) result = result.substring('Exception: '.length);

    final lower = result.toLowerCase();
    if (lower.contains('string should have at least')) {
      final match = RegExp(r'at least (\d+) characters?').firstMatch(result);
      final min = match?.group(1);
      if (min != null) return 'Поле заполнено слишком коротко. Минимум $min символов.';
    }
    if (lower.contains('string should have at most')) {
      final match = RegExp(r'at most (\d+) characters?').firstMatch(result);
      final max = match?.group(1);
      if (max != null) return 'Поле заполнено слишком длинно. Максимум $max символов.';
    }
    if (lower.contains('field required')) return 'Заполните обязательные поля.';
    if (lower.contains('input should be')) return 'Проверьте корректность введённых данных.';

    return result;
  }
}

String apiErrorText(Object error) {
  if (error is DioException && error.error is ApiException) return (error.error as ApiException).message;
  if (error is ApiException) return error.message;
  final text = error.toString();
  if (text.startsWith('Exception: ')) return text.substring('Exception: '.length);
  return text;
}
