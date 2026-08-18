import '../../../core/api/api_client.dart';
import '../models/asset_models.dart';

class AssetsApi {
  final ApiClient client;
  AssetsApi(this.client);

  /// Dio иногда передаёт null-параметры как пустые строки.
  /// Backend строго проверяет enum-поля, поэтому перед запросом убираем null/пустые значения.
  Map<String, dynamic> _cleanQuery(Map<String, dynamic>? query) {
    final result = <String, dynamic>{};
    query?.forEach((key, value) {
      if (value == null) return;
      if (value is String && value.trim().isEmpty) return;
      result[key] = value;
    });
    return result;
  }

  Future<AssetListResponse> list({Map<String, dynamic>? query}) async {
    final r = await client.dio.get('/assets', queryParameters: _cleanQuery(query));
    return AssetListResponse.fromJson(r.data);
  }

  Future<AssetStatsResponse> stats() async {
    final r = await client.dio.get('/assets/stats');
    return AssetStatsResponse.fromJson(Map<String, dynamic>.from(r.data));
  }

  Future<Asset> get(int id) async => Asset.fromJson((await client.dio.get('/assets/$id')).data);
  Future<Asset> getByCode(String code) async => Asset.fromJson((await client.dio.get('/assets/by-code/$code')).data);
  Future<Asset> create(Map<String, dynamic> body) async => Asset.fromJson((await client.dio.post('/assets', data: body)).data);
  Future<Asset> update(int id, Map<String, dynamic> body) async => Asset.fromJson((await client.dio.put('/assets/$id', data: body)).data);
  Future<void> delete(int id) async => client.dio.delete('/assets/$id');
}
