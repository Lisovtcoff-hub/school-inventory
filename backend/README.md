# Backend

FastAPI service for organization activation, users, equipment inventory, audit history, QR labels and PDF reports.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Run tests with `pytest`.
