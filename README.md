# Medication Reminder

A full-stack medication management app: a **FastAPI + SQLAlchemy** REST API with JWT
authentication for users, medications, reminders, and caregiver–patient links, plus a
lightweight vanilla HTML/JS frontend that consumes the API.

![status](https://github.com/LuluwahGW/MedicationReminderBackEnd/actions/workflows/ci.yml/badge.svg)

## Features

- **Authentication** — registration with password-strength rules, JWT bearer tokens
  (`python-jose`), bcrypt password hashing (`passlib`).
- **Medications** — full CRUD per user, plus archive / unarchive; every query is scoped
  to the authenticated owner.
- **Reminders** — CRUD linked to a medication, with `ONCE` / `DAILY` / `WEEKLY` /
  `MONTHLY` frequency; a reminder can only be created against a medication you own.
- **Caregivers** — a patient can assign another user as a caregiver; caregivers get a
  read-only view of their patients' active medications.
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
| Frontend | HTML + vanilla JS (`fetch`) + CSS |

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
│   ├── caregiver_related/          # caregiver assignment + patient views
│   ├── motivationtext_related/     # random messages + motivation_quotes.json
│   └── tests/
├── frontend/                       # index.html, script.js, styles.css
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

The database (SQLite file) and tables are created automatically on first run.

### Frontend

Serve `frontend/` with any static server on port 5500 so it matches the CORS allow-list
(VS Code Live Server, or):

```bash
cd frontend && python -m http.server 5500 --bind 127.0.0.1
```

Then open <http://127.0.0.1:5500>.

### Docker

```bash
cd backend
docker build -t medication-reminder .
docker run -p 8000:8000 -e SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(32))") medication-reminder
```

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
| `POST /caregivers/assign` · `DELETE /caregivers/{cg_id}` | Manage own caregivers |
| `GET /caregivers/me/patients` · `GET /caregivers/patients/{id}/medications` | Caregiver views |
| `GET /motivation/random` · `POST /motivation/` | Random message / add one |

## Roadmap

- Actually *deliver* reminders (background scheduler + email/push) — currently reminders
  are only stored and queried.
- Alembic migrations instead of `create_all`.
- Caregiver invitations require the caregiver's acceptance.
- Move `/login` and auth helpers into a dedicated `auth` module.
