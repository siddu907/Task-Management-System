from datetime import timedelta

from app.core.security import create_access_token


def test_duplicate_email_is_rejected(client, register):
    _, _, payload = register("Duplicate User")
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_invalid_and_expired_tokens_are_rejected(client):
    assert client.get("/auth/profile", headers={"Authorization": "Bearer not-a-token"}).status_code == 401
    expired = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
    assert client.get("/auth/profile", headers={"Authorization": f"Bearer {expired}"}).status_code == 401


def test_invalid_registration_fields_are_rejected(client):
    assert client.post("/auth/register", json={"name": "Bad", "email": "not-an-email", "password": "Strong@123"}).status_code == 422
    assert client.post("/auth/register", json={"name": "Bad", "email": "bad-phone@example.com", "phone": "123", "password": "Strong@123"}).status_code == 422
    assert client.post("/auth/register", json={"name": "Bad", "email": "bad-password@example.com", "password": "NoStrength"}).status_code == 422


def test_change_password_requires_current_password(client, register):
    _, headers, _ = register("Password Check")
    response = client.put("/auth/change-password", json={"current_password": "Wrong@123", "new_password": "NewStrong@123"}, headers=headers)
    assert response.status_code == 400
