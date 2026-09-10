def _create_med(client, headers, name="Aspirin", dosage="100mg"):
    return client.post(
        "/medications/", json={"name": name, "dosage": dosage}, headers=headers
    )


def test_medication_crud_flow(client, auth_headers):
    resp = _create_med(client, auth_headers)
    assert resp.status_code == 200
    med = resp.json()
    med_id = med["id"]
    assert med["archived"] is False

    # get by id returns that one medication (not a list)
    resp = client.get(f"/medications/{med_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == med_id

    # update
    resp = client.put(
        f"/medications/{med_id}", json={"dosage": "200mg"}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["dosage"] == "200mg"

    # archive
    resp = client.put(f"/medications/archive/{med_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert client.get("/medications/me", headers=auth_headers).json() == []
    assert len(client.get("/medications/archived", headers=auth_headers).json()) == 1

    # delete
    assert client.delete(f"/medications/{med_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/medications/{med_id}", headers=auth_headers).status_code == 404


def test_medications_require_auth(client):
    assert client.get("/medications/me").status_code == 401


def test_duplicate_medication_rejected(client, auth_headers):
    assert _create_med(client, auth_headers).status_code == 200
    assert _create_med(client, auth_headers).status_code == 400


def test_cannot_read_another_users_medication(client, auth_headers):
    other = _create_med(client, auth_headers).json()

    client.post(
        "/users/register",
        json={"email": "intruder@example.com", "password": "Secret123", "name": "I"},
    )
    token = client.post(
        "/login", data={"username": "intruder@example.com", "password": "Secret123"}
    ).json()["access_token"]
    intruder = {"Authorization": f"Bearer {token}"}

    assert client.get(f"/medications/{other['id']}", headers=intruder).status_code == 404
