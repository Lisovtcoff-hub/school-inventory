import '../../../core/api/api_client.dart';
import '../models/asset_history.dart';
class AssetHistoryApi { final ApiClient client; AssetHistoryApi(this.client); Future<List<AssetHistory>> list(int assetId) async => ((await client.dio.get('/assets/$assetId/history')).data as List).map((e)=>AssetHistory.fromJson(e)).toList(); Future<AssetHistory> addNote(int assetId, String message) async => AssetHistory.fromJson((await client.dio.post('/assets/$assetId/history', data:{'event_type':'manual_note','message':message})).data); }
