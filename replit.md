# Medication Reminder

## Run on Replit

Use the **Start application** workflow (or Run). It starts:

```sh
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

FastAPI serves both the existing `frontend/` files and the API on one origin.
The preview opens `/`; API documentation is at `/docs`, and `/health` reports
server status.

## Dependencies

Python 3.12 is configured. The original pinned dependencies remain in
`backend/requirements.txt`; `pyproject.toml` and `uv.lock` support Replit's
Python package environment. Keep dependency declarations consistent when updating.

## Configuration and data

- Authentication uses `SECRET_KEY`, or the existing Replit `SESSION_SECRET`
  when `SECRET_KEY` is absent. Never commit secret values.
- SQLite is retained as the original default. The workflow creates
  `backend/medications_db.db` and seeds motivation quotes automatically.
- `DATABASE_URL` can select an external database supported by the project.
  No database migration or external service was configured during import setup.
- Local SQLite is suitable for workspace testing, but should not be relied on
  for durable published data. Configure durable storage before real use.
- Reminder schedules are stored; the project does not yet deliver notifications.

## Tests

```sh
cd backend && python -m pytest
```

The tests use an in-memory database for API operations and a test-only signing key.
The application lifespan also initializes the configured application database.
