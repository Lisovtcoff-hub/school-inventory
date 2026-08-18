import '../../../core/api/api_client.dart';
import '../models/auth_models.dart';

class AuthApi {
  final ApiClient client; AuthApi(this.client);
  Future<MeResponse> me() async => MeResponse.fromJson((await client.dio.get('/auth/me')).data);
  Future<MeResponse> activate(Map<String,dynamic> body) async {
    final r = await client.dio.post('/auth/activate', data: body);
    await client.tokenStorage.saveToken(r.data['access_token']);
    return MeResponse(user: AuthUser.fromJson(r.data['user']), organization: AuthOrganization.fromJson(r.data['organization']));
  }
  Future<void> login(String email, String password) async {
    final r = await client.dio.post('/auth/login', data: {'email': email, 'password': password});
    await client.tokenStorage.saveToken(r.data['access_token']);
  }
}
