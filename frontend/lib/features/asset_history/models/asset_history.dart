class AssetHistory {
  final int id; final int assetId; final int? userId; final String eventType; final String? fieldName; final String? oldValue; final String? newValue; final String message; final DateTime createdAt;
  AssetHistory({required this.id, required this.assetId, this.userId, required this.eventType, this.fieldName, this.oldValue, this.newValue, required this.message, required this.createdAt});
  factory AssetHistory.fromJson(Map<String,dynamic> j)=>AssetHistory(id:j['id'],assetId:j['asset_id'],userId:j['user_id'],eventType:j['event_type'],fieldName:j['field_name'],oldValue:j['old_value'],newValue:j['new_value'],message:j['message'],createdAt:DateTime.parse(j['created_at']));
}
