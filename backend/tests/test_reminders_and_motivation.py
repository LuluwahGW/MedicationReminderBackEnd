def _med(client, headers):
    return client.post(
        "/medications/", json={"name": "Aspirin", "dosage": "100mg"}, headers=headers
    ).json()


def test_reminder_flow(client, auth_headers):
    med = _med(client, auth_headers)
    resp = client.post(
        "/reminders/",
        json={
            "medication_id": med["id"],
            "name": "Morning dose",
            "reminder_time": "2026-09-12T08:00:00",
            "frequency": "DAILY",
            "message": "Take with water",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    reminder = resp.json()
    assert reminder["isTaken"] is False

    resp = client.get("/reminders/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.patch(
        f"/reminders/{reminder['id']}", json={"isTaken": True}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["isTaken"] is True
    assert resp.json()["id"] == reminder["id"]  # full object, not just the update

    assert client.delete(
        f"/reminders/{reminder['id']}", headers=auth_headers
    ).status_code == 200


def test_reminder_rejects_medication_of_another_user(client, auth_headers):
    client.post(
        "/users/register",
        json={"email": "other@example.com", "password": "Secret123", "name": "O"},
    )
    token = client.post(
        "/login", data={"username": "other@example.com", "password": "Secret123"}
    ).json()["access_token"]
    other_med = _med(client, {"Authorization": f"Bearer {token}"})

    resp = client.post(
        "/reminders/",
        json={
            "medication_id": other_med["id"],
            "name": "x",
            "reminder_time": "2026-09-12T08:00:00",
            "frequency": "ONCE",
            "message": "x",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_motivation_random_returns_a_quote(client):
    resp = client.get("/motivation/random")
    assert resp.status_code == 200
    assert isinstance(resp.json(), str)
    assert len(resp.json()) > 0
