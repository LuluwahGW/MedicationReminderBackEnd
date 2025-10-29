# Medication Reminder API

A backend API built with FastAPI and SQLAlchemy for creating and managing users, medications, reminders, and caregiver-patient links.

## Features

* **User Management:** User registration, login, and profile updates.
* **Authentication:** Secure JWT (JSON Web Token) authentication for all protected routes.
* **Medication Management:** Full CRUD (Create, Read, Update, Delete) operations for medications, including archiving.
* **Reminder Management:** Full CRUD operations for reminders, linked to specific medications and users.
* **Caregiver System:**
    * Patients can assign caregivers.
    * Caregivers can view a list of their assigned patients and their non-archived medications.
* **Motivational Text:** A simple endpoint to retrieve random motivational messages.
* **CORS Enabled:** Configured to allow requests from `http://localhost:3000` and `http://127.0.0.1:5500`.

## 🛠 Tech Stack

* Python 3.11+
* FastAPI
* SQLAlchemy
* MySQL
* Pydantic
* Uvicorn
* Passlib (for password hashing)
* python-jose (for JWT)

## 🚀 Getting Started

### 1. Prerequisites

* Python 3.11+
* A running MySQL server

### 2. Installation & Setup

1.  Clone the repository:
    
    git clone [https://github.com/LuluwahGW/MedicationReminderBackEnd.git]
    cd [MedicationReminderBackEnd]
    

2.  Install dependencies:
    
    pip install -r requirements.txt
    

3.  Configure the database:
    * Ensure your MySQL server is running.
    * Create a database (e.g., `medications_db`).
    * Update the `DATABASE_URL` string in `database_utilis_related/database.py` with your MySQL username, password, host, and database name.

4.  Run the server:
    
    uvicorn main:app --reload
    
    The API will be live at `http://127.0.0.1:8000`.

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