import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database_utilis_related.database import Base
from database_utilis_related.utils import get_db
from motivationtext_related.motivationtext_route import load_quotes_into_db
import main

# One shared in-memory SQLite DB for the whole test session.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    # The app's lifespan seeds quotes into the real DB; do the same for the
    # test DB so motivation endpoints have data.
    seed_db = TestingSessionLocal()
    load_quotes_into_db(seed_db)
    seed_db.close()

    main.app.dependency_overrides[get_db] = _override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(client):
    """Register a user and return an Authorization header for them."""
    client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "Passw0rd", "name": "Test"},
    )
    resp = client.post(
        "/login",
        data={"username": "test@example.com", "password": "Passw0rd"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
