# School Inventory

[![CI](https://github.com/Lisovtcoff-hub/school-inventory/actions/workflows/ci.yml/badge.svg)](https://github.com/Lisovtcoff-hub/school-inventory/actions/workflows/ci.yml)

A cross-platform asset management system for schools and other educational organizations. The project combines a FastAPI backend with an Android and Windows Flutter client, tracks equipment throughout its lifecycle, generates QR labels, keeps an audit history, and produces regulatory and operational PDF reports.

> This public repository is a portfolio-safe source version. It contains no school records, real license codes, or deployment credentials.

## What the project does

- activates organizations through license codes;
- provides JWT authentication and administrator, editor, and viewer roles;
- isolates data by organization;
- manages an equipment catalog with search, filters, pagination, and soft deletion;
- generates 16-digit asset identifiers and printable QR labels;
- records important field changes and manual audit notes;
- calculates dashboard statistics across the inventory;
- generates OO-2 section 2.1 and classroom passport PDF reports;
- validates the PostgreSQL migration chain and application behavior in CI.

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

The backend is organized into API routes, services, repositories, and SQLAlchemy models. The Flutter application is grouped by product feature and communicates through one authenticated API client.

See [docs/architecture.md](docs/architecture.md) for additional details.

## Technology stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic
- **Database:** PostgreSQL; SQLite for isolated tests
- **Client:** Flutter, Dart, Provider, GoRouter, Dio
- **Documents:** ReportLab, Pillow, qrcode
- **Infrastructure:** Docker Compose, GitHub Actions
- **Testing:** Pytest, FastAPI TestClient, Flutter Test

## Quick start

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

## Project structure

```text
backend/      FastAPI application, migrations, and API tests
frontend/     Flutter application and Dart tests
docs/         architecture and security notes
scripts/      reproducible Flutter platform bootstrap
compose.yaml  PostgreSQL and backend development stack
```

## Security and operational notes

- Passwords are stored as bcrypt hashes.
- JWT secrets and database credentials are loaded from environment variables.
- Production mode rejects placeholder secrets and unsupported database configuration.
- Organization scope is derived from the authenticated user.
- Viewer accounts cannot modify inventory.
- Regulatory reports are calculation aids and must be checked against current official requirements.

See [docs/security.md](docs/security.md) for implementation details.

## Project status

The repository demonstrates a complete asset-management workflow with backend and client CI. Generated platform files are reproducible, while local databases, environment files, and operational data remain outside Git.

## Author

Sergey Inozemtsev — Python backend developer

GitHub: https://github.com/Lisovtcoff-hub
