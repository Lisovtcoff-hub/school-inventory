# Architecture

## Backend layers

The FastAPI application uses a conventional route-service-repository structure:

- **Routes** validate HTTP input and expose response models.
- **Services** implement authorization, license limits, asset lifecycle rules, reporting and QR generation.
- **Repositories** contain SQLAlchemy queries and persistence operations.
- **Models and schemas** separate database entities from public API contracts.

The authenticated user is resolved from the JWT token. Every inventory, user and report operation derives the organization ID from that user, which prevents clients from selecting another tenant through request data.

## Asset identity

Each organization receives an eight-digit public identifier. Assets receive an organization-local sequence number. Their public asset code is produced by concatenating both values:

```text
organization public ID + eight-digit local number
12345678               + 00000001 = 1234567800000001
```

A database uniqueness constraint protects the local number inside an organization. Asset creation retries on a concurrent uniqueness conflict.

## Audit history

Asset creation, deletion and selected field changes create history records in the same transaction as the asset operation. Manual notes use the same history stream and include the acting user.

## Reporting

Report services read normalized inventory records and return typed preview models. PDF rendering is kept in the service layer so the same calculations serve both the Flutter preview and exported documents.

Available reports:

- OO-2 section 2.1 calculation aid
- Classroom passport grouped by equipment purpose

## Flutter client

The client is split into feature modules:

```text
features/
  auth/
  dashboard/
  organization/
  users/
  assets/
  asset_history/
  qr/
  reports/
```

`ApiClient` owns authentication headers and backend error normalization. `AuthController` owns session bootstrap and logout. Navigation is guarded by authentication state through GoRouter.
