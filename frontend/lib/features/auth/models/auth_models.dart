class AuthUser {
  final int id; final String email; final String fullName; final String role; final int organizationId;
  AuthUser({required this.id, required this.email, required this.fullName, required this.role, required this.organizationId});
  factory AuthUser.fromJson(Map<String,dynamic> j)=>AuthUser(id:j['id'],email:j['email'],fullName:j['full_name'],role:j['role'],organizationId:j['organization_id']);
}
class AuthOrganization {
  final int id; final String publicId; final String name;
  AuthOrganization({required this.id, required this.publicId, required this.name});
  factory AuthOrganization.fromJson(Map<String,dynamic> j)=>AuthOrganization(id:j['id'],publicId:j['public_id'],name:j['name']);
}
class MeResponse {
  final AuthUser user; final AuthOrganization organization;
  MeResponse({required this.user, required this.organization});
  factory MeResponse.fromJson(Map<String,dynamic> j)=>MeResponse(user:AuthUser.fromJson(j['user']),organization:AuthOrganization.fromJson(j['organization']));
}
