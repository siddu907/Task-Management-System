import asyncio
from uuid import uuid4

import httpx
import pytest

from app.core.security import create_access_token, hash_password
from app.database import SessionLocal
from app.main import app
from app.models.user import User


class ApiClient:
    def _request(self, method: str, url: str, **kwargs):
        async def request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, url, **kwargs)
        return asyncio.run(request())

    def get(self, url: str, **kwargs):
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self._request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        return self._request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self._request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self._request("DELETE", url, **kwargs)


@pytest.fixture
def client():
    return ApiClient()


@pytest.fixture
def register(client):
    def create(name="Test User", role="user", phone=None):
        payload = {
            "name": name,
            "email": f"{uuid4().hex}@example.com",
            "password": "Strong@123",
            "role": role,
        }
        if phone:
            payload["phone"] = phone
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        return data["user"], {"Authorization": f"Bearer {data['access_token']}"}, payload
    return create


@pytest.fixture
def admin():
    email = f"{uuid4().hex}@example.com"
    with SessionLocal() as db:
        user = User(
            name="Test Admin",
            email=email,
            phone="9999999999",
            password_hash=hash_password("Strong@123"),
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        access_token = create_access_token(user.id, user.role)
        user_data = {"id": user.id, "email": user.email, "role": user.role}
    return user_data, {"Authorization": f"Bearer {access_token}"}
