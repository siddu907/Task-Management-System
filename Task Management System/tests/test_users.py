from uuid import uuid4


def test_admin_user_management(client, admin):
    _, admin_headers = admin
    response = client.post("/users", json={"name": "Managed", "email": f"managed-{uuid4().hex}@example.com", "password": "Strong@123", "role": "user"}, headers=admin_headers)
    assert response.status_code == 201
    user_id = response.json()["id"]
    assert client.get("/users", headers=admin_headers).status_code == 200
    assert client.get(f"/users/{user_id}", headers=admin_headers).status_code == 200
    assert client.put(f"/users/{user_id}", json={"full_name": "Renamed"}, headers=admin_headers).status_code == 200
    assert client.delete(f"/users/{user_id}", headers=admin_headers).status_code == 200


def test_admin_cannot_create_duplicate_email_case_insensitive(client, admin):
    _, admin_headers = admin
    first_email = f"duplicate-case-{uuid4().hex}@example.com"

    first = client.post("/users", json={"name": "Duplicate", "email": first_email, "password": "Strong@123", "role": "user"}, headers=admin_headers)
    assert first.status_code == 201

    duplicate = client.post("/users", json={"name": "Duplicate 2", "email": first_email.upper(), "password": "Strong@123", "role": "user"}, headers=admin_headers)
    assert duplicate.status_code == 409


def test_regular_user_cannot_manage_users(client, register):
    _, headers, _ = register("Regular")
    assert client.get("/users", headers=headers).status_code == 403
    assert client.post("/users", json={"name": "Denied", "email": "denied@example.com", "password": "Strong@123"}, headers=headers).status_code == 403
