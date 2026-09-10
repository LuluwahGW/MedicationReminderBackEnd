def test_health(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_and_login(client):
    resp = client.post(
        "/users/register",
        json={"email": "new@example.com", "password": "Secret123", "name": "New"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"name": "New", "email": "new@example.com"}

    resp = client.post(
        "/login", data={"username": "new@example.com", "password": "Secret123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_rejects_weak_password(client):
    resp = client.post(
        "/users/register",
        json={"email": "weak@example.com", "password": "short", "name": "W"},
    )
    assert resp.status_code == 422


def test_register_rejects_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "Secret123", "name": "D"}
    assert client.post("/users/register", json=payload).status_code == 200
    assert client.post("/users/register", json=payload).status_code == 400


def test_login_with_wrong_password(client):
    client.post(
        "/users/register",
        json={"email": "x@example.com", "password": "Secret123", "name": "X"},
    )
    resp = client.post("/login", data={"username": "x@example.com", "password": "nope"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/me").status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"
