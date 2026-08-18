import 'package:flutter_test/flutter_test.dart';
import 'package:school_inventory_frontend/features/assets/models/asset_models.dart';

void main() {
  test('Asset.fromJson applies reporting defaults', () {
    final asset = Asset.fromJson({
      'id': 1,
      'organization_id': 2,
      'asset_code': '1234567800000001',
      'local_number': 1,
      'type': 'laptop',
      'name': 'Classroom laptop',
      'status': 'in_use',
      'created_at': '2026-01-01T00:00:00',
      'updated_at': '2026-01-01T00:00:00',
    });

    expect(asset.includeInReports, isTrue);
    expect(asset.isUsedForEducation, isFalse);
    expect(asset.assetCode, hasLength(16));
  });

  test('toCreateJson omits generated identifiers', () {
    final asset = Asset(
      id: 1,
      organizationId: 2,
      assetCode: '1234567800000001',
      localNumber: 1,
      type: 'laptop',
      name: 'Classroom laptop',
      status: 'in_use',
      isUsedForEducation: true,
      isAvailableForStudents: true,
      hasLan: true,
      hasInternet: true,
      hasIntranet: false,
      receivedInCurrentYear: false,
      includeInReports: true,
    );

    final payload = asset.toCreateJson();
    expect(payload.containsKey('id'), isFalse);
    expect(payload.containsKey('asset_code'), isFalse);
    expect(payload.containsKey('local_number'), isFalse);
    expect(payload['type'], 'laptop');
  });
}
