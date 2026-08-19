# School Inventory

[![CI](https://github.com/lisovcoff/school-inventory/actions/workflows/ci.yml/badge.svg)](https://github.com/lisovcoff/school-inventory/actions/workflows/ci.yml)

Asset management platform for schools and similar organizations. The project combines a FastAPI backend with Flutter clients for Android and Windows, supports organization-level data isolation, generates QR labels, keeps an audit history, and produces PDF reports.

## Highlights

- organization activation through license codes;
- JWT authentication with administrator, editor, and viewer roles;
- inventory catalog with search, filters, pagination, and soft deletion;
- generated 16-digit asset identifiers and printable QR labels;
- audit trail for important field changes and manual notes;
- dashboard statistics and PDF exports for operational reporting;
- backend and client CI coverage.

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic
- **Database:** PostgreSQL; SQLite for isolated tests
- **Client:** Flutter, Dart, Provider, GoRouter, Dio
- **Documents:** ReportLab, Pillow, qrcode
- **Infrastructure:** Docker Compose, GitHub Actions
- **Testing:** Pytest, FastAPI TestClient, Flutter Test

## Architecture

```text
Flutter client (Android / Windows)
               |
               | REST + JWT
               v
        FastAPI backend
          /           \
 PostgreSQL       QR / PDF services
```

The backend is split into API routes, services, repositories, and SQLAlchemy models. The Flutter application is organized by product feature and uses a single authenticated API client.

Additional notes: [architecture](docs/architecture.md), [security](docs/security.md).

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

The API is available at `http://localhost:8000`, OpenAPI at `/docs`, and the health check at `/health`.

Create a development license after startup:

```bash
docker compose exec api python -m app.scripts.create_license
```

## Development and tests

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
pytest
```

Client:

```bash
python scripts/bootstrap_flutter.py
cd frontend
flutter pub get
flutter analyze
flutter test
```

Run Android Emulator with `--dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1`.

## Repository layout

```text
backend/      FastAPI application, migrations, and API tests
frontend/     Flutter application and Dart tests
docs/         architecture and security notes
scripts/      reproducible Flutter platform bootstrap
compose.yaml  PostgreSQL and backend development stack
```

## Notes

- Secrets and environment-specific settings are loaded from environment variables.
- This public repository excludes organization data, deployment credentials, and real license codes.
- Regulatory reports should be validated against current local requirements before operational use.
