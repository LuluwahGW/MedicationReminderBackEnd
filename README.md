# Medication Reminder

A full-stack medication management app: a **FastAPI + SQLAlchemy** REST API with JWT
authentication for users, medications, reminders, and caregiver–patient links, plus a
separate frontend that consumes the API. The current frontend is built with Lovable; the
original vanilla HTML/JS frontend is kept in `archive/frontend-vanilla/`.

![status](https://github.com/LuluwahGW/MedicationReminderBackEnd/actions/workflows/ci.yml/badge.svg)

## Features

- **Authentication** — registration with password-strength rules, JWT bearer tokens
  (`python-jose`), bcrypt password hashing (`passlib`).
- **Medications** — full CRUD per user, plus archive / unarchive; every query is scoped
  to the authenticated owner.
- **Reminders** — CRUD linked to a medication, with `ONCE` / `DAILY` / `WEEKLY` /
  `MONTHLY` frequency; a reminder can only be created against a medication you own.
- **Caregivers** — a patient creates a single-use invite link; the caregiver must sign in
  and accept before getting a read-only view of the patient's active medications.
- **Motivational messages** — random message endpoint, seeded from a committed JSON file
  that is synced into the database on startup (no manual seeding step).
- **Tested** — pytest suite covering auth, ownership isolation, and the main flows; run
  automatically in CI on every push.

## Tech stack

| Layer    | Choice |
|----------|--------|
| API      | FastAPI, Pydantic v2 |
| ORM / DB | SQLAlchemy 2, SQLite by default (`DATABASE_URL` swaps in Postgres/MySQL) |
| Auth     | JWT (`python-jose`), bcrypt (`passlib`) |
| Config   | `python-dotenv` |
| Tests    | pytest, Starlette `TestClient` |
| CI       | GitHub Actions |
| Frontend | Lovable-built web app (current) · vanilla HTML/JS in `archive/frontend-vanilla/` |

## Project structure

```
MedicationReminderBackEnd/
├── backend/
│   ├── main.py                     # app factory, lifespan, /login, /me, health
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── .env.example
│   ├── database_utilis_related/    # engine/session, ORM models, auth utils
│   ├── user_related/               # register, update, delete account
│   ├── medications_related/        # medication CRUD + archive
│   ├── reminders_related/          # reminder CRUD
│   ├── caregiver_related/          # invite links + caregiver/patient views
│   ├── motivationtext_related/     # random messages + motivation_quotes.json
│   └── tests/
└── archive/frontend-vanilla/       # original plain HTML/JS frontend (still works)
└── .github/workflows/ci.yml
```

## Getting started

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# set SECRET_KEY in .env — generate one with:
python -c "import secrets; print(secrets.token_urlsafe(32))"

uvicorn main:app --reload
```

API: <http://127.0.0.1:8000> · interactive docs: <http://127.0.0.1:8000/docs>

The backend is an API only by default. To also serve the archived vanilla frontend from it,
set `FRONTEND_DIR=../archive/frontend-vanilla` in `.env` and open the backend URL.
The database (SQLite file) and tables are created automatically on first run.

### Frontend

A deployed frontend (Lovable) must be allowed by CORS: set `CORS_ORIGINS` (comma-separated
origins) and/or `CORS_ORIGIN_REGEX` on the host. Login is form-encoded (`username`,
`password`); other requests use `Authorization: Bearer <token>`.

To run the archived vanilla frontend with a separate static server (e.g. VS Code Live
Server), serve `archive/frontend-vanilla/` on
port 5500 — the page then calls the API at `http://127.0.0.1:8000`, which is on the CORS
allow-list:

```bash
cd archive/frontend-vanilla && python -m http.server 5500 --bind 127.0.0.1
```

### Docker

```bash
cd backend
docker build -t medication-reminder .
docker run -p 8000:8000 -e SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(32))") medication-reminder
```

### Deploy on Replit

1. Create a Repl with **Import from GitHub** (Python 3.11). The included `.replit` file
   installs dependencies and starts the app on port 8000.
2. In **Secrets**, add `SECRET_KEY` (generate one with the command above).
3. For data that survives restarts and redeploys, add Replit's **PostgreSQL** database and
   make sure `DATABASE_URL` is set (Replit normally adds it). Without it the app falls back
   to a local SQLite file, which may be wiped on redeploy.
4. Run, then Deploy. Make sure the deployment also has `SECRET_KEY` and `DATABASE_URL`.

## Tests

```bash
cd backend && pytest
```

## API overview

Protected routes require an `Authorization: Bearer <token>` header.

| Method & path | Description |
|---|---|
| `POST /users/register` | Create an account |
| `POST /login` | Get a JWT (form-encoded: `username`, `password`) |
| `GET /me` | Current user |
| `PATCH /users/me` · `DELETE /users/me` | Update / delete own account |
| `POST /medications/` · `GET /medications/me` · `GET /medications/archived` | Create / list |
| `GET /medications/{id}` · `PUT /medications/{id}` · `DELETE /medications/{id}` | Read / update / delete one |
| `PUT /medications/archive/{id}` | Archive |
| `POST /reminders/` · `GET /reminders/` | Create / list own reminders |
| `PATCH /reminders/{id}` · `DELETE /reminders/{id}` | Update / delete |
| `POST /caregivers/invite-links` | Create a single-use, 7-day invite link to give to a caregiver |
| `GET /caregivers/invite-links/{token}` · `POST /caregivers/invite-links/{token}/accept` | Caregiver previews who invited them / accepts (grants access) |
| `GET /caregivers/me` · `DELETE /caregivers/{cg_id}` | List my caregivers + status / remove a caregiver |
| `GET /caregivers/me/patients` · `GET /caregivers/patients/{id}/medications` | Caregiver views (accepted links only) |
| `GET /motivation/random` | Random motivational message |

## Roadmap

- Actually *deliver* reminders (background scheduler + email/push) — currently reminders
  are only stored and queried.
- Alembic migrations instead of `create_all`.
- Move `/login` and auth helpers into a dedicated `auth` module.
