import 'dart:io';
import 'package:dio/dio.dart';
import 'package:file_selector/file_selector.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';
import '../../../core/api/api_client.dart';

class QrApi { final ApiClient client; QrApi(this.client);
  Future<String> generateLabelsPdf(Map<String,dynamic> body) async {
    final r = await client.dio.post<List<int>>('/qr/labels.pdf', data: body, options: Options(responseType: ResponseType.bytes));
    final bytes = r.data!;
    final name = 'qr_labels_${DateTime.now().millisecondsSinceEpoch}.pdf';
    String path;
    if (Platform.isWindows) {
      final location = await getSaveLocation(suggestedName: name, acceptedTypeGroups: [const XTypeGroup(label: 'PDF', extensions: ['pdf'])]);
      if (location == null) throw Exception('Сохранение отменено');
      path = location.path;
    } else {
      final dir = await getApplicationDocumentsDirectory();
      path = '${dir.path}/$name';
    }
    await File(path).writeAsBytes(bytes);
    await OpenFilex.open(path);
    return path;
  }
}
