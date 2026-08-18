import 'dart:io';

import 'package:dio/dio.dart';
import 'package:file_selector/file_selector.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';

import '../../../core/api/api_client.dart';

class ReportsApi {
  final ApiClient client;

  ReportsApi(this.client);

  Future<List<Map<String, dynamic>>> getReports() async {
    final response = await client.dio.get('/reports');
    return (response.data as List)
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  Future<Map<String, dynamic>> oo2({int? year}) async {
    final response = await client.dio.get(
      '/reports/oo2/section-2-1',
      queryParameters: {'year': year},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<String> oo2Pdf({int? year}) async {
    final response = await client.dio.get<List<int>>(
      '/reports/oo2/section-2-1.pdf',
      queryParameters: {'year': year},
      options: Options(responseType: ResponseType.bytes),
    );

    final name = 'oo2_section_2_1_${year ?? DateTime.now().year}.pdf';
    return _saveAndOpenPdf(response.data!, name);
  }

  Future<List<String>> getCabinetPassportLocations() async {
    final response = await client.dio.get('/reports/cabinet-passport/locations');
    return (response.data as List).map((item) => item.toString()).toList();
  }

  Future<Map<String, dynamic>> getCabinetPassport(String location) async {
    final response = await client.dio.get(
      '/reports/cabinet-passport',
      queryParameters: {'location': location},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<String> cabinetPassportPdf(String location) async {
    final response = await client.dio.get<List<int>>(
      '/reports/cabinet-passport.pdf',
      queryParameters: {'location': location},
      options: Options(responseType: ResponseType.bytes),
    );

    final safeLocation = location
        .replaceAll(RegExp(r'[^\w\dа-яА-ЯёЁ]+'), '_')
        .replaceAll(RegExp(r'_+'), '_')
        .replaceAll(RegExp(r'^_|_$'), '');
    final name = 'cabinet_passport_${safeLocation.isEmpty ? 'cabinet' : safeLocation}.pdf';
    return _saveAndOpenPdf(response.data!, name);
  }

  Future<String> _saveAndOpenPdf(List<int> bytes, String suggestedName) async {
    String path;

    if (Platform.isWindows) {
      final location = await getSaveLocation(
        suggestedName: suggestedName,
        acceptedTypeGroups: [const XTypeGroup(label: 'PDF', extensions: ['pdf'])],
      );
      if (location == null) throw Exception('Сохранение отменено');
      path = location.path;
    } else {
      final dir = await getApplicationDocumentsDirectory();
      path = '${dir.path}/$suggestedName';
    }

    await File(path).writeAsBytes(bytes);
    await OpenFilex.open(path);
    return path;
  }
}
