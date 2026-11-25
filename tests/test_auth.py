from datetime import timedelta

import jwt
import pytest

from app.models.user import User, UserProfile
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_password_hash,
    hash_password,
    verify_password,
)


@pytest.mark.asyncio
async def test_register_user_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "profile": {
                "native_language": "fa",
                "target_language": "en",
                "level": "A2",
            },
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert data["profile"]["level"] == "A2"
    assert data["profile"]["native_language"] == "fa"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "strongpassword123",
    }
    resp1 = await client.post("/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/auth/register", json=payload)
    assert resp2.status_code == 400
    assert "already been registered" in resp2.json()["detail"]


def test_password_hashing_and_verification():
    hashed = hash_password("strongpassword123")
    assert hashed != "strongpassword123"
    assert verify_password("strongpassword123", hashed) is True
    assert verify_password("wrongpassword", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password("strongpassword123", "not-a-valid-hash") is False
    assert get_password_hash is hash_password

    with pytest.raises(ValueError, match="empty"):
        hash_password("")


@pytest.mark.asyncio
async def test_authenticate_user(db):
    active_user = User(
        email="active@example.com",
        hashed_password=hash_password("secretpass123"),
        is_active=True,
        profile=UserProfile(),
    )
    inactive_user = User(
        email="inactive@example.com",
        hashed_password=hash_password("secretpass123"),
        is_active=False,
        profile=UserProfile(),
    )
    db.add_all([active_user, inactive_user])
    await db.commit()

    authed = await authenticate_user(db, "active@example.com", "secretpass123")
    assert authed is not None
    assert authed.email == "active@example.com"

    assert await authenticate_user(db, "active@example.com", "wrong") is None
    assert await authenticate_user(db, "missing@example.com", "secretpass123") is None
    assert await authenticate_user(db, "inactive@example.com", "secretpass123") is None


def test_jwt_create_and_decode():
    token = create_access_token({"sub": "42", "email": "learner@example.com"})
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "learner@example.com"
    assert "exp" in payload

    expired_token = create_access_token({"sub": "42"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("invalid.jwt.token")
