# Medication Reminder

A full-stack medication reminder project: a **FastAPI + SQLAlchemy + MySQL backend** for managing users, medications, reminders, and caregiver-patient links, plus a **simple vanilla HTML/JS frontend** for testing the API.

## Project Structure

```
MedicationReminderBackEnd/
├── backend/
│   ├── main.py                     # FastAPI app entrypoint, routers, auth
│   ├── requirements.txt            # Python dependencies
│   ├── database_utilis_related/    # DB connection, models, auth utils
│   ├── user_related/               # Registration, login, profile
│   ├── medications_related/        # Medication CRUD
│   ├── reminders_related/          # Reminder CRUD
│   ├── caregiver_related/          # Caregiver-patient linking
│   └── motivationtext_related/     # Random motivational messages
└── frontend/
    ├── index.html                  # Test UI (login, dashboard, forms)
    └── script.js                   # Calls the backend API
```

## Features

* **User Management:** Registration, login, and profile updates.
* **Authentication:** JWT (JSON Web Token) authentication for all protected routes.
* **Medication Management:** Full CRUD (Create, Read, Update, Delete) operations for medications, including archiving.
* **Reminder Management:** Full CRUD operations for reminders, linked to specific medications and users, with support for one-time, daily, weekly, and monthly frequency.
* **Caregiver System:**
    * Patients can assign caregivers.
    * Caregivers can view a list of their assigned patients and their non-archived medications.
* **Motivational Text:** An endpoint to retrieve random motivational messages, surfaced on the dashboard.
* **CORS Enabled:** Configured to allow requests from the local frontend (`http://127.0.0.1:5500` by default).

## Frontend Status

The `frontend/` folder is a minimal, functional HTML/JS client used to exercise the API (login, add/view/archive medications, create reminders, fetch motivation). **It currently has no styling** — `index.html` references a `styles.css` file that doesn't exist yet, so the page will render unstyled. Styling is a planned next step; contributions welcome.

## 🛠 Tech Stack

**Backend**
* Python 3.11+
* FastAPI
* SQLAlchemy
* MySQL
* Pydantic
* Uvicorn
* Passlib (for password hashing)
* python-jose (for JWT)

**Frontend**
* HTML5
* Vanilla JavaScript (fetch API)
* CSS — *not yet implemented*

## Getting Started

### 1. Prerequisites

* Python 3.11+
* A running MySQL server
* (Optional) A simple static server for the frontend, e.g. VS Code's Live Server extension

### 2. Backend Setup

1.  Clone the repository:
    ```
    git clone https://github.com/LuluwahGW/MedicationReminderBackEnd.git
    cd MedicationReminderBackEnd/backend
    ```

2.  Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3.  Configure the database:
    * Ensure your MySQL server is running.
    * Create a database (e.g., `medications_db`).
    * Update the `DATABASE_URL` string in `database_utilis_related/database.py` with your MySQL username, password, host, and database name.

4.  Run the server:
    ```
    uvicorn main:app --reload
    ```
    The API will be live at `http://127.0.0.1:8000`.

### 3. Frontend Setup

1.  Open `frontend/index.html` with a static file server (e.g. Live Server, defaulting to `http://127.0.0.1:5500`), so it matches the CORS origin configured in `main.py`.
2.  The page will load unstyled until `frontend/styles.css` is added — the JS functionality (login, medication/reminder management) works regardless.

## API Endpoints

All protected routes require a `Bearer` token in the Authorization header.

* `POST /login`: Authenticate and receive a JWT token.
* `POST /users/register`: Register a new user.
* `PATCH /users/me`: Update the current user's details.
* `DELETE /users/me`: Delete the current user and their associated data.
* `POST /medications/`: Create a new medication.
* `GET /medications/me`: List all of the current user's medications.
* `GET /medications/{med_id}`: Get a specific medication.
* `PUT /medications/{med_id}`: Update a medication.
* `DELETE /medications/archive/{med_id}`: Archive a medication.
* `DELETE /medications/{med_id}`: Permanently delete a medication.
* `POST /reminders/`: Create a new reminder.
* `GET /reminders/{user_id}`: Get all reminders for the current user.
* `PATCH /reminders/{reminder_id}`: Update a reminder.
* `DELETE /reminders/{reminder_id}`: Delete a reminder.
* `POST /caregivers/assign`: Assign a caregiver to the current user.
* `DELETE /caregivers/{caregiver_id}`: Remove an assigned caregiver.
* `GET /caregivers/me/patients`: (As a caregiver) Get all assigned patients and their medications.
* `GET /caregivers/patients/{patient_id}/medications`: (As a caregiver) Get medications for a specific patient.
* `GET /motivation/random`: Get a random motivational text.