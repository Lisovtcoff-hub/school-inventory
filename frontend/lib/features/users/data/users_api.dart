import '../../../core/api/api_client.dart';
class UsersApi { final ApiClient client; UsersApi(this.client); Future<Map<String,dynamic>> list() async => Map<String,dynamic>.from((await client.dio.get('/users')).data); Future<Map<String,dynamic>> create(Map<String,dynamic> body) async => Map<String,dynamic>.from((await client.dio.post('/users',data:body)).data); }
