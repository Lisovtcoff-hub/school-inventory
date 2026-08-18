import '../../../core/api/api_client.dart';
class OrganizationApi { final ApiClient client; OrganizationApi(this.client); Future<Map<String,dynamic>> get() async => Map<String,dynamic>.from((await client.dio.get('/organization/me')).data); Future<Map<String,dynamic>> update(Map<String,dynamic> body) async => Map<String,dynamic>.from((await client.dio.put('/organization/me',data:body)).data); }
