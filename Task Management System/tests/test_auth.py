def test_register_login_profile_logout_and_change_password(client, register):
    user, headers, payload = register("Auth User", phone="1234567890")
    assert user["role"] == "user"
    assert client.get("/auth/profile", headers=headers).json()["email"] == payload["email"]
    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    changed = client.put("/auth/change-password", json={"current_password": "Strong@123", "new_password": "NewStrong@123"}, headers=headers)
    assert changed.status_code == 200
    assert client.get("/auth/profile", headers=headers).status_code == 401
    assert client.post("/auth/login", json={"email": payload["email"], "password": "NewStrong@123"}).status_code == 200


def test_auth_validation_and_protected_access(client):
    assert client.get("/auth/profile").status_code == 401
    assert client.post("/auth/login", json={"email": "invalid@example.com", "password": "bad"}).status_code == 401
    assert client.post("/auth/register", json={"name": "Weak", "email": "weak@example.com", "password": "weak"}).status_code == 422


def test_register_and_login_only_access_token(client, register):
    _, _, payload = register("Refresh User")
    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert "refresh_token" not in data
