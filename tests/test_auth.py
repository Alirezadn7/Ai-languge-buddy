import pytest


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
