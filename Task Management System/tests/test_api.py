import asyncio
from uuid import uuid4

import httpx

from app.core.security import hash_password, verify_password
from app.main import app


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


client = ApiClient()


def test_password_hash_round_trip():
    hashed = hash_password("Strong@123")
    assert hashed != "Strong@123"
    assert verify_password("Strong@123", hashed)
    assert not verify_password("Wrong@123", hashed)


def test_register_create_task_and_reject_invalid_transition():
    email = f"{uuid4().hex}@example.com"
    response = client.post(
        "/auth/register",
        json={"name": "Test User", "email": email, "phone": "5555555555", "password": "Strong@123", "role": "user"},
    )
    assert response.status_code == 201
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    response = client.post("/tasks", json={"title": "Test task", "priority": "high"}, headers=headers)
    assert response.status_code == 201
    task_id = response.json()["id"]

    response = client.put(f"/tasks/{task_id}/status?status=completed", headers=headers)
    assert response.status_code == 400


def test_public_registration_cannot_create_admin():
    email = f"{uuid4().hex}@example.com"
    response = client.post(
        "/auth/register",
        json={"name": "Not Admin", "email": email, "phone": "5555555556", "password": "Strong@123", "role": "admin"},
    )
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "user"


def test_task_filters_validate_sorting_and_priority():
    email = f"{uuid4().hex}@example.com"
    response = client.post(
        "/auth/register",
        json={"name": "Filter User", "email": email, "phone": "5555555557", "password": "Strong@123"},
    )
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    assert client.get("/tasks?sort_by=unknown", headers=headers).status_code == 422
    assert client.get("/tasks?priority=critical&sort_by=due_date&sort_order=asc", headers=headers).status_code == 200


def register_user(name: str) -> tuple[dict, dict]:
    response = client.post(
        "/auth/register",
        json={"name": name, "email": f"{uuid4().hex}@example.com", "password": "Strong@123"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return response.json()["user"], {"Authorization": f"Bearer {token}"}


def test_comments_notifications_and_closed_task_rules():
    _, creator_headers = register_user("Creator")
    assignee, assignee_headers = register_user("Assignee")
    response = client.post(
        "/tasks",
        json={"title": "Collaborative task"},
        headers=creator_headers,
    )
    assert response.status_code == 201
    task_id = response.json()["id"]
    assert client.put(f"/tasks/{task_id}/assign", json={"assigned_to_id": assignee["id"]}, headers=creator_headers).status_code == 200

    notifications = client.get("/notifications", headers=assignee_headers)
    assert notifications.status_code == 200
    assert any(item["notification_type"] == "task_assigned" for item in notifications.json())

    comment = client.post(
        f"/tasks/{task_id}/comments", json={"content": "Started"}, headers=assignee_headers
    )
    assert comment.status_code == 201
    assert client.put(f"/tasks/{task_id}/status?status=in_progress", headers=assignee_headers).status_code == 200
    assert client.put(f"/tasks/{task_id}/status?status=completed", headers=assignee_headers).status_code == 200
    assert client.post(f"/tasks/{task_id}/comments", json={"content": "Too late"}, headers=creator_headers).status_code == 400


def test_change_password_and_attachment_validation():
    user, headers = register_user("Password User")
    response = client.put(
        "/auth/change-password",
        json={"current_password": "Strong@123", "new_password": "NewStrong@123"},
        headers=headers,
    )
    assert response.status_code == 200
    assert client.post("/auth/login", json={"email": "missing@example.com", "password": "NewStrong@123"}).status_code == 401

    login = client.post("/auth/login", json={"email": user["email"], "password": "NewStrong@123"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    task = client.post("/tasks", json={"title": "Attachment task"}, headers=headers)
    task_id = task.json()["id"]
    upload = client.post(
        f"/tasks/{task_id}/attachments",
        files={"file": ("malware.exe", b"bad", "application/octet-stream")},
        headers=headers,
    )
    assert upload.status_code == 400
