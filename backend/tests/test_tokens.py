"""Regression coverage for the JWT library replacement and algorithm restrictions."""

import base64
import hashlib
import hmac
import json
from datetime import timedelta

import jwt
import pytest
from fastapi import HTTPException

from database_utilis_related import utils


TEST_KEY = "test-only-signing-key-with-at-least-32-bytes"


@pytest.fixture(autouse=True)
def token_settings(monkeypatch):
    monkeypatch.setattr(utils, "SECRET_KEY", TEST_KEY)
    monkeypatch.setattr(utils, "ALGORITHM", "HS256")


def test_new_token_round_trip():
    claims = {"sub": "42"}
    token = utils.create_access_token(claims)
    assert utils.verify_token(token) == "42"
    assert "exp" in jwt.decode(token, TEST_KEY, algorithms=["HS256"])
    assert claims == {"sub": "42"}


def test_legacy_hs256_token_remains_valid():
    # Build the standard compact JWT representation emitted by python-jose,
    # independently of PyJWT, so existing sessions need not be invalidated.
    def encode(data):
        return base64.urlsafe_b64encode(data).rstrip(b"=")

    header = encode(b'{"alg":"HS256","typ":"JWT"}')
    payload = encode(json.dumps({"sub": "42", "exp": 4102444800}).encode())
    message = header + b"." + payload
    signature = encode(hmac.new(TEST_KEY.encode(), message, hashlib.sha256).digest())
    assert utils.verify_token((message + b"." + signature).decode()) == "42"


def test_expired_token_is_unauthorized():
    token = utils.create_access_token({"sub": "42"}, timedelta(seconds=-1))
    with pytest.raises(HTTPException) as error:
        utils.verify_token(token)
    assert error.value.status_code == 401
    assert error.value.detail == "Token Expired"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-token",
        jwt.encode({"sub": "42"}, "wrong-key-with-at-least-32-bytes-long", algorithm="HS256"),
        jwt.encode({"sub": "42"}, TEST_KEY, algorithm="HS384"),
        jwt.encode({"sub": "42"}, "", algorithm="none"),
        jwt.encode({"sub": 42}, TEST_KEY, algorithm="HS256"),
        jwt.encode({}, TEST_KEY, algorithm="HS256"),
    ],
)
def test_invalid_tokens_are_unauthorized(client, token):
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_tampered_token_is_unauthorized(client):
    token = utils.create_access_token({"sub": "42"})
    header, _, signature = token.split(".")
    payload = base64.urlsafe_b64encode(b'{"sub":"1","exp":4102444800}').rstrip(b"=").decode()
    response = client.get(
        "/me", headers={"Authorization": f"Bearer {header}.{payload}.{signature}"}
    )
    assert response.status_code == 401
