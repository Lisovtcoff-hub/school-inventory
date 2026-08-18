# Security notes

## Authentication

The API issues signed JWT access tokens after organization activation or user login. Passwords are hashed with bcrypt and are never returned through API schemas.

## Authorization

Roles are enforced in the service layer:

- `admin` manages organization data, users and inventory.
- `editor` manages inventory.
- `viewer` has read-only inventory access.

Organization identifiers are never accepted as trusted input for tenant-scoped operations.

## Configuration

Production mode requires:

- a secret of at least 32 characters;
- PostgreSQL as the database;
- explicit CORS origins;
- HTTPS at the reverse proxy or ingress layer.

The repository contains only placeholders. Real `.env` files, databases and generated reports are ignored by Git.

## Operational recommendations

A public deployment should also add request rate limiting for login and activation, centralized logging, regular database backups and short-lived access tokens with a refresh-token strategy where required.
